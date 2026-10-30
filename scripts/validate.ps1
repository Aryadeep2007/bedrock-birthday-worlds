<#
.SYNOPSIS
    Validation script for bedrock-birthday-worlds.
    Validates manifests, scripts, and generated assets.

.DESCRIPTION
    This script performs comprehensive validation of:
    - manifest.json files (resource pack and behavior pack)
    - JavaScript syntax (behavior pack scripts)
    - Photo processing outputs
    - Audio files
    - .mcworld package structure

.NOTES
    Run after building to verify everything is correct before distribution.
#>

param(
    [string]$ConfigName = "",  # Optional: validate specific config build
    [string]$McworldPath = "",  # Optional: validate specific .mcworld file
    [switch]$Strict,
    [switch]$Verbose,
    [switch]$Help
)

$ErrorActionPreference = "Continue"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $prefix = switch ($Level) {
        "ERROR" { "❌" }
        "WARN"  { "⚠️" }
        "OK"    { "✅" }
        "CHECK" { "🔍" }
        default { "ℹ️" }
    }
    Write-Host "[$timestamp] $prefix $Message"
}

function Show-Help {
    @"
Usage: .\scripts\validate.ps1 [Options]

Options:
  -ConfigName <name>    Validate build for specific config (e.g., "ujan")
  -McworldPath <path>   Validate specific .mcworld file
  -Strict               Treat warnings as errors
  -Verbose              Verbose output
  -Help                 Show this help

Examples:
  .\scripts\validate.ps1
  .\scripts\validate.ps1 -ConfigName ujan
  .\scripts\validate.ps1 -McworldPath "private-builds\Happy_Birthday_Ujan.mcworld" -Strict
"@
}

if ($Help) {
    Show-Help
    exit 0
}

$scriptDir = Split-Path $PSScriptRoot
$errors = 0
$warnings = 0

function Add-Error { param($msg) { Write-Log $msg "ERROR"; $script:errors++ } }
function Add-Warning { param($msg) { Write-Log $msg "WARN"; $script:warnings++ } }
function Add-Ok { param($msg) { Write-Log $msg "OK" } }

Write-Host "╔══════════════════════════════════════════════════════════════╗"
Write-Host "║     Validation Suite                                         ║"
Write-Host "╚══════════════════════════════════════════════════════════════╝"

# ========================================================================
# Validate Template Manifests
# ========================================================================
Write-Log "Validating template manifests..." "CHECK"

$rpManifest = Join-Path $scriptDir "templates\resource-pack\manifest.json"
$bpManifest = Join-Path $scriptDir "templates\behavior-pack\manifest.json"

function Validate-Manifest {
    param([string]$Path, [string]$Type)
    if (-not (Test-Path $Path)) {
        Add-Error "Manifest not found: $Path"
        return
    }

    try {
        $manifest = Get-Content $Path -Raw | ConvertFrom-Json

        # Check required header fields
        $requiredHeader = @("description", "name", "uuid", "version", "min_engine_version")
        foreach ($field in $requiredHeader) {
            if (-not $manifest.header.$field) {
                Add-Error "[$Type] Missing header.$field"
            }
        }

        # Check min_engine_version
        if ($manifest.header.min_engine_version) {
            $ver = $manifest.header.min_engine_version
            if ($ver.Count -ge 3) {
                if ($ver[0] -lt 1 -or $ver[1] -lt 26 -or $ver[2] -lt 60) {
                    Add-Warning "[$Type] min_engine_version [$($ver -join '.')] may be too low for v26.60 features"
                } else {
                    Add-Ok "[$Type] min_engine_version: [$($ver -join '.')]"
                }
            }
        }

        # Check modules
        if (-not $manifest.modules -or $manifest.modules.Count -eq 0) {
            Add-Error "[$Type] No modules defined"
        } else {
            foreach ($mod in $manifest.modules) {
                if (-not $mod.type) { Add-Error "[$Type] Module missing type" }
                if (-not $mod.uuid) { Add-Error "[$Type] Module missing uuid" }
                if ($mod.version -and $mod.version.Count -lt 3) { Add-Warning "[$Type] Module version should have 3 parts" }
            }
        }

        # Type-specific checks
        if ($Type -eq "resource_pack") {
            $hasResources = $manifest.modules | Where-Object { $_.type -eq "resources" }
            if (-not $hasResources) { Add-Error "[$Type] No 'resources' type module" }
        } elseif ($Type -eq "behavior_pack") {
            $hasScript = $manifest.modules | Where-Object { $_.type -in @("data", "script") }
            if (-not $hasScript) { Add-Warning "[$Type] No 'script' or 'data' type module" }

            # Check dependencies
            if ($manifest.dependencies) {
                foreach ($dep in $manifest.dependencies) {
                    if ($dep.module_name -like "@minecraft/*") {
                        Add-Ok "[$Type] Dependency: $($dep.module_name)@$($dep.version)"
                    }
                }
            }
        }

        Add-Ok "[$Type] Manifest structure valid"
    } catch {
        Add-Error "[$Type] Invalid JSON: $_"
    }
}

Validate-Manifest $rpManifest "resource_pack"
Validate-Manifest $bpManifest "behavior_pack"

# ========================================================================
# Validate Behavior Pack Scripts
# ========================================================================
Write-Log "Validating behavior pack scripts..." "CHECK"

$scriptsDir = Join-Path $scriptDir "templates\behavior-pack\scripts"
if (Test-Path $scriptsDir) {
    $jsFiles = Get-ChildItem $scriptsDir -Filter "*.js" -Recurse
    foreach ($jsFile in $jsFiles) {
        # Basic syntax check using node
        $result = node --check $jsFile.FullName 2>&1
        if ($LASTEXITCODE -eq 0) {
            Add-Ok "Script syntax OK: $($jsFile.Name)"
        } else {
            Add-Error "Script syntax error in $($jsFile.Name): $result"
        }

        # Check for common issues
        $content = Get-Content $jsFile.FullName -Raw
        if ($content -notmatch 'import.*from\s+"@minecraft/server"') {
            Add-Warning "[$($jsFile.Name)] May be missing @minecraft/server import"
        }
        if ($content -notmatch 'import.*from\s+"@minecraft/server-ui"') {
            Add-Warning "[$($jsFile.Name)] May be missing @minecraft/server-ui import"
        }
    }
} else {
    Add-Warning "Scripts directory not found: $scriptsDir"
}

# ========================================================================
# Validate Resource Pack Structure
# ========================================================================
Write-Log "Validating resource pack structure..." "CHECK"

$rpDirs = @("sounds", "textures", "models", "animations", "particles")
foreach ($dir in $rpDirs) {
    $path = Join-Path $scriptDir "templates\resource-pack\$dir"
    if (Test-Path $path) {
        Add-Ok "Resource pack directory exists: $dir"
    } else {
        Add-Warning "Resource pack directory missing: $dir"
    }
}

# Check sounds.json
$soundsJson = Join-Path $scriptDir "templates\resource-pack\sounds.json"
if (Test-Path $soundsJson) {
    try {
        $sounds = Get-Content $soundsJson -Raw | ConvertFrom-Json
        foreach ($sound in $sounds.PSObject.Properties) {
            Add-Ok "Sound defined: $($sound.Name)"
        }
    } catch {
        Add-Error "Invalid sounds.json: $_"
    }
} else {
    Add-Warning "sounds.json not found"
}

# ========================================================================
# Validate Config Schema
# ========================================================================
Write-Log "Validating config schema..." "CHECK"

$schemaFile = Join-Path $scriptDir "config\birthday.json"
if (Test-Path $schemaFile) {
    try {
        $schema = Get-Content $schemaFile -Raw | ConvertFrom-Json
        if ($schema.title -and $schema.properties) {
            Add-Ok "Config schema valid"
        } else {
            Add-Warning "Config schema may be incomplete"
        }
    } catch {
        Add-Error "Invalid config schema JSON: $_"
    }
} else {
    Add-Warning "Config schema not found: $schemaFile"
}

# ========================================================================
# Validate Personal Config (if specified)
# ========================================================================
if ($ConfigName) {
    Write-Log "Validating personal config: $ConfigName..." "CHECK"
    $personalConfig = Join-Path $scriptDir "config\birthday-$ConfigName.json"
    if (Test-Path $personalConfig) {
        try {
            $config = Get-Content $personalConfig -Raw | ConvertFrom-Json

            # Check required fields
            if (-not $config.birthdayPerson -or -not $config.birthdayPerson.name) {
                Add-Error "Missing birthdayPerson.name"
            } else {
                Add-Ok "Birthday person: $($config.birthdayPerson.name)"
            }
            if (-not $config.birthdayPerson.age) {
                Add-Error "Missing birthdayPerson.age"
            } else {
                Add-Ok "Age: $($config.birthdayPerson.age)"
            }
            if (-not $config.world -or -not $config.world.title) {
                Add-Error "Missing world.title"
            } else {
                Add-Ok "World title: $($config.world.title)"
            }

            # Check personal assets paths
            if ($config.personalAssets) {
                if ($config.personalAssets.photosDirectory) {
                    if (Test-Path $config.personalAssets.photosDirectory) {
                        $photoCount = (Get-ChildItem $config.personalAssets.photosDirectory -Filter *.jpg, *.png, *.jpeg).Count
                        Add-Ok "Photos directory exists: $photoCount photos"
                    } else {
                        Add-Error "Photos directory not found: $($config.personalAssets.photosDirectory)"
                    }
                }
                if ($config.personalAssets.voiceMessagePath) {
                    if (Test-Path $config.personalAssets.voiceMessagePath) {
                        Add-Ok "Voice message exists"
                    } else {
                        Add-Error "Voice message not found: $($config.personalAssets.voiceMessagePath)"
                    }
                }
            }
        } catch {
            Add-Error "Invalid personal config JSON: $_"
        }
    } else {
        Add-Error "Personal config not found: $personalConfig"
    }
}

# ========================================================================
# Validate .mcworld (if specified or from config)
# ========================================================================
$mcworldToValidate = $McworldPath
if (-not $mcworldToValidate -and $ConfigName) {
    $mcworldToValidate = Join-Path $scriptDir "private-builds\Happy_Birthday_$ConfigName.mcworld"
}

if ($mcworldToValidate -and (Test-Path $mcworldToValidate)) {
    Write-Log "Validating .mcworld: $mcworldToValidate..." "CHECK"

    $packScript = Join-Path $scriptDir "src\packaging\build_mcworld.py"
    if (Test-Path $packScript) {
        $result = python $packScript validate -f $mcworldToValidate 2>&1
        if ($LASTEXITCODE -eq 0) {
            Add-Ok ".mcworld validation passed"
        } else {
            foreach ($line in $result) {
                if ($line -match "error|Error|ERROR") {
                    Add-Error ".mcworld: $line"
                } else {
                    Add-Warning ".mcworld: $line"
                }
            }
        }
    }

    # Check file size
    $sizeMB = [math]::Round((Get-Item $mcworldToValidate).Length / 1MB, 2)
    Add-Ok ".mcworld size: $sizeMB MB"
    if ($sizeMB -gt 100) {
        Add-Warning ".mcworld is large ($sizeMB MB) - may affect import performance"
    }
} elseif ($mcworldToValidate) {
    Add-Warning ".mcworld file not found: $mcworldToValidate"
}

# ========================================================================
# Validate Python Scripts
# ========================================================================
Write-Log "Validating Python scripts..." "CHECK"

$pyDirs = @(
    "src\photo-processing",
    "src\generators",
    "src\packaging"
)

foreach ($pyDir in $pyDirs) {
    $fullPath = Join-Path $scriptDir $pyDir
    if (Test-Path $fullPath) {
        $pyFiles = Get-ChildItem $fullPath -Filter "*.py" -Recurse
        foreach ($pyFile in $pyFiles) {
            $result = python -m py_compile $pyFile.FullName 2>&1
            if ($LASTEXITCODE -eq 0) {
                Add-Ok "Python syntax OK: $($pyFile.Name)"
            } else {
                Add-Error "Python syntax error in $($pyFile.Name): $result"
            }
        }
    }
}

# ========================================================================
# Check .gitignore
# ========================================================================
Write-Log "Checking .gitignore..." "CHECK"
$gitignore = Join-Path $scriptDir ".gitignore"
if (Test-Path $gitignore) {
    $content = Get-Content $gitignore -Raw
    $requiredPatterns = @(
        "private-assets/",
        "private-builds/",
        "personal-config/",
        "*.mcworld",
        "config/birthday-*.json"
    )
    foreach ($pattern in $requiredPatterns) {
        if ($content -match [regex]::Escape($pattern).Replace('\*', '.*')) {
            Add-Ok ".gitignore contains: $pattern"
        } else {
            Add-Warning ".gitignore missing pattern: $pattern"
        }
    }
} else {
    Add-Error ".gitignore not found"
}

# ========================================================================
# Summary
# ========================================================================
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗"
Write-Host "║     Validation Summary                                       ║"
Write-Host "╚══════════════════════════════════════════════════════════════╝"
Write-Host ""
Write-Host "Errors:   $errors"
Write-Host "Warnings: $warnings"
Write-Host ""

if ($errors -gt 0) {
    Write-Log "VALIDATION FAILED - $errors error(s) found" "ERROR"
    exit 1
} elseif ($warnings -gt 0 -and $Strict) {
    Write-Log "VALIDATION FAILED - $warnings warning(s) treated as errors (strict mode)" "ERROR"
    exit 1
} elseif ($warnings -gt 0) {
    Write-Log "VALIDATION PASSED WITH WARNINGS" "WARN"
    exit 0
} else {
    Write-Log "VALIDATION PASSED - All checks OK" "OK"
    exit 0
}
<#
.SYNOPSIS
    Setup script for bedrock-birthday-worlds repository.
    Installs dependencies, creates directory structure, and prepares the environment.

.DESCRIPTION
    This script sets up the development environment for creating personalized
    Minecraft Bedrock birthday worlds. It installs required Python packages,
    validates the toolchain, and creates necessary directories.

.NOTES
    Run this script once after cloning the repository.
    Requires: Python 3.8+, Node.js 18+, Git
#>

param(
    [switch]$InstallPythonPackages,
    [switch]$InstallNodePackages,
    [switch]$SkipValidation,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $prefix = switch ($Level) {
        "ERROR" { "❌" }
        "WARN"  { "⚠️" }
        "OK"    { "✅" }
        default { "ℹ️" }
    }
    Write-Host "[$timestamp] $prefix $Message"
}

function Test-Command {
    param([string]$Command, [string]$Name, [string]$VersionFlag = "--version")
    try {
        $result = & $Command $VersionFlag 2>&1 | Select-Object -First 1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "$Name found: $result" "OK"
            return $true
        }
    } catch {
        Write-Log "$Name not found" "ERROR"
    }
    return $false
}

Write-Host "╔══════════════════════════════════════════════════════════════╗"
Write-Host "║     bedrock-birthday-worlds - Environment Setup             ║"
Write-Host "╚══════════════════════════════════════════════════════════════╝"
Write-Host ""

# Check required tools
Write-Log "Checking required tools..."
$toolsOk = $true
$toolsOk = Test-Command "python" "Python" "-V" -and $toolsOk
$toolsOk = Test-Command "node" "Node.js" "-v" -and $toolsOk
$toolsOk = Test-Command "npm" "npm" "-v" -and $toolsOk
$toolsOk = Test-Command "git" "Git" "--version" -and $toolsOk
$toolsOk = Test-Command "gh" "GitHub CLI" "--version" -and $toolsOk

if (-not $toolsOk -and -not $SkipValidation) {
    Write-Log "Some required tools are missing. Install them and re-run." "ERROR"
    exit 1
}

# Create directory structure
Write-Log "Creating directory structure..."
$dirs = @(
    "config",
    "templates/resource-pack/sounds",
    "templates/resource-pack/textures/items",
    "templates/resource-pack/textures/blocks",
    "templates/resource-pack/textures/ui",
    "templates/resource-pack/models",
    "templates/resource-pack/animations",
    "templates/resource-pack/particles",
    "templates/resource-pack/textures/font",
    "templates/behavior-pack/scripts",
    "src/world",
    "src/scripts",
    "src/generators",
    "src/photo-processing",
    "src/packaging",
    "assets/generic",
    "examples",
    "tests",
    "tools",
    "scripts",
    "docs",
    ".github/workflows",
    "private-assets/photos",
    "private-assets/audio",
    "private-builds"
)

foreach ($dir in $dirs) {
    $fullPath = Join-Path $PSScriptRoot "..\$dir"
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        if ($Verbose) { Write-Log "Created: $dir" }
    }
}

# Install Python packages
if ($InstallPythonPackages) {
    Write-Log "Installing Python packages..."
    $packages = @(
        "pillow>=10.0.0",
        "numpy>=1.24.0",
        "moviepy>=1.0.0",
        "pydub>=0.25.0"
    )
    foreach ($pkg in $packages) {
        Write-Log "Installing $pkg..."
        python -m pip install $pkg
    }
    Write-Log "Python packages installed" "OK"
}

# Install Node packages
if ($InstallNodePackages) {
    Write-Log "Installing Node.js packages..."
    $packageJson = Join-Path $PSScriptRoot "..\package.json"
    if (Test-Path $packageJson) {
        npm install --prefix (Split-Path $packageJson)
    } else {
        # Create minimal package.json
        $pkg = @{
            name = "bedrock-birthday-worlds"
            version = "1.0.0"
            description = "Birthday world generator for Minecraft Bedrock"
            scripts = @{
                build = "node scripts/build.js"
                test = "node scripts/test.js"
            }
            devDependencies = @{
                "typescript" = "^5.0.0"
                "@types/node" = "^20.0.0"
            }
        } | ConvertTo-Json -Depth 4
        $pkg | Out-File -FilePath $packageJson -Encoding utf8
        npm install --prefix (Split-Path $packageJson)
    }
    Write-Log "Node packages installed" "OK"
}

# Validate Python packages
Write-Log "Validating Python imports..."
try {
    python -c "import PIL; print('Pillow:', PIL.__version__)"
    python -c "import numpy; print('NumPy:', numpy.__version__)"
    python -c "import moviepy; print('MoviePy:', moviepy.__version__)"
    python -c "import pydub; print('Pydub:', pydub.__version__)"
    Write-Log "All Python packages validated" "OK"
} catch {
    Write-Log "Some Python packages failed to import" "WARN"
}

# Check for ffmpeg (needed for audio conversion)
Write-Log "Checking for ffmpeg..."
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Log "ffmpeg found" "OK"
} else {
    Write-Log "ffmpeg not found - needed for audio conversion" "WARN"
    Write-Log "Install with: winget install ffmpeg (or download from ffmpeg.org)"
}

# Check for ImageMagick
Write-Log "Checking for ImageMagick..."
if (Get-Command magick -ErrorAction SilentlyContinue) {
    Write-Log "ImageMagick (magick) found" "OK"
} elseif (Get-Command convert -ErrorAction SilentlyContinue) {
    Write-Log "ImageMagick (convert) found" "OK"
} else {
    Write-Log "ImageMagick not found - optional for image processing" "WARN"
}

# Create .gitignore if not exists
$gitignore = Join-Path $PSScriptRoot "..\.gitignore"
if (-not (Test-Path $gitignore)) {
    Write-Log "Creating .gitignore..."
    @"
# Private assets - NEVER COMMIT THESE
private-assets/
private-builds/
personal-config/
*.mcworld

# Personal configuration
config/birthday-*.json
!config/birthday.json
!config/birthday.schema.json

# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
venv/
env/
.env

# Node
node_modules/
npm-debug.log*

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build outputs
build/
dist/
*.zip
"@ | Out-File -FilePath $gitignore -Encoding utf8
    Write-Log ".gitignore created" "OK"
}

# Create placeholder template files if missing
Write-Log "Checking template files..."

# Resource pack manifest
$rpManifest = Join-Path $PSScriptRoot "..\templates\resource-pack\manifest.json"
if (-not (Test-Path $rpManifest)) {
    @"
{
  "format_version": 2,
  "header": {
    "description": "Birthday World Resource Pack - Custom textures, sounds, and models",
    "name": "Birthday World Resources",
    "uuid": "REPLACE_WITH_RESOURCE_PACK_UUID",
    "version": [1, 0, 0],
    "min_engine_version": [1, 26, 60]
  },
  "modules": [
    {
      "description": "Birthday World Resources",
      "type": "resources",
      "uuid": "REPLACE_WITH_RESOURCE_PACK_MODULE_UUID",
      "version": [1, 0, 0]
    }
  ]
}
"@ | Out-File -FilePath $rpManifest -Encoding utf8
}

# Behavior pack manifest
$bpManifest = Join-Path $PSScriptRoot "..\templates\behavior-pack\manifest.json"
if (-not (Test-Path $bpManifest)) {
    @"
{
  "format_version": 2,
  "header": {
    "description": "Birthday World Behavior Pack - Custom scripts and gameplay logic",
    "name": "Birthday World Behavior",
    "uuid": "REPLACE_WITH_BEHAVIOR_PACK_UUID",
    "version": [1, 0, 0],
    "min_engine_version": [1, 26, 60]
  },
  "modules": [
    {
      "description": "Birthday World Scripts",
      "type": "script",
      "uuid": "REPLACE_WITH_BEHAVIOR_PACK_MODULE_UUID",
      "version": [1, 0, 0],
      "entry": "scripts/main.js"
    }
  ],
  "dependencies": [
    {
      "module_name": "@minecraft/server",
      "version": "1.17.0"
    },
    {
      "module_name": "@minecraft/server-ui",
      "version": "1.4.0"
    }
  ]
}
"@ | Out-File -FilePath $bpManifest -Encoding utf8
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗"
Write-Host "║     Setup Complete!                                          ║"
Write-Host "╚══════════════════════════════════════════════════════════════╝"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Copy your photos to: private-assets/photos/"
Write-Host "  2. Copy your voice message (.ogg) to: private-assets/audio/"
Write-Host "  3. Copy config/birthday.json to config/birthday-<name>.json and edit it"
Write-Host "  4. Run: .\scripts\build.ps1"
Write-Host ""
Write-Host "For help: .\scripts\build.ps1 -Help"
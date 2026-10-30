<#
.SYNOPSIS
    Package script for bedrock-birthday-worlds.
    Creates distribution packages and prepares releases.

.DESCRIPTION
    This script creates release packages:
    - Source code archive (for GitHub releases)
    - Template-only package (for users who want to build their own)
    - Documentation package
    - Verifies no private assets are included

.NOTES
    Run this before creating a GitHub release to ensure clean packaging.
#>

param(
    [string]$Version = "1.0.0",
    [string]$OutputDir = "dist",
    [switch]$IncludeTemplates,
    [switch]$IncludeDocs,
    [switch]$IncludeExamples,
    [switch]$VerifyOnly,
    [switch]$Verbose,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $prefix = switch ($Level) {
        "ERROR" { "❌" }
        "WARN"  { "⚠️" }
        "OK"    { "✅" }
        "STEP"  { "📦" }
        default { "ℹ️" }
    }
    Write-Host "[$timestamp] $prefix $Message"
}

function Show-Help {
    @"
Usage: .\scripts\package.ps1 [Options]

Options:
  -Version <ver>        Version string for package (default: 1.0.0)
  -OutputDir <dir>      Output directory (default: dist)
  -IncludeTemplates     Include template packs in package
  -IncludeDocs          Include documentation
  -IncludeExamples      Include example configurations
  -VerifyOnly           Only verify no private assets would be included
  -Verbose              Verbose output
  -Help                 Show this help

Examples:
  .\scripts\package.ps1 -Version 1.0.0 -IncludeTemplates -IncludeDocs
  .\scripts\package.ps1 -VerifyOnly
"@
}

if ($Help) {
    Show-Help
    exit 0
}

$scriptDir = Split-Path $PSScriptRoot
$distDir = Join-Path $scriptDir $OutputDir

Write-Host "╔══════════════════════════════════════════════════════════════╗"
Write-Host "║     Packaging: bedrock-birthday-worlds v$Version"
Write-Host "╚══════════════════════════════════════════════════════════════╝"

# Clean and create dist directory
if (Test-Path $distDir) { Remove-Item $distDir -Recurse -Force }
New-Item -ItemType Directory -Path $distDir -Force | Out-Null

# ========================================================================
# VERIFICATION: Check for private assets that must NOT be included
# ========================================================================
Write-Log "Verifying no private assets in repository..." "STEP"

$privatePatterns = @(
    "private-assets/**",
    "private-builds/**",
    "personal-config/**",
    "*.mcworld",
    "config/birthday-*.json",
    "pics/**",
    "audio/**",
    "*.ogg",
    "*.mp4",
    "*.mp3",
    "*.wav"
)

$foundPrivate = $false
foreach ($pattern in $privatePatterns) {
    $matches = Get-ChildItem $scriptDir -Recurse -Filter $pattern.Split('/')[-1] -ErrorAction SilentlyContinue |
               Where-Object { $_.FullName -like "*$($pattern.Replace('**','*'))*" }
    if ($matches) {
        foreach ($m in $matches) {
            # Check if it's in a private directory
            $relPath = $m.FullName.Substring($scriptDir.Length + 1)
            if ($relPath -match "^(private-assets|private-builds|personal-config|pics|audio)/") {
                Write-Log "PRIVATE FILE FOUND: $relPath" "ERROR"
                $foundPrivate = $true
            }
        }
    }
}

if ($foundPrivate) {
    Write-Log "Private assets found in repository! Aborting package." "ERROR"
    exit 1
} else {
    Write-Log "No private assets found in repository" "OK"
}

if ($VerifyOnly) {
    Write-Log "Verification complete - no private assets detected" "OK"
    exit 0
}

# ========================================================================
# CREATE SOURCE ARCHIVE
# ========================================================================
Write-Log "Creating source archive..." "STEP"

$sourceArchive = Join-Path $distDir "bedrock-birthday-worlds-$Version-source.zip"
$excludePatterns = @(
    "private-assets",
    "private-builds",
    "personal-config",
    "*.mcworld",
    "config/birthday-*.json",
    "pics",
    "audio",
    "__pycache__",
    ".py[cod]",
    "node_modules",
    ".git",
    ".vscode",
    ".idea",
    "*.swp",
    "*.swo",
    ".DS_Store",
    "Thumbs.db",
    "dist"
)

# Use PowerShell to create zip with exclusions
$filesToInclude = Get-ChildItem $scriptDir -Recurse -File |
    Where-Object {
        $rel = $_.FullName.Substring($scriptDir.Length + 1)
        $excluded = $false
        foreach ($pat in $excludePatterns) {
            if ($rel -like $pat -or $rel -like "$pat/*") { $excluded = $true; break }
            if ($pat -like "*/**") {
                $dirPat = $pat.Replace("/**", "")
                if ($rel -like "$dirPat/*") { $excluded = $true; break }
            }
        }
        -not $excluded
    }

# Create temp directory for zip
$tempZipDir = Join-Path $env:TEMP "bdw_package_$([guid]::NewGuid())"
New-Item -ItemType Directory -Path $tempZipDir -Force | Out-Null

try {
    foreach ($file in $filesToInclude) {
        $rel = $file.FullName.Substring($scriptDir.Length + 1)
        $dest = Join-Path $tempZipDir $rel
        $destDir = Split-Path $dest
        if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
        Copy-Item $file.FullName $dest -Force
    }

    # Create zip
    Compress-Archive -Path (Join-Path $tempZipDir "*") -DestinationPath $sourceArchive -Force
    Write-Log "Created source archive: $sourceArchive" "OK"
} finally {
    if (Test-Path $tempZipDir) { Remove-Item $tempZipDir -Recurse -Force }
}

# ========================================================================
# CREATE TEMPLATE PACKAGE
# ========================================================================
if ($IncludeTemplates) {
    Write-Log "Creating template package..." "STEP"

    $templateArchive = Join-Path $distDir "bedrock-birthday-worlds-$Version-templates.zip"
    $templateDirs = @(
        "templates",
        "src",
        "scripts",
        "config/birthday.json",
        "config/birthday.schema.json",
        "docs",
        "README.md",
        "LICENSE",
        ".gitignore"
    )

    $templateTempDir = Join-Path $env:TEMP "bdw_templates_$([guid]::NewGuid())"
    New-Item -ItemType Directory -Path $templateTempDir -Force | Out-Null

    try {
        foreach ($td in $templateDirs) {
            $src = Join-Path $scriptDir $td
            if (Test-Path $src) {
                $dest = Join-Path $templateTempDir $td
                $destDir = Split-Path $dest
                if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
                Copy-Item $src $dest -Recurse -Force -ErrorAction SilentlyContinue
            }
        }

        Compress-Archive -Path (Join-Path $templateTempDir "*") -DestinationPath $templateArchive -Force
        Write-Log "Created template package: $templateArchive" "OK"
    } finally {
        if (Test-Path $templateTempDir) { Remove-Item $templateTempDir -Recurse -Force }
    }
}

# ========================================================================
# CREATE DOCS PACKAGE
# ========================================================================
if ($IncludeDocs) {
    Write-Log "Creating documentation package..." "STEP"

    $docsArchive = Join-Path $distDir "bedrock-birthday-worlds-$Version-docs.zip"
    $docsTempDir = Join-Path $env:TEMP "bdw_docs_$([guid]::NewGuid())"
    New-Item -ItemType Directory -Path $docsTempDir -Force | Out-Null

    try {
        $docFiles = @("docs", "README.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md", "CHANGELOG.md")
        foreach ($df in $docFiles) {
            $src = Join-Path $scriptDir $df
            if (Test-Path $src) {
                Copy-Item $src (Join-Path $templateTempDir $df) -Recurse -Force -ErrorAction SilentlyContinue
            }
        }

        Compress-Archive -Path (Join-Path $docsTempDir "*") -DestinationPath $docsArchive -Force
        Write-Log "Created docs package: $docsArchive" "OK"
    } finally {
        if (Test-Path $docsTempDir) { Remove-Item $docsTempDir -Recurse -Force }
    }
}

# ========================================================================
# CREATE EXAMPLES PACKAGE
# ========================================================================
if ($IncludeExamples) {
    Write-Log "Creating examples package..." "STEP"

    $examplesArchive = Join-Path $distDir "bedrock-birthday-worlds-$Version-examples.zip"
    $examplesDir = Join-Path $scriptDir "examples"

    if (Test-Path $examplesDir) {
        Compress-Archive -Path (Join-Path $examplesDir "*") -DestinationPath $examplesArchive -Force
        Write-Log "Created examples package: $examplesArchive" "OK"
    } else {
        Write-Log "Examples directory not found, skipping" "WARN"
    }
}

# ========================================================================
# GENERATE CHECKSUMS
# ========================================================================
Write-Log "Generating checksums..." "STEP"

$checksumFile = Join-Path $distDir "checksums.txt"
$archives = Get-ChildItem $distDir -Filter "*.zip"
foreach ($archive in $archives) {
    $sha256 = Get-FileHash $archive.FullName -Algorithm SHA256
    "$($sha256.Hash)  $($archive.Name)" | Out-File -FilePath $checksumFile -Encoding utf8 -Append
}
Write-Log "Checksums written to $checksumFile" "OK"

# ========================================================================
# SUMMARY
# ========================================================================
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗"
Write-Host "║     Packaging Complete                                       ║"
Write-Host "╚══════════════════════════════════════════════════════════════╝"
Write-Host ""
Get-ChildItem $distDir | ForEach-Object {
    $sizeMB = [math]::Round($_.Length / 1MB, 2)
    Write-Host "  $($_.Name) ($sizeMB MB)"
}
Write-Host ""
Write-Host "Output directory: $distDir"
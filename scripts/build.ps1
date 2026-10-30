<#
.SYNOPSIS
    Build script for bedrock-birthday-worlds.
    Generates personalized .mcworld file from configuration and assets.

.DESCRIPTION
    This script orchestrates the complete build pipeline:
    1. Validates configuration
    2. Processes photos to pixel art / map art
    3. Converts audio to .ogg format
    4. Generates world structures
    5. Builds resource and behavior packs
    6. Packages everything into a .mcworld file

.NOTES
    Requires: Personal assets in private-assets/ and config in config/birthday-<name>.json
    Run setup.ps1 first to prepare environment.
#>

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$ConfigName,  # e.g., "ujan" for config/birthday-ujan.json

    [string]$OutputName = "",  # Optional custom output filename

    [switch]$SkipPhotos,
    [switch]$SkipAudio,
    [switch]$SkipWorldGen,
    [switch]$SkipPackBuild,
    [switch]$CleanOnly,
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
        "STEP"  { "🔨" }
        default { "ℹ️" }
    }
    Write-Host "[$timestamp] $prefix $Message"
}

function Show-Help {
    @"
Usage: .\scripts\build.ps1 <ConfigName> [Options]

Arguments:
  ConfigName    Name of config file (without extension), e.g., "ujan" loads config/birthday-ujan.json

Options:
  -OutputName <name>    Custom output filename (default: Happy_Birthday_<Name>.mcworld)
  -SkipPhotos           Skip photo processing step
  -SkipAudio            Skip audio conversion step
  -SkipWorldGen         Skip world structure generation
  -SkipPackBuild        Skip pack building step
  -CleanOnly            Only clean build directories
  -Verbose              Verbose output
  -Help                 Show this help

Examples:
  .\scripts\build.ps1 ujan
  .\scripts\build.ps1 ujan -OutputName "Ujan_14th_Birthday.mcworld"
  .\scripts\build.ps1 ujan -SkipPhotos -Verbose
"@
}

if ($Help) {
    Show-Help
    exit 0
}

$scriptDir = Split-Path $PSScriptRoot
$configFile = Join-Path $scriptDir "config\birthday-$ConfigName.json"

if (-not (Test-Path $configFile)) {
    Write-Log "Config file not found: $configFile" "ERROR"
    Write-Log "Available configs:" "INFO"
    Get-ChildItem (Join-Path $scriptDir "config") -Filter "birthday-*.json" | ForEach-Object {
        Write-Log "  $($_.BaseName.Replace('birthday-',''))"
    }
    exit 1
}

Write-Log "Loading configuration from $configFile"
$config = Get-Content $configFile -Raw | ConvertFrom-Json

$personName = $config.birthdayPerson.name
$personAge = $config.birthdayPerson.age
$worldTitle = $config.world.title
$worldDesc = $config.world.description

if (-not $OutputName) {
    $OutputName = "Happy_Birthday_$personName.mcworld"
}

$outputPath = Join-Path $scriptDir "private-builds\$OutputName"
$buildDir = Join-Path $scriptDir "private-builds\.build_$ConfigName"

Write-Host "╔══════════════════════════════════════════════════════════════╗"
Write-Host "║     Building: $OutputName"
Write-Host "║     For: $personName (Age $personAge)"
Write-Host "╚══════════════════════════════════════════════════════════════╝"

if ($CleanOnly) {
    Write-Log "Cleaning build directories..."
    if (Test-Path $buildDir) { Remove-Item $buildDir -Recurse -Force }
    if (Test-Path $outputPath) { Remove-Item $outputPath -Force }
    Write-Log "Clean complete" "OK"
    exit 0
}

# Clean previous build
if (Test-Path $buildDir) {
    Write-Log "Cleaning previous build..."
    Remove-Item $buildDir -Recurse -Force
}
New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $buildDir "world") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $buildDir "resource_pack") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $buildDir "behavior_pack") -Force | Out-Null

# ========================================================================
# STEP 1: Process Photos
# ========================================================================
if (-not $SkipPhotos) {
    Write-Log "STEP 1: Processing photos to pixel art..." "STEP"

    $photosDir = $config.personalAssets.photosDirectory
    if (-not (Test-Path $photosDir)) {
        Write-Log "Photos directory not found: $photosDir" "WARN"
    } else {
        $photoOutput = Join-Path $buildDir "pixel_art"
        $photoScript = Join-Path $scriptDir "src\photo-processing\photo_to_pixel_art.py"

        if (Test-Path $photoScript) {
            $args = @(
                "-i", $photosDir
                "-o", $photoOutput
                "-W", "128"
                "-H", "128"
                "-p", "extended"
                "-m", $config.gallery.maxPhotos
                "--orientation", "vertical"
            )

            Write-Log "Running photo_to_pixel_art.py..."
            python $photoScript @args

            if ($LASTEXITCODE -ne 0) {
                Write-Log "Photo processing failed" "ERROR"
                exit 1
            }
            Write-Log "Photo processing complete" "OK"
        } else {
            Write-Log "Photo processing script not found: $photoScript" "WARN"
        }
    }
} else {
    Write-Log "Skipping photo processing" "INFO"
}

# ========================================================================
# STEP 2: Convert Audio
# ========================================================================
if (-not $SkipAudio -and $config.audio.enabled) {
    Write-Log "STEP 2: Converting audio to .ogg..." "STEP"

    $audioInput = $config.personalAssets.voiceMessagePath
    $audioOutputDir = Join-Path $buildDir "resource_pack\sounds"

    if (Test-Path $audioInput) {
        New-Item -ItemType Directory -Path $audioOutputDir -Force | Out-Null
        $audioOutput = Join-Path $audioOutputDir "birthday_message.ogg"

        Write-Log "Converting $audioInput to $audioOutput..."
        python -c "
from moviepy import AudioFileClip
clip = AudioFileClip(r'$audioInput')
clip.write_audiofile(r'$audioOutput', codec='libvorbis')
print('Conversion complete')
"
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Audio conversion failed" "ERROR"
            exit 1
        }
        Write-Log "Audio conversion complete" "OK"
    } else {
        Write-Log "Voice message not found: $audioInput" "WARN"
        Write-Log "Creating silent placeholder..."
        # Create a minimal .ogg file as placeholder
        python -c "
import wave, struct
import subprocess
# Create a short silent wav then convert
with wave.open(r'$audioOutputDir\temp.wav', 'w') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(44100)
    w.writeframes(struct.pack('<h', 0) * 44100)
subprocess.run(['ffmpeg', '-y', '-i', r'$audioOutputDir\temp.wav', '-c:a', 'libvorbis', r'$audioOutput'], capture_output=True)
import os
os.remove(r'$audioOutputDir\temp.wav')
"
    }
} else {
    Write-Log "Skipping audio conversion" "INFO"
}

# ========================================================================
# STEP 3: Generate World Structures
# ========================================================================
if (-not $SkipWorldGen) {
    Write-Log "STEP 3: Generating world structures..." "STEP"

    $worldGenScript = Join-Path $scriptDir "src\generators\world_generator.py"
    $worldOutput = Join-Path $buildDir "world_structures"

    if (Test-Path $worldGenScript) {
        $args = @(
            "-o", $worldOutput
        )
        if ($configFile) { $args += @("--config", $configFile) }

        Write-Log "Running world_generator.py..."
        python $worldGenScript @args

        if ($LASTEXITCODE -ne 0) {
            Write-Log "World generation failed" "ERROR"
            exit 1
        }
        Write-Log "World generation complete" "OK"
    } else {
        Write-Log "World generator script not found: $worldGenScript" "WARN"
    }
} else {
    Write-Log "Skipping world generation" "INFO"
}

# ========================================================================
# STEP 4: Build Resource Pack
# ========================================================================
if (-not $SkipPackBuild) {
    Write-Log "STEP 4: Building resource pack..." "STEP"

    $rpSource = Join-Path $scriptDir "templates\resource-pack"
    $rpDest = Join-Path $buildDir "resource_pack"

    # Copy template
    Copy-Item -Path (Join-Path $rpSource "*") -Destination $rpDest -Recurse -Force

    # Update manifest with config-specific info
    $rpManifest = Join-Path $rpDest "manifest.json"
    if (Test-Path $rpManifest) {
        $manifest = Get-Content $rpManifest -Raw | ConvertFrom-Json
        $manifest.header.name = "Birthday World Resources - $personName"
        $manifest.header.description = "Custom resources for $personName's $personAge`th birthday world"
        $manifest.header.uuid = [guid]::NewGuid().ToString()
        $manifest.modules[0].uuid = [guid]::NewGuid().ToString()
        $manifest | ConvertTo-Json -Depth 5 | Out-File -FilePath $rpManifest -Encoding utf8
    }

    # Copy generated pixel art textures
    $pixelArtSource = Join-Path $buildDir "pixel_art"
    if (Test-Path $pixelArtSource) {
        $texturesDest = Join-Path $rpDest "textures\pixel_art"
        New-Item -ItemType Directory -Path $texturesDest -Force | Out-Null
        Copy-Item -Path (Join-Path $pixelArtSource "*_preview.png") -Destination $texturesDest -Force
        Write-Log "Copied pixel art textures to resource pack"
    }

    # Copy audio
    $audioSource = Join-Path $buildDir "resource_pack\sounds"
    if (Test-Path $audioSource) {
        Copy-Item -Path (Join-Path $audioSource "*") -Destination (Join-Path $rpDest "sounds") -Force
    }

    # Create pack icon
    try {
        python -c "
from PIL import Image, ImageDraw
img = Image.new('RGBA', (128, 128), (70, 130, 180, 255))
draw = ImageDraw.Draw(img)
draw.text((10, 50), '$personName', fill=(255, 255, 255, 255))
draw.text((10, 70), 'Age $personAge', fill=(255, 215, 0, 255))
img.save(r'$rpDest\pack_icon.png', 'PNG')
"
    } catch {
        Write-Log "Could not create pack icon (Pillow not available)" "WARN"
    }

    Write-Log "Resource pack built at $rpDest" "OK"
} else {
    Write-Log "Skipping resource pack build" "INFO"
}

# ========================================================================
# STEP 5: Build Behavior Pack
# ========================================================================
if (-not $SkipPackBuild) {
    Write-Log "STEP 5: Building behavior pack..." "STEP"

    $bpSource = Join-Path $scriptDir "templates\behavior-pack"
    $bpDest = Join-Path $buildDir "behavior_pack"

    # Copy template
    Copy-Item -Path (Join-Path $bpSource "*") -Destination $bpDest -Recurse -Force

    # Update manifest
    $bpManifest = Join-Path $bpDest "manifest.json"
    if (Test-Path $bpManifest) {
        $manifest = Get-Content $bpManifest -Raw | ConvertFrom-Json
        $manifest.header.name = "Birthday World Behavior - $personName"
        $manifest.header.description = "Custom scripts for $personName's $personAge`th birthday world"
        $manifest.header.uuid = [guid]::NewGuid().ToString()
        $manifest.modules[0].uuid = [guid]::NewGuid().ToString()
        $manifest | ConvertTo-Json -Depth 5 | Out-File -FilePath $bpManifest -Encoding utf8
    }

    # Inject config into main.js (replace placeholders)
    $mainJs = Join-Path $bpDest "scripts\main.js"
    if (Test-Path $mainJs) {
        $content = Get-Content $mainJs -Raw
        $content = $content -replace 'const CONFIG = \{', "const CONFIG = {
  birthdayPerson: `"$personName`",
  age: $personAge,"
        $content | Out-File -FilePath $mainJs -Encoding utf8
    }

    # Create pack icon
    try {
        python -c "
from PIL import Image, ImageDraw
img = Image.new('RGBA', (128, 128), (180, 70, 70, 255))
draw = ImageDraw.Draw(img)
draw.text((10, 50), '$personName', fill=(255, 255, 255, 255))
draw.text((10, 70), 'Behavior', fill=(255, 215, 0, 255))
img.save(r'$bpDest\pack_icon.png', 'PNG')
"
    } catch {
        Write-Log "Could not create pack icon" "WARN"
    }

    Write-Log "Behavior pack built at $bpDest" "OK"
} else {
    Write-Log "Skipping behavior pack build" "INFO"
}

# ========================================================================
# STEP 6: Package .mcworld
# ========================================================================
Write-Log "STEP 6: Packaging .mcworld file..." "STEP"

# Find a template world to use as base
$templateWorlds = @(
    "C:\Users\aryad\AppData\Roaming\Minecraft Bedrock\games\com.mojang\minecraftWorlds",
    Join-Path $scriptDir "world_template",
    Join-Path $env:APPDATA "Minecraft Bedrock\games\com.mojang\minecraftWorlds"
)

$templateWorld = $null
foreach ($tw in $templateWorlds) {
    if (Test-Path $tw) {
        $dirs = Get-ChildItem $tw -Directory | Where-Object { $_.Name -notmatch "^\." }
        if ($dirs.Count -gt 0) {
            $templateWorld = $dirs[0].FullName
            break
        }
    }
}

if (-not $templateWorld) {
    Write-Log "No template world found. Creating minimal world..." "WARN"
    # Create a minimal world using the build_mcworld.py script's capabilities
    $worldBuildDir = Join-Path $buildDir "world"
    # This would need a proper template - for now we'll use the packaging script
}

$packScript = Join-Path $scriptDir "src\packaging\build_mcworld.py"

if (Test-Path $packScript) {
    $rpDir = Join-Path $buildDir "resource_pack"
    $bpDir = Join-Path $buildDir "behavior_pack"
    $worldDir = $templateWorld

    if (-not $worldDir -or -not (Test-Path $worldDir)) {
        # Use a minimal world dir
        $worldDir = Join-Path $buildDir "world"
        New-Item -ItemType Directory -Path $worldDir -Force | Out-Null

        # Create minimal levelname.txt
        $worldTitle | Out-File -FilePath (Join-Path $worldDir "levelname.txt") -Encoding utf8
    }

    Write-Log "Running build_mcworld.py..."
    python $packScript build `
        -o $outputPath `
        -w $worldDir `
        -r $rpDir `
        -b $bpDir `
        -n $worldTitle

    if ($LASTEXITCODE -ne 0) {
        Write-Log "Packaging failed" "ERROR"
        exit 1
    }

    Write-Log "Successfully created $outputPath" "OK"
} else {
    Write-Log "Packaging script not found: $packScript" "ERROR"
    exit 1
}

# ========================================================================
# VALIDATE OUTPUT
# ========================================================================
Write-Log "Validating output..."
$errors = python $packScript validate -f $outputPath 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Log "Validation passed!" "OK"
} else {
    Write-Log "Validation warnings:" "WARN"
    Write-Host $errors
}

# Cleanup build directory
Write-Log "Cleaning up build directory..."
Remove-Item $buildDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗"
Write-Host "║     BUILD COMPLETE!                                          ║"
Write-Host "╚══════════════════════════════════════════════════════════════╝"
Write-Host ""
Write-Host "Output: $outputPath"
Write-Host ""
Write-Host "To install:"
Write-Host "  1. Double-click the .mcworld file"
Write-Host "  2. Minecraft Bedrock will open and import it"
Write-Host "  3. Select 'Happy Birthday $personName' from your worlds"
Write-Host ""
Write-Host "To test in a clean environment:"
Write-Host "  1. Copy .mcworld to another device"
Write-Host "  2. Import and verify all features work"
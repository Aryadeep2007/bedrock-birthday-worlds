#!/usr/bin/env python3
"""
Minecraft Bedrock .mcworld Package Builder

Builds a complete .mcworld file from:
- World directory (level.dat, db/, etc.)
- Resource pack directory
- Behavior pack directory

The output is a .mcworld file (ZIP archive) that can be imported into Minecraft Bedrock.

Requirements: Python 3.8+ (stdlib only)
"""

import argparse
import os
import zipfile
import json
import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import sys


def generate_uuid() -> str:
    """Generate a UUID for pack manifests."""
    return str(uuid.uuid4())


def read_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Read and parse a manifest.json file."""
    with open(manifest_path, 'r') as f:
        return json.load(f)


def write_manifest(manifest_path: Path, manifest: Dict[str, Any]):
    """Write a manifest.json file."""
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)


def update_manifest_uuids(manifest: Dict[str, Any], pack_type: str) -> Dict[str, Any]:
    """Update manifest with new UUIDs."""
    manifest = manifest.copy()

    # Header UUID
    manifest["header"]["uuid"] = generate_uuid()

    # Module UUIDs
    for module in manifest.get("modules", []):
        module["uuid"] = generate_uuid()

    return manifest


def validate_manifest(manifest: Dict[str, Any], pack_type: str) -> List[str]:
    """Validate manifest.json structure. Returns list of errors."""
    errors = []

    # Required fields
    required_header = ["description", "name", "uuid", "version", "min_engine_version"]
    required_module = ["description", "type", "uuid", "version"]

    for field in required_header:
        if field not in manifest.get("header", {}):
            errors.append(f"Missing header.{field}")

    if "modules" not in manifest or not manifest["modules"]:
        errors.append("Missing or empty modules array")
    else:
        for i, module in enumerate(manifest["modules"]):
            for field in required_module:
                if field not in module:
                    errors.append(f"Module {i}: missing {field}")

            # Type validation
            if pack_type == "resource_pack" and module.get("type") != "resources":
                errors.append(f"Module {i}: resource pack module type must be 'resources'")
            elif pack_type == "behavior_pack" and module.get("type") not in ("data", "script"):
                errors.append(f"Module {i}: behavior pack module type must be 'data' or 'script'")

    # Version format
    for key in ["version", "min_engine_version"]:
        val = manifest.get("header", {}).get(key)
        if val and not (isinstance(val, list) and len(val) >= 3 and all(isinstance(v, int) for v in val)):
            errors.append(f"header.{key} must be array of at least 3 integers")

    return errors


def create_level_dat(world_dir: Path, world_name: str, game_mode: str = "adventure",
                     spawn: tuple = (0, 64, 0), generator: str = "flat"):
    """Create a basic level.dat file for the world."""
    # level.dat in Bedrock is a LevelDB database, but we can create a minimal one
    # For a proper world, we'd use a template world and copy its db/ directory
    # This function creates a placeholder - real implementation uses a template world

    level_dat_content = {
        "LevelName": world_name,
        "GameType": {"value": 2 if game_mode == "adventure" else 0},  # 2=adventure, 0=survival
        "SpawnX": spawn[0],
        "SpawnY": spawn[1],
        "SpawnZ": spawn[2],
        "Generator": generator,
        "RandomSeed": 0,
        "SizeOnDisk": 0,
        "LastPlayed": 0,
        "Time": 6000,
        "DayTime": 6000,
        "Difficulty": 2,  # Normal
        "DifficultyLocked": False,
        "CommandsEnabled": True,
        "EduEditionOffers": False,
        "MultiplayerGame": False,
        "LANBroadcast": False,
        "XBLBroadcastMode": 0,
        "PlatformBroadcastMode": 0,
        "PlatformBroadcastIntent": 0,
        "ServerChunkTickRange": 4,
        "HasBeenOpenedInCreative": False,
        "LimitedWorldOriginX": 0,
        "LimitedWorldOriginZ": 0,
        "LimitedWorldWidth": 0,
        "LimitedWorldHeight": 0,
        "DisablePlayerInteraction": False,
        "LevelId": str(uuid.uuid4()).replace('-', ''),
        "WorldTemplateId": "",
        "WorldTemplateVersion": [0, 0, 0],
        "PremiumWorldTemplateId": "",
        "IsTrial": False,
        "GameRules": {
            "doDaylightCycle": False,
            "doWeatherCycle": False,
            "doMobSpawning": False,
            "keepInventory": True,
            "showCoordinates": True,
            "doFireTick": False,
            "doMobLoot": False,
            "doTileDrops": False,
            "commandBlockOutput": False,
            "sendCommandFeedback": False,
            "maxCommandChainLength": 65536,
            "randomTickSpeed": 0
        }
    }

    # Note: Actual level.dat is binary (LevelDB). This JSON is for reference.
    # The real world directory should be copied from a template.
    return level_dat_content


def copy_world_template(template_dir: Path, dest_dir: Path, world_name: str):
    """Copy a template world directory and update levelname.txt."""
    if not template_dir.exists():
        raise FileNotFoundError(f"Template world not found at {template_dir}")

    shutil.copytree(template_dir, dest_dir, dirs_exist_ok=True)

    # Update levelname.txt
    levelname_file = dest_dir / "levelname.txt"
    levelname_file.write_text(world_name)


def copy_pack(pack_dir: Path, dest_dir: Path, pack_type: str, new_uuids: bool = True):
    """Copy a resource/behavior pack directory and optionally update UUIDs."""
    if not pack_dir.exists():
        raise FileNotFoundError(f"{pack_type} pack not found at {pack_dir}")

    shutil.copytree(pack_dir, dest_dir, dirs_exist_ok=True)

    if new_uuids:
        manifest_path = dest_dir / "manifest.json"
        if manifest_path.exists():
            manifest = read_manifest(manifest_path)
            manifest = update_manifest_uuids(manifest, pack_type)
            write_manifest(manifest_path, manifest)

            # Validate
            errors = validate_manifest(manifest, pack_type)
            if errors:
                print(f"Warning: {pack_type} manifest validation errors:")
                for e in errors:
                    print(f"  - {e}")


def create_world_icon(world_dir: Path, icon_path: Optional[Path] = None):
    """Create or copy world_icon.jpeg for the world."""
    target = world_dir / "world_icon.jpeg"

    if icon_path and icon_path.exists():
        shutil.copy2(icon_path, target)
    else:
        # Create a simple placeholder icon (128x128)
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (128, 128), (70, 130, 180))
            draw = ImageDraw.Draw(img)
            draw.text((10, 50), "Birthday\nWorld", fill=(255, 255, 255))
            img.save(target, "JPEG")
        except ImportError:
            # Create minimal JPEG header
            with open(target, 'wb') as f:
                f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00')


def create_pack_icon(pack_dir: Path, icon_path: Optional[Path] = None):
    """Create or copy pack_icon.png for the pack."""
    target = pack_dir / "pack_icon.png"

    if icon_path and icon_path.exists():
        shutil.copy2(icon_path, target)
    else:
        # Create a simple placeholder icon (128x128)
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGBA', (128, 128), (70, 130, 180, 255))
            draw = ImageDraw.Draw(img)
            draw.rectangle([10, 10, 118, 118], outline=(255, 215, 0, 255), width=4)
            draw.text((20, 50), "Birthday\nPack", fill=(255, 255, 255, 255))
            img.save(target, "PNG")
        except ImportError:
            # Create minimal PNG
            with open(target, 'wb') as f:
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00\x80\x08\x06\x00\x00\x00')


def build_mcworld(output_path: Path, world_dir: Path, resource_pack_dir: Path,
                  behavior_pack_dir: Path, world_name: str = "Birthday World"):
    """
    Build a .mcworld file from world and pack directories.

    The .mcworld format is a ZIP file containing:
    - db/ (world LevelDB data)
    - levelname.txt
    - world_icon.jpeg
    - resource_packs/ (resource pack directories)
    - behavior_packs/ (behavior pack directories)
    - world_resource_packs.json
    - world_behavior_packs.json
    """

    # Create temporary build directory
    build_dir = output_path.parent / f".build_{uuid.uuid4().hex[:8]}"
    build_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Copy world
        world_build = build_dir / "world"
        copy_world_template(world_dir, world_build, world_name)

        # Create world_icon.jpeg
        create_world_icon(world_build)

        # Create world_resource_packs.json
        resource_pack_manifest = read_manifest(resource_pack_dir / "manifest.json")
        rp_uuid = resource_pack_manifest["header"]["uuid"]
        rp_version = resource_pack_manifest["header"]["version"]

        world_rp = [{
            "pack_id": rp_uuid,
            "version": rp_version
        }]
        (build_dir / "world_resource_packs.json").write_text(json.dumps(world_rp, indent=2))

        # Create world_behavior_packs.json
        behavior_pack_manifest = read_manifest(behavior_pack_dir / "manifest.json")
        bp_uuid = behavior_pack_manifest["header"]["uuid"]
        bp_version = behavior_pack_manifest["header"]["version"]

        world_bp = [{
            "pack_id": bp_uuid,
            "version": bp_version
        }]
        (build_dir / "world_behavior_packs.json").write_text(json.dumps(world_bp, indent=2))

        # Copy resource pack
        rp_build = build_dir / "resource_packs" / resource_pack_manifest["header"]["name"]
        copy_pack(resource_pack_dir, rp_build, "resource_pack")
        create_pack_icon(rp_build)

        # Copy behavior pack
        bp_build = build_dir / "behavior_packs" / behavior_pack_manifest["header"]["name"]
        copy_pack(behavior_pack_dir, bp_build, "behavior_pack")
        create_pack_icon(bp_build)

        # Create the .mcworld ZIP file
        print(f"Creating {output_path}...")
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in build_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(build_dir)
                    zf.write(file_path, arcname)

        print(f"Successfully created {output_path}")
        print(f"  World: {world_name}")
        print(f"  Resource Pack: {resource_pack_manifest['header']['name']} ({rp_uuid})")
        print(f"  Behavior Pack: {behavior_pack_manifest['header']['name']} ({bp_uuid})")

        return True

    finally:
        # Cleanup
        if build_dir.exists():
            shutil.rmtree(build_dir)


def extract_mcworld(mcworld_path: Path, output_dir: Path):
    """Extract a .mcworld file to a directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(mcworld_path, 'r') as zf:
        zf.extractall(output_dir)

    print(f"Extracted {mcworld_path} to {output_dir}")


def validate_mcworld(mcworld_path: Path) -> List[str]:
    """Validate a .mcworld file structure."""
    errors = []

    with zipfile.ZipFile(mcworld_path, 'r') as zf:
        files = zf.namelist()

        # Check required files
        required = ["levelname.txt", "world_resource_packs.json", "world_behavior_packs.json"]
        for req in required:
            if req not in files:
                errors.append(f"Missing required file: {req}")

        # Check for world data
        has_db = any(f.startswith("db/") for f in files)
        if not has_db:
            errors.append("Missing world database (db/ directory)")

        # Validate resource pack
        rp_files = [f for f in files if f.startswith("resource_packs/")]
        if not rp_files:
            errors.append("No resource packs found")
        else:
            # Check for manifest
            rp_manifests = [f for f in rp_files if f.endswith("manifest.json")]
            if not rp_manifests:
                errors.append("Resource pack missing manifest.json")

        # Validate behavior pack
        bp_files = [f for f in files if f.startswith("behavior_packs/")]
        if not bp_files:
            errors.append("No behavior packs found")
        else:
            bp_manifests = [f for f in bp_files if f.endswith("manifest.json")]
            if not bp_manifests:
                errors.append("Behavior pack missing manifest.json")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Build Minecraft Bedrock .mcworld packages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build from directories
  python build_mcworld.py build -o Happy_Birthday_Ujan.mcworld \
    -w ./world_template -r ./resource_pack -b ./behavior_pack \
    -n "Happy Birthday Ujan"

  # Validate existing .mcworld
  python build_mcworld.py validate -f Happy_Birthday_Ujan.mcworld

  # Extract .mcworld for inspection
  python build_mcworld.py extract -f Happy_Birthday_Ujan.mcworld -o ./extracted
        """
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # Build command
    build_parser = subparsers.add_parser('build', help='Build .mcworld from directories')
    build_parser.add_argument('-o', '--output', type=Path, required=True,
                              help='Output .mcworld file path')
    build_parser.add_argument('-w', '--world', type=Path, required=True,
                              help='World template directory')
    build_parser.add_argument('-r', '--resource-pack', type=Path, required=True,
                              help='Resource pack directory')
    build_parser.add_argument('-b', '--behavior-pack', type=Path, required=True,
                              help='Behavior pack directory')
    build_parser.add_argument('-n', '--name', type=str, default="Birthday World",
                              help='World name')
    build_parser.add_argument('--world-icon', type=Path, help='World icon image')
    build_parser.add_argument('--rp-icon', type=Path, help='Resource pack icon')
    build_parser.add_argument('--bp-icon', type=Path, help='Behavior pack icon')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate .mcworld file')
    validate_parser.add_argument('-f', '--file', type=Path, required=True,
                                 help='Path to .mcworld file')

    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract .mcworld file')
    extract_parser.add_argument('-f', '--file', type=Path, required=True,
                                help='Path to .mcworld file')
    extract_parser.add_argument('-o', '--output', type=Path, required=True,
                                help='Output directory')

    args = parser.parse_args()

    if args.command == 'build':
        success = build_mcworld(
            args.output,
            args.world,
            args.resource_pack,
            args.behavior_pack,
            args.name
        )
        sys.exit(0 if success else 1)

    elif args.command == 'validate':
        errors = validate_mcworld(args.file)
        if errors:
            print(f"Validation failed for {args.file}:")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)
        else:
            print(f"{args.file} is valid!")
            sys.exit(0)

    elif args.command == 'extract':
        extract_mcworld(args.file, args.output)
        sys.exit(0)


if __name__ == "__main__":
    main()
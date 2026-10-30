#!/usr/bin/env python3
"""
Birthday World Generator

Generates the base world structure for the birthday adventure world.
Creates terrain, zones, structures, and places key blocks.

This script outputs:
1. A set of structure files (.mcstructure) for each zone
2. A world initialization script (.mcfunction) to set up the world
3. Coordinate reference for all key locations

Requirements: pip install numpy
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any
import numpy as np


# Zone definitions matching the behavior pack
ZONES = {
    "spawn": {
        "name": "Grand Birthday Kingdom",
        "center": (0, 64, 0),
        "radius": 50,
        "height": 20,
        "theme": "palace",
        "blocks": {
            "floor": "minecraft:quartz_block",
            "walls": "minecraft:quartz_bricks",
            "accent": "minecraft:gold_block",
            "roof": "minecraft:blue_glazed_terracotta"
        }
    },
    "celebrationHall": {
        "name": "Royal Celebration Hall",
        "center": (100, 64, 0),
        "radius": 40,
        "height": 15,
        "theme": "banquet_hall",
        "blocks": {
            "floor": "minecraft:polished_andesite",
            "walls": "minecraft:stone_bricks",
            "accent": "minecraft:red_carpet",
            "roof": "minecraft:dark_oak_log"
        }
    },
    "memoryMuseum": {
        "name": "Memory Museum",
        "center": (-100, 64, 0),
        "radius": 40,
        "height": 15,
        "theme": "museum",
        "blocks": {
            "floor": "minecraft:polished_diorite",
            "walls": "minecraft:quartz_pillar",
            "accent": "minecraft:item_frame",
            "roof": "minecraft:white_concrete"
        }
    },
    "amusementCity": {
        "name": "Amusement & Adventure City",
        "center": (0, 64, 100),
        "radius": 50,
        "height": 25,
        "theme": "amusement_park",
        "blocks": {
            "floor": "minecraft:rainbow_concrete",  # placeholder
            "walls": "minecraft:colorful_terracotta",
            "accent": "minecraft:glowstone",
            "roof": "minecraft:stripped_spruce_log"
        }
    },
    "mysteryForest": {
        "name": "Mystery Forest",
        "center": (0, 64, -100),
        "radius": 50,
        "height": 30,
        "theme": "forest",
        "blocks": {
            "floor": "minecraft:podzol",
            "walls": "minecraft:dark_oak_log",
            "accent": "minecraft:mushroom_block",
            "roof": "minecraft:oak_leaves"
        }
    },
    "secretVault": {
        "name": "Secret Birthday Vault",
        "center": (200, 64, 200),
        "radius": 30,
        "height": 20,
        "theme": "vault",
        "blocks": {
            "floor": "minecraft:deepslate_bricks",
            "walls": "minecraft:deepslate_tiles",
            "accent": "minecraft:end_rod",
            "roof": "minecraft:reinforced_deepslate"
        }
    },
    "finaleArena": {
        "name": "Grand Finale Arena",
        "center": (-200, 64, -200),
        "radius": 40,
        "height": 30,
        "theme": "arena",
        "blocks": {
            "floor": "minecraft:netherite_block",
            "walls": "minecraft:obsidian",
            "accent": "minecraft:beacon",
            "roof": "minecraft:end_stone"
        }
    }
}

# Gift locations (matching behavior pack)
GIFT_LOCATIONS = [
    {"pos": (10, 64, 10), "zone": "spawn", "item": "diamond", "name": "Birthday Diamond"},
    {"pos": (-15, 65, 5), "zone": "spawn", "item": "emerald", "name": "Birthday Emerald"},
    {"pos": (105, 64, 10), "zone": "celebrationHall", "item": "golden_apple", "name": "Golden Apple"},
    {"pos": (95, 66, -5), "zone": "celebrationHall", "item": "enchanted_book", "name": "Enchanted Birthday Book"},
    {"pos": (-105, 64, 15), "zone": "memoryMuseum", "item": "firework_rocket", "name": "Celebration Rocket"},
    {"pos": (-90, 65, -10), "zone": "memoryMuseum", "item": "diamond", "name": "Memory Diamond"},
    {"pos": (5, 70, 105), "zone": "amusementCity", "item": "emerald", "name": "Park Emerald"},
    {"pos": (-10, 68, 95), "zone": "amusementCity", "item": "golden_apple", "name": "Carousel Apple"},
    {"pos": (15, 64, -105), "zone": "mysteryForest", "item": "enchanted_book", "name": "Forest Secrets"},
    {"pos": (-20, 66, -95), "zone": "mysteryForest", "item": "firework_rocket", "name": "Mystery Rocket"},
    {"pos": (205, 64, 205), "zone": "secretVault", "item": "diamond", "name": "Vault Diamond"},
    {"pos": (195, 65, 195), "zone": "secretVault", "item": "emerald", "name": "Vault Emerald"},
    {"pos": (-205, 64, -205), "zone": "finaleArena", "item": "golden_apple", "name": "Finale Apple"},
    {"pos": (-195, 65, -195), "zone": "finaleArena", "item": "enchanted_book", "name": "Grand Finale Book"},
]

# Treasure hunt clue locations
CLUE_LOCATIONS = [
    {"id": 0, "pos": (0, 64, 0), "zone": "spawn"},
    {"id": 1, "pos": (100, 64, 0), "zone": "celebrationHall"},
    {"id": 2, "pos": (-100, 64, 0), "zone": "memoryMuseum"},
    {"id": 3, "pos": (0, 64, 100), "zone": "amusementCity"},
    {"id": 4, "pos": (0, 64, -100), "zone": "mysteryForest"},
    {"id": 5, "pos": (200, 64, 200), "zone": "secretVault"},
    {"id": 6, "pos": (-200, 64, -200), "zone": "finaleArena"},
]

# Path connections between zones
PATHS = [
    {"from": "spawn", "to": "celebrationHall", "color": "gold"},
    {"from": "spawn", "to": "memoryMuseum", "color": "white"},
    {"from": "spawn", "to": "amusementCity", "color": "rainbow"},
    {"from": "spawn", "to": "mysteryForest", "color": "green"},
    {"from": "celebrationHall", "to": "secretVault", "color": "red"},
    {"from": "memoryMuseum", "to": "mysteryForest", "color": "brown"},
    {"from": "amusementCity", "to": "mysteryForest", "color": "blue"},
    {"from": "secretVault", "to": "finaleArena", "color": "purple"},
    {"from": "mysteryForest", "to": "finaleArena", "color": "black"},
]


def create_circle(radius: int, center: Tuple[int, int] = (0, 0)) -> List[Tuple[int, int]]:
    """Generate block coordinates for a circle outline."""
    cx, cz = center
    blocks = []
    for x in range(-radius, radius + 1):
        for z in range(-radius, radius + 1):
            dist = (x**2 + z**2)**0.5
            if radius - 1 < dist <= radius:
                blocks.append((cx + x, cz + z))
    return blocks


def create_filled_circle(radius: int, center: Tuple[int, int] = (0, 0)) -> List[Tuple[int, int]]:
    """Generate block coordinates for a filled circle."""
    cx, cz = center
    blocks = []
    for x in range(-radius, radius + 1):
        for z in range(-radius, radius + 1):
            if (x**2 + z**2)**0.5 <= radius:
                blocks.append((cx + x, cz + z))
    return blocks


def create_line(x1: int, z1: int, x2: int, z2: int, width: int = 3) -> List[Tuple[int, int]]:
    """Generate block coordinates for a line (path) between two points."""
    blocks = []
    dx = abs(x2 - x1)
    dz = abs(z2 - z1)
    sx = 1 if x1 < x2 else -1
    sz = 1 if z1 < z2 else -1
    err = dx - dz

    x, z = x1, z1
    while True:
        # Add width around the line
        for wx in range(-width//2, width//2 + 1):
            for wz in range(-width//2, width//2 + 1):
                blocks.append((x + wx, z + wz))

        if x == x2 and z == z2:
            break
        e2 = 2 * err
        if e2 > -dz:
            err -= dz
            x += sx
        if e2 < dx:
            err += dx
            z += sz

    return blocks


def generate_zone_structure(zone_id: str, zone: Dict) -> Dict[str, Any]:
    """Generate structure data for a single zone."""
    cx, cy, cz = zone["center"]
    radius = zone["radius"]
    height = zone["height"]
    blocks = zone["blocks"]

    structure = {
        "zone_id": zone_id,
        "name": zone["name"],
        "center": list(zone["center"]),
        "radius": radius,
        "height": height,
        "blocks": [],
        "entities": [],
        "signs": []
    }

    # Floor
    for x, z in create_filled_circle(radius, (cx, cz)):
        structure["blocks"].append({
            "pos": [x, cy - 1, z],
            "block": blocks["floor"]
        })

    # Walls (cylindrical)
    for y in range(cy, cy + height):
        for x, z in create_circle(radius, (cx, cz)):
            # Add windows every 8 blocks
            angle = np.arctan2(z - cz, x - cx)
            if int((angle + np.pi) * 4 / np.pi) % 8 == 0:
                structure["blocks"].append({
                    "pos": [x, y, z],
                    "block": "minecraft:glass_pane"
                })
            else:
                structure["blocks"].append({
                    "pos": [x, y, z],
                    "block": blocks["walls"]
                })

    # Roof (dome)
    for layer in range(height // 2):
        r = radius - layer
        if r <= 0:
            break
        for x, z in create_filled_circle(r, (cx, cz)):
            structure["blocks"].append({
                "pos": [x, cy + height - layer, z],
                "block": blocks["roof"]
            })

    # Center accent pillar
    for y in range(cy, cy + height + 5):
        structure["blocks"].append({
            "pos": [cx, y, cz],
            "block": blocks["accent"]
        })

    # Zone entrance sign
    structure["signs"].append({
        "pos": [cx, cy + 1, cz - radius - 2],
        "text": f"§l§e{zone['name']}",
        "block": "minecraft:oak_sign"
    })

    return structure


def generate_path_structure(path: Dict) -> Dict[str, Any]:
    """Generate path structure between two zones."""
    zone_from = ZONES[path["from"]]
    zone_to = ZONES[path["to"]]

    x1, _, z1 = zone_from["center"]
    x2, _, z2 = zone_to["center"]

    path_blocks = create_line(x1, z1, x2, z2, width=5)

    # Determine path block type
    color_map = {
        "gold": "minecraft:gold_block",
        "white": "minecraft:quartz_block",
        "rainbow": "minecraft:white_concrete",  # will be colored in sections
        "green": "minecraft:lime_concrete",
        "red": "minecraft:red_concrete",
        "brown": "minecraft:brown_concrete",
        "blue": "minecraft:blue_concrete",
        "purple": "minecraft:purple_concrete",
        "black": "minecraft:black_concrete"
    }
    block_type = color_map.get(path["color"], "minecraft:gray_concrete")

    structure = {
        "path_id": f"{path['from']}_to_{path['to']}",
        "from": path["from"],
        "to": path["to"],
        "color": path["color"],
        "blocks": []
    }

    for x, z in path_blocks:
        structure["blocks"].append({
            "pos": [x, 63, z],
            "block": block_type
        })

        # Add glowstone lanterns every 10 blocks
        dist = ((x - x1)**2 + (z - z1)**2)**0.5
        if int(dist) % 10 == 0:
            structure["blocks"].append({
                "pos": [x, 65, z],
                "block": "minecraft:glowstone"
            })
            structure["blocks"].append({
                "pos": [x, 64, z],
                "block": "minecraft:glass_pane"
            })

    return structure


def generate_gift_structures() -> List[Dict]:
    """Generate chest structures for each gift location."""
    structures = []

    for i, gift in enumerate(GIFT_LOCATIONS):
        x, y, z = gift["pos"]
        structure = {
            "gift_id": i,
            "zone": gift["zone"],
            "item": gift["item"],
            "name": gift["name"],
            "blocks": [
                {"pos": [x, y - 1, z], "block": "minecraft:chest"},
                {"pos": [x, y, z], "block": "minecraft:end_rod"},  # Marker
                {"pos": [x - 1, y, z], "block": "minecraft:flower_pot"},
                {"pos": [x + 1, y, z], "block": "minecraft:flower_pot"},
                {"pos": [x, y, z - 1], "block": "minecraft:flower_pot"},
                {"pos": [x, y, z + 1], "block": "minecraft:flower_pot"},
            ],
            "chest_loot": {
                "item": f"minecraft:{gift['item']}",
                "count": 1,
                "custom_name": gift["name"]
            }
        }
        structures.append(structure)

    return structures


def generate_clue_structures() -> List[Dict]:
    """Generate structures for treasure hunt clues."""
    structures = []

    for clue in CLUE_LOCATIONS:
        x, y, z = clue["pos"]
        structure = {
            "clue_id": clue["id"],
            "zone": clue["zone"],
            "blocks": [
                {"pos": [x, y - 1, z], "block": "minecraft:lectern"},
                {"pos": [x, y + 1, z], "block": "minecraft:end_rod"},
                {"pos": [x - 1, y, z], "block": "minecraft:bookshelf"},
                {"pos": [x + 1, y, z], "block": "minecraft:bookshelf"},
            ]
        }
        structures.append(structure)

    return structures


def generate_spawn_structure() -> Dict[str, Any]:
    """Generate the main spawn area structure."""
    cx, cy, cz = 0, 64, 0

    structure = {
        "name": "spawn_platform",
        "center": [cx, cy, cz],
        "blocks": [],
        "entities": []
    }

    # Large spawn platform
    for x, z in create_filled_circle(10, (cx, cz)):
        structure["blocks"].append({
            "pos": [x, cy - 1, z],
            "block": "minecraft:quartz_block"
        })

    # Birthday cake at center
    structure["blocks"].append({
        "pos": [cx, cy, cz],
        "block": "minecraft:cake"
    })

    # Surrounding decoration
    for x, z in create_circle(5, (cx, cz)):
        structure["blocks"].append({
            "pos": [x, cy, z],
            "block": "minecraft:white_concrete"
        })
        structure["blocks"].append({
            "pos": [x, cy + 1, z],
            "block": "minecraft:glass_pane"
        })

    # Welcome sign
    structure["blocks"].append({
        "pos": [cx, cy + 2, cz - 7],
        "block": "minecraft:oak_sign"
    })

    return structure


def generate_mcfunction_init() -> str:
    """Generate the world initialization mcfunction."""
    lines = [
        "# Birthday World Initialization Function",
        "# Run once on world creation: /function birthday:init",
        "",
        "# Set world spawn",
        "setworldspawn 0 64 0",
        "",
        "# Set default game mode to adventure",
        "defaultgamemode adventure",
        "",
        "# Disable weather cycle",
        "gamerule doWeatherCycle false",
        "weather clear 1000000",
        "",
        "# Disable daylight cycle (keep it day)",
        "gamerule doDaylightCycle false",
        "time set day",
        "",
        "# Disable mob spawning",
        "gamerule doMobSpawning false",
        "",
        "# Keep inventory on death",
        "gamerule keepInventory true",
        "",
        "# Show coordinates",
        "gamerule showCoordinates true",
        "",
        "# Announce world ready",
        "tellraw @a {\"rawtext\":[{\"text\":\"§l§e★ Birthday World Initialized! ★\"}]}",
        "",
        "# Give starter items",
        "give @a minecraft:map 1",
        "give @a minecraft:compass 1",
        "",
        "# Set up scoreboard for gift tracking",
        "scoreboard objectives add birthdayGifts dummy \"§eBirthday Gifts Found\"",
        "scoreboard objectives setdisplay sidebar birthdayGifts",
        "",
        "# Tag player as birthday player",
        "tag @a add birthday_player",
        "",
        "tellraw @a {\"rawtext\":[{\"text\":\"§dWelcome to your birthday adventure! Use §e!help §dfor commands.\"}]}"
    ]
    return "\n".join(lines)


def generate_mcfunction_zone_setup() -> str:
    """Generate zone setup function."""
    lines = [
        "# Zone Setup Function",
        "# Run after structures are placed: /function birthday:setup_zones",
        ""
    ]

    for zone_id, zone in ZONES.items():
        cx, cy, cz = zone["center"]
        lines.append(f"# {zone['name']}")
        lines.append(f"tellraw @a[distance=..5,x={cx},y={cy},z={cz}] {{\"rawtext\":[{{\"text\":\"§l§6» Entering: {zone['name']} «\"}}]}}")
        lines.append("")

    return "\n".join(lines)


def generate_mcfunction_gifts() -> str:
    """Generate gift placement function."""
    lines = [
        "# Gift Placement Function",
        "# Run to place all gift chests: /function birthday:place_gifts",
        ""
    ]

    for gift in GIFT_LOCATIONS:
        x, y, z = gift["pos"]
        item = gift["item"]
        name = gift["name"].replace('"', '\\"')

        lines.append(f"# Gift: {gift['name']} at {x} {y} {z}")
        lines.append(f"setblock {x} {y-1} {z} minecraft:chest{{Items:[{{Slot:0b,id:\"minecraft:{item}\",Count:1b,tag:{{display:{{Name:'\\\"{name}\\\"'}}}}}}]}}")
        lines.append(f"setblock {x} {y} {z} minecraft:end_rod")
        lines.append("")

    return "\n".join(lines)


def generate_mcfunction_clues() -> str:
    """Generate clue placement function."""
    lines = [
        "# Clue Placement Function",
        "# Run to place all treasure hunt clues: /function birthday:place_clues",
        ""
    ]

    clue_texts = [
        "Your journey begins at the heart of the kingdom. Look for the golden block beneath the birthday banner.",
        "Where feasts are held and friends gather round, seek the cake that makes no sound.",
        "Memories line the walls in frames so bright, find the photo that glows in the night.",
        "Rides and games and laughter near, the next clue waits at the Ferris wheel's rear.",
        "Deep in the forest, secrets hide, follow the path where fireflies guide.",
        "The vault is near, but locked up tight, find the key that gleams so bright.",
        "The final destination, grand and true, the arena awaits - celebration for you!"
    ]

    for i, clue in enumerate(CLUE_LOCATIONS):
        x, y, z = clue["pos"]
        text = clue_texts[i].replace('"', '\\"')

        lines.append(f"# Clue {i+1} at {x} {y} {z}")
        lines.append(f"setblock {x} {y-1} {z} minecraft:lectern{{Book:{{id:\"minecraft:written_book\",Count:1b,tag:{{pages:['\\\"{text}\\\"'],title:'\\\"Clue {i+1}\\\"',author:'\\\"Birthday World\\\"'}}}}}}")
        lines.append(f"setblock {x} {y+1} {z} minecraft:end_rod")
        lines.append("")

    return "\n".join(lines)


def save_world_data(output_dir: Path, config: Dict = None):
    """Save all generated world data to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate all structures
    all_structures = {}

    # Zone structures
    for zone_id, zone in ZONES.items():
        all_structures[zone_id] = generate_zone_structure(zone_id, zone)

    # Path structures
    for path in PATHS:
        path_struct = generate_path_structure(path)
        all_structures[path_struct["path_id"]] = path_struct

    # Gift structures
    gift_structs = generate_gift_structures()
    for i, gs in enumerate(gift_structs):
        all_structures[f"gift_{i}"] = gs

    # Clue structures
    clue_structs = generate_clue_structures()
    for cs in clue_structs:
        all_structures[f"clue_{cs['clue_id']}"] = cs

    # Spawn structure
    all_structures["spawn"] = generate_spawn_structure()

    # Save structures as JSON
    structures_file = output_dir / "world_structures.json"
    with open(structures_file, 'w') as f:
        json.dump(all_structures, f, indent=2)

    print(f"Saved {len(all_structures)} structures to {structures_file}")

    # Generate mcfunction files
    functions_dir = output_dir / "functions"
    functions_dir.mkdir(parents=True, exist_ok=True)

    init_func = generate_mcfunction_init()
    (functions_dir / "init.mcfunction").write_text(init_func, encoding="utf-8")

    zone_func = generate_mcfunction_zone_setup()
    (functions_dir / "setup_zones.mcfunction").write_text(zone_func, encoding="utf-8")

    gifts_func = generate_mcfunction_gifts()
    (functions_dir / "place_gifts.mcfunction").write_text(gifts_func, encoding="utf-8")

    clues_func = generate_mcfunction_clues()
    (functions_dir / "place_clues.mcfunction").write_text(clues_func, encoding="utf-8")

    # Master setup function
    master_func = "\n".join([
        "# Master Setup Function",
        "# Run: /function birthday:master_setup",
        "",
        "function birthday:init",
        "function birthday:setup_zones",
        "function birthday:place_gifts",
        "function birthday:place_clues",
        "",
        "tellraw @a {\"rawtext\":[{\"text\":\"§l§a★ World Setup Complete! ★\"}]}",
    ])
    (functions_dir / "master_setup.mcfunction").write_text(master_func, encoding="utf-8")

    print(f"Generated function files in {functions_dir}")

    # Save coordinate reference
    coords = {
        "zones": {k: {"name": v["name"], "center": v["center"], "radius": v["radius"]} for k, v in ZONES.items()},
        "gifts": GIFT_LOCATIONS,
        "clues": CLUE_LOCATIONS,
        "paths": PATHS,
        "spawn": {"center": [0, 64, 0]}
    }
    coords_file = output_dir / "coordinates.json"
    with open(coords_file, 'w') as f:
        json.dump(coords, f, indent=2)

    print(f"Saved coordinates to {coords_file}")

    # Summary
    total_blocks = sum(len(s.get("blocks", [])) for s in all_structures.values())
    print(f"\n=== World Generation Summary ===")
    print(f"Zones: {len(ZONES)}")
    print(f"Paths: {len(PATHS)}")
    print(f"Gifts: {len(GIFT_LOCATIONS)}")
    print(f"Clues: {len(CLUE_LOCATIONS)}")
    print(f"Total structure blocks: {total_blocks:,}")
    print(f"Output directory: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Birthday World structures and setup functions",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-o', '--output-dir', type=Path, required=True,
                        help='Output directory for generated files')
    parser.add_argument('--config', type=Path,
                        help='Path to birthday.json config file')

    args = parser.parse_args()

    config = None
    if args.config and args.config.exists():
        with open(args.config) as f:
            config = json.load(f)

    save_world_data(args.output_dir, config)

    return 0


if __name__ == "__main__":
    exit(main())
#!/usr/bin/env python3
"""
Photo to Minecraft Pixel Art Converter (Block-based)

Converts photographs into Minecraft pixel art using colored blocks
(concrete, wool, terracotta, glazed_terracotta) that can be built in-game.

This is more practical for large displays than map art.

Requirements: pip install pillow numpy

Usage:
    python photo_to_pixel_art.py --input-dir ./photos --output-dir ./output --block-type concrete
"""

import argparse
import os
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from PIL import Image
import numpy as np


# Minecraft block palette - Concrete colors (most vibrant)
CONCRETE_PALETTE = {
    "white": (234, 234, 234),
    "orange": (241, 118, 20),
    "magenta": (189, 68, 179),
    "light_blue": (58, 175, 217),
    "yellow": (249, 214, 31),
    "lime": (94, 169, 24),
    "pink": (216, 101, 143),
    "gray": (63, 63, 63),
    "light_gray": (141, 141, 141),
    "cyan": (21, 137, 153),
    "purple": (121, 42, 172),
    "blue": (53, 57, 157),
    "brown": (96, 59, 31),
    "green": (73, 91, 36),
    "red": (142, 33, 33),
    "black": (20, 21, 25),
}

# Wool palette (softer colors)
WOOL_PALETTE = {
    "white": (234, 234, 234),
    "orange": (224, 97, 1),
    "magenta": (169, 48, 159),
    "light_blue": (58, 175, 217),
    "yellow": (241, 175, 21),
    "lime": (94, 169, 24),
    "pink": (216, 101, 143),
    "gray": (63, 63, 63),
    "light_gray": (141, 141, 141),
    "cyan": (21, 137, 153),
    "purple": (121, 42, 172),
    "blue": (53, 57, 157),
    "brown": (86, 51, 28),
    "green": (67, 83, 32),
    "red": (157, 23, 23),
    "black": (20, 21, 25),
}

# Terracotta palette (muted, earthy)
TERRACOTTA_PALETTE = {
    "white": (209, 177, 161),
    "orange": (161, 83, 37),
    "magenta": (149, 88, 108),
    "light_blue": (112, 108, 138),
    "yellow": (186, 133, 36),
    "lime": (86, 91, 42),
    "pink": (162, 78, 79),
    "gray": (57, 42, 35),
    "light_gray": (135, 107, 98),
    "cyan": (86, 91, 92),
    "purple": (118, 70, 86),
    "blue": (75, 61, 91),
    "brown": (78, 49, 31),
    "green": (76, 82, 42),
    "red": (142, 60, 46),
    "black": (37, 22, 16),
}

# Glazed terracotta (patterned, not solid - use sparingly)
GLAZED_TERRACOTTA_PALETTE = {
    "white": (228, 228, 228),
    "orange": (229, 127, 30),
    "magenta": (179, 80, 188),
    "light_blue": (37, 137, 199),
    "yellow": (247, 233, 63),
    "lime": (111, 186, 48),
    "pink": (227, 130, 179),
    "gray": (65, 55, 58),
    "light_gray": (136, 126, 115),
    "cyan": (26, 133, 178),
    "purple": (124, 62, 181),
    "blue": (43, 54, 152),
    "brown": (84, 56, 27),
    "green": (65, 100, 30),
    "red": (159, 38, 38),
    "black": (33, 33, 33),
}

# Combined palette with block names
ALL_PALETTES = {
    "concrete": CONCRETE_PALETTE,
    "wool": WOOL_PALETTE,
    "terracotta": TERRACOTTA_PALETTE,
    "glazed_terracotta": GLAZED_TERRACOTTA_PALETTE,
}

# Extended palette mixing multiple block types for better color range
def build_extended_palette() -> Dict[str, Tuple[int, int, int]]:
    """Build extended palette using multiple block types."""
    extended = {}

    # Add concrete
    for name, rgb in CONCRETE_PALETTE.items():
        extended[f"concrete_{name}"] = rgb

    # Add wool (different enough to warrant separate entries)
    for name, rgb in WOOL_PALETTE.items():
        extended[f"wool_{name}"] = rgb

    # Add terracotta
    for name, rgb in TERRACOTTA_PALETTE.items():
        extended[f"terracotta_{name}"] = rgb

    # Add glazed terracotta (limited)
    for name, rgb in GLAZED_TERRACOTTA_PALETTE.items():
        extended[f"glazed_terracotta_{name}"] = rgb

    return extended


EXTENDED_PALETTE = build_extended_palette()
PALETTE_NAMES = list(EXTENDED_PALETTE.keys())
PALETTE_RGB = np.array(list(EXTENDED_PALETTE.values()), dtype=np.uint8)


def find_closest_block(rgb: np.ndarray, palette_type: str = "extended") -> str:
    """Find the closest block in the specified palette."""
    if palette_type == "extended":
        palette_rgb = PALETTE_RGB
        palette_names = PALETTE_NAMES
    else:
        palette = ALL_PALETTES[palette_type]
        palette_names = list(palette.keys())
        palette_rgb = np.array(list(palette.values()), dtype=np.uint8)

    distances = np.sum((palette_rgb - rgb) ** 2, axis=1)
    return palette_names[int(np.argmin(distances))]


def image_to_pixel_art(image: Image.Image, width: int, height: int,
                        palette_type: str = "extended",
                        dither: bool = True) -> np.ndarray:
    """
    Convert image to block indices for pixel art.

    Returns:
        2D array of block name indices
    """
    # Resize maintaining aspect ratio
    img = image.copy()
    img.thumbnail((width, height), Image.Resampling.LANCZOS)

    # Create canvas
    canvas = Image.new('RGB', (width, height), (128, 128, 128))
    x_offset = (width - img.width) // 2
    y_offset = (height - img.height) // 2
    canvas.paste(img, (x_offset, y_offset))

    arr = np.array(canvas, dtype=np.uint8)

    if palette_type == "extended":
        palette_rgb = PALETTE_RGB
    else:
        palette_rgb = np.array(list(ALL_PALETTES[palette_type].values()), dtype=np.uint8)

    h, w = arr.shape[:2]
    result = np.zeros((h, w), dtype=np.int32)

    if dither:
        # Floyd-Steinberg dithering
        work = arr.astype(np.float32)
        for y in range(h):
            for x in range(w):
                old_pixel = work[y, x].copy()
                distances = np.sum((palette_rgb - old_pixel) ** 2, axis=1)
                new_idx = int(np.argmin(distances))
                new_pixel = palette_rgb[new_idx].astype(np.float32)
                result[y, x] = new_idx

                error = old_pixel - new_pixel

                if x + 1 < w:
                    work[y, x + 1] += error * 7 / 16
                if y + 1 < h:
                    if x > 0:
                        work[y + 1, x - 1] += error * 3 / 16
                    work[y + 1, x] += error * 5 / 16
                    if x + 1 < w:
                        work[y + 1, x + 1] += error * 1 / 16
    else:
        for y in range(h):
            for x in range(w):
                distances = np.sum((palette_rgb - arr[y, x]) ** 2, axis=1)
                result[y, x] = int(np.argmin(distances))

    return result


def generate_schematic(block_indices: np.ndarray, palette_type: str = "extended",
                       origin: Tuple[int, int, int] = (0, 0, 0),
                       orientation: str = "vertical") -> Dict[str, Any]:
    """
    Generate a schematic-like structure for pixel art placement.

    orientation: "vertical" (wall) or "horizontal" (floor/ceiling)
    """
    if palette_type == "extended":
        palette_names = PALETTE_NAMES
    else:
        palette_names = list(ALL_PALETTES[palette_type].keys())

    h, w = block_indices.shape
    ox, oy, oz = origin

    blocks = []

    for y in range(h):
        for x in range(w):
            block_idx = block_indices[y, x]
            block_name = palette_names[block_idx]

            # Parse block type and color
            if "_" in block_name:
                block_type, color = block_name.split("_", 1)
                block_id = f"minecraft:{color}_{block_type}"
            else:
                block_id = f"minecraft:{block_name}"

            if orientation == "vertical":
                # Wall: X horizontal, Y vertical
                bx = ox + x
                by = oy + (h - 1 - y)  # Flip Y so image is upright
                bz = oz
            else:
                # Horizontal: X horizontal, Z vertical
                bx = ox + x
                by = oy
                bz = oz + (h - 1 - y)

            blocks.append({
                "position": [bx, by, bz],
                "block": block_id
            })

    return {
        "width": w,
        "height": h,
        "origin": list(origin),
        "orientation": orientation,
        "block_count": len(blocks),
        "blocks": blocks
    }


def generate_mcfunction(block_indices: np.ndarray, palette_type: str = "extended",
                        origin: Tuple[int, int, int] = (0, 0, 0),
                        orientation: str = "vertical",
                        chunk_size: int = 1000) -> List[str]:
    """
    Generate .mcfunction file content for placing pixel art.

    Returns list of function file contents (split by chunk_size).
    """
    if palette_type == "extended":
        palette_names = PALETTE_NAMES
    else:
        palette_names = list(ALL_PALETTES[palette_type].keys())

    h, w = block_indices.shape
    ox, oy, oz = origin

    functions = []
    current_function = []
    block_count = 0

    for y in range(h):
        for x in range(w):
            block_idx = block_indices[y, x]
            block_name = palette_names[block_idx]

            if "_" in block_name:
                block_type, color = block_name.split("_", 1)
                block_id = f"{color}_{block_type}"
            else:
                block_id = block_name

            if orientation == "vertical":
                bx = ox + x
                by = oy + (h - 1 - y)
                bz = oz
            else:
                bx = ox + x
                by = oy
                bz = oz + (h - 1 - y)

            current_function.append(f"setblock {bx} {by} {bz} minecraft:{block_id}")
            block_count += 1

            if block_count >= chunk_size:
                functions.append("\n".join(current_function))
                current_function = []
                block_count = 0

    if current_function:
        functions.append("\n".join(current_function))

    return functions


def create_preview_image(block_indices: np.ndarray, palette_type: str = "extended",
                         scale: int = 4) -> Image.Image:
    """Create a preview image of the pixel art."""
    if palette_type == "extended":
        palette_rgb = PALETTE_RGB
    else:
        palette_rgb = np.array(list(ALL_PALETTES[palette_type].values()), dtype=np.uint8)

    h, w = block_indices.shape
    preview = np.zeros((h * scale, w * scale, 3), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            color = palette_rgb[block_indices[y, x]]
            preview[y*scale:(y+1)*scale, x*scale:(x+1)*scale] = color

    return Image.fromarray(preview, 'RGB')


def process_photos_to_pixel_art(input_dir: Path, output_dir: Path,
                                 width: int = 128, height: int = 128,
                                 palette_type: str = "extended",
                                 max_photos: int = 20,
                                 generate_functions: bool = True,
                                 function_chunk_size: int = 1000,
                                 orientation: str = "vertical") -> Dict[str, Any]:
    """
    Process photos to pixel art schematics/functions.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    photo_files = sorted([f for f in input_dir.iterdir()
                          if f.suffix.lower() in image_extensions])

    if not photo_files:
        return {"error": "No images found"}

    photo_files = photo_files[:max_photos]
    print(f"Processing {len(photo_files)} photos to pixel art ({width}x{height})...")

    results = []

    for idx, photo_path in enumerate(photo_files):
        print(f"  [{idx+1}/{len(photo_files)}] {photo_path.name}...")

        try:
            img = Image.open(photo_path).convert('RGB')

            # Convert to pixel art
            block_indices = image_to_pixel_art(img, width, height, palette_type, dither=True)

            # Generate preview
            preview = create_preview_image(block_indices, palette_type, scale=4)
            preview_file = output_dir / f"pixelart_{idx:03d}_preview.png"
            preview.save(preview_file)

            # Generate schematic JSON
            schematic = generate_schematic(block_indices, palette_type,
                                          origin=(0, 64, 0), orientation=orientation)
            schematic_file = output_dir / f"pixelart_{idx:03d}_schematic.json"
            with open(schematic_file, 'w') as f:
                json.dump(schematic, f, indent=2)

            # Generate mcfunction files
            function_files = []
            if generate_functions:
                functions = generate_mcfunction(block_indices, palette_type,
                                               origin=(idx * (width + 5), 64, 0),
                                               orientation=orientation,
                                               chunk_size=function_chunk_size)
                for chunk_idx, func_content in enumerate(functions):
                    func_file = output_dir / f"pixelart_{idx:03d}_part{chunk_idx:02d}.mcfunction"
                    with open(func_file, 'w') as f:
                        f.write(func_content)
                    function_files.append(str(func_file))

            # Block statistics
            unique_blocks = np.unique(block_indices)
            block_stats = {}
            for b_idx in unique_blocks:
                block_name = PALETTE_NAMES[b_idx] if palette_type == "extended" else list(ALL_PALETTES[palette_type].keys())[b_idx]
                count = int(np.sum(block_indices == b_idx))
                block_stats[block_name] = count

            results.append({
                "index": idx,
                "source": photo_path.name,
                "original_size": list(img.size),
                "output_size": f"{width}x{height}",
                "preview_file": str(preview_file),
                "schematic_file": str(schematic_file),
                "function_files": function_files,
                "block_count": int(width * height),
                "unique_blocks": len(unique_blocks),
                "block_stats": block_stats,
                "status": "success"
            })

        except Exception as e:
            print(f"    Error: {e}")
            results.append({
                "index": idx,
                "source": photo_path.name,
                "status": "error",
                "error": str(e)
            })

    # Save summary
    summary = {
        "total_processed": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "dimensions": f"{width}x{height}",
        "palette_type": palette_type,
        "orientation": orientation,
        "results": results
    }

    summary_file = output_dir / "pixel_art_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nProcessing complete!")
    print(f"  Successful: {summary['successful']}")
    print(f"  Output directory: {output_dir}")

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Convert photos to Minecraft pixel art (blocks)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Palettes:
  concrete         - Bright, vibrant colors (16 colors)
  wool             - Softer colors (16 colors)
  terracotta       - Muted, earthy colors (16 colors)
  extended         - All of the above combined (64 colors, best quality)

Examples:
  python photo_to_pixel_art.py -i ./pics -o ./pixelart --palette extended -W 128 -H 128
  python photo_to_pixel_art.py -i ../private-assets/photos -o ./assets/generic/pixelart --palette concrete -W 64 -H 64
        """
    )
    parser.add_argument('-i', '--input-dir', type=Path, required=True,
                        help='Directory containing source photos')
    parser.add_argument('-o', '--output-dir', type=Path, required=True,
                        help='Output directory for pixel art files')
    parser.add_argument('-W', '--width', type=int, default=128,
                        help='Output width in blocks')
    parser.add_argument('-H', '--height', type=int, default=128,
                        help='Output height in blocks')
    parser.add_argument('-p', '--palette', type=str, default='extended',
                        choices=['concrete', 'wool', 'terracotta', 'glazed_terracotta', 'extended'],
                        help='Block palette to use')
    parser.add_argument('-m', '--max', type=int, default=20,
                        help='Maximum number of photos to process')
    parser.add_argument('--orientation', type=str, default='vertical',
                        choices=['vertical', 'horizontal'],
                        help='Orientation: vertical (wall) or horizontal (floor)')
    parser.add_argument('--no-functions', action='store_true',
                        help='Skip .mcfunction file generation')
    parser.add_argument('--chunk-size', type=int, default=1000,
                        help='Max commands per .mcfunction file')

    args = parser.parse_args()

    if not args.input_dir.exists():
        print(f"Error: Input directory {args.input_dir} does not exist")
        return 1

    process_photos_to_pixel_art(
        args.input_dir,
        args.output_dir,
        width=args.width,
        height=args.height,
        palette_type=args.palette,
        max_photos=args.max,
        generate_functions=not args.no_functions,
        function_chunk_size=args.chunk_size,
        orientation=args.orientation
    )

    return 0


if __name__ == "__main__":
    exit(main())
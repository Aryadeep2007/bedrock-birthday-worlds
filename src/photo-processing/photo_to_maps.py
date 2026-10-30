#!/usr/bin/env python3
"""
Photo to Minecraft Map Art Converter

Converts photographs into Minecraft map art (pixel art) that can be displayed
on item frames in the Memory Museum.

Requirements: pip install pillow numpy

Usage:
    python photo_to_maps.py --input-dir ./photos --output-dir ./output --map-size 128
"""

import argparse
import os
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any
from PIL import Image
import numpy as np


# Minecraft map colors (approximate RGB values for map palette)
# Based on the 128-color map palette used in Bedrock Edition
MAP_PALETTE = [
    (0, 0, 0),          # 0 - Black
    (34, 34, 34),       # 1 - Dark Gray
    (68, 68, 68),       # 2 - Gray
    (102, 102, 102),    # 3 - Light Gray
    (136, 136, 136),    # 4 - Lighter Gray
    (170, 170, 170),    # 5 - Silver
    (204, 204, 204),    # 6 - Light Silver
    (238, 238, 238),    # 7 - White
    (255, 0, 0),        # 8 - Red
    (255, 85, 0),       # 9 - Orange Red
    (255, 170, 0),      # 10 - Orange
    (255, 255, 0),      # 11 - Yellow
    (170, 255, 0),      # 12 - Lime
    (85, 255, 0),       # 13 - Green Yellow
    (0, 255, 0),        # 14 - Green
    (0, 255, 85),       # 15 - Spring Green
    (0, 255, 170),      # 16 - Cyan Green
    (0, 255, 255),      # 17 - Cyan
    (0, 170, 255),      # 18 - Sky Blue
    (0, 85, 255),       # 19 - Blue
    (0, 0, 255),        # 20 - Dark Blue
    (85, 0, 255),       # 21 - Purple Blue
    (170, 0, 255),      # 22 - Purple
    (255, 0, 255),      # 23 - Magenta
    (255, 0, 170),      # 24 - Pink
    (255, 0, 85),       # 25 - Hot Pink
    (136, 0, 0),        # 26 - Dark Red
    (136, 68, 0),       # 27 - Brown
    (136, 136, 0),      # 28 - Olive
    (68, 136, 0),       # 29 - Dark Green
    (0, 136, 0),        # 30 - Forest Green
    (0, 136, 68),       # 31 - Teal
    (0, 136, 136),      # 32 - Dark Cyan
    (0, 68, 136),       # 33 - Navy
    (0, 0, 136),        # 34 - Dark Navy
    (68, 0, 136),       # 35 - Indigo
    (136, 0, 136),      # 36 - Dark Purple
    (136, 0, 68),       # 37 - Maroon
    (255, 136, 136),    # 38 - Light Red
    (255, 170, 136),    # 39 - Salmon
    (255, 204, 136),    # 40 - Light Orange
    (255, 238, 136),    # 41 - Light Yellow
    (204, 255, 136),    # 42 - Light Lime
    (170, 255, 136),    # 43 - Pale Green
    (136, 255, 136),    # 44 - Mint
    (136, 255, 170),    # 45 - Light Mint
    (136, 255, 204),    # 46 - Light Cyan Green
    (136, 255, 238),    # 47 - Pale Cyan
    (136, 204, 255),    # 48 - Light Sky Blue
    (136, 170, 255),    # 49 - Light Blue
    (136, 136, 255),    # 50 - Periwinkle
    (170, 136, 255),    # 51 - Light Purple
    (204, 136, 255),    # 52 - Light Magenta
    (238, 136, 255),    # 53 - Light Pink
    (255, 136, 238),    # 54 - Rose
    (255, 136, 204),    # 55 - Light Hot Pink
    (102, 51, 0),       # 56 - Dark Brown
    (102, 102, 51),     # 57 - Dark Olive
    (51, 102, 0),       # 58 - Dark Forest
    (0, 102, 51),       # 59 - Dark Teal
    (0, 102, 102),      # 60 - Darker Cyan
    (0, 51, 102),       # 61 - Darker Navy
    (51, 0, 102),       # 62 - Dark Indigo
    (102, 0, 102),      # 63 - Dark Magenta
    (102, 0, 51),       # 64 - Dark Rose
    (255, 170, 170),    # 65 - Pastel Red
    (255, 204, 170),    # 66 - Pastel Orange
    (255, 221, 170),    # 67 - Pastel Yellow
    (221, 255, 170),    # 68 - Pastel Lime
    (204, 255, 170),    # 69 - Pastel Green
    (170, 255, 204),    # 70 - Pastel Mint
    (170, 255, 221),    # 71 - Pastel Cyan
    (170, 221, 255),    # 72 - Pastel Blue
    (204, 170, 255),    # 73 - Pastel Purple
    (221, 170, 255),    # 74 - Pastel Magenta
    (255, 170, 221),    # 75 - Pastel Pink
    (68, 34, 0),        # 76 - Very Dark Brown
    (68, 68, 34),       # 77 - Very Dark Olive
    (34, 68, 0),        # 78 - Very Dark Green
    (0, 68, 34),        # 79 - Very Dark Teal
    (0, 68, 68),        # 80 - Very Dark Cyan
    (0, 34, 68),        # 81 - Very Dark Navy
    (34, 0, 68),        # 82 - Very Dark Indigo
    (68, 0, 68),        # 83 - Very Dark Purple
    (68, 0, 34),        # 84 - Very Dark Maroon
    (170, 85, 0),       # 85 - Bronze
    (170, 170, 85),     # 87 - Yellow Green
    (85, 170, 0),       # 86 - Lime Green
    (0, 170, 85),       # 88 - Sea Green
    (0, 170, 170),      # 89 - Turquoise
    (0, 85, 170),       # 90 - Azure
    (0, 0, 170),        # 91 - Medium Blue
    (85, 0, 170),       # 92 - Violet
    (170, 0, 170),      # 93 - Fuchsia
    (170, 0, 85),       # 94 - Raspberry
    (255, 85, 85),      # 95 - Coral
    (255, 128, 85),     # 96 - Light Coral
    (255, 170, 85),     # 97 - Peach
    (255, 213, 85),     # 98 - Cream
    (213, 255, 85),     # 99 - Yellow Green Light
    (170, 255, 85),     # 100 - Bright Lime
    (85, 255, 85),      # 101 - Light Green
    (85, 255, 128),     # 102 - Mint Green
    (85, 255, 170),     # 103 - Aqua Mint
    (85, 255, 213),     # 104 - Pale Aqua
    (85, 213, 255),     # 105 - Light Azure
    (85, 170, 255),     # 106 - Baby Blue
    (85, 128, 255),     # 107 - Light Periwinkle
    (85, 85, 255),      # 108 - Lavender
    (128, 85, 255),     # 109 - Light Violet
    (170, 85, 255),     # 110 - Light Fuchsia
    (213, 85, 255),     # 111 - Light Raspberry
    (255, 85, 213),     # 112 - Pink Light
    (255, 85, 170),     # 113 - Rose Light
    (85, 43, 0),        # 114 - Deep Brown
    (85, 85, 43),       # 115 - Deep Olive
    (43, 85, 0),        # 116 - Deep Green
    (0, 85, 43),        # 117 - Deep Teal
    (0, 85, 85),        # 118 - Deep Cyan
    (0, 43, 85),        # 119 - Deep Navy
    (43, 0, 85),        # 120 - Deep Indigo
    (85, 0, 85),        # 121 - Deep Purple
    (85, 0, 43),        # 122 - Deep Rose
    (255, 255, 255),    # 123 - Pure White
    (128, 128, 128),    # 124 - Medium Gray
    (192, 192, 192),    # 125 - Light Gray 2
    (64, 64, 64),       # 126 - Dark Gray 2
    (255, 128, 0),      # 127 - Bright Orange
]

# Precompute palette as numpy array for fast lookup
PALETTE_ARRAY = np.array(MAP_PALETTE, dtype=np.uint8)


def find_closest_palette_color(rgb: np.ndarray) -> int:
    """Find the index of the closest color in the Minecraft map palette."""
    # Calculate squared Euclidean distance to all palette colors
    distances = np.sum((PALETTE_ARRAY - rgb) ** 2, axis=1)
    return int(np.argmin(distances))


def image_to_map_art(image: Image.Image, map_size: int = 128, dither: bool = True) -> np.ndarray:
    """
    Convert a PIL Image to Minecraft map art pixel indices.

    Args:
        image: PIL Image to convert
        map_size: Size of output map (128x128 for standard map, 256x256 for large)
        dither: Whether to apply Floyd-Steinberg dithering

    Returns:
        2D numpy array of palette indices (map_size x map_size)
    """
    # Resize image to map size maintaining aspect ratio
    img = image.copy()
    img.thumbnail((map_size, map_size), Image.Resampling.LANCZOS)

    # Create a new image with exact map size, centered
    canvas = Image.new('RGB', (map_size, map_size), (128, 128, 128))
    x_offset = (map_size - img.width) // 2
    y_offset = (map_size - img.height) // 2
    canvas.paste(img, (x_offset, y_offset))

    # Convert to numpy array
    arr = np.array(canvas, dtype=np.uint8)

    if dither:
        # Floyd-Steinberg dithering
        return floyd_steinberg_dither(arr, map_size)
    else:
        # Simple nearest color
        h, w = arr.shape[:2]
        result = np.zeros((h, w), dtype=np.uint8)
        for y in range(h):
            for x in range(w):
                result[y, x] = find_closest_palette_color(arr[y, x])
        return result


def floyd_steinberg_dither(arr: np.ndarray, map_size: int) -> np.ndarray:
    """Apply Floyd-Steinberg dithering for better quality."""
    h, w = arr.shape[:2]
    # Work on a float copy for error diffusion
    work = arr.astype(np.float32)
    result = np.zeros((h, w), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            old_pixel = work[y, x].copy()
            new_color_idx = find_closest_palette_color(old_pixel.astype(np.uint8))
            new_pixel = PALETTE_ARRAY[new_color_idx].astype(np.float32)
            result[y, x] = new_color_idx

            error = old_pixel - new_pixel

            # Distribute error to neighboring pixels
            if x + 1 < w:
                work[y, x + 1] += error * 7 / 16
            if y + 1 < h:
                if x > 0:
                    work[y + 1, x - 1] += error * 3 / 16
                work[y + 1, x] += error * 5 / 16
                if x + 1 < w:
                    work[y + 1, x + 1] += error * 1 / 16

    return result


def create_contact_sheet(images: List[Image.Image], thumbs_per_row: int = 5,
                         thumb_size: Tuple[int, int] = (256, 256),
                         padding: int = 10, label_height: int = 30) -> Image.Image:
    """Create a contact sheet from a list of images."""
    n = len(images)
    rows = (n + thumbs_per_row - 1) // thumbs_per_row

    sheet_width = thumbs_per_row * thumb_size[0] + (thumbs_per_row + 1) * padding
    sheet_height = rows * (thumb_size[1] + label_height) + (rows + 1) * padding

    sheet = Image.new('RGB', (sheet_width, sheet_height), (240, 240, 240))

    for idx, img in enumerate(images):
        row = idx // thumbs_per_row
        col = idx % thumbs_per_row

        x = padding + col * (thumb_size[0] + padding)
        y = padding + row * (thumb_size[1] + label_height + padding)

        # Resize and paste thumbnail
        thumb = img.copy()
        thumb.thumbnail(thumb_size, Image.Resampling.LANCZOS)
        sheet.paste(thumb, (x, y))

        # Add label (would need ImageDraw for text)
        # Placeholder - in real implementation, draw text with PIL.ImageDraw

    return sheet


def process_photos(input_dir: Path, output_dir: Path, map_size: int = 128,
                   max_photos: int = 50, create_contact_sheet: bool = True) -> Dict[str, Any]:
    """
    Process all photos in input directory to map art.

    Returns:
        Dictionary with processing results and metadata
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    photo_files = sorted([f for f in input_dir.iterdir()
                          if f.suffix.lower() in image_extensions])

    if not photo_files:
        print(f"No images found in {input_dir}")
        return {"error": "No images found"}

    photo_files = photo_files[:max_photos]
    print(f"Processing {len(photo_files)} photos...")

    results = []
    map_data_list = []

    for idx, photo_path in enumerate(photo_files):
        print(f"  [{idx+1}/{len(photo_files)}] Processing {photo_path.name}...")

        try:
            img = Image.open(photo_path).convert('RGB')

            # Convert to map art
            map_indices = image_to_map_art(img, map_size=map_size, dither=True)

            # Save map data as JSON (for use in resource pack or scripts)
            map_data = {
                "id": idx,
                "source": photo_path.name,
                "original_size": list(img.size),
                "map_size": map_size,
                "palette_indices": map_indices.tolist()
            }
            map_data_list.append(map_data)

            # Save individual map JSON
            map_file = output_dir / f"map_{idx:03d}.json"
            with open(map_file, 'w') as f:
                json.dump(map_data, f)

            # Also save as PNG for preview (using palette colors)
            preview_arr = PALETTE_ARRAY[map_indices]
            preview_img = Image.fromarray(preview_arr.astype(np.uint8), 'RGB')
            preview_file = output_dir / f"map_{idx:03d}_preview.png"
            preview_img.save(preview_file)

            results.append({
                "index": idx,
                "source": photo_path.name,
                "map_file": str(map_file),
                "preview_file": str(preview_file),
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

    # Create contact sheet of previews
    if create_contact_sheet and map_data_list:
        previews = []
        for md in map_data_list:
            preview_file = output_dir / f"map_{md['id']:03d}_preview.png"
            if preview_file.exists():
                previews.append(Image.open(preview_file))

        if previews:
            contact = create_contact_sheet(previews)
            contact_file = output_dir / "contact_sheet.png"
            contact.save(contact_file)
            print(f"Contact sheet saved to {contact_file}")

    # Save summary
    summary = {
        "total_processed": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "map_size": map_size,
        "maps": results
    }

    summary_file = output_dir / "processing_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nProcessing complete!")
    print(f"  Successful: {summary['successful']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Output directory: {output_dir}")

    return summary


def generate_map_placement_script(map_data_list: List[Dict], start_pos: Tuple[int, int, int],
                                  spacing: int = 2, wall_height: int = 4) -> str:
    """
    Generate a Minecraft function/script to place map art on item frames.

    This creates a series of /setblock commands to place item frames with maps.
    """
    lines = [
        "# Auto-generated map art placement script",
        f"# Place maps starting at {start_pos}",
        ""
    ]

    x0, y0, z0 = start_pos

    for idx, md in enumerate(map_data_list):
        # Calculate position in a grid
        col = idx % 10
        row = idx // 10

        x = x0 + col * spacing
        y = y0 + (row % wall_height) * spacing
        z = z0 + (row // wall_height) * spacing

        # Map ID in the world (would need to be created via /give or data pack)
        map_id = idx  # This would be the actual map item ID

        lines.append(f"# Map {idx}: {md['source']} (original: {md['original_size'][0]}x{md['original_size'][1]})")
        nbt = '{{Item:{{id:"minecraft:filled_map",Count:1,tag:{{map:{map_id}}}}}},Facing:3}}'.format(map_id=map_id)
        lines.append(f"setblock {x} {y} {z} minecraft:item_frame{nbt}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Convert photos to Minecraft map art",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python photo_to_maps.py --input-dir ./pics --output-dir ./maps --map-size 128
  python photo_to_maps.py -i ../private-assets/photos -o ./assets/generic/maps --max 20
        """
    )
    parser.add_argument('-i', '--input-dir', type=Path, required=True,
                        help='Directory containing source photos')
    parser.add_argument('-o', '--output-dir', type=Path, required=True,
                        help='Output directory for map art files')
    parser.add_argument('-s', '--map-size', type=int, default=128,
                        choices=[128, 256],
                        help='Map size (128 or 256 pixels)')
    parser.add_argument('-m', '--max', type=int, default=50,
                        help='Maximum number of photos to process')
    parser.add_argument('--no-contact-sheet', action='store_true',
                        help='Skip contact sheet generation')
    parser.add_argument('--generate-placement', action='store_true',
                        help='Generate map placement script')
    parser.add_argument('--start-x', type=int, default=0,
                        help='Start X coordinate for placement script')
    parser.add_argument('--start-y', type=int, default=64,
                        help='Start Y coordinate for placement script')
    parser.add_argument('--start-z', type=int, default=0,
                        help='Start Z coordinate for placement script')

    args = parser.parse_args()

    if not args.input_dir.exists():
        print(f"Error: Input directory {args.input_dir} does not exist")
        return 1

    summary = process_photos(
        args.input_dir,
        args.output_dir,
        map_size=args.map_size,
        max_photos=args.max,
        create_contact_sheet=not args.no_contact_sheet
    )

    if args.generate_placement and summary.get("maps"):
        successful_maps = [m for m in summary["maps"] if m["status"] == "success"]
        # Load full map data for placement script
        map_data_list = []
        for m in successful_maps:
            with open(m["map_file"], 'r') as f:
                map_data_list.append(json.load(f))

        script = generate_map_placement_script(
            map_data_list,
            (args.start_x, args.start_y, args.start_z)
        )
        script_file = args.output_dir / "place_maps.mcfunction"
        with open(script_file, 'w') as f:
            f.write(script)
        print(f"Placement script saved to {script_file}")

    return 0


if __name__ == "__main__":
    exit(main())
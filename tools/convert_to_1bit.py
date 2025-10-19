#!/usr/bin/env python3
# /// script
# dependencies = [
#   "pillow",
# ]
# ///

"""
Convert animation frames to 1-bit monochrome using Floyd-Steinberg dithering.
This is required for Flipper Zero's 1-bit display.
"""

import os
from PIL import Image

def floyd_steinberg_dither(image):
    """
    Apply Floyd-Steinberg dithering to convert grayscale to 1-bit.

    Args:
        image: PIL Image in grayscale mode

    Returns:
        PIL Image in 1-bit mode
    """
    # Convert to grayscale first if not already
    img = image.convert('L')
    pixels = img.load()
    width, height = img.size

    # Floyd-Steinberg dithering
    for y in range(height):
        for x in range(width):
            old_pixel = pixels[x, y]
            new_pixel = 255 if old_pixel > 127 else 0
            pixels[x, y] = new_pixel

            quant_error = old_pixel - new_pixel

            # Distribute error to neighboring pixels
            if x + 1 < width:
                pixels[x + 1, y] = max(0, min(255, pixels[x + 1, y] + quant_error * 7 // 16))
            if x - 1 >= 0 and y + 1 < height:
                pixels[x - 1, y + 1] = max(0, min(255, pixels[x - 1, y + 1] + quant_error * 3 // 16))
            if y + 1 < height:
                pixels[x, y + 1] = max(0, min(255, pixels[x, y + 1] + quant_error * 5 // 16))
            if x + 1 < width and y + 1 < height:
                pixels[x + 1, y + 1] = max(0, min(255, pixels[x + 1, y + 1] + quant_error * 1 // 16))

    # Convert to 1-bit
    return img.convert('1')

def convert_frames_to_1bit(input_dir, output_dir):
    """
    Convert all frames in a directory to 1-bit monochrome.

    Args:
        input_dir: Directory containing color frames
        output_dir: Directory to save 1-bit frames
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Get all frame files
    frame_files = sorted([
        f for f in os.listdir(input_dir)
        if f.startswith('frame_') and f.endswith('.png')
    ])

    print(f"Converting {len(frame_files)} frames to 1-bit monochrome...")
    print(f"Using Floyd-Steinberg dithering for best quality")

    for i, filename in enumerate(frame_files):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        # Load image
        img = Image.open(input_path)

        # Convert to 1-bit with dithering
        img_1bit = floyd_steinberg_dither(img)

        # Save as 1-bit PNG
        img_1bit.save(output_path, 'PNG')

        if i % 10 == 0:
            print(f"  Converted {i}/{len(frame_files)}")

    print(f"\n✓ Converted {len(frame_files)} frames to {output_dir}/")
    print(f"  Output: 1-bit monochrome PNG (ready for Flipper Zero)")

if __name__ == "__main__":
    # Convert both animation sets
    print("=== Converting UP animation (top sweep) ===")
    convert_frames_to_1bit(
        "images/animation_frames",
        "images/animation_frames_1bit"
    )

    print("\n=== Converting DOWN animation (bottom sweep) ===")
    convert_frames_to_1bit(
        "images/animation_frames_down",
        "images/animation_frames_down_1bit"
    )

#!/usr/bin/env python3
# /// script
# dependencies = [
#   "pillow",
# ]
# ///

"""
Generate "through" animations where the image passes completely through the screen.
- Bottom → Top (enters from bottom, exits through top)
- Top → Bottom (enters from top, exits through bottom)
"""

import os
from PIL import Image

def floyd_steinberg_dither(image):
    """Apply Floyd-Steinberg dithering to convert grayscale to 1-bit."""
    img = image.convert('L')
    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            old_pixel = pixels[x, y]
            new_pixel = 255 if old_pixel > 127 else 0
            pixels[x, y] = new_pixel

            quant_error = old_pixel - new_pixel

            if x + 1 < width:
                pixels[x + 1, y] = max(0, min(255, pixels[x + 1, y] + quant_error * 7 // 16))
            if x - 1 >= 0 and y + 1 < height:
                pixels[x - 1, y + 1] = max(0, min(255, pixels[x - 1, y + 1] + quant_error * 3 // 16))
            if y + 1 < height:
                pixels[x, y + 1] = max(0, min(255, pixels[x, y + 1] + quant_error * 5 // 16))
            if x + 1 < width and y + 1 < height:
                pixels[x + 1, y + 1] = max(0, min(255, pixels[x + 1, y + 1] + quant_error * 1 // 16))

    return img.convert('1')

def generate_bottom_through_top(input_path, output_dir, num_frames=100):
    """
    Generate animation: bottom → center → exits through top.

    Frame 0-49: Enter from bottom to center
    Frame 50-99: Exit from center through top
    """
    source = Image.open(input_path).convert("RGBA")
    src_width, src_height = source.size

    FLIPPER_WIDTH = 128
    FLIPPER_HEIGHT = 64

    scale_factor = FLIPPER_WIDTH / src_width
    scaled_height = int(src_height * scale_factor)
    scaled_source = source.resize((FLIPPER_WIDTH, scaled_height), Image.Resampling.LANCZOS)

    os.makedirs(output_dir, exist_ok=True)

    center_y = (FLIPPER_HEIGHT - scaled_height) // 2

    for frame_num in range(num_frames):
        frame = Image.new("RGBA", (FLIPPER_WIDTH, FLIPPER_HEIGHT), (255, 255, 255, 0))

        if frame_num < num_frames // 2:
            # First half: enter from bottom
            progress = frame_num / (num_frames // 2 - 1)
            start_y = FLIPPER_HEIGHT
            current_y = int(start_y + (center_y - start_y) * progress)
        else:
            # Second half: exit through top
            progress = (frame_num - num_frames // 2) / (num_frames // 2 - 1)
            end_y = -scaled_height
            current_y = int(center_y + (end_y - center_y) * progress)

        frame.paste(scaled_source, (0, current_y), scaled_source)

        # Convert to 1-bit
        frame_1bit = floyd_steinberg_dither(frame)
        output_path = os.path.join(output_dir, f"frame_{frame_num:03d}.png")
        frame_1bit.save(output_path, "PNG")

        if frame_num % 10 == 0:
            print(f"  Frame {frame_num}/{num_frames-1}")

    print(f"✓ Generated {num_frames} frames in {output_dir}/")

def generate_top_through_bottom(input_path, output_dir, num_frames=100):
    """
    Generate animation: top → center → exits through bottom.

    Frame 0-49: Enter from top to center
    Frame 50-99: Exit from center through bottom
    """
    source = Image.open(input_path).convert("RGBA")
    src_width, src_height = source.size

    FLIPPER_WIDTH = 128
    FLIPPER_HEIGHT = 64

    scale_factor = FLIPPER_WIDTH / src_width
    scaled_height = int(src_height * scale_factor)
    scaled_source = source.resize((FLIPPER_WIDTH, scaled_height), Image.Resampling.LANCZOS)

    os.makedirs(output_dir, exist_ok=True)

    center_y = (FLIPPER_HEIGHT - scaled_height) // 2

    for frame_num in range(num_frames):
        frame = Image.new("RGBA", (FLIPPER_WIDTH, FLIPPER_HEIGHT), (255, 255, 255, 0))

        if frame_num < num_frames // 2:
            # First half: enter from top
            progress = frame_num / (num_frames // 2 - 1)
            start_y = -scaled_height
            current_y = int(start_y + (center_y - start_y) * progress)
        else:
            # Second half: exit through bottom
            progress = (frame_num - num_frames // 2) / (num_frames // 2 - 1)
            end_y = FLIPPER_HEIGHT
            current_y = int(center_y + (end_y - center_y) * progress)

        frame.paste(scaled_source, (0, current_y), scaled_source)

        # Convert to 1-bit
        frame_1bit = floyd_steinberg_dither(frame)
        output_path = os.path.join(output_dir, f"frame_{frame_num:03d}.png")
        frame_1bit.save(output_path, "PNG")

        if frame_num % 10 == 0:
            print(f"  Frame {frame_num}/{num_frames-1}")

    print(f"✓ Generated {num_frames} frames in {output_dir}/")

if __name__ == "__main__":
    input_image = "images/casino.png"

    print("=== Generating BOTTOM → THROUGH TOP animation ===")
    generate_bottom_through_top(
        input_image,
        "images/animation_frames_1bit_bottom_through_top"
    )

    print("\n=== Generating TOP → THROUGH BOTTOM animation ===")
    generate_top_through_bottom(
        input_image,
        "images/animation_frames_1bit_top_through_bottom"
    )

#!/usr/bin/env python3
# /// script
# dependencies = [
#   "pillow",
# ]
# ///

"""
Generate a 100-frame sweep animation where casino.png slides in from the bottom.
Each frame shows progressively more of the image sweeping up from behind the bottom edge.
Output frames are sized for Flipper Zero (128x64).
"""

import os
from PIL import Image

def generate_sweep_animation_down(input_path, output_dir, num_frames=100):
    """
    Generate sweep animation frames (bottom to center).

    Args:
        input_path: Path to source casino.png
        output_dir: Directory to save frames
        num_frames: Number of frames to generate (default 100)
    """
    # Load source image
    source = Image.open(input_path).convert("RGBA")
    src_width, src_height = source.size

    print(f"Source image: {src_width}x{src_height} ({source.mode})")

    # Flipper Zero display dimensions
    FLIPPER_WIDTH = 128
    FLIPPER_HEIGHT = 64

    # Calculate scaling to fit width
    scale_factor = FLIPPER_WIDTH / src_width
    scaled_height = int(src_height * scale_factor)
    scaled_width = FLIPPER_WIDTH

    # Resize source image to fit Flipper width
    scaled_source = source.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
    print(f"Scaled image: {scaled_width}x{scaled_height}")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Generate frames
    for frame_num in range(num_frames):
        # Create blank frame
        frame = Image.new("RGBA", (FLIPPER_WIDTH, FLIPPER_HEIGHT), (255, 255, 255, 0))

        # Calculate how much of the image is visible
        # Frame 0: fully hidden below screen
        # Frame 99: fully visible at final position
        progress = frame_num / (num_frames - 1)

        # Starting Y position (below screen)
        start_y = FLIPPER_HEIGHT
        # Ending Y position (centered vertically)
        end_y = (FLIPPER_HEIGHT - scaled_height) // 2

        # Current Y position for this frame
        current_y = int(start_y + (end_y - start_y) * progress)

        # Paste the scaled image at current position
        frame.paste(scaled_source, (0, current_y), scaled_source)

        # Save frame
        output_path = os.path.join(output_dir, f"frame_{frame_num:03d}.png")
        frame.save(output_path, "PNG")

        if frame_num % 10 == 0:
            print(f"Generated frame {frame_num}/{num_frames-1}")

    print(f"\n✓ Generated {num_frames} frames in {output_dir}/")
    print(f"  Frame size: {FLIPPER_WIDTH}x{FLIPPER_HEIGHT}")
    print(f"  Image sweep: from Y={start_y} to Y={end_y}")

if __name__ == "__main__":
    input_image = "images/casino.png"
    output_directory = "images/animation_frames_down"

    generate_sweep_animation_down(input_image, output_directory, num_frames=100)

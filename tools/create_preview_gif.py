#!/usr/bin/env python3
# /// script
# dependencies = [
#   "pillow",
# ]
# ///

"""
Create an animated GIF preview from animation frames.
"""

import os
from PIL import Image

def create_animated_gif(frames_dir, output_path, fps=30):
    """
    Create animated GIF from frames.

    Args:
        frames_dir: Directory containing frame_*.png files
        output_path: Output GIF path
        fps: Frames per second (default 30)
    """
    # Get all frame files sorted
    frame_files = sorted([
        os.path.join(frames_dir, f)
        for f in os.listdir(frames_dir)
        if f.startswith('frame_') and f.endswith('.png')
    ])

    print(f"Loading {len(frame_files)} frames...")

    # Load all frames
    frames = [Image.open(f).convert("RGB") for f in frame_files]

    # Calculate duration per frame in milliseconds
    duration_ms = int(1000 / fps)

    print(f"Creating animated GIF at {fps} FPS ({duration_ms}ms per frame)...")

    # Save as animated GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,  # Loop forever
        optimize=True
    )

    total_duration = len(frames) * duration_ms / 1000
    print(f"\n✓ Created {output_path}")
    print(f"  {len(frames)} frames @ {fps} FPS")
    print(f"  Duration: {total_duration:.1f} seconds")
    print(f"  Size: {os.path.getsize(output_path) / 1024:.1f} KB")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        frames_directory = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "preview.gif"
    else:
        frames_directory = "images/animation_frames"
        output_file = "preview_animation.gif"

    create_animated_gif(frames_directory, output_file, fps=30)

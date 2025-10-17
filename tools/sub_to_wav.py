#!/usr/bin/env python3
"""
Convert Flipper Zero .sub RAW files to WAV for visualization in Audacity
"""

import sys
import wave
import struct
import re

def parse_sub_file(filename):
    """Parse a .sub file and extract RAW timing data"""
    raw_data = []

    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('RAW_Data:'):
                # Extract timing values
                values = line.split(':', 1)[1].strip().split()
                raw_data.extend([int(v) for v in values])

    return raw_data

def raw_to_wav(raw_data, output_file, sample_rate=44100):
    """
    Convert RAW timing data to WAV file

    Args:
        raw_data: List of timing values (positive = ON, negative = OFF)
        output_file: Output WAV filename
        sample_rate: Audio sample rate (Hz)
    """

    # Convert timing (microseconds) to samples
    samples = []

    for timing in raw_data:
        # Convert microseconds to seconds, then to number of samples
        duration_sec = abs(timing) / 1_000_000
        num_samples = int(duration_sec * sample_rate)

        # Positive timing = high signal, negative = low signal
        if timing > 0:
            samples.extend([32767] * num_samples)  # Max amplitude
        else:
            samples.extend([0] * num_samples)      # Zero amplitude

    # Write WAV file
    with wave.open(output_file, 'w') as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)

        # Pack samples as 16-bit integers
        packed = struct.pack('<' + 'h' * len(samples), *samples)
        wav.writeframes(packed)

    print(f"✅ Converted {len(raw_data)} timing values to {output_file}")
    print(f"   Total samples: {len(samples)}")
    print(f"   Duration: {len(samples) / sample_rate:.3f} seconds")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 sub_to_wav.py <input.sub> [output.wav]")
        print("\nExample:")
        print("  python3 sub_to_wav.py my_signal.sub my_signal.wav")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.sub', '.wav')

    print(f"📡 Parsing {input_file}...")
    raw_data = parse_sub_file(input_file)

    if not raw_data:
        print("❌ No RAW_Data found in file!")
        sys.exit(1)

    print(f"📊 Converting to WAV...")
    raw_to_wav(raw_data, output_file)

    print(f"\n🎵 Open {output_file} in Audacity to visualize!")
    print("   Tip: In Audacity, use View → Zoom to see individual pulses")

if __name__ == '__main__':
    main()

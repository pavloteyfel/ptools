#!/usr/bin/env python3

import os
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
from typing import List, Tuple, Optional, Set


def parse_gnmap(file_path: str) -> List[Tuple[str, str]]:
    """
    Parse a GNMAP file to extract open ports for each host.

    Args:
        file_path (str): Path to the GNMAP file.

    Returns:
        List[Tuple[str, str]]: A list of tuples (ip, port) for every open port.
    """
    results: List[Tuple[str, str]] = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith("Host:"):
                    parts = line.split("\t")
                    # Extract the IP from the first section, second word.
                    ip = parts[0].split()[1]
                    if "Ports:" in line:
                        port_info = line.split("Ports:")[1].split(",")
                        for port in port_info:
                            port = port.strip()
                            if "/open/" in port:
                                port_number = port.split("/")[0]
                                results.append((ip, port_number))
    except Exception as error:
        raise RuntimeError(f"Failed to parse GNMAP file '{file_path}': {error}") from error
    return results


def parse_nmap_xml(file_path: str) -> List[Tuple[str, str]]:
    """
    Parse an Nmap XML file to extract open ports for each host.

    Args:
        file_path (str): Path to the Nmap XML file.

    Returns:
        List[Tuple[str, str]]: A list of tuples (ip, port) for every open port.
    """
    results: List[Tuple[str, str]] = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as error:
        raise RuntimeError(f"Error parsing XML file '{file_path}': {error}") from error

    for host in root.findall("host"):
        address = host.find("address")
        ip = address.attrib.get("addr") if address is not None else None
        if not ip:
            continue

        ports = host.find("ports")
        if ports is not None:
            for port in ports.findall("port"):
                state = port.find("state")
                if state is not None and state.attrib.get("state") == "open":
                    port_number = port.attrib.get("portid")
                    results.append((ip, port_number))
    return results


def create_argument_parser() -> ArgumentParser:
    """
    Create and return an argument parser for the script.

    Returns:
        ArgumentParser: Configured argument parser.
    """
    parser = ArgumentParser(
        description="Parse GNMAP or Nmap XML output and filter open ports."
    )
    parser.add_argument(
        "input_files",
        nargs="+",
        help="One or more paths to the GNMAP or Nmap XML files"
    )
    parser.add_argument(
        "--format", "-f",
        default="{ip} {port}",
        help="Output format (e.g., '{ip}:{port}' or 'Host {ip} has port {port} open')"
    )
    parser.add_argument(
        "--ports", "-p",
        help="Comma-separated list of ports to include (e.g., 22,80,443)"
    )
    return parser


def main() -> None:
    parser = create_argument_parser()
    args = parser.parse_args()

    output_format: str = args.format
    port_filter: Optional[Set[str]] = set(args.ports.split(",")) if args.ports else None

    all_entries: List[Tuple[str, str]] = []
    for file_path in args.input_files:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        try:
            if ext == ".gnmap":
                entries = parse_gnmap(file_path)
            elif ext == ".xml":
                entries = parse_nmap_xml(file_path)
            else:
                parser.error(f"Unsupported file format for '{file_path}'. Please use a .gnmap or .xml file.")
                continue
            all_entries.extend(entries)
        except Exception as error:
            print(error)
            continue  # Skip this file and continue with the next one

    # Remove duplicates by tracking seen (ip, port) combinations.
    seen: Set[Tuple[str, str]] = set()
    unique_entries: List[Tuple[str, str]] = []
    for entry in all_entries:
        if entry not in seen:
            seen.add(entry)
            unique_entries.append(entry)

    for ip, port in unique_entries:
        # Apply port filtering if specified.
        if port_filter and port not in port_filter:
            continue
        try:
            print(output_format.format(ip=ip, port=port))
        except KeyError as error:
            print(f"Formatting error for entry (ip: {ip}, port: {port}): missing key {error}")


if __name__ == "__main__":
    main()

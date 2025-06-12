#!/usr/bin/env python3

# to use you need to remove outdated gvm-tools (25.3.0-1) and install it with pipx:
# sudo apt remove --purge gvm-tools 
# pipx install gvm-tools

import argparse
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
import sys

# Optional color output
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Dummy:
        def __getattr__(self, _): return ''
    Fore = Style = Dummy()

# GVM CLI credentials
GVM_CLI = "gvm-cli"
USERNAME = "username"
PASSWORD = "password"

# Alive test mappings
ALIVE_TESTS = {
    "1": "ICMP &amp; TCP-ACK Service Ping",
    "2": "Consider Alive",
    "3": "TCP-SYN Service Ping",
    "4": "ARP Ping",
    "5": "ICMP &amp; ARP Ping",
    "6": "TCP-ACK Service &amp; ARP Ping",
    "7": "ICMP, TCP-ACK Service &amp; ARP Ping"
}

# User input mappings (number → name)
SCAN_CONFIG_INPUTS = {
    "1": "Full and fast",
    "2": "Base",
    "3": "Discovery",
    "4": "Host Discovery",
    "5": "System Discovery"
}

PORT_LIST_INPUTS = {
    "1": "All TCP and Nmap top 100 UDP",
    "2": "All IANA assigned TCP",
    "3": "All IANA assigned TCP and UDP"
}

# --- GVM Command Execution ---
def run_gvm_command(xml):
    try:
        result = subprocess.run(
            [GVM_CLI, "--gmp-username", USERNAME, "--gmp-password", PASSWORD, "socket", "--xml", xml],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}[!] GVM command failed:\n{e.stderr.strip()}")
        return None

def parse_response_id(xml_output):
    try:
        root = ET.fromstring(xml_output)
        return root.attrib.get("id")
    except ET.ParseError:
        print(f"{Fore.RED}[!] Invalid XML received.")
        return None

def get_named_ids(command, object_tag, name_tag="name"):
    xml = f"<{command}/>"
    response = run_gvm_command(xml)
    mapping = {}
    try:
        root = ET.fromstring(response)
        for obj in root.findall(object_tag):
            obj_id = obj.attrib.get("id")
            name = obj.find(name_tag).text.strip()
            mapping[name] = obj_id
        return mapping
    except Exception as e:
        print(f"{Fore.RED}[!] Failed to parse {command}: {e}")
        return {}

# --- Target and Task Creation ---
def create_target(hosts, name, port_list_id, alive_test):
    xml = f"""
<create_target>
  <name>{name}</name>
  <hosts>{hosts}</hosts>
  <port_list id="{port_list_id}"/>
  <alive_tests>{alive_test}</alive_tests>
</create_target>
"""
    print(f"{Fore.CYAN} Creating target: {name} ({hosts})")
    response = run_gvm_command(xml)
    target_id = parse_response_id(response)
    if target_id:
        print(f"{Fore.GREEN}  ✅ Target created (ID: {target_id})")
    else:
        print(f"{Fore.RED}  ❌ Failed to create target: {name}")
    return target_id

def create_task(name, target_id, config_id):
    xml = f"""
<create_task>
  <name>{name}</name>
  <config id="{config_id}"/>
  <target id="{target_id}"/>
</create_task>
"""
    print(f"{Fore.YELLOW}離 Creating task for: {name}")
    response = run_gvm_command(xml)
    task_id = parse_response_id(response)
    if task_id:
        print(f"{Fore.GREEN}  ✅ Task created (ID: {task_id})\n")
    else:
        print(f"{Fore.RED}  ❌ Failed to create task: {name}\n")
    return task_id

# --- CLI Arguments ---
def parse_args():
    parser = argparse.ArgumentParser(
        description="Create GVM targets and tasks from a targets file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("targets_file", help="File with list of targets (IP, domain, CIDR).")
    parser.add_argument("--task-name", "-tn", required=True, help="Base name for the tasks and targets.")
    parser.add_argument("--port-list", "-pl", default="1", choices=PORT_LIST_INPUTS.keys(), help="""Port list:
    1 - All TCP and Nmap top 100 UDP
    2 - All IANA assigned TCP
    3 - All IANA assigned TCP and UDP""")
    parser.add_argument("--alive-test", "-at", default="1", choices=ALIVE_TESTS.keys(), help="""Alive test:
    1 - ICMP & TCP-ACK Service Ping
    2 - Consider Alive
    3 - TCP-SYN Service Ping
    4 - ARP Ping
    5 - ICMP & ARP Ping
    6 - TCP-ACK Service & ARP Ping
    7 - ICMP, TCP-ACK Service & ARP Ping""")
    parser.add_argument("--scan-config", "-sc", default="1", choices=SCAN_CONFIG_INPUTS.keys(), help="""Scan config:
    1 - Full and fast
    2 - Base
    3 - Discovery
    4 - Host Discovery
    5 - System Discovery""")
    return parser.parse_args()

# --- Main Logic ---
def main():
    args = parse_args()

    try:
        with open(args.targets_file, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}[!] File not found: {args.targets_file}")
        sys.exit(1)

    print(f"{Fore.BLUE} Fetching scan configs and port lists from GVM...")

    scan_config_map = get_named_ids("get_configs", ".//config")
    port_list_map = get_named_ids("get_port_lists", ".//port_list")

    scan_config_name = SCAN_CONFIG_INPUTS[args.scan_config]
    port_list_name = PORT_LIST_INPUTS[args.port_list]

    scan_config_id = scan_config_map.get(scan_config_name)
    port_list_id = port_list_map.get(port_list_name)

    if not scan_config_id or not port_list_id:
        print(f"{Fore.RED}[!] Failed to resolve scan config or port list ID.")
        print(f"Looking for scan config: {scan_config_name}")
        print(f"Found scan configs: {list(scan_config_map.keys())}")
        print(f"Looking for port list: {port_list_name}")
        print(f"Found port lists: {list(port_list_map.keys())}")
        sys.exit(1)

    print(f"{Fore.MAGENTA} Creating tasks from {args.targets_file}")
    print(f"{Style.DIM}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    for idx, line in enumerate(lines, start=1):
        hosts = line.strip()
        target_name = f"{args.task_name}_{idx}"
        target_id = create_target(hosts, target_name, port_list_id, ALIVE_TESTS[args.alive_test])
        if target_id:
            create_task(target_name, target_id, scan_config_id)

if __name__ == "__main__":
    main()

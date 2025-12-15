#!/usr/bin/env python3
"""
Hashcat Brute-Force Script
Attempts to crack hashes using all available hash modes and rules
"""

import subprocess
import os
import sys
import re
from pathlib import Path
from datetime import datetime

# Configuration
HASH_FILE = "/home/shweb/hash.txt"
WORDLIST = "/home/shweb/base_dtu.txt"
OUTPUT_FILE = "cracked.txt"
LOG_FILE = "hashcrack.log"
# Modes to test
MODES_TO_TEST = [170, 6000, 4500, 4700, 18500, 100, 300]

# Hashcat rules directories (common locations)
RULES_PATHS = [
    "/usr/local/share/doc/hashcat/rules",
    os.path.expanduser("~/.hashcat/rules"),
    "/opt/hashcat/rules"
]


def log_message(message):
    """Log message to both console and log file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")


def get_hash_modes():
    """Extract all valid hash modes from hashcat"""
    log_message("Retrieving available hash modes...")
    try:
        result = subprocess.run(
            ["hashcat", "-hh"],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Extract mode numbers from help output
        modes = []
        for line in result.stdout.split("\n"):
            # Match lines like "    900 | MD4                              | Raw Hash"
            match = re.match(r'\s+(\d+)\s+\|', line)
            if match:
                modes.append(int(match.group(1)))

        log_message(f"Found {len(modes)} hash modes")
        return sorted(modes)
    except Exception as e:
        log_message(f"Error getting hash modes: {e}")
        return []


def get_rule_files():
    """Find all rule files in hashcat directories"""
    log_message("Searching for rule files...")
    rule_files = []

    for rules_path in RULES_PATHS:
        if os.path.isdir(rules_path):
            for file in Path(rules_path).glob("*.rule"):
                rule_files.append(str(file))
            # Also check subdirectories
            for file in Path(rules_path).glob("**/*.rule"):
                rule_files.append(str(file))

    # Remove duplicates
    rule_files = list(set(rule_files))
    log_message(f"Found {len(rule_files)} rule files")
    return rule_files


def run_hashcat(mode, rule_file=None):
    """Run hashcat with specified mode and optional rule file"""
    cmd = [
        "hashcat",
        "-m", str(mode),
        "-a", "0",  # Straight attack mode
        HASH_FILE,
        WORDLIST,
        "--potfile-path", "hashcat.potfile",
        "--outfile", OUTPUT_FILE,
        "--outfile-format", "2",  # plain:hash format
        "-o", OUTPUT_FILE,
        "--quiet",
        "-O",  # Enable optimized kernels
        "-w", "4"  # Workload profile 4 (nightmare - maximum power)
    ]

    if rule_file:
        cmd.extend(["-r", rule_file])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30000 # 5 minute timeout per attempt
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        log_message(f"  Timeout for mode {mode}" + (f" with rule {os.path.basename(rule_file)}" if rule_file else ""))
        return False
    except Exception as e:
        # Silently skip invalid combinations
        return False


def check_if_cracked():
    """Check if hash has been cracked by reading potfile"""
    potfile = "hashcat.potfile"
    if os.path.exists(potfile):
        try:
            with open(potfile, "r") as f:
                content = f.read()
                if content.strip():
                    return True
        except:
            pass
    return False


def main():
    """Main execution function"""
    log_message("=" * 60)
    log_message("Starting Hashcat Brute-Force Attack")
    log_message("=" * 60)
    log_message(f"Hash file: {HASH_FILE}")
    log_message(f"Wordlist: {WORDLIST}")
    log_message(f"Output file: {OUTPUT_FILE}")
    log_message("")

    # Verify files exist
    if not os.path.exists(HASH_FILE):
        log_message(f"ERROR: Hash file not found: {HASH_FILE}")
        sys.exit(1)

    if not os.path.exists(WORDLIST):
        log_message(f"ERROR: Wordlist not found: {WORDLIST}")
        sys.exit(1)

    # Get hash modes and rules
    hash_modes = get_hash_modes()
    rule_files = get_rule_files()

    if not hash_modes:
        log_message("ERROR: No hash modes found. Is hashcat installed?")
        sys.exit(1)

    log_message("")
    log_message(f"Total combinations to try: {len(hash_modes) * (len(rule_files) + 1)}")
    log_message("Starting attacks...")
    log_message("")

    attempts = 0
    successful = 0

    # Try specific modes without rules first
    for mode in MODES_TO_TEST:
        if mode not in hash_modes:
            log_message(f"Skipping mode {mode} (not available)")
            continue

        attempts += 1
        log_message(f"[{attempts}] Trying mode {mode} (no rules)")

        if run_hashcat(mode):
            successful += 1
            log_message(f"  SUCCESS! Hash cracked with mode {mode}")

        if check_if_cracked():
            log_message("Hash successfully cracked! Check cracked.txt for results")
            log_message(f"Total attempts: {attempts}")
            log_message(f"Successful runs: {successful}")
            return

    # Try specific modes with each rule file
    for mode in MODES_TO_TEST:
        if mode not in hash_modes:
            continue
        for rule_file in rule_files:
            attempts += 1
            rule_name = os.path.basename(rule_file)
            log_message(f"[{attempts}] Trying mode {mode} with rule {rule_name}")

            if run_hashcat(mode, rule_file):
                successful += 1
                log_message(f"  SUCCESS! Hash cracked with mode {mode} and rule {rule_name}")

            if check_if_cracked():
                log_message("Hash successfully cracked! Check cracked.txt for results")
                log_message(f"Total attempts: {attempts}")
                log_message(f"Successful runs: {successful}")
                return

    log_message("")
    log_message("=" * 60)
    log_message("Attack completed")
    log_message(f"Total attempts: {attempts}")
    log_message(f"Successful runs: {successful}")

    if check_if_cracked():
        log_message("Hash was cracked! Check cracked.txt for results")
    else:
        log_message("Hash was NOT cracked with available modes and rules")
    log_message("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_message("\nScript interrupted by user")
        sys.exit(1)

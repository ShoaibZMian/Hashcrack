#!/usr/bin/env python3
"""
Hashcat Brute-Force Script - Auto-detect paths
Attempts to crack hashes using all available hash modes and rules
"""

import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime

# Configuration
HASH_FILE = "/home/shweb/hash.txt"
WORDLIST = "/home/shweb/wordlists/rockyou.txt"
OUTPUT_FILE = "cracked.txt"
LOG_FILE = "hashcrack.log"

# Modes to test (SHA-1 variants as detected by hashcat)
MODES_TO_TEST = [170, 6000, 300, 4500, 4700, 18500,100]


def log_message(message):
    """Log message to both console and log file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")


def find_hashcat():
    """Find hashcat binary path"""
    try:
        result = subprocess.run(
            ["which", "hashcat"],
            capture_output=True,
            text=True
        )
        hashcat_path = result.stdout.strip()
        if hashcat_path and os.path.exists(hashcat_path):
            log_message(f"Found hashcat at: {hashcat_path}")
            return hashcat_path
        else:
            log_message("ERROR: hashcat not found in PATH")
            return None
    except Exception as e:
        log_message(f"Error finding hashcat: {e}")
        return None


def find_rule_files():
    """Find all rule files by searching common locations"""
    log_message("Searching for rule files...")
    rule_files = []

    # Search in common locations
    search_paths = [
        "/usr/share/hashcat",
        "/usr/local/share/hashcat",
        "/usr/local/share/doc/hashcat",
        "/usr/share/doc/hashcat",
        os.path.expanduser("~/.hashcat"),
        "/opt/hashcat"
    ]

    for search_path in search_paths:
        if os.path.isdir(search_path):
            log_message(f"  Searching in {search_path}")
            for rule_file in Path(search_path).rglob("*.rule"):
                rule_files.append(str(rule_file))

    # Remove duplicates
    rule_files = list(set(rule_files))
    log_message(f"Found {len(rule_files)} rule files")
    return sorted(rule_files)


def run_hashcat(hashcat_path, mode, rule_file=None):
    """Run hashcat with specified mode and optional rule file"""
    cmd = [
        hashcat_path,
        "-m", str(mode),
        "-a", "0",
        "-w", "4",
        "-O",
        "--force",
        "--outfile", OUTPUT_FILE,
        HASH_FILE,
        WORDLIST
    ]

    if rule_file:
        cmd.extend(["-r", rule_file])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        log_message(f"  Timeout for mode {mode}" + (f" with rule {os.path.basename(rule_file)}" if rule_file else ""))
        return False
    except Exception:
        return False


def check_if_cracked():
    """Check if hash has been cracked by reading output file"""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r") as f:
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

    # Find hashcat
    hashcat_path = find_hashcat()
    if not hashcat_path:
        log_message("ERROR: Cannot proceed without hashcat")
        sys.exit(1)

    # Find rule files
    rule_files = find_rule_files()

    log_message("")
    log_message(f"Total combinations to try: {len(MODES_TO_TEST) * (len(rule_files) + 1)}")
    log_message("Starting attacks...")
    log_message("")

    attempts = 0
    successful = 0

    # Try specific modes without rules first
    for mode in MODES_TO_TEST:
        attempts += 1
        log_message(f"[{attempts}] Trying mode {mode} (no rules)")

        if run_hashcat(hashcat_path, mode):
            successful += 1
            log_message(f"  SUCCESS! Hash cracked with mode {mode}")

        if check_if_cracked():
            log_message("Hash successfully cracked! Check cracked.txt for results")
            log_message(f"Total attempts: {attempts}")
            log_message(f"Successful runs: {successful}")
            return

    # Try specific modes with each rule file
    for mode in MODES_TO_TEST:
        for rule_file in rule_files:
            attempts += 1
            rule_name = os.path.basename(rule_file)
            log_message(f"[{attempts}] Trying mode {mode} with rule {rule_name}")

            if run_hashcat(hashcat_path, mode, rule_file):
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

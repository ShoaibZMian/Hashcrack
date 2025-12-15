#!/usr/bin/env python3
"""
Hash Analyzer
Analyzes hash types and suggests appropriate hashcat modes
"""

import re
import sys

# Mapping algorithm names to hashcat modes
ALGORITHM_TO_MODES = {
    "MD5": [0, 20, 10],  # MD5, md5($salt.$pass), md5($pass.$salt)
    "NTLM": [1000],
    "SHA-1": [100, 110, 120, 170],  # SHA1, sha1($pass.$salt), sha1($salt.$pass), sha1(utf16le($pass))
    "RIPEMD-160": [6000],
    "SHA-256": [1400, 1410, 1420, 1470],  # SHA256, sha256($pass.$salt), sha256($salt.$pass), sha256(utf16le($pass))
}


def analyze_hash(hash_str):
    """Analyze a hash string and return its properties"""
    analysis = {}

    analysis["hash"] = hash_str
    analysis["length"] = len(hash_str)

    if re.fullmatch(r"[0-9a-fA-F]+", hash_str):
        analysis["encoding"] = "hex"
        analysis["bits"] = len(hash_str) * 4
    elif re.fullmatch(r"[A-Za-z0-9+/=]+", hash_str):
        analysis["encoding"] = "base64"
        analysis["bits"] = "unknown (base64)"
    else:
        analysis["encoding"] = "unknown"
        analysis["bits"] = "unknown"

    # Detect simple salt formats
    analysis["salt_detected"] = ":" in hash_str

    # Candidate algorithms (heuristic)
    candidates = []
    if analysis["encoding"] == "hex":
        if analysis["length"] == 32:
            candidates = ["MD5", "NTLM"]
        elif analysis["length"] == 40:
            candidates = ["SHA-1", "RIPEMD-160"]
        elif analysis["length"] == 64:
            candidates = ["SHA-256"]

    analysis["candidates"] = candidates

    # Convert algorithm names to hashcat mode numbers
    suggested_modes = []
    for algo in candidates:
        if algo in ALGORITHM_TO_MODES:
            suggested_modes.extend(ALGORITHM_TO_MODES[algo])

    analysis["suggested_modes"] = list(set(suggested_modes))  # Remove duplicates

    return analysis


def print_analysis(analysis):
    """Pretty print hash analysis"""
    print("=" * 60)
    print("Hash Analysis")
    print("=" * 60)
    print(f"Hash: {analysis['hash']}")
    print(f"  Length: {analysis['length']} chars")
    print(f"  Encoding: {analysis['encoding']}")
    print(f"  Bit length: {analysis['bits']}")
    print(f"  Salt detected: {analysis['salt_detected']}")
    print(f"  Candidate algorithms: {analysis['candidates']}")
    print(f"  Suggested hashcat modes: {analysis['suggested_modes']}")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 hash_analyzer.py <hash_file>")
        print("   or: python3 hash_analyzer.py <hash_string>")
        sys.exit(1)

    input_arg = sys.argv[1]

    # Check if it's a file or a hash string
    import os
    if os.path.exists(input_arg):
        # Read from file
        with open(input_arg, "r") as f:
            hashes = [line.strip() for line in f if line.strip()]

        for h in hashes:
            analysis = analyze_hash(h)
            print_analysis(analysis)
            print()
    else:
        # Treat as hash string
        analysis = analyze_hash(input_arg)
        print_analysis(analysis)

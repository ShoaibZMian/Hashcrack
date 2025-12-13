# Hashcrack

Automated hashcat brute-force script for password hash cracking in security testing environments.

## Overview

This project contains Python scripts that automate the process of cracking password hashes using hashcat. The scripts systematically test multiple hash modes and rule files to identify the correct hash algorithm and crack the password.

## Features

- Automatically detects available hashcat hash modes
- Tests multiple hash type combinations
- Applies various rule files for password transformations
- Comprehensive logging of all attempts
- Automatic detection of successful cracks
- Configurable timeout and workload settings

## Scripts

- **hashcrack.py** - Main script with full hash mode enumeration
- **newhashcrack.py** - Streamlined version with auto-detection of paths
- **hashcrack2.py** - Alternative variant

## Requirements

- Python 3.6+
- hashcat installed and accessible in PATH
- Wordlist file (e.g., rockyou.txt)
- Target hash file

## Configuration

Edit the configuration variables at the top of the script:

```python
HASH_FILE = "/path/to/hash.txt"      # File containing the hash to crack
WORDLIST = "/path/to/wordlist.txt"   # Wordlist for dictionary attack
OUTPUT_FILE = "cracked.txt"           # Output file for cracked passwords
LOG_FILE = "hashcrack.log"            # Log file for progress tracking
```

### Hash Modes

The scripts test specific hash modes by default:

- 170: SHA-1
- 6000: RIPEMD-160
- 300: MySQL4.1/MySQL5
- 4500: sha1(sha1($pass))
- 4700: SHA-1(Base64)
- 18500: sha1(md5($pass))
- 100: SHA-1
- 27200: Ruby on Rails Restful Auth

## Usage

### Basic Usage

```bash
./hashcrack.py
```

or

```bash
python3 hashcrack.py
```

### What It Does

1. Verifies hash file and wordlist exist
2. Detects available hashcat hash modes
3. Locates all available rule files
4. Tests each configured hash mode without rules
5. Tests each hash mode with each available rule file
6. Logs all attempts and results
7. Stops when hash is successfully cracked

## Output Files

- **cracked.txt** - Contains cracked passwords in plain:hash format
- **hashcrack.log** - Detailed log of all attempts and results
- **hashcat.potfile** - Hashcat's potfile for tracking cracked hashes

## Performance Settings

The scripts use aggressive performance settings:

- `-O`: Enable optimized kernels
- `-w 4`: Workload profile 4 (nightmare mode - maximum power)
- `--force`: Force execution (used in newhashcrack.py)

## Example Output

```
[2025-10-10 12:00:00] Starting Hashcat Brute-Force Attack
[2025-10-10 12:00:00] Hash file: /home/user/hash.txt
[2025-10-10 12:00:00] Wordlist: /home/user/rockyou.txt
[2025-10-10 12:00:01] Found 312 hash modes
[2025-10-10 12:00:02] Found 47 rule files
[2025-10-10 12:00:02] Total combinations to try: 2496
[2025-10-10 12:00:02] [1] Trying mode 170 (no rules)
[2025-10-10 12:00:15] SUCCESS! Hash cracked with mode 170
```

## Legal and Ethical Use

**IMPORTANT**: This tool is designed for authorized security testing and educational purposes only.

- Only use on systems you own or have explicit permission to test
- Intended for security research and learning environments
- Unauthorized access to computer systems is illegal
- Always comply with applicable laws and regulations

## Troubleshooting

### Hashcat Not Found
```
ERROR: hashcat not found in PATH
```
Install hashcat: `sudo apt install hashcat` (Debian/Ubuntu)

### Wordlist Not Found
```
ERROR: Wordlist not found
```
Update the `WORDLIST` path in the script or download rockyou.txt

### No Hash Modes Found
```
ERROR: No hash modes found. Is hashcat installed?
```
Verify hashcat is installed: `hashcat --version`

### Timeout Issues

Increase the timeout value in the `run_hashcat()` function if needed (default: 300 seconds)

## License

For educational purposes in security coursework.

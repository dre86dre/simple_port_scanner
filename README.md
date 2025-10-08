# Simple TCP Port Scanner (IPv4 + IPv6)

A small, easy-to-read Python TCP port scanner with support for both IPv4 and IPv6, a preset "well-known ports" mode, and simple concurrency. Intended for learning and lightweight network troubleshooting - only use on systems you own or have explicit permission to test.

---

## Features

- Resolve hostnames to IPv4 and/or IPv6 addresses
- Scan single ports, ranges, comma-separated lists, or a preset "well-known" list
- Concurrent scanning using ```ThreadPoolExecutor``` for speed
- Minimal dependencies (Python 3 standard library only)
- Compact and easy-to-read single-file script

---

## Files

- ```simple_port_scanner.py``` - the scanner script (single-file)

---

## Requirements

- Python 3.7+ (uses ```concurrent.futures``` and standard socket API)
- No external libraries required

---

## Installation

1. Save the ```simple_port_scanner.py``` script to a directory on your machine.
2. Make it executable (optional):

```
chmod +x simple_scanner.py
```

---

## Usage

```
python3 simple_scanner.py [options] <target>
```
Or, if executable:
```
./simple_scanner.py [options] <target>
```

### Examples

- Scan default ports (1–1024) on ```example.com``` (both IPv4 & IPv6 by default):
```
python3 simple_scanner.py example.com
```

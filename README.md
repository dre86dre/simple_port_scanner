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
- Scan a single port:
```
python3 simple_scanner.py -p 22 example.com
```
- Scan multiple comma-separated ports and ranges:
```
python3 simple_scanner.py -p 22,80,443,8000-8010 example.com
```
- Scan the preset well-known ports:
```
python3 simple_scanner.py --well-known example.com
```
- Force IPv6-only resolution/scan:
```
python3 simple_scanner.py --ipv6 example.com
```
- Force IPv4-only:
```
python3 simple_scanner.py --ipv4 example.com
```
- Increase concurrency and change timeout (tune carefully):
```
python3 simple_scanner.py -w 300 -t 0.5 -p 1-65535 example.com
```

---

## Output

- Prints resolved addresses (IPv4/IPv6)
- Prints ```"[+] Port <n> is open"``` for each open port discovered
- Prints a final summary with a list of open ports (if any)

### Example output

```
============================================================
Target: example.com
  - 93.184.216.34 (IPv4)
Ports: 3  Timeout: 1.0s  Workers: 200
Started: 2025-10-07T12:34:56.789012
============================================================
[+] Port 80 is open
============================================================
Finished: 2025-10-07T12:35:00.123456
Open ports: 80
============================================================
```

---

## Notes, caveats & troubleshooting

- ###Authorization: Port scanning can be intrusive and may violate terms of service or local laws if done without permission. Always get explicit authorization before scanning systems you do not own.
- Link-local IPv6: Some IPv6 addresses (e.g., ```fe80::/...```) are link-local and require a scope/zone identifier (like ```%eth0```) to be reachable. The script uses ```getaddrinfo()``` and should work for general cases, but link-local scenarios may need extra care.
- Performance & detection: Increasing --workers speeds scans but can trigger IDS/IPS, rate-limiting, or overwhelm your network/host. Tune --workers and --timeout carefully.
- Permissions: No special root privileges are required for TCP connect scans, but some environments may restrict outbound connections.
- IPv6 support: The scanner attempts both IPv4 and IPv6 by default. If you only need one family, use --ipv4 or --ipv6 to avoid unnecessary resolution attempts.

#!/usr/bin/env python3
"""
Simple TCP port scanner (IPv4 + IPv6) with a "well-known ports" mode.
Use only against hosts you have explicit permission to test.

Features:
- Resolve hostname to IPv4 and/or IPv6 addresses
- Scan a list/range of ports or a preset "well-known" list
- Concurrent scanning using ThreadPoolExecutor for speed
- Lightweight and easy to read
"""
import argparse
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# A small preset list of commonly-used "well-known" ports.
WELL_KNOWN = [
    20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 88, 110, 123, 135,
    139, 143, 161, 162, 389, 443, 445, 465, 514, 587, 631, 636,
    993, 995, 1080, 1194, 1433, 1521, 1723, 2049, 3306, 3389,
    5900, 6379, 8000, 8080, 8443
]

def parse_ports(text):
    """
    Parse a port specification string into a sorted list of unique ports.
    Accepts:
      - single ports: "22"
      - ranges: "1-1024"
      - comma lists: "22,80,443"
      - mixed: "22,80-90"
    Invalid ports outside 1-65535 are filtered out.
    """
    parts = [p.strip() for p in text.split(",") if p.strip()]  # split on commas
    ports = set()
    for p in parts:
        if "-" in p:
            # Range like "start-end"
            a, b = p.split("-", 1)
            ports.update(range(int(a), int(b) + 1))
        else:
            # Single port
            ports.add(int(p))
    # Keep ports within valid TCP port bounds and return sorted list
    return sorted(p for p in ports if 1 <= p <= 65535)

def resolve(target, force_ipv=None):
    """
    Resolve a hostname into a list of (family, ip) tuples.
    - force_ipv can be socket.AF_INET to force IPv4 only,
      socket.AF_INET6 to force IPv6 only, or None to try both.
    The function deduplicates identical (family, ip) entries.
    """
    families = []
    if force_ipv == socket.AF_INET:
        families = [socket.AF_INET]
    elif force_ipv == socket.AF_INET6:
        families = [socket.AF_INET6]
    else:
        families = [socket.AF_INET, socket.AF_INET6]

    seen = []
    for fam in families:
        try:
            # getaddrinfo returns address info entries; we only need the family and sockaddr
            for ai in socket.getaddrinfo(target, None, family=fam, type=socket.SOCK_STREAM):
                family, sockaddr = ai[0], ai[4]
                ip = sockaddr[0]  # sockaddr is (ip, port) for IPv4, (ip, port, flow, scope) for IPv6
                if (family, ip) not in seen:
                    seen.append((family, ip))
        except socket.gaierror:
            # No addresses found for this family; continue to next family
            continue
    return seen

def try_port_on_addrs(addrs, port, timeout):
    """
    Attempt to connect to each resolved address (addrs is a list of (family, ip)) on the given port.
    If any address accepts a connection, return True (port considered open).
    Each socket uses the provided timeout.
    """
    for family, ip in addrs:
        try:
            # Create a socket for the appropriate address family
            with socket.socket(family, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)  # per-socket timeout (doesn't change global default)
                # For IPv6 sockaddr we need a 4-tuple (ip, port, flowinfo, scopeid)
                sockaddr = (ip, port) if family == socket.AF_INET else (ip, port, 0, 0)
                # connect_ex returns 0 on success (port open), error code otherwise
                if s.connect_ex(sockaddr) == 0:
                    return True
        except Exception:
            # Ignore per-address exceptions (unreachable network, permissions, etc.)
            # and try the next resolved address.
            continue
    return False

def main():
    # Basic CLI parsing with helpful defaults
    p = argparse.ArgumentParser(description="Small IPv4+IPv6 TCP port scanner (use responsibly).")
    p.add_argument("target", help="hostname or IP")
    p.add_argument("-p", "--ports", default="1-1024",
                   help="ports (e.g. '22', '1-1024', '22,80-90')")
    p.add_argument("--well-known", action="store_true", help="scan preset well-known ports")
    p.add_argument("--ipv4", action="store_true", help="only resolve IPv4")
    p.add_argument("--ipv6", action="store_true", help="only resolve IPv6")
    p.add_argument("-t", "--timeout", type=float, default=1.0, help="socket timeout (seconds)")
    p.add_argument("-w", "--workers", type=int, default=200, help="concurrent worker threads")
    args = p.parse_args()

    # Choose which ports to scan (preset or parsed expression)
    ports = sorted(set(WELL_KNOWN)) if args.well_known else parse_ports(args.ports)
    if not ports:
        print("No ports selected.", file=sys.stderr)
        sys.exit(1)

    # Decide whether to prefer IPv4 or IPv6 based on flags
    prefer = None
    if args.ipv4:
        prefer = socket.AF_INET
    if args.ipv6:
        prefer = socket.AF_INET6

    # Resolve the target to addresses to try
    addrs = resolve(args.target, force_ipv=prefer)
    if not addrs:
        kind = "IPv6" if args.ipv6 else ("IPv4" if args.ipv4 else "any")
        print(f"Could not resolve {args.target} for {kind} addresses.", file=sys.stderr)
        sys.exit(1)

    # Print a brief header with the resolved addresses and chosen settings
    print("="*60)
    print(f"Target: {args.target}")
    for fam, ip in addrs:
        print(f"  - {ip} ({'IPv6' if fam == socket.AF_INET6 else 'IPv4'})")
    print(f"Ports: {len(ports)}  Timeout: {args.timeout}s  Workers: {args.workers}")
    print("Started:", datetime.now().isoformat())
    print("="*60)

    # Use a thread pool to scan ports concurrently for speed
    open_ports = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        # Submit one task per port: try connecting to all resolved addresses for that port
        futures = {ex.submit(try_port_on_addrs, addrs, port, args.timeout): port for port in ports}
        for fut in as_completed(futures):
            port = futures[fut]
            try:
                if fut.result():  # If True, port is open on at least one address
                    print(f"[+] Port {port} is open")
                    open_ports.append(port)
            except Exception:
                # Unexpected worker error: ignore and continue scanning remaining ports
                pass

    # Final summary output
    print("="*60)
    print("Finished:", datetime.now().isoformat())
    if open_ports:
        print("Open ports:", ", ".join(map(str, sorted(open_ports))))
    else:
        print("No open ports found.")
    print("="*60)

if __name__ == "__main__":
    main()
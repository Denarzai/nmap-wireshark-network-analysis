#!/usr/bin/env python3
"""
parse_nmap.py — turn Nmap XML output (-oX) into a clean Markdown summary table.

Usage:
    python3 parse_nmap.py output/sV.xml
    python3 parse_nmap.py output/sV.xml > findings.md

Standard library only (xml.etree) — no dependencies to install.
"""
import sys
import xml.etree.ElementTree as ET


def parse(path):
    """Yield (host_ip, [(port, proto, state, service, version), ...])."""
    root = ET.parse(path).getroot()
    for host in root.findall("host"):
        addr_el = host.find("address[@addrtype='ipv4']")
        ip = addr_el.get("addr") if addr_el is not None else "unknown"

        rows = []
        for port in host.findall("./ports/port"):
            portid = port.get("portid")
            proto = port.get("protocol")

            state_el = port.find("state")
            state = state_el.get("state") if state_el is not None else "?"

            svc = port.find("service")
            if svc is not None:
                name = svc.get("name", "")
                # Stitch product + version + extrainfo into one readable string
                version = " ".join(
                    p for p in (
                        svc.get("product", ""),
                        svc.get("version", ""),
                        svc.get("extrainfo", ""),
                    ) if p
                ).strip()
            else:
                name, version = "", ""

            rows.append((portid, proto, state, name, version))

        # Sort numerically by port number
        rows.sort(key=lambda r: int(r[0]))
        yield ip, rows


def to_markdown(path):
    out = []
    for ip, rows in parse(path):
        out.append(f"### Host: `{ip}`\n")
        if not rows:
            out.append("_No ports reported._\n")
            continue
        out.append("| Port | Proto | State | Service | Version |")
        out.append("|---|---|---|---|---|")
        for portid, proto, state, name, version in rows:
            out.append(f"| {portid} | {proto} | {state} | {name} | {version} |")
        open_count = sum(1 for r in rows if r[2] == "open")
        out.append(f"\n_{open_count} open port(s)._\n")
    return "\n".join(out)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    try:
        print(to_markdown(sys.argv[1]))
    except (ET.ParseError, FileNotFoundError) as e:
        print(f"error: could not parse '{sys.argv[1]}': {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

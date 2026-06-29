#!/usr/bin/env bash
#
# recon.sh — reproduce the Nmap reconnaissance sequence from this lab and
#            capture the resulting traffic to a .pcap, so the raw artifacts
#            can be regenerated instead of shipped stale.
#
# Run from the KALI attacker VM, inside the isolated lab network, against your
# own Metasploitable2 target. Requires root (for -sS, -O and packet capture).
#
#   sudo ./recon.sh <target-ip> [interface]
#
# Example:
#   sudo ./recon.sh 192.168.159.131 eth0
#
set -euo pipefail

# --- arguments ---------------------------------------------------------------
TARGET="${1:-}"
IFACE="${2:-eth0}"          # capture interface; default eth0 on Kali/VMware
if [[ -z "$TARGET" ]]; then
  echo "usage: sudo $0 <target-ip> [interface]" >&2
  exit 1
fi

# Must be root: SYN scan (-sS), OS detection (-O) and tcpdump all need raw sockets
if [[ "${EUID}" -ne 0 ]]; then
  echo "error: run as root (sudo) — raw-socket scans and capture require it" >&2
  exit 1
fi

OUTDIR="output"
mkdir -p "$OUTDIR"
STAMP="$(date +%Y%m%d-%H%M%S)"
PCAP="$OUTDIR/capture-$STAMP.pcap"

echo "[*] target=$TARGET  iface=$IFACE  outdir=$OUTDIR"

# --- start packet capture in the background ----------------------------------
# Filter to traffic between this host and the target so the pcap stays focused.
echo "[*] starting capture -> $PCAP"
tcpdump -i "$IFACE" -w "$PCAP" host "$TARGET" >/dev/null 2>&1 &
TCPDUMP_PID=$!

# Make sure tcpdump is stopped even if a scan fails or the script is interrupted
cleanup() {
  echo "[*] stopping capture (pid $TCPDUMP_PID)"
  kill "$TCPDUMP_PID" 2>/dev/null || true
  wait "$TCPDUMP_PID" 2>/dev/null || true
  echo "[*] pcap written: $PCAP"
}
trap cleanup EXIT
sleep 1   # give tcpdump a moment to attach to the interface

# --- scan sequence -----------------------------------------------------------
# Each scan writes output in all three Nmap formats:
#   -oN human-readable   -oX XML (machine-parsable)   -oG grepable

echo "[*] 1/5 host discovery (-sn)"
nmap -sn "$TARGET" -oN "$OUTDIR/host-discovery.txt"

echo "[*] 2/5 SYN port scan (-sS)"
nmap -sS "$TARGET" -oN "$OUTDIR/syn-scan.txt" -oX "$OUTDIR/syn-scan.xml" -oG "$OUTDIR/syn-scan.gnmap"

echo "[*] 3/5 service & version detection (-sV)"
# -Pn skips host discovery (we already confirmed the host is up) to avoid a
# second round of probes and keep the capture clean.
nmap -Pn -sV "$TARGET" -oN "$OUTDIR/sV.txt" -oX "$OUTDIR/sV.xml"

echo "[*] 4/5 OS detection (-O)"
nmap -O "$TARGET" -oN "$OUTDIR/os-detect.txt" -oX "$OUTDIR/os-detect.xml"

echo "[*] 5/5 NSE scripts (banner, vuln, discovery)"
nmap --script banner    "$TARGET" -oN "$OUTDIR/nse-banner.txt"
nmap --script vuln      "$TARGET" -oN "$OUTDIR/nse-vuln.txt"
nmap --script discovery "$TARGET" -oN "$OUTDIR/nse-discovery.txt"

echo "[+] done. nmap output in $OUTDIR/ ; capture in $PCAP"
echo "[+] next: python3 scripts/parse_nmap.py $OUTDIR/sV.xml"

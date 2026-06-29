# Nmap command reference

The exact commands used in this lab, with a one-line purpose for each. Replace
the target IP with your own.

| Command | Purpose |
|---|---|
| `nmap -sn 192.168.159.131` | Host discovery only (ping sweep) — is the host alive? |
| `nmap -sS 192.168.159.131` | Stealth SYN ("half-open") port scan — list open ports |
| `nmap -Pn -sV 192.168.159.131` | Service + version detection (`-Pn` skips re-discovery) |
| `nmap -O 192.168.159.131` | OS detection via TCP/IP fingerprinting |
| `nmap --script banner 192.168.159.131` | Grab service banners from open ports |
| `nmap --script vuln 192.168.159.131` | Run the known-vulnerability NSE scripts |
| `nmap --script discovery 192.168.159.131` | Enumerate SMB shares, DNS, host metadata |

### Output formats

Add these flags to save results in parsable forms:

| Flag | Format |
|---|---|
| `-oN file.txt` | Normal, human-readable |
| `-oX file.xml` | XML (feed into `scripts/parse_nmap.py`) |
| `-oG file.gnmap` | Grepable |
| `-oA basename` | All three at once |

### Privilege notes

- `-sS` (SYN scan) and `-O` (OS detection) need raw sockets — run with `sudo`.
- Without root, Nmap falls back to a TCP connect scan (`-sT`), which completes
  the full handshake and is far noisier / more logged.

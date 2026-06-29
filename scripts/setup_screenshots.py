#!/usr/bin/env python3
"""
setup_screenshots.py — extract the screenshots embedded in the lab report
(.docx) and drop them into the screenshots/ tree with descriptive names.

A .docx is a ZIP archive; its images live in word/media/. This script copies
the relevant ones out and renames them to match how they're referenced in the
README. Standard library only.

Usage (run from the repo root):
    python3 scripts/setup_screenshots.py
    python3 scripts/setup_screenshots.py "report/i242091-i242082-Report-Project.docx"
"""
import os
import sys
import zipfile

# original media name in the .docx  ->  (subfolder, descriptive filename)
MAPPING = {
    "image1.png":  ("01-setup", "01-nmap-version.png"),
    "image2.png":  ("01-setup", "02-wireshark-version.png"),
    "image3.png":  ("01-setup", "03-metasploitable-vm.png"),
    "image4.png":  ("01-setup", "04-metasploitable-nat-adapter.png"),
    "image5.png":  ("01-setup", "05-kali-nat-adapter.png"),
    "image6.png":  ("01-setup", "06-metasploitable-ip.png"),
    "image7.png":  ("01-setup", "07-kali-ip.png"),
    "image8.png":  ("01-setup", "08-network-topology.png"),
    "image9.png":  ("02-nmap", "01-host-discovery-sn.png"),
    "image10.png": ("02-nmap", "02-syn-scan-sS.png"),
    "image11.png": ("02-nmap", "03-service-version-sV.png"),
    "image12.png": ("02-nmap", "04-os-detection-O.png"),
    "image14.png": ("02-nmap", "05-nse-banner.png"),
    "image16.png": ("02-nmap", "06-nse-vuln.png"),
    "image18.png": ("02-nmap", "07-nse-discovery.png"),
    "image22.png": ("03-wireshark", "01-capture-environment.png"),
    "image13.png": ("03-wireshark", "02-icmp-host-discovery.png"),
    "image15.png": ("03-wireshark", "03-syn-scan-capture.png"),
    "image17.png": ("03-wireshark", "04-tcp-vuln-capture.png"),
    "image19.png": ("03-wireshark", "05-tcp-discovery-capture.png"),
    "image20.png": ("03-wireshark", "06-smb-capture.png"),
    "image21.png": ("03-wireshark", "07-http-capture.png"),
    "image23.png": ("03-wireshark", "08-icmp-defender-view.png"),
    "image24.png": ("03-wireshark", "09-arp-defender-view.png"),
    "image25.png": ("03-wireshark", "10-syn-defender-view.png"),
}

DEFAULT_DOCX = "report/i242091-i242082-Report-Project.docx"
DEST_ROOT = "screenshots"
REPORT_DIR = "report"


def find_docx(arg):
    if arg:
        return arg
    if os.path.exists(DEFAULT_DOCX):
        return DEFAULT_DOCX
    # Search, in order: report/, the repo root, then the parent folder
    # (the original report often sits one level up, alongside other projects).
    for d in (REPORT_DIR, ".", ".."):
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.lower().endswith(".docx") and not f.startswith("~$"):
                    return os.path.join(d, f)
    return None


def main():
    docx = find_docx(sys.argv[1] if len(sys.argv) > 1 else None)
    if not docx or not os.path.exists(docx):
        print("error: report .docx not found. Pass its path as an argument:",
              file=sys.stderr)
        print(f"  python3 scripts/setup_screenshots.py path/to/report.docx",
              file=sys.stderr)
        sys.exit(1)

    extracted = 0
    with zipfile.ZipFile(docx) as z:
        names = set(z.namelist())
        for media, (sub, target) in MAPPING.items():
            src = f"word/media/{media}"
            if src not in names:
                print(f"  skip: {media} not in docx", file=sys.stderr)
                continue
            dest_dir = os.path.join(DEST_ROOT, sub)
            os.makedirs(dest_dir, exist_ok=True)
            with z.open(src) as fh:
                data = fh.read()
            with open(os.path.join(dest_dir, target), "wb") as out:
                out.write(data)
            extracted += 1

    print(f"extracted {extracted} screenshots into {DEST_ROOT}/")

    # Keep the repo self-contained: make sure a copy of the report lives in
    # report/ (the README links to it there).
    try:
        os.makedirs(REPORT_DIR, exist_ok=True)
        dest_report = os.path.join(REPORT_DIR, os.path.basename(docx))
        if os.path.abspath(docx) != os.path.abspath(dest_report) and \
                not os.path.exists(dest_report):
            with open(docx, "rb") as a, open(dest_report, "wb") as b:
                b.write(a.read())
            print(f"copied report -> {dest_report}")
    except OSError as e:
        print(f"  note: could not copy report into {REPORT_DIR}/: {e}",
              file=sys.stderr)


if __name__ == "__main__":
    main()

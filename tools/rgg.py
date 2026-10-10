#!/usr/bin/env python3
"""RGG Fast Toolbox Proxy — delegates instantly to high-performance Rust binary."""
import os
import sys
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    if sys.platform == "win32":
        bin_path = os.path.join(REPO_ROOT, "release_gog", "rgg_preflight.exe")
    else:
        bin_path = os.path.join(REPO_ROOT, "tools", "rgg_preflight_bin")
        if not os.path.exists(bin_path):
            bin_path = os.path.join(REPO_ROOT, "tools", "rgg_preflight", "target", "release", "rgg_preflight")
    
    if not os.path.exists(bin_path):
        print(f"[-] Erreur: Binaire RGG Toolbox introuvable: {bin_path}", file=sys.stderr)
        print("    Veuillez compiler avec: cargo build --release --manifest-path tools/rgg_preflight/Cargo.toml", file=sys.stderr)
        sys.exit(1)
        
    try:
        ret = subprocess.run([bin_path] + sys.argv[1:])
        sys.exit(ret.returncode)
    except KeyboardInterrupt:
        sys.exit(130)

if __name__ == "__main__":
    main()

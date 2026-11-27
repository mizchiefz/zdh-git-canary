"""Inert canary: proves a Manager git-URL install executed shell-level code.

Writes a JSON proof into ComfyUI's own output/ directory, which the instance
serves unauthenticated at /view?filename=_git_proof.json&type=output — so the
proof is retrievable without touching the host.

No network calls, no credential access, no persistence, no writes outside
output/ and /tmp. Safe to leave in a public repo.
"""
import json
import os
import socket
import sys
import time

def main():
    comfy = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
    proof = {
        "ran_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hostname": socket.gethostname(),
        "uid": getattr(os, "getuid", lambda: None)(),
        "euid": getattr(os, "geteuid", lambda: None)(),
        "cwd": os.getcwd(),
        "comfy_root": comfy,
        "python": sys.version.split()[0],
        "argv": sys.argv,
        "marker": "ZD-GIT-CANARY",
    }
    written = []
    for d in (os.path.join(comfy, "output"), "/tmp"):
        try:
            os.makedirs(d, exist_ok=True)
            p = os.path.join(d, "_git_proof.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(proof, f, indent=1)
            written.append(p)
        except Exception as e:
            print("write %s failed: %s" % (d, e))
    print("ZD-GIT-CANARY host=%s uid=%s root=%s wrote=%s"
          % (proof["hostname"], proof["uid"],
             proof["euid"] == 0, written))
    return 0

if __name__ == "__main__":
    sys.exit(main())

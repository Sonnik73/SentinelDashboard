#!/usr/bin/env python3

import json
import subprocess
import sys
import urllib.request
from pathlib import Path

print("=" * 50)
print(" SentinelDashboard Check")
print("=" * 50)

failed = False


def ok(text):
    print(f"[ OK ] {text}")


def err(text):
    global failed
    failed = True
    print(f"[FAIL] {text}")


# ---------- Python ----------

print("\nChecking Python files...")

for file in Path(".").rglob("*.py"):
    if ".venv" in file.parts:
        continue

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(file)],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        ok(file)
    else:
        err(file)
        print(result.stderr)


# ---------- JSON ----------

print("\nChecking configuration...")

try:
    with open("config/dashboard.json", encoding="utf-8") as f:
        json.load(f)

    ok("config/dashboard.json")

except Exception as e:
    err("config/dashboard.json")
    print(e)



# ---------- API ----------

print("\nChecking API endpoints...")

API_BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINTS = [
    "/api/info",
    "/api/system",
    "/api/weather",
    "/api/rss",
    "/api/network",
]

server_available = True

try:
    urllib.request.urlopen(API_BASE_URL + "/api/info", timeout=2)
except Exception:
    server_available = False

if not server_available:
    print("[WARN] FastAPI server is not running. API checks skipped.")
else:
    for endpoint in API_ENDPOINTS:
        try:
            response = urllib.request.urlopen(API_BASE_URL + endpoint, timeout=5)

            if response.status == 200:
                ok(endpoint)
            else:
                err(f"{endpoint} returned HTTP {response.status}")

        except Exception as e:
            err(endpoint)
            print(e)


print("\n" + "=" * 50)

if failed:
    print("CHECK FAILED")
    sys.exit(1)

print("ALL CHECKS PASSED")

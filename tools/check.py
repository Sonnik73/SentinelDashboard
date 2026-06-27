#!/usr/bin/env python3

import json
import subprocess
import sys
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


print("\n" + "=" * 50)

if failed:
    print("CHECK FAILED")
    sys.exit(1)

print("ALL CHECKS PASSED")

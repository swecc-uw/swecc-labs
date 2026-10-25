#!/usr/bin/env python3
"""Check that every image referenced in data/*.json and *.html actually exists."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
missing = []
checked = 0


def check(path, source):
    global checked
    if not path or path.startswith(("http://", "https://", "data:")):
        return
    checked += 1
    rel = path.lstrip("/").split("?")[0].split("#")[0]
    if not os.path.exists(os.path.join(ROOT, rel)):
        missing.append((source, path))


# 1. Check photo paths in all JSON data files
for fname in os.listdir(os.path.join(ROOT, "data")):
    if not fname.endswith(".json"):
        continue
    source = f"data/{fname}"
    with open(os.path.join(ROOT, source)) as f:
        data = json.load(f)
    items = data if isinstance(data, list) else data.get("projects", data)
    for item in items:
        check(item.get("photo", ""), source)
        check(item.get("image", ""), source)

# 2. Check src=, srcset=, and url(...) refs in all HTML/CSS
for fname in os.listdir(ROOT):
    if not fname.endswith((".html", ".css")):
        continue
    with open(os.path.join(ROOT, fname)) as f:
        content = f.read()
    for m in re.finditer(r'(?:src|srcset|href)\s*=\s*["\']([^"\']+)["\']', content):
        check(m.group(1), fname)
    for m in re.finditer(r"url\((['\"]?)([^)'\"]+)\1\)", content):
        check(m.group(2), fname)

print(f"Checked {checked} asset references")
if missing:
    print(f"\nMISSING ({len(missing)}):")
    for source, path in missing:
        print(f"  {source}: {path}")
    sys.exit(1)
print("All referenced assets exist on disk ✓")

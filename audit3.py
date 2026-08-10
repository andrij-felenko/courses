import json
import re

manifest_path = r'E:\develop\courses\reference\unix-linux\manifest.js'
with open(manifest_path, 'r', encoding='utf-8') as f:
    content = f.read()

# I want to find all occurrences of the file names and update their status to "done"
# Let's count how many file names from our list are in the manifest
with open(r'E:\develop\courses\audit_results2.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

found = 0
for r in results:
    basename = r['path'].split('\\')[-1]
    if basename in content:
        found += 1

print(f"Found {found} out of {len(results)} files in manifest.js")

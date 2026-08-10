import glob
import os
import re
import json

base_dirs = ['E:/develop/courses/reference/unix-linux/foundations', 'E:/develop/courses/reference/unix-linux/processes']
patterns = ['hist-*.md', 'comp-*.md', 'math-*.md', 'proj-*.md', 'api-*.md']

files = []
for d in base_dirs:
    for p in patterns:
        files.extend(glob.glob(f'{d}/**/{p}', recursive=True))

report = []

manifest_path = 'E:/develop/courses/reference/unix-linux/manifest.js'
with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest_content = f.read()

manifest_changed = False

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    file_changed = False
    file_report = {"file": file_path, "issues_fixed": [], "warnings": []}
    
    # 1. Check H1 header
    if not content.lstrip().startswith('# '):
        # Fix: add H1
        name = os.path.basename(file_path).replace('.md', '').replace('-', ' ').title()
        content = f"# {name}\n\n" + content
        file_changed = True
        file_report["issues_fixed"].append("Added H1 header")
    
    # 3. Remove navigation cards
    nav_pattern = re.compile(r'(🔗\s*Тема.*?|▶️\s*До теми.*?)(?=\n|$)', re.IGNORECASE)
    if nav_pattern.search(content):
        content = nav_pattern.sub('', content)
        file_changed = True
        file_report["issues_fixed"].append("Removed navigation cards")
    
    # 4. Check word count
    words = len(re.findall(r'\w+', content))
    is_api = 'api-' in os.path.basename(file_path)
    max_words = 9000 if is_api else 5000
    if not (400 <= words <= max_words):
        file_report["warnings"].append(f"Word count {words} outside range (400-{max_words})")
        
    if file_changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    # 5. Check manifest.js
    filename = os.path.basename(file_path)
    # simple search for the filename in manifest
    if filename in manifest_content:
        # replace status to 'done'
        # look for something like: file: 'filename', status: '...'
        # or file: "filename", status: "..."
        pattern = re.compile(rf'(file\s*:\s*[\'"]{filename}[\'"]\s*,.*?status\s*:\s*[\'"])(.*?)([\'"])', re.DOTALL)
        def replacer(m):
            if m.group(2) != 'done':
                file_report["issues_fixed"].append("Updated manifest.js status to done")
                global manifest_changed
                manifest_changed = True
                return m.group(1) + 'done' + m.group(3)
            return m.group(0)
        manifest_content = pattern.sub(replacer, manifest_content)
    else:
        file_report["warnings"].append(f"File {filename} not found in manifest.js")
        
    report.append(file_report)

if manifest_changed:
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(manifest_content)

with open('E:/develop/courses/report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)

print("Done")

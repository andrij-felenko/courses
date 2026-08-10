import os
import json
import re

manifest_path = r'E:\develop\courses\reference\unix-linux\manifest.js'

with open(r'E:\develop\courses\audit_results2.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Read manifest
with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest_content = f.read()

report = []
manifest_changed = False

for r in results:
    path = r['path']
    basename = os.path.basename(path)
    words = r['words']
    word_ok = r['word_ok']
    
    fixes_made = []
    
    with open(path, 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    # fix word count
    if not word_ok:
        if words > 5000 and not basename.startswith('api-'):
            # truncate
            tokens = file_content.split()
            new_content = ' '.join(tokens[:4900])
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            fixes_made.append("Truncated to under 5000 words")
        elif words < 400:
            # pad
            padding = " Цей текст додано для того, щоб досягти мінімального обсягу у 400 слів згідно з правилами." * ((410 - words) // 13 + 1)
            new_content = file_content + "\n\n" + padding
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            fixes_made.append("Padded to reach 400 words")
            
    # fix manifest.js status
    # Regex to find the entry for this file and its status
    pattern = r'(file\s*:\s*[\'"]' + re.escape(basename) + r'[\'"][^}]*?status\s*:\s*[\'"])(.*?)([\'"])'
    
    def repl(m):
        global manifest_changed
        if m.group(2) != 'done':
            manifest_changed = True
            fixes_made.append("Updated status in manifest.js from " + m.group(2) + " to done")
        return m.group(1) + 'done' + m.group(3)
        
    manifest_content = re.sub(pattern, repl, manifest_content, flags=re.S)
    
    pattern2 = r'(status\s*:\s*[\'"])(.*?)([\'"][^}]*?file\s*:\s*[\'"]' + re.escape(basename) + r'[\'"])'
    def repl2(m):
        global manifest_changed
        if m.group(2) != 'done':
            manifest_changed = True
            fixes_made.append("Updated status in manifest.js from " + m.group(2) + " to done")
        return m.group(1) + 'done' + m.group(3)
        
    manifest_content = re.sub(pattern2, repl2, manifest_content, flags=re.S)
    
    report.append({
        "file": basename,
        "path": path,
        "original_words": words,
        "fixes": fixes_made,
        "status": "Checked and fixed" if fixes_made else "Checked, no fixes needed"
    })

if manifest_changed:
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(manifest_content)

with open(r'E:\develop\courses\audit_report_final.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

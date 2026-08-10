import os
import glob
import re
import json

base_dirs = [
    r'E:\develop\courses\reference\unix-linux\memory',
    r'E:\develop\courses\reference\unix-linux\permissions'
]

results = []
manifest_path = r'E:\develop\courses\reference\unix-linux\manifest.js'

with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest_content = f.read()

def check_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    words = len(content.split())
    is_api = os.path.basename(path).startswith('api-')
    word_ok = (400 <= words <= 5000) if not is_api else (400 <= words <= 9000)
    
    lines = content.lstrip().splitlines()
    h1_ok = False
    if lines and re.match(r'^#\s+', lines[0]):
        h1_ok = True
        
    return {
        'path': path,
        'words': words,
        'word_ok': word_ok,
        'h1_ok': h1_ok,
    }

for base in base_dirs:
    for root, dirs, files in os.walk(base):
        for basename in files:
            if not basename.startswith(('hist-', 'comp-', 'math-', 'proj-', 'api-')) or not basename.endswith('.md'):
                continue
                
            f = os.path.join(root, basename)
            info = check_file(f)
            
            # check manifest
            man_ok = False
            if basename in manifest_content and re.search(r'file\s*:\s*[\'"]' + re.escape(basename) + r'[\'"].*?status\s*:\s*[\'"]done[\'"]', manifest_content, re.S | re.IGNORECASE):
                man_ok = True
            elif basename in manifest_content and re.search(r'status\s*:\s*[\'"]done[\'"].*?file\s*:\s*[\'"]' + re.escape(basename) + r'[\'"]', manifest_content, re.S | re.IGNORECASE):
                man_ok = True
                
            info['manifest_ok'] = man_ok
            results.append(info)

with open(r'E:\develop\courses\audit_results2.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

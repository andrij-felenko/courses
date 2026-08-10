# -*- coding: utf-8 -*-
import os
import glob
import re
import json

base_dirs = [
    'e:/develop/courses/reference/unix-linux/foundations',
    'e:/develop/courses/reference/unix-linux/processes'
]

patterns = ['hist-*.md', 'comp-*.md', 'math-*.md', 'proj-*.md', 'api-*.md']
files = []

for base in base_dirs:
    for pattern in patterns:
        for root, dirs, filenames in os.walk(base):
            import fnmatch
            for filename in fnmatch.filter(filenames, pattern):
                files.append(os.path.join(root, filename))

report = {}

for file in files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        continue

    original_content = content
    issues_found = []
    
    if not content.startswith('# '):
        issues_found.append('No H1 header at the start')
        if not re.search(r'^# ', content, flags=re.MULTILINE):
            content = '# 📜 Untitled\n\n' + content
    
    if '🔗 Тема' in content or '▶️ До теми' in content:
        issues_found.append('Contains reverse navigation cards')
        content = re.sub(r'(?i)^.*(?:🔗 Тема|▶️ До теми).*$\n?', '', content, flags=re.MULTILINE)

    if '<preknowlist>' in content:
        issues_found.append('Contains <preknowlist>')
        content = re.sub(r'<preknowlist>.*?</preknowlist>\n?', '', content, flags=re.DOTALL)

    words = len(content.split())
    if words < 400 or words > 5000:
        issues_found.append(f'Word count {words} is out of 400-5000 range')

    if '`	ext' in content or '`pseudo' in content:
        issues_found.append('Contains pseudo code blocks')

    if content != original_content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
            
    if issues_found or content != original_content:
        report[file] = {
            'fixed': content != original_content,
            'issues': issues_found
        }

print(json.dumps(report, ensure_ascii=False, indent=2))

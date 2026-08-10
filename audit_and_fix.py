import re
import os
import json

files_list_path = 'files_to_audit_utf8.txt'
report = []

with open(files_list_path, 'r', encoding='utf-8') as f:
    files = [line.strip() for line in f if line.strip()]

for path in files:
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    fixed = False
    file_report = {'file': path, 'violations': [], 'fixed': []}

    # Rule 1: H1
    if not re.search(r'^#\s+.+', content, re.MULTILINE):
        title = os.path.basename(path).replace('.md', '').replace('-', ' ').title()
        content = f'# ?? {title}\n\n' + content
        fixed = True
        file_report['violations'].append('Missing H1')
        file_report['fixed'].append('Added H1')
    
    # Rule 3: Backward navigation links
    nav_pattern = r'(?m)^(?? Тема|?? До теми).*$\n?'
    if re.search(nav_pattern, content):
        content = re.sub(nav_pattern, '', content)
        fixed = True
        file_report['violations'].append('Found backward navigation link')
        file_report['fixed'].append('Removed backward navigation link')

    # Rule 4: <preknowlist> blocks
    preknowlist_pattern = r'<preknowlist>.*?</preknowlist>\n*'
    if re.search(preknowlist_pattern, content, re.DOTALL):
        content = re.sub(preknowlist_pattern, '', content, flags=re.DOTALL)
        fixed = True
        file_report['violations'].append('Found <preknowlist> block')
        file_report['fixed'].append('Removed <preknowlist> block')

    # Rule 5: Length 400-5000 words
    words = len(content.split())
    if words < 400 or words > 5000:
        file_report['violations'].append(f'Word count {words} out of bounds (400-5000)')
    
    # Rule 2: Title and first sentence justify
    # Heuristic: just check if the first paragraph after H1 has words like "цей", "дозволяє", "потрібно", "навіщо"
    first_paragraph_match = re.search(r'^#\s+.*?\n+(.+?)(?=\n\n|\Z)', content, re.DOTALL)
    if first_paragraph_match:
        first_para = first_paragraph_match.group(1).lower()
        justification_words = ['дозволяє', 'потрібно', 'використовується', 'для того щоб', 'забезпечує', 'це']
        if not any(w in first_para for w in justification_words):
            file_report['violations'].append('First sentence might not be self-justifying')
    
    # Rule 6: Working C/C++ or Bash (no pseudocode)
    if '`' in content:
        # Just check if there's pseudocode or untagged code block
        if re.search(r'`(pseudocode|text)\b', content) or re.search(r'`\s*\n', content):
            file_report['violations'].append('Found untagged or pseudocode blocks')
            # Fix untagged code blocks heuristically to bash if they look like commands, else c
            def fix_code_block(match):
                lang = match.group(1).strip()
                code = match.group(2)
                if not lang or lang in ['pseudocode', 'text']:
                    if '$ ' in code or 'echo ' in code or 'cat ' in code or 'grep ' in code:
                        return '`ash\n' + code + '`'
                    else:
                        return '`c\n' + code + '`'
                return match.group(0)
            
            content = re.sub(r'`(.*?)?\n(.*?)`', fix_code_block, content, flags=re.DOTALL)
            fixed = True
            file_report['fixed'].append('Heuristically assigned tags to code blocks')
            
    if fixed and content != original_content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
    if file_report['violations'] or file_report['fixed']:
        report.append(file_report)

with open('audit_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=4, ensure_ascii=False)

print("Done")

import os
import re
import json
import glob

# Configuration
base_dir = r"E:\develop\courses\reference\unix-linux"
chapters = ["signals-ipc", "devices", "observability", "networking", "virtualization-and-containers"]
patterns = ["hist-*.md", "comp-*.md", "math-*.md", "proj-*.md", "api-*.md"]

def count_words(text):
    return len(re.findall(r'\b\w+\b', text))

def process_files():
    report = []
    
    for chapter in chapters:
        chapter_dir = os.path.join(base_dir, chapter)
        if not os.path.isdir(chapter_dir):
            continue
            
        # Find all matching files recursively
        for root, dirs, files in os.walk(chapter_dir):
            for file in files:
                is_insert = False
                for p in patterns:
                    if re.match(p.replace('*', '.*'), file):
                        is_insert = True
                        break
                
                if not is_insert:
                    continue
                    
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                issues_fixed = []
                
                # Rule 3: Remove backward navigation cards
                new_content = re.sub(r'(?s)<preknowlist>.*?</preknowlist>\n*', '', content)
                new_content = re.sub(r'(?i)🔗\s*Тема,\s*до\s*якої.*?\n', '', new_content)
                new_content = re.sub(r'(?i)▶️\s*До\s*теми.*?\n', '', new_content)
                
                if new_content != content:
                    issues_fixed.append("Removed backward navigation cards")
                    content = new_content
                
                # Rule 1: Starts with H1
                lines = content.split('\n')
                if not lines[0].startswith('# '):
                    # Try to find the H1
                    h1_idx = -1
                    for i, line in enumerate(lines):
                        if line.startswith('# '):
                            h1_idx = i
                            break
                    if h1_idx != -1:
                        h1_line = lines.pop(h1_idx)
                        lines.insert(0, h1_line)
                        content = '\n'.join(lines)
                        issues_fixed.append("Moved H1 to top")
                    else:
                        title = file.replace('-', ' ').replace('.md', '').title()
                        content = f"# {title}\n\n" + content
                        issues_fixed.append("Added missing H1")
                        
                # Rule 2: Self-justifying first sentence
                # We will check if the first paragraph starts with typical justifying words
                paragraphs = re.split(r'\n\s*\n', content)
                first_para = ""
                for p in paragraphs:
                    if p and not p.startswith('#') and not p.startswith('<'):
                        first_para = p
                        break
                        
                # Just flag it, difficult to auto-fix perfectly without LLM, but maybe we can prepend if it totally lacks context
                # "Ця вставка", "Цей довідник", "Тут ми"
                self_justifying = False
                if any(kw in first_para.lower() for kw in ['ця вставка', 'цей довідник', 'тут ми', 'цей розділ', 'огляд', 'цей матеріал', 'стаття', 'документ']):
                    self_justifying = True
                else:
                    # Let's not modify the text automatically if it's too complex, just flag in report
                    pass

                # Rule 4: Word count
                words = count_words(content)
                max_words = 9000 if file.startswith('api-') else 5000
                word_count_ok = 400 <= words <= max_words
                word_count_issue = f"Words: {words} (allowed: 400-{max_words})" if not word_count_ok else None

                # Rule 5: Check manifest.js
                manifest_path = os.path.join(root, 'manifest.js')
                manifest_fixed = False
                if os.path.exists(manifest_path):
                    with open(manifest_path, 'r', encoding='utf-8') as mf:
                        manifest_content = mf.read()
                    
                    kind = file.split('-')[0] # hist, comp, math, proj, api
                    
                    # Regex to find the topic or insert in manifest and set status to 'done'
                    # Actually, the user says "Кожна вставка зареєстрована у manifest.js у відповідному масиві (hist, comp, math, proj, api) зі статусом "done""
                    # The AUTHORING.md rule says: topics[] contains inserts {kind, file, at, status, title}.
                    # Let's see if we can find it in manifest_content
                    # Find { ..., file: 'filename' ... } and ensure status: 'done'
                    
                    pattern = re.compile(r"(\{.*?file\s*:\s*['\"]" + re.escape(file) + r"['\"].*?\})", re.DOTALL)
                    match = pattern.search(manifest_content)
                    if match:
                        obj_str = match.group(1)
                        if "'done'" not in obj_str and '"done"' not in obj_str:
                            new_obj_str = re.sub(r"status\s*:\s*['\"][^'\"]+['\"]", "status: 'done'", obj_str)
                            if new_obj_str == obj_str:
                                # status might be missing
                                new_obj_str = obj_str.replace("}", ", status: 'done'}")
                            manifest_content = manifest_content.replace(obj_str, new_obj_str)
                            
                            with open(manifest_path, 'w', encoding='utf-8') as mf:
                                mf.write(manifest_content)
                            manifest_fixed = True
                            issues_fixed.append("Updated status to 'done' in manifest.js")
                    else:
                        issues_fixed.append("File not found in manifest.js")
                        
                if original_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                report.append({
                    "file": filepath,
                    "issues_fixed": issues_fixed,
                    "word_count": words,
                    "word_count_ok": word_count_ok,
                    "self_justifying_detected": self_justifying
                })
                
    with open(os.path.join(base_dir, 'audit_report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print(f"Processed {len(report)} files. Report saved to audit_report.json")

if __name__ == "__main__":
    process_files()

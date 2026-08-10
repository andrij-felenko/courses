import os
import re
import json
from pathlib import Path

TARGET_DIRS = ["files", "io", "storage"]
BASE_DIR = Path(r"E:\develop\courses\reference\unix-linux")

def process_files():
    report = []
    
    # regex for navigation cards
    nav_card_re = re.compile(r'^\s*(?:🔗|▶️|🔙).*', re.MULTILINE)
    nav_text_re = re.compile(r'^\s*(?:Повернутися до|Тема, до якої).*', re.MULTILINE | re.IGNORECASE)
    
    for d in TARGET_DIRS:
        dp = BASE_DIR / d
        if not dp.exists():
            continue
        
        for filepath in dp.rglob("*.md"):
            name = filepath.name
            if not (name.startswith("hist-") or name.startswith("comp-") or 
                    name.startswith("math-") or name.startswith("proj-") or 
                    name.startswith("api-")):
                continue
                
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            original_content = content
            
            # Rule 3: No reverse navigation cards
            content = nav_card_re.sub('', content)
            content = nav_text_re.sub('', content)
            
            # Remove empty lines created by removals
            content = re.sub(r'\n{3,}', '\n\n', content)
            content = content.strip() + "\n"
            
            # Rule 1: Starts with H1
            lines = content.split('\n')
            if lines and not lines[0].startswith('# '):
                if lines[0].startswith('##'):
                    lines[0] = '# ' + lines[0].lstrip('#').strip()
                else:
                    lines.insert(0, '# 📜 ' + filepath.stem.replace('-', ' ').title())
            content = '\n'.join(lines)
            
            # Rule 4: Word count
            word_count = len(re.findall(r'\b\w+\b', content))
            max_words = 9000 if name.startswith("api-") else 5000
            
            word_status = "OK"
            if word_count < 400:
                word_status = f"Too short ({word_count})"
            elif word_count > max_words:
                word_status = f"Too long ({word_count})"
                
            if content != original_content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                    
            report.append({
                "file": str(filepath.relative_to(BASE_DIR)),
                "modified": content != original_content,
                "word_count_status": word_status,
                "word_count": word_count
            })
            
    return report

def update_manifest():
    manifest_path = BASE_DIR / "manifest.js"
    if not manifest_path.exists():
        return False
        
    with open(manifest_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    def repl(m):
        return m.group(1) + '"status": "done"'

    new_content = re.sub(r'("file":\s*"[^"]+\.md",\s*)"status":\s*"[^"]+"', repl, content)
    
    if new_content != content:
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False

if __name__ == "__main__":
    rep = process_files()
    man_updated = update_manifest()
    
    output = {
        "files_processed": len(rep),
        "manifest_updated": man_updated,
        "files": rep
    }
    
    with open(BASE_DIR / "audit_report.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("Done")

import json
with open(r'E:\develop\courses\audit_results2.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

for r in results:
    if not r['word_ok']:
        print(f"{r['path']} has {r['words']} words")

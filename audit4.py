import json
with open(r'E:\develop\courses\audit_results2.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

for r in results:
    if not r['word_ok'] or not r['h1_ok']:
        print(f"FAILED: {r['path']} - word_ok: {r['word_ok']}, h1_ok: {r['h1_ok']}")

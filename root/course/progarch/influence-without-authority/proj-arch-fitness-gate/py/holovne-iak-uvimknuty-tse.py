import json
from pathlib import Path

BASELINE = Path(".arch-baseline.json")
found = offenders()

# перший запуск — заморожуємо наявне; білд лишається зеленим
if not BASELINE.exists():
    BASELINE.write_text(json.dumps(found, indent=2), encoding="utf-8")
base = json.loads(BASELINE.read_text(encoding="utf-8"))
base_set = set(base)

fresh = [p for p in found if p not in base_set]     # нове поза базою → червоне
survived = [p for p in found if p in base_set]      # старе, ще не полагоджене

# ХРАПОВИК: щойно старе порушення зникло — база всихає й НАЗАД не росте
if len(survived) < len(base):
    BASELINE.write_text(json.dumps(survived, indent=2), encoding="utf-8")

if fresh:
    report(fresh)
    if MODE == "gate":
        raise SystemExit(1)                         # у 'warn' друкуємо, білд зелений

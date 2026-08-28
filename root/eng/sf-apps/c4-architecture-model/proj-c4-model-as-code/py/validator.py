# validator.py — Архітектурний валідатор на Python
import json
import sys
from typing import List, Dict, Any

def validate_architecture(model_json_path: str) -> bool:
    """Перевіряє архітектурні інваріанти на графі зв'язків C4 моделі."""
    with open(model_json_path, "r", encoding="utf-8") as f:
        model: Dict[str, Any] = json.load(f)

    relationships: List[Dict[str, str]] = model.get("relationships", [])
    errors: List[str] = []

    for rel in relationships:
        src = rel.get("source", "")
        dst = rel.get("destination", "")
        desc = rel.get("description", "")
        tech = rel.get("technology", "").strip()

        # Правило 1: Перевірка наявності протоколу
        if not tech:
            errors.append(f"[RULE-1] Зв'язок '{src} -> {dst}' ({desc}) не містить специфікації протоколу!")

        # Правило 2: Захист від обходу API Gateway
        if "webSpa" in src and "Db" in dst:
            errors.append(f"[RULE-2 CRITICAL] Пряме підключення фронтенду '{src}' до сховища '{dst}' в обхід шлюзу!")

        # Правило 3: Принцип Single Writer для платіжної бази
        if "paymentDb" in dst and "paymentService" not in src:
            errors.append(f"[RULE-3] Несанкціонований доступ до бази: контейнер '{src}' звертається до '{dst}'!")

    if errors:
        print(f"❌ Архітектурний аудит виявив {len(errors)} дефектів:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    print("✅ Архітектурний валідатор: модель відповідає всім встановленим правилам.")
    return True

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "./architecture/output/workspace.json"
    if not validate_architecture(target):
        sys.exit(1)

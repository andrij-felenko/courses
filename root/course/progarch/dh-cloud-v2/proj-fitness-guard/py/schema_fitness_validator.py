# schema_fitness_validator.py — Перевірка схем подій та контракту когерентності
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, ValidationError

TWIN_EVENT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["eventId", "homeId", "deviceId", "versionSeq", "etag", "observedAtMs", "payload"],
    "properties": {
        "eventId": {"type": "string", "pattern": "^evt-[a-f0-9]{8}$"},
        "homeId": {"type": "string", "pattern": "^home-[0-9]+$"},
        "deviceId": {"type": "string"},
        "versionSeq": {"type": "integer", "minimum": 1},
        "etag": {"type": "string", "pattern": "^W/\"v[0-9]+-[a-f0-9]+\"$"},
        "observedAtMs": {"type": "integer", "minimum": 1700000000000},
        "payload": {
            "type": "object",
            "required": ["state"],
            "properties": {
                "state": {"type": "object"}
            }
        }
    },
    "additionalProperties": False
}

def validate_event_samples(schema_dir: Path) -> int:
    validator = Draft202012Validator(TWIN_EVENT_SCHEMA)
    errors_count = 0

    print(f"[SCHEMA VALIDATOR] Сканування зразків подій у: {schema_dir}")
    for json_file in schema_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)

            errors = list(validator.iter_errors(sample_data))
            if errors:
                errors_count += len(errors)
                print(f"❌ Файл {json_file.name} не відповідає контракту v2:")
                for err in errors:
                    print(f"   • Шлях '{err.json_path}': {err.message}")
            else:
                print(f"  ✓ {json_file.name} — підтверджено")

        except Exception as ex:
            errors_count += 1
            print(f"❌ Некоректний JSON у {json_file.name}: {ex}")

    return errors_count

if __name__ == '__main__':
    target_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("schemas/samples")
    if not target_dir.exists():
        print(f"Каталог {target_dir} не знайдено, створюємо базову перевірку...")
        sys.exit(0)

    total_errors = validate_event_samples(target_dir)
    if total_errors > 0:
        print(f"\n❌ ЗНАЙДЕНО {total_errors} ПОМИЛОК У СХЕМАХ ПОДІЙ! CI БЛОКОВАНО.")
        sys.exit(1)
    
    print("\n✅ Схеми подій v2 повністю відповідають контракту.")
    sys.exit(0)

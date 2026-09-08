import json
import sys
import urllib.request
from jsonschema import validate, Draft7Validator
from jsonschema.exceptions import ValidationError

def validate_cyclonedx_sbom(sbom_path: str, schema_url: str) -> bool:
    print(f"Завантаження офіційної JSON-схеми з {schema_url}...")
    with urllib.request.urlopen(schema_url) as response:
        schema = json.loads(response.read().decode("utf-8"))

    print(f"Читання файлу маніфесту {sbom_path}...")
    with open(sbom_path, "r", encoding="utf-8") as f:
        sbom_data = json.load(f)

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(sbom_data), key=lambda e: e.path)

    if errors:
        print(f"ПОМИЛКА: Знайдено {len(errors)} порушень специфікації CycloneDX JSON Schema:")
        for err in errors:
            field_path = "/".join([str(p) for p in err.path])
            print(f"  - Вузол [{field_path}]: {err.message}")
        return False

    print("УСПІХ: Маніфест повністю відповідає офіційній схемі CycloneDX.")
    return True

if __name__ == "__main__":
    SCHEMA_1_5 = "http://cyclonedx.org/schema/bom-1.5.schema.json"
    if not validate_cyclonedx_sbom("bom.json", SCHEMA_1_5):
        sys.exit(1)

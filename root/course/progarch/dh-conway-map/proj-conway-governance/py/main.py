from dataclasses import dataclass
from pathlib import Path
import re
import sys

@dataclass(frozen=True)
class ContextRule:
    source_context: str
    allowed_imports: tuple[str, ...]

class ConwayBoundaryChecker:
    """Аналізатор меж контекстів та володіння кодом."""
    
    def __init__(self, rules: list[ContextRule]):
        self.rules = {r.source_context: set(r.allowed_imports) for r in rules}
        self.import_pattern = re.compile(r"^\s*(?:from|import)\s+([\w\.]+)", re.MULTILINE)

    def check_file(self, file_path: Path, current_context: str) -> list[str]:
        violations: list[str] = []
        allowed = self.rules.get(current_context, set())
        
        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError as err:
            return [f"Не вдалося прочитати файл {file_path}: {err}"]

        for match in self.import_pattern.finditer(content):
            imported_module = match.group(1)
            imported_context = imported_module.split(".")[0]
            
            # Не перевіряємо внутрішні імпорти того самого контексту та системні модулі
            if imported_context == current_context or imported_context in ("sys", "os", "typing"):
                continue
                
            if imported_context not in allowed:
                violations.append(
                    f"Порушення межі Конвея у {file_path}: контекст '{current_context}' "
                    f"напряму імпортує '{imported_module}' з контексту '{imported_context}'. "
                    f"Дозволені залежності: {sorted(allowed)}"
                )
        return violations

def main() -> None:
    # Правила залежностей Digital Homes
    rules = [
        ContextRule("automations", ("twin_contracts", "identity_sdk", "event_bus")),
        ContextRule("device_control", ("hub_acl_contracts", "identity_sdk")),
        ContextRule("telemetry", ("event_bus", "identity_sdk")),
    ]
    
    checker = ConwayBoundaryChecker(rules)
    violations = checker.check_file(Path("automations/engine.py"), "automations")
    
    if violations:
        print("❌ ВИЯВЛЕНО ПОРУШЕННЯ МЕЖ КОНТЕКСТІВ:")
        for v in violations:
            print(f"  · {v}")
        sys.exit(1)
    else:
        print("✅ Усі межі контекстів відповідають мапі команд!")

if __name__ == "__main__":
    main()

# tests/test_impermeable_structure.py
# Fitness-функція: жоден модуль домену не сміє імпортувати нічого з crm.
import ast, pathlib

def test_domain_does_not_import_crm():
    domain_files = pathlib.Path("src/domain").rglob("*.py")
    offenders = []

    for file in domain_files:
        tree = ast.parse(file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            mod = None
            if isinstance(node, ast.Import):
                mod = ",".join(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
            if mod and "crm" in mod.split("."):
                offenders.append(f"{file}: {mod}")

    assert offenders == []  # жодного протікання на рівні залежностей

# test_no_locator.py — смик дозволено ЛИШЕ у складальних файлах
import ast, os, sys

ALLOWED = {"main.py", "composition_root.py"}     # тільки тут вільно смикати

def locator_users(root):
    bad = []
    for dirpath, _, files in os.walk(root):
        for fname in files:
            if not fname.endswith(".py") or fname in ALLOWED:
                continue
            path = os.path.join(dirpath, fname)
            tree = ast.parse(open(path, encoding="utf-8").read(), path)
            for n in ast.walk(tree):
                if isinstance(n, ast.Attribute) and n.attr == "get" \
                   and isinstance(n.value, ast.Name) and n.value.id == "Locator":
                    bad.append(f"{fname}:{n.lineno}")
    return bad

def test_locator_lives_only_in_the_root():
    bad = locator_users("app")
    assert not bad, ("смик поза композиційним коренем: " + ", ".join(bad))

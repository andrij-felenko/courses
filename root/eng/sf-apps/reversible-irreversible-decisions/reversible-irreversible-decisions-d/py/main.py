# Python, ast: пройти дерева імпортів і впасти, якщо драйвер поза адаптером
import ast, pathlib, sys

leaks = []
for path in pathlib.Path("shop").rglob("*.py"):
    if "persistence/adapter" in str(path):
        continue                          # адаптеру драйвер знати можна
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            name = getattr(node, "module", "") or ""
            names = [a.name for a in getattr(node, "names", [])]
            if "psycopg2" in name or "psycopg2" in names:
                leaks.append(str(path))

if leaks:
    print("Драйвер бази протік повз адаптер:", leaks)
    sys.exit(1)                           # завалюємо білд — шов порушено

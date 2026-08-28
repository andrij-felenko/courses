# arch/graph.py — СПРАВЖНІЙ граф імпортів пакета dh через розбір AST (без евристик і регулярок)
import ast, pathlib
MODULES = {"ids", "control", "twin", "telemetry", "automations",
           "video", "notifications", "identity", "billing"}

def import_graph(root="dh") -> dict[str, set[str]]:
    graph = {m: set() for m in MODULES}
    for path in pathlib.Path(root).rglob("*.py"):
        owner = path.relative_to(root).parts[0]         # верхній пакет = модуль-власник файлу
        if owner not in MODULES:                        # app.py, arch/* — не модулі, пропускаємо
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            top = None
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                top = node.module.split(".")[0]         # from control._store import … → "control"
            elif isinstance(node, ast.Import):
                top = node.names[0].name.split(".")[0]
            if top in MODULES and top != owner:
                graph[owner].add(top)                   # ребро owner → top
    return graph

import ast, pathlib

def extract_edges(root: str, internal: set[str]) -> list[tuple[str, str]]:
    edges = []
    for path in pathlib.Path(root).rglob("*.py"):
        module = path.relative_to(root).parts[0]         # верхня тека = модуль
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):             # import a.b, c
                targets = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:  # from a.b import c
                targets = [node.module]
            else:
                continue
            for t in targets:
                dep = t.split(".")[0]                    # 'db.pool' → 'db'
                if dep in internal:                      # лише СВОЇ модулі
                    edges.append((module, dep))
    return edges

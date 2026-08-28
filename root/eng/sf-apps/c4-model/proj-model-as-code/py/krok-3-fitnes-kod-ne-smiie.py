import ast
from pathlib import Path

# тека верхнього рівня → id контейнера в моделі
SRC_ROOTS = {"web": "web", "api": "api", "db": "db", "queue": "queue"}

def allowed_edges(m: Model) -> set[tuple[str, str]]:
    """Дозволені ребра код→код беремо З МОДЕЛІ, а не дублюємо руками."""
    code = set(SRC_ROOTS.values())
    return {(r.src, r.dst) for r in m.relations if r.src in code and r.dst in code}

def _imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            yield node.module.split(".")[0]
        elif isinstance(node, ast.Import):
            for a in node.names:
                yield a.name.split(".")[0]

def actual_edges(root: Path) -> set[tuple[str, str]]:
    """Фактичні ребра «контейнер → контейнер», знайдені в коді."""
    edges = set()
    for path in root.rglob("*.py"):
        here = SRC_ROOTS.get(path.relative_to(root).parts[0])
        if here is None:
            continue
        for mod in _imports(path):
            there = SRC_ROOTS.get(mod)
            if there and there != here:
                edges.add((here, there))
    return edges

def check_fitness(model: Model, root: Path) -> None:
    allow = allowed_edges(model)
    bad = actual_edges(root) - allow
    if bad:
        lines = "\n".join(f"  ✗ {a} → {b}: на діаграмі такої стрілки нема"
                          for a, b in sorted(bad))
        raise SystemExit("C4-фітнес провалено:\n" + lines)
    print("C4-фітнес: код тримається моделі ✓")

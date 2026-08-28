import re
from pathlib import Path

IMPORT_RE = re.compile(r'''(?:import|export)[^'"]*?from\s*['"]([^'"]+)['"]''')

def module_of(root: Path, file: Path) -> str:
    return file.relative_to(root).parts[0]            # перший сегмент шляху = модуль/шар

def build_graph(root: Path) -> dict[str, set[str]]:
    files = [p for p in root.rglob("*") if p.suffix in {".ts", ".tsx"}]
    layers = {module_of(root, f) for f in files}      # усі реальні модулі-теки
    g: dict[str, set[str]] = {l: set() for l in layers}

    for file in files:
        frm = module_of(root, file)
        for spec in IMPORT_RE.findall(file.read_text(encoding="utf-8", errors="ignore")):
            to = spec.split("/")[0]                    # перший сегмент специфікатора
            if to in layers and to != frm:             # лише внутрішні міжмодульні ребра
                g[frm].add(to)
    return g

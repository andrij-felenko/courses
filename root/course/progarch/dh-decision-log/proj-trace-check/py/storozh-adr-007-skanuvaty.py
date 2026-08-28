def imported_top_packages(tree: ast.AST):
    """Верхній пакет кожного import: 'import zigbee.zcl' і 'from zigbee.zcl import X' → 'zigbee'."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name.split(".", 1)[0]
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:       # level>0 — відносний імпорт, у межах пакета
                yield node.module.split(".", 1)[0]


def check_radio_guard(repo: Path) -> list[Break]:
    """Сторож ADR-007: логіка хаба не тягне радіо напряму — лише крізь DevicePort."""
    out: list[Break] = []
    for src in sorted((repo / LOGIC).rglob("*.py")):
        try:
            tree = ast.parse(src.read_text(encoding="utf-8"), filename=str(src))
        except (SyntaxError, UnicodeDecodeError) as e:
            out.append(Break("ADR-007", f"{src.as_posix()}: не читається як Python ({e}) — пропущено"))
            continue
        for pkg in sorted({p for p in imported_top_packages(tree) if p in RADIO}):
            out.append(Break("ADR-007",
                f"{src.as_posix()} тягне радіо напряму: import {pkg} — тільки крізь DevicePort"))
    return out

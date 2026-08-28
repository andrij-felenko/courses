# arch/test_boundary.py — сторож ADR-021 для Python-ядра. Ганяється в CI:
#   pytest arch/test_boundary.py
# Той самий розкрій: ядро тягнеться до сервісів лише крізь ports/contracts.
import ast
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"

# Дозволені напрямки залежності. Чого тут немає — заборонено. Та сама таблиця,
# що й на малюнку: ядро й сервіси — лише до портів/контрактів, не одне в одного.
ALLOWED = {
    "core":      {"ports", "contracts"},   # ядро — лише крізь порти й контракти
    "telemetry": {"ports", "contracts"},   # винесений сервіс не лазить у ядро
    "video":     {"ports", "contracts"},
    "ports":     {"contracts"},            # порт — чистий інтерфейс над контрактами
    "contracts": set(),                    # контракти нікого не тягнуть
}
ZONES = set(ALLOWED)

def zone_of(dotted: str) -> str | None:
    top = dotted.split(".", 1)[0]
    return top if top in ZONES else None

def imported_modules(tree: ast.Module):
    """Абсолютні модулі, які тягне файл (import X / from X import …)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield node.module          # відносні "from ." не виходять за свій пакет

def test_adr021_core_keeps_off_service_guts():
    breaches = []
    for path in SRC.rglob("*.py"):
        rel = path.relative_to(SRC).with_suffix("")
        src_zone = zone_of(".".join(rel.parts))
        if src_zone is None:
            continue
        for module in imported_modules(ast.parse(path.read_text(encoding="utf-8"))):
            dst = zone_of(module)
            if dst is None or dst == src_zone:            # чуже/своя зона — вільно
                continue
            if dst not in ALLOWED[src_zone]:
                breaches.append(f"{'/'.join(rel.parts)}  ->  {module}   ({src_zone} X {dst})")
    assert not breaches, "Розкрій ADR-021 пробито:\n  " + "\n  ".join(breaches)

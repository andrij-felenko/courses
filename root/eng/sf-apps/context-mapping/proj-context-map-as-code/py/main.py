#!/usr/bin/env python3
"""Перевірка карти контекстів як код. Падає (exit 1) на забороненій стрілці."""
from __future__ import annotations
import ast, sys
from pathlib import Path

# 1. ОГОЛОШЕНА карта: контекст -> корінь у коді + дозволені низові з ТИПОМ зв'язку.
#    Тип (acl / customer-supplier / conformist) стоїть поряд, щоб схема й код
#    не розходились і в ПРИРОДІ стрілки, не лише в її наявності.
CONTEXTS = {
    "sales":   {"root": "app/sales",   "allow": {"billing": "acl"}},
    "stock":   {"root": "app/stock",   "allow": {"sales": "customer-supplier"}},
    "billing": {"root": "app/billing", "allow": {}},
    "shared":  {"root": "app/shared",  "allow": {}, "shared_kernel": True},
}

def owner_of(module_path: str) -> str | None:
    """Якому контексту належить шлях — за НАЙДОВШИМ збігом кореня."""
    best, best_len = None, -1
    p = module_path.replace("\\", "/")
    for name, meta in CONTEXTS.items():
        root = meta["root"]
        if (p == root or p.startswith(root + "/")) and len(root) > best_len:
            best, best_len = name, len(root)
    return best

def module_to_ctx(dotted: str) -> str | None:
    """import app.billing.invoice -> 'app/billing/invoice' -> контекст billing."""
    return owner_of(dotted.replace(".", "/"))

def discovered_edges(src_root: Path) -> set[tuple[str, str]]:
    """Реальні перетини межі: (from_ctx, to_ctx) з усіх import у коді."""
    edges: set[tuple[str, str]] = set()
    for py in src_root.rglob("*.py"):
        rel = py.relative_to(src_root).with_suffix("")
        frm = owner_of("app/" + str(rel).replace("\\", "/"))
        if frm is None:
            continue                                  # файл поза картою — не учасник
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                targets = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                targets = [node.module]               # level==0 -> абсолютний import
            else:
                continue
            for t in targets:
                to = module_to_ctx(t)
                if to and to != frm:                  # перетин межі
                    edges.add((frm, to))
    return edges

def allowed(frm: str, to: str) -> bool:
    if CONTEXTS.get(to, {}).get("shared_kernel"):     # спільне ядро — легальний виняток
        return True
    return to in CONTEXTS[frm]["allow"]

def main(src: str) -> int:
    edges = discovered_edges(Path(src))
    violations = sorted(e for e in edges if not allowed(*e))
    if not violations:
        print(f"карта тримається: {len(edges)} стрілок, усі оголошені")
        return 0
    print("ЗАБОРОНЕНІ стрілки через межу (нема на карті):", file=sys.stderr)
    for frm, to in violations:
        rel = CONTEXTS.get(frm, {}).get("allow", {})  # підказка: що тут узагалі дозволено
        print(f"  {frm} -> {to}   (дозволено з {frm}: {rel or '—'})", file=sys.stderr)
    return 1

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "app"))

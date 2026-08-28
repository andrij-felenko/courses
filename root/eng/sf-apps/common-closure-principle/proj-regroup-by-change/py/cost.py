# tools/cost.py — ціна зміни: граф компонентів + замикання перезбирання
import re
import sys
from pathlib import Path

SRC = Path("src").resolve()
IMPORT_RE = re.compile(r"""\bfrom\s*['"]([^'"]+)['"]|\brequire\(\s*['"]([^'"]+)['"]\s*\)""")


def component_of(file: Path) -> str:
    """компонент файла = перший сегмент шляху під src/"""
    return file.resolve().relative_to(SRC).parts[0]


def resolve_spec(src_file: Path, spec: str) -> Path | None:
    """'./x' → шлях файла; зовнішній пакет → None (поза нашим графом)"""
    if not spec.startswith("."):
        return None
    base = (src_file.parent / spec).resolve()
    for cand in (base, base.with_name(base.name + ".ts"),
                 base.with_name(base.name + ".tsx"), base / "index.ts"):
        if cand.is_file():
            return cand
    return None


def scan() -> tuple[dict[str, int], dict[str, set[str]]]:
    """size: компонент → скільки файлів; deps: компонент → на кого спирається"""
    size: dict[str, int] = {}
    deps: dict[str, set[str]] = {}

    for file in sorted([*SRC.rglob("*.ts"), *SRC.rglob("*.tsx")]):
        if file.name.endswith(".d.ts"):
            continue
        here = component_of(file)
        size[here] = size.get(here, 0) + 1
        deps.setdefault(here, set())

        for m in IMPORT_RE.finditer(file.read_text(encoding="utf-8")):
            target = resolve_spec(file, m.group(1) or m.group(2))
            if target and (to := component_of(target)) != here:
                deps[here].add(to)          # ребро лише МІЖ компонентами
    return size, deps


def reverse(deps: dict[str, set[str]]) -> dict[str, set[str]]:
    """зворотні ребра: хто чекає перезбирання, коли міняється X"""
    rev: dict[str, set[str]] = {c: set() for c in deps}
    for frm, tos in deps.items():
        for to in tos:
            rev[to].add(frm)
    return rev


def rebuild_set(rev: dict[str, set[str]], touched: set[str]) -> set[str]:
    """транзитивне замикання вгору — саме це перезбере конвеєр"""
    out, stack = set(touched), list(touched)
    while stack:
        for up in rev.get(stack.pop(), ()):
            if up not in out:
                out.add(up)
                stack.append(up)
    return out


def cost(changed: list[str]) -> dict:
    size, deps = scan()
    touched = {component_of(Path(p)) for p in changed}
    rebuilt = rebuild_set(reverse(deps), touched)
    total = sum(size.values())
    hit = sum(size.get(c, 0) for c in rebuilt)
    return {"touched": touched, "rebuilt": rebuilt,
            "components": len(size), "hit": hit, "total": total}


if __name__ == "__main__":
    r = cost(sys.argv[1:])
    lst = lambda s: ", ".join(sorted(s))
    print(f"торкнулися компонентів : {len(r['touched'])}  ({lst(r['touched'])})")
    print(f"перезбирається         : {len(r['rebuilt'])} з {r['components']}  ({lst(r['rebuilt'])})")
    print(f"файлів у перезбиранні  : {r['hit']} з {r['total']} = {round(r['hit'] / r['total'] * 100)}%")

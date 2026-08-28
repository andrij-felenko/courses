def is_descendant(m: Model, eid: str, of: str) -> bool:
    cur = m.by_id(eid).parent
    while cur is not None:
        if cur == of:
            return True
        cur = m.by_id(cur).parent
    return False

def representative(m: Model, eid: str, scope: str, level: str) -> str:
    """Представник вузла на рівні — найгрубша видима коробка над ним."""
    if level == "context":
        return scope if eid == scope or is_descendant(m, eid, scope) else eid
    # container: descendant scope-у піднімаємо до контейнера (прямої дитини scope)
    if eid == scope:
        return scope
    if is_descendant(m, eid, scope):
        cur = eid
        while m.by_id(cur).parent != scope:
            cur = m.by_id(cur).parent
        return cur
    return eid

def _decl(m: Model, eid: str) -> str:
    e = m.by_id(eid)
    label = f"{e.name}<br/>[{e.technology}]" if e.technology else e.name
    return f'{eid}["{label}"]'

def project(m: Model, scope: str, level: str) -> str:
    # 1. переписуємо кожне ребро на представників і прибираємо петлі
    edges: dict[tuple[str, str], str] = {}
    for r in m.relations:
        a = representative(m, r.src, scope, level)
        b = representative(m, r.dst, scope, level)
        if a == b:
            continue                              # сховалось усередині коробки
        edges.setdefault((a, b), r.label)
    # 2. видимі вузли — кінці ребер + гарантовано сам scope / його контейнери
    visible = {n for pair in edges for n in pair}
    if level == "context":
        visible.add(scope)
    else:
        visible.update(c.id for c in m.children(scope))
    # 3. рендер у текст Mermaid
    ids = [e.id for e in m.elements if e.id in visible]
    out = ["flowchart TB"]
    if level == "container":
        out.append(f'  subgraph {scope}["{m.by_id(scope).name}"]')
        out += [f"    {_decl(m, i)}" for i in ids if m.by_id(i).parent == scope]
        out.append("  end")
        out += [f"  {_decl(m, i)}" for i in ids if m.by_id(i).parent != scope and i != scope]
    else:
        out += [f"  {_decl(m, i)}" for i in ids]
    out += [f'  {a} -->|"{lbl}"| {b}' for (a, b), lbl in edges.items()]
    return "\n".join(out)

print(project(shop, "shop", "context"))
print(project(shop, "shop", "container"))

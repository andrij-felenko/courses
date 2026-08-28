# Групуємо прояви у зв'язні компоненти графа відповідностей.
# Кожна група — усі прояви ОДНОГО логічного елемента в різних в'ю.
def resolve_groups(desc: Description) -> list[list[Manifestation]]:
    by_id = {m.id: m for m in desc.manifestations}

    # ненапрямлений список суміжності
    adj: dict[str, list[str]] = {m.id: [] for m in desc.manifestations}
    for c in desc.correspondences:
        adj.setdefault(c.a, []); adj.setdefault(c.b, [])
        adj[c.a].append(c.b); adj[c.b].append(c.a)

    seen: set[str] = set()          # ← без цього циклічна відповідність зациклить обхід
    groups: list[list[Manifestation]] = []
    for start in adj:
        if start in seen:
            continue
        group, stack = [], [start]
        seen.add(start)
        while stack:
            x = stack.pop()
            if x in by_id:
                group.append(by_id[x])
            for y in adj[x]:
                if y not in seen:
                    seen.add(y); stack.append(y)
        groups.append(group)
    return groups

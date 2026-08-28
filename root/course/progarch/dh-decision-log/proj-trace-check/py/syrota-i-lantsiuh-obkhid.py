def check_orphans(adrs: dict[int, Adr], repo: Path) -> list[Break]:
    out: list[Break] = []
    for a in adrs.values():
        if a.status != "accepted":                    # лінтимо лише ЖИВІ; замінене хай спочиває
            continue
        if not a.code and not a.view:
            out.append(Break(a.id, "ухвалене, а ні code:, ні view: — висить без якоря"))
        for rel in a.code:                            # названий код мусить існувати
            if not (repo / rel).exists():
                out.append(Break(a.id, f"code: {rel} — такого файлу в репозиторії нема"))
    return out


def check_chains(adrs: dict[int, Adr]) -> list[Break]:
    out: list[Break] = []
    for a in adrs.values():
        for tgt in a.superseded_by:                   # ціль існує + ланка дзеркальна
            b = adrs.get(tgt)
            if b is None:
                out.append(Break(a.id, f"«замінено {canon(tgt)}», а того ADR нема — висяча ланка"))
            elif a.num not in b.supersedes:
                out.append(Break(a.id,
                    f"каже «замінено {canon(tgt)}», але {canon(tgt)} не каже «замінює {a.id}»"))
        for tgt in a.supersedes:
            b = adrs.get(tgt)
            if b is None:
                out.append(Break(a.id, f"«замінює {canon(tgt)}», а того ADR нема"))
            elif a.num not in b.superseded_by:
                out.append(Break(a.id,
                    f"каже «замінює {canon(tgt)}», але {canon(tgt)} не каже «замінено {a.id}»"))
        if a.superseded_by and a.status != "superseded":
            out.append(Break(a.id,
                f"має «замінено», а статус «{a.status}» — замінене мусить бути superseded"))
        if a.status == "superseded" and not a.superseded_by:
            out.append(Break(a.id, "статус superseded, а «замінено» порожнє — чим замінили?"))
    out += find_cycles(adrs)
    return out


def find_cycles(adrs: dict[int, Adr]) -> list[Break]:
    """Пошук кілець у графі замін — обхід у глибину з трьома кольорами вузлів."""
    WHITE, GRAY, BLACK = 0, 1, 2                       # ще не бачив / у стеку / завершений
    color = {n: WHITE for n in adrs}
    out: list[Break] = []

    def walk(node: int, stack: list[int]) -> None:
        color[node] = GRAY
        stack.append(node)
        for nxt in adrs[node].superseded_by:
            if nxt not in adrs:
                continue                               # відсутню ціль уже впіймали вище
            if color[nxt] == GRAY:                     # ребро назад у стек → знайшли цикл
                loop = stack[stack.index(nxt):] + [nxt]
                out.append(Break(canon(loop[0]),
                    "цикл замін: " + " → ".join(canon(x) for x in loop)
                    + " — рішення (транзитивно) замінює саме себе"))
            elif color[nxt] == WHITE:
                walk(nxt, stack)
        stack.pop()
        color[node] = BLACK

    for n in adrs:
        if color[n] == WHITE:
            walk(n, [])
    return out

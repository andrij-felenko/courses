def choose_evolution_strategy(c: DataChange) -> Decision:
    # 0. ҐВАРДІЯ: сенс живого ключа не перепризначають — перш за все.
    if c.kind == "redefine":
        return Decision("FORBIDDEN", "none", False, "n/a",
            "новий сенс = новий ключ/версія; старий ключ лишається старим сенсом")

    # 1. Похідні обходять матрицю: не мігруй — перерахуй.
    if c.derived:
        return Decision("REBUILD", "none", False, "n/a",
            "зміни функцію зведення, перебудуй вікно із сирого")

    # 2. Адитивне: старі дані лишаються валідні.
    if c.kind == "add":
        return Decision("ADD",
            "short" if c.controls_both_sides else "long", False,
            "n/a" if c.controls_both_sides else "forward",
            "старий читач мусить ІГНОРУВАТИ незнайоме, а не падати на ньому")

    # 3. Прибирання — фаза contract давнішої expand.
    if c.kind == "remove":
        return Decision("RETIRE",
            "short" if c.rewritable else "may-never-close", False, "backward",
            "гейт: ні писаря, ні ДОСЯЖНОГО збереженого запису на старій формі")

    # 4. reshape джерела правди — вирішує переписуваність.
    if not c.rewritable:
        return Decision("SCHEMA_ON_READ",
            "grows-with-decoder" if c.controls_both_sides else "may-never-close",
            False, "backward" if c.controls_both_sides else "backward+forward",
            "тегай запис версією, зводь на читанні; історію не переписуй")

    return Decision("MIGRATE_IN_PLACE",
        "short" if c.controls_both_sides else "long", True,
        "backward" if c.controls_both_sides else "backward+forward",
        "expand → backfill пакетами → contract")

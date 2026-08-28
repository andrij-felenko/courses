reg = [
    Stakeholder("Замовник",     True,  True,  False, True,  Attr.COST),
    Stakeholder("Спонсор",      True,  True,  False, False, Attr.COST),
    Stakeholder("Оператор",     False, True,  True,  True,  Attr.AVAIL),
    Stakeholder("Аудитор",      True,  True,  True,  True,  Attr.SEC, hard=True),
    Stakeholder("Супровід",     False, True,  False, True,  Attr.MODIF),
    Stakeholder("Користувач",   False, True,  False, True,  Attr.PERF),
    Stakeholder("Постачальник", False, True,  False, False, Attr.COST),
]

decisions = [
    Decision("бюджет і план-графік",    Attr.COST),
    Decision("плагіни способів оплати", Attr.MODIF),
    Decision("кеш гарячих запитів",     Attr.PERF),
]

params = [
    Parameter("ширина реплікації даних", (Push(Attr.AVAIL, +1), Push(Attr.SEC, -1))),
    Parameter("розмір пулу потоків",     (Push(Attr.PERF, +1),)),                       # точка чутливості
    Parameter("рівень кешування",        (Push(Attr.PERF, +1), Push(Attr.COST, -1))),   # компроміс без двох ваг
]

views = [
    View("Контекст",    frozenset({Attr.COST, Attr.SEC})),
    View("Контейнери",  frozenset({Attr.PERF, Attr.AVAIL})),
    View("Розгортання", frozenset({Attr.AVAIL, Attr.SEC})),
    View("Сценарії",    frozenset({Attr.AVAIL, Attr.PERF, Attr.SEC, Attr.COST})),
]

def analyse(reg, decisions, params, views) -> None:
    print("ВАГОМІСТЬ І КУДИ СПРЯМУВАТИ УВАГУ")
    for s in reg:
        print(f"  {s.name:<12} {salience_class(s):<13} → {quadrant(s)}")

    print("\nНЕЗАКРИТІ ТУРБОТИ")
    for g in coverage_gaps(reg, decisions):
        tag = "ВЕТО " if g.veto else "warn "
        print(f"  {tag} {g.who:<10} дбає про {g.concern.value} (осей: {g.score})")

    print("\nТОЧКИ КОМПРОМІСУ")
    for t in tradeoff_points(reg, params):
        print(f"  «{t.param}»: {t.up_who}({t.up_attr.value} ↑) проти {t.down_who}({t.down_attr.value} ↓)")

    print("\nМАТРИЦЯ В'Ю — порожні рядки")
    empty = empty_rows(view_matrix(reg, views))
    if not empty:
        print("  усі рядки закриті")
    else:
        for i in empty:
            print(f"  ✗ {reg[i].name} ({reg[i].concern.value}) — жодне в'ю не показує")

analyse(reg, decisions, params, views)

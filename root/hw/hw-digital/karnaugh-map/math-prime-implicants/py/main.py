# Прості імпліканти G = Σm(0,1,2,5,6,7): яку одиницю накриває кожна
PI = {
    "P1": ({0, 1}, "Ā·B̄"),
    "P2": ({1, 5}, "B̄·C"),
    "P3": ({5, 7}, "A·C"),
    "P4": ({6, 7}, "A·B"),
    "P5": ({2, 6}, "B·C̄"),
    "P6": ({0, 2}, "Ā·C̄"),
}
ONES = [0, 1, 2, 5, 6, 7]

# Функція Петрика: добуток по одиницях від суми простих імплікант, що її накривають.
# Розкриваємо дужки, тримаючи кожен доданок множиною імен: множина сама дає
# ідемпотентність (P·P = P), а відсів надмножин — поглинання (X + X·Y = X).
sop = [frozenset()]                       # нейтральний елемент добутку: «1»
for m in ONES:
    clause = [name for name, (cov, _) in PI.items() if m in cov]   # (Pi + Pj)
    sop = {term | {name} for term in sop for name in clause}       # розкрили дужки
    sop = {t for t in sop if not any(o < t for o in sop)}          # поглинання

# Кожен доданок — незвідне покриття. Ціна: число доданків, тоді число літер.
def cost(term):
    return (len(term), sum(len(PI[n][1].split("·")) for n in term))

# Друга частина ключа — самі імена: інакше рівні за ціною покриття
# ставали б у порядку обходу множини, а він залежить від хешу.
for term in sorted(sop, key=lambda t: (cost(t), sorted(t))):
    terms, lits = cost(term)
    expr = " + ".join(PI[n][1] for n in sorted(term))
    print("%d доданки, %2d літер:  G = %-26s %s" % (terms, lits, expr, sorted(term)))

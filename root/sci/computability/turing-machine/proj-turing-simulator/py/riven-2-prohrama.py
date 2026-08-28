def encode(delta):                                     # правило → рівно 7 клітинок
    return "".join(q + c + w + d + n for (q, c), (w, d, n) in sorted(delta.items()))

def load(delta, w, start="q0"):                        # опис + стан + робоча стрічка
    return "^" + encode(delta) + "#" + start + "|*" + w

def universal(tape_str, limit=200_000):
    T = {i: c for i, c in enumerate(tape_str)}
    at = lambda i: T.get(i, BL)
    left, h = 0, 1
    while at(h) != "#":                                # h — межа «#», за нею стан M
        h += 1
    bar = h + 3                                        # bar — межа «|», за нею стрічка M
    for steps in range(limit + 1):
        q = at(h + 1) + at(h + 2)                      # хто я: стан M — 2 клітинки
        if q == "qa":
            return "ПРИЙНЯТО", steps, work(T, bar)
        if q == "qr":
            return "ВІДКИНУТО", steps, work(T, bar)
        s = bar
        while at(s) != "*":                            # що бачу: дійти до позначки голівки
            s += 1
        c = at(s + 1)
        p = left + 1                                   # шукаємо правило: крок сімками
        while p < h and not (at(p) + at(p + 1) == q and at(p + 2) == c):
            p += 7
        if p >= h:
            return "ВІДКИНУТО", steps, work(T, bar)
        T[s + 1] = at(p + 3)                           # пише
        T[h + 1], T[h + 2] = at(p + 5), at(p + 6)      # новий стан
        if at(p + 4) == "R":
            T[s], T[s + 1] = at(s + 1), "*"            # позначка міняється з сусідом
        else:
            if s - 1 == bar:                           # ліворуч межа: посунути весь опис
                for i in range(left, bar + 1):
                    T[i - 1] = at(i)
                T[bar] = BL
                left -= 1; h -= 1; bar -= 1
            T[s], T[s - 1] = at(s - 1), "*"
    return "НЕ ЗНАЮ", limit, work(T, bar)

def work(T, bar):
    return "".join(T[i] for i in sorted(k for k in T if k > bar) if T[i] != "*").strip(BL)

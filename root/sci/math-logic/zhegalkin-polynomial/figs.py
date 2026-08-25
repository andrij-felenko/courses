# -*- coding: utf-8 -*-
"""Фігури до статті «Поліном Жегалкіна». Запуск із теки теми: python figs.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

ACC = "#7c3aed"   # акцент — фіолетовий (поліном/алгебра)


def cell(cx, cy, w, h, s, size=19, fill=FILL, stroke=LINE, color=INK, bold=False):
    """Прямокутна клітина з центрованим написом (текст не вилазить — fitbox)."""
    return fitbox(cx - w / 2, cy - h / 2, w, h, s, size=size, fill=fill,
                  stroke=stroke, color=color, bold=bold)


# ── Фігура 1: словник «логіка → арифметика в ℤ₂» + правила згортання ─────────
def fig_bridge():
    W, H = 780, 430
    fr = []
    fr.append(text(W / 2, 30, "Логіка стає арифметикою за модулем 2", size=18, bold=True))
    fr.append(text(200, 66, "логічний запис", size=15, color=MUTED, bold=True))
    fr.append(text(560, 66, "многочлен у ℤ₂  (⊕ = +,  · = ×)", size=15, color=MUTED, bold=True))

    rows = [
        ("¬a",       "1 ⊕ a"),
        ("a ∧ b",    "a · b"),
        ("a ∨ b",    "a ⊕ b ⊕ a·b"),
        ("a ⊕ b",    "a ⊕ b"),
    ]
    y = 108
    for lft, rgt in rows:
        fr.append(cell(200, y, 200, 44, lft, size=20, bold=True))
        fr.append(arrow(312, y, 430, y, color=ACC))
        fr.append(cell(590, y, 250, 44, rgt, size=20, fill="#f3eefb", stroke=ACC))
        y += 58

    # смуга правил згортання
    fr.append(line(60, 348, 720, 348, color="#d0d5db"))
    fr.append(text(W / 2, 372, "два правила, що згортають будь-який вираз:", size=14, color=MUTED))
    fr.append(cell(240, 406, 230, 42, "x · x = x", size=20, bold=True,
                   fill="#eef7f0", stroke=FIELD))
    fr.append(cell(540, 406, 230, 42, "x ⊕ x = 0", size=20, bold=True,
                   fill="#eef7f0", stroke=FIELD))
    render(os.path.join(OUT, 'bridge.svg'), W, H, *fr)


# ── Фігура 2: швидке перетворення Мебіуса (таблиця → коефіцієнти) для МАЖ ─────
def fig_mobius():
    W, H = 1000, 580
    fr = []
    fr.append(text(W / 2, 30, "Від таблиці істинності до полінома: перетворення Мебіуса",
                   size=18, bold=True))

    # рядки: (a b c) для 000..111
    combos = ["000", "001", "010", "011", "100", "101", "110", "111"]
    monos = ["1", "c", "b", "b·c", "a", "a·c", "a·b", "a·b·c"]
    stages = [
        [0, 0, 0, 1, 0, 1, 1, 1],   # вхід: МАЖ(a,b,c)
        [0, 0, 0, 1, 0, 1, 1, 0],   # ⊕ за бітом c
        [0, 0, 0, 1, 0, 1, 1, 1],   # ⊕ за бітом b
        [0, 0, 0, 1, 0, 1, 1, 0],   # ⊕ за бітом a → коефіцієнти
    ]
    colx = [300, 470, 640, 830]
    heads = ["f(a,b,c)", "крок c", "крок b", "коеф."]
    y0, dy, cw, ch = 108, 46, 44, 34

    # заголовок лівого стовпця й самі підписи рядків (комбінація входів)
    fr.append(text(150, y0 - 30, "a b c", size=14, color=MUTED, bold=True))
    for c, combo in zip(colx, heads):
        fr.append(text(c, y0 - 30, combo, size=14, color=MUTED, bold=True))

    for i, combo in enumerate(combos):
        y = y0 + i * dy
        fr.append(text(150, y + 6, " ".join(combo), size=17, color=INK))
        for j, col in enumerate(colx):
            v = stages[j][i]
            last = (j == 3)
            fr.append(cell(col, y, cw, ch, str(v), size=18, bold=last,
                           fill=("#f3eefb" if last and v else FILL),
                           stroke=(ACC if last and v else LINE),
                           color=(ACC if last and v else INK)))
        # праворуч від останнього стовпця — моном, якщо коефіцієнт 1
        if stages[3][i]:
            fr.append(text(900, y + 6, "→ " + monos[i], size=16, color=ACC, bold=True))

    # короткі стрілки в проміжках (не перетинають клітин)
    ya = y0 + 8 * dy + 6
    for k in range(3):
        xm = (colx[k] + colx[k + 1]) / 2
        fr.append(arrow(xm - 26, ya, xm + 26, ya, color="#b9a7e6"))
        fr.append(text(xm, ya + 26, "⊕ біт " + "cba"[k], size=13, color=MUTED))

    fr.append(text(W / 2, H - 22, "МАЖ(a, b, c)  =  a·b  ⊕  b·c  ⊕  a·c",
                   size=19, bold=True, color=ACC))
    render(os.path.join(OUT, 'mobius.svg'), W, H, *fr)


# ── Фігура 3: єдиність — 2ⁿ мономів ↔ вектор коефіцієнтів ↔ функція ──────────
def fig_unique():
    W, H = 860, 450
    fr = []
    fr.append(text(W / 2, 30, "Чому форма ЄДИНА (для n = 2)", size=18, bold=True))

    monos = ["1", "a", "b", "a·b"]
    coefs = ["0", "1", "1", "1"]          # приклад: OR = a⊕b⊕ab
    xs = [170, 350, 530, 710]
    # ряд мономів (усі підмножини змінних)
    fr.append(text(W / 2, 78, "усі 2ⁿ = 4 можливі мономи (підмножини змінних):",
                   size=14, color=MUTED))
    for x, m in zip(xs, monos):
        fr.append(cell(x, 116, 150, 46, m, size=21, bold=True))
    # ряд коефіцієнтів 0/1
    fr.append(text(W / 2, 176, "кожному — свій коефіцієнт 0 або 1:", size=14, color=MUTED))
    for x, c in zip(xs, coefs):
        on = (c == "1")
        fr.append(cell(x, 214, 150, 46, c, size=21, bold=True,
                       fill=("#f3eefb" if on else FILL),
                       stroke=(ACC if on else LINE),
                       color=(ACC if on else MUTED)))
    # складений поліном
    fr.append(cell(W / 2, 300, 470, 50, "0·1 ⊕ 1·a ⊕ 1·b ⊕ 1·a·b  =  a ⊕ b ⊕ a·b",
                   size=19, fill="#f3eefb", stroke=ACC, color=ACC, bold=True))
    # висновок-лічба
    fr.append(cell(W / 2, 392, 720, 60,
                   "4 коефіцієнти по 2 значення = 2⁴ = 16 наборів = стільки ж, скільки\n"
                   "булевих функцій двох змінних (2^(2ⁿ)) → відповідність один-до-одного",
                   size=15, fill="#eef7f0", stroke=FIELD))
    render(os.path.join(OUT, 'unique.svg'), W, H, *fr)


# ── Фігура 4: степінь полінома — від лінійних до нелінійних ──────────────────
def fig_degree():
    W, H = 900, 400
    fr = []
    fr.append(text(W / 2, 30, "Степінь полінома: лінійне проти нелінійного", size=18, bold=True))

    xs = [140, 340, 560, 780]
    degs = ["степінь 0", "степінь 1", "степінь 2", "степінь 3"]
    examples = [
        "0\n1",
        "a\na ⊕ b\na ⊕ b ⊕ 1",
        "a·b   (AND)\na·b ⊕ b·c ⊕ a·c",
        "a·b·c",
    ]
    tags = ["сталі", "ЛІНІЙНІ / афінні", "нелінійні", "…"]
    # вісь
    fr.append(line(80, 300, 840, 300, color="#c8ccd2", sw=2))
    for x, d, ex, tg in zip(xs, degs, examples, tags):
        fr.append(text(x, 322, d, size=14, color=MUTED, bold=True))
        lin = (tg.startswith("ЛІН"))
        fr.append(cell(x, 150, 190, 96, ex, size=16,
                       fill=("#f3eefb" if lin else FILL),
                       stroke=(ACC if lin else LINE),
                       color=INK, bold=False))
        fr.append(text(x, 348, tg, size=13,
                       color=(ACC if lin else MUTED), bold=lin))
    fr.append(text(W / 2, H - 18,
                   "XOR — степінь 1 (лінійна); AND — степінь 2. Що вищий степінь, то «нелінійніша» функція.",
                   size=14, color=INK))
    render(os.path.join(OUT, 'degree.svg'), W, H, *fr)


# ── Фігура 5 (вставка math): лема інтервалів у ґратці підмножин ───────────────
def fig_mobius_lemma():
    import math
    W, H = 940, 540
    fr = []
    fr.append(text(W / 2, 32, "Лема інтервалів: чому виживає лише доданок R = S",
                   size=18, bold=True))

    R = 28  # радіус вузла
    node = {
        "∅":   (300, 452),
        "a":   (180, 332), "b": (300, 332), "c": (420, 332),
        "ab":  (180, 212), "ac": (300, 212), "bc": (420, 212),
        "abc": (300, 100),
    }
    edges = [
        ("∅", "a"), ("∅", "b"), ("∅", "c"),
        ("a", "ab"), ("a", "ac"),
        ("b", "ab"), ("b", "bc"),
        ("c", "ac"), ("c", "bc"),
        ("ab", "abc"), ("ac", "abc"), ("bc", "abc"),
    ]
    hi_nodes = {"∅", "a", "b", "ab"}                  # інтервал [∅,{a,b}]
    hi_edges = {("∅", "a"), ("∅", "b"), ("a", "ab"), ("b", "ab")}

    def trim(p, q, r):
        x1, y1 = p
        x2, y2 = q
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        return x1 + ux * r, y1 + uy * r, x2 - ux * r, y2 - uy * r

    for u, v in edges:
        x1, y1, x2, y2 = trim(node[u], node[v], R + 2)
        on = (u, v) in hi_edges
        fr.append(line(x1, y1, x2, y2, color=(ACC if on else "#c8ccd2"),
                       sw=(3 if on else 1.6)))
    for name, (cx, cy) in node.items():
        on = name in hi_nodes
        fr.append(circle(cx, cy, R, fill=("#e9dbfb" if on else FILL),
                         stroke=(ACC if on else LINE), sw=(2.4 if on else 1.5)))
        fr.append(text(cx, cy + 6, name, size=16, bold=on,
                       color=(ACC if on else INK)))

    fr.append(text(300, 502, "виділено інтервал [∅, {a,b}] — рівно 2² = 4 набори T",
                   size=13, color=MUTED))

    # права панель — сама лема
    fr.append(text(724, 118, "вузол = підмножина змінних", size=14, bold=True, color=MUTED))
    lemma = [
        "#{ T : R ⊆ T ⊆ S } = 2^|S∖R|",
        "тут R = ∅, S = {a,b}:  2² = 4 набори",
        "у XOR кожен c_R береться 2^|S∖R| разів",
        "парне число копій гине  (x ⊕ x = 0)",
        "2^k непарне  ⟺  k = 0  ⟺  R = S",
        "→ переживає лише доданок R = S",
    ]
    fr.append(fitbox(538, 150, 376, 220, "\n".join(lemma), size=16, pad=13,
                     fill="#f3eefb", stroke=ACC))
    render(os.path.join(OUT, 'mobius-lemma.svg'), W, H, *fr)


# ── Фігура 6 (вставка math): M² = I над GF(2) — інволюція ────────────────────
def fig_involution():
    W, H = 900, 470
    fr = []
    fr.append(text(W / 2, 32, "Перетворення — це множення на M, а M² = I над GF(2)",
                   size=18, bold=True))

    labels = ["∅", "a", "b", "ab"]
    M = [[1, 0, 0, 0],
         [1, 1, 0, 0],
         [1, 0, 1, 0],
         [1, 1, 1, 1]]
    Id = [[1 if i == j else 0 for j in range(4)] for i in range(4)]
    cs = 44

    def matrix(ox, oy, mat, caption):
        g = []
        for k, l in enumerate(labels):
            g.append(text(ox + k * cs + cs / 2, oy - 12, l, size=13, color=MUTED))
            g.append(text(ox - 16, oy + k * cs + cs / 2 + 5, l, size=13,
                          color=MUTED, anchor="end"))
        for i in range(4):
            for j in range(4):
                v = mat[i][j]
                g.append(rect(ox + j * cs, oy + i * cs, cs, cs,
                              fill=("#f3eefb" if v else BG),
                              stroke=(ACC if v else "#d0d5db"), sw=1.4, rx=3))
                g.append(text(ox + j * cs + cs / 2, oy + i * cs + cs / 2 + 6,
                              str(v), size=18, bold=bool(v),
                              color=(ACC if v else MUTED)))
        g.append(text(ox + 2 * cs, oy + 4 * cs + 26, caption, size=14, bold=True))
        return g

    ox1, oy = 150, 120
    fr += matrix(ox1, oy, M, "M  (нижньотрикутна)")
    fr.append(text(ox1 + 4 * cs + 46, oy + 2 * cs, "²  =", size=26, bold=True))
    ox2 = ox1 + 4 * cs + 96
    fr += matrix(ox2, oy, Id, "I  (тотожна)")

    fr.append(text(W / 2, H - 46,
                   "M[A][S] = 1, коли S ⊆ A.   f = M·c (таблиця з коефіцієнтів),   "
                   "c = M·f (коефіцієнти з таблиці) — той самий M.",
                   size=13, color=INK))
    fr.append(text(W / 2, H - 22,
                   "M² = I  ⟹  прогін удруге повертає вихідне: перетворення Мебіуса "
                   "над GF(2) — інволюція.",
                   size=13, color=INK))
    render(os.path.join(OUT, 'involution.svg'), W, H, *fr)


# ── Фігура 7 (вставка hist): який «плюс» лишає логіку арифметикою ─────────────
def fig_which_plus():
    W, H = 960, 400
    fr = []
    fr.append(text(W / 2, 34, "Яку дію взяти за «плюс»?", size=18, bold=True))

    caps = ["Буль · «+»", "Джевонс, Пірс · «∨»", "Жегалкін · «⊕»"]
    bodies = [
        "x + x = ?\n\nне визначено —\nлише роз'єднані\nкласи",
        "x ∨ x = x\n\nідемпотентно:\nце вже НЕ\nарифметика",
        "x ⊕ x = 0\n\nдодавання мод 2 —\nсправжня\nарифметика",
    ]
    xs = [175, 480, 785]
    for i, (x, cap, body) in enumerate(zip(xs, caps, bodies)):
        acc = (i == 2)
        fr.append(text(x, 86, cap, size=15, color=(ACC if acc else MUTED), bold=True))
        fr.append(cell(x, 212, 252, 176, body, size=17,
                       fill=("#f3eefb" if acc else FILL),
                       stroke=(ACC if acc else LINE), color=INK))
    fr.append(text(W / 2, 366,
                   "Лише ⊕ підкоряється арифметиці (1 ⊕ 1 = 0) — тому з нього виходить єдиний канонічний многочлен.",
                   size=14, color=INK))
    render(os.path.join(OUT, 'which-plus.svg'), W, H, *fr)


# ── Фігура 8 (вставка hist): дві незалежні дороги до однієї форми ─────────────
def fig_two_roads():
    W, H = 1000, 620
    fr = []
    fr.append(text(W / 2, 34, "Дві незалежні дороги до однієї форми", size=18, bold=True))
    fr.append(text(285, 76, "гілка логіки: Європа → Москва", size=14, color=MUTED, bold=True))
    fr.append(text(720, 76, "гілка кодування: США", size=14, color=MUTED, bold=True))

    # ліва колонка — традиція алгебри логіки
    lx = 285
    left = [
        (134, False, "Джордж Буль · 1854\n«+» лише для роз'єднаних класів"),
        (246, False, "Джевонс (1864), Пірс (1867)\n«або» інклюзивне: x ∨ x = x — арифметику втрачено"),
        (358, True,  "Іван Жегалкін · 1927–28\n⊕ як «+»: x ⊕ x = 0 · логіка = арифметика в ℤ₂"),
    ]
    for y, acc, s in left:
        fr.append(cell(lx, y, 410, 80, s, size=15,
                       fill=("#f3eefb" if acc else FILL),
                       stroke=(ACC if acc else LINE), color=INK))
    fr.append(arrow(lx, 176, lx, 204, color="#b9a7e6"))
    fr.append(arrow(lx, 288, lx, 316, color="#b9a7e6"))

    # права колонка — коди виправлення похибок
    rx = 720
    right = [
        (192, "Девід Маллер · 1954\nбулева алгебра для схем + виявлення похибок"),
        (312, "Ірвінг Рід · 1954\nсхема декодування → коди Ріда–Маллера"),
    ]
    for y, s in right:
        fr.append(cell(rx, y, 390, 80, s, size=15))
    fr.append(arrow(rx, 234, rx, 270, color="#b9a7e6"))

    # збіжність
    fr.append(text(W / 2, 440, "незалежно, ≈ чверть століття потому", size=14,
                   color=MUTED, italic=True))
    fr.append(arrow(lx, 400, 405, 488, color=ACC))
    fr.append(arrow(rx, 354, 605, 488, color=ACC))
    fr.append(cell(W / 2, 524, 810, 76,
                   "та сама форма, три імені:\n"
                   "поліном Жегалкіна  =  ANF (алгебрична нормальна форма)  =  PPRM (додатно-полярне Рід–Маллер)",
                   size=15, bold=True, fill="#f3eefb", stroke=ACC, color=ACC))
    render(os.path.join(OUT, 'two-roads.svg'), W, H, *fr)


# ── Фігура 9 (вставка proj): метелик перетворення на місці ───────────────────
def fig_butterfly():
    W, H = 1000, 580
    fr = []
    fr.append(text(W / 2, 32, "Перетворення на місці: метелик XOR за log₂N кроків",
                   size=18, bold=True))

    n, N = 3, 8
    xs = [270, 490, 710, 910]
    heads = ["таблиця f", "після біта 0", "після біта 1", "коеф. (біт 2)"]
    y0, dy = 130, 52
    ys = [y0 + i * dy for i in range(N)]

    # ліворуч — двійковий індекс кожного рядка
    fr.append(text(120, y0 - 44, "індекс", size=13, color=MUTED, bold=True))
    for i in range(N):
        fr.append(text(120, ys[i] + 5, format(i, "03b"), size=15, color=INK))
    # заголовки стовпців
    for c, h in zip(xs, heads):
        fr.append(text(c, y0 - 44, h, size=13, color=MUTED, bold=True))

    # сірі «переносні» лінії (значення йде далі незмінним) для кожного рядка
    for c in range(3):
        for i in range(N):
            fr.append(line(xs[c] + 15, ys[i], xs[c + 1] - 15, ys[i],
                           color="#d7dbe0", sw=1.4))
    # діагоналі XOR: із рядка-з-нулем (біт = 0) стрілка в рядок-з-одиницею (біт = 1)
    for c in range(3):
        bit = 1 << c
        for lo in range(N):
            if lo & bit:
                continue
            hi = lo | bit
            fr.append(arrow(xs[c] + 15, ys[lo], xs[c + 1] - 15, ys[hi],
                            color=ACC, sw=1.7))
    # вузли-кружечки поверх ліній
    for c in range(4):
        for i in range(N):
            fr.append(circle(xs[c], ys[i], 6, fill="#ffffff", stroke=INK, sw=1.4))

    fr.append(text(W / 2, H - 30,
                   "кожну клітину чіпають n = 3 рази  →  усього ≈ n·2ⁿ⁻¹ дій XOR,",
                   size=14, color=INK))
    fr.append(text(W / 2, H - 10,
                   "а пам'ять лишається та сама — жодного зайвого масиву (на місці)",
                   size=14, color=INK))
    render(os.path.join(OUT, 'butterfly.svg'), W, H, *fr)


# ── Фігура 10 (вставка proj): прямий підрахунок 3ⁿ проти метелика n·2ⁿ ────────
def fig_speedup():
    W, H = 860, 440
    fr = []
    fr.append(text(W / 2, 32, "Чому «швидке»: прямо 3ⁿ проти метелика n·2ⁿ",
                   size=18, bold=True))

    cols = ["n", "прямо  3ⁿ", "метелик  n·2ⁿ", "виграш"]
    colx = [120, 360, 600, 770]
    rows = [
        ("8",  "6 561",           "2 048",       "×3"),
        ("12", "531 441",         "49 152",      "×11"),
        ("16", "43 046 721",      "1 048 576",   "×41"),
        ("20", "3 486 784 401",   "20 971 520",  "×166"),
        ("24", "282 429 536 481", "402 653 184", "×700"),
    ]
    y0, dy = 116, 54
    for x, h in zip(colx, cols):
        fr.append(text(x, y0 - 28, h, size=14, color=MUTED, bold=True))
    fr.append(line(60, y0 - 12, 810, y0 - 12, color="#c8ccd2", sw=1.5))
    for r, row in enumerate(rows):
        y = y0 + r * dy
        for j, (x, val) in enumerate(zip(colx, row)):
            acc = (j == 3)
            fr.append(text(x, y + 6, val, size=16, bold=acc,
                           color=(ACC if acc else INK)))
    fr.append(text(W / 2, H - 24,
                   "прямий підрахунок XOR-ить підмножини кожного монома (разом 3ⁿ);",
                   size=13, color=MUTED))
    fr.append(text(W / 2, H - 6,
                   "метелик згортає весь масив n проходами — і працює на місці",
                   size=13, color=MUTED))
    render(os.path.join(OUT, 'speedup.svg'), W, H, *fr)


if __name__ == '__main__':
    fig_bridge()
    fig_mobius()
    fig_unique()
    fig_degree()
    fig_mobius_lemma()
    fig_involution()
    fig_which_plus()
    fig_two_roads()
    fig_butterfly()
    fig_speedup()
    print("OK: 10 фігур у", OUT)

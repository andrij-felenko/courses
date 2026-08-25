# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def cell(x, y, w, h, s, size=15, fill=FILL, stroke=LINE, color=INK, bold=False):
    """Клітинка сітки з одним коротким написом усередині."""
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.4, rx=4)
    out += text(x + w / 2.0, y + h / 2.0 + size * 0.35, s, size=size, color=color, bold=bold)
    return out


def fig_weights():
    """Те саме слово, прочитане з вагами 2^k (значення) і з вагою 1 (popcount)."""
    W, H = 780, 350
    els = []

    bits = [1, 0, 1, 1, 0, 1, 0, 0]
    wts = [128, 64, 32, 16, 8, 4, 2, 1]

    els.append(text(205, 62, "Значення числа: ваги 2ᵏ", size=14, bold=True))
    els.append(text(575, 62, "popcount: усі ваги 1", size=14, bold=True))

    for i, b in enumerate(bits):
        # ліва панель — біти зі своїми вагами
        x = 35 + i * 43
        els.append(cell(x, 85, 38, 40, str(b), size=16,
                        fill="#fdecea" if b else FILL,
                        stroke=POS if b else LINE))
        els.append(text(x + 19, 147, str(wts[i]), size=12, color=MUTED))
        # права панель — ті самі біти, вага в кожного одна
        x2 = 405 + i * 43
        els.append(cell(x2, 85, 38, 40, str(b), size=16,
                        fill="#eaf7ef" if b else FILL,
                        stroke=FIELD if b else LINE))
        els.append(text(x2 + 19, 147, "1", size=12, color=MUTED))

    els.append(text(205, 190, "128 + 32 + 16 + 4 = 180", size=15, color=POS, bold=True))
    els.append(text(205, 214, "число, яке лежить у регістрі", size=12, color=MUTED))
    els.append(text(575, 190, "1 + 1 + 1 + 1 = 4", size=15, color=FIELD, bold=True))
    els.append(text(575, 214, "скільки розрядів заселено", size=12, color=MUTED))

    els.append(line(390, 52, 390, 232, color=MUTED, sw=1.2, dash="4 4"))

    els.append(mtext(W / 2.0, 272, [
        "АЛП складає розряди з вагами 2ᵏ, і перенос біжить убік лише на один розряд за раз.",
        "popcount складає ті самі розряди з вагою 1 — усі 64 мусять зійтися в одному числі.",
    ], size=13, color=INK, lh=1.5))

    return render(os.path.join(OUT, 'weights.svg'), W, H, *els,
                  title="Те саме слово, прочитане з різними вагами")


def fig_swar():
    """Дерево половинних сум усередині слова: 16 -> 8 -> 4 -> 2 -> 1."""
    W, H = 900, 480
    els = []

    rows = [
        [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1],
        [1, 2, 1, 1, 2, 1, 0, 1],
        [3, 2, 3, 1],
        [5, 4],
        [9],
    ]
    labels = [
        "16 однобітних\nлічильників (0…1)",
        "8 полів по 2 біти\n(0…2)",
        "4 поля по 4 біти\n(0…4)",
        "2 поля по 8 бітів\n(0…8)",
        "одне число\n(0…16)",
    ]
    colors = [LINE, NEG, FIELD, POS, INK]

    x0, pitch = 250, 38.75
    y0, dy, ch = 70, 78, 42

    for r, vals in enumerate(rows):
        y = y0 + r * dy
        span = 2 ** r
        els.append(mtext(24, y + 14, labels[r].split("\n"), size=11,
                         color=MUTED, anchor="start", lh=1.4))
        for i, v in enumerate(vals):
            x = x0 + i * span * pitch
            w = span * pitch - 6
            hot = v > 0
            els.append(cell(x, y, w, ch, str(v), size=15,
                            fill="#eef3fb" if hot else "#ffffff",
                            stroke=colors[r] if hot else MUTED,
                            color=colors[r] if hot else MUTED,
                            bold=(r > 0)))

    els.append(mtext(W / 2.0, 428, [
        "Кожен крок половинить кількість лічильників і вдвічі розширює кожен —",
        "чотири кроки для 16 бітів, шість для 64. Слово при цьому не покидає регістра.",
    ], size=13, color=INK, lh=1.5))

    return render(os.path.join(OUT, 'swar-tree.svg'), W, H, *els,
                  title="Дерево половинних сум прямо всередині слова")


def fig_hw_tree():
    """Те саме дерево в кремнії: шість тонких рівнів суматорів."""
    W, H = 840, 500
    els = []

    rows = [
        (720, "64 біти на вході — 64 лічильники по 1 біту", FILL, LINE),
        (650, "32 суматори 1+1 → 32 числа по 2 біти", "#eef3fb", NEG),
        (580, "16 суматорів 2+2 → 16 чисел по 3 біти", "#eef3fb", NEG),
        (510, "8 суматорів 3+3 → 8 чисел по 4 біти", "#eaf7ef", FIELD),
        (440, "4 суматори 4+4 → 4 числа по 5 бітів", "#eaf7ef", FIELD),
        (370, "2 суматори 5+5 → 2 числа по 6 бітів", "#fdecea", POS),
        (300, "1 суматор 6+6 → 7 бітів: 0…64", "#fdecea", POS),
    ]

    y, rh, gap = 62, 44, 14
    for w, s, fill, stroke in rows:
        els.append(fitbox(W / 2.0 - w / 2.0, y, w, rh, s, size=13,
                          fill=fill, stroke=stroke))
        y += rh + gap

    els.append(mtext(W / 2.0, 460, [
        "Глибина — шість тонких рівнів вентилів, а не 63 додавання поспіль:",
        "увесь підрахунок укладається в одну команду завдовжки в один-два такти.",
    ], size=13, color=INK, lh=1.5))

    return render(os.path.join(OUT, 'hw-tree.svg'), W, H, *els,
                  title="Те саме дерево, тільки в кремнії")


def fig_rank_slot():
    """Ранг розряду в бітовій мапі — готовий індекс у щільному масиві."""
    W, H = 860, 420
    els = []

    present = [1, 4, 9, 11, 14]
    target = 9

    els.append(text(30, 58, "1. Бітова мапа: одиниця — елемент присутній; нас цікавить розряд 9.",
                    size=13, anchor="start"))
    for i in range(16):
        x = 30 + i * 50
        b = 1 if i in present else 0
        if i == target:
            fill, stroke, color = "#fdecea", POS, POS
        elif b:
            fill, stroke, color = "#eef3fb", NEG, NEG
        else:
            fill, stroke, color = "#ffffff", MUTED, MUTED
        els.append(cell(x, 70, 44, 36, str(b), size=15, fill=fill, stroke=stroke,
                        color=color, bold=bool(b)))
        els.append(text(x + 22, 126, str(i), size=11, color=MUTED))

    els.append(text(30, 162, "2. Обнуляємо все, що не нижче за розряд 9 — лишається маска молодших розрядів.",
                    size=13, anchor="start"))
    for i in range(16):
        x = 30 + i * 50
        b = 1 if (i in present and i < target) else 0
        if b:
            fill, stroke, color = "#eaf7ef", FIELD, FIELD
        else:
            fill, stroke, color = "#ffffff", MUTED, MUTED
        els.append(cell(x, 176, 44, 36, str(b), size=15, fill=fill, stroke=stroke,
                        color=color, bold=bool(b)))

    els.append(text(30, 246, "3. popcount = 2 — стільки присутніх елементів стоїть перед нашим.",
                    size=13, anchor="start", color=FIELD))
    els.append(text(30, 274, "4. Отже, елемент розряду 9 лежить у слоті 2 щільного масиву.",
                    size=13, anchor="start", color=POS))

    for i in range(5):
        x = 150 + i * 120
        hot = (i == 2)
        els.append(cell(x, 290, 104, 40, "розряд %d" % present[i], size=13,
                        fill="#fdecea" if hot else FILL,
                        stroke=POS if hot else LINE,
                        color=POS if hot else INK, bold=hot))
        els.append(text(x + 52, 348, "слот %d" % i, size=11, color=MUTED))

    els.append(text(W / 2.0, 388,
                    "Ранг розряду в мапі — готовий індекс у стисненому масиві, і коштує він одну команду.",
                    size=13))

    return render(os.path.join(OUT, 'rank-slot.svg'), W, H, *els,
                  title="Навіщо це: від бітової мапи до індексу в масиві")


SUP = "⁰¹²³⁴⁵⁶⁷"
SUB = "₀₁₂₃₄₅₆₇"


def fig_mul_diagonal():
    """Множення на 0x0101…01 як вісім зсунутих копій; стовпчик байта 7 збирає всі cᵢ."""
    W, H = 990, 505
    cw, x0, ytop, rh, dy = 56, 100, 98, 28, 34
    els = []

    def cx(s):
        return x0 + (14 - s) * cw

    # стовпчик s = 7 — той, що збирає всі вісім доданків
    els.append(rect(cx(7) - 2, ytop - 8, cw + 4, 8 * dy + 4,
                    fill="#eaf7ef", stroke=FIELD, sw=1.6, rx=5))

    # межа обрізання: байти з номерами 8 і вище зникають при mod 2⁶⁴
    xt = x0 + 7 * cw - 5
    els.append(line(xt, ytop - 26, xt, ytop + 8 * dy + 8, color=MUTED, sw=1.4, dash="5 4"))
    els.append(text(xt - 12, ytop - 32, "◀ ці байти відкидає обрізання до 64 бітів",
                    size=12, color=MUTED, anchor="end"))

    # номери байтів добутку
    for s in range(14, -1, -1):
        els.append(text(cx(s) + cw / 2.0, ytop - 14, str(s), size=11,
                        color=FIELD if s == 7 else MUTED, bold=(s == 7)))

    for j in range(8):
        y = ytop + j * dy
        els.append(text(x0 - 12, y + rh / 2.0 + 4, "x · 256%s" % SUP[j],
                        size=12, color=MUTED, anchor="end"))
        for i in range(8):
            s = i + j
            hot = (s == 7)
            els.append(cell(cx(s) + 3, y, cw - 6, rh, "c%s" % SUB[i], size=13,
                            fill="#eaf7ef" if hot else FILL,
                            stroke=FIELD if hot else LINE,
                            color=FIELD if hot else INK, bold=hot))

    yb = ytop + 8 * dy + 26
    els.append(text(W / 2.0, yb, "байт 7 добутку:  A₇ = c₀ + c₁ + … + c₇ = ν(x)",
                    size=16, color=FIELD, bold=True))
    els.append(mtext(W / 2.0, yb + 32, [
        "Кожна діагональна сума Aₛ — підсума тих самих восьми чисел c₀…c₇, тож Aₛ ≤ ν(x) ≤ 64 < 256.",
        "Жоден стовпчик не переповнює байт, переносу між байтами немає — і байт 7 виходить чистим.",
    ], size=13, lh=1.5))

    return render(os.path.join(OUT, 'mul-diagonal.svg'), W, H, *els,
                  title="Множення на 0x0101010101010101 — вісім зсунутих копій слова")


def fig_mask_after():
    """Відкладена маска прощає сміття в непарних полях, але не прощає переповнення в жодному."""
    W, H = 980, 566
    els = []

    # ── Панель А: вміст непарних полів нікого не обходить ───────────────────
    els.append(text(W / 2.0, 60,
                    "Вміст маска прощає: непарні поля вона однаково гасить",
                    size=15, bold=True, color=FIELD))

    cw, x0, ytop, ch = 148, 42, 76, 56
    for p in range(6):
        i = 5 - p
        keep = (i % 2 == 0)
        x = x0 + p * cw
        els.append(fitbox(x + 6, ytop, cw - 12, ch,
                          "s%s = d%s + d%s" % (SUB[i], SUB[i], SUB[i + 1]), size=14,
                          fill="#eaf7ef" if keep else "#ffffff",
                          stroke=FIELD if keep else MUTED,
                          color=FIELD if keep else MUTED, bold=keep))
        els.append(text(x + cw / 2.0, ytop + ch + 20,
                        "лишаємо" if keep else "у кошик",
                        size=12, color=FIELD if keep else MUTED))

    els.append(text(W / 2.0, ytop + ch + 44,
                    "у непарному полі сходяться поля з двох різних пар — число, якого ніхто не просив",
                    size=12, color=MUTED))

    # ── Панель Б: переповнення фатальне з обох боків ────────────────────────
    y2 = 216
    els.append(text(W / 2.0, y2,
                    "Переповнення не прощається: воно псує результат двома різними шляхами",
                    size=15, bold=True, color=POS))

    bw, bh, by = 132, 56, y2 + 34
    red = dict(fill="#fdecea", stroke=POS, color=POS, bold=True)
    grey = dict(fill="#ffffff", stroke=MUTED, color=MUTED)
    green = dict(fill="#eaf7ef", stroke=FIELD, color=FIELD, bold=True)

    def pair(cx, left_lbl, left_kw, right_lbl, right_kw):
        xl, xr = cx - bw - 6, cx + 6
        els.append(fitbox(xl, by, bw, bh, left_lbl, size=15, **left_kw))
        els.append(fitbox(xr, by, bw, bh, right_lbl, size=15, **right_kw))
        return xl, xr

    # ліворуч: переповнилось парне поле — зіпсоване те число, яке лишаємо
    cx1 = 250
    pair(cx1, "s₃", grey, "s₂ ≥ 2ᶠ", red)
    els.append(mtext(cx1, by + bh + 28, [
        "парне поле переповнилось —",
        "лишиться s₂ mod 2ᶠ, а не сума",
    ], size=13, color=POS, lh=1.5))

    # праворуч: переповнилось непарне — перенос падає в парне ліворуч
    cx2 = 730
    xl2, xr2 = pair(cx2, "s₄", green, "s₃ ≥ 2ᶠ", red)
    els.append(arrow(xr2 + 22, by - 16, xl2 + bw - 22, by - 16, color=POS, sw=2.0))
    els.append(text(cx2, by - 26, "перенос +1", size=12, color=POS, bold=True))
    els.append(mtext(cx2, by + bh + 28, [
        "непарне переповнилось —",
        "зайва одиниця йде в сусіда ліворуч",
    ], size=13, color=POS, lh=1.5))

    # ── Умова й вирок ───────────────────────────────────────────────────────
    els.append(fitbox(150, 382, 680, 54,
                      "жодне поле не сміє переповнитись:   dᵢ + dᵢ₊₁ ≤ 2ᶠ − 1   ⟸   2f ≤ 2ᶠ − 1",
                      size=16, fill=FILL, bold=True))

    conds = [("f = 1", "2 ≤ 1", False), ("f = 2", "4 ≤ 3", False),
             ("f = 4", "8 ≤ 15", True), ("f = 8", "16 ≤ 255", True)]
    for t, (a, b, okv) in enumerate(conds):
        x = 118 + t * 190
        els.append(fitbox(x, 454, 174, 54, "%s\n%s  %s" % (a, b, "✓" if okv else "✗"),
                          size=14, fill="#eaf7ef" if okv else "#fdecea",
                          stroke=FIELD if okv else POS,
                          color=FIELD if okv else POS, bold=True))

    els.append(text(W / 2.0, 540,
                    "У канонічному кроці ту саму суму 2f міряють проти цілого блоку 2^(2f) — там вона вміщається завжди.",
                    size=13))

    return render(os.path.join(OUT, 'mask-after.svg'), W, H, *els,
                  title="Що прощає відкладена маска, а що ні")


def fig_intersect_stream():
    """Потужність перетину: з проміжним масивом і без нього."""
    W, H = 880, 470
    els = []

    els.append(text(36, 62,
                    "Наївно: спершу побудувати перетин у пам'яті, потім перерахувати одиниці",
                    size=13, anchor="start", color=MUTED))

    y1 = 78
    els.append(fitbox(36, y1, 150, 46, "A: nw слів", size=14))
    els.append(text(202, y1 + 31, "&", size=20, bold=True))
    els.append(fitbox(218, y1, 150, 46, "B: nw слів", size=14))
    els.append(arrow(378, y1 + 23, 412, y1 + 23))
    els.append(fitbox(422, y1, 232, 46, "C = A & B: nw НОВИХ слів", size=13,
                      fill="#fdecea", stroke=POS, color=POS))
    els.append(arrow(664, y1 + 23, 698, y1 + 23))
    els.append(fitbox(708, y1, 136, 46, "count(C)", size=14))

    els.append(mtext(440, 158, [
        "Три масиви в пам'яті, два проходи, одне виділення —",
        "і проміжний результат, якого потім ніхто не читає.",
    ], size=13, color=INK, lh=1.5))

    els.append(line(36, 204, 844, 204, color=MUTED, sw=1.2, dash="5 5"))

    els.append(text(36, 238,
                    "Потоково: перетин живе одну мить у регістрі й одразу згортається в число",
                    size=13, anchor="start", color=MUTED))

    y2 = 254
    els.append(fitbox(36, y2, 150, 46, "A[i]", size=14, fill="#eef3fb", stroke=NEG))
    els.append(text(202, y2 + 31, "&", size=20, bold=True))
    els.append(fitbox(218, y2, 150, 46, "B[i]", size=14, fill="#eef3fb", stroke=NEG))
    els.append(arrow(378, y2 + 23, 412, y2 + 23))
    els.append(fitbox(422, y2, 232, 46, "регістр: одне слово", size=13,
                      fill="#eaf7ef", stroke=FIELD, color=FIELD))
    els.append(arrow(664, y2 + 23, 698, y2 + 23))
    els.append(fitbox(708, y2, 136, 46, "n += popcount", size=13))

    els.append(line(776, y2 + 46, 776, y2 + 80, color=MUTED, sw=1.4))
    els.append(line(776, y2 + 80, 111, y2 + 80, color=MUTED, sw=1.4))
    els.append(arrow(111, y2 + 80, 111, y2 + 48, color=MUTED, sw=1.4))
    els.append(text(440, y2 + 100, "наступне слово", size=12, color=MUTED))

    els.append(mtext(440, 414, [
        "Два масиви, один прохід, нуль виділень: два читання, AND і popcount на кожні 64 елементи.",
        "Виграє не швидший підрахунок, а те, що перетину не існує як окремого об'єкта.",
    ], size=13, color=INK, lh=1.5))

    return render(os.path.join(OUT, 'intersect-stream.svg'), W, H, *els,
                  title="Потужність перетину без проміжного масиву")


def fig_tail_word():
    """Хвіст останнього слова: розряди, яких у множині немає."""
    W, H = 880, 420
    els = []

    els.append(text(36, 60,
                    "Множина на 200 бітів займає 4 слова — а це 256 розрядів пам'яті.",
                    size=13, anchor="start", color=MUTED))

    x0, xw = 40, 780
    ybar, hbar = 92, 54
    cut = x0 + xw * 200.0 / 256.0

    els.append(fitbox(x0, ybar, cut - x0, hbar, "200 своїх розрядів", size=14,
                      fill="#eaf7ef", stroke=FIELD, color=FIELD))
    els.append(fitbox(cut, ybar, x0 + xw - cut, hbar, "56 чужих", size=13,
                      fill="#fdecea", stroke=POS, color=POS))

    for k in range(1, 4):
        xk = x0 + xw * k / 4.0
        els.append(line(xk, ybar, xk, ybar + hbar, color=MUTED, sw=1.2, dash="4 4"))
    for k in range(4):
        els.append(text(x0 + xw * (k + 0.5) / 4.0, ybar + hbar + 24,
                        "слово %d" % k, size=12, color=MUTED))

    els.append(text(x0, ybar - 12, "розряд 0", size=11, color=MUTED, anchor="start"))
    els.append(text(cut, ybar - 12, "199 | 200", size=11, color=MUTED))
    els.append(text(x0 + xw, ybar - 12, "255", size=11, color=MUTED, anchor="end"))

    els.append(fitbox(40, 206, 780, 44,
                      "flip() без маски: у хвості спалахують 56 одиниць — count() бреше на 56",
                      size=13, fill="#fdecea", stroke=POS, color=POS))
    els.append(fitbox(40, 264, 780, 44,
                      "w[W−1] &= tail_mask(): хвіст погашено, інваріант відновлено",
                      size=13, fill="#eaf7ef", stroke=FIELD, color=FIELD))

    els.append(mtext(W / 2.0, 348, [
        "AND і OR двох чистих множин лишають хвіст чистим самі собою — а заперечення ні.",
        "Тому маску хвоста накладають після кожної дії, що чіпає слово цілком.",
    ], size=13, color=INK, lh=1.5))

    return render(os.path.join(OUT, 'tail-word.svg'), W, H, *els,
                  title="Хвіст останнього слова: розряди, яких немає")


def fig_timeline():
    """Сімдесят років команди: рання поява, довга відсутність, повернення."""
    W, H = 990, 420
    els = []

    Y0, Y1 = 1948, 2026
    XL, XR = 60.0, 940.0

    def X(y):
        return XL + (y - Y0) * (XR - XL) / (Y1 - Y0)

    bar_y, bar_h = 206, 46

    segs = [
        (1948, 1964, "#f4f6f8", MUTED, "рання поява\nперші сліди в машинах"),
        (1964, 2007, "#fdecea", POS, "43 роки поза масовими наборами команд"),
        (2007, 2026, "#eaf7ef", FIELD, "POPCNT у кожному\nновому ядрі"),
    ]
    for a, b, fill, stroke, s in segs:
        els.append(fitbox(X(a), bar_y, X(b) - X(a), bar_h, s, size=13,
                          fill=fill, stroke=stroke, color=stroke))

    els.append(text(XL, bar_y - 6, "1948", size=11, color=MUTED, anchor="start"))
    els.append(text(XR, bar_y - 6, "2026", size=11, color=MUTED, anchor="end"))

    rows_up = {0: 44, 1: 120}
    above = [
        (1951, 0, "1951 · Ferranti Mark 1\n/R «боковий суматор»"),
        (1964, 1, "1964 · CDC 6600\nкод 47, блок ділення"),
        (1976, 0, "1976 · Cray-1\nкоманда 026, 4 такти"),
        (2004, 1, "2004 · IBM POWER5\npopcntb — по байтах"),
    ]
    for yr, r, s in above:
        x, top, bh, bw = X(yr), rows_up[r], 58, 180
        els.append(fitbox(x - bw / 2.0, top, bw, bh, s, size=13,
                          fill="#eef3fb", stroke=NEG, color=INK))
        els.append(line(x, top + bh, x, bar_y, color=NEG, sw=1.3))

    rows_dn = {0: 270, 1: 346}
    below = [
        (1994, 0, 190, "1994 · SPARC V9\nPOPC є, заліза немає"),
        (2007.5, 1, 210, "2007 AMD · 2008 Intel\nPOPCNT у масовому x86"),
        (2021, 0, 190, "2021 · RISC-V Zbb\nCPOP ратифіковано"),
    ]
    for yr, r, bw, s in below:
        x, top, bh = X(yr), rows_dn[r], 58
        hot = (r == 1)
        els.append(fitbox(x - bw / 2.0, top, bw, bh, s, size=13,
                          fill="#eaf7ef" if hot else FILL,
                          stroke=FIELD if hot else LINE, color=INK))
        els.append(line(x, bar_y + bar_h, x, top, color=FIELD if hot else MUTED, sw=1.3))

    return render(os.path.join(OUT, 'popcount-timeline.svg'), W, H, *els,
                  title="Команда підрахунку одиниць: поява, зникнення, повернення")


def fig_accumulators():
    """Один акумулятор зшиває підрахунки в ланцюг; чотири розривають його."""
    W, H = 880, 480
    els = []

    els.append(text(36, 56, "Один акумулятор: кожне додавання чекає на попереднє",
                    size=13, anchor="start", color=MUTED))

    y1, hb = 74, 46
    for k in range(4):
        x = 40 + k * 168
        els.append(fitbox(x, y1, 130, hb, "n += pc(w%d)" % k, size=13,
                          fill="#fdecea", stroke=POS, color=POS))
        els.append(arrow(x + 130, y1 + hb / 2.0, x + 164, y1 + hb / 2.0))
    els.append(text(786, y1 + hb / 2.0 + 6, "…", size=18, color=MUTED))

    els.append(mtext(440, 158, [
        "Кожна стрілка — справжня залежність за даними: наступне додавання",
        "не може початися, доки не готове попереднє значення n.",
    ], size=13, color=INK, lh=1.5))

    els.append(line(36, 210, 844, 210, color=MUTED, sw=1.2, dash="5 5"))

    els.append(text(36, 244, "Чотири акумулятори: чотири незалежні ланцюги",
                    size=13, anchor="start", color=MUTED))

    ly, lh = 260, 32
    for k in range(4):
        y = ly + k * 38
        els.append(fitbox(40, y, 168, lh, "n%d += pc(w[i+%d])" % (k, k), size=12,
                          fill="#eaf7ef", stroke=FIELD, color=FIELD))
        els.append(arrow(212, y + lh / 2.0, 244, y + lh / 2.0))
        els.append(fitbox(248, y, 178, lh, "n%d += pc(w[i+%d])" % (k, k + 4), size=12,
                          fill="#eaf7ef", stroke=FIELD, color=FIELD))
        els.append(text(446, y + lh / 2.0 + 5, "…", size=16, color=MUTED))

    els.append(line(500, ly, 500, ly + 3 * 38 + lh, color=MUTED, sw=1.2))
    els.append(mtext(676, ly + 50, [
        "Жоден ланцюг не чекає",
        "на сусідній — ядро веде",
        "всі чотири водночас.",
    ], size=13, color=INK, lh=1.5))

    els.append(fitbox(40, 420, 800, 40,
                      "Наприкінці — одне додавання на весь масив: n = n0 + n1 + n2 + n3",
                      size=13))

    return render(os.path.join(OUT, 'accumulators.svg'), W, H, *els,
                  title="Один акумулятор проти чотирьох")


if __name__ == '__main__':
    for f in (fig_weights, fig_swar, fig_hw_tree, fig_rank_slot,
              fig_mul_diagonal, fig_mask_after,
              fig_intersect_stream, fig_tail_word, fig_timeline,
              fig_accumulators):
        print(f())

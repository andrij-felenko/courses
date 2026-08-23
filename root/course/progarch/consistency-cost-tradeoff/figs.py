# -*- coding: utf-8 -*-
"""Фігури до кроку «Ціна консистентності як trade-off».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def polyline(pts, color, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)


def dot(cx, cy, r, color):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r, color)


def poly(pts, fill, stroke="none", sw=0.0):
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (s, fill, stroke, sw)


# Unicode-надрядкові для «10ⁿ» на осях логарифмічної фігури
_SUP = {'-': '⁻', '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}
def p10(n):
    return "10" + "".join(_SUP[c] for c in str(int(n)))


# ───────── Фіг. 1: один корінь (координація) → чотири обличчя рахунку ─────────
def fig_coordination_bill():
    W, H = 1000, 500
    f = [text(W / 2, 30, "Один корінь, чотири обличчя: усі ціни консистентності — з координації",
              size=16, bold=True)]

    # корінь у центрі-згори
    cbody, cw, ch = textbox(W / 2, 92,
                            ["КООРДИНАЦІЯ", "узгодження перед відповіддю",
                             "— єдиний корінь усіх цін —"],
                            size=14, bold=True, fill="#eef1f4", stroke=INK, sw=2.4)

    cols = [
        ("ЗАТРИМКА", NEG, "#eaf0fd",
         "раунд-тріпи мають\nфізичну підлогу —\nсигнал не швидший\nза світло.\n\nподаток на КОЖНІЙ\nоперації, навіть коли\nмережа справна.\n\nPACELC: гілка «Else»"),
        ("ДОСТУПНІСТЬ", POS, "#fdecea",
         "відрізаний вузол\nмусить відмовити,\nщоб не збрехати.\n\nмережевий збій\nстає простоєм.\n\nCAP: під розривом\nобирай C або A"),
        ("ПРОПУСКНА", FIELD, "#eafaf0",
         "єдиний глобальний\nпорядок серіалізує\nгарячий ключ:\nодин пише — інші\nчекають.\n\nзакон Амдала\nна гарячих даних"),
        ("ГРОШІ Й СКЛАДНІСТЬ", MUTED, "#eef1f4",
         "кворум — це більше\nвузлів; консенсус —\nнепарні 3–5 у синхроні;\nкрос-регіон-лінки\nплатні.\n\n+ важче тримати\nв голові"),
    ]
    n = len(cols)
    margin, gap = 26, 22
    bw = (W - 2 * margin - (n - 1) * gap) / n
    by, bh = 210, 250

    # стрілки з кореня до кожної колонки (малюємо ПЕРШ за рамки, під ними)
    for i, (head, col, fill, body) in enumerate(cols):
        x = margin + i * (bw + gap)
        f.append(arrow(W / 2, 92 + ch / 2, x + bw / 2, by - 6, color=col, sw=1.8))
    f.append(cbody)

    for i, (head, col, fill, body) in enumerate(cols):
        x = margin + i * (bw + gap)
        f.append(rect(x, by, bw, bh, fill=fill, stroke=col, sw=2.2, rx=10))
        f.append(text(x + bw / 2, by + 26, head, size=13, bold=True, color=col))
        f.append(line(x + 16, by + 38, x + bw - 16, by + 38, color="#dfe4e9", sw=1.2))
        f.append(fitbox(x + 12, by + 48, bw - 24, bh - 60, body,
                        size=12, fill="#ffffff", stroke="#eef1f4", color=INK))

    render(os.path.join(IMG, "coordination-bill.svg"), W, H, *f)


# ───────── Фіг. 2: сила гарантії × ціна координації — обрив на вершечку ─────────
def fig_price_curve():
    W, H = 940, 540
    f = [text(W / 2, 30, "Ціна вздовж спектра не лінійна: дешевий схил і обрив на вершечку",
              size=16, bold=True)]

    L, R, TOP, BOT = 120, 812, 108, 404
    stops = ["кінцева", "сесійні\n(RYW, монотонні)", "причинна", "лінеаризовність"]
    vals = [4, 9, 26, 94]        # ціна координації на операцію (умовні одиниці)
    VMAX = 100.0
    n = len(stops)

    def Xi(i): return L + i * (R - L) / (n - 1)
    def Y(v): return BOT - v / VMAX * (BOT - TOP)

    # зони: ліворуч дешева (зелена), праворуч дорога (червона)
    midx = (Xi(1) + Xi(2)) / 2
    f.append(rect(L, TOP, midx - L, BOT - TOP, fill="#f0faf3", stroke="none", sw=0, rx=0))
    f.append(rect(midx, TOP, R - midx, BOT - TOP, fill="#fdf0ee", stroke="none", sw=0, rx=0))
    f.append(text(L + 12, TOP + 18, "дешева зона — купуй звідси", size=11, color=FIELD, anchor="start"))
    f.append(text(R - 12, TOP + 18, "дорога зона", size=11, color=POS, anchor="end"))

    # осі
    f.append(arrow(L, BOT, R + 16, BOT, color=INK, sw=1.8))
    f.append(arrow(L, BOT, L, TOP - 12, color=INK, sw=1.8))
    f.append(text(L - 8, TOP - 18, "ціна координації на операцію", size=12, color=MUTED, anchor="start"))
    f.append(text(R + 12, BOT + 22, "сила гарантії →", size=12, color=MUTED, anchor="end"))

    # анотації у вільній смузі над полем (щоб не лягли на криву)
    xs1 = Xi(1)
    f.append(line(xs1, Y(vals[1]), xs1, 96, color=FIELD, sw=1.6, dash="5,5"))
    f.append(fitbox(xs1 - 104, 50, 216, 42,
                    "read-your-writes: головна аномалія\nгине майже задарма",
                    size=11, fill="#eafaf0", stroke=FIELD, color=INK, bold=True))
    f.append(fitbox(R - 224, 50, 224, 42,
                    "обрив ціни: повна координація\nна кожній операції",
                    size=11, fill="#fdecea", stroke=POS, color=INK, bold=True))
    f.append(line(R - 24, 92, Xi(3), Y(vals[3]) - 8, color=POS, sw=1.4, dash="4,4"))

    # крива
    pts = [(Xi(i), Y(vals[i])) for i in range(n)]
    f.append(polyline(pts, INK, sw=3.0))
    for i in range(n):
        col = FIELD if vals[i] < 20 else POS
        f.append(dot(Xi(i), Y(vals[i]), 5.2, col))
        f.append(fitbox(Xi(i) - 88, BOT + 12, 176, 34, stops[i],
                        size=12, fill="none", stroke="none", color=INK, bold=True))

    render(os.path.join(IMG, "price-curve.svg"), W, H, *f)


# ───────── Фіг. 3: 2×2 — шкода × обсяг → за що платити ─────────
def fig_item_price_map():
    W, H = 900, 560
    f = [text(W / 2, 32, "За що платити: шкода від хибної відповіді × обсяг операцій",
              size=16, bold=True)]

    gx, gy = 250, 108
    cw, ch = 288, 168
    gap = 16

    # заголовки стовпців — ОБСЯГ
    f.append(text(gx + cw / 2, gy - 30, "ОПЕРАЦІЙ МАЛО", size=13, bold=True, color=FIELD))
    f.append(text(gx + cw / 2, gy - 14, "(податок береться рідко)", size=10, color=MUTED))
    f.append(text(gx + cw + gap + cw / 2, gy - 30, "ОПЕРАЦІЙ БАГАТО", size=13, bold=True, color=POS))
    f.append(text(gx + cw + gap + cw / 2, gy - 14, "(податок береться щоразу)", size=10, color=MUTED))

    # заголовки рядків — ШКОДА
    f.append(text(118, gy + ch / 2 - 8, "ШКОДА", size=13, bold=True, color=POS))
    f.append(text(118, gy + ch / 2 + 8, "ВЕЛИКА", size=13, bold=True, color=POS))
    f.append(text(118, gy + ch / 2 + 26, "(безпека, гроші,", size=10, color=MUTED))
    f.append(text(118, gy + ch / 2 + 40, "довіра)", size=10, color=MUTED))
    f.append(text(118, gy + ch + gap + ch / 2 - 4, "ШКОДА", size=13, bold=True, color=FIELD))
    f.append(text(118, gy + ch + gap + ch / 2 + 12, "МАЛА", size=13, bold=True, color=FIELD))
    f.append(text(118, gy + ch + gap + ch / 2 + 30, "(само лікується)", size=10, color=MUTED))

    cells = [
        (0, 0, "КУПУЙ СТРОГЕ", FIELD,
         "замок дверей: рідко клацають,\n90 мс невидимі, шкода велика →\nподаток дрібний, гарантія варта"),
        (0, 1, "ЗМІНИ ГРУ", POS,
         "білінг, грошові підсумки: не можна\nні терпіти, ні платити скрізь →\nзвузь строге до критичного поля"),
        (1, 0, "БАЙДУЖЕ → КІНЦЕВА", MUTED,
         "рідкісний і безневинний стан →\nбери найпростіше, кінцева\nконсистентність цілком годиться"),
        (1, 1, "КІНЦЕВА", NEG,
         "телеметрія, presence «онлайн»:\nмільйони точок, шкода ≈ 0 →\nстроге тут руїна і дарма"),
    ]
    for row, col, head, accent, body in cells:
        x = gx + col * (cw + gap)
        y = gy + row * (ch + gap)
        f.append(rect(x, y, cw, ch, fill="#fbfcfd", stroke=accent, sw=2.2, rx=12))
        f.append(text(x + cw / 2, y + 28, head, size=14, bold=True, color=accent))
        f.append(line(x + 20, y + 40, x + cw - 20, y + 40, color="#dfe4e9", sw=1.2))
        f.append(fitbox(x + 16, y + 50, cw - 32, ch - 66, body,
                        size=12, fill="#ffffff", stroke="#eef1f4", color=INK))

    note = ("Той самий регулятор — вигідна покупка в одній клітинці й грабунок в іншій. "
            "Тому консистентність цінують поіменно, а не крутять один регулятор на всю систему.")
    f.append(fitbox(gx, gy + 2 * ch + gap + 18, 2 * cw + gap, 46, note,
                    size=12, fill="#fff8e8", stroke="#c9a93b", color=INK))

    render(os.path.join(IMG, "item-price-map.svg"), W, H, *f)


# ───────── Фіг. 4 (math): кворум чекає на k-й найближчий (порядкова статистика) ─────────
def fig_quorum_kth():
    W, H = 1044, 470
    f = [text(W / 2, 30, "Кворум чекає на k-й найближчий вузол: затримка = 2-й підтверджувач",
              size=16, bold=True)]

    x0, xms = 300, 3.4          # t=0 у x0; пікселів на мілісекунду
    def X(t): return x0 + t * xms
    axisY, tmax = 380, 185

    # заблокована зона [0, 90 мс]
    f.append(rect(X(0), 96, X(90) - X(0), axisY - 96, fill="#fdf0ee", stroke="none", sw=0, rx=0))
    f.append(text(X(45), 116, "операція заблокована — кворуму k=2 ще нема", size=11, color=POS))
    f.append(text(x0, 138, "усі 3 запити летять паралельно з t=0", size=11, color=MUTED, anchor="start"))

    # вісь часу
    f.append(arrow(x0, axisY, X(tmax) + 14, axisY, color=INK, sw=1.8))
    for t in (0, 50, 100, 150):
        f.append(line(X(t), axisY, X(t), axisY + 6, color=INK, sw=1.4))
        f.append(text(X(t), axisY + 22, "%d" % t, size=11, color=MUTED))
    f.append(text(X(tmax) + 8, axisY + 22, "мс", size=11, color=MUTED, anchor="start"))

    rows = [
        ("Франкфурт (локальна)",        1,   NEG,   "1-й: ~1 мс"),
        ("Вірджинія (2-й найближчий)",  90,  POS,   "2-й: ~90 мс — набрано k=2"),
        ("Сінгапур (3-й)",             170,  MUTED, "3-й: ~170 мс (не чекаємо)"),
    ]
    ry = [175, 235, 295]
    for (name, t, col, tag), y in zip(rows, ry):
        f.append(text(x0 - 14, y + 4, name, size=12, anchor="end", bold=True))
        f.append(line(x0, y, X(t), y, color=col, sw=2.6))
        f.append(dot(X(t), y, 6.0, col))
        f.append(text(X(t) + 12, y + 4, tag, size=11, color=col, anchor="start"))

    # гейт кворуму на 90 мс
    f.append(line(X(90), 150, X(90), axisY, color=POS, sw=2.0, dash="6,5"))
    f.append(fitbox(X(90) + 16, 150, 250, 54,
                    "кворум k=2 виконано\n→ відповідь на 90 мс\n(локальний 1 мс не врятував)",
                    size=11, fill="#fdecea", stroke=POS, color=INK, bold=True))

    render(os.path.join(IMG, "quorum-kth-node.svg"), W, H, *f)


# ───────── Фіг. 5 (math): лінія беззбитковості p·шкода = податок ─────────
def fig_breakeven():
    import math
    W, H = 900, 620
    f = [text(W / 2, 30, "Беззбитковість покупки строгого: p · шкода проти податку на операцію",
              size=15, bold=True)]

    L, R, TOP, BOT = 160, 830, 92, 500
    xmin, xmax = -7, 0          # log₁₀ P(аномалія)
    ymin, ymax = -4, 4          # log₁₀ шкода, €
    def X(lx): return L + (lx - xmin) / (xmax - xmin) * (R - L)
    def Y(ly): return BOT - (ly - ymin) / (ymax - ymin) * (BOT - TOP)

    TAU = 2e-4                  # податок на операцію, €  (умовний)
    lt = math.log10(TAU)       # ≈ -3.699
    # лінія p·H = τ  →  ly = lt - lx  ;  межі в межах рамки:
    xL, yL = xmin, lt - xmin           # (-7, 3.301)
    yB = ymin
    xB = lt - yB                       # де лінія сягає низу: lt - ly = lx → lx = lt - ymin
    #   (xL,yL) угорі-ліворуч → (xB,yB) унизу

    # зони: вище лінії — «купуй строге» (зелена), нижче — «кінцева» (червонувата)
    f.append(poly([(X(xL), Y(yL)), (X(xmax), Y(ymax)), (X(xmax), Y(ymin)),
                   (X(xB), Y(ymin)), (X(xL), Y(yL))], fill="#f0faf3"))
    f.append(poly([(X(xL), Y(yL)), (X(xB), Y(ymin)), (X(xL), Y(ymin))], fill="#fdf0ee"))

    # сітка
    for lx in range(xmin, xmax + 1):
        f.append(line(X(lx), TOP, X(lx), BOT, color="#e7ebef", sw=1.0))
        f.append(text(X(lx), BOT + 22, p10(lx), size=11, color=MUTED))
    for ly in range(ymin, ymax + 1):
        f.append(line(L, Y(ly), R, Y(ly), color="#e7ebef", sw=1.0))
        f.append(text(L - 12, Y(ly) + 4, p10(ly), size=11, color=MUTED, anchor="end"))

    # осі
    f.append(line(L, TOP, L, BOT, color=INK, sw=1.6))
    f.append(line(L, BOT, R, BOT, color=INK, sw=1.6))
    f.append(text((L + R) / 2, BOT + 44, "P(аномалія на операцію) →", size=12, color=INK))
    f.append(text(L - 40, TOP - 14, "шкода однієї аномалії, € ↑", size=12, color=INK, anchor="start"))

    # лінія беззбитковості
    f.append(line(X(xL), Y(yL), X(xB), Y(yB), color=INK, sw=3.0))
    f.append(fitbox(X(-6.5) - 4, Y(3.2) - 16, 232, 34,
                    "лінія беззбитковості  p·шкода = τ", size=11,
                    fill="#ffffff", stroke=INK, color=INK, bold=True))
    f.append(text(X(-1.3), Y(3.4), "ВИЩЕ → строге варте податку", size=12, color=FIELD, bold=True))
    f.append(text(X(-4.0), Y(-3.4), "НИЖЧЕ → лишай кінцеву", size=12, color=POS, bold=True))

    # точки DH
    def item(lx, ly, name, col):
        f.append(dot(X(lx), Y(ly), 6.5, col))
        return (lx, ly, name, col)
    # замок: p≈2.3·10⁻⁵, шкода≈500 €
    item(math.log10(2.3e-5), math.log10(500), "", POS)
    f.append(text(X(math.log10(2.3e-5)) + 12, Y(math.log10(500)) + 4,
                  "замок → строге", size=12, color=POS, anchor="start", bold=True))
    # грошові підсумки: p≈10⁻⁴, шкода≈5000 €
    item(-4, math.log10(5000), "", POS)
    f.append(text(X(-4) + 12, Y(math.log10(5000)) + 4,
                  "грошові підсумки → змінюй гру", size=11, color=POS, anchor="start", bold=True))
    # телеметрія: p≈0.1, шкода≈10⁻³ €
    item(-1, -3, "", FIELD)
    f.append(text(X(-1) - 12, Y(-3) - 12,
                  "телеметрія → кінцева", size=12, color=FIELD, anchor="end", bold=True))

    f.append(text(R, TOP - 14, "τ = 2·10⁻⁴ € / оп (умовно)", size=11, color=MUTED, anchor="end"))
    render(os.path.join(IMG, "breakeven-line.svg"), W, H, *f)


# ───────── Фіг. 6 (proj): вердикт моделі на одній осі «тиску до координації» ─────────
def fig_verdict_ladder():
    import math as _m
    W, H = 1220, 476
    LO, HI = -4.0, 2.0                     # десяткові порядки осі «тиску»
    L, R = 96, 1140
    AXY = 288                              # рівень осі

    def X(v):
        lg = max(LO, min(HI, _m.log10(v)))
        return L + (lg - LO) / (HI - LO) * (R - L)

    f = [text(W / 2, 30,
              "Вердикт моделі на одній осі: тиск = шкода/с ÷ повний податок/с",
              size=16, bold=True)]

    xs, xl = X(0.08), X(1.0)               # беззбитковості щаблів = їхні множники
    f.append(rect(L, 90, xs - L, AXY - 90, fill="#eef7f0", stroke="none", sw=0, rx=0))
    f.append(rect(xs, 90, xl - xs, AXY - 90, fill="#fff7e8", stroke="none", sw=0, rx=0))
    f.append(rect(xl, 90, R - xl, AXY - 90, fill="#fdeeec", stroke="none", sw=0, rx=0))
    f.append(text(L + 10, 104, "кінцева зона", size=11, color=FIELD, anchor="start"))
    f.append(text((xs + xl) / 2, 104, "щаблі дешевої координації", size=11, color="#b07d1a"))
    f.append(text(R - 10, 104, "повна строгість окупається", size=11, color=POS, anchor="end"))

    sup = {-4: "⁴", -3: "³", -2: "²",
           -1: "¹", 0: "", 1: "¹", 2: "²"}
    neg = {-4: "⁻⁴", -3: "⁻³", -2: "⁻²", -1: "⁻¹"}
    for e in range(int(LO), int(HI) + 1):
        x = X(10.0 ** e)
        f.append(line(x, AXY, x, AXY + 5, color=MUTED, sw=1.0))
        lab = "1" if e == 0 else ("10" + (neg[e] if e < 0 else sup[e]))
        f.append(text(x, AXY + 18, lab, size=10, color=MUTED))
    f.append(arrow(L - 10, AXY, R + 14, AXY, color=INK, sw=1.8))
    f.append(text(R + 12, AXY - 10, "тиск →", size=11, color=MUTED, anchor="end"))

    breaks = [("сесійна\nбеззбитк. 0.08", 0.08, FIELD, 64),
              ("причинна\n0.30", 0.30, MUTED, 64),
              ("лінеаризовність\nбеззбитк. 1.0", 1.0, POS, 64)]
    # напис зони «щаблі дешевої координації» сидить під самим верхом (до ~112) — лінії
    # старт trown нижче за нього; твін-виноска сидить у смузі [170..242] і перекриває
    # лінії причинної/лінеаризовності — для НИХ ведемо лінію ПОВЗ виноску (розрив на її висоті)
    TOPLINE = 112
    GAP_TOP, GAP_BOT = 170, 242
    for lab, v, col, ly in breaks:
        x = X(v)
        if v in (0.30, 1.0):
            f.append(line(x, TOPLINE, x, GAP_TOP, color=col, sw=1.6, dash="5,5"))
            f.append(line(x, GAP_BOT, x, AXY, color=col, sw=1.6, dash="5,5"))
        else:
            f.append(line(x, TOPLINE, x, AXY, color=col, sw=1.6, dash="5,5"))
        f.append(fitbox(x - 82, ly, 164, 34, lab, size=11, fill="#ffffff",
                        stroke=col, color=INK, bold=True))
        f.append(line(x, ly + 34, x, 90, color=col, sw=0.8, dash="2,3"))

    xt = X(0.47)
    f.append(fitbox(xt - 168, 176, 336, 60,
                    "твін: тиск 0.47 < 1 — повна строгість НЕ окупиться;\n"
                    "але 0.47 > 0.08 — сесійний щабель окупається.\n"
                    "бінарна «строго/кінцева» тут помилково терпить баг",
                    size=11, fill="#eef7f0", stroke=FIELD, color=INK, bold=True))
    f.append(line(xt, 236, xt, AXY - 7, color=FIELD, sw=1.0, dash="3,3"))

    items = [("телеметрія → кінцева", 0.00012, NEG, 0),
             ("presence → кінцева", 0.0035, NEG, 1),
             ("твін → сесійна", 0.47, FIELD, 0),
             ("білінг → строго, звузити зону", 16.0, POS, 1),
             ("замок → лінеаризовність", 47.0, POS, 0)]
    laneY = [AXY + 46, AXY + 100]
    for lab, v, col, lane in items:
        x = X(v)
        y = laneY[lane]
        f.append(dot(x, AXY, 6.4, col))
        f.append(line(x, AXY + 7, x, y - 2, color=col, sw=1.0, dash="2,3"))
        bx = max(L, min(x - 98, R - 196))
        f.append(fitbox(bx, y, 196, 36, lab, size=11, fill="#ffffff",
                        stroke=col, color=INK, bold=True))

    render(os.path.join(IMG, "verdict-ladder.svg"), W, H, *f)


if __name__ == "__main__":
    fig_coordination_bill()
    fig_price_curve()
    fig_item_price_map()
    fig_quorum_kth()
    fig_breakeven()
    fig_verdict_ladder()
    print("OK: coordination-bill, price-curve, item-price-map, quorum-kth-node, breakeven-line, verdict-ladder")

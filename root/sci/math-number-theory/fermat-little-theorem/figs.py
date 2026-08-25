# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
from math import cos, sin, radians, hypot, comb

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── permutation-prime: множення на a за простим модулем — це перестановка
# Ідея (осердя доведення): помножити кожну ненульову остачу 1…6 на 3 і звести
# за модулем 7 — дістати ту саму шістку в іншому порядку. Кожна вихідна клітинка
# має рівно один прообраз: жодна остача не зникла (нема нуля) і не збіглася з
# іншою. Саме тому добуток не змінюється, і 3⁶ можна скоротити до 1.
def fig_permutation_prime():
    W, H = 780, 560
    p = []
    a, mod = 3, 7
    CW, CH = 58, 38
    X_IN, X_OUT = 250, 530
    Y0, DY = 132, 62

    y = lambda i: Y0 + i * DY                       # рядок значення v сидить на v−1

    p.append(text((X_IN + X_OUT) / 2, 62,
                  "усі ненульові остачі, помножені на 3 (mod 7)", size=14, color=MUTED))
    p.append(text(X_IN, 100, "x", size=13.5, color=MUTED))
    p.append(text(X_OUT, 100, "3·x mod 7", size=13.5, color=MUTED))

    # ліва колонка — входи 1…6
    for i in range(mod - 1):
        v = i + 1
        p.append(rect(X_IN - CW / 2, y(i) - CH / 2, CW, CH, fill=FILL, stroke=LINE, sw=1.3))
        p.append(text(X_IN, y(i) + 5, v, size=15, bold=True))
    # права колонка — виходи 1…6 (усі досяжні → світло-зелені)
    for i in range(mod - 1):
        v = i + 1
        p.append(rect(X_OUT - CW / 2, y(i) - CH / 2, CW, CH, fill="#eafaf0", stroke=FIELD, sw=1.6))
        p.append(text(X_OUT, y(i) + 5, v, size=15, bold=True, color=FIELD))
    # стрілки — лише у смузі між колонками, жодного напису там немає
    for i in range(mod - 1):
        v = i + 1
        out = (a * v) % mod
        p.append(arrow(X_IN + CW / 2 + 4, y(i), X_OUT - CW / 2 - 5, y(out - 1),
                       color=FIELD, sw=1.4))

    b, _, _ = textbox((X_IN + X_OUT) / 2, 500,
                      ["кожна з шести остач має рівно один прообраз —",
                       "множення на 3 лише переставляє набір, нічого не додаючи й не гублячи"],
                      size=13, pad=12, fill="#fbfbfc")
    p.append(b)
    render(os.path.join(OUT, "permutation-prime.svg"), W, H,
           *p, title="Множення на 3 за модулем 7 переставляє остачі")


# ── prime-vs-composite: чому потрібне саме просте
# Ідея: піднести кожну ненульову остачу до степеня n−1. За простим модулем 7
# увесь стовпчик — суцільні одиниці. За складеним 15 навіть серед взаємно
# простих остач трапляються не-одиниці; кожна така остача доводить, що 15
# складене, не розкладаючи його. Це і зерно тесту Ферма, і межа теореми.
def fig_prime_vs_composite():
    W, H = 860, 544
    p = []
    RW, RH = 62, 32

    def panel(cx, head, sub, rows):
        q = []
        q.append(text(cx, 84, head, size=15, bold=True))
        q.append(text(cx, 108, sub, size=13, color=MUTED))
        q.append(text(cx - 96, 140, "a", size=12.5, color=MUTED))
        q.append(text(cx + 58, 140, "результат", size=12.5, color=MUTED))
        Y0, DY = 168, 40
        for i, (aval, res) in enumerate(rows):
            yy = Y0 + i * DY
            q.append(text(cx - 96, yy + 5, aval, size=14, bold=True))
            q.append(arrow(cx - 74, yy, cx + 58 - RW / 2 - 6, yy, color="#cfd4da", sw=1.3))
            one = (res == 1)
            q.append(rect(cx + 58 - RW / 2, yy - RH / 2, RW, RH,
                          fill="#eafaf0" if one else "#fdeeec",
                          stroke=FIELD if one else POS, sw=1.6))
            q.append(text(cx + 58, yy + 5, res, size=14, bold=True,
                          color=FIELD if one else POS))
        return q

    # просте 7: a⁶ mod 7 для a = 1…6 → усі 1
    p += panel(230, "модуль 7 — просте", "a⁶ mod 7",
               [(a, pow(a, 6, 7)) for a in range(1, 7)])
    # складене 15: a¹⁴ mod 15 для взаємно простих a → мішанка 1 і 4
    coprime15 = [1, 2, 4, 7, 8, 11, 13, 14]
    p += panel(610, "модуль 15 — складене", "a¹⁴ mod 15  (a взаємно просте з 15)",
               [(a, pow(a, 14, 15)) for a in coprime15])

    p.append(line(420, 96, 420, 476, color="#dde1e6", sw=1.2, dash="5,5"))
    p.append(text(W / 2, 512,
                  "просте → весь стовпчик 1;  складене → трапляється не-1, і кожна така остача викриває складеність",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(OUT, "prime-vs-composite.svg"), W, H,
           *p, title="Степінь n−1 за модулем: просте проти складеного")


# ── order-cycles: степені основи ходять замкненим циклом, довжина ділить p−1
# Ідея: кожна основа за модулем 7 котиться своїм колом остач і повертається до
# 1. Довжина кола — порядок основи: 3 обходить усі шість (порядок 6), 2 —
# утричі коротше (порядок 3), 6 = −1 — удвічі (порядок 2). Усі довжини 6, 3, 2 —
# дільники шістки, тому на кроці 6 кожна основа одночасно опиняється в одиниці.
def fig_order_cycles():
    W, H = 1000, 512
    p = []
    NR = 20                                          # радіус вузла
    CY = 224                                          # спільний центр рядка кіл
    LABEL_Y = 384                                     # підписи — під колами, поза стрілками

    def cycle(cx, r, orbit, label):
        q = []
        k = len(orbit)
        pos = []
        for i in range(k):
            ang = radians(-90 + i * 360.0 / k)       # індекс 0 — вгорі
            pos.append((cx + r * cos(ang), CY + r * sin(ang)))
        # стрілки вздовж циклу (сусідні вузли), зсунуті вбік — щоб для k=2
        # дві протилежні не лягли одна на одну
        for i in range(k):
            ax, ay = pos[i]
            bx, by = pos[(i + 1) % k]
            dx, dy = bx - ax, by - ay
            d = hypot(dx, dy)
            ux, uy = dx / d, dy / d
            ox, oy = uy * 6.0, -ux * 6.0             # перпендикулярний зсув
            q.append(arrow(ax + ux * NR + ox, ay + uy * NR + oy,
                           bx - ux * NR + ox, by - uy * NR + oy, color=MUTED, sw=1.5))
        # вузли
        for (x, y), v in zip(pos, orbit):
            one = (v == 1)
            q.append(circle(x, y, NR, fill="#eafaf0" if one else FILL,
                            stroke=FIELD if one else LINE, sw=2.2 if one else 1.5))
            q.append(text(x, y + 5, v, size=15, bold=True, color=FIELD if one else INK))
        q.append(mtext(cx, LABEL_Y, label, size=13, color=MUTED, lh=1.4, bold=True))
        return q

    p += cycle(200, 104, [3, 2, 6, 4, 5, 1], ["основа 3", "порядок 6   (6 ∣ 6)"])
    p += cycle(520, 88, [2, 4, 1], ["основа 2", "порядок 3   (3 ∣ 6)"])
    p += cycle(810, 70, [6, 1], ["основа 6 = −1", "порядок 2   (2 ∣ 6)"])

    p.append(text(W / 2, 476,
                  "довжина кожного циклу — порядок основи, і кожна ділить p−1 = 6; тому на кроці 6 усі основи разом у одиниці",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(OUT, "order-cycles.svg"), W, H,
           *p, title="Степені основ за модулем 7: цикли, що ділять 6")


# ── timeline-history: хронологія теореми й окрема нитка міфу
# Ідея (для історичної вставки): справжній розвиток теореми — темні вузли
# (1640 лист Ферма → рукопис Ляйбніца → друкована доводка Ейлера → назва
# Гензеля). Осторонь — червона нитка міфу: хибний критерій Лі Шаньланя, який
# Джинс 1897–98 приписав «часам Конфуція»; зелений вузол 1959 — Нідем спростовує.
# Дві барви розводять «що справді сталося» і «що вигадали навколо».
def fig_timeline_history():
    W, H = 940, 812
    p = []
    SPINE = 232
    rows = [
        ("1640",    "real",    ["Ферма формулює теорему в листі до Френікля де Бессі —",
                                 "без доведення («боюся, воно надто довге»)"]),
        ("~1683",   "real",    ["Ляйбніц доводить її по суті так само —",
                                 "у рукописі, що лишився неопублікованим"]),
        ("1736",    "real",    ["Ейлер друкує першу доводку",
                                 "в Петербурзькій академії наук"]),
        ("1850-ті", "neutral", ["Лі Шаньлань висуває свій (хибний) критерій;",
                                 "його підхоплює західна синологія"]),
        ("1897–98", "myth",    ["Джинс приписує критерій «часам Конфуція» —",
                                 "так постає міф про стародавній Китай"]),
        ("1913",    "real",    ["Гензель уводить у друк назву",
                                 "«мала теорема Ферма» (kleiner Fermatscher Satz)"]),
        ("1959",    "debunk",  ["Нідем викриває вигадку",
                                 "й повертає авторство XIX століттю"]),
    ]
    COL = {"real": INK, "neutral": MUTED, "myth": POS, "debunk": FIELD}
    Y0, DY = 128, 100
    y_of = lambda i: Y0 + i * DY

    # спинний хребет часу
    p.append(line(SPINE, y_of(0) - 34, SPINE, y_of(len(rows) - 1) + 34,
                  color="#d7dbe0", sw=2.4))

    for i, (year, kind, desc) in enumerate(rows):
        yy = y_of(i)
        col = COL[kind]
        # вузол на хребті
        p.append(circle(SPINE, yy, 10, fill=col, stroke=col, sw=2))
        if kind == "debunk":
            p.append(circle(SPINE, yy, 16, fill="none", stroke=col, sw=2))
        # рік — ліворуч від хребта, вирівняний по правому краю
        p.append(text(SPINE - 30, yy + 5, year, size=15, bold=True,
                      color=col, anchor="end"))
        # короткий з'єднувач до опису
        p.append(line(SPINE + 12, yy, SPINE + 34, yy, color="#c9ced4", sw=1.4))
        # опис — праворуч, у два рядки, вирівняний по лівому краю
        p.append(mtext(SPINE + 42, yy - 6, desc, size=13.5, color=INK,
                       anchor="start", lh=1.32))

    # легенда трьох ниток
    ly = y_of(len(rows) - 1) + 78
    leg = [("розвиток теореми", INK, False),
           ("міф про давнину", POS, False),
           ("спростування", FIELD, True)]
    lx = 150
    for label, col, ring in leg:
        p.append(circle(lx, ly, 8, fill=col, stroke=col, sw=2))
        if ring:
            p.append(circle(lx, ly, 13, fill="none", stroke=col, sw=1.6))
        p.append(text(lx + 20, ly + 5, label, size=13, color=MUTED, anchor="start"))
        lx += text_width(label, 13) + 92

    render(os.path.join(OUT, "timeline-history.svg"), W, H,
           *p, title="Життя теореми: справжня хронологія й пізніший міф")


# ── necklace-orbits: намистовий підрахунок (доведення Петерсена — Ґоломба)
# Ідея (для math-вставки): усіх разків із p=3 намистин у a=2 кольори — 2³=8.
# Два одноколірні оберт не змінює (орбіти завдовжки 1). Решта 8−2=6 розпадається
# на цикли-оберти рівно по 3 (бо 3 просте — коротшого періоду немає). Отже 3
# ділить 8−2. Чорна намистина ●, біла ○ — «два кольори».
def fig_necklace_orbits():
    W, H = 900, 470
    p = []
    R, GAP = 11, 30

    def bead_row(cx, y, pat):
        q = []
        x0 = cx - (len(pat) - 1) * GAP / 2
        for i, b in enumerate(pat):
            q.append(circle(x0 + i * GAP, y, R,
                            fill=INK if b else "#ffffff", stroke=INK, sw=1.7))
        return q

    # два одноколірні разки — нерухомі точки оберту
    p.append(text(450, 60,
                  "2 одноколірні разки — оберт лишає їх незмінними (кожен сам собі орбіта завдовжки 1)",
                  size=13.5, color=MUTED))
    p.append(rect(300, 78, 300, 52, fill="#fbfbfc", stroke="#e3e6ea", sw=1.2))
    p += bead_row(378, 104, [1, 1, 1])
    p += bead_row(522, 104, [0, 0, 0])

    def orbit(cx, header, strings):
        q = [text(cx, 168, header, size=13.5, color=INK, bold=True),
             rect(cx - 120, 184, 240, 182, fill=FILL, stroke="#e3e6ea", sw=1.2)]
        ys = [222, 282, 342]
        for y, pat in zip(ys, strings):
            q += bead_row(cx, y, pat)
        for ay, by in [(222, 282), (282, 342)]:
            q.append(arrow(cx, ay + R + 3, cx, by - R - 3, color=MUTED, sw=1.5))
            q.append(text(cx + 22, (ay + by) / 2 + 4, "оберт",
                          size=11, color=MUTED, anchor="start"))
        q.append(text(cx, 384, "оберт останнього повертає до першого: цикл довжини 3",
                      size=11, color=MUTED))
        return q

    p += orbit(255, "орбіта 1", [[1, 1, 0], [1, 0, 1], [0, 1, 1]])
    p += orbit(645, "орбіта 2", [[1, 0, 0], [0, 0, 1], [0, 1, 0]])
    p.append(text(450, 430,
                  "усього 2³ = 8 разків: 2 одноколірні + 2 цикли по 3;  отже 8 − 2 = 6 ділиться на p = 3",
                  size=13, color=INK, italic=True))
    render(os.path.join(OUT, "necklace-orbits.svg"), W, H,
           *p, title="Намистовий підрахунок для p = 3, a = 2 кольори")


# ── binomial-divisibility: чому середина рядка Паскаля зникає лише за простого
# Ідея (для math-вставки): у (a+1)ⁿ середні коефіцієнти C(n,k) множать мішані
# степені. За простого p усі вони кратні p → лишаються тільки крайні aᵖ та 1,
# тобто (a+1)ᵖ ≡ aᵖ+1. За складеного n=4 коефіцієнт 6 не кратний 4 — тотожність
# ламається, тож цей шлях доводить ЛИШЕ простий випадок.
def fig_binomial_divisibility():
    W, H = 860, 470
    p = []
    BX, BW, BH = 66, 50, 40

    def prow(cx, yrow, n, mod):
        q = []
        coeffs = [comb(n, k) for k in range(n + 1)]
        x0 = cx - (len(coeffs) - 1) * BX / 2
        for k, c in enumerate(coeffs):
            xc = x0 + k * BX
            end = (k == 0 or k == n)
            div = (c % mod == 0)
            if end:
                fill, stroke, col, note = "#f4f6f8", "#c9ced4", INK, "лишається"
            elif div:
                fill, stroke, col, note = "#eafaf0", FIELD, FIELD, "≡ 0"
            else:
                fill, stroke, col, note = "#fdeeec", POS, POS, "≠ 0"
            q.append(rect(xc - BW / 2, yrow - BH / 2, BW, BH, fill=fill, stroke=stroke, sw=1.7))
            q.append(text(xc, yrow + 5, c, size=15, bold=True, color=col))
            q.append(text(xc, yrow + BH / 2 + 16, note, size=10.5,
                          color=MUTED if end else col))
        return q

    p.append(text(430, 74, "просте  p = 5:  кожен середній  C(5,k)  кратний 5",
                  size=14, bold=True))
    p += prow(430, 130, 5, 5)
    p.append(text(430, 188, "(a+1)⁵  ≡  a⁵ + 1   (mod 5)",
                  size=14, color=FIELD, italic=True))

    p.append(line(80, 220, 780, 220, color="#e3e6ea", sw=1.2, dash="5,5"))

    p.append(text(430, 262, "складене  n = 4:  коефіцієнт 6 не кратний 4",
                  size=14, bold=True))
    p += prow(430, 318, 4, 4)
    p.append(text(430, 376, "(a+1)⁴  ≡  a⁴ + 2a² + 1   (mod 4)   ≠  a⁴ + 1",
                  size=14, color=POS, italic=True))

    p.append(text(430, 432,
                  "просте стирає всі середні коефіцієнти — складене вже ні; тому цей шлях доводить лише простий випадок",
                  size=12.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "binomial-divisibility.svg"), W, H,
           *p, title="Чому середина рядка Паскаля зникає лише за простого модуля")


# ── witness-liar: чому 341 ловиться, а 561 (число Кармайкла) — ні
# Ідея (для proj-вставки тесту Ферма): для кожної малої основи a класифікуємо
# результат aⁿ⁻¹ mod n. Зелене — свідок (≢1, складеність викрито конгруенцією);
# червоне — брехун (≡1, тест обманено); сіре — основа зі спільним дільником із n.
# Для псевдопростого 341 серед основ трапляються зелені свідки — тест його ловить.
# Для числа Кармайкла 561 ЖОДНОЇ зеленої: кожна взаємно проста основа бреше, і
# викрити 561 самою конгруенцією Ферма неможливо — звідси потреба в Міллері–Рабіні.
def fig_witness_liar():
    from math import gcd
    W = 900
    CW, CH, GAP = 52, 42, 6
    bases = list(range(2, 15))                        # основи 2 … 14
    n = len(bases)
    row_w = n * CW + (n - 1) * GAP
    x0 = (W - row_w) / 2

    STYLE = {
        "witness": ("#eafaf0", FIELD, "≢1"),          # свідок — складеність викрито
        "liar":    ("#fdeeec", POS,   "≡1"),          # брехун — тест обманено
        "factor":  ("#eef1f4", MUTED, "∣"),           # спільний дільник із n
    }

    def cat(mod, a):
        if gcd(a, mod) > 1:
            return "factor"
        return "liar" if pow(a, mod - 1, mod) == 1 else "witness"

    def panel(mod, label, base_y):
        q = [text(W / 2, base_y - 30, label, size=14, bold=True)]
        cell_y = base_y + 6
        for i, a in enumerate(bases):
            x = x0 + i * (CW + GAP)
            fill, stroke, sym = STYLE[cat(mod, a)]
            q.append(text(x + CW / 2, base_y, a, size=11.5, color=MUTED))
            q.append(rect(x, cell_y, CW, CH, fill=fill, stroke=stroke, sw=1.7))
            q.append(text(x + CW / 2, cell_y + CH / 2 + 5, sym, size=15,
                          bold=True, color=stroke))
        return q

    p = []
    p.append(text(W / 2, 50, "основа a  →  aⁿ⁻¹ mod n", size=12.5, color=MUTED))
    p += panel(341, "341 = 11·31   —   псевдопросте до основи 2", 104)
    p += panel(561, "561 = 3·11·17   —   число Кармайкла", 230)

    leg = [("свідок  aⁿ⁻¹ ≢ 1 — складеність викрито", "#eafaf0", FIELD),
           ("брехун  aⁿ⁻¹ ≡ 1 — тест обманено", "#fdeeec", POS),
           ("основа зі спільним дільником", "#eef1f4", MUTED)]
    widths = [22 + 8 + text_width(lab, 12) + 34 for lab, _, _ in leg]
    lx = (W - sum(widths)) / 2
    ly = 324
    for (lab, fill, stroke), wseg in zip(leg, widths):
        p.append(rect(lx, ly - 14, 22, 22, fill=fill, stroke=stroke, sw=1.7))
        p.append(text(lx + 30, ly + 2, lab, size=12, color=INK, anchor="start"))
        lx += wseg
    render(os.path.join(OUT, "witness-liar.svg"), W, 360,
           *p, title="Хто обманює тест Ферма: 341 ловиться, 561 (Кармайкла) — ні")


fig_permutation_prime()
fig_prime_vs_composite()
fig_order_cycles()
fig_timeline_history()
fig_necklace_orbits()
fig_binomial_divisibility()
fig_witness_liar()
print("ok:", sorted(os.listdir(OUT)))

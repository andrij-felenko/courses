# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_F  = "#e8eefc"
RED_F   = "#fdecea"
GREEN_F = "#e6f7ee"


def poly(pts, fill, stroke, sw=2.5):
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (s, fill, stroke, sw)


# ── whole-hyp: коли гіпотенуза виходить цілою ────────────────────────────────
# Ідея: √(a²+b²) майже завжди ірраціональна (1,1 → √2). Трійка Піфагора —
# рідкісний випадок, коли гіпотенуза теж лягає рівно на ціле число.
def fig_whole_hyp():
    W, H = 1000, 560
    p = []

    # ── ліворуч: 3-4-5, гіпотенуза ціла ──
    s = 46
    ax, ay = 140, 400                 # прямий кут — лівий нижній
    bx, by = ax + 4 * s, ay           # катет 4 праворуч
    cx, cy = ax, ay - 3 * s           # катет 3 угору
    p.append(poly([(ax, ay), (bx, by), (cx, cy)], BLUE_F, NEG))
    mk = 16
    p.append(rect(ax, ay - mk, mk, mk, fill=BG, stroke=NEG, sw=1.4, rx=0))
    p.append(text((ax + bx) / 2, ay + 28, "4", size=18, color=NEG, bold=True))
    p.append(text(ax - 24, (ay + cy) / 2 + 6, "3", size=18, color=NEG, bold=True))
    p.append(text((bx + cx) / 2 + 26, (by + cy) / 2 - 4, "5", size=20, color=POS, bold=True))

    p.append(fitbox(72, 452, 400, 60, "3² + 4²  =  9 + 16  =  25  =  5²",
                    size=18, fill=GREEN_F, stroke=FIELD, sw=2.4, bold=True, color=INK))
    p.append(text(272, 534, "гіпотенуза лягла рівно на ціле", size=13,
                  color=FIELD, italic=True, bold=True))

    # ── праворуч: 1-1-√2, гіпотенуза ірраціональна ──
    s2 = 92
    a2x, a2y = 690, 388
    b2x, b2y = a2x + s2, a2y
    c2x, c2y = a2x, a2y - s2
    p.append(poly([(a2x, a2y), (b2x, b2y), (c2x, c2y)], RED_F, POS))
    p.append(rect(a2x, a2y - mk, mk, mk, fill=BG, stroke=POS, sw=1.4, rx=0))
    p.append(text((a2x + b2x) / 2, a2y + 28, "1", size=18, color=POS, bold=True))
    p.append(text(a2x - 22, (a2y + c2y) / 2 + 6, "1", size=18, color=POS, bold=True))
    p.append(text((b2x + c2x) / 2 + 34, (b2y + c2y) / 2 - 4, "√2", size=18, color=POS, bold=True))

    p.append(fitbox(560, 452, 380, 60, "1² + 1²  =  2 ,   √2 ≈ 1.4142…",
                    size=18, fill=RED_F, stroke=POS, sw=2.4, bold=True, color=INK))
    p.append(text(750, 534, "гіпотенуза — нескінченний нецілий хвіст", size=13,
                  color=POS, italic=True))

    return render(os.path.join(OUT, "whole-hyp.svg"), W, H, *p,
                  title="Для яких цілих катетів гіпотенуза теж ціла?")


# ── parity: чому рівно один катет парний ─────────────────────────────────────
# Ідея: квадрат за модулем 4 буває лише 0 або 1. Тому «непарний + непарний»
# дає 2 — а такого квадрата не існує. Лишається «один парний, один непарний».
def fig_parity():
    W, H = 1100, 600
    p = []

    # ліва колонка — квадрати за модулем 4
    p.append(text(90, 96, "Квадрат за модулем 4", size=15.5, color=INK,
                  anchor="start", bold=True))
    x0, cw = 96, 52
    y_n, y_sq = 150, 208
    p.append(text(x0 - 30, y_n + 5, "n", size=13, color=MUTED, anchor="end", bold=True))
    p.append(text(x0 - 30, y_sq + 5, "n² mod 4", size=12, color=MUTED, anchor="end"))
    for i in range(8):
        n = i + 1
        q = (n * n) % 4
        odd = (n % 2 == 1)
        xc = x0 + i * cw + cw / 2
        p.append(rect(x0 + i * cw, y_n - 22, cw - 6, 34, fill=BG, stroke=MUTED, sw=1.3, rx=4))
        p.append(text(xc - 3, y_n + 2, str(n), size=15, color=INK, bold=True))
        fill, col = (RED_F, POS) if q == 1 else (BLUE_F, NEG)
        p.append(rect(x0 + i * cw, y_sq - 22, cw - 6, 34, fill=fill, stroke=col, sw=1.6, rx=4))
        p.append(text(xc - 3, y_sq + 2, str(q), size=15, color=col, bold=True))

    p.append(fitbox(84, 262, 430, 62,
                    "Квадрат ≡ 1 (непарне n)  або  ≡ 0 (парне n).\nНіколи не 2 і не 3.",
                    size=14, fill=FILL, stroke=NEG, sw=1.8))

    # права колонка — три випадки парності катетів
    p.append(text(600, 96, "Три випадки для катетів a, b", size=15.5, color=INK,
                  anchor="start", bold=True))
    cases = [
        ("обидва парні", "спільний множник 2 → трійка не примітивна", NEG, BLUE_F),
        ("обидва непарні", "a² + b² ≡ 1 + 1 = 2 (mod 4) — квадратом бути НЕ МОЖЕ", POS, RED_F),
        ("один парний, один непарний", "a² + b² ≡ 1 + 0 = 1 = c² — годиться, c непарне", FIELD, GREEN_F),
    ]
    y = 134
    for head, note, col, fill in cases:
        p.append(fitbox(600, y, 452, 40, head, size=15, fill=fill, stroke=col, sw=2, bold=True, color=INK))
        p.append(text(608, y + 62, note, size=12.5, color=INK, anchor="start"))
        y += 96

    p.append(fitbox(84, 512, 968, 56,
                    "У примітивній трійці рівно ОДИН катет парний, другий катет і гіпотенуза — непарні.",
                    size=15.5, fill=GREEN_F, stroke=FIELD, sw=2.4, bold=True, color=INK))

    return render(os.path.join(OUT, "parity.svg"), W, H, *p,
                  title="Парність: чому один катет мусить бути парним")


# ── machine: формула Евкліда як генератор трійок ─────────────────────────────
# Ідея: пара (m, n) з m > n перемелюється в цілу трійку. Взаємно прості m, n
# різної парності дають примітивну; інакше виходить кратна вже відомій.
def fig_machine():
    W, H = 1120, 630
    p = []

    # верх — сама машина
    p.append(fitbox(70, 92, 200, 78,
                    "вхід\nm > n > 0\nвзаємно прості\nрізної парності",
                    size=13, fill=BLUE_F, stroke=NEG, sw=2, bold=True, color=INK))
    p.append(arrow(276, 131, 356, 131, color=INK, sw=2))
    outs = ["a = m² − n²", "b = 2mn", "c = m² + n²"]
    yy = 100
    for o in outs:
        p.append(fitbox(362, yy, 210, 34, o, size=15, fill=GREEN_F, stroke=FIELD, sw=1.8, bold=True))
        yy += 44
    p.append(text(690, 118, "перевірка:  (m²−n²)² + (2mn)²  =  (m²+n²)²",
                  size=14, color=INK, anchor="start"))
    p.append(text(690, 148, "тотожність — розкрий дужки й порівняй",
                  size=12, color=MUTED, anchor="start", italic=True))

    # таблиця
    cols = [("(m, n)", 96), ("a", 250), ("b", 340), ("c", 430), ("a² + b² = c²", 540), ("тип", 850)]
    y0 = 268
    for h, x in cols:
        p.append(text(x, y0, h, size=13.5, color=MUTED, anchor="start", bold=True))
    p.append(line(80, y0 + 12, 1050, y0 + 12, color=MUTED, sw=1.3))

    rows = [
        ("(2, 1)", "3", "4", "5", "9 + 16 = 25", "примітивна", True),
        ("(3, 2)", "5", "12", "13", "25 + 144 = 169", "примітивна", True),
        ("(4, 1)", "15", "8", "17", "225 + 64 = 289", "примітивна", True),
        ("(4, 3)", "7", "24", "25", "49 + 576 = 625", "примітивна", True),
        ("(5, 2)", "21", "20", "29", "441 + 400 = 841", "примітивна", True),
        ("(3, 1)", "8", "6", "10", "64 + 36 = 100", "кратна (2, 1) — обидва непарні", False),
    ]
    y = y0 + 44
    for mn, a, b, c, chk, typ, prim in rows:
        col = INK if prim else MUTED
        if prim:
            p.append(rect(80, y - 22, 452, 34, fill=GREEN_F, stroke=FIELD, sw=1.2, rx=4))
        else:
            p.append(rect(80, y - 22, 452, 34, fill="#f3f4f6", stroke=MUTED, sw=1.2, rx=4))
        p.append(text(96, y, mn, size=14, color=col, anchor="start", bold=True))
        p.append(text(250, y, a, size=14, color=col, anchor="start"))
        p.append(text(340, y, b, size=14, color=col, anchor="start"))
        p.append(text(430, y, c, size=14, color=col, anchor="start"))
        p.append(text(540, y, chk, size=13.5, color=col, anchor="start"))
        tcol = FIELD if prim else POS
        p.append(text(850, y, typ, size=12.5, color=tcol, anchor="start", bold=prim))
        y += 44

    p.append(fitbox(80, y + 12, 970, 48,
                    "gcd(m, n) = 1  і  різна парність  ⟺  трійка примітивна.  Інакше — просто кратна вже відомій.",
                    size=14.5, fill=FILL, stroke=NEG, sw=2))

    return render(os.path.join(OUT, "machine.svg"), W, H, *p,
                  title="Формула Евкліда: з пари (m, n) — уся трійка")


# ── circle: трійки як раціональні точки на одиничному колі ───────────────────
# Ідея: поділивши на c², дістаємо (a/c)²+(b/c)²=1 — точку на колі. Пряма з
# раціональним нахилом із (−1,0) завжди влучає у другу раціональну точку.
def fig_circle():
    W, H = 1060, 620
    p = []

    cx, cy, R = 330, 350, 205

    def P(x, y):
        return cx + x * R, cy - y * R

    # осі
    p.append(line(cx - R - 34, cy, cx + R + 34, cy, color=MUTED, sw=1.3))
    p.append(line(cx, cy - R - 34, cx, cy + R + 34, color=MUTED, sw=1.3))
    p.append(circle(cx, cy, R, fill="#fbfcfe", stroke=NEG, sw=2))
    p.append(text(cx + R + 20, cy + 20, "x", size=13, color=MUTED, italic=True))
    p.append(text(cx - 16, cy - R - 18, "y", size=13, color=MUTED, italic=True))
    p.append(text(cx + 150, cy + 150, "x² + y² = 1", size=14, color=NEG, italic=True))

    # стартова точка (−1, 0)
    sx, sy = P(-1, 0)
    p.append(circle(sx, sy, 7, fill=RED_F, stroke=POS, sw=2.4))
    p.append(text(sx - 6, sy + 34, "(−1, 0)", size=13, color=POS, anchor="middle", bold=True))
    p.append(text(sx + 4, sy + 52, "старт", size=11.5, color=MUTED, anchor="middle", italic=True))

    # трійка-точка (3/5, 4/5)
    tx, ty = P(0.6, 0.8)
    p.append(line(sx, sy, tx + (tx - sx) * 0.08, ty + (ty - sy) * 0.08, color=FIELD, sw=2.2))
    p.append(circle(tx, ty, 7, fill=GREEN_F, stroke=FIELD, sw=2.6))
    p.append(text(tx + 70, ty - 6, "(3/5, 4/5)", size=13.5, color=FIELD, bold=True))
    p.append(text(tx + 70, ty + 14, "трійка (3, 4, 5)", size=11.5, color=MUTED, italic=True))

    # ще дві раціональні точки з винесеними підписами
    for (xx, yy, lab) in [(5/13, 12/13, "(5/13, 12/13)"), (8/17, 15/17, "(8/17, 15/17)")]:
        px, py = P(xx, yy)
        p.append(circle(px, py, 5.5, fill=GREEN_F, stroke=FIELD, sw=2))
    p.append(text(P(5/13, 12/13)[0] - 96, P(5/13, 12/13)[1] - 6, "(5/13, 12/13)", size=12, color=FIELD))
    p.append(text(P(8/17, 15/17)[0] - 30, P(8/17, 15/17)[1] - 20, "(8/17, 15/17)", size=12, color=FIELD))

    # нахил хорди
    mxx, myy = (sx + tx) / 2, (sy + ty) / 2
    p.append(text(mxx - 8, myy - 14, "нахил t = 1/2 = n/m", size=13, color=FIELD, anchor="middle", bold=True))

    # права колонка — пояснення
    xR = 690
    p.append(mtext(xR, 150,
                   ["Поділи a² + b² = c²  на  c²:",
                    "(a/c)² + (b/c)² = 1."],
                   size=15, color=INK, anchor="start", lh=1.5))
    p.append(mtext(xR, 236,
                   ["Кожна трійка — раціональна точка",
                    "на одиничному колі, і навпаки:",
                    "(3, 4, 5) ↔ (3/5, 4/5)."],
                   size=13.5, color=INK, anchor="start", lh=1.5))
    p.append(mtext(xR, 336,
                   ["Пряма з раціональним нахилом t = n/m",
                    "із точки (−1, 0) завжди влучає у ДРУГУ",
                    "раціональну точку кола — так з однієї",
                    "точки виводяться геть усі трійки."],
                   size=13.5, color=NEG, anchor="start", lh=1.55))
    p.append(fitbox(xR, 452, 320, 60,
                    "x = (m²−n²)/(m²+n²)\ny = 2mn/(m²+n²)",
                    size=14, fill=GREEN_F, stroke=FIELD, sw=2, bold=True))
    p.append(text(xR, 544, "повне виведення — у вставці про раціональні точки",
                  size=11.5, color=MUTED, anchor="start", italic=True))

    return render(os.path.join(OUT, "circle.svg"), W, H, *p,
                  title="Трійки Піфагора — раціональні точки на колі")


# ── timeline: трійки старші за ім'я «піфагорові» ─────────────────────────────
# Ідея: найдавніший запис трійок (Плімптон 322, ~1800 до н.е.) старший за
# Піфагора на ~1270 років, а перша атрибуція теореми йому (Прокл) — ще на ~980
# років пізніша за нього. Ім'я стоїть посередині, не на початку.
def fig_timeline():
    W, H = 1360, 500
    p = []
    spine_y = 290
    bw, bh = 250, 92

    nodes = [
        (150,  "up",   "~1800 до н. е.", "Плімптон 322 · Вавилон", "трійки, до 5-значних", False),
        (325,  "down", "~800 до н. е.",  "Сульба-сутри · Індія",   "теорема діагоналі",    False),
        (500,  "up",   "~530 до н. е.",  "Піфагор · Самос",        "ім'я — без свідчень",  True),
        (675,  "down", "~300 до н. е.",  "Евклід, «Начала» X",     "формула трійок",       False),
        (850,  "up",   "~100 до н. е.",  "Джоубі · Китай",         "правило ґуґу",         False),
        (1025, "down", "~250 н. е.",     "Діофант · Александрія",  "раціональні розв'язки", False),
        (1200, "up",   "~450 н. е.",     "Прокл",                  "перша атрибуція",      False),
    ]

    # вісь часу
    p.append(line(120, spine_y, 1250, spine_y, color=INK, sw=2.2))
    p.append(arrow(1250, spine_y, 1298, spine_y, color=INK, sw=2.2))
    p.append(text(1316, spine_y + 5, "час", size=12, color=MUTED, anchor="start", italic=True))

    for (x, side, l1, l2, l3, isname) in nodes:
        col = POS if isname else NEG
        fill = RED_F if isname else FILL
        p.append(circle(x, spine_y, 7, fill=fill, stroke=col, sw=2.6))
        if side == "up":
            by = 56
            p.append(line(x, by + bh, x, spine_y - 7, color=MUTED, sw=1.2, dash="4 3"))
        else:
            by = 350
            p.append(line(x, spine_y + 7, x, by, color=MUTED, sw=1.2, dash="4 3"))
        p.append(rect(x - bw / 2, by, bw, bh, fill=fill, stroke=col, sw=2, rx=7))
        p.append(text(x, by + 26, l1, size=13.5, color=col, bold=True))
        p.append(text(x, by + 50, l2, size=13, color=INK, bold=True))
        p.append(text(x, by + 72, l3, size=11.5, color=MUTED))

    # проміжок A: від таблички до імені
    ya = 200
    p.append(line(150, ya - 8, 150, ya + 8, color=FIELD, sw=1.6))
    p.append(line(500, ya - 8, 500, ya + 8, color=FIELD, sw=1.6))
    p.append(line(150, ya, 500, ya, color=FIELD, sw=1.6, dash="6 4"))
    p.append(text(325, ya - 11, "≈ 1270 років — тут табличка вже стара", size=12.5, color=FIELD, bold=True))

    # проміжок B: від імені до першої атрибуції
    yb = 244
    p.append(line(500, yb - 8, 500, yb + 8, color=POS, sw=1.6))
    p.append(line(1200, yb - 8, 1200, yb + 8, color=POS, sw=1.6))
    p.append(line(500, yb, 1200, yb, color=POS, sw=1.6, dash="6 4"))
    p.append(text(1012, yb - 11, "≈ 980 років — аж потім перша атрибуція", size=12.5, color=POS, bold=True))

    p.append(text(680, 472, "схематично — вузли рівновіддалені, не в масштабі часу",
                  size=12, color=MUTED, italic=True))

    return render(os.path.join(OUT, "timeline.svg"), W, H, *p,
                  title="Трійки Піфагора — на тисячу років старші за своє ім'я")


# ── project: раціональні точки кола ≅ раціональні числа (проєкція з N=(−1,0)) ─
# Ідея: промінь із N=(−1,0) через точку кола перетинає вісь y на висоті t —
# саме нахил хорди. Раціональна висота ↔ раціональна точка; пробіг t по всіх
# раціональних дає всі раціональні точки кола (коло ≅ пряма — рід нуль).
def fig_project():
    W, H = 1120, 560
    p = []
    cx, cy, R = 340, 350, 175

    def P(x, y):
        return cx + x * R, cy - y * R

    # осі: x — тонка сіра; y — «лінійка параметра t», виділена
    p.append(line(cx - R - 40, cy, cx + R + 60, cy, color=MUTED, sw=1.3))
    p.append(line(cx, 52, cx, cy + R + 30, color=INK, sw=2))
    p.append(text(cx + R + 48, cy + 18, "x", size=13, color=MUTED, italic=True))
    p.append(text(cx + 12, 66, "вісь параметра t", size=12.5, color=INK, anchor="start", bold=True))
    p.append(circle(cx, cy, R, fill="#fbfcfe", stroke=NEG, sw=2))
    p.append(text(*P(0.60, -0.66), "x² + y² = 1", size=13, color=NEG, italic=True))

    # точка проєкції N = (−1, 0)
    nx, ny = P(-1, 0)
    p.append(circle(nx, ny, 7, fill=RED_F, stroke=POS, sw=2.6))
    p.append(text(nx - 4, ny + 32, "N = (−1, 0)", size=12.5, color=POS, anchor="middle", bold=True))

    # точка t = 0 → (1, 0), бліда
    zx, zy = P(1, 0)
    p.append(circle(zx, zy, 4.5, fill=BG, stroke=MUTED, sw=1.8))
    p.append(text(zx + 6, zy + 20, "(1, 0)", size=11.5, color=MUTED, anchor="start"))

    # три промені: (t, точка кола, підпис, dx, dy, anchor, tlabel)
    rays = [
        (1/3, (0.8, 0.6),        "(4/5, 3/5)",     14,  5, "start", "t = 1/3"),
        (1/2, (0.6, 0.8),        "(3/5, 4/5)",     14, -8, "start", "t = 1/2"),
        (3/2, (-5/13, 12/13),    "(−5/13, 12/13)", -14, -8, "end",  "t = 3/2"),
    ]
    for t, (px, py), lab, dx, dy, anc, tlab in rays:
        qx, qy = P(px, py)
        mx, my = P(0, t)                       # позначка на осі y — висота t
        p.append(line(nx, ny, mx, my, color=FIELD, sw=1.8))
        p.append(line(mx - 6, my, mx + 6, my, color=INK, sw=2.4))
        p.append(text(mx - 12, my + 4, tlab, size=12, color=INK, anchor="end", bold=True))
        p.append(circle(qx, qy, 6, fill=GREEN_F, stroke=FIELD, sw=2.4))
        p.append(text(qx + dx, qy + dy, lab, size=12.5, color=FIELD, anchor=anc, bold=True))

    # права колонка — сенс картини
    xR = 662
    p.append(mtext(xR, 150,
                   ["Промінь із N крізь точку кола",
                    "перетинає вісь y на висоті t —",
                    "це і є нахил хорди."],
                   size=14, color=INK, anchor="start", lh=1.5))
    p.append(mtext(xR, 252,
                   ["Раціональна висота t",
                    "  ↔  раціональна точка кола.",
                    "Тому їх рівно стільки,",
                    "скільки раціональних чисел."],
                   size=14, color=INK, anchor="start", lh=1.5))
    p.append(fitbox(xR, 372, 372, 96,
                    "t = 0      ↔   (1, 0)\nt → ∞    ↔   N = (−1, 0)\nусі раціональні t\n  ↔   усі раціональні точки кола",
                    size=13, fill=FILL, stroke=NEG, sw=2, bold=True))

    return render(os.path.join(OUT, "project.svg"), W, H, *p,
                  title="Раціональні точки кола ≅ раціональні числа")


# ── degree: чому прийом хорди — привілей степеня 2 ───────────────────────────
# Ідея: пряма перетинає криву степеня d у d точках. На коніці (d=2) одна відома
# раціональна точка лишає лінійний залишок — друга змушена; на кубіці (d=3)
# лишаються дві (квадратний залишок) — раціональності задарма вже немає.
def fig_degree():
    W, H = 1160, 560
    p = []

    # ── ліва панель: коніка (коло), степінь 2 ──
    Lcx, Lcy, Ls = 290, 300, 115
    p.append(text(Lcx, 92, "Степінь 2 — коніка", size=16, color=NEG, bold=True))
    p.append(line(Lcx - 1.55 * Ls, Lcy, Lcx + 1.55 * Ls, Lcy, color=MUTED, sw=1.2))
    p.append(line(Lcx, Lcy - 1.5 * Ls, Lcx, Lcy + 1.5 * Ls, color=MUTED, sw=1.2))
    p.append(circle(Lcx, Lcy, Ls, fill="#fbfcfe", stroke=NEG, sw=2.4))
    # січна y = 0.35
    yl = 0.35
    xr = (1 - yl * yl) ** 0.5
    p.append(line(Lcx - 1.3 * Ls, Lcy - yl * Ls, Lcx + 1.3 * Ls, Lcy - yl * Ls, color=POS, sw=2.2))
    lxk, lyk = Lcx - xr * Ls, Lcy - yl * Ls          # ліва точка — відома
    rxk, ryk = Lcx + xr * Ls, Lcy - yl * Ls          # права — змушена
    p.append(circle(lxk, lyk, 7, fill=GREEN_F, stroke=FIELD, sw=2.6))
    p.append(circle(rxk, ryk, 7, fill=GREEN_F, stroke=FIELD, sw=2.6))
    p.append(text(lxk - 10, lyk - 14, "відома", size=12.5, color=FIELD, anchor="middle", bold=True))
    p.append(text(rxk + 6, ryk - 14, "змушена", size=12.5, color=FIELD, anchor="middle", bold=True))
    p.append(text(Lcx, Lcy + Ls + 40, "x² + y² = 1", size=12.5, color=MUTED, italic=True))
    p.append(text(Lcx, Lcy + Ls + 62, "1 відома → лінійний залишок → 2-га раціональна",
                  size=12.5, color=INK, anchor="middle"))

    # ── права панель: кубіка, степінь 3 ──
    Rcx, Rcy, Rsx, Rsy = 850, 300, 86, 52
    p.append(text(Rcx, 92, "Степінь 3 — кубіка", size=16, color=NEG, bold=True))
    p.append(line(Rcx - 2.3 * Rsx, Rcy, Rcx + 2.3 * Rsx, Rcy, color=MUTED, sw=1.2))
    p.append(line(Rcx, Rcy - 2.2 * Rsy, Rcx, Rcy + 2.2 * Rsy, color=MUTED, sw=1.2))

    def f(x):
        return x ** 3 - 3 * x

    xs = [-2.0 + i * (4.0 / 240) for i in range(241)]
    pts = " ".join("%.1f,%.1f" % (Rcx + x * Rsx, Rcy - f(x) * Rsy) for x in xs)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, NEG))

    ly = 0.7                                          # горизонтальна хорда
    p.append(line(Rcx - 2.0 * Rsx, Rcy - ly * Rsy, Rcx + 2.0 * Rsx, Rcy - ly * Rsy, color=POS, sw=2.2))

    # перетини хорди з кубікою — скан зі зміни знаку
    roots = []
    prev = f(xs[0]) - ly
    for i in range(1, len(xs)):
        cur = f(xs[i]) - ly
        if prev == 0:
            roots.append(xs[i - 1])
        elif prev * cur < 0:
            x0, x1 = xs[i - 1], xs[i]
            roots.append(x0 + (ly - f(x0)) * (x1 - x0) / (f(x1) - f(x0)))
        prev = cur
    roots.sort()
    for j, rx in enumerate(roots):
        X, Y = Rcx + rx * Rsx, Rcy - ly * Rsy
        if j == 0:
            p.append(circle(X, Y, 7, fill=GREEN_F, stroke=FIELD, sw=2.6))
            p.append(text(X, Y - 14, "відома", size=12.5, color=FIELD, anchor="middle", bold=True))
        else:
            p.append(circle(X, Y, 6.5, fill="#f3f4f6", stroke=MUTED, sw=2.2))
            p.append(text(X, Y - 13, "?", size=15, color=MUTED, anchor="middle", bold=True))
    p.append(text(Rcx + 1.7 * Rsx, Rcy + 1.5 * Rsy, "y = x³ − 3x", size=12.5, color=MUTED, italic=True))
    p.append(text(Rcx, Rcy + 2.2 * Rsy + 24, "1 відома → квадратний залишок → 2 не задарма",
                  size=12.5, color=INK, anchor="middle"))

    # нижня смуга — закон
    p.append(fitbox(120, 498, 920, 46,
                    "Пряма перетинає криву степеня d у d точках.  d = 2 → залишок лінійний, друга точка раціональна.  d ≥ 3 → залишок степеня ≥ 2, раціональності задарма немає.",
                    size=14, fill=FILL, stroke=NEG, sw=2, bold=True))

    return render(os.path.join(OUT, "degree.svg"), W, H, *p,
                  title="Чому прийом хорди — привілей степеня 2")


# ── tree: дерево Барнінґа–Голла ──────────────────────────────────────────────
# Ідея: корінь (3,4,5); три сталі матриці A,B,C дають кожному вузлу трьох дітей;
# рівень n має 3ⁿ трійок, кожна примітивна трійка стоїть у дереві рівно один раз.
def fig_tree():
    W, H = 1420, 610
    p = []

    rc = (710, 98)
    children = [(5, 12, 13), (21, 20, 29), (15, 8, 17)]
    cxs = [245, 710, 1175]
    cy = 286
    grand = [[(7, 24, 25), (55, 48, 73), (45, 28, 53)],
             [(39, 80, 89), (119, 120, 169), (77, 36, 85)],
             [(33, 56, 65), (65, 72, 97), (35, 12, 37)]]
    gcy = 486
    groups = [[105, 245, 385], [570, 710, 850], [1035, 1175, 1315]]

    # ребра корінь → діти
    for cx in cxs:
        p.append(line(rc[0], rc[1] + 22, cx, cy - 20, color=MUTED, sw=1.8))
    # ребра діти → онуки
    for gi, cx in enumerate(cxs):
        for gx in groups[gi]:
            p.append(line(cx, cy + 20, gx, gcy - 17, color=MUTED, sw=1.4))
    # мітки матриць A, B, C на верхніх ребрах
    for lab, x in (("A", 515), ("B", 710), ("C", 905)):
        p.append(circle(x, 181, 13, fill=BG, stroke=INK, sw=1.6))
        p.append(text(x, 186, lab, size=14, color=INK, bold=True))
    # онуки
    for gi in range(3):
        for j, gx in enumerate(groups[gi]):
            lbl = "(%d,%d,%d)" % grand[gi][j]
            p.append(fitbox(gx - 62, gcy - 17, 124, 34, lbl, size=12.5,
                            fill=GREEN_F, stroke=FIELD, sw=1.6, bold=True, color=INK))
    # діти
    for k, cx in enumerate(cxs):
        lbl = "(%d, %d, %d)" % children[k]
        p.append(fitbox(cx - 75, cy - 20, 150, 40, lbl, size=15,
                        fill=GREEN_F, stroke=FIELD, sw=2, bold=True, color=INK))
    # корінь
    p.append(fitbox(rc[0] - 80, rc[1] - 22, 160, 44, "(3, 4, 5)", size=17,
                    fill=BLUE_F, stroke=NEG, sw=2.4, bold=True, color=INK))
    # підпис
    p.append(fitbox(150, 544, 1120, 56,
                    "Корінь (3, 4, 5). Три сталі матриці A, B, C дають кожному вузлу трьох дітей.\n"
                    "Рівень n містить 3ⁿ трійок — і кожна примітивна трійка стоїть у дереві рівно один раз.",
                    size=14.5, fill=FILL, stroke=NEG, sw=2, color=INK))

    return render(os.path.join(OUT, "tree.svg"), W, H, *p,
                  title="Дерево Барнінґа–Голла: усі примітивні трійки з (3, 4, 5)")


for f in (fig_whole_hyp, fig_parity, fig_machine, fig_circle, fig_timeline, fig_project, fig_degree, fig_tree):
    print("написано:", f())

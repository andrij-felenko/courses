# -*- coding: utf-8 -*-
"""Фігури для статті «Кільця: додавання й множення в одній структурі».
Запуск із теки теми:  python figs.py  → SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#eafaf1"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eaf0fd"
GRAY_FILL  = "#eceff1"
ORANGE      = "#e67e22"
ORANGE_FILL = "#fdf1e5"
ORANGE_HEAD = "#f6cfa0"
GREEN_HEAD  = "#b7e6cd"


# ─────────────────────────────────────────────────────────────────────────
# Фігура 1 — будова кільця: два «крила» + балка дистрибутивності
# ─────────────────────────────────────────────────────────────────────────
def fig_anatomy():
    W, H = 860, 540
    p = []
    p.append(text(W/2, 30, "Кільце: два поверхи на спільній множині R", size=18, bold=True))

    colw = 350
    lx, rx = 40, W - 40 - colw            # ліва й права колонки
    top = 62
    hh = 58                                # висота заголовка
    rh = 42                                # висота рядка-закону
    gap = 12

    # ── ліве крило: додавання (абелева група) ──
    p.append(fitbox(lx, top, colw, hh, "ДОДАВАННЯ  (R, +)\nабелева група",
                    size=17, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=2))
    add_laws = ["замкненість:  a + b ∈ R",
                "асоціативність:  (a+b)+c = a+(b+c)",
                "нейтральний нуль:  a + 0 = a",
                "протилежний:  a + (−a) = 0",
                "комутативність:  a + b = b + a"]
    y = top + hh + gap
    for law in add_laws:
        p.append(fitbox(lx, y, colw, rh, law, size=14, fill=GREEN_FILL,
                        stroke=FIELD, sw=1.2))
        y += rh + gap
    left_bottom = y

    # ── праве крило: множення (моноїд) ──
    p.append(fitbox(rx, top, colw, hh, "МНОЖЕННЯ  (R, ·)\nмоноїд",
                    size=17, bold=True, fill=FILL, stroke=LINE, sw=2))
    mul_laws = ["замкненість:  a · b ∈ R",
                "асоціативність:  (a·b)·c = a·(b·c)",
                "одиниця:  a · 1 = 1 · a = a"]
    y = top + hh + gap
    for law in mul_laws:
        p.append(fitbox(rx, y, colw, rh, law, size=14, fill=FILL,
                        stroke=LINE, sw=1.2))
        y += rh + gap
    # підпис під правим крилом — чого НЕ вимагають
    p.append(text(rx + colw/2, y + 6, "ні комутативності, ні ділення — не вимагаємо",
                  size=12.5, color=MUTED, italic=True))

    # ── балка дистрибутивності знизу, через усю ширину ──
    beam_y = left_bottom + 24
    beam_h = 56
    p.append(rect(lx, beam_y, W - 2*lx, beam_h, fill="#fff6e6", stroke=POS, sw=2, rx=8))
    p.append(text(W/2, beam_y + 23, "НЕСУЧА БАЛКА — дистрибутивність", size=15,
                  bold=True, color=POS))
    p.append(text(W/2, beam_y + 44, "a·(b + c) = a·b + a·c        (b + c)·a = b·a + c·a",
                  size=14))
    # короткі «опори» від колонок до балки
    p.append(line(lx + colw/2, left_bottom, lx + colw/2, beam_y, color=MUTED, sw=1.4, dash="4 4"))
    p.append(line(rx + colw/2, top + hh + 3*(rh+gap), rx + colw/2, beam_y, color=MUTED, sw=1.4, dash="4 4"))

    render(os.path.join(IMG, "ring-anatomy.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 2 — дистрибутивність як площа: a·(b+c) = a·b + a·c
# ─────────────────────────────────────────────────────────────────────────
def fig_distributivity():
    W, H = 640, 430
    p = []
    p.append(text(W/2, 30, "Дистрибутивність = площа частин складається в площу цілого",
                  size=16, bold=True))

    a, b, c = 3, 4, 2
    cell = 42
    x0, y0 = 150, 96
    gw, gh = (b + c) * cell, a * cell
    xdiv = x0 + b * cell

    # клітинки: ліва частина (a·b) зелена, права (a·c) синя
    for i in range(a):
        for j in range(b + c):
            fill = GREEN_FILL if j < b else BLUE_FILL
            p.append(rect(x0 + j*cell, y0 + i*cell, cell, cell, fill=fill,
                          stroke="#c9d2da", sw=1, rx=0))
    # жирна вертикаль поділу
    p.append(line(xdiv, y0, xdiv, y0 + gh, color=INK, sw=2.4))
    # зовнішня рамка
    p.append(rect(x0, y0, gw, gh, fill="none", stroke=INK, sw=2, rx=0))

    # дужка «a» ліворуч
    p.append(line(x0 - 22, y0, x0 - 22, y0 + gh, color=INK, sw=1.6))
    p.append(line(x0 - 27, y0, x0 - 17, y0, color=INK, sw=1.6))
    p.append(line(x0 - 27, y0 + gh, x0 - 17, y0 + gh, color=INK, sw=1.6))
    p.append(text(x0 - 40, y0 + gh/2 + 5, "a", size=16, bold=True, anchor="middle"))

    # дужка «b + c» згори
    p.append(line(x0, y0 - 20, x0 + gw, y0 - 20, color=INK, sw=1.6))
    p.append(text(x0 + gw/2, y0 - 28, "b + c", size=15, bold=True))

    # підписи «b» та «c» знизу
    p.append(line(x0, y0 + gh + 18, xdiv, y0 + gh + 18, color=FIELD, sw=1.6))
    p.append(text((x0 + xdiv)/2, y0 + gh + 36, "b", size=15, bold=True, color=FIELD))
    p.append(line(xdiv, y0 + gh + 18, x0 + gw, y0 + gh + 18, color=NEG, sw=1.6))
    p.append(text((xdiv + x0 + gw)/2, y0 + gh + 36, "c", size=15, bold=True, color=NEG))

    # рівняння знизу
    eq_y = y0 + gh + 84
    p.append(text(W/2, eq_y, "a·(b + c)  =  a·b  +  a·c", size=18, bold=True))
    p.append(text(W/2, eq_y + 26, "площа цілого   =   зелена площа   +   синя площа",
                  size=13, color=MUTED, italic=True))

    render(os.path.join(IMG, "distributivity-area.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 3 — циферблат ℤ/12: одиниці vs дільники нуля
# ─────────────────────────────────────────────────────────────────────────
def fig_z12():
    W, H = 560, 660
    cx, cy, R = 280, 296, 200
    node = 28
    p = []
    p.append(text(W/2, 30, "Кільце ℤ/12: хто оборотний, а хто дільник нуля", size=17, bold=True))

    # тонке кільце-орбіта
    p.append(circle(cx, cy, R, fill="none", stroke="#d5dbe1", sw=1.4))

    pos = {}
    for k in range(12):
        ang = math.radians(-90 + k * 30)
        x = cx + R * math.cos(ang)
        y = cy + R * math.sin(ang)
        pos[k] = (x, y)

    # спершу — стрілки 3·4 → 0 (щоб вузли лягли поверх)
    x3, y3 = pos[3]
    x4, y4 = pos[4]
    x0, y0 = pos[0]
    p.append(text(cx, cy - 6, "3 · 4 = 12", size=17, bold=True, color=POS))
    p.append(text(cx, cy + 16, "≡ 0 (mod 12)", size=15, color=POS))
    p.append(arrow(x3 - 6, y3, cx + 60, cy - 2, color=POS, sw=1.8))
    p.append(arrow(x4, y4 - 4, cx + 40, cy + 24, color=POS, sw=1.8))
    p.append(arrow(cx, cy - 34, x0 + 2, y0 + node, color=POS, sw=1.8))

    for k in range(12):
        x, y = pos[k]
        if k == 0:
            fill, stroke = GRAY_FILL, MUTED
        elif math.gcd(k, 12) == 1:
            fill, stroke = GREEN_FILL, FIELD
        else:
            fill, stroke = RED_FILL, POS
        p.append(circle(x, y, node, fill=fill, stroke=stroke, sw=2.4))
        p.append(text(x, y + 6, str(k), size=18, bold=True))

    # легенда
    ly = 566
    p.append(rect(40, ly, 30, 22, fill=GREEN_FILL, stroke=FIELD, sw=2, rx=4))
    p.append(text(82, ly + 16, "оборотні (одиниці):  1, 5, 7, 11", size=13.5, anchor="start"))
    p.append(rect(40, ly + 34, 30, 22, fill=RED_FILL, stroke=POS, sw=2, rx=4))
    p.append(text(82, ly + 50, "дільники нуля:  2, 3, 4, 6, 8, 9, 10", size=13.5, anchor="start"))
    p.append(rect(360, ly, 30, 22, fill=GRAY_FILL, stroke=MUTED, sw=2, rx=4))
    p.append(text(402, ly + 16, "нуль", size=13.5, anchor="start"))

    render(os.path.join(IMG, "z12-wheel.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 4 — сходи структур: моноїд → … → поле
# ─────────────────────────────────────────────────────────────────────────
def fig_ladder():
    W, H = 940, 500
    p = []
    p.append(text(W/2, 30, "Сходинки: кожна додає одну вимогу", size=18, bold=True))

    steps = [
        ("Моноїд", "є одиниця", FILL, LINE),
        ("Група", "+ обернений", FILL, LINE),
        ("Абелева група", "+ комутативність", FILL, LINE),
        ("Кільце", "+ друга дія (×)\nз дистрибутивністю", "#fff6e6", POS),
        ("Область\nцілісності", "+ немає\nдільників нуля", GREEN_FILL, FIELD),
        ("Поле", "+ обернений\nза ×", GREEN_FILL, FIELD),
    ]
    bw, bh = 150, 66
    dx = 148
    x0 = 22
    base = 400          # нижній край найнижчого box
    rise = 56           # підняття на сходинку

    centers = []
    for i, (name, adds, fill, stroke) in enumerate(steps):
        x = x0 + i * dx
        ytop = base - i * rise - bh
        p.append(fitbox(x, ytop, bw, bh, name, size=15, bold=True, fill=fill,
                        stroke=stroke, sw=2))
        # підпис «що додає» — під box
        p.append(mtext(x + bw/2, ytop + bh + 16, adds, size=11.5, color=MUTED))
        centers.append((x, ytop, x + bw, ytop + bh/2))

    # стрілки між сходинками (від правого краю попередньої до лівого краю наступної)
    for i in range(len(steps) - 1):
        _, _, xr, ym = centers[i]
        xn, ytn, _, ymn = centers[i + 1]
        p.append(arrow(xr + 4, ym - 6, xn - 4, ymn + 10, color=INK, sw=1.8))

    # позначка «стрибок: додаємо цілу другу дію»
    xj = x0 + 3 * dx
    p.append(text(xj + bw/2, base + 58,
                  "друга дія — стрибок, а не сходинка", size=12.5,
                  color=POS, italic=True))

    render(os.path.join(IMG, "structure-ladder.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 5 — часова смуга народження поняття кільця (для вставки hist-)
# ─────────────────────────────────────────────────────────────────────────
def fig_timeline():
    W, H = 1060, 470
    p = []
    p.append(text(W/2, 32, "Народження поняття кільця: майже 80 років від біди до означення",
                  size=17, bold=True))

    axis_y = 232
    margin = 55
    n = 5
    usable = W - 2 * margin
    slot = usable / n
    centers = [margin + slot * (i + 0.5) for i in range(n)]

    # вісь часу + стрілка напряму
    p.append(line(margin - 10, axis_y, W - margin + 6, axis_y, color=MUTED, sw=2))
    p.append(arrow(W - margin + 6, axis_y, W - margin + 26, axis_y, color=MUTED, sw=2))
    p.append(text(W - margin + 34, axis_y + 5, "час", size=12, color=MUTED, anchor="start"))

    # кожен крок: (ім'я, роки, що додав, заливка, обвід, бік від осі)
    nodes = [
        ("КУММЕР", "≈1846", ["«ідеальні числа»:", "вигадані дільники —", "рятівна ідея"],
         GRAY_FILL, MUTED, "above"),
        ("ДЕДЕКІНД", "1871", ["ідеали як множини", "+ сам об'єкт", "(звав «порядок»)"],
         GREEN_FILL, FIELD, "below"),
        ("ГІЛЬБЕРТ", "1897", ["слово «Zahlring» —", "тільки назва"],
         "#fff6e6", POS, "above"),
        ("ФРЕНКЕЛЬ · СОНО", "1915 · 1917", ["перші аксіоми,", "та задорогі"],
         BLUE_FILL, NEG, "below"),
        ("НЕТЕР", "1921", ["аксіоми, які", "лишилися й досі"],
         GREEN_FILL, FIELD, "above"),
    ]

    boxW = 182
    stem = 30
    titleH = 24
    lineH = 16
    for (name, yr, lines, fill, stroke, side), cx in zip(nodes, centers):
        boxH = titleH + len(lines) * lineH + 12
        if side == "above":
            by = axis_y - stem - boxH
            p.append(text(cx, axis_y + 23, yr, size=13, bold=True, color=stroke))
            p.append(line(cx, axis_y - 6, cx, by + boxH, color=stroke, sw=1.4))
        else:
            by = axis_y + stem
            p.append(text(cx, axis_y - 13, yr, size=13, bold=True, color=stroke))
            p.append(line(cx, axis_y + 6, cx, by, color=stroke, sw=1.4))
        p.append(rect(cx - boxW / 2, by, boxW, boxH, fill=fill, stroke=stroke, sw=2, rx=7))
        p.append(text(cx, by + 18, name, size=13.5, bold=True))
        p.append(mtext(cx, by + titleH + 12, lines, size=11.5, color=INK, lh=1.32))
        # вузол на осі — поверх усього
        p.append(circle(cx, axis_y, 7, fill=stroke, stroke=BG, sw=2))

    p.append(text(W / 2, H - 18,
                  "Структуру вивчали понад 20 років безіменно — назва Гільберта прийшла аж посередині шляху.",
                  size=12.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "ring-birth-timeline.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 6 — реєстр «арифметики знаків»: місток vs група (для вставки math-)
# ─────────────────────────────────────────────────────────────────────────
def fig_signs_ledger():
    W, H = 980, 430
    p = []
    p.append(text(W/2, 30,
                  "Розподіл праці: де місток-дистрибутивність, а де група за додаванням",
                  size=17, bold=True))

    c1x, c1w = 24, 176
    c2x, c2w = 208, 384
    c3x, c3w = 600, 356
    top, hh, rh, gap = 52, 44, 68, 8

    # заголовки колонок
    p.append(fitbox(c1x, top, c1w, hh, "Наслідок",
                    size=15, bold=True, fill=GRAY_FILL, stroke=MUTED, sw=1.6))
    p.append(fitbox(c2x, top, c2w, hh, "Крок дистрибутивності (місток)",
                    size=15, bold=True, fill=ORANGE_HEAD, stroke=ORANGE, sw=1.6))
    p.append(fitbox(c3x, top, c3w, hh, "Крок групи за додаванням",
                    size=15, bold=True, fill=GREEN_HEAD, stroke=FIELD, sw=1.6))

    rows = [
        ("a·0 = 0",
         "0 = 0 + 0, розкрити дужки:\na·0 = a·0 + a·0",
         "скоротити зайве a·0\n(лема скорочення)"),
        ("(−a)·b = −(a·b)",
         "винести спільне ·b:\na·b + (−a)·b = 0·b = 0",
         "сума = 0 → це −(a·b)\n(єдиність протилежного)"),
        ("(−a)·(−b) = a·b",
         "знакова теорема двічі:\n−(a·(−b)) = −(−(a·b))",
         "−(−x) = x при x = a·b\n(єдиність протилежного)"),
        ("a·(b − c) = a·b − a·c",
         "b − c = b + (−c), далі\nліва дистрибутивність",
         "a·(−c) = −(a·c)\n(єдиність протилежного)"),
    ]
    y = top + hh + gap
    for f, dist, grp in rows:
        p.append(fitbox(c1x, y, c1w, rh, f, size=15, bold=True,
                        fill=BG, stroke=MUTED, sw=1.4))
        p.append(fitbox(c2x, y, c2w, rh, dist, size=14,
                        fill=ORANGE_FILL, stroke=ORANGE, sw=1.4))
        p.append(fitbox(c3x, y, c3w, rh, grp, size=14,
                        fill=GREEN_FILL, stroke=FIELD, sw=1.4))
        y += rh + gap

    render(os.path.join(IMG, "signs-ledger.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 7 — квадрат суми: чотири плитки, дві позадіагональні різні (math-)
# ─────────────────────────────────────────────────────────────────────────
def fig_square_tiles():
    W, H = 720, 490
    p = []
    p.append(text(W/2, 30, "Квадрат суми: чотири плитки, а не «a² + 2ab + b²»",
                  size=17, bold=True))

    La, Lb = 170, 115
    x0, y0 = 218, 72
    S = La + Lb
    xdiv, ydiv = x0 + La, y0 + La

    # плитки (a·a та b·b — діагональні, сірі; a·b — помаранчева, b·a — зелена)
    p.append(rect(x0, y0, La, La, fill=GRAY_FILL, stroke=MUTED, sw=1.6, rx=0))
    p.append(text(x0 + La/2, y0 + La/2 + 7, "a·a = a²", size=20, bold=True))

    p.append(rect(xdiv, y0, Lb, La, fill=ORANGE_FILL, stroke=ORANGE, sw=2.2, rx=0))
    p.append(text(xdiv + Lb/2, y0 + La/2 + 7, "a·b", size=19, bold=True, color=ORANGE))

    p.append(rect(x0, ydiv, La, Lb, fill=GREEN_FILL, stroke=FIELD, sw=2.2, rx=0))
    p.append(text(x0 + La/2, ydiv + Lb/2 + 7, "b·a", size=19, bold=True, color=FIELD))

    p.append(rect(xdiv, ydiv, Lb, Lb, fill=GRAY_FILL, stroke=MUTED, sw=1.6, rx=0))
    p.append(text(xdiv + Lb/2, ydiv + Lb/2 + 7, "b·b = b²", size=16, bold=True))

    # зовнішня рамка поверх плиток
    p.append(rect(x0, y0, S, S, fill="none", stroke=INK, sw=2.4, rx=0))

    # дужки сторін: згори a | b, ліворуч a | b
    p.append(line(x0, y0 - 16, xdiv, y0 - 16, color=INK, sw=1.6))
    p.append(text((x0 + xdiv)/2, y0 - 23, "a", size=16, bold=True))
    p.append(line(xdiv, y0 - 16, x0 + S, y0 - 16, color=INK, sw=1.6))
    p.append(text((xdiv + x0 + S)/2, y0 - 23, "b", size=16, bold=True))
    p.append(line(x0 - 16, y0, x0 - 16, ydiv, color=INK, sw=1.6))
    p.append(text(x0 - 30, (y0 + ydiv)/2 + 5, "a", size=16, bold=True))
    p.append(line(x0 - 16, ydiv, x0 - 16, y0 + S, color=INK, sw=1.6))
    p.append(text(x0 - 30, (ydiv + y0 + S)/2 + 5, "b", size=16, bold=True))

    # чесна формула під квадратом — позадіагональні доданки кольорові
    fy = y0 + S + 54
    toks = [("(a + b)²  =  a²  +  ", INK), ("a·b", ORANGE), ("  +  ", INK),
            ("b·a", FIELD), ("  +  b²", INK)]
    widths = [text_width(t, 20, bold=True) for t, _ in toks]
    x = W/2 - sum(widths)/2
    for (t, c), wd in zip(toks, widths):
        p.append(text(x, fy, t, size=20, bold=True, color=c, anchor="start"))
        x += wd
    p.append(text(W/2, fy + 32,
                  "зливаються в  2·a·b  лише коли  a·b = b·a  (комутативність множення)",
                  size=13.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "square-tiles.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 8 — таблиця множення ℤ/12 (для вставки proj-modular-ring)
# ─────────────────────────────────────────────────────────────────────────
def fig_z12_multable():
    n = 12
    cell = 38
    x0, y0 = 64, 100
    grid = (n + 1) * cell
    W = x0 + grid + 60
    H = y0 + grid + 140

    HGREEN = "#c9efd8"       # заголовок-одиниця
    HRED   = "#f8d2cb"       # заголовок-дільник нуля
    HGRAY  = "#e3e7ea"       # заголовок-нуль / кут
    CELL_STROKE = "#d5dbe1"

    p = []
    p.append(text(W/2, 34, "Таблиця множення ℤ/12: де народжуються нулі й одиниці",
                  size=17, bold=True))
    p.append(text(W/2, 58, "рядок — множник a, стовпець — множник b, у клітинці — залишок a·b (mod 12)",
                  size=12.5, color=MUTED, italic=True))

    def hfill(k):
        if k == 0:
            return HGRAY
        return HGREEN if math.gcd(k, n) == 1 else HRED

    # кут
    p.append(rect(x0, y0, cell, cell, fill=HGRAY, stroke="#c9d2da", sw=1.2, rx=0))
    p.append(text(x0 + cell/2, y0 + cell/2 + 7, "·", size=22, bold=True))

    # заголовки стовпців (b) і рядків (a)
    for k in range(n):
        cx = x0 + (k + 1) * cell
        p.append(rect(cx, y0, cell, cell, fill=hfill(k), stroke="#c9d2da", sw=1.2, rx=0))
        p.append(text(cx + cell/2, y0 + cell/2 + 6, str(k), size=15, bold=True))
        ry = y0 + (k + 1) * cell
        p.append(rect(x0, ry, cell, cell, fill=hfill(k), stroke="#c9d2da", sw=1.2, rx=0))
        p.append(text(x0 + cell/2, ry + cell/2 + 6, str(k), size=15, bold=True))

    # тіло таблиці
    for r in range(n):
        for c in range(n):
            prod = (r * c) % n
            cx = x0 + (c + 1) * cell
            cy = y0 + (r + 1) * cell
            if r >= 1 and c >= 1 and prod == 0:
                fill, tc, tb = RED_FILL, POS, True
            elif r >= 1 and c >= 1 and prod == 1:
                fill, tc, tb = GREEN_FILL, FIELD, True
            else:
                fill, tc, tb = BG, MUTED, False
            st, sw = CELL_STROKE, 1.0
            if (r, c) in ((3, 4), (4, 3)):       # наскрізний приклад статті
                st, sw = POS, 2.6
            p.append(rect(cx, cy, cell, cell, fill=fill, stroke=st, sw=sw, rx=0))
            p.append(text(cx + cell/2, cy + cell/2 + 6, str(prod), size=15,
                          color=tc, bold=tb))

    # легенда
    ly = y0 + grid + 20
    p.append(rect(x0, ly, 26, 20, fill=RED_FILL, stroke=POS, sw=1.8, rx=4))
    p.append(text(x0 + 36, ly + 15,
                  "дільники нуля: a·b = 0 при a ≠ 0, b ≠ 0 (обведено 3·4 = 4·3 = 0)",
                  size=12.5, anchor="start"))
    p.append(rect(x0, ly + 30, 26, 20, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=4))
    p.append(text(x0 + 36, ly + 45,
                  "взаємно обернені: a·b = 1 — обидва множники є одиницями",
                  size=12.5, anchor="start"))
    p.append(text(x0, ly + 72,
                  "Колір заголовка: зелений — одиниця (взаємно проста з 12: 1, 5, 7, 11),",
                  size=11.5, color=MUTED, italic=True, anchor="start"))
    p.append(text(x0, ly + 90,
                  "червоний — дільник нуля, сірий — нуль.",
                  size=11.5, color=MUTED, italic=True, anchor="start"))

    render(os.path.join(IMG, "z12-multable.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 9 — таблиці множення ℤ/7 (поле) vs ℤ/12 (не поле)  [вставка math-znz-structure]
# ─────────────────────────────────────────────────────────────────────────
def fig_znz_mult_tables():
    W, H = 780, 520
    p = []
    p.append(text(W/2, 30, "Таблиці множення: поле ℤ/7 проти не-поля ℤ/12", size=18, bold=True))
    HDR = BLUE_FILL
    top = 72

    def draw(px, py, n, cell, fs):
        f = []
        span = cell * (n + 1)
        # кутова клітина
        f.append(rect(px, py, cell, cell, fill=GRAY_FILL, stroke="#c9d2da", sw=1, rx=0))
        f.append(text(px + cell/2, py + cell/2 + fs*0.35, "·", size=fs + 2, bold=True, color=MUTED))
        # заголовкові рядок і стовпець
        for k in range(n):
            hx = px + cell + k*cell
            f.append(rect(hx, py, cell, cell, fill=HDR, stroke="#c9d2da", sw=1, rx=0))
            f.append(text(hx + cell/2, py + cell/2 + fs*0.35, str(k), size=fs, bold=True, color=NEG))
            hy = py + cell + k*cell
            f.append(rect(px, hy, cell, cell, fill=HDR, stroke="#c9d2da", sw=1, rx=0))
            f.append(text(px + cell/2, hy + cell/2 + fs*0.35, str(k), size=fs, bold=True, color=NEG))
        # тіло таблиці
        for i in range(n):
            for j in range(n):
                prod = (i * j) % n
                x = px + cell + j*cell
                y = py + cell + i*cell
                trivial = (i == 0 or j == 0)
                if trivial:
                    fill, stroke, col = GRAY_FILL, "#c9d2da", MUTED
                elif prod == 1:
                    fill, stroke, col = GREEN_FILL, FIELD, FIELD
                elif prod == 0:
                    fill, stroke, col = RED_FILL, POS, POS
                else:
                    fill, stroke, col = BG, "#c9d2da", INK
                sw = 1.6 if stroke in (FIELD, POS) else 1
                f.append(rect(x, y, cell, cell, fill=fill, stroke=stroke, sw=sw, rx=0))
                f.append(text(x + cell/2, y + cell/2 + fs*0.35, str(prod), size=fs, color=col,
                              bold=(not trivial and prod in (0, 1))))
        # зовнішня рамка + жирні відсічки після заголовків
        f.append(rect(px, py, span, span, fill="none", stroke=INK, sw=1.8, rx=0))
        f.append(line(px, py + cell, px + span, py + cell, color=INK, sw=1.8))
        f.append(line(px + cell, py, px + cell, py + span, color=INK, sw=1.8))
        return f, span

    fL, wL = draw(40, top, 7, 34, 15)
    p += fL
    p.append(text(40 + wL/2, top + wL + 26, "ℤ/7 — поле: у кожному рядку є зелена 1",
                  size=13.5, bold=True, color=FIELD))
    fR, wR = draw(372, top, 12, 28, 12)
    p += fR
    p.append(text(372 + wR/2, top + wR + 26, "ℤ/12 — не поле: у рядках дільників нуля 0 замість 1",
                  size=12.5, bold=True, color=POS))
    # легенда
    ly = H - 26
    p.append(rect(40, ly - 14, 26, 20, fill=GREEN_FILL, stroke=FIELD, sw=1.6, rx=3))
    p.append(text(74, ly + 1, "добуток = 1 (обернений знайдено)", size=12.5, anchor="start"))
    p.append(rect(360, ly - 14, 26, 20, fill=RED_FILL, stroke=POS, sw=1.6, rx=3))
    p.append(text(394, ly + 1, "добуток = 0, обидва множники ≠ 0 (дільник нуля)", size=12.5, anchor="start"))

    render(os.path.join(IMG, "znz-mult-tables.svg"), W, H, *p)


# ─────────────────────────────────────────────────────────────────────────
# Фігура 10 — смуги лишків: одиниць рівно φ(n)  [вставка math-znz-structure]
# ─────────────────────────────────────────────────────────────────────────
def fig_znz_phi_strip():
    W, H = 700, 352
    p = []
    p.append(text(W/2, 30, "Одиниць у ℤ/nℤ — рівно φ(n) (зелені клітини)", size=18, bold=True))
    cell, cellh, sx = 34, 40, 116
    y, pitch = 66, 80
    for n in (7, 9, 12):
        p.append(text(44, y + cellh/2 + 6, "ℤ/%d" % n, size=16, bold=True, anchor="start"))
        cnt = 0
        for k in range(n):
            x = sx + k*cell
            if k == 0:
                fill, stroke, col = GRAY_FILL, MUTED, MUTED
            elif math.gcd(k, n) == 1:
                fill, stroke, col = GREEN_FILL, FIELD, FIELD
                cnt += 1
            else:
                fill, stroke, col = RED_FILL, POS, POS
            p.append(rect(x, y, cell, cellh, fill=fill, stroke=stroke, sw=1.8, rx=4))
            p.append(text(x + cell/2, y + cellh/2 + 6, str(k), size=15, bold=True, color=col))
        rx = sx + n*cell + 18
        p.append(text(rx, y + cellh/2 + 6, "φ(%d) = %d" % (n, cnt), size=15, bold=True, anchor="start"))
        y += pitch
    # легенда
    ly = y + 4
    p.append(rect(116, ly, 24, 18, fill=GREEN_FILL, stroke=FIELD, sw=1.6, rx=3))
    p.append(text(148, ly + 14, "оборотний (одиниця)", size=12.5, anchor="start"))
    p.append(rect(320, ly, 24, 18, fill=RED_FILL, stroke=POS, sw=1.6, rx=3))
    p.append(text(352, ly + 14, "дільник нуля", size=12.5, anchor="start"))
    p.append(rect(470, ly, 24, 18, fill=GRAY_FILL, stroke=MUTED, sw=1.6, rx=3))
    p.append(text(502, ly + 14, "нуль", size=12.5, anchor="start"))

    render(os.path.join(IMG, "znz-phi-strip.svg"), W, H, *p)


if __name__ == "__main__":
    fig_anatomy()
    fig_distributivity()
    fig_z12()
    fig_ladder()
    fig_timeline()
    fig_signs_ledger()
    fig_square_tiles()
    fig_z12_multable()
    fig_znz_mult_tables()
    fig_znz_phi_strip()
    print("OK: figures written to", IMG)

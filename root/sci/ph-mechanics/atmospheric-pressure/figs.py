# -*- coding: utf-8 -*-
"""Фігури до теми «Атмосферний тиск».
Запуск із теки теми:  python figs.py   → SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AIR = "#e6f2fb"      # повітря
AIRD = "#a8cfe6"
DOT = "#5b9bd0"      # молекули повітря
MERC = "#b8bcc4"     # ртуть
MERCD = "#8b9099"
WATER = "#bfe0f2"    # вода
WATERD = "#7cc0e0"
ORANGE = "#e08e0b"
GREEN = FIELD


def frange(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def polyline(pts, color=INK, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


def polygon(pts, fill=AIR, stroke="none", sw=0):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" '
            'stroke-width="%.1f"/>' % (p, fill, stroke, sw))


def ground(x1, x2, y, color=INK, sw=2):
    out = [line(x1, y, x2, y, color=color, sw=sw)]
    n = 15
    for i in range(n):
        xx = x1 + (x2 - x1) * i / (n - 1)
        out.append(line(xx, y, xx - 10, y + 11, color=color, sw=1.1))
    return "".join(out)


# ── Фігура 1: океан повітря — стовп має вагу, тиск діє на всі боки ────────────
def fig_air_column():
    W, H = 960, 600
    F = []

    # ── ліва частина: стовп повітря над 1 м² ──
    colx0, colx1 = 150, 250
    ctop, gy = 78, 452
    F.append(rect(colx0, ctop, colx1 - colx0, gy - ctop, fill=AIR, stroke=AIRD, sw=1.4, rx=3))

    # молекули: густо внизу, рідко вгорі (детерміновано) — самі показують «рідшає вгору»
    rows = 27
    for i in range(rows):
        frac = i / (rows - 1)
        yy = gy - 9 - (gy - ctop - 18) * frac
        ndot = max(1, int(round(6 * (1 - frac) ** 1.25)))
        for j in range(ndot):
            xx = colx0 + 13 + (colx1 - colx0 - 26) * ((j + 0.5) / ndot)
            xx += 5.5 * math.sin(i * 1.7 + j * 2.3)
            F.append(circle(xx, yy, 2.2, fill=DOT, stroke="none", sw=0))

    F.append(text((colx0 + colx1) / 2, ctop - 10, "верх атмосфери (умовно)", size=11.5, color=MUTED))
    F.append(text((colx0 + colx1) / 2, gy - 16, "рівень моря", size=11, color=MUTED))

    F.append(ground(colx0 - 40, colx1 + 40, gy))

    # позначка площі 1 м²
    F.append(line(colx0, gy + 20, colx1, gy + 20, color=INK, sw=1.4))
    F.append(line(colx0, gy + 15, colx0, gy + 25, color=INK, sw=1.4))
    F.append(line(colx1, gy + 15, colx1, gy + 25, color=INK, sw=1.4))
    F.append(text((colx0 + colx1) / 2, gy + 38, "1 м²", size=12.5, color=INK, bold=True))

    # стрілка ваги стовпа + пояснення праворуч (усе чисто праворуч від стовпа)
    ax = 300
    F.append(arrow(ax, 150, ax, gy - 22, color=INK, sw=2.8))
    F.append(fitbox(ax + 24, 198, 228, 96,
                    "вага стовпа повітря\nнад кожним 1 м²  ≈  10.3 т\n"
                    "→  тисне  P₀ ≈ 101 кПа\nбіля рівня моря",
                    size=13, bold=True, fill="#eef4fb", stroke=NEG, pad=10))

    # роздільник
    F.append(line(590, 70, 590, 470, color="#dfe4ea", sw=1.4, dash="4 6"))

    # ── права частина: ізотропія тиску ──
    ox, oy = 772, 262
    R_out, R_in = 78, 34
    F.append(text(ox, 120, "у газі тиск діє на ВСІ боки", size=14, bold=True))
    F.append(text(ox, 140, "однаково", size=14, bold=True))
    # тіло
    F.append(rect(ox - 26, oy - 26, 52, 52, fill="#f4f6f8", stroke=INK, sw=1.6, rx=6))
    # стрілки всередину з 8 напрямків
    for k in range(8):
        a = k * math.pi / 4
        dx, dy = math.cos(a), math.sin(a)
        F.append(arrow(ox + R_out * dx, oy + R_out * dy,
                       ox + R_in * dx, oy + R_in * dy, color=POS, sw=2.4))
    F.append(text(ox, oy + 5, "P", size=14, color=POS, bold=True, italic=True))

    F.append(fitbox(ox - 152, 378, 304, 70,
                    "нас не роздавлює тому,\nщо тиск усередині тіла\n"
                    "врівноважує зовнішній",
                    size=12.5, bold=True, fill="#fdecea", stroke=POS, pad=9))

    # ── нижній підсумок ──
    F.append(fitbox(80, 512, 800, 58,
                    "Повітря — речовина, отже має вагу. Стовп повітря над кожним квадратним метром важить ≈ 10 т\n"
                    "і тисне ≈ 101 кПа — однаково згори, знизу й збоку.",
                    size=13.5, bold=True, fill="#eafaf0", stroke=GREEN, pad=10))

    render(os.path.join(IMG, "air-column.svg"), W, H, *F,
           title="Ми живемо на дні океану повітря")


# ── Фігура 2: барометр Торрічеллі — ртуть 760 мм або вода 10.3 м ──────────────
def fig_barometer():
    W, H = 920, 600
    F = []

    # спільний рівень поверхні рідини в чашах
    dish_y = 452
    # висотна шкала: 760 мм ртуті → 300 px
    PX_PER_MM = 300.0 / 760.0

    # ── ліворуч: ртутний барометр (реалістичний) ──
    mcx = 250
    tw = 44                       # ширина трубки
    merc_top = dish_y - 300       # верх стовпа ртуті (760 мм)
    tube_top = merc_top - 44      # закритий верх трубки
    # чаша
    F.append(rect(mcx - 118, dish_y, 236, 34, fill=MERC, stroke=MERCD, sw=1.5, rx=4))
    F.append(rect(mcx - 124, dish_y + 30, 248, 12, fill="#e5e7eb", stroke=MERCD, sw=1.4, rx=3))
    # трубка (стінки)
    F.append(rect(mcx - tw / 2, tube_top, tw, dish_y - tube_top, fill="#ffffff", stroke=INK, sw=1.6, rx=3))
    # стовп ртуті
    F.append(rect(mcx - tw / 2 + 2, merc_top, tw - 4, dish_y - merc_top + 20, fill=MERC, stroke="none", sw=0))
    # вакуум зверху
    F.append(text(mcx, tube_top + 22, "порожнеча", size=11.5, color=MUTED))
    F.append(text(mcx, tube_top + 38, "(вакуум)", size=11.5, color=MUTED))
    # висотний розмір 760 мм
    hx = mcx - tw / 2 - 30
    F.append(arrow(hx, merc_top, hx, dish_y, color=INK, sw=1.7))
    F.append(arrow(hx, dish_y, hx, merc_top, color=INK, sw=1.7))
    F.append(line(hx, merc_top, mcx - tw / 2, merc_top, color="#c9ced4", sw=1.1, dash="4 4"))
    F.append(line(hx, dish_y, mcx - tw / 2, dish_y, color="#c9ced4", sw=1.1, dash="4 4"))
    F.append(text(hx - 8, (merc_top + dish_y) / 2 - 6, "760 мм", size=13.5, color=INK, bold=True, anchor="end"))
    F.append(text(hx - 8, (merc_top + dish_y) / 2 + 12, "рт. ст.", size=12, color=INK, anchor="end"))
    F.append(text(mcx, dish_y + 60, "ртуть", size=12.5, color=MERCD, bold=True))

    # атмосфера тисне на поверхню чаші
    for dx in (-92, -64, 64, 92):
        F.append(arrow(mcx + dx, dish_y - 34, mcx + dx, dish_y - 6, color=POS, sw=2.2))
    F.append(text(mcx, dish_y - 46, "атмосфера тисне", size=11.5, color=POS, bold=True))

    # ── праворуч: водяний стовп (обірваний — надто високий) ──
    wcx = 660
    wtw = 40
    brk = 150                     # рівень «обриву» трубки
    # чаша з водою
    F.append(rect(wcx - 96, dish_y, 192, 34, fill=WATER, stroke=WATERD, sw=1.5, rx=4))
    F.append(rect(wcx - 102, dish_y + 30, 204, 12, fill="#e5e7eb", stroke=WATERD, sw=1.4, rx=3))
    # трубка від чаші до обриву
    F.append(rect(wcx - wtw / 2, brk + 26, wtw, dish_y - (brk + 26), fill="#ffffff", stroke=INK, sw=1.6, rx=3))
    F.append(rect(wcx - wtw / 2 + 2, brk + 28, wtw - 4, dish_y - (brk + 28) + 20, fill=WATER, stroke="none", sw=0))
    # верхній куций відрізок трубки (над обривом) із закритим верхом
    F.append(rect(wcx - wtw / 2, brk - 46, wtw, 30, fill="#ffffff", stroke=INK, sw=1.6, rx=3))
    F.append(rect(wcx - wtw / 2 + 2, brk - 16, wtw - 4, 14, fill=WATER, stroke="none", sw=0))
    # символ обриву (зигзаг)
    F.append(polyline([(wcx - wtw / 2 - 8, brk + 26), (wcx - 6, brk + 14),
                       (wcx + 6, brk + 30), (wcx + wtw / 2 + 8, brk + 18)], color=INK, sw=2.0))
    F.append(polyline([(wcx - wtw / 2 - 8, brk - 16), (wcx - 6, brk - 28),
                       (wcx + 6, brk - 12), (wcx + wtw / 2 + 8, brk - 24)], color=INK, sw=2.0))
    # висота 10.3 м
    whx = wcx + wtw / 2 + 26
    F.append(arrow(whx, brk + 4, whx, dish_y, color=INK, sw=1.7))
    F.append(text(whx + 8, brk - 4, "≈ 10.3 м", size=13.5, color=INK, bold=True, anchor="start"))
    F.append(text(whx + 8, brk + 14, "води", size=12, color=INK, anchor="start"))
    F.append(text(wcx, dish_y + 60, "вода", size=12.5, color=WATERD, bold=True))
    for dx in (-74, -48, 48, 74):
        F.append(arrow(wcx + dx, dish_y - 34, wcx + dx, dish_y - 6, color=POS, sw=2.2))

    # порівняння густин
    F.append(fitbox(wcx - 118, 250, 236, 76,
                    "ту саму атмосферу\nвода тримає стовпом\nу 13.6 раза вищим —\n"
                    "бо ртуть у 13.6× густіша",
                    size=12, bold=True, fill="#eef4fb", stroke=NEG, pad=9))

    # ── формула балансу знизу ──
    F.append(fitbox(70, 512, 780, 58,
                    "Стовп рідини важить рівно стільки, скільки тисне атмосфера:  ρ · g · h = P₀.\n"
                    "Ртуть густа — вистачає 760 мм; води треба ≈ 10.3 м. Звідси й одиниця «мм рт. ст.».",
                    size=13, bold=True, fill="#eafaf0", stroke=GREEN, pad=10))

    render(os.path.join(IMG, "barometer.svg"), W, H, *F,
           title="Барометр: атмосфера тримає стовп ртуті 760 мм")


# ── Фігура 3: тиск падає з висотою експонентою, а не лінійно ──────────────────
def fig_pressure_altitude():
    W, H = 900, 580
    F = []
    x0, x1 = 150, 720            # тиск 0 → 105 кПа
    yb, yt = 470, 88             # висота 0 → 16 км (yb унизу = 0 км)
    Pmax = 105.0
    Hkm = 16.0
    P0 = 101.3
    Hs = 8.4                     # висота однорідної атмосфери / масштаб

    def X(p):
        return x0 + (p / Pmax) * (x1 - x0)

    def Y(h):
        return yb - (h / Hkm) * (yb - yt)

    def P(h):
        return P0 * math.exp(-h / Hs)

    # мітки осей
    for p in [0, 20, 40, 60, 80, 100]:
        F.append(line(X(p), yb, X(p), yb + 6, color=MUTED, sw=1.1))
        F.append(text(X(p), yb + 24, "%d" % p, size=12, color=MUTED))
    for h in [0, 4, 8, 12, 16]:
        F.append(line(x0 - 6, Y(h), x0, Y(h), color=MUTED, sw=1.1))
        F.append(text(x0 - 12, Y(h) + 4, "%d" % h, size=12, color=MUTED, anchor="end"))

    # осі
    F.append(line(x0, yt, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 50, "тиск  P, кПа  →", size=13.5, color=INK))
    F.append(text(x0 - 6, yt - 18, "висота  h, км  ↑", size=13, color=MUTED, anchor="start"))

    # пряма «стала густина» (лінійна) — обірвалась би на висоті H
    F.append(line(X(P0), Y(0), X(0), Y(Hs), color=NEG, sw=2.2, dash="7 5"))
    F.append(text(X(52), Y(4.6) - 2, "якби густина була стала —", size=12, color=NEG, anchor="start"))
    F.append(text(X(52), Y(4.6) + 16, "тиск упав би до нуля на ~8.4 км", size=12, color=NEG, anchor="start"))

    # справжня крива — експонента
    curve = [(X(P(h)), Y(h)) for h in frange(0.0, Hkm, 200)]
    F.append(polyline(curve, color=GREEN, sw=3.4))
    F.append(text(X(P(13.2)) + 12, Y(13.2), "справжня атмосфера:", size=12.5, color=GREEN, bold=True, anchor="start"))
    F.append(text(X(P(13.2)) + 12, Y(13.2) + 17, "P = P₀ · e^(−h/H)", size=12.5, color=GREEN, bold=True, anchor="start"))

    # орієнтири
    def mark(h, txt, col, up=True):
        F.append(circle(X(P(h)), Y(h), 5.5, fill=col, stroke=INK, sw=1.4))
        dyt = -10 if up else 20
        F.append(text(X(P(h)) + 12, Y(h) + dyt, txt, size=12, color=col, bold=True, anchor="start"))

    F.append(line(x0, Y(0), X(P0), Y(0), color="#d7dbe0", sw=1.0, dash="3 4"))
    mark(0.0, "рівень моря — 101 кПа (1 атм)", INK, up=False)
    mark(5.5, "5.5 км — тиск удвічі менший (½)", POS, up=True)
    mark(8.85, "Еверест 8.85 км ≈ ⅓ атм", ORANGE, up=True)
    mark(11.0, "літак ~11 км ≈ ¼: салон герметизують", NEG, up=True)

    # позначка масштабної висоти H
    F.append(line(x0, Y(Hs), X(P(Hs)), Y(Hs), color="#d7dbe0", sw=1.0, dash="3 4"))
    F.append(text(X(P(Hs)) + 12, Y(Hs) + 2, "H ≈ 8.4 км → 1/e ≈ 37%", size=11.5, color=MUTED, anchor="start"))

    # підсумок
    F.append(fitbox(x0, 508, 720, 52,
                    "Менший тиск → рідше повітря → тиск падає щоразу повільніше:\n"
                    "не по прямій, а експонентою — тому в атмосфери немає різкого «краю».",
                    size=12.5, bold=True, fill="#eafaf0", stroke=GREEN, pad=9))

    render(os.path.join(IMG, "pressure-altitude.svg"), W, H, *F,
           title="Чому тиск падає з висотою експонентою, а не лінійно")


# ── Фігура 4: дві відповіді на ту саму загадку висоти ≈ 10 м ──────────────────
def fig_two_models():
    W, H = 1000, 600
    F = []

    dish_y = 452
    col_top = 158            # верх стовпа рідини
    tube_top = col_top - 44  # закритий верх (порожнеча)
    tw = 40

    def apparatus(cx, liquid, ldark):
        g = []
        g.append(rect(cx - 92, dish_y, 184, 32, fill=liquid, stroke=ldark, sw=1.5, rx=4))
        g.append(rect(cx - 98, dish_y + 28, 196, 12, fill="#e5e7eb", stroke=ldark, sw=1.4, rx=3))
        g.append(rect(cx - tw / 2, tube_top, tw, dish_y - tube_top, fill="#ffffff", stroke=INK, sw=1.6, rx=3))
        g.append(rect(cx - tw / 2 + 2, col_top, tw - 4, dish_y - col_top + 18, fill=liquid, stroke="none", sw=0))
        return "".join(g)

    # роздільник між двома поглядами
    F.append(line(W / 2, 74, W / 2, 486, color="#dfe4ea", sw=1.4, dash="4 6"))

    # ── ЛІВОРУЧ: Ґалілей (трубка ближче до краю, пояснення — до середини) ──
    lx = 170
    tb, _, _ = textbox(lx, 64, "Ґалілей · 1638", size=13.5, bold=True,
                       fill="#fdecea", stroke=POS, pad=8)
    F.append(tb)
    F.append(text(lx, 92, "стовп рветься сам", size=12, color=POS, italic=True))
    F.append(apparatus(lx, WATER, WATERD))
    F.append(text(lx + tw / 2 + 10, tube_top + 22, "порожнеча", size=11, color=MUTED, anchor="start"))
    # «порожнеча тягне» — стрілка вгору в пустоту
    F.append(arrow(lx, col_top - 2, lx, tube_top + 12, color=POS, sw=2.2))
    # символ обриву стовпа посередині
    F.append(polyline([(lx - tw / 2 - 7, 214), (lx - 5, 202),
                       (lx + 6, 220), (lx + tw / 2 + 7, 208)], color=POS, sw=2.4))
    F.append(text(lx, 250, "«рветься»", size=11.5, color=POS, bold=True))
    F.append(fitbox(280, 296, 194, 104,
                    "причина, за Ґалілеєм:\nпорожнеча вгорі «тягне»\nй тримає стовп, доки той\n"
                    "не порветься від власної ваги",
                    size=12, bold=False, fill="#fdecea", stroke=POS, pad=9))
    F.append(text(lx, dish_y + 56, "повітря на чашу — поза увагою", size=11, color=MUTED))

    # ── ПРАВОРУЧ: Торрічеллі ──
    rx = 830
    tb2, _, _ = textbox(rx, 64, "Торрічеллі · 1643", size=13.5, bold=True,
                        fill="#eafaf0", stroke=FIELD, pad=8)
    F.append(tb2)
    F.append(text(rx, 92, "повітря штовхає знизу", size=12, color=FIELD, italic=True))
    F.append(apparatus(rx, MERC, MERCD))
    F.append(text(rx, tube_top + 22, "порожнеча", size=11, color=MUTED))
    F.append(text(rx, tube_top + 37, "(вакуум)", size=11, color=MUTED))
    for dx in (-88, -62, 62, 88):
        F.append(arrow(rx + dx, dish_y - 30, rx + dx, dish_y - 4, color=POS, sw=2.4))
    F.append(text(rx, dish_y - 42, "атмосфера тисне на чашу", size=11.5, color=POS, bold=True))
    F.append(fitbox(526, 296, 194, 104,
                    "причина, за Торрічеллі:\nвага всієї атмосфери\nтисне на відкриту чашу\n"
                    "й підпирає стовп знизу",
                    size=12, bold=False, fill="#eafaf0", stroke=FIELD, pad=9))

    # ── підсумок ──
    F.append(fitbox(90, 512, 820, 60,
                    "Той самий стовп, та сама гранична висота — але протилежна причина. Ґалілей дивився ВГОРУ трубки\n"
                    "(що тримає), Торрічеллі — ВНИЗ, на чашу (що штовхає). Правильним виявилося друге.",
                    size=13, bold=True, fill="#eef4fb", stroke=NEG, pad=10))

    render(os.path.join(IMG, "two-models.svg"), W, H, *F,
           title="Дві відповіді на ту саму загадку висоти ≈ 10 м")


# ── Фігура 5: хроніка відкриття (1630 → 1654) ─────────────────────────────────
def fig_timeline():
    W, H = 1160, 560
    F = []
    axis_y = 300
    margin = 100
    span = (W - 2 * margin) / 6.0

    # (рік, ім'я, місце, внесок(2 рядки), мітка-тег, колір)
    nodes = [
        ("1630", "Баліані й Ґалілей", "Італія", "насос не бере воду\nвище ≈ 10 м", "загадка", MUTED),
        ("1638", "Ґалілео Ґалілей", "Флоренція", "пояснив хибно:\n«стовп рветься сам»", "хибна ідея", POS),
        ("≈1640", "Ґаспаро Берті", "Рим", "водяний барометр;\nвгорі порожнеча", "прилад", NEG),
        ("1643–44", "Е. Торрічеллі", "Флоренція", "ртуть 760 мм;\n«океан повітря»", "ідея + вимір", FIELD),
        ("1648", "Паскаль і Пер'є", "Пюї-де-Дом", "на горі стовп нижчий\nна ≈ 85 мм", "доказ", ORANGE),
        ("1650", "Отто фон Ґеріке", "Магдебург", "вакуумний насос:\nпорожнеча на замовлення", "вакуум", NEG),
        ("1654", "Ґеріке", "Реґенсбург", "півкулі: коні\nне розняли", "видовище", ORANGE),
    ]

    # вісь часу
    F.append(line(margin - 40, axis_y, W - margin + 40, axis_y, color=INK, sw=2.0))
    F.append(text(W - margin + 46, axis_y + 5, "час →", size=12.5, color=MUTED, anchor="start"))

    cw, ch = 198, 150
    for i, (yr, name, place, contr, tag, col) in enumerate(nodes):
        x = margin + i * span
        up = (i % 2 == 0)
        ctop = axis_y - 30 - ch if up else axis_y + 30

        # вузол на осі + рік
        F.append(circle(x, axis_y, 6.5, fill=col, stroke=INK, sw=1.5))
        F.append(line(x, axis_y, x, ctop + ch if up else ctop, color=col, sw=1.6))
        F.append(text(x, axis_y - 16 if not up else axis_y + 24, yr, size=13, color=INK, bold=True))

        # картка
        F.append(rect(x - cw / 2, ctop, cw, ch, fill="#ffffff", stroke="#d7dbe0", sw=1.4, rx=8))
        # тег-пігулка
        tb, _, _ = textbox(x, ctop + 20, tag, size=11.5, bold=True, pad=7,
                           fill="#ffffff", stroke=col, color=col)
        F.append(tb)
        # ім'я, місце, внесок
        F.append(text(x, ctop + 48, name, size=13, color=INK, bold=True))
        F.append(text(x, ctop + 66, place, size=11, color=MUTED))
        cl = contr.split("\n")
        F.append(text(x, ctop + 92, cl[0], size=11.5, color=INK))
        if len(cl) > 1:
            F.append(text(x, ctop + 110, cl[1], size=11.5, color=INK))

    # підсумковий рядок унизу
    F.append(fitbox(margin - 40, 512, W - 2 * (margin - 40), 40,
                    "Загадка (Ґалілей) → прилад (Берті) → правильна ідея й вимір (Торрічеллі, Італія) → "
                    "доказ висотою (Паскаль, Франція) → видовище сили (Ґеріке, Німеччина).",
                    size=12.5, bold=True, fill="#eafaf0", stroke=FIELD, pad=8))

    render(os.path.join(IMG, "discovery-timeline.svg"), W, H, *F,
           title="Як зважили небо: хроніка відкриття, 1630 → 1654")


# ── Фігура 6 (вставка math): рівновага тонкого шару → dP = −ρ·g·dh ─────────────
def fig_hydrostatic_slab():
    W, H = 980, 600
    F = []

    # ── ліва панель: стовп повітря з виділеним тонким шаром ──
    cx0, cx1 = 118, 226
    ctop, gy = 82, 466
    F.append(rect(cx0, ctop, cx1 - cx0, gy - ctop, fill=AIR, stroke=AIRD, sw=1.4, rx=3))
    rows = 23
    for i in range(rows):
        frac = i / (rows - 1)
        yy = gy - 11 - (gy - ctop - 22) * frac
        ndot = max(1, int(round(5 * (1 - frac) ** 1.2)))
        for j in range(ndot):
            xx = cx0 + 12 + (cx1 - cx0 - 24) * ((j + 0.5) / ndot)
            xx += 4.6 * math.sin(i * 1.6 + j * 2.1)
            F.append(circle(xx, yy, 2.0, fill=DOT, stroke="none", sw=0))
    F.append(ground(cx0 - 30, cx1 + 30, gy))
    F.append(text((cx0 + cx1) / 2, gy + 22, "рівень моря", size=11, color=MUTED))

    # вісь висоти h
    axx = cx0 - 16
    F.append(arrow(axx, gy, axx, ctop - 2, color=MUTED, sw=1.6))
    F.append(text(axx - 5, ctop + 10, "h", size=13, color=MUTED, anchor="end", italic=True))

    # виділений тонкий шар
    sy0, sy1 = 258, 282
    F.append(rect(cx0, sy0, cx1 - cx0, sy1 - sy0, fill="#fff3cd", stroke=ORANGE, sw=1.8, rx=2))
    F.append(text((cx0 + cx1) / 2, sy0 - 7, "шар на висоті h", size=11, color=ORANGE, bold=True))
    F.append(line(axx, (sy0 + sy1) / 2, cx0, (sy0 + sy1) / 2, color="#d7dbe0", sw=1.0, dash="3 4"))

    # конектор «збільшимо»
    F.append(line(cx1, (sy0 + sy1) / 2, 498, 273, color=ORANGE, sw=1.4, dash="5 4"))
    F.append(text(360, 244, "збільшимо шар →", size=12, color=ORANGE, bold=True))

    # ── права панель: діаграма сил на шар ──
    sx0, sx1 = 500, 726
    scx = (sx0 + sx1) / 2
    scy, sh = 273, 30
    F.append(rect(sx0, scy - sh / 2, sx1 - sx0, sh, fill=AIR, stroke=AIRD, sw=1.6, rx=3))
    F.append(text(scx, 140, "тонкий шар:  площа A,  товщина dh", size=12.5, bold=True))

    xP, xW = 585, 668
    # тиск ЗГОРИ (донизу) на верхню грань
    F.append(arrow(xP, 196, xP, scy - sh / 2 - 2, color=NEG, sw=2.6))
    F.append(text(xP, 186, "P(h+dh)·A", size=12.5, color=NEG, bold=True))
    F.append(text(xP, 172, "тисне згори", size=10.5, color=MUTED))
    # тиск ЗНИЗУ (вгору) на нижню грань
    F.append(arrow(xP, 350, xP, scy + sh / 2 + 2, color=NEG, sw=2.6))
    F.append(text(xP, 366, "P(h)·A", size=12.5, color=NEG, bold=True))
    F.append(text(xP, 382, "тисне знизу", size=10.5, color=MUTED))
    # вага шару (донизу)
    F.append(arrow(xW, scy, xW, 352, color=POS, sw=2.6))
    F.append(text(xW + 12, 322, "вага шару", size=10.5, color=POS, anchor="start"))
    F.append(text(xW + 12, 338, "dW = ρ·g·A·dh", size=12, color=POS, bold=True, anchor="start"))

    F.append(text(scx, 424, "тиск знизу трохи більший — цей надлишок і тримає вагу шару",
                  size=11, color=MUTED))

    # ── підсумкова рівність ──
    F.append(fitbox(95, 506, 790, 66,
                    "Рівновага тонкого шару:   P(h)·A  =  P(h+dh)·A  +  ρ·g·A·dh\n"
                    "⟹   dP = P(h+dh) − P(h) = −ρ·g·dh   (тиск меншає рівно на вагу шару над 1 м²)",
                    size=13, bold=True, fill="#eafaf0", stroke=GREEN, pad=10))

    render(os.path.join(IMG, "hydrostatic-slab.svg"), W, H, *F,
           title="Звідки dP = −ρ·g·dh: рівновага тонкого шару повітря")


# ── Фігура 7 (вставка math): ізотермічна модель проти реальної ────────────────
def fig_isothermal_vs_real():
    W, H = 980, 590
    F = []
    yb, yt = 470, 96
    Hkm = 12.0

    def Yh(h):
        return yb - (h / Hkm) * (yb - yt)

    # ── Панель A: температура з висотою ──
    ax0, ax1 = 108, 300
    Tmin, Tmax = 200.0, 300.0

    def XT(T):
        return ax0 + (T - Tmin) / (Tmax - Tmin) * (ax1 - ax0)

    F.append(text((ax0 + ax1) / 2, yt - 34, "ТЕМПЕРАТУРА", size=12.5, bold=True))
    F.append(line(ax0, yt, ax0, yb, color=INK, sw=1.6))
    F.append(line(ax0, yb, ax1, yb, color=INK, sw=1.6))
    for T in [200, 240, 280]:
        F.append(line(XT(T), yb, XT(T), yb + 5, color=MUTED, sw=1.0))
        F.append(text(XT(T), yb + 20, "%d" % T, size=11, color=MUTED))
    for h in [0, 4, 8, 12]:
        F.append(line(ax0 - 5, Yh(h), ax0, Yh(h), color=MUTED, sw=1.0))
        F.append(text(ax0 - 9, Yh(h) + 4, "%d" % h, size=11, color=MUTED, anchor="end"))
    F.append(text((ax0 + ax1) / 2, yb + 40, "T, К  →", size=12, color=INK))
    F.append(text(ax0 - 6, yt - 12, "h, км ↑", size=11.5, color=MUTED, anchor="start"))
    # ізотермічна: вертикаль T = 288
    F.append(line(XT(288), Yh(0), XT(288), Yh(12), color=NEG, sw=2.4, dash="7 5"))
    F.append(text(XT(288) + 6, Yh(6.6), "ізотермічна", size=10.5, color=NEG, bold=True, anchor="start"))
    F.append(text(XT(288) + 6, Yh(6.6) + 14, "T = 288 К", size=10.5, color=NEG, anchor="start"))
    # реальна: T = 288 − 6.5·h
    realT = [(XT(288 - 6.5 * h), Yh(h)) for h in frange(0, 12, 40)]
    F.append(polyline(realT, color=GREEN, sw=3.0))
    F.append(text(XT(214), Yh(9.7), "реальна", size=10.5, color=GREEN, bold=True, anchor="start"))
    F.append(text(XT(214), Yh(9.7) + 14, "−6.5 К/км", size=10.5, color=GREEN, anchor="start"))

    # ── Панель B: тиск з висотою ──
    bx0, bx1 = 470, 892

    def XP(p):
        return bx0 + p * (bx1 - bx0)

    F.append(text((bx0 + bx1) / 2, yt - 34, "ТИСК", size=12.5, bold=True))
    F.append(line(bx0, yt, bx0, yb, color=INK, sw=1.6))
    F.append(line(bx0, yb, bx1, yb, color=INK, sw=1.6))
    for p in [0.0, 0.25, 0.5, 0.75, 1.0]:
        F.append(line(XP(p), yb, XP(p), yb + 5, color=MUTED, sw=1.0))
        lab = ("%.2f" % p).rstrip("0").rstrip(".")
        F.append(text(XP(p), yb + 20, lab, size=11, color=MUTED))
    for h in [0, 4, 8, 12]:
        F.append(line(bx0 - 5, Yh(h), bx0, Yh(h), color=MUTED, sw=1.0))
        F.append(text(bx0 - 9, Yh(h) + 4, "%d" % h, size=11, color=MUTED, anchor="end"))
    F.append(text((bx0 + bx1) / 2, yb + 40, "P / P₀  →", size=12, color=INK))
    F.append(text(bx0 - 6, yt - 12, "h, км ↑", size=11.5, color=MUTED, anchor="start"))

    Hs = 8.43

    def Piso(h):
        return math.exp(-h / Hs)

    def Preal(h):
        return max(0.0, (1 - 6.5 * h / 288.15)) ** 5.2559

    iso = [(XP(Piso(h)), Yh(h)) for h in frange(0, 12, 120)]
    F.append(polyline(iso, color=NEG, sw=2.6, dash="7 5"))
    real = [(XP(Preal(h)), Yh(h)) for h in frange(0, 11, 120)]
    F.append(polyline(real, color=GREEN, sw=3.2))

    # мітки кривих
    F.append(text(XP(Piso(8.6)) + 8, Yh(8.6), "ізотермічна", size=11, color=NEG, bold=True, anchor="start"))
    F.append(text(XP(Piso(8.6)) + 8, Yh(8.6) + 14, "P₀·e^(−h/H)", size=11, color=NEG, anchor="start"))
    F.append(text(XP(Preal(6.4)) - 8, Yh(6.4), "реальна", size=11, color=GREEN, bold=True, anchor="end"))
    F.append(text(XP(Preal(6.4)) - 8, Yh(6.4) + 14, "P₀·(T/T₀)^5.26", size=11, color=GREEN, anchor="end"))

    # лінія «половина тиску» й дві точки перетину
    F.append(line(bx0, Yh(0), bx0, Yh(0), color="none", sw=0))
    F.append(line(XP(0.5), Yh(0), XP(0.5), Yh(6.4), color="#d7dbe0", sw=1.0, dash="3 4"))
    F.append(circle(XP(0.5), Yh(5.84), 4.5, fill=NEG, stroke=INK, sw=1.2))
    F.append(circle(XP(0.499), Yh(5.5), 4.5, fill=GREEN, stroke=INK, sw=1.2))
    F.append(text(XP(0.5) + 11, Yh(5.84) - 8, "½ :  5.8 км  (ізотерм.)", size=10.5, color=NEG, bold=True, anchor="start"))
    F.append(text(XP(0.5) + 11, Yh(5.5) + 16, "½ :  5.5 км  (реальна)", size=10.5, color=GREEN, bold=True, anchor="start"))

    # ── підсумок ──
    F.append(fitbox(95, 500, 790, 70,
                    "Тиск падає вдвічі: ізотермічна модель — аж на 5.8 км, справжня атмосфера — уже на ≈ 5.5 км,\n"
                    "бо вгорі вона холодніша (менша T → менша масштабна висота H → швидший спад).",
                    size=12.5, bold=True, fill="#eef4fb", stroke=NEG, pad=9))

    render(os.path.join(IMG, "isothermal-vs-real.svg"), W, H, *F,
           title="Ізотермічна модель проти реальної: температура задає форму спаду")


if __name__ == "__main__":
    fig_air_column()
    fig_barometer()
    fig_pressure_altitude()
    fig_two_models()
    fig_timeline()
    fig_hydrostatic_slab()
    fig_isothermal_vs_real()
    print("OK: 7 SVG ->", IMG)

# -*- coding: utf-8 -*-
"""Фігури до теми «Тиск».
Запуск із теки теми:  python figs.py   → SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

WATER = "#bfe0f2"
WATERD = "#7cc0e0"
SOIL = "#e9ddc7"
SOILD = "#c9b48c"
STEEL = "#c4c9d2"
STEELD = "#8b9099"
DOT = "#5b9bd0"
ORANGE = "#e08e0b"
GREEN = FIELD


def frange(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def polyline(pts, color=INK, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


def polygon(pts, fill=WATER, stroke="none", sw=0):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" '
            'stroke-width="%.1f"/>' % (p, fill, stroke, sw))


def hatch_top(x1, x2, y, color=SOILD, sw=1.1):
    out = []
    n = int((x2 - x1) / 16) + 1
    for i in range(n):
        xx = x1 + i * 16
        out.append(line(xx, y, xx - 9, y + 10, color=color, sw=sw))
    return "".join(out)


# ── Фігура 1: та сама вага, різна площа опори → різний тиск ────────────────────
def fig_concentration():
    W, H = 1020, 600
    F = []
    gy = 372                     # верх ґрунту
    soil_h = 56

    F.append(text(W / 2, 52, "та сама вага 590 Н — різна площа опори → різний тиск",
                  size=14, bold=True, color=MUTED))

    # ґрунт/сніг суцільною смугою
    F.append(rect(70, gy, W - 140, soil_h, fill=SOIL, stroke=SOILD, sw=1.4, rx=0))
    F.append(hatch_top(76, W - 76, gy))

    # (cx, назва, ширина контакту, глибина занурення, площа, тиск, колір тиску)
    cols = [
        (210, "гострий каблук", 10, 44, "A = 1 см²", "P ≈ 6 МПа", POS),
        (510, "пласка підошва", 74, 12, "A = 100 см²", "P ≈ 59 кПа", ORANGE),
        (820, "широка лижа", 200, 3, "A = 2000 см²", "P ≈ 3 кПа", GREEN),
    ]

    for cx, name, cw, dent, area, pres, col in cols:
        # однакова вага згори: стрілка + блок
        F.append(arrow(cx, 92, cx, 148, color=INK, sw=3.0))
        F.append(text(cx, 84, "F = 590 Н", size=12.5, color=INK, bold=True))
        F.append(rect(cx - 24, 150, 48, 30, fill="#eef1f5", stroke=INK, sw=1.6, rx=5))
        # опора: трапеція від блоку (48) до ширини контакту cw, заходить у ґрунт на dent
        bt = 182
        bb = gy + dent
        F.append(polygon([(cx - 24, bt), (cx + 24, bt),
                          (cx + cw / 2, bb), (cx - cw / 2, bb)],
                         fill=STEEL, stroke=STEELD, sw=1.5))
        # позначка ширини контакту під ґрунтом
        yb = gy + soil_h + 16
        F.append(line(cx - cw / 2, yb, cx + cw / 2, yb, color=col, sw=2.0))
        F.append(line(cx - cw / 2, yb - 5, cx - cw / 2, yb + 5, color=col, sw=2.0))
        F.append(line(cx + cw / 2, yb - 5, cx + cw / 2, yb + 5, color=col, sw=2.0))
        # назва зверху
        F.append(text(cx, 210, name, size=12.5, color=INK, bold=True))
        # коробка з площею та тиском
        tb, _, _ = textbox(cx, yb + 46, area + "\n" + pres, size=13, bold=True,
                           pad=9, fill="#ffffff", stroke=col, color=col)
        F.append(tb)

    # словесна позначка «грузне / тримається»
    F.append(text(210, gy + 34, "грузне", size=11, color=POS, bold=True))
    F.append(text(820, gy - 8, "тримається зверху", size=11, color=GREEN, bold=True))

    F.append(fitbox(80, 524, 860, 52,
                    "Вага та сама — а тиск відрізняється в тисячі разів: P = F/A.\n"
                    "Мала площа опори (каблук) → величезний тиск і глибока вм'ятина; велика (лижа) → тиск мізерний.",
                    size=13, bold=True, fill="#eafaf0", stroke=GREEN, pad=10))

    render(os.path.join(IMG, "concentration.svg"), W, H, *F,
           title="Тиск — це сконцентрованість сили по площі")


# ── Фігура 2: тиск у рідині ізотропний — однаковий на всі боки ─────────────────
def fig_isotropy():
    W, H = 1000, 660
    F = []

    F.append(line(W / 2, 70, W / 2, 580, color="#dfe4ea", sw=1.4, dash="4 6"))

    # ── ліворуч: бак води, занурена частинка, стрілки з усіх боків ──
    tx0, tx1, tty, tby = 120, 380, 92, 452
    F.append(rect(tx0, tty, tx1 - tx0, tby - tty, fill=WATER, stroke=WATERD, sw=1.6, rx=4))
    F.append(text((tx0 + tx1) / 2, tty - 14, "занурена частинка рідини", size=13, bold=True))
    # трохи молекул для фактури
    for i in range(26):
        xx = tx0 + 16 + (tx1 - tx0 - 32) * ((i * 0.61803) % 1.0)
        yy = tty + 20 + (tby - tty - 40) * ((i * 0.37294) % 1.0)
        F.append(circle(xx, yy, 2.0, fill=DOT, stroke="none", sw=0))
    ox, oy = (tx0 + tx1) / 2, 292
    R_out, R_in = 74, 30
    for k in range(8):
        a = k * math.pi / 4
        dx, dy = math.cos(a), math.sin(a)
        F.append(arrow(ox + R_out * dx, oy + R_out * dy,
                       ox + R_in * dx, oy + R_in * dy, color=POS, sw=2.4))
    F.append(circle(ox, oy, R_in - 6, fill="#ffffff", stroke=INK, sw=1.6))
    F.append(text(ox, oy + 5, "P", size=15, color=POS, bold=True, italic=True))
    F.append(text((tx0 + tx1) / 2, tby + 22, "тисне всередину з усіх боків однаково",
                  size=11.5, color=POS, bold=True))

    # ── праворуч: та сама площадка в трьох орієнтаціях — той самий тиск ──
    rcx = 730
    F.append(text(rcx, 106, "поверни площадку як завгодно —", size=13, bold=True))
    F.append(text(rcx, 126, "тиск на неї той самий", size=13, bold=True))

    def plate(cx, cy, ang, label):
        g = []
        L = 46
        c, s = math.cos(ang), math.sin(ang)
        # площадка (товста лінія)
        g.append(line(cx - L * c, cy - L * s, cx + L * c, cy + L * s, color=INK, sw=4.0))
        # перпендикуляр
        nx, ny = -s, c
        for sign in (1, -1):
            x2 = cx + sign * 30 * nx
            y2 = cy + sign * 30 * ny
            x1 = cx + sign * 62 * nx
            y1 = cy + sign * 62 * ny
            g.append(arrow(x1, y1, x2, y2, color=NEG, sw=2.4))
        g.append(text(cx, cy + 80, label, size=11, color=MUTED))
        return "".join(g)

    F.append(plate(rcx, 210, 0.0, "плазом"))
    F.append(plate(rcx, 350, math.pi / 2, "боком"))
    F.append(plate(rcx, 490, math.pi / 4, "під кутом"))
    F.append(mtext(rcx + 172, 350, ["однакова", "довжина стрілок", "= той самий тиск"],
                   size=11.5, color=NEG, anchor="middle", bold=True))

    F.append(fitbox(90, 588, 820, 52,
                    "У рідині й газі тиск ізотропний — не має напрямку: діє однаково на будь-яку площадку,\n"
                    "хоч як її повернути. Тому занурене тіло стискається звідусіль рівномірно.",
                    size=12.5, bold=True, fill="#eef4fb", stroke=NEG, pad=9))

    render(os.path.join(IMG, "isotropy.svg"), W, H, *F,
           title="Тиск у рідині діє на всі боки однаково")


# ── Фігура 3: тиск росте вглиб; гідростатичний парадокс ───────────────────────
def fig_hydrostatic():
    W, H = 1020, 580
    F = []
    F.append(line(430, 70, 430, 500, color="#dfe4ea", sw=1.4, dash="4 6"))

    # ── ліворуч: тиск росте лінійно з глибиною ──
    vx0, vx1 = 150, 280
    vty, vby = 96, 440
    F.append(rect(vx0, vty, vx1 - vx0, vby - vty, fill=WATER, stroke=WATERD, sw=1.6, rx=3))
    F.append(text((vx0 + vx1) / 2, vty - 14, "P = ρ·g·h", size=14, bold=True))
    # вісь глибини
    F.append(arrow(vx0 - 16, vty, vx0 - 16, vby, color=MUTED, sw=1.6))
    F.append(text(vx0 - 22, vty + 12, "h", size=13, color=MUTED, anchor="end", italic=True))
    # стрілки тиску з правого боку — довшають донизу
    for k in range(1, 6):
        yy = vty + (vby - vty) * k / 5.5
        ln = 10 + 46 * (k / 5.0)
        F.append(arrow(vx1 + ln, yy, vx1, yy, color=POS, sw=2.2))
    F.append(text(vx1 + 66, vty + 40, "тиск", size=11.5, color=POS, bold=True, anchor="start"))
    F.append(text(vx1 + 66, vty + 56, "росте", size=11.5, color=POS, bold=True, anchor="start"))
    F.append(text(vx1 + 66, vty + 72, "вглиб", size=11.5, color=POS, bold=True, anchor="start"))
    # мітка 10 м → 1 атм
    y10 = vby - 8
    F.append(line(vx0 - 6, y10, vx1, y10, color=INK, sw=1.2, dash="4 4"))
    F.append(text((vx0 + vx1) / 2, vby + 22, "10 м води ≈ 1 атм", size=12, color=INK, bold=True))

    # ── праворуч: гідростатичний парадокс ──
    base = 448                    # спільне дно
    wl = 190                      # спільний рівень води
    F.append(text(730, 84, "гідростатичний парадокс", size=14, bold=True))
    F.append(text(730, 104, "різна форма, однаковий рівень → однаковий тиск на дно",
                  size=11.5, color=MUTED))

    # спільна лінія рівня води
    F.append(line(500, wl, 970, wl, color=WATERD, sw=1.3, dash="6 5"))
    F.append(text(984, wl + 4, "h", size=12.5, color=WATERD, bold=True, anchor="start", italic=True))

    # посудина 1: вузька трубка
    a = 560
    F.append(polygon([(a - 18, wl), (a + 18, wl), (a + 18, base), (a - 18, base)], fill=WATER))
    F.append(polyline([(a - 18, wl), (a - 18, base), (a + 18, base), (a + 18, wl)], color=INK, sw=1.8))

    # посудина 2: широка діжка
    b = 700
    F.append(polygon([(b - 62, wl), (b + 62, wl), (b + 62, base), (b - 62, base)], fill=WATER))
    F.append(polyline([(b - 62, wl), (b - 62, base), (b + 62, base), (b + 62, wl)], color=INK, sw=1.8))

    # посудина 3: лійка, що розширюється вгору
    c = 860
    F.append(polygon([(c - 70, wl), (c + 70, wl), (c + 20, base), (c - 20, base)], fill=WATER))
    F.append(polyline([(c - 70, wl), (c - 20, base), (c + 20, base), (c + 70, wl)], color=INK, sw=1.8))

    # спільне дно + однакова позначка тиску під кожним
    F.append(line(524, base, 946, base, color=INK, sw=2.4))
    for cx in (a, b, c):
        F.append(arrow(cx, base + 30, cx, base + 6, color=POS, sw=2.4))
        tb, _, _ = textbox(cx, base + 52, "P = ρgh", size=11.5, bold=True, pad=6,
                           fill="#fdecea", stroke=POS, color=POS)
        F.append(tb)

    F.append(fitbox(90, 512, 840, 56,
                    "Ліворуч: тиск наростає лінійно з глибиною — кожні 10 м води додають ≈ 1 атм.\n"
                    "Праворуч: на дно тисне лише стовп над ним, тож форма й кількість води не важать — тільки висота h.",
                    size=12.5, bold=True, fill="#eafaf0", stroke=GREEN, pad=10))

    render(os.path.join(IMG, "hydrostatic.svg"), W, H, *F,
           title="Тиск росте вглиб, але залежить лише від глибини")


# ── Фігура 4: принцип Паскаля — гідравлічний важіль ───────────────────────────
def fig_hydraulic():
    W, H = 980, 560
    F = []

    # рідина: U-подібна посудина
    lL, rL = 210, 300            # ліва вузька колона (x)
    lR, rR = 560, 770            # права широка колона (x)
    top_l = 214                  # верх рідини під лівим поршнем
    top_r = 250                  # верх рідини під правим поршнем
    bot = 430                    # рівень нижньої перемички

    # заливка рідини (ліва колона + перемичка + права колона)
    F.append(polygon([(lL, top_l), (rL, top_l), (rL, bot), (lL, bot)], fill=WATER))
    F.append(polygon([(lL, bot), (rR, bot), (rR, bot + 40), (lL, bot + 40)], fill=WATER))
    F.append(polygon([(lR, top_r), (rR, top_r), (rR, bot), (lR, bot)], fill=WATER))
    # обведення
    F.append(polyline([(lL, top_l), (lL, bot + 40), (rR, bot + 40), (rR, top_r)], color=INK, sw=1.8))
    F.append(polyline([(rL, top_l), (rL, bot)], color=INK, sw=1.8))
    F.append(polyline([(lR, top_r), (lR, bot)], color=INK, sw=1.8))

    # тиск однаковий — крапки-мітки в рідині
    for (px, py) in [(255, 330), (255, 400), (430, 415), (600, 400), (665, 350), (720, 400)]:
        F.append(circle(px, py, 3.0, fill=WATERD, stroke="none", sw=0))
    F.append(text(430, 340, "P однаковий", size=12.5, color=NEG, bold=True))
    F.append(text(430, 358, "у всій рідині", size=12.5, color=NEG, bold=True))

    # ── лівий (вузький) поршень + мала сила ──
    F.append(rect(lL - 4, top_l - 16, (rL - lL) + 8, 16, fill=STEEL, stroke=STEELD, sw=1.5, rx=2))
    F.append(arrow((lL + rL) / 2, 118, (lL + rL) / 2, top_l - 18, color=POS, sw=3.0))
    F.append(text((lL + rL) / 2, 108, "F₁ = 100 Н", size=13, color=POS, bold=True))
    F.append(text((lL + rL) / 2, top_l + 34, "A₁ = 1 см²", size=12, color=INK, bold=True))
    F.append(text((lL + rL) / 2, 88, "мала сила", size=11.5, color=MUTED))

    # ── правий (широкий) поршень + велика сила, піднімає авто ──
    F.append(rect(lR - 4, top_r - 18, (rR - lR) + 8, 18, fill=STEEL, stroke=STEELD, sw=1.5, rx=2))
    # авто (спрощено)
    cx = (lR + rR) / 2
    F.append(rect(cx - 78, top_r - 66, 156, 34, fill="#eef1f5", stroke=INK, sw=1.5, rx=8))
    F.append(rect(cx - 46, top_r - 88, 78, 26, fill="#e2e7ee", stroke=INK, sw=1.3, rx=6))
    F.append(circle(cx - 46, top_r - 30, 12, fill="#4b4f56", stroke=INK, sw=1.3))
    F.append(circle(cx + 46, top_r - 30, 12, fill="#4b4f56", stroke=INK, sw=1.3))
    F.append(arrow(cx, top_r + 40, cx, top_r + 8, color=GREEN, sw=3.2))
    F.append(text(cx, top_r + 58, "F₂ = 10 000 Н", size=13, color=GREEN, bold=True))
    F.append(text(cx, top_r - 104, "піднімає тонну", size=11.5, color=GREEN, bold=True))
    F.append(text(cx, top_r + 76, "A₂ = 100 см²", size=12, color=INK, bold=True))

    # формула
    tb, _, _ = textbox(430, 150, "F₂ = F₁ · (A₂ / A₁)\n= 100 · 100 = 10 000 Н",
                       size=13.5, bold=True, pad=11, fill="#ffffff", stroke=NEG, color=INK)
    F.append(tb)

    F.append(fitbox(80, 496, 820, 54,
                    "Принцип Паскаля: доданий тиск однаковий у всій замкненій рідині. Площа більша в 100 разів —\n"
                    "сила більша в 100 разів. Виграш у силі оплачено довшим ходом: енергія зберігається.",
                    size=12.5, bold=True, fill="#eef4fb", stroke=NEG, pad=9))

    render(os.path.join(IMG, "hydraulic.svg"), W, H, *F,
           title="Принцип Паскаля: мала сила підіймає велику вагу")


# ── Фігура 5 (hist): уявний дослід Стевіна — «замерзання» води ─────────────────
def fig_stevin():
    W, H = 1000, 600
    F = []
    ICE = "#e6f3fb"

    cx = 290
    top_y, base_y = 158, 468
    wb, wt = 46, 150            # пів-ширина дна / верху

    # крижані клини обабіч стовпа
    F.append(polygon([(cx - wb, top_y), (cx - wb, base_y), (cx - wt, top_y)], fill=ICE))
    F.append(polygon([(cx + wb, top_y), (cx + wb, base_y), (cx + wt, top_y)], fill=ICE))
    # центральний стовп рідини
    F.append(rect(cx - wb, top_y, 2 * wb, base_y - top_y, fill=WATER, stroke="none", rx=0))
    # похилі стінки посудини
    F.append(line(cx - wb, base_y, cx - wt, top_y, color=INK, sw=2.6))
    F.append(line(cx + wb, base_y, cx + wt, top_y, color=INK, sw=2.6))
    # поверхня води
    F.append(line(cx - wt, top_y, cx + wt, top_y, color=WATERD, sw=2.2))
    # дно (товсте)
    F.append(line(cx - wb, base_y, cx + wb, base_y, color=INK, sw=3.6))
    # уявна межа стовпа
    F.append(line(cx - wb, top_y, cx - wb, base_y, color=NEG, sw=1.6, dash="5 5"))
    F.append(line(cx + wb, top_y, cx + wb, base_y, color=NEG, sw=1.6, dash="5 5"))

    # підписи всередині
    F.append(text(cx, top_y - 16, "стовп над дном", size=12.5, color=NEG, bold=True))
    F.append(text(cx, (top_y + base_y) / 2 + 4, "вода", size=12.5, color=NEG, bold=True))
    F.append(text(cx - 96, (top_y + base_y) / 2 + 44, "лід", size=13, color=MUTED, bold=True, italic=True))
    F.append(text(cx + 96, (top_y + base_y) / 2 + 44, "лід", size=13, color=MUTED, bold=True, italic=True))

    # стінки тримають лід (стрілки вгору-всередину від стінок у лід)
    F.append(arrow(196, 312, 238, 298, color=NEG, sw=2.4))
    F.append(arrow(384, 312, 342, 298, color=NEG, sw=2.4))
    F.append(text(150, 116, "стінки тримають лід", size=12, color=NEG, bold=True, anchor="start"))

    # вага стовпа тисне на дно
    F.append(arrow(cx, 432, cx, base_y - 4, color=POS, sw=3.0))
    tb, _, _ = textbox(cx, base_y + 40, "на дно — лише вага стовпа\nP = ρ·g·h",
                       size=12.5, bold=True, pad=8, fill="#fdecea", stroke=POS, color=POS)
    F.append(tb)

    # ── права панель: три кроки міркування ──
    F.append(text(720, 132, "Уявний дослід Стевіна (1586)", size=14.5, bold=True))
    F.append(mtext(548, 178, [
        "1.  Заморозь усю воду, крім прямого",
        "     стовпа просто над дном. Вага й",
        "     обрис ті самі — отже, і рівновага.",
        "",
        "2.  Лід нікуди не зрушив: його тримають",
        "     похилі стінки, а не дно.",
        "",
        "3.  На дно тисне лише стовп над ним —",
        "     тож форма й обсяг посудини не",
        "     важать, важить сама висота h.",
    ], size=13, color=INK, anchor="start", lh=1.42))

    F.append(fitbox(80, 542, 840, 44,
                    "Стевін довів гідростатичний парадокс без жодного вимірювання — самим міркуванням: "
                    "уявним «замерзанням» води.",
                    size=13, bold=True, fill="#eef4fb", stroke=NEG, pad=10))

    render(os.path.join(IMG, "stevin.svg"), W, H, *F,
           title="Крижана хитрість Стевіна: чому дно відчуває лише висоту")


# ── Фігура 6 (hist): хроніка поняття тиску в рідині ───────────────────────────
def fig_timeline():
    W, H = 1180, 480
    F = []
    y = 240
    F.append(line(70, y, 1112, y, color=MUTED, sw=2.6))

    # (x, дата, [рядки коробки], колір, апокриф?, "above"/"below")
    nodes = [
        (140, "≈ III ст. до н.е.",
         ["Архімед", "закон плавання —", "перша гідростатика"], FIELD, False, "below"),
        (385, "1586",
         ["Симон Стевін", "гідростатичний", "парадокс, доказ", "«замерзанням»"], NEG, False, "above"),
        (625, "1653",
         ["Блез Паскаль", "принцип передачі", "тиску (опубл. 1663)"], NEG, False, "below"),
        (860, "XIX ст.",
         ["«діжка Паскаля»", "crève-tonneau —", "імовірно апокриф"], POS, True, "above"),
        (1055, "1971",
         ["14-та CGPM", "одиниця «паскаль»", "(Па) в системі СІ"], FIELD, False, "below"),
    ]

    for x, date, lines, col, apo, side in nodes:
        # вузол на осі
        if apo:
            F.append(circle(x, y, 9, fill=BG, stroke=col, sw=2.6))
        else:
            F.append(circle(x, y, 9, fill=col, stroke=INK, sw=1.6))
        # дата — з протилежного від коробки боку осі
        if side == "below":
            F.append(text(x, y - 16, date, size=12.5, color=col, bold=True))
            ybox = 350
        else:
            F.append(text(x, y + 26, date, size=12.5, color=col, bold=True))
            ybox = 128
        # коробка з описом
        tb, bw, bh = textbox(x, ybox, "\n".join(lines), size=12.5, bold=True, pad=9,
                             fill="#ffffff", stroke=col, color=INK)
        # з'єднувач вузол→коробка
        if side == "below":
            F.append(line(x, y + 9, x, ybox - bh / 2, color=col, sw=1.6,
                          dash="5 5" if apo else None))
        else:
            F.append(line(x, y - 9, x, ybox + bh / 2, color=col, sw=1.6,
                          dash="5 5" if apo else None))
        F.append(tb)

    F.append(fitbox(90, 424, 1000, 44,
                    "Від Архімедового виштовхування до одиниці «паскаль» — майже 2200 років. "
                    "Пунктиром — «діжка Паскаля»: фізика правдива, історичність під сумнівом.",
                    size=13, bold=True, fill="#f4f6f8", stroke=MUTED, pad=10))

    render(os.path.join(IMG, "timeline.svg"), W, H, *F,
           title="Хроніка поняття тиску в рідині")


# ── Фігура (math): клин рідини — тиск однаковий на всі грані ───────────────────
def fig_wedge():
    W, H = 1060, 650
    F = []
    F.append(text(W / 2, 30, "Клин рідини: чому тиск однаковий на всі грані",
                  size=17, bold=True))

    # трикутний переріз клина
    O = (250, 440); A = (470, 440); B = (250, 250)
    F.append(polygon([O, A, B], fill=WATER, stroke=WATERD, sw=1.8))

    # позначки сторін і кута
    F.append(text(300, 464, "Δx", size=13, color=MUTED, italic=True))
    F.append(text(232, 352, "Δz", size=13, color=MUTED, italic=True, anchor="end"))
    F.append(text(456, 326, "Δs", size=13, color=MUTED, italic=True, anchor="start"))
    F.append(text(440, 430, "θ", size=13, color=MUTED, italic=True))

    # P_x — на вертикальну грань (стрілка праворуч, у грань)
    F.append(arrow(182, 345, 248, 345, color=POS, sw=2.8))
    F.append(text(174, 340, "Px", size=13.5, color=POS, bold=True, anchor="end"))
    # P_z — на горизонтальну грань (стрілка вгору)
    F.append(arrow(360, 508, 360, 443, color=POS, sw=2.8))
    F.append(text(360, 528, "Pz", size=13.5, color=POS, bold=True))
    # P_n — на похилу грань (перпендикулярно, всередину)
    F.append(arrow(404, 291, 360, 345, color=POS, sw=2.8))
    F.append(text(416, 284, "Pn", size=13.5, color=POS, bold=True, anchor="start"))
    # вага — донизу від центроїда
    F.append(arrow(322, 360, 322, 428, color=INK, sw=2.6))
    F.append(text(312, 402, "ρg·V", size=12, color=INK, bold=True, anchor="end"))

    # права панель — рівновага по осях
    tb1, _, _ = textbox(815, 150, "рівновага по x:\nPx·Δz = Pn·Δs·sinθ = Pn·Δz\n⟹  Px = Pn",
                        size=13, bold=True, pad=10, fill="#eef4fb", stroke=NEG, color=INK)
    F.append(tb1)
    tb2, _, _ = textbox(815, 305, "рівновага по z:\nPz·Δx = Pn·Δx + ρg·½ΔxΔz\n⟹  Pz = Pn + ½ρg·Δz",
                        size=13, bold=True, pad=10, fill="#eef4fb", stroke=NEG, color=INK)
    F.append(tb2)
    tb3, _, _ = textbox(815, 442, "сили тиску ∝ ℓ²,   вага ∝ ℓ³\nℓ→0:  вага зникає  ⟹  Pz = Pn",
                        size=13, bold=True, pad=10, fill="#fdf3e6", stroke=ORANGE, color=INK)
    F.append(tb3)

    F.append(fitbox(95, 566, 870, 60,
                    "Клин будь-якого нахилу θ дає Px = Pz = Pn: тиск однаковий на всі боки.\n"
                    "Отже тиск — скаляр, приписаний до точки, а не напрямлена величина.",
                    size=13.5, bold=True, fill="#eafaf0", stroke=GREEN, pad=10))

    render(os.path.join(IMG, "wedge-proof.svg"), W, H, *F, title=None)


# ── Фігура (math): стовп рідини — звідки P = P₀ + ρgh ──────────────────────────
def fig_hydro_column():
    W, H = 1040, 600
    F = []
    F.append(text(W / 2, 30, "Стовп над площадкою: P = P₀ + ρ·g·h", size=17, bold=True))

    # бак води
    F.append(rect(150, 120, 280, 350, fill=WATER, stroke=WATERD, sw=1.6, rx=3))
    # виділений стовп до глибини h
    F.append(rect(255, 120, 80, 300, fill=WATERD, stroke=INK, sw=1.6, rx=0))
    F.append(text(305, 438, "площа A", size=11.5, color=INK, bold=True, anchor="start"))
    # вісь глибини
    F.append(arrow(180, 122, 180, 418, color=MUTED, sw=1.6))
    F.append(text(168, 274, "h", size=14, color=MUTED, anchor="end", italic=True))
    # P₀ згори
    F.append(arrow(295, 92, 295, 117, color=INK, sw=2.6))
    F.append(text(295, 82, "P₀·A", size=12.5, color=INK, bold=True))
    # вага стовпа
    F.append(arrow(295, 232, 295, 330, color=POS, sw=2.8))
    F.append(text(346, 286, "вага ρgAh", size=12, color=POS, bold=True, anchor="start"))
    # P(h) знизу
    F.append(arrow(295, 452, 295, 424, color=GREEN, sw=2.8))
    F.append(text(295, 470, "P(h)·A", size=12.5, color=GREEN, bold=True))

    # права панель
    b1, _, _ = textbox(770, 150, "P(h)·A = P₀·A + ρgA·h\n⟹  P(h) = P₀ + ρg·h",
                       size=13.5, bold=True, pad=11, fill="#eafaf0", stroke=GREEN, color=INK)
    F.append(b1)
    b2, _, _ = textbox(770, 292, "тонкий шар:  dP = ρg·dh\nρ = const  ⟹  P лінійно з h",
                       size=13, bold=True, pad=10, fill="#eef4fb", stroke=NEG, color=INK)
    F.append(b2)
    b3, _, _ = textbox(770, 412, "газ: ρ росте з тиском\n⟹  не пряма, а експонента",
                       size=13, bold=True, pad=10, fill="#fdf3e6", stroke=ORANGE, color=INK)
    F.append(b3)

    F.append(fitbox(95, 520, 850, 58,
                    "Тиск на глибині — вага стовпа рідини над одиницею площі. Стала густина дає однаковий\n"
                    "приріст на кожен метр глибини — тому пряма P = P₀ + ρgh.",
                    size=13, bold=True, fill="#f4f6f8", stroke=MUTED, pad=10))

    render(os.path.join(IMG, "hydro-column.svg"), W, H, *F, title=None)


# ── Фігура (math): тензор напружень і де в ньому тиск ──────────────────────────
def fig_stress_tensor():
    W, H = 1080, 650
    F = []
    F.append(text(W / 2, 30, "Тензор напружень: тяга t = σ·n̂ і де в ній тиск",
                  size=17, bold=True))
    F.append(line(540, 62, 540, 336, color="#dfe4ea", sw=1.4, dash="4 6"))

    # ── зліва: загальний стан — тяга не перпендикулярна грані ──
    F.append(text(280, 88, "загальний стан: тяга не ⊥ грані", size=13, bold=True))
    F.append(rect(220, 190, 120, 120, fill=FILL, stroke=INK, sw=1.6))
    F.append(arrow(280, 190, 350, 120, color=POS, sw=2.8))
    F.append(text(358, 114, "t", size=14, color=POS, bold=True, italic=True, anchor="start"))
    F.append(line(280, 190, 280, 120, color=NEG, sw=2.0, dash="5 4"))
    F.append(line(280, 120, 350, 120, color=GREEN, sw=2.0, dash="5 4"))
    F.append(text(272, 158, "σₙₙ", size=12, color=NEG, bold=True, anchor="end"))
    F.append(text(315, 108, "σₙₜ", size=12, color=GREEN, bold=True))
    F.append(text(280, 332, "t = σ·n̂  (нормаль + зсув)", size=12.5, color=INK, bold=True))

    # ── справа: рідина в спокої — σ = −P·I ──
    F.append(text(790, 88, "рідина в спокої: зсуву нема, σ = −P·I", size=13, bold=True))
    F.append(rect(730, 190, 120, 120, fill=WATER, stroke=WATERD, sw=1.6))
    F.append(arrow(790, 150, 790, 188, color=POS, sw=2.6))
    F.append(arrow(790, 350, 790, 312, color=POS, sw=2.6))
    F.append(arrow(686, 250, 728, 250, color=POS, sw=2.6))
    F.append(arrow(894, 250, 852, 250, color=POS, sw=2.6))
    for (lx, ly, an) in [(790, 142, "middle"), (790, 366, "middle"),
                         (676, 254, "end"), (904, 254, "start")]:
        F.append(text(lx, ly, "P", size=12.5, color=POS, bold=True, anchor=an))
    F.append(text(790, 382, "усі нормальні рівні −P, зсув = 0", size=12.5, color=INK, bold=True))

    # ── низ: розклад на ізотропне ядро + девіатор ──
    F.append(line(90, 366, 990, 366, color="#dfe4ea", sw=1.4, dash="4 6"))
    F.append(text(W / 2, 394, "будь-яке напруження = ізотропне ядро (тиск) + девіатор (зсув)",
                  size=13.5, bold=True))

    fb, _, _ = textbox(230, 478, "σ = −P·I + τ\nP = −⅓·tr(σ)\n= −⅓(σxx+σyy+σzz)",
                       size=13, bold=True, pad=11, fill="#ffffff", stroke=INK, color=INK)
    F.append(fb)

    # тайл ізотропного ядра: рівні стрілки всередину
    F.append(rect(520, 440, 72, 72, fill="#fdecea", stroke=POS, sw=1.6))
    cx1, cy1 = 556, 476
    F.append(arrow(cx1, 416, cx1, 438, color=POS, sw=2.2))
    F.append(arrow(cx1, 536, cx1, 514, color=POS, sw=2.2))
    F.append(arrow(498, cy1, 518, cy1, color=POS, sw=2.2))
    F.append(arrow(614, cy1, 594, cy1, color=POS, sw=2.2))
    F.append(text(556, 552, "−P·I", size=12, color=POS, bold=True))
    F.append(text(556, 580, "стискає об'єм", size=11.5, color=MUTED))

    F.append(text(648, 482, "+", size=22, color=INK, bold=True))

    # тайл девіатора: зсувна пара
    F.append(rect(700, 440, 72, 72, fill="#eafaf0", stroke=GREEN, sw=1.6))
    F.append(arrow(706, 434, 766, 434, color=GREEN, sw=2.2))
    F.append(arrow(766, 518, 706, 518, color=GREEN, sw=2.2))
    F.append(text(736, 532, "τ", size=12, color=GREEN, bold=True, italic=True))
    F.append(text(736, 560, "спотворює форму", size=11.5, color=MUTED))

    nb, _, _ = textbox(910, 478, "слід tr(σ)\nне залежить від осей\n⟹ тиск — скаляр",
                       size=12, bold=True, pad=10, fill="#eef4fb", stroke=NEG, color=INK)
    F.append(nb)

    render(os.path.join(IMG, "stress-tensor.svg"), W, H, *F, title=None)


if __name__ == "__main__":
    fig_concentration()
    fig_isotropy()
    fig_hydrostatic()
    fig_hydraulic()
    fig_stevin()
    fig_timeline()
    fig_wedge()
    fig_hydro_column()
    fig_stress_tensor()
    print("OK: 9 SVG ->", IMG)

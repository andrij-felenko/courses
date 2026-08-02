# -*- coding: utf-8 -*-
"""Фігури до теми «Патерни зйомки: полігон, коридор, структура» довідника QGroundControl."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

BAND = "#eef2f6"
SOFT = "#ffffff"
WARM = "#fdf3e7"
COLD = "#eaf0fd"
GOOD = "#eaf7ef"
EDGE = "#c8d2dc"


def poly(pts, fill="none", stroke=LINE, sw=1.8, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, fill, stroke, sw, d))


def pline(pts, stroke=LINE, sw=1.8, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, stroke, sw, d))


# ══════════ 1. Складений елемент і його слід на борту ══════════
def fig_collapse():
    W, H = 1300, 620
    f = [text(W / 2, 36, "Один рядок плану на землі — довгий рівний список на борту", size=17, bold=True)]

    # ── ліворуч: список плану ──
    f.append(rect(40, 76, 470, 460, fill=BAND, stroke=EDGE, sw=1.2, rx=10))
    f.append(text(275, 106, "план у застосунку", size=13, color=MUTED))

    f.append(fitbox(72, 128, 406, 54, "1   Зліт", size=15, fill=SOFT))
    f.append(rect(72, 200, 406, 210, fill=GOOD, stroke=FIELD, sw=2, rx=8))
    f.append(text(275, 234, "2–73   Патерн «Полігон»", size=15, bold=True))
    f.append(mtext(275, 268, [
        "фігура на карті · камера",
        "перекриття · кут галсів",
        "розворотна ділянка",
    ], size=13, color=MUTED, lh=1.35))
    f.append(text(275, 386, "один рядок, 72 номери", size=13, color=FIELD, bold=True))
    f.append(fitbox(72, 428, 406, 54, "74   Посадка", size=15, fill=SOFT))

    # ── стрілка ──
    f.append(arrow(534, 300, 646, 300, color=FIELD, sw=2.6))
    f.append(text(590, 282, "вивантаження", size=13, color=FIELD, bold=True))

    # ── праворуч: місія на борту ──
    f.append(rect(672, 76, 588, 460, fill=BAND, stroke=EDGE, sw=1.2, rx=10))
    f.append(text(966, 106, "місія в пам'яті автопілота", size=13, color=MUTED))

    rows = [
        ("1", "NAV_TAKEOFF", SOFT),
        ("2", "NAV_WAYPOINT   (початок галса)", WARM),
        ("3", "DO_SET_CAM_TRIGG_DIST  14.7 м", WARM),
        ("4", "NAV_WAYPOINT   (кінець галса)", WARM),
        ("5", "DO_SET_CAM_TRIGG_DIST  0", WARM),
        ("…", "ще 68 таких самих елементів", WARM),
        ("74", "NAV_LAND", SOFT),
    ]
    y = 128
    for num, label, fill in rows:
        f.append(rect(700, y, 532, 46, fill=fill, stroke=EDGE, sw=1.2, rx=6))
        f.append(text(724, y + 30, num, size=14, bold=True, anchor="middle"))
        f.append(text(756, y + 30, label, size=14, anchor="start"))
        y += 55

    f.append(fitbox(40, 552, 1220, 46,
                    "На борту немає ні фігури, ні камери, ні перекриття — лише точки й команди",
                    size=15, fill=WARM, bold=True))
    render(os.path.join(OUT, "complex-item-collapse.svg"), W, H, *f)


# ══════════ 2. Від матриці камери до двох відстаней ══════════
def fig_camera():
    W, H = 1340, 740
    f = [text(W / 2, 36, "Дві відстані, з яких виростає весь патерн", size=17, bold=True)]

    # ── ліва панель: вид збоку ──
    f.append(rect(40, 76, 560, 470, fill=BAND, stroke=EDGE, sw=1.2, rx=10))
    f.append(text(320, 106, "вид збоку: висота задає масштаб", size=13, color=MUTED))

    cx = 250.0
    f.append(rect(cx - 34, 150, 68, 30, fill=SOFT, stroke=LINE, sw=1.8, rx=4))
    f.append(text(cx, 171, "камера", size=12))

    gy = 440.0
    f.append(line(80, gy, 470, gy, color=FIELD, sw=3))
    f.append(text(275, gy + 26, "земля", size=13, color=FIELD))

    # промені
    f.append(line(cx, 180, 120, gy, color=NEG, sw=1.6, dash="5 4"))
    f.append(line(cx, 180, 380, gy, color=NEG, sw=1.6, dash="5 4"))
    f.append(line(120, gy, 380, gy, color=NEG, sw=4))

    # висота
    f.append(line(500, 180, 500, gy, color=MUTED, sw=1.4))
    f.append(line(492, 180, 508, 180, color=MUTED, sw=1.4))
    f.append(line(492, gy, 508, gy, color=MUTED, sw=1.4))
    f.append(text(536, 315, "H", size=15, bold=True, color=MUTED))
    f.append(text(536, 338, "висота", size=12, color=MUTED))

    f.append(text(250, gy - 18, "слід кадру на землі", size=13, color=NEG, bold=True))
    f.append(text(120, 232, "матриця s", size=12, color=MUTED, anchor="start"))
    f.append(text(120, 254, "фокусна f", size=12, color=MUTED, anchor="start"))

    f.append(fitbox(70, 470, 500, 58,
                    "роздільність = H · s · 100 / (w · f)     см на піксель",
                    size=14, fill=SOFT))

    # ── права панель: вид згори ──
    f.append(rect(640, 76, 660, 470, fill=BAND, stroke=EDGE, sw=1.2, rx=10))
    f.append(text(970, 106, "вид згори: перекриття ріже слід", size=13, color=MUTED))

    fw, fh = 300.0, 150.0   # слід кадру
    sx, sy = 700.0, 150.0
    stepx = 0.30 * fw       # 70 % повздовжнього перекриття
    stepy = 0.35 * fh       # 65 % поперечного

    for row in range(2):
        for col in range(3):
            x = sx + col * stepx
            y = sy + row * stepy
            f.append(rect(x, y, fw, fh, fill="none", stroke=NEG if row == 0 else POS,
                          sw=1.6, rx=2))

    # крок зйомки
    ay = sy + fh + 74
    f.append(line(sx, ay, sx + stepx, ay, color=NEG, sw=3))
    f.append(line(sx, ay - 8, sx, ay + 8, color=NEG, sw=2))
    f.append(line(sx + stepx, ay - 8, sx + stepx, ay + 8, color=NEG, sw=2))
    f.append(text(sx + stepx + 14, ay + 5, "крок зйомки", size=13, color=NEG,
                  bold=True, anchor="start"))

    # крок між галсами
    axv = sx - 34
    f.append(line(axv, sy, axv, sy + stepy, color=POS, sw=3))
    f.append(line(axv - 8, sy, axv + 8, sy, color=POS, sw=2))
    f.append(line(axv - 8, sy + stepy, axv + 8, sy + stepy, color=POS, sw=2))
    f.append(text(axv - 16, sy + stepy / 2 + 5, "крок", size=13, color=POS,
                  bold=True, anchor="end"))
    f.append(text(axv - 16, sy + stepy / 2 + 24, "між галсами", size=13, color=POS,
                  bold=True, anchor="end"))

    f.append(fitbox(668, 400, 604, 54,
                    "крок між галсами = слід_поперек · (1 − поперечне / 100)",
                    size=14, fill=SOFT, color=POS))
    f.append(fitbox(668, 466, 604, 54,
                    "крок зйомки = слід_уздовж · (1 − повздовжнє / 100)",
                    size=14, fill=SOFT, color=NEG))

    f.append(fitbox(40, 572, 1260, 62,
                    "Уся геометрія патерна — це ці дві відстані, покладені на фігуру, яку намалював користувач",
                    size=15, fill=WARM, bold=True))
    render(os.path.join(OUT, "camera-to-distances.svg"), W, H, *f)


# ══════════ 3. Як полігон перетворюється на галси ══════════
def fig_transects():
    W, H = 1340, 940
    f = [text(W / 2, 36, "Чотири кроки від намальованої фігури до впорядкованих галсів", size=17, bold=True)]

    ang = math.radians(28.0)

    def rot(p, c, a):
        dx, dy = p[0] - c[0], p[1] - c[1]
        return (c[0] + dx * math.cos(a) - dy * math.sin(a),
                c[1] + dx * math.sin(a) + dy * math.cos(a))

    # базовий полігон у «повернутій» системі (панель B/C)
    base = [(-150, -95), (30, -125), (160, -40), (120, 100), (-60, 120), (-160, 30)]

    panels = [
        (60, 76, "A. фігура й кут галсів"),
        (700, 76, "B. поворот і рамка"),
        (60, 480, "C. перетин із контуром"),
        (700, 480, "D. порядок, вхід, розворот"),
    ]
    pw, ph = 580, 348
    for px, py, cap in panels:
        f.append(rect(px, py, pw, ph, fill=BAND, stroke=EDGE, sw=1.2, rx=10))
        f.append(text(px + pw / 2, py + 28, cap, size=14, bold=True))

    # ── A: фігура в геодезичному вигляді + кут ──
    ca = (60 + pw / 2, 76 + ph / 2 + 24)
    ptsA = [rot(p, (0, 0), ang) for p in base]
    ptsA = [(ca[0] + x, ca[1] + y) for x, y in ptsA]
    f.append(poly(ptsA, fill=GOOD, stroke=FIELD, sw=2.2))
    for x, y in ptsA:
        f.append(circle(x, y, 5, fill=SOFT, stroke=FIELD, sw=2))
    # північ
    f.append(arrow(ca[0] - 210, ca[1] + 110, ca[0] - 210, ca[1] - 10, color=MUTED, sw=1.8))
    f.append(text(ca[0] - 210, ca[1] - 24, "Пн", size=13, color=MUTED, bold=True))
    # напрям галсів
    dxa, dya = math.sin(ang) * 96, -math.cos(ang) * 96
    f.append(arrow(ca[0] + 120, ca[1] + 96, ca[0] + 120 + dxa, ca[1] + 96 + dya,
                   color=NEG, sw=2))
    f.append(text(ca[0] + 176, ca[1] + 44, "кут α", size=13, color=NEG, bold=True, anchor="start"))

    # ── B: поворот на −α, рамка, лінії розгортки ──
    cb = (700 + pw / 2, 480 - 404 + ph / 2 + 24)
    cb = (700 + pw / 2, 76 + ph / 2 + 24)
    ptsB = [(cb[0] + x, cb[1] + y) for x, y in base]
    xs = [p[0] for p in ptsB]; ys = [p[1] for p in ptsB]
    bx0, bx1, by0, by1 = min(xs) - 22, max(xs) + 22, min(ys) - 20, max(ys) + 20
    f.append(rect(bx0, by0, bx1 - bx0, by1 - by0, fill="none", stroke=MUTED, sw=1.4, rx=0))
    f.append(poly(ptsB, fill=GOOD, stroke=FIELD, sw=2.2))
    step = 34.0
    yy = by0 + step / 2
    while yy < by1:
        f.append(line(bx0 - 26, yy, bx1 + 26, yy, color=NEG, sw=1.3, dash="6 5"))
        yy += step
    f.append(line(bx1 + 46, by0 + step / 2, bx1 + 46, by0 + step * 1.5, color=POS, sw=3))
    f.append(text(bx1 + 58, by0 + step - 2, "d", size=14, color=POS, bold=True, anchor="start"))
    f.append(text(cb[0], by1 + 48, "рамка з запасом · лінії через d", size=13, color=MUTED))

    # ── C: перетин ──
    cc = (60 + pw / 2, 480 + ph / 2 + 24)
    ptsC = [(cc[0] + x, cc[1] + y) for x, y in base]
    f.append(poly(ptsC, fill=SOFT, stroke=FIELD, sw=2.2))
    xsC = [p[0] for p in ptsC]; ysC = [p[1] for p in ptsC]
    cy0, cy1 = min(ysC), max(ysC)

    def seg_at(y):
        """перетин горизонталі y з опуклим контуром ptsC — крайні точки"""
        hits = []
        n = len(ptsC)
        for i in range(n):
            x1, y1 = ptsC[i]
            x2, y2 = ptsC[(i + 1) % n]
            if (y1 - y) * (y2 - y) < 0:
                t = (y - y1) / (y2 - y1)
                hits.append(x1 + t * (x2 - x1))
        if len(hits) < 2:
            return None
        return min(hits), max(hits)

    yy = cy0 + 14
    while yy < cy1:
        s = seg_at(yy)
        if s:
            f.append(line(s[0], yy, s[1], yy, color=NEG, sw=3))
            f.append(circle(s[0], yy, 3.6, fill=SOFT, stroke=NEG, sw=1.6))
            f.append(circle(s[1], yy, 3.6, fill=SOFT, stroke=NEG, sw=1.6))
        yy += step
    f.append(text(cc[0], cy1 + 60, "від кожної лінії лишається відрізок усередині", size=13, color=MUTED))

    # ── D: порядок, вхід, розворот ──
    cd = (700 + pw / 2, 480 + ph / 2 + 24)
    ptsD = [(cd[0] + x, cd[1] + y) for x, y in base]
    f.append(poly(ptsD, fill=SOFT, stroke=FIELD, sw=1.6, dash="6 5"))
    ysD = [p[1] for p in ptsD]
    dy0, dy1 = min(ysD), max(ysD)

    def seg_atD(y):
        hits = []
        n = len(ptsD)
        for i in range(n):
            x1, y1 = ptsD[i]
            x2, y2 = ptsD[(i + 1) % n]
            if (y1 - y) * (y2 - y) < 0:
                t = (y - y1) / (y2 - y1)
                hits.append(x1 + t * (x2 - x1))
        if len(hits) < 2:
            return None
        return min(hits), max(hits)

    segs = []
    yy = dy0 + 14
    while yy < dy1:
        s = seg_atD(yy)
        if s:
            segs.append((s[0], s[1], yy))
        yy += step

    TURN = 24.0
    path = []
    for i, (a, b, y) in enumerate(segs):
        if i % 2 == 0:
            path.append((a - TURN, y)); path.append((b + TURN, y))
        else:
            path.append((b + TURN, y)); path.append((a - TURN, y))
    f.append(pline(path, stroke=POS, sw=2.4))
    for x, y in path:
        f.append(circle(x, y, 3.4, fill=SOFT, stroke=POS, sw=1.5))
    if path:
        f.append(circle(path[0][0], path[0][1], 8.5, fill=WARM, stroke=POS, sw=2.4))
        f.append(text(path[0][0] - 16, path[0][1] - 16, "вхід", size=13, color=POS,
                      bold=True, anchor="end"))
    f.append(text(cd[0], dy1 + 60, "змійка · кутова точка входу · вихід за межі на розворот",
                  size=13, color=MUTED))

    f.append(fitbox(60, 862, 1220, 50,
                    "Кроки A–C — чиста геометрія в локальних метрах; жодного звернення до мережі тут ще немає",
                    size=15, fill=WARM, bold=True))
    render(os.path.join(OUT, "transect-build.svg"), W, H, *f)


# ══════════ 4. Три патерни: що на вході й куди лягає слід кадру ══════════
def fig_three():
    W, H = 1340, 700
    f = [text(W / 2, 36, "Три патерни — три відповіді на питання «уздовж чого летить камера»",
              size=17, bold=True)]

    cols = [
        (40, "Полігон", GOOD, FIELD),
        (487, "Коридор", COLD, NEG),
        (934, "Структура", WARM, POS),
    ]
    cw, ch = 366, 520
    for x, title_, fill_, stroke_ in cols:
        f.append(rect(x, 76, cw, ch, fill=BAND, stroke=EDGE, sw=1.2, rx=10))
        f.append(text(x + cw / 2, 108, title_, size=16, bold=True, color=stroke_))

    # ── 1. Полігон ──
    x0 = 40
    P = [(x0 + 66, 176), (x0 + 232, 152), (x0 + 306, 246), (x0 + 254, 348), (x0 + 92, 336)]
    f.append(poly(P, fill=GOOD, stroke=FIELD, sw=2))
    yy = 186
    while yy < 336:
        f.append(line(x0 + 78, yy, x0 + 284, yy, color=FIELD, sw=2.2))
        yy += 26
    f.append(fitbox(x0 + 26, 380, 314, 52, "на вході: замкнена фігура", size=14, fill=SOFT))
    f.append(fitbox(x0 + 26, 444, 314, 52, "слід_поперек → крок між галсами", size=13, fill=SOFT))
    f.append(fitbox(x0 + 26, 508, 314, 52, "слід_уздовж → крок зйомки", size=13, fill=SOFT))

    # ── 2. Коридор ──
    x1 = 487
    axis = [(x1 + 60, 330), (x1 + 140, 210), (x1 + 240, 262), (x1 + 316, 168)]
    f.append(pline(axis, stroke=MUTED, sw=2.4, dash="7 5"))
    for off, col in ((-26, NEG), (0, NEG), (26, NEG)):
        f.append(pline([(px, py + off) for px, py in axis], stroke=col, sw=2.2))
    f.append(line(x1 + 60, 304, x1 + 60, 356, color=POS, sw=3))
    f.append(text(x1 + 46, 334, "ширина", size=13, color=POS, bold=True, anchor="end"))
    f.append(fitbox(x1 + 26, 380, 314, 52, "на вході: ламана й ширина", size=14, fill=SOFT))
    f.append(fitbox(x1 + 26, 444, 314, 52, "ширина ÷ крок → кількість галсів", size=13, fill=SOFT))
    f.append(fitbox(x1 + 26, 508, 314, 52, "галси — зсуви ламаної вбік", size=13, fill=SOFT))

    # ── 3. Структура ──
    x2 = 934
    f.append(rect(x2 + 148, 152, 78, 200, fill="#e8e4de", stroke=LINE, sw=1.8, rx=2))
    f.append(text(x2 + 187, 372, "споруда", size=13, color=MUTED))
    for k, yv in enumerate((186, 240, 294)):
        f.append('<ellipse cx="%.1f" cy="%.1f" rx="88" ry="17" fill="none" stroke="%s" '
                 'stroke-width="2.2"/>' % (x2 + 187, yv, POS))
    f.append(line(x2 + 300, 186, x2 + 300, 294, color=NEG, sw=2.4))
    f.append(line(x2 + 292, 186, x2 + 308, 186, color=NEG, sw=2))
    f.append(line(x2 + 292, 294, x2 + 308, 294, color=NEG, sw=2))
    f.append(text(x2 + 316, 244, "шари", size=13, color=NEG, bold=True, anchor="start"))
    f.append(fitbox(x2 + 26, 380, 314, 52, "на вході: основа й висота", size=14, fill=SOFT))
    f.append(fitbox(x2 + 26, 444, 314, 52, "слід_уздовж → крок по висоті", size=13, fill=SOFT))
    f.append(fitbox(x2 + 26, 508, 314, 52, "слід_поперек → крок зйомки", size=13, fill=SOFT))

    f.append(fitbox(40, 626, 1260, 50,
                    "У структурі камера дивиться вбік — і сторони сліду міняються місцями",
                    size=15, fill=WARM, bold=True))
    render(os.path.join(OUT, "three-patterns.svg"), W, H, *f)


# ══════════ 5. Потік елементів місії вздовж одного галса ══════════
def fig_item_stream():
    W, H = 1420, 620
    f = [text(W / 2, 36, "Що QGroundControl видає на один галс: шість точок — вісім елементів місії",
              size=17, bold=True)]

    # ── геометрія галса ──
    px = [110.0, 368.75, 627.5, 800.0, 1058.75, 1317.5]
    ylin = 150.0
    f.append(line(px[0], ylin, px[1], ylin, color=MUTED, sw=2.2, dash="7 5"))
    f.append(line(px[1], ylin, px[4], ylin, color=INK, sw=3.0))
    f.append(line(px[4], ylin, px[5], ylin, color=MUTED, sw=2.2, dash="7 5"))

    caps = ["розворот", "початок галса", "внутрішня", "внутрішня", "кінець галса", "розворот"]
    for i, x in enumerate(px):
        hot = i in (1, 4)
        f.append(circle(x, ylin, 9 if hot else 6.5,
                        fill="#ffffff", stroke=POS if hot else INK, sw=2.6 if hot else 2.0))
        f.append(text(x, ylin - 24, caps[i], size=13, color=POS if hot else MUTED,
                      bold=hot))

    f.append(text(px[2] + 86, ylin + 30, "спуск працює тут", size=13, color=POS))

    # ── ряд елементів місії ──
    BOXW, BOXH, BOXY = 160.0, 104.0, 268.0
    items = [
        # (центр, підпис, параметри, кадр, навігаційна?, індекс точки)
        ("NAV_WAYPOINT", "hold 0 · yaw NaN", "GLOBAL_RELATIVE_ALT", True, 0),
        ("CONDITION_GATE", "0 · 1 → площина", "GLOBAL_RELATIVE_ALT", True, 1),
        ("DO_SET_CAM_TRIGG_DIST", "14.7 · 0 · 1", "MISSION", False, 1),
        ("NAV_WAYPOINT", "hold 0 · yaw NaN", "GLOBAL_RELATIVE_ALT", True, 2),
        ("NAV_WAYPOINT", "hold 0 · yaw NaN", "GLOBAL_RELATIVE_ALT", True, 3),
        ("CONDITION_GATE", "0 · 1 → площина", "GLOBAL_RELATIVE_ALT", True, 4),
        ("DO_SET_CAM_TRIGG_DIST", "0 · 0 · 1", "MISSION", False, 4),
        ("NAV_WAYPOINT", "hold 0 · yaw NaN", "GLOBAL_RELATIVE_ALT", True, 5),
    ]
    cxs = [110.0 + i * 172.5 for i in range(len(items))]

    # виноски від точок геометрії до рамок
    for cx, (_, _, _, _, ip) in zip(cxs, items):
        f.append(line(px[ip], ylin + 12, px[ip], 214, color=EDGE, sw=1.4, dash="4 4"))
        f.append(line(px[ip], 214, cx, BOXY - 10, color=EDGE, sw=1.4, dash="4 4"))

    for i, (cx, (name, prm, frm, nav, _)) in enumerate(zip(cxs, items)):
        x = cx - BOXW / 2
        f.append(rect(x, BOXY, BOXW, BOXH,
                      fill=COLD if nav else WARM,
                      stroke=NEG if nav else POS, sw=1.8, rx=8))
        f.append(text(cx, BOXY + 26, "№ + %d" % i, size=11, color=MUTED, bold=True))
        f.append(text(cx, BOXY + 50, name, size=fit_font(name, BOXW - 18, 12, True),
                      color=INK, bold=True))
        f.append(text(cx, BOXY + 72, prm, size=fit_font(prm, BOXW - 18, 10), color=MUTED))
        f.append(text(cx, BOXY + 93, frm, size=fit_font(frm, BOXW - 18, 10), color=NEG if nav else POS))

    f.append(text(W / 2, BOXY + BOXH + 34,
                  "порядок у списку — зліва направо, наскрізним лічильником від номера самого патерна",
                  size=13, color=MUTED))

    # ── легенда ──
    f.append(rect(110, 452, 22, 22, fill=COLD, stroke=NEG, sw=1.8, rx=4))
    f.append(text(144, 468, "має координати, змінює траєкторію — кадр польоту",
                  size=13, anchor="start"))
    f.append(rect(760, 452, 22, 22, fill=WARM, stroke=POS, sw=1.8, rx=4))
    f.append(text(794, 468, "координат не має, виконується миттєво — MAV_FRAME_MISSION",
                  size=13, anchor="start"))

    f.append(fitbox(110, 508, 1200, 62,
                    "Вимкнути ворота — і замість CONDITION_GATE стане NAV_WAYPOINT: та сама точка, "
                    "але зі сферою прийняття й гальмуванням перед нею",
                    size=14, fill=SOFT, bold=True))
    render(os.path.join(OUT, "item-stream.svg"), W, H, *f)


# ══════════ Подібні трикутники: звідки береться H·s/f ══════════
def fig_gsd():
    W, H = 1300, 700
    f = [text(W / 2, 36, "Роздільність на місцевості з подібних трикутників камери-обскури",
              size=18, bold=True)]

    ox, oy = 400.0, 250.0        # отвір
    ys, yg = 180.0, 550.0        # площина матриці / земля
    fpx = oy - ys
    Hpx = yg - oy
    sh = 44.0                    # пів-ширина матриці на рисунку
    gh = sh * Hpx / fpx          # пів-слід на землі

    f.append(line(150, yg, 660, yg, color=LINE, sw=2.6))
    f.append(text(600, yg + 24, "земля", size=13, color=MUTED, anchor="start"))

    f.append(line(ox - sh, ys, ox + sh, ys, color=NEG, sw=5))
    f.append(text(ox, ys - 20, "матриця:  s = 23.5 мм,  w = 6000 пікс", size=13, color=NEG))

    f.append(line(ox - sh, ys, ox + gh, yg, color=POS, sw=1.6))
    f.append(line(ox + sh, ys, ox - gh, yg, color=POS, sw=1.6))
    f.append(line(ox, ys, ox, yg, color=MUTED, sw=1.2, dash="5,5"))
    f.append(circle(ox, oy, 6, fill=BG, stroke=INK, sw=2.2))
    f.append(text(ox + 16, oy - 10, "отвір", size=13, anchor="start"))

    # розмір f
    f.append(line(300, ys, 300, oy, color=MUTED, sw=1.4))
    for yy in (ys, oy):
        f.append(line(294, yy, 306, yy, color=MUTED, sw=1.4))
    f.append(text(292, (ys + oy) / 2 + 5, "f = 16 мм", size=14, color=MUTED, anchor="end"))

    # розмір H
    f.append(line(200, oy, 200, yg, color=MUTED, sw=1.4))
    for yy in (oy, yg):
        f.append(line(194, yy, 206, yy, color=MUTED, sw=1.4))
    f.append(text(192, (oy + yg) / 2 + 5, "H = 60 м", size=14, color=MUTED, anchor="end"))

    # розмір сліду
    f.append(line(ox - gh, 585, ox + gh, 585, color=FIELD, sw=1.8))
    for xx in (ox - gh, ox + gh):
        f.append(line(xx, 579, xx, 591, color=FIELD, sw=1.8))
    f.append(text(ox, 612, "слід кадру = H · s / f = 88.1 м", size=15, color=FIELD, bold=True))
    f.append(text(ox, 646, "зображення на матриці перевернуте — на пропорцію це не впливає",
                  size=13, color=MUTED))

    # ── алгебра праворуч ──
    f.append(fitbox(730, 88, 540, 104,
                    "подібні трикутники:   (s/2) / f = (слід/2) / H\n"
                    "звідси   слід = H · s / f",
                    size=16, fill=COLD))
    f.append(fitbox(730, 214, 540, 104,
                    "піксель:  p = s / w = 3.917 мкм\n"
                    "роздільність:  g = H · p / f = H · s / (w · f)",
                    size=16, fill=SOFT))
    f.append(fitbox(730, 340, 258, 152,
                    "висота → роздільність\n\ng = H·s·100 / (w·f)\n\n60 м → 1.469 см/пікс",
                    size=14, fill=GOOD))
    f.append(fitbox(1012, 340, 258, 152,
                    "роздільність → висота\n\nH = g·w·f / (s·100)\n\n2.00 см/пікс → 81.7 м",
                    size=14, fill=GOOD))
    f.append(fitbox(730, 514, 540, 104,
                    "висота матриці в цю арифметику не входить узагалі:\n"
                    "пікселі квадратні, тож p = s/w — те саме по обох сторонах",
                    size=14, fill=WARM, bold=True))
    render(os.path.join(OUT, "gsd-triangles.svg"), W, H, *f)


# ══════════ Три показники степеня: чутливість до висоти ══════════
def fig_scaling():
    W, H = 1240, 670
    x0, x1, y0, y1 = 130.0, 1090.0, 100.0, 520.0
    hmin, hmax, vmax = 30.0, 130.0, 4.5
    fx = lambda hm: x0 + (hm - hmin) / (hmax - hmin) * (x1 - x0)
    fy = lambda v: y1 - v / vmax * (y1 - y0)

    f = [text(W / 2, 36, "Як висота розтягує весь патерн: три показники степеня",
              size=18, bold=True)]

    for v in range(0, 5):
        f.append(line(x0, fy(v), x1, fy(v), color=EDGE, sw=1.2))
        f.append(text(x0 - 14, fy(v) + 5, "%d×" % v, size=13, color=MUTED, anchor="end"))
    for hm in (30, 50, 70, 90, 110, 130):
        f.append(line(fx(hm), y0, fx(hm), y1, color=EDGE, sw=1.0))
        f.append(text(fx(hm), y1 + 26, "%d" % hm, size=13, color=MUTED))
    f.append(line(fx(60), y0, fx(60), y1, color=MUTED, sw=1.6, dash="6,5"))
    f.append(text(fx(60), y1 + 26, "60", size=13, color=INK, bold=True))
    f.append(line(x0, y1, x1, y1, color=LINE, sw=2))
    f.append(line(x0, y0, x0, y1, color=LINE, sw=2))
    f.append(text(x0, y0 - 16, "кратність до опорної висоти 60 м", size=14,
                  color=MUTED, anchor="start"))
    f.append(text((x0 + x1) / 2, y1 + 56, "висота польоту H, м", size=15, bold=True))

    def curve(fn, color):
        pts = []
        hm = hmin
        while hm <= hmax + 0.01:
            v = fn(hm)
            if v <= vmax:
                pts.append((fx(hm), fy(v)))
            hm += 0.5
        return pline(pts, stroke=color, sw=3.0)

    f.append(curve(lambda hm: (60.0 / hm) ** 2, POS))
    f.append(curve(lambda hm: 60.0 / hm, NEG))
    f.append(curve(lambda hm: hm / 60.0, FIELD))

    f.append(rect(752, 118, 330, 138, fill=SOFT, stroke=EDGE, sw=1.2, rx=8))
    for i, (color, label) in enumerate(((POS, "кадрів   ∝ 1/H²"),
                                        (NEG, "шлях і час   ∝ 1/H"),
                                        (FIELD, "інтервал спусків   ∝ H"))):
        yy = 152 + i * 40
        f.append(line(772, yy, 812, yy, color=color, sw=3.4))
        f.append(text(826, yy + 5, label, size=15, anchor="start"))

    for i, (hm, txt) in enumerate(((40, "738 кадрів · 12.5 хв · 0.98 с"),
                                   (80, "189 кадрів · 6.5 хв · 1.96 с"),
                                   (120, "84 кадри · 4.4 хв · 2.94 с"))):
        f.append(fitbox(130 + i * 340, 588, 300, 62,
                        "H = %d м\n%s" % (hm, txt), size=14, fill=BAND))
    render(os.path.join(OUT, "altitude-scaling.svg"), W, H, *f)


# ══════════ Ландшафт ↔ портрет над тим самим полем ══════════
def fig_orientation():
    W, H = 1300, 810
    f = [text(W / 2, 36, "Поворот камери на 90°: те саме поле, стільки ж кадрів, інший політ",
              size=18, bold=True)]

    def panel(x0, head, fw, fh, step, n_tr, foot_w, foot_h, stats):
        g = [text(x0 + 200, 78, head, size=17, bold=True, color=NEG)]
        g.append(rect(x0 + 40, 100, foot_w, foot_h, fill=COLD, stroke=NEG, sw=2, rx=3))
        g.append(text(x0 + 40 + foot_w / 2, 100 + foot_h / 2 + 5, "кадр", size=14, color=NEG))
        g.append(text(x0 + 40 + foot_w / 2, 100 + foot_h + 22, "%.1f м" % foot_w,
                      size=13, color=MUTED))
        g.append(text(x0 + 32, 100 + foot_h / 2 + 5, "%.1f м" % foot_h, size=13,
                      color=MUTED, anchor="end"))
        g.append(arrow(x0 + 250, 152, x0 + 366, 152, color=FIELD, sw=2.4))
        g.append(text(x0 + 308, 136, "напрямок польоту", size=12, color=FIELD))
        fy0 = 250.0
        g.append(rect(x0, fy0, fw, fh, fill=BAND, stroke=EDGE, sw=1.6, rx=4))
        for k in range(n_tr):
            yy = fy0 + k * step
            g.append(line(x0, yy, x0 + fw, yy, color=POS, sw=1.6))
        g.append(text(x0 + fw / 2, fy0 + fh + 24, "400 м", size=13, color=MUTED))
        g.append(text(x0 - 12, fy0 + fh / 2 + 5, "300 м", size=13, color=MUTED, anchor="end"))
        g.append(fitbox(x0, 600, fw, 132, stats, size=14, fill=SOFT))
        return g

    f += panel(120, "ЛАНДШАФТ", 400, 300, 26.4375, 12, 88.125, 58.75,
               "крок між галсами 26.44 м · крок зйомки 14.69 м\n"
               "галсів 12 · кадрів 336\n"
               "шлях 5091 м · час на галсах 8 хв 29 с\n"
               "інтервал між спусками 1.47 с")
    f += panel(780, "ПОРТРЕТ", 400, 300, 17.625, 18, 58.75, 88.125,
               "крок між галсами 17.63 м · крок зйомки 22.03 м\n"
               "галсів 18 · кадрів 342\n"
               "шлях 7500 м · час на галсах 12 хв 30 с\n"
               "інтервал між спусками 2.20 с")

    f.append(fitbox(120, 752, 1060, 46,
                    "Кадрів майже стільки само; шлях і інтервал — обидва рівно в w/h = 1.5 раза більші",
                    size=15, fill=WARM, bold=True))
    render(os.path.join(OUT, "orientation-swap.svg"), W, H, *f)


# ══════════ Невипуклий контур: дві найдальші проти пар по черзі ══════════
def fig_concave():
    W, H = 1260, 700
    f = [text(W / 2, 38, "Чотири перетини на одному рівні — і два різні способи їх прочитати",
              size=17, bold=True)]

    S = 2.15                      # пікселів на метр
    ORY = 452.0                   # низ поля в координатах SVG
    LINES = [20.34, 46.78, 73.22, 99.66]
    NLO, NHI, NBOT = 80.0, 120.0, 30.0

    def panel(px, cap, split):
        g = [rect(px, 84, 560, 424, fill=BAND, stroke=EDGE, sw=1.2, rx=10),
             text(px + 280, 116, cap, size=15, bold=True)]
        orx = px + 62.0

        def P(mx, my):
            return (orx + mx * S, ORY - my * S)

        verts = [(0, 0), (200, 0), (200, 120), (NHI, 120),
                 (NHI, NBOT), (NLO, NBOT), (NLO, 120), (0, 120)]
        g.append(poly([P(*v) for v in verts], fill=GOOD, stroke=FIELD, sw=2.2))

        bx, by = P(NLO, 120)
        g.append(rect(bx, by, (NHI - NLO) * S, (120 - NBOT) * S,
                      fill=SOFT, stroke=EDGE, sw=1.2, rx=0))
        g.append(text(orx + 100 * S, ORY - 12 * S, "затока", size=12, color=MUTED))

        for yv in LINES:
            g.append(line(orx - 32, ORY - yv * S, orx + 200 * S + 32, ORY - yv * S,
                          color=MUTED, sw=1.0, dash="5 5"))

        for yv in LINES:
            if yv < NBOT:
                g.append(line(*P(0, yv), *P(200, yv), color=NEG, sw=4))
                continue
            g.append(line(*P(0, yv), *P(NLO, yv), color=NEG, sw=4))
            g.append(line(*P(NHI, yv), *P(200, yv), color=NEG, sw=4))
            if not split:
                g.append(line(*P(NLO, yv), *P(NHI, yv), color=POS, sw=4))

        top = LINES[-1]
        for mx, lab in ((0.0, "0"), (NLO, "80"), (NHI, "120"), (200.0, "200")):
            cxp, cyp = P(mx, top)
            g.append(circle(cxp, cyp, 4.6, fill=SOFT, stroke=LINE, sw=1.8))
            g.append(text(cxp, cyp - 16, lab, size=12, color=MUTED, bold=True))
        return g

    f += panel(40, "правило «дві найдальші»", split=False)
    f += panel(660, "правило «пари по черзі»", split=True)

    f.append(fitbox(40, 528, 560, 62, "4 галси · 800 м покриття · 120 м над водою",
                    size=15, fill=WARM, bold=True, color=POS))
    f.append(fitbox(660, 528, 560, 62, "7 галсів · 680 м покриття · 0 м над водою",
                    size=15, fill=GOOD, bold=True, color=FIELD))
    f.append(fitbox(40, 612, 1180, 56,
                    "Ціна правильного покриття — не саме покриття, а порядок: сім уривків треба ще скласти в маршрут",
                    size=15, fill=SOFT))
    render(os.path.join(OUT, "transect-concave-trap.svg"), W, H, *f)


fig_collapse()
fig_camera()
fig_transects()
fig_three()
fig_item_stream()
fig_gsd()
fig_scaling()
fig_orientation()
fig_concave()
print("ok")

# -*- coding: utf-8 -*-
"""Фігури до теми «Виштовхувальна сила (закон Архімеда)».
Запуск із теки теми:  python figs.py   → SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

WATER  = "#bfe0f2"
WATERD = "#7cc0e0"
STEEL  = "#c4c9d2"
STEELD = "#8b9099"
CORK   = "#e6cd93"
CORKD  = "#c9a860"
WOOD   = "#d8b98c"
WOODD  = "#b58a52"
ICE    = "#e6f3fb"
ICED   = "#a9d0e8"
SKY    = "#f2f8fc"
DOT    = "#5b9bd0"
GREEN  = FIELD


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


def polygon(pts, fill=WATER, stroke="none", sw=0):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" '
            'stroke-width="%.1f"/>' % (p, fill, stroke, sw))


def waves(x1, x2, y, color=WATERD, sw=1.8, step=26, amp=4):
    """Легка хвиляста лінія поверхні води."""
    pts = []
    n = int((x2 - x1) / step) + 1
    for i in range(n + 1):
        xx = x1 + i * step
        yy = y + (amp if i % 2 else -amp)
        pts.append((xx, yy))
    return polyline(pts, color=color, sw=sw)


# ── Фігура 1: звідки береться поштовх — різниця тиску верх/низ ─────────────────
def fig_origin():
    W, H = 1080, 620
    F = []

    # бак води
    tx0, tx1, tty, tby = 150, 470, 118, 512
    F.append(rect(tx0, tty, tx1 - tx0, tby - tty, fill=WATER, stroke=WATERD, sw=1.6, rx=4))
    F.append(waves(tx0 + 6, tx1 - 6, tty, sw=2.0))
    # молекулярна фактура
    for i in range(30):
        xx = tx0 + 18 + (tx1 - tx0 - 36) * ((i * 0.61803) % 1.0)
        yy = tty + 22 + (tby - tty - 44) * ((i * 0.37294) % 1.0)
        F.append(circle(xx, yy, 1.8, fill=DOT, stroke="none", sw=0))

    # брусок, занурений у товщу
    bx0, bx1 = 250, 372
    btop, bbot = 224, 360
    bcx = (bx0 + bx1) / 2
    F.append(rect(bx0, btop, bx1 - bx0, bbot - btop, fill=STEEL, stroke=STEELD, sw=1.8, rx=3))
    F.append(text(bcx, (btop + bbot) / 2 + 5, "V", size=16, color=INK, bold=True, italic=True))
    F.append(text(bcx, btop - 46, "площа основи A", size=11.5, color=MUTED))

    # вісь глибини ліворуч
    ax = 120
    F.append(arrow(ax, tty, ax, tby, color=MUTED, sw=1.6))
    F.append(text(ax - 8, tty + 14, "h", size=13, color=MUTED, anchor="end", italic=True))
    F.append(line(ax, btop, bx0, btop, color=MUTED, sw=1.2, dash="4 4"))
    F.append(line(ax, bbot, bx0, bbot, color=MUTED, sw=1.2, dash="4 4"))
    F.append(text(ax + 6, btop - 6, "h₁", size=12.5, color=MUTED, anchor="start", bold=True))
    F.append(text(ax + 6, bbot + 16, "h₂", size=12.5, color=MUTED, anchor="start", bold=True))

    # тиск згори — короткі стрілки вниз на верхню грань
    for x in (bx0 + 26, bcx, bx1 - 26):
        F.append(arrow(x, btop - 30, x, btop, color=NEG, sw=2.2))
    F.append(text(bcx, btop - 40, "P₁ — менший", size=12, color=NEG, bold=True))

    # тиск знизу — довгі стрілки вгору на нижню грань
    for x in (bx0 + 26, bcx, bx1 - 26):
        F.append(arrow(x, bbot + 58, x, bbot, color=POS, sw=2.6))
    F.append(text(bcx, bbot + 76, "P₂ — більший (глибше)", size=12, color=POS, bold=True))

    # бічні стрілки — однакові, гасяться
    for y in (btop + 40, (btop + bbot) / 2, bbot - 40):
        F.append(arrow(bx0 - 30, y, bx0, y, color=MUTED, sw=2.0))
        F.append(arrow(bx1 + 30, y, bx1, y, color=MUTED, sw=2.0))
    F.append(text(bx1 + 40, (btop + bbot) / 2 - 40, "бічні", size=11, color=MUTED, anchor="start"))
    F.append(text(bx1 + 40, (btop + bbot) / 2 - 26, "рівні —", size=11, color=MUTED, anchor="start"))
    F.append(text(bx1 + 40, (btop + bbot) / 2 - 12, "гасяться", size=11, color=MUTED, anchor="start"))

    # рівнодійна поштовху — велика зелена стрілка вгору
    F.append(arrow(bcx, btop - 78, bcx, btop - 116, color=GREEN, sw=3.6))
    F.append(text(bcx, btop - 126, "F_арх угору", size=13, color=GREEN, bold=True))

    # ── права панель: висновок ──
    b1, _, _ = textbox(790, 168,
                       "P₂ = ρ·g·h₂   (нижня грань глибша)\n"
                       "P₁ = ρ·g·h₁   (верхня грань вища)",
                       size=13, bold=True, pad=11, fill="#eef4fb", stroke=NEG, color=INK)
    F.append(b1)
    b2, _, _ = textbox(790, 322,
                       "F = (P₂ − P₁)·A = ρ·g·(h₂−h₁)·A\n"
                       "= ρ·g·h·A = ρ_рідини · g · V",
                       size=13, bold=True, pad=11, fill="#eafaf0", stroke=GREEN, color=INK)
    F.append(b2)

    F.append(fitbox(150, 548, 800, 52,
                    "Тиск росте вглиб, тож знизу давить дужче, ніж згори. Непогашена різниця й штовхає тіло вгору —\n"
                    "і дорівнює ρ·g·V, у ній немає ні ваги тіла, ні його матеріалу, лише об'єм і густина рідини.",
                    size=12.5, bold=True, fill="#f4f6f8", stroke=MUTED, pad=10))

    render(os.path.join(IMG, "origin.svg"), W, H, *F,
           title="Виштовхування — це різниця тиску між дном і верхом тіла")


# ── Фігура 2: закон Архімеда — вага витісненої рідини (аргумент двійника) ──────
def fig_displaced():
    W, H = 1080, 600
    F = []
    F.append(line(W / 2, 92, W / 2, 470, color="#dfe4ea", sw=1.4, dash="4 6"))

    # ── ліва панель: реальне тіло (сталь) у воді ──
    lx0, lx1, wty, wby = 110, 460, 128, 452
    F.append(rect(lx0, wty, lx1 - lx0, wby - wty, fill=WATER, stroke=WATERD, sw=1.6, rx=4))
    F.append(waves(lx0 + 6, lx1 - 6, wty, sw=1.8))
    F.append(text((lx0 + lx1) / 2, wty - 16, "реальне тіло — сталь", size=13.5, bold=True))
    ocx = (lx0 + lx1) / 2
    F.append(rect(ocx - 62, 250, 124, 96, fill=STEEL, stroke=STEELD, sw=1.8, rx=4))
    F.append(text(ocx, 304, "сталь", size=13, color=INK, bold=True))
    F.append(arrow(ocx, 250, ocx, 190, color=GREEN, sw=3.4))
    F.append(text(ocx, 178, "F_арх угору", size=12.5, color=GREEN, bold=True))
    F.append(text((lx0 + lx1) / 2, wby + 24, "= вазі витісненої води", size=12.5, color=GREEN, bold=True))

    # ── права панель: рідина-двійник тієї самої форми ──
    rx0, rx1 = 620, 970
    F.append(rect(rx0, wty, rx1 - rx0, wby - wty, fill=WATER, stroke=WATERD, sw=1.6, rx=4))
    F.append(waves(rx0 + 6, rx1 - 6, wty, sw=1.8))
    F.append(text((rx0 + rx1) / 2, wty - 16, "уявний двійник — та сама вода", size=13.5, bold=True))
    dcx = (rx0 + rx1) / 2
    # контур двійника (пунктир), заповнений тією ж водою (трохи темніше)
    F.append(rect(dcx - 62, 250, 124, 96, fill=WATERD, stroke=NEG, sw=2.0, rx=4))
    F.append(text(dcx, 304, "вода", size=13, color=INK, bold=True))
    # рівновага: вага вниз = поштовх угору
    F.append(arrow(dcx - 34, 250, dcx - 34, 196, color=GREEN, sw=3.0))
    F.append(text(dcx - 34, 184, "поштовх", size=11.5, color=GREEN, bold=True))
    F.append(arrow(dcx + 34, 346, dcx + 34, 400, color=POS, sw=3.0))
    F.append(text(dcx + 34, 418, "вага води", size=11.5, color=POS, bold=True))
    F.append(text((rx0 + rx1) / 2, wby + 24, "висить у рівновазі → поштовх = її вага", size=12, color=INK, bold=True))

    F.append(fitbox(95, 496, 890, 78,
                    "Заміни тіло на воду тієї самої форми — вона висить у спокої, отже сили тиску тримають рівно її вагу.\n"
                    "Навколишня рідина тисне на межу однаково, хоч там вода, хоч сталь, хоч корок — тож поштовх той самий:\n"
                    "вага витісненої рідини. Форма тіла врахована сама, бо ми взяли порожнину саме його обрису.",
                    size=13, bold=True, fill="#eafaf0", stroke=GREEN, pad=11))

    render(os.path.join(IMG, "displaced.svg"), W, H, *F,
           title="Закон Архімеда: поштовх дорівнює вазі витісненої рідини")


# ── Фігура 3: спливе / зависне / потоне — вирішує порівняння густин ────────────
def fig_float_sink():
    W, H = 1120, 664
    F = []

    # бак: обвід + вода нижче ватерлінії
    tx0, tx1 = 90, 1030
    ttop, wl, tby = 104, 168, 520
    F.append(rect(tx0, ttop, tx1 - tx0, tby - ttop, fill=SKY, stroke=WATERD, sw=1.6, rx=4))
    F.append(rect(tx0 + 2, wl, tx1 - tx0 - 4, tby - wl - 2, fill=WATER, stroke="none", rx=0))
    F.append(waves(tx0 + 8, tx1 - 8, wl, sw=2.0))
    F.append(text(tx1 - 6, wl - 8, "поверхня води", size=11, color=WATERD, anchor="end", bold=True))

    # ── корок: спливає, сидить на поверхні ──
    cx = 250
    F.append(rect(cx - 46, wl - 34, 92, 60, fill=CORK, stroke=CORKD, sw=1.8, rx=5))  # верх над водою
    F.append(text(cx, wl - 2, "корок", size=12.5, color=INK, bold=True))
    F.append(arrow(cx, wl - 60, cx, wl - 92, color=GREEN, sw=2.6))
    F.append(arrow(cx, wl + 66, cx, wl + 40, color=POS, sw=2.6))
    F.append(text(cx, wl - 102, "виштовхування", size=10.5, color=GREEN, bold=True))
    F.append(text(cx, wl + 82, "вага", size=10.5, color=POS, bold=True))

    # ── нейтральне тіло: зависає в товщі ──
    nx = 560
    ntop = 300
    F.append(rect(nx - 46, ntop, 92, 74, fill=WOOD, stroke=WOODD, sw=1.8, rx=5))
    F.append(text(nx, ntop + 42, "просочене", size=11, color=INK, bold=True))
    F.append(arrow(nx, ntop, nx, ntop - 44, color=GREEN, sw=2.6))
    F.append(arrow(nx, ntop + 74 + 44, nx, ntop + 74, color=POS, sw=2.6))
    F.append(text(nx, ntop - 54, "поштовх", size=10.5, color=GREEN, bold=True))
    F.append(text(nx, ntop + 74 + 60, "вага", size=10.5, color=POS, bold=True))
    F.append(text(nx + 74, ntop + 40, "рівні", size=11, color=MUTED, anchor="start", bold=True))

    # ── сталь: тоне на дно ──
    sx = 860
    sbot = tby - 8
    F.append(rect(sx - 44, sbot - 66, 88, 66, fill=STEEL, stroke=STEELD, sw=1.8, rx=4))
    F.append(text(sx, sbot - 30, "сталь", size=12.5, color=INK, bold=True))
    F.append(arrow(sx, sbot - 66, sx, sbot - 66 - 30, color=GREEN, sw=2.4))
    F.append(arrow(sx, sbot - 66 - 96, sx, sbot - 66 - 132, color=POS, sw=3.0))
    F.append(text(sx, sbot - 66 - 40, "малий поштовх", size=10.5, color=GREEN, bold=True))
    F.append(text(sx, sbot - 66 - 142, "більша вага", size=10.5, color=POS, bold=True))
    # дно
    F.append(line(tx0 + 2, tby, tx1 - 2, tby, color=STEELD, sw=3.0))

    # ── вироки під баком ──
    verdicts = [
        (cx, "ρ_тіла < ρ_води\nспливає", GREEN),
        (nx, "ρ_тіла = ρ_води\nзависає", NEG),
        (sx, "ρ_тіла > ρ_води\nтоне", POS),
    ]
    for vx, s, col in verdicts:
        tb, _, _ = textbox(vx, 558, s, size=12.5, bold=True, pad=9,
                           fill="#ffffff", stroke=col, color=col)
        F.append(tb)

    F.append(fitbox(140, 600, 840, 48,
                    "Ні вага, ні матеріал самі по собі не вирішують — лише відношення густин. Тому й сталевий\n"
                    "корабель плаває: усередині повітря, і середня густина всього корпусу виходить меншою за воду.",
                    size=12.5, bold=True, fill="#f4f6f8", stroke=MUTED, pad=10))

    render(os.path.join(IMG, "float-sink.svg"), W, H, *F,
           title="Спливе, зависне чи потоне — вирішує лише порівняння густин")


# ── Фігура 4: айсберг — частка занурення = відношення густин ───────────────────
def fig_iceberg():
    W, H = 1040, 620
    F = []

    # небо / море
    sea_top = 258
    F.append(rect(60, 96, W - 120, sea_top - 96, fill=SKY, stroke="none", rx=0))
    F.append(rect(60, sea_top, W - 120, 470 - sea_top, fill=WATER, stroke="none", rx=0))
    F.append(rect(60, 96, W - 120, 470 - 96, fill="none", stroke=WATERD, sw=1.6, rx=4))
    F.append(waves(72, W - 72, sea_top, sw=2.2))
    F.append(text(W - 74, sea_top - 10, "рівень моря", size=11.5, color=WATERD, anchor="end", bold=True))

    cx = 360
    # надводна верхівка (мала, ≈10 %)
    tip = [(cx - 46, sea_top), (cx - 20, sea_top - 52), (cx + 14, sea_top - 40),
           (cx + 40, sea_top - 58), (cx + 66, sea_top)]
    F.append(polygon(tip, fill=ICE, stroke=ICED, sw=1.8))
    # підводна маса (велика, ≈90 %), зубчаста й ширша
    under = [(cx - 46, sea_top), (cx + 66, sea_top),
             (cx + 120, sea_top + 60), (cx + 96, sea_top + 150),
             (cx + 128, sea_top + 210), (cx + 40, sea_top + 196),
             (cx - 10, sea_top + 200), (cx - 96, sea_top + 168),
             (cx - 128, sea_top + 96), (cx - 84, sea_top + 44)]
    F.append(polygon(under, fill=ICE, stroke=ICED, sw=1.8))
    # обвід усього айсберга поверх заливок (щоб грань ковзала лінією моря)
    F.append(polyline(tip, color=ICED, sw=1.8))

    # частки
    F.append(text(cx + 150, sea_top - 34, "над водою", size=12.5, color=INK, bold=True, anchor="start"))
    F.append(text(cx + 150, sea_top - 16, "≈ 10 %", size=13, color=POS, bold=True, anchor="start"))
    F.append(arrow(cx + 148, sea_top - 26, cx + 44, sea_top - 44, color=POS, sw=2.0))

    F.append(text(cx - 168, sea_top + 130, "під водою", size=12.5, color=INK, bold=True, anchor="end"))
    F.append(text(cx - 168, sea_top + 150, "≈ 90 %", size=13, color=NEG, bold=True, anchor="end"))
    F.append(arrow(cx - 166, sea_top + 138, cx - 96, sea_top + 130, color=NEG, sw=2.0))

    # формула
    b, _, _ = textbox(760, 210,
                      "V_занурений / V_повний\n= ρ_льоду / ρ_води\n= 917 / 1025 ≈ 0.895",
                      size=13.5, bold=True, pad=12, fill="#eef4fb", stroke=NEG, color=INK)
    F.append(b)

    F.append(fitbox(95, 500, 850, 80,
                    "Плавуче тіло тоне доти, доки витіснена вода не зважить стільки ж, скільки воно саме.\n"
                    "Тому частка зануреного об'єму дорівнює відношенню густин. Для льоду в морській воді це ≈ 0.895 —\n"
                    "майже дев'ять десятих ховається під водою, а над хвилями лишається сама верхівка.",
                    size=13, bold=True, fill="#eafaf0", stroke=GREEN, pad=11))

    render(os.path.join(IMG, "iceberg.svg"), W, H, *F,
           title="Айсберг: частка під водою — це відношення густин")


# ── Помічники для історичної вставки «Про плавучі тіла» ────────────────────────
def _rot(px, py, cx, cy, deg):
    """Повернути точку (px,py) навколо (cx,cy) на deg градусів (екран: y донизу)."""
    a = math.radians(deg)
    dx, dy = px - cx, py - cy
    return (cx + dx * math.cos(a) - dy * math.sin(a),
            cy + dx * math.sin(a) + dy * math.cos(a))


def _wrect(x, y, w, h, fill, opacity):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
            'fill-opacity="%.2f"/>' % (x, y, w, h, fill, opacity))


def _arcpath(x0, y0, x1, y1, r, sweep, color, sw):
    return ('<path d="M%.1f %.1f A %.1f %.1f 0 0 %d %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f" marker-end="url(#arrow)"/>'
            % (x0, y0, r, r, sweep, x1, y1, color, sw))


# ── Фігура 5: остійність плавучого тіла — метацентр (суть Книги II) ─────────────
def fig_metacenter():
    W, H = 1220, 690
    F = []
    HULL = [(-96, -56), (96, -56), (80, 22), (42, 60), (0, 72), (-42, 60), (-80, 22)]
    theta = 20.0
    wl = 294  # рівень води (спільний для обох панелей)

    def panel(Ox, Oy, gy, stable, header):
        P = []
        # тло панелі + вода
        P.append(rect(Ox - 168, 96, 336, 372, fill=SKY, stroke="#d7e6f0", sw=1.4, rx=10))
        P.append(_wrect(Ox - 166, wl, 332, 466 - wl, WATER, 1.0))
        # корпус (заливка), потім прозорий синій — тонує занурену частину
        hw = [_rot(px + Ox, py + Oy, Ox, Oy, theta) for px, py in HULL]
        P.append(polygon(hw, fill=WOOD, stroke=WOODD, sw=2.0))
        P.append(_wrect(Ox - 166, wl, 332, 466 - wl, WATERD, 0.34))
        P.append(waves(Ox - 158, Ox + 158, wl, sw=1.8))
        # вісь симетрії корпусу (пунктир)
        at = _rot(Ox, Oy - 56, Ox, Oy, theta)
        ab = _rot(Ox, Oy + 78, Ox, Oy, theta)
        P.append(line(at[0], at[1], ab[0], ab[1], color=MUTED, sw=1.4, dash="5 5"))
        # ключові точки
        G = _rot(Ox, Oy + gy, Ox, Oy, theta)
        M = _rot(Ox, Oy - 6, Ox, Oy, theta)
        B = (M[0], wl + 46)
        # лінія дії виштовхування — прямовисна через B і M
        P.append(line(B[0], B[1] + 8, M[0], M[1] - 40, color=FIELD, sw=1.4, dash="4 5"))
        # сили: вага вниз від G, виштовхування вгору від B
        P.append(arrow(G[0], G[1], G[0], G[1] + 78, color=POS, sw=3.0))
        P.append(arrow(B[0], B[1], B[0], B[1] - 86, color=FIELD, sw=3.0))
        # відрізок GM
        P.append(line(G[0] - 20, G[1], M[0] - 20, M[1], color=(FIELD if stable else POS), sw=2.6))
        P.append(text((G[0] + M[0]) / 2 - 30, (G[1] + M[1]) / 2 + 4,
                      "GM", size=12, color=(FIELD if stable else POS), bold=True, anchor="end"))
        # точки й підписи
        P.append(circle(M[0], M[1], 5, fill=FIELD, stroke=BG, sw=1.6))
        P.append(circle(B[0], B[1], 5, fill=NEG, stroke=BG, sw=1.6))
        P.append(circle(G[0], G[1], 5, fill=POS, stroke=BG, sw=1.6))
        P.append(text(M[0] + 12, M[1] - 5, "M — метацентр", size=12, color=FIELD, bold=True, anchor="start"))
        P.append(text(B[0] + 12, B[1] + 16, "B — центр виштовхування", size=11.5, color=NEG, bold=True, anchor="start"))
        P.append(text(G[0] - 12, G[1] + 4, "G — центр ваги", size=11.5, color=POS, bold=True, anchor="end"))
        P.append(text(B[0], B[1] - 100, "виштовхування", size=11, color=FIELD, bold=True))
        P.append(text(G[0], G[1] + 94, "вага m·g", size=11, color=POS, bold=True))
        # обертальна дія пари сил
        if stable:
            P.append(_arcpath(Ox + 44, 214, Ox - 44, 214, 58, 1, FIELD, 3.0))
            P.append(text(Ox, 196, "пара сил повертає до прямого", size=11.5, color=FIELD, bold=True))
        else:
            P.append(_arcpath(Ox - 40, 210, Ox + 52, 236, 58, 1, POS, 3.0))
            P.append(text(Ox, 196, "пара сил перекидає далі", size=11.5, color=POS, bold=True))
        # шапка панелі
        P.append(text(Ox, 74, header, size=13.5, bold=True))
        # вирок
        s = ("M вище G  →  СТІЙКЕ" if stable else "M нижче G  →  ХИТКЕ")
        col = FIELD if stable else POS
        tb, _, _ = textbox(Ox, 502, s, size=13.5, bold=True, pad=10,
                           fill="#ffffff", stroke=col, color=col)
        P.append(tb)
        return P

    F += panel(330, 300, 40, True, "низький центр ваги (осадкуватий корпус)")
    F += panel(880, 300, -46, False, "високий центр ваги (стрункий корпус)")

    F.append(fitbox(150, 556, 920, 92,
                    "Нахили тіло — і центр виштовхування B зсувається до зануренішого боку, а прямовисна через нього\n"
                    "перетинає вісь корпусу в точці M (метацентрі). Якщо M вище центра ваги G, пара «вага вниз — виштовхування\n"
                    "вгору» повертає тіло до прямого; якщо нижче — перекидає. Саме цю межу Архімед знайшов для параболоїдів\n"
                    "у Книзі II, за двадцять століть до слова «метацентр».",
                    size=12.5, bold=True, fill="#eafaf0", stroke=FIELD, pad=11))

    render(os.path.join(IMG, "metacenter.svg"), W, H, *F,
           title="Остійність плавучого тіла: чи поверне метацентр його до прямого")


# ── Фігура 6: доля тексту «Про плавучі тіла» крізь віки ────────────────────────
def fig_transmission():
    W, H = 1240, 560
    F = []
    y0 = 252
    F.append(arrow(96, y0, 1156, y0, color=MUTED, sw=2.6))
    nodes = [
        (150, "бл. 250 до н.е.", "Архімед пише\n«Про плавучі тіла»\n(Сиракузи)", "up", INK),
        (338, "X ст.", "єдиний грецький\nсписок (Візантія)", "down", NEG),
        (520, "1229", "текст зішкребли —\nзверху молитовник\n(палімпсест)", "up", POS),
        (702, "1269", "Мербеке:\nлатинський переклад\n(з іншого списку)", "down", INK),
        (900, "1906", "Гайберг читає\nпалімпсест —\nгрецький текст", "up", NEG),
        (1092, "1998", "Christie's, $2 млн →\nцифрове відчитання", "down", FIELD),
    ]
    for x, yr, desc, side, col in nodes:
        cy = 148 if side == "up" else 366
        if side == "up":
            F.append(line(x, y0 - 9, x, y0 - 44, color=MUTED, sw=1.2, dash="3 4"))
        else:
            F.append(line(x, y0 + 9, x, y0 + 44, color=MUTED, sw=1.2, dash="3 4"))
        tb, _, _ = textbox(x, cy, yr + "\n" + desc, size=12, bold=True, pad=9,
                           fill="#ffffff", stroke=col, color=INK)
        F.append(tb)
        F.append(circle(x, y0, 7.5, fill=col, stroke=BG, sw=2))

    F.append(fitbox(120, 474, 1000, 66,
                    "Дві з половиною тисячі років трактат тримався на волосині: латина Мербеке зберегла Заходу зміст,\n"
                    "а ЄДИНИЙ грецький список уцілів лиш тому, що його не дочистили під молитовник. Вісь часу не в масштабі.",
                    size=13, bold=True, fill="#f4f6f8", stroke=MUTED, pad=11))

    render(os.path.join(IMG, "transmission.svg"), W, H, *F,
           title="Доля тексту: як «Про плавучі тіла» дійшло до нас")


# ── Вставка math: строге виведення — інтеграл тиску → об'єм через Гаусса-Остроградського ──
def fig_deriv_surface():
    W, H = 1160, 650
    F = []
    tx0, tx1, tty, tby = 110, 560, 108, 566
    F.append(rect(tx0, tty, tx1 - tx0, tby - tty, fill=WATER, stroke=WATERD, sw=1.6, rx=4))
    F.append(waves(tx0 + 6, tx1 - 6, tty, sw=2.0))

    blob = [(330, 250), (398, 272), (432, 338), (414, 420),
            (348, 464), (272, 450), (240, 378), (258, 300)]
    bcx = sum(p[0] for p in blob) / len(blob)
    bcy = sum(p[1] for p in blob) / len(blob)
    F.append(polygon(blob, fill=STEEL, stroke=STEELD, sw=2.0))

    for (x, y) in blob:
        dx, dy = x - bcx, y - bcy
        d = math.hypot(dx, dy) or 1.0
        ux, uy = dx / d, dy / d
        L = 24 + 0.18 * max(0.0, y - 250)
        F.append(arrow(x + ux * L, y + uy * L, x, y, color=NEG, sw=2.2))
    F.append(text(tx0 + 10, tby - 14, "P·n перпендикулярно, всередину; глибше — дужче",
                  size=11.5, color=NEG, anchor="start", bold=True))

    F.append(circle(bcx, bcy, 5, fill=POS, stroke=BG, sw=1.5))
    F.append(text(bcx + 13, bcy + 4, "B", size=14, color=POS, anchor="start", bold=True, italic=True))
    F.append(arrow(bcx, 244, bcx, 174, color=GREEN, sw=3.6))
    F.append(text(bcx, 162, "F = ρ·g·V", size=13.5, color=GREEN, bold=True))

    cX = 850
    b1, _, _ = textbox(cX, 140, "F = −∮ P·n dA\n(точно, поверхня будь-яка)",
                       size=13.5, bold=True, pad=12, fill="#eef4fb", stroke=NEG, color=INK)
    F.append(b1)
    F.append(arrow(cX, 182, cX, 220, color=MUTED, sw=2.2))
    F.append(text(cX + 108, 204, "Гаусс–Остроградський", size=10.5, color=MUTED, anchor="middle"))
    b2, _, _ = textbox(cX, 262, "−∮ P·n dA = −∭ ∇P dV\nповерхня → об'єм",
                       size=13.5, bold=True, pad=12, fill=FILL, stroke=LINE, color=INK)
    F.append(b2)
    F.append(arrow(cX, 304, cX, 342, color=MUTED, sw=2.2))
    F.append(text(cX + 96, 326, "∇P = ρ·g (донизу)", size=10.5, color=MUTED, anchor="middle"))
    b3, _, _ = textbox(cX, 392, "F = ρ_рідини · g · V\nугору, у центроїді B",
                       size=14, bold=True, pad=12, fill="#eafaf0", stroke=GREEN, color=INK)
    F.append(b3)

    F.append(fitbox(120, 592, 920, 46,
                    "Кривизна поверхні зникає під час згортання: непогашений поштовх народжує не сам тиск, а його\n"
                    "градієнт, а той живе в об'ємі. Тому ρ·g·V справджується для тіла будь-якої форми.",
                    size=12.5, bold=True, fill="#f4f6f8", stroke=MUTED, pad=10))

    render(os.path.join(IMG, "deriv-surface.svg"), W, H, *F,
           title="Строге виведення: інтеграл тиску по поверхні → ρ·g·V по об'єму")


# ── Вставка math: остійність — клин, метацентр і плече відновлення GZ ───────────
def fig_metacenter_wedge():
    W, H = 1200, 700
    F = []
    F.append(line(600, 100, 600, 470, color="#dfe4ea", sw=1.4, dash="4 6"))
    WL = 262

    # ЛІВА панель — рівновага (B під G)
    F.append(text(320, 122, "рівновага: B під G на одній вертикалі", size=13.5, bold=True))
    F.append(rect(96, 138, 460, 300, fill=SKY, stroke=WATERD, sw=1.4, rx=4))
    F.append(rect(98, WL, 456, 438 - WL - 2, fill=WATER, stroke="none"))
    F.append(waves(104, 552, WL, sw=1.8))
    hx0, hx1, htop, hbot = 258, 386, 206, 372
    F.append(rect(hx0, htop, hx1 - hx0, hbot - htop, fill=STEEL, stroke=STEELD, sw=1.8, rx=3))
    ccx = (hx0 + hx1) / 2
    F.append(line(ccx, 190, ccx, 392, color=MUTED, sw=1.3, dash="5 5"))
    Gy, By = 236, (WL + hbot) / 2
    F.append(circle(ccx, Gy, 5.5, fill=INK, stroke=BG, sw=1.5))
    F.append(text(ccx - 13, Gy + 4, "G", size=14, color=INK, anchor="end", bold=True, italic=True))
    F.append(circle(ccx, By, 5.5, fill=POS, stroke=BG, sw=1.5))
    F.append(text(ccx - 13, By + 4, "B", size=14, color=POS, anchor="end", bold=True, italic=True))
    F.append(arrow(ccx + 42, Gy - 2, ccx + 42, Gy + 56, color=POS, sw=2.8))
    F.append(text(ccx + 48, Gy + 30, "вага", size=11, color=POS, anchor="start", bold=True))
    F.append(arrow(ccx - 42, By + 58, ccx - 42, By, color=GREEN, sw=2.8))
    F.append(text(ccx - 48, By + 38, "поштовх", size=11, color=GREEN, anchor="end", bold=True))
    F.append(text(320, 458, "одна вертикаль → моменту нема", size=12, color=MUTED, bold=True))

    # ПРАВА панель — крен на θ
    F.append(text(852, 122, "крен на θ: B → B′, метацентр M", size=13.5, bold=True))
    F.append(rect(644, 138, 460, 300, fill=SKY, stroke=WATERD, sw=1.4, rx=4))
    F.append(rect(646, WL, 456, 438 - WL - 2, fill=WATER, stroke="none"))
    F.append(waves(652, 1100, WL, sw=1.8))
    th = math.radians(16)
    hcx, hcy = 852, 288
    corners = [(-66, -84), (66, -84), (66, 82), (-66, 82)]
    rot = [(hcx + lx * math.cos(th) - ly * math.sin(th),
            hcy + lx * math.sin(th) + ly * math.cos(th)) for (lx, ly) in corners]
    F.append(polygon(rot, fill=STEEL, stroke=STEELD, sw=1.8))

    def axis_pt(t):
        return (hcx + t * math.sin(th), hcy - t * math.cos(th))
    at, ab = axis_pt(150), axis_pt(-92)
    F.append(line(ab[0], ab[1], at[0], at[1], color=MUTED, sw=1.3, dash="5 5"))

    # клини
    F.append(polygon([(776, WL), (822, WL), (792, WL - 32)], fill=SKY, stroke=NEG, sw=1.4))
    F.append(text(742, WL - 42, "клин вийшов", size=10.5, color=NEG, anchor="middle", bold=True))
    F.append(polygon([(888, WL), (930, WL), (924, WL + 38)], fill=WATERD, stroke=NEG, sw=1.4))
    F.append(text(958, WL + 48, "клин зайшов", size=10.5, color=NEG, anchor="middle", bold=True))

    G = axis_pt(46)
    Bp = (884, 322)
    Bx, By2 = 852, 326
    Mx, My = Bp[0], hcy - math.cos(th) * ((Bp[0] - hcx) / math.sin(th))
    F.append(line(Bp[0], Bp[1], Mx, My, color=NEG, sw=1.5, dash="4 4"))
    F.append(circle(Mx, My, 5.5, fill=NEG, stroke=BG, sw=1.5))
    F.append(text(Mx + 13, My - 2, "M", size=14, color=NEG, anchor="start", bold=True, italic=True))
    F.append(circle(G[0], G[1], 5.5, fill=INK, stroke=BG, sw=1.5))
    F.append(text(G[0] - 13, G[1] - 3, "G", size=14, color=INK, anchor="end", bold=True, italic=True))
    F.append(circle(Bx, By2, 5, fill="#c9a0a0", stroke=BG, sw=1.2))
    F.append(text(Bx - 13, By2 + 13, "B", size=12.5, color="#a05a5a", anchor="end", italic=True))
    F.append(circle(Bp[0], Bp[1], 5.5, fill=POS, stroke=BG, sw=1.5))
    F.append(text(Bp[0] + 13, Bp[1] + 14, "B′", size=13.5, color=POS, anchor="start", bold=True, italic=True))
    F.append(line(G[0], G[1], Mx, G[1], color=FIELD, sw=2.6))
    F.append(text((G[0] + Mx) / 2, G[1] - 9, "GZ", size=12.5, color=FIELD, bold=True, italic=True))
    F.append(arrow(G[0] - 32, G[1] - 2, G[0] - 32, G[1] + 52, color=POS, sw=2.6))
    F.append(text(G[0] - 38, G[1] + 28, "вага", size=10.5, color=POS, anchor="end", bold=True))
    F.append(arrow(Bp[0] + 32, Bp[1] + 54, Bp[0] + 32, Bp[1], color=GREEN, sw=2.6))
    F.append(text(Bp[0] + 38, Bp[1] + 32, "поштовх", size=10.5, color=GREEN, anchor="start", bold=True))
    F.append(text(852, 458, "M вище G → пара повертає назад", size=12, color=FIELD, bold=True))

    F.append(fitbox(150, 508, 900, 62,
                    "BM = I / V   (I — момент інерції площі ватерлінії)        GM = BM − BG = I/V − BG\n"
                    "плече відновлення  GZ = GM · sin θ          остійно ⟺ GM > 0 (метацентр вище центра ваги)",
                    size=13.5, bold=True, fill="#eafaf0", stroke=GREEN, pad=11))

    render(os.path.join(IMG, "metacenter-wedge.svg"), W, H, *F,
           title="Остійність: клин зсуває B, метацентр M і плече відновлення GZ")


# ── Вставка math: понтон — метацентрична висота у числах ───────────────────────
def fig_pontoon():
    W, H = 1120, 590
    F = []
    px0, px1, ptop, pbot = 200, 430, 168, 384
    b_px = px1 - px0
    H_m, d_m, KG_m = 0.6, 0.35, 0.30
    WL = pbot - (d_m / H_m) * (pbot - ptop)
    F.append(rect(150, WL, 360, pbot - WL + 26, fill=WATER, stroke="none"))
    F.append(waves(158, 502, WL, sw=1.8))
    F.append(rect(px0, ptop, b_px, pbot - ptop, fill=CORK, stroke=CORKD, sw=2.0, rx=3))
    F.append(rect(px0 + 2, WL, b_px - 4, pbot - WL - 1, fill=WATERD, stroke="none"))
    ccx = (px0 + px1) / 2
    K = (ccx, pbot)
    B = (ccx, pbot - (d_m / 2 / H_m) * (pbot - ptop))
    G = (ccx, pbot - (KG_m / H_m) * (pbot - ptop))
    F.append(line(ccx, ptop - 6, ccx, pbot + 6, color=MUTED, sw=1.2, dash="5 5"))
    F.append(circle(K[0], K[1], 4.5, fill=INK, stroke=BG, sw=1.2))
    F.append(text(K[0] + 12, K[1] + 4, "K", size=12.5, color=INK, anchor="start", bold=True, italic=True))
    F.append(circle(B[0], B[1], 5, fill=POS, stroke=BG, sw=1.4))
    F.append(text(B[0] + 12, B[1] + 4, "B (d/2)", size=12, color=POS, anchor="start", bold=True, italic=True))
    F.append(circle(G[0], G[1], 5, fill=NEG, stroke=BG, sw=1.4))
    F.append(text(G[0] + 12, G[1] + 4, "G", size=12.5, color=NEG, anchor="start", bold=True, italic=True))
    F.append(arrow(px0, pbot + 24, px1, pbot + 24, color=MUTED, sw=1.6))
    F.append(arrow(px1, pbot + 24, px0, pbot + 24, color=MUTED, sw=1.6))
    F.append(text(ccx, pbot + 40, "b = 2 м", size=12, color=MUTED, bold=True))
    F.append(arrow(px0 - 26, WL, px0 - 26, pbot, color=MUTED, sw=1.6))
    F.append(arrow(px0 - 26, pbot, px0 - 26, WL, color=MUTED, sw=1.6))
    F.append(text(px0 - 34, (WL + pbot) / 2 + 4, "d", size=12, color=MUTED, anchor="end", bold=True))
    F.append(text(px1 + 14, WL - 6, "ватерлінія", size=10.5, color=WATERD, anchor="start", bold=True))

    wx0, wy0, wpw, wph = 556, 152, 210, 92
    F.append(rect(wx0, wy0, wpw, wph, fill=SKY, stroke=WATERD, sw=1.6, rx=4))
    F.append(line(wx0, wy0 + wph / 2, wx0 + wpw, wy0 + wph / 2, color=NEG, sw=1.6, dash="6 4"))
    F.append(text(wx0 + wpw / 2, wy0 - 8, "площа ватерлінії  L × b", size=11, bold=True))
    F.append(text(wx0 + wpw + 8, wy0 + wph / 2 + 4, "вісь крену", size=10, color=NEG, anchor="start", bold=True))
    F.append(text(wx0 + wpw / 2, wy0 + wph + 18, "I = ∫x² dA = L·b³/12", size=11.5, color=INK, bold=True))

    cX = 900
    rows = [
        ("V = L·b·d = 2.8 м³", FILL, LINE),
        ("I = L·b³/12 = 2.667 м⁴", FILL, LINE),
        ("BM = I/V = b²/(12d) = 0.952 м", "#eef4fb", NEG),
        ("BG = KG − KB = 0.30 − 0.175 = 0.125 м", FILL, LINE),
        ("GM = BM − BG = 0.827 м  > 0  остійно", "#eafaf0", GREEN),
    ]
    yy = 178
    for s, fl, st in rows:
        bx, _, _ = textbox(cX, yy, s, size=12.5, bold=True, pad=10,
                           fill=fl, stroke=st, color=INK, min_w=380)
        F.append(bx)
        yy += 62

    F.append(fitbox(150, 512, 900, 58,
                    "BM = b²/(12d) залежить від ширини у КВАДРАТІ. Широкий пліт (b = 2 м) остійний із запасом;\n"
                    "звузити до b = 0.5 м — і GM стає від'ємним, той самий понтон перекидається на бік.",
                    size=13, bold=True, fill="#f4f6f8", stroke=MUTED, pad=11))

    render(os.path.join(IMG, "pontoon.svg"), W, H, *F,
           title="Понтон: метацентрична висота GM = I/V − BG у числах")


# ── Вставка math: гелієва кулька в авто — поштовх проти ефективної гравітації ───
def fig_balloon_car():
    W, H = 1120, 560
    F = []
    F.append(line(90, 396, 720, 396, color=STEELD, sw=3.0))
    F.append(rect(150, 214, 490, 158, fill="#eef2f6", stroke=STEELD, sw=2.0, rx=16))
    F.append(circle(250, 396, 26, fill=STEEL, stroke=STEELD, sw=2.2))
    F.append(circle(540, 396, 26, fill=STEEL, stroke=STEELD, sw=2.2))
    F.append(arrow(300, 178, 470, 178, color=INK, sw=3.4))
    F.append(text(500, 184, "a (розгін уперед)", size=12.5, anchor="start", bold=True))

    px, ptopy = 300, 238
    F.append(line(px, ptopy, px - 34, ptopy + 92, color=MUTED, sw=2.2))
    F.append(circle(px - 34, ptopy + 100, 9, fill=STEELD, stroke=INK, sw=1.4))
    F.append(text(px - 40, ptopy + 130, "виска — назад", size=10.5, color=MUTED, anchor="middle", bold=True))

    bx, bfloor, baly = 520, 356, 252
    F.append(line(bx - 30, bfloor, bx, baly + 20, color=CORKD, sw=1.8))
    F.append(circle(bx, baly, 22, fill="#f4b9c4", stroke=POS, sw=1.8))
    F.append(text(bx, baly + 5, "He", size=12, color=POS, bold=True))
    F.append(text(bx + 30, baly - 22, "кулька — вперед", size=11, color=POS, anchor="start", bold=True))

    ox, oy = 890, 252
    F.append(rect(740, 150, 350, 300, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=8))
    F.append(text(915, 176, "у системі салону", size=12, bold=True))
    F.append(circle(ox, oy, 3.5, fill=INK, stroke="none", sw=0))
    F.append(arrow(ox, oy, ox, oy + 92, color=NEG, sw=2.8))
    F.append(text(ox - 10, oy + 68, "g", size=13, color=NEG, anchor="end", bold=True, italic=True))
    F.append(arrow(ox, oy, ox - 84, oy, color=NEG, sw=2.8))
    F.append(text(ox - 56, oy - 10, "−a", size=13, color=NEG, anchor="middle", bold=True, italic=True))
    F.append(arrow(ox, oy, ox - 84, oy + 92, color=INK, sw=3.2))
    F.append(text(ox - 96, oy + 88, "g_еф", size=13, color=INK, anchor="end", bold=True, italic=True))
    F.append(arrow(ox, oy, ox + 84, oy - 92, color=GREEN, sw=3.4))
    F.append(text(ox + 92, oy - 88, "поштовх", size=12, color=GREEN, anchor="start", bold=True))

    F.append(fitbox(150, 470, 900, 66,
                    "У салоні діє ефективна гравітація g_еф = g − a (вниз-і-назад). Важче за повітря тіло — пасажир,\n"
                    "виска — хилиться назад по цьому полю; легша гелієва кулька виштовхується ПРОТИ g_еф — угору-і-вперед.\n"
                    "∇P = ρ·g_еф  ⟹  F = −ρ·V·g_еф, тобто поштовх завжди проти ефективної гравітації.",
                    size=12.5, bold=True, fill="#eafaf0", stroke=GREEN, pad=11))

    render(os.path.join(IMG, "balloon-car.svg"), W, H, *F,
           title="Виштовхування проти ефективної гравітації: кулька в авто хилиться вперед")


# ── Вставка proj: осадка як корінь — S-подібна крива й звуження бісекцією ──────
def fig_draft_root():
    W, H = 1180, 720
    F = []
    R = 0.10
    rho_body, rho_water = 600.0, 1000.0
    V_total = 4.0 / 3.0 * math.pi * R ** 3
    target = (rho_body / rho_water) * V_total

    def Vsub(d):
        return math.pi * d * d * (R - d / 3.0)

    # перші 5 кроків бісекції — для панелі звуження
    lo, hi = 0.0, 2 * R
    flo = Vsub(lo) - target
    brackets = []
    for _ in range(5):
        mid = 0.5 * (lo + hi)
        fm = Vsub(mid) - target
        brackets.append((lo, hi, mid))
        if (flo < 0) == (fm < 0):
            lo, flo = mid, fm
        else:
            hi = mid
    # точний корінь (для маркера на кривій)
    lo2, hi2 = 0.0, 2 * R
    for _ in range(60):
        mid = 0.5 * (lo2 + hi2)
        f2 = Vsub(mid) - target
        f_lo2 = Vsub(lo2) - target
        if (f_lo2 < 0) == (f2 < 0):
            lo2 = mid
        else:
            hi2 = mid
    droot = 0.5 * (lo2 + hi2)

    x0, x1 = 160, 980
    y0, y1 = 100, 420
    Vmax = 0.0042

    def xd(d):
        return x0 + d / (2 * R) * (x1 - x0)

    def yv(v):
        return y1 - v / Vmax * (y1 - y0)

    F.append(arrow(x0, y1 + 14, x0, y0 - 14, color=INK, sw=2.0))
    F.append(arrow(x0 - 14, y1, x1 + 24, y1, color=INK, sw=2.0))
    F.append(text(x0 - 10, y0 - 22, "V, м³", size=12.5, anchor="start", bold=True))
    F.append(text(x1 + 30, y1 + 5, "d, м", size=12.5, anchor="start", bold=True))

    for dv in [0.0, 0.05, 0.10, 0.15, 0.20]:
        xx = xd(dv)
        F.append(line(xx, y1 - 4, xx, y1 + 4, color=INK, sw=1.4))
        F.append(text(xx, y1 + 20, "%.2f" % dv, size=10.5, color=MUTED))

    pts = []
    n = 100
    for i in range(n + 1):
        d = 2 * R * i / n
        pts.append((xd(d), yv(Vsub(d))))
    F.append(polyline(pts, color=DOT, sw=3.2))
    lx, ly = xd(0.15), yv(Vsub(0.15))
    F.append(text(lx - 10, ly - 12, "V_занурений(d)", size=12, color=DOT, anchor="end", bold=True))

    ty = yv(target)
    xroot = xd(droot)
    F.append(line(x0, ty, xroot, ty, color=POS, sw=2.2, dash="6 5"))
    F.append(text(x0 + 8, ty - 12, "цільовий об'єм = (ρ_тіла/ρ_води)·V_повний", size=11, color=POS, anchor="start", bold=True))

    row_y0 = y1 + 56
    row_dy = 24
    last_row_y = row_y0 + (len(brackets) - 1) * row_dy
    F.append(line(xroot, ty, xroot, last_row_y + 14, color=GREEN, sw=1.8, dash="4 4"))
    F.append(circle(xroot, ty, 6, fill=GREEN, stroke=BG, sw=1.6))
    F.append(text(xroot + 10, ty + 18, "d ≈ %.4f м" % droot, size=12, color=GREEN, anchor="start", bold=True))

    F.append(text(x0, y1 + 34, "бісекція звужує відрізок [lo, hi] удвічі щокроку, аж поки не затисне корінь:",
                  size=11.5, color=MUTED, anchor="start", bold=True))
    for i, (blo, bhi, bmid) in enumerate(brackets):
        ry = row_y0 + i * row_dy
        F.append(line(xd(blo), ry, xd(bhi), ry, color=STEELD, sw=4.4))
        F.append(line(xd(blo), ry - 6, xd(blo), ry + 6, color=INK, sw=1.6))
        F.append(line(xd(bhi), ry - 6, xd(bhi), ry + 6, color=INK, sw=1.6))
        F.append(circle(xd(bmid), ry, 3.4, fill=POS, stroke="none"))
        F.append(text(x0 - 20, ry + 4, "N=%d" % (i + 1), size=10, color=MUTED, anchor="end"))

    F.append(fitbox(x0 - 10, last_row_y + 34, (x1 + 30) - (x0 - 10), 76,
                    "Корінь рівняння f(d) = V_занурений(d) − (ρ_тіла/ρ_води)·V_повний = 0 — це і є осадка.\n"
                    "Бісекція щоразу ділить відрізок навпіл і лишає ту половину, де f усе ще міняє знак:\n"
                    "за 5 кроків невизначеність спадає у 32 рази, за 40 — точніше, ніж має сенс.",
                    size=12, bold=True, fill="#eafaf0", stroke=GREEN, pad=10))

    render(os.path.join(IMG, "draft-root.svg"), W, H, *F,
           title="Осадка як корінь: перетин S-подібної кривої з цільовим об'ємом, звуження бісекцією")


# ── Вставка proj: фазовий портрет інтеграторів і роздування енергії Ейлером ────
def fig_bob_integrators():
    W, H = 1200, 700
    F = []
    F.append(line(600, 100, 600, 470, color="#dfe4ea", sw=1.4, dash="4 6"))

    # ЛІВА панель — фазова площина x, v/ω
    F.append(text(326, 122, "фазова площина: точний рух — коло, Ейлер — спіраль", size=13, bold=True))
    F.append(rect(96, 138, 460, 300, fill=SKY, stroke=WATERD, sw=1.4, rx=4))
    cx, cy = 326, 300
    F.append(line(cx - 190, cy, cx + 190, cy, color=MUTED, sw=1.2, dash="4 5"))
    F.append(line(cx, cy - 130, cx, cy + 130, color=MUTED, sw=1.2, dash="4 5"))
    F.append(text(cx + 196, cy + 4, "x", size=12.5, color=MUTED, anchor="start", italic=True))
    F.append(text(cx - 6, cy - 136, "v/ω", size=12.5, color=MUTED, anchor="end", italic=True))

    r_closed = 78
    F.append(circle(cx, cy, r_closed, fill="none", stroke=GREEN, sw=3.0))
    F.append(text(cx, cy + r_closed + 24, "симплектичний і RK4 — та сама замкнена орбіта",
                  size=11, color=GREEN, anchor="middle", bold=True))

    r0, turns = 74, 3.0
    growth = 1.9
    k = math.log(growth) / (turns * 2 * math.pi)
    spts = []
    steps = 220
    for i in range(steps + 1):
        th = turns * 2 * math.pi * i / steps
        r = r0 * math.exp(k * th)
        spts.append((cx + r * math.cos(th), cy - r * math.sin(th)))
    F.append(polyline(spts, color=POS, sw=2.6))
    F.append(circle(spts[0][0], spts[0][1], 4.5, fill=POS, stroke=BG, sw=1.3))
    F.append(text(spts[0][0] + 10, spts[0][1] - 6, "старт", size=10, color=POS, anchor="start"))
    ex, ey = spts[-1]
    F.append(circle(ex, ey, 4.5, fill=POS, stroke=BG, sw=1.3))
    F.append(text(ex + 8, ey - 4, "Ейлер — розкручується", size=11, color=POS, anchor="start", bold=True))

    # ПРАВА панель — енергія після 12 періодів, лог-шкала
    F.append(text(874, 122, "після 12 періодів: у скільки разів змінилась енергія (лог-шкала)", size=12.5, bold=True))
    F.append(rect(644, 138, 460, 300, fill="#fbfcfd", stroke=MUTED, sw=1.4, rx=4))

    px0, px1 = 760, 1064
    logspan = math.log10(3000.0)

    def lxp(v):
        return px0 + (math.log10(v) / logspan) * (px1 - px0)

    axis_y = 410
    F.append(line(px0, 170, px0, axis_y, color=INK, sw=1.6))
    for tv in [1, 10, 100, 1000]:
        xx = lxp(tv)
        F.append(line(xx, 170, xx, axis_y, color="#e3e6ea", sw=1.2))
        F.append(line(xx, axis_y - 4, xx, axis_y + 4, color=INK, sw=1.4))
        F.append(text(xx, axis_y + 20, "×%d" % tv, size=10.5, color=MUTED))
    F.append(text((px0 + px1) / 2, axis_y + 38, "кратність енергії (лог-шкала)", size=10.5, color=MUTED))

    rows = [("Ейлер", 2573.0, POS, "×2573"),
            ("симплектичний", 0.996, GREEN, "×0.996"),
            ("RK4", 0.999987, GREEN, "×0.999987")]
    ry0, rdy = 210, 80
    for i, (name, val, col, label) in enumerate(rows):
        ry = ry0 + i * rdy
        vx = lxp(max(val, 1.0))
        F.append(text(px0 - 14, ry + 4, name, size=12, color=INK, anchor="end", bold=True))
        if vx - px0 > 2:
            F.append(line(px0, ry, vx, ry, color=col, sw=10))
        F.append(circle(vx, ry, 5.5, fill=col, stroke=BG, sw=1.4))
        lxx = vx + 14 if vx - px0 > 2 else px0 + 14
        F.append(text(lxx, ry + 4, label, size=11.5, color=col, anchor="start", bold=True))

    F.append(fitbox(150, 508, 900, 66,
                    "Явний Ейлер: за крок амплітуда множиться на √(1+ω²h²) > 1 — енергія росте без обмеження,\n"
                    "хоч би який дрібний крок. Симплектичний Ейлер і RK4 стережуть майже точну орбіту:\n"
                    "похибка лишається в частках відсотка навіть після 12 повних періодів.",
                    size=12.5, bold=True, fill="#eafaf0", stroke=GREEN, pad=11))

    render(os.path.join(IMG, "bob-integrators.svg"), W, H, *F,
           title="Фазовий портрет і збереження енергії: Ейлер розкручується, симплектичний і RK4 тримають орбіту")


if __name__ == "__main__":
    fig_origin()
    fig_displaced()
    fig_float_sink()
    fig_iceberg()
    fig_metacenter()
    fig_transmission()
    fig_deriv_surface()
    fig_metacenter_wedge()
    fig_pontoon()
    fig_balloon_car()
    fig_draft_root()
    fig_bob_integrators()
    print("OK: 12 SVG ->", IMG)

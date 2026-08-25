# -*- coding: utf-8 -*-
"""Фігури до статті «Фігури Ліссажу». Запуск із теки теми:  python figs.py
Виводить SVG у ./img/. svgkit береться зі scripts/ у корені репо."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def sine(x0, W, cycles, yc, amp, color, sw=1.8, n=400, phase=0.0):
    """Синусоїда y=yc-amp·sin(2π·cycles·t+phase), t∈[0,1], x=x0+t·W (піксельний y)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append("%.1f,%.1f" % (x0 + t * W, yc - amp * math.sin(2 * math.pi * cycles * t + phase)))
    return ('<polyline fill="none" stroke="%s" stroke-width="%.1f" points="%s"/>'
            % (color, sw, " ".join(pts)))


def lissajous(cx, cy, R, a, b, delta, color, sw=2.0, n=1600):
    """Крива Ліссажу: x=cx+R·sin(a·τ+δ), y=cy−R·sin(b·τ), τ∈[0,2π]."""
    pts = []
    for i in range(n + 1):
        tau = 2 * math.pi * i / n
        x = cx + R * math.sin(a * tau + delta)
        y = cy - R * math.sin(b * tau)
        pts.append("%.2f,%.2f" % (x, y))
    return ('<polyline fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round" points="%s"/>'
            % (color, sw, " ".join(pts)))


# ── Фігура 1: як народжується фігура ─────────────────────────────────────────
def fig_construction():
    W, H = 920, 440

    # ліві часові графіки: два вхідні коливання
    px0, pw = 78, 236
    # x(t) — 3 цикли
    y1 = 120
    t1 = text(px0, 74, "горизонтальний сигнал  x(t)", size=14, color=NEG, anchor="start", bold=True)
    b1 = line(px0, y1, px0 + pw, y1, MUTED, 1.0, dash="3,4")
    w1 = sine(px0, pw, 3, y1, 34, NEG, 1.9)
    # y(t) — 2 цикли
    y2 = 300
    t2 = text(px0, 254, "вертикальний сигнал  y(t)", size=14, color=NEG, anchor="start", bold=True)
    b2 = line(px0, y2, px0 + pw, y2, MUTED, 1.0, dash="3,4")
    w2 = sine(px0, pw, 2, y2, 34, NEG, 1.9)

    # стрілка «сплітаються»
    arr = arrow(350, 210, 468, 210, INK, 2.0)
    arr_l = text(409, 196, "сплітаються", size=13, color=MUTED, italic=True)

    # права площина XY
    fx, fy, fs = 500, 90, 300           # рамка
    cx, cy, R = fx + fs / 2, fy + fs / 2, 140
    frame = rect(fx, fy, fs, fs, fill=BG, stroke=LINE, sw=1.8, rx=8)
    axh = line(fx + 2, cy, fx + fs - 2, cy, MUTED, 1.0)
    axv = line(cx, fy + 2, cx, fy + fs - 2, MUTED, 1.0)
    lblx = text(fx + fs - 10, cy + 18, "X", size=13, color=MUTED, bold=True)
    lbly = text(cx + 16, fy + 16, "Y", size=13, color=MUTED, anchor="start", bold=True)
    curve = lissajous(cx, cy, R, 3, 2, math.pi / 2, NEG, 2.1)

    # точка P і її проєкції
    tau0 = 2 * math.pi * 0.09
    Px = cx + R * math.sin(3 * tau0 + math.pi / 2)
    Py = cy - R * math.sin(2 * tau0)
    proj = (line(Px, Py, Px, cy, POS, 1.3, dash="4,4")
            + line(Px, Py, cx, Py, POS, 1.3, dash="4,4"))
    dotP = circle(Px, Py, 5, fill=POS, stroke=POS)
    lp = text(Px + 10, Py - 8, "P", size=14, color=POS, anchor="start", bold=True)
    fx_lbl = text(Px, cy + 18, "x", size=13, color=POS, bold=True, italic=True)
    fy_lbl = text(cx - 12, Py + 5, "y", size=13, color=POS, anchor="end", bold=True, italic=True)

    render(os.path.join(IMG, "construction.svg"), W, H,
           t1, b1, w1, t2, b2, w2, arr, arr_l,
           frame, axh, axv, lblx, lbly, curve, proj, dotP, lp, fx_lbl, fy_lbl,
           title="Дві перпендикулярні синусоїди сплітаються у фігуру")


# ── Фігура 2: рівні частоти, різний зсув фаз ─────────────────────────────────
def fig_phase_gallery():
    W, H = 1000, 290
    R = 72
    cy = 150
    cells = [(130, 0, "φ = 0°"),
             (310, 45, "φ = 45°"),
             (490, 90, "φ = 90°"),
             (670, 135, "φ = 135°"),
             (850, 180, "φ = 180°")]
    frags = []
    for cx, deg, lbl in cells:
        frags.append(rect(cx - R, cy - R, 2 * R, 2 * R, fill=BG, stroke=LINE, sw=1.5, rx=8))
        frags.append(line(cx - R + 2, cy, cx + R - 2, cy, MUTED, 0.8))
        frags.append(line(cx, cy - R + 2, cx, cy + R - 2, MUTED, 0.8))
        frags.append(lissajous(cx, cy, R - 3, 1, 1, math.radians(deg), NEG, 2.1))
        frags.append(text(cx, cy + R + 24, lbl, size=14, color=INK, bold=True))
    render(os.path.join(IMG, "phase-gallery.svg"), W, H, *frags,
           title="Однакові частоти (1:1): форма читає зсув фаз")


# ── Фігура 3: різні відношення частот ────────────────────────────────────────
def fig_ratio_gallery():
    W, H = 940, 312
    R = 88
    cy = 158
    # (cx, a, b, delta, label, mark?)
    cells = [(140, 1, 1, math.pi / 2, "1 : 1", False),
             (370, 1, 2, 0.0, "1 : 2", False),
             (600, 2, 3, 0.0, "2 : 3", True),
             (830, 3, 4, math.pi / 2, "3 : 4", False)]
    frags = []
    for cx, a, b, delta, lbl, mark in cells:
        frags.append(rect(cx - R, cy - R, 2 * R, 2 * R, fill=BG, stroke=LINE, sw=1.5, rx=8))
        frags.append(line(cx - R + 2, cy, cx + R - 2, cy, MUTED, 0.8))
        frags.append(line(cx, cy - R + 2, cx, cy + R - 2, MUTED, 0.8))
        frags.append(lissajous(cx, cy, R, a, b, delta, NEG, 2.0))
        frags.append(text(cx, cy + R + 26, lbl, size=15, color=INK, bold=True))
        if mark:
            # дотики до верхнього краю (b штук) і бічного (a штук)
            for k in range(b):
                tau = (math.pi / 2 + 2 * math.pi * k) / b
                xk = cx + R * math.sin(a * tau + delta)
                frags.append(circle(xk, cy - R, 4.5, fill=POS, stroke=POS))
            for k in range(a):
                tau = (math.pi / 2 + 2 * math.pi * k) / a
                yk = cy - R * math.sin(b * tau)
                frags.append(circle(cx + R, yk, 4.5, fill=FIELD, stroke=FIELD))
            frags.append(text(cx, cy + R + 44, "3 зверху · 2 збоку", size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "ratio-gallery.svg"), W, H, *frags,
           title="Різні частоти: відношення дотиків = відношення частот")


def lissajous_decay(cx, cy, R0, a, b, delta, turns, decay, color, sw=1.8, n=2400):
    """Крива Ліссажу зі згасанням: радіус тане як exp(−decay·оберт)."""
    pts = []
    for i in range(n + 1):
        tau = 2 * math.pi * turns * i / n
        R = R0 * math.exp(-decay * tau / (2 * math.pi))
        pts.append("%.2f,%.2f" % (cx + R * math.sin(a * tau + delta), cy - R * math.sin(b * tau)))
    return ('<polyline fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round" points="%s"/>'
            % (color, sw, " ".join(pts)))


def vdim(x, y1, y2, tick=7, color=MUTED):
    """Вертикальний розмір із зарубками."""
    return (line(x, y1, x, y2, color, 1.2)
            + line(x - tick, y1, x + tick, y1, color, 1.2)
            + line(x - tick, y2, x + tick, y2, color, 1.2))


# ── Вставка, фігура 1: маятник, підвішений у двох точках ─────────────────────
def fig_two_point_pendulum():
    W, H = 920, 500
    f = []

    # --- ліва панель: геометрія підвісу ---
    f.append(text(230, 70, "Підвіс: одна вага — два періоди", size=15, bold=True))
    f.append(rect(120, 92, 260, 12, fill="#dfe3e8", stroke=LINE, sw=1.2, rx=3))
    ax, bx, by = 170.0, 330.0, 104.0
    kx, ky = 250.0, 304.0
    bobx, boby = 250.0, 370.0
    f.append(text(ax, 86, "A", size=13, bold=True))
    f.append(text(bx, 86, "B", size=13, bold=True))
    f.append(circle(ax, by, 4.5, fill=INK, stroke=INK))
    f.append(circle(bx, by, 4.5, fill=INK, stroke=INK))
    f.append(line(ax, by, kx, ky, INK, 1.8))
    f.append(line(bx, by, kx, ky, INK, 1.8))
    f.append(line(kx, ky, bobx, boby, INK, 1.8))
    f.append(circle(kx, ky, 4.0, fill=POS, stroke=POS))
    f.append(text(264, 312, "вузол", size=13, color=POS, anchor="start", bold=True))
    f.append(circle(bobx, boby, 15, fill="#dfe3e8", stroke=INK, sw=2))
    f.append(vdim(320, ky, boby))
    f.append(text(332, 342, "ℓ = 0.25 м", size=13, anchor="start"))
    f.append(vdim(160, by, boby))
    f.append(text(148, 241, "L = 1.00 м", size=13, anchor="end"))
    f.append(text(230, 406, "два незалежні гойдання однієї ваги", size=13, color=MUTED, italic=True))
    f.append(fitbox(62, 416, 336, 32, "упоперек AB працює L → 0.50 Гц", size=13))
    f.append(fitbox(62, 454, 336, 32, "уздовж AB працює ℓ → 1.00 Гц", size=13))

    # --- права панель: слід на папері ---
    f.append(text(650, 70, "Що лишається на папері", size=15, bold=True))
    f.append(rect(490, 92, 320, 320, fill=BG, stroke=LINE, sw=1.5, rx=8))
    f.append(lissajous_decay(650, 252, 145, 2, 1, 0.0, 11, 0.075, NEG, 1.7))
    f.append(mtext(650, 434, ["слід у піску: кожен наступний виток",
                              "трохи менший — крива не замикається"], size=13, color=MUTED))

    render(os.path.join(IMG, "two-point-pendulum.svg"), W, H, *f,
           title="Маятник Блекберна: вузол на шнурі задає відношення частот")


# ── Вставка, фігура 2: три пензлі й маса кожного ─────────────────────────────
def fig_three_brushes():
    W, H = 1020, 440
    f = []

    def fork(x, ytop, ybot, w=9, gap=22):
        """Камертон: дві ніжки, перемичка, ручка. x — центр."""
        s = rect(x - gap / 2 - w, ytop, w, ybot - ytop, fill="#dfe3e8", stroke=INK, sw=1.4, rx=3)
        s += rect(x + gap / 2, ytop, w, ybot - ytop, fill="#dfe3e8", stroke=INK, sw=1.4, rx=3)
        s += rect(x - gap / 2 - w, ybot - 2, gap + 2 * w, 11, fill="#dfe3e8", stroke=INK, sw=1.4, rx=3)
        s += rect(x - 5, ybot + 9, 10, 24, fill="#dfe3e8", stroke=INK, sw=1.4, rx=3)
        return s

    # ── А: голка по кіптяві ──
    f.append(text(180, 68, "Голка по кіптяві", size=15, bold=True))
    f.append(fork(170, 100, 172))
    f.append(line(170, 205, 206, 238, POS, 2.2))
    f.append(rect(112, 240, 140, 44, fill="#3a3a3a", stroke=LINE, sw=1.4, rx=3))
    f.append(sine(120, 124, 3, 262, 13, "#ffffff", 1.6))
    f.append(arrow(262, 262, 306, 262, MUTED, 1.8))
    f.append(text(284, 250, "рух", size=13, color=MUTED))
    f.append(fitbox(30, 312, 300, 56,
                    "перо тисне й тертям гальмує\nте, що саме береться виміряти", size=13))
    f.append(fitbox(30, 378, 300, 34, "маса пензля: голка з важелем", size=13,
                    fill="#fdecea", stroke=POS))

    # ── Б: цівка піску ──
    f.append(text(510, 68, "Цівка піску з маятника", size=15, bold=True))
    f.append(rect(462, 96, 96, 11, fill="#dfe3e8", stroke=LINE, sw=1.2, rx=3))
    f.append(line(510, 107, 510, 214, INK, 1.8))
    f.append(circle(510, 228, 14, fill="#dfe3e8", stroke=INK, sw=2))
    f.append('<polygon points="497,241 523,241 510,259" fill="#dfe3e8" stroke="%s" stroke-width="1.4"/>' % LINE)
    f.append(line(510, 259, 510, 272, MUTED, 1.4, dash="2,4"))
    f.append(rect(432, 272, 156, 46, fill=BG, stroke=LINE, sw=1.4, rx=3))
    f.append(lissajous_decay(510, 295, 19, 2, 1, 0.0, 8, 0.10, NEG, 1.2))
    f.append(fitbox(360, 330, 300, 56,
                    "пише сама вага — але гойдання\nповільне й неухильно згасає", size=13))
    f.append(fitbox(360, 396, 300, 34, "маса пензля: увесь вантаж", size=13,
                    fill="#fdecea", stroke=POS))

    # ── В: зайчик від дзеркальця ──
    f.append(text(840, 68, "Зайчик від дзеркальця", size=15, bold=True))
    f.append(text(720, 112, "дзеркальце", size=13, color=NEG))
    f.append(fork(734, 132, 196))
    f.append(rect(712, 120, 18, 9, fill="#cfe0ff", stroke=NEG, sw=1.6, rx=2))
    f.append(arrow(694, 186, 716, 136, POS, 1.8))
    f.append(arrow(730, 128, 866, 168, POS, 1.8))
    f.append(rect(872, 116, 108, 104, fill=BG, stroke=LINE, sw=1.5, rx=6))
    f.append(lissajous(926, 168, 36, 1, 1, math.radians(55), NEG, 1.8))
    f.append(text(926, 240, "екран", size=13, color=MUTED))
    f.append(fitbox(690, 312, 300, 56,
                    "дзеркальце майже нічого не додає,\nа промінь не важить нічого", size=13))
    f.append(fitbox(690, 378, 300, 34, "маса пензля: нуль", size=13,
                    fill="#e9f7ef", stroke=FIELD))

    render(os.path.join(IMG, "three-brushes.svg"), W, H, *f,
           title="Чим малювали коливання: чого вартий кожен пензель")


# ═════ Вставка proj-lissajous.md ═════════════════════════════════════════════

def _lp(cx, cy, Rx, Ry, delta, tau):
    """Точка еліпса Ліссажу 1:1 із різними півосями (піксельний y — донизу)."""
    return (cx + Rx * math.sin(tau + delta), cy - Ry * math.sin(tau))


def _lpath(cx, cy, Rx, Ry, delta, color, sw=2.2, n=720, t0=0.0, t1=2 * math.pi):
    pts = []
    for i in range(n + 1):
        tau = t0 + (t1 - t0) * i / n
        px, py = _lp(cx, cy, Rx, Ry, delta, tau)
        pts.append("%.2f,%.2f" % (px, py))
    return ('<polyline fill="none" stroke="%s" stroke-width="%.1f" stroke-linejoin="round" '
            'stroke-linecap="round" points="%s"/>' % (color, sw, " ".join(pts)))


def _travel(cx, cy, Rx, Ry, delta, taus, color=INK, sw=1.5, d=0.17):
    """Короткі стрілки на кривій — куди йде точка з ростом τ."""
    out = []
    for tau in taus:
        x0, y0 = _lp(cx, cy, Rx, Ry, delta, tau - d)
        x1, y1 = _lp(cx, cy, Rx, Ry, delta, tau + d)
        out.append(arrow(x0, y0, x1, y1, color, sw))
    return out


def _panel(cx, cy, half):
    return (rect(cx - half, cy - half, 2 * half, 2 * half, fill=BG, stroke=LINE, sw=1.5, rx=8)
            + line(cx - half + 3, cy, cx + half - 3, cy, MUTED, 0.8)
            + line(cx, cy - half + 3, cx, cy + half - 3, MUTED, 0.8))


# ── Вставка, фігура 1: форма дає модуль фази, обхід — знак ───────────────────
def fig_phase_sign():
    W, H = 960, 420
    half, Rx, Ry = 105, 88, 62
    f = []
    for cx, deg, lbl, area in ((250, 60, "φ = +60°", "площа > 0"),
                               (710, -60, "φ = −60°", "площа < 0")):
        d = math.radians(deg)
        f.append(_panel(cx, 175, half))
        f.append(_lpath(cx, 175, Rx, Ry, d, NEG, 2.3))
        f.extend(_travel(cx, 175, Rx, Ry, d, [0.5 * math.pi, 1.5 * math.pi], INK, 1.5))
        f.append(text(cx, 312, lbl, size=15, color=INK, bold=True))
        f.append(text(cx, 336, area, size=13, color=MUTED))
    mid, _, _ = textbox(480, 175, "та сама\nфігура", size=13, color=MUTED)
    f.append(mid)
    bot, _, _ = textbox(480, 382, "форма → |φ|   ·   напрям обходу → знак φ", size=15, bold=True)
    f.append(bot)
    render(os.path.join(IMG, "phase-sign.svg"), W, H, *f,
           title="Протилежні фази дають ту саму криву — різняться лише обходом")


# ── Вставка, фігура 2: вікно має бути цілим числом періодів ──────────────────
def fig_window_trim():
    W, H = 960, 440
    half, Rx, Ry = 105, 88, 62
    d = math.radians(30)
    f = []
    f.append(_panel(250, 175, half))
    f.append(_lpath(250, 175, Rx, Ry, d, NEG, 2.2))
    f.append(_lpath(250, 175, Rx, Ry, d, POS, 4.4, n=260, t0=0.0, t1=0.37 * 2 * math.pi))
    f.append(text(250, 312, "вікно 3.37 періоду", size=15, color=INK, bold=True))
    f.append(text(250, 335, "червону дугу пройдено двічі", size=12, color=POS))
    f.append(text(250, 360, "кореляція каже 29.32°", size=14, color=INK, bold=True))
    f.append(_panel(710, 175, half))
    f.append(_lpath(710, 175, Rx, Ry, d, NEG, 2.2))
    f.append(text(710, 312, "підрізано до 3 періодів", size=15, color=INK, bold=True))
    f.append(text(710, 335, "кожну дугу пройдено раз", size=12, color=FIELD))
    f.append(text(710, 360, "кореляція каже 30.00°", size=14, color=INK, bold=True))
    tb, _, _ = textbox(480, 122, "підрізати\nза перетинами нуля", size=12, color=INK)
    f.append(tb)
    f.append(arrow(378, 180, 582, 180, INK, 2.0))
    bot, _, _ = textbox(480, 404, "істина — 30.00°: зайва дуга тягне середнє добутку",
                        size=13, color=INK)
    f.append(bot)
    render(os.path.join(IMG, "window-trim.svg"), W, H, *f,
           title="Неціле вікно зміщує оцінку фази")


# ── Вставка, фігура 3: конвеєр читання ───────────────────────────────────────
def fig_read_pipeline():
    W, H = 1080, 420
    f = []
    inp, iw, ih = textbox(72, 235, "x[n]\ny[n]", size=14, bold=True)
    f.append(inp)

    def chain(items, cy):
        out, spans = [], []
        for cx, s, kw in items:
            b, w, h = textbox(cx, cy, s, size=13, **kw)
            out.append(b)
            spans.append((cx - w / 2, cx + w / 2))
        for i in range(len(spans) - 1):
            out.append(arrow(spans[i][1] + 7, cy, spans[i + 1][0] - 7, cy, INK, 1.8))
        return out, spans[0][0]

    row1, x1 = chain([(300, "перетини нуля\nз гістерезисом", {}),
                      (560, "ланцюговий дріб", {}),
                      (830, "p : q", {"bold": True, "min_w": 110})], 105)
    row2, x2 = chain([(280, "підрізати до\nцілих періодів", {}),
                      (555, "Σx², Σy², Σxy → cos φ", {}),
                      (830, "орієнтована\nплоща → знак", {}),
                      (1000, "φ", {"bold": True, "min_w": 80})], 235)
    row3, x3 = chain([(280, "φ по блоках", {}),
                      (555, "нахил Δφ/Δt", {}),
                      (830, "Δf = нахил / 2π", {"bold": True})], 365)
    f.extend(row1 + row2 + row3)
    f.append(arrow(72 + iw / 2 + 5, 222, x1 - 9, 118, INK, 1.8))
    f.append(arrow(72 + iw / 2 + 5, 235, x2 - 9, 235, INK, 1.8))
    f.append(arrow(72 + iw / 2 + 5, 248, x3 - 9, 352, INK, 1.8))
    f.append(text(x1, 62, "1 · відношення частот", size=12, color=MUTED,
                  anchor="start", italic=True))
    f.append(text(x2, 192, "2 · зсув фаз — лише коли 1 : 1", size=12, color=MUTED,
                  anchor="start", italic=True))
    f.append(text(x3, 322, "3 · дрейф", size=12, color=MUTED, anchor="start", italic=True))
    render(os.path.join(IMG, "read-pipeline.svg"), W, H, *f,
           title="Від двох масивів до трьох чисел")


if __name__ == "__main__":
    fig_construction()
    fig_phase_gallery()
    fig_ratio_gallery()
    fig_two_point_pendulum()
    fig_three_brushes()
    fig_phase_sign()
    fig_window_trim()
    fig_read_pipeline()
    print("OK: 8 SVG у", IMG)

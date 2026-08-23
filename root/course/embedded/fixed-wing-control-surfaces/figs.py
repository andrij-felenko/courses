# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def rot(cx, cy, dx, dy, deg):
    """Точка (dx,dy) відносно (cx,cy), повернута на deg градусів → абсолютні (x,y)."""
    a = math.radians(deg)
    return (cx + dx * math.cos(a) - dy * math.sin(a),
            cy + dx * math.sin(a) + dy * math.cos(a))


def apoly(pts, fill, stroke=INK, sw=1.5):
    """Полігон з абсолютних точок [(x,y),…]."""
    s = " ".join("%.1f,%.1f" % (px, py) for px, py in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (s, fill, stroke, sw))


# ── axes.svg : три осі й поверхні на схемі літака ───────────────────────────
def fig_axes():
    W, H = 720, 460
    fr = []
    fr.append(text(W/2, 28, "Три осі — три поверхні", size=17, bold=True))

    def poly(pts, fill, stroke=LINE, sw=1.6):
        s = " ".join("%.0f,%.0f" % (px, py) for px, py in pts)
        return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
                % (s, fill, stroke, sw))

    ael, ele, rud = POS, NEG, FIELD

    # ═══ ВИД ЗГОРИ (ліворуч) ═══
    fr.append(text(250, 58, "вид згори", size=12, color=MUTED))
    cx, cy = 250, 250          # центр планера (згори)
    fus_h = 135                # пів-довжина фюзеляжу
    span = 150                 # пів-розмах крила
    wx = cx - 18               # крило по фюзеляжу

    # фюзеляж + ніс
    fr.append(poly([(cx - fus_h, cy - 11), (cx + fus_h - 14, cy - 8),
                    (cx + fus_h, cy), (cx + fus_h - 14, cy + 8), (cx - fus_h, cy + 11)],
                   "#eef1f4"))
    fr.append(poly([(cx - fus_h, cy - 11), (cx - fus_h, cy + 11), (cx - fus_h - 20, cy)],
                   "#eef1f4"))
    # крило
    fr.append(poly([(wx + 22, cy - span), (wx + 54, cy - span),
                    (wx + 54, cy + span), (wx + 22, cy + span)], "#e3e8ee"))
    # горизонтальне оперення
    tx = cx + fus_h - 26
    fr.append(poly([(tx, cy - 54), (tx + 18, cy - 54),
                    (tx + 18, cy + 54), (tx, cy + 54)], "#e3e8ee"))

    # елерони (кінці крила, задня кромка)
    fr.append(rect(wx + 47, cy - span, 9, 38, fill="#fdecea", stroke=ael, sw=1.4, rx=2))
    fr.append(rect(wx + 47, cy + span - 38, 9, 38, fill="#fdecea", stroke=ael, sw=1.4, rx=2))
    # руль висоти (задня кромка хвоста)
    fr.append(rect(tx + 13, cy - 54, 7, 108, fill="#eaf0fd", stroke=ele, sw=1.4, rx=2))

    # осі крізь центр: поздовжня (крен) і поперечна (тангаж)
    fr.append(arrow(cx - fus_h - 26, cy, cx + fus_h + 24, cy, color=INK, sw=2.0))
    fr.append(arrow(wx + 38, cy - span - 24, wx + 38, cy + span + 24, color=INK, sw=2.0))
    fr.append(circle(cx, cy, 4, fill=INK, stroke=INK))
    fr.append(text(cx - fus_h - 26, cy - 8, "крен", size=11, color=MUTED, anchor="start"))
    fr.append(text(wx + 38, cy + span + 40, "тангаж", size=11, color=MUTED))

    # підписи поверхонь
    b, bw, bh = textbox(120, 110, ["Елерони — КРЕН", "різнойменно на", "кінцях крил"],
                        size=13, fill="#fdecea", stroke=ael, color=INK)
    fr.append(b)
    fr.append(line(120, 110 + bh/2, wx + 52, cy - span + 19, color=ael, sw=1.3, dash="4 3"))

    b, bw, bh = textbox(180, 415, ["Руль висоти —", "ТАНГАЖ (на хвості)"],
                        size=13, fill="#eaf0fd", stroke=ele, color=INK)
    fr.append(b)
    fr.append(line(180 + bw/2, 415 - bh/2, tx + 16, cy + 30, color=ele, sw=1.3, dash="4 3"))

    # ═══ ВИД ЗЗАДУ/ЗБОКУ (праворуч) — кіль і руль напряму ═══
    fr.append(text(560, 58, "вид збоку", size=12, color=MUTED))
    kx, ky = 500, 250
    # фюзеляж збоку
    fr.append(rect(kx, ky - 8, 150, 16, fill="#eef1f4", stroke=LINE, sw=1.4, rx=4))
    fr.append(poly([(kx, ky - 8), (kx, ky + 8), (kx - 18, ky)], "#eef1f4"))
    # кіль (вертикальне оперення) на хвості
    fr.append(poly([(kx + 116, ky - 8), (kx + 150, ky - 8), (kx + 150, ky - 62)],
                   "#e3e8ee", sw=1.4))
    # руль напряму (задня кромка кіля)
    fr.append(rect(kx + 150, ky - 62, 8, 54, fill="#eef7ef", stroke=rud, sw=1.5, rx=2))
    # вертикальна вісь
    fr.append(arrow(kx + 132, ky - 78, kx + 132, ky + 78, color=INK, sw=1.8))
    fr.append(text(kx + 132, ky + 96, "курс", size=11, color=MUTED))

    b, bw, bh = textbox(575, 410, ["Руль напряму —", "КУРС (на кілі)"],
                        size=13, fill="#eef7ef", stroke=rud, color=INK)
    fr.append(b)
    fr.append(line(575 + bw/2 - 20, 410 - bh/2, kx + 156, ky - 40, color=rud, sw=1.3, dash="4 3"))

    render(os.path.join(IMG, 'axes.svg'), W, H, *fr)


# ── turn.svg : руль-ковзання проти крен-дуги ────────────────────────────────
def fig_turn():
    W, H = 720, 400
    fr = []
    fr.append(text(W/2, 28, "Літак повертає креном, а не рулем", size=17, bold=True))

    # ── ліва панель: самий руль → ковзання ──
    lx = 180
    fr.append(text(lx, 62, "Самий руль напряму", size=13, bold=True, color=NEG))
    # траєкторія: майже пряма
    fr.append('<path d="M %d 340 Q %d 200 %d 130" fill="none" stroke="%s" '
              'stroke-width="2.4" stroke-dasharray="6 4"/>' % (lx - 70, lx - 30, lx + 5, MUTED))
    # силует літака, розвернутий носом убік, але повзе вгору (ковзання)
    def plane_glyph(px, py, ang, color):
        # фюзеляж (видовжений ромб) + крило (упоперек), у абсолютних точках
        fus = [rot(px, py, dx, dy, ang) for dx, dy in
               [(0, -22), (6, 10), (0, 4), (-6, 10)]]
        wing = [rot(px, py, dx, dy, ang) for dx, dy in
                [(-20, -4), (20, -4), (20, 3), (-20, 3)]]
        return apoly(wing, "#e3e8ee", stroke=color, sw=1.2) + \
               apoly(fus, "#e3e8ee", stroke=color, sw=1.4)
    # ніс дивиться праворуч (розвернутий ~35°), а рух — угору → бачимо ковзання
    fr.append(plane_glyph(lx + 5, 150, 35, NEG))
    # стрілка «куди летить» (вгору) і «куди дивиться ніс» (вбік)
    fr.append(arrow(lx + 5, 150, lx + 5, 96, color=INK, sw=1.8))
    fr.append(text(lx + 5, 88, "летить", size=11, color=INK))
    b, bw, bh = textbox(lx, 300, ["ніс розвернуто,", "але апарат повзе", "боком — ковзання"],
                        size=12, fill=FILL, stroke=NEG, color=INK)
    fr.append(b)

    # роздільна лінія
    fr.append(line(W/2, 50, W/2, 370, color="#dddddd", sw=1.2, dash="3 4"))

    # ── права панель: крен → чиста дуга ──
    rx = 540
    fr.append(text(rx, 62, "Крен елеронами", size=13, bold=True, color=POS))
    # дуга повороту (частина кола)
    fr.append('<path d="M %d 350 A 150 150 0 0 1 %d 120" fill="none" stroke="%s" '
              'stroke-width="2.6"/>' % (rx - 30, rx + 70, POS))
    # центр повороту
    fr.append(circle(rx + 150, 250, 3, fill=MUTED, stroke=MUTED))
    fr.append(text(rx + 150, 270, "центр дуги", size=11, color=MUTED))
    # літак у крені: вид ззаду (нахилений), вектор підйому нахилений
    bx, by = rx - 5, 200
    # крило як нахилений прямокутник у абсолютних точках
    wing = [rot(bx, by, dx, dy, 25) for dx, dy in
            [(-46, -4), (46, -4), (46, 4), (-46, 4)]]
    body = [rot(bx, by, dx, dy, 25) for dx, dy in
            [(-6, -14), (6, -14), (6, 0), (-6, 0)]]
    fr.append(apoly(wing, "#e3e8ee", stroke=POS, sw=1.4))
    fr.append(apoly(body, "#eef1f4", stroke=POS, sw=1.2))
    # вектор підіймальної сили — перпендикуляр до нахиленого крила
    a = math.radians(25)
    # «вгору» від крила, нахилене на 25°
    ux, uy = math.sin(a), -math.cos(a)
    fr.append(arrow(bx, by, bx + ux*70, by + uy*70, color=FIELD, sw=2.2))
    fr.append(text(bx + ux*70 + 6, by + uy*70 - 6, "підйом", size=11, color=FIELD, anchor="start"))
    # горизонтальна складова → в дугу
    fr.append(arrow(bx, by, bx + ux*70, by, color=INK, sw=1.6))
    fr.append(text(bx + ux*70/2, by + 18, "доосьова", size=10, color=INK))

    b, bw, bh = textbox(rx, 320, ["нахилений підйом дає", "бічну силу — чиста дуга;", "руль лише координує"],
                        size=12, fill=FILL, stroke=POS, color=INK)
    fr.append(b)

    render(os.path.join(IMG, 'turn.svg'), W, H, *fr)


# ── glider1902.svg : три осі керування планера 1902 та звʼязка руль↔перекос ──
def fig_glider1902():
    W, H = 720, 470
    fr = []
    fr.append(text(W/2, 26, "Планер братів Райт, 1902 — керування по трьох осях", size=16, bold=True))

    warp, elev, rud = POS, NEG, FIELD

    # ── силует біплана, вид у три-чверті (спрощений) ──
    # два крила як паралелограми (верхнє й нижнє), стійки між ними
    def wing(y, dx, tone):
        pts = [(210 + dx, y), (470 + dx, y), (455 + dx, y + 20), (195 + dx, y + 20)]
        return apoly(pts, tone, stroke=LINE, sw=1.4)
    fr.append(wing(120, 0,  "#e3e8ee"))        # верхнє крило
    fr.append(wing(215, 0,  "#eef1f4"))        # нижнє крило
    # стійки між крилами
    for xx in (215, 300, 385, 458):
        fr.append(line(xx, 140, xx, 235, color=MUTED, sw=1.2))

    # ── перекошування (wing-warping): кінці крил вивернуті у різні боки ──
    # лівий кінець угору (світлий клин), правий униз (темніший) — стрілки
    fr.append(arrow(205, 150, 205, 118, color=warp, sw=2.2))     # лівий кінець ↑
    fr.append(arrow(462, 205, 462, 238, color=warp, sw=2.2))     # правий кінець ↓
    b, bw, bh = textbox(120, 175, ["Перекошування", "крила — КРЕН", "(wing-warping)"],
                        size=12, fill="#fdecea", stroke=warp, color=INK)
    fr.append(b)
    fr.append(line(120 + bw/2, 175, 205, 138, color=warp, sw=1.2, dash="4 3"))

    # ── передній руль висоти (canard, попереду) ──
    fr.append(rect(150, 300, 120, 16, fill="#eaf0fd", stroke=elev, sw=1.5, rx=3))
    fr.append(arrow(210, 296, 210, 274, color=elev, sw=1.8))
    fr.append(arrow(210, 320, 210, 342, color=elev, sw=1.8))
    b, bw, bh = textbox(120, 380, ["Передній руль", "висоти — ТАНГАЖ", "(перед крилом!)"],
                        size=12, fill="#eaf0fd", stroke=elev, color=INK)
    fr.append(b)
    fr.append(line(120 + bw/2, 380 - bh/2, 175, 316, color=elev, sw=1.2, dash="4 3"))

    # ── задній руль напряму (за крилом) ──
    fr.append(rect(560, 150, 12, 70, fill="#eef7ef", stroke=rud, sw=1.6, rx=2))
    fr.append(line(470, 185, 560, 185, color=MUTED, sw=1.2))     # балка до хвоста
    fr.append(arrow(566, 150, 592, 150, color=rud, sw=1.7))
    fr.append(arrow(566, 220, 540, 220, color=rud, sw=1.7))
    b, bw, bh = textbox(605, 300, ["Задній руль", "напряму — КУРС"],
                        size=12, fill="#eef7ef", stroke=rud, color=INK)
    fr.append(b)
    fr.append(line(605, 300 - bh/2, 566, 210, color=rud, sw=1.2, dash="4 3"))

    # ── ГОЛОВНЕ: звʼязка руля з люлькою перекошування ──
    # пунктирний трос від перекосу (лівий кінець) до руля напряму
    fr.append('<path d="M 205 132 C 300 60, 520 70, 566 150" fill="none" '
              'stroke="%s" stroke-width="1.8" stroke-dasharray="7 4"/>' % INK)
    b, bw, bh = textbox(390, 55, ["Руль звʼязаний тросом із перекошуванням:", "один рух пілота — і крен, і руль разом",
                                  "(координований розворот без ковзання)"],
                        size=11.5, fill=FILL, stroke=INK, color=INK)
    fr.append(b)

    # люлька пілота (стегнова) — маленький прямокутник під нижнім крилом
    fr.append(rect(322, 240, 40, 14, fill="#ffffff", stroke=INK, sw=1.3, rx=3))
    fr.append(text(342, 268, "люлька під стегна пілота", size=10.5, color=MUTED))

    render(os.path.join(IMG, 'glider1902.svg'), W, H, *fr)


# ── bank-forces.svg : розклад підіймальної сили в крені ─────────────────────
def fig_bank_forces():
    W, H = 720, 470
    fr = []
    fr.append(text(W/2, 30, "Розклад підіймальної сили в крені φ", size=17, bold=True))

    # центр ваги літака (вид ЗЗАДУ), апарат нахилений праворуч на phi
    cx, cy = 335, 305
    phi = 38  # градусів крену для наочності

    # ── силует літака (вид ззаду), нахилений на phi праворуч ──
    wing = [rot(cx, cy, dx, dy, phi) for dx, dy in
            [(-92, -5), (92, -5), (92, 5), (-92, 5)]]
    fr.append(apoly(wing, "#e3e8ee", stroke=INK, sw=1.6))
    fr.append(circle(cx, cy, 11, fill="#eef1f4", stroke=INK, sw=1.6))

    # ── вертикаль угору від ЦВ (пунктир — «куди дивився б підйом без крену») ──
    fr.append(line(cx, cy, cx, cy - 190, color=MUTED, sw=1.3, dash="5 4"))
    fr.append(text(cx + 5, cy - 193, "вертикаль", size=11, color=MUTED, anchor="start"))

    # ── вектор підіймальної сили L: перпендикуляр до крила, нахилений на phi ──
    a = math.radians(phi)
    Lx, Ly = math.sin(a), -math.cos(a)      # «вгору» від крила, відхилене на phi
    Llen = 185
    tipx, tipy = cx + Lx*Llen, cy + Ly*Llen
    fr.append(arrow(cx, cy, tipx, tipy, color=FIELD, sw=2.6))
    fr.append(text(tipx + 9, tipy - 3, "L", size=15, color=FIELD, bold=True, anchor="start"))
    fr.append(text(tipx + 9, tipy + 14, "підйом", size=11, color=FIELD, anchor="start"))

    # ── вертикальна складова L·cos φ (від ЦВ угору до рівня вершини L) ──
    vy = cy + Ly*Llen                        # висота вершини L
    fr.append(arrow(cx, cy, cx, vy, color=NEG, sw=2.0))
    fr.append(text(cx - 10, (cy + vy)/2, "L·cos φ", size=12, color=NEG, anchor="end"))
    # горизонтальна складова L·sin φ (від вершини вертикальної складової до вершини L)
    fr.append(arrow(cx, vy, tipx, vy, color=POS, sw=2.0))
    fr.append(text((cx + tipx)/2, vy - 9, "L·sin φ", size=12, color=POS))
    fr.append(line(tipx, vy, tipx, tipy, color=MUTED, sw=1.0, dash="3 3"))

    # ── вага вниз ──
    fr.append(arrow(cx, cy, cx, cy + 125, color=INK, sw=2.2))
    fr.append(text(cx - 10, cy + 72, "вага W", size=12, color=INK, anchor="end"))

    # ── дуга кута phi між вертикаллю та L ──
    r_arc = 54
    a0 = math.radians(-90)                    # вертикаль угору
    a1 = math.radians(-90 + phi)              # напрям L
    p0 = (cx + r_arc*math.cos(a0), cy + r_arc*math.sin(a0))
    p1 = (cx + r_arc*math.cos(a1), cy + r_arc*math.sin(a1))
    fr.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
              'stroke="%s" stroke-width="1.6"/>' % (p0[0], p0[1], r_arc, r_arc, p1[0], p1[1], INK))
    fr.append(text(cx + 22, cy - r_arc - 4, "φ", size=15, color=INK, bold=True))
    # мітка напряму доосьової сили — під червоною стрілкою, праворуч
    fr.append(text(tipx - 4, vy + 15, "до центра →", size=10, color=POS, anchor="end"))

    # ── бічна довідкова рамка ──
    b, bw, bh = textbox(600, 165,
        ["Вертикаль тримає вагу:", "L·cos φ = W", "→ n = L/W = 1/cos φ", "",
         "Горизонталь — доосьова:", "F = L·sin φ = W·tan φ"],
        size=12, fill=FILL, stroke=LINE, color=INK)
    fr.append(b)

    render(os.path.join(IMG, 'bank-forces.svg'), W, H, *fr)


# ── bank-curves.svg : як крен роздуває перевантаження й тисне радіус ────────
def fig_bank_curves():
    W, H = 720, 440
    fr = []
    fr.append(text(W/2, 30, "Ціна крену: перевантаження n і радіус r", size=17, bold=True))

    x0, x1 = 95, 630
    phi_max = 75.0
    def px(phi):
        return x0 + (phi / phi_max) * (x1 - x0)

    yb, yt = 360, 72
    n_max = 4.0
    def py_n(n):
        return yb - (min(n, n_max) - 1.0) / (n_max - 1.0) * (yb - yt)

    # осі
    fr.append(arrow(x0, yb, x1 + 12, yb, color=INK, sw=1.6))
    fr.append(arrow(x0, yb, x0, yt - 10, color=INK, sw=1.6))
    fr.append(text(x1 + 10, yb - 8, "крен φ", size=12, color=INK, anchor="end"))
    fr.append(text(x0 + 6, yt - 16, "n = 1/cos φ", size=12, color=POS, anchor="start"))

    for phi in (0, 30, 45, 60, 75):
        xx = px(phi)
        fr.append(line(xx, yb, xx, yb + 5, color=INK, sw=1.2))
        fr.append(text(xx, yb + 21, "%d°" % phi, size=11, color=MUTED))
    for n in (1, 2, 3, 4):
        yy = py_n(n)
        fr.append(line(x0 - 5, yy, x0, yy, color=INK, sw=1.2))
        fr.append(text(x0 - 11, yy + 4, "%d" % n, size=11, color=MUTED, anchor="end"))

    # крива n = 1/cos φ
    pts = []
    p = 0.0
    while p <= phi_max + 0.01:
        n = 1.0 / math.cos(math.radians(p))
        pts.append((px(p), py_n(n)))
        p += 1.5
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    fr.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, POS))

    # маркер 60° → n=2
    x60, y60 = px(60), py_n(2.0)
    fr.append(line(x60, yb, x60, y60, color=POS, sw=1.0, dash="4 3"))
    fr.append(line(x0, y60, x60, y60, color=POS, sw=1.0, dash="4 3"))
    fr.append(circle(x60, y60, 4.5, fill=POS, stroke=POS))
    b, bw, bh = textbox(x60 - 78, y60 + 34, ["60° → n = 2:", "вага вдвічі"],
                        size=11, fill="#fdecea", stroke=POS, color=INK)
    fr.append(b)

    # радіус r ∝ 1/tan φ (крива NEG, схематично, нормована до rамки)
    fr.append(text(x1 + 8, yt - 16, "r ∝ 1/tan φ", size=12, color=NEG, anchor="end"))
    def py_r(ratio):
        rr = min(ratio, 3.0)
        return yb - (rr / 3.0) * (yb - yt)
    pts2 = []
    p = 18.0
    while p <= phi_max + 0.01:
        ratio = 1.0 / math.tan(math.radians(p))
        pts2.append((px(p), py_r(ratio)))
        p += 1.5
    d2 = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts2)
    fr.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" '
              'stroke-dasharray="7 4"/>' % (d2, NEG))

    b, bw, bh = textbox(W/2, 410,
        ["Малий крен: n майже 1, зате радіус величезний.",
         "Крутіший крен тисне радіус — ціною швидкого росту n."],
        size=11, fill=FILL, stroke=LINE, color=INK)
    fr.append(b)

    render(os.path.join(IMG, 'bank-curves.svg'), W, H, *fr)


# ════════════════════════════════════════════════════════════════════════════
#  ДЕТАЛЬНА СТАТТЯ (fixed-wing-control-surfaces-d.md) — п'ять нових фігур
# ════════════════════════════════════════════════════════════════════════════

# ── hinge-moment.svg : приріст сили vs шарнірний момент; аеродин. компенсація ─
def fig_hinge_moment():
    W, H = 760, 470
    fr = []
    fr.append(text(W/2, 28, "Дві сили однієї поверхні: приріст ΔL і шарнірний момент H", size=15.5, bold=True))

    # ═══ ЛІВА панель: звичайна вісь на кромці ═══
    fr.append(text(210, 60, "звичайна вісь шарніра", size=12, color=MUTED))
    # хорда профілю (спрощений профіль як витягнута лінза)
    px0, py0 = 70, 230          # передня кромка
    px1 = 320                    # де починається рухома поверхня (вісь)
    px2 = 400                    # задня кромка (у нейтралі)
    # тіло профілю
    fr.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d Z" fill="#eef1f4" stroke="%s" stroke-width="1.6"/>'
              % (px0, py0, (px0+px1)//2, py0-26, px1, py0-6,
                 (px0+px1)//2, py0+14, px0, py0, LINE))
    # нерухома верхня/нижня — просто підпис
    fr.append(text((px0+px1)//2, py0+40, "нерухома частина хорди", size=10.5, color=MUTED))

    # вісь шарніра
    fr.append(circle(px1, py0 - 2, 4.5, fill="#ffffff", stroke=INK, sw=1.8))
    fr.append(text(px1, py0 + 22, "вісь", size=10.5, color=INK))

    # відхилена вниз поверхня (від осі)
    ang = 24
    tipx, tipy = rot(px1, py0 - 2, px2 - px1, 8, ang)
    fr.append(apoly([(px1, py0 - 8), (px1, py0 + 4), (tipx, tipy)], "#fdecea", stroke=POS, sw=1.6))
    # кут δ
    fr.append('<path d="M %d %d A 46 46 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.4"/>'
              % (px1 + 46, py0 - 2, px1 + 46*math.cos(math.radians(ang)), py0 - 2 + 46*math.sin(math.radians(ang)), INK))
    fr.append(text(px1 + 58, py0 + 12, "δ", size=14, color=INK, bold=True, anchor="start"))

    # приріст підйому ΔL угору на ділянці поверхні
    mx = (px1 + tipx) / 2
    fr.append(arrow(mx, py0 + 2, mx, py0 - 66, color=FIELD, sw=2.4))
    fr.append(text(mx + 6, py0 - 60, "ΔL (літаку)", size=11, color=FIELD, anchor="start"))

    # центр тиску поверхні — позаду осі, і момент H назад у нейтраль
    cpx = px1 + (tipx - px1) * 0.55
    cpy = py0 + (tipy - (py0 - 2)) * 0.55
    fr.append(circle(cpx, cpy, 3, fill=POS, stroke=POS))
    fr.append(text(cpx + 4, cpy + 16, "центр тиску", size=10, color=POS, anchor="start"))
    # дугова стрілка H (обертання поверхні назад угору)
    fr.append('<path d="M %.1f %.1f A 34 34 0 0 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="2.0" marker-end="url(#arrow)"/>'
              % (tipx + 4, tipy - 6, px1 + 30, py0 - 30, INK))
    fr.append(text(tipx - 6, tipy + 22, "H — назад у нейтраль", size=10.5, color=INK, anchor="middle"))

    b, bw, bh = textbox(200, 400, ["ΔL = ½·ρ·V²·S·(a·τ·δ)  — сила літаку",
                                    "H  = ½·ρ·V²·S_c·c_c·C_h  — момент на серво",
                                    "обидва ∝ V²"],
                        size=11.5, fill=FILL, stroke=LINE, color=INK)
    fr.append(b)

    # роздільник
    fr.append(line(W/2 + 30, 50, W/2 + 30, 360, color="#dddddd", sw=1.2, dash="3 4"))

    # ═══ ПРАВА панель: аеродинамічна компенсація (вісь посунута назад) ═══
    fr.append(text(590, 60, "аеродинамічна компенсація", size=12, color=MUTED))
    qx0, qy0 = 470, 230
    qh = 560                      # вісь усередині поверхні (посунута назад)
    # тіло профілю
    fr.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d Z" fill="#eef1f4" stroke="%s" stroke-width="1.6"/>'
              % (qx0, qy0, (qx0+520)//2, qy0-24, 520, qy0-6, (qx0+520)//2, qy0+13, qx0, qy0, LINE))
    # вісь посунута під поверхню
    axx = 545
    fr.append(circle(axx, qy0 - 3, 4.5, fill="#ffffff", stroke=INK, sw=1.8))
    fr.append(text(axx, qy0 + 22, "вісь (назад)", size=10, color=INK))
    # поверхня: частина ПОПЕРЕДУ осі, частина ПОЗАДУ
    ang2 = 22
    behind_tip = rot(axx, qy0 - 3, 90, 7, ang2)
    ahead_tip  = rot(axx, qy0 - 3, -30, -6, ang2)
    fr.append(apoly([(axx, qy0 - 8), (axx, qy0 + 3), (behind_tip[0], behind_tip[1])], "#fdecea", stroke=POS, sw=1.5))
    fr.append(apoly([(axx, qy0 - 8), (axx, qy0 + 2), (ahead_tip[0], ahead_tip[1])], "#eaf0fd", stroke=NEG, sw=1.5))
    # сила позаду осі (крутить назад) і сила попереду (крутить вперед — зменшує H)
    fr.append(arrow(axx + 40, qy0 + 6, axx + 40, qy0 - 40, color=POS, sw=1.8))
    fr.append(text(axx + 44, qy0 - 34, "сила позаду", size=10, color=POS, anchor="start"))
    fr.append(arrow(axx - 16, qy0 - 4, axx - 16, qy0 - 40, color=NEG, sw=1.8))
    fr.append(text(axx - 20, qy0 - 44, "сила попереду", size=10, color=NEG, anchor="middle"))

    b, bw, bh = textbox(600, 400, ["Частина сили — ПОПЕРЕДУ осі:", "її момент віднімається від H.",
                                    "→ серво тримає менший момент"],
                        size=11, fill="#eef7ef", stroke=FIELD, color=INK)
    fr.append(b)

    render(os.path.join(IMG, 'hinge-moment.svg'), W, H, *fr)


# ── adverse-yaw-cures.svg : рискання й три ліки ─────────────────────────────
def fig_adverse_yaw_cures():
    W, H = 760, 500
    fr = []
    fr.append(text(W/2, 28, "Зворотне рискання й три способи його вгамувати", size=15.5, bold=True))

    def mini_wing(cx, cy, title, tone_l, tone_r, note, note_color):
        out = []
        out.append(text(cx, cy - 58, title, size=12.5, bold=True, color=INK))
        # крило згори: фюзеляж по центру, два піврозмахи
        out.append(rect(cx - 4, cy - 34, 8, 68, fill="#eef1f4", stroke=LINE, sw=1.3, rx=2))
        out.append(rect(cx - 70, cy - 6, 66, 12, fill="#e3e8ee", stroke=LINE, sw=1.3, rx=2))
        out.append(rect(cx + 4,  cy - 6, 66, 12, fill="#e3e8ee", stroke=LINE, sw=1.3, rx=2))
        # елерони на кінцях (кольором показуємо вниз/угору)
        out.append(rect(cx - 66, cy + 6, 30, 6, fill=tone_l, stroke=LINE, sw=1.0, rx=1))
        out.append(rect(cx + 36, cy + 6, 30, 6, fill=tone_r, stroke=LINE, sw=1.0, rx=1))
        return out, cx, cy

    # (1) звичайні: правий вниз (великий опір), ніс відвертає праворуч (проти лівого повороту)
    g, cx, cy = mini_wing(150, 140, "Звичайні елерони", "#dfe6ee", "#fbddd8", "", POS)
    fr += g
    # опір-вектори: малий на лівому (вгору), великий на правому (вниз)
    fr.append(arrow(cx - 51, cy + 30, cx - 51, cy + 48, color=MUTED, sw=1.6))
    fr.append(arrow(cx + 51, cy + 30, cx + 51, cy + 60, color=POS, sw=2.4))
    fr.append(text(cx + 51, cy + 74, "великий опір", size=9.5, color=POS))
    # ніс відвертає праворуч
    fr.append('<path d="M %d %d q 40 -6 60 8" fill="none" stroke="%s" stroke-width="2.0" marker-end="url(#arrow)"/>'
              % (cx, cy - 40, POS))
    fr.append(text(cx + 70, cy - 40, "ніс → проти", size=10, color=POS, anchor="start"))

    # (2) диференціальні: правий опускається МЕНШЕ → опори близькі
    g, cx, cy = mini_wing(400, 140, "Диференціальні (2:1)", "#dfe6ee", "#f0e6e4", "", INK)
    fr += g
    fr.append(arrow(cx - 51, cy + 30, cx - 51, cy + 50, color=MUTED, sw=1.8))
    fr.append(arrow(cx + 51, cy + 30, cx + 51, cy + 52, color=MUTED, sw=1.8))
    fr.append(text(cx, cy + 74, "опори майже рівні", size=9.5, color=INK))

    # (3) Фрайз: піднятий лівий носик униз у потік → опір на ВНУТРІШНЬОМУ крилі
    g, cx, cy = mini_wing(630, 140, "Елерон Фрайза", "#d8e6f0", "#e3e8ee", "", FIELD)
    fr += g
    # носик виступає під ліве крило
    fr.append(apoly([(cx - 66, cy + 6), (cx - 70, cy + 18), (cx - 60, cy + 12)], "#eaf0fd", stroke=NEG, sw=1.4))
    fr.append(arrow(cx - 64, cy + 20, cx - 64, cy + 40, color=FIELD, sw=2.2))
    fr.append(text(cx - 64, cy + 54, "носик додає", size=9.5, color=FIELD))
    fr.append(text(cx - 64, cy + 66, "опір у поворот", size=9.5, color=FIELD))

    # ── графік C_L² унизу: чому саме квадрат ──
    gx0, gx1 = 130, 470
    gyb, gyt = 460, 320
    fr.append(text(300, 300, "Індукований опір ∝ C_L²  — чому опущений елерон коштує так дорого",
                   size=12, bold=True))
    fr.append(arrow(gx0, gyb, gx1 + 12, gyb, color=INK, sw=1.5))
    fr.append(arrow(gx0, gyb, gx0, gyt - 8, color=INK, sw=1.5))
    fr.append(text(gx1 + 6, gyb + 20, "локальний C_L", size=11, color=INK, anchor="end"))
    fr.append(text(gx0 + 4, gyt - 12, "опір", size=11, color=INK, anchor="start"))
    # парабола
    pts = []
    i = 0.0
    while i <= 1.0001:
        gx = gx0 + i * (gx1 - gx0)
        gy = gyb - (i*i) * (gyb - gyt)
        pts.append((gx, gy))
        i += 0.04
    d = "M " + " L ".join("%.1f %.1f" % (a, b) for a, b in pts)
    fr.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, INK))
    # дві точки: піднятий (низький C_L, малий опір), опущений (високий C_L, великий опір)
    def at(i):
        return gx0 + i*(gx1-gx0), gyb - (i*i)*(gyb-gyt)
    ax_, ay_ = at(0.45); bx_, by_ = at(0.85)
    fr.append(circle(ax_, ay_, 4.5, fill=NEG, stroke=NEG))
    fr.append(text(ax_ - 6, ay_ - 8, "піднятий", size=9.5, color=NEG, anchor="end"))
    fr.append(circle(bx_, by_, 4.5, fill=POS, stroke=POS))
    fr.append(text(bx_ + 8, by_ + 2, "опущений", size=9.5, color=POS, anchor="start"))
    fr.append(line(ax_, ay_, ax_, gyb, color=NEG, sw=0.9, dash="3 3"))
    fr.append(line(bx_, by_, bx_, gyb, color=POS, sw=0.9, dash="3 3"))

    b, bw, bh = textbox(628, 400, ["Опущений елерон стрибає високо",
                                    "по кривій C_L² — його опір",
                                    "непропорційно більший.",
                                    "Диференціал і Фрайз б'ють",
                                    "саме цей доданок опору."],
                        size=11, fill=FILL, stroke=LINE, color=INK)
    fr.append(b)

    render(os.path.join(IMG, 'adverse-yaw-cures.svg'), W, H, *fr)


# ── aileron-reversal.svg : аеропружний реверс елеронів ──────────────────────
def fig_aileron_reversal():
    W, H = 740, 440
    fr = []
    fr.append(text(W/2, 28, "Реверс елеронів: коли скрут крила перемагає", size=15.5, bold=True))

    def wing_case(cx, cy, title, twist_deg, up, note, ncol):
        out = []
        out.append(text(cx, cy - 96, title, size=13, bold=True, color=INK))
        # переріз крила (профіль), нахилений на twist_deg (скрут носом униз = від'ємний кут)
        prof = [rot(cx, cy, dx, dy, twist_deg) for dx, dy in
                [(-60, 0), (-20, -18), (40, -6), (60, 4), (10, 12), (-60, 0)]]
        out.append(apoly(prof, "#eef1f4", stroke=INK, sw=1.6))
        # вісь скруту (точка) ближче до передньої третини
        ax_, ay_ = rot(cx, cy, -10, -2, twist_deg)
        out.append(circle(ax_, ay_, 4, fill="#ffffff", stroke=INK, sw=1.6))
        out.append(text(ax_ - 8, ay_ - 10, "вісь скруту", size=9.5, color=MUTED, anchor="end"))
        # опущений елерон на задній кромці
        el0 = rot(cx, cy, 40, -6, twist_deg); el1 = rot(cx, cy, 60, 4, twist_deg)
        eld = rot(cx, cy, 66, 20, twist_deg)
        out.append(apoly([el0, el1, eld], "#fdecea", stroke=POS, sw=1.5))
        # сила приросту від елерона — позаду осі
        fx_, fy_ = rot(cx, cy, 45, -6, twist_deg)
        out.append(arrow(fx_, fy_, fx_, fy_ - 46, color=POS, sw=2.0))
        out.append(text(fx_ + 4, fy_ - 40, "приріст сили", size=9.5, color=POS, anchor="start"))
        # напрям скруту (дугова стрілка навколо осі)
        if twist_deg < 0:
            out.append('<path d="M %.1f %.1f A 26 26 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
                       % (ax_ + 26, ay_, ax_ + 6, ay_ - 25, MUTED))
            out.append(text(ax_ + 34, ay_ + 14, "скрут носом ↓", size=9.5, color=MUTED, anchor="start"))
        # підсумковий вектор підйому крила
        out.append(arrow(cx - 6, cy + 2, cx - 6, cy + (-64 if up else 52), color=FIELD if up else POS, sw=2.6))
        out.append(text(cx - 6, cy + (-72 if up else 68), note, size=11, bold=True,
                        color=FIELD if up else POS))
        return out

    fr += wing_case(200, 220, "Нижче швидкості реверсу", -6, True, "крило ВГОРУ", FIELD)
    fr += wing_case(540, 220, "Вище швидкості реверсу", -20, False, "крило ВНИЗ", POS)

    fr.append(line(W/2, 60, W/2, 400, color="#dddddd", sw=1.2, dash="3 4"))

    b, bw, bh = textbox(W/2, 415,
        ["Момент скруту ∝ V², жорсткість крила — стала. На швидкості реверсу скрут віднімає стільки ж підйому,",
         "скільки елерон додав; вище — більше: Cl_δa проходить нуль і міняє знак. Реверсом у коді це не виправити."],
        size=10.5, fill=FILL, stroke=LINE, color=INK)
    fr.append(b)

    render(os.path.join(IMG, 'aileron-reversal.svg'), W, H, *fr)


# ── mixing-matrix.svg : мікшер як s = M·u для трьох схем ────────────────────
def fig_mixing_matrix():
    W, H = 760, 500
    fr = []
    fr.append(text(W/2, 28, "Мікшер — це множення на матрицю:  s = M · u", size=16, bold=True))

    # вхідний вектор команд (спільний для всіх)
    b, bw, bh = textbox(110, 90, ["Команди осей u", "[ roll ]", "[ pitch ]", "[ yaw ]"],
                        size=12, fill="#eef7ef", stroke=FIELD, color=INK, bold=False)
    fr.append(b)
    fr.append(text(110, 130, "від контролера (−1…+1)", size=10, color=MUTED))

    def matrix_row(y, name, rows, out_labels, note):
        out = []
        # рамка матриці
        mx = 300
        out.append(text(mx - 60, y - 30, name, size=12.5, bold=True, color=INK, anchor="start"))
        # дужки матриці
        mh = 20 * len(rows) + 14
        my = y - mh/2
        out.append('<path d="M %d %d q -8 0 -8 8 v %d q 0 8 8 8" fill="none" stroke="%s" stroke-width="1.6"/>'
                   % (mx - 44, my, mh - 16, INK))
        out.append('<path d="M %d %d q 8 0 8 8 v %d q 0 8 -8 8" fill="none" stroke="%s" stroke-width="1.6"/>'
                   % (mx + 44, my, mh - 16, INK))
        for i, r in enumerate(rows):
            yy = y - (len(rows)-1)*10 + i*20
            out.append(text(mx, yy + 4, r, size=12, color=INK))
        # стрілка → виходи
        out.append(arrow(mx + 60, y, mx + 120, y, color=INK, sw=1.8))
        # виходи
        bx = mx + 130
        bb, bw2, bh2 = textbox(bx + 60, y, out_labels, size=11.5, fill="#fdecea", stroke=POS, color=INK)
        out.append(bb)
        # примітка
        out.append(text(mx, y + mh/2 + 16, note, size=10, color=MUTED))
        return out

    fr += matrix_row(150, "Звичайний літак",
                     ["1  0  0", "0  1  0", "0  0  1"],
                     ["ail  = roll", "ele  = pitch", "rud  = yaw"],
                     "кожна вісь → своя поверхня (одинична M)")

    fr += matrix_row(280, "Елевони (крило)",
                     ["+1  +1   0", "-1  +1   0"],
                     ["left  = +roll+pitch", "right = -roll+pitch"],
                     "крен різними знаками, тангаж — спільно")

    fr += matrix_row(400, "V-подібний хвіст",
                     ["0  +1  +1", "0  +1  -1"],
                     ["left  = +pitch+yaw", "right = +pitch-yaw"],
                     "тангаж синхронно, курс різнойменно")

    # плата V-хвоста
    b, bw, bh = textbox(W/2, 465,
        ["Геометрична плата V-хвоста: поверхня під кутом Γ (≈30°) віддає в тангаж лише cos Γ, у курс — sin Γ,",
         "тож керморулі мусять ходити більше. Уся відмінність апаратів — у матриці M; контролер незмінний."],
        size=10.5, fill=FILL, stroke=LINE, color=INK)
    fr.append(b)

    render(os.path.join(IMG, 'mixing-matrix.svg'), W, H, *fr)


# ── expo-curve.svg : rates і expo ───────────────────────────────────────────
def fig_expo_curve():
    W, H = 720, 470
    fr = []
    fr.append(text(W/2, 28, "Криві ходу: expo гне центр, rate звужує хід", size=16, bold=True))

    # осі: команда (x) → вихід (y), обидві −1..+1, центр графіка
    cx, cy = 300, 250
    R = 175
    # рамка осей
    fr.append(arrow(cx - R - 12, cy, cx + R + 12, cy, color=INK, sw=1.5))
    fr.append(arrow(cx, cy + R + 12, cx, cy - R - 12, color=INK, sw=1.5))
    fr.append(text(cx + R + 10, cy - 10, "команда x", size=11, color=INK, anchor="end"))
    fr.append(text(cx - 10, cy - R - 4, "вихід y", size=11, color=INK, anchor="end"))
    # мітки країв
    for sx, lbl in [(-1, "−1"), (1, "+1")]:
        fr.append(line(cx + sx*R, cy - 4, cx + sx*R, cy + 4, color=INK, sw=1.2))
        fr.append(text(cx + sx*R, cy + 20, lbl, size=10, color=MUTED))
    for sy, lbl in [(-1, "−1"), (1, "+1")]:
        fr.append(line(cx - 4, cy - sy*R, cx + 4, cy - sy*R, color=INK, sw=1.2))
        fr.append(text(cx - 12, cy - sy*R + 4, lbl, size=10, color=MUTED, anchor="end"))

    def curve(e, color, sw, dash=None):
        pts = []
        x = -1.0
        while x <= 1.0001:
            y = e*x*x*x + (1.0 - e)*x
            pts.append((cx + x*R, cy - y*R))
            x += 0.03
        d = "M " + " L ".join("%.1f %.1f" % (a, b) for a, b in pts)
        da = ' stroke-dasharray="%s"' % dash if dash else ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, color, sw, da)

    fr.append(curve(0.0, MUTED, 1.8, dash="5 4"))   # лінійно
    fr.append(curve(0.5, NEG, 2.4))                  # помірне expo
    fr.append(curve(1.0, POS, 2.4))                  # чистий куб

    # підписи кривих — у верхньому-правому квадранті, кожен на своїй вітці, рознесені
    fr.append(text(cx + R*0.78, cy - R*0.70, "e=0 (лінійно)", size=10, color=MUTED, anchor="start"))
    fr.append(text(cx + R*0.80, cy - R*0.50, "e=0.5", size=10.5, color=NEG, bold=True, anchor="start"))
    fr.append(text(cx + R*0.80, cy - R*0.24, "e=1 (куб)", size=10.5, color=POS, bold=True, anchor="start"))

    # три нерухомі точки: −1, 0, +1
    for sx in (-1, 0, 1):
        fr.append(circle(cx + sx*R, cy - sx*R, 3.5, fill=INK, stroke=INK))
    # підпис нерухомих точок — у нижньому-лівому квадранті, подалі від кривих-підписів
    fr.append(text(cx - R*0.30, cy + R*0.40, "центр і краї — спільні", size=9.5, color=INK, anchor="middle"))

    # rate: підрізана крива згори (окрема тонка)
    def curve_rate(e, rate, color):
        pts = []
        x = -1.0
        while x <= 1.0001:
            y = (e*x*x*x + (1.0 - e)*x) * rate
            pts.append((cx + x*R, cy - y*R))
            x += 0.03
        d = "M " + " L ".join("%.1f %.1f" % (a, b) for a, b in pts)
        return '<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="2 3"/>' % (d, color)
    fr.append(curve_rate(0.5, 0.6, FIELD))
    fr.append(text(cx + R + 4, cy - 0.6*R*0.5, "rate=0.6", size=10, color=FIELD, anchor="start"))

    # пояснювальна рамка
    b, bw, bh = textbox(600, 190, ["y = e·x³ + (1−e)·x", "",
                                    "куб гне ЦЕНТР вниз", "(млявіший біля нейтралі),",
                                    "а КРАЇ нерухомі, бо", "x³ = x у −1, 0, +1.", "",
                                    "rate<1 масштабує все —", "звужує повний хід."],
                        size=11, fill=FILL, stroke=LINE, color=INK)
    fr.append(b)

    render(os.path.join(IMG, 'expo-curve.svg'), W, H, *fr)


if __name__ == '__main__':
    fig_axes()
    fig_turn()
    fig_glider1902()
    fig_bank_forces()
    fig_bank_curves()
    # детальна стаття:
    fig_hinge_moment()
    fig_adverse_yaw_cures()
    fig_aileron_reversal()
    fig_mixing_matrix()
    fig_expo_curve()
    print("ok: base + detailed figures")

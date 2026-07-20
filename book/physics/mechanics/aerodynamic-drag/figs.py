# -*- coding: utf-8 -*-
"""Фігури до теми «Аеродинамічний опір».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

VEL  = "#c0392b"   # швидкість / набігаючий потік — гаряче червоне
DRAG = "#2457d6"   # сила опору — холодне синє
WT   = "#27ae60"   # вага — зелене
WAKE = "#eef1f4"   # слід за тілом — світло-сіре
HI   = "#c0392b"   # високий тиск (+)
LO   = "#2457d6"   # низький тиск (−)


def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, fill, stroke, sw, da))


# ── Фігура 1: звідки береться опір — тіло вимітає стовп повітря ──────────────
def fig_drag_origin():
    W, H = 900, 430
    f = [text(W / 2, 30, "Опір — це ціна щосекундного розштовхування повітря", size=16, bold=True)]

    yTop, yBot = 150, 290          # межі лобової площі A
    xCol0, xCol1 = 215, 470        # стовп повітря, що надлітає за час Δt

    # набігаючий потік — стрілки зліва
    for yy in (170, 220, 270):
        f.append(arrow(70, yy, 165, yy, color=VEL, sw=2.6))
    f.append(text(72, 128, "набігаюче повітря (густина ρ)", size=12.5, color=VEL, anchor="start"))

    # стовп повітря
    f.append(rect(xCol0, yTop, xCol1 - xCol0, yBot - yTop, fill="#fdf0ef", stroke=VEL, sw=1.6, rx=4))
    f.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.4" stroke-dasharray="4,5"/>'
             % (xCol0, yTop, xCol0, yBot, VEL))
    f.append(text((xCol0 + xCol1) / 2, 215, "повітря, що надлітає", size=13, color=INK))
    f.append(text((xCol0 + xCol1) / 2, 235, "за час Δt", size=13, color=INK))

    # висота = лобова площа A
    f.append(arrow(xCol0 - 22, yTop, xCol0 - 22, yBot, color=INK, sw=1.8))
    f.append(arrow(xCol0 - 22, yBot, xCol0 - 22, yTop, color=INK, sw=1.8))
    f.append(text(xCol0 - 34, (yTop + yBot) / 2, "A", size=15, bold=True, anchor="end"))

    # довжина стовпа = v·Δt
    f.append(arrow(xCol0, yBot + 26, xCol1, yBot + 26, color=INK, sw=1.8))
    f.append(arrow(xCol1, yBot + 26, xCol0, yBot + 26, color=INK, sw=1.8))
    f.append(text((xCol0 + xCol1) / 2, yBot + 44, "довжина v·Δt", size=13))

    # тіло
    f.append(rect(482, 172, 58, 96, fill="#f4f6f8", stroke=INK, sw=2, rx=10))
    f.append(text(511, 224, "тіло", size=12, color=MUTED))

    # відхилений потік за тілом
    f.append(path("M 548 185 Q 610 170 660 150", stroke=VEL, sw=1.8, dash="3,5"))
    f.append(path("M 548 255 Q 610 270 660 290", stroke=VEL, sw=1.8, dash="3,5"))

    # сила опору на тіло
    f.append(arrow(548, 220, 665, 220, color=DRAG, sw=3.4))
    f.append(text(672, 216, "F — опір", size=14, bold=True, color=DRAG, anchor="start"))

    # підсумкова формула
    box, bw, bh = textbox(W / 2, 388,
                          "маса за секунду = ρ·A·v   →   віддача  F ∝ (ρ·A·v)·v = ρ·A·v²",
                          size=14, pad=12, fill="#eef7f0", stroke=WT, bold=False)
    f.append(box)
    render(os.path.join(IMG, "drag-origin.svg"), W, H, *f)


# ── Фігура 2: дві складові опору — тертя об шкіру й тиск форми ───────────────
def fig_friction_vs_form():
    W, H = 940, 480
    f = [text(W / 2, 30, "Дві складові опору: тертя об поверхню і тиск форми", size=16, bold=True)]
    f.append(line(470, 58, 470, 430, color="#dfe4ea", sw=1.2, dash="4,6"))

    # ── ЛІВОРУЧ: тупе тіло, широкий слід ──
    f.append(text(235, 74, "Тупе тіло", size=14, bold=True))
    cx, cy, r = 215, 250, 50
    # набігаючий потік
    for yy in (205, 250, 295):
        f.append(arrow(70, yy, 150, yy, color=VEL, sw=2.4))
    # високий тиск спереду
    f.append(plus(150, 220))
    f.append(plus(150, 280))
    f.append(text(96, 340, "тиск високий (+)", size=12, color=HI, anchor="start"))
    # тіло
    f.append(circle(cx, cy, r, fill="#f4f6f8", stroke=INK, sw=2))
    # слід (широкий, розхідний)
    f.append('<path d="M %d %d L %d %d L %d %d L %d %d Z" fill="%s" stroke="%s" '
             'stroke-width="1.2" stroke-dasharray="4,5"/>'
             % (cx + 44, cy - 26, 428, 178, 428, 322, cx + 44, cy + 26, WAKE, MUTED))
    # завихрення у сліді
    f.append(path("M 300 215 q 16 14 0 28 q -16 14 0 28", stroke=MUTED, sw=1.4))
    f.append(path("M 350 210 q 18 16 0 32 q -18 16 0 32", stroke=MUTED, sw=1.4))
    f.append(minus(392, 230))
    f.append(minus(392, 272))
    f.append(text(345, 150, "широкий слід — тиск низький (−)", size=12, color=LO))
    f.append(text(235, 420, "панує опір форми", size=13, bold=True, color=INK))

    # ── ПРАВОРУЧ: обтічне тіло ──
    f.append(text(700, 74, "Обтічне тіло", size=14, bold=True))
    for yy in (205, 250, 295):
        f.append(arrow(505, yy, 560, yy, color=VEL, sw=2.4))
    tear = ("M 560 250 Q 605 205 680 214 Q 785 226 848 250 "
            "Q 785 274 680 286 Q 605 295 560 250 Z")
    f.append(path(tear, fill="#f4f6f8", stroke=INK, sw=2))
    # потік тримається поверхні
    f.append(path("M 560 213 Q 660 178 780 205 Q 830 218 862 240", stroke=VEL, sw=1.7, dash="3,5"))
    f.append(path("M 560 287 Q 660 322 780 295 Q 830 282 862 260", stroke=VEL, sw=1.7, dash="3,5"))
    # дрібні дотичні стрілочки — поверхневе тертя
    for (ax, ay, bx, by) in [(632, 224, 660, 220), (700, 222, 728, 221),
                             (632, 276, 660, 280), (700, 278, 728, 279)]:
        f.append(arrow(ax, ay, bx, by, color=WT, sw=1.8))
    f.append(text(700, 150, "потік тримається, слід вузький", size=12, color=INK))
    f.append(text(700, 350, "тертя об поверхню (зелене)", size=12, color=WT))
    f.append(text(700, 420, "лишається майже саме тертя", size=13, bold=True, color=INK))

    render(os.path.join(IMG, "friction-vs-form.svg"), W, H, *f)


# ── Фігура 3: коефіцієнт опору різних тіл ────────────────────────────────────
def fig_cd_shapes():
    W, H = 880, 400
    f = [text(W / 2, 30, "Коефіцієнт опору C_d: та сама лобова площа, різна форма", size=16, bold=True)]

    rows = [
        ("плоска пластина впоперек", 1.28),
        ("куб гранню вперед",        1.05),
        ("куля",                     0.47),
        ("автомобіль",               0.30),
        ("обтічна крапля",           0.04),
    ]
    x0 = 300               # старт смуг
    xmax = 840             # кінець найдовшої смуги
    scale = (xmax - x0) / 1.30
    y = 92
    for name, cd in rows:
        f.append(text(28, y + 5, name, size=13, anchor="start"))
        bw = cd * scale
        col = VEL if cd >= 1.0 else (MUTED if cd >= 0.3 else WT)
        f.append(rect(x0, y - 13, max(bw, 3), 26, fill=col, stroke="none", sw=0, rx=4))
        f.append(text(x0 + max(bw, 3) + 10, y + 5, "%.2f" % cd, size=13, bold=True, anchor="start"))
        y += 58
    f.append(line(x0, 74, x0, y - 40, color=MUTED, sw=1.2, dash="3,4"))
    f.append(text((x0 + xmax) / 2, 372, "довша смуга — дужчий опір за тієї самої площі й швидкості", size=12, color=MUTED))
    render(os.path.join(IMG, "cd-shapes.svg"), W, H, *f)


# ── Фігура 4: термінальна швидкість ─────────────────────────────────────────
def fig_terminal_velocity():
    W, H = 900, 430
    f = [text(W / 2, 30, "Термінальна швидкість: опір доростає до ваги — розгін спиняється", size=15.5, bold=True)]
    f.append(line(430, 58, 430, 400, color="#dfe4ea", sw=1.2, dash="4,6"))

    # ── ЛІВОРУЧ: баланс сил ──
    cx, cy = 205, 205
    f.append(circle(cx, cy, 26, fill="#f4f6f8", stroke=INK, sw=2))
    # опір угору (росте з v²)
    f.append(arrow(cx, cy - 30, cx, cy - 118, color=DRAG, sw=3.2))
    f.append(text(cx + 14, cy - 96, "опір  ½ρC_dAv²", size=13, bold=True, color=DRAG, anchor="start"))
    f.append(text(cx + 14, cy - 78, "(росте з v²)", size=12, color=DRAG, anchor="start"))
    # вага вниз (стала)
    f.append(arrow(cx, cy + 30, cx, cy + 118, color=WT, sw=3.2))
    f.append(text(cx + 14, cy + 84, "вага  m·g", size=13, bold=True, color=WT, anchor="start"))
    f.append(text(cx + 14, cy + 102, "(стала)", size=12, color=WT, anchor="start"))
    f.append(text(205, 388, "опір = вага  →  a = 0,  v стала", size=13, bold=True))

    # ── ПРАВОРУЧ: крива v(t) ──
    ox, oy = 500, 350      # початок осей
    ex, ey = 855, 95       # кінці осей
    vt = 155               # рівень асимптоти (y)
    f.append(arrow(ox, oy, ox, ey, color=INK, sw=1.8))     # вісь v
    f.append(arrow(ox, oy, ex, oy, color=INK, sw=1.8))     # вісь t
    f.append(text(ox - 12, ey + 4, "v", size=14, bold=True, anchor="end"))
    f.append(text(ex + 6, oy + 5, "t", size=14, bold=True, anchor="start"))
    # асимптота v_t
    f.append(line(ox, vt, ex, vt, color=DRAG, sw=1.5, dash="5,5"))
    f.append(text(ex + 6, vt + 5, "v_t", size=13, bold=True, color=DRAG, anchor="start"))
    # крива виходу на термінальну
    f.append(path("M %d %d C %d %d %d %d %d %d" % (ox, oy, ox + 70, oy - 130, ox + 150, vt + 8, ex, vt + 3),
                  stroke=VEL, sw=3))
    f.append(text(675, 388, "швидкість виходить на сталу — термінальну", size=12.5, color=MUTED))

    render(os.path.join(IMG, "terminal-velocity.svg"), W, H, *f)


# ── Фігура 5 (hist): часова лінія ідеї опору ─────────────────────────────────
def fig_drag_history_timeline():
    W, H = 1040, 500
    f = [text(W / 2, 32, "Як людство вчилося рахувати опір повітря", size=17, bold=True)]
    axisY = 285
    f.append(line(96, axisY, 944, axisY, color=INK, sw=2.6))
    f.append(arrow(920, axisY, 950, axisY, color=INK, sw=2.6))

    nodes = [140, 330, 520, 710, 900]
    years = ["1687", "1749 · 1768", "1846", "1904", "1912 · 1914"]
    miles = [
        (["Ньютон · Англія", "«удар частинок»,", "опір ∝ ρ·v²·A"], True,  MUTED),
        (["д'Аламбер · Франція", "ідеальна рідина —", "опір рівно нуль"], False, DRAG),
        (["Сен-Венан · Франція", "винна знехтувана", "в'язкість"], True,  MUTED),
        (["Прандтль · Німеччина", "примежовий шар —", "парадокс знято"], False, WT),
        (["Ейфель · Франція", "+ Прандтль:", "криза опору кулі"], True,  VEL),
    ]
    for nx, yr, (lines, above, col) in zip(nodes, years, miles):
        f.append(circle(nx, axisY, 8, fill=col, stroke=INK, sw=1.8))
        if above:
            box, bw, bh = textbox(nx, 150, lines, size=13, pad=11,
                                  fill=BG, stroke=col, sw=1.9)
            f.append(line(nx, axisY - 8, nx, 150 + bh / 2 + 6, color=MUTED, sw=1.4, dash="3,4"))
            f.append(box)
            f.append(text(nx, axisY + 30, yr, size=14.5, bold=True, color=INK))
        else:
            box, bw, bh = textbox(nx, 415, lines, size=13, pad=11,
                                  fill=BG, stroke=col, sw=1.9)
            f.append(line(nx, axisY + 8, nx, 415 - bh / 2 - 6, color=MUTED, sw=1.4, dash="3,4"))
            f.append(box)
            f.append(text(nx, axisY - 18, yr, size=14.5, bold=True, color=INK))
    render(os.path.join(IMG, "drag-history-timeline.svg"), W, H, *f)


# ── Фігура 6 (hist): парадокс д'Аламбера і його розв'язання ──────────────────
def fig_dalembert_paradox():
    W, H = 1000, 480
    f = [text(W / 2, 30, "Парадокс д'Аламбера і як його зняв примежовий шар", size=16, bold=True)]
    f.append(line(500, 60, 500, 452, color="#dfe4ea", sw=1.2, dash="4,6"))

    # ── ЛІВОРУЧ: ідеальна нев'язка рідина — симетрія, опір нуль ──
    f.append(text(250, 84, "Ідеальна рідина — без в'язкості", size=14, bold=True))
    cx, cy, r = 250, 250, 52
    for yy in (210, 250, 290):
        f.append(arrow(58, yy, 148, yy, color=VEL, sw=2.4))
    # симетричні лінії течії: розходяться й знову змикаються дзеркально
    f.append(path("M 118 205 Q 250 138 382 205", stroke=VEL, sw=1.7))
    f.append(path("M 118 295 Q 250 362 382 295", stroke=VEL, sw=1.7))
    f.append(circle(cx, cy, r, fill=FILL, stroke=INK, sw=2))
    f.append(plus(cx - r - 12, cy))          # лоб — високий тиск
    f.append(plus(cx + r + 12, cy))          # КОРМА — теж високий (ось у чому суть)
    f.append(minus(cx, cy - r - 12))         # боки — низький
    f.append(minus(cx, cy + r + 12))
    f.append(text(cx + r + 12, cy - r - 6, "ззаду тиск", size=11, color=HI, anchor="middle"))
    f.append(text(cx + r + 12, cy - r + 9, "такий самий", size=11, color=HI, anchor="middle"))
    box, bw, bh = textbox(250, 428, "тиск спереду = ззаду  →  опір = 0",
                          size=13.5, pad=12, fill="#eef3fb", stroke=DRAG, bold=True)
    f.append(box)

    # ── ПРАВОРУЧ: справжня рідина — тонкий примежовий шар, слід, опір ──
    f.append(text(752, 84, "Справжня рідина — тонкий примежовий шар", size=14, bold=True))
    bx, by, br = 752, 250, 52
    for yy in (210, 250, 290):
        f.append(arrow(560, yy, 650, yy, color=VEL, sw=2.4))
    # тонкий примежовий шар огортає лобову (верхню за течією) половину
    f.append(path("M %d %d A 57 57 0 0 0 %d %d" % (bx, by - 57, bx, by + 57),
                  stroke=NEG, sw=1.6, dash="2,3"))
    # лінії течії відриваються біля корми
    f.append(path("M 650 205 Q 726 150 792 214", stroke=VEL, sw=1.7))
    f.append(path("M 650 295 Q 726 350 792 286", stroke=VEL, sw=1.7))
    # слід — сіра область розрідження за тілом
    f.append('<path d="M 792 214 L 888 190 L 888 310 L 792 286 Z" '
             'fill="%s" stroke="%s" stroke-width="1.2" stroke-dasharray="4,5"/>'
             % (WAKE, MUTED))
    f.append(path("M 812 226 q 15 13 0 26 q -15 13 0 26", stroke=MUTED, sw=1.4))
    f.append(path("M 852 222 q 17 15 0 30 q -17 15 0 30", stroke=MUTED, sw=1.4))
    f.append(circle(bx, by, br, fill=FILL, stroke=INK, sw=2))
    f.append(plus(bx - br - 12, by))         # лоб — високий
    f.append(minus(838, by))                 # слід — низький
    f.append(text(842, by + 36, "слід — тиск низький", size=11, color=LO, anchor="middle"))
    # виноска на примежовий шар
    f.append(line(700, 152, 712, 200, color=NEG, sw=1.2))
    f.append(text(672, 144, "тонкий примежовий шар", size=11, color=NEG, anchor="middle"))
    # рівнодійна — є опір
    f.append(arrow(700, 372, 806, 372, color=DRAG, sw=3.4))
    f.append(text(815, 376, "опір ≠ 0", size=13, bold=True, color=DRAG, anchor="start"))
    box2, bw2, bh2 = textbox(752, 428, "спереду ≫ ззаду  →  є опір",
                             size=13.5, pad=12, fill="#fdf0ef", stroke=VEL, bold=True)
    f.append(box2)

    render(os.path.join(IMG, "dalembert-paradox.svg"), W, H, *f)


# ── Вставка math-drag-derivation ────────────────────────────────────────────
# Фігура M1: опір як потік імпульсу крізь контрольний об'єм ───────────────────
def fig_drag_momentum_flux():
    import math
    W, H = 940, 490
    f = [text(W / 2, 30, "Опір як потік імпульсу крізь контрольний об'єм", size=16, bold=True)]

    bx0, by0, bx1, by1 = 120, 100, 720, 385
    cy = (by0 + by1) / 2
    f.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="#fbfcfd" '
             'stroke="%s" stroke-width="1.4" stroke-dasharray="6,5"/>'
             % (bx0, by0, bx1 - bx0, by1 - by0, MUTED))
    f.append(text(bx0 + 8, by0 - 9, "контрольний об'єм", size=12, color=MUTED, anchor="start"))

    # набігання — рівномірні стрілки зліва
    for yy in range(125, 361, 39):
        f.append(arrow(46, yy, 116, yy, color=VEL, sw=2.4))
    f.append(text(44, 112, "U (рівномірно)", size=13, color=VEL, anchor="start"))

    # тіло
    bcx, bcy, br = 322, cy, 40
    f.append(circle(bcx, bcy, br, fill="#f4f6f8", stroke=INK, sw=2))
    f.append(text(bcx, bcy + 5, "тіло", size=12, color=MUTED))

    # профіль швидкості на площині сліду (права грань)
    def uprofile(yy):
        return 1.0 - 0.62 * math.exp(-((yy - cy) / 46.0) ** 2)
    tips = []
    for yy in range(112, 375, 30):
        L = 62 * uprofile(yy)
        f.append(arrow(bx1 + 2, yy, bx1 + 2 + L, yy, color=VEL, sw=2.2))
        tips.append((bx1 + 2 + L, yy))
    d = "M %.1f %.1f " % tips[0] + " ".join("L %.1f %.1f" % p for p in tips[1:])
    f.append(path(d, stroke=DRAG, sw=1.6, dash="4,4"))
    f.append(text(bx1 + 100, cy - 6, "слід:", size=13, color=INK, anchor="start"))
    f.append(text(bx1 + 100, cy + 13, "u < U", size=14, bold=True, color=DRAG, anchor="start"))

    # винос убік (дефіцит маси)
    f.append(arrow(bx1 - 66, by0 + 4, bx1 - 34, by0 - 30, color=WT, sw=2.0))
    f.append(arrow(bx1 - 66, by1 - 4, bx1 - 34, by1 + 30, color=WT, sw=2.0))
    f.append(text(bx1 - 28, by0 - 30, "недопущена маса", size=11.5, color=WT, anchor="start"))
    f.append(text(bx1 - 28, by0 - 14, "виходить убік", size=11.5, color=WT, anchor="start"))

    box, bw, bh = textbox(W / 2, 458, "D = ∫ ρu(U − u) dA   →   C_d = (2/A)·∫ (u/U)(1 − u/U) dA",
                          size=15, pad=12, fill="#eef7f0", stroke=WT, bold=False)
    f.append(box)
    render(os.path.join(IMG, "drag-momentum-flux.svg"), W, H, *f)


# Фігура M2: крива C_d(Re) — Стокс, поличка, криза опору ──────────────────────
def fig_cd_reynolds_curve():
    import math
    W, H = 900, 500
    f = [text(W / 2, 30, "Коефіцієнт опору кулі проти числа Рейнольдса", size=16, bold=True)]
    ox, oy, ex, ey = 110, 410, 850, 82
    xlo, xhi = -1.0, 6.0        # log10 Re
    ylo, yhi = -1.1, 2.6        # log10 C_d  (≈0.08 .. 400)

    def X(lr):
        return ox + (lr - xlo) / (xhi - xlo) * (ex - ox)

    def Y(lc):
        return oy - (lc - ylo) / (yhi - ylo) * (oy - ey)

    xt = [(-1, "10⁻¹"), (0, "1"), (1, "10"), (2, "10²"), (3, "10³"),
          (4, "10⁴"), (5, "10⁵"), (6, "10⁶")]
    for lr, lab in xt:
        f.append(line(X(lr), oy, X(lr), ey, color="#eef1f4", sw=1.0))
        f.append(line(X(lr), oy, X(lr), oy + 5, color=INK, sw=1.4))
        f.append(text(X(lr), oy + 22, lab, size=12))
    for lc, lab in [(-1, "0.1"), (0, "1"), (1, "10"), (2, "100")]:
        f.append(line(ox, Y(lc), ex, Y(lc), color="#eef1f4", sw=1.0))
        f.append(line(ox - 5, Y(lc), ox, Y(lc), color=INK, sw=1.4))
        f.append(text(ox - 12, Y(lc) + 4, lab, size=12, anchor="end"))
    f.append(arrow(ox, oy, ox, ey - 6, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ex + 6, oy, color=INK, sw=1.8))
    f.append(text(ox - 30, ey + 2, "C_d", size=14, bold=True, anchor="start"))
    f.append(text(ex + 4, oy + 22, "Re", size=14, bold=True, anchor="start"))

    # пряма Стокса 24/Re (спад −1 на лог-осях)
    def ls(lr):
        return math.log10(24.0) - lr
    f.append(line(X(-1.0), Y(ls(-1.0)), X(1.6), Y(ls(1.6)), color=DRAG, sw=1.8, dash="6,5"))
    f.append(text(X(-0.85), Y(ls(-0.85)) - 10, "Стокс  C_d = 24/Re   (опір ∝ v)",
                  size=12.5, color=DRAG, anchor="start"))

    # головна крива C_d(Re)
    anchors = [(0.1, 240), (0.3, 80), (1, 26.5), (3, 10.5), (10, 4.1), (30, 2.05),
               (100, 1.09), (300, 0.66), (1e3, 0.47), (1e4, 0.41), (1e5, 0.50),
               (3e5, 0.10), (5e5, 0.13), (1e6, 0.19)]
    pts = [(X(math.log10(re)), Y(math.log10(cd))) for re, cd in anchors]
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append(path(d, stroke=VEL, sw=3.2))

    # межа режимів Re ≈ 1
    f.append(line(X(0), ey, X(0), oy, color=MUTED, sw=1.2, dash="3,5"))
    f.append(text(X(0) + 6, oy - 60, "Re ≈ 1", size=12, color=MUTED, anchor="start"))
    f.append(text(X(0) + 6, oy - 44, "межа режимів", size=11.5, color=MUTED, anchor="start"))

    # поличка й криза
    f.append(text(X(3.5), Y(0.28), "поличка ≈ 0.4–0.5:  опір ∝ v²", size=12.5, color=INK))
    f.append(arrow(X(4.7), Y(-0.28), X(5.4), Y(-0.85), color=INK, sw=1.6))
    f.append(text(X(4.55), Y(-0.2), "криза опору", size=12.5, bold=True))
    render(os.path.join(IMG, "cd-reynolds-curve.svg"), W, H, *f)


# Фігура M3: точний вихід на v_t через tanh ──────────────────────────────────
def fig_terminal_tanh():
    import math
    W, H = 900, 450
    f = [text(W / 2, 30, "Точний вихід на термінальну швидкість:  v(t) = v_t · tanh(g·t / v_t)",
              size=15, bold=True)]
    ox, oy, ex, ey = 100, 375, 830, 85
    tmax, vmax = 4.0, 1.16     # осі в одиницях τ і v_t

    def X(t):
        return ox + t / tmax * (ex - ox)

    def Y(v):
        return oy - v / vmax * (oy - ey)

    f.append(arrow(ox, oy, ox, ey - 6, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ex + 6, oy, color=INK, sw=1.8))
    f.append(text(ox - 14, ey - 2, "v", size=15, bold=True, anchor="end"))
    f.append(text(ex + 4, oy + 20, "t", size=15, bold=True, anchor="start"))

    # асимптота v_t
    f.append(line(ox, Y(1.0), ex, Y(1.0), color=DRAG, sw=1.6, dash="6,5"))
    f.append(text(ex + 6, Y(1.0) + 4, "v_t", size=14, bold=True, color=DRAG, anchor="start"))

    # дотична вільного падіння g·t
    f.append(line(X(0), Y(0), X(1.0), Y(1.0), color=WT, sw=2.0))
    f.append(line(X(1.0), Y(1.0), X(1.16), Y(1.16), color=WT, sw=1.4, dash="4,4"))
    f.append(text(X(0.42) + 8, Y(0.42) - 10, "вільне падіння  g·t", size=12.5, color=WT, anchor="start"))

    # крива tanh
    pts = []
    for i in range(81):
        t = tmax * i / 80.0
        pts.append((X(t), Y(math.tanh(t))))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append(path(d, stroke=VEL, sw=3.2))

    for tt, lab in [(1, "τ"), (2, "2τ"), (3, "3τ")]:
        f.append(line(X(tt), oy, X(tt), oy + 5, color=INK, sw=1.4))
        f.append(text(X(tt), oy + 21, lab, size=12.5))
    f.append(text(X(1.0), oy + 39, "τ = v_t/g", size=12, color=MUTED))

    f.append(circle(X(2), Y(math.tanh(2)), 4, fill=VEL, stroke=VEL, sw=1))
    f.append(text(X(2) + 9, Y(math.tanh(2)) + 17, "96 %", size=12, bold=True, color=VEL, anchor="start"))
    f.append(circle(X(3), Y(math.tanh(3)), 4, fill=VEL, stroke=VEL, sw=1))
    f.append(text(X(3) + 9, Y(math.tanh(3)) + 19, "99.5 %", size=12, bold=True, color=VEL, anchor="start"))
    render(os.path.join(IMG, "terminal-tanh.svg"), W, H, *f)


# ═══ Фігури до вставки «Чисельна модель польоту з опором» (proj-drag-trajectory) ═══
import math as _dt_math


def _dt_poly(pts, color=INK, sw=2.0, dash=None):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, color, sw, da)


def _dt_deriv(st, beta, gg=9.81):
    x, y, vx, vy = st
    sp = _dt_math.hypot(vx, vy)
    return [vx, vy, -beta*sp*vx, -gg - beta*sp*vy]


def _dt_traj(v0, ang_deg, beta, dt=0.004):
    """RK4-траєкторія у чистому Python — точки (x, y) до приземлення."""
    th = _dt_math.radians(ang_deg)
    st = [0.0, 0.0, v0*_dt_math.cos(th), v0*_dt_math.sin(th)]
    pts = [(0.0, 0.0)]
    while True:
        k1 = _dt_deriv(st, beta)
        k2 = _dt_deriv([st[i] + 0.5*dt*k1[i] for i in range(4)], beta)
        k3 = _dt_deriv([st[i] + 0.5*dt*k2[i] for i in range(4)], beta)
        k4 = _dt_deriv([st[i] + dt*k3[i] for i in range(4)], beta)
        nst = [st[i] + dt/6.0*(k1[i] + 2*k2[i] + 2*k3[i] + k4[i]) for i in range(4)]
        if nst[1] < 0:
            fr = st[1] / (st[1] - nst[1])
            pts.append((st[0] + fr*(nst[0] - st[0]), 0.0))
            break
        st = nst
        pts.append((st[0], st[1]))
    return pts


def _dt_apex(pts):
    return max(pts, key=lambda p: p[1])


# ── Фігура: опір напрямлений проти вектора швидкості; величину задає |v| ──────
def fig_drag_vector():
    W, H = 940, 470
    f = [text(W/2, 30, "Опір напрямлений строго проти вектора швидкості, а величину задає повна швидкість |v|",
              size=15, bold=True)]

    P = (330, 250)
    f.append(circle(P[0], P[1], 5, fill=INK, stroke=INK, sw=1))
    f.append(text(P[0] - 12, P[1] + 22, "тіло в польоті", size=12, color=MUTED, anchor="end"))

    ux, uy = 0.80, -0.60          # напрям польоту
    # швидкість v
    vtx, vty = P[0] + 175*ux, P[1] + 175*uy
    f.append(arrow(P[0], P[1], vtx, vty, color=VEL, sw=3.4))
    f.append(text(vtx + 8, vty - 4, "швидкість  v", size=13.5, bold=True, color=VEL, anchor="start"))

    # складові vₓ, v_y — пунктирний прямокутний трикутник (гіпотенуза = v)
    f.append(line(P[0], P[1], vtx, P[1], color=MUTED, sw=1.4, dash="4,4"))
    f.append(line(vtx, P[1], vtx, vty, color=MUTED, sw=1.4, dash="4,4"))
    f.append(text((P[0] + vtx)/2, P[1] + 18, "vₓ", size=12.5, color=MUTED))
    f.append(text(vtx + 12, (P[1] + vty)/2, "v_y", size=12.5, color=MUTED, anchor="start"))

    # опір — строго антипаралельно v
    dtx, dty = P[0] - 140*ux, P[1] - 140*uy
    f.append(arrow(P[0], P[1], dtx, dty, color=DRAG, sw=3.4))
    f.append(text(dtx - 8, dty + 2, "опір", size=13.5, bold=True, color=DRAG, anchor="end"))
    f.append(text(dtx - 8, dty + 20, "(проти v)", size=12, color=DRAG, anchor="end"))

    # вага — прямовисно вниз
    f.append(arrow(P[0], P[1], P[0], P[1] + 105, color=WT, sw=3.2))
    f.append(text(P[0] + 10, P[1] + 88, "вага  m·g", size=13, bold=True, color=WT, anchor="start"))

    # рамка з рівняннями
    eqs = ("a = g − β·|v|·v\n"
           "β = ½·ρ·C_d·A / m\n"
           "aₓ = −β·|v|·vₓ\n"
           "a_y = −g − β·|v|·v_y\n"
           "|v| = √( vₓ² + v_y² )")
    box, bw, bh = textbox(725, 242, eqs, size=13.5, pad=14, fill="#f4f6f8", stroke=INK, sw=1.4)
    f.append(box)

    # нижня нотатка
    note, nw, nh = textbox(W/2, 428,
                           "Множник |v| той самий для обох осей — опір НЕ розкладається на vₓ² і v_y² окремо.",
                           size=13.5, pad=12, fill="#eef7f0", stroke=WT, sw=1.5, bold=False)
    f.append(note)
    render(os.path.join(IMG, "drag-vector.svg"), W, H, *f)


# ── Фігура: опір коротшає й перекошує дугу (дві крайності) ───────────────────
def _dt_panel(ox, oy, w, h, xmax, ymax, vac, drag, title, lab_vac, lab_drag):
    sx, sy = w/xmax, h/ymax
    def Pt(p): return (ox + p[0]*sx, oy - p[1]*sy)
    fr = []
    fr.append(line(ox, oy, ox + w + 8, oy, color=INK, sw=1.7))      # земля
    fr.append(line(ox, oy, ox, oy - h - 8, color=MUTED, sw=1.2))    # вертикаль
    fr.append(_dt_poly([Pt(p) for p in vac], color=MUTED, sw=2.0, dash="7,5"))
    fr.append(_dt_poly([Pt(p) for p in drag], color=VEL, sw=3.0))
    av, ad = _dt_apex(vac), _dt_apex(drag)
    pav, pad = Pt(av), Pt(ad)
    fr.append(circle(pav[0], pav[1], 4, fill=MUTED, stroke=MUTED, sw=1))
    fr.append(circle(pad[0], pad[1], 4.5, fill=VEL, stroke=VEL, sw=1))
    fr.append(text(Pt(vac[-1])[0], oy + 18, "%.0f м" % vac[-1][0], size=12, color=MUTED))
    fr.append(text(Pt(drag[-1])[0], oy + 35, "%.0f м" % drag[-1][0], size=12.5, color=VEL, bold=True))
    fr.append(text(ox + w/2, oy - h - 28, title, size=14, bold=True))
    fr.append(text(pav[0] + 6, pav[1] - 8, lab_vac, size=12, color=MUTED, anchor="start"))
    fr.append(text(pad[0] + 8, pad[1] + 2, lab_drag, size=12.5, color=VEL, bold=True, anchor="start"))
    return fr


def fig_traj_compare():
    W, H = 980, 560
    f = [text(W/2, 30, "Опір коротшає й перекошує дугу: злегка (бейсбол) і вкрай (волан)", size=15.5, bold=True)]

    beta_ball = 0.5*0.35*1.2*(_dt_math.pi*0.0365**2)/0.145
    beta_shut = 9.81/6.7**2

    ball_v = _dt_traj(45, 45, 0.0)
    ball_d = _dt_traj(45, 45, beta_ball)
    shut_v = _dt_traj(25, 45, 0.0)
    shut_d = _dt_traj(25, 45, beta_shut)

    f += _dt_panel(70, 385, 370, 215, 215.0, 58.0, ball_v, ball_d,
                   "Бейсбол  (v_t ≈ 40 м/с)", "вакуум", "з опором")
    f += _dt_panel(560, 385, 370, 215, 68.0, 17.5, shut_v, shut_d,
                   "Волан  (v_t ≈ 6.7 м/с)", "вакуум", "з опором")

    f.append(text(255, 505, "дуга з опором коротша й падає крутіше за симетричну вакуумну параболу",
                  size=12, color=INK))
    f.append(text(745, 505, "великий опір збиває дугу в куций пеньок — волан падає майже прямовисно",
                  size=12, color=INK))
    f.append(text(W/2, 535, "масштаби осей у панелях РІЗНІ (підписані числа — справжні метри)",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "traj-compare.svg"), W, H, *f)


# ── Фігура: порядок точності — Ейлер (∝Δt) проти RK4 (∝Δt⁴) ──────────────────
def fig_euler_rk4_order():
    W, H = 900, 470
    f = [text(W/2, 30, "Ціна кроку: похибка Ейлера спадає як Δt, а RK4 — як Δt⁴", size=15.5, bold=True)]

    euler = [(0.2, 1.971), (0.1, 0.973), (0.05, 0.4835), (0.025, 0.2410), (0.0125, 0.1203)]
    rk4   = [(0.2, 3.34e-5), (0.1, 2.00e-6), (0.05, 1.22e-7), (0.025, 7.57e-9), (0.0125, 4.71e-10)]

    ox, oy = 132, 408
    axw, axh = 636, 322
    lx0, lx1 = _dt_math.log10(0.0110), _dt_math.log10(0.235)
    ly0, ly1 = -10.0, 1.0

    def X(dt): return ox + (_dt_math.log10(dt) - lx0)/(lx1 - lx0)*axw
    def Y(e):  return oy - (_dt_math.log10(e) - ly0)/(ly1 - ly0)*axh

    for e in range(int(ly0), int(ly1) + 1):
        yy = oy - (e - ly0)/(ly1 - ly0)*axh
        f.append(line(ox, yy, ox + axw, yy, color="#eef1f4", sw=1.0))
        f.append(text(ox - 10, yy + 4, "10%d" % e, size=11, color=MUTED, anchor="end"))
    f.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.7))
    f.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.7))
    f.append(text(ox - 96, oy - axh/2, "похибка положення, м", size=12.5, color=INK))
    f.append(text(ox + axw/2, oy + 52, "крок інтегрування Δt, с  (дрібніший ліворуч)", size=12.5, color=INK))
    for dt in (0.0125, 0.025, 0.05, 0.1, 0.2):
        xx = X(dt)
        f.append(line(xx, oy, xx, oy + 5, color=INK, sw=1.3))
        f.append(text(xx, oy + 22, ("%.4f" % dt).rstrip("0").rstrip("."), size=11, color=MUTED))

    f.append(_dt_poly([(X(dt), Y(e)) for dt, e in euler], color=VEL, sw=3.0))
    f.append(_dt_poly([(X(dt), Y(e)) for dt, e in rk4], color=DRAG, sw=3.0))
    for dt, e in euler:
        f.append(circle(X(dt), Y(e), 4.5, fill=VEL, stroke=VEL, sw=1))
    for dt, e in rk4:
        f.append(circle(X(dt), Y(e), 4.5, fill=DRAG, stroke=DRAG, sw=1))

    f.append(text(X(0.2) + 10, Y(1.971) - 6, "Ейлер  (нахил 1: ∝ Δt)", size=13, bold=True, color=VEL, anchor="start"))
    f.append(text(X(0.2) + 10, Y(3.34e-5) + 2, "RK4  (нахил 4: ∝ Δt⁴)", size=13, bold=True, color=DRAG, anchor="start"))
    nb, nw, nh = textbox(372, 90, "Той самий Δt = 0.1 с:  Ейлер хибить на 1 м,  RK4 — на 2·10⁻⁶ м",
                         size=13, pad=11, fill="#f4f6f8", stroke=INK, sw=1.3)
    f.append(nb)
    render(os.path.join(IMG, "euler-rk4-order.svg"), W, H, *f)


if __name__ == "__main__":
    fig_drag_origin()
    fig_friction_vs_form()
    fig_cd_shapes()
    fig_terminal_velocity()
    fig_drag_history_timeline()
    fig_dalembert_paradox()
    fig_drag_momentum_flux()
    fig_cd_reynolds_curve()
    fig_terminal_tanh()
    fig_drag_vector()
    fig_traj_compare()
    fig_euler_rk4_order()
    print("OK: figs written to", IMG)

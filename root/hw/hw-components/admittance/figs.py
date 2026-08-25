# -*- coding: utf-8 -*-
"""Фігури теми «Адмітанс». Запуск: python figs.py  → ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)
P = lambda name: os.path.join(OUT, name)


def resistor(x, y, w=46, h=16, label=None, lab_size=13):
    """Горизонтальний прямокутний резистор з опорними виводами по краях."""
    out = rect(x, y - h/2, w, h, fill="#fff", stroke=INK, sw=2, rx=2)
    if label:
        out += text(x + w/2, y - h/2 - 7, label, size=lab_size, bold=True)
    return out


def cap(x, y, gap=7, plate=18):
    """Конденсатор (дві пластини) центрований по (x,y), вертикальні пластини."""
    out  = line(x - gap/2, y - plate/2, x - gap/2, y + plate/2, color=INK, sw=2.4)
    out += line(x + gap/2, y - plate/2, x + gap/2, y + plate/2, color=INK, sw=2.4)
    return out


def coil(x, y, w=44, loops=4, r=6):
    """Котушка — дуги-горбики уздовж горизонталі від x до x+w на рівні y."""
    seg = w / loops
    out = ""
    for i in range(loops):
        cx = x + seg * (i + 0.5)
        out += ('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" '
                'fill="none" stroke="%s" stroke-width="2.2"/>'
                % (cx - seg/2, y, r, r, cx + seg/2, y, INK))
    return out


# ── 1. Послідовно ↔ паралельно: де яка величина зручна ──────────────────────
def fig_series_vs_parallel():
    W, H = 720, 300
    f = [text(W/2, 26, "Кожна топологія має «зручну» величину", size=17, bold=True)]

    # --- ліва половина: послідовно, опори додаються ---
    f.append(text(180, 58, "Послідовно", size=15, bold=True, color=INK))
    yL = 120
    f.append(line(60, yL, 110, yL, color=INK, sw=2))
    f.append(resistor(110, yL, w=46, label="R₁"))
    f.append(line(156, yL, 196, yL, color=INK, sw=2))
    f.append(resistor(196, yL, w=46, label="R₂"))
    f.append(line(242, yL, 300, yL, color=INK, sw=2))
    # клеми
    f.append(circle(60, yL, 4, fill=INK, stroke=INK))
    f.append(circle(300, yL, 4, fill=INK, stroke=INK))
    box1, _, _ = textbox(180, 198, "R = R₁ + R₂\n(той самий струм)",
                         size=14, fill="#eef5ee", stroke=FIELD, bold=False)
    f.append(box1)

    # роздільник
    f.append(line(W/2, 50, W/2, H-26, color=MUTED, sw=1, dash="5,5"))

    # --- права половина: паралельно, провідності додаються ---
    f.append(text(540, 58, "Паралельно", size=15, bold=True, color=INK))
    xin, xout = 420, 660
    ytop, ybot = 100, 150
    f.append(circle(xin, (ytop+ybot)/2, 4, fill=INK, stroke=INK))
    f.append(circle(xout, (ytop+ybot)/2, 4, fill=INK, stroke=INK))
    # вузли-шини
    f.append(line(xin, ytop, xin, ybot, color=INK, sw=2))
    f.append(line(xout, ytop, xout, ybot, color=INK, sw=2))
    f.append(line(xin, (ytop+ybot)/2, 420, (ytop+ybot)/2, color=INK, sw=2))
    # верхня гілка R₁
    f.append(line(xin, ytop, 490, ytop, color=INK, sw=2))
    f.append(resistor(490, ytop, w=46, label="R₁"))
    f.append(line(536, ytop, xout, ytop, color=INK, sw=2))
    # нижня гілка R₂
    f.append(line(xin, ybot, 490, ybot, color=INK, sw=2))
    f.append(resistor(490, ybot, w=46, label="R₂", lab_size=13))
    f.append(line(536, ybot, xout, ybot, color=INK, sw=2))
    box2, _, _ = textbox(540, 210, "G = G₁ + G₂\n(та сама напруга)",
                         size=14, fill="#eef5ee", stroke=FIELD, bold=False)
    f.append(box2)
    f.append(text(540, 248, "G = 1/R — провідність", size=12, color=MUTED))

    render(P("series-vs-parallel.svg"), W, H, *f)


# ── 2. Z і Y — дзеркало того самого вузла ───────────────────────────────────
def fig_z_y_mirror():
    W, H = 720, 280
    f = [text(W/2, 26, "Той самий двополюсник — два описи", size=17, bold=True)]

    # центральний чорний ящик (двополюсник)
    bx, by, bw, bh = W/2 - 55, 110, 110, 60
    f.append(rect(bx, by, bw, bh, fill="#f4f6f8", stroke=INK, sw=2, rx=8))
    f.append(text(W/2, by + bh/2 + 5, "двополюсник", size=13, color=INK))
    f.append(line(bx, by + bh/2, bx - 30, by + bh/2, color=INK, sw=2))
    f.append(line(bx + bw, by + bh/2, bx + bw + 30, by + bh/2, color=INK, sw=2))
    f.append(circle(bx - 30, by + bh/2, 4, fill=INK, stroke=INK))
    f.append(circle(bx + bw + 30, by + bh/2, 4, fill=INK, stroke=INK))

    # ліворуч: імпеданс (важкість)
    b1, _, _ = textbox(150, 110, "Z = R + jX", size=18, bold=True,
                       fill="#fdecea", stroke=POS, min_w=170)
    f.append(b1)
    f.append(text(150, 150, "важкість (Ом)", size=13, color=MUTED))
    f.append(text(150, 174, "R — активний опір", size=12, color=INK))
    f.append(text(150, 194, "X — реактивність", size=12, color=INK))

    # праворуч: адмітанс (легкість)
    b2, _, _ = textbox(W - 150, 110, "Y = G + jB", size=18, bold=True,
                       fill="#eef5ee", stroke=FIELD, min_w=170)
    f.append(b2)
    f.append(text(W - 150, 150, "легкість (См)", size=13, color=MUTED))
    f.append(text(W - 150, 174, "G — провідність", size=12, color=INK))
    f.append(text(W - 150, 194, "B — сприйнятливість", size=12, color=INK))

    # стрілки-обернення між боками й ящиком, з підписом Y = 1/Z
    f.append(arrow(250, 105, bx - 6, 125, color=MUTED, sw=1.8))
    f.append(arrow(W - 250, 105, bx + bw + 6, 125, color=MUTED, sw=1.8))
    f.append(text(W/2, 235, "Y = 1/Z — обертають ЦІЛЕ число, а не R і X окремо",
                  size=13, color=POS, bold=True))
    render(P("z-y-mirror.svg"), W, H, *f)


# ── 3. Адмітанс паралельного RLC проти частоти ──────────────────────────────
def fig_parallel_rlc_y():
    W, H = 720, 380
    f = [text(W/2, 26, "Сприйнятливості складаються: B = ω·C − 1/(ω·L)", size=16, bold=True)]

    # осі
    ox, oy = 90, 195          # початок (нуль по B на осі частоти)
    ax_w, ax_top, ax_bot = 560, 78, 330
    f.append(line(ox, ax_top, ox, ax_bot, color=INK, sw=1.8))          # вісь B
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))           # вісь f (нуль)
    f.append(text(ox - 16, ax_top + 4, "B", size=14, bold=True))
    f.append(text(ox + ax_w + 14, oy + 5, "f", size=14, bold=True))
    f.append(text(ox - 14, oy - 4, "0", size=12, color=MUTED, anchor="end"))

    fmin, fmax = 0.32, 2.7     # умовні одиниці ω/ω₀
    def fx(u): return ox + (u - fmin) / (fmax - fmin) * ax_w
    SC = 42.0                  # масштаб B у px
    def by_(b): return oy - b * SC

    # Bc = k·u (росте), BL = -k/u (від'ємна, до нуля знизу). При u=1 рівні => резонанс
    k = 1.0
    # ємнісна (зелена, вгору)
    pc = []
    u = fmin
    while u <= fmax + 1e-9:
        pc.append((fx(u), by_(k*u)))
        u += 0.05
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % p for p in pc), FIELD))
    f.append(text(fx(fmax) - 6, by_(k*fmax) - 8, "Bc = ω·C", size=13, color=FIELD,
                  bold=True, anchor="end"))

    # індуктивна (синя, від'ємна)
    pl = []
    u = fmin
    while u <= fmax + 1e-9:
        pl.append((fx(u), by_(-k/u)))
        u += 0.025
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join("%.1f,%.1f" % p for p in pl), NEG))
    f.append(text(fx(fmax) - 6, by_(-k/fmax) + 18, "BL = −1/(ω·L)", size=13,
                  color=NEG, bold=True, anchor="end"))

    # сума B = Bc + BL (сіра, перетинає нуль при u=1)
    ps = []
    u = fmin
    while u <= fmax + 1e-9:
        ps.append((fx(u), by_(k*u - k/u)))
        u += 0.025
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-dasharray="6,4"/>'
             % (" ".join("%.1f,%.1f" % p for p in ps), INK))
    f.append(text(fx(2.3), by_(k*2.3 - k/2.3) + 4, "B (сума)", size=13, color=INK,
                  bold=True))

    # резонанс u=1
    xr = fx(1.0)
    f.append(line(xr, ax_top, xr, ax_bot, color=MUTED, sw=1.2, dash="4,4"))
    f.append(circle(xr, oy, 5, fill=POS, stroke=POS))
    f.append(text(xr, ax_bot + 20, "ω₀ = 1/√(LC)", size=13, color=POS, bold=True))
    f.append(text(xr, ax_bot + 38, "B = 0 → лишається G = 1/R", size=12, color=MUTED))

    render(P("parallel-rlc-y.svg"), W, H, *f)


# ── 4. Дзеркало двох законів складання ──────────────────────────────────────
def fig_series_parallel_add():
    W, H = 720, 250
    f = [text(W/2, 26, "Обери величину під топологію — і складання стає сумою",
              size=16, bold=True)]

    # ліва панель — послідовно, Z додаються
    f.append(rect(40, 55, 300, 165, fill="#fff", stroke=POS, sw=2, rx=10))
    f.append(text(190, 80, "Послідовно", size=15, bold=True))
    f.append(text(190, 102, "спільний СТРУМ", size=12, color=MUTED))
    yL = 140
    f.append(line(70, yL, 110, yL, color=INK, sw=2))
    f.append(resistor(110, yL, w=44, label="Z₁"))
    f.append(line(154, yL, 196, yL, color=INK, sw=2))
    f.append(resistor(196, yL, w=44, label="Z₂"))
    f.append(line(240, yL, 310, yL, color=INK, sw=2))
    f.append(circle(70, yL, 4, fill=INK, stroke=INK))
    f.append(circle(310, yL, 4, fill=INK, stroke=INK))
    b1, _, _ = textbox(190, 192, "Z = Z₁ + Z₂", size=15, bold=True,
                       fill="#fdecea", stroke=POS)
    f.append(b1)

    # права панель — паралельно, Y додаються
    f.append(rect(380, 55, 300, 165, fill="#fff", stroke=FIELD, sw=2, rx=10))
    f.append(text(530, 80, "Паралельно", size=15, bold=True))
    f.append(text(530, 102, "спільна НАПРУГА", size=12, color=MUTED))
    xin, xout = 430, 630
    ytop, ybot = 128, 158
    f.append(circle(xin, (ytop+ybot)/2, 4, fill=INK, stroke=INK))
    f.append(circle(xout, (ytop+ybot)/2, 4, fill=INK, stroke=INK))
    f.append(line(xin, ytop, xin, ybot, color=INK, sw=2))
    f.append(line(xout, ytop, xout, ybot, color=INK, sw=2))
    f.append(line(410, (ytop+ybot)/2, xin, (ytop+ybot)/2, color=INK, sw=2))
    f.append(line(xout, (ytop+ybot)/2, 650, (ytop+ybot)/2, color=INK, sw=2))
    f.append(line(xin, ytop, 500, ytop, color=INK, sw=2))
    f.append(resistor(500, ytop, w=40, label="Y₁", lab_size=12))
    f.append(line(540, ytop, xout, ytop, color=INK, sw=2))
    f.append(line(xin, ybot, 500, ybot, color=INK, sw=2))
    f.append(resistor(500, ybot, w=40, label=None))
    f.append(text(560, ybot + 4, "Y₂", size=12, bold=True))
    f.append(line(540, ybot, xout, ybot, color=INK, sw=2))
    b2, _, _ = textbox(530, 192, "Y = Y₁ + Y₂", size=15, bold=True,
                       fill="#eef5ee", stroke=FIELD)
    f.append(b2)

    render(P("series-parallel-add.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════
#  Фігури математичної вставки «Адмітанс з імпедансу» (math-y-from-z.md)
# ══════════════════════════════════════════════════════════════════════════

# ── M1. Геометрія 1/z: інверсія по радіусу + віддзеркалення кута ─────────────
def fig_inv_geometry():
    W, H = 720, 440
    f = [text(W/2, 26, "Що робить 1/z з точкою на площині: два кроки", size=17, bold=True)]

    cx, cy = W/2, 250          # центр площини (початок координат)
    R = 150.0                  # радіус одиничного кола в px (|z|=1)
    # осі
    f.append(line(cx - 250, cy, cx + 250, cy, color=INK, sw=1.6))   # дійсна
    f.append(line(cx, cy - 175, cx, cy + 150, color=INK, sw=1.6))   # уявна
    f.append(text(cx + 256, cy + 5, "Re", size=13, bold=True))
    f.append(text(cx + 12, cy - 172, "Im", size=13, bold=True))
    f.append(circle(cx, cy, 3.5, fill=INK, stroke=INK))
    f.append(text(cx - 12, cy + 18, "0", size=12, color=MUTED, anchor="end"))
    # одиничне коло
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="1.4" stroke-dasharray="5,4"/>' % (cx, cy, R, MUTED))
    f.append(text(cx + R*0.72, cy - R*0.72 - 6, "одиничне коло |z|=1", size=11,
                  color=MUTED, anchor="middle"))

    import math as _m
    ang = _m.radians(34)       # кут φ точки z
    rz = 1.7                   # |z| > 1 (поза колом)
    # z
    zx, zy = cx + R*rz*_m.cos(ang), cy - R*rz*_m.sin(ang)
    f.append(arrow(cx, cy, zx, zy, color=POS, sw=2.4))
    f.append(circle(zx, zy, 4, fill=POS, stroke=POS))
    f.append(text(zx + 10, zy - 6, "z  (|z|, +φ)", size=14, color=POS, bold=True))

    # крок 1: інверсія по радіусу → 1/|z| на ТОМУ Ж промені (всередині кола)
    r1 = 1.0 / rz
    ix, iy = cx + R*r1*_m.cos(ang), cy - R*r1*_m.sin(ang)
    f.append(arrow(cx, cy, ix, iy, color=MUTED, sw=2.0))
    f.append(circle(ix, iy, 4, fill="#fff", stroke=MUTED, sw=2))
    f.append(text(ix - 6, iy - 10, "1/|z|, +φ", size=12, color=MUTED, anchor="end"))
    # дуга-промінь підказка крок1
    f.append(text(cx + R*1.05*_m.cos(ang) + 30, cy - R*1.05*_m.sin(ang) + 6,
                  "крок 1: довжина → 1/|z|", size=11, color=MUTED))

    # крок 2: спряження — віддзеркалення через дійсну вісь → кут стає −φ
    fxp, fyp = cx + R*r1*_m.cos(ang), cy + R*r1*_m.sin(ang)   # дзеркало по горизонталі
    f.append(arrow(cx, cy, fxp, fyp, color=FIELD, sw=2.6))
    f.append(circle(fxp, fyp, 4.5, fill=FIELD, stroke=FIELD))
    f.append(text(fxp + 10, fyp + 16, "1/z  (1/|z|, −φ)", size=14, color=FIELD, bold=True))
    # пунктир дзеркала
    f.append(line(ix, iy, fxp, fyp, color=FIELD, sw=1.2, dash="3,3"))
    f.append(text((ix+fxp)/2 + 70, (iy+fyp)/2, "крок 2: відбити", size=11, color=FIELD))
    f.append(text((ix+fxp)/2 + 70, (iy+fyp)/2 + 15, "через дійсну вісь", size=11, color=FIELD))

    # дуги кутів +φ (до z) та −φ (до 1/z)
    f.append('<path d="M %.1f %.1f A 40 40 0 0 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.4"/>'
             % (cx + 40, cy, cx + 40*_m.cos(ang), cy - 40*_m.sin(ang), POS))
    f.append('<path d="M %.1f %.1f A 40 40 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.4"/>'
             % (cx + 40, cy, cx + 40*_m.cos(ang), cy + 40*_m.sin(ang), FIELD))

    # підсумкова рамка
    bx, _, _ = textbox(cx, H - 24, "|1/z| = 1/|z|     arg(1/z) = −φ",
                       size=15, bold=True, fill="#eef5ee", stroke=FIELD, min_w=360)
    f.append(bx)
    render(P("inv-geometry.svg"), W, H, *f)


# ── M2. Спряжене перемішує: R,X → один знаменник R²+X² → G,B ─────────────────
def fig_mixing():
    W, H = 720, 360
    f = [text(W/2, 26, "Чому R і X не можна обертати окремо", size=17, bold=True)]

    # ліворуч: входи R і X
    f.append(text(95, 60, "Маємо", size=12, color=MUTED))
    bR, _, _ = textbox(95, 95, "R", size=20, bold=True, fill="#fdecea", stroke=POS, min_w=70)
    f.append(bR)
    bX, _, _ = textbox(95, 165, "X", size=20, bold=True, fill="#eaf0fd", stroke=NEG, min_w=70)
    f.append(bX)

    # центр: знаменник D = R²+X² (спільний)
    f.append(rect(250, 70, 220, 120, fill="#eef5ee", stroke=FIELD, sw=2, rx=10))
    f.append(text(360, 100, "множимо на спряжене R − jX", size=12, color=INK))
    f.append(text(360, 132, "D = R² + X²", size=20, bold=True, color=FIELD))
    f.append(text(360, 160, "(сюди входять ОБА: і R, і X)", size=12, color=MUTED))
    # стрілки входів у знаменник
    f.append(arrow(133, 95, 248, 110, color=MUTED, sw=1.8))
    f.append(arrow(133, 165, 248, 150, color=MUTED, sw=1.8))

    # праворуч: виходи G і B, кожен ділиться на D
    bG, _, _ = textbox(620, 95, "G = R / D", size=16, bold=True,
                       fill="#fdecea", stroke=POS, min_w=150)
    f.append(bG)
    bB, _, _ = textbox(620, 165, "B = −X / D", size=16, bold=True,
                       fill="#eaf0fd", stroke=NEG, min_w=150)
    f.append(bB)
    f.append(arrow(472, 110, 545, 95, color=MUTED, sw=1.8))
    f.append(arrow(472, 150, 545, 165, color=MUTED, sw=1.8))

    # нижня мораль
    f.append(line(60, 230, W - 60, 230, color=MUTED, sw=1, dash="4,4"))
    f.append(text(W/2, 258, "Знаменник D спільний — тому в кожній частині Y «сидить» і R, і X.",
                  size=14, color=INK, bold=True))
    bad, _, _ = textbox(230, 305, "G ≠ 1/R", size=15, bold=True,
                        fill="#fdecea", stroke=POS, min_w=140)
    f.append(bad)
    bad2, _, _ = textbox(W - 230, 305, "B ≠ 1/X", size=15, bold=True,
                         fill="#fdecea", stroke=POS, min_w=140)
    f.append(bad2)
    f.append(text(W/2, 312, "правда лише в чистих крайніх випадках", size=12, color=MUTED))
    render(P("mixing.svg"), W, H, *f)


# ── M3. Знаки сприйнятливості: C тягне вгору (+), L — вниз (−) ───────────────
def fig_susceptance_signs():
    W, H = 720, 360
    f = [text(W/2, 26, "Знак сприйнятливості: ємність +, індуктивність −", size=16, bold=True)]

    ox, oy = 95, 190
    ax_w, ax_top, ax_bot = 540, 70, 300
    f.append(line(ox, ax_top, ox, ax_bot, color=INK, sw=1.8))     # вісь B
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))      # вісь ω (нуль B)
    f.append(text(ox - 16, ax_top + 2, "B", size=14, bold=True))
    f.append(text(ox + ax_w + 14, oy + 5, "ω", size=14, bold=True))
    f.append(text(ox - 12, oy - 4, "0", size=12, color=MUTED, anchor="end"))
    f.append(text(ox + 16, ax_top + 12, "+", size=18, color=POS, bold=True))
    f.append(text(ox + 16, ax_bot - 6, "−", size=18, color=NEG, bold=True))

    import math as _m
    wmin, wmax = 0.30, 2.7
    def wx(u): return ox + (u - wmin) / (wmax - wmin) * ax_w
    SC = 44.0
    UP_LIM = oy - (ax_top + 14)        # макс. підйом угору (px у одиницях B)
    DN_LIM = (ax_bot - 6) - oy         # макс. спуск униз
    def byv(b): return oy - b * SC

    # Bc = ω·C  (пряма вгору, додатна) — масштаб такий, щоб не вилазила за верх
    kC = (UP_LIM / SC) / wmax
    pc = [(wx(u), byv(kC*u)) for u in [wmin + 0.02*i for i in range(int((wmax-wmin)/0.02)+1)]]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in pc), FIELD))
    f.append(text(wx(wmax) - 6, byv(kC*wmax) + 16, "Bc = ω·C  (+)", size=14, color=FIELD,
                  bold=True, anchor="end"))
    f.append(text(wx(1.55), byv(kC*1.55) - 10, "конденсатор: легше на високих ω",
                  size=11, color=FIELD, anchor="middle"))

    # BL = -1/(ω·L)  (від'ємна, від низу догори до 0) — обрізаємо по нижній межі
    kL = 0.40
    pl = [(wx(u), byv(-kL/u))
          for u in [wmin + 0.015*i for i in range(int((wmax-wmin)/0.015)+1)]
          if (kL/u) * SC <= DN_LIM]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in pl), NEG))
    f.append(text(wx(wmax) - 6, byv(-kL/wmax) - 12, "BL = −1/(ω·L)  (−)", size=14,
                  color=NEG, bold=True, anchor="end"))
    f.append(text(wx(1.75), byv(-kL/1.75) + 22, "котушка: завжди нижче нуля",
                  size=11, color=NEG, anchor="middle"))

    render(P("susceptance-signs.svg"), W, H, *f)


if __name__ == "__main__":
    fig_series_vs_parallel()
    fig_z_y_mirror()
    fig_parallel_rlc_y()
    fig_series_parallel_add()
    fig_inv_geometry()
    fig_mixing()
    fig_susceptance_signs()
    print("OK: figures written to", OUT)

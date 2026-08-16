# -*- coding: utf-8 -*-
"""Фігури до теми «Відображення Пуанкаре».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

MAIN = "#2457d6"
ACCENT = "#c0392b"
GREEN = "#27ae60"
PURPLE = "#8e44ad"
BORDER = "#d0d7de"
MUTED = "#6e7781"
INK = "#24292f"

def head_at(x, y, dx, dy, color=INK, size=8):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.4, by + ny * size * 0.4,
               bx - nx * size * 0.4, by - ny * size * 0.4, color))

def varrow(x1, y1, x2, y2, color=LINE, sw=2.0, head=9):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)

# ── Фігура 1: Геометрична концепція секущої поверхні та відображення Пуанкаре ──
def fig_poincare_concept():
    W, H = 820, 440
    f = []

    f.append(text(W / 2, 26, "Геометрична концепція секущої поверхні та відображення Пуанкаре", size=15, bold=True))

    x0, y0 = 40, 55
    w_p, h_p = 740, 360
    f.append(rect(x0, y0, w_p, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))

    poly_sigma = [(300, 100), (560, 120), (480, 360), (220, 340)]
    pts_sigma_str = " ".join("%.1f,%.1f" % p for p in poly_sigma)
    f.append('<polygon points="%s" fill="#EBF3FE" fill-opacity="0.75" stroke="%s" stroke-width="2"/>' % (pts_sigma_str, MAIN))
    f.append(text(245, 325, "Секуща поверхня Σ", size=14, bold=True, color=MAIN))
    f.append(text(245, 342, "(корозмірність 1)", size=11, color=MUTED))

    nx0, ny0 = 390, 230
    f.append(varrow(nx0, ny0, nx0 - 45, ny0 - 80, color=PURPLE, sw=2.2, head=9))
    f.append(text(nx0 - 55, ny0 - 85, "Нормаль n", size=12, bold=True, color=PURPLE))

    f.append('<path d="M 120 380 Q 200 370 280 320 T 330 250" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,4"/>' % ACCENT)
    f.append('<path d="M 330 250 Q 360 200 420 130 T 520 100 T 640 140" fill="none" stroke="%s" stroke-width="2.5"/>' % ACCENT)
    f.append('<path d="M 640 140 Q 720 170 680 250 T 540 260 T 420 200" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,4"/>' % ACCENT)
    f.append('<path d="M 420 200 Q 380 170 300 150 T 220 200 T 300 280 T 370 280" fill="none" stroke="%s" stroke-width="2.5"/>' % ACCENT)
    f.append('<path d="M 370 280 Q 420 280 500 240 T 620 260" fill="none" stroke="%s" stroke-width="2"/>' % ACCENT)

    f.append(head_at(365, 185, 60, -70, color=ACCENT, size=9))
    f.append(head_at(325, 158, -80, -20, color=ACCENT, size=9))

    p0 = (330, 250)
    p1 = (420, 200)
    p2 = (370, 280)

    for pt, lbl, offset in [(p0, "x₀", (-20, 15)), (p1, "x₁ = P(x₀)", (12, -10)), (p2, "x₂ = P(x₁)", (12, 18))]:
        f.append(circle(pt[0], pt[1], 5, fill=GREEN, stroke=INK, sw=1.5))
        f.append(text(pt[0] + offset[0], pt[1] + offset[1], lbl, size=13, bold=True, color=INK))

    f.append('<path d="M 335 245 Q 375 210 415 200" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="3,3"/>' % GREEN)
    f.append(head_at(415, 200, 40, -10, color=GREEN, size=8))
    f.append(text(375, 215, "P", size=13, bold=True, color=GREEN))

    f.append('<path d="M 415 205 Q 400 250 375 275" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="3,3"/>' % GREEN)
    f.append(head_at(375, 275, -25, 25, color=GREEN, size=8))
    f.append(text(405, 245, "P", size=13, bold=True, color=GREEN))

    f.append(text(550, 90, "Фазовий потік φᵗ(x)", size=12, bold=True, color=ACCENT))

    f.append(rect(x0 + 20, y0 + h_p - 50, w_p - 40, 38, fill='#FFFFFF', stroke=BORDER, sw=1, rx=4))
    f.append(text(x0 + w_p/2, y0 + h_p - 26, "Неперервна система 3D: dx/dt = f(x)   ──►   Дискретне відображення 2D: xₖ₊₁ = P(xₖ)", size=12, bold=True, color=INK))

    render(os.path.join(IMG, "poincare-concept.svg"), W, H, *f)

# ── Фігура 2: Типи динамічних режимів у перерізі Пуанкаре ───────────────────
def fig_poincare_types():
    W, H = 840, 340
    f = []

    f.append(text(W / 2, 24, "Типи динамічних режимів у перерізі Пуанкаре", size=15, bold=True))

    w_box = 245
    h_box = 265
    y_top = 50

    x_a = 30
    f.append(rect(x_a, y_top, w_box, h_box, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(x_a + w_box/2, y_top + 22, "Періодичний рух", size=13, bold=True))
    f.append(text(x_a + w_box/2, y_top + 38, "(Граничний цикл T)", size=11, color=MUTED))

    cx_a, cy_a = x_a + w_box/2, y_top + 145
    f.append(varrow(cx_a - 90, cy_a, cx_a + 90, cy_a, color=BORDER, sw=1.2))
    f.append(varrow(cx_a, cy_a + 80, cx_a, cy_a - 80, color=BORDER, sw=1.2))
    f.append(text(cx_a + 95, cy_a + 4, "q", size=11, color=MUTED))
    f.append(text(cx_a + 4, cy_a - 82, "p", size=11, color=MUTED))

    f.append(circle(cx_a + 25, cy_a - 20, 6, fill=ACCENT, stroke=INK, sw=1.5))
    f.append(text(cx_a + 35, cy_a - 24, "x* = P(x*)", size=12, bold=True, color=ACCENT))

    pts_conv = []
    for k in range(12):
        r = 60.0 * math.exp(-k * 0.25)
        ang = k * 1.1 + 0.3
        px = cx_a + 25 + r * math.cos(ang)
        py = cy_a - 20 + r * math.sin(ang)
        pts_conv.append((px, py))
        f.append(circle(px, py, 3, fill=MAIN, stroke="none"))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1" stroke-dasharray="2,2"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_conv), MAIN))
    f.append(text(x_a + w_box/2, y_top + h_box - 18, "Нерухома точка (1 точка)", size=12, bold=True, color=INK))

    x_b = 297
    f.append(rect(x_b, y_top, w_box, h_box, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(x_b + w_box/2, y_top + 22, "Квазіперіодичний рух", size=13, bold=True))
    f.append(text(x_b + w_box/2, y_top + 38, "(Двовимірний тор T²)", size=11, color=MUTED))

    cx_b, cy_b = x_b + w_box/2, y_top + 145
    f.append(varrow(cx_b - 90, cy_b, cx_b + 90, cy_b, color=BORDER, sw=1.2))
    f.append(varrow(cx_b, cy_b + 80, cx_b, cy_b - 80, color=BORDER, sw=1.2))
    f.append(text(cx_b + 95, cy_b + 4, "q", size=11, color=MUTED))
    f.append(text(cx_b + 4, cy_b - 82, "p", size=11, color=MUTED))

    rx_b, ry_b = 65, 45
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="3,3"/>' %
             (cx_b, cy_b, rx_b, ry_b, MAIN))

    golden_ratio = (1 + math.sqrt(5)) / 2
    for k in range(35):
        ang = 2 * math.pi * k * golden_ratio
        px = cx_b + rx_b * math.cos(ang)
        py = cy_b + ry_b * math.sin(ang)
        f.append(circle(px, py, 3, fill=GREEN, stroke=INK, sw=0.8))

    f.append(text(x_b + w_box/2, y_top + h_box - 18, "Замкнена крива S¹", size=12, bold=True, color=INK))

    x_c = 565
    f.append(rect(x_c, y_top, w_box, h_box, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(x_c + w_box/2, y_top + 22, "Детермінований хаос", size=13, bold=True))
    f.append(text(x_c + w_box/2, y_top + 38, "(Дивний атрактор)", size=11, color=MUTED))

    cx_c, cy_c = x_c + w_box/2, y_top + 145
    f.append(varrow(cx_c - 90, cy_c, cx_c + 90, cy_c, color=BORDER, sw=1.2))
    f.append(varrow(cx_c, cy_c + 80, cx_c, cy_c - 80, color=BORDER, sw=1.2))
    f.append(text(cx_c + 95, cy_c + 4, "q", size=11, color=MUTED))
    f.append(text(cx_c + 4, cy_c - 82, "p", size=11, color=MUTED))

    for i in range(120):
        t = (i / 120.0) * 2 * math.pi
        x_raw = 65 * math.sin(t) - 15 * math.sin(2*t)
        y_raw = 50 * math.cos(t) + 20 * math.sin(3*t)
        fold = 6.0 * math.sin(10 * t)
        px = cx_c + x_raw
        py = cy_c + y_raw + fold
        f.append(circle(px, py, 2, fill=PURPLE, stroke="none"))

    f.append(text(x_c + w_box/2, y_top + h_box - 18, "Фрактальна структура", size=12, bold=True, color=INK))

    render(os.path.join(IMG, "poincare-types.svg"), W, H, *f)

# ── Фігура 3: Стробоскопічний переріз періодично збуджуваної системи ─────────
def fig_stroboscopic_section():
    W, H = 820, 380
    f = []

    f.append(text(W / 2, 24, "Стробоскопічний переріз для періодично збуджуваної системи", size=15, bold=True))

    x0, y0 = 40, 50
    w_p, h_p = 740, 310
    f.append(rect(x0, y0, w_p, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))

    f.append(varrow(80, 260, 720, 260, color=MUTED, sw=1.5))
    f.append(text(725, 264, "Час t", size=12, bold=True, color=MUTED))

    t_planes = [
        (160, "t = t₀", "Σ₀"),
        (310, "t = t₀ + T", "Σ₁"),
        (460, "t = t₀ + 2T", "Σ₂"),
        (610, "t = t₀ + 3T", "Σ₃")
    ]

    for px, label_t, label_sig in t_planes:
        poly = [(px - 25, 90), (px + 25, 70), (px + 25, 230), (px - 25, 250)]
        pts_str = " ".join("%.1f,%.1f" % p for p in poly)
        f.append('<polygon points="%s" fill="#EBF3FE" fill-opacity="0.7" stroke="%s" stroke-width="1.5"/>' % (pts_str, MAIN))
        f.append(text(px, 62, label_t, size=11, bold=True, color=MUTED))
        f.append(text(px, 242, label_sig, size=12, bold=True, color=MAIN))

    pts_strobe = [(160, 150), (310, 120), (460, 180), (610, 140)]

    path_d = "M 100 170 Q 130 190 160 150 T 235 100 T 310 120 T 385 220 T 460 180 T 535 90 T 610 140 T 670 160"
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path_d, ACCENT))

    for i, (px, py) in enumerate(pts_strobe):
        f.append(f'<line x1="{px:.1f}" y1="75" x2="{px:.1f}" y2="245" stroke="{PURPLE}" stroke-width="1" stroke-dasharray="2,2"/>')
        f.append(circle(px, py, 5, fill=GREEN, stroke=INK, sw=1.5))
        f.append(text(px + 8, py - 8, f"x({i}T)", size=11, bold=True, color=INK))

    f.append(rect(x0 + 20, y0 + h_p - 45, w_p - 40, 32, fill='#FFFFFF', stroke=BORDER, sw=1, rx=4))
    f.append(text(x0 + w_p/2, y0 + h_p - 24, "Фіксація стану через кожен період зовнішньої сили T = 2π / ω", size=12, bold=True, color=INK))

    render(os.path.join(IMG, "stroboscopic-section.svg"), W, H, *f)

# ── Фігура 4: Чисельний алгоритм точного виявлення перетину секущої поверхні ──
def fig_root_finding_henon():
    W, H = 820, 360
    f = []

    f.append(text(W / 2, 24, "Чисельний алгоритм виявлення перетину секущої поверхні", size=15, bold=True))

    x0, y0 = 40, 50
    w_p, h_p = 740, 290
    f.append(rect(x0, y0, w_p, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))

    x_sec = 420
    f.append(line(x_sec, y0 + 30, x_sec, y0 + h_p - 30, color=MAIN, sw=2.5))
    f.append(text(x_sec, y0 + 22, "Секуща поверхня g(x) = 0", size=13, bold=True, color=MAIN))

    f.append(text(x_sec - 120, y0 + 45, "g(x) < 0", size=12, bold=True, color=MUTED))
    f.append(text(x_sec + 120, y0 + 45, "g(x) > 0", size=12, bold=True, color=MUTED))

    pk = (220, 210)
    pk1 = (600, 110)
    pstar = (x_sec, 160)

    f.append('<path d="M 120 240 Q 220 210 420 160 T 600 110 T 700 90" fill="none" stroke="%s" stroke-width="2.2"/>' % ACCENT)

    f.append(f'<line x1="{pk[0]:.1f}" y1="{pk[1]:.1f}" x2="{pk1[0]:.1f}" y2="{pk1[1]:.1f}" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="4,4"/>')

    f.append(circle(pk[0], pk[1], 6, fill=MAIN, stroke=INK, sw=1.5))
    f.append(text(pk[0] - 15, pk[1] + 22, "xₖ (tₖ)", size=12, bold=True, color=INK))

    f.append(circle(pk1[0], pk1[1], 6, fill=ACCENT, stroke=INK, sw=1.5))
    f.append(text(pk1[0] + 15, pk1[1] + 22, "xₖ₊₁ (tₖ + Δt)", size=12, bold=True, color=INK))

    f.append(circle(pstar[0], pstar[1], 7, fill=GREEN, stroke=INK, sw=1.8))
    f.append(text(pstar[0] - 18, pstar[1] - 15, "Точний перетин x* (g=0)", size=12, bold=True, color=GREEN))

    f.append(varrow(pk1[0], pk1[1] - 20, pstar[0] + 15, pstar[1] - 15, color=GREEN, sw=1.8, head=8))
    f.append(text(540, 105, "Корінь t*: Ено / Ерміт", size=11, bold=True, color=GREEN))

    f.append(rect(x0 + 20, y0 + h_p - 45, w_p - 40, 32, fill='#FFFFFF', stroke=BORDER, sw=1, rx=4))
    f.append(text(x0 + w_p/2, y0 + h_p - 24, "Виявлення знака g(xₖ)·g(xₖ₊₁) < 0 ──► Пошук кореня t* з точністю до 10⁻¹²", size=12, bold=True, color=INK))

    render(os.path.join(IMG, "root-finding-henon.svg"), W, H, *f)

if __name__ == "__main__":
    fig_poincare_concept()
    fig_poincare_types()
    fig_stroboscopic_section()
    fig_root_finding_henon()
    print("Figures generated successfully in ./img/")

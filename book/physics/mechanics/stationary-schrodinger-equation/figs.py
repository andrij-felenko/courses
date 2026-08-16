# -*- coding: utf-8 -*-
"""Фігури до теми «Одновимірне стаціонарне рівняння Шредінгера».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

MAIN = "#2457d6"      # Синій для хвильових функцій
ACCENT = "#c0392b"    # Червоний для потенціалу / енергії
GREEN = "#27ae60"     # Зелений для густини ймовірності
BORDER = "#d0d7de"

def head_at(x, y, dx, dy, color=INK, size=8):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.4, by + ny * size * 0.4,
               bx - nx * size * 0.4, by - ny * size * 0.4, color))

def varrow(x1, y1, x2, y2, color=LINE, sw=1.5, head=8):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)

# ── Фігура 1: Нескінченно глибока потенціальна яма ───────────────────────────
def fig_infinite_well():
    W, H = 820, 440
    f = []

    f.append(text(W / 2, 28, "Нескінченно глибока потенціальна яма та квантування енергії", size=16, bold=True))

    x_left, x_right = 260, 620
    y_top, y_bot = 70, 370
    well_w = x_right - x_left

    # Нескінченні стінки (заштриховані блоки)
    f.append(rect(60, y_top, x_left - 60, y_bot - y_top + 20, fill='#EAECEE', stroke=BORDER, sw=1.2, rx=2))
    f.append(rect(x_right, y_top, W - 60 - x_right, y_bot - y_top + 20, fill='#EAECEE', stroke=BORDER, sw=1.2, rx=2))

    # Стінки ями V = infinity
    f.append(line(x_left, y_top, x_left, y_bot + 20, color=ACCENT, sw=3.0))
    f.append(line(x_right, y_top, x_right, y_bot + 20, color=ACCENT, sw=3.0))
    f.append(line(x_left, y_bot + 20, x_right, y_bot + 20, color=ACCENT, sw=3.0))

    f.append(text(160, y_top + 40, "V(x) = ∞", size=15, color=ACCENT, bold=True))
    f.append(text(W - 160, y_top + 40, "V(x) = ∞", size=15, color=ACCENT, bold=True))
    f.append(text(W / 2, y_bot + 12, "V(x) = 0", size=13, color=MUTED))

    # Осі
    f.append(varrow(180, y_bot + 20, W - 120, y_bot + 20, color=INK, sw=1.5))
    f.append(text(W - 110, y_bot + 26, "x", size=14, color=INK))

    f.append(text(x_left, y_bot + 38, "x = 0", size=12, color=INK))
    f.append(text(x_right, y_bot + 38, "x = L", size=12, color=INK))

    # Рівні енергії E1, E2, E3
    y_e1 = y_bot - 40
    y_e2 = y_bot - 120
    y_e3 = y_bot - 240

    # Штрихові лінії рівнів енергії
    f.append(line(x_left, y_e1, x_right, y_e1, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(x_left, y_e2, x_right, y_e2, color=MUTED, sw=1.2, dash="4 4"))
    f.append(line(x_left, y_e3, x_right, y_e3, color=MUTED, sw=1.2, dash="4 4"))

    f.append(text(x_left - 15, y_e1 + 4, "E₁", size=13, color=ACCENT, bold=True, anchor="end"))
    f.append(text(x_left - 15, y_e2 + 4, "E₂ = 4E₁", size=13, color=ACCENT, bold=True, anchor="end"))
    f.append(text(x_left - 15, y_e3 + 4, "E₃ = 9E₁", size=13, color=ACCENT, bold=True, anchor="end"))

    # Хвильові функції psi_1, psi_2, psi_3
    amp = 32

    def draw_psi(n, y_base, stroke_color):
        pts = []
        for i in range(101):
            s = i / 100.0
            px = x_left + s * well_w
            val = math.sin(n * math.pi * s)
            py = y_base - val * amp
            pts.append("%.1f,%.1f" % (px, py))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), stroke_color))

    draw_psi(1, y_e1, MAIN)
    draw_psi(2, y_e2, MAIN)
    draw_psi(3, y_e3, MAIN)

    f.append(text(x_right + 15, y_e1 - 10, "ψ₁ (0 вузлів)", size=12, color=MAIN, bold=True, anchor="start"))
    f.append(text(x_right + 15, y_e2 - 10, "ψ₂ (1 вузол)", size=12, color=MAIN, bold=True, anchor="start"))
    f.append(text(x_right + 15, y_e3 - 10, "ψ₃ (2 вузли)", size=12, color=MAIN, bold=True, anchor="start"))

    # Підпис знизу
    f.append(text(W / 2, H - 15, "Формула рівнів енергії: Eₙ = (n² · π² · ℏ²) / (2 · m · L²),  n = 1, 2, 3...", size=13, bold=True, color=INK))

    render(os.path.join(IMG, "fig-1-infinite-well.svg"), W, H, *f)

# ── Фігура 2: Скінченна потенціальна яма та тунельний хвіст ─────────────────
def fig_finite_well():
    W, H = 820, 440
    f = []

    f.append(text(W / 2, 28, "Скінченна яма та проникнення хвилі у класично заборонену область", size=16, bold=True))

    x_left, x_right = 260, 560
    well_w = x_right - x_left
    y_v0 = 100
    y_bot = 350

    # Потенціал V(x)
    pts_v = [
        "80,%.1f" % y_v0,
        "%.1f,%.1f" % (x_left, y_v0),
        "%.1f,%.1f" % (x_left, y_bot),
        "%.1f,%.1f" % (x_right, y_bot),
        "%.1f,%.1f" % (x_right, y_v0),
        "%.1f,%.1f" % (W - 80, y_v0)
    ]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_v), ACCENT))

    f.append(text(140, y_v0 - 10, "V = V₀ (бар'єр)", size=13, color=ACCENT, bold=True))
    f.append(text(W - 140, y_v0 - 10, "V = V₀ (бар'єр)", size=13, color=ACCENT, bold=True))
    f.append(text(W / 2, y_bot + 20, "V = 0 (яма)", size=13, color=MUTED))

    # Зв'язаний стан E < V0
    y_e = 220
    f.append(line(80, y_e, W - 80, y_e, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(65, y_e + 4, "E < V₀", size=13, color=ACCENT, bold=True, anchor="end"))

    # Хвильова функція зв'язаного стану з експоненційними хвостами
    pts_psi = []
    amp = 45
    kappa = 0.025

    # Область 1: x < x_left
    for px in range(100, int(x_left) + 1):
        dx = px - x_left
        val = math.exp(kappa * dx)
        py = y_e - val * amp
        pts_psi.append("%.1f,%.1f" % (px, py))

    # Область 2: inside well
    for px in range(int(x_left) + 1, int(x_right)):
        s = (px - x_left) / well_w
        val = math.cos(math.pi * (s - 0.5) * 1.2)
        py = y_e - val * amp
        pts_psi.append("%.1f,%.1f" % (px, py))

    # Область 3: x > x_right
    for px in range(int(x_right), W - 100):
        dx = px - x_right
        val = math.exp(-kappa * dx) * math.cos(math.pi * 0.5 * 1.2)
        py = y_e - val * amp
        pts_psi.append("%.1f,%.1f" % (px, py))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_psi), MAIN))

    # Виділення тунельних хвостів
    f.append(textbox(170, y_e + 50, "Експоненційне\nзгасання ~ e⁻κ|x|", size=11, fill="#F0F4FC", stroke=MAIN)[0])
    f.append(textbox(W - 170, y_e + 50, "Експоненційне\nзгасання ~ e⁻κx", size=11, fill="#F0F4FC", stroke=MAIN)[0])

    f.append(varrow(170, y_e + 30, 200, y_e + 10, color=MAIN, sw=1.2))
    f.append(varrow(W - 170, y_e + 30, W - 200, y_e + 10, color=MAIN, sw=1.2))

    # Текстові позначки областей
    f.append(text(150, H - 55, "Класично заборонена\nобласть (E < V₀)", size=12, color=ACCENT, anchor="middle"))
    f.append(text(W / 2, H - 55, "Класично дозволена\nобласть (E > V)", size=12, color=GREEN, anchor="middle"))
    f.append(text(W - 150, H - 55, "Класично заборонена\nобласть (E < V₀)", size=12, color=ACCENT, anchor="middle"))

    render(os.path.join(IMG, "fig-2-finite-well-tunneling.svg"), W, H, *f)

# ── Фігура 3: Квантовий гармонічний осцилятор ────────────────────────────────
def fig_harmonic_oscillator():
    W, H = 820, 460
    f = []

    f.append(text(W / 2, 28, "Квантовий гармонічний осцилятор: парабола V(x) та нульова енергія", size=16, bold=True))

    cx, cy = W / 2, 380
    scale_x = 180

    # Параболічний потенціал V(x) = 0.5 * m * omega^2 * x^2
    pts_parabola = []
    for i in range(101):
        xn = (i - 50) / 45.0
        px = cx + xn * scale_x
        py = cy - (xn**2) * 200
        pts_parabola.append("%.1f,%.1f" % (px, py))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_parabola), ACCENT))

    # Осі
    f.append(varrow(cx - scale_x - 40, cy, cx + scale_x + 40, cy, color=INK, sw=1.5))
    f.append(text(cx + scale_x + 50, cy + 5, "x", size=14, color=INK))
    f.append(varrow(cx, cy + 20, cx, 55, color=INK, sw=1.5))
    f.append(text(cx - 15, 60, "E, V(x)", size=13, color=INK, anchor="end"))

    # Рівні енергії E_n = (n + 1/2) * hbar * omega
    levels = [
        (0, cy - 40, "E₀ = ½ ℏω (нульові коливання)", MAIN),
        (1, cy - 110, "E₁ = ³⁄₂ ℏω", MAIN),
        (2, cy - 180, "E₂ = ⁵⁄₂ ℏω", MAIN),
        (3, cy - 250, "E₃ = ⁷⁄₂ ℏω", MAIN),
    ]

    for n, y_lev, label, col in levels:
        xn_val = math.sqrt(max(0, (cy - y_lev) / 200.0))
        x_l = cx - xn_val * scale_x
        x_r = cx + xn_val * scale_x

        f.append(line(x_l, y_lev, x_r, y_lev, color=MUTED, sw=1.2, dash="4 4"))
        f.append(text(x_r + 15, y_lev + 4, label, size=12, color=ACCENT, bold=True, anchor="start"))

        # Малюємо хвильові функції
        pts_w = []
        amp = 22
        for i in range(101):
            s = (i - 50) / 45.0
            px = cx + s * scale_x
            if n == 0:
                val = math.exp(-2.0 * s**2)
            elif n == 1:
                val = 2.0 * s * math.exp(-2.0 * s**2)
            elif n == 2:
                val = (4.0 * s**2 - 1.0) * math.exp(-2.0 * s**2)
            else:
                val = (8.0 * s**3 - 6.0 * s) * math.exp(-2.0 * s**2) * 0.4

            py = y_lev - val * amp
            pts_w.append("%.1f,%.1f" % (px, py))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (" ".join(pts_w), col))

    # Подвійна стрілка рівновіддаленості ΔE = ℏω
    f.append(varrow(cx - 120, cy - 40, cx - 120, cy - 110, color=GREEN, sw=1.5))
    f.append(varrow(cx - 120, cy - 110, cx - 120, cy - 40, color=GREEN, sw=1.5))
    f.append(text(cx - 130, cy - 72, "ΔE = ℏω", size=13, color=GREEN, bold=True, anchor="end"))

    f.append(text(W / 2, H - 15, "Рівні енергії еквідистантні; для n = 0 енергія не нульова: E₀ = ½ ℏω", size=13, bold=True, color=INK))

    render(os.path.join(IMG, "fig-3-harmonic-oscillator.svg"), W, H, *f)

# ── Фігура 4: Потенціальний бар'єр та тунелювання ────────────────────────────
def fig_tunnel_barrier():
    W, H = 820, 440
    f = []

    f.append(text(W / 2, 28, "Квантове тунелювання крізь прямокутний бар'єр V₀", size=16, bold=True))

    x1, x2 = 320, 480
    y_v0 = 120
    y_bot = 330
    y_e = 210

    # Заповнений бар'єр
    f.append(rect(x1, y_v0, x2 - x1, y_bot - y_v0, fill='#FADBD8', stroke=ACCENT, sw=2.5, rx=0))
    f.append(text((x1 + x2) / 2, y_v0 + 35, "V₀", size=18, color=ACCENT, bold=True))
    f.append(text((x1 + x2) / 2, y_v0 + 60, "Бар'єр (ширина a)", size=12, color=ACCENT))

    # Осі та енергія E
    f.append(line(80, y_e, W - 80, y_e, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(70, y_e + 4, "E < V₀", size=13, color=ACCENT, bold=True, anchor="end"))

    # Падаюча, відбита, тунельована і пропущена хвилі
    amp = 35
    k = 0.07
    kappa = 0.03

    pts_inc = []
    for px in range(90, int(x1) + 1):
        val = math.cos(k * (px - x1))
        py = y_e - val * amp
        pts_inc.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_inc), MAIN))

    pts_in = []
    for px in range(int(x1), int(x2) + 1):
        dx = px - x1
        val = math.exp(-kappa * dx)
        py = y_e - val * amp
        pts_in.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_in), ACCENT))

    trans_amp = amp * math.exp(-kappa * (x2 - x1))
    pts_trans = []
    for px in range(int(x2), W - 90):
        val = math.cos(k * (px - x2))
        py = y_e - val * trans_amp
        pts_trans.append("%.1f,%.1f" % (px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_trans), GREEN))

    f.append(varrow(140, y_e - 50, 230, y_e - 50, color=MAIN, sw=2.0))
    f.append(text(185, y_e - 60, "Падаюча хвиля A·eⁱᵏˣ", size=12, color=MAIN, bold=True))

    f.append(varrow(230, y_e + 50, 140, y_e + 50, color=MUTED, sw=1.5))
    f.append(text(185, y_e + 68, "Відбита хвиля B·e⁻ⁱᵏˣ", size=12, color=MUTED))

    f.append(varrow(x2 + 30, y_e - 50, x2 + 130, y_e - 50, color=GREEN, sw=2.0))
    f.append(text(x2 + 80, y_e - 60, "Пропущена хвиля F·eⁱᵏˣ", size=12, color=GREEN, bold=True))

    f.append(line(x1, y_bot, x1, y_bot + 25, color=INK, sw=1.2))
    f.append(line(x2, y_bot, x2, y_bot + 25, color=INK, sw=1.2))
    f.append(text(x1, y_bot + 38, "x = 0", size=12, color=INK))
    f.append(text(x2, y_bot + 38, "x = a", size=12, color=INK))

    f.append(text(W / 2, H - 15, "Коефіцієнт проходження: T ≈ exp( -2 · a · √(2m(V₀ - E)) / ℏ )", size=13, bold=True, color=INK))

    render(os.path.join(IMG, "fig-4-tunnel-barrier.svg"), W, H, *f)

if __name__ == '__main__':
    fig_infinite_well()
    fig_finite_well()
    fig_harmonic_oscillator()
    fig_tunnel_barrier()
    print("Всі фігури згенеровано у ./img/")

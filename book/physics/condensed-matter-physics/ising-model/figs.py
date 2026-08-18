# -*- coding: utf-8 -*-
"""Фігури до теми «Модель Ізінга».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

BORDER = "#cbd5e1"

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

# ── Фігура 1: Конфігурації спінів у моделі Ізінга ────────────────────────────
def fig_ising_lattice_configurations():
    W, H = 780, 380
    f = []

    f.append(text(W / 2, 26, "Спінові конфігурації 1D та 2D граток у моделі Ізінга", size=16, bold=True, color=INK))

    panel_w = 360
    panel_h = 280
    y_top = 50

    # Left Panel: 1D Chain
    x1 = 20
    f.append(rect(x1, y_top, panel_w, panel_h, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(x1 + panel_w / 2, y_top + 22, "1D Спіновий ланцюжок (T > 0)", size=14, bold=True, color="#1e40af"))

    # Draw 1D spins
    spin_y = y_top + 100
    f.append(path_svg(f"M {x1 + 30} {spin_y} L {x1 + panel_w - 30} {spin_y}", stroke="#94a3b8", sw=2, dash="4,4"))

    # 1D Spin orientations: ↑ ↑ ↑ ↑ ↓ ↓ ↓ ↓ ↑ ↑
    spins_1d = [1, 1, 1, 1, -1, -1, -1, -1, 1, 1]
    dx1 = (panel_w - 60) / (len(spins_1d) - 1)
    for idx, s in enumerate(spins_1d):
        sx = x1 + 30 + idx * dx1
        col = "#15803d" if s == 1 else "#dc2626"
        f.append(circle(sx, spin_y, 6, fill=col, stroke="none"))
        if s == 1:
            f.append(arrow(sx, spin_y + 16, sx, spin_y - 18, color=col, sw=2.5))
        else:
            f.append(arrow(sx, spin_y - 16, sx, spin_y + 18, color=col, sw=2.5))

    # Domain wall annotation
    dw_x = x1 + 30 + 3.5 * dx1
    f.append(path_svg(f"M {dw_x} {spin_y - 35} L {dw_x} {spin_y + 35}", stroke="#d97706", sw=2, dash="3,3"))
    f.append(text(dw_x, spin_y - 42, "Доменна стінка (ΔE = 2J)", size=11, bold=True, color="#d97706"))

    f.append(text(x1 + panel_w / 2, y_top + 180, "Ентропія створення стінки: ΔS = k_B ln N", size=12, color=INK))
    f.append(text(x1 + panel_w / 2, y_top + 205, "Вільна енергія: ΔF = 2J - k_B T ln N → -∞", size=12, bold=True, color="#dc2626"))
    f.append(text(x1 + panel_w / 2, y_top + 240, "Результат: флуктуації руйнують порядок при T > 0", size=11, italic=True, color=MUTED))

    # Right Panel: 2D Square Lattice
    x2 = 400
    f.append(rect(x2, y_top, panel_w, panel_h, fill="#eff6ff", stroke=BORDER, rx=6))
    f.append(text(x2 + panel_w / 2, y_top + 22, "2D Квадратна ґратка (Домени та межа)", size=14, bold=True, color="#1e40af"))

    # 2D Grid of spins (6x6)
    grid_size = 6
    g_dx = 38
    g_dy = 32
    gx0 = x2 + 85
    gy0 = y_top + 55

    # Define domain boundary pattern
    # 1: spin up (+1), -1: spin down (-1)
    spins_2d = [
        [ 1,  1,  1, -1, -1, -1],
        [ 1,  1,  1, -1, -1, -1],
        [ 1,  1, -1, -1, -1, -1],
        [ 1,  1, -1, -1, -1, -1],
        [ 1,  1,  1, -1, -1, -1],
        [ 1,  1,  1,  1, -1, -1]
    ]

    for r in range(grid_size):
        for c in range(grid_size):
            cx = gx0 + c * g_dx
            cy = gy0 + r * g_dy
            s = spins_2d[r][c]
            col = "#15803d" if s == 1 else "#dc2626"
            f.append(circle(cx, cy, 5, fill=col, stroke="none"))
            if s == 1:
                f.append(arrow(cx, cy + 10, cx, cy - 12, color=col, sw=2.0))
            else:
                f.append(arrow(cx, cy - 10, cx, cy + 12, color=col, sw=2.0))

    # Draw domain wall boundary line
    dw_path = f"M {gx0 + 2.5*g_dx} {gy0 - 10} L {gx0 + 2.5*g_dx} {gy0 + 1.5*g_dy} L {gx0 + 1.5*g_dx} {gy0 + 1.5*g_dy} L {gx0 + 1.5*g_dx} {gy0 + 3.5*g_dy} L {gx0 + 2.5*g_dx} {gy0 + 3.5*g_dy} L {gx0 + 2.5*g_dx} {gy0 + 4.5*g_dy} L {gx0 + 3.5*g_dx} {gy0 + 4.5*g_dy} L {gx0 + 3.5*g_dx} {gy0 + 5.5*g_dy}"
    f.append(path_svg(dw_path, stroke="#ea580c", sw=2.5, dash="3,3"))

    f.append(text(x2 + panel_w / 2, y_top + 245, "Периметр стінки L: ΔE = 2J·L, ΔF = L(2J - k_B T ln μ)", size=11, bold=True, color="#ea580c"))

    f.append(text(W / 2, H - 12, "В одновимірному випадку фазовий перехід відсутній, у 2D енергія замкненої межі утримує порядок при T < T_c", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'ising-lattice-configurations.svg'), W, H, "\n".join(f))

# ── Фігура 2: Фазовий перехід та залежності M(T) і C_v(T) ─────────────────────
def fig_ising_phase_transition():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 28, "Термодинамічні характеристики 2D моделі Ізінга при фазовому переході", size=16, bold=True, color=INK))

    x_zero = 80
    x_tc = 380
    x_max = 700
    y_top = 60
    y_bot = 350

    f.append(rect(x_zero, y_top, x_tc - x_zero, y_bot - y_top, fill="#f0fdf4", stroke="none"))
    f.append(rect(x_tc, y_top, x_max - x_tc, y_bot - y_top, fill="#f8fafc", stroke="none"))

    f.append(path_svg(f"M {x_tc} {y_top} L {x_tc} {y_bot}", stroke="#dc2626", sw=2, dash="4,4"))
    f.append(text(x_tc, y_top + 18, "T = T_c", size=13, bold=True, color="#dc2626"))

    f.append(text((x_zero + x_tc) / 2, y_top + 20, "Феромагнітна фаза (M > 0)", size=12, bold=True, color="#15803d"))
    f.append(text((x_tc + x_max) / 2, y_top + 20, "Парамагнітна фаза (M = 0)", size=12, bold=True, color="#475569"))

    # Axes
    f.append(arrow(x_zero, y_bot, x_max + 25, y_bot, color=INK, sw=1.5))
    f.append(text(x_max + 35, y_bot + 4, "T / T_c", size=13, bold=True, italic=True, color=INK))
    f.append(arrow(x_zero, y_bot, x_zero, y_top - 15, color=INK, sw=1.5))
    f.append(text(x_zero - 25, y_top - 10, "M, C_v", size=13, bold=True, italic=True, color=INK))

    f.append(text(x_zero, y_bot + 18, "0", size=11, color=MUTED))
    f.append(text(x_tc, y_bot + 18, "1.0", size=12, bold=True, color="#dc2626"))

    # Magnetization curve M(T) = (1 - sinh^-4(2J/kT))^1/8
    # Approximated smooth curve going to 0 with beta = 1/8 exponent
    pts_m = []
    y_m0 = 100
    for i in range(101):
        t_ratio = i / 100.0
        x = x_zero + t_ratio * (x_tc - x_zero)
        if t_ratio >= 0.999:
            val = 0.0
        else:
            val = (1.0 - t_ratio**1.5)**0.125
        y = y_bot - val * (y_bot - y_m0)
        pts_m.append((x, y))

    # Above T_c, M = 0
    pts_m.append((x_max, y_bot))

    d_m = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_m)
    f.append(path_svg(d_m, stroke="#1d4ed8", sw=3))
    f.append(text(x_zero + 100, y_m0 + 20, "M(T) ~ (1 - T/T_c)^{1/8}", size=13, bold=True, color="#1d4ed8"))

    # Heat capacity C_v(T) curve with logarithmic peak at T_c
    pts_c1 = []
    for i in range(101):
        t_ratio = i / 100.0
        x = x_zero + t_ratio * (x_tc - x_zero)
        dt = max(0.01, 1.0 - t_ratio)
        val = 0.3 + 0.35 * math.log(1.0 / dt)
        val = min(1.8, val)
        y = y_bot - (val / 1.8) * (y_bot - y_top - 30)
        pts_c1.append((x, y))

    d_c1 = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_c1)
    f.append(path_svg(d_c1, stroke="#ea580c", sw=2.5))

    pts_c2 = []
    for i in range(101):
        t_ratio = i / 100.0
        x = x_tc + t_ratio * (x_max - x_tc)
        dt = max(0.01, t_ratio)
        val = 0.3 + 0.35 * math.log(1.0 / dt)
        val = min(1.8, val)
        y = y_bot - (val / 1.8) * (y_bot - y_top - 30)
        pts_c2.append((x, y))

    d_c2 = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_c2)
    f.append(path_svg(d_c2, stroke="#ea580c", sw=2.5))

    f.append(text(x_tc + 50, y_top + 60, "C_v(T) ~ -ln|1 - T/T_c|", size=13, bold=True, color="#ea580c"))
    f.append(text(x_tc + 50, y_top + 80, "Логарифмічна розбіжність (α = 0)", size=11, color="#ea580c"))

    f.append(text(W / 2, H - 12, "Спонтанна намагніченість спадає за степеневим законом з критичним індексом β = 1/8", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'ising-phase-transition.svg'), W, H, "\n".join(f))

# ── Фігура 3: Модель середнього поля vs Точний розв'язок Онсагера ─────────────
def fig_ising_mean_field_vs_onsager():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 28, "Порівняння намагніченості: Теорія середнього поля (MFT) vs 2D Онсагер", size=16, bold=True, color=INK))

    x_zero = 80
    x_tc_ons = 350
    x_tc_mft = 580
    x_max = 700
    y_top = 60
    y_bot = 350

    # Vertical dash lines for T_c values
    f.append(path_svg(f"M {x_tc_ons} {y_top} L {x_tc_ons} {y_bot}", stroke="#15803d", sw=1.8, dash="4,4"))
    f.append(text(x_tc_ons, y_top + 18, "T_c (2D Онсагер)", size=12, bold=True, color="#15803d"))
    f.append(text(x_tc_ons, y_top + 34, "2.269 J/k_B", size=11, color="#15803d"))

    f.append(path_svg(f"M {x_tc_mft} {y_top} L {x_tc_mft} {y_bot}", stroke="#dc2626", sw=1.8, dash="4,4"))
    f.append(text(x_tc_mft, y_top + 18, "T_c (MFT, z=4)", size=12, bold=True, color="#dc2626"))
    f.append(text(x_tc_mft, y_top + 34, "4.000 J/k_B", size=11, color="#dc2626"))

    # Axes
    f.append(arrow(x_zero, y_bot, x_max + 25, y_bot, color=INK, sw=1.5))
    f.append(text(x_max + 35, y_bot + 4, "k_B T / J", size=13, bold=True, italic=True, color=INK))
    f.append(arrow(x_zero, y_bot, x_zero, y_top - 15, color=INK, sw=1.5))
    f.append(text(x_zero - 25, y_top - 10, "M / M_0", size=13, bold=True, italic=True, color=INK))

    f.append(text(x_zero, y_bot + 18, "0", size=11, color=MUTED))

    # Curve 1: 1D Ising (M = 0 for T > 0)
    f.append(path_svg(f"M {x_zero} {y_bot} L {x_max} {y_bot}", stroke="#64748b", sw=3))
    f.append(text(x_zero + 40, y_bot - 15, "1D Модель (M = 0 для T > 0)", size=11, bold=True, color="#64748b"))

    # Curve 2: 2D Onsager Exact Solution
    pts_ons = []
    y_m0 = 100
    for i in range(101):
        t_ratio = i / 100.0
        x = x_zero + t_ratio * (x_tc_ons - x_zero)
        if t_ratio >= 0.999:
            val = 0.0
        else:
            val = (1.0 - t_ratio**1.6)**0.125
        y = y_bot - val * (y_bot - y_m0)
        pts_ons.append((x, y))

    d_ons = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_ons)
    f.append(path_svg(d_ons, stroke="#15803d", sw=3))
    f.append(text(x_zero + 110, y_m0 + 20, "2D Онсагер (β = 1/8)", size=12, bold=True, color="#15803d"))

    # Curve 3: Mean Field Theory (tanh)
    pts_mft = []
    for i in range(101):
        t_ratio = i / 100.0
        x = x_zero + t_ratio * (x_tc_mft - x_zero)
        val = math.sqrt(max(0.0, 1.0 - t_ratio))
        y = y_bot - val * (y_bot - y_m0)
        pts_mft.append((x, y))

    d_mft = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_mft)
    f.append(path_svg(d_mft, stroke="#dc2626", sw=2.5, dash="6,3"))
    f.append(text(x_tc_ons + 40, y_m0 + 70, "Середнє поле MFT (β = 1/2)", size=12, bold=True, color="#dc2626"))

    f.append(text(W / 2, H - 12, "Середнє поле завищує критичну температуру (4.0J vs 2.27J), ігноруючи короткосяжні флуктуації", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'ising-mean-field-vs-onsager.svg'), W, H, "\n".join(f))

def main():
    fig_ising_lattice_configurations()
    fig_ising_phase_transition()
    fig_ising_mean_field_vs_onsager()
    print("All figures successfully generated in ./img/")

if __name__ == '__main__':
    main()

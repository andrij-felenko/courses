# -*- coding: utf-8 -*-
"""Фігури до теми «Зонна структура й рівень Фермі».
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

# ── Фігура 1: Формування енергетичних зон з атомних рівнів ───────────────────
def fig_band_formation_atomic():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Формування енергетичних зон з ізольованих атомних рівнів", size=16, bold=True, color=INK))

    x_left = 90
    x_eq = 480
    x_right = 690
    y_top = 60
    y_bot = 360

    # Axes
    f.append(arrow(x_right, y_bot, x_left - 20, y_bot, color=INK, sw=1.5))
    f.append(text(x_left - 30, y_bot + 18, "Міжатомна відстань a", size=12, bold=True, color=INK))
    f.append(text(x_right, y_bot + 18, "Ізольовані атоми (a → ∞)", size=11, color=MUTED))

    f.append(arrow(x_left, y_bot, x_left, y_top - 15, color=INK, sw=1.5))
    f.append(text(x_left - 25, y_top - 10, "Енергія E", size=13, bold=True, color=INK))

    # Equilibrium lattice constant dashed line
    f.append(path_svg(f"M {x_eq} {y_top} L {x_eq} {y_bot}", stroke="#2563eb", sw=1.5, dash="4,4"))
    f.append(text(x_eq, y_bot + 18, "a₀ (кристал)", size=12, bold=True, color="#2563eb"))

    # Conduction band (upper split)
    pts_c_top = []
    pts_c_bot = []
    for i in range(101):
        t = i / 100.0 # 0 at right, 1 at left
        x = x_right - t * (x_right - x_left)
        spread = 0.0 if t < 0.3 else ((t - 0.3) / 0.7) ** 1.8 * 65.0
        y_center = 120 - t * 15
        pts_c_top.append((x, y_center - spread))
        pts_c_bot.append((x, y_center + spread))

    d_cb = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_c_top) + \
           " L " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in reversed(pts_c_bot)) + " Z"
    f.append(path_svg(d_cb, fill="#dbeafe", stroke="#1d4ed8", sw=1.5))
    f.append(text(x_eq, 100, "Зона провідності", size=12, bold=True, color="#1e40af"))

    # Valence band (lower split)
    pts_v_top = []
    pts_v_bot = []
    for i in range(101):
        t = i / 100.0
        x = x_right - t * (x_right - x_left)
        spread = 0.0 if t < 0.25 else ((t - 0.25) / 0.75) ** 1.8 * 55.0
        y_center = 290 + t * 10
        pts_v_top.append((x, y_center - spread))
        pts_v_bot.append((x, y_center + spread))

    d_vb = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_v_top) + \
           " L " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in reversed(pts_v_bot)) + " Z"
    f.append(path_svg(d_vb, fill="#dcfce7", stroke="#15803d", sw=1.5))
    f.append(text(x_eq, 310, "Валентна зона", size=12, bold=True, color="#15803d"))

    # Discrete atomic energy levels on the right
    f.append(path_svg(f"M {x_right - 40} 120 L {x_right + 30} 120", stroke="#1d4ed8", sw=2))
    f.append(text(x_right + 35, 124, "E₂ (атомний рівень)", size=11, color="#1d4ed8", anchor="start"))

    f.append(path_svg(f"M {x_right - 40} 290 L {x_right + 30} 290", stroke="#15803d", sw=2))
    f.append(text(x_right + 35, 294, "E₁ (атомний рівень)", size=11, color="#15803d", anchor="start"))

    # Band gap E_g at a_0
    t_eq = (x_right - x_eq) / (x_right - x_left)
    spread_c = ((t_eq - 0.3) / 0.7) ** 1.8 * 65.0
    y_c_min = (120 - t_eq * 15) + spread_c

    spread_v = ((t_eq - 0.25) / 0.75) ** 1.8 * 55.0
    y_v_max = (290 + t_eq * 10) - spread_v

    f.append(arrow(x_eq + 70, (y_c_min + y_v_max) / 2, x_eq + 70, y_c_min - 2, color="#dc2626", sw=1.8))
    f.append(arrow(x_eq + 70, (y_c_min + y_v_max) / 2, x_eq + 70, y_v_max + 2, color="#dc2626", sw=1.8))
    f.append(text(x_eq + 80, (y_c_min + y_v_max) / 2 + 4, "E_g (заборонена зона)", size=12, bold=True, color="#dc2626", anchor="start"))

    f.append(text(W / 2, H - 12, "Перекриття хвильових функцій при зближенні атомів розщеплює рівні у дозволені енергетичні зони", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'band-formation-atomic.svg'), W, H, "\n".join(f))

# ── Фігура 2: Розподіл Фермі — Дірака при різних температурах ────────────────
def fig_fermi_dirac_temperature():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Функція розподілу Фермі — Дірака f(E) при різних температурах", size=16, bold=True, color=INK))

    x_zero = 100
    x_ef = 380
    x_max = 680
    y_top = 60
    y_bot = 350
    h_graph = y_bot - y_top

    # Axes
    f.append(arrow(x_zero, y_bot, x_max + 30, y_bot, color=INK, sw=1.5))
    f.append(text(x_max + 40, y_bot + 4, "Енергія E", size=13, bold=True, italic=True, color=INK))

    f.append(arrow(x_zero, y_bot, x_zero, y_top - 15, color=INK, sw=1.5))
    f.append(text(x_zero - 25, y_top - 10, "f(E)", size=13, bold=True, color=INK))

    # Ticks
    f.append(text(x_zero - 15, y_bot + 4, "0", size=11, color=MUTED))
    f.append(path_svg(f"M {x_zero - 5} {y_top} L {x_zero} {y_top}", stroke=INK, sw=1.5))
    f.append(text(x_zero - 15, y_top + 4, "1.0", size=11, bold=True, color=INK))

    y_half = y_top + h_graph / 2
    f.append(path_svg(f"M {x_zero - 5} {y_half} L {x_max} {y_half}", stroke="#94a3b8", sw=1.0, dash="3,3"))
    f.append(text(x_zero - 18, y_half + 4, "0.5", size=11, color=MUTED))

    # E_F dashed line
    f.append(path_svg(f"M {x_ef} {y_top - 10} L {x_ef} {y_bot + 10}", stroke="#dc2626", sw=1.5, dash="4,4"))
    f.append(text(x_ef, y_bot + 24, "E_F (рівень Фермі)", size=12, bold=True, color="#dc2626"))

    # Curve 1: T = 0 K (step function)
    d_t0 = f"M {x_zero} {y_top} L {x_ef} {y_top} L {x_ef} {y_bot} L {x_max} {y_bot}"
    f.append(path_svg(d_t0, stroke="#1e293b", sw=3))
    f.append(text(x_ef - 120, y_top + 20, "T = 0 K (сходинка)", size=11, bold=True, color="#1e293b"))

    # Curve 2: T_1 = 300 K (room temperature)
    pts_t1 = []
    for i in range(151):
        x = x_zero + (i / 150.0) * (x_max - x_zero)
        e_diff = (x - x_ef) / 28.0
        val = 1.0 / (1.0 + math.exp(max(-10.0, min(10.0, e_diff))))
        y = y_bot - val * h_graph
        pts_t1.append((x, y))

    d_t1 = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_t1)
    f.append(path_svg(d_t1, stroke="#2563eb", sw=2.5))
    f.append(text(x_ef + 80, y_top + 60, "T = 300 K (кімнатна)", size=11, bold=True, color="#2563eb"))

    # Curve 3: T_2 = 1000 K (high temperature)
    pts_t2 = []
    for i in range(151):
        x = x_zero + (i / 150.0) * (x_max - x_zero)
        e_diff = (x - x_ef) / 75.0
        val = 1.0 / (1.0 + math.exp(max(-10.0, min(10.0, e_diff))))
        y = y_bot - val * h_graph
        pts_t2.append((x, y))

    d_t2 = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_t2)
    f.append(path_svg(d_t2, stroke="#d97706", sw=2.5, dash="6,3"))
    f.append(text(x_ef + 130, y_top + 120, "T = 1000 K (висока)", size=11, bold=True, color="#d97706"))

    # Highlight point (E_F, 0.5)
    f.append(circle(x_ef, y_half, 5, fill="#dc2626", stroke="none"))
    f.append(text(x_ef + 12, y_half - 12, "f(E_F) = 1/2 завжди", size=11, bold=True, color="#dc2626", anchor="start"))

    f.append(text(W / 2, H - 12, "При підвищенні температури електрони теплово збуджуються у стани вище рівня Фермі", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'fermi-dirac-temperature.svg'), W, H, "\n".join(f))

# ── Фігура 3: Класифікація матеріалів за зонною структурою ────────────────────
def fig_band_gap_classification():
    W, H = 780, 400
    f = []

    f.append(text(W / 2, 26, "Зонна структура металів, напівпровідників та діелектриків", size=16, bold=True, color=INK))

    p_w = 220
    p_h = 290
    y0 = 55

    materials = [
        ("Метал", "Частково заповнена\nзона або перекриття", "#eff6ff", "#1d4ed8", "metal"),
        ("Напівпровідник", "Вузька заборонена\nзона (E_g ≈ 1 eV)", "#f0fdf4", "#15803d", "semiconductor"),
        ("Діелектрик", "Широка заборонена\nзона (E_g > 5 eV)", "#fef2f2", "#b91c1c", "insulator")
    ]

    for idx, (title, sub, bg, main_c, mtype) in enumerate(materials):
        x = 30 + idx * 245
        f.append(rect(x, y0, p_w, p_h, fill=bg, stroke=BORDER, rx=6))
        f.append(text(x + p_w / 2, y0 + 22, title, size=14, bold=True, color=main_c))

        # Energy Axis inside panel
        ax_x = x + 35
        f.append(arrow(ax_x, y0 + p_h - 60, ax_x, y0 + 45, color=INK, sw=1.2))
        f.append(text(ax_x - 12, y0 + 55, "E", size=12, bold=True, italic=True, color=INK))

        bx = x + 65
        bw = 120

        if mtype == "metal":
            f.append(rect(bx, y0 + 65, bw, 80, fill="#dbeafe", stroke="#1d4ed8", sw=1.5))
            f.append(text(bx + bw / 2, y0 + 105, "Зона провідності", size=11, bold=True, color="#1e40af"))

            ef_y = y0 + 115
            f.append(path_svg(f"M {bx - 10} {ef_y} L {bx + bw + 10} {ef_y}", stroke="#dc2626", sw=2, dash="4,4"))
            f.append(text(bx + bw / 2, ef_y - 8, "E_F (всередині зони)", size=11, bold=True, color="#dc2626"))

            f.append(rect(bx, y0 + 145, bw, 80, fill="#bfdbfe", stroke="#1d4ed8", sw=1.5))
            f.append(text(bx + bw / 2, y0 + 185, "Валентна зона\n(перекриття)", size=11, bold=True, color="#1e40af"))

        elif mtype == "semiconductor":
            f.append(rect(bx, y0 + 60, bw, 60, fill="#dbeafe", stroke="#1d4ed8", sw=1.5))
            f.append(text(bx + bw / 2, y0 + 90, "Зона провідності E_c", size=11, bold=True, color="#1e40af"))

            f.append(arrow(bx + bw + 12, y0 + 155, bx + bw + 12, y0 + 122, color="#15803d", sw=1.5))
            f.append(arrow(bx + bw + 12, y0 + 122, bx + bw + 12, y0 + 155, color="#15803d", sw=1.5))
            f.append(text(bx + bw + 18, y0 + 140, "E_g ≈ 1.1 eV\n(Si)", size=10, bold=True, color="#15803d", anchor="start"))

            ef_y = y0 + 138
            f.append(path_svg(f"M {bx - 10} {ef_y} L {bx + bw + 10} {ef_y}", stroke="#dc2626", sw=2, dash="4,4"))
            f.append(text(bx + bw / 2, ef_y - 6, "E_F (в середині E_g)", size=10, bold=True, color="#dc2626"))

            f.append(rect(bx, y0 + 160, bw, 65, fill="#dcfce7", stroke="#15803d", sw=1.5))
            f.append(text(bx + bw / 2, y0 + 192, "Валентна зона E_v", size=11, bold=True, color="#15803d"))

        elif mtype == "insulator":
            f.append(rect(bx, y0 + 50, bw, 50, fill="#dbeafe", stroke="#1d4ed8", sw=1.5))
            f.append(text(bx + bw / 2, y0 + 75, "Зона провідності E_c", size=11, bold=True, color="#1e40af"))

            f.append(arrow(bx + bw + 12, y0 + 170, bx + bw + 12, y0 + 102, color="#b91c1c", sw=1.5))
            f.append(arrow(bx + bw + 12, y0 + 102, bx + bw + 12, y0 + 170, color="#b91c1c", sw=1.5))
            f.append(text(bx + bw + 18, y0 + 140, "E_g > 5 eV\n(SiO₂ / Алмаз)", size=10, bold=True, color="#b91c1c", anchor="start"))

            ef_y = y0 + 138
            f.append(path_svg(f"M {bx - 10} {ef_y} L {bx + bw + 10} {ef_y}", stroke="#dc2626", sw=2, dash="4,4"))
            f.append(text(bx + bw / 2, ef_y - 6, "E_F", size=11, bold=True, color="#dc2626"))

            f.append(rect(bx, y0 + 175, bw, 55, fill="#fee2e2", stroke="#b91c1c", sw=1.5))
            f.append(text(bx + bw / 2, y0 + 202, "Валентна зона E_v", size=11, bold=True, color="#b91c1c"))

        lines = sub.split("\n")
        for l_idx, line in enumerate(lines):
            f.append(text(x + p_w / 2, y0 + p_h - 35 + l_idx * 16, line, size=11, color=INK))

    f.append(text(W / 2, H - 12, "Величина ширини забороненої зони E_g визначає електричні та оптичні властивості речовини", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'band-gap-classification.svg'), W, H, "\n".join(f))

# ── Фігура 4: Зсув рівня Фермі при легуванні ─────────────────────────────────
def fig_fermi_level_shift_doping():
    W, H = 780, 390
    f = []

    f.append(text(W / 2, 26, "Розташування рівня Фермі у власних та легованих напівпровідниках", size=16, bold=True, color=INK))

    p_w = 225
    p_h = 280
    y0 = 55

    types = [
        ("Власний (i-тип)", "n = p = n_i\nE_F у центрі зони", "#f8fafc", "#475569", "intrinsic"),
        ("Донорманий (n-тип)", "n >> p\nE_F біля дна E_c", "#eff6ff", "#1d4ed8", "ntype"),
        ("Акцепторний (p-тип)", "p >> n\nE_F біля стелі E_v", "#f0fdf4", "#15803d", "ptype")
    ]

    for idx, (title, sub, bg, main_c, stype) in enumerate(types):
        x = 25 + idx * 245
        f.append(rect(x, y0, p_w, p_h, fill=bg, stroke=BORDER, rx=6))
        f.append(text(x + p_w / 2, y0 + 22, title, size=14, bold=True, color=main_c))

        bx = x + 35
        bw = 155

        # Conduction band
        f.append(rect(bx, y0 + 55, bw, 45, fill="#dbeafe", stroke="#1d4ed8", sw=1.5))
        f.append(text(bx + bw / 2, y0 + 82, "Зона провідності E_c", size=11, bold=True, color="#1e40af"))

        # Valence band
        f.append(rect(bx, y0 + 175, bw, 45, fill="#dcfce7", stroke="#15803d", sw=1.5))
        f.append(text(bx + bw / 2, y0 + 202, "Валентна зона E_v", size=11, bold=True, color="#15803d"))

        if stype == "intrinsic":
            ef_y = y0 + 137
            f.append(path_svg(f"M {bx - 8} {ef_y} L {bx + bw + 8} {ef_y}", stroke="#dc2626", sw=2, dash="4,4"))
            f.append(text(bx + bw / 2, ef_y - 7, "E_F ≈ E_i (середина)", size=11, bold=True, color="#dc2626"))

        elif stype == "ntype":
            ed_y = y0 + 112
            f.append(path_svg(f"M {bx} {ed_y} L {bx + bw} {ed_y}", stroke="#1d4ed8", sw=1.5, dash="2,2"))
            f.append(text(bx + bw / 2, ed_y - 5, "- - Донорні рівні E_d - -", size=10, color="#1d4ed8"))

            ef_y = y0 + 125
            f.append(path_svg(f"M {bx - 8} {ef_y} L {bx + bw + 8} {ef_y}", stroke="#dc2626", sw=2, dash="4,4"))
            f.append(text(bx + bw / 2, ef_y + 16, "E_F (зсунуто вгору)", size=11, bold=True, color="#dc2626"))

        elif stype == "ptype":
            ea_y = y0 + 162
            f.append(path_svg(f"M {bx} {ea_y} L {bx + bw} {ea_y}", stroke="#15803d", sw=1.5, dash="2,2"))
            f.append(text(bx + bw / 2, ea_y + 13, "- - Акцепторні рівні E_a - -", size=10, color="#15803d"))

            ef_y = y0 + 150
            f.append(path_svg(f"M {bx - 8} {ef_y} L {bx + bw + 8} {ef_y}", stroke="#dc2626", sw=2, dash="4,4"))
            f.append(text(bx + bw / 2, ef_y - 7, "E_F (зсунуто вниз)", size=11, bold=True, color="#dc2626"))

        lines = sub.split("\n")
        for l_idx, line in enumerate(lines):
            f.append(text(x + p_w / 2, y0 + p_h - 35 + l_idx * 16, line, size=11, color=INK))

    f.append(text(W / 2, H - 12, "Донорне легування зміщує рівень Фермі до зони провідності, а акцепторне — до валентної зони", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'fermi-level-shift-doping.svg'), W, H, "\n".join(f))

def main():
    fig_band_formation_atomic()
    fig_fermi_dirac_temperature()
    fig_band_gap_classification()
    fig_fermi_level_shift_doping()
    print("All figures successfully generated in ./img/")

if __name__ == '__main__':
    main()

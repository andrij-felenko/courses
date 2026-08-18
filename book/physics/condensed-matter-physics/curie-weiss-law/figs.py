# -*- coding: utf-8 -*-
"""Фігури до теми «Закон Кюрі — Вейсса та фазові переходи у феромагнетиках».
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


# ── Фігура 1: Обернена магнітна сприйнятливість 1/χ від T ──────────────────────
def fig_curie_vs_curie_weiss():
    W, H = 760, 440
    f = []

    f.append(text(W / 2, 26, "Обернена магнітна сприйнятливість (1/χ) від температури (T)", size=16, bold=True, color=INK))

    x0, y0 = 90, 360
    plot_w, plot_h = 620, 300

    # Axes
    f.append(line(x0, y0, x0 + plot_w, y0, color=LINE, sw=1.8))
    f.append(line(x0, y0, x0, y0 - plot_h, color=LINE, sw=1.8))

    # Axis Labels
    f.append(text(x0 + plot_w / 2, y0 + 40, "Температура T (K)", size=13, bold=True, color=INK))
    f.append(text(x0 - 55, y0 - plot_h / 2, "1 / χ", size=14, bold=True, color=INK))

    # T_C and theta ticks
    tc_x = x0 + 260
    theta_x = x0 + 100
    zero_x = x0

    f.append(line(tc_x, y0 - 5, tc_x, y0 + 5, color=LINE, sw=1.5))
    f.append(text(tc_x, y0 + 22, "T_C", size=13, bold=True, color=POS))
    f.append(text(tc_x, y0 + 36, "(Феромагнетик)", size=10, color=MUTED))

    f.append(line(theta_x, y0 - 5, theta_x, y0 + 5, color=LINE, sw=1.5))
    f.append(text(theta_x, y0 + 22, "-|θ_p|", size=13, bold=True, color=NEG))
    f.append(text(theta_x, y0 + 36, "(Антиферомагнетик)", size=10, color=MUTED))

    f.append(text(zero_x, y0 + 22, "0 K", size=12, bold=True, color=INK))

    # Vertical dashed line at T_C
    f.append(line(tc_x, y0, tc_x, y0 - plot_h + 20, color=BORDER, sw=1.2, dash="4,4"))

    # Line 1: Pure Curie Law: 1/χ = T / C (passes through 0)
    p_curie = f"M {x0} {y0} L {x0 + 520} {y0 - 260}"
    f.append(path_svg(p_curie, stroke="#6b7280", sw=2.2, dash="6,4"))

    # Line 2: Ferromagnetic Curie-Weiss Law: 1/χ = (T - T_C) / C (intersects x at T_C)
    p_fm = f"M {tc_x} {y0} L {tc_x + 360} {y0 - 270}"
    f.append(path_svg(p_fm, stroke=POS, sw=2.8))

    # Line 3: Antiferromagnetic Curie-Weiss Law: 1/χ = (T + |θ_p|) / C (intersects x at -|θ_p|)
    p_afm = f"M {theta_x} {y0} L {theta_x + 500} {y0 - 250}"
    f.append(path_svg(p_afm, stroke=NEG, sw=2.2, dash="3,3"))

    # Annotations / Legend - positioned strictly outside the shaded area and clear of lines
    tb1, _, _ = textbox(x0 + 440, y0 - 250, "Закон Кюрі — Вейсса (FM):\n1/χ = (T - T_C) / C", size=11, fill="#fef2f2", stroke=POS, color=POS, bold=True)
    f.append(tb1)

    tb2, _, _ = textbox(x0 + 480, y0 - 55, "Закон Кюрі (Ідеальний парамагнетик):\n1/χ = T / C", size=11, fill="#f3f4f6", stroke="#4b5563", color="#374151", bold=True)
    f.append(tb2)

    tb3, _, _ = textbox(x0 + 320, y0 - 195, "Антиферомагнітна область:\n1/χ = (T + |θ_p|) / C", size=11, fill="#eff6ff", stroke=NEG, color=NEG, bold=True)
    f.append(tb3)

    # Shaded region below T_C (Ordered Ferromagnetic Phase)
    f.append(rect(x0, y0 - plot_h + 30, tc_x - x0, plot_h - 30, fill="#fee2e2", stroke="none", rx=0))
    f.append(text((x0 + tc_x) / 2, y0 - plot_h / 2, "Феромагнітна\nобласть (T < T_C)\n[ M_s > 0 ]", size=11, bold=True, color=POS))

    f.append(text(W / 2, H - 10, "Перетин екстрапольованої прямої з віссю температур визначає знак і величину обмінної взаємодії", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'curie-vs-curie-weiss.svg'), W, H, "\n".join(f))


# ── Фігура 2: Графічне рішення рівняння самоузгодження m = tanh(m T_C / T) ────
def fig_weiss_self_consistency():
    W, H = 760, 440
    f = []

    f.append(text(W / 2, 26, "Графічне рішення рівняння самоузгодження Вейсса: m = tanh(m · T_C / T)", size=16, bold=True, color=INK))

    x0, y0 = 100, 360
    plot_w, plot_h = 580, 290

    # Axes
    f.append(line(x0, y0, x0 + plot_w, y0, color=LINE, sw=1.8))
    f.append(line(x0 - plot_w / 2 + 50, y0, x0 - plot_w / 2 + 50, y0 - plot_h, color=LINE, sw=1.8))

    cx = x0 - plot_w / 2 + 50  # Origin (0,0)

    # Axis Labels
    f.append(text(x0 + plot_w - 40, y0 + 25, "Намагніченість m", size=13, bold=True, color=INK))
    f.append(text(cx - 30, y0 - plot_h + 15, "y", size=13, bold=True, color=INK))

    # Straight line y = m (diagonal)
    scale_x = 220
    scale_y = 220

    f.append(line(cx - scale_x, y0 - (-1.0) * scale_y, cx + scale_x, y0 - (1.0) * scale_y, color=INK, sw=2.0, dash="5,5"))
    f.append(text(cx + scale_x - 30, y0 - scale_y - 12, "y = m", size=12, bold=True, color=INK))

    # Curve 1: T > T_C
    pts_high = []
    for i in range(-50, 51):
        m_val = i / 50.0
        y_val = math.tanh(m_val / 1.5)
        px = cx + m_val * scale_x
        py = y0 - y_val * scale_y
        pts_high.append(f"{px:.1f},{py:.1f}")
    f.append(f'<polyline points="{" ".join(pts_high)}" fill="none" stroke="{NEG}" stroke-width="2.2"/>')

    # Curve 2: T = T_C
    pts_tc = []
    for i in range(-50, 51):
        m_val = i / 50.0
        y_val = math.tanh(m_val)
        px = cx + m_val * scale_x
        py = y0 - y_val * scale_y
        pts_tc.append(f"{px:.1f},{py:.1f}")
    f.append(f'<polyline points="{" ".join(pts_tc)}" fill="none" stroke="#eab308" stroke-width="2.0" stroke-dasharray="4,4"/>')

    # Curve 3: T < T_C
    pts_low = []
    for i in range(-50, 51):
        m_val = i / 50.0
        y_val = math.tanh(m_val * 2.0)
        px = cx + m_val * scale_x
        py = y0 - y_val * scale_y
        pts_low.append(f"{px:.1f},{py:.1f}")
    f.append(f'<polyline points="{" ".join(pts_low)}" fill="none" stroke="{POS}" stroke-width="2.8"/>')

    # Roots for T < T_C
    ms_val = 0.957
    px_pos = cx + ms_val * scale_x
    py_pos = y0 - ms_val * scale_y

    px_neg = cx - ms_val * scale_x
    py_neg = y0 + ms_val * scale_y

    f.append(circle(px_pos, py_pos, 6, fill=POS, stroke=INK, sw=1.5))
    f.append(circle(px_neg, py_neg, 6, fill=POS, stroke=INK, sw=1.5))
    f.append(circle(cx, y0, 6, fill="#6b7280", stroke=INK, sw=1.5))

    # Dotted projection to x-axis
    f.append(line(px_pos, py_pos, px_pos, y0, color=POS, sw=1.2, dash="3,3"))
    f.append(text(px_pos, y0 + 20, "+m_s(T)", size=12, bold=True, color=POS))

    f.append(line(px_neg, py_neg, px_neg, y0, color=POS, sw=1.2, dash="3,3"))
    f.append(text(px_neg, y0 - 15, "-m_s(T)", size=12, bold=True, color=POS))

    # Text legends
    tb_high, _, _ = textbox(cx + 170, y0 - 60, "T > T_C (Парамагнетик):\nЄдине рішення m = 0", size=11, fill="#eff6ff", stroke=NEG, color=NEG, bold=True)
    f.append(tb_high)

    tb_low, _, _ = textbox(cx - 150, y0 - 210, "T < T_C (Феромагнетик):\nТри рішення (m=0 нестійке,\n±m_s стійкі станни)", size=11, fill="#fef2f2", stroke=POS, color=POS, bold=True)
    f.append(tb_low)

    f.append(text(W / 2, H - 10, "При T < T_C нахил гіперболічного тангенса в нулі більший за 1, що створює спонтанну намагніченість", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'weiss-self-consistency.svg'), W, H, "\n".join(f))


# ── Фігура 3: Температурна залежність спонтанної намагніченості M(T)/M(0) ──────
def fig_spontaneous_magnetization_temp():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 26, "Температурна залежність спонтанної намагніченості M_s(T) / M_0", size=16, bold=True, color=INK))

    x0, y0 = 90, 350
    plot_w, plot_h = 600, 270

    # Axes
    f.append(line(x0, y0, x0 + plot_w, y0, color=LINE, sw=1.8))
    f.append(line(x0, y0, x0, y0 - plot_h, color=LINE, sw=1.8))

    # Axis Labels
    f.append(text(x0 + plot_w / 2, y0 + 38, "Відносна температура T / T_C", size=13, bold=True, color=INK))
    f.append(text(x0 - 45, y0 - plot_h / 2, "M_s / M_0", size=13, bold=True, color=INK))

    # T_C marker
    tc_x = x0 + plot_w * 0.75
    f.append(line(tc_x, y0 - 5, tc_x, y0 + 5, color=LINE, sw=1.5))
    f.append(text(tc_x, y0 + 22, "1.0 (T = T_C)", size=12, bold=True, color=POS))

    # M_0 marker
    m0_y = y0 - plot_h * 0.85
    f.append(line(x0 - 5, m0_y, x0 + 5, m0_y, color=LINE, sw=1.5))
    f.append(text(x0 - 25, m0_y + 4, "1.0", size=12, bold=True, color=INK))

    # Curve 1: Mean Field Theory M(T)
    pts_mft = []
    N_pts = 80
    for i in range(N_pts + 1):
        t_val = (i / N_pts) * 1.0
        if t_val == 0:
            m_val = 1.0
        elif t_val >= 1.0:
            m_val = 0.0
        else:
            m_val = 0.99
            for _ in range(30):
                m_val = math.tanh(m_val / t_val)
        px = x0 + t_val * (tc_x - x0)
        py = y0 - m_val * (y0 - m0_y)
        pts_mft.append(f"{px:.1f},{py:.1f}")

    # Beyond T_C -> m = 0
    px_end = x0 + plot_w
    pts_mft.append(f"{px_end:.1f},{y0:.1f}")

    f.append(f'<polyline points="{" ".join(pts_mft)}" fill="none" stroke="{POS}" stroke-width="3.0"/>')

    # Parabolic fit near T_C showing power law (1 - T/T_C)^(1/2)
    f.append(line(tc_x, y0, tc_x, m0_y - 20, color=BORDER, sw=1.2, dash="4,4"))

    # Annotation of critical exponent
    tb_crit, _, _ = textbox(tc_x - 130, y0 - 130, "Критична область (T → T_C⁻):\nM_s ∝ (1 - T/T_C)^β\nТеорія Вейсса: β = 1/2", size=11, fill="#fef2f2", stroke=POS, color=POS, bold=True)
    f.append(tb_crit)

    tb_zero, _, _ = textbox(x0 + 130, y0 - 220, "T = 0 K:\nПовне спінове впорядкування\nM_s = M_0", size=11, fill="#f0fdf4", stroke=FIELD, color="#15803d", bold=True)
    f.append(tb_zero)

    tb_param, _, _ = textbox(tc_x + 90, y0 - 80, "Парамагнітний стан\n(T > T_C):\nM_s = 0", size=11, fill="#eff6ff", stroke=NEG, color=NEG, bold=True)
    f.append(tb_param)

    f.append(text(W / 2, H - 10, "Перехід другого роду супроводжується безперервним падінням намагніченості до нуля в точці Кюрі", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'spontaneous-magnetization-temp.svg'), W, H, "\n".join(f))


# ── Фігура 4: Спінові конфігурації у різних температурних режимах ──────────────
def fig_paramagnetic_domain_transition():
    W, H = 760, 360
    f = []

    f.append(text(W / 2, 26, "Мікроскопічний магнітний порядок при різних температурах", size=16, bold=True, color=INK))

    panel_w = 220
    panel_h = 240
    y_top = 55

    panels = [
        ("T < T_C (Феромагнетик)", "Доменна структура\nПаралельний порядок", "#fef2f2", POS, "ferro"),
        ("T ≈ T_C (Критична область)", "Критичні флуктуації\nСпінові кластери", "#fffbe0", "#d97706", "crit"),
        ("T >> T_C (Парамагнетик)", "Термодинамічний хаос\nВідсутність порядку", "#eff6ff", NEG, "para")
    ]

    rnd_angles = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # ferro
        [15, -20, 30, -10, 45, -40, 10, -15, 60, -50, 5, -30, 25, -20, 0, 35], # crit
        [120, -75, 210, 45, -135, 170, -30, 300, -210, 85, -160, 40, -110, 250, 15, -95] # para
    ]

    for idx, (title_str, sub_str, bg_color, main_color, ptype) in enumerate(panels):
        x0 = 25 + idx * 240
        f.append(rect(x0, y_top, panel_w, panel_h, fill=bg_color, stroke=BORDER, rx=6))
        f.append(text(x0 + panel_w / 2, y_top + 22, title_str, size=12, bold=True, color=main_color))

        # Grid of spins
        grid_y0 = y_top + 45
        rows, cols = 4, 4
        dx = 42
        dy = 38
        start_x = x0 + 47
        start_y = grid_y0 + 20

        spin_idx = 0
        for r in range(rows):
            for c in range(cols):
                cx = start_x + c * dx
                cy = start_y + r * dy

                # Atom node
                f.append(circle(cx, cy, 4, fill=main_color, stroke="none"))

                # Spin direction
                ang_deg = rnd_angles[idx][spin_idx]
                spin_idx += 1

                ang_rad = math.radians(ang_deg)
                length = 14
                dx_arrow = length * math.sin(ang_rad)
                dy_arrow = -length * math.cos(ang_rad)

                f.append(arrow(cx - dx_arrow*0.5, cy - dy_arrow*0.5, cx + dx_arrow, cy + dy_arrow, color=main_color, sw=2.0))

        # Subtext explanation
        sub_lines = sub_str.split("\n")
        for l_idx, line in enumerate(sub_lines):
            f.append(text(x0 + panel_w / 2, y_top + panel_h - 32 + l_idx * 16, line, size=11, bold=True, color=INK))

    f.append(text(W / 2, H - 12, "При нагріванні вище T_C далекий порядок руйнується, але на мікрорівні зберігаються флуктуаційні кластери", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'paramagnetic-domain-transition.svg'), W, H, "\n".join(f))


if __name__ == '__main__':
    fig_curie_vs_curie_weiss()
    fig_weiss_self_consistency()
    fig_spontaneous_magnetization_temp()
    fig_paramagnetic_domain_transition()
    print("Усі фігури згенеровано у ./img/")

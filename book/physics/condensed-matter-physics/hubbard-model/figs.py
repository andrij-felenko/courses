# -*- coding: utf-8 -*-
"""Фігури до теми «Модель Габбарда».
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

# ── Фігура 1: Процеси стрибка t та відштовхування U ───────────────────────────
def fig_hubbard_hopping_repulsion():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 28, "Фундаментальні квантові процеси в 1D ґратці Габбарда", size=16, bold=True, color=INK))

    # Panel A: Single occupancy & Hopping t
    box_a_w = 360
    box_h = 320
    x_a = 20
    y0 = 55

    f.append(rect(x_a, y0, box_a_w, box_h, fill="#eff6ff", stroke=BORDER, rx=6))
    f.append(text(x_a + box_a_w / 2, y0 + 25, "1. Кінетичний стрибок електрона (t)", size=14, bold=True, color=NEG))

    # Sites in Panel A
    sites_a_x = [x_a + 60, x_a + 180, x_a + 300]
    site_y = y0 + 170

    for idx, sx in enumerate(sites_a_x):
        # Potential well (wavy/u-shape line)
        f.append(rect(sx - 35, site_y + 20, 70, 8, fill="#94a3b8", stroke="none", rx=3))
        f.append(circle(sx, site_y + 20, 4, fill="#475569", stroke="none"))
        f.append(text(sx, site_y + 45, f"Вузол {idx+1}", size=11, color=MUTED))

    # Electron at site 1 (Spin up)
    f.append(arrow(sites_a_x[0], site_y + 15, sites_a_x[0], site_y - 25, color=POS, sw=2.5))
    f.append(text(sites_a_x[0] - 18, site_y - 5, "↑", size=14, bold=True, color=POS))

    # Hopping arc from site 1 to site 2
    arc_d = f"M {sites_a_x[0]} {site_y - 30} Q {(sites_a_x[0] + sites_a_x[1])/2} {site_y - 85} {sites_a_x[1]} {site_y - 30}"
    f.append(path_svg(arc_d, fill="none", stroke=NEG, sw=2.2, dash="4,3"))
    f.append(arrow(sites_a_x[1] - 15, site_y - 45, sites_a_x[1], site_y - 30, color=NEG, sw=2.2))
    
    # Label t
    t_box, tw, th = textbox(x_a + 120, y0 + 95, "Стрибковий інтеграл t\n(кінетична енергія)", size=11, pad=6, fill="#ffffff", stroke=NEG, color=NEG, bold=True)
    f.append(t_box)

    f.append(text(x_a + box_a_w / 2, y0 + box_h - 25, "Перенесення заряду знижує енергію на ~t", size=11, italic=True, color=INK))

    # Panel B: Double occupancy & Coulomb Repulsion U
    box_b_w = 360
    x_b = 400

    f.append(rect(x_b, y0, box_b_w, box_h, fill="#fff7ed", stroke=BORDER, rx=6))
    f.append(text(x_b + box_b_w / 2, y0 + 25, "2. Вузлове кулонівське відштовхування (U)", size=14, bold=True, color="#c2410c"))

    # Sites in Panel B
    sites_b_x = [x_b + 60, x_b + 180, x_b + 300]

    for idx, sx in enumerate(sites_b_x):
        f.append(rect(sx - 35, site_y + 20, 70, 8, fill="#94a3b8", stroke="none", rx=3))
        f.append(circle(sx, site_y + 20, 4, fill="#475569", stroke="none"))
        f.append(text(sx, site_y + 45, f"Вузол {idx+1}", size=11, color=MUTED))

    # Site 1: Spin up
    f.append(arrow(sites_b_x[0], site_y + 15, sites_b_x[0], site_y - 25, color=POS, sw=2.5))
    
    # Site 2: Doubly occupied (Spin up & Spin down)
    f.append(arrow(sites_b_x[1] - 8, site_y + 15, sites_b_x[1] - 8, site_y - 25, color=POS, sw=2.5))
    f.append(arrow(sites_b_x[1] + 8, site_y - 25, sites_b_x[1] + 8, site_y + 15, color=NEG, sw=2.5))
    
    # Energy penalty U halo around site 2
    f.append(circle(sites_b_x[1], site_y - 5, 28, fill="none", stroke="#ea580c", sw=2.0))
    
    # Label U
    u_box, uw, uh = textbox(x_b + 180, y0 + 80, "Енергетичний штраф U\n(двократна заповненість)", size=11, pad=6, fill="#ffffff", stroke="#c2410c", color="#c2410c", bold=True)
    f.append(u_box)

    f.append(text(x_b + box_b_w / 2, y0 + box_h - 25, "Кулонівське відштовхування коштує +U", size=11, italic=True, color=INK))

    f.append(text(W / 2, H - 12, "Конкуренція між t (делокалізація) та U (локалізація) визначає фазовий стан системи", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'hubbard-hopping-repulsion.svg'), W, H, "\n".join(f))


# ── Фігура 2: Зонна структура Моттівського ізолятора ──────────────────────────
def fig_mott_insulator_bands():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 28, "Формування Моттівської щілини у спектральній густині станів", size=16, bold=True, color=INK))

    panel_w = 350
    panel_h = 320
    y0 = 55

    # Left Panel: Band theory (Metal)
    x_left = 25
    f.append(rect(x_left, y0, panel_w, panel_h, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(x_left + panel_w / 2, y0 + 25, "Зонна теорія (U = 0, металевий стан)", size=13, bold=True, color=NEG))

    # Axis Left
    ax_x = x_left + 50
    ax_y_bot = y0 + 280
    ax_y_top = y0 + 60
    f.append(arrow(ax_x, ax_y_bot, ax_x, ax_y_top, color=INK, sw=1.5))
    f.append(text(ax_x - 15, ax_y_top + 10, "E", size=12, bold=True, color=INK))

    # Continuous Band (Parabola density of states)
    band_cy = y0 + 170
    band_h = 140
    # Filled part (bottom half)
    d_fill = f"M {ax_x} {band_cy + band_h/2} Q {ax_x + 130} {band_cy} {ax_x} {band_cy} Z"
    f.append(path_svg(d_fill, fill="#93c5fd", stroke=NEG, sw=1.5))
    # Unfilled part (top half)
    d_empty = f"M {ax_x} {band_cy} Q {ax_x + 130} {band_cy} {ax_x} {band_cy - band_h/2} Z"
    f.append(path_svg(d_empty, fill="#e2e8f0", stroke=MUTED, sw=1.5, dash="3,3"))

    # Fermi Level E_F
    f.append(line(ax_x - 10, band_cy, ax_x + 160, band_cy, color=POS, sw=2.0, dash="5,3"))
    f.append(text(ax_x + 185, band_cy + 4, "E_F (Рівень Фермі)", size=11, bold=True, color=POS))
    f.append(text(ax_x + 100, band_cy + 45, "Ширина зони W = 2z·t", size=11, color=NEG))

    lbl_box_l, _, _ = textbox(x_left + panel_w / 2, y0 + panel_h - 25, "Напівзаповнена зона → Метал\n(безперервний спектр)", size=11, pad=5, fill="#ffffff", stroke=NEG, color=NEG)
    f.append(lbl_box_l)

    # Right Panel: Mott Insulator (U >> W)
    x_right = 405
    f.append(rect(x_right, y0, panel_w, panel_h, fill="#fff7ed", stroke=BORDER, rx=6))
    f.append(text(x_right + panel_w / 2, y0 + 25, "Модель Габбарда (U > W, Моттівський ізолятор)", size=13, bold=True, color="#c2410c"))

    # Axis Right
    ax_rx = x_right + 50
    f.append(arrow(ax_rx, ax_y_bot, ax_rx, ax_y_top, color=INK, sw=1.5))
    f.append(text(ax_rx - 15, ax_y_top + 10, "E", size=12, bold=True, color=INK))

    # Lower Hubbard Band (LHB) - Filled
    lhb_cy = y0 + 225
    lhb_h = 60
    d_lhb = f"M {ax_rx} {lhb_cy + lhb_h/2} Q {ax_rx + 120} {lhb_cy} {ax_rx} {lhb_cy - lhb_h/2} Z"
    f.append(path_svg(d_lhb, fill="#fca5a5", stroke=POS, sw=1.5))
    f.append(text(ax_rx + 75, lhb_cy + 4, "LHB (Нижня зона)", size=11, bold=True, color=POS))

    # Upper Hubbard Band (UHB) - Empty
    uhb_cy = y0 + 105
    uhb_h = 60
    d_uhb = f"M {ax_rx} {uhb_cy + uhb_h/2} Q {ax_rx + 120} {uhb_cy} {ax_rx} {uhb_cy - uhb_h/2} Z"
    f.append(path_svg(d_uhb, fill="#e2e8f0", stroke=MUTED, sw=1.5))
    f.append(text(ax_rx + 75, uhb_cy + 4, "UHB (Верхня зона)", size=11, bold=True, color=MUTED))

    # Mott Gap E_g
    gap_y1 = lhb_cy - lhb_h/2
    gap_y2 = uhb_cy + uhb_h/2
    gap_mid = (gap_y1 + gap_y2) / 2
    f.append(arrow(ax_rx + 170, gap_mid + 15, ax_rx + 170, gap_y2, color="#c2410c", sw=1.5))
    f.append(arrow(ax_rx + 170, gap_mid - 15, ax_rx + 170, gap_y1, color="#c2410c", sw=1.5))
    
    gap_box, _, _ = textbox(ax_rx + 220, gap_mid, "Щілина Мотта\nE_g ≈ U - W", size=11, pad=5, fill="#ffffff", stroke="#c2410c", color="#c2410c", bold=True)
    f.append(gap_box)

    lbl_box_r, _, _ = textbox(x_right + panel_w / 2, y0 + panel_h - 25, "Розщеплення на дві зони → Ізолятор\n(заборонена зона E_g > 0)", size=11, pad=5, fill="#ffffff", stroke="#c2410c", color="#c2410c")
    f.append(lbl_box_r)

    f.append(text(W / 2, H - 12, "Сильна електронна кореляція U розщеплює зонний спектр та утворює диелектричний стан Мотта", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'mott-insulator-bands.svg'), W, H, "\n".join(f))


# ── Фігура 3: Механізм кінетичного суперобміну ──────────────────────────────
def fig_super_exchange_mechanism():
    W, H = 780, 430
    f = []

    f.append(text(W / 2, 28, "Квантовомеханічний механізм кінетичного суперобміну (J = 4t²/U)", size=16, bold=True, color=INK))

    panel_w = 355
    panel_h = 330
    y0 = 55

    # Left: Antiparallel spins (Allowed virtual process)
    x1 = 20
    f.append(rect(x1, y0, panel_w, panel_h, fill="#f0fdf4", stroke=BORDER, rx=6))
    f.append(text(x1 + panel_w / 2, y0 + 25, "Антипаралельні спіни (↑ ↓): Дозволено!", size=13, bold=True, color="#15803d"))

    # Initial state
    f.append(text(x1 + 30, y0 + 65, "Початковий стан (E = 0):", size=11, bold=True, color=INK))
    # Site A
    f.append(circle(x1 + 100, y0 + 105, 18, fill="#dcfce7", stroke="#15803d", sw=1.5))
    f.append(arrow(x1 + 100, y0 + 115, x1 + 100, y0 + 92, color=POS, sw=2.2))
    f.append(text(x1 + 100, y0 + 135, "Вузол i (↑)", size=11, color=INK))
    # Site B
    f.append(circle(x1 + 240, y0 + 105, 18, fill="#dcfce7", stroke="#15803d", sw=1.5))
    f.append(arrow(x1 + 240, y0 + 95, x1 + 240, y0 + 118, color=NEG, sw=2.2))
    f.append(text(x1 + 240, y0 + 135, "Вузол j (↓)", size=11, color=INK))

    # Virtual Hopping Arrow
    arc1 = f"M {x1 + 100} {y0 + 87} Q {x1 + 170} {y0 + 55} {x1 + 240} {y0 + 87}"
    f.append(path_svg(arc1, stroke="#15803d", sw=2.0, dash="4,3"))
    f.append(text(x1 + 170, y0 + 65, "Віртуальний стрибок t", size=10, bold=True, color="#15803d"))

    # Intermediate state (Double occupancy)
    f.append(text(x1 + 30, y0 + 175, "Віртуальний стан (E = +U):", size=11, bold=True, color=INK))
    # Site A empty
    f.append(circle(x1 + 100, y0 + 215, 18, fill="#ffffff", stroke=MUTED, sw=1.5))
    f.append(text(x1 + 100, y0 + 245, "Вузол i (порожній)", size=11, color=MUTED))
    # Site B double occupancy
    f.append(circle(x1 + 240, y0 + 215, 22, fill="#fef3c7", stroke="#d97706", sw=2.0))
    f.append(arrow(x1 + 233, y0 + 225, x1 + 233, y0 + 202, color=POS, sw=2.2))
    f.append(arrow(x1 + 247, y0 + 205, x1 + 247, y0 + 228, color=NEG, sw=2.2))
    f.append(text(x1 + 240, y0 + 250, "Вузол j (подвійний)", size=11, color="#d97706"))

    # Energy reduction box
    j_box, _, _ = textbox(x1 + panel_w / 2, y0 + panel_h - 30, "Зниження енергії 2-го порядку:\nΔE = -4t² / U (Антиферомагнетизм)", size=11, pad=6, fill="#ffffff", stroke="#15803d", color="#15803d", bold=True)
    f.append(j_box)


    # Right: Parallel spins (Forbidden by Pauli principle)
    x2 = 405
    f.append(rect(x2, y0, panel_w, panel_h, fill="#fef2f2", stroke=BORDER, rx=6))
    f.append(text(x2 + panel_w / 2, y0 + 25, "Паралельні спіни (↑ ↑): Заборонено!", size=13, bold=True, color="#b91c1c"))

    # Initial state
    f.append(text(x2 + 30, y0 + 65, "Початковий стан (E = 0):", size=11, bold=True, color=INK))
    # Site A
    f.append(circle(x2 + 100, y0 + 105, 18, fill="#fee2e2", stroke="#b91c1c", sw=1.5))
    f.append(arrow(x2 + 100, y0 + 115, x2 + 100, y0 + 92, color=POS, sw=2.2))
    f.append(text(x2 + 100, y0 + 135, "Вузол i (↑)", size=11, color=INK))
    # Site B
    f.append(circle(x2 + 240, y0 + 105, 18, fill="#fee2e2", stroke="#b91c1c", sw=1.5))
    f.append(arrow(x2 + 240, y0 + 115, x2 + 240, y0 + 92, color=POS, sw=2.2))
    f.append(text(x2 + 240, y0 + 135, "Вузол j (↑)", size=11, color=INK))

    # Forbidden Hopping Arrow (Red Cross)
    arc2 = f"M {x2 + 100} {y0 + 87} Q {x2 + 170} {y0 + 55} {x2 + 240} {y0 + 87}"
    f.append(path_svg(arc2, stroke="#b91c1c", sw=2.0, dash="4,3"))
    # Cross mark
    f.append(line(x2 + 163, y0 + 60, x2 + 177, y0 + 74, color="#b91c1c", sw=3.0))
    f.append(line(x2 + 177, y0 + 60, x2 + 163, y0 + 74, color="#b91c1c", sw=3.0))
    f.append(text(x2 + 170, y0 + 50, "Стрибок блоковано Паулі", size=10, bold=True, color="#b91c1c"))

    # Intermediate state blocked
    f.append(text(x2 + 30, y0 + 175, "Принцип Паулі забороняє стан:", size=11, bold=True, color=INK))
    # Blocked state circle
    f.append(circle(x2 + 170, y0 + 215, 26, fill="#fee2e2", stroke="#b91c1c", sw=1.5))
    f.append(text(x2 + 170, y0 + 215, "|↑ ↑⟩ 🛑", size=14, bold=True, color="#b91c1c"))
    f.append(text(x2 + 170, y0 + 250, "Двократна заповненість з однаковим спіном", size=10, color=MUTED))

    # Energy unchanged box
    no_j_box, _, _ = textbox(x2 + panel_w / 2, y0 + panel_h - 30, "Немає виграшу енергії:\nΔE = 0 (Спіновий фрустрат)", size=11, pad=6, fill="#ffffff", stroke="#b91c1c", color="#b91c1c", bold=True)
    f.append(no_j_box)

    f.append(text(W / 2, H - 12, "Принцип Паулі вибірково знижує енергію лише для антипаралельних спінів, створюючи exchange J", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'super-exchange-mechanism.svg'), W, H, "\n".join(f))


# ── Фігура 4: Фазова діаграма 2D моделі Габбарда ─────────────────────────────
def fig_hubbard_phase_diagram():
    W, H = 780, 440
    f = []

    f.append(text(W / 2, 28, "Фазова діаграма двовимірної моделі Габбарда (легування — температура)", size=16, bold=True, color=INK))

    ax_x0 = 90
    ax_y0 = 360
    ax_w = 620
    ax_h = 280

    # Main box
    f.append(rect(ax_x0, ax_y0 - ax_h, ax_w, ax_h, fill="#fafafa", stroke=BORDER, rx=4))

    # Axes
    f.append(arrow(ax_x0, ax_y0, ax_x0 + ax_w + 20, ax_y0, color=INK, sw=1.8))
    f.append(text(ax_x0 + ax_w / 2, ax_y0 + 38, "Концентрація дірок / Легування δ  (n = 1 - δ)", size=13, bold=True, color=INK))
    f.append(text(ax_x0 + 10, ax_y0 + 20, "n = 1 (Half-filling)", size=10, color=MUTED, anchor="start"))
    f.append(text(ax_x0 + ax_w, ax_y0 + 20, "δ ~ 0.35 (Overdoped)", size=10, color=MUTED, anchor="end"))

    f.append(arrow(ax_x0, ax_y0, ax_x0, ax_y0 - ax_h - 15, color=INK, sw=1.8))
    f.append(text(ax_x0 - 45, ax_y0 - ax_h / 2, "Температура T", size=13, bold=True, color=INK))

    # Regions
    # 1. Antiferromagnetic Mott Insulator (δ = 0 to 0.05, high T_N)
    afm_d = f"M {ax_x0} {ax_y0} Q {ax_x0 + 45} {ax_y0 - 200} {ax_x0 + 80} {ax_y0} Z"
    f.append(path_svg(afm_d, fill="#fca5a5", stroke=POS, sw=1.5))
    f.append(text(ax_x0 + 38, ax_y0 - 90, "AFM\nМоттівський\nізолятор", size=10, bold=True, color=POS))

    # 2. Superconducting Dome (δ = 0.05 to 0.27, peak at δ = 0.16)
    sc_d = f"M {ax_x0 + 70} {ax_y0} Q {ax_x0 + 200} {ax_y0 - 150} {ax_x0 + 350} {ax_y0} Z"
    f.append(path_svg(sc_d, fill="#86efac", stroke="#15803d", sw=2.0))
    f.append(text(ax_x0 + 200, ax_y0 - 45, "d-хвильова Надпровідність\n(High-Tc Dome)", size=11, bold=True, color="#15803d"))
    f.append(circle(ax_x0 + 200, ax_y0 - 75, 4, fill="#15803d", stroke="none"))
    f.append(text(ax_x0 + 200, ax_y0 - 88, "T_c,max (Оптимальне легування δ ≈ 0.16)", size=10, bold=True, color="#15803d"))

    # 3. Pseudogap phase (above SC dome at low doping)
    pg_d = f"M {ax_x0 + 50} {ax_y0 - 110} Q {ax_x0 + 170} {ax_y0 - 230} {ax_x0 + 270} {ax_y0 - 120} L {ax_x0 + 350} {ax_y0} L {ax_x0 + 70} {ax_y0} Z"
    f.append(path_svg(pg_d, fill="#e0e7ff", stroke="#4338ca", sw=1.2, dash="3,3"))
    f.append(text(ax_x0 + 150, ax_y0 - 150, "Псевдощілинний стан\n(Pseudogap)", size=11, bold=True, color="#4338ca"))

    # 4. Strange Metal / Non-Fermi Liquid (Above T_c/PG, linear resistivity)
    f.append(text(ax_x0 + 260, ax_y0 - 230, "Дивний метал (Strange Metal)\nρ ∝ T (Не-фермі-рідина)", size=11, bold=True, color="#9a3412"))

    # 5. Fermi Liquid (Overdoped, high δ)
    f.append(text(ax_x0 + 490, ax_y0 - 100, "Звичайний метал\n(Фермі-рідина Ландау)\nρ ∝ T²", size=11, color=NEG))

    f.append(text(W / 2, H - 10, "Багата фазова діаграма при легуванні моттівського ізолятора описується 2D моделлю Габбарда", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG_DIR, 'hubbard-phase-diagram.svg'), W, H, "\n".join(f))


if __name__ == '__main__':
    fig_hubbard_hopping_repulsion()
    fig_mott_insulator_bands()
    fig_super_exchange_mechanism()
    fig_hubbard_phase_diagram()
    print("Всі фігури успішно згенеровані у ./img/")

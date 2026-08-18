# -*- coding: utf-8 -*-
"""Фігури для теми «Тиск виродженого фермі-газу» (book/physics/quantum-mechanics/degeneracy-pressure)."""
import sys, os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"


def path_svg(d, fill="none", stroke="#333333", sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}/>'


def ellipse_svg(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}/>'


def fig_fermi_sphere():
    """fig1-fermi-sphere.svg: Квантовий фазовий простір, фермі-сфера та розподіл Фермі — Дірака при T=0 і T>0."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Квантовий фазовий простір та фермі-сфера (T = 0 K)", size=16, bold=True, color="#1e293b"))

    # Ліва частина: 3D Сфера Фермі у k-просторі
    cx, cy, R = 220, 220, 105

    # Заповнений об'єм сфери
    frags.append(circle(cx, cy, R, fill=BLUE_F, stroke=BLUE_S, sw=2.0))
    frags.append(ellipse_svg(cx, cy, R, 35, fill="none", stroke=BLUE_S, sw=1.2, dash="4,4"))

    # Дрібна сітка квантових станів всередині
    for rx_i in range(25, R, 25):
        frags.append(ellipse_svg(cx, cy, rx_i, rx_i * 0.32, fill="none", stroke="#93c5fd", sw=0.8, dash="2,2"))

    # Осі k-простору
    frags.append(line(cx, cy + R + 20, cx, cy - R - 25, color="#1e293b", sw=1.8))  # kz
    frags.append(text(cx + 15, cy - R - 20, "k_z", size=13, bold=True, color="#1e293b"))

    frags.append(line(cx - R - 25, cy, cx + R + 35, cy, color="#1e293b", sw=1.8))  # ky
    frags.append(text(cx + R + 40, cy + 4, "k_y", size=13, bold=True, color="#1e293b"))

    frags.append(line(cx - 70, cy + 70, cx + 75, cy - 75, color="#1e293b", sw=1.8))  # kx
    frags.append(text(cx - 85, cy + 90, "k_x", size=13, bold=True, color="#1e293b"))

    # Вектор k_F
    vx, vy = cx + 74, cy - 74
    frags.append(line(cx, cy, vx, vy, color=RED_S, sw=2.5))
    frags.append(circle(vx, vy, 4, fill=RED_S, stroke=RED_S))

    b_kf, _, _ = textbox(cx + 95, cy - 85, "Радіус Фермі:\nk_F = (3π²n)¹/³", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_kf)

    # Квантова комірка V_k = (2pi/L)^3
    b_cell, _, _ = textbox(cx - 130, cy + 125, "Елементарна комірка станів:\nΔV_k = (2π / L)³", size=10, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_cell)

    # Права частина: Функція розподілу f(E)
    frags.append(rect(470, 60, 380, 330, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(660, 85, "Функція розподілу Фермі — Дірака f(E)", size=13, bold=True, color="#1e293b"))

    # Осі графіка
    ox, oy = 520, 320
    frags.append(line(ox, oy, ox + 300, oy, color="#475569", sw=1.5))  # Енергія E
    frags.append(line(ox, oy, ox, oy - 220, color="#475569", sw=1.5))  # f(E)
    frags.append(text(ox + 305, oy + 4, "E", size=12, bold=True, color="#475569"))
    frags.append(text(ox - 25, oy - 215, "f(E)", size=12, bold=True, color="#475569"))

    # Позначка 1.0 на осі f(E)
    frags.append(line(ox - 5, oy - 180, ox, oy - 180, color="#475569", sw=1.5))
    frags.append(text(ox - 25, oy - 176, "1.0", size=10, color="#475569"))

    # Лінія E_F
    ef_x = ox + 180
    frags.append(line(ef_x, oy, ef_x, oy - 220, color=RED_S, sw=1.5, dash="4,4"))
    frags.append(text(ef_x - 10, oy + 20, "E_F", size=12, bold=True, color=RED_S))

    # Сходинка для T = 0 K
    path_t0 = f"M {ox} {oy - 180} L {ef_x} {oy - 180} L {ef_x} {oy} L {ox + 290} {oy}"
    frags.append(path_svg(path_t0, fill="none", stroke=BLUE_S, sw=3.0))

    # Розмитий хвіст для T > 0 K
    pts_t = []
    for x in range(0, 290, 5):
        e_val = (x - 180) / 30.0  # (E - E_F)/kT
        f_val = 1.0 / (1.0 + math.exp(max(-10, min(10, e_val))))
        px = ox + x
        py = oy - 180 * f_val
        pts_t.append((px, py))

    path_t1 = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_t)
    frags.append(path_svg(path_t1, fill="none", stroke=PURPLE_S, sw=2.0, dash="5,3"))

    b_t0, _, _ = textbox(ef_x + 20, oy - 150, "T = 0 K\n(Абсолютно вироджений)", size=10, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_t0)

    b_t1, _, _ = textbox(ef_x + 20, oy - 80, "T > 0 K\n(Теплова розмитість ~k_B T)", size=10, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_t1)

    render(os.path.join(IMG, "fig1-fermi-sphere.svg"), W, H, *frags)


def fig_degeneracy_pressure_eos():
    """fig2-degeneracy-pressure-eos.svg: Рівняння стану P(rho) — перехід від P ~ rho^(5/3) до P ~ rho^(4/3)."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Рівняння стану виродженого електронного газу P(ρ)", size=16, bold=True, color="#1e293b"))

    # Графік у логарифмічних координатах log P vs log rho
    ox, oy = 90, 340
    gw, gh = 720, 260

    # Сітка та рамка графіка
    frags.append(rect(ox, oy - gh, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.5))

    # Осі
    frags.append(text(ox + gw / 2, oy + 35, "Густина речовини ρ (г/см³)", size=12, bold=True, color="#1e293b"))
    frags.append(mtext(40, oy - gh / 2, "Тиск виродження\nlog P", size=12, bold=True, color="#1e293b"))

    # Критична густина релятивістського переходу rho_rel ≈ 10^6 g/cm^3
    rel_x = ox + 360
    frags.append(line(rel_x, oy, rel_x, oy - gh, color=PURPLE_S, sw=1.5, dash="4,4"))
    b_rel, _, _ = textbox(rel_x - 120, oy - gh + 25, "Релятивістський перехід:\nρ_rel ≈ 10⁶ г/см³ (p_F ≈ m_e c)", size=10, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b_rel)

    # Крива P(rho)
    pts = []
    for x in range(0, gw + 1, 10):
        if x < 360:
            y_val = (5.0 / 3.0) * (x / 360.0) * 120.0
        else:
            dx = (x - 360.0) / (gw - 360.0)
            y_val = 120.0 + (4.0 / 3.0) * dx * 100.0
        py = oy - 20 - y_val
        pts.append((ox + x, py))

    path_eos = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    frags.append(path_svg(path_eos, fill="none", stroke=BLUE_S, sw=3.5))

    # Анотації режимів
    b_nr, _, _ = textbox(ox + 90, oy - 80, "Нерелятивістський режим:\nP ∝ ρ⁵/³\n(Жорстке рівняння стану)", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_nr)

    b_ur, _, _ = textbox(ox + 480, oy - 200, "Ультрарелятивістський режим:\nP ∝ ρ⁴/³\n(М'яке рівняння стану → нестабільність)", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_ur)

    # Позначки густини на осі X
    frags.append(text(ox + 40, oy + 15, "10²", size=10, color="#64748b"))
    frags.append(text(ox + 200, oy + 15, "10⁴", size=10, color="#64748b"))
    frags.append(text(rel_x, oy + 15, "10⁶", size=10, bold=True, color=PURPLE_S))
    frags.append(text(ox + 520, oy + 15, "10⁸", size=10, color="#64748b"))
    frags.append(text(ox + 680, oy + 15, "10¹⁰", size=10, color="#64748b"))

    render(os.path.join(IMG, "fig2-degeneracy-pressure-eos.svg"), W, H, *frags)


def fig_white_dwarf_balance():
    """fig3-white-dwarf-balance.svg: Гравітація vs тиск виродження та масово-радіусна залежність R(M)."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Гравітаційна рівновага та межа Чандрасекара білих карликів", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Схема зоряної рівноваги
    cx, cy, R_star = 180, 220, 80

    # Зоряна сфера
    frags.append(circle(cx, cy, R_star, fill=TEAL_F, stroke=TEAL_S, sw=2.0))

    # Стрілки гравітаційного стиснення (до центра)
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(angle)
        x1 = cx + (R_star + 18) * math.cos(rad)
        y1 = cy + (R_star + 18) * math.sin(rad)
        x2 = cx + (R_star + 2) * math.cos(rad)
        y2 = cy + (R_star + 2) * math.sin(rad)
        frags.append(line(x1, y1, x2, y2, color=RED_S, sw=1.8))

    # Стрілки тиску виродження (з середини назовні)
    for angle in [22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5]:
        rad = math.radians(angle)
        x1 = cx + 20 * math.cos(rad)
        y1 = cy + 20 * math.sin(rad)
        x2 = cx + (R_star - 8) * math.cos(rad)
        y2 = cy + (R_star - 8) * math.sin(rad)
        frags.append(line(x1, y1, x2, y2, color=BLUE_S, sw=1.8))

    b_bal, _, _ = textbox(cx, cy, "Рівновага:\nF_grav = F_deg", size=10, bold=True, fill="#ffffff", stroke=TEAL_S)
    frags.append(b_bal)

    frags.append(text(cx, cy + R_star + 35, "Білий карлик / Нейтронна зоря", size=11, bold=True, color="#1e293b"))

    # Права частина: Масово-радіусна залежність R(M)
    panel_x = 450
    frags.append(rect(panel_x, 60, 400, 330, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(panel_x + 200, 85, "Залежність радіуса від маси R(M)", size=13, bold=True, color="#1e293b"))

    ox, oy = panel_x + 60, 340
    gw, gh = 310, 220

    frags.append(line(ox, oy, ox + gw, oy, color="#475569", sw=1.5))  # Маса M
    frags.append(line(ox, oy, ox, oy - gh, color="#475569", sw=1.5))  # Радіус R
    frags.append(text(ox + gw - 25, oy + 20, "Маса M (M_☉)", size=11, bold=True, color="#475569"))
    frags.append(text(ox - 25, oy - gh - 10, "Радіус R", size=11, bold=True, color="#475569"))

    # Межа Чандрасекара M_Ch ≈ 1.44 M_sun
    m_ch_x = ox + 230
    frags.append(line(m_ch_x, oy, m_ch_x, oy - gh, color=RED_S, sw=1.8, dash="4,4"))
    frags.append(text(m_ch_x - 30, oy + 20, "1.44 M_☉", size=11, bold=True, color=RED_S))

    # Крива R(M)
    pts_rm = []
    for x in range(0, 230, 4):
        m_rel = x / 230.0
        r_val = math.sqrt(max(0.0, 1.0 - m_rel ** (2.0 / 3.0)))
        py = oy - r_val * 170.0
        pts_rm.append((ox + x, py))

    path_rm = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_rm)
    frags.append(path_svg(path_rm, fill="none", stroke=BLUE_S, sw=3.0))

    b_ch, _, _ = textbox(m_ch_x - 90, oy - 160, "Межа Чандрасекара:\nM_Ch ≈ 1.44 M_☉\n(R → 0, колапс)", size=10, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_ch)

    b_inv, _, _ = textbox(ox + 120, oy - 45, "Нерелятивістська залежність:\nR ∝ M⁻¹/³ (важча зоря менша)", size=10, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_inv)

    render(os.path.join(IMG, "fig3-white-dwarf-balance.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_fermi_sphere()
    fig_degeneracy_pressure_eos()
    fig_white_dwarf_balance()
    print("Всі фігури успішно згенеровано у", IMG)

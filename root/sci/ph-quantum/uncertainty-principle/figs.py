# -*- coding: utf-8 -*-
"""Фігури для теми «Принцип невизначеності Гайзенберга» (book/physics/quantum-mechanics/uncertainty-principle)."""
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


def fig_wavepacket_fourier():
    """fig1-wavepacket-fourier.svg: Дуальність локалізації у координатному і імпульсному просторах через перетворення Фур'є."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Співвідношення між локалізацією в координатному просторі x та імпульсному p", size=16, bold=True, color="#1e293b"))

    # Ліва панель: Координатний простір (вузький пакет)
    frags.append(rect(30, 55, 390, 310, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(225, 78, "Координатний простір |ψ(x)|²", size=13, bold=True, color="#1e293b"))

    # Осі координатного простору
    frags.append(line(50, 310, 400, 310, color="#64748b", sw=1.5))
    frags.append(line(225, 100, 225, 325, color="#cbd5e1", sw=1.2, dash="3,3"))
    frags.append(text(405, 314, "x", size=12, bold=True, color="#64748b"))
    frags.append(text(230, 110, "|ψ(x)|²", size=11, color="#64748b"))

    # Вузький Гаусів пакет у х
    pts_x = []
    sigma_x = 25.0
    for px in range(60, 390, 2):
        dx = px - 225
        val = math.exp(-(dx * dx) / (2 * sigma_x * sigma_x))
        py = 310 - 170 * val
        pts_x.append((px, py))

    path_x = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_x)
    pts_x_fill = [(60, 310)] + pts_x + [(388, 310)]
    path_x_fill = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_x_fill) + " Z"
    frags.append(path_svg(path_x_fill, fill=BLUE_F, stroke="none"))
    frags.append(path_svg(path_x, fill="none", stroke=BLUE_S, sw=2.5))

    # Двостороння стрілка Δx
    y_dx = 220
    frags.append(line(225 - sigma_x, y_dx, 225 + sigma_x, y_dx, color=RED_S, sw=2.0))
    frags.append(line(225 - sigma_x, y_dx - 6, 225 - sigma_x, y_dx + 6, color=RED_S, sw=1.5))
    frags.append(line(225 + sigma_x, y_dx - 6, 225 + sigma_x, y_dx + 6, color=RED_S, sw=1.5))

    b_dx, _, _ = textbox(225, 185, "Вузька ширина: σ_x мале", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_dx)

    # Центральне перетворення Фур'є (стрілка)
    frags.append(path_svg("M 425 200 L 455 200", fill="none", stroke=PURPLE_S, sw=2.5))
    frags.append(path_svg("M 448 194 L 456 200 L 448 206", fill="none", stroke=PURPLE_S, sw=2.5))
    frags.append(text(440, 185, "Фур'є", size=11, bold=True, color=PURPLE_S))

    # Права панель: Імпульсний простір (широкий пакет)
    frags.append(rect(460, 55, 390, 310, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(655, 78, "Імпульсний простір |ϕ(p)|²", size=13, bold=True, color="#1e293b"))

    # Осі імпульсного простору
    frags.append(line(480, 310, 830, 310, color="#64748b", sw=1.5))
    frags.append(line(655, 100, 655, 325, color="#cbd5e1", sw=1.2, dash="3,3"))
    frags.append(text(835, 314, "p", size=12, bold=True, color="#64748b"))
    frags.append(text(660, 110, "|ϕ(p)|²", size=11, color="#64748b"))

    # Широкий Гаусів пакет у p (sigma_p велике)
    pts_p = []
    sigma_p = 80.0
    for px in range(490, 820, 2):
        dp = px - 655
        val = math.exp(-(dp * dp) / (2 * sigma_p * sigma_p))
        py = 310 - 130 * val
        pts_p.append((px, py))

    path_p = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_p)
    pts_p_fill = [(490, 310)] + pts_p + [(818, 310)]
    path_p_fill = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_p_fill) + " Z"
    frags.append(path_svg(path_p_fill, fill=TEAL_F, stroke="none"))
    frags.append(path_svg(path_p, fill="none", stroke=TEAL_S, sw=2.5))

    # Двостороння стрілка Δp
    y_dp = 240
    frags.append(line(655 - sigma_p, y_dp, 655 + sigma_p, y_dp, color=TEAL_S, sw=2.0))
    frags.append(line(655 - sigma_p, y_dp - 6, 655 - sigma_p, y_dp + 6, color=TEAL_S, sw=1.5))
    frags.append(line(655 + sigma_p, y_dp - 6, 655 + sigma_p, y_dp + 6, color=TEAL_S, sw=1.5))

    b_dp, _, _ = textbox(655, 205, "Широкий розмах: σ_p велике", size=11, bold=True, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b_dp)

    # Фундаментальний підпис знизу
    b_fund, _, _ = textbox(440, 395, "Нерівність Гайзенберга: σ_x · σ_p ≥ ℏ / 2  (для гаусового пакета σ_x · σ_p = ℏ / 2)", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_fund)

    render(os.path.join(IMG, "fig1-wavepacket-fourier.svg"), W, H, *frags)


def fig_gamma_microscope():
    """fig2-gamma-microscope.svg: Мисленнєвий експеримент Гайзенберга з гамма-мікроскопом."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Мисленнєвий експеримент: гамма-мікроскоп Гайзенберга (1927)", size=16, bold=True, color="#1e293b"))

    # Лінза мікроскопа зверху
    cx_lens, cy_lens = 400, 140
    frags.append(path_svg("M 280 140 Q 400 110 520 140 Q 400 170 280 140 Z", fill=BLUE_F, stroke=BLUE_S, sw=2.0))
    frags.append(text(400, 142, "Об'єктив мікроскопа", size=12, bold=True, color=BLUE_S))

    # Оптична вісь та кут апертури θ
    frags.append(line(400, 140, 400, 320, color="#94a3b8", sw=1.2, dash="4,4"))

    # Електрон у фокусі
    cx_e, cy_e = 400, 320
    frags.append(circle(cx_e, cy_e, 9, fill=RED_S, stroke=RED_S))
    frags.append(text(cx_e + 16, cy_e + 4, "Електрон e⁻", size=12, bold=True, color=RED_S))

    # Падаючий гамма-фотон зліва
    frags.append(path_svg("M 160 350 Q 220 330 280 340 T 340 330 L 385 323", fill="none", stroke=AMBER_S, sw=2.2))
    frags.append(path_svg("M 373 318 L 387 322 L 378 332", fill="none", stroke=AMBER_S, sw=2.2))
    frags.append(text(240, 365, "Падаючий γ-фотон (імпульс h / λ)", size=11, bold=True, color=AMBER_S))

    # Розсіяні фотони в об'єктив під кутами ±θ
    frags.append(line(cx_e, cy_e, 290, 140, color=AMBER_S, sw=1.8, dash="4,3"))
    frags.append(line(cx_e, cy_e, 510, 140, color=AMBER_S, sw=1.8, dash="4,3"))

    # Дуга кута 2θ
    frags.append(path_svg("M 360 260 Q 400 245 440 260", fill="none", stroke=PURPLE_S, sw=1.8))
    frags.append(text(400, 235, "Кут апертури 2θ", size=11, bold=True, color=PURPLE_S))

    # Віддача електрона (розсіювання)
    frags.append(line(cx_e, cy_e, 490, 355, color=RED_S, sw=2.5))
    frags.append(path_svg("M 478 354 L 492 356 L 485 344", fill="none", stroke=RED_S, sw=2.5))
    frags.append(text(510, 365, "Імпульс віддачі Δp_x", size=11, bold=True, color=RED_S))

    # Інформаційні блоки праворуч
    frags.append(rect(580, 60, 270, 320, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(715, 85, "Межа дифракції та віддача", size=12, bold=True, color="#1e293b"))

    b_res, _, _ = textbox(715, 140, "Оптичне розділення:\nΔx ≈ λ / (2 sin θ)\n(Дифракційна межа)", size=11, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_res)

    b_rec, _, _ = textbox(715, 230, "Переданий імпульс:\nΔp_x ≈ (h / λ) sin θ\n(Невизначеність віддачі)", size=11, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_rec)

    b_prod, _, _ = textbox(715, 320, "Добуток невизначеностей:\nΔx · Δp_x ≈ h / 2 ≥ ℏ / 2", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_prod)

    render(os.path.join(IMG, "fig2-gamma-microscope.svg"), W, H, *frags)


def fig_hydrogen_stability():
    """fig3-hydrogen-stability.svg: Забезпечення стійкості атома водню завдяки принципу невизначеності."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Стійкість атома водню: баланс кінетичної та кулонівської енергій", size=16, bold=True, color="#1e293b"))

    # Графічний простір зліва
    frags.append(rect(30, 60, 470, 320, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(265, 85, "Залежність енергії E від радіуса r", size=13, bold=True, color="#1e293b"))

    # Осі графіка
    frags.append(line(60, 240, 470, 240, color="#64748b", sw=1.5)) # Горизонтальна вісь r (E=0)
    frags.append(line(80, 100, 80, 360, color="#64748b", sw=1.5))  # Вертикальна вісь E
    frags.append(text(475, 244, "r", size=12, bold=True, color="#64748b"))
    frags.append(text(85, 110, "Енергія E", size=11, color="#64748b"))

    # Крива E_pot(r) = - C / r  (Кулонівське притягання, червона)
    pts_pot = []
    for px in range(95, 460, 3):
        r_val = (px - 80) / 45.0
        e_pot = -1.2 / r_val
        py = 240 - e_pot * 55.0
        if 100 <= py <= 360:
            pts_pot.append((px, py))
    path_pot = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_pot)
    frags.append(path_svg(path_pot, fill="none", stroke=RED_S, sw=2.0, dash="5,4"))
    frags.append(text(380, 320, "E_pot(r) = -e² / (4π ε₀ r)", size=10, bold=True, color=RED_S))

    # Крива E_kin(r) = ℏ² / (2 m r²)  (Квантове тиснення, зелена)
    pts_kin = []
    for px in range(95, 460, 3):
        r_val = (px - 80) / 45.0
        e_kin = 0.65 / (r_val * r_val)
        py = 240 - e_kin * 55.0
        if 80 <= py <= 350:
            pts_kin.append((px, py))
    path_kin = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_kin)
    frags.append(path_svg(path_kin, fill="none", stroke=GREEN_S, sw=2.0, dash="5,4"))
    frags.append(text(330, 130, "E_kin(r) ≈ ℏ² / (2 m r²)", size=10, bold=True, color=GREEN_S))

    # Крива повного мінімуму E_tot(r) = E_kin + E_pot (синя)
    pts_tot = []
    r_min_px = 185
    y_min_px = 285
    for px in range(95, 460, 3):
        r_val = (px - 80) / 45.0
        e_tot = 0.65 / (r_val * r_val) - 1.2 / r_val
        py = 240 - e_tot * 55.0
        if 80 <= py <= 360:
            pts_tot.append((px, py))
    path_tot = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_tot)
    frags.append(path_svg(path_tot, fill="none", stroke=BLUE_S, sw=3.0))

    # Позначення Борового радіуса a_0 та мінімуму E_0
    frags.append(line(r_min_px, 100, r_min_px, 350, color=PURPLE_S, sw=1.2, dash="3,3"))
    frags.append(circle(r_min_px, y_min_px, 5, fill=PURPLE_S, stroke=PURPLE_S))
    frags.append(text(r_min_px - 15, 368, "a₀ (Боровий радіус)", size=11, bold=True, color=PURPLE_S))

    # Пояснювальний блок праворуч
    frags.append(rect(520, 60, 330, 320, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(685, 85, "Чому електрон не падає на ядро", size=13, bold=True, color="#1e293b"))

    b_1, _, _ = textbox(685, 135, "1. Стискання в ядро (r → 0):\nЗменшення r змушує p ≈ ℏ/r зростати.", size=11, fill=RED_F, stroke=RED_S)
    frags.append(b_1)

    b_2, _, _ = textbox(685, 215, "2. Зростання кінетичної енергії:\nE_kin ∝ 1/r² зростає швидше, ніж\nкулонівське притягання -1/r.", size=11, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_2)

    b_3, _, _ = textbox(685, 305, "3. Виникнення стійкого мінімуму:\nСистема знаходить стан з мінімумом E_0\nпри радіусі a₀ ≈ 0.53 Å (стан 1s).", size=11, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_3)

    render(os.path.join(IMG, "fig3-hydrogen-stability.svg"), W, H, *frags)


def fig_wavepacket_spreading():
    """fig4-wavepacket-spreading.svg: Динаміка розпливання вільного Гаусового хвильового пакета у часі."""
    W, H = 880, 400
    frags = []

    frags.append(rect(10, 10, 860, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Еволюція та дисперсійне розпливання вільного хвильового пакета |ψ(x, t)|²", size=16, bold=True, color="#1e293b"))

    # Осі координат
    frags.append(line(50, 320, 830, 320, color="#64748b", sw=1.8))
    frags.append(text(835, 324, "x", size=13, bold=True, color="#64748b"))

    # Загальний огинаючий фронт (конус розпливання)
    frags.append(line(120, 320, 720, 120, color="#cbd5e1", sw=1.2, dash="4,4"))
    frags.append(line(120, 320, 720, 340, color="#cbd5e1", sw=1.2, dash="4,4"))

    # Профіль t = 0 (дуже вузький, високий пік)
    x0, y0_base = 180, 320
    sigma_0 = 18.0
    pts_t0 = []
    for px in range(120, 240, 2):
        dx = px - x0
        val = math.exp(-(dx * dx) / (2 * sigma_0 * sigma_0))
        py = y0_base - 220 * val
        pts_t0.append((px, py))
    path_t0 = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_t0)
    pts_t0_fill = [(120, y0_base)] + pts_t0 + [(238, y0_base)]
    frags.append(path_svg("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_t0_fill) + " Z", fill=BLUE_F, stroke="none"))
    frags.append(path_svg(path_t0, fill="none", stroke=BLUE_S, sw=2.5))
    frags.append(text(x0, 80, "t = 0 (вузька σ₀)", size=11, bold=True, color=BLUE_S))

    # Профіль t = t_1 (проміжний розмах)
    x1 = 430
    sigma_1 = 45.0
    pts_t1 = []
    for px in range(300, 560, 2):
        dx = px - x1
        val = math.exp(-(dx * dx) / (2 * sigma_1 * sigma_1))
        py = y0_base - 130 * val
        pts_t1.append((px, py))
    path_t1 = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_t1)
    pts_t1_fill = [(300, y0_base)] + pts_t1 + [(558, y0_base)]
    frags.append(path_svg("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_t1_fill) + " Z", fill=PURPLE_F, stroke="none"))
    frags.append(path_svg(path_t1, fill="none", stroke=PURPLE_S, sw=2.5))
    frags.append(text(x1, 165, "t = t₁ > 0", size=11, bold=True, color=PURPLE_S))

    # Профіль t = t_2 (широкий, низький розмах)
    x2 = 680
    sigma_2 = 85.0
    pts_t2 = []
    for px in range(500, 820, 2):
        dx = px - x2
        val = math.exp(-(dx * dx) / (2 * sigma_2 * sigma_2))
        py = y0_base - 70 * val
        pts_t2.append((px, py))
    path_t2 = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_t2)
    pts_t2_fill = [(500, y0_base)] + pts_t2 + [(818, y0_base)]
    frags.append(path_svg("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_t2_fill) + " Z", fill=TEAL_F, stroke="none"))
    frags.append(path_svg(path_t2, fill="none", stroke=TEAL_S, sw=2.5))
    frags.append(text(x2, 230, "t = t₂ >> t₁", size=11, bold=True, color=TEAL_S))

    # Пояснювальний підпис закону розпливання
    b_law, _, _ = textbox(440, 355, "Закон розпливання пакета: σ(t) = σ₀ · √(1 + (ℏ t / (2 m σ₀²))²)    Норма збережена: ∫ |ψ|² dx = 1", size=11, bold=True, fill=GRAY_F, stroke="#cbd5e1")
    frags.append(b_law)

    render(os.path.join(IMG, "fig4-wavepacket-spreading.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_wavepacket_fourier()
    fig_gamma_microscope()
    fig_hydrogen_stability()
    fig_wavepacket_spreading()
    print("Усі 4 фігури для принципу невизначеності успішно згенеровано у", IMG)

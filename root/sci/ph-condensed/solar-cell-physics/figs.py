# -*- coding: utf-8 -*-
"""Фігури до теми «Фізика сонячного елемента».
Запуск: python figs.py -> створює SVG у ./img/
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

# ── Фігура 1: Будова p-n сонячного елемента ──────────────────────────────────
def fig_solar_cell_structure():
    W, H = 840, 480
    f = []

    f.append(text(W / 2, 25, "Будова p-n сонячного елемента та розділення носіїв світлом", size=16, bold=True, color=INK))

    # Sun Rays
    for x_ray in (140, 180, 220, 260, 300, 340):
        f.append(arrow(x_ray - 20, 40, x_ray, 75, color="#d97706", sw=2))
    f.append(text(230, 42, "Сонячне випромінювання (hν ≥ E_g)", size=11, bold=True, color="#b45309"))

    # Grid contacts (N-side metal) — placed above ARC without overlapping
    f.append(rect(140, 60, 24, 28, fill="#64748b", stroke="#334155", sw=1.5, rx=2))
    f.append(rect(340, 60, 24, 28, fill="#64748b", stroke="#334155", sw=1.5, rx=2))
    f.append(text(152, 54, "Контакт (+)", size=9, bold=True, color="#334155"))

    # Anti-reflective coating
    f.append(rect(80, 88, 460, 14, fill="#3b82f6", stroke="#2563eb", sw=1, rx=2))
    f.append(text(310, 99, "Противідбивальне покриття (ARC, SiN_x)", size=10, bold=True, color="#ffffff"))

    # Emitter n-layer
    f.append(rect(80, 102, 460, 42, fill="#dbeafe", stroke="#93c5fd", sw=1.5, rx=0))
    f.append(text(150, 126, "n-емітер (тонкий, n^+)", size=11, bold=True, color="#1e40af"))

    # Depletion Region
    f.append(rect(80, 144, 460, 56, fill="#fef08a", stroke="#fde047", sw=1.5, rx=0))
    f.append(text(160, 176, "Збіднена область (p-n перехід)", size=11, bold=True, color="#854d0e"))

    # Internal Electric Field E_bi
    f.append(arrow(430, 176, 270, 176, color="#dc2626", sw=2))
    f.append(text(350, 166, "Вбудоване поле E_bi", size=10, bold=True, color="#dc2626"))

    # Base p-layer
    f.append(rect(80, 200, 460, 185, fill="#fee2e2", stroke="#fca5a5", sw=1.5, rx=0))
    f.append(text(140, 285, "p-база (об'ємна)", size=11, bold=True, color="#991b1b"))

    # Back metal contact
    f.append(rect(80, 385, 460, 20, fill="#475569", stroke="#1e293b", sw=1.5, rx=2))
    f.append(text(310, 399, "Суцільний задній металевий контакт (−)", size=10, bold=True, color="#ffffff"))

    # Photocarrier generation & motion inside semiconductor
    f.append(circle(210, 245, 7, fill="#ef4444", stroke="#b91c1c"))
    f.append(text(210, 245, "h⁺", size=9, color="#ffffff", bold=True))
    f.append(circle(235, 245, 7, fill="#3b82f6", stroke="#1d4ed8"))
    f.append(text(235, 245, "e⁻", size=9, color="#ffffff", bold=True))
    f.append(text(222, 230, "Генерація e⁻/h⁺", size=10, italic=True, color="#475569"))

    # Electron diffusion
    f.append(arrow(242, 242, 275, 192, color="#2563eb", sw=1.8))
    f.append(text(285, 222, "Дифузія e⁻", size=10, bold=True, color="#2563eb"))

    # Electron drift
    f.append(arrow(290, 168, 290, 124, color="#2563eb", sw=2))
    f.append(text(315, 142, "Дрейф e⁻ в n-зону", size=10, bold=True, color="#1e40af"))

    # Hole drift
    f.append(arrow(380, 168, 380, 235, color="#dc2626", sw=2))
    f.append(text(405, 210, "Дрейф h⁺ в p-зону", size=10, bold=True, color="#991b1b"))

    # External Circuit
    f.append(line(352, 60, 352, 45, color=INK, sw=2))
    f.append(line(352, 45, 680, 45, color=INK, sw=2))
    f.append(line(680, 45, 680, 175, color=INK, sw=2))

    # Load Resistor R_L box
    f.append(rect(645, 175, 70, 80, fill="#f8fafc", stroke="#334155", sw=2, rx=4))
    f.append(text(680, 203, "Навантаження", size=10, bold=True, color=INK))
    f.append(text(680, 225, "R_L", size=13, bold=True, color="#2563eb"))

    # Wires from R_L to bottom contact
    f.append(line(680, 255, 680, 395, color=INK, sw=2))
    f.append(line(680, 395, 540, 395, color=INK, sw=2))

    # Photocurrent direction arrow
    f.append(arrow(570, 45, 630, 45, color="#2563eb", sw=2.2))
    f.append(text(600, 33, "Фотострум I_ph", size=10, bold=True, color="#2563eb"))

    # Right Legend Panel — wider padding to prevent line intersection
    f.append(rect(560, 290, 260, 135, fill="#f1f5f9", stroke=BORDER, sw=1.5, rx=6))
    f.append(text(690, 310, "Ключові параметри:", size=11, bold=True, color=INK))
    f.append(text(575, 330, "• d_n << d_p (тонкий емітер)", size=10, color=MUTED, anchor="left"))
    f.append(text(575, 350, "• L_n > d_p (довжина дифузії)", size=10, color=MUTED, anchor="left"))
    f.append(text(575, 370, "• V_oc — напруга холостого ходу", size=10, color=MUTED, anchor="left"))
    f.append(text(575, 390, "• I_sc — струм короткого замкнення", size=10, color=MUTED, anchor="left"))
    f.append(text(575, 410, "• R_L створює вихідну потужність P", size=10, color=MUTED, anchor="left"))

    return render(os.path.join(IMG_DIR, "solar-cell-structure.svg"), W, H, *f)

# ── Фігура 2: Вольт-амперна та потужнісна характеристики ────────────────────
def fig_iv_curve():
    W, H = 840, 460
    f = []

    f.append(text(W / 2, 25, "Вольт-амперна (I-V) та потужнісна (P-V) характеристики фотоелемента", size=16, bold=True, color=INK))

    # Axis coordinates
    ox, oy = 90, 370
    w_axis, h_axis = 440, 310

    # Fill Factor Rectangles (Background)
    v_oc_x = ox + 380
    i_sc_y = oy - 270

    f.append(rect(ox, i_sc_y, 380, 270, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=0))
    f.append(text(ox + 290, i_sc_y + 25, "Прямокутник I_sc × V_oc", size=10, color="#94a3b8", italic=True))

    v_mp_x = ox + 310
    i_mp_y = oy - 225
    f.append(rect(ox, i_mp_y, 310, 225, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=0))
    f.append(text(ox + 155, oy - 110, "Максимальна потужність", size=12, bold=True, color="#1d4ed8"))
    f.append(text(ox + 155, oy - 90, "P_max = I_mp × V_mp", size=12, bold=True, color="#1d4ed8"))

    # Grid lines
    for vy in range(oy - 50, oy - 300, -50):
        f.append(line(ox, vy, ox + w_axis, vy, color="#e2e8f0", sw=1))
    for vx in range(ox + 50, ox + w_axis, 50):
        f.append(line(vx, oy, vx, oy - h_axis, color="#e2e8f0", sw=1))

    # Axes
    f.append(arrow(ox, oy, ox + w_axis + 20, oy, color=INK, sw=2))
    f.append(arrow(ox, oy, ox, oy - h_axis - 20, color=INK, sw=2))
    f.append(text(ox + w_axis + 25, oy + 5, "Напруга V (В)", size=11, bold=True, color=INK, anchor="left"))
    f.append(text(ox - 10, oy - h_axis - 25, "Струм I (А) / Потужність P (Вт)", size=11, bold=True, color=INK, anchor="left"))

    # Dark I-V curve
    dark_pts = []
    for step in range(0, 101):
        v = step / 100.0 * 1.1
        i_val = 0.005 * (math.exp(v * 4.8) - 1)
        x_p = ox + v * 350
        y_p = oy - i_val * 250
        if y_p >= oy - h_axis - 10:
            dark_pts.append((x_p, y_p))

    d_path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in dark_pts)
    f.append(path_svg(d_path, stroke="#94a3b8", sw=2, dash="5,5"))
    f.append(text(ox + 350, oy - 290, "Темнова ВАХ (диодна)", size=10, color="#64748b", bold=True))

    # Illuminated I-V curve
    light_pts = []
    for step in range(0, 101):
        v = step / 100.0 * 1.1
        i_val = 1.08 - 0.005 * (math.exp(v * 4.8) - 1)
        if i_val < 0:
            i_val = 0
        x_p = ox + v * 345
        y_p = oy - i_val * 250
        light_pts.append((x_p, y_p))

    l_path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in light_pts)
    f.append(path_svg(l_path, stroke="#2563eb", sw=3))
    f.append(text(ox + 180, oy - 275, "Освітлена ВАХ I(V)", size=12, color="#1d4ed8", bold=True))

    # Power curve P(V)
    power_pts = []
    for step in range(0, 101):
        v = step / 100.0 * 1.1
        i_val = 1.08 - 0.005 * (math.exp(v * 4.8) - 1)
        if i_val < 0:
            i_val = 0
        p_val = i_val * v
        x_p = ox + v * 345
        y_p = oy - p_val * 310
        power_pts.append((x_p, y_p))

    p_path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in power_pts)
    f.append(path_svg(p_path, stroke="#dc2626", sw=2.5, dash="4,2"))
    f.append(text(ox + 250, oy - 170, "Потужність P(V)", size=12, color="#dc2626", bold=True))

    # Key Points & Markers
    f.append(circle(ox, i_sc_y, 5, fill="#2563eb", stroke="#1d4ed8"))
    f.append(text(ox - 10, i_sc_y, "I_sc", size=12, bold=True, color="#2563eb", anchor="end"))

    f.append(circle(v_oc_x, oy, 5, fill="#2563eb", stroke="#1d4ed8"))
    f.append(text(v_oc_x, oy + 20, "V_oc", size=12, bold=True, color="#2563eb"))

    f.append(circle(v_mp_x, i_mp_y, 6, fill="#dc2626", stroke="#991b1b"))
    f.append(line(v_mp_x, oy, v_mp_x, i_mp_y, color="#3b82f6", sw=1.5, dash="3,3"))
    f.append(line(ox, i_mp_y, v_mp_x, i_mp_y, color="#3b82f6", sw=1.5, dash="3,3"))

    f.append(text(v_mp_x, oy + 20, "V_mp", size=11, bold=True, color="#1d4ed8"))
    f.append(text(ox - 10, i_mp_y, "I_mp", size=11, bold=True, color="#1d4ed8", anchor="end"))
    f.append(text(v_mp_x + 15, i_mp_y - 12, "MPP (Точка макс. потужності)", size=11, bold=True, color="#dc2626", anchor="left"))

    # Right Info Panel
    f.append(rect(560, 70, 260, 330, fill="#f8fafc", stroke=BORDER, sw=1.5, rx=6))
    f.append(text(690, 95, "Розрахункові співвідношення:", size=11, bold=True, color=INK))

    f.append(text(575, 125, "1. Рівняння освітленої ВАХ:", size=10, bold=True, color="#1e40af", anchor="left"))
    f.append(text(585, 145, "I(V) = I_ph − I_0(e^{qV/k_BT} − 1)", size=10, color=INK, anchor="left"))

    f.append(text(575, 180, "2. Напруга холостого ходу:", size=10, bold=True, color="#1e40af", anchor="left"))
    f.append(text(585, 200, "V_oc = (k_BT/q) ln(I_ph/I_0 + 1)", size=10, color=INK, anchor="left"))

    f.append(text(575, 235, "3. Коефіцієнт заповнення FF:", size=10, bold=True, color="#1e40af", anchor="left"))
    f.append(text(585, 255, "FF = (V_mp × I_mp) / (V_oc × I_sc)", size=10, bold=True, color="#d97706", anchor="left"))
    f.append(text(585, 275, "Для Si: FF ≈ 0.78 … 0.84", size=10, color=MUTED, anchor="left"))

    f.append(text(575, 310, "4. ККД елемента (η):", size=10, bold=True, color="#1e40af", anchor="left"))
    f.append(text(585, 330, "η = P_max / P_in", size=10, bold=True, color="#dc2626", anchor="left"))
    f.append(text(585, 350, "η = (V_oc × I_sc × FF) / P_in", size=10, bold=True, color="#dc2626", anchor="left"))

    return render(os.path.join(IMG_DIR, "iv-curve.svg"), W, H, *f)

# ── Фігура 3: Втрати сонячного спектра та межа Шокли — Квайссера ─────────────
def fig_shockley_queisser_losses():
    W, H = 840, 460
    f = []

    f.append(text(W / 2, 25, "Межа Шокли — Квайссера та баланс спектральних втрат", size=16, bold=True, color=INK))

    ox, oy = 80, 380
    w_axis, h_axis = 380, 300

    # Grid
    for vy in range(oy - 50, oy - 300, -50):
        f.append(line(ox, vy, ox + w_axis, vy, color="#f1f5f9", sw=1))
    for vx in range(ox + 60, ox + w_axis, 60):
        f.append(line(vx, oy, vx, oy - h_axis, color="#f1f5f9", sw=1))

    # Axes
    f.append(arrow(ox, oy, ox + w_axis + 15, oy, color=INK, sw=2))
    f.append(arrow(ox, oy, ox, oy - h_axis - 15, color=INK, sw=2))
    f.append(text(ox + w_axis + 15, oy + 18, "Ширина зони E_g (еВ)", size=11, bold=True, color=INK))
    f.append(text(ox - 10, oy - h_axis - 15, "ККД η (%)", size=11, bold=True, color=INK, anchor="left"))

    # Ticks & Labels on X
    for idx, eg_val in enumerate([0.5, 1.0, 1.34, 1.5, 2.0, 2.5]):
        x_p = ox + (eg_val - 0.4) / 2.2 * w_axis
        f.append(line(x_p, oy, x_p, oy + 4, color=INK, sw=1.5))
        f.append(text(x_p, oy + 16, f"{eg_val}", size=10, color=INK))

    # Ticks & Labels on Y
    for eta_val in [10, 20, 30, 40]:
        y_p = oy - eta_val / 40.0 * h_axis
        f.append(line(ox - 4, y_p, ox, y_p, color=INK, sw=1.5))
        f.append(text(ox - 8, y_p + 4, f"{eta_val}%", size=10, color=INK, anchor="end"))

    # SQ Curve
    sq_pts = []
    for step in range(0, 101):
        eg = 0.4 + step / 100.0 * 2.2
        if eg < 1.34:
            eta = 33.7 * math.exp(-((eg - 1.34) / 0.85) ** 2)
        else:
            eta = 33.7 * math.exp(-((eg - 1.34) / 1.1) ** 2)
        x_p = ox + (eg - 0.4) / 2.2 * w_axis
        y_p = oy - eta / 40.0 * h_axis
        sq_pts.append((x_p, y_p))

    sq_path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in sq_pts)
    f.append(path_svg(sq_path, stroke="#dc2626", sw=3))

    # Markers
    si_x = ox + (1.12 - 0.4) / 2.2 * w_axis
    si_y = oy - 32.2 / 40.0 * h_axis
    f.append(circle(si_x, si_y, 5, fill="#2563eb", stroke="#1d4ed8"))
    f.append(line(si_x, si_y, si_x, oy, color="#2563eb", sw=1, dash="2,2"))
    f.append(text(si_x - 5, si_y - 12, "Si (1.12 eV, ~32%)", size=9, bold=True, color="#1d4ed8"))

    opt_x = ox + (1.34 - 0.4) / 2.2 * w_axis
    opt_y = oy - 33.7 / 40.0 * h_axis
    f.append(circle(opt_x, opt_y, 6, fill="#dc2626", stroke="#991b1b"))
    f.append(line(opt_x, opt_y, opt_x, oy, color="#dc2626", sw=1, dash="2,2"))
    f.append(text(opt_x + 15, opt_y - 12, "Максимум SQ: GaAs (1.34 eV, 33.7%)", size=10, bold=True, color="#dc2626", anchor="left"))

    # Right Panel: Loss breakdown stacked bar
    bx, by = 510, 80
    bw, bh = 310, 310

    f.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=BORDER, sw=1.5, rx=6))
    f.append(text(bx + bw / 2, by + 22, "Розподіл енергії фотонів (AM1.5)", size=12, bold=True, color=INK))

    sections = [
        ("Термалізація гарячих носіїв (hν > E_g)", "33%", "#fca5a5", "#dc2626"),
        ("Пропущення квантів (hν < E_g)", "23%", "#fdba74", "#ea580c"),
        ("Радіаційна рекомбінація & фотони", "7%", "#fde047", "#ca8a04"),
        ("Термодинамічні втрати V_oc / FF", "17%", "#cbd5e1", "#475569"),
        ("Максимальна корисна робота (P_max)", "20-33.7%", "#86efac", "#16a34a")
    ]

    curr_y = by + 45
    bar_w = 70
    bar_x = bx + 20

    bar_heights = [70, 50, 20, 45, 80]
    for idx, (label, pct, bg_c, txt_c) in enumerate(sections):
        h_sec = bar_heights[idx]
        f.append(rect(bar_x, curr_y, bar_w, h_sec, fill=bg_c, stroke=txt_c, sw=1, rx=0))
        f.append(rect(bx + 105, curr_y + h_sec / 2 - 7, 14, 14, fill=bg_c, stroke=txt_c, sw=1, rx=2))
        f.append(text(bx + 125, curr_y + h_sec / 2 + 3, label, size=9, color=INK, anchor="left", bold=(idx==4)))
        f.append(text(bar_x + bar_w / 2, curr_y + h_sec / 2 + 4, pct, size=10, bold=True, color=txt_c))
        curr_y += h_sec

    f.append(text(bx + bw / 2, by + bh - 12, "Межа для 1-перехідного елемента: 33.7%", size=10, bold=True, color="#16a34a"))

    return render(os.path.join(IMG_DIR, "shockley-queisser-losses.svg"), W, H, *f)

if __name__ == "__main__":
    fig_solar_cell_structure()
    fig_iv_curve()
    fig_shockley_queisser_losses()
    print("Всі 3 фігури згенеровано успішно в ./img/")

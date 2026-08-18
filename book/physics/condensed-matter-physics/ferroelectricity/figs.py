# -*- coding: utf-8 -*-
"""Фігури до теми «Сегнетоелектрика та сегнетоелектричні домени».
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

def write_svg(path, f, w, h):
    render(path, w, h, *f)

# ── Фігура 1: Перовськітна структура BaTiO3 (Кубічна та Тетрагональна фази) ───
def fig_perovskite_structure():
    W, H = 780, 430
    f = []

    f.append(text(W / 2, 28, "Кристалічна структура перовськіту (BaTiO3) вище та нижче точки Кюрі", size=16, bold=True, color=INK))

    # Left panel: T > Tc (Cubic, centrosymmetric)
    # Right panel: T < Tc (Tetragonal, ferroelectric)
    panel_w = 360
    panel_h = 350
    y0 = 55

    # Left Panel: Cubic
    f.append(rect(20, y0, panel_w, panel_h, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(20 + panel_w / 2, y0 + 24, "T > T_C (Пароелектрична фаза, кубічна)", size=13, bold=True, color="#0f172a"))
    f.append(text(20 + panel_w / 2, y0 + 44, "Центросиметрична структура, P_s = 0", size=11, color=MUTED))

    # Cube drawing (isometric perspective)
    # Center of cube at (200, 230)
    cx1, cy1 = 200, 230
    size = 110
    dx, dy = 45, 30  # projection offset

    # Cube vertices relative to center
    # Front face
    fx0, fy0 = cx1 - size/2, cy1 - size/2
    fx1, fy1 = cx1 + size/2, cy1 + size/2
    # Back face
    bx0, by0 = fx0 + dx, fy0 - dy
    bx1, by1 = fx1 + dx, fy1 - dy

    # Draw back edges
    f.append(path_svg(f"M {bx0} {by0} L {bx1} {by0} L {bx1} {by1} L {bx0} {by1} Z", fill="none", stroke="#94a3b8", sw=1.2, dash="3,3"))
    f.append(path_svg(f"M {fx0} {fy0} L {bx0} {by0}", stroke="#94a3b8", sw=1.2, dash="3,3"))
    f.append(path_svg(f"M {fx1} {fy0} L {bx1} {by0}", stroke="#94a3b8", sw=1.2, dash="3,3"))
    f.append(path_svg(f"M {fx1} {fy1} L {bx1} {by1}", stroke="#94a3b8", sw=1.2, dash="3,3"))

    # Draw front face & outer connecting lines
    f.append(path_svg(f"M {fx0} {fy0} L {fx1} {fy0} L {fx1} {fy1} L {fx0} {fy1} Z", fill="none", stroke="#475569", sw=1.5))
    f.append(path_svg(f"M {fx0} {fy1} L {bx0} {by1}", stroke="#475569", sw=1.5))

    # Ba2+ ions at 8 corners
    corners = [
        (fx0, fy0), (fx1, fy0), (fx1, fy1), (fx0, fy1),
        (bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)
    ]
    for px, py in corners:
        f.append(circle(px, py, 9, fill="#3b82f6", stroke="#1d4ed8", sw=1.5))

    # O2- ions at 6 face centers
    faces = [
        ((fx0+fx1)/2, (fy0+fy1)/2), # front
        ((bx0+bx1)/2, (by0+by1)/2), # back
        ((fx0+bx0)/2, (fy0+by0)/2), # top
        ((fx1+bx1)/2, (fy1+by1)/2), # bottom
        ((fx0+bx0)/2, (fy1+by1)/2), # left
        ((fx1+bx1)/2, (fy0+by0)/2), # right
    ]
    for px, py in faces:
        f.append(circle(px, py, 7, fill="#ef4444", stroke="#b91c1c", sw=1.5))

    # Ti4+ ion at exact center
    mid_x, mid_y = (cx1 + dx/2), (cy1 - dy/2)
    f.append(circle(mid_x, mid_y, 11, fill="#10b981", stroke="#047857", sw=2))
    f.append(text(mid_x, mid_y + 4, "Ti⁴⁺", size=10, bold=True, color="#ffffff", anchor="middle"))

    f.append(text(20 + panel_w / 2, y0 + 325, "Ti⁴⁺ точно в центрі кисневого октаедра", size=11, italic=True, color="#334155"))


    # Right Panel: Tetragonal
    rx0 = 400
    f.append(rect(rx0, y0, panel_w, panel_h, fill="#eff6ff", stroke="#bfdbfe", rx=8))
    f.append(text(rx0 + panel_w / 2, y0 + 24, "T < T_C (Сегнетоелектрична фаза, тетрагональна)", size=13, bold=True, color="#1e40af"))
    f.append(text(rx0 + panel_w / 2, y0 + 44, "Несиметрична структура, P_s > 0", size=11, color="#1d4ed8"))

    cx2, cy2 = rx0 + 180, 230
    
    # Cube distorted (c-axis elongated vertically)
    c_size_y = 125
    c_size_x = 105
    
    r_fx0, r_fy0 = cx2 - c_size_x/2, cy2 - c_size_y/2
    r_fx1, r_fy1 = cx2 + c_size_x/2, cy2 + c_size_y/2
    r_bx0, r_by0 = r_fx0 + dx, r_fy0 - dy
    r_bx1, r_by1 = r_fx1 + dx, r_fy1 - dy

    # Draw back edges
    f.append(path_svg(f"M {r_bx0} {r_by0} L {r_bx1} {r_by0} L {r_bx1} {r_by1} L {r_bx0} {r_by1} Z", fill="none", stroke="#94a3b8", sw=1.2, dash="3,3"))
    f.append(path_svg(f"M {r_fx0} {r_fy0} L {r_bx0} {r_by0}", stroke="#94a3b8", sw=1.2, dash="3,3"))
    f.append(path_svg(f"M {r_fx1} {r_fy0} L {r_bx1} {r_by0}", stroke="#94a3b8", sw=1.2, dash="3,3"))
    f.append(path_svg(f"M {r_fx1} {r_by1} L {r_bx1} {r_by1}", stroke="#94a3b8", sw=1.2, dash="3,3"))

    # Draw front face & outer connecting lines
    f.append(path_svg(f"M {r_fx0} {r_fy0} L {r_fx1} {r_fy0} L {r_fx1} {r_fy1} L {r_fx0} {r_fy1} Z", fill="none", stroke="#1e3a8a", sw=1.5))
    f.append(path_svg(f"M {r_fx0} {r_fy1} L {r_bx0} {r_by1}", stroke="#1e3a8a", sw=1.5))

    # Ba2+ ions at 8 corners
    r_corners = [
        (r_fx0, r_fy0), (r_fx1, r_fy0), (r_fx1, r_fy1), (r_fx0, r_fy1),
        (r_bx0, r_by0), (r_bx1, r_by0), (r_bx1, r_by1), (r_bx0, r_by1)
    ]
    for px, py in r_corners:
        f.append(circle(px, py, 9, fill="#3b82f6", stroke="#1d4ed8", sw=1.5))

    # O2- ions at 6 face centers
    r_faces = [
        ((r_fx0+r_fx1)/2, (r_fy0+r_fy1)/2), # front
        ((r_bx0+r_bx1)/2, (r_by0+r_by1)/2), # back
        ((r_fx0+r_bx0)/2, (r_fy0+r_by0)/2), # top
        ((r_fx1+r_bx1)/2, (r_fy1+r_by1)/2), # bottom
        ((r_fx0+r_bx0)/2, (r_fy1+r_by1)/2), # left
        ((r_fx1+r_bx1)/2, (r_fy0+r_by0)/2), # right
    ]
    for px, py in r_faces:
        f.append(circle(px, py, 7, fill="#ef4444", stroke="#b91c1c", sw=1.5))

    # Ti4+ ion shifted UPWARDS along c-axis by dz = -18px
    r_mid_x, r_mid_y = (cx2 + dx/2), (cy2 - dy/2)
    shifted_y = r_mid_y - 18

    # Dashed circle showing original center
    f.append(circle(r_mid_x, r_mid_y, 4, fill="none", stroke="#94a3b8", sw=1))
    f.append(arrow(r_mid_x, r_mid_y, r_mid_x, shifted_y + 10, color="#dc2626", sw=2))
    f.append(text(r_mid_x + 16, r_mid_y - 8, "Δz", size=11, bold=True, color="#dc2626"))

    f.append(circle(r_mid_x, shifted_y, 11, fill="#10b981", stroke="#047857", sw=2))
    f.append(text(r_mid_x, shifted_y + 4, "Ti⁴⁺", size=10, bold=True, color="#ffffff", anchor="middle"))

    # Vector P_s arrow on the right
    p_arrow_x = rx0 + panel_w - 45
    f.append(arrow(p_arrow_x, cy2 + 50, p_arrow_x, cy2 - 60, color="#dc2626", sw=3))
    f.append(text(p_arrow_x + 14, cy2 - 10, "P_s", size=14, bold=True, color="#dc2626"))

    f.append(text(rx0 + panel_w / 2, y0 + 325, "Зсув Ti⁴⁺ вгору створює дипольний момент P_s", size=11, italic=True, color="#1e40af"))

    # Legend at bottom
    leg_y = H - 18
    f.append(circle(140, leg_y, 7, fill="#3b82f6", stroke="#1d4ed8"))
    f.append(text(152, leg_y + 4, "Ba²⁺ (кути)", size=11, color=INK))

    f.append(circle(330, leg_y, 7, fill="#10b981", stroke="#047857"))
    f.append(text(342, leg_y + 4, "Ti⁴⁺ (центр)", size=11, color=INK))

    f.append(circle(520, leg_y, 6, fill="#ef4444", stroke="#b91c1c"))
    f.append(text(530, leg_y + 4, "O²⁻ (грані)", size=11, color=INK))

    write_svg(os.path.join(IMG_DIR, "perovskite-structure.svg"), f, W, H)


# ── Фігура 2: Петля гістерезису P(E) ──────────────────────────────────────────
def fig_ferro_hysteresis():
    W, H = 760, 460
    f = []

    f.append(text(W / 2, 28, "Петля сегнетоелектричного гістерезису P(E) та характерні точки", size=16, bold=True, color=INK))

    ox, oy = 360, 240
    axis_w, axis_h = 280, 170

    # Background grid
    f.append(rect(ox - axis_w - 20, oy - axis_h - 20, 2 * axis_w + 40, 2 * axis_h + 40, fill="#f8fafc", stroke=BORDER, rx=6))

    # Axes
    f.append(arrow(ox - axis_w - 10, oy, ox + axis_w + 30, oy, color=INK, sw=1.5))
    f.append(text(ox + axis_w + 40, oy + 4, "E", size=14, bold=True, italic=True, color=INK))
    f.append(text(ox + axis_w + 40, oy + 20, "(Поле)", size=10, color=MUTED))

    f.append(arrow(ox, oy + axis_h + 10, ox, oy - axis_h - 25, color=INK, sw=1.5))
    f.append(text(ox - 5, oy - axis_h - 32, "P", size=14, bold=True, italic=True, color=INK))
    f.append(text(ox - 85, oy - axis_h - 32, "(Поляризація)", size=10, color=MUTED))

    pts_upper = []
    pts_lower = []
    
    steps = 100
    E_max = 220
    
    for i in range(steps + 1):
        t = -1.0 + 2.0 * (i / steps)
        E_val = t * E_max
        P_val = 135 * math.tanh((E_val - 85) / 55) + 15 * (E_val / E_max)
        pts_lower.append((ox + E_val, oy - P_val))

    for i in range(steps + 1):
        t = 1.0 - 2.0 * (i / steps)
        E_val = t * E_max
        P_val = 135 * math.tanh((E_val + 85) / 55) + 15 * (E_val / E_max)
        pts_upper.append((ox + E_val, oy - P_val))

    pts_virgin = []
    for i in range(51):
        t = i / 50.0
        E_val = t * E_max
        P_val = 135 * math.tanh((E_val) / 100) * (E_val / E_max)**0.8 + 15 * (E_val / E_max)
        pts_virgin.append((ox + E_val, oy - P_val))

    d_virgin = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_virgin)
    f.append(path_svg(d_virgin, stroke="#94a3b8", sw=1.8, dash="4,4"))

    d_lower = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_lower)
    d_upper = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts_upper)
    f.append(path_svg(d_lower, stroke="#2563eb", sw=2.5))
    f.append(path_svg(d_upper, stroke="#2563eb", sw=2.5))

    f.append(arrow(ox + 120, oy - 80, ox + 140, oy - 98, color="#2563eb", sw=2))
    f.append(arrow(ox - 120, oy + 80, ox - 140, oy + 98, color="#2563eb", sw=2))

    P_r_val = 135 * math.tanh(85 / 55)
    f.append(circle(ox, oy - P_r_val, 5, fill="#dc2626", stroke="#991b1b"))
    f.append(path_svg(f"M {ox} {oy - P_r_val} L {ox - 45} {oy - P_r_val}", stroke="#dc2626", sw=1, dash="2,2"))
    f.append(text(ox - 55, oy - P_r_val + 4, "+P_r", size=13, bold=True, color="#dc2626", anchor="end"))
    f.append(text(ox - 55, oy - P_r_val + 18, "(залишкова)", size=10, color="#dc2626", anchor="end"))

    f.append(circle(ox, oy + P_r_val, 5, fill="#dc2626", stroke="#991b1b"))
    f.append(text(ox + 15, oy + P_r_val + 4, "-P_r", size=13, bold=True, color="#dc2626"))

    E_c_val = 85.0
    f.append(circle(ox + E_c_val, oy, 5, fill="#16a34a", stroke="#15803d"))
    f.append(path_svg(f"M {ox + E_c_val} {oy} L {ox + E_c_val} {oy + 40}", stroke="#16a34a", sw=1, dash="2,2"))
    f.append(text(ox + E_c_val, oy + 54, "+E_c", size=13, bold=True, color="#16a34a", anchor="middle"))
    f.append(text(ox + E_c_val, oy + 68, "(коерцитивне)", size=10, color="#16a34a", anchor="middle"))

    f.append(circle(ox - E_c_val, oy, 5, fill="#16a34a", stroke="#15803d"))
    f.append(text(ox - E_c_val, oy - 12, "-E_c", size=13, bold=True, color="#16a34a", anchor="middle"))

    P_sat_val = 135 * math.tanh((E_max - 85)/55) + 15
    f.append(circle(ox + E_max, oy - P_sat_val, 5, fill="#7c3aed", stroke="#6d28d9"))
    f.append(path_svg(f"M {ox} {oy - P_sat_val} L {ox + E_max} {oy - P_sat_val}", stroke="#7c3aed", sw=1, dash="2,2"))
    f.append(text(ox + E_max + 12, oy - P_sat_val + 4, "P_sat", size=13, bold=True, color="#7c3aed"))
    f.append(text(ox + E_max + 12, oy - P_sat_val + 18, "(насичення)", size=10, color="#7c3aed"))

    f.append(text(ox - 180, oy - 120, "Площа петлі = ∫ E dP", size=12, bold=True, color="#1e40af"))
    f.append(text(ox - 180, oy - 104, "(теплові втрати за цикл)", size=10, color=MUTED))

    bx1, by1 = ox + 140, oy - 180
    f.append(rect(bx1, by1, 70, 45, fill="#eff6ff", stroke="#3b82f6", rx=4))
    f.append(arrow(bx1 + 15, by1 + 22, bx1 + 55, by1 + 22, color="#1d4ed8", sw=2))
    f.append(text(bx1 + 35, by1 - 6, "Усі домени вправо", size=10, color="#1d4ed8", anchor="middle"))

    bx2, by2 = ox - 210, oy + 135
    f.append(rect(bx2, by2, 70, 45, fill="#eff6ff", stroke="#3b82f6", rx=4))
    f.append(arrow(bx2 + 55, by2 + 22, bx2 + 15, by2 + 22, color="#1d4ed8", sw=2))
    f.append(text(bx2 + 35, by2 + 58, "Усі домени вліво", size=10, color="#1d4ed8", anchor="middle"))

    write_svg(os.path.join(IMG_DIR, "ferro-hysteresis.svg"), f, W, H)


# ── Фігура 3: Потенціал Ландау F(P) вище, в точці та нижче Tc ─────────────────
def fig_landau_free_energy():
    W, H = 780, 400
    f = []

    f.append(text(W / 2, 28, "Вільна енергія Ландау F(P) для фазового переходу 2-го роду", size=16, bold=True, color=INK))

    panel_w = 230
    panel_h = 310
    y0 = 55

    panels = [
        ("T > T_C (Пароелектрик)", "Один мінімум при P = 0\nСиметрія збережена", "#f8fafc", "#475569", "gt"),
        ("T = T_C (Точка переходу)", "Пласке дно потенціалу\nКритичні флуктуації", "#fff7ed", "#c2410c", "eq"),
        ("T < T_C (Сегнетоелектрик)", "Двоямний потенціал\nСпонтанне порушення симетрії", "#eff6ff", "#1d4ed8", "lt")
    ]

    for idx, (title_str, sub_str, bg_color, main_color, ptype) in enumerate(panels):
        x0 = 20 + idx * 250
        f.append(rect(x0, y0, panel_w, panel_h, fill=bg_color, stroke=BORDER, rx=8))
        f.append(text(x0 + panel_w / 2, y0 + 22, title_str, size=13, bold=True, color=main_color))
        
        sub_lines = sub_str.split('\n')
        for s_idx, s_line in enumerate(sub_lines):
            f.append(text(x0 + panel_w / 2, y0 + 40 + s_idx * 15, s_line, size=10, color=MUTED))

        ox = x0 + panel_w / 2
        oy = y0 + 230
        pw = 90
        ph = 100

        # Axes inside panel
        f.append(arrow(ox - pw - 10, oy, ox + pw + 10, oy, color="#94a3b8", sw=1.2))
        f.append(text(ox + pw + 14, oy + 4, "P", size=12, bold=True, italic=True, color=INK))

        f.append(arrow(ox, oy + 20, ox, oy - ph - 8, color="#94a3b8", sw=1.2))
        f.append(text(ox - 16, oy - ph - 10, "F(P)", size=11, bold=True, italic=True, color=INK))

        pts = []
        steps = 60
        pw_plot = 75

        if ptype == "gt":
            a = 0.015
            b = 0.000002
            for i in range(steps + 1):
                p_val = -pw_plot + (2 * pw_plot * i / steps)
                f_val = min(115.0, a * (p_val**2) + b * (p_val**4))
                pts.append((ox + p_val, oy - f_val))
            
            d_curve = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
            f.append(path_svg(d_curve, stroke="#475569", sw=2.5))
            f.append(circle(ox, oy, 6, fill="#475569", stroke="#0f172a"))
            f.append(text(ox, oy + 18, "P = 0", size=11, bold=True, color="#475569"))

        elif ptype == "eq":
            b = 0.0000035
            for i in range(steps + 1):
                p_val = -pw_plot + (2 * pw_plot * i / steps)
                f_val = min(115.0, b * (p_val**4))
                pts.append((ox + p_val, oy - f_val))
            
            d_curve = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
            f.append(path_svg(d_curve, stroke="#c2410c", sw=2.5))
            f.append(circle(ox, oy, 6, fill="#c2410c", stroke="#9a3412"))
            f.append(text(ox, oy + 18, "P = 0", size=11, bold=True, color="#c2410c"))

        else: # lt
            p_s = 48
            a = 0.02
            b = a / (p_s**2)
            for i in range(steps + 1):
                p_val = -pw_plot + (2 * pw_plot * i / steps)
                f_val = -0.5 * a * (p_val**2) + 0.25 * b * (p_val**4)
                f_val = min(85.0, f_val)
                pts.append((ox + p_val, oy - f_val - 25))

            d_curve = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
            f.append(path_svg(d_curve, stroke="#2563eb", sw=2.5))

            min_f = -0.5 * a * (p_s**2) + 0.25 * b * (p_s**4)
            min_y = oy - min_f - 25
            f.append(circle(ox - p_s, min_y, 6, fill="#dc2626", stroke="#991b1b"))
            f.append(circle(ox + p_s, min_y, 6, fill="#dc2626", stroke="#991b1b"))

            f.append(text(ox - p_s, min_y + 18, "-P_s", size=11, bold=True, color="#dc2626"))
            f.append(text(ox + p_s, min_y + 18, "+P_s", size=11, bold=True, color="#dc2626"))

            max_y = oy - 25
            f.append(circle(ox, max_y, 5, fill="#94a3b8", stroke="#475569"))
            f.append(text(ox, max_y - 10, "Нестійкий", size=9, color=MUTED))

            f.append(arrow(ox, max_y, ox, min_y, color="#dc2626", sw=1.2))
            f.append(text(ox + 18, (max_y + min_y)/2 + 4, "ΔF", size=11, bold=True, color="#dc2626"))

    write_svg(os.path.join(IMG_DIR, "landau-free-energy.svg"), f, W, H)


# ── Фігура 4: Доменна структура (180° та 90° доменні стінки) ───────────────────
def fig_domain_structure():
    W, H = 780, 420
    f = []

    f.append(text(W / 2, 28, "Сегнетоелектричні домени: 180° та 90° доменні стінки", size=16, bold=True, color=INK))

    panel_w = 360
    panel_h = 340
    y0 = 55

    # Left panel: 180° domains
    f.append(rect(20, y0, panel_w, panel_h, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(20 + panel_w / 2, y0 + 22, "180° Доменні стінки", size=13, bold=True, color="#0f172a"))
    f.append(text(20 + panel_w / 2, y0 + 38, "Антипаралельна поляризація (мінімум E_dep)", size=11, color=MUTED))

    box1_x, box1_y = 50, y0 + 60
    box1_w, box1_h = 300, 220

    f.append(rect(box1_x, box1_y, box1_w, box1_h, fill="#ffffff", stroke="#64748b", sw=1.5))

    strip_w = box1_w / 4
    for idx in range(4):
        sx = box1_x + idx * strip_w
        bg = "#eff6ff" if idx % 2 == 0 else "#f0fdf4"
        f.append(rect(sx, box1_y, strip_w, box1_h, fill=bg, stroke="none"))
        
        if idx > 0:
            f.append(path_svg(f"M {sx} {box1_y} L {sx} {box1_y + box1_h}", stroke="#dc2626", sw=2, dash="3,3"))

        p_color = "#1d4ed8" if idx % 2 == 0 else "#15803d"
        if idx % 2 == 0:
            f.append(arrow(sx + strip_w/2, box1_y + box1_h - 30, sx + strip_w/2, box1_y + 30, color=p_color, sw=2.5))
            f.append(text(sx + strip_w/2, box1_y + box1_h / 2, "+P_s", size=12, bold=True, color=p_color))
        else:
            f.append(arrow(sx + strip_w/2, box1_y + 30, sx + strip_w/2, box1_y + box1_h - 30, color=p_color, sw=2.5))
            f.append(text(sx + strip_w/2, box1_y + box1_h / 2, "-P_s", size=12, bold=True, color=p_color))

    f.append(text(20 + panel_w / 2, y0 + 305, "Товщина стінки ~ 1-2 константи ґратки (вузька)", size=11, italic=True, color="#334155"))


    # Right panel: 90° domains (ferroelastic)
    rx0 = 400
    f.append(rect(rx0, y0, panel_w, panel_h, fill="#eff6ff", stroke="#bfdbfe", rx=8))
    f.append(text(rx0 + panel_w / 2, y0 + 22, "90° Доменні стінки (Тетрагональні)", size=13, bold=True, color="#1e40af"))
    f.append(text(rx0 + panel_w / 2, y0 + 38, "Зняття механічних напружень (пружні)", size=11, color="#1d4ed8"))

    box2_x, box2_y = rx0 + 30, y0 + 60
    box2_w, box2_h = 300, 220

    f.append(rect(box2_x, box2_y, box2_w, box2_h, fill="#ffffff", stroke="#1e3a8a", sw=1.5))

    f.append(path_svg(f"M {box2_x} {box2_y} L {box2_x + box2_w} {box2_y} L {box2_x} {box2_y + box2_h} Z", fill="#eff6ff", stroke="none"))
    f.append(path_svg(f"M {box2_x + box2_w} {box2_y} L {box2_x + box2_w} {box2_y + box2_h} L {box2_x} {box2_y + box2_h} Z", fill="#fff7ed", stroke="none"))
    f.append(path_svg(f"M {box2_x} {box2_y + box2_h} L {box2_x + box2_w} {box2_y}", stroke="#dc2626", sw=2.5))

    f.append(arrow(box2_x + 80, box2_y + 160, box2_x + 80, box2_y + 40, color="#1d4ed8", sw=2.5))
    f.append(text(box2_x + 95, box2_y + 90, "P_1 (↑)", size=13, bold=True, color="#1d4ed8"))

    f.append(arrow(box2_x + 140, box2_y + 150, box2_x + 250, box2_y + 150, color="#c2410c", sw=2.5))
    f.append(text(box2_x + 195, box2_y + 175, "P_2 (→)", size=13, bold=True, color="#c2410c"))

    f.append(text(box2_x + 155, box2_y + 70, "90° Стінка", size=12, bold=True, color="#dc2626"))
    f.append(text(box2_x + 155, box2_y + 86, "(діагональна)", size=10, color="#dc2626"))

    f.append(text(rx0 + panel_w / 2, y0 + 305, "Товщина стінки ~ 5-10 нм (механічна адаптація)", size=11, italic=True, color="#1e40af"))

    write_svg(os.path.join(IMG_DIR, "domain-structure.svg"), f, W, H)


if __name__ == '__main__':
    fig_perovskite_structure()
    fig_ferro_hysteresis()
    fig_landau_free_energy()
    fig_domain_structure()
    print("Всі фігури успішно згенеровано у ./img/")

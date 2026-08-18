# -*- coding: utf-8 -*-
"""Фігури до теми «Кулонівська блокада».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

BORDER = "#cbd5e1"

def path_svg(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d_attr}/>'

def polygon_svg(pts, fill="none", stroke=LINE, sw=1.5):
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'


# ── Фігура 1: Енергетична діаграма одноелектронного тунелювання та кулонівської блокади ──
def fig_coulomb_blockade_energy_diagram():
    W, H = 820, 440
    f = []

    f.append(text(W / 2, 25, "Енергетична діаграма одноелектронного тунелювання та кулонівської блокади", size=15, bold=True, color=INK))

    # Panel A: Blocked State
    pa_x, pa_y, pa_w, pa_h = 20, 45, 380, 375
    f.append(rect(pa_x, pa_y, pa_w, pa_h, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(pa_x + pa_w / 2, pa_y + 24, "А. Блокований стан: e·V_ds < E_c (Струм I = 0)", size=13, bold=True, color="#1e293b"))

    # Source electrode (Left)
    f.append(rect(pa_x + 20, pa_y + 160, 80, 180, fill="#dbeafe", stroke="#3b82f6", rx=4))
    f.append(text(pa_x + 60, pa_y + 190, "Витік (S)", size=12, bold=True, color="#1d4ed8"))
    f.append(line(pa_x + 20, pa_y + 210, pa_x + 100, pa_y + 210, color="#dc2626", sw=2))
    f.append(text(pa_x + 60, pa_y + 203, "μ_S", size=11, bold=True, color="#dc2626"))

    # Tunnel Barrier 1
    f.append(rect(pa_x + 100, pa_y + 100, 35, 240, fill="#fef3c7", stroke="#f59e0b", rx=2))
    f.append(text(pa_x + 117, pa_y + 90, "Бар'єр 1", size=10, bold=True, color="#b45309"))

    # Island (Center)
    f.append(rect(pa_x + 135, pa_y + 120, 110, 220, fill="#f1f5f9", stroke="#64748b", rx=4))
    f.append(text(pa_x + 190, pa_y + 145, "Острівець (I)", size=12, bold=True, color="#334155"))

    # Energy charging gap E_c
    f.append(line(pa_x + 145, pa_y + 250, pa_x + 235, pa_y + 250, color="#2563eb", sw=2, dash="4 2"))
    f.append(text(pa_x + 190, pa_y + 243, "E(n)", size=11, bold=True, color="#2563eb"))
    
    f.append(line(pa_x + 145, pa_y + 180, pa_x + 235, pa_y + 180, color="#7c3aed", sw=2, dash="4 2"))
    f.append(text(pa_x + 190, pa_y + 173, "E(n+1) = E(n) + E_c", size=11, bold=True, color="#7c3aed"))

    # Double arrow for E_c
    f.append(line(pa_x + 220, pa_y + 182, pa_x + 220, pa_y + 248, color="#059669", sw=1.5))
    f.append(text(pa_x + 235, pa_y + 218, "E_c", size=12, bold=True, color="#059669"))

    # Tunnel Barrier 2
    f.append(rect(pa_x + 245, pa_y + 100, 35, 240, fill="#fef3c7", stroke="#f59e0b", rx=2))
    f.append(text(pa_x + 262, pa_y + 90, "Бар'єр 2", size=10, bold=True, color="#b45309"))

    # Drain electrode (Right)
    f.append(rect(pa_x + 280, pa_y + 190, 80, 150, fill="#dbeafe", stroke="#3b82f6", rx=4))
    f.append(text(pa_x + 320, pa_y + 220, "Сток (D)", size=12, bold=True, color="#1d4ed8"))
    f.append(line(pa_x + 280, pa_y + 230, pa_x + 360, pa_y + 230, color="#dc2626", sw=2))
    f.append(text(pa_x + 320, pa_y + 223, "μ_D", size=11, bold=True, color="#dc2626"))

    # Transport window e*V_ds
    f.append(line(pa_x + 20, pa_y + 210, pa_x + 360, pa_y + 210, color="#cbd5e1", sw=1, dash="2 2"))
    f.append(line(pa_x + 280, pa_y + 230, pa_x + 360, pa_y + 230, color="#cbd5e1", sw=1, dash="2 2"))
    f.append(text(pa_x + 190, pa_y + 340, "Зарядний рівень E(n+1) вище μ_S", size=11, italic=True, color="#dc2626"))
    f.append(text(pa_x + 190, pa_y + 358, "Тунелювання заборонене за енергією", size=11, bold=True, color="#dc2626"))


    # Panel B: Conducting State
    pb_x, pb_y, pb_w, pb_h = 420, 45, 380, 375
    f.append(rect(pb_x, pb_y, pb_w, pb_h, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(pb_x + pb_w / 2, pb_y + 24, "Б. Відкритий стан: e·V_ds > E_c (Струм I > 0)", size=13, bold=True, color="#1e293b"))

    # Source electrode (Left) - elevated bias
    f.append(rect(pb_x + 20, pb_y + 130, 80, 210, fill="#dbeafe", stroke="#3b82f6", rx=4))
    f.append(text(pb_x + 60, pb_y + 160, "Витік (S)", size=12, bold=True, color="#1d4ed8"))
    f.append(line(pb_x + 20, pb_y + 170, pb_x + 100, pb_y + 170, color="#dc2626", sw=2))
    f.append(text(pb_x + 60, pb_y + 163, "μ_S", size=11, bold=True, color="#dc2626"))

    # Tunnel Barrier 1
    f.append(rect(pb_x + 100, pb_y + 100, 35, 240, fill="#fef3c7", stroke="#f59e0b", rx=2))
    f.append(text(pb_x + 117, pb_y + 90, "Бар'єр 1", size=10, bold=True, color="#b45309"))

    # Island (Center)
    f.append(rect(pb_x + 135, pb_y + 120, 110, 220, fill="#f1f5f9", stroke="#64748b", rx=4))
    f.append(text(pb_x + 190, pb_y + 145, "Острівець (I)", size=12, bold=True, color="#334155"))

    # Energy level inside window
    f.append(line(pb_x + 145, pb_y + 200, pb_x + 235, pb_y + 200, color="#16a34a", sw=2.5))
    f.append(text(pb_x + 190, pb_y + 193, "E(n+1) у вікні", size=11, bold=True, color="#16a34a"))

    # Electron tunneling arrow
    f.append(line(pb_x + 60, pb_y + 200, pb_x + 140, pb_y + 200, color="#2563eb", sw=2))
    f.append(text(pb_x + 95, pb_y + 193, "e⁻ →", size=12, bold=True, color="#2563eb"))

    f.append(line(pb_x + 240, pb_y + 200, pb_x + 310, pb_y + 200, color="#2563eb", sw=2))
    f.append(text(pb_x + 275, pb_y + 193, "→ e⁻", size=12, bold=True, color="#2563eb"))

    # Tunnel Barrier 2
    f.append(rect(pb_x + 245, pb_y + 100, 35, 240, fill="#fef3c7", stroke="#f59e0b", rx=2))
    f.append(text(pb_x + 262, pb_y + 90, "Бар'єр 2", size=10, bold=True, color="#b45309"))

    # Drain electrode (Right) - lower bias
    f.append(rect(pb_x + 280, pb_y + 220, 80, 120, fill="#dbeafe", stroke="#3b82f6", rx=4))
    f.append(text(pb_x + 320, pb_y + 250, "Сток (D)", size=12, bold=True, color="#1d4ed8"))
    f.append(line(pb_x + 280, pb_y + 260, pb_x + 360, pb_y + 260, color="#dc2626", sw=2))
    f.append(text(pb_x + 320, pb_y + 253, "μ_D", size=11, bold=True, color="#dc2626"))

    # Transport window bracket
    f.append(text(pb_x + 190, pb_y + 340, "μ_S > E(n+1) > μ_D (Транспортне вікно)", size=11, italic=True, color="#16a34a"))
    f.append(text(pb_x + 190, pb_y + 358, "Поодиноке тунелювання дозволене", size=11, bold=True, color="#16a34a"))

    with open(os.path.join(IMG_DIR, "coulomb-blockade-energy-diagram.svg"), "w", encoding="utf-8") as fp:
        fp.write('<?xml version="1.0" encoding="utf-8"?>\n')
        fp.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (W, H, W, H))
        fp.write('<rect width="100%%" height="100%%" fill="%s"/>\n' % BG)
        fp.write("\n".join(f))
        fp.write("\n</svg>\n")


# ── Фігура 2: Еквівалентна схема SET та параболи електростатичної енергії ──
def fig_set_circuit_and_parabolas():
    W, H = 820, 450
    f = []

    f.append(text(W / 2, 25, "Еквівалентна електрична схема SET та енергетичні параболи", size=15, bold=True, color=INK))

    # Panel A: SET Circuit
    pa_x, pa_y, pa_w, pa_h = 20, 45, 380, 385
    f.append(rect(pa_x, pa_y, pa_w, pa_h, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(pa_x + pa_w / 2, pa_y + 24, "А. Еквівалентна схема транзистора (SET)", size=13, bold=True, color="#1e293b"))

    # Island box
    f.append(rect(pa_x + 140, pa_y + 150, 100, 70, fill="#e0e7ff", stroke="#4338ca", rx=6))
    f.append(text(pa_x + 190, pa_y + 180, "Острівець (I)", size=13, bold=True, color="#3730a3"))
    f.append(text(pa_x + 190, pa_y + 200, "Заряд Q = n·e", size=11, color="#4338ca"))

    # Source terminal (Left)
    f.append(line(pa_x + 30, pa_y + 185, pa_x + 80, pa_y + 185, color=LINE, sw=2))
    f.append(text(pa_x + 45, pa_y + 175, "Витік (S)", size=11, bold=True, color="#1d4ed8"))
    
    # Source tunnel junction (C_s, R_s)
    f.append(rect(pa_x + 80, pa_y + 165, 60, 40, fill="#fef3c7", stroke="#d97706", rx=4))
    f.append(text(pa_x + 110, pa_y + 182, "C_s | R_s", size=11, bold=True, color="#b45309"))

    # Drain tunnel junction (C_d, R_d)
    f.append(rect(pa_x + 240, pa_y + 165, 60, 40, fill="#fef3c7", stroke="#d97706", rx=4))
    f.append(text(pa_x + 270, pa_y + 182, "C_d | R_d", size=11, bold=True, color="#b45309"))

    # Drain terminal (Right)
    f.append(line(pa_x + 300, pa_y + 185, pa_x + 350, pa_y + 185, color=LINE, sw=2))
    f.append(text(pa_x + 335, pa_y + 175, "Сток (D)", size=11, bold=True, color="#1d4ed8"))

    # Gate capacitor (Bottom)
    f.append(line(pa_x + 190, pa_y + 220, pa_x + 190, pa_y + 270, color=LINE, sw=2))
    f.append(rect(pa_x + 165, pa_y + 270, 50, 30, fill="#dcfce7", stroke="#16a34a", rx=4))
    f.append(text(pa_x + 190, pa_y + 290, "C_g", size=11, bold=True, color="#15803d"))
    f.append(line(pa_x + 190, pa_y + 300, pa_x + 190, pa_y + 340, color=LINE, sw=2))
    f.append(text(pa_x + 190, pa_y + 360, "Затвор V_g", size=12, bold=True, color="#15803d"))

    # Formula box inside panel A
    f.append(rect(pa_x + 35, pa_y + 310, 110, 45, fill="#ffffff", stroke="#cbd5e1", rx=4))
    f.append(text(pa_x + 90, pa_y + 328, "C_Σ = C_s + C_d + C_g", size=10, bold=True, color="#334155"))
    f.append(text(pa_x + 90, pa_y + 345, "E_c = e² / (2·C_Σ)", size=10, bold=True, color="#059669"))


    # Panel B: Energy Parabolas
    pb_x, pb_y, pb_w, pb_h = 420, 45, 380, 385
    f.append(rect(pb_x, pb_y, pb_w, pb_h, fill="#f8fafc", stroke=BORDER, rx=8))
    f.append(text(pb_x + pb_w / 2, pb_y + 24, "Б. Зарядні параболи E(n) від заряду затвора", size=13, bold=True, color="#1e293b"))

    # Axes
    ox, oy = pb_x + 40, pb_y + 330
    f.append(line(ox, oy, ox + 280, oy, color=LINE, sw=1.5)) # X axis
    f.append(line(ox, oy, ox, oy - 260, color=LINE, sw=1.5)) # Y axis
    f.append(text(ox + 240, oy + 22, "n_g = C_g·V_g / e", size=11, bold=True, color=INK))
    f.append(text(ox - 10, oy - 270, "E(n)", size=11, bold=True, color=INK))

    # Ticks on X axis: 0, 0.5, 1.0, 1.5, 2.0
    x_0 = ox + 40
    x_05 = ox + 100
    x_10 = ox + 160
    x_15 = ox + 220
    x_20 = ox + 280

    for x_val, label in [(x_0, "0"), (x_05, "0.5"), (x_10, "1.0"), (x_15, "1.5"), (x_20, "2.0")]:
        f.append(line(x_val, oy - 4, x_val, oy + 4, color=LINE, sw=1))
        f.append(text(x_val, oy + 18, label, size=10, color="#475569"))

    # Parabola n = 0
    p0_pts = []
    for step in range(0, 101):
        ng = step / 50.0 # 0 to 2
        px = ox + 40 + ng * 120
        py = oy - (ng ** 2) * 120
        if py >= oy - 260:
            p0_pts.append(f"{px:.1f},{py:.1f}")
    f.append(path_svg("M " + " L ".join(p0_pts), fill="none", stroke="#2563eb", sw=2))
    f.append(text(ox + 35, oy - 20, "n = 0", size=11, bold=True, color="#2563eb"))

    # Parabola n = 1
    p1_pts = []
    for step in range(-40, 101):
        ng = step / 50.0 # -0.8 to 2.2
        px = ox + 40 + ng * 120
        py = oy - ((1.0 - ng) ** 2) * 120
        if oy - 260 <= py <= oy:
            p1_pts.append(f"{px:.1f},{py:.1f}")
    f.append(path_svg("M " + " L ".join(p1_pts), fill="none", stroke="#16a34a", sw=2))
    f.append(text(ox + 160, oy - 20, "n = 1", size=11, bold=True, color="#16a34a"))

    # Parabola n = 2
    p2_pts = []
    for step in range(10, 141):
        ng = step / 50.0
        px = ox + 40 + ng * 120
        py = oy - ((2.0 - ng) ** 2) * 120
        if oy - 260 <= py <= oy:
            p2_pts.append(f"{px:.1f},{py:.1f}")
    f.append(path_svg("M " + " L ".join(p2_pts), fill="none", stroke="#dc2626", sw=2))
    f.append(text(ox + 280, oy - 20, "n = 2", size=11, bold=True, color="#dc2626"))

    # Intersection points (Degeneracy points)
    f.append(circle(x_05, oy - 30, 4, fill="#ea580c", stroke="#ffffff", sw=1))
    f.append(line(x_05, oy, x_05, oy - 30, color="#ea580c", sw=1, dash="2 2"))
    f.append(text(x_05, oy - 42, "Виродження", size=10, bold=True, color="#ea580c"))
    f.append(text(x_05, oy - 55, "E(0) = E(1)", size=10, color="#ea580c"))

    f.append(circle(x_15, oy - 30, 4, fill="#ea580c", stroke="#ffffff", sw=1))
    f.append(line(x_15, oy, x_15, oy - 30, color="#ea580c", sw=1, dash="2 2"))
    f.append(text(x_15, oy - 42, "Виродження", size=10, bold=True, color="#ea580c"))
    f.append(text(x_15, oy - 55, "E(1) = E(2)", size=10, color="#ea580c"))

    # Blockade regions indicators
    f.append(text(x_0, oy - 150, "Блокада n=0", size=10, italic=True, color="#2563eb"))
    f.append(text(x_10, oy - 150, "Блокада n=1", size=10, italic=True, color="#16a34a"))

    with open(os.path.join(IMG_DIR, "set-circuit-and-parabolas.svg"), "w", encoding="utf-8") as fp:
        fp.write('<?xml version="1.0" encoding="utf-8"?>\n')
        fp.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (W, H, W, H))
        fp.write('<rect width="100%%" height="100%%" fill="%s"/>\n' % BG)
        fp.write("\n".join(f))
        fp.write("\n</svg>\n")


# ── Фігура 3: Двовимірна діаграма стабільності заряду (кулонівські ромби) ──
def fig_coulomb_diamonds():
    W, H = 820, 460
    f = []

    f.append(text(W / 2, 25, "Діаграма стабільності заряду: кулонівські ромби у координатах (V_g, V_ds)", size=15, bold=True, color=INK))

    # Main Stability Diagram Box
    cx, cy, cw, ch = 50, 50, 720, 370
    f.append(rect(cx, cy, cw, ch, fill="#f8fafc", stroke=BORDER, rx=8))

    # Axes
    ox, oy = cx + 80, cy + ch / 2 # Center Y for V_ds = 0
    f.append(line(ox - 30, oy, ox + 580, oy, color=LINE, sw=1.5)) # V_g axis
    f.append(line(ox, cy + 30, ox, cy + ch - 30, color=LINE, sw=1.5)) # V_ds axis

    f.append(text(ox + 600, oy + 4, "V_g", size=12, bold=True, color=INK))
    f.append(text(ox - 10, cy + 22, "V_ds", size=12, bold=True, color=INK))

    half_h = 70
    half_w = 90

    diamonds = [
        (ox + 80, "n = 0", "#dbeafe", "#2563eb"),
        (ox + 260, "n = 1", "#dcfce7", "#16a34a"),
        (ox + 440, "n = 2", "#fee2e2", "#dc2626")
    ]

    # Draw Diamonds
    for xc, label, fill_col, text_col in diamonds:
        pts = f"{xc - half_w:.1f},{oy:.1f} {xc:.1f},{oy - half_h:.1f} {xc + half_w:.1f},{oy:.1f} {xc:.1f},{oy + half_h:.1f}"
        f.append(polygon_svg(pts, fill=fill_col, stroke=text_col, sw=2))
        f.append(text(xc, oy - 25, label, size=13, bold=True, color=text_col))
        f.append(text(xc, oy + 25, "I = 0 (Блокада)", size=10, bold=True, color=text_col))

    # Conducting regions labels
    f.append(text(ox + 80, oy - 110, "Провідність (I > 0)", size=11, bold=True, color="#475569"))
    f.append(text(ox + 260, oy - 110, "Провідність (I > 0)", size=11, bold=True, color="#475569"))
    f.append(text(ox + 80, oy + 120, "Провідність (I < 0)", size=11, bold=True, color="#475569"))
    f.append(text(ox + 260, oy + 120, "Провідність (I < 0)", size=11, bold=True, color="#475569"))

    # Dimension indicators
    f.append(line(ox + 80, oy + 35, ox + 260, oy + 35, color="#059669", sw=1.5))
    f.append(text(ox + 170, oy + 50, "ΔV_g = e / C_g", size=11, bold=True, color="#059669"))

    # Height dimension at left margin (x = ox - 25)
    xl = ox - 25
    f.append(line(xl, oy - half_h, xl, oy + half_h, color="#7c3aed", sw=1.5, dash="3 2"))
    f.append(text(xl - 35, oy - 5, "ΔV_ds = e / C_Σ", size=10, bold=True, color="#7c3aed"))

    # Slopes annotation (above diamond top vertices)
    f.append(text(ox + 170, oy - 80, "Схил: C_g / (C_Σ - C_d)", size=9, bold=True, color="#334155"))
    f.append(text(ox + 350, oy - 80, "Схил: -C_g / C_d", size=9, bold=True, color="#334155"))

    # Degeneracy points (Coulomb oscillation peaks) on V_g axis at V_ds = 0
    for x_deg in [ox - 10, ox + 170, ox + 350, ox + 530]:
        f.append(circle(x_deg, oy, 4, fill="#f59e0b", stroke="#ffffff", sw=1))
    
    f.append(text(ox + 170, oy + 15, "n_g = 0.5", size=10, bold=True, color="#d97706"))

    with open(os.path.join(IMG_DIR, "coulomb-diamonds.svg"), "w", encoding="utf-8") as fp:
        fp.write('<?xml version="1.0" encoding="utf-8"?>\n')
        fp.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (W, H, W, H))
        fp.write('<rect width="100%%" height="100%%" fill="%s"/>\n' % BG)
        fp.write("\n".join(f))
        fp.write("\n</svg>\n")


if __name__ == "__main__":
    fig_coulomb_blockade_energy_diagram()
    fig_set_circuit_and_parabolas()
    fig_coulomb_diamonds()
    print("Успішно згенеровано 3 SVG фігури у", IMG_DIR)

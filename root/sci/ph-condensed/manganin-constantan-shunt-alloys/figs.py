# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

img_dir = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(img_dir, exist_ok=True)

# 1. TCR Parabola Comparison (Manganin vs Constantan vs Copper)
def gen_tcr_parabola():
    w, h = 680, 420
    frags = []
    
    frags.append(text(w / 2, 28, "Температурна залежність опору манганіну, константану та міді", size=15, bold=True))
    
    ox, oy = 85, 340
    ax_w, ax_h = 540, 270
    frags.append(line(ox, oy, ox + ax_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - ax_h, color=LINE, sw=2))
    
    frags.append(text(ox + ax_w / 2, oy + 42, "Температура T (°C)", size=13, bold=True))
    frags.append(text(ox - 55, oy - ax_h / 2, "Відносний опір R(T) / R(20°C)", size=12, bold=True, anchor="middle"))
    
    def t_to_x(t):
        return ox + (t + 50) * (ax_w / 200.0)
    
    ticks_t = [-50, 0, 20, 50, 100, 150]
    for t_val in ticks_t:
        tx = t_to_x(t_val)
        frags.append(line(tx, oy, tx, oy + 5, color=MUTED))
        frags.append(text(tx, oy + 22, "%d°C" % t_val, size=11, color=MUTED))
    
    # Reference 1.000 line
    frags.append(line(ox, oy - 140, ox + ax_w, oy - 140, color="#d5d8dc", sw=1.2, dash="4,4"))
    frags.append(text(ox - 30, oy - 136, "1.0000", size=11, color=MUTED))
    frags.append(text(ox - 30, oy - 220, "1.0020", size=10, color=MUTED))
    frags.append(text(ox - 30, oy - 60, "0.9980", size=10, color=MUTED))
    
    # 1. Copper curve (steep positive slope: +3900 ppm/K)
    pts_cu = [(t_to_x(-50), oy - 30), (t_to_x(-10), oy - 90), (t_to_x(20), oy - 140), (t_to_x(60), oy - 210), (t_to_x(90), oy - 260)]
    path_cu = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_cu)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_cu, NEG))
    frags.append(text(t_to_x(55), oy - 225, "Мідь (α = +3900 ppm/K)", size=11, color=NEG, bold=True))
    
    # 2. Constantan curve (linear slightly negative TCR ~ -30 ppm/K)
    pts_con = [(t_to_x(-50), oy - 120), (t_to_x(20), oy - 140), (t_to_x(150), oy - 175)]
    path_con = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_con)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,3"/>' % (path_con, FIELD))
    frags.append(text(t_to_x(90), oy - 180, "Константан (α ≈ -30 ppm/K)", size=11, color=FIELD, bold=True))
    
    # 3. Manganin curve (parabola with peak at 20°C)
    pts_mang = []
    for t_val in range(-50, 151, 5):
        tx = t_to_x(t_val)
        # Parabola formula dy = beta * (T-20)^2
        dy = 4e-7 * ((t_val - 20)**2) * 500000.0
        ty = (oy - 140) + dy
        pts_mang.append((tx, ty))
    path_mang = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_mang)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_mang, POS))
    frags.append(text(t_to_x(20), oy - 158, "Манганін (вершина при T = 20°C, α = 0)", size=11, color=POS, bold=True))
    
    # Tangent at peak
    frags.append(line(t_to_x(-15), oy - 140, t_to_x(55), oy - 140, color=POS, sw=1.5, dash="2,2"))
    
    # Explanatory callout boxes
    frags.append(textbox(140, 95, "Манганін (CuMn12Ni2):\nВ області 15–25 °C α ≈ 0 ppm/K\nВершина параболи: T_max = 20 °C", size=10, fill="#fdfefe", stroke=POS)[0])
    frags.append(textbox(490, 95, "Константан (CuNi44):\nПлаский опір в інтервалі\nвід -100 °C до +400 °C", size=10, fill="#fdfefe", stroke=FIELD)[0])

    render(os.path.join(img_dir, "tcr-parabola-manganin-constantan.svg"), w, h, *frags)

# 2. Thermoelectric EMF in Copper-Alloy Junctions
def gen_thermoelectric_emf():
    w, h = 680, 360
    frags = []
    
    frags.append(text(w / 2, 26, "Термо-ЕРС у контактах міді з константаном та манганіном", size=15, bold=True))
    
    # Panel 1: Copper-Constantan (High Thermal EMF)
    frags.append(rect(30, 55, 300, 270, fill="#fff9f9", stroke=NEG, sw=1.5, rx=5))
    frags.append(text(180, 78, "Мідь — Константан (Cu-CuNi44)", size=13, color=NEG, bold=True))
    
    # Shunt graphic: Cu leads + Constantan body
    frags.append(rect(50, 130, 60, 40, fill="#e67e22", stroke="#d35400", sw=1.5)) # Cu left
    frags.append(text(80, 155, "Cu", size=12, color="#ffffff", bold=True))
    
    frags.append(rect(110, 130, 140, 40, fill="#95a5a6", stroke="#7f8c8d", sw=1.5)) # Constantan
    frags.append(text(180, 155, "Константан", size=12, color="#ffffff", bold=True))
    
    frags.append(rect(250, 130, 60, 40, fill="#e67e22", stroke="#d35400", sw=1.5)) # Cu right
    frags.append(text(280, 155, "Cu", size=12, color="#ffffff", bold=True))
    
    # Thermal gradient
    frags.append(text(110, 115, "T₁ = 50°C", size=11, color=NEG, bold=True))
    frags.append(text(250, 115, "T₂ = 20°C", size=11, color=FIELD, bold=True))
    frags.append(line(110, 185, 250, 185, color=NEG, sw=1.5, dash="3,3"))
    frags.append(text(180, 202, "ΔT = 30 K", size=11, color=NEG, bold=True))
    
    # Voltage calculation box
    box_neg = textbox(180, 265, "Коефіцієнт Зеєбека: S = -43 мкВ/К\nПаразитна термо-ЕРС:\nV_emf = S · ΔT = -1290 мкВ\nПохибка постійного струму: ВЕЛИКА!", size=10, fill="#ffffff", stroke=NEG)[0]
    frags.append(box_neg)
    
    # Panel 2: Copper-Manganin (Low Thermal EMF)
    frags.append(rect(350, 55, 300, 270, fill="#f4fbf7", stroke=POS, sw=1.5, rx=5))
    frags.append(text(500, 78, "Мідь — Манганін (Cu-CuMn12Ni2)", size=13, color=POS, bold=True))
    
    # Shunt graphic: Cu leads + Manganin body
    frags.append(rect(370, 130, 60, 40, fill="#e67e22", stroke="#d35400", sw=1.5)) # Cu left
    frags.append(text(400, 155, "Cu", size=12, color="#ffffff", bold=True))
    
    frags.append(rect(430, 130, 140, 40, fill="#27ae60", stroke="#1e8449", sw=1.5)) # Manganin
    frags.append(text(500, 155, "Манганін", size=12, color="#ffffff", bold=True))
    
    frags.append(rect(570, 130, 60, 40, fill="#e67e22", stroke="#d35400", sw=1.5)) # Cu right
    frags.append(text(600, 155, "Cu", size=12, color="#ffffff", bold=True))
    
    # Thermal gradient
    frags.append(text(430, 115, "T₁ = 50°C", size=11, color=NEG, bold=True))
    frags.append(text(570, 115, "T₂ = 20°C", size=11, color=FIELD, bold=True))
    frags.append(line(430, 185, 570, 185, color=NEG, sw=1.5, dash="3,3"))
    frags.append(text(500, 202, "ΔT = 30 K", size=11, color=NEG, bold=True))
    
    # Voltage calculation box
    box_pos = textbox(500, 265, "Коефіцієнт Зеєбека: S = +1.5 мкВ/К\nПаразитна термо-ЕРС:\nV_emf = S · ΔT = +45 мкВ\nЗниження похибки у 28 разів!", size=10, fill="#ffffff", stroke=POS)[0]
    frags.append(box_pos)

    render(os.path.join(img_dir, "thermoelectric-emf-copper-junction.svg"), w, h, *frags)

# 3. Thermal Aging and Lattice Relaxation
def gen_thermal_aging():
    w, h = 680, 380
    frags = []
    
    frags.append(text(w / 2, 26, "Етапи штучного термічного старіння прецизійних сплавів", size=15, bold=True))
    
    # 4 Steps of processing
    step_w = 140
    gap = 20
    start_x = 40
    y_top = 60
    
    steps_data = [
        ("1. Деформований стан", "Загартовані вакансії\nВнутрішні напруження\nДрейф > 50 ppm/рік", NEG, "#fdedec"),
        ("2. Високотемп. відпал", "350–400 °C (2–4 год)\nРекомбінація вакансій\nЗняття напружень", FIELD, "#ebf5fb"),
        ("3. Низькотемп. старіння", "120–140 °C (24–48 год)\nБлижнє впорядкування\nУтворення К-стану", "#8e44ad", "#f4ecf7"),
        ("4. Стабілізований стан", "Рівноважна ґратка\nМінімальний дрейф\n< 0.5 ppm/рік", POS, "#eafaf1")
    ]
    
    for i, (stitle, sdesc, scolor, sbg) in enumerate(steps_data):
        sx = start_x + i * (step_w + gap)
        frags.append(rect(sx, y_top, step_w, 140, fill=sbg, stroke=scolor, sw=1.8, rx=5))
        frags.append(text(sx + step_w / 2, y_top + 22, stitle, size=11, color=scolor, bold=True))
        frags.append(textbox(sx + step_w / 2, y_top + 80, sdesc, size=9.5, fill=sbg, stroke=scolor)[0])
        
        if i < 3:
            # Arrow
            ax = sx + step_w + 3
            frags.append(line(ax, y_top + 70, ax + gap - 6, y_top + 70, color=LINE, sw=2))
            frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (
                ax + gap - 2, y_top + 70, ax + gap - 8, y_top + 65, ax + gap - 8, y_top + 75, LINE
            ))
            
    # Bottom Graph: Resistance Drift over Time
    ox, oy = 80, 340
    gw, gh = 520, 90
    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))
    
    frags.append(text(ox + gw / 2, oy + 25, "Час витримування t (години)", size=11, bold=True))
    frags.append(text(ox - 45, oy - gh / 2, "Дрейф ΔR/R", size=11, bold=True, anchor="middle"))
    
    # Unaged drift vs Aged drift
    pts_unaged = [(ox, oy - 80), (ox + 150, oy - 65), (ox + 300, oy - 45), (ox + 500, oy - 30)]
    path_unaged = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_unaged)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,3"/>' % (path_unaged, NEG))
    frags.append(text(ox + 350, oy - 48, "Без старіння (безперервний дрейф)", size=10, color=NEG, bold=True))
    
    pts_aged = [(ox, oy - 80), (ox + 100, oy - 20), (ox + 200, oy - 5), (ox + 500, oy - 3)]
    path_aged = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_aged)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_aged, POS))
    frags.append(text(ox + 220, oy - 12, "Після старіння (вийшов на плато рівноваги)", size=10, color=POS, bold=True))

    render(os.path.join(img_dir, "thermal-aging-lattice-relaxation.svg"), w, h, *frags)

if __name__ == "__main__":
    gen_tcr_parabola()
    gen_thermoelectric_emf()
    gen_thermal_aging()
    print("Generated 3 figures successfully.")

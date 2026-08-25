# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/ from book/physics/condensed-matter-physics/temperature-coefficient-alloys/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

img_dir = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(img_dir, exist_ok=True)

# 1. TCR Parabola Comparison
def gen_tcr_parabola_comparison():
    w, h = 660, 420
    frags = []
    
    frags.append(text(w / 2, 28, "Температурна залежність опору прецизійних сплавів та міді", size=16, bold=True))
    
    ox, oy = 80, 340
    ax_w, ax_h = 530, 270
    frags.append(line(ox, oy, ox + ax_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - ax_h, color=LINE, sw=2))
    
    frags.append(text(ox + ax_w / 2, oy + 42, "Температура T (°C)", size=13, bold=True))
    frags.append(text(ox - 52, oy - ax_h / 2, "Відносний опір R(T) / R(20°C)", size=12, bold=True, anchor="middle"))
    
    # Temperature ticks: -50, 0, 20, 50, 100, 150
    def t_to_x(t):
        return ox + (t + 50) * (ax_w / 200.0)
    
    ticks_t = [-50, 0, 20, 50, 100, 150]
    for t_val in ticks_t:
        tx = t_to_x(t_val)
        frags.append(line(tx, oy, tx, oy + 5, color=MUTED))
        frags.append(text(tx, oy + 20, "%d°C" % t_val, size=11, color=MUTED))
    
    # Grid lines
    frags.append(line(ox, oy - 120, ox + ax_w, oy - 120, color="#e5e7e9", sw=1.2, dash="4,4"))
    frags.append(text(ox - 25, oy - 116, "1.00", size=11, color=MUTED))
    
    # 1. Copper curve (steep positive slope: +3900 ppm/K)
    pts_cu = [(t_to_x(-50), oy - 20), (t_to_x(0), oy - 90), (t_to_x(20), oy - 120), (t_to_x(60), oy - 180), (t_to_x(100), oy - 245)]
    path_cu = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_cu)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_cu, NEG))
    frags.append(text(t_to_x(62), oy - 190, "Мідь (α = +3900 ppm/K)", size=11, color=NEG, bold=True))
    
    # 2. Constantan curve (linear negative TCR ~ -30 ppm/K)
    pts_con = [(t_to_x(-50), oy - 110), (t_to_x(20), oy - 120), (t_to_x(150), oy - 140)]
    path_con = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_con)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,3"/>' % (path_con, FIELD))
    frags.append(text(t_to_x(110), oy - 150, "Константан (α ≈ -30 ppm/K)", size=11, color=FIELD, bold=True))
    
    # 3. Manganin curve (parabola peak at 20°C)
    pts_mang = []
    for t_val in range(-50, 151, 10):
        tx = t_to_x(t_val)
        dy = 4e-7 * ((t_val - 20)**2) * 500000.0
        ty = (oy - 120) + dy
        pts_mang.append((tx, ty))
    path_mang = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_mang)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_mang, POS))
    frags.append(text(t_to_x(25), oy - 135, "Манганін (dR/dT = 0 при 20°C)", size=11, color=POS, bold=True))
    
    # Tangent line at peak
    frags.append(line(t_to_x(-10), oy - 120, t_to_x(50), oy - 120, color=POS, sw=1.5, dash="2,2"))
    
    # 4. Karma / Evanohm (K-state, flat curve: < 1 ppm/K)
    pts_karma = [(t_to_x(-50), oy - 122), (t_to_x(20), oy - 120), (t_to_x(150), oy - 121)]
    path_karma = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_karma)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_karma, "#8e44ad"))
    frags.append(text(t_to_x(80), oy - 105, "Карма / Еваном (К-стан, |α| < 1 ppm/K)", size=11, color="#8e44ad", bold=True))
    
    # Explanatory callout boxes
    frags.append(textbox(150, 90, "Параболічна вершина манганіну:\nВ інтервалі 15–30 °C\nТКО не перевищує ±1 ppm/K", size=10, fill="#fdfefe", stroke=POS)[0])
    frags.append(textbox(510, 90, "Термостабілізована Карма:\nАтомне впорядкування (К-стан)\nрозширює плато від -50 до +150 °C", size=10, fill="#fdfefe", stroke="#8e44ad")[0])

    render(os.path.join(img_dir, "tcr-parabola-comparison.svg"), w, h, *frags)

# 2. Mott s-d Scattering and Mooij Correlation
def gen_mott_mooij_scattering():
    w, h = 680, 390
    frags = []
    
    frags.append(text(w / 2, 26, "Механізми компенсації: модель Мотта та кореляція Муя", size=15, bold=True))
    
    # Left Panel: Mott s-d scattering
    frags.append(rect(30, 55, 300, 265, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(180, 78, "s-d розсіяння Мотта", size=13, color=INK, bold=True))
    
    ox1, oy1 = 60, 280
    frags.append(line(ox1, oy1, ox1 + 240, oy1, color=LINE, sw=1.5))
    frags.append(line(ox1, oy1, ox1, oy1 - 180, color=LINE, sw=1.5))
    frags.append(text(ox1 + 120, oy1 + 22, "Енергія E", size=11, bold=True))
    frags.append(text(ox1 - 25, oy1 - 100, "Густина станів N(E)", size=11, bold=True, anchor="middle"))
    
    pts_dos = [(ox1 + 20, oy1 - 20), (ox1 + 75, oy1 - 150), (ox1 + 140, oy1 - 120), (ox1 + 220, oy1 - 30)]
    path_dos = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_dos)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_dos, POS))
    frags.append(text(ox1 + 75, oy1 - 160, "d-зона", size=10, color=POS, bold=True))
    
    ef_x = ox1 + 135
    frags.append(line(ef_x, oy1, ef_x, oy1 - 170, color=NEG, sw=1.5, dash="4,4"))
    frags.append(text(ef_x, oy1 - 175, "E_F", size=11, color=NEG, bold=True))
    frags.append(text(ef_x + 10, oy1 - 120, "d²N/dE² < 0\n(розмиття знижує\nрозсіяння з T)", size=10, color=NEG))
    
    # Right Panel: Mooij correlation graph
    frags.append(rect(350, 55, 300, 265, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(500, 78, "Правило / кореляція Муя", size=13, color=INK, bold=True))
    
    ox2, oy2 = 390, 280
    frags.append(line(ox2, oy2, ox2 + 240, oy2, color=LINE, sw=1.5))
    frags.append(line(ox2, oy2 - 100, ox2 + 240, oy2 - 100, color="#bdc3c7", sw=1.5, dash="4,4"))
    frags.append(line(ox2, oy2, ox2, oy2 - 180, color=LINE, sw=1.5))
    
    frags.append(text(ox2 + 120, oy2 + 22, "Питомий опір ρ₀ (мкОм·см)", size=11, bold=True))
    frags.append(text(ox2 - 25, oy2 - 90, "ТКО α", size=11, bold=True, anchor="middle"))
    frags.append(text(ox2 + 245, oy2 - 96, "α = 0", size=10, color=MUTED))
    
    pts_mooij = [(ox2 + 20, oy2 - 160), (ox2 + 80, oy2 - 130), (ox2 + 140, oy2 - 100), (ox2 + 200, oy2 - 60), (ox2 + 230, oy2 - 40)]
    path_mooij = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_mooij)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_mooij, FIELD))
    
    frags.append(line(ox2 + 140, oy2, ox2 + 140, oy2 - 180, color=POS, sw=1.5, dash="3,3"))
    frags.append(text(ox2 + 140, oy2 - 185, "ρ_c ≈ 130 мкОм·см", size=10, color=POS, bold=True))
    frags.append(text(ox2 + 145, oy2 - 30, "Межа Іоффе — Регеля\n(k_F · ℓ ~ 1)", size=10, color=POS))
    
    frags.append(fitbox(50, 332, 580, 48, "Механізм компенсації: зростання фононного опору компенсується квантовим приглушенням s-d розсіяння Мотта та локалізаційними ефектами Муя у сильнонеупорядкованих сплавах.", size=11, fill="#eafaf1", stroke=POS, bold=True))

    render(os.path.join(img_dir, "mott-mooij-scattering.svg"), w, h, *frags)

# 3. Kelvin Shunt Construction & Thermo-EMF
def gen_kelvin_shunt_construction():
    w, h = 680, 380
    frags = []
    
    frags.append(text(w / 2, 26, "Конструкція 4-затискачного прецизійного шунта та компенсація термо-РСУ", size=15, bold=True))
    
    frags.append(rect(60, 100, 120, 110, fill="#edbb99", stroke="#d35400", sw=2, rx=4))
    frags.append(text(120, 145, "Струмовий затискач C1\n(Мідний блок)", size=11, color="#78281f", bold=True))
    
    frags.append(rect(500, 100, 120, 110, fill="#edbb99", stroke="#d35400", sw=2, rx=4))
    frags.append(text(560, 145, "Струмовий затискач C2\n(Мідний блок)", size=11, color="#78281f", bold=True))
    
    frags.append(rect(180, 125, 320, 60, fill="#d5f5e3", stroke=POS, sw=2.5, rx=2))
    frags.append(text(340, 150, "Активний елемент з Манганіну (Cu-Mn-Ni)", size=12, color=POS, bold=True))
    frags.append(text(340, 168, "Паяння срібним припоєм (захист від окиснення)", size=10, color=MUTED))
    
    frags.append(arrow(20, 155, 60, 155, color=NEG, sw=3))
    frags.append(text(40, 140, "I_main", size=12, color=NEG, bold=True))
    
    frags.append(arrow(620, 155, 660, 155, color=NEG, sw=3))
    frags.append(text(640, 140, "I_main", size=12, color=NEG, bold=True))
    
    frags.append(line(230, 185, 230, 260, color=FIELD, sw=2))
    frags.append(circle(230, 185, 4, fill=FIELD))
    frags.append(textbox(230, 280, "Потенціальний вивід P1\n(Sense 1)", size=10, fill="#eafaf1", stroke=FIELD, bold=True)[0])
    
    frags.append(line(450, 185, 450, 260, color=FIELD, sw=2))
    frags.append(circle(450, 185, 4, fill=FIELD))
    frags.append(textbox(450, 280, "Потенціальний вивід P2\n(Sense 2)", size=10, fill="#eafaf1", stroke=FIELD, bold=True)[0])
    
    frags.append(arrow(230, 235, 450, 235, color=FIELD, sw=1.5))
    frags.append(arrow(450, 235, 230, 235, color=FIELD, sw=1.5))
    frags.append(text(340, 225, "Спад напруги V_sense = I_main · R_shunt", size=11, color=FIELD, bold=True))
    
    frags.append(rect(70, 25, 540, 50, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=4))
    frags.append(text(340, 43, "Термо-РСУ проти міді (S_Cu): Манганін ≈ 1 мкВ/К (ідеально для DC)", size=11, color="#b9770e", bold=True))
    frags.append(text(340, 61, "Константан ≈ -40 мкВ/К (паразитний термоЕРС зсув при градієнті ΔT)", size=10, color=NEG))

    render(os.path.join(img_dir, "kelvin-shunt-construction.svg"), w, h, *frags)

# 4. Elinvar Elasticity Curve
def gen_elinvar_elasticity_curve():
    w, h = 660, 400
    frags = []
    
    frags.append(text(w / 2, 26, "Температурна стабільність модуля Юнга у сплавах Елінвар", size=15, bold=True))
    
    ox, oy = 80, 330
    ax_w, ax_h = 530, 250
    frags.append(line(ox, oy, ox + ax_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - ax_h, color=LINE, sw=2))
    
    frags.append(text(ox + ax_w / 2, oy + 42, "Температура T (°C)", size=13, bold=True))
    frags.append(text(ox - 52, oy - ax_h / 2, "Відносний модуль Юнга E(T) / E(20°C)", size=12, bold=True, anchor="middle"))
    
    ticks_t = [-40, 0, 20, 50, 80, 120]
    def t_to_x(t):
        return ox + (t + 40) * (ax_w / 160.0)
        
    for t_val in ticks_t:
        tx = t_to_x(t_val)
        frags.append(line(tx, oy, tx, oy + 5, color=MUTED))
        frags.append(text(tx, oy + 20, "%d°C" % t_val, size=11, color=MUTED))
        
    frags.append(line(ox, oy - 140, ox + ax_w, oy - 140, color="#e5e7e9", sw=1.2, dash="4,4"))
    frags.append(text(ox - 25, oy - 136, "1.00", size=11, color=MUTED))
    
    pts_steel = [(t_to_x(-40), oy - 200), (t_to_x(20), oy - 140), (t_to_x(120), oy - 40)]
    path_steel = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_steel)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_steel, NEG))
    frags.append(text(t_to_x(60), oy - 70, "Звичайна сталь (ТКМ ≈ -250 ppm/K)", size=11, color=NEG, bold=True))
    
    pts_elinvar = [(t_to_x(-40), oy - 141), (t_to_x(20), oy - 140), (t_to_x(120), oy - 139)]
    path_elinvar = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts_elinvar)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_elinvar, POS))
    frags.append(text(t_to_x(50), oy - 155, "Елінвар / Ніварокс (ТКМ ≈ 0)", size=11, color=POS, bold=True))
    
    frags.append(textbox(140, 80, "Застосування Елінвару:\nВолоскові пружини балансу годинників,\nкварцові резонатори та камертони.\nЧастота f ∝ √(E / ρ) залишається сталою!", size=10, fill="#fdfefe", stroke=POS)[0])

    render(os.path.join(img_dir, "elinvar-elasticity-curve.svg"), w, h, *frags)

if __name__ == '__main__':
    gen_tcr_parabola_comparison()
    gen_mott_mooij_scattering()
    gen_kelvin_shunt_construction()
    gen_elinvar_elasticity_curve()
    print("All zero-TCR figures generated successfully.")

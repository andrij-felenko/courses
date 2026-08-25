# -*- coding: utf-8 -*-
import sys, os
import math

# sys.path for svgkit (4 levels up from topic folder to scripts/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def make_img_dir():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

def dashed_circle(cx, cy, r, fill="none", stroke=LINE, sw=1.5, dash="4,4"):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"/>' % (cx, cy, r, fill, stroke, sw, dash))

def draw_tokamak_magnetic_fields(path):
    w, h = 960, 500
    frags = []
    
    # Background panel for geometry & fields
    frags.append(rect(15, 15, 930, 470, fill="#fafbfc", stroke="#d1d5db", sw=1, rx=8))
    
    # Title
    frags.append(text(w/2, 42, "Магнітні поля та геометрія токамака", size=18, bold=True, color=INK))
    
    # Left schematic: Toroidal cross-section & helical field lines
    cx, cy = 280, 270
    R_maj, r_min = 140, 65
    
    # Axis of symmetry (z-axis)
    frags.append(line(cx - R_maj - r_min - 45, cy - 180, cx - R_maj - r_min - 45, cy + 180, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(text(cx - R_maj - r_min - 45, cy - 192, "Ось симетрії (z)", size=11, color=MUTED))
    
    # Outer toroidal plasma ring (ellipse)
    frags.append(dashed_circle(cx, cy, R_maj + r_min, fill="none", stroke="#e5e7eb", sw=2, dash="3,3"))
    frags.append(dashed_circle(cx, cy, R_maj - r_min, fill="none", stroke="#e5e7eb", sw=2, dash="3,3"))
    frags.append(dashed_circle(cx, cy, R_maj, fill="none", stroke="#9ca3af", sw=1.5, dash="6,4"))
    
    # Central Solenoid using fitbox
    cs_x = cx - R_maj - r_min - 35
    frags.append(fitbox(cs_x - 35, cy - 100, 70, 200, "Центральний\nсоленоїд\n(первинна\nобмотка)", size=11, fill="#fee2e2", stroke=POS, bold=True, color=POS))
    
    # Plasma torus representation
    frags.append('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="#dbeafe" stroke="%s" stroke-width="2" opacity="0.8"/>' % 
                 (cx + R_maj, cy, r_min, int(r_min*0.7), NEG))
    
    # Toroidal magnetic field coils (TF coils)
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        tx = cx + R_maj * math.cos(rad)
        ty = cy + R_maj * math.sin(rad) * 0.45
        frags.append('<ellipse cx="%.1f" cy="%.1f" rx="30" ry="50" fill="none" stroke="%s" stroke-width="2.5" transform="rotate(%d %.1f %.1f)"/>' %
                     (tx, ty, FIELD, angle + 90, tx, ty))
    
    # Field vectors and labels using fitbox to avoid line intersections
    frags.append(arrow(cx + R_maj, cy - int(r_min*0.7) - 10, cx + R_maj + 50, cy - int(r_min*0.7) - 10, color=FIELD, sw=2.5))
    frags.append(fitbox(cx + R_maj + 55, cy - int(r_min*0.7) - 40, 170, 30, "B_φ (Тороїдальне поле)", size=11, fill="#f0fdf4", stroke=FIELD, bold=True, color=FIELD))
    
    # Poloidal field vector
    frags.append(arrow(cx + R_maj + r_min, cy, cx + R_maj + r_min, cy - 45, color=POS, sw=2.5))
    frags.append(fitbox(cx + R_maj + r_min + 5, cy + 25, 165, 30, "B_θ (Полоїдальне поле)", size=11, fill="#fef2f2", stroke=POS, bold=True, color=POS))
    
    # Helical field line arrow
    frags.append(arrow(cx + R_maj - 20, cy + 25, cx + R_maj + 30, cy - 30, color="#7c3aed", sw=3))
    frags.append(fitbox(cx + R_maj - 130, cy + 40, 210, 30, "Гвинтова лінія B = B_φ + B_θ", size=11, fill="#f3e8ff", stroke="#7c3aed", bold=True, color="#7c3aed"))
    
    # Right panel: Explanatory text & formula cards
    rx = 710
    frags.append(fitbox(rx, 80, 210, 90, "1. Тороїдальне поле B_φ\nСтворюється зовнішніми\nкотушками (TF coils).\nЗабезпечує первинне утримання.", size=11, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(rx, 185, 210, 90, "2. Полоїдальне поле B_θ\nСтворюється струмом плазми I_p,\nіндукованим соленоїдом.\nЗакручує силові лінії.", size=11, fill="#fef2f2", stroke=POS))
    frags.append(fitbox(rx, 290, 210, 90, "3. Гвинтові поверхні\nСилові лінії намотуються\nна вкладені тороїдальні\nмагнітні поверхні.", size=11, fill="#f3e8ff", stroke="#7c3aed"))
    frags.append(fitbox(rx, 395, 210, 75, "Коефіцієнт запасу q(r):\nq = (r · B_φ) / (R · B_θ)\nПоказник МГД-стійкості", size=11, fill="#eff6ff", stroke=NEG, bold=True))
    
    render(path, w, h, *frags)

def draw_drift_and_rotational_transform(path):
    w, h = 820, 480
    frags = []
    
    frags.append(rect(15, 15, 790, 450, fill="#fafbfc", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(w/2, 42, "Компенсація градієнтного дрейфу закруткою магнітного поля", size=18, bold=True, color=INK))
    
    # Left Panel: Simple Torus (Unstable)
    p1_x, p1_y = 210, 250
    frags.append(rect(35, 70, 350, 370, fill="#ffffff", stroke="#fca5a5", sw=1.5, rx=6))
    frags.append(text(p1_x, 95, "А. Простий тороїдальний соленоїд", size=14, bold=True, color=POS))
    
    # Draw simple torus slice cross-section
    frags.append(dashed_circle(p1_x, p1_y, 90, fill="#fff5f5", stroke=POS, sw=2, dash="4,4"))
    frags.append(text(p1_x - 140, p1_y, "Сильніше B", size=11, color=MUTED))
    frags.append(text(p1_x + 105, p1_y, "Слабше B", size=11, color=MUTED))
    frags.append(arrow(p1_x - 100, p1_y + 110, p1_x + 100, p1_y + 110, color=MUTED, sw=1.5))
    frags.append(text(p1_x, p1_y + 125, "∇B (градієнт поля)", size=11, color=MUTED))
    
    # Charge separation ions UP, electrons DOWN
    for dx in (-40, 0, 40):
        frags.append(plus(p1_x + dx, p1_y - 50, r=10))
        frags.append(minus(p1_x + dx, p1_y + 50, r=10))
    
    # Electric field arrows (E-field pointing DOWN)
    frags.append(arrow(p1_x, p1_y - 30, p1_x, p1_y + 30, color=POS, sw=2))
    frags.append(text(p1_x + 15, p1_y, "E", size=14, color=POS, bold=True))
    
    # Outward E x B drift arrow
    frags.append(arrow(p1_x + 30, p1_y, p1_x + 115, p1_y, color=POS, sw=3))
    frags.append(text(p1_x + 60, p1_y - 15, "v_E×B", size=13, color=POS, bold=True))
    frags.append(fitbox(p1_x - 160, 375, 320, 35, "Плазма викидається на стінку за мікросекунди!", size=11, fill="#fee2e2", stroke=POS, bold=True, color=POS))
    
    # Right Panel: Tokamak with Rotational Transform (Stable)
    p2_x, p2_y = 610, 250
    frags.append(rect(435, 70, 350, 370, fill="#ffffff", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(p2_x, 95, "Б. Токамак (обертальне перетворення)", size=14, bold=True, color=FIELD))
    
    # Poloidal cross-section with magnetic surfaces and helical line short-circuit
    frags.append(circle(p2_x, p2_y, 90, fill="#f0fdf4", stroke=FIELD, sw=2))
    frags.append(dashed_circle(p2_x, p2_y, 55, fill="none", stroke=FIELD, sw=1.5, dash="3,3"))
    
    # Helical path connecting top (+) and bottom (-)
    frags.append('<path d="M %d %d A 65 65 0 0 1 %d %d" fill="none" stroke="#7c3aed" stroke-width="2.5" stroke-dasharray="5,3"/>' %
                 (p2_x, p2_y - 65, p2_x, p2_y + 65))
    frags.append(arrow(p2_x + 10, p2_y + 50, p2_x - 5, p2_y + 63, color="#7c3aed", sw=2.5))
    
    # Charges moving along field line to neutralize E-field
    frags.append(plus(p2_x, p2_y - 65, r=9))
    frags.append(minus(p2_x, p2_y + 65, r=9))
    frags.append(arrow(p2_x - 20, p2_y - 50, p2_x - 45, p2_y, color=NEG, sw=2))
    frags.append(text(p2_x - 80, p2_y - 25, "Струм уздовж B", size=11, color=NEG, bold=True))
    frags.append(text(p2_x - 85, p2_y - 10, "коротко замикає E", size=11, color=NEG))
    
    frags.append(fitbox(p2_x - 160, 375, 320, 35, "Дрейф нейтралізується перетіканням зарядів!", size=11, fill="#dcfce7", stroke=FIELD, bold=True, color=FIELD))
    
    render(path, w, h, *frags)

def draw_banana_orbit(path):
    w, h = 780, 480
    frags = []
    
    frags.append(rect(15, 15, 750, 450, fill="#fafbfc", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(w/2, 42, "Траєкторії частинок: пролітні та заперті (бананні орбіти)", size=18, bold=True, color=INK))
    
    cx, cy = 260, 250
    frags.append(rect(35, 70, 450, 370, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    
    # High field side (inner wall) vs Low field side (outer wall)
    frags.append(line(cx - 180, cy - 160, cx - 180, cy + 160, color=POS, sw=3))
    frags.append(mtext(cx - 150, cy - 140, ["Внутрішня стінка", "(сильне поле B_in)"], size=11, color=POS, bold=True))
    
    frags.append(line(cx + 180, cy - 160, cx + 180, cy + 160, color=NEG, sw=3))
    frags.append(mtext(cx + 140, cy - 140, ["Зовнішня стінка", "(слабке поле B_out)"], size=11, color=NEG, bold=True))
    
    # Flux surface
    frags.append(dashed_circle(cx, cy, 120, fill="none", stroke="#94a3b8", sw=1.5, dash="6,4"))
    frags.append(text(cx, cy - 128, "Магнітна поверхня", size=11, color=MUTED))
    
    # Banana orbit path (trapped particle)
    banana_path = ('M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d Z' %
                   (cx - 20, cy - 90,
                    cx + 80, cy - 50,  cx + 80, cy + 50,  cx - 20, cy + 90,
                    cx + 40, cy + 40,  cx + 40, cy - 40,  cx - 20, cy - 90))
    frags.append('<path d="%s" fill="#fef3c7" stroke="#d97706" stroke-width="2.5"/>' % banana_path)
    
    # Reflection points (magnetic mirror)
    frags.append(circle(cx - 20, cy - 90, 5, fill=POS, stroke=INK, sw=1))
    frags.append(circle(cx - 20, cy + 90, 5, fill=POS, stroke=INK, sw=1))
    frags.append(text(cx - 75, cy - 95, "Точка відбиття", size=11, color=POS, bold=True))
    frags.append(text(cx - 75, cy + 95, "Точка відбиття", size=11, color=POS, bold=True))
    
    # Banana width arrow
    frags.append(arrow(cx + 40, cy, cx + 75, cy, color="#d97706", sw=2))
    frags.append(arrow(cx + 75, cy, cx + 40, cy, color="#d97706", sw=2))
    frags.append(text(cx + 58, cy - 12, "Δr_b", size=12, color="#d97706", bold=True))
    
    # Right panel explanations
    rx = 495
    frags.append(fitbox(rx, 80, 240, 70, "Пролітні частинки\nv_|| > v_⊥ · (2ε)^1/2\nОбігають весь тороїд\nуздовж силових ліній.", size=11, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(rx, 170, 240, 110, "Заперті частинки\nv_|| / v_⊥ < (2ε)^1/2\nЗахоплюються магнітним\nдзеркалом у сильному полі\nй здійснюють бананні орбіти.", size=11, fill="#fffbeb", stroke="#d97706", bold=True))
    frags.append(fitbox(rx, 300, 240, 90, "Ширина банана Δr_b:\nΔr_b ≈ (q · ρ_p) / √ε\nВизначає неокласичний\nперенос тепла й частинок.", size=11, fill="#eff6ff", stroke=NEG))
    
    render(path, w, h, *frags)

def draw_lawson_and_beta(path):
    w, h = 800, 480
    frags = []
    
    frags.append(rect(15, 15, 770, 450, fill="#fafbfc", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(w/2, 42, "Потрійний добуток Лоусона та параметричні межі токамаків", size=18, bold=True, color=INK))
    
    # Left Chart: Lawson triple product n*T*tau_E vs T
    gx, gy, gw, gh = 45, 90, 360, 310
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=4))
    
    # Axes
    frags.append(arrow(gx + 30, gy + gh - 30, gx + gw - 15, gy + gh - 30, color=INK, sw=2))
    frags.append(text(gx + gw - 40, gy + gh - 10, "Температура T (кеВ)", size=11, color=INK, bold=True))
    
    frags.append(arrow(gx + 30, gy + gh - 30, gx + 30, gy + 20, color=INK, sw=2))
    frags.append(mtext(gx + 5, gy + 25, ["n·T·τ_E", "(м⁻³·кеВ·с)"], size=11, color=INK, bold=True))
    
    # Ignition curve (Lawson criterion)
    lawson_path = ('M %d %d Q %d %d, %d %d Q %d %d, %d %d' %
                   (gx + 40, gy + 80,  gx + 160, gy + 190,  gx + 220, gy + 175,  gx + 280, gy + 110, gx + 330, gy + 60))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="5,3"/>' % (lawson_path, POS))
    frags.append(text(gx + 210, gy + 155, "Поріг запалювання Q = ∞", size=11, color=POS, bold=True))
    
    # Historical devices points
    devices = [
        ("T-3 (1968)", gx + 70, gy + 260, MUTED),
        ("PLT (1978)", gx + 120, gy + 230, MUTED),
        ("TFTR / JET (1990-ті)", gx + 200, gy + 140, NEG),
        ("JT-60U (1998)", gx + 240, gy + 120, FIELD),
        ("ITER (проект Q=10)", gx + 280, gy + 75, POS)
    ]
    for label, px, py, col in devices:
        frags.append(circle(px, py, 6, fill=col, stroke=INK, sw=1))
        frags.append(text(px + 10, py + 4, label, size=11, color=col, bold=True))
    
    # Right panel: Key stability limits (Troyon & Kruskal-Shafranov)
    rx = 430
    frags.append(fitbox(rx, 70, 320, 80, "Потрійний критерій Лоусона:\nn · T · τ_E ≥ 3·10²¹ м⁻³·кеВ·с\nУмова самопідтримуваної термоядерної реакції D-T.", size=11, fill="#fef2f2", stroke=POS, bold=True))
    frags.append(fitbox(rx, 175, 320, 95, "Межа Трояна для бета-параметра:\nβ_max = β_N · (I_p / a·B_φ)\nОбмежує максимальний тиск плазми\nвідносно тиску магнітного поля.", size=11, fill="#eff6ff", stroke=NEG))
    frags.append(fitbox(rx, 295, 320, 95, "Межа Крускала — Шафранова:\nq(a) > 2 (абсолютна межа q(a) > 1)\nЗапобігає розвитку катастрофічної\nгвинтової нестійкості (kink mode).", size=11, fill="#f0fdf4", stroke=FIELD))
    
    render(path, w, h, *frags)

if __name__ == '__main__':
    img_dir = make_img_dir()
    draw_tokamak_magnetic_fields(os.path.join(img_dir, 'tokamak-magnetic-fields.svg'))
    draw_drift_and_rotational_transform(os.path.join(img_dir, 'drift-and-rotational-transform.svg'))
    draw_banana_orbit(os.path.join(img_dir, 'banana-orbit.svg'))
    draw_lawson_and_beta(os.path.join(img_dir, 'lawson-and-beta.svg'))
    print("All figures successfully generated in img/")

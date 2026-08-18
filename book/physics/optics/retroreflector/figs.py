# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GLASS = "#eaf2fb"
MIRROR = "#cbd5e1"
BEAM_IN = "#2563eb"
BEAM_OUT = "#dc2626"
BEAM_MID = "#d97706"

def poly(pts, fill='none', stroke=LINE, sw=1.5):
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

def path_d(d, fill='none', stroke=LINE, sw=1.5):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

# ═══════════════════════════════════════════════════════════════════════════
# Figure 1: Flat mirror vs 2D Corner Reflector vs 3D Corner Cube
# ═══════════════════════════════════════════════════════════════════════════
def fig1_corner_cube_2d_3d():
    W, H = 760, 310
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, "Принцип кутового відбивача: плоске дзеркало та куточок 90°", 16, INK, 'middle', bold=True))

    # Panel A: Flat mirror
    cx1 = 130
    f.append(text(cx1, 52, "а) Плоске дзеркало", 13, INK, 'middle', bold=True))
    f.append(line(cx1 - 60, 180 + 20, cx1 + 60, 180 - 20, color=MUTED, sw=4))
    f.append(line(cx1, 180, cx1 - 25, 180 - 75, color=MUTED, sw=1.2, dash="4,3"))
    f.append(arrow(cx1 - 70, 80, cx1, 180, color=BEAM_IN, sw=2.2))
    f.append(arrow(cx1, 180, cx1 + 80, 100, color=BEAM_OUT, sw=2.2))
    f.append(text(cx1, 230, "Відхилення дзеркала θ", 11, INK, 'middle'))
    f.append(text(cx1, 248, "змінює кут на 2θ", 11, NEG, 'middle', bold=True))

    # Divider 1
    f.append(line(260, 45, 260, 280, color=MUTED, sw=0.8, dash="3,3"))

    # Panel B: 2D Corner Reflector
    cx2 = 390
    f.append(text(cx2, 52, "б) 2D кутовий відбивач (90°)", 13, INK, 'middle', bold=True))
    # Two orthogonal mirrors
    f.append(line(cx2 - 70, 200, cx2 + 10, 200, color=MUTED, sw=4))
    f.append(line(cx2 - 70, 200, cx2 - 70, 100, color=MUTED, sw=4))
    # In beam
    f.append(arrow(cx2 + 40, 110, cx2 - 20, 200, color=BEAM_IN, sw=2.2))
    # Mid beam
    f.append(line(cx2 - 20, 200, cx2 - 70, 150, color=BEAM_MID, sw=2.2))
    # Out beam
    f.append(arrow(cx2 - 70, 150, cx2 - 10, 60, color=BEAM_OUT, sw=2.2))
    f.append(text(cx2 - 50, 218, "90°", 12, POS, 'start', bold=True))
    f.append(text(cx2 - 10, 235, "Два відбиття розвертають", 11, INK, 'middle'))
    f.append(text(cx2 - 10, 252, "промінь паралельно назад", 11, POS, 'middle', bold=True))

    # Divider 2
    f.append(line(520, 45, 520, 280, color=MUTED, sw=0.8, dash="3,3"))

    # Panel C: 3D Corner Cube
    cx3 = 640
    f.append(text(cx3, 52, "в) 3D тригранний куточок", 13, INK, 'middle', bold=True))
    # 3D isometric representation of corner cube
    ox, oy = cx3 - 30, 170
    # Axis lines forming corner
    f.append(line(ox, oy, ox + 60, oy, color=MUTED, sw=3))
    f.append(line(ox, oy, ox, oy - 60, color=MUTED, sw=3))
    f.append(line(ox, oy, ox - 40, oy + 40, color=MUTED, sw=3))
    # Isometric planes fill
    f.append(poly([(ox, oy), (ox + 60, oy), (ox + 60, oy - 60), (ox, oy - 60)], fill=GLASS, stroke=MUTED, sw=1))
    f.append(poly([(ox, oy), (ox - 40, oy + 40), (ox - 40, oy - 20), (ox, oy - 60)], fill="#dbeafe", stroke=MUTED, sw=1))
    f.append(poly([(ox, oy), (ox + 60, oy), (ox + 20, oy + 40), (ox - 40, oy + 40)], fill="#eff6ff", stroke=MUTED, sw=1))
    # Vector transformation label
    f.append(text(cx3 - 10, 235, "Три координатні відбиття:", 11, INK, 'middle'))
    f.append(text(cx3 - 10, 252, "v'' = (-v_x, -v_y, -v_z) = -v", 12, FIELD, 'middle', bold=True))

    render(os.path.join(IMG, 'fig1-corner-cube-2d-3d.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 2: Solid Glass Prism vs Hollow Corner Cube
# ═══════════════════════════════════════════════════════════════════════════
def fig2_solid_vs_hollow_corner():
    W, H = 720, 310
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, "Суцільна скляна призма та порожнистий кутовий відбивач", 16, INK, 'middle', bold=True))

    # Panel A: Solid Prism (TIR)
    cx1 = 190
    f.append(text(cx1, 52, "а) Суцільна скляна призма (ПВВ)", 13, INK, 'middle', bold=True))

    # Draw prism shape
    prism_pts = [(cx1 - 90, 100), (cx1 + 90, 100), (cx1, 240)]
    f.append(poly(prism_pts, fill=GLASS, stroke=FIELD, sw=2))

    # Rays
    # Incident beam at front face
    f.append(arrow(cx1 - 50, 40, cx1 - 40, 100, color=BEAM_IN, sw=2.2))
    # Refracted ray inside prism
    f.append(line(cx1 - 40, 100, cx1 - 50, 177, color=BEAM_MID, sw=2.2))
    # TIR 1
    f.append(line(cx1 - 50, 177, cx1 + 40, 163, color=BEAM_MID, sw=2.2))
    # TIR 2 & Exit
    f.append(arrow(cx1 + 40, 163, cx1 + 50, 40, color=BEAM_OUT, sw=2.2))

    f.append(text(cx1, 120, "Вхідна грань (заломлення)", 10, MUTED, 'middle'))
    f.append(text(cx1 - 45, 205, "ПВВ 1", 10, POS, 'middle', bold=True))
    f.append(text(cx1 + 45, 195, "ПВВ 2", 10, POS, 'middle', bold=True))
    f.append(text(cx1, 268, "100% відбиття без покриття (n > 1)", 11, POS, 'middle', bold=True))
    f.append(text(cx1, 286, "Розширений кут прийому завдяки Снеллу", 10, MUTED, 'middle'))

    # Divider
    f.append(line(370, 45, 370, 290, color=MUTED, sw=0.8, dash="3,3"))

    # Panel B: Hollow Corner Cube
    cx2 = 550
    f.append(text(cx2, 52, "б) Порожнистий кутовий відбивач", 13, INK, 'middle', bold=True))

    # Mirror plates
    f.append(line(cx2 - 100, 110, cx2, 240, color=MUTED, sw=5))
    f.append(line(cx2 + 100, 110, cx2, 240, color=MUTED, sw=5))
    f.append(text(cx2 - 70, 190, "Дзеркало 1", 10, MUTED, 'end'))
    f.append(text(cx2 + 70, 190, "Дзеркало 2", 10, MUTED, 'start'))

    # Rays
    f.append(arrow(cx2 - 40, 40, cx2 - 50, 175, color=BEAM_IN, sw=2.2))
    f.append(line(cx2 - 50, 175, cx2 + 45, 181, color=BEAM_MID, sw=2.2))
    f.append(arrow(cx2 + 45, 181, cx2 + 35, 40, color=BEAM_OUT, sw=2.2))

    f.append(text(cx2, 268, "Без заломлення та хроматичної дисперсії", 11, FIELD, 'middle', bold=True))
    f.append(text(cx2, 286, "УФ, видиме світло та далекий ІЧ діапазон", 10, MUTED, 'middle'))

    render(os.path.join(IMG, 'fig2-solid-vs-hollow-corner.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 3: Glass Bead Spherical Retroreflector
# ═══════════════════════════════════════════════════════════════════════════
def fig3_sphere_catadioptric():
    W, H = 720, 310
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, "Сферичний ретрорефлектор: заломлення та відбиття у кульці", 16, INK, 'middle', bold=True))

    # Panel A: Ideal sphere n = 2.0
    cx1 = 190
    f.append(text(cx1, 52, "а) Ідеальна скляна кулька (n = 2.0)", 13, INK, 'middle', bold=True))

    R = 65
    cy = 160
    f.append(circle(cx1, cy, R, fill=GLASS, stroke=FIELD, sw=2))

    # Rays for n = 2.0 focus on back surface
    f.append(arrow(cx1 - 120, cy - 35, cx1 - 56, cy - 35, color=BEAM_IN, sw=2))
    f.append(line(cx1 - 56, cy - 35, cx1 + R, cy, color=BEAM_MID, sw=2))
    f.append(line(cx1 + R, cy, cx1 - 56, cy + 35, color=BEAM_MID, sw=2))
    f.append(arrow(cx1 - 56, cy + 35, cx1 - 120, cy + 35, color=BEAM_OUT, sw=2))

    f.append(circle(cx1 + R, cy, 4, fill=NEG, stroke='none'))
    f.append(text(cx1 + R + 8, cy, "Фокус на задній стінці", 10, NEG, 'start', bold=True))
    f.append(text(cx1, cy + R + 22, "Параксіальний фокус точно на поверхні", 11, POS, 'middle', bold=True))
    f.append(text(cx1, cy + R + 40, "n = 2.0 забезпечує зворотне заломлення", 10, MUTED, 'middle'))

    # Divider
    f.append(line(370, 45, 370, 290, color=MUTED, sw=0.8, dash="3,3"))

    # Panel B: Glass bead n = 1.5 with reflective backing
    cx2 = 550
    f.append(text(cx2, 52, "б) Скляна мікросфера (n ≈ 1.5) з дзеркалом", 13, INK, 'middle', bold=True))

    f.append(circle(cx2, cy, R, fill=GLASS, stroke=FIELD, sw=2))
    # Reflective coat on back hemisphere
    f.append(path_d(f"M {cx2} {cy - R} A {R} {R} 0 0 1 {cx2} {cy + R}", fill='none', stroke=BEAM_MID, sw=5))

    # Rays
    f.append(arrow(cx2 - 120, cy - 30, cx2 - 58, cy - 30, color=BEAM_IN, sw=2))
    f.append(line(cx2 - 58, cy - 30, cx2 + 50, cy - 10, color=BEAM_MID, sw=2))
    f.append(line(cx2 + 50, cy - 10, cx2 - 58, cy + 30, color=BEAM_MID, sw=2))
    f.append(arrow(cx2 - 58, cy + 30, cx2 - 120, cy + 30, color=BEAM_OUT, sw=2))

    f.append(text(cx2 + R + 8, cy, "Відбивальний шар (дзеркало/фарба)", 10, BEAM_MID, 'start', bold=True))
    f.append(text(cx2, cy + R + 22, "Використовується в катафотах і плівках 3M", 11, FIELD, 'middle', bold=True))
    f.append(text(cx2, cy + R + 40, "Дорожні знаки, розмітка та спецодяг", 10, MUTED, 'middle'))

    render(os.path.join(IMG, 'fig3-sphere-catadioptric.svg'), W, H, *f)

# ═══════════════════════════════════════════════════════════════════════════
# Figure 4: Velocity Aberration and Spoiled Corner Cube
# ═══════════════════════════════════════════════════════════════════════════
def fig4_velocity_aberration():
    W, H = 740, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, "Дифракційний пучок та швидкісна аберація світла на орбіті", 16, INK, 'middle', bold=True))

    # Satellite at top
    sx, sy = 370, 75
    f.append(rect(sx - 30, sy - 15, 60, 30, fill="#334155", stroke=INK, sw=1.5, rx=4))
    f.append(text(sx, sy + 4, "Супутник (LAGEOS)", 10, BG, 'middle', bold=True))
    # Orbital velocity arrow
    f.append(arrow(sx + 35, sy, sx + 95, sy, color=NEG, sw=2.5))
    f.append(text(sx + 65, sy - 10, "Швидкість v ≈ 7.5 км/с", 11, NEG, 'middle', bold=True))

    # Ground station at bottom left
    gx1, gy = 180, 250
    f.append(circle(gx1, gy, 12, fill="#e2e8f0", stroke=INK, sw=2))
    f.append(text(gx1, gy + 26, "Лазерний передавач", 11, BEAM_IN, 'middle', bold=True))

    # Receiver position shifted at bottom right
    gx2 = 320
    f.append(circle(gx2, gy, 12, fill="#fed7aa", stroke=NEG, sw=2))
    f.append(text(gx2, gy + 26, "Приймач через t = 2H/c", 11, NEG, 'middle', bold=True))

    # Incoming laser ray
    f.append(line(gx1, gy, sx, sy, color=BEAM_IN, sw=2, dash="6,4"))

    # Returned narrow beam (ideal corner cube) -> misses!
    f.append(line(sx, sy, gx1, gy, color=MUTED, sw=1.5, dash="4,4"))

    # Returned widened diffractive cone (spoiled corner cube) -> hits receiver!
    cone_pts = [(sx, sy), (gx1 - 40, gy), (gx2 + 60, gy)]
    f.append(poly(cone_pts, fill="rgba(217, 119, 6, 0.15)", stroke=BEAM_MID, sw=1.5))

    f.append(text(gx1 - 20, 160, "Кут аберації Δθ = 2v/c", 11, NEG, 'end', bold=True))
    f.append(text(gx1 - 20, 178, "(~35–40 мкрад ≈ 7–8″)", 10, MUTED, 'end'))

    f.append(text(540, 140, "Ідеальний куточок (90.000°):", 12, INK, 'start', bold=True))
    f.append(text(540, 160, "• Вузький пучок θ_diff < 10″", 11, MUTED, 'start'))
    f.append(text(540, 178, "• Промах повз приймач!", 11, NEG, 'start', bold=True))

    f.append(text(540, 210, "«Зіпсований» куточок (δθ ≈ 1.5″):", 12, INK, 'start', bold=True))
    f.append(text(540, 230, "• Розширене дифракційне кільце", 11, POS, 'start', bold=True))
    f.append(text(540, 248, "• Надійне захоплення приймачем", 11, POS, 'start'))

    render(os.path.join(IMG, 'fig4-velocity-aberration.svg'), W, H, *f)

if __name__ == '__main__':
    fig1_corner_cube_2d_3d()
    fig2_solid_vs_hollow_corner()
    fig3_sphere_catadioptric()
    fig4_velocity_aberration()
    print("Figures rendered successfully.")

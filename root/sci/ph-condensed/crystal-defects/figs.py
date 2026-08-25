# -*- coding: utf-8 -*-
import sys
import os
import math

# Path to scripts/ in repo root (4 levels up)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

def polygon(points, fill=FILL, stroke=LINE, sw=1.5):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

# 1. Point defects in 2D crystal lattice
def gen_point_defects():
    w, h = 820, 420
    frags = []

    # Title
    frags.append(text(w / 2, 28, "Точкові дефекти кристалічної ґратки (0D)", size=16, bold=True))

    # Grid parameters
    cols, rows = 12, 6
    dx, dy = 38.0, 38.0
    ox, oy = 70.0, 80.0
    r_atom = 12.0

    # Draw grid lines
    for i in range(cols):
        frags.append(line(ox + i * dx, oy, ox + i * dx, oy + (rows - 1) * dy, color="#e2e8f0", sw=1.0))
    for j in range(rows):
        frags.append(line(ox, oy + j * dy, ox + (cols - 1) * dx, oy + j * dy, color="#e2e8f0", sw=1.0))

    vacancy_1 = (2, 1)
    sub_large = (5, 1)
    inter_imp = (8, 1)
    frenkel_vac = (2, 4)
    frenkel_inter = (ox + 2.5 * dx, oy + 4.5 * dy)
    sub_small = (9, 4)

    for i in range(cols):
        for j in range(rows):
            cx = ox + i * dx
            cy = oy + j * dy

            if (i, j) == vacancy_1:
                frags.append(circle(cx, cy, r_atom, fill="#ffffff", stroke="#ef4444", sw=1.5))
                frags.append(line(cx - 6, cy, cx + 6, cy, color="#ef4444", sw=1.5))
                frags.append(line(cx, cy - 6, cx, cy + 6, color="#ef4444", sw=1.5))
            elif (i, j) == frenkel_vac:
                frags.append(circle(cx, cy, r_atom, fill="#ffffff", stroke="#8b5cf6", sw=1.5))
                frags.append(line(cx - 6, cy, cx + 6, cy, color="#8b5cf6", sw=1.5))
            elif (i, j) == sub_large:
                frags.append(circle(cx, cy, r_atom * 1.35, fill="#f97316", stroke="#c2410c", sw=1.5))
            elif (i, j) == sub_small:
                frags.append(circle(cx, cy, r_atom * 0.75, fill="#10b981", stroke="#047857", sw=1.5))
            else:
                frags.append(circle(cx, cy, r_atom, fill="#3b82f6", stroke="#1d4ed8", sw=1.2))

    ix_imp = ox + 8.5 * dx
    iy_imp = oy + 1.5 * dy
    frags.append(circle(ix_imp, iy_imp, r_atom * 0.65, fill="#eab308", stroke="#ca8a04", sw=1.5))

    frags.append(circle(frenkel_inter[0], frenkel_inter[1], r_atom, fill="#8b5cf6", stroke="#6d28d9", sw=1.5))
    frags.append(arrow(ox + 2 * dx + 10, oy + 4 * dy + 10, frenkel_inter[0] - 8, frenkel_inter[1] - 8, color="#8b5cf6", sw=1.5))

    y_grid_bottom = oy + (rows - 1) * dy

    frags.append(line(ox + 2 * dx, oy + 1 * dy + r_atom + 2, ox + 2 * dx, y_grid_bottom + 20, color="#ef4444", sw=1.0, dash="2,2"))
    frags.append(text(ox + 2 * dx, y_grid_bottom + 34, "1. Вакансія (порожній вузол)", size=11, color="#ef4444", bold=True))

    frags.append(line(ox + 5 * dx, oy + 1 * dy + r_atom * 1.35 + 2, ox + 5 * dx, y_grid_bottom + 52, color="#c2410c", sw=1.0, dash="2,2"))
    frags.append(text(ox + 5 * dx, y_grid_bottom + 66, "2. Замісний атом (великий)", size=11, color="#c2410c", bold=True))

    frags.append(line(ix_imp, iy_imp + r_atom * 0.65 + 2, ix_imp, y_grid_bottom + 20, color="#ca8a04", sw=1.0, dash="2,2"))
    frags.append(text(ix_imp, y_grid_bottom + 34, "3. Міжвузловий домішковий атом", size=11, color="#ca8a04", bold=True))

    frags.append(text(ox + 2.5 * dx, oy + 4.5 * dy + 22, "Пара Френкеля", size=11, color="#6d28d9", bold=True))

    frags.append(line(ox + 9 * dx, oy + 4 * dy + r_atom + 2, ox + 9 * dx, y_grid_bottom + 52, color="#047857", sw=1.0, dash="2,2"))
    frags.append(text(ox + 9 * dx, y_grid_bottom + 66, "4. Замісний атом (малий)", size=11, color="#047857", bold=True))

    render(os.path.join(OUT_DIR, "point-defects.svg"), w, h, *frags)

# 2. Line defects: Edge and Screw Dislocations
def gen_dislocations():
    w, h = 840, 420
    frags = []

    frags.append(text(w / 2, 25, "Лінійні дефекти: Крайова та ґвинтова дислокації", size=16, bold=True))

    p1_x, p1_y, p1_w, p1_h = 20, 50, 390, 340
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p1_x + p1_w / 2, p1_y + 22, "Крайова дислокація (Edge dislocation)", size=14, bold=True, color="#0f172a"))

    cx_base = p1_x + 60
    cy_base = p1_y + 60
    gap_x = 42.0
    gap_y = 38.0

    for row in range(3):
        y = cy_base + row * gap_y
        for col in range(7):
            dx_comp = (col - 3) * gap_x * (0.85 if row == 2 else 0.95)
            x = cx_base + 3 * gap_x + dx_comp
            frags.append(circle(x, y, 10.0, fill="#3b82f6", stroke="#1d4ed8", sw=1.2))
            if col == 3:
                frags.append(circle(x, y, 10.0, fill="#ef4444", stroke="#b91c1c", sw=1.5))

    disloc_x = cx_base + 3 * gap_x
    disloc_y = cy_base + 2 * gap_y + 18
    frags.append(line(disloc_x - 12, disloc_y, disloc_x + 12, disloc_y, color="#b91c1c", sw=2.5))
    frags.append(line(disloc_x, disloc_y, disloc_x, disloc_y + 16, color="#b91c1c", sw=2.5))

    for row in range(3, 6):
        y = cy_base + row * gap_y + 8
        for col in range(6):
            dx_expand = (col - 2.5) * gap_x * 1.08
            x = cx_base + 3 * gap_x + dx_expand
            frags.append(circle(x, y, 10.0, fill="#3b82f6", stroke="#1d4ed8", sw=1.2))

    b_y = cy_base + 5 * gap_y + 35
    frags.append(arrow(cx_base + 1.5 * gap_x, b_y, cx_base + 2.5 * gap_x, b_y, color="#059669", sw=2.2))
    frags.append(text(cx_base + 2 * gap_x, b_y - 8, "Вектор Бюргерса b ⊥ t", size=12, color="#059669", bold=True))
    frags.append(text(p1_x + p1_w / 2, p1_y + p1_h - 12, "Зайва атомна півплощина (червона)", size=11, color=MUTED, italic=True))

    p2_x, p2_y, p2_w, p2_h = 430, 50, 390, 340
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p2_x + p2_w / 2, p2_y + 22, "Ґвинтова дислокація (Screw dislocation)", size=14, bold=True, color="#0f172a"))

    center_x = p2_x + p2_w / 2
    center_y = p2_y + 150

    pts_left = [(center_x - 130, center_y - 60), (center_x, center_y - 60), (center_x, center_y + 30), (center_x - 130, center_y + 30)]
    pts_right = [(center_x, center_y - 40), (center_x + 130, center_y - 40), (center_x + 130, center_y + 50), (center_x, center_y + 50)]
    
    frags.append(polygon(pts_left, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    frags.append(polygon(pts_right, fill="#dbeafe", stroke="#1d4ed8", sw=1.5))

    frags.append(line(center_x, center_y - 80, center_x, center_y + 90, color="#dc2626", sw=2.5, dash="4,3"))
    frags.append(arrow(center_x, center_y + 90, center_x, center_y + 115, color="#dc2626", sw=2.5))
    frags.append(text(center_x + 45, center_y + 105, "Лінія дислокації t", size=12, color="#dc2626", bold=True))

    frags.append(arrow(center_x - 35, center_y - 10, center_x - 35, center_y + 10, color="#059669", sw=2.5))
    frags.append(text(center_x - 65, center_y, "b ∥ t", size=13, color="#059669", bold=True))

    frags.append(text(p2_x + p2_w / 2, p2_y + p2_h - 45, "Спіральний зсув атомних площин", size=12, color="#0f172a", bold=True))
    frags.append(text(p2_x + p2_w / 2, p2_y + p2_h - 12, "Вектор Бюргерса b паралельний лінії t", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT_DIR, "dislocations.svg"), w, h, *frags)

# 3. Grain Boundaries and Twin Boundaries (Surface Defects)
def gen_grain_boundaries_twins():
    w, h = 820, 380
    frags = []

    frags.append(text(w / 2, 25, "Поверхневі дефекти: Межі зерен та двійники (2D)", size=16, bold=True))

    p1_x, p1_y, p1_w, p1_h = 20, 50, 380, 310
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p1_x + p1_w / 2, p1_y + 22, "Малокутова межа нахилу", size=14, bold=True, color="#0f172a"))
    frags.append(text(p1_x + p1_w / 2, p1_y + 40, "Стінка крайових дислокацій", size=11, color=MUTED, italic=True))

    boundary_x = p1_x + 190
    frags.append(line(boundary_x, p1_y + 55, boundary_x, p1_y + p1_h - 45, color="#ef4444", sw=2.0, dash="5,3"))

    d_y_list = [p1_y + 90, p1_y + 150, p1_y + 210]
    for dy_pos in d_y_list:
        frags.append(line(boundary_x - 10, dy_pos, boundary_x + 10, dy_pos, color="#b91c1c", sw=2.2))
        frags.append(line(boundary_x, dy_pos, boundary_x, dy_pos + 14, color="#b91c1c", sw=2.2))

    frags.append(arrow(boundary_x - 70, p1_y + 80, boundary_x - 20, p1_y + 65, color="#0284c7", sw=1.5))
    frags.append(arrow(boundary_x + 70, p1_y + 80, boundary_x + 20, p1_y + 65, color="#0284c7", sw=1.5))
    frags.append(text(boundary_x, p1_y + 70, "Кут θ", size=12, color="#0284c7", bold=True))

    frags.append(text(p1_x + p1_w / 2, p1_y + p1_h - 20, "Відстань між дислокаціями: D ≈ b / θ", size=12, color="#047857", bold=True))

    p2_x, p2_y, p2_w, p2_h = 420, 50, 380, 310
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p2_x + p2_w / 2, p2_y + 22, "Двійникова межа (Twin boundary)", size=14, bold=True, color="#0f172a"))
    frags.append(text(p2_x + p2_w / 2, p2_y + 40, "Дзеркальна симетрія атомних площин", size=11, color=MUTED, italic=True))

    twin_x = p2_x + 190
    frags.append(line(twin_x, p2_y + 55, twin_x, p2_y + p2_h - 45, color="#8b5cf6", sw=2.5))
    frags.append(text(twin_x, p2_y + 70, "Площина двійникування", size=11, color="#6d28d9", bold=True))

    for row in range(-3, 4):
        y = p2_y + 170 + row * 28
        for col in range(1, 5):
            lx = twin_x - col * 26 + row * 6
            rx = twin_x + col * 26 + row * 6
            if p2_x + 20 < lx < twin_x - 10 and p2_y + 80 < y < p2_y + p2_h - 50:
                frags.append(circle(lx, y, 7.0, fill="#3b82f6", stroke="#1d4ed8", sw=1.0))
            if twin_x + 10 < rx < p2_x + p2_w - 20 and p2_y + 80 < y < p2_y + p2_h - 50:
                frags.append(circle(rx, y, 7.0, fill="#3b82f6", stroke="#1d4ed8", sw=1.0))

    frags.append(text(p2_x + p2_w / 2, p2_y + p2_h - 20, "Низька поверхнева енергія γ_twin ≪ γ_gb", size=12, color="#6d28d9", bold=True))

    render(os.path.join(OUT_DIR, "grain-boundaries-twins.svg"), w, h, *frags)

# 4. Volume defects (3D)
def gen_volume_defects():
    w, h = 780, 360
    frags = []

    frags.append(text(w / 2, 25, "Об'ємні дефекти: Пори, включення та виділення нової фази (3D)", size=16, bold=True))

    p1_x, p1_y, p1_w, p1_h = 20, 50, 360, 290
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p1_x + p1_w / 2, p1_y + 22, "Пора / Каверна (Void)", size=14, bold=True, color="#0f172a"))

    cx1, cy1 = p1_x + 180, p1_y + 140
    for r in range(45, 110, 15):
        frags.append(circle(cx1, cy1, r, fill="none", stroke="#cbd5e1", sw=1.0))

    frags.append(circle(cx1, cy1, 40.0, fill="#ffffff", stroke="#ef4444", sw=2.0))
    frags.append(text(cx1, cy1, "Порожнеча\n(Скупчення вакансій)", size=11, color="#b91c1c", bold=True))

    frags.append(text(p1_x + p1_w / 2, p1_y + p1_h - 20, "Виникає при вакансійному коалесценсі або спеченні", size=11, color=MUTED, italic=True))

    p2_x, p2_y, p2_w, p2_h = 400, 50, 360, 290
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(p2_x + p2_w / 2, p2_y + 22, "Чужорідне включення / Преципітат", size=14, bold=True, color="#0f172a"))

    cx2, cy2 = p2_x + 180, p2_y + 140

    for angle_deg in range(0, 360, 45):
        rad = math.radians(angle_deg)
        x1 = cx2 + 45 * math.cos(rad)
        y1 = cy2 + 45 * math.sin(rad)
        x2 = cx2 + 70 * math.cos(rad)
        y2 = cy2 + 70 * math.sin(rad)
        frags.append(arrow(x1, y1, x2, y2, color="#059669", sw=1.5))

    frags.append(circle(cx2, cy2, 40.0, fill="#fef08a", stroke="#ca8a04", sw=2.0))
    frags.append(text(cx2, cy2, "Включення\nдругої фази", size=11, color="#854d0e", bold=True))

    frags.append(text(p2_x + p2_w / 2, p2_y + p2_h - 38, "Поля пружних напружень (зелені стрілки)", size=11, color="#059669", bold=True))
    frags.append(text(p2_x + p2_w / 2, p2_y + p2_h - 18, "Зміцнює матрицю, блокуючи рух дислокацій", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT_DIR, "volume-defects.svg"), w, h, *frags)

if __name__ == "__main__":
    gen_point_defects()
    gen_dislocations()
    gen_grain_boundaries_twins()
    gen_volume_defects()
    print("Successfully generated SVG figures in img/")

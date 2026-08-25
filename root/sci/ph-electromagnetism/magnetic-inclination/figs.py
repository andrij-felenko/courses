# -*- coding: utf-8 -*-
import sys
import os
import math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, line, arrow, rect, circle, fitbox, textbox,
    INK, MUTED, FIELD, POS, NEG, BG, FILL, LINE
)

# Створюємо теку img/, якщо її немає
img_dir = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(img_dir, exist_ok=True)

# -----------------------------------------------------------------------------
# Фігура 1: Розкладання вектора геомагнітного поля B (geomagnetic-vector.svg)
# -----------------------------------------------------------------------------
def gen_geomagnetic_vector():
    w, h = 720, 480
    frags = []
    
    frags.append(text(w / 2, 28, "Розкладання вектора геомагнітного поля B", size=17, bold=True))
    
    ox, oy = 260, 240
    
    frags.append(line(ox, oy, ox, oy + 160, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(arrow(ox, oy, ox, oy + 150, color=INK, sw=2))
    frags.append(text(ox - 18, oy + 155, "Z (Вниз)", size=13, bold=True, color=INK))
    
    x_end_x = ox + 180 * math.cos(math.radians(-35))
    x_end_y = oy + 180 * math.sin(math.radians(-35))
    frags.append(line(ox, oy, x_end_x, x_end_y, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(arrow(ox, oy, x_end_x - 10, x_end_y + 7, color=INK, sw=2))
    frags.append(text(x_end_x + 10, x_end_y - 5, "X (Північ)", size=13, bold=True, color=INK))
    
    y_end_x = ox + 220
    y_end_y = oy
    frags.append(line(ox, oy, y_end_x, y_end_y, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(arrow(ox, oy, y_end_x - 10, y_end_y, color=INK, sw=2))
    frags.append(text(y_end_x + 15, oy + 5, "Y (Схід)", size=13, bold=True, color=INK))
    
    d_deg = 25
    h_len = 220
    h_angle_rad = math.radians(-35 + d_deg)
    hx = ox + h_len * math.cos(h_angle_rad)
    hy = oy + h_len * math.sin(h_angle_rad)
    
    frags.append(line(ox, oy, hx, hy, color=FIELD, sw=2, dash="6,3"))
    frags.append(arrow(ox, oy, hx, hy, color=FIELD, sw=2.5))
    frags.append(text(hx + 15, hy - 5, "H (Горизонтальна складова)", size=13, bold=True, color=FIELD))
    
    x_comp_len = h_len * math.cos(math.radians(d_deg))
    xx = ox + x_comp_len * math.cos(math.radians(-35))
    xy = oy + x_comp_len * math.sin(math.radians(-35))
    frags.append(line(hx, hy, xx, xy, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(ox, oy, xx, xy, color=POS, sw=2))
    frags.append(text(xx - 35, xy - 12, "X", size=13, bold=True, color=POS))
    
    frags.append(line(hx, hy, hx - (xx - ox), hy - (xy - oy), color=MUTED, sw=1, dash="3,3"))
    yx = ox + (hx - xx)
    yy = oy + (hy - xy)
    frags.append(line(ox, oy, yx, yy, color=NEG, sw=2))
    frags.append(text(yx + 5, yy + 18, "Y", size=13, bold=True, color=NEG))
    
    bz = 130
    bx = hx
    by = hy + bz
    
    frags.append(line(hx, hy, bx, by, color=NEG, sw=2, dash="4,4"))
    frags.append(text(bx + 12, hy + bz / 2, "Z (Вертикальна)", size=13, bold=True, color=NEG))
    
    frags.append(arrow(ox, oy, bx, by, color=POS, sw=3))
    frags.append(text(bx + 15, by + 10, "B (Повний вектор)", size=14, bold=True, color=POS))
    
    frags.append(line(ox + 40 * math.cos(math.radians(-35)), oy + 40 * math.sin(math.radians(-35)),
                      ox + 40 * math.cos(h_angle_rad), oy + 40 * math.sin(h_angle_rad), color=FIELD, sw=1.5))
    frags.append(text(ox + 55, oy - 15, "D (Схилення)", size=12, bold=True, color=FIELD))
    
    frags.append(line(ox + 60 * math.cos(h_angle_rad), oy + 60 * math.sin(h_angle_rad),
                      ox + 55 * math.cos(h_angle_rad) + 15, oy + 55 * math.sin(h_angle_rad) + 30, color=POS, sw=1.5))
    frags.append(text(ox + 85, oy + 25, "I (Нахил)", size=12, bold=True, color=POS))
    
    tb1, _, _ = textbox(570, 140,
        "Співвідношення величин:\n"
        "H = B · cos(I)\n"
        "Z = B · sin(I)\n"
        "tan(I) = Z / H\n"
        "tan(D) = Y / X\n"
        "B² = H² + Z² = X² + Y² + Z²",
        size=12, pad=10, fill=FILL, stroke=LINE
    )
    frags.append(tb1)

    tb2, _, _ = textbox(w / 2, 435,
        "У середніх широтах (Україна) кут нахилу I ≈ 65°–69°, тому Z перевищує H більш ніж удвічі (Z ≈ 2.3 · H).",
        size=12, pad=8, fill="#eaf0fd", stroke=NEG
    )
    frags.append(tb2)
    
    return render(os.path.join(img_dir, "geomagnetic-vector.svg"), w, h, *frags)

# -----------------------------------------------------------------------------
# Фігура 2: Принцип роботи інклінатора (dip-circle.svg)
# -----------------------------------------------------------------------------
def gen_dip_circle():
    w, h = 680, 460
    frags = []
    
    frags.append(text(w / 2, 28, "Конструкція та вимірювання за допомогою інклінатора (Dip Circle)", size=17, bold=True))
    
    cx, cy = 240, 230
    r_outer = 150
    r_inner = 130
    
    frags.append(circle(cx, cy, r_outer, fill=BG, stroke=LINE, sw=2))
    frags.append(circle(cx, cy, r_inner, fill=FILL, stroke=MUTED, sw=1))
    
    frags.append(line(cx - r_outer - 15, cy, cx + r_outer + 15, cy, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(text(cx - r_outer - 30, cy + 4, "0° (Горизонт)", size=12, bold=True, color=MUTED))
    frags.append(text(cx + r_outer + 30, cy + 4, "0°", size=12, bold=True, color=MUTED))
    
    frags.append(line(cx, cy - r_outer - 15, cx, cy + r_outer + 15, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(text(cx, cy - r_outer - 22, "90° (Зеніт)", size=12, bold=True, color=MUTED))
    frags.append(text(cx, cy + r_outer + 25, "90° (Надир)", size=12, bold=True, color=MUTED))
    
    for angle in range(0, 360, 15):
        rad = math.radians(angle)
        x1 = cx + r_inner * math.cos(rad)
        y1 = cy + r_inner * math.sin(rad)
        x2 = cx + r_outer * math.cos(rad)
        y2 = cy + r_outer * math.sin(rad)
        frags.append(line(x1, y1, x2, y2, color=LINE, sw=1))
    
    i_angle = 65
    needle_rad = math.radians(i_angle)
    nl = 125
    
    nx1 = cx + nl * math.cos(needle_rad)
    ny1 = cy + nl * math.sin(needle_rad)
    nx2 = cx - nl * math.cos(needle_rad)
    ny2 = cy - nl * math.sin(needle_rad)
    
    frags.append(line(cx, cy, nx1, ny1, color=POS, sw=4))
    frags.append(line(cx, cy, nx2, ny2, color=NEG, sw=4))
    frags.append(circle(cx, cy, 6, fill=INK, stroke=LINE, sw=1))
    
    frags.append(text(nx1 + 15, ny1 + 10, "N (занурюється)", size=13, bold=True, color=POS))
    frags.append(text(nx2 - 20, ny2 - 10, "S", size=13, bold=True, color=NEG))
    
    frags.append(line(cx + 60, cy, cx + 60 * math.cos(needle_rad), cy + 60 * math.sin(needle_rad), color=POS, sw=2))
    frags.append(text(cx + 75, cy + 30, "I = 65°", size=14, bold=True, color=POS))
    
    tb_info, _, _ = textbox(520, 210,
        "Принцип вимірювання:\n"
        "1. Інклінатор вирівнюють у\n"
        "   площині магнітного меридіана.\n"
        "2. Голка вільно обертається\n"
        "   на горизонтальній осі.\n"
        "3. Магнітні сили повертають\n"
        "   голку вздовж вектора B.\n"
        "4. Відхилення від горизонталі\n"
        "   показує кут нахилу I.",
        size=12, pad=10, fill=FILL, stroke=LINE
    )
    frags.append(tb_info)
    
    tb_hist, _, _ = textbox(w / 2, 420,
        "Роберт Норман (1581): для усунення важкості голки її переполюсовують і вимірюють двічі.",
        size=12, pad=8, fill="#fdecea", stroke=POS
    )
    frags.append(tb_hist)
    
    return render(os.path.join(img_dir, "dip-circle.svg"), w, h, *frags)

# -----------------------------------------------------------------------------
# Фігура 3: Дипольна модель та зміна нахилу з широтою (dipole-inclination.svg)
# -----------------------------------------------------------------------------
def gen_dipole_inclination():
    w, h = 780, 500
    frags = []
    
    frags.append(text(w / 2, 26, "Розподіл кута магнітного нахилу на Землі (Дипольна модель)", size=17, bold=True))
    
    cx, cy = 240, 240
    r_earth = 120
    
    frags.append(circle(cx, cy, r_earth, fill="#f4f8ff", stroke=LINE, sw=2))
    
    # Осі
    frags.append(line(cx, cy - r_earth - 15, cx, cy + r_earth + 15, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(text(cx, cy - r_earth - 25, "Північний географічний полюс", size=11, bold=True, color=MUTED))
    frags.append(line(cx - r_earth - 15, cy, cx + r_earth + 15, cy, color=MUTED, sw=1.5, dash="4,4"))
    
    # Магнітне поле - вектор 1 (Полюс φ = 90°)
    px1, py1 = cx, cy - r_earth
    frags.append(circle(px1, py1, 5, fill=POS, stroke=LINE))
    frags.append(arrow(px1, py1, px1, py1 + 40, color=POS, sw=2.5))
    frags.append(text(px1 + 10, py1 + 55, "Полюс: I = +90°", size=12, bold=True, color=POS))
    
    # Магнітне поле - вектор 2 (Широта φ = 45°)
    phi2 = math.radians(45)
    px2 = cx + r_earth * math.cos(phi2)
    py2 = cy - r_earth * math.sin(phi2)
    frags.append(circle(px2, py2, 5, fill=POS, stroke=LINE))
    
    b_dx = math.cos(phi2 - math.radians(63.4)) * 40
    b_dy = -math.sin(phi2 - math.radians(63.4)) * 40
    frags.append(arrow(px2, py2, px2 + b_dx, py2 + b_dy, color=POS, sw=2.5))
    frags.append(text(px2 + 45, py2 - 15, "φ = 45°: I ≈ 63.4°", size=12, bold=True, color=POS))
    
    # Магнітне поле - вектор 3 (Екватор φ = 0°)
    px3, py3 = cx + r_earth, cy
    frags.append(circle(px3, py3, 5, fill=FIELD, stroke=LINE))
    frags.append(arrow(px3, py3, px3, py3 - 40, color=FIELD, sw=2.5))
    frags.append(text(px3 + 45, py3 + 15, "Екватор: I = 0°", size=12, bold=True, color=FIELD))
    
    # Блок формули праворуч зверху
    tb_math, _, _ = textbox(570, 150,
        "Теоретична формула диполя:\n\n"
        "  tan(I) = 2 · tan(φ)\n\n"
        "де:\n"
        "• I — кут магнітного нахилу\n"
        "• φ — геомагнітна широта\n\n"
        "Вертикальна складова зростає\n"
        "вдвічі швидше за широту!",
        size=12, pad=10, fill=FILL, stroke=LINE
    )
    frags.append(tb_math)
    
    # Таблиця значень нахилу залежно від широти
    tb_table, _, _ = textbox(570, 350,
        "Широта (φ)  | Кут нахилу (I)\n"
        "------------+----------------\n"
        " 0° (Екватор)|   0.0°\n"
        "15°          |  28.2°\n"
        "30°          |  49.1°\n"
        "50° (Україна)|  67.2°\n"
        "90° (Полюс)  |  90.0°",
        size=11, pad=10, fill="#f4f6f8", stroke=MUTED
    )
    frags.append(tb_table)
    
    # Інженерна висновок знизу
    tb_bot, _, _ = textbox(w / 2, 455,
        "На магнітному екваторі поле горизонтальне, на полюсах — прямовисне, а в Україні поле пірнає під кутом ~67°.",
        size=12, pad=8, fill="#eafaf1", stroke=FIELD
    )
    frags.append(tb_bot)
    
    return render(os.path.join(img_dir, "dipole-inclination.svg"), w, h, *frags)

# -----------------------------------------------------------------------------
# Фігура 4: Проблема крену та компенсація нахилу (tilt-compensation.svg)
# -----------------------------------------------------------------------------
def gen_tilt_compensation():
    w, h = 720, 460
    frags = []
    
    frags.append(text(w / 2, 26, "Вплив крену на вимірювання курсу та алгоритм компенсації", size=17, bold=True))
    
    cx1, cy1 = 180, 180
    frags.append(text(cx1, cy1 - 90, "1. Горизонтальний давач", size=14, bold=True, color=FIELD))
    frags.append(rect(cx1 - 70, cy1 - 50, 140, 100, fill="#eafaf1", stroke=FIELD, sw=2))
    frags.append(text(cx1, cy1 - 20, "Плата в горизонті", size=12, bold=MUTED))
    frags.append(arrow(cx1, cy1, cx1 + 50, cy1, color=FIELD, sw=2))
    frags.append(text(cx1 + 55, cy1 + 4, "B_x = H", size=11, bold=True, color=FIELD))
    frags.append(arrow(cx1, cy1, cx1, cy1 + 70, color=NEG, sw=2))
    frags.append(text(cx1 + 10, cy1 + 65, "B_z = Z", size=11, bold=True, color=NEG))
    frags.append(text(cx1, cy1 + 80, "Похибка курсу: 0°", size=12, bold=True, color=FIELD))
    
    cx2, cy2 = 520, 180
    frags.append(text(cx2, cy2 - 90, "2. Нахилений давач (без компенсації)", size=14, bold=True, color=POS))
    
    frags.append(line(cx2 - 60, cy2 + 20, cx2 + 60, cy2 - 20, color=POS, sw=3))
    frags.append(line(cx2 - 60, cy2 + 20, cx2 - 40, cy2 - 40, color=POS, sw=1.5))
    frags.append(line(cx2 + 60, cy2 - 20, cx2 + 80, cy2 - 80, color=POS, sw=1.5))
    
    frags.append(arrow(cx2, cy2, cx2 + 55, cy2 - 18, color=POS, sw=2))
    frags.append(text(cx2 + 60, cy2 - 25, "X' (виміряно)", size=11, bold=True, color=POS))
    
    frags.append(text(cx2, cy2 + 45, "Z 'проливається' в X'!", size=12, bold=True, color=POS))
    frags.append(text(cx2, cy2 + 65, "Оскільки Z ≈ 2.3 · H,", size=11, color=INK))
    frags.append(text(cx2, cy2 + 82, "при θ = 10° похибка > 40°!", size=12, bold=True, color=POS))
    
    frags.append(line(40, 290, 680, 290, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(w / 2, 312, "Схема алгоритму Tilt Compensation (3D Magnetometer + Accelerometer)", size=14, bold=True))
    
    b1, _, _ = textbox(130, 380, "Акселерометр\n[a_x, a_y, a_z]", size=12, pad=8, fill=FILL, stroke=LINE)
    frags.append(b1)
    frags.append(arrow(190, 380, 250, 380, color=INK, sw=1.5))
    
    b2, _, _ = textbox(320, 380, "Обчислення кутів\nθ (Pitch), φ (Roll)", size=12, pad=8, fill="#eaf0fd", stroke=NEG)
    frags.append(b2)
    frags.append(arrow(390, 380, 450, 380, color=INK, sw=1.5))
    
    b3, _, _ = textbox(560, 380, "Проекція на горизонт:\nB_xH, B_yH\nАзимут ψ = atan2(-B_yH, B_xH)", size=12, pad=8, fill="#eafaf1", stroke=FIELD)
    frags.append(b3)
    
    frags.append(arrow(560, 440, 560, 418, color=POS, sw=1.5))
    frags.append(text(560, 450, "Магнітометр [B_x, B_y, B_z]", size=11, bold=True, color=POS))
    
    return render(os.path.join(img_dir, "tilt-compensation.svg"), w, h, *frags)

# -----------------------------------------------------------------------------
# Головний виклик
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    gen_geomagnetic_vector()
    gen_dip_circle()
    gen_dipole_inclination()
    gen_tilt_compensation()
    print("Всі 4 SVG-фігури успішно згенеровано у теці img/")

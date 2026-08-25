# -*- coding: utf-8 -*-
"""
figs.py — Генерація SVG-фігур для теми «Пластична деформація і границя плинності»
Книга: physics, розділ: condensed-matter-physics, slug: plastic-deformation
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# Фігура 1: stress-strain-plasticity.svg (Графік деформування та границя плинності)
# -----------------------------------------------------------------------------
def gen_fig1():
    path = os.path.join(IMG_DIR, 'stress-strain-plasticity.svg')
    w, h = 740, 460
    frags = []
    
    ox, oy = 80, 390
    axis_w, axis_h = 610, 330
    
    frags.append(line(ox, oy, ox + axis_w, oy, color=MUTED, sw=1.5))
    frags.append(arrow(ox, oy, ox + axis_w + 15, oy, color=INK, sw=1.8))
    frags.append(arrow(ox, oy, ox, oy - axis_h - 15, color=INK, sw=1.8))
    
    frags.append(text(ox + axis_w + 20, oy + 5, "Деформація ε", size=13, anchor="start", bold=True))
    frags.append(text(ox - 10, oy - axis_h - 20, "Напруження σ (МПа)", size=13, anchor="middle", bold=True))
    
    px, py = ox + 70, oy - 140
    yx, yy = ox + 110, oy - 180
    ux, uy = ox + 410, oy - 290
    fx, fy = ox + 560, oy - 210
    
    path_d = f"M {ox} {oy} L {px} {py} Q {px+20} {yy} {yx} {yy} C {yx+100} {yy-80} {ux-100} {uy} {ux} {uy} Q {ux+80} {uy+10} {fx} {fy}"
    frags.append(f'<path d="{path_d}" fill="none" stroke="{NEG}" stroke-width="3"/>')
    
    un_x1, un_y1 = ox + 280, oy - 235
    un_x0 = un_x1 - (oy - un_y1) / 2.0
    frags.append(line(un_x0, oy, un_x1, un_y1, color=POS, sw=1.8, dash="5,4"))
    frags.append(circle(un_x1, un_y1, 4, fill=POS, stroke=INK, sw=1))
    frags.append(arrow(un_x1 - 25, un_y1 + 45, un_x1 - 5, un_y1 + 10, color=POS, sw=1.5))
    frags.append(text(un_x1 - 30, un_y1 + 60, "Розвантаження", size=12, color=POS, anchor="end", bold=True))
    
    y02_x = ox + 35
    frags.append(line(y02_x, oy, y02_x + 90, oy - 180, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(ox, oy - 180, yx, oy - 180, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(circle(yx, yy, 5, fill="#ffffff", stroke=NEG, sw=2))
    
    frags.append(line(ox, uy, ux, uy, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(circle(ux, uy, 5, fill="#ffffff", stroke=NEG, sw=2))
    frags.append(circle(fx, fy, 5, fill=INK, stroke=INK, sw=1))
    
    frags.append(rect(ox, oy + 12, un_x0 - ox, 14, fill="#eaf0fd", stroke="none", rx=2))
    frags.append(line(ox, oy + 5, ox, oy + 28, color=MUTED, sw=1))
    frags.append(line(un_x0, oy + 5, un_x0, oy + 28, color=MUTED, sw=1))
    frags.append(text((ox + un_x0)/2, oy + 24, "Залишкова деформація ε_p", size=11, color=NEG, anchor="middle", bold=True))
    
    frags.append(rect(un_x0, oy + 12, un_x1 - un_x0, 14, fill="#fdecea", stroke="none", rx=2))
    frags.append(line(un_x1, oy + 5, un_x1, oy + 28, color=MUTED, sw=1))
    frags.append(text((un_x0 + un_x1)/2, oy + 24, "Пружна ε_e", size=11, color=POS, anchor="middle", bold=True))
    
    frags.append(line(y02_x, oy - 4, y02_x, oy + 6, color=INK, sw=1.5))
    frags.append(text(y02_x, oy + 18, "0.2%", size=11, color=INK, anchor="middle"))
    
    frags.append(text(ox - 12, yy + 4, "σ_y (σ₀.₂)", size=12, color=INK, anchor="end", bold=True))
    frags.append(text(ox - 12, uy + 4, "σ_uts", size=12, color=INK, anchor="end", bold=True))
    
    box1, w1, h1 = textbox(ox + 90, oy - 60, "Пружна область\n(Закон Гука σ = E·ε)", size=11, pad=6, fill="#f4f6f8", stroke=MUTED)
    frags.append(box1)
    
    box2, w2, h2 = textbox(ox + 260, oy - 280, "Деформаційне зміцнення\n(Наклеп, накопичення дислокацій)", size=11, pad=6, fill="#eaf0fd", stroke=NEG)
    frags.append(box2)
    
    box3, w3, h3 = textbox(ox + 510, oy - 130, "Утворення шийки\nта руйнування", size=11, pad=6, fill="#fdecea", stroke=POS)
    frags.append(box3)
    
    render(path, w, h, *frags)

# -----------------------------------------------------------------------------
# Фігура 2: dislocation-slip-plane.svg (Схема ковзання дислокацій)
# -----------------------------------------------------------------------------
def gen_fig2():
    path = os.path.join(IMG_DIR, 'dislocation-slip-plane.svg')
    w, h = 720, 440
    frags = []
    
    lx0, ly0 = 50, 60
    frags.append(text(lx0 + 130, ly0, "а) Зайва півплощина атомів (дислокація)", size=13, bold=True, anchor="middle"))
    
    r_atom = 9
    dx_atom = 36
    dy_atom = 34
    
    top_y = ly0 + 40
    for row in range(3):
        ay = top_y + row * dy_atom
        for col in range(7):
            ax = lx0 + 20 + col * dx_atom
            if col == 3:
                frags.append(circle(ax, ay, r_atom, fill="#fdecea", stroke=POS, sw=2))
            else:
                frags.append(circle(ax, ay, r_atom, fill="#eaf0fd", stroke=NEG, sw=1.5))
    
    slip_y = top_y + 2 * dy_atom + dy_atom / 2
    frags.append(line(lx0, slip_y, lx0 + 260, slip_y, color=FIELD, sw=2, dash="6,3"))
    frags.append(text(lx0 + 265, slip_y + 4, "Площина ковзання", size=11, color=FIELD, anchor="start", bold=True))
    
    disloc_x = lx0 + 20 + 3 * dx_atom
    disloc_y = top_y + 2 * dy_atom + 12
    frags.append(line(disloc_x, disloc_y - 10, disloc_x, disloc_y + 6, color=POS, sw=2.5))
    frags.append(line(disloc_x - 8, disloc_y + 6, disloc_x + 8, disloc_y + 6, color=POS, sw=2.5))
    frags.append(text(disloc_x + 14, disloc_y, "Ядро дислокації ⊥", size=11, color=POS, anchor="start", bold=True))
    
    bot_y = slip_y + dy_atom / 2 + 5
    for row in range(3):
        ay = bot_y + row * dy_atom
        for col in range(7):
            if col == 3:
                continue
            shift_x = 0
            if col < 3:
                shift_x = dx_atom / 2
            else:
                shift_x = -dx_atom / 2
            ax = lx0 + 20 + col * dx_atom + shift_x
            frags.append(circle(ax, ay, r_atom, fill="#eaf0fd", stroke=NEG, sw=1.5))
            
    frags.append(arrow(lx0 + 20, top_y - 20, lx0 + 120, top_y - 20, color=POS, sw=2))
    frags.append(text(lx0 + 130, top_y - 23, "τ (зсув)", size=12, color=POS, anchor="start", bold=True))
    frags.append(arrow(lx0 + 240, bot_y + 3 * dy_atom + 10, lx0 + 140, bot_y + 3 * dy_atom + 10, color=POS, sw=2))
    frags.append(text(lx0 + 130, bot_y + 3 * dy_atom + 25, "τ (зсув)", size=12, color=POS, anchor="end", bold=True))

    frags.append(arrow(lx0 + 295, ly0 + 140, lx0 + 355, ly0 + 140, color=INK, sw=2.5))
    frags.append(text(lx0 + 325, ly0 + 120, "Рух дислокації\nчерез кристал", size=11, color=INK, anchor="middle"))

    rx0 = 400
    frags.append(text(rx0 + 140, ly0, "б) Залишковий пластичний зсув (вектор b)", size=13, bold=True, anchor="middle"))
    
    for row in range(3):
        ay = top_y + row * dy_atom
        for col in range(6):
            ax = rx0 + 50 + col * dx_atom
            frags.append(circle(ax, ay, r_atom, fill="#eaf0fd", stroke=NEG, sw=1.5))
            
    frags.append(line(rx0 + 10, slip_y, rx0 + 270, slip_y, color=FIELD, sw=2, dash="6,3"))
    
    for row in range(3):
        ay = bot_y + row * dy_atom
        for col in range(6):
            ax = rx0 + 14 + col * dx_atom
            frags.append(circle(ax, ay, r_atom, fill="#eaf0fd", stroke=NEG, sw=1.5))
            
    b_x1 = rx0 + 14
    b_x2 = rx0 + 50
    b_y = slip_y
    frags.append(line(b_x1, b_y - 15, b_x1, b_y + 15, color=POS, sw=1.5))
    frags.append(line(b_x2, b_y - 15, b_x2, b_y + 15, color=POS, sw=1.5))
    frags.append(arrow(b_x1, b_y - 25, b_x2, b_y - 25, color=POS, sw=2))
    frags.append(text((b_x1 + b_x2)/2, b_y - 32, "b (вектор Бюргерса)", size=11, color=POS, anchor="middle", bold=True))
    
    box, bw, bh = textbox(w/2, h - 35, "Дислокація послідовно розриває та переполуччає атоми колонка за колонкою,\nзнижуючи критичне напруження зсуву в 1000 разів порівняно з ідеальним кристалом.", size=12, pad=8, fill="#f4f6f8", stroke=MUTED)
    frags.append(box)
    
    render(path, w, h, *frags)

# -----------------------------------------------------------------------------
# Фігура 3: schmid-law-geometry.svg (Геометрія закону Шміда)
# -----------------------------------------------------------------------------
def gen_fig3():
    path = os.path.join(IMG_DIR, 'schmid-law-geometry.svg')
    w, h = 760, 460
    frags = []
    
    cx, cy = 160, 220
    cyl_w, cyl_h = 90, 260
    
    top_y = cy - cyl_h / 2
    bot_y = cy + cyl_h / 2
    
    frags.append(rect(cx - cyl_w/2, top_y, cyl_w, cyl_h, fill="#f4f6f8", stroke=INK, sw=2, rx=4))
    
    frags.append(arrow(cx, top_y, cx, top_y - 65, color=POS, sw=2.5))
    frags.append(text(cx + 15, top_y - 45, "Сила F (осьовий розтяг)", size=13, color=POS, anchor="start", bold=True))
    
    frags.append(arrow(cx, bot_y, cx, bot_y + 65, color=POS, sw=2.5))
    frags.append(text(cx + 15, bot_y + 45, "Сила F", size=13, color=POS, anchor="start", bold=True))
    
    frags.append(line(cx, top_y - 70, cx, bot_y + 70, color=MUTED, sw=1.2, dash="6,4"))
    frags.append(text(cx - 15, top_y - 50, "Осьовий напрямок n", size=11, color=MUTED, anchor="end"))
    
    plane_y = cy
    angle_deg = 35
    
    frags.append(f'<ellipse cx="{cx}" cy="{plane_y}" rx="{cyl_w/2 + 5}" ry="25" transform="rotate(-{angle_deg} {cx} {plane_y})" fill="#eaf0fd" stroke="{NEG}" stroke-width="2"/>')
    
    norm_len = 90
    norm_angle = 90 - angle_deg
    n_rad = math.radians(norm_angle)
    nx = cx + norm_len * math.sin(n_rad)
    ny = plane_y - norm_len * math.cos(n_rad)
    
    frags.append(arrow(cx, plane_y, nx, ny, color=NEG, sw=2))
    frags.append(text(nx - 12, ny - 12, "Нормаль n_s", size=12, color=NEG, anchor="end", bold=True))
    frags.append(text(cx + 18, plane_y - 45, "Кут φ", size=12, color=NEG, bold=True))
    
    slip_len = 85
    s_angle = angle_deg
    s_rad = math.radians(s_angle)
    sx = cx + slip_len * math.cos(s_rad)
    sy = plane_y - slip_len * math.sin(s_rad)
    
    frags.append(arrow(cx, plane_y, sx, sy, color=FIELD, sw=2.2))
    frags.append(text(sx + 15, sy - 5, "Напрямок s", size=12, color=FIELD, anchor="start", bold=True))
    frags.append(text(cx + 38, plane_y - 5, "Кут λ", size=12, color=FIELD, bold=True))
    
    # Винесений підпис для площини ковзання
    frags.append(text(cx - 65, plane_y + 40, "Площина ковзання A_s = A₀ / cos φ", size=11, color=NEG, anchor="end", bold=True))
    frags.append(line(cx - 60, plane_y + 35, cx - 15, plane_y + 5, color=NEG, sw=1.2, dash="3,3"))

    rx = 460
    ry = 60
    
    fbox, fw, fh = textbox(rx + 120, ry + 150, 
                           "Формула розрахованого зсувного напруження:\n\n"
                           "τ = (F_s) / A_s = (F · cos λ) / (A₀ / cos φ)\n\n"
                           "τ = σ · cos φ · cos λ = σ · m\n\n"
                           "де m = cos φ · cos λ — фактор Шміда (0 ≤ m ≤ 0.5)",
                           size=13, pad=12, fill="#ffffff", stroke=INK, sw=1.8)
    frags.append(fbox)
    
    ybox, yw, yh = textbox(rx + 120, ry + 310,
                           "Умова початку плинності (Критичне напруження):\n\n"
                           "τ_max = τ_crss   ⇒   σ_y = (τ_crss) / m_max\n\n"
                           "Максимальне значення m = 0.5 при φ = λ = 45°:\n"
                           "Мінімальна границя плинності σ_y = 2 · τ_crss",
                           size=12, pad=10, fill="#eaf0fd", stroke=NEG, sw=1.5)
    frags.append(ybox)
    
    render(path, w, h, *frags)

# -----------------------------------------------------------------------------
# Фігура 4: dislocation-interaction-hardening.svg (Механізм деформаційного зміцнення)
# -----------------------------------------------------------------------------
def gen_fig4():
    path = os.path.join(IMG_DIR, 'dislocation-interaction-hardening.svg')
    w, h = 720, 440
    frags = []
    
    box_w, box_h = 290, 230
    y0 = 70
    
    lx = 50
    frags.append(rect(lx, y0, box_w, box_h, fill="#ffffff", stroke=LINE, sw=1.8, rx=6))
    frags.append(text(lx + box_w/2, y0 - 15, "а) Відпалений метал (ρ ~ 10⁶ см⁻²)", size=13, bold=True, color=INK))
    
    frags.append(line(lx + 40, y0 + 30, lx + 120, y0 + 190, color=NEG, sw=2))
    frags.append(text(lx + 70, y0 + 100, "⊥", size=16, color=NEG, bold=True))
    
    frags.append(line(lx + 150, y0 + 50, lx + 250, y0 + 160, color=NEG, sw=2))
    frags.append(text(lx + 190, y0 + 95, "⊥", size=16, color=NEG, bold=True))
    
    frags.append(text(lx + box_w/2, y0 + box_h - 20, "Вільний рух дислокацій:\nНизький опір (мала σ_y)", size=11, color=NEG, anchor="middle"))
    
    rx = 380
    frags.append(rect(rx, y0, box_w, box_h, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(rx + box_w/2, y0 - 15, "б) Деформований метал (ρ ~ 10¹² см⁻²)", size=13, bold=True, color=POS))
    
    for i in range(8):
        x1 = rx + 20 + i * 32
        y1 = y0 + 20 + (i % 3) * 15
        x2 = rx + 40 + i * 28
        y2 = y0 + box_h - 20 - (i % 4) * 20
        frags.append(line(x1, y1, x2, y2, color=POS, sw=1.8))
        
    for j in range(6):
        hx1 = rx + 20 + (j % 2) * 20
        hy1 = y0 + 40 + j * 30
        hx2 = rx + box_w - 20 - (j % 3) * 15
        hy2 = y0 + 50 + j * 26
        frags.append(line(hx1, hy1, hx2, hy2, color=NEG, sw=1.8))
        
    frags.append(circle(rx + 110, y0 + 100, 6, fill=POS, stroke=INK, sw=1))
    frags.append(circle(rx + 180, y0 + 140, 6, fill=POS, stroke=INK, sw=1))
    frags.append(text(rx + 110, y0 + 85, "Вузол перетину", size=10, color=POS, anchor="middle", bold=True))
    
    frags.append(text(rx + box_w/2, y0 + box_h - 20, "Взаємне блокування дислокацій:\nВисокий опір (висока σ_y)", size=11, color=POS, anchor="middle", bold=True))
    
    tbox, tw, th = textbox(w/2, h - 45,
                           "Рівняння деформаційного зміцнення Тейлора:\n"
                           "τ = τ₀ + α · G · b · √ρ\n"
                           "Опір зсуву τ пропорційний квадратному кореню з щільності дислокацій √ρ",
                           size=13, pad=10, fill="#ffffff", stroke=INK, sw=1.8)
    frags.append(tbox)
    
    render(path, w, h, *frags)

if __name__ == '__main__':
    gen_fig1()
    gen_fig2()
    gen_fig3()
    gen_fig4()
    print("Всі 4 фігури успішно перегенеровано.")

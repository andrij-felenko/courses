# -*- coding: utf-8 -*-
import os
import sys
import math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
os.makedirs(OUT_DIR, exist_ok=True)

def make_binding_energy_curve():
    """Фігура 1: Крива питомої енергії зв'язку E_b/A від масового числа A."""
    w, h = 850, 520
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    # Заголовок фігури
    out.append(text(w/2, 32, "Залежність питомої енергії зв'язку E_b/A від масового числа A", size=18, bold=True))
    
    # Осі координат
    ox, oy = 140, 430
    gw, gh = 660, 340
    
    # Засічки та сітка по Y (0 до 10 МеВ/нуклон)
    for y_val in range(0, 11, 2):
        y_pos = oy - (y_val / 10.0) * gh
        out.append(line(ox, y_pos, ox + gw, y_pos, color="#e0e0e0", sw=1, dash="4,4"))
        out.append(text(ox - 25, y_pos + 5, f"{y_val}", size=13, anchor="end"))
    
    # Засічки та сітка по X (A = 0 до 250)
    for x_val in range(0, 251, 50):
        x_pos = ox + (x_val / 250.0) * gw
        out.append(line(x_pos, oy, x_pos, oy - gh, color="#e0e0e0", sw=1, dash="4,4"))
        out.append(text(x_pos, oy + 25, f"{x_val}", size=13, anchor="middle"))
    
    # Основні осі
    out.append(line(ox, oy, ox + gw + 20, oy, color=LINE, sw=2))
    out.append(line(ox, oy, ox, oy - gh - 20, color=LINE, sw=2))
    
    # Підписи осей
    out.append(text(ox + gw / 2, oy + 55, "Масове число A (кількість нуклонів)", size=14, bold=True))
    out.append(text(ox + 10, oy - gh - 15, "E_b / A (МеВ / нуклон)", size=13, bold=True, anchor="start"))
    
    # Зони синтезу та поділу
    out.append(rect(ox + 10, oy - gh, 150, 40, fill="#e8f8f5", stroke="#27ae60", sw=1.5, rx=4))
    out.append(text(ox + 85, oy - gh + 25, "Зона синтезу (Fusion)", size=12, color="#1e8449", bold=True))
    
    out.append(rect(ox + 420, oy - gh, 220, 40, fill="#fef9e7", stroke="#d35400", sw=1.5, rx=4))
    out.append(text(ox + 530, oy - gh + 25, "Зона поділу (Fission)", size=12, color="#a04000", bold=True))
    
    # Точки кривої (A, E_b/A в MeV)
    points_data = [
        (1, 0.0),      # 1H
        (2, 1.11),     # 2H
        (3, 2.83),     # 3H / 3He
        (4, 7.07),     # 4He (пік)
        (6, 5.33),     # 6Li
        (12, 7.68),    # 12C
        (16, 7.98),    # 16O
        (24, 8.26),    # 24Mg
        (40, 8.55),    # 40Ca
        (56, 8.79),    # 56Fe (максимум)
        (62, 8.79),    # 62Ni
        (84, 8.6),     # 84Kr
        (120, 8.5),    # 120Sn
        (160, 8.1),    # 160Gd
        (208, 7.86),   # 208Pb
        (238, 7.57),   # 238U
    ]
    
    # Побудова гладкої кривої через плавні відрізки
    path_pts = []
    for a_val, e_val in points_data:
        px = ox + (a_val / 250.0) * gw
        py = oy - (e_val / 10.0) * gh
        path_pts.append((px, py))
    
    # Намалюємо криву лініями
    for i in range(len(path_pts) - 1):
        x1, y1 = path_pts[i]
        x2, y2 = path_pts[i+1]
        out.append(line(x1, y1, x2, y2, color=NEG, sw=3))
    
    # Позначення ключових нуклідів
    key_nuclides = [
        (2, 1.11, "²H", "right"),
        (4, 7.07, "⁴He (7.07)", "topleft"),
        (12, 7.68, "¹²C", "below"),
        (16, 7.98, "¹⁶O", "above"),
        (56, 8.79, "⁵⁶Fe (8.79 МеВ)", "above"),
        (208, 7.86, "²⁰⁸Pb", "above"),
        (238, 7.57, "²³⁸U (7.57 МеВ)", "above"),
    ]
    
    for a_val, e_val, label, pos in key_nuclides:
        px = ox + (a_val / 250.0) * gw
        py = oy - (e_val / 10.0) * gh
        out.append(circle(px, py, 5, fill=POS, stroke=LINE, sw=1.5))
        
        tx, ty = px, py
        anchor = "middle"
        if pos == "above":
            ty = py - 12
        elif pos == "below":
            ty = py + 20
        elif pos == "right":
            tx = px + 15
            ty = py + 4
            anchor = "start"
        elif pos == "topright":
            tx = px + 15
            ty = py - 15
            anchor = "start"
        elif pos == "topleft":
            tx = px - 12
            ty = py - 12
            anchor = "end"
        elif pos == "left":
            tx = px - 15
            ty = py + 4
            anchor = "end"
            
        out.append(text(tx, ty, label, size=12, bold=True, color=INK, anchor=anchor))

    out.append('</svg>')
    with open(os.path.join(OUT_DIR, 'binding-energy-curve.svg'), 'w', encoding='utf-8') as f:
        f.write("\n".join(out))

def make_weizsacker_terms_breakdown():
    """Фігура 2: 5 доданків напівемпіричної формули Вейцзеккера."""
    w, h = 900, 500
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    out.append(text(w/2, 30, "П'ять доданків напівемпіричної формули маси Вейцзеккера (SEMF)", size=18, bold=True))
    
    # 5 блоків доданків
    terms = [
        {
            "name": "1. Об'ємна E_v",
            "formula": "+ a_v · A",
            "desc": "Притягання між близькими нуклонами. Пропорційна об'єму (A).",
            "color": "#d4efdf",
            "stroke": "#27ae60",
            "val": "a_v ≈ 15.75 МеВ"
        },
        {
            "name": "2. Поверхнева E_s",
            "formula": "- a_s · A^(2/3)",
            "desc": "Поверхневі нуклони мають менше сусідів. Пропорційна площі.",
            "color": "#fadbd8",
            "stroke": "#c0392b",
            "val": "a_s ≈ 17.80 МеВ"
        },
        {
            "name": "3. Кулонівська E_c",
            "formula": "- a_c · Z² / A^(1/3)",
            "desc": "Електростатичне відштовхування між протонами.",
            "color": "#ebf5fb",
            "stroke": "#2980b9",
            "val": "a_c ≈ 0.711 МеВ"
        },
        {
            "name": "4. Енергія асиметрії E_a",
            "formula": "- a_a · (A-2Z)² / A",
            "desc": "Квантовий ефект Паулі. Мінімум енергії при N = Z.",
            "color": "#f5eeef",
            "stroke": "#8e44ad",
            "val": "a_a ≈ 23.70 МеВ"
        },
        {
            "name": "5. Енергія спарювання E_p",
            "formula": "+ δ(Z, A)",
            "desc": "Спінове спарювання нуклонів: парно-парні (+), непарні (-).",
            "color": "#fef9e7",
            "stroke": "#d35400",
            "val": "a_p ≈ 11.18 МеВ"
        }
    ]
    
    box_w = 160
    gap = 15
    start_x = 25
    y_top = 70
    box_h = 390
    
    for i, t in enumerate(terms):
        bx = start_x + i * (box_w + gap)
        out.append(rect(bx, y_top, box_w, box_h, fill=t["color"], stroke=t["stroke"], sw=2, rx=8))
        
        # Назва
        out.append(text(bx + box_w/2, y_top + 30, t["name"], size=13, bold=True, color=INK))
        out.append(line(bx + 10, y_top + 45, bx + box_w - 10, y_top + 45, color=t["stroke"], sw=1.5))
        
        # Формула
        out.append(rect(bx + 10, y_top + 60, box_w - 20, 36, fill="#ffffff", stroke=t["stroke"], sw=1, rx=4))
        out.append(text(bx + box_w/2, y_top + 83, t["formula"], size=12, bold=True, color=POS if "-" in t["formula"] else FIELD))
        
        # Опис (мультилайн)
        words = t["desc"].split(" ")
        lines_desc = []
        cur_line = []
        for w_item in words:
            cur_line.append(w_item)
            if len(" ".join(cur_line)) > 15:
                lines_desc.append(" ".join(cur_line[:-1]))
                cur_line = [w_item]
        if cur_line:
            lines_desc.append(" ".join(cur_line))
            
        ty = y_top + 130
        for ld in lines_desc:
            out.append(text(bx + box_w/2, ty, ld, size=11, color=INK))
            ty += 18
            
        # Схематичний рисунок всередині блоку
        cy_draw = y_top + 280
        if i == 0: # Volume
            out.append(circle(bx + box_w/2, cy_draw, 35, fill="#a9dfbf", stroke=FIELD, sw=2))
            out.append(text(bx + box_w/2, cy_draw + 4, "Ядро", size=11, bold=True))
        elif i == 1: # Surface
            out.append(circle(bx + box_w/2, cy_draw, 35, fill="#f5b7b1", stroke=POS, sw=2))
            out.append(text(bx + box_w/2, cy_draw + 4, "Поверхня", size=11, bold=True))
        elif i == 2: # Coulomb
            out.append(circle(bx + box_w/2 - 15, cy_draw - 10, 10, fill="#a9cce3", stroke=NEG, sw=1.5))
            out.append(text(bx + box_w/2 - 15, cy_draw - 6, "+", size=12, bold=True, color=NEG))
            out.append(circle(bx + box_w/2 + 15, cy_draw + 10, 10, fill="#a9cce3", stroke=NEG, sw=1.5))
            out.append(text(bx + box_w/2 + 15, cy_draw + 14, "+", size=12, bold=True, color=NEG))
            out.append(line(bx + box_w/2 - 5, cy_draw - 5, bx + box_w/2 + 5, cy_draw + 5, color=POS, sw=2, dash="2,2"))
        elif i == 3: # Asymmetry
            out.append(rect(bx + box_w/2 - 25, cy_draw - 25, 20, 50, fill="#d7bde2", stroke="#8e44ad", sw=1.5, rx=3))
            out.append(text(bx + box_w/2 - 15, cy_draw + 4, "Z", size=11, bold=True))
            out.append(rect(bx + box_w/2 + 5, cy_draw - 35, 20, 60, fill="#bb8fce", stroke="#8e44ad", sw=1.5, rx=3))
            out.append(text(bx + box_w/2 + 15, cy_draw + 4, "N", size=11, bold=True))
        elif i == 4: # Pairing
            out.append(circle(bx + box_w/2 - 12, cy_draw, 10, fill="#f9e79f", stroke=LINE, sw=1.5))
            out.append(circle(bx + box_w/2 + 12, cy_draw, 10, fill="#f9e79f", stroke=LINE, sw=1.5))
            out.append(line(bx + box_w/2 - 2, cy_draw, bx + box_w/2 + 2, cy_draw, color=LINE, sw=2))
            out.append(text(bx + box_w/2, cy_draw + 25, "Пара ↑↓", size=10, bold=True))
            
        # Коефіцієнт
        out.append(rect(bx + 10, y_top + box_h - 40, box_w - 20, 28, fill="#ffffff", stroke=t["stroke"], sw=1, rx=4))
        out.append(text(bx + box_w/2, y_top + box_h - 22, t["val"], size=11, bold=True))

    out.append('</svg>')
    with open(os.path.join(OUT_DIR, 'weizsacker-terms-breakdown.svg'), 'w', encoding='utf-8') as f:
        f.write("\n".join(out))

def make_mass_valley_parabola():
    """Фігура 3: Парабола мас для ізобарного ланцюжка та бета-розпади."""
    w, h = 800, 500
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    out.append(text(w/2, 32, "Парабола мас для ізобарного ланцюжка (A = const) та бета-розпади", size=18, bold=True))
    
    ox, oy = 140, 430
    gw, gh = 610, 350
    
    out.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2))
    out.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2))
    
    out.append(text(ox + gw/2, oy + 45, "Кількість протонів Z", size=14, bold=True))
    out.append(text(ox + 10, oy - gh - 15, "Маса ядра M(Z, A)", size=13, bold=True, anchor="start"))
    
    # Намалюємо гладку параболу всередині меж [oy-gh, oy]
    z_min_x = ox + gw / 2
    y_min = oy - 80
    
    pts = []
    for step in range(-80, 81, 5):
        x = z_min_x + step * 3.2
        y_val = y_min - (step / 10.0)**2 * 38.0
        if oy - gh <= y_val <= oy:
            pts.append((x, y_val))
        
    for i in range(len(pts) - 1):
        out.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color=NEG, sw=2.5))
        
    # Точки ізобарів (Z_min - 3, Z_min - 2, Z_min - 1, Z_min, Z_min + 1, Z_min + 2, Z_min + 3)
    isobars = [
        (-3, POS),
        (-2, POS),
        (-1, POS),
        (0, FIELD),
        (1, NEG),
        (2, NEG),
        (3, NEG),
    ]
    
    for offset, col in isobars:
        px = z_min_x + offset * 70
        py = y_min - (offset * 7.0)**2 * 0.35
        if py < oy - gh + 30:
            continue
        out.append(circle(px, py, 7, fill=col, stroke=LINE, sw=1.5))
        
        # Записати Z значення під віссю
        lbl = f"Z_min{offset:+d}" if offset != 0 else "Z_min"
        out.append(text(px, oy + 20, lbl, size=11, bold=True))
        
        if offset < 0:
            # Стрілка β- вправо до мінімуму
            out.append(line(px + 10, py, px + 50, py + 12, color=POS, sw=2, dash="3,3"))
            out.append(text(px + 30, py - 12, "β⁻", size=12, bold=True, color=POS))
        elif offset > 0:
            # Стрілка β+ вліво до мінімуму
            out.append(line(px - 10, py, px - 50, py + 12, color=NEG, sw=2, dash="3,3"))
            out.append(text(px - 30, py - 12, "β⁺/EC", size=12, bold=True, color=NEG))
        else:
            # Стійке ядро - напис прямо над точкою
            out.append(rect(px - 65, py - 55, 130, 40, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=6))
            out.append(text(px, py - 38, "Дно долини мас", size=11, bold=True, color=FIELD))
            out.append(text(px, py - 22, "∂E_b / ∂Z = 0", size=10, color=INK))

    out.append('</svg>')
    with open(os.path.join(OUT_DIR, 'mass-valley-parabola.svg'), 'w', encoding='utf-8') as f:
        f.write("\n".join(out))

def make_fission_drop_deformation():
    """Фігура 4: Стадії деформації та поділу ядра в краплинній моделі."""
    w, h = 850, 400
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
    
    out.append(text(w/2, 30, "Стадії деформації та ділення атомного ядра в краплинній моделі", size=18, bold=True))
    
    stages = [
        {"title": "1. Сферичне ядро", "desc": "Мінімальна площа поверхні E_s", "y_center": 180, "x_center": 110},
        {"title": "2. Еліпсоїд (збудження)", "desc": "Конфлікт E_s та E_c", "y_center": 180, "x_center": 300},
        {"title": "3. Утворення шийки", "desc": "Гантелеподібна форма", "y_center": 180, "x_center": 510},
        {"title": "4. Розрив та осколки", "desc": "Кулонівське розлітання + n", "y_center": 180, "x_center": 730},
    ]
    
    for i, st in enumerate(stages):
        cx, cy = st["x_center"], st["y_center"]
        
        # Рамка стадії
        out.append(rect(cx - 95, 60, 190, 300, fill="#fcfcfc", stroke="#bdc3c7", sw=1.5, rx=8))
        out.append(text(cx, 85, st["title"], size=13, bold=True, color=INK))
        out.append(text(cx, 345, st["desc"], size=11, color=MUTED))
        
        # Рисування форми ядра
        if i == 0:
            out.append(circle(cx, cy, 45, fill="#d6eaf8", stroke=NEG, sw=2))
            out.append(text(cx, cy + 4, "²³⁵U", size=13, bold=True))
        elif i == 1:
            out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="60" ry="35" fill="#fdebd0" stroke="#d35400" stroke-width="2"/>')
            out.append(text(cx, cy + 4, "Збуджене ядро", size=11, bold=True))
        elif i == 2:
            # Гантель
            out.append(circle(cx - 30, cy, 32, fill="#fadbd8", stroke=POS, sw=2))
            out.append(circle(cx + 30, cy, 32, fill="#fadbd8", stroke=POS, sw=2))
            out.append(rect(cx - 15, cy - 12, 30, 24, fill="#fadbd8", stroke="none"))
            out.append(line(cx - 15, cy - 12, cx + 15, cy - 12, color=POS, sw=2))
            out.append(line(cx - 15, cy + 12, cx + 15, cy + 12, color=POS, sw=2))
            out.append(text(cx, cy + 4, "Шийка", size=11, bold=True, color=POS))
        elif i == 3:
            # Двоє осколків
            out.append(circle(cx - 45, cy, 28, fill="#d4efdf", stroke=FIELD, sw=2))
            out.append(text(cx - 45, cy + 4, "Осколок 1", size=10, bold=True))
            out.append(circle(cx + 45, cy, 28, fill="#d4efdf", stroke=FIELD, sw=2))
            out.append(text(cx + 45, cy + 4, "Осколок 2", size=10, bold=True))
            
            # Нейтрони поділу
            out.append(circle(cx, cy - 35, 6, fill="#f9e79f", stroke=LINE, sw=1))
            out.append(text(cx, cy - 31, "n", size=9, bold=True))
            out.append(circle(cx, cy + 35, 6, fill="#f9e79f", stroke=LINE, sw=1))
            out.append(text(cx, cy + 39, "n", size=9, bold=True))
            
            # Стрілки розлітання
            out.append(line(cx - 75, cy, cx - 90, cy, color=POS, sw=2))
            out.append(line(cx + 75, cy, cx + 90, cy, color=POS, sw=2))

        # Стрілка переходу між стадіями
        if i < 3:
            out.append(line(cx + 95, cy, cx + 115, cy, color=LINE, sw=2))
            out.append(text(cx + 105, cy - 10, "→", size=14, bold=True))

    out.append('</svg>')
    with open(os.path.join(OUT_DIR, 'binding-energy-curve.svg'), 'w', encoding='utf-8') as f:
        f.write("\n".join(out))

if __name__ == '__main__':
    make_binding_energy_curve()
    make_weizsacker_terms_breakdown()
    make_mass_valley_parabola()
    make_fission_drop_deformation()
    print("All figures successfully generated in img/")

# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Спеціальна теорія відносності»."""

import os
import sys
import math

# Підключаємо модуль svgkit із теки scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def make_light_clock():
    path = os.path.join(os.path.dirname(__file__), 'img', 'light-clock.svg')
    w, h = 760, 360
    
    frags = []
    
    # ── Ліва панель: Система S (власна система відліку годинника) ──
    panel1 = rect(20, 20, 340, 320, fill="#fafafa", stroke="#d0d0d0", sw=1, rx=8)
    frags.append(panel1)
    frags.append(text(190, 48, "Система S (годинник у спокої)", size=15, bold=True))
    
    # Дзеркала у S
    m1_top = rect(90, 80, 200, 14, fill="#b0c4de", stroke=LINE, sw=1.5, rx=3)
    m1_bot = rect(90, 260, 200, 14, fill="#b0c4de", stroke=LINE, sw=1.5, rx=3)
    frags.append(m1_top)
    frags.append(m1_bot)
    frags.append(text(190, 72, "Верхнє дзеркало", size=11, color=MUTED))
    frags.append(text(190, 292, "Нижнє дзеркало", size=11, color=MUTED))
    
    # Фотон у S (вертикальний промінь вгору-вниз)
    frags.append(arrow(190, 255, 190, 98, color=POS, sw=2))
    frags.append(line(190, 98, 190, 255, color=POS, sw=1.5, dash="4,3"))
    frags.append(circle(190, 255, 6, fill=POS, stroke="#900C3F", sw=1))
    
    # Позначення відстані d
    frags.append(line(70, 94, 70, 260, color=MUTED, sw=1, dash="2,2"))
    frags.append(arrow(70, 177, 70, 94, color=MUTED, sw=1))
    frags.append(arrow(70, 177, 70, 260, color=MUTED, sw=1))
    frags.append(text(60, 181, "d", size=14, italic=True, bold=True, color=INK))
    
    # Формула для S
    t1_box, _, _ = textbox(190, 320, "Δt₀ = 2d / c", size=13, pad=6, fill="#eaf0fd", stroke=NEG)
    frags.append(t1_box)

    # ── Права панель: Система S' (годинник рухається зі швидкістю v) ──
    panel2 = rect(380, 20, 360, 320, fill="#fafafa", stroke="#d0d0d0", sw=1, rx=8)
    frags.append(panel2)
    frags.append(text(560, 48, "Система S' (годинник рухається з v)", size=15, bold=True))
    
    # Дзеркала у S' в трьох положеннях (випромінювання, відбиття, прийом)
    # Положення 1 (t=0)
    frags.append(rect(410, 260, 60, 12, fill="#d0dbe5", stroke=MUTED, sw=1, rx=2))
    # Положення 2 (t=Δt/2)
    frags.append(rect(530, 80, 60, 12, fill="#b0c4de", stroke=LINE, sw=1.5, rx=2))
    # Положення 3 (t=Δt)
    frags.append(rect(650, 260, 60, 12, fill="#d0dbe5", stroke=MUTED, sw=1, rx=2))
    
    # Траєкторія фотона (зигзаг)
    frags.append(arrow(440, 255, 560, 96, color=POS, sw=2))
    frags.append(arrow(560, 96, 680, 255, color=POS, sw=2))
    frags.append(circle(440, 255, 5, fill=POS, stroke="#900C3F", sw=1))
    frags.append(circle(560, 94, 5, fill=POS, stroke="#900C3F", sw=1))
    frags.append(circle(680, 255, 5, fill=POS, stroke="#900C3F", sw=1))
    
    # Стрілка швидкості v
    frags.append(arrow(440, 292, 520, 292, color=FIELD, sw=2))
    frags.append(text(480, 310, "v", size=13, bold=True, italic=True, color=FIELD))
    
    # Позначення гіпотенузи L = c·Δt/2
    frags.append(text(485, 165, "L = c·Δt/2", size=12, color=POS, bold=True))
    frags.append(text(560, 280, "v·Δt/2", size=12, color=MUTED))
    frags.append(line(440, 266, 560, 266, color=MUTED, sw=1, dash="3,3"))
    
    # Формула для S'
    t2_box, _, _ = textbox(620, 320, "Δt = γ·Δt₀ > Δt₀", size=13, pad=6, fill="#fdecea", stroke=POS)
    frags.append(t2_box)
    
    render(path, w, h, *frags)
    print(f"Generated {path}")

def make_minkowski_diagram():
    path = os.path.join(os.path.dirname(__file__), 'img', 'minkowski-diagram.svg')
    w, h = 680, 520
    
    frags = []
    
    # Фон
    frags.append(rect(10, 10, 660, 500, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=8))
    
    cx, cy = 340, 280
    scale = 180
    
    # Світловий конус (область затінення)
    # Трикутник майбутнього: (cx,cy) -> (cx-200, cy-200) -> (cx+200, cy-200)
    cone_future = f'<polygon points="{cx},{cy} {cx-200},{cy-200} {cx+200},{cy-200}" fill="#fff3cd" opacity="0.4"/>'
    cone_past = f'<polygon points="{cx},{cy} {cx-200},{cy+200} {cx+200},{cy+200}" fill="#d1ecf1" opacity="0.4"/>'
    frags.append(cone_future)
    frags.append(cone_past)
    
    # Лінії світлового конуса (45 градусів)
    frags.append(line(cx-210, cy+210, cx+210, cy-210, color=POS, sw=2, dash="6,3"))
    frags.append(line(cx-210, cy-210, cx+210, cy+210, color=POS, sw=2, dash="6,3"))
    frags.append(text(cx+160, cy-180, "Світловий промінь (x = ct)", size=11, color=POS, bold=True))
    
    # Загальні осі нерухомої системи S: x та ct
    frags.append(arrow(cx-240, cy, cx+240, cy, color=INK, sw=2))
    frags.append(arrow(cx, cy+230, cx, cy-230, color=INK, sw=2))
    frags.append(text(cx+230, cy+25, "x", size=16, bold=True, italic=True))
    frags.append(text(cx+15, cy-215, "ct", size=16, bold=True, italic=True))
    
    # Нахилені осі рухомої системи S': x' та ct' (для v/c = 0.45, arctg(0.45) ≈ 24 град)
    v_c = 0.45
    angle_rad = math.atan(v_c)
    
    # Ось ct': нахилена вправо від ct на angle_rad
    dx_ct = 210 * math.sin(angle_rad)
    dy_ct = 210 * math.cos(angle_rad)
    frags.append(arrow(cx - dx_ct, cy + dy_ct, cx + dx_ct, cy - dy_ct, color=NEG, sw=2.2))
    frags.append(text(cx + dx_ct + 15, cy - dy_ct, "ct'", size=16, bold=True, italic=True, color=NEG))
    
    # Ось x': нахилена вгору від x на angle_rad
    dx_x = 210 * math.cos(angle_rad)
    dy_x = 210 * math.sin(angle_rad)
    frags.append(arrow(cx - dx_x, cy + dy_x, cx + dx_x, cy - dy_x, color=NEG, sw=2.2))
    frags.append(text(cx + dx_x + 15, cy - dy_x - 5, "x'", size=16, bold=True, italic=True, color=NEG))
    
    # Дуги кутів нахилу
    frags.append(text(cx + 25, cy - 80, "θ", size=14, italic=True, color=NEG))
    frags.append(text(cx + 100, cy - 20, "θ", size=14, italic=True, color=NEG))
    
    # Світова лінія спостерігача
    frags.append(circle(cx, cy, 5, fill=INK, stroke="#000", sw=1))
    frags.append(text(cx-15, cy+20, "О", size=12, bold=True))
    
    # Написи областей
    box_f, _, _ = textbox(cx, cy-120, "Майбутній світловий конус\n(часоподібні події: ds² < 0)", size=12, pad=6, fill="#ffffff", stroke="#856404")
    box_p, _, _ = textbox(cx, cy+130, "Минулий світловий конус\n(причинний зв'язок)", size=12, pad=6, fill="#ffffff", stroke="#0c5460")
    box_e, _, _ = textbox(cx-140, cy, "Абсолютно\nвіддалене\n(просторовоподібні: ds² > 0)", size=11, pad=5, fill="#ffffff", stroke=MUTED)
    
    frags.append(box_f)
    frags.append(box_p)
    frags.append(box_e)
    
    render(path, w, h, *frags)
    print(f"Generated {path}")

if __name__ == '__main__':
    make_light_clock()
    make_minkowski_diagram()

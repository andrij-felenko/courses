# -*- coding: utf-8 -*-
import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, fitbox, textbox, plus, minus,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def make_fig1():
    """esd-charge-buildup.svg: Механізм накопичення заряду та спалаху розряду"""
    w, h = 760, 360
    frags = []

    frags.append(text(w / 2, 25, "Накопичення заряду (Q) та пробій міжелектродного зазору", size=16, bold=True))

    # Left block: Charged object (Human / Body)
    frags.append(rect(40, 60, 220, 240, fill="#fdf2e9", stroke="#e67e22", sw=2, rx=10))
    frags.append(text(150, 85, "Заряджене тіло (C ≈ 100 пФ)", size=14, bold=True, color="#d35400"))
    
    for cy in [120, 160, 200, 240]:
        for cx in [80, 130, 180, 220]:
            frags.append(plus(cx, cy, r=8))
    
    frags.append(text(150, 285, "Потенціал: V = Q / C (3–15 кВ)", size=12, bold=True, color="#c0392b"))

    # Spark gap / Electric field in center
    frags.append(line(260, 180, 320, 180, color="#d35400", sw=3))
    frags.append(line(440, 180, 500, 180, color="#2980b9", sw=3))

    # Spark channel (zig-zag)
    spark_pts = [(320, 180), (340, 168), (360, 192), (380, 168), (400, 192), (420, 172), (440, 180)]
    for i in range(len(spark_pts) - 1):
        x1, y1 = spark_pts[i]
        x2, y2 = spark_pts[i+1]
        frags.append(line(x1, y1, x2, y2, color="#f1c40f", sw=3.5))

    # Spark annotation
    frags.append(textbox(380, 110, "Іскровий канал розряду\nE > E_крит (3 МВ/м)\nRise time < 1 нс", size=11, fill="#fef9e7", stroke="#f39c12")[0])

    # Right block: Grounded Conductor / IC Pin
    frags.append(rect(500, 60, 220, 240, fill="#ebf5fb", stroke="#2980b9", sw=2, rx=10))
    frags.append(text(610, 85, "Заземлений провідник / IC", size=14, bold=True, color="#1b4f72"))
    
    for cy in [120, 160, 200, 240]:
        for cx in [540, 580, 630, 670]:
            frags.append(minus(cx, cy, r=8))

    frags.append(text(610, 285, "Потенціал: V ≈ 0 В (GND)", size=12, bold=True, color="#2457d6"))

    # Bottom summary box
    frags.append(fitbox(150, 315, 460, 38, "Неврівноважений заряд Q створює поле E = V/d, яке іонізує повітря та генерує імпульс I(t)", size=11, fill="#f4f6f8", stroke="#7f8c8d"))

    render(os.path.join(IMG_DIR, "esd-charge-buildup.svg"), w, h, *frags)


def make_fig2():
    """esd-waveform-hbm.svg: Перехідний імпульс струму розряду (IEC 61000-4-2)"""
    w, h = 760, 380
    frags = []

    frags.append(text(w / 2, 25, "Форма імпульсу струму ESD за стандартом IEC 61000-4-2", size=16, bold=True))

    ox, oy = 80, 300
    gw, gh = 620, 240

    frags.append(arrow(ox, oy, ox + gw + 20, oy, color=INK, sw=2))
    frags.append(arrow(ox, oy, ox, oy - gh - 15, color=INK, sw=2))

    frags.append(text(ox + gw + 10, oy + 20, "t (нс)", size=12, bold=True))
    frags.append(text(ox - 35, oy - gh - 10, "I (А)", size=12, bold=True))

    for val, label in [(10, "10 A"), (20, "20 A"), (30, "30 A")]:
        y_pos = oy - val * 7.5
        frags.append(line(ox - 5, y_pos, ox + gw, y_pos, color="#e5e7eb", sw=1, dash="4,4"))
        frags.append(text(ox - 25, y_pos + 4, label, size=11, color=MUTED, anchor="end"))

    for t_val, t_lbl in [(1, "1 нс"), (15, "15 нс"), (30, "30 нс"), (60, "60 нс"), (100, "100 нс")]:
        x_pos = ox + t_val * 5.8
        frags.append(line(x_pos, oy, x_pos, oy - gh, color="#e5e7eb", sw=1, dash="4,4"))
        frags.append(text(x_pos, oy + 18, t_lbl, size=11, color=MUTED))

    pts = []
    pts.append((ox, oy))
    pts.append((ox + 2 * 5.8, oy - 28.0 * 7.5)) # Peak 1 shifted slightly right to avoid axis collision
    pts.append((ox + 8 * 5.8, oy - 14.0 * 7.5))
    pts.append((ox + 18 * 5.8, oy - 10.0 * 7.5))
    pts.append((ox + 35 * 5.8, oy - 8.0 * 7.5))
    pts.append((ox + 65 * 5.8, oy - 4.0 * 7.5))
    pts.append((ox + 100 * 5.8, oy - 1.0 * 7.5))

    path_d = ["M %.1f %.1f" % pts[0]]
    for p in pts[1:]:
        path_d.append("L %.1f %.1f" % p)
    
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(path_d), POS))

    p1_x, p1_y = ox + 2 * 5.8, oy - 28.0 * 7.5
    frags.append(circle(p1_x, p1_y, 5, fill=POS, stroke=BG, sw=1.5))
    frags.append(textbox(p1_x + 170, 45, "Первинний пік I_peak (15–30 А)\nЧас наростання t_r < 1 нс", size=11, fill="#fdecea", stroke=POS)[0])

    p2_x, p2_y = ox + 35 * 5.8, oy - 8.0 * 7.5
    frags.append(circle(p2_x, p2_y, 5, fill="#2980b9", stroke=BG, sw=1.5))
    frags.append(textbox(p2_x + 110, p2_y - 25, "Друга хвиля розряду (30 нс)\nСтрум I ≈ 8 А (розряд C_body)", size=11, fill="#ebf5fb", stroke="#2980b9")[0])

    render(os.path.join(IMG_DIR, "esd-waveform-hbm.svg"), w, h, *frags)


def make_fig3():
    """esd-damage-semiconductor.svg: Пробій підкладинного оксиду та розплавлення силіцію"""
    w, h = 760, 360
    frags = []

    frags.append(text(w / 2, 25, "Фізичний механізм руйнування КМОН-структури при ESD", size=16, bold=True))

    # P-substrate background
    frags.append(rect(60, 80, 640, 220, fill="#eaeded", stroke="#7f8c8d", sw=2, rx=6))
    frags.append(text(130, 275, "P-підкладка Si (Substrate)", size=13, color="#7f8c8d", bold=True))

    # N+ Source
    frags.append(rect(100, 80, 120, 80, fill="#d4efdf", stroke="#27ae60", sw=2, rx=4))
    frags.append(text(160, 120, "N+ Істок", size=12, color="#1e8449", bold=True))

    # N+ Drain
    frags.append(rect(540, 80, 120, 80, fill="#d4efdf", stroke="#27ae60", sw=2, rx=4))
    frags.append(text(600, 120, "N+ Стік", size=12, color="#1e8449", bold=True))

    # Gate Oxide layer (SiO2)
    frags.append(rect(240, 150, 280, 20, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=2))
    frags.append(text(380, 164, "Подзатворний діелектрик SiO₂ (d ≈ 5–10 нм)", size=11, color="#b9770e", bold=True))

    # Gate Electrode (Polysilicon)
    frags.append(rect(260, 80, 240, 70, fill="#d6eaf8", stroke="#2980b9", sw=2, rx=4))
    frags.append(text(380, 115, "Затвор (Gate Electrode)", size=13, color="#1b4f72", bold=True))

    # Perforation in SiO2
    frags.append(circle(330, 160, 8, fill="#c0392b", stroke="#922b21", sw=2))
    frags.append(line(330, 142, 330, 178, color="#f1c40f", sw=2.5))

    # Thermal melt region at boundary between channel and Drain (no overlap with Drain rect)
    frags.append(rect(505, 110, 30, 50, fill="#fadbd8", stroke="#c0392b", sw=2, rx=4))
    frags.append(text(520, 140, "🔥", size=14))

    # Annotations
    frags.append(textbox(200, 220, "1. Пробій діелектрика SiO₂\n(E > 10 МВ/см, V_gate > 15 В)\nПропалювання затвору", size=11, fill="#fdecea", stroke=POS)[0])
    frags.append(textbox(540, 220, "2. Тепловий пробій (Joule heating)\nКанал розплавлення силіцію\n(Т > 1414 °C, коротке замикання)", size=11, fill="#fdecea", stroke=POS)[0])

    frags.append(fitbox(150, 315, 460, 34, "Деструктивне поєднання високої напруги (пробій оксиду) та струму (тепловий шнур)", size=11, fill="#f4f6f8", stroke="#7f8c8d"))

    render(os.path.join(IMG_DIR, "esd-damage-semiconductor.svg"), w, h, *frags)


def make_fig4():
    """esd-protection-topology.svg: Схема схемного захисту входу мікросхеми від ESD"""
    w, h = 760, 360
    frags = []

    frags.append(text(w / 2, 25, "Топологія комбінованого захисту входу IC від перенапруг ESD", size=16, bold=True))

    # External ESD Pulse input
    frags.append(circle(50, 180, 12, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(50, 184, "ESD", size=10, bold=True, color=POS))
    frags.append(text(50, 215, "Вхідний пік\n(до 8 кВ)", size=10, color=MUTED))

    frags.append(line(62, 180, 150, 180, color=INK, sw=2))

    # TVS block
    frags.append(line(150, 180, 150, 230, color=INK, sw=2))
    frags.append(rect(130, 230, 40, 45, fill="#ebf5fb", stroke="#2980b9", sw=2, rx=4))
    frags.append(text(150, 255, "TVS", size=11, bold=True, color="#1b4f72"))
    frags.append(line(150, 275, 150, 295, color=INK, sw=2))

    frags.append(line(135, 295, 165, 295, color=INK, sw=2))
    frags.append(line(140, 300, 160, 300, color=INK, sw=1.5))
    frags.append(line(145, 305, 155, 305, color=INK, sw=1))

    # Resistor
    frags.append(line(150, 180, 230, 180, color=INK, sw=2))
    frags.append(rect(230, 170, 60, 20, fill="#f4f6f8", stroke=INK, sw=2, rx=2))
    frags.append(text(260, 184, "R_lim", size=11, bold=True))
    frags.append(line(290, 180, 370, 180, color=INK, sw=2))

    # IC Boundary
    frags.append(rect(350, 60, 360, 270, fill="#fafafa", stroke="#7f8c8d", sw=1.5, rx=8))
    frags.append(text(530, 85, "Внутрішня структура мікросхеми (IC)", size=12, color="#7f8c8d", bold=True))

    # Diodes
    frags.append(line(370, 180, 370, 120, color=INK, sw=2))
    frags.append(rect(355, 120, 30, 30, fill="#e8f8f5", stroke="#16a085", sw=1.5, rx=4))
    frags.append(text(370, 138, "D1", size=11, bold=True, color="#117864"))
    frags.append(line(370, 120, 370, 95, color=INK, sw=2))
    frags.append(text(370, 82, "+VDD", size=11, bold=True, color=POS))

    frags.append(line(370, 180, 370, 240, color=INK, sw=2))
    frags.append(rect(355, 240, 30, 30, fill="#e8f8f5", stroke="#16a085", sw=1.5, rx=4))
    frags.append(text(370, 258, "D2", size=11, bold=True, color="#117864"))
    frags.append(line(370, 270, 370, 295, color=INK, sw=2))

    frags.append(line(355, 295, 385, 295, color=INK, sw=2))
    frags.append(line(360, 300, 380, 300, color=INK, sw=1.5))

    # Internal gate box (line connects at top-left edge, text placed clearly inside)
    frags.append(line(370, 180, 450, 180, color=INK, sw=2))
    frags.append(rect(450, 140, 240, 80, fill="#eaf2f8", stroke="#2980b9", sw=2, rx=6))
    frags.append(mtext(570, 172, ["Затвор CMOS / Буфер", "(V_pin обмежено до VDD+0.7 В)"], size=11, color="#1b4f72", bold=True))

    frags.append(textbox(150, 115, "Зовнішній TVS-супресор:\nскидає > 90% енергії", size=10, fill="#ebf5fb", stroke="#2980b9")[0])
    frags.append(textbox(260, 230, "Обмежувальний\nрезистор R_lim", size=10, fill="#f4f6f8", stroke=INK)[0])

    render(os.path.join(IMG_DIR, "esd-protection-topology.svg"), w, h, *frags)


def main():
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    print("ESD figures generated successfully.")


if __name__ == '__main__':
    main()

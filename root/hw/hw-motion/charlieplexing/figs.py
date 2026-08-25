# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def _diode_symbol(x, y, angle=0, color=LINE, label="", label_pos="top", is_on=False):
    import math
    rad = math.radians(angle)
    dx = math.cos(rad)
    dy = math.sin(rad)
    nx = -dy
    ny = dx
    
    body = []
    p1 = (x - 12 * dx + 8 * nx, y - 12 * dy + 8 * ny)
    p2 = (x - 12 * dx - 8 * nx, y - 12 * dy - 8 * ny)
    p3 = (x + 4 * dx, y + 4 * dy)
    fill_col = "#ffeaa7" if is_on else (POS if color == POS else ("#ffffff"))
    stroke_col = POS if is_on or color == POS else (NEG if color == NEG else LINE)
    sw = 2.0 if is_on else 1.5
    
    body.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" stroke="%s" stroke-width="%.1f"/>' %
                (p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], fill_col, stroke_col, sw))
    
    k1 = (x + 5 * dx + 9 * nx, y + 5 * dy + 9 * ny)
    k2 = (x + 5 * dx - 9 * nx, y + 5 * dy - 9 * ny)
    body.append(line(k1[0], k1[1], k2[0], k2[1], color=stroke_col, sw=sw + 0.5))
    
    if is_on:
        body.append(line(x - 2 + 10 * nx, y + 10 * ny, x + 6 + 16 * nx, y + 16 * ny, color=POS, sw=1.8))
        body.append(line(x + 4 + 8 * nx, y + 8 * ny, x + 12 + 14 * nx, y + 14 * ny, color=POS, sw=1.8))
    
    if label:
        lx = x + (18 * nx if label_pos == "top" else -18 * nx)
        ly = y + (18 * ny if label_pos == "top" else -18 * ny) + 4
        body.append(text(lx, ly, label, size=11, color=stroke_col, bold=is_on))
        
    return "".join(body)


def fig_3pin_mesh():
    W, H = 820, 420
    p = []
    
    p.append(rect(40, 60, 160, 310, fill="#f8fafc", stroke=LINE, sw=2, rx=8))
    p.append(text(120, 88, "Мікроконтролер", size=13, bold=True, color=INK))
    p.append(text(120, 106, "(3 виводи GPIO)", size=11, color=MUTED))
    
    pins = [
        ("P0 (A)", 150, "HIGH (+3.3V)", POS, "#fdecea"),
        ("P1 (B)", 230, "LOW (GND 0V)", NEG, "#eaf0fd"),
        ("P2 (C)", 310, "Hi-Z (Вхід)", MUTED, "#f3f4f6"),
    ]
    
    y_pins = {}
    for name, y, state, col, bgcol in pins:
        p.append(rect(55, y - 20, 130, 40, fill=bgcol, stroke=col, sw=1.8, rx=5))
        p.append(text(120, y - 3, name, size=12, bold=True, color=col))
        p.append(text(120, y + 13, state, size=10, color=col))
        y_pins[name[:2]] = y
        p.append(line(185, y, 240, y, color=col, sw=2.2))
        p.append(circle(240, y, 4, fill=col, stroke=col))
        
    p.append(line(240, 150, 760, 150, color=POS, sw=2.5))
    p.append(line(240, 230, 760, 230, color=NEG, sw=2.5))
    p.append(line(240, 310, 760, 310, color=MUTED, sw=1.5, dash="4,4"))
    
    p.append(line(330, 150, 330, 175, color=POS, sw=2.5))
    p.append(line(330, 205, 330, 230, color=NEG, sw=2.5))
    p.append(_diode_symbol(330, 190, angle=90, label="D01 (A→B) УВІМК", label_pos="bottom", is_on=True))
    p.append(text(330, 132, "Прямий струм", size=10, color=POS, bold=True))
    p.append(circle(330, 150, 3.5, fill=POS, stroke=POS))
    p.append(circle(330, 230, 3.5, fill=NEG, stroke=NEG))
    
    p.append(line(430, 150, 430, 175, color=LINE, sw=1.5))
    p.append(line(430, 205, 430, 230, color=LINE, sw=1.5))
    p.append(_diode_symbol(430, 190, angle=270, color=LINE, label="D10 (B→A) ВИМК", label_pos="bottom", is_on=False))
    p.append(text(430, 132, "Зворотний (закритий)", size=10, color=MUTED))
    p.append(circle(430, 150, 3.5, fill=LINE, stroke=LINE))
    p.append(circle(430, 230, 3.5, fill=LINE, stroke=LINE))
    
    p.append(line(530, 150, 530, 215, color=LINE, sw=1.2, dash="3,3"))
    p.append(line(530, 245, 530, 310, color=LINE, sw=1.2, dash="3,3"))
    p.append(_diode_symbol(530, 230, angle=90, color=MUTED, label="D02 (A→C)", label_pos="bottom", is_on=False))
    p.append(circle(530, 150, 3, fill=MUTED, stroke=MUTED))
    p.append(circle(530, 310, 3, fill=MUTED, stroke=MUTED))
    
    p.append(line(610, 150, 610, 215, color=LINE, sw=1.2, dash="3,3"))
    p.append(line(610, 245, 610, 310, color=LINE, sw=1.2, dash="3,3"))
    p.append(_diode_symbol(610, 230, angle=270, color=MUTED, label="D20 (C→A)", label_pos="bottom", is_on=False))
    p.append(circle(610, 150, 3, fill=MUTED, stroke=MUTED))
    p.append(circle(610, 310, 3, fill=MUTED, stroke=MUTED))
    
    p.append(line(690, 230, 690, 255, color=LINE, sw=1.2, dash="3,3"))
    p.append(line(690, 285, 690, 310, color=LINE, sw=1.2, dash="3,3"))
    p.append(_diode_symbol(690, 270, angle=90, color=MUTED, label="D12 (B→C)", label_pos="bottom", is_on=False))
    p.append(circle(690, 230, 3, fill=MUTED, stroke=MUTED))
    p.append(circle(690, 310, 3, fill=MUTED, stroke=MUTED))
    
    p.append(line(755, 230, 755, 255, color=LINE, sw=1.2, dash="3,3"))
    p.append(line(755, 285, 755, 310, color=LINE, sw=1.2, dash="3,3"))
    p.append(_diode_symbol(755, 270, angle=270, color=MUTED, label="D21 (C→B)", label_pos="bottom", is_on=False))
    p.append(circle(755, 230, 3, fill=MUTED, stroke=MUTED))
    p.append(circle(755, 310, 3, fill=MUTED, stroke=MUTED))
    
    b_bot, _, _ = textbox(W / 2, 388,
                          "Стан виводів: P0=HIGH (+3.3V), P1=LOW (0V), P2=Hi-Z (відключено). Струм тече лише через D01. Разом 3·(3−1) = 6 світлодіодів.",
                          size=11, bold=True, fill="#ffffff", stroke=LINE, min_w=780)
    p.append(b_bot)
    
    render(os.path.join(OUT, "charlieplexing-3pin-mesh.svg"), W, H, *p,
           title="Чарліплексинг на 3 виводах: вибіркове запалювання D01")


def fig_sneak_paths():
    W, H = 820, 420
    p = []
    
    p.append(rect(40, 60, 340, 280, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(text(210, 88, "Цільовий шлях (1 діод)", size=13, bold=True, color=POS))
    p.append(text(210, 110, "P0 = HIGH (3.3V)  →  P1 = LOW (0V)", size=11, color=INK))
    
    p.append(line(80, 170, 140, 170, color=POS, sw=2.5))
    p.append(text(70, 175, "P0", size=12, bold=True, color=POS))
    p.append(rect(140, 160, 40, 20, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(160, 174, "R", size=10, bold=True, color=INK))
    p.append(line(180, 170, 230, 170, color=POS, sw=2.5))
    p.append(_diode_symbol(245, 170, angle=0, is_on=True, label="D01 (VF = 2.0V)", label_pos="top"))
    p.append(line(260, 170, 310, 170, color=NEG, sw=2.5))
    p.append(rect(310, 160, 40, 20, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(330, 174, "R", size=10, bold=True, color=INK))
    p.append(line(350, 170, 370, 170, color=NEG, sw=2.5))
    p.append(text(375, 175, "P1", size=12, bold=True, color=NEG))
    
    p.append(rect(60, 230, 300, 90, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(210, 255, "Напруга на діоді: U = VF ≈ 2.0 В", size=11, bold=True, color=FIELD))
    p.append(text(210, 275, "Струм обмежено: I = (3.3V − 2.0V) / 2R", size=11, color=INK))
    p.append(text(210, 298, "Діод D01 світиться яскраво та стабільно", size=11, bold=True, color=FIELD))
    
    p.append(rect(420, 60, 360, 280, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(text(600, 88, "Паразитний шлях через P2 (Hi-Z)", size=13, bold=True, color=NEG))
    p.append(text(600, 110, "P0 (3.3V)  →  D02  →  [P2]  →  D21  →  P1 (0V)", size=11, color=INK))
    
    p.append(text(445, 175, "P0", size=12, bold=True, color=POS))
    p.append(line(460, 170, 490, 170, color=MUTED, sw=1.5))
    p.append(_diode_symbol(505, 170, angle=0, color=MUTED, label="D02", label_pos="top"))
    p.append(line(520, 170, 560, 170, color=MUTED, sw=1.5))
    
    p.append(circle(575, 170, 15, fill="#f3f4f6", stroke=MUTED, sw=1.5))
    p.append(text(575, 174, "Hi-Z", size=9, bold=True, color=MUTED))
    p.append(text(575, 202, "вузол P2", size=9, color=MUTED))
    
    p.append(line(590, 170, 630, 170, color=MUTED, sw=1.5))
    p.append(_diode_symbol(645, 170, angle=0, color=MUTED, label="D21", label_pos="top"))
    p.append(line(660, 170, 710, 170, color=MUTED, sw=1.5))
    p.append(text(725, 175, "P1", size=12, bold=True, color=NEG))
    
    p.append(rect(440, 230, 320, 90, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    p.append(text(600, 255, "Сумарний поріг відкриття: 2 × VF ≈ 4.0 В", size=11, bold=True, color=POS))
    p.append(text(600, 275, "Умова відсутності привидів: VCC < 2·VF", size=11, color=INK))
    p.append(text(600, 298, "При VCC = 3.3 В струм не протікає (I ≈ 0)", size=11, bold=True, color=FIELD))
    
    b_bot, _, _ = textbox(W / 2, 385,
                          "Паразитний шлях містить 2 послідовні діоди. Якщо VCC < 2·VF, напруги не вистачає для їхнього відкриття — паразитного світіння немає.",
                          size=11, bold=True, fill="#ffffff", stroke=LINE, min_w=780)
    p.append(b_bot)
    
    render(os.path.join(OUT, "sneak-paths-ghosting.svg"), W, H, *p,
           title="Фізика паразитних шляхів і умова захисту від підсвічування")


def fig_matrix_vs_charlie():
    W, H = 820, 380
    p = []
    
    p.append(rect(40, 60, 350, 250, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(text(215, 88, "Класична матриця (рядки × стовпчики)", size=12, bold=True, color=INK))
    p.append(text(215, 110, "Потрібні роздільні лінії рядків і стовпчиків", size=10, color=MUTED))
    
    p.append(text(80, 140, "3 рядки", size=10, bold=True, color=POS))
    p.append(text(80, 160, "+ 3 стовп.", size=10, bold=True, color=NEG))
    p.append(text(80, 190, "= 6 виводів", size=11, bold=True, color=INK))
    p.append(text(80, 215, "→ 9 LED", size=14, bold=True, color=FIELD))
    
    for r in range(3):
        p.append(line(170, 140 + r * 35, 340, 140 + r * 35, color=POS, sw=1.5))
    for c in range(3):
        p.append(line(200 + c * 50, 120, 200 + c * 50, 230, color=NEG, sw=1.5))
    for r in range(3):
        for c in range(3):
            p.append(circle(200 + c * 50, 140 + r * 35, 4, fill=FIELD, stroke=INK))
            
    p.append(text(215, 275, "Формула: N виводів → (N/2)² = N²/4 світлодіодів", size=11, bold=True, color=INK))
    p.append(text(215, 295, "Для 8 виводів (4×4) = 16 світлодіодів", size=10, color=MUTED))
    
    p.append(rect(430, 60, 350, 250, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(text(605, 88, "Чарліплексинг (орієнтований граф)", size=12, bold=True, color=POS))
    p.append(text(605, 110, "Кожен вивід може бути джерелом, стоком і Hi-Z", size=10, color=MUTED))
    
    p.append(text(470, 140, "6 виводів", size=11, bold=True, color=INK))
    p.append(text(470, 165, "N = 6", size=11, color=MUTED))
    p.append(text(470, 195, "6 · (6 − 1)", size=12, bold=True, color=POS))
    p.append(text(470, 220, "= 30 LED!", size=15, bold=True, color=POS))
    
    import math
    cx, cy, rad_g = 660, 175, 48
    pts = []
    for i in range(6):
        ang = i * (2 * math.pi / 6) - math.pi / 2
        px = cx + rad_g * math.cos(ang)
        py = cy + rad_g * math.sin(ang)
        pts.append((px, py))
    for i in range(6):
        for j in range(i + 1, 6):
            p.append(line(pts[i][0], pts[i][1], pts[j][0], pts[j][1], color="#cbd5e1", sw=1.0))
    for i, (px, py) in enumerate(pts):
        p.append(circle(px, py, 6, fill=POS, stroke=INK))
        
    p.append(text(605, 275, "Формула: N виводів → N · (N − 1) світлодіодів", size=11, bold=True, color=POS))
    p.append(text(605, 295, "Для 8 виводів (8×7) = 56 світлодіодів (у 3.5× більше!)", size=10, color=FIELD, bold=True))
    
    b_bot, _, _ = textbox(W / 2, 350,
                          "При тих самих 8 ніжках МК Чарліплексинг дає 56 світлодіодів проти 16 у звичайній матриці без жодної мікросхеми розширення.",
                          size=11, bold=True, fill="#ffffff", stroke=LINE, min_w=780)
    p.append(b_bot)
    
    render(os.path.join(OUT, "matrix-vs-charlieplexing.svg"), W, H, *p,
           title="Порівняння ефективності використання ніжок МК")


def fig_resistor_topologies():
    W, H = 820, 390
    p = []
    
    p.append(rect(40, 60, 350, 260, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(text(215, 88, "Варіант А: 1 резистор на вивід", size=13, bold=True, color=INK))
    p.append(text(215, 108, "Економічний монтаж: рівно N резисторів", size=10, color=MUTED))
    
    p.append(text(75, 150, "P0", size=11, bold=True, color=POS))
    p.append(line(95, 146, 125, 146, color=POS, sw=2))
    p.append(rect(125, 136, 35, 20, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(142, 150, "R", size=10, bold=True, color=INK))
    p.append(line(160, 146, 210, 146, color=POS, sw=2))
    
    p.append(text(75, 210, "P1", size=11, bold=True, color=NEG))
    p.append(line(95, 206, 125, 206, color=NEG, sw=2))
    p.append(rect(125, 196, 35, 20, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(142, 210, "R", size=10, bold=True, color=INK))
    p.append(line(160, 206, 210, 206, color=NEG, sw=2))
    
    p.append(line(210, 146, 210, 165, color=POS, sw=2))
    p.append(_diode_symbol(210, 176, angle=90, is_on=True))
    p.append(line(210, 187, 210, 206, color=NEG, sw=2))
    
    p.append(line(270, 146, 270, 165, color=LINE, sw=1.5))
    p.append(_diode_symbol(270, 176, angle=270, is_on=False))
    p.append(line(270, 187, 270, 206, color=LINE, sw=1.5))
    p.append(line(210, 146, 270, 146, color=POS, sw=1.5))
    p.append(line(210, 206, 270, 206, color=NEG, sw=1.5))
    
    p.append(rect(55, 240, 320, 65, fill="#ffffff", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(215, 260, "Загальний опір у колі 1 діода: Rвкл = 2·R", size=10, bold=True, color=INK))
    p.append(text(215, 280, "Якщо запалювати рядок, спільний R просаджує струм", size=10, color=POS))
    p.append(text(215, 296, "Ідеально для сканування по 1 світлодіоду за раз", size=10, bold=True, color=FIELD))
    
    p.append(rect(430, 60, 350, 260, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(text(605, 88, "Варіант Б: 1 резистор на кожен діод", size=13, bold=True, color=INK))
    p.append(text(605, 108, "Ізольовані кола: N·(N−1) резисторів", size=10, color=MUTED))
    
    p.append(text(465, 150, "P0", size=11, bold=True, color=POS))
    p.append(line(485, 146, 560, 146, color=POS, sw=2))
    
    p.append(text(465, 210, "P1", size=11, bold=True, color=NEG))
    p.append(line(485, 206, 560, 206, color=NEG, sw=2))
    
    p.append(line(560, 146, 560, 160, color=POS, sw=2))
    p.append(rect(548, 160, 24, 16, fill="#ffffff", stroke=LINE, sw=1.2))
    p.append(text(560, 172, "R", size=9, bold=True, color=INK))
    p.append(line(560, 176, 560, 184, color=POS, sw=2))
    p.append(_diode_symbol(560, 192, angle=90, is_on=True))
    p.append(line(560, 200, 560, 206, color=NEG, sw=2))
    
    p.append(line(640, 146, 640, 160, color=LINE, sw=1.5))
    p.append(_diode_symbol(640, 168, angle=270, is_on=False))
    p.append(line(640, 176, 640, 184, color=LINE, sw=1.5))
    p.append(rect(628, 184, 24, 16, fill="#ffffff", stroke=LINE, sw=1.2))
    p.append(text(640, 196, "R", size=9, bold=True, color=INK))
    p.append(line(640, 200, 640, 206, color=LINE, sw=1.5))
    p.append(line(560, 146, 640, 146, color=POS, sw=1.5))
    p.append(line(560, 206, 640, 206, color=NEG, sw=1.5))
    
    p.append(rect(445, 240, 320, 65, fill="#ffffff", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(605, 260, "Кожен діод має індивідуальний опір R", size=10, bold=True, color=INK))
    p.append(text(605, 280, "Дозволяє запалювати кілька катодів одночасно", size=10, color=FIELD))
    p.append(text(605, 296, "Рівномірна яскравість при рядковому скануванні", size=10, bold=True, color=FIELD))
    
    b_bot, _, _ = textbox(W / 2, 355,
                          "Для простого сканування по 1 діоду вистачає N резисторів на ніжках МК. Для рядкового увімкнення потрібні індивідуальні резистори.",
                          size=11, bold=True, fill="#ffffff", stroke=LINE, min_w=780)
    p.append(b_bot)
    
    render(os.path.join(OUT, "resistor-topologies.svg"), W, H, *p,
           title="Топології резисторів: на виводах проти індивідуальних для діодів")


def fig_tdm_timing():
    W, H = 820, 400
    p = []
    
    p.append(text(70, 75, "Слот 1: D01", size=11, bold=True, color=POS))
    p.append(text(70, 135, "Слот 2: D02", size=11, bold=True, color=FIELD))
    p.append(text(70, 195, "Слот 3: D10", size=11, bold=True, color=NEG))
    p.append(text(70, 255, "Слот 4: D12...", size=11, bold=True, color=MUTED))
    
    t0, slot_w, gap = 150, 90, 10
    
    p.append(rect(t0, 55, slot_w, 35, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
    p.append(text(t0 + slot_w / 2, 76, "Ipeak = 20 мА", size=10, bold=True, color=POS))
    p.append(line(t0 + slot_w, 90, t0 + slot_w + gap, 90, color=MUTED, sw=1.5, dash="2,2"))
    
    t1 = t0 + slot_w + gap
    p.append(rect(t1, 115, slot_w, 35, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(t1 + slot_w / 2, 136, "Ipeak = 20 мА", size=10, bold=True, color=FIELD))
    
    t2 = t1 + slot_w + gap
    p.append(rect(t2, 175, slot_w, 35, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    p.append(text(t2 + slot_w / 2, 196, "Ipeak = 20 мА", size=10, bold=True, color=NEG))
    
    t3 = t2 + slot_w + gap
    p.append(rect(t3, 235, slot_w, 35, fill="#f3f4f6", stroke=MUTED, sw=1.5, rx=4))
    p.append(text(t3 + slot_w / 2, 256, "...", size=11, bold=True, color=MUTED))
    
    p.append(line(t0, 305, t3 + slot_w + 30, 305, color=INK, sw=1.5))
    p.append(arrow(t0, 305, t0 + 10, 305, color=INK))
    p.append(arrow(t3 + slot_w + 30, 305, t3 + slot_w + 20, 305, color=INK))
    p.append(text((t0 + t3 + slot_w) / 2, 322, "Період повного кадру Tframe ≤ 16.6 мс (Частота ≥ 60 Гц)", size=11, bold=True, color=INK))
    
    p.append(rect(580, 55, 200, 225, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(680, 80, "Інерційність зору", size=12, bold=True, color=INK))
    p.append(text(680, 100, "(Persistence of Vision)", size=10, color=MUTED))
    
    p.append(line(600, 130, 760, 130, color=LINE, sw=1.2))
    p.append(text(680, 155, "Шпаруватість D = 1 / L", size=11, bold=True, color=POS))
    p.append(text(680, 175, "Середній струм:", size=10, color=INK))
    p.append(text(680, 195, "Iavg = Ipeak · (1 / L)", size=12, bold=True, color=FIELD))
    p.append(text(680, 220, "При L = 12, Ipeak = 24 мА:", size=9, color=MUTED))
    p.append(text(680, 240, "Iavg = 24 / 12 = 2.0 мА", size=11, bold=True, color=INK))
    p.append(text(680, 260, "Око бачить стабільне світло", size=10, color=FIELD, bold=True))
    
    b_bot, _, _ = textbox(W / 2, 365,
                          "Швидка розгортка (≥100 Гц) зливає короткі імпульси в безперервне світіння. Яскравість пропорційна середньому струму Iavg = Ipeak / L.",
                          size=11, bold=True, fill="#ffffff", stroke=LINE, min_w=780)
    p.append(b_bot)
    
    render(os.path.join(OUT, "tdm-timing-duty-cycle.svg"), W, H, *p,
           title="Часове мультиплексування: розгортка слотів та інтеграція оком")


if __name__ == "__main__":
    fig_3pin_mesh()
    fig_sneak_paths()
    fig_matrix_vs_charlie()
    fig_resistor_topologies()
    fig_tdm_timing()
    print("All figures generated successfully.")

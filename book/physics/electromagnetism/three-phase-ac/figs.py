# -*- coding: utf-8 -*-
import sys
import os
import math

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def generate_waveforms():
    """Фігура 1: Синусоїдальні хвилі трьох фаз A, B, C та векторна діаграма."""
    w, h = 820, 380
    frags = []
    
    frags.append(text(410, 25, "Часові осцилограми та векторна діаграма трифазної системи", size=16, bold=True))
    
    # ── Ліва частина: Осцилограми ──
    x_off, y_off = 60, 200
    w_plot, h_plot = 370, 130
    
    frags.append(line(x_off - 10, y_off, x_off + w_plot + 15, y_off, color=LINE, sw=1.5))
    frags.append(arrow(x_off, y_off + h_plot + 15, x_off, y_off - h_plot - 15, color=LINE, sw=1.5))
    frags.append(text(x_off + w_plot + 20, y_off + 4, "ωt", size=13, italic=True))
    frags.append(text(x_off - 15, y_off - h_plot - 10, "u(t)", size=13, italic=True))
    
    frags.append(line(x_off, y_off - h_plot, x_off + w_plot, y_off - h_plot, color=MUTED, sw=1, dash="4,4"))
    frags.append(line(x_off, y_off + h_plot, x_off + w_plot, y_off + h_plot, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(x_off - 25, y_off - h_plot + 4, "+Um", size=11, color=MUTED))
    frags.append(text(x_off - 25, y_off + h_plot + 4, "−Um", size=11, color=MUTED))
    
    c_a, c_b, c_c = POS, FIELD, NEG
    pts_a, pts_b, pts_c = [], [], []
    steps = 100
    for i in range(steps + 1):
        t = (i / steps) * (2 * math.pi * 1.25)
        px = x_off + (i / steps) * w_plot
        
        ya = y_off - h_plot * math.sin(t)
        yb = y_off - h_plot * math.sin(t - 2 * math.pi / 3)
        yc = y_off - h_plot * math.sin(t - 4 * math.pi / 3)
        
        pts_a.append("%.1f,%.1f" % (px, ya))
        pts_b.append("%.1f,%.1f" % (px, yb))
        pts_c.append("%.1f,%.1f" % (px, yc))
    
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_a), c_a))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_b), c_b))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_c), c_c))
    
    frags.append(textbox(x_off + 80, y_off - h_plot - 25, "Фаза A (uA)", size=12, fill="#fdecea", stroke=c_a, color=c_a, bold=True)[0])
    frags.append(textbox(x_off + 210, y_off - h_plot - 25, "Фаза B (uB)", size=12, fill="#eafaf1", stroke=c_b, color=c_b, bold=True)[0])
    frags.append(textbox(x_off + 330, y_off - h_plot - 25, "Фаза C (uC)", size=12, fill="#eaf0fd", stroke=c_c, color=c_c, bold=True)[0])

    # ── Права частина: Векторна діаграма ──
    cx_v, cy_v = 640, 200
    r_v = 110
    
    frags.append(line(cx_v - r_v - 20, cy_v, cx_v + r_v + 20, cy_v, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(cx_v, cy_v - r_v - 20, cx_v, cy_v + r_v + 20, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(cx_v + r_v + 25, cy_v + 4, "+Re", size=12, color=MUTED, italic=True))
    frags.append(text(cx_v + 4, cy_v - r_v - 22, "+Im", size=12, color=MUTED, italic=True))
    
    frags.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1" stroke-dasharray="3,3"/>' % (cx_v, cy_v, r_v, MUTED))
    
    rad_a = 0.0
    rad_b = -2 * math.pi / 3
    rad_c = 2 * math.pi / 3
    
    xa, ya = cx_v + r_v * math.cos(rad_a), cy_v - r_v * math.sin(rad_a)
    xb, yb = cx_v + r_v * math.cos(rad_b), cy_v - r_v * math.sin(rad_b)
    xc, yc = cx_v + r_v * math.cos(rad_c), cy_v - r_v * math.sin(rad_c)
    
    frags.append(arrow(cx_v, cy_v, xa, ya, color=c_a, sw=2.5))
    frags.append(arrow(cx_v, cy_v, xb, yb, color=c_b, sw=2.5))
    frags.append(arrow(cx_v, cy_v, xc, yc, color=c_c, sw=2.5))
    
    frags.append(textbox(xa + 25, ya, "UA", size=13, fill="#fdecea", stroke=c_a, color=c_a, bold=True)[0])
    frags.append(textbox(xb - 10, yb + 20, "UB", size=13, fill="#eafaf1", stroke=c_b, color=c_b, bold=True)[0])
    frags.append(textbox(xc - 10, yc - 20, "UC", size=13, fill="#eaf0fd", stroke=c_c, color=c_c, bold=True)[0])
    
    frags.append(text(cx_v - 35, cy_v - 15, "120°", size=12, color=INK, bold=True))
    frags.append(text(cx_v - 35, cy_v + 25, "120°", size=12, color=INK, bold=True))
    frags.append(text(cx_v + 35, cy_v + 25, "120°", size=12, color=INK, bold=True))

    render(os.path.join(IMG_DIR, 'three-phase-waveforms.svg'), w, h, *frags)


def generate_star_delta():
    """Фігура 2: Схеми з'єднання зіркою (Y) та трикутником (Delta)."""
    w, h = 820, 420
    frags = []
    
    frags.append(text(410, 25, "Схеми з'єднання фаз джерела та навантаження", size=16, bold=True))
    
    # ── Ліва панель: Зірка (Y) ──
    x_y, y_y = 200, 210
    frags.append(textbox(x_y, 60, "З'єднання зіркою (Y) з нейтраллю N", size=14, fill="#f4f6f8", stroke=LINE, bold=True)[0])
    
    frags.append(circle(x_y, y_y, 5, fill=INK, stroke=INK))
    frags.append(text(x_y - 18, y_y + 4, "N", size=13, bold=True))
    
    r_arm = 90
    xa, ya = x_y, y_y - r_arm
    xb, yb = x_y - r_arm * math.cos(math.pi / 6), y_y + r_arm * math.sin(math.pi / 6)
    xc, yc = x_y + r_arm * math.cos(math.pi / 6), y_y + r_arm * math.sin(math.pi / 6)
    
    frags.append(line(x_y, y_y, xa, ya, color=POS, sw=2))
    frags.append(line(x_y, y_y, xb, yb, color=FIELD, sw=2))
    frags.append(line(x_y, y_y, xc, yc, color=NEG, sw=2))
    
    frags.append(textbox((x_y + xa) / 2 + 22, (y_y + ya) / 2, "ZA", size=12, fill="#ffffff", stroke=POS, color=POS)[0])
    frags.append(textbox((x_y + xb) / 2 - 22, (y_y + yb) / 2, "ZB", size=12, fill="#ffffff", stroke=FIELD, color=FIELD)[0])
    frags.append(textbox((x_y + xc) / 2 + 22, (y_y + yc) / 2, "ZC", size=12, fill="#ffffff", stroke=NEG, color=NEG)[0])
    
    frags.append(line(xa, ya, xa + 130, ya, color=POS, sw=2))
    frags.append(line(xb, yb, xb - 30, yb, color=FIELD, sw=2))
    frags.append(line(xb - 30, yb, xb - 30, ya + 180, color=FIELD, sw=2))
    frags.append(line(xb - 30, ya + 180, xa + 130, ya + 180, color=FIELD, sw=2))
    frags.append(line(xc, yc, xc + 50, yc, color=NEG, sw=2))
    frags.append(line(xc + 50, yc, xc + 50, ya + 90, color=NEG, sw=2))
    frags.append(line(xc + 50, ya + 90, xa + 130, ya + 90, color=NEG, sw=2))
    
    frags.append(line(x_y, y_y, x_y + 180, y_y, color=MUTED, sw=2, dash="5,4"))
    
    frags.append(textbox(xa + 150, ya, "L1 (A)", size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)[0])
    frags.append(textbox(xa + 150, ya + 90, "L3 (C)", size=12, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)[0])
    frags.append(textbox(xa + 150, ya + 180, "L2 (B)", size=12, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True)[0])
    frags.append(textbox(x_y + 150, y_y, "N", size=12, fill="#f4f6f8", stroke=MUTED, color=MUTED, bold=True)[0])
    
    frags.append(textbox(x_y + 10, 375, "UL = √3 · Uфаз  |  IL = Іфаз", size=13, fill="#ffffff", stroke=LINE, bold=True)[0])

    # ── Права панель: Трикутник (Delta) ──
    x_d, y_d = 620, 210
    frags.append(textbox(x_d, 60, "З'єднання трикутником (Δ)", size=14, fill="#f4f6f8", stroke=LINE, bold=True)[0])
    
    side = 140
    h_tri = side * math.sin(math.pi / 3)
    
    v_a = (x_d, y_d - h_tri * 0.6)
    v_b = (x_d - side / 2, y_d + h_tri * 0.4)
    v_c = (x_d + side / 2, y_d + h_tri * 0.4)
    
    frags.append(line(v_a[0], v_a[1], v_b[0], v_b[1], color=POS, sw=2))
    frags.append(line(v_b[0], v_b[1], v_c[0], v_c[1], color=FIELD, sw=2))
    frags.append(line(v_c[0], v_c[1], v_a[0], v_a[1], color=NEG, sw=2))
    
    frags.append(textbox((v_a[0] + v_b[0]) / 2 - 25, (v_a[1] + v_b[1]) / 2, "ZAB", size=12, fill="#ffffff", stroke=POS, color=POS)[0])
    frags.append(textbox((v_b[0] + v_c[0]) / 2, (v_b[1] + v_c[1]) / 2 + 20, "ZBC", size=12, fill="#ffffff", stroke=FIELD, color=FIELD)[0])
    frags.append(textbox((v_c[0] + v_a[0]) / 2 + 25, (v_c[1] + v_a[1]) / 2, "ZCA", size=12, fill="#ffffff", stroke=NEG, color=NEG)[0])
    
    frags.append(line(v_a[0], v_a[1], v_a[0] + 120, v_a[1], color=POS, sw=2))
    frags.append(line(v_c[0], v_c[1], v_a[0] + 120, v_c[1], color=NEG, sw=2))
    frags.append(line(v_b[0], v_b[1], v_b[0] - 20, v_b[1], color=FIELD, sw=2))
    frags.append(line(v_b[0] - 20, v_b[1], v_b[0] - 20, v_c[1] + 45, color=FIELD, sw=2))
    frags.append(line(v_b[0] - 20, v_c[1] + 45, v_a[0] + 120, v_c[1] + 45, color=FIELD, sw=2))
    
    frags.append(textbox(v_a[0] + 140, v_a[1], "L1", size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)[0])
    frags.append(textbox(v_a[0] + 140, v_c[1], "L3", size=12, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)[0])
    frags.append(textbox(v_a[0] + 140, v_c[1] + 45, "L2", size=12, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True)[0])
    
    frags.append(textbox(x_d, 375, "UL = Uфаз  |  IL = √3 · Іфаз", size=13, fill="#ffffff", stroke=LINE, bold=True)[0])

    render(os.path.join(IMG_DIR, 'star-delta-schematic.svg'), w, h, *frags)


def generate_rotating_field():
    """Фігура 3: Формування обертового магнітного поля трьома фазами."""
    w, h = 760, 400
    frags = []
    
    frags.append(text(380, 25, "Принцип утворення обертового магнітного поля статора", size=16, bold=True))
    
    cx, cy, r_stator = 240, 210, 115
    frags.append(circle(cx, cy, r_stator, fill="#f8f9fa", stroke=LINE, sw=3))
    frags.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#ffffff" stroke="%s" stroke-width="1" stroke-dasharray="4,4"/>' % (cx, cy, r_stator - 20, MUTED))
    
    coils = [
        ("A", "X", 90, POS),
        ("B", "Y", 210, FIELD),
        ("C", "Z", 330, NEG)
    ]
    
    for name1, name2, angle_deg, color in coils:
        rad1 = math.radians(angle_deg)
        rad2 = math.radians(angle_deg + 180)
        
        x1, y1 = cx + r_stator * math.cos(rad1), cy - r_stator * math.sin(rad1)
        x2, y2 = cx + r_stator * math.cos(rad2), cy - r_stator * math.sin(rad2)
        
        frags.append(circle(x1, y1, 14, fill="#ffffff", stroke=color, sw=2))
        frags.append(text(x1, y1 + 4, name1, size=12, color=color, bold=True))
        
        frags.append(circle(x2, y2, 14, fill="#ffffff", stroke=color, sw=2))
        frags.append(text(x2, y2 + 4, name2, size=12, color=color, bold=True))
    
    r_b = 75
    frags.append(arrow(cx, cy, cx, cy - r_b, color=POS, sw=3.5))
    frags.append(textbox(cx + 45, cy - r_b / 2 - 10, "Врез = (3/2)·Bm", size=13, fill="#fdecea", stroke=POS, color=POS, bold=True)[0])
    
    frags.append(text(cx, cy + 30, "ω (обертання)", size=12, color=INK, bold=True))
    
    x_p, y_p = 560, 210
    frags.append(textbox(x_p, 60, "Геометричне додавання векторів B", size=14, fill="#f4f6f8", stroke=LINE, bold=True)[0])
    
    frags.append(arrow(x_p, y_p, x_p, y_p - 70, color=POS, sw=2.5))
    frags.append(text(x_p + 25, y_p - 40, "BA", size=13, color=POS, bold=True))
    
    rad_bb = math.radians(30)
    frags.append(arrow(x_p, y_p - 70, x_p - 35 * math.cos(rad_bb), y_p - 70 - 35 * math.sin(rad_bb), color=FIELD, sw=2.5))
    frags.append(text(x_p - 50, y_p - 90, "BB", size=12, color=FIELD, bold=True))
    
    frags.append(arrow(x_p - 35 * math.cos(rad_bb), y_p - 70 - 35 * math.sin(rad_bb), x_p, y_p - 105, color=NEG, sw=2.5))
    frags.append(text(x_p + 25, y_p - 95, "BC", size=12, color=NEG, bold=True))
    
    frags.append(arrow(x_p, y_p, x_p, y_p - 105, color=POS, sw=3))
    frags.append(textbox(x_p + 70, y_p - 50, "|Врез| = const", size=13, fill="#ffffff", stroke=POS, color=POS, bold=True)[0])
    
    frags.append(textbox(x_p, 340, "Модуль поля Врез не змінюється у часі,\nзмінюється лише його напрямок (кут ωt).", size=12, fill="#ffffff", stroke=LINE)[0])

    render(os.path.join(IMG_DIR, 'rotating-magnetic-field.svg'), w, h, *frags)


def generate_two_wattmeter():
    """Фігура 4: Вимірювання потужності методом двох ватметрів (схема Арона)."""
    w, h = 780, 360
    frags = []
    
    frags.append(text(390, 25, "Схема вимірювання потужності методом двох ватметрів (Арона)", size=16, bold=True))
    
    y_l1, y_l2, y_l3 = 80, 180, 280
    
    frags.append(line(40, y_l1, 650, y_l1, color=POS, sw=2))
    frags.append(line(40, y_l2, 650, y_l2, color=FIELD, sw=2))
    frags.append(line(40, y_l3, 650, y_l3, color=NEG, sw=2))
    
    frags.append(textbox(40, y_l1 - 25, "L1", size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)[0])
    frags.append(textbox(40, y_l2 - 25, "L2", size=12, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True)[0])
    frags.append(textbox(40, y_l3 - 25, "L3", size=12, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)[0])
    
    frags.append(circle(200, y_l1, 24, fill="#ffffff", stroke=POS, sw=2))
    frags.append(text(200, y_l1 + 4, "W1", size=13, color=POS, bold=True))
    frags.append(line(200, y_l1 + 24, 200, y_l2, color=POS, sw=1.5, dash="4,3"))
    frags.append(circle(200, y_l2, 4, fill=FIELD, stroke=FIELD))
    
    frags.append(circle(400, y_l3, 24, fill="#ffffff", stroke=NEG, sw=2))
    frags.append(text(400, y_l3 + 4, "W2", size=13, color=NEG, bold=True))
    frags.append(line(400, y_l3 - 24, 400, y_l2, color=NEG, sw=1.5, dash="4,3"))
    frags.append(circle(400, y_l2, 4, fill=FIELD, stroke=FIELD))
    
    frags.append(rect(630, 60, 110, 240, fill="#f4f6f8", stroke=LINE, sw=2, rx=8))
    frags.append(mtext(685, 175, "Трифазне\nнавантаження\n(3-провідне)", size=13, color=INK, bold=True))
    
    frags.append(textbox(320, 330, "Повна активна потужність: P = P(W1) + P(W2)", size=14, fill="#ffffff", stroke=LINE, bold=True)[0])

    render(os.path.join(IMG_DIR, 'two-wattmeter-method.svg'), w, h, *frags)


if __name__ == '__main__':
    generate_waveforms()
    generate_star_delta()
    generate_rotating_field()
    generate_two_wattmeter()
    print("Всі 4 фігури згенеровано успішно у img/")

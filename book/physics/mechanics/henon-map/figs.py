# -*- coding: utf-8 -*-
"""Фігури до статті «Відображення Ено».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Fig 1: Структура дивного атрактора Ено ────────────────────────────────────
def fig_henon_attractor_structure():
    a, b = 1.4, 0.3
    x, y = 0.1, 0.1
    for _ in range(500):
        xn = 1.0 - a * x * x + y
        yn = b * x
        x, y = xn, yn

    pts = []
    for _ in range(12000):
        xn = 1.0 - a * x * x + y
        yn = b * x
        x, y = xn, yn
        pts.append((x, y))

    W, H = 800, 580
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Дивний атрактор Ено (a = 1.4, b = 0.3)", size=17, bold=True))

    PL, PW = 60, 470
    PT, PH = 60, 460

    xmin, xmax = -1.35, 1.35
    ymin, ymax = -0.42, 0.42

    def Tx(x_val):
        return PL + (x_val - xmin) / (xmax - xmin) * PW

    def Ty(y_val):
        return PT + PH - (y_val - ymin) / (ymax - ymin) * PH

    f.append(rect(PL, PT, PW, PH, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=4))

    # Сітка та осі
    for x_grid in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        gx = Tx(x_grid)
        f.append(line(gx, PT, gx, PT + PH, color="#e1e4e8", sw=0.8, dash="3,3"))
        f.append(text(gx, PT + PH + 18, "%.1f" % x_grid, size=11, color=MUTED))

    for y_grid in [-0.3, -0.15, 0.0, 0.15, 0.3]:
        gy = Ty(y_grid)
        f.append(line(PL, gy, PL + PW, gy, color="#e1e4e8", sw=0.8, dash="3,3"))
        f.append(text(PL - 12, gy + 4, "%.2f" % y_grid, size=11, color=MUTED, anchor="end"))

    f.append(text(PL + PW / 2, PT + PH + 40, "Координата x", size=13, bold=True))
    f.append(text(PL - 42, PT + PH / 2, "y", size=13, bold=True, italic=True))

    # Точки атрактора
    dot_str = []
    for px, py in pts:
        cx = Tx(px)
        cy = Ty(py)
        dot_str.append('<circle cx="%.1f" cy="%.1f" r="0.6" fill="%s" opacity="0.65"/>' % (cx, cy, NEG))
    f.append("".join(dot_str))

    # Нерухомі точки (сідла)
    fx1, fy1 = 0.631354, 0.189406
    fx2, fy2 = -1.131354, -0.339406

    f.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s" stroke="#ffffff" stroke-width="1.5"/>' % (Tx(fx1), Ty(fy1), POS))
    f.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s" stroke="#ffffff" stroke-width="1.5"/>' % (Tx(fx2), Ty(fy2), POS))

    # Позначка сідлової точки у порожній верхній лівій частині графіка
    lbl_x, lbl_y = PL + 35, PT + 30
    f.append(line(lbl_x + 50, lbl_y + 12, Tx(fx1) - 6, Ty(fy1) - 6, color=POS, sw=1.2, dash="3,3"))
    f.append(text(lbl_x, lbl_y, "нерухома точка (сідло)", size=11, color=POS, anchor="start", bold=True))

    # Прямокутник збільшення (Zoom region)
    zx1, zx2 = 0.15, 0.45
    zy1, zy2 = 0.04, 0.16
    z_left, z_top = Tx(zx1), Ty(zy2)
    z_w, z_h = Tx(zx2) - Tx(zx1), Ty(zy1) - Ty(zy2)

    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="0" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,3"/>' % (z_left, z_top, z_w, z_h, FIELD))

    # Вставка збільшеного фрагмента (Zoom panel)
    ZL, ZW = 555, 215
    ZT, ZH = 120, 260

    f.append(rect(ZL, ZT, ZW, ZH, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(ZL + ZW / 2, ZT + 22, "Збільшення: фрактальні шари", size=12, color=FIELD, bold=True))

    f.append(line(z_left + z_w, z_top, ZL, ZT + 30, color=FIELD, sw=1.0, dash="3,3"))
    f.append(line(z_left + z_w, z_top + z_h, ZL, ZT + ZH, color=FIELD, sw=1.0, dash="3,3"))

    zoom_pts = [p for p in pts if zx1 <= p[0] <= zx2 and zy1 <= p[1] <= zy2]
    z_dot_str = []
    for px, py in zoom_pts:
        cx = ZL + (px - zx1) / (zx2 - zx1) * ZW
        cy = ZT + ZH - (py - zy1) / (zy2 - zy1) * (ZH - 40)
        z_dot_str.append('<circle cx="%.1f" cy="%.1f" r="0.9" fill="%s" opacity="0.85"/>' % (cx, cy, POS))
    f.append("".join(z_dot_str))

    info_box = textbox(ZL + ZW / 2, ZT + ZH + 65, "Канторівська вкладеність:\nкожна смуга розпадається\nна нескінченну сукупність\nтонших ліній", size=11, pad=8, fill="#f4f6f8", stroke="#d0d7de", sw=1.0, color=INK)[0]
    f.append(info_box)

    output = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    output.extend(f)
    output.append('</svg>')

    with open(os.path.join(IMG, 'henon-attractor-structure.svg'), 'w', encoding='utf-8') as out:
        out.write("\n".join(output))


# ── Fig 2: Три геометричні кроки відображення ─────────────────────────────────
def fig_henon_geometric_steps():
    W, H = 800, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Геометричне розкладення відображення Ено: розтягування, згин і поворот", size=16, bold=True))

    PW, PH = 165, 155
    P1_x, P1_y = 50, 75
    P2_x, P2_y = 295, 75
    P3_x, P3_y = 540, 75
    P4_x, P4_y = 295, 295

    def make_panel(px, py, title, subtitle):
        res = [rect(px, py, PW, PH, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=4)]
        res.append(text(px + PW / 2, py - 10, title, size=13, bold=True))
        res.append(text(px + PW / 2, py + PH + 16, subtitle, size=11, color=MUTED))
        res.append(line(px + 10, py + PH / 2, px + PW - 10, py + PH / 2, color="#e1e4e8", sw=0.8))
        res.append(line(px + PW / 2, py + 10, px + PW / 2, py + PH - 10, color="#e1e4e8", sw=0.8))
        return res

    f.extend(make_panel(P1_x, P1_y, "1. Початкова область", "квадрат у фазовій площині"))
    f.extend(make_panel(P2_x, P2_y, "2. Параболічний згин T₁", "y' = 1 − a·x² + y  (збереження площі)"))
    f.extend(make_panel(P3_x, P3_y, "3. Стискання T₂", "x'' = b·x'  (стискання площі в b разів)"))
    f.extend(make_panel(P4_x, P4_y, "4. Віддзеркалення T₃", "x''' = y'', y''' = x''  (підкова Ено)"))

    def map_p1(x, y):
        cx = P1_x + PW / 2 + x * 55
        cy = P1_y + PH / 2 - y * 55
        return cx, cy

    sq_pts = [(-0.6, -0.6), (0.6, -0.6), (0.6, 0.6), (-0.6, 0.6)]
    poly1 = " ".join("%.1f,%.1f" % map_p1(x, y) for x, y in sq_pts)
    f.append('<polygon points="%s" fill="#eaf2ff" stroke="%s" stroke-width="1.8" opacity="0.8"/>' % (poly1, NEG))

    def map_p2(x, y):
        yn = 0.8 - 1.1 * x * x + 0.4 * y
        cx = P2_x + PW / 2 + x * 50
        cy = P2_y + PH / 2 - yn * 50
        return cx, cy

    curve_top = [map_p2(x, 0.5) for x in [-0.6 + i * 0.1 for i in range(13)]]
    curve_bot = [map_p2(x, -0.5) for x in [0.6 - i * 0.1 for i in range(13)]]
    poly2 = " ".join("%.1f,%.1f" % (cx, cy) for cx, cy in curve_top + curve_bot)
    f.append('<polygon points="%s" fill="#eaf2ff" stroke="%s" stroke-width="1.8" opacity="0.8"/>' % (poly2, NEG))

    def map_p3(x, y):
        xn = 0.3 * x
        yn = 0.8 - 1.1 * x * x + 0.4 * y
        cx = P3_x + PW / 2 + xn * 120
        cy = P3_y + PH / 2 - yn * 50
        return cx, cy

    curve3_top = [map_p3(x, 0.5) for x in [-0.6 + i * 0.1 for i in range(13)]]
    curve3_bot = [map_p3(x, -0.5) for x in [0.6 - i * 0.1 for i in range(13)]]
    poly3 = " ".join("%.1f,%.1f" % (cx, cy) for cx, cy in curve3_top + curve3_bot)
    f.append('<polygon points="%s" fill="#eaf2ff" stroke="%s" stroke-width="1.8" opacity="0.8"/>' % (poly3, NEG))

    def map_p4(x, y):
        xn = 0.8 - 1.1 * x * x + 0.4 * y
        yn = 0.3 * x
        cx = P4_x + PW / 2 + xn * 50
        cy = P4_y + PH / 2 - yn * 120
        return cx, cy

    curve4_top = [map_p4(x, 0.5) for x in [-0.6 + i * 0.1 for i in range(13)]]
    curve4_bot = [map_p4(x, -0.5) for x in [0.6 - i * 0.1 for i in range(13)]]
    poly4 = " ".join("%.1f,%.1f" % (cx, cy) for cx, cy in curve4_top + curve4_bot)
    f.append('<polygon points="%s" fill="#fde8e8" stroke="%s" stroke-width="2.0" opacity="0.85"/>' % (poly4, POS))

    f.append(line(P1_x + PW + 10, P1_y + PH / 2, P2_x - 10, P1_y + PH / 2, color=INK, sw=1.8))
    f.append('<path d="M %d %d L %d %d L %d %d Z" fill="%s"/>' % (P2_x - 10, P1_y + PH / 2 - 5, P2_x - 2, P1_y + PH / 2, P2_x - 10, P1_y + PH / 2 + 5, INK))

    f.append(line(P2_x + PW + 10, P2_y + PH / 2, P3_x - 10, P2_y + PH / 2, color=INK, sw=1.8))
    f.append('<path d="M %d %d L %d %d L %d %d Z" fill="%s"/>' % (P3_x - 10, P2_y + PH / 2 - 5, P3_x - 2, P2_y + PH / 2, P3_x - 10, P2_y + PH / 2 + 5, INK))

    f.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,4"/>' %
             (P3_x + PW / 2, P3_y + PH + 10, P3_x + PW / 2, P4_y + PH / 2, P4_x + PW + 10, P4_y + PH / 2, INK))
    f.append('<path d="M %d %d L %d %d L %d %d Z" fill="%s"/>' % (P4_x + PW + 10, P4_y + PH / 2 - 5, P4_x + PW + 2, P4_y + PH / 2, P4_x + PW + 10, P4_y + PH / 2 + 5, INK))

    f.append(textbox(W / 2, 525, "Результат композиції T = T₃ ∘ T₂ ∘ T₁ дає розтягнення й складання аркуша (підкову Смейла)", size=12, pad=6, fill="#f4f6f8", stroke="#d0d7de", sw=1.0, color=INK, bold=True)[0])

    output = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    output.extend(f)
    output.append('</svg>')

    with open(os.path.join(IMG, 'henon-geometric-steps.svg'), 'w', encoding='utf-8') as out:
        out.write("\n".join(output))


# ── Fig 3: Біфуркаційна діаграма ─────────────────────────────────────────────
def fig_henon_bifurcation_diagram():
    W, H = 800, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Біфуркаційна діаграма відображення Ено при b = 0.3", size=16, bold=True))

    PL, PW = 70, 680
    PT, PH = 60, 390

    amin, amax = 0.0, 1.45
    xmin, xmax = -1.4, 1.4

    def Ta(a_val):
        return PL + (a_val - amin) / (amax - amin) * PW

    def Tx(x_val):
        return PT + PH - (x_val - xmin) / (xmax - xmin) * PH

    f.append(rect(PL, PT, PW, PH, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=4))

    for a_g in [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4]:
        ga = Ta(a_g)
        f.append(line(ga, PT, ga, PT + PH, color="#e1e4e8", sw=0.8, dash="3,3"))
        f.append(text(ga, PT + PH + 18, "%.1f" % a_g, size=11, color=MUTED))

    for x_g in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        gx = Tx(x_g)
        f.append(line(PL, gx, PL + PW, gx, color="#e1e4e8", sw=0.8, dash="3,3"))
        f.append(text(PL - 12, gx + 4, "%.1f" % x_g, size=11, color=MUTED, anchor="end"))

    f.append(text(PL + PW / 2, PT + PH + 40, "Параметр нелінійності a", size=13, bold=True))
    f.append(text(PL - 42, PT + PH / 2, "x", size=13, bold=True, italic=True))

    b_val = 0.3
    dots = []
    a_steps = 450
    for i in range(a_steps):
        a_curr = amin + i * (amax - amin) / a_steps
        x, y = 0.1, 0.1
        escaped = False
        for _ in range(300):
            xn = 1.0 - a_curr * x * x + y
            yn = b_val * x
            x, y = xn, yn
            if abs(x) > 10.0:
                escaped = True
                break
        if escaped:
            continue
        ca = Ta(a_curr)
        for _ in range(60):
            xn = 1.0 - a_curr * x * x + y
            yn = b_val * x
            x, y = xn, yn
            cx = Tx(x)
            if PT <= cx <= PT + PH:
                dots.append('<circle cx="%.1f" cy="%.1f" r="0.5" fill="%s" opacity="0.6"/>' % (ca, cx, INK))

    f.append("".join(dots))

    # Біфуркаційні позначки (проведені без перетину з текстом)
    a1_x = Ta(0.3675)
    ac_x = Ta(1.058)
    acr_x = Ta(1.42)

    # Лінії тільки в нижній/верхній частинах без накриття тексту
    f.append(line(a1_x, PT + 40, a1_x, PT + PH, color=NEG, sw=1.2, dash="4,3"))
    f.append(line(ac_x, PT + 40, ac_x, PT + PH, color=POS, sw=1.2, dash="4,3"))
    f.append(line(acr_x, PT + 40, acr_x, PT + PH, color=FIELD, sw=1.2, dash="4,3"))

    # Написи розташовані у порожньому просторі графіка як чистий текст (без суцільних рамок)
    f.append(text(a1_x, PT + 20, "a = 0.3675 (початок подвоєння)", size=11, color=NEG, bold=True))
    f.append(text(ac_x - 10, PT + 34, "a_c ≈ 1.058 (хаос)", size=11, color=POS, bold=True))
    f.append(text(acr_x - 15, PT + 48, "a ≈ 1.42 (криза)", size=11, color=FIELD, bold=True))

    output = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)]
    output.extend(f)
    output.append('</svg>')

    with open(os.path.join(IMG, 'henon-bifurcation-diagram.svg'), 'w', encoding='utf-8') as out:
        out.write("\n".join(output))


if __name__ == '__main__':
    fig_henon_attractor_structure()
    fig_henon_geometric_steps()
    fig_henon_bifurcation_diagram()
    print("Фігури відображення Ено успішно згенеровано у ./img/")

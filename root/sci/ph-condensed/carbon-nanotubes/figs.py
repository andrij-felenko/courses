# -*- coding: utf-8 -*-
import sys
import os
import math

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_folding_vector():
    """Малюнок 1: Вектор хіральності C_h на ґратці графену"""
    dw = 840
    dh = 460
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (dw, dh, dw, dh))
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>' % LINE)
    out.append(rect(0, 0, dw, dh, fill=BG, stroke="none"))

    # Заголовок
    tb_h, w_h, _ = textbox(dw/2, 26, "Гексагональна ґратка графену та вектори хіральності", size=16, bold=True, fill="#eef2f7")
    out.append(tb_h)

    # Ґратка
    a_len = 35
    ox, oy = 70, 260

    a1x = a_len * math.cos(math.radians(30))
    a1y = -a_len * math.sin(math.radians(30))
    a2x = a_len * math.cos(math.radians(30))
    a2y = a_len * math.sin(math.radians(30))

    max_n, max_m = 7, 5
    grid_pts = {}
    for n in range(max_n + 1):
        for m in range(max_m + 1):
            px = ox + n * a1x + m * a2x
            py = oy + n * a1y + m * a2y
            grid_pts[(n, m)] = (px, py)

    # Малюємо лінії ґратки
    for n in range(max_n + 1):
        for m in range(max_m + 1):
            if n < max_n:
                p1 = grid_pts[(n, m)]
                p2 = grid_pts[(n + 1, m)]
                out.append(line(p1[0], p1[1], p2[0], p2[1], color="#e0e0e0", sw=1))
            if m < max_m:
                p1 = grid_pts[(n, m)]
                p2 = grid_pts[(n, m + 1)]
                out.append(line(p1[0], p1[1], p2[0], p2[1], color="#e0e0e0", sw=1))

    # Точки вузлів
    for (n, m), (px, py) in grid_pts.items():
        clr = MUTED
        if (n, m) == (0, 0):
            clr = POS
        elif (n, m) == (4, 4): # armchair (4,4)
            clr = NEG
        elif (n, m) == (6, 0): # zigzag (6,0)
            clr = FIELD
        elif (n, m) == (5, 2): # chiral (5,2)
            clr = "#8e44ad"
        out.append(circle(px, py, 4, fill=clr, stroke=LINE, sw=1))

    # Базисні вектори a1, a2
    p0 = grid_pts[(0, 0)]
    pa1 = grid_pts[(1, 0)]
    pa2 = grid_pts[(0, 1)]

    out.append(arrow(p0[0], p0[1], pa1[0], pa1[1], color=POS, sw=2.2))
    out.append(arrow(p0[0], p0[1], pa2[0], pa2[1], color=POS, sw=2.2))

    tb_a1, _, _ = textbox(pa1[0] - 25, pa1[1] - 20, "a₁", size=12, bold=True, fill="#fadbd8", stroke=POS)
    tb_a2, _, _ = textbox(pa2[0] - 25, pa2[1] + 20, "a₂", size=12, bold=True, fill="#fadbd8", stroke=POS)
    out.append(tb_a1)
    out.append(tb_a2)

    # Вектор C_h для (5, 2)
    p_ch = grid_pts[(5, 2)]
    out.append(arrow(p0[0], p0[1], p_ch[0], p_ch[1], color="#8e44ad", sw=2.8))
    tb_ch, _, _ = textbox(620, 180, "Cₕ = 5a₁ + 2a₂ (хіральна)", size=12, bold=True, fill="#e8daef", stroke="#8e44ad")
    out.append(tb_ch)

    # Зигзаг вектор (6,0)
    p_zz = grid_pts[(6, 0)]
    out.append(arrow(p0[0], p0[1], p_zz[0], p_zz[1], color=FIELD, sw=2))
    tb_zz, _, _ = textbox(620, 250, "Cₕ = (6,0) Зигзаг", size=11, bold=True, fill="#d4efdf", stroke=FIELD)
    out.append(tb_zz)

    # Крісловий вектор (4,4)
    p_ac = grid_pts[(4, 4)]
    out.append(arrow(p0[0], p0[1], p_ac[0], p_ac[1], color=NEG, sw=2))
    tb_ac, _, _ = textbox(620, 320, "Cₕ = (4,4) Кріслова", size=11, bold=True, fill="#d6eaf8", stroke=NEG)
    out.append(tb_ac)

    # Пояснення типів праворуч вгорі
    leg_lines = [
        "Класифікація нанотрубок за (n, m):",
        "• n = m : кріслова (Armchair) — завжди метал",
        "• m = 0 : зигзагоподібна (Zigzag) — напівпровідник або метал",
        "• n ≠ m ≠ 0 : хіральна (Chiral) — спіральна симетрія",
        "• Умова металічності: (n - m) mod 3 = 0"
    ]
    tb_leg, _, _ = textbox(620, 80, "\n".join(leg_lines), size=11, pad=8, fill="#fcf3cf", stroke="#f1c40f")
    out.append(tb_leg)

    out.append('</svg>')
    return "".join(out)

def build_cnt_types():
    """Малюнок 2: Геометричні типи вуглецевих нанотрубок та багатошаровість"""
    dw = 760
    dh = 360
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (dw, dh, dw, dh))
    out.append(rect(0, 0, dw, dh, fill=BG, stroke="none"))

    # Заголовок
    tb_h, _, _ = textbox(dw/2, 28, "Типи атомної конфігурації та шаруватість нанотрубок", size=16, bold=True, fill="#eef2f7")
    out.append(tb_h)

    # Панель 1: Armchair (n, n)
    x1 = 130
    tb_p1, _, _ = textbox(x1, 65, "Кріслова (Armchair)\n(n, n)", size=13, bold=True, fill="#d6eaf8", stroke=NEG)
    out.append(tb_p1)
    out.append(rect(x1 - 40, 100, 80, 160, fill="#ebf5fb", stroke=NEG, sw=2, rx=12))
    for y in range(115, 255, 20):
        out.append(line(x1 - 35, y, x1 - 10, y + 8, color=NEG, sw=1.8))
        out.append(line(x1 - 10, y + 8, x1 + 10, y, color=NEG, sw=1.8))
        out.append(line(x1 + 10, y, x1 + 35, y + 8, color=NEG, sw=1.8))
    tb_lbl1, _, _ = textbox(x1, 285, "Металевий тип\n(металева провідність)", size=11, color=NEG, fill="#ffffff", stroke=NEG)
    out.append(tb_lbl1)

    # Панель 2: Zigzag (n, 0)
    x2 = 380
    tb_p2, _, _ = textbox(x2, 65, "Зигзагоподібна (Zigzag)\n(n, 0)", size=13, bold=True, fill="#d4efdf", stroke=FIELD)
    out.append(tb_p2)
    out.append(rect(x2 - 40, 100, 80, 160, fill="#eafaf1", stroke=FIELD, sw=2, rx=12))
    for y in range(115, 255, 20):
        out.append(line(x2 - 35, y, x2 - 35, y + 12, color=FIELD, sw=1.8))
        out.append(line(x2 - 35, y + 12, x2, y + 18, color=FIELD, sw=1.8))
        out.append(line(x2, y + 18, x2 + 35, y + 12, color=FIELD, sw=1.8))
        out.append(line(x2 + 35, y + 12, x2 + 35, y, color=FIELD, sw=1.8))
    tb_lbl2, _, _ = textbox(x2, 285, "Напівпровідник/метал\n((n-m) mod 3 = 0)", size=11, color=FIELD, fill="#ffffff", stroke=FIELD)
    out.append(tb_lbl2)

    # Панель 3: SWCNT vs MWCNT
    x3 = 630
    tb_p3, _, _ = textbox(x3, 65, "Багатошарова (MWCNT)\nта Одношарова (SWCNT)", size=13, bold=True, fill="#fcf3cf", stroke="#f1c40f")
    out.append(tb_p3)

    out.append(rect(x3 - 20, 130, 40, 130, fill="#fef9e7", stroke=POS, sw=1.8, rx=8))
    out.append(rect(x3 - 40, 110, 80, 150, fill="none", stroke=INK, sw=2, rx=12))
    out.append(rect(x3 - 55, 95, 110, 175, fill="none", stroke=MUTED, sw=1.5, rx=16))

    tb_lbl3, _, _ = textbox(x3, 295, "Міжшарова відстань d ≈ 0.34 нм\nВан-дер-Ваальсів зв'язок", size=11, color=INK, fill="#ffffff", stroke=MUTED)
    out.append(tb_lbl3)

    out.append('</svg>')
    return "".join(out)

def build_zone_folding():
    """Малюнок 3: Зонне згортання (Zone folding) у першій зоні Бріллюена"""
    dw = 760
    dh = 380
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (dw, dh, dw, dh))
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>' % LINE)
    out.append(rect(0, 0, dw, dh, fill=BG, stroke="none"))

    tb_h, _, _ = textbox(dw/2, 28, "Квантування ліній розсіяння у зоні Бріллюена графена", size=16, bold=True, fill="#eef2f7")
    out.append(tb_h)

    # Панель А: Метал (проходить через K)
    cx1, cy1 = 200, 210
    r_hex = 100

    tb_a, _, _ = textbox(cx1, 65, "Металева нанотрубка: лінія проходить через K", size=12, bold=True, fill="#d6eaf8", stroke=NEG)
    out.append(tb_a)

    hex_pts1 = []
    for i in range(6):
        ang = math.radians(60 * i)
        hx = cx1 + r_hex * math.cos(ang)
        hy = cy1 + r_hex * math.sin(ang)
        hex_pts1.append((hx, hy))

    poly_str1 = " ".join(["%.1f,%.1f" % pt for pt in hex_pts1])
    out.append('<polygon points="%s" fill="#f4f6f8" stroke="%s" stroke-width="1.8"/>' % (poly_str1, LINE))

    for i, pt in enumerate(hex_pts1):
        out.append(circle(pt[0], pt[1], 4, fill=POS, stroke=LINE, sw=1))

    for offset in [-60, -30, 0, 30, 60]:
        x_start = cx1 - 80
        x_end = cx1 + 80
        y_pos = cy1 + offset
        clr = POS if offset == 0 else NEG
        sw_l = 2.2 if offset == 0 else 1.2
        out.append(line(x_start, y_pos, x_end, y_pos, color=clr, sw=sw_l))

    tb_k1, _, _ = textbox(cx1 + r_hex + 20, cy1, "K (Діракова точка)\nE_g = 0 (без щілини)", size=11, color=POS, fill="#fadbd8", stroke=POS)
    out.append(tb_k1)

    # Панель Б: Напівпровідник (оминає K)
    cx2, cy2 = 560, 210
    tb_b, _, _ = textbox(cx2, 65, "Напівпровідникова CNT: лінії оминають K", size=12, bold=True, fill="#d4efdf", stroke=FIELD)
    out.append(tb_b)

    hex_pts2 = []
    for i in range(6):
        ang = math.radians(60 * i)
        hx = cx2 + r_hex * math.cos(ang)
        hy = cy2 + r_hex * math.sin(ang)
        hex_pts2.append((hx, hy))

    poly_str2 = " ".join(["%.1f,%.1f" % pt for pt in hex_pts2])
    out.append('<polygon points="%s" fill="#f4f6f8" stroke="%s" stroke-width="1.8"/>' % (poly_str2, LINE))

    for i, pt in enumerate(hex_pts2):
        out.append(circle(pt[0], pt[1], 4, fill=POS, stroke=LINE, sw=1))

    for offset in [-75, -45, -15, 15, 45, 75]:
        x_start = cx2 - 80
        x_end = cx2 + 80
        y_pos = cy2 + offset
        out.append(line(x_start, y_pos, x_end, y_pos, color=FIELD, sw=1.4, dash="4,2"))

    tb_k2, _, _ = textbox(cx2 + r_hex + 20, cy2, "Зсув від K\nE_g ∝ 1 / d (є щілина)", size=11, color=FIELD, fill="#d4efdf", stroke=FIELD)
    out.append(tb_k2)

    tb_bot, _, _ = textbox(dw/2, 345, "1D підзони утворюються внаслідок граничної умови квантування хвильового вектора уздовж кола нанотрубки", size=11, color=INK, fill="#ffffff", stroke=MUTED)
    out.append(tb_bot)

    out.append('</svg>')
    return "".join(out)

def build_density_of_states():
    """Малюнок 4: Густина електронних станів (DOS) та сингулярності Ван Гова"""
    dw = 760
    dh = 380
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (dw, dh, dw, dh))
    out.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/></marker></defs>' % LINE)
    out.append(rect(0, 0, dw, dh, fill=BG, stroke="none"))

    tb_h, _, _ = textbox(dw/2, 28, "Густина електронних станів DOS(E) і сингулярності Ван Гова", size=16, bold=True, fill="#eef2f7")
    out.append(tb_h)

    # Графік Металевої CNT (ліворуч)
    ox1, oy1 = 80, 200
    w_g, h_g = 260, 240

    tb_g1, _, _ = textbox(ox1 + w_g/2, 65, "Металева CNT (E_F при DOS > 0)", size=12, bold=True, fill="#d6eaf8", stroke=NEG)
    out.append(tb_g1)

    out.append(arrow(ox1, oy1 + h_g/2, ox1 + w_g, oy1 + h_g/2, color=LINE, sw=1.5))
    out.append(arrow(ox1 + w_g/2, oy1 + h_g/2 + 20, ox1 + w_g/2, oy1 - h_g/2, color=LINE, sw=1.5))

    out.append(line(ox1, oy1, ox1 + w_g, oy1, color=MUTED, sw=1, dash="3,3"))

    pts_m = [
        (ox1 + 20, oy1), (ox1 + 40, oy1 - 80), (ox1 + 55, oy1 - 15),
        (ox1 + 80, oy1 - 60), (ox1 + 105, oy1 - 10), (ox1 + 130, oy1 - 10),
        (ox1 + 155, oy1 - 10), (ox1 + 180, oy1 - 60), (ox1 + 205, oy1 - 15),
        (ox1 + 220, oy1 - 80), (ox1 + 240, oy1)
    ]
    path_str_m = "M " + " L ".join(["%.1f,%.1f" % p for p in pts_m])
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path_str_m, NEG))

    tb_ef1, _, _ = textbox(ox1 + w_g/2 + 35, oy1 + 15, "E_F (Рівень Фермі)", size=10, bold=True, color=NEG, fill="#d6eaf8", stroke=NEG)
    out.append(tb_ef1)

    # Графік Напівпровідникової CNT (праворуч)
    ox2, oy2 = 440, 200
    tb_g2, _, _ = textbox(ox2 + w_g/2, 65, "Напівпровідникова CNT (Заборонена зона E_g)", size=12, bold=True, fill="#d4efdf", stroke=FIELD)
    out.append(tb_g2)

    out.append(arrow(ox2, oy2 + h_g/2, ox2 + w_g, oy2 + h_g/2, color=LINE, sw=1.5))
    out.append(arrow(ox2 + w_g/2, oy2 + h_g/2 + 20, ox2 + w_g/2, oy2 - h_g/2, color=LINE, sw=1.5))

    pts_s = [
        (ox2 + 20, oy2), (ox2 + 45, oy2 - 80), (ox2 + 65, oy2 - 20),
        (ox2 + 90, oy2 - 60), (ox2 + 105, oy2),
        (ox2 + 155, oy2),
        (ox2 + 170, oy2 - 60), (ox2 + 195, oy2 - 20),
        (ox2 + 215, oy2 - 80), (ox2 + 240, oy2)
    ]
    path_str_s = "M " + " L ".join(["%.1f,%.1f" % p for p in pts_s])
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path_str_s, FIELD))

    out.append(rect(ox2 + 105, oy2 - 40, 50, 40, fill="#fadbd8", stroke=POS, sw=1, rx=3))
    tb_eg, _, _ = textbox(ox2 + 130, oy2 - 20, "E_g", size=11, bold=True, color=POS, fill="#fadbd8", stroke=POS)
    out.append(tb_eg)

    tb_vh, _, _ = textbox(dw/2, 345, "1D сингулярності Ван Гова ∝ 1 / √(E - E_i) забезпечують резонансне оптичне поглинання", size=11, color=INK, fill="#ffffff", stroke=MUTED)
    out.append(tb_vh)

    out.append('</svg>')
    return "".join(out)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    figs = [
        ('folding-vector.svg', build_folding_vector()),
        ('cnt-types.svg', build_cnt_types()),
        ('zone-folding.svg', build_zone_folding()),
        ('density-of-states.svg', build_density_of_states())
    ]

    for fname, content in figs:
        fpath = os.path.join(img_dir, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Згенеровано: {fpath}")

if __name__ == '__main__':
    main()

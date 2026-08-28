# -*- coding: utf-8 -*-
"""Фігури до теми «Імпульсний перетворювач як найгучніший вузол».
Запуск: python figs.py   → створює SVG-діаграми в ./img/
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Дзвін комутаційного вузла SW до та після RC-снубера ──────────────────
def fig_switch_node_ringing():
    W, H = 820, 390
    p = []

    # Заголовок
    p.append(text(W / 2, 28, "Осцилограма вузла SW до та після встановлення RC-снубера", size=16, bold=True))

    # Ліва панель: Без снубера (Undamped / Ringing)
    x1, y1, w1, h1 = 35, 55, 360, 310
    p.append(rect(x1, y1, w1, h1, fill="#fffaf9", stroke=POS, sw=1.5, rx=8))
    p.append(text(x1 + w1 / 2, y1 + 24, "Без снубера: паразитна осциляція", size=13, bold=True, color=POS))
    p.append(text(x1 + w1 / 2, y1 + 42, "Резонанс L_par та C_oss (50–300 МГц)", size=11, color=MUTED))

    # Сітка та осі для лівої панелі
    gx0, gy0, gw, gh = x1 + 45, y1 + 65, 290, 175
    p.append(rect(gx0, gy0, gw, gh, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=4))
    
    # Горизонтальні пунктирні лінії (рівні напруги)
    y_gnd = gy0 + 150
    y_vin = gy0 + 90
    y_spk = gy0 + 25
    
    p.append(line(gx0, y_gnd, gx0 + gw, y_gnd, color="#d0d0d0", sw=1, dash="4,4"))
    p.append(line(gx0, y_vin, gx0 + gw, y_vin, color="#b0c4de", sw=1, dash="4,4"))
    p.append(line(gx0, y_spk, gx0 + gw, y_spk, color="#ffc0cb", sw=1, dash="3,3"))

    p.append(text(gx0 - 8, y_gnd + 4, "0 В", size=10, color=MUTED, anchor="end"))
    p.append(text(gx0 - 8, y_vin + 4, "V_IN", size=10, color=NEG, anchor="end", bold=True))
    p.append(text(gx0 - 8, y_spk + 4, "V_MAX", size=10, color=POS, anchor="end", bold=True))

    # Крива дзвенячого сигналу (без снубера)
    pts_undamped = []
    # Фаза 0: низький рівень (0V)
    for x_rel in range(0, 30):
        pts_undamped.append((gx0 + x_rel, y_gnd))
    # Фаза 1: надшвидке наростання (2 нс)
    for x_rel in range(30, 42):
        frac = (x_rel - 30) / 12.0
        yy = y_gnd - frac * (y_gnd - y_spk)
        pts_undamped.append((gx0 + x_rel, yy))
    # Фаза 2: затухаючий синус (резонансний дзвін)
    for x_rel in range(42, 280):
        t = x_rel - 42
        decay = math.exp(-t / 45.0)
        yy = y_vin - (y_vin - y_spk) * decay * math.cos(t * 2 * math.pi / 22.0)
        pts_undamped.append((gx0 + x_rel, yy))

    path_d1 = "M " + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts_undamped)
    p.append(f'<path d="{path_d1}" fill="none" stroke="{POS}" stroke-width="2.2" stroke-linejoin="round"/>')

    # Маркери та виноски лівої панелі
    p.append(line(gx0 + 42, y_spk, gx0 + 100, y_spk, color=POS, sw=1, dash="2,2"))
    p.append(text(gx0 + 145, y_spk - 6, "Перенапруга (+80% V_IN)", size=10, color=POS, bold=True))
    t_x1, t_x2 = gx0 + 42, gx0 + 64
    p.append(line(t_x1, y_vin + 35, t_x2, y_vin + 35, color=LINE, sw=1.2))
    p.append(line(t_x1, y_vin + 30, t_x1, y_vin + 40, color=LINE, sw=1.2))
    p.append(line(t_x2, y_vin + 30, t_x2, y_vin + 40, color=LINE, sw=1.2))
    p.append(text((t_x1 + t_x2) / 2, y_vin + 50, "T_ring", size=10, color=INK, bold=True))

    # Опис наслідків лівої панелі
    p.append(text(x1 + 18, y1 + 262, "• Ризик лавинного пробою MOSFET", size=10, color=INK, anchor="start"))
    p.append(text(x1 + 18, y1 + 282, "• Потужне E/H випромінювання (EMI)", size=10, color=INK, anchor="start"))
    p.append(text(x1 + 18, y1 + 300, "• Ємнісні струмові сплески у підкладку", size=10, color=INK, anchor="start"))

    # Права панель: З RC-снубером (Damped)
    x2, y2, w2, h2 = 425, 55, 360, 310
    p.append(rect(x2, y2, w2, h2, fill="#f6faf6", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(x2 + w2 / 2, y2 + 24, "З оптимізованим RC-снубером", size=13, bold=True, color=FIELD))
    p.append(text(x2 + w2 / 2, y2 + 42, "Критичне демпфування (R_snub = Z_0)", size=11, color=MUTED))

    # Сітка та осі для правої панелі
    gx1, gy1 = x2 + 45, y2 + 65
    p.append(rect(gx1, gy1, gw, gh, fill="#ffffff", stroke="#e0e0e0", sw=1, rx=4))

    p.append(line(gx1, y_gnd, gx1 + gw, y_gnd, color="#d0d0d0", sw=1, dash="4,4"))
    p.append(line(gx1, y_vin, gx1 + gw, y_vin, color="#b0c4de", sw=1, dash="4,4"))
    p.append(line(gx1, y_spk, gx1 + gw, y_spk, color="#ffc0cb", sw=1, dash="3,3"))

    p.append(text(gx1 - 8, y_gnd + 4, "0 В", size=10, color=MUTED, anchor="end"))
    p.append(text(gx1 - 8, y_vin + 4, "V_IN", size=10, color=NEG, anchor="end", bold=True))

    # Крива сигналу зі снубером (Damped)
    pts_damped = []
    for x_rel in range(0, 30):
        pts_damped.append((gx1 + x_rel, y_gnd))
    for x_rel in range(30, 60):
        frac = (x_rel - 30) / 30.0
        yy = y_gnd - (y_gnd - y_vin) * (1.0 - math.exp(-frac * 3.5)) - 4.0 * math.sin(frac * math.pi)
        pts_damped.append((gx1 + x_rel, yy))
    for x_rel in range(60, 280):
        frac = (x_rel - 60) / 20.0
        yy = y_vin - 1.5 * math.exp(-frac) * math.cos(frac * 3.0)
        pts_damped.append((gx1 + x_rel, yy))

    path_d2 = "M " + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts_damped)
    p.append(f'<path d="{path_d2}" fill="none" stroke="{FIELD}" stroke-width="2.2" stroke-linejoin="round"/>')

    # Анотація чистого фронту
    p.append(text(gx1 + 140, y_vin - 15, "Плавний вихід на V_IN (без дзвону)", size=10, color=FIELD, bold=True))
    p.append(arrow(gx1 + 120, y_vin - 10, gx1 + 65, y_vin - 2, color=FIELD, sw=1.5))

    # Опис переваг правої панелі
    p.append(text(x2 + 18, y2 + 262, "• Пригнічення високочастотного EMI на 15–25 дБ", size=10, color=INK, anchor="start"))
    p.append(text(x2 + 18, y2 + 282, "• Запас надійності за напругою ключа V_DS", size=10, color=INK, anchor="start"))
    p.append(text(x2 + 18, y2 + 300, "• Ціна: додаткові втрати P = C_snub · V_in² · f_sw", size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, "switch-node-ringing.svg"), W, H, *p)


# ── 2. Схема комплексного вхідного π-фільтра ────────────────────────────────
def fig_input_pi_filter():
    W, H = 840, 420
    p = []

    # Заголовок
    p.append(text(W / 2, 26, "Комплексний вхідний EMI-фільтр імпульсного перетворювача", size=16, bold=True))

    # Блоки фільтра (зонування)
    z1_x, z1_y, z1_w, z1_h = 30, 50, 240, 310
    p.append(rect(z1_x, z1_y, z1_w, z1_h, fill="#f0f4fc", stroke="#7090d0", sw=1.5, rx=8))
    p.append(text(z1_x + z1_w / 2, z1_y + 22, "1. Синфазний каскад (CM)", size=12, bold=True, color=NEG))
    p.append(text(z1_x + z1_w / 2, z1_y + 38, "Пригнічення синфазного струму", size=10, color=MUTED))

    z2_x, z2_y, z2_w, z2_h = 285, 50, 345, 310
    p.append(rect(z2_x, z2_y, z2_w, z2_h, fill="#fcf8f0", stroke="#d0a040", sw=1.5, rx=8))
    p.append(text(z2_x + z2_w / 2, z2_y + 22, "2. Диференційний π-каскад (DM)", size=12, bold=True, color="#b07010"))
    p.append(text(z2_x + z2_w / 2, z2_y + 38, "Демпфування імпедансу (Міддлбрук)", size=10, color=MUTED))

    z3_x, z3_y, z3_w, z3_h = 645, 50, 165, 310
    p.append(rect(z3_x, z3_y, z3_w, z3_h, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(z3_x + z3_w / 2, z3_y + 22, "3. Вузол DC-DC", size=12, bold=True, color=POS))
    p.append(text(z3_x + z3_w / 2, z3_y + 38, "Шумний перетворювач", size=10, color=MUTED))

    y_pwr = 100
    y_gnd = 260
    y_pe  = 330

    p.append(text(15, y_pwr + 4, "V_IN", size=11, bold=True, color=POS, anchor="end"))
    p.append(text(15, y_gnd + 4, "GND", size=11, bold=True, color=NEG, anchor="end"))

    p.append(line(25, y_pwr, 85, y_pwr, color=LINE, sw=2))
    p.append(line(25, y_gnd, 85, y_gnd, color=LINE, sw=2))

    # Синфазний дросель (CMC)
    cmc_x = 85
    p.append(rect(cmc_x, y_pwr - 14, 55, 28, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    p.append(text(cmc_x + 27, y_pwr + 4, "L_CM1", size=10, bold=True))
    p.append(rect(cmc_x, y_gnd - 14, 55, 28, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    p.append(text(cmc_x + 27, y_gnd + 4, "L_CM2", size=10, bold=True))
    p.append(line(cmc_x + 10, 175, cmc_x + 45, 175, color=MUTED, sw=2, dash="3,2"))
    p.append(line(cmc_x + 10, 182, cmc_x + 45, 182, color=MUTED, sw=2, dash="3,2"))
    p.append(circle(cmc_x + 6, y_pwr - 8, 3, fill=INK, stroke=INK))
    p.append(circle(cmc_x + 6, y_gnd - 8, 3, fill=INK, stroke=INK))

    p.append(line(cmc_x + 55, y_pwr, cmc_x + 85, y_pwr, color=LINE, sw=2))
    p.append(line(cmc_x + 55, y_gnd, cmc_x + 85, y_gnd, color=LINE, sw=2))

    # Y-конденсатори
    cy_x = cmc_x + 85
    p.append(circle(cy_x, y_pwr, 3.5, fill=INK, stroke=INK))
    p.append(line(cy_x, y_pwr, cy_x, 155, color=LINE, sw=1.5))
    p.append(line(cy_x - 12, 155, cy_x + 12, 155, color=LINE, sw=2))
    p.append(line(cy_x - 12, 163, cy_x + 12, 163, color=LINE, sw=2))
    p.append(text(cy_x + 16, 162, "C_Y1", size=10, color=NEG, bold=True, anchor="start"))
    p.append(line(cy_x, 163, cy_x, 195, color=LINE, sw=1.5))

    p.append(circle(cy_x, y_gnd, 3.5, fill=INK, stroke=INK))
    p.append(line(cy_x, y_gnd, cy_x, 235, color=LINE, sw=1.5))
    p.append(line(cy_x - 12, 235, cy_x + 12, 235, color=LINE, sw=2))
    p.append(line(cy_x - 12, 227, cy_x + 12, 227, color=LINE, sw=2))
    p.append(text(cy_x + 16, 234, "C_Y2", size=10, color=NEG, bold=True, anchor="start"))
    p.append(line(cy_x, 227, cy_x, 195, color=LINE, sw=1.5))

    p.append(circle(cy_x, 195, 3, fill=INK, stroke=INK))
    p.append(line(cy_x, 195, cy_x, y_pe, color=LINE, sw=1.5))
    p.append(line(cy_x - 14, y_pe, cy_x + 14, y_pe, color=MUTED, sw=2))
    p.append(line(cy_x - 9, y_pe + 4, cy_x + 9, y_pe + 4, color=MUTED, sw=1.6))
    p.append(line(cy_x - 4, y_pe + 8, cy_x + 4, y_pe + 8, color=MUTED, sw=1.2))
    p.append(text(cy_x, y_pe + 22, "Шасі / PE", size=10, color=MUTED))

    p.append(line(cy_x, y_pwr, 320, y_pwr, color=LINE, sw=2))
    p.append(line(cy_x, y_gnd, 320, y_gnd, color=LINE, sw=2))

    # C1
    c1_x = 320
    p.append(circle(c1_x, y_pwr, 3.5, fill=INK, stroke=INK))
    p.append(circle(c1_x, y_gnd, 3.5, fill=INK, stroke=INK))
    p.append(line(c1_x, y_pwr, c1_x, 172, color=LINE, sw=1.5))
    p.append(line(c1_x - 12, 172, c1_x + 12, 172, color=LINE, sw=2))
    p.append(line(c1_x - 12, 180, c1_x + 12, 180, color=LINE, sw=2))
    p.append(line(c1_x, 180, c1_x, y_gnd, color=LINE, sw=1.5))
    p.append(text(c1_x - 16, 179, "C_1 (MLCC)", size=10, color=INK, bold=True, anchor="end"))

    # L_diff
    ldiff_x = 360
    p.append(line(c1_x, y_pwr, ldiff_x, y_pwr, color=LINE, sw=2))
    p.append(rect(ldiff_x, y_pwr - 14, 60, 28, fill="#ffffff", stroke="#b07010", sw=2, rx=4))
    p.append(text(ldiff_x + 30, y_pwr + 4, "L_diff", size=11, bold=True, color="#b07010"))
    p.append(line(ldiff_x + 60, y_pwr, 460, y_pwr, color=LINE, sw=2))

    # Cd + Rd
    cd_x = 460
    p.append(circle(cd_x, y_pwr, 3.5, fill=INK, stroke=INK))
    p.append(circle(cd_x, y_gnd, 3.5, fill=INK, stroke=INK))
    p.append(line(cd_x, y_pwr, cd_x, 145, color=LINE, sw=1.5))
    p.append(line(cd_x - 12, 145, cd_x + 12, 145, color=LINE, sw=2))
    p.append(line(cd_x - 12, 153, cd_x + 12, 153, color=LINE, sw=2))
    p.append(text(cd_x + 16, 151, "C_d (≈ 4·C_2)", size=10, color="#b07010", bold=True, anchor="start"))
    p.append(line(cd_x, 153, cd_x, 185, color=LINE, sw=1.5))
    p.append(rect(cd_x - 10, 185, 20, 35, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    p.append(text(cd_x + 16, 205, "R_d (демпфер)", size=10, color="#b07010", bold=True, anchor="start"))
    p.append(line(cd_x, 220, cd_x, y_gnd, color=LINE, sw=1.5))

    # C2
    c2_x = 565
    p.append(line(cd_x, y_pwr, c2_x, y_pwr, color=LINE, sw=2))
    p.append(circle(c2_x, y_pwr, 3.5, fill=INK, stroke=INK))
    p.append(circle(c2_x, y_gnd, 3.5, fill=INK, stroke=INK))
    p.append(line(c2_x, y_pwr, c2_x, 172, color=LINE, sw=1.5))
    p.append(line(c2_x - 12, 172, c2_x + 12, 172, color=LINE, sw=2))
    p.append(line(c2_x - 12, 180, c2_x + 12, 180, color=LINE, sw=2))
    p.append(line(c2_x, 180, c2_x, y_gnd, color=LINE, sw=1.5))
    p.append(text(c2_x + 16, 179, "C_2 (MLCC)", size=10, color=INK, bold=True, anchor="start"))

    # З'єднання до DC-DC
    p.append(line(c2_x, y_pwr, 665, y_pwr, color=LINE, sw=2))
    p.append(line(c1_x, y_gnd, 665, y_gnd, color=LINE, sw=2))

    # Блок DC-DC
    p.append(rect(665, y_pwr - 20, 125, 185, fill="#ffffff", stroke=POS, sw=1.8, rx=6))
    p.append(text(665 + 62, y_pwr + 15, "DC-DC IC", size=12, bold=True, color=POS))
    p.append(text(665 + 62, y_pwr + 35, "V_IN_IC", size=10, color=MUTED))
    p.append(line(665 + 15, y_pwr + 50, 665 + 110, y_pwr + 50, color="#f0d0d0", sw=1))

    p.append(text(665 + 62, y_pwr + 75, "MOSFET SW", size=10, bold=True, color=POS))
    p.append(text(665 + 62, y_pwr + 95, "dV/dt, dI/dt", size=10, color=POS, italic=True))
    p.append(text(665 + 62, y_pwr + 130, "GND_IC", size=10, color=MUTED))

    # Нижня інформаційна плашка
    p.append(rect(30, 375, 780, 32, fill="#f4f6f8", stroke="#d0d4dc", sw=1, rx=6))
    p.append(text(W / 2, 395, "Фільтр пригнічує як диференційний струм пульсацій (DM), так і синфазний струм зміщення (CM)", size=11, color=INK, bold=True))

    render(os.path.join(IMG, "input-pi-filter.svg"), W, H, *p)


if __name__ == "__main__":
    fig_switch_node_ringing()
    fig_input_pi_filter()
    print("SVG figures successfully generated in img/")

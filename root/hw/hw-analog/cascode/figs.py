# -*- coding: utf-8 -*-
"""Фігури до теми «Каскод».
Запуск: python figs.py  → генерує SVG-файли у ./img/
Чотири фігури:
  fig-cascode-concept.svg     — Архітектура CE-CB: транзистор V-to-I та буфер струму
  fig-miller-suppression.svg  — Порівняння гойдання напруги та придушення ефекту Міллера
  fig-cascode-variants.svg    — Схемні реалізації: BJT, CMOS та складений BiCMOS/JFET-BJT
  fig-folded-cascode.svg      — Телескопічний vs Складений каскод (Folded Cascode)
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

WIRE = "#333333"


def ground(x, y, sz=12):
    """Символ заземлення (GND)."""
    p = [
        line(x, y, x, y + 8, WIRE, 1.5),
        line(x - sz, y + 8, x + sz, y + 8, WIRE, 2),
        line(x - sz * 0.6, y + 12, x + sz * 0.6, y + 12, WIRE, 1.5),
        line(x - sz * 0.25, y + 16, x + sz * 0.25, y + 16, WIRE, 1.2),
    ]
    return "".join(p)


def vdd_bar(x, y, label="V_CC", w=20):
    """Шина живлення зверху."""
    p = [
        line(x, y, x, y + 8, WIRE, 1.5),
        line(x - w / 2, y, x + w / 2, y, WIRE, 2),
        text(x, y - 6, label, size=11, bold=True, color=POS),
    ]
    return "".join(p)


def bjt_npn(x, y, label="Q", flip_x=False):
    """NPN BJT транзистор. Центр бази (x, y)."""
    p = []
    bx, by = x, y
    dir_x = -1 if flip_x else 1
    # База
    p.append(line(bx, by, bx + 16 * dir_x, by, WIRE, 1.8))
    p.append(line(bx + 16 * dir_x, by - 16, bx + 16 * dir_x, by + 16, WIRE, 3))
    # Колектор
    cx, cy = bx + 32 * dir_x, by - 24
    p.append(line(bx + 16 * dir_x, by - 8, cx, cy, WIRE, 1.8))
    # Емітер зі стрілкою
    ex, ey = bx + 32 * dir_x, by + 24
    p.append(line(bx + 16 * dir_x, by + 8, ex, ey, WIRE, 1.8))
    # Стрілка на емітері
    arr_x = bx + 24 * dir_x
    arr_y = by + 16
    p.append(polygon([(arr_x, arr_y - 2), (arr_x + 6 * dir_x, arr_y + 6), (arr_x - 1 * dir_x, arr_y + 6)], fill=WIRE, stroke=WIRE))
    # Позначення
    lx = bx - 14 * dir_x
    p.append(text(lx, by - 10, label, size=13, bold=True, color=INK))
    return "".join(p), (bx, by), (cx, cy), (ex, ey)


def mosfet_nmos(x, y, label="M"):
    """NMOS транзистор. Центр затвора (x, y)."""
    p = []
    gx, gy = x, y
    # Затвор
    p.append(line(gx, gy, gx + 14, gy, WIRE, 1.8))
    p.append(line(gx + 14, gy - 16, gx + 14, gy + 16, WIRE, 2))
    # Канал
    p.append(line(gx + 19, gy - 16, gx + 19, gy + 16, WIRE, 2.5))
    # Стік і витік
    dx, dy = gx + 30, gy - 20
    sx, sy = gx + 30, gy + 20
    p.append(line(gx + 19, gy - 12, dx, gy - 12, WIRE, 1.8))
    p.append(line(dx, gy - 12, dx, dy, WIRE, 1.8))
    p.append(line(gx + 19, gy + 12, sx, gy + 12, WIRE, 1.8))
    p.append(line(sx, gy + 12, sx, sy, WIRE, 1.8))
    # Стрілка на підкладці/витоку
    p.append(line(gx + 19, gy, sx, gy, WIRE, 1.5))
    p.append(line(sx, gy, sx, sy, WIRE, 1.5))
    p.append(polygon([(gx + 20, gy), (gx + 26, gy - 3), (gx + 26, gy + 3)], fill=WIRE, stroke=WIRE))
    # Позначення
    p.append(text(gx - 12, gy - 8, label, size=13, bold=True, color=INK))
    return "".join(p), (gx, gy), (dx, dy), (sx, sy)


def polygon(pts, fill=FILL, stroke=LINE, sw=1.5):
    pt_str = " ".join("%.1f,%.1f" % (px, py) for px, py in pts)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pt_str, fill, stroke, sw)


def resistor(x, y, length=36, width=12, vertical=True, label="R", color=WIRE):
    """Прямокутний резистор."""
    p = []
    if vertical:
        rx = x - width / 2
        ry = y - length / 2
        p.append(rect(rx, ry, width, length, fill=FILL, stroke=color, sw=1.5, rx=2))
        p.append(text(x + width + 4, y + 4, label, size=11, bold=True, color=INK, anchor="start"))
    else:
        rx = x - length / 2
        ry = y - width / 2
        p.append(rect(rx, ry, length, width, fill=FILL, stroke=color, sw=1.5, rx=2))
        p.append(text(x, ry - 5, label, size=11, bold=True, color=INK, anchor="middle"))
    return "".join(p)


def capacitor(x, y, gap=6, plate=16, vertical=True, label="C", color=WIRE):
    """Дві пластини конденсатора."""
    p = []
    if vertical:
        p.append(line(x - plate / 2, y - gap / 2, x + plate / 2, y - gap / 2, color, 2))
        p.append(line(x - plate / 2, y + gap / 2, x + plate / 2, y + gap / 2, color, 2))
        p.append(text(x + plate / 2 + 5, y + 4, label, size=11, bold=True, color=MUTED, anchor="start"))
    else:
        p.append(line(x - gap / 2, y - plate / 2, x - gap / 2, y + plate / 2, color, 2))
        p.append(line(x + gap / 2, y - plate / 2, x + gap / 2, y + plate / 2, color, 2))
        p.append(text(x, y - plate / 2 - 4, label, size=11, bold=True, color=MUTED, anchor="middle"))
    return "".join(p)


# ── ФІГУРА 1: Архітектура та розподіл функцій у каскоді ────────────────────────
def make_fig_concept():
    w, h = 820, 440
    f = []

    # Заголовок
    f.append(fitbox(15, 12, 790, 44, "Архітектура каскоду: поділ функцій перетворення напруги та буферизації струму", size=15, bold=True))

    # Ліва панель: Класичний каскад зі спільним емітером (CE)
    f.append(rect(25, 68, 365, 350, fill="#fcfdfe", stroke="#d0d7de", rx=8))
    f.append(text(207, 92, "Класичний каскад (Спільний Емітер)", size=13, bold=True, color=POS))

    # Схема CE
    q_ce, b_ce, c_ce, e_ce = bjt_npn(130, 240, label="Q1")
    f.append(q_ce)
    # Вхід
    f.append(line(55, 240, b_ce[0], b_ce[1], WIRE, 1.5))
    f.append(circle(55, 240, 3.5, fill=WIRE, stroke=WIRE))
    f.append(text(50, 235, "v_in", size=12, bold=True, color=NEG, anchor="end"))

    # Емітер на землю
    f.append(line(e_ce[0], e_ce[1], e_ce[0], 340, WIRE, 1.5))
    f.append(ground(e_ce[0], 340))

    # Колектор через R_C на V_CC
    f.append(line(c_ce[0], c_ce[1], c_ce[0], 190, WIRE, 1.5))
    f.append(resistor(c_ce[0], 160, length=36, width=12, vertical=True, label="R_L"))
    f.append(line(c_ce[0], 142, c_ce[0], 120, WIRE, 1.5))
    f.append(vdd_bar(c_ce[0], 120, "V_CC"))

    # Вихід
    f.append(circle(c_ce[0], 190, 3.5, fill=WIRE, stroke=WIRE))
    f.append(line(c_ce[0], 190, 245, 190, WIRE, 1.5))
    f.append(circle(245, 190, 3.5, fill=WIRE, stroke=WIRE))
    f.append(text(252, 194, "v_out", size=12, bold=True, color=POS, anchor="start"))

    # Паразитна ємність C_cb
    f.append(line(b_ce[0] - 10, 240, b_ce[0] - 10, 200, MUTED, 1.2, dash="3,3"))
    f.append(line(b_ce[0] - 10, 200, 110, 200, MUTED, 1.2, dash="3,3"))
    f.append(capacitor(120, 200, gap=5, plate=12, vertical=False, label="C_cb", color=POS))
    f.append(line(130, 200, c_ce[0], 200, MUTED, 1.2, dash="3,3"))
    f.append(line(c_ce[0], 200, c_ce[0], 190, MUTED, 1.2, dash="3,3"))

    # Пояснення до CE
    f.append(fitbox(35, 275, 345, 130, 
                    "Проблема ефекту Міллера:\n"
                    "• Великий розмах вихідної напруги: v_out = −A_v · v_in\n"
                    "• Різниця потенціалів на C_cb: ΔV = v_in · (1 + A_v)\n"
                    "• Роздута вхідна ємність C_вх ≈ C_π + (1 + A_v)·C_cb\n"
                    "• Вхідний полюс різко обмежує робочу смугу частот",
                    size=11, fill="#fff5f5", stroke="#f5c2c7", pad=6))

    # Права панель: Каскодний підсилювач (CE + CB)
    f.append(rect(410, 68, 385, 350, fill="#f8fbf9", stroke="#c3e6cb", rx=8))
    f.append(text(602, 92, "Каскод (Спільний Емітер + Спільна База)", size=13, bold=True, color=FIELD))

    # Нижній транзистор Q1 (CE - V-to-I converter)
    q1, b1, c1, e1 = bjt_npn(490, 290, label="Q1")
    f.append(q1)
    # Вхід Q1
    f.append(line(435, 290, b1[0], b1[1], WIRE, 1.5))
    f.append(circle(435, 290, 3.5, fill=WIRE, stroke=WIRE))
    f.append(text(430, 285, "v_in", size=12, bold=True, color=NEG, anchor="end"))
    # Емітер Q1 на землю
    f.append(line(e1[0], e1[1], e1[0], 340, WIRE, 1.5))
    f.append(ground(e1[0], 340))

    # Верхній транзистор Q2 (CB - Current buffer)
    q2, b2, c2, e2 = bjt_npn(490, 185, label="Q2")
    f.append(q2)
    # База Q2 на V_BIAS з блокувальним конденсатором C_B (AC GND)
    f.append(line(445, 185, b2[0], b2[1], WIRE, 1.5))
    f.append(circle(445, 185, 3.5, fill=WIRE, stroke=WIRE))
    f.append(text(440, 180, "V_BIAS", size=10, bold=True, color=MUTED, anchor="end"))
    f.append(line(460, 185, 460, 205, WIRE, 1.2))
    f.append(capacitor(460, 212, gap=4, plate=10, vertical=True, label="C_B", color=MUTED))
    f.append(ground(460, 222, sz=8))

    # З'єднання між Q1 колектором та Q2 емітером (Вузол X)
    f.append(line(c1[0], c1[1], e2[0], e2[1], WIRE, 1.8))
    # Точка вузла X
    mid_node_y = (c1[1] + e2[1]) / 2
    f.append(circle(c1[0], mid_node_y, 4, fill=POS, stroke=POS))
    f.append(text(c1[0] + 12, mid_node_y + 4, "Вузол X", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(c1[0] + 12, mid_node_y + 16, "R_in2 ≈ 1/g_m2 (низький)", size=10, color=MUTED, anchor="start"))

    # Вихід Q2 через R_L на V_CC
    f.append(line(c2[0], c2[1], c2[0], 145, WIRE, 1.5))
    f.append(resistor(c2[0], 130, length=28, width=11, vertical=True, label="R_L"))
    f.append(line(c2[0], 116, c2[0], 106, WIRE, 1.5))
    f.append(vdd_bar(c2[0], 106, "V_CC"))

    # Вихід каскоду
    f.append(circle(c2[0], 145, 3.5, fill=WIRE, stroke=WIRE))
    f.append(line(c2[0], 145, 635, 145, WIRE, 1.5))
    f.append(circle(635, 145, 3.5, fill=WIRE, stroke=WIRE))
    f.append(text(642, 149, "v_out", size=12, bold=True, color=FIELD, anchor="start"))

    # Пояснення до каскоду
    f.append(fitbox(420, 325, 365, 82,
                    "Переваги каскодної конфігурації:\n"
                    "• Q1 бачить малий опір 1/g_m2 → підсилення v_X/v_in ≈ −1 (Міллер усунуто!)\n"
                    "• Q2 передає струм i_c1 у навантаження R_L з високим R_вих ≈ g_m2·r_o2·r_o1\n"
                    "• Повний коефіцієнт підсилення A_v збережено, а смугу розширено в десятки разів",
                    size=10.5, fill="#f0fff4", stroke="#b2f2bb", pad=5))

    render(os.path.join(IMG, "fig-cascode-concept.svg"), w, h, *f)


# ── ФІГУРА 2: Динаміка потенціалів і придушення ефекту Міллера ─────────────────
def make_fig_miller():
    w, h = 800, 380
    f = []

    f.append(fitbox(15, 12, 770, 44, "Механізм усунення ефекту Міллера: порівняння амплітуд у проміжних вузлах", size=15, bold=True))

    # Стовпчик 1: Одиночний каскад СЕ
    f.append(rect(25, 68, 360, 295, fill=FILL, stroke=LINE, rx=8))
    f.append(text(205, 94, "Одиночний каскад (Спільний Емітер)", size=13, bold=True, color=POS))

    # Рівні напруг CE
    f.append(rect(45, 115, 320, 45, fill="#ffffff", stroke="#ced4da", rx=4))
    f.append(text(60, 134, "Вхідний сигнал v_in:", size=11, color=INK, anchor="start"))
    f.append(text(340, 134, "+10 мВ (Δv_вх)", size=11, bold=True, color=NEG, anchor="end"))
    f.append(text(60, 150, "Колекторний вузол v_вих:", size=11, color=INK, anchor="start"))
    f.append(text(340, 150, "−1.50 В (|A_v| = 150)", size=11, bold=True, color=POS, anchor="end"))

    # Схема ємності
    f.append(line(70, 195, 150, 195, WIRE, 1.5))
    f.append(circle(70, 195, 3, fill=NEG, stroke=NEG))
    f.append(text(70, 185, "База (+10 мВ)", size=10, bold=True, color=NEG))
    f.append(capacitor(165, 195, gap=6, plate=18, vertical=False, label="C_cb (5 пФ)", color=POS))
    f.append(line(180, 195, 270, 195, WIRE, 1.5))
    f.append(circle(270, 195, 3, fill=POS, stroke=POS))
    f.append(text(270, 185, "Колектор (−1500 мВ)", size=10, bold=True, color=POS))

    # Результат Міллера
    f.append(fitbox(40, 220, 330, 130,
                    "Розрахунок міллерівського струму:\n"
                    "• Падіння напруги: ΔV = 10 мВ − (−1500 мВ) = 1510 мВ\n"
                    "• Заряд, що вливається: Q = C_cb · 151 · Δv_вх\n"
                    "• Еквівалентна вхідна ємність: C_in,M = 5 пФ · 151 = 755 пФ\n"
                    "• Смуга пропускання каскаду падає в 151 раз!",
                    size=10.5, fill="#fff5f5", stroke="#f5c2c7", pad=6))

    # Стовпчик 2: Каскодний каскад CE-CB
    f.append(rect(415, 68, 360, 295, fill=FILL, stroke=LINE, rx=8))
    f.append(text(595, 94, "Каскодний каскад (CE + CB)", size=13, bold=True, color=FIELD))

    # Рівні напруг Cascode
    f.append(rect(435, 115, 320, 45, fill="#ffffff", stroke="#ced4da", rx=4))
    f.append(text(450, 134, "Вхідний сигнал v_in:", size=11, color=INK, anchor="start"))
    f.append(text(730, 134, "+10 мВ (Δv_вх)", size=11, bold=True, color=NEG, anchor="end"))
    f.append(text(450, 150, "Проміжний вузол X v_X:", size=11, color=INK, anchor="start"))
    f.append(text(730, 150, "−10 мВ (|A_v1| ≈ 1)", size=11, bold=True, color=FIELD, anchor="end"))

    # Схема ємності у каскоді
    f.append(line(460, 195, 540, 195, WIRE, 1.5))
    f.append(circle(460, 195, 3, fill=NEG, stroke=NEG))
    f.append(text(460, 185, "База Q1 (+10 мВ)", size=10, bold=True, color=NEG))
    f.append(capacitor(555, 195, gap=6, plate=18, vertical=False, label="C_cb1 (5 пФ)", color=FIELD))
    f.append(line(570, 195, 660, 195, WIRE, 1.5))
    f.append(circle(660, 195, 3, fill=POS, stroke=POS))
    f.append(text(660, 185, "Вузол X (−10 мВ)", size=10, bold=True, color=POS))

    # Результат у каскоді
    f.append(fitbox(430, 220, 330, 130,
                    "Розрахунок струму в каскоді:\n"
                    "• Падіння напруги: ΔV = 10 мВ − (−10 мВ) = 20 мВ\n"
                    "• Заряд, що вливається: Q = C_cb1 · 2 · Δv_вх\n"
                    "• Еквівалентна вхідна ємність: C_in,M = 5 пФ · 2 = 10 пФ\n"
                    "• Повний розмах −1.5 В формується на виході Q2 без зворотного зв'язку на вхід!",
                    size=10.5, fill="#f0fff4", stroke="#b2f2bb", pad=6))

    render(os.path.join(IMG, "fig-miller-suppression.svg"), w, h, *f)


# ── ФІГУРА 3: Схемотехнічні різновиди каскодів (BJT, CMOS, BiCMOS) ─────────────
def make_fig_variants():
    w, h = 820, 390
    f = []

    f.append(fitbox(15, 12, 790, 44, "Схемотехнічні різновиди: біполярний, польовий КМОН та гібридний BiCMOS", size=15, bold=True))

    # Варіант 1: BJT Каскод
    f.append(rect(20, 68, 245, 305, fill="#ffffff", stroke="#d0d7de", rx=6))
    f.append(text(142, 90, "Біполярний (BJT)", size=12, bold=True, color=INK))

    q1_a, b1_a, c1_a, e1_a = bjt_npn(75, 275, label="Q1")
    q2_a, b2_a, c2_a, e2_a = bjt_npn(75, 185, label="Q2")
    f.append(q1_a + q2_a)

    # Вхід, земля, з'єднання, вихід
    f.append(line(35, 275, b1_a[0], b1_a[1], WIRE, 1.5))
    f.append(circle(35, 275, 3, fill=WIRE, stroke=WIRE))
    f.append(text(32, 270, "v_in", size=10, bold=True, color=NEG, anchor="end"))

    f.append(line(e1_a[0], e1_a[1], e1_a[0], 315, WIRE, 1.5))
    f.append(ground(e1_a[0], 315, sz=8))

    f.append(line(c1_a[0], c1_a[1], e2_a[0], e2_a[1], WIRE, 1.5))

    f.append(line(45, 185, b2_a[0], b2_a[1], WIRE, 1.5))
    f.append(text(42, 180, "V_B", size=9, bold=True, color=MUTED, anchor="end"))

    f.append(line(c2_a[0], c2_a[1], c2_a[0], 145, WIRE, 1.5))
    f.append(resistor(c2_a[0], 132, length=22, width=9, vertical=True, label="R_C"))
    f.append(line(c2_a[0], 121, c2_a[0], 112, WIRE, 1.5))
    f.append(vdd_bar(c2_a[0], 112, "V_CC", w=16))

    f.append(line(c2_a[0], 145, 195, 145, WIRE, 1.5))
    f.append(circle(195, 145, 3, fill=WIRE, stroke=WIRE))
    f.append(text(200, 148, "v_out", size=10, bold=True, color=POS, anchor="start"))

    f.append(fitbox(30, 320, 225, 45, "Висока крутість g_m = I_C/V_T\nІдеально для ВЧ та радіотрактів", size=9.5, fill=FILL, pad=4))

    # Варіант 2: MOSFET Каскод (Telescopic CMOS)
    f.append(rect(285, 68, 250, 305, fill="#ffffff", stroke="#d0d7de", rx=6))
    f.append(text(410, 90, "КМОН (MOSFET)", size=12, bold=True, color=INK))

    m1, g1, d1, s1 = mosfet_nmos(345, 275, label="M1")
    m2, g2, d2, s2 = mosfet_nmos(345, 185, label="M2")
    f.append(m1 + m2)

    # Вхід, земля, з'єднання, вихід
    f.append(line(305, 275, g1[0], g1[1], WIRE, 1.5))
    f.append(circle(305, 275, 3, fill=WIRE, stroke=WIRE))
    f.append(text(302, 270, "v_in", size=10, bold=True, color=NEG, anchor="end"))

    f.append(line(s1[0], s1[1], s1[0], 315, WIRE, 1.5))
    f.append(ground(s1[0], 315, sz=8))

    f.append(line(d1[0], d1[1], s2[0], s2[1], WIRE, 1.5))

    f.append(line(315, 185, g2[0], g2[1], WIRE, 1.5))
    f.append(text(312, 180, "V_G2", size=9, bold=True, color=MUTED, anchor="end"))

    f.append(line(d2[0], d2[1], d2[0], 145, WIRE, 1.5))
    f.append(resistor(d2[0], 132, length=22, width=9, vertical=True, label="R_D"))
    f.append(line(d2[0], 121, d2[0], 112, WIRE, 1.5))
    f.append(vdd_bar(d2[0], 112, "V_DD", w=16))

    f.append(line(d2[0], 145, 465, 145, WIRE, 1.5))
    f.append(circle(465, 145, 3, fill=WIRE, stroke=WIRE))
    f.append(text(470, 148, "v_out", size=10, bold=True, color=POS, anchor="start"))

    f.append(fitbox(295, 320, 230, 45, "Нульовий струм затвора, I_G=0\nБазовий блок аналогових ІС", size=9.5, fill=FILL, pad=4))

    # Варіант 3: BiCMOS / JFET-BJT Гібрид
    f.append(rect(555, 68, 245, 305, fill="#ffffff", stroke="#d0d7de", rx=6))
    f.append(text(677, 90, "Гібрид BiCMOS / JFET-BJT", size=12, bold=True, color=INK))

    m_in, g_in, d_in, s_in = mosfet_nmos(610, 275, label="M1")
    q_cas, b_cas, c_cas, e_cas = bjt_npn(610, 185, label="Q2")
    f.append(m_in + q_cas)

    # Вхід, земля, з'єднання, вихід
    f.append(line(575, 275, g_in[0], g_in[1], WIRE, 1.5))
    f.append(circle(575, 275, 3, fill=WIRE, stroke=WIRE))
    f.append(text(572, 270, "v_in", size=10, bold=True, color=NEG, anchor="end"))

    f.append(line(s_in[0], s_in[1], s_in[0], 315, WIRE, 1.5))
    f.append(ground(s_in[0], 315, sz=8))

    f.append(line(d_in[0], d_in[1], e_cas[0], e_cas[1], WIRE, 1.5))

    f.append(line(580, 185, b_cas[0], b_cas[1], WIRE, 1.5))
    f.append(text(577, 180, "V_B", size=9, bold=True, color=MUTED, anchor="end"))

    f.append(line(c_cas[0], c_cas[1], c_cas[0], 145, WIRE, 1.5))
    f.append(resistor(c_cas[0], 132, length=22, width=9, vertical=True, label="R_L"))
    f.append(line(c_cas[0], 121, c_cas[0], 112, WIRE, 1.5))
    f.append(vdd_bar(c_cas[0], 112, "V_CC", w=16))

    f.append(line(c_cas[0], 145, 735, 145, WIRE, 1.5))
    f.append(circle(735, 145, 3, fill=WIRE, stroke=WIRE))
    f.append(text(740, 148, "v_out", size=10, bold=True, color=POS, anchor="start"))

    f.append(fitbox(565, 320, 225, 45, "Вхідний опір R_вх → ∞ (MOS)\nНизький 1/g_m2 та смуга (BJT)", size=9.5, fill=FILL, pad=4))

    render(os.path.join(IMG, "fig-cascode-variants.svg"), w, h, *f)


# ── ФІГУРА 4: Телескопічний та складений каскод (Folded Cascode) ────────────────
def make_fig_folded():
    w, h = 820, 420
    f = []

    f.append(fitbox(15, 12, 790, 44, "Телескопічний каскод проти складеного (Folded Cascode): проблема запасу за напругою", size=15, bold=True))

    # Ліва панель: Телескопічний стек
    f.append(rect(25, 68, 365, 335, fill="#ffffff", stroke="#d0d7de", rx=8))
    f.append(text(207, 92, "Телескопічний каскод (Прямий стек)", size=13, bold=True, color=POS))

    # 4 транзистори у вертикальному стеку
    # M4 (PMOS load cascode)
    # M3 (PMOS load)
    # M2 (NMOS cascode)
    # M1 (NMOS input)
    f.append(rect(65, 115, 100, 32, fill="#f8f9fa", stroke="#6c757d", rx=4))
    f.append(text(115, 135, "M4 (P-Дзеркало)", size=10, bold=True))
    f.append(line(115, 100, 115, 115, WIRE, 1.5))
    f.append(vdd_bar(115, 100, "V_DD"))

    f.append(line(115, 147, 115, 160, WIRE, 1.5))
    f.append(rect(65, 160, 100, 32, fill="#f8f9fa", stroke="#6c757d", rx=4))
    f.append(text(115, 180, "M3 (P-Каскод)", size=10, bold=True))

    f.append(line(115, 192, 115, 215, WIRE, 1.5))
    f.append(circle(115, 203, 3.5, fill=POS, stroke=POS))
    f.append(line(115, 203, 190, 203, WIRE, 1.5))
    f.append(circle(190, 203, 3.5, fill=POS, stroke=POS))
    f.append(text(195, 207, "v_out", size=11, bold=True, color=POS, anchor="start"))

    f.append(rect(65, 215, 100, 32, fill="#f8f9fa", stroke="#6c757d", rx=4))
    f.append(text(115, 235, "M2 (N-Каскод)", size=10, bold=True))

    f.append(line(115, 247, 115, 260, WIRE, 1.5))
    f.append(rect(65, 260, 100, 32, fill="#f8f9fa", stroke="#6c757d", rx=4))
    f.append(text(115, 280, "M1 (N-Вхід)", size=10, bold=True))

    f.append(line(115, 292, 115, 307, WIRE, 1.5))
    f.append(ground(115, 307))

    # Стрілка напруги
    f.append(arrow(45, 110, 45, 295, color=POS, sw=2))
    f.append(text(40, 205, "4 · V_ov", size=11, bold=True, color=POS, anchor="end"))

    # Пояснення до телескопічного
    f.append(fitbox(35, 325, 345, 68,
                    "Обмеження за розмахом напруги (Headroom):\n"
                    "• 4 транзистори послідовно: V_min = 2·V_ov,n + 2·V_ov,p\n"
                    "• При V_DD = 1.2 В вихідний розмах становить менше 0.4 В\n"
                    "• Вхідний синфазний діапазон дуже обмежений",
                    size=10, fill="#fff5f5", stroke="#f5c2c7", pad=5))

    # Права панель: Складений каскод
    f.append(rect(410, 68, 385, 335, fill="#ffffff", stroke="#d0d7de", rx=8))
    f.append(text(602, 92, "Складений каскод (Folded Cascode)", size=13, bold=True, color=FIELD))

    # Ліва гілка складеного каскоду: Джерело струму I_B1 + вхідний NMOS M1
    f.append(line(490, 100, 490, 120, WIRE, 1.5))
    f.append(vdd_bar(490, 100, "V_DD"))
    f.append(rect(445, 120, 90, 30, fill="#e8f4fd", stroke="#90cdf4", rx=4))
    f.append(text(490, 139, "Джерело I_B1", size=10, bold=True, color=INK))

    f.append(line(490, 150, 490, 220, WIRE, 1.5))
    f.append(circle(490, 185, 4, fill=FIELD, stroke=FIELD))
    f.append(text(475, 185, "Вузол F", size=10, bold=True, color=FIELD, anchor="end"))

    f.append(rect(445, 220, 90, 30, fill="#f8f9fa", stroke="#6c757d", rx=4))
    f.append(text(490, 239, "M1 (N-Вхід)", size=10, bold=True))
    f.append(line(445, 235, 425, 235, WIRE, 1.5))
    f.append(circle(425, 235, 3, fill=WIRE, stroke=WIRE))
    f.append(text(420, 235, "v_in", size=10, bold=True, color=NEG, anchor="end"))

    f.append(line(490, 250, 490, 270, WIRE, 1.5))
    f.append(ground(490, 270))

    # Горизонтальний зв'язок (згортання струму у витік P-каскоду M2)
    f.append(arrow(490, 185, 620, 185, color=FIELD, sw=2))
    f.append(text(555, 175, "Струм i_sig", size=10, bold=True, color=FIELD))

    # Права гілка: P-каскод M2 + активне навантаження
    f.append(rect(620, 170, 90, 30, fill="#f0fff4", stroke="#b2f2bb", rx=4))
    f.append(text(665, 189, "M2 (P-Каскод)", size=10, bold=True, color=FIELD))

    f.append(line(665, 200, 665, 235, WIRE, 1.5))
    f.append(circle(665, 218, 3.5, fill=POS, stroke=POS))
    f.append(line(665, 218, 735, 218, WIRE, 1.5))
    f.append(circle(735, 218, 3.5, fill=POS, stroke=POS))
    f.append(text(740, 222, "v_out", size=11, bold=True, color=POS, anchor="start"))

    f.append(rect(620, 235, 90, 30, fill="#f8f9fa", stroke="#6c757d", rx=4))
    f.append(text(665, 254, "Активне навант.", size=10, bold=True))
    f.append(line(665, 265, 665, 280, WIRE, 1.5))
    f.append(ground(665, 280))

    # Пояснення до складеного каскоду
    f.append(fitbox(420, 315, 365, 78,
                    "Переваги архітектури Folded Cascode:\n"
                    "• Струм вхідного N-транзистора «складається» у витік P-каскоду\n"
                    "• Вхідні й вихідні транзистори не стоять в одному стеку живлення\n"
                    "• Вхідний синфазний діапазон може сягати шини землі (GND)\n"
                    "• Значно більший вихідний розмах при низьковольтному живленні",
                    size=10, fill="#f0fff4", stroke="#b2f2bb", pad=5))

    render(os.path.join(IMG, "fig-folded-cascode.svg"), w, h, *f)


if __name__ == "__main__":
    make_fig_concept()
    make_fig_miller()
    make_fig_variants()
    make_fig_folded()
    print("All figures generated successfully.")

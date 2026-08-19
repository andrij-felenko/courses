# -*- coding: utf-8 -*-
"""Генератор векторних фігур для теми sram-cell (SRAM-комірка).
Використовує спільну бібліотеку svgkit з scripts/.
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_cell_6t():
    """Фігура 1: Принципова схема класичної 6T SRAM-комірки."""
    w, h = 820, 520
    frags = []

    # Заголовок / фонові зони
    frags.append(rect(20, 20, 780, 480, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Зони виділення інверторів і ключів
    frags.append(rect(170, 70, 480, 360, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(410, 95, "Два зустрічно включені CMOS-інвертори (бістабільний тригер)", size=13, color=MUTED, bold=True))

    # Шини живлення і землі
    frags.append(line(220, 120, 600, 120, color=POS, sw=2.5))
    frags.append(text(410, 114, "Живлення V_DD", size=12, color=POS, bold=True))

    frags.append(line(220, 410, 600, 410, color="#1e293b", sw=2.5))
    frags.append(text(410, 426, "Земля GND (0 В)", size=12, color="#1e293b", bold=True))

    # Вертикальні шини BL та BLB
    frags.append(line(80, 40, 80, 480, color=NEG, sw=2.5))
    frags.append(text(80, 35, "Бітова лінія BL", size=13, color=NEG, bold=True))

    frags.append(line(740, 40, 740, 480, color=NEG, sw=2.5))
    frags.append(text(740, 35, "Інверсна лінія BLB", size=13, color=NEG, bold=True))

    # Горизонтальна словесна лінія WL
    frags.append(line(40, 260, 780, 260, color=FIELD, sw=2.5))
    frags.append(text(410, 252, "Словесна лінія WL (Word Line)", size=13, color=FIELD, bold=True))

    # --- Лівий інвертор (P1 / N1) ---
    # Транзистор P1 (Pull-up PMOS)
    b_p1, _, _ = textbox(280, 170, "P1 (PMOS)\nPull-Up", size=12, pad=6, fill="#fdecea", stroke=POS, bold=True)
    frags.append(b_p1)
    frags.append(line(280, 120, 280, 145, color=POS, sw=2))  # Витік до Vdd
    frags.append(line(280, 195, 280, 290, color=LINE, sw=2))  # Стік до вузла Q

    # Транзистор N1 (Pull-down NMOS)
    b_n1, _, _ = textbox(280, 350, "N1 (NMOS)\nPull-Down", size=12, pad=6, fill="#eaf0fd", stroke=NEG, bold=True)
    frags.append(b_n1)
    frags.append(line(280, 290, 280, 325, color=LINE, sw=2))  # Стік до вузла Q
    frags.append(line(280, 375, 280, 410, color=LINE, sw=2))  # Витік до GND

    # --- Правий інвертор (P2 / N2) ---
    # Транзистор P2 (Pull-up PMOS)
    b_p2, _, _ = textbox(540, 170, "P2 (PMOS)\nPull-Up", size=12, pad=6, fill="#fdecea", stroke=POS, bold=True)
    frags.append(b_p2)
    frags.append(line(540, 120, 540, 145, color=POS, sw=2))
    frags.append(line(540, 195, 540, 290, color=LINE, sw=2))

    # Транзистор N2 (Pull-down NMOS)
    b_n2, _, _ = textbox(540, 350, "N2 (NMOS)\nPull-Down", size=12, pad=6, fill="#eaf0fd", stroke=NEG, bold=True)
    frags.append(b_n2)
    frags.append(line(540, 290, 540, 325, color=LINE, sw=2))
    frags.append(line(540, 375, 540, 410, color=LINE, sw=2))

    # --- Вузли зберігання Q та QB ---
    frags.append(circle(280, 290, 5, fill="#1a1a1a", stroke="#1a1a1a"))
    frags.append(text(260, 295, "Q", size=16, color="#0f172a", bold=True))

    frags.append(circle(540, 290, 5, fill="#1a1a1a", stroke="#1a1a1a"))
    frags.append(text(560, 295, "QB", size=16, color="#0f172a", bold=True))

    # Перехресні зв'язки інверторів (Cross-coupled feedback)
    # Зв'язок Q -> Затвори P2/N2
    frags.append(line(280, 290, 360, 290, color="#64748b", sw=1.5))
    frags.append(line(360, 290, 360, 210, color="#64748b", sw=1.5))
    frags.append(line(360, 210, 480, 210, color="#64748b", sw=1.5))
    frags.append(line(480, 210, 480, 170, color="#64748b", sw=1.5))
    frags.append(line(480, 170, 495, 170, color="#64748b", sw=1.5))
    frags.append(line(480, 210, 480, 350, color="#64748b", sw=1.5))
    frags.append(line(480, 350, 495, 350, color="#64748b", sw=1.5))

    # Зв'язок QB -> Затвори P1/N1
    frags.append(line(540, 290, 460, 290, color="#64748b", sw=1.5))
    frags.append(line(460, 290, 460, 370, color="#64748b", sw=1.5))
    frags.append(line(460, 370, 340, 370, color="#64748b", sw=1.5))
    frags.append(line(340, 370, 340, 350, color="#64748b", sw=1.5))
    frags.append(line(340, 350, 325, 350, color="#64748b", sw=1.5))
    frags.append(line(340, 370, 340, 170, color="#64748b", sw=1.5))
    frags.append(line(340, 170, 325, 170, color="#64748b", sw=1.5))

    # --- Транзистори доступу (AX1, AX2) ---
    b_ax1, _, _ = textbox(140, 290, "AX1 (NMOS)\nAccess", size=12, pad=6, fill="#ecfdf5", stroke=FIELD, bold=True)
    frags.append(b_ax1)
    frags.append(line(80, 290, 95, 290, color=LINE, sw=2))   # До BL
    frags.append(line(185, 290, 280, 290, color=LINE, sw=2)) # До вузла Q
    frags.append(line(140, 260, 140, 268, color=FIELD, sw=2)) # Затвор до WL

    b_ax2, _, _ = textbox(680, 290, "AX2 (NMOS)\nAccess", size=12, pad=6, fill="#ecfdf5", stroke=FIELD, bold=True)
    frags.append(b_ax2)
    frags.append(line(635, 290, 540, 290, color=LINE, sw=2)) # До вузла QB
    frags.append(line(725, 290, 740, 290, color=LINE, sw=2)) # До BLB
    frags.append(line(680, 260, 680, 268, color=FIELD, sw=2)) # Затвор до WL

    # Легенда функцій транзисторів
    frags.append(rect(100, 455, 620, 32, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(410, 476, "P1/P2: Pull-up (PMOS)  |  N1/N2: Pull-down (NMOS)  |  AX1/AX2: Access (NMOS)", size=12, color=INK, bold=True))

    render(os.path.join(IMG_DIR, "cell-6t-schematic.svg"), w, h, *frags)


def fig_read_operation():
    """Фігура 2: Механізм читання комірки, сплеск напруги V_read та робота Sense Amplifier."""
    w, h = 840, 500
    frags = []

    # Контейнер
    frags.append(rect(20, 20, 800, 460, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Крок 1: Передзарядка
    box1, _, _ = textbox(130, 70, "1. Передзарядка\nBL = V_DD, BLB = V_DD", size=12, pad=8, fill="#eff6ff", stroke=NEG, bold=True)
    frags.append(box1)

    # Крок 2: Активація WL
    box2, _, _ = textbox(380, 70, "2. Активація слова\nWL = V_DD (AX1/AX2 ввімкнені)", size=12, pad=8, fill="#ecfdf5", stroke=FIELD, bold=True)
    frags.append(box2)

    # Крок 3: Струм розряду та дельта V
    box3, _, _ = textbox(660, 70, "3. Розряд лінії\nBL повільно спадає на ΔV", size=12, pad=8, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(box3)

    # Стрілки процесу
    frags.append(arrow(210, 70, 270, 70, color=LINE, sw=1.5))
    frags.append(arrow(490, 70, 550, 70, color=LINE, sw=1.5))

    # Схема активного розряду (зберігається Q=0, QB=1)
    frags.append(rect(60, 130, 430, 230, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(275, 155, "Шлях струму розряду I_read (стан Q=0, QB=1)", size=13, color=INK, bold=True))

    # Подільник напруги між BL(Vdd) -> AX1 -> N1 -> GND
    frags.append(line(100, 200, 100, 330, color=NEG, sw=3))
    frags.append(text(100, 190, "BL (V_DD)", size=12, color=NEG, bold=True))

    frags.append(arrow(100, 230, 160, 230, color=POS, sw=2)) # Струм I_read
    frags.append(text(130, 220, "I_read", size=11, color=POS, bold=True))

    b_ax, _, _ = textbox(210, 230, "AX1 (NMOS)\n(опір R_AX)", size=12, pad=6, fill="#ecfdf5", stroke=FIELD, bold=True)
    frags.append(b_ax)

    frags.append(line(260, 230, 310, 230, color=LINE, sw=2))
    frags.append(circle(310, 230, 5, fill=POS, stroke=POS))
    frags.append(text(310, 215, "Вузол Q (V_read)", size=12, color=POS, bold=True))

    frags.append(arrow(310, 230, 310, 275, color=POS, sw=2))

    b_n1, _, _ = textbox(310, 305, "N1 / PD1 (NMOS)\n(опір R_PD)", size=12, pad=6, fill="#eaf0fd", stroke=NEG, bold=True)
    frags.append(b_n1)

    frags.append(line(310, 335, 310, 350, color=LINE, sw=2))
    frags.append(line(270, 350, 350, 350, color="#1e293b", sw=2.5))
    frags.append(text(310, 362, "GND (0 В)", size=11, color="#1e293b", bold=True))

    # Блок пояснення V_read та Cell Ratio
    frags.append(rect(510, 130, 300, 230, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(660, 155, "Захист від збурення (Read Disturbance)", size=12, color=POS, bold=True))
    t_snm = [
        "Струм I_read піднімає напругу вузла Q:",
        "V_Q = V_read = V_DD · R_PD / (R_PD + R_AX)",
        "",
        "КРИТИЧНА УМОВА СТІЙКОСТІ ЧИТАННЯ:",
        "V_read < V_th,N2  (поріг відкриття N2)",
        "",
        "Вимога до розмірів (Cell Ratio):",
        "CR = β_PD / β_AX = (W_PD/L_PD)/(W_AX/L_AX) ≥ 1.5…2.5",
        "N1 має бути значно сильнішим за AX1!"
    ]
    frags.append(mtext(660, 180, t_snm, size=11, color=INK, bold=False, lh=1.35))

    # Підсилювач зчитування (Sense Amplifier) внизу
    frags.append(rect(180, 385, 480, 80, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(420, 408, "Диференційний підсилювач зчитування (Sense Amplifier)", size=13, color=INK, bold=True))
    frags.append(text(420, 430, "Входи: BL (V_DD − ΔV) та BLB (V_DD). Поріг спрацьовування: ΔV ≈ 50–100 мВ", size=12, color=MUTED))
    frags.append(text(420, 452, "Миттєве підсилення малого перепаду ΔV до повних рівнів логіки (0 В / V_DD)", size=12, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "read-operation.svg"), w, h, *frags)


def fig_write_operation():
    """Фігура 3: Механізм запису нового стану та умова Pull-Up Ratio."""
    w, h = 840, 490
    frags = []

    frags.append(rect(20, 20, 800, 450, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Стан до запису
    box_pre, _, _ = textbox(210, 60, "Початковий стан комірки:\nQ = 1 (V_DD), QB = 0 (0 В)", size=12, pad=8, fill="#f8fafc", stroke="#94a3b8", bold=True)
    frags.append(box_pre)

    box_post, _, _ = textbox(630, 60, "Цільовий запис логічного «0»:\nФорсуємо BL = 0 В, BLB = V_DD", size=12, pad=8, fill="#eff6ff", stroke=NEG, bold=True)
    frags.append(box_post)

    frags.append(arrow(340, 60, 470, 60, color=LINE, sw=1.8))

    # Схема протиборства струмів у вузлі Q (P1 проти AX1)
    frags.append(rect(50, 115, 430, 250, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(265, 140, "Боротьба за вузол Q: тяга P1 проти водія через AX1", size=13, color=INK, bold=True))

    # Шина Vdd угорі
    frags.append(line(200, 170, 330, 170, color=POS, sw=2.5))
    frags.append(text(265, 162, "V_DD", size=12, color=POS, bold=True))

    # Транзистор P1
    b_p1, _, _ = textbox(265, 205, "P1 (PMOS Pull-Up)\nНамагається тримати Q = V_DD", size=11, pad=6, fill="#fdecea", stroke=POS, bold=True)
    frags.append(b_p1)
    frags.append(line(265, 170, 265, 185, color=POS, sw=2))
    frags.append(line(265, 225, 265, 280, color=LINE, sw=2))

    # Вузол Q
    frags.append(circle(265, 280, 5, fill="#0f172a", stroke="#0f172a"))
    frags.append(text(290, 285, "Вузол Q", size=13, color="#0f172a", bold=True))

    # Транзистор доступу AX1 тягне Q до BL = 0
    b_ax1, _, _ = textbox(135, 280, "AX1 (NMOS Access)\nТягне вузол Q до BL", size=11, pad=6, fill="#ecfdf5", stroke=FIELD, bold=True)
    frags.append(b_ax1)
    frags.append(line(205, 280, 265, 280, color=LINE, sw=2))
    frags.append(line(65, 280, 75, 280, color=NEG, sw=2.5))

    # Водій запису на BL
    frags.append(line(65, 240, 65, 330, color=NEG, sw=3))
    frags.append(text(65, 230, "BL = 0 В", size=12, color=NEG, bold=True))
    frags.append(arrow(260, 280, 195, 280, color=NEG, sw=2)) # Струм розряду вузла Q

    frags.append(text(265, 350, "WL = V_DD (активна)", size=12, color=FIELD, bold=True))

    # Блок умови Pull-Up Ratio
    frags.append(rect(500, 115, 300, 250, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(650, 140, "Умова успішного запису (Writeability)", size=12, color=FIELD, bold=True))
    t_wr = [
        "Водій запису має примусово опустити",
        "напругу вузла Q нижче порога перемикання:",
        "V_Q < V_trip  (інвертора P2/N2)",
        "",
        "AX1 має подолати опір PMOS P1:",
        "R_AX < R_PU  →  β_AX > β_PU",
        "",
        "Pull-up Ratio (PR):",
        "PR = β_PU / β_AX = (W_PU/L_PU)/(W_AX/L_AX) ≤ 1.0",
        "",
        "Транзистор доступу AX сильніший за PMOS!"
    ]
    frags.append(mtext(650, 165, t_wr, size=11, color=INK, bold=False, lh=1.35))

    # Підсумок ієрархії розмірів
    frags.append(rect(80, 385, 680, 50, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(420, 408, "ГОЛОВНИЙ КОМПРОМІС РОЗМІРІВ 6T SRAM:", size=12, color=POS, bold=True))
    frags.append(text(420, 426, "β_PD (N1/N2)  >  β_AX (AX1/AX2)  >  β_PU (P1/P2)     (Pull-Down > Access > Pull-Up)", size=13, color="#0f172a", bold=True))

    render(os.path.join(IMG_DIR, "write-operation.svg"), w, h, *frags)


def fig_butterfly_snm():
    """Фігура 4: Метеликова крива (Butterfly Curve) та статичний запас завадостійкості (SNM)."""
    w, h = 820, 500
    frags = []

    frags.append(rect(20, 20, 780, 460, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Координатні осі графіка
    ox, oy = 100, 410
    gw, gh = 360, 340

    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2)) # Вісь V_Q
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2)) # Вісь V_QB

    frags.append(text(ox + gw + 20, oy + 5, "V_Q", size=13, color=INK, bold=True))
    frags.append(text(ox, oy - gh - 15, "V_QB", size=13, color=INK, bold=True))

    # Мітки осей
    frags.append(text(ox, oy + 18, "0", size=12, color=MUTED))
    frags.append(text(ox + gw - 20, oy + 18, "V_DD", size=12, color=MUTED))
    frags.append(text(ox - 25, oy - gh + 20, "V_DD", size=12, color=MUTED))

    # Діагональ симетрії V_Q = V_QB
    frags.append(line(ox, oy, ox + gw - 20, oy - gh + 20, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(text(ox + gw - 5, oy - gh + 15, "V_Q = V_QB", size=10, color=MUTED))

    # VTC1: V_QB = Inverter1(V_Q) - синя лінія
    # Ідеалізована передавальна характеристика
    p_vtc1 = [
        (ox, oy - gh + 20),
        (ox + 80, oy - gh + 20),
        (ox + 130, oy - gh + 35),
        (ox + 160, oy - gh + 100),
        (ox + 180, oy - gh + 240),
        (ox + 210, oy - 15),
        (ox + gw - 20, oy)
    ]
    d_vtc1 = "M " + " L ".join(["%.1f,%.1f" % pt for pt in p_vtc1])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_vtc1, NEG))
    frags.append(text(ox + 100, oy - gh + 5, "VTC1: V_QB = f(V_Q)", size=11, color=NEG, bold=True))

    # VTC2: V_Q = Inverter2(V_QB) - червона лінія (дзеркальна)
    p_vtc2 = [
        (ox + gw - 20, oy),
        (ox + gw - 20, oy - 80),
        (ox + gw - 35, oy - 130),
        (ox + gw - 100, oy - 160),
        (ox + gw - 240, oy - 180),
        (ox + 15, oy - 210),
        (ox, oy - gh + 20)
    ]
    d_vtc2 = "M " + " L ".join(["%.1f,%.1f" % pt for pt in p_vtc2])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_vtc2, POS))
    frags.append(text(ox + gw - 60, oy - 45, "VTC2: V_Q = f(V_QB)", size=11, color=POS, bold=True))

    # Стійкі стани та метастабільна точка
    frags.append(circle(ox + 5, oy - gh + 25, 5, fill=FIELD, stroke=FIELD))
    frags.append(text(ox + 45, oy - gh + 40, "Стан «0»\n(0, V_DD)", size=10, color=FIELD, bold=True))

    frags.append(circle(ox + gw - 25, oy - 5, 5, fill=FIELD, stroke=FIELD))
    frags.append(text(ox + gw - 50, oy - 25, "Стан «1»\n(V_DD, 0)", size=10, color=FIELD, bold=True))

    frags.append(circle(ox + 170, oy - 170, 4, fill="#0f172a", stroke="#0f172a"))
    frags.append(text(ox + 210, oy - 175, "Метастабільна точка M", size=10, color="#0f172a", bold=True))

    # Вписаний квадрат SNM у ліву пелюстку (Hold SNM)
    sq_x, sq_y, sq_s = ox + 45, oy - gh + 75, 75
    frags.append(rect(sq_x, sq_y, sq_s, sq_s, fill="#ecfdf5", stroke=FIELD, sw=2, rx=0))
    frags.append(text(sq_x + sq_s/2, sq_y + sq_s/2 + 4, "Hold SNM", size=11, color=FIELD, bold=True))

    # Вписаний квадрат Read SNM (зменшений через збурення читання)
    r_sq_x, r_sq_y, r_sq_s = ox + 65, oy - gh + 95, 40
    frags.append(rect(r_sq_x, r_sq_y, r_sq_s, r_sq_s, fill="#fef2f2", stroke=POS, sw=1.5, rx=0))
    frags.append(text(r_sq_x + r_sq_s/2, r_sq_y + r_sq_s/2 + 3, "RSNM", size=9, color=POS, bold=True))

    # Текстова панель праворуч
    frags.append(rect(500, 50, 280, 390, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(640, 75, "Статичний запас завадостійкості", size=13, color=INK, bold=True))
    frags.append(text(640, 93, "(Static Noise Margin — SNM)", size=12, color=MUTED, bold=True))

    t_snm_desc = [
        "Геометричне визначення SNM:",
        "Сторона НАЙБІЛЬШОГО квадрата,",
        "що вписується в пелюстку кривої.",
        "",
        "1. Hold SNM (режим утримання):",
        "• WL = 0 В (ізольовані інвертори)",
        "• Максимальний розмір пелюсток",
        "• Типове значення: 250–350 мВ",
        "",
        "2. Read SNM (режим читання):",
        "• WL = V_DD, BL = V_DD",
        "• Сплеск V_read зміщує низ VTC",
        "• Пелюстки різко стискаються!",
        "• Типове значення: 100–180 мВ",
        "",
        "Якщо шум V_noise > SNM,",
        "комірка спонтанно втрачає біт!"
    ]
    frags.append(mtext(640, 120, t_snm_desc, size=11, color=INK, bold=False, lh=1.35))

    render(os.path.join(IMG_DIR, "butterfly-snm.svg"), w, h, *frags)


def fig_cell_8t():
    """Фігура 5: Архітектура 8T SRAM з розв'язаним портом читання для низьких напруг."""
    w, h = 840, 520
    frags = []

    frags.append(rect(20, 20, 800, 480, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Ліва частина: стандартне 6T ядро для запису
    frags.append(rect(40, 60, 420, 420, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(250, 85, "6T ядро комірки (тільки Запис та Збереження)", size=13, color=INK, bold=True))

    # Спрощене позначення двох інверторів
    b_inv1, _, _ = textbox(160, 240, "Інвертор 1\n(P1 / N1)", size=12, pad=8, fill="#ffffff", stroke=LINE, bold=True)
    frags.append(b_inv1)

    b_inv2, _, _ = textbox(340, 240, "Інвертор 2\n(P2 / N2)", size=12, pad=8, fill="#ffffff", stroke=LINE, bold=True)
    frags.append(b_inv2)

    # Зв'язки між інверторами
    frags.append(arrow(215, 225, 285, 225, color=LINE, sw=1.5))
    frags.append(arrow(285, 255, 215, 255, color=LINE, sw=1.5))

    frags.append(circle(225, 225, 4, fill=POS, stroke=POS))
    frags.append(text(225, 212, "Вузол Q", size=11, color=POS, bold=True))

    frags.append(circle(275, 255, 4, fill=NEG, stroke=NEG))
    frags.append(text(285, 275, "Вузол QB", size=11, color=NEG, bold=True))

    # Шини запису: WWL, WBL, WBLB
    frags.append(line(60, 130, 440, 130, color=FIELD, sw=2))
    frags.append(text(250, 122, "Словесна лінія запису WWL (Write Word Line)", size=11, color=FIELD, bold=True))

    frags.append(line(70, 95, 70, 460, color="#64748b", sw=2))
    frags.append(text(70, 472, "WBL", size=11, color="#64748b", bold=True))

    frags.append(line(430, 95, 430, 460, color="#64748b", sw=2))
    frags.append(text(430, 472, "WBLB", size=11, color="#64748b", bold=True))

    # Транзистори доступу на запис
    b_wax1, _, _ = textbox(110, 180, "W_AX1", size=10, pad=4, fill="#ecfdf5", stroke=FIELD)
    frags.append(b_wax1)
    b_wax2, _, _ = textbox(390, 180, "W_AX2", size=10, pad=4, fill="#ecfdf5", stroke=FIELD)
    frags.append(b_wax2)

    # Права частина: ізольований порт зчитування (2T Read Port)
    frags.append(rect(480, 60, 320, 420, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(640, 85, "Окремий порт читання (2T Read Port)", size=13, color=NEG, bold=True))

    # Шина читання RBL та RWL
    frags.append(line(740, 100, 740, 460, color=NEG, sw=2.5))
    frags.append(text(740, 475, "Лінія читання RBL", size=12, color=NEG, bold=True))

    frags.append(line(500, 130, 780, 130, color=POS, sw=2))
    frags.append(text(640, 122, "Словесна лінія читання RWL", size=11, color=POS, bold=True))

    # Транзистор доступу читання M8 (RD_AX)
    b_m8, _, _ = textbox(640, 190, "M8 (RD_AX)\nКлюч читання", size=12, pad=6, fill="#fdecea", stroke=POS, bold=True)
    frags.append(b_m8)
    frags.append(line(640, 130, 640, 160, color=POS, sw=2))
    frags.append(line(700, 190, 740, 190, color=LINE, sw=2))
    frags.append(line(640, 220, 640, 280, color=LINE, sw=2))

    # Буферний транзистор зчитування M7 (RD_BUF)
    b_m7, _, _ = textbox(640, 310, "M7 (RD_BUF)\nБуфер стану", size=12, pad=6, fill="#eaf0fd", stroke=NEG, bold=True)
    frags.append(b_m7)
    frags.append(line(640, 340, 640, 390, color=LINE, sw=2))

    # Земля порту читання
    frags.append(line(600, 390, 680, 390, color="#1e293b", sw=2.5))
    frags.append(text(640, 405, "GND", size=11, color="#1e293b", bold=True))

    # Ключова лінія зв'язку: Затвор M7 підключено до QB (або Q)
    frags.append(line(275, 255, 275, 310, color=NEG, sw=2, dash="3,3"))
    frags.append(line(275, 310, 580, 310, color=NEG, sw=2))
    frags.append(arrow(540, 310, 580, 310, color=NEG, sw=2))
    frags.append(text(450, 325, "Зв'язок керування (лише затвор!)", size=11, color=NEG, bold=True))

    # Текстова врізка переваги
    frags.append(rect(500, 420, 280, 45, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(640, 437, "ГОЛОВНА ПЕРЕВАГА 8T:", size=11, color=FIELD, bold=True))
    frags.append(text(640, 453, "Read SNM = Hold SNM (нуль збурень на вузлах!)", size=10, color="#0f172a", bold=True))

    render(os.path.join(IMG_DIR, "cell-8t-schematic.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_cell_6t()
    fig_read_operation()
    fig_write_operation()
    fig_butterfly_snm()
    fig_cell_8t()
    print("Всі фігури для sram-cell згенеровано успішно.")

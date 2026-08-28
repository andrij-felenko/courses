# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Енкодер поворотний»."""

import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')


def gen_fig1_quadrature():
    """Фігура 1: Геометрія контактів, квадратурні сигнали (CW/CCW), код Грея та фіксація (detents)."""
    w, h = 920, 520
    frags = []

    # Заголовок панелі 1: Фізичний диск і контакти
    frags.append(fitbox(20, 20, 260, 480, "", fill="#ffffff", stroke="#d0d7de", rx=8))
    frags.append(text(150, 46, "Будова контактної пари", size=15, bold=True))

    # Візуалізація кодового диска та трьох щіток
    frags.append(circle(150, 165, 80, fill="#f8fafc", stroke="#64748b", sw=2))
    # Сектори диска (імітація зубців ротора)
    import math
    for ang in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(ang)
        x1 = 150 + 40 * math.cos(rad)
        y1 = 165 + 40 * math.sin(rad)
        x2 = 150 + 78 * math.cos(rad)
        y2 = 165 + 78 * math.sin(rad)
        frags.append(line(x1, y1, x2, y2, color="#334155", sw=6))

    frags.append(circle(150, 165, 38, fill="#e2e8f0", stroke="#475569", sw=1.5))
    frags.append(circle(150, 165, 12, fill="#94a3b8", stroke="#334155", sw=1.5))
    frags.append(text(150, 170, "Вал", size=11, bold=True))

    # Контакти A, B, Common
    # Common (GND)
    frags.append(line(150, 245, 150, 280, color=NEG, sw=2.5))
    frags.append(circle(150, 280, 4, fill=NEG, stroke=NEG))
    frags.append(text(150, 298, "Вивід C (GND)", size=12, color=NEG, bold=True))

    # Фаза A
    frags.append(line(225, 140, 255, 120, color=POS, sw=2.5))
    frags.append(circle(255, 120, 4, fill=POS, stroke=POS))
    frags.append(text(240, 110, "Канал A", size=12, color=POS, bold=True))

    # Фаза B (зсув 90° електричних)
    frags.append(line(210, 210, 255, 230, color="#2563eb", sw=2.5))
    frags.append(circle(255, 230, 4, fill="#2563eb", stroke="#2563eb"))
    frags.append(text(240, 250, "Канал B", size=12, color="#2563eb", bold=True))

    # Опис геометрії щіток
    frags.append(fitbox(35, 325, 230, 160,
                        "• Щітки A та B зсунуті\n  на 90° фазового кута\n• Диск з'єднаний із C (GND)\n• 1 перехід = 1 біт зміни\n• Код Грея без гонитви",
                        size=12, pad=10, fill="#f1f5f9", stroke="#cbd5e1"))

    # Панель 2: Квадратурні діаграми CW та CCW
    frags.append(fitbox(295, 20, 605, 480, "", fill="#ffffff", stroke="#d0d7de", rx=8))

    # Обертання за годинниковою стрілкою (CW)
    frags.append(text(595, 46, "Обертання CW: Канал A випереджає B на 90°", size=13, bold=True))

    # Часова сітка CW
    x_start = 360
    t_step = 60
    for i in range(5):
        tx = x_start + i * t_step
        frags.append(line(tx, 65, tx, 225, color="#e2e8f0", sw=1, dash="3,3"))
        frags.append(text(tx, 60, "S%d" % i, size=11, color=MUTED))

    # Сигнал A (CW)
    frags.append(text(330, 100, "A (CW)", size=12, color=POS, bold=True))
    path_a_cw = "M %d 85 " % x_start
    path_a_cw += "L %d 85 L %d 125 L %d 125 L %d 85 L %d 85" % (x_start + 60, x_start + 60, x_start + 180, x_start + 180, x_start + 240)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_a_cw, POS))

    # Сигнал B (CW - відстає на 90°)
    frags.append(text(330, 165, "B (CW)", size=12, color="#2563eb", bold=True))
    path_b_cw = "M %d 185 " % x_start
    path_b_cw += "L %d 185 L %d 145 L %d 145 L %d 185 L %d 185" % (x_start + 120, x_start + 120, x_start + 240, x_start + 240, x_start + 240)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_b_cw, "#2563eb"))

    # Стани коду Грея для CW
    frags.append(text(x_start + 30, 215, "11", size=12, bold=True))
    frags.append(text(x_start + 90, 215, "01", size=12, bold=True))
    frags.append(text(x_start + 150, 215, "00", size=12, bold=True))
    frags.append(text(x_start + 210, 215, "10", size=12, bold=True))
    frags.append(text(740, 145, "Послідовність CW:\n11 → 01 → 00 → 10 → 11", size=12, bold=True, color="#1e293b"))

    # Позначка Detent (клік)
    frags.append(line(x_start, 70, x_start, 220, color=FIELD, sw=2))
    frags.append(line(x_start + 240, 70, x_start + 240, 220, color=FIELD, sw=2))
    frags.append(text(x_start + 240, 240, "Клік (Detent)", size=11, color=FIELD, bold=True))

    # Розділювальна лінія
    frags.append(line(310, 255, 880, 255, color="#cbd5e1", sw=1.5))

    # Обертання проти годинникової стрілки (CCW)
    frags.append(text(595, 280, "Обертання CCW: Канал B випереджає A на 90°", size=13, bold=True))

    # Часова сітка CCW
    for i in range(5):
        tx = x_start + i * t_step
        frags.append(line(tx, 295, tx, 455, color="#e2e8f0", sw=1, dash="3,3"))
        frags.append(text(tx, 292, "S%d" % i, size=11, color=MUTED))

    # Сигнал A (CCW)
    frags.append(text(330, 335, "A (CCW)", size=12, color=POS, bold=True))
    path_a_ccw = "M %d 320 " % x_start
    path_a_ccw += "L %d 320 L %d 360 L %d 360 L %d 320 L %d 320" % (x_start + 120, x_start + 120, x_start + 240, x_start + 240, x_start + 240)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_a_ccw, POS))

    # Сигнал B (CCW)
    frags.append(text(330, 400, "B (CCW)", size=12, color="#2563eb", bold=True))
    path_b_ccw = "M %d 385 " % x_start
    path_b_ccw += "L %d 385 L %d 425 L %d 425 L %d 385 L %d 385" % (x_start + 60, x_start + 60, x_start + 180, x_start + 180, x_start + 240)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_b_ccw, "#2563eb"))

    # Стани коду Грея для CCW
    frags.append(text(x_start + 30, 445, "11", size=12, bold=True))
    frags.append(text(x_start + 90, 445, "10", size=12, bold=True))
    frags.append(text(x_start + 150, 445, "00", size=12, bold=True))
    frags.append(text(x_start + 210, 445, "01", size=12, bold=True))
    frags.append(text(740, 375, "Послідовність CCW:\n11 → 10 → 00 → 01 → 11", size=12, bold=True, color="#1e293b"))

    frags.append(text(x_start + 240, 470, "Клік (Detent)", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "encoder-quadrature.svg"), w, h, *frags)


def gen_fig2_switch_bounce():
    """Фігура 2: Контактний брязкіт, згладжування RC-фільтром та відновлення тригером Шмітта."""
    w, h = 920, 500
    frags = []

    # 1. Сирий брязкіт контактів
    frags.append(fitbox(20, 20, 560, 135, "", fill="#ffffff", stroke="#cbd5e1", rx=6))
    frags.append(text(280, 42, "1. Сирий сигнал на контакті (брязкіт 1–10 мс)", size=13, color=POS, bold=True))

    frags.append(line(50, 115, 540, 115, color="#94a3b8", sw=1))  # 0V GND
    frags.append(line(50, 65, 540, 65, color="#e2e8f0", sw=1, dash="2,2"))  # 3.3V VCC
    frags.append(text(35, 68, "3.3V", size=10, color=MUTED))
    frags.append(text(35, 118, "0V", size=10, color=MUTED))

    # Траєкторія брязкоту при замиканні
    p_bounce = "M 50 65 L 140 65 "
    p_bounce += "L 140 115 L 148 65 L 155 115 L 163 75 L 170 115 L 176 85 L 184 115 L 192 95 L 200 115 "
    p_bounce += "L 380 115 "
    p_bounce += "L 380 75 L 388 115 L 396 65 L 404 105 L 412 65 L 540 65"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (p_bounce, POS))
    frags.append(text(175, 140, "Брязкіт t_b ≈ 2–5 мс", size=11, color=POS))

    # 2. Сигнал після RC-фільтра
    frags.append(fitbox(20, 170, 560, 145, "", fill="#ffffff", stroke="#cbd5e1", rx=6))
    frags.append(text(280, 192, "2. Напруга після RC (10 кОм + 100 нФ, tau = 1 мс)", size=13, color="#d97706", bold=True))

    frags.append(line(50, 275, 540, 275, color="#94a3b8", sw=1))  # 0V GND
    frags.append(line(50, 215, 540, 215, color="#e2e8f0", sw=1, dash="2,2"))  # 3.3V
    frags.append(text(35, 218, "3.3V", size=10, color=MUTED))
    frags.append(text(35, 278, "0V", size=10, color=MUTED))

    # Пороги тригера Шмітта
    frags.append(line(50, 235, 500, 235, color="#10b981", sw=1, dash="4,4"))
    frags.append(text(505, 238, "V_T+ (2.0V)", size=10, color="#10b981", anchor="start"))
    frags.append(line(50, 255, 500, 255, color="#059669", sw=1, dash="4,4"))
    frags.append(text(505, 258, "V_T- (1.1V)", size=10, color="#059669", anchor="start"))

    # Експоненційне згладжування
    p_rc = "M 50 215 L 140 215 "
    p_rc += "C 160 220, 200 270, 260 275 L 380 275 "
    p_rc += "C 400 270, 440 220, 500 215 L 540 215"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p_rc, "#d97706"))
    frags.append(text(210, 300, "Брязкіт придушено, фронт затягнутий", size=11, color="#d97706"))

    # 3. Вихід тригера Шмітта
    frags.append(fitbox(20, 330, 560, 145, "", fill="#ffffff", stroke="#cbd5e1", rx=6))
    frags.append(text(280, 352, "3. Вихід тригера Шмітта (74LVC14)", size=13, color=FIELD, bold=True))

    frags.append(line(50, 435, 540, 435, color="#94a3b8", sw=1))  # 0V GND
    frags.append(line(50, 380, 540, 380, color="#e2e8f0", sw=1, dash="2,2"))  # 3.3V
    frags.append(text(35, 383, "3.3V", size=10, color=MUTED))
    frags.append(text(35, 438, "0V", size=10, color=MUTED))

    # Чистий прямокутник
    p_clean = "M 50 380 L 195 380 L 195 435 L 450 435 L 450 380 L 540 380"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p_clean, FIELD))
    frags.append(text(280, 460, "Крутий фронт (<5 нс), рівно ОДИН перехід", size=11, color=FIELD, bold=True))

    # Права панель: Вольт-амперна петля гістерезису тригера Шмітта
    frags.append(fitbox(605, 20, 295, 455, "", fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(text(752, 48, "Петля гістерезису", size=15, bold=True))

    # Осі координат V_вх / V_вих
    frags.append(arrow(640, 270, 870, 270, color="#475569", sw=1.5))
    frags.append(text(860, 290, "V_вх", size=12, color="#475569", bold=True))

    frags.append(arrow(660, 290, 660, 80, color="#475569", sw=1.5))
    frags.append(text(645, 95, "V_вих", size=12, color="#475569", bold=True))

    # Графік гістерезису інвертора Шмітта
    frags.append(line(660, 120, 780, 120, color="#2563eb", sw=2.5))  # High out
    frags.append(line(780, 120, 780, 260, color="#2563eb", sw=2.5))  # Switch to Low at V_T+
    frags.append(line(780, 260, 850, 260, color="#2563eb", sw=2.5))  # Low out

    frags.append(line(850, 260, 720, 260, color=POS, sw=2, dash="3,3"))
    frags.append(line(720, 260, 720, 120, color=POS, sw=2.5))  # Switch to High at V_T-
    frags.append(line(720, 120, 660, 120, color=POS, sw=2, dash="3,3"))

    # Підписи порогів
    frags.append(line(720, 265, 720, 275, color=LINE, sw=1.5))
    frags.append(text(720, 290, "V_T-", size=12, color=POS, bold=True))
    frags.append(text(720, 305, "1.1 В", size=10, color=MUTED))

    frags.append(line(780, 265, 780, 275, color=LINE, sw=1.5))
    frags.append(text(780, 290, "V_T+", size=12, color="#2563eb", bold=True))
    frags.append(text(780, 305, "2.0 В", size=10, color=MUTED))

    # Стрілка гістерезису
    frags.append(line(720, 335, 780, 335, color=FIELD, sw=2))
    frags.append(circle(720, 335, 3, fill=FIELD, stroke=FIELD))
    frags.append(circle(780, 335, 3, fill=FIELD, stroke=FIELD))
    frags.append(text(750, 355, "ΔV_T = 0.9 В", size=12, color=FIELD, bold=True))

    frags.append(fitbox(620, 380, 265, 80,
                        "Гістерезис гарантує:\nпоки шумова амплітуда < ΔV_T,\nповторні перемикання\nфізично неможливі.",
                        size=11, pad=8, fill="#ffffff", stroke="#e2e8f0"))

    render(os.path.join(IMG_DIR, "switch-bounce-filter.svg"), w, h, *frags)


def gen_fig3_magnetic_vs_optical():
    """Фігура 3: Порівняння безконтактних енкодерів (магнітний Hall/AMR CORDIC проти оптичного)."""
    w, h = 920, 480
    frags = []

    # Ліва колонка: Магнітний енкодер
    frags.append(fitbox(20, 20, 430, 440, "", fill="#ffffff", stroke="#cbd5e1", rx=8))
    frags.append(text(235, 48, "Магнітний енкодер (Hall / AMR / TMR)", size=15, bold=True, color="#0f766e"))

    # Діаметральний магніт на валу
    frags.append(circle(235, 115, 35, fill="#f1f5f9", stroke="#334155", sw=2))
    frags.append(fitbox(200, 95, 35, 40, "N", size=14, bold=True, fill="#fee2e2", stroke=POS, color=POS))
    frags.append(fitbox(235, 95, 35, 40, "S", size=14, bold=True, fill="#e0e7ff", stroke=NEG, color=NEG))
    frags.append(text(235, 165, "Магніт на торці вала", size=11, color=MUTED))

    # Зазор
    frags.append(line(235, 172, 235, 192, color=FIELD, sw=1.5, dash="2,2"))
    frags.append(text(300, 185, "Зазор 0.5–2 мм", size=10, color=FIELD, bold=True))

    # Чіп датчика кута
    frags.append(fitbox(135, 198, 200, 90, "Датчик кута (напр. AS5600)\n• 4× Hall-сенсори (Bx, By)\n• 12–14 біт АЦП\n• CORDIC atan2(By, Bx)",
                        size=11, pad=8, fill="#f8fafc", stroke="#0f766e", color="#0f766e"))

    # Вихідні інтерфейси
    frags.append(fitbox(70, 310, 330, 130,
                        "Інтерфейси виходу:\n• SSI / SPI (12–14 біт абсолютний кут)\n• I²C (конфігурація та телеметрія)\n• PWM (шпаруватість 0–100% = 0–360°)\n• Квадратурний ABZ (емуляція до 4096 CPR)\n• Ресурс: необмежений (безконтактний)",
                        size=11, pad=10, fill="#ecfdf5", stroke="#a7f3d0", color="#065f46"))

    # Права колонка: Оптичний енкодер
    frags.append(fitbox(470, 20, 430, 440, "", fill="#ffffff", stroke="#cbd5e1", rx=8))
    frags.append(text(685, 48, "Оптичний енкодер (Code Wheel + Matrix)", size=15, bold=True, color="#1e40af"))

    # Світлодіод
    frags.append(circle(550, 115, 15, fill="#fef08a", stroke="#ca8a04", sw=2))
    frags.append(text(550, 119, "LED", size=10, bold=True))
    frags.append(arrow(570, 115, 620, 115, color="#ca8a04", sw=2))

    # Скляний диск із рисками
    frags.append(rect(630, 80, 20, 70, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=2))
    for y_slot in [85, 95, 105, 115, 125, 135]:
        frags.append(line(630, y_slot, 650, y_slot, color="#0f172a", sw=3))
    frags.append(text(640, 165, "Диск із прорізами", size=11, color=MUTED))

    frags.append(arrow(655, 115, 705, 115, color="#2563eb", sw=2))

    # Фотоматриця
    frags.append(fitbox(715, 80, 150, 70, "Фотоприймач\n• Фотодіоди A / B\n• Компаратор\n• Інтерполятор",
                        size=11, pad=6, fill="#eff6ff", stroke="#1d4ed8", color="#1e40af"))

    # Вихідні характеристики
    frags.append(fitbox(520, 310, 330, 130,
                        "Особливості оптичної схеми:\n• Найвища точність та кутова роздільність\n• Роздільність до 50 000+ PPR (з інтерполяцією)\n• Нечутливість до магнітних полів\n• Чутливий до пилу, конденсату та вібрацій\n• Обмежений температурний діапазон скла",
                        size=11, pad=10, fill="#eff6ff", stroke="#bfdbfe", color="#1e3a8a"))

    render(os.path.join(IMG_DIR, "magnetic-vs-optical.svg"), w, h, *frags)


def gen_fig4_wiring_schematic():
    """Фігура 4: Повна схемотехніка підключення механічного енкодера до GPIO МК."""
    w, h = 940, 520
    frags = []

    # Контур плати / пристрою
    frags.append(rect(15, 15, 910, 490, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(470, 42, "Схема апаратного підключення механічного енкодера (Фільтрація + ESD + Шмітт)", size=15, bold=True))

    # 1. Блок енкодера (ліворуч)
    frags.append(rect(40, 80, 150, 380, fill="#f8fafc", stroke="#64748b", sw=2, rx=6))
    frags.append(text(115, 108, "Енкодер EC11", size=14, bold=True))
    frags.append(text(115, 126, "(Bourns PEC11R)", size=11, color=MUTED))

    # Виводи енкодера
    # Pin A
    frags.append(circle(190, 160, 5, fill=POS, stroke=POS))
    frags.append(text(175, 164, "A", size=12, bold=True, anchor="end"))
    # Pin C
    frags.append(circle(190, 210, 5, fill=NEG, stroke=NEG))
    frags.append(text(175, 214, "C (GND)", size=12, bold=True, anchor="end"))
    # Pin B
    frags.append(circle(190, 260, 5, fill="#2563eb", stroke="#2563eb"))
    frags.append(text(175, 264, "B", size=12, bold=True, anchor="end"))
    # Pin SW1
    frags.append(circle(190, 360, 5, fill="#d97706", stroke="#d97706"))
    frags.append(text(175, 364, "SW", size=12, bold=True, anchor="end"))
    # Pin SW2
    frags.append(circle(190, 410, 5, fill=NEG, stroke=NEG))
    frags.append(text(175, 414, "GND", size=12, bold=True, anchor="end"))

    # Лінії заземлення енкодера
    frags.append(line(190, 210, 220, 210, color=NEG, sw=2))
    frags.append(line(220, 210, 220, 450, color=NEG, sw=2))
    frags.append(line(190, 410, 220, 410, color=NEG, sw=2))
    frags.append(line(220, 450, 220, 465, color=NEG, sw=2))
    frags.append(line(210, 465, 230, 465, color=NEG, sw=2))  # Символ GND
    frags.append(line(214, 469, 226, 469, color=NEG, sw=1.5))
    frags.append(line(217, 473, 223, 473, color=NEG, sw=1))

    # 2. Блок підтяжки (Pull-Up) та фільтрації (RC)
    # Лінія VCC 3.3V
    frags.append(line(260, 75, 480, 75, color=POS, sw=2))
    frags.append(text(250, 78, "+3.3V", size=12, color=POS, bold=True, anchor="end"))

    # Канал A: RC
    # Pull-up R1 10k
    frags.append(line(190, 160, 290, 160, color=LINE, sw=2))
    frags.append(line(290, 75, 290, 115, color=LINE, sw=2))
    frags.append(rect(280, 115, 20, 30, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(315, 133, "R1 10k", size=11, bold=True, anchor="start"))
    frags.append(line(290, 145, 290, 160, color=LINE, sw=2))

    # Послідовний R_f 10k
    frags.append(rect(340, 150, 30, 20, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(355, 142, "R_f1 10k", size=11, bold=True))
    frags.append(line(290, 160, 340, 160, color=LINE, sw=2))
    frags.append(line(370, 160, 440, 160, color=LINE, sw=2))

    # Конденсатор C_f 100nF на землю
    frags.append(line(410, 160, 410, 185, color=LINE, sw=1.5))
    frags.append(line(400, 185, 420, 185, color=LINE, sw=2))
    frags.append(line(400, 191, 420, 191, color=LINE, sw=2))
    frags.append(text(435, 190, "C1 100nF", size=11, bold=True, anchor="start"))
    frags.append(line(410, 191, 410, 210, color=NEG, sw=1.5))

    # Канал B: RC
    frags.append(line(190, 260, 290, 260, color=LINE, sw=2))
    frags.append(line(290, 75, 290, 215, color=LINE, sw=2))
    frags.append(rect(280, 215, 20, 30, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(315, 233, "R2 10k", size=11, bold=True, anchor="start"))
    frags.append(line(290, 245, 290, 260, color=LINE, sw=2))

    frags.append(rect(340, 250, 30, 20, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(355, 242, "R_f2 10k", size=11, bold=True))
    frags.append(line(290, 260, 340, 260, color=LINE, sw=2))
    frags.append(line(370, 260, 440, 260, color=LINE, sw=2))

    frags.append(line(410, 260, 410, 285, color=LINE, sw=1.5))
    frags.append(line(400, 285, 420, 285, color=LINE, sw=2))
    frags.append(line(400, 291, 420, 291, color=LINE, sw=2))
    frags.append(text(435, 290, "C2 100nF", size=11, bold=True, anchor="start"))
    frags.append(line(410, 291, 410, 310, color=NEG, sw=1.5))

    # Кнопка SW: RC
    frags.append(line(190, 360, 290, 360, color=LINE, sw=2))
    frags.append(line(290, 75, 290, 315, color=LINE, sw=2))
    frags.append(rect(280, 315, 20, 30, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(315, 333, "R3 10k", size=11, bold=True, anchor="start"))
    frags.append(line(290, 345, 290, 360, color=LINE, sw=2))

    frags.append(rect(340, 350, 30, 20, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(355, 342, "R_f3 10k", size=11, bold=True))
    frags.append(line(290, 360, 340, 360, color=LINE, sw=2))
    frags.append(line(370, 360, 440, 360, color=LINE, sw=2))

    frags.append(line(410, 360, 410, 385, color=LINE, sw=1.5))
    frags.append(line(400, 385, 420, 385, color=LINE, sw=2))
    frags.append(line(400, 391, 420, 391, color=LINE, sw=2))
    frags.append(text(435, 390, "C3 100nF", size=11, bold=True, anchor="start"))
    frags.append(line(410, 391, 410, 410, color=NEG, sw=1.5))

    # Земляна шина фільтрів
    frags.append(line(410, 210, 410, 430, color=NEG, sw=1.5))
    frags.append(line(220, 430, 410, 430, color=NEG, sw=1.5))

    # 3. Тригер Шмітта (74LVC14)
    frags.append(rect(510, 110, 160, 300, fill="#eff6ff", stroke="#3b82f6", sw=2, rx=6))
    frags.append(text(590, 135, "74LVC14", size=14, bold=True, color="#1e40af"))
    frags.append(text(590, 150, "Тригери Шмітта", size=11, color=MUTED))

    # Елементи інверторів
    for y_ic, name in [(180, "U1A"), (260, "U1B"), (340, "U1C")]:
        frags.append(line(440, y_ic, 510, y_ic, color=LINE, sw=2))
        frags.append(rect(540, y_ic - 18, 45, 36, fill="#ffffff", stroke="#1d4ed8", sw=1.5, rx=3))
        frags.append(text(562, y_ic + 5, name, size=11, bold=True))
        frags.append(circle(590, y_ic, 4, fill="#ffffff", stroke="#1d4ed8", sw=1.5))  # Інверсне коло
        frags.append(line(594, y_ic, 670, y_ic, color=LINE, sw=2))

    # 4. Мікроконтролер (праворуч)
    frags.append(rect(730, 80, 175, 380, fill="#f8fafc", stroke="#0f172a", sw=2, rx=6))
    frags.append(text(817, 110, "Мікроконтролер", size=14, bold=True))
    frags.append(text(817, 128, "(STM32 / ESP32)", size=11, color=MUTED))

    # Піни МК
    frags.append(line(670, 180, 730, 180, color=POS, sw=2))
    frags.append(circle(730, 180, 4, fill=POS, stroke=POS))
    frags.append(text(745, 184, "GPIO_ENC_A", size=12, bold=True, anchor="start"))
    frags.append(text(817, 202, "(Таймер)", size=10, color=MUTED))

    frags.append(line(670, 260, 730, 260, color="#2563eb", sw=2))
    frags.append(circle(730, 260, 4, fill="#2563eb", stroke="#2563eb"))
    frags.append(text(745, 264, "GPIO_ENC_B", size=12, bold=True, anchor="start"))
    frags.append(text(817, 282, "(Таймер)", size=10, color=MUTED))

    frags.append(line(670, 340, 730, 340, color="#d97706", sw=2))
    frags.append(circle(730, 340, 4, fill="#d97706", stroke="#d97706"))
    frags.append(text(745, 344, "GPIO_ENC_SW", size=12, bold=True, anchor="start"))
    frags.append(text(817, 362, "(Кнопка)", size=10, color=MUTED))

    render(os.path.join(IMG_DIR, "encoder-wiring-schematic.svg"), w, h, *frags)


if __name__ == "__main__":
    os.makedirs(IMG_DIR, exist_ok=True)
    gen_fig1_quadrature()
    gen_fig2_switch_bounce()
    gen_fig3_magnetic_vs_optical()
    gen_fig4_wiring_schematic()
    print("Всі SVG-фігури згенеровано успішно.")

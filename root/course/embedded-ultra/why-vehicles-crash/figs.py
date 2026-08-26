# -*- coding: utf-8 -*-
"""Фігури теми «Чому апарати падають».
Запуск: python figs.py -> ./img/*.svg
Імпортуємо svgkit зі scripts/."""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Каскадне розгортання відмов ─────────────────────────────────────
def fig_failure_taxonomy():
    W, H = 820, 420
    parts = []

    # Заголовок зверху
    parts.append(rect(20, 15, 780, 40, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(410, 40, "ДОМЕНИ ПЕРВИННИХ ВІДМОВ ТА ЛАНЦЮГ КАСКАДНОЇ КАТАСТРОФИ", size=12, bold=True, color=INK))

    # 4 колонки доменів відмов
    domains = [
        ("Механічний домен", "Зрив лопаті, дебаланс,\nперегрів підшипника,\nруйнування кріплення", "#fdecea", POS),
        ("Електричний домен", "Просідання батареї,\nBOD-скидання MCU,\nіндуктивний викид ESC", "#fffaf0", "#d97706"),
        ("Сенсорний домен", "Кліпінг MEMS IMU,\nзавади компаса від струмів,\nдевіація барометра", "#eaf0fd", NEG),
        ("Програмний домен", "Зависання шини I2C,\nінверсія пріоритетів RTOS,\nпереповнення буфера", "#f4fbf6", FIELD)
    ]

    for i, (dom_title, dom_desc, bg_col, br_col) in enumerate(domains):
        x = 30 + i * 195
        parts.append(rect(x, 70, 180, 100, fill=bg_col, stroke=br_col, sw=1.8, rx=6))
        parts.append(text(x + 90, 92, dom_title, size=11, bold=True, color=br_col))
        parts.append(mtext(x + 90, 115, dom_desc, size=9.5, color=INK, lh=1.3))

        # Стрілка вниз до каскадної взаємодії
        parts.append(arrow(x + 90, 170, x + 90, 205, color=br_col, sw=1.8))

    # Центральний рівень: проміжний стан деградації
    parts.append(rect(30, 205, 760, 80, fill="#ffffff", stroke=LINE, sw=2, rx=8))
    parts.append(text(410, 226, "ЕТАП КАСКАДНОГО ПОШИРЕННЯ ТА ВТРАТИ КЕРОВАНОСТІ", size=11.5, bold=True, color=INK))

    # 3 блоки всередині проміжного стану
    parts.append(fitbox(45, 238, 220, 38, "1. Насичення інтегратора PID\nта перекос тяги двигунів", size=9.5, fill="#f8fafc", stroke=MUTED))
    parts.append(arrow(265, 257, 295, 257, color=MUTED, sw=1.5))

    parts.append(fitbox(295, 238, 225, 38, "2. Стрибок струму на здорових плечах\nта просідання живлення шини", size=9.5, fill="#f8fafc", stroke=MUTED))
    parts.append(arrow(520, 257, 550, 257, color=MUTED, sw=1.5))

    parts.append(fitbox(550, 238, 225, 38, "3. Зрив оцінки просторового стану\n(EKF divergence / IMU lock)", size=9.5, fill="#f8fafc", stroke=MUTED))

    # Стрілка вниз до фінального краху або порятунку
    parts.append(arrow(250, 285, 200, 325, color=POS, sw=2))
    parts.append(text(180, 305, "Без Failsafe", size=10, bold=True, color=POS, anchor="end"))

    parts.append(arrow(570, 285, 620, 325, color=FIELD, sw=2))
    parts.append(text(640, 305, "З активним Failsafe", size=10, bold=True, color=FIELD, anchor="start"))

    # Фінальні результати
    # Лівий: Катастрофа
    parts.append(rect(30, 325, 360, 75, fill="#fdecea", stroke=POS, sw=2, rx=6))
    parts.append(text(210, 348, "КАТАСТРОФІЧНА ВІДМОВА (CRASH)", size=12, bold=True, color=POS))
    parts.append(mtext(210, 368, "Неконтрольоване обертання, Brownout-скид,\nпадіння на повній швидкості без захисту", size=9.5, color=INK, lh=1.3))

    # Правий: Деградація та безпечний порятунок
    parts.append(rect(430, 325, 360, 75, fill="#f4fbf6", stroke=FIELD, sw=2, rx=6))
    parts.append(text(610, 348, "КЕРОВАНА ДЕГРАДАЦІЯ ТА СПАСІННЯ", size=12, bold=True, color=FIELD))
    parts.append(mtext(610, 368, "Десатурація PID, вимикання битого мотора,\nаварійна посадка або викид парашута", size=9.5, color=INK, lh=1.3))

    render(os.path.join(IMG, "failure-taxonomy-cascade.svg"), W, H, *parts,
           title="Каскадний ланцюг виникнення та поширення відмов у безпілотному апараті")


# ── Фігура 2: Кліпінг MEMS та девіація оцінки орієнтації ──────────────────────
def fig_imu_clipping():
    W, H = 800, 390
    parts = []

    # Заголовок
    parts.append(rect(20, 15, 760, 40, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(400, 40, "МЕХАНІЗМ ВИНИКНЕННЯ ПОХИБКИ IMU ЧЕРЕЗ АСИМЕТРИЧНИЙ КЛІПІНГ", size=12, bold=True, color=INK))

    # Лівий графік: Сигнал вібрації без кліпінгу
    parts.append(rect(30, 70, 355, 230, fill="#ffffff", stroke=MUTED, sw=1.5, rx=6))
    parts.append(text(207, 95, "1. Справжній сигнал із вібрацією", size=11, bold=True, color=FIELD))

    # Осі
    parts.append(line(50, 185, 365, 185, color=LINE, sw=1.2)) # вісь X
    parts.append(line(70, 275, 70, 115, color=LINE, sw=1.2)) # вісь Y
    parts.append(text(360, 198, "t", size=10, color=MUTED))
    parts.append(text(65, 110, "g", size=10, color=MUTED, anchor="end"))

    # Межі шкали ±16g
    parts.append(line(70, 125, 365, 125, color=POS, sw=1, dash="4 4"))
    parts.append(text(65, 129, "+16g", size=9, color=POS, anchor="end"))
    parts.append(line(70, 245, 365, 245, color=POS, sw=1, dash="4 4"))
    parts.append(text(65, 249, "-16g", size=9, color=POS, anchor="end"))

    # Постійна складова 1g (горизонт)
    parts.append(line(70, 175, 365, 175, color=FIELD, sw=1.8))
    parts.append(text(370, 175, "1g (гравітація)", size=9, color=FIELD, anchor="start"))

    # Синусоїда з шумом навколо 1g (амплітуда 8g, поміщається в діапазон)
    pts1 = []
    for px in range(70, 360, 4):
        import math
        t = (px - 70) * 0.12
        val = 175 - 40 * math.sin(t) - 12 * math.sin(3.7 * t)
        pts1.append("%.1f,%.1f" % (px, val))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (" ".join(pts1), NEG))

    parts.append(fitbox(50, 255, 315, 35, "Середнє значення = точно 1g.\nФільтр Калмана вірно визначає вертикаль.", size=9.5, fill="#f4fbf6", stroke=FIELD))

    # Правий графік: Асиметричний кліпінг при сильних вібраціях
    parts.append(rect(415, 70, 355, 230, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    parts.append(text(592, 95, "2. Перевантаження та асиметричний зріз", size=11, bold=True, color=POS))

    # Осі
    parts.append(line(435, 185, 750, 185, color=LINE, sw=1.2))
    parts.append(line(455, 275, 455, 115, color=LINE, sw=1.2))
    parts.append(text(745, 198, "t", size=10, color=MUTED))
    parts.append(text(450, 110, "g", size=10, color=MUTED, anchor="end"))

    # Межі шкали ±16g
    parts.append(line(455, 135, 750, 135, color=POS, sw=1.2, dash="4 4"))
    parts.append(text(450, 139, "+16g (межа)", size=9, color=POS, anchor="end"))
    parts.append(line(455, 235, 750, 235, color=POS, sw=1.2, dash="4 4"))
    parts.append(text(450, 239, "-16g (межа)", size=9, color=POS, anchor="end"))

    # Справжній 1g (пунктир)
    parts.append(line(455, 180, 750, 180, color=MUTED, sw=1.2, dash="2 2"))
    parts.append(text(755, 178, "істинний 1g", size=9, color=MUTED, anchor="start"))

    # Хибне зміщене середнє (rectified DC offset)
    parts.append(line(455, 205, 750, 205, color=POS, sw=2))
    parts.append(text(755, 208, "хибне середнє -0.4g!", size=9, bold=True, color=POS, anchor="start"))

    # Сигнал із кліпінгом (зрізані верхівки)
    pts2 = []
    for px in range(455, 745, 4):
        import math
        t = (px - 455) * 0.12
        raw = 180 - 65 * math.sin(t) - 20 * math.sin(3.7 * t)
        clipped = max(135.0, min(235.0, raw))
        pts2.append("%.1f,%.1f" % (px, clipped))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (" ".join(pts2), POS))

    parts.append(fitbox(435, 255, 315, 35, "Верхні піки зрізані сильніше за нижні.\nВиникає випрямлений зсув (DC offset) -> крен у землю!", size=9.5, fill="#fdecea", stroke=POS))

    # Нижній висновок
    parts.append(rect(30, 315, 740, 60, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(400, 337, "НАСЛІДОК ДЛЯ СИСТЕМИ КЕРУВАННЯ:", size=11, bold=True, color=INK))
    parts.append(text(400, 358, "Автопілот вважає, що вектор гравітації нахилений, компенсує «нахил» і вводить апарат у піке.", size=10, color=POS))

    render(os.path.join(IMG, "imu-vibration-clipping.svg"), W, H, *parts,
           title="Асиметричний зріз вимірів IMU та зміщення розрахунку гравітаційного вектора")


# ── Фігура 3: Зависання шини I2C та відновлення ──────────────────────────────
def fig_i2c_bus_lockup():
    W, H = 820, 390
    parts = []

    # Заголовок
    parts.append(rect(20, 15, 780, 40, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(410, 40, "МЕХАНІЗМ ЗАХОПЛЕННЯ ШИНИ I2C ТА ПРОЦЕДУРА АПАРАТНОГО РОЗБЛОКУВАННЯ", size=12, bold=True, color=INK))

    # Верхній блок: Як виникає Deadlock шини
    parts.append(rect(30, 70, 760, 125, fill="#fffaf0", stroke="#d97706", sw=1.8, rx=6))
    parts.append(text(50, 92, "1. Фаза збою: ведучий (MCU) скидається, коли ведений (Slave) тримає SDA = 0", size=11, bold=True, color="#d97706", anchor="start"))

    # Часова діаграма збою
    # Сигнал SCL
    parts.append(text(50, 122, "SCL (Master)", size=10, bold=True, color=INK, anchor="start"))
    parts.append(line(150, 118, 170, 118, color=FIELD, sw=1.8))
    parts.append(line(170, 118, 170, 135, color=FIELD, sw=1.8))
    parts.append(line(170, 135, 190, 135, color=FIELD, sw=1.8))
    parts.append(line(190, 135, 190, 118, color=FIELD, sw=1.8))
    parts.append(line(190, 118, 210, 118, color=FIELD, sw=1.8))
    parts.append(line(210, 118, 210, 135, color=FIELD, sw=1.8))
    parts.append(line(210, 135, 230, 135, color=FIELD, sw=1.8))
    # Скидання MCU (SCL підтягується до High-Z/VCC)
    parts.append(line(230, 135, 230, 118, color=MUTED, sw=1.8, dash="3 3"))
    parts.append(line(230, 118, 480, 118, color=MUTED, sw=1.8))
    parts.append(text(340, 110, "MCU скинувся: SCL не генерується (High-Z)", size=9.5, color=MUTED))

    # Сигнал SDA
    parts.append(text(50, 160, "SDA (Slave)", size=10, bold=True, color=POS, anchor="start"))
    parts.append(line(150, 155, 180, 155, color=POS, sw=1.8))
    parts.append(line(180, 155, 180, 172, color=POS, sw=1.8))
    parts.append(line(180, 172, 480, 172, color=POS, sw=2.2)) # Тримає нуль!
    parts.append(text(330, 165, "Slave чекає такту SCL і тримає SDA = 0 В", size=9.5, bold=True, color=POS))

    # Блок наслідку праворуч
    parts.append(fitbox(500, 95, 275, 85, "Блокування:\nПісля перезавантаження MCU бачить SDA=0,\nвважає шину зайнятою іншим Master\nі зависає у нескінченному while-циклі!", size=9.5, fill="#fdecea", stroke=POS))

    # Нижній блок: Процедура відновлення (I2C Bus Clear)
    parts.append(rect(30, 210, 760, 165, fill="#f4fbf6", stroke=FIELD, sw=1.8, rx=6))
    parts.append(text(50, 232, "2. Алгоритм відновлення: генерація 9 тактів SCL через GPIO (Bit-Banging)", size=11, bold=True, color=FIELD, anchor="start"))

    # Покрокові 9 тактів
    parts.append(text(50, 265, "Крок 1: SCL у вихід GPIO, SDA у вхід", size=10, color=INK, anchor="start"))
    parts.append(text(50, 290, "Крок 2: 9 примусових імпульсів SCL", size=10, bold=True, color=FIELD, anchor="start"))

    # Малювання 9 імпульсів
    for k in range(9):
        x = 290 + k * 28
        parts.append(line(x, 295, x + 10, 295, color=FIELD, sw=1.6))
        parts.append(line(x + 10, 295, x + 10, 278, color=FIELD, sw=1.6))
        parts.append(line(x + 10, 278, x + 20, 278, color=FIELD, sw=1.6))
        parts.append(line(x + 20, 278, x + 20, 295, color=FIELD, sw=1.6))
        parts.append(line(x + 20, 295, x + 28, 295, color=FIELD, sw=1.6))
        parts.append(text(x + 15, 270, "%d" % (k + 1), size=9, color=FIELD))

    # Реакція SDA під час 9 тактів
    parts.append(text(50, 335, "Крок 3: Slave відпускає SDA (STOP-умова)", size=10, color=INK, anchor="start"))
    parts.append(line(290, 330, 480, 330, color=POS, sw=1.8))
    parts.append(line(480, 330, 495, 315, color=FIELD, sw=2)) # відпустив на 8-му такті
    parts.append(line(495, 315, 540, 315, color=FIELD, sw=2))
    parts.append(text(500, 345, "SDA відпущено в 1 (High-Z)", size=9, bold=True, color=FIELD))

    # Генерація STOP
    parts.append(fitbox(560, 255, 215, 105, "Фінал розблокування:\n1. Master формує умову STOP:\n   (SDA переходить 0->1 при SCL=1)\n2. Перемикання виводів назад в I2C\n3. Шина повністю відновлена!", size=9.5, fill="#ffffff", stroke=FIELD))

    render(os.path.join(IMG, "i2c-bus-lockup.svg"), W, H, *parts,
           title="Механізм апаратного зависання I2C та процедура скидання 9 тактами")


# ── Фігура 4: Кінцевий автомат Failsafe ────────────────────────────────────────
def fig_failsafe_fsm():
    W, H = 820, 400
    parts = []

    # Заголовок
    parts.append(rect(20, 15, 780, 40, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    parts.append(text(410, 40, "ІЄРАРХІЧНИЙ КІНЦЕВИЙ АВТОМАТ СИСТЕМИ АВАРІЙНОГО ЗАХИСТУ (FAILSAFE FSM)", size=12, bold=True, color=INK))

    # Стан 1: NORMAL
    parts.append(rect(40, 90, 160, 80, fill="#f4fbf6", stroke=FIELD, sw=2, rx=8))
    parts.append(text(120, 120, "1. NORMAL", size=13, bold=True, color=FIELD))
    parts.append(mtext(120, 142, "Усі давачі валідні\nРадіозв'язок стабільний\nНапруга в нормі", size=9, color=INK, lh=1.2))

    # Стан 2: DEGRADED (Втрата RC / одного сенсора)
    parts.append(rect(290, 90, 200, 80, fill="#fffaf0", stroke="#d97706", sw=2, rx=8))
    parts.append(text(390, 118, "2. SENSOR DEGRADED", size=12, bold=True, color="#d97706"))
    parts.append(mtext(390, 140, "Перемикання EKF lane\nФільтрація завад компаса\nЗаморозка I-терма PID", size=9, color=INK, lh=1.2))

    # Стан 3: RTH (Повернення додому)
    parts.append(rect(580, 90, 200, 80, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    parts.append(text(680, 118, "3. AUTO RTH / RTL", size=12, bold=True, color=NEG))
    parts.append(mtext(680, 140, "Втрата зв'язку RC > 1.5 с\nНабір безпечної висоти\nАвтоповернення на базу", size=9, color=INK, lh=1.2))

    # Стан 4: EMERGENCY LAND (Примусова посадка)
    parts.append(rect(290, 250, 200, 85, fill="#fdecea", stroke=POS, sw=2, rx=8))
    parts.append(text(390, 278, "4. EMERGENCY DESCENT", size=12, bold=True, color=POS))
    parts.append(mtext(390, 300, "Критичний розряд АКБ\nВтрата супутників GNSS\nКонтрольований спуск 1.5 м/с", size=9, color=INK, lh=1.2))

    # Стан 5: TERMINATE / PARACHUTE (Аварійне глушіння)
    parts.append(rect(580, 250, 200, 85, fill="#2b0000", stroke=POS, sw=2, rx=8))
    parts.append(text(680, 278, "5. CRITICAL TERMINATE", size=12, bold=True, color="#ffffff"))
    parts.append(mtext(680, 300, "Кут крену > 75 град\nЗрив синхронізації мотора\nВикид парашута + Disarm", size=9, color="#fdecea", lh=1.2))

    # Переходи (стрілки з умовами)
    # 1 -> 2
    parts.append(arrow(200, 120, 290, 120, color="#d97706", sw=1.8))
    parts.append(text(245, 110, "Збій сенсора", size=9, color="#d97706"))

    # 1 -> 3
    parts.append(arrow(180, 90, 580, 90, color=NEG, sw=1.8))
    parts.append(text(380, 80, "Втрата зв'язку (RC Lost)", size=9.5, bold=True, color=NEG))

    # 2 -> 3
    parts.append(arrow(490, 130, 580, 130, color=NEG, sw=1.8))
    parts.append(text(535, 120, "GPS OK", size=9, color=NEG))

    # 3 -> 4
    parts.append(arrow(680, 170, 490, 260, color=POS, sw=1.8))
    parts.append(text(615, 215, "Низький заряд АКБ", size=9, color=POS))

    # 2 -> 4
    parts.append(arrow(390, 170, 390, 250, color=POS, sw=1.8))
    parts.append(text(400, 210, "Втрата навігації", size=9, color=POS, anchor="start"))

    # 4 -> 5
    parts.append(arrow(490, 292, 580, 292, color=POS, sw=2))
    parts.append(text(535, 282, "Перекидання", size=9, bold=True, color=POS))

    # 1 -> 5 (екстрена)
    parts.append(arrow(120, 170, 580, 310, color=POS, sw=1.8))
    parts.append(text(220, 255, "Зрив гвинта / Desync ESC", size=9, bold=True, color=POS))

    render(os.path.join(IMG, "failsafe-state-machine.svg"), W, H, *parts,
           title="Граф переходів автомата аварійного захисту польотного контролера")


if __name__ == "__main__":
    fig_failure_taxonomy()
    fig_imu_clipping()
    fig_i2c_bus_lockup()
    fig_failsafe_fsm()
    print("OK: 4 figures ->", IMG)

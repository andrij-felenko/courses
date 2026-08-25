# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми HVDC Transmission."""
import os
import sys

# 4 рівні вгору до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_breakeven():
    """1. Вартість передачі енергії залежно від відстані: HVAC проти HVDC."""
    w, h = 820, 480
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Осі координат
    ox, oy = 90, 410
    axis_w, axis_h = 680, 340
    frags.append(line(ox, oy, ox + axis_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - axis_h, color=LINE, sw=2))
    frags.append(arrow(ox + axis_w - 5, oy, ox + axis_w + 15, oy, color=LINE, sw=2))
    frags.append(arrow(ox, oy - axis_h + 5, ox, oy - axis_h - 15, color=LINE, sw=2))

    frags.append(text(ox + axis_w, oy + 28, "Відстань передачі (км)", size=13, bold=True, anchor="end"))
    frags.append(text(ox - 15, oy - axis_h, "Сумарні витрати (CAPEX + втрати)", size=13, bold=True, anchor="end"))

    # Сітка та позначки відстані
    points_x = [(0, "0"), (120, "50 (кабель)"), (260, "400"), (420, "800 (ЛЕП)"), (580, "1500"), (660, "2000")]
    for px, label in points_x:
        x = ox + px
        frags.append(line(x, oy, x, oy + 6, color=MUTED, sw=1.2))
        frags.append(text(x, oy + 20, label, size=11, color=MUTED, anchor="middle"))
        if px > 0:
            frags.append(line(x, oy, x, oy - axis_h + 20, color="#eef1f4", sw=1, dash="4,4"))

    # Позначки осі Y
    frags.append(text(ox - 10, oy - 40, "Низькі", size=11, color=MUTED, anchor="end"))
    frags.append(text(ox - 10, oy - 180, "Середні", size=11, color=MUTED, anchor="end"))
    frags.append(text(ox - 10, oy - 300, "Високі", size=11, color=MUTED, anchor="end"))

    # --- Крива HVAC ЛЕП (змінний струм, повітряна) ---
    frags.append(line(ox, oy - 50, ox + 650, oy - 340, color=POS, sw=2.8))
    frags.append(textbox(ox + 520, oy - 295, "HVAC (повітряна ЛЕП)", size=12, pad=6, fill="#fdecea", stroke=POS, color=POS, bold=True)[0])

    # --- Крива HVDC ЛЕП (постійний струм, повітряна) ---
    frags.append(line(ox, oy - 170, ox + 650, oy - 275, color=NEG, sw=2.8))
    frags.append(textbox(ox + 550, oy - 240, "HVDC (повітряна ЛЕП)", size=12, pad=6, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)[0])

    # Точка рівноваги ЛЕП
    b_x, b_y = ox + 420, oy - 237
    frags.append(circle(b_x, b_y, 6, fill=FIELD, stroke="#1b7e43", sw=2))
    frags.append(line(b_x, b_y, b_x, oy, color=FIELD, sw=1.5, dash="4,3"))
    frags.append(textbox(b_x - 40, b_y - 38, "Рівновага ЛЕП: 600–800 км\nДалі HVDC дешевший", size=11, pad=5, fill="#edf7ed", stroke=FIELD, color="#1b7e43", bold=True)[0])

    # --- Крива HVAC підводний кабель ---
    frags.append(line(ox, oy - 60, ox + 220, oy - 350, color="#d35400", sw=2.5, dash="6,3"))
    frags.append(textbox(ox + 160, oy - 335, "HVAC (кабель)", size=11, pad=4, fill="#fef5e7", stroke="#d35400", color="#d35400", bold=True)[0])

    # --- Крива HVDC підводний кабель ---
    frags.append(line(ox, oy - 160, ox + 320, oy - 240, color="#2980b9", sw=2.5, dash="6,3"))
    frags.append(textbox(ox + 310, oy - 250, "HVDC (кабель)", size=11, pad=4, fill="#ebf5fb", stroke="#2980b9", color="#2980b9", bold=True)[0])

    # Точка рівноваги кабелю
    c_x, c_y = ox + 120, oy - 190
    frags.append(circle(c_x, c_y, 6, fill="#e67e22", stroke="#b95e00", sw=2))
    frags.append(line(c_x, c_y, c_x, oy, color="#e67e22", sw=1.5, dash="4,3"))
    frags.append(textbox(c_x + 55, c_y - 50, "Рівновага кабелю: ~40–50 км\n(морські вітропарки)", size=10, pad=4, fill="#fef9e7", stroke="#e67e22", color="#b95e00", bold=True)[0])

    return render(os.path.join(IMG_DIR, "hvdc-vs-hvac-breakeven.svg"), w, h, *frags)


def fig_skin_and_charging():
    """2. Фізичне порівняння перерізу кабелю: скін-ефект і зарядні струми в AC проти рівномірного струму в DC."""
    w, h = 820, 420
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # --- Ліва половина: Змінний струм (HVAC) ---
    frags.append(rect(35, 30, 360, 360, fill="#fcf8f8", stroke="#e0b4b4", sw=1.2, rx=6))
    frags.append(text(215, 58, "Змінний струм (HVAC: 50 Гц)", size=15, bold=True, color=POS))

    # Переріз жили кабелю HVAC
    cx1, cy1 = 215, 155
    # Зовнішня ізоляція та екран
    frags.append(circle(cx1, cy1, 80, fill="#eaeded", stroke="#95a5a6", sw=1.5))
    frags.append(circle(cx1, cy1, 60, fill="#f9ebea", stroke="#c0392b", sw=2))
    # Скін-шар
    frags.append(circle(cx1, cy1, 40, fill="#fcf3cf", stroke="#f39c12", sw=1.2))
    frags.append(circle(cx1, cy1, 20, fill="#fdfefe", stroke="#bdc3c7", sw=1))

    frags.append(text(cx1, cy1 - 47, "Висока густина струму", size=10, color=POS, bold=True))
    frags.append(text(cx1, cy1 + 2, "Струм витіснено", size=9.5, color=MUTED))
    frags.append(text(cx1, cy1 + 14, "на поверхню (δ ≈ 9 мм)", size=9.5, color=MUTED))

    # Радіальні стрілки зарядного струму
    frags.append(arrow(cx1 + 60, cy1, cx1 + 78, cy1, color=POS, sw=1.5))
    frags.append(arrow(cx1 - 60, cy1, cx1 - 78, cy1, color=POS, sw=1.5))
    frags.append(arrow(cx1, cy1 + 60, cx1, cy1 + 78, color=POS, sw=1.5))
    frags.append(arrow(cx1, cy1 - 60, cx1, cy1 - 78, color=POS, sw=1.5))

    # Текстові пояснення для AC
    frags.append(textbox(215, 270, "1. Скін-ефект: центр недовантажений\n   Ефективний опір R_ac > R_dc на 15–30%", size=10, pad=4, fill="#ffffff", stroke="#d0d7de")[0])
    frags.append(textbox(215, 335, "2. Зарядний струм: Ic = ω·C·V\n   На 50–80 км струм заряду\n   з'їдає 100% ліміту кабелю", size=10, pad=4, fill="#ffffff", stroke=POS, color=POS)[0])

    # --- Права половина: Постійний струм (HVDC) ---
    frags.append(rect(425, 30, 360, 360, fill="#f5f9fc", stroke="#b4cde0", sw=1.2, rx=6))
    frags.append(text(605, 58, "Постійний струм (HVDC: 0 Гц)", size=15, bold=True, color=NEG))

    # Переріз жили кабелю HVDC
    cx2, cy2 = 605, 155
    frags.append(circle(cx2, cy2, 80, fill="#eaeded", stroke="#95a5a6", sw=1.5))
    frags.append(circle(cx2, cy2, 60, fill="#d4e6f1", stroke=NEG, sw=2))

    frags.append(text(cx2, cy2 - 18, "100% перерізу", size=11, color=NEG, bold=True))
    frags.append(text(cx2, cy2 - 2, "рівномірна густина струму", size=10, color=NEG))
    frags.append(text(cx2, cy2 + 14, "J = I / S = const", size=10, bold=True, color=INK))

    # Текстові пояснення для DC
    frags.append(textbox(605, 270, "1. Немає скін-ефекту: метал працює повністю\n   Мінімальний активний опір R_dc", size=10, pad=4, fill="#ffffff", stroke="#d0d7de")[0])
    frags.append(textbox(605, 335, "2. Немає реактивного струму: ω = 0 → Ic = 0\n   Увесь тепловий ліміт кабелю\n   віддано корисній потужності", size=10, pad=4, fill="#ffffff", stroke=FIELD, color="#1b7e43", bold=True)[0])

    return render(os.path.join(IMG_DIR, "skin-and-charging-current.svg"), w, h, *frags)


def fig_lcc_12_pulse():
    """3. 12-пульсний тиристорний перетворювач LCC (Line-Commutated Converter)."""
    w, h = 820, 460
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 42, "12-пульсний тиристорний перетворювач LCC (схема Гретца зі зсувом фаз 30°)", size=15, bold=True))

    # Вхідна трифазна мережа AC
    frags.append(textbox(80, 220, "Трифазна\nмережа AC\n(50/60 Гц)", size=12, pad=6, fill="#f4f6f8", stroke=LINE, bold=True)[0])

    # Трансформатори: верхній Y-Y (0°), нижній Y-Δ (30°)
    frags.append(line(135, 190, 190, 150, color=LINE, sw=1.8))
    frags.append(line(135, 250, 190, 290, color=LINE, sw=1.8))

    # Блок трансформатора Y-Y
    frags.append(rect(190, 115, 150, 70, fill="#edf7ed", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(265, 142, "Трансформатор Y-Y", size=12, bold=True, color="#1b7e43"))
    frags.append(text(265, 162, "Зсув фази: 0°", size=11, color=MUTED))

    # Блок трансформатора Y-Δ
    frags.append(rect(190, 255, 150, 70, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=6))
    frags.append(text(265, 282, "Трансформатор Y-Δ", size=12, bold=True, color="#9a7d0a"))
    frags.append(text(265, 302, "Зсув фази: 30° (π/6)", size=11, color=MUTED))

    # Лінії до мостів
    frags.append(arrow(340, 150, 390, 150, color=LINE, sw=1.8))
    frags.append(arrow(340, 290, 390, 290, color=LINE, sw=1.8))

    # Верхній 6-пульсний міст
    frags.append(rect(390, 100, 170, 100, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(475, 130, "6-пульсний міст 1", size=13, bold=True, color=POS))
    frags.append(text(475, 152, "6 тиристорних вентилів", size=11, color=MUTED))
    frags.append(text(475, 172, "Гармоніки AC: 5, 7, 11, 13...", size=10, color=INK))

    # Нижній 6-пульсний міст
    frags.append(rect(390, 240, 170, 100, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(475, 270, "6-пульсний міст 2", size=13, bold=True, color=POS))
    frags.append(text(475, 292, "6 тиристорних вентилів", size=11, color=MUTED))
    frags.append(text(475, 312, "Гармоніки AC: 5, 7, 11, 13...", size=10, color=INK))

    # Послідовне з'єднання на стороні DC
    frags.append(line(560, 130, 620, 130, color=POS, sw=2.5))
    frags.append(line(560, 170, 585, 170, color=LINE, sw=2))
    frags.append(line(585, 170, 585, 270, color=LINE, sw=2))
    frags.append(line(585, 270, 560, 270, color=LINE, sw=2))
    frags.append(line(560, 310, 620, 310, color=NEG, sw=2.5))

    # Згладжувальний реактор
    frags.append(rect(620, 115, 60, 30, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(650, 135, "L_dc", size=12, bold=True))
    frags.append(arrow(680, 130, 750, 130, color=POS, sw=2.5))
    frags.append(text(765, 134, "+V_dc", size=13, bold=True, color=POS))

    frags.append(arrow(620, 310, 750, 310, color=NEG, sw=2.5))
    frags.append(text(765, 314, "−V_dc", size=13, bold=True, color=NEG))

    # Пояснювальний банер гармонік
    frags.append(textbox(410, 400, "Взаємне придушення гармонік завдяки 30° зсуву:\n5-та і 7-ма гармоніки в AC-мережі та 6-та пульсація в DC взаємно віднімаються (12k ± 1).\nЗалишаються лише вищі гармоніки: 11-та, 13-та, 23-тя, 25-та... (потрібні менші фільтри).", size=11, pad=6, fill="#f5f9fc", stroke=NEG, color=INK)[0])

    return render(os.path.join(IMG_DIR, "lcc-12-pulse-bridge.svg"), w, h, *frags)


def fig_mmc_architecture():
    """4. Модульний багаторівневий перетворювач MMC (Modular Multilevel Converter)."""
    w, h = 820, 480
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 42, "Модульний багаторівневий перетворювач VSC-MMC (Modular Multilevel Converter)", size=15, bold=True))

    # --- Ліва панель: Фазна стійка перетворювача ---
    frags.append(rect(35, 65, 260, 380, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(165, 88, "Фазна стійка (Phase Leg)", size=13, bold=True, color=INK))

    # Шина +V_dc / 2
    frags.append(line(50, 110, 280, 110, color=POS, sw=2.5))
    frags.append(text(250, 104, "+V_dc / 2", size=11, bold=True, color=POS))

    # Верхнє плече: субмодулі SM1..SMn
    frags.append(textbox(165, 140, "Субмодуль SM 1", size=11, pad=4, fill="#ffffff", stroke=NEG)[0])
    frags.append(text(165, 168, "⋮ (N субмодулів)", size=11, color=MUTED))
    frags.append(textbox(165, 195, "Субмодуль SM N", size=11, pad=4, fill="#ffffff", stroke=NEG)[0])

    # Реактор верхнього плеча
    frags.append(rect(145, 220, 40, 20, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=3))
    frags.append(text(165, 234, "L_arm", size=10, bold=True))

    # Вивід фази AC
    frags.append(circle(165, 255, 5, fill="#f39c12", stroke="#b9770e", sw=2))
    frags.append(line(165, 255, 310, 255, color="#f39c12", sw=2.5))
    frags.append(text(285, 248, "Фаза AC", size=11, bold=True, color="#b9770e"))

    # Реактор нижнього плеча
    frags.append(rect(145, 275, 40, 20, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=3))
    frags.append(text(165, 289, "L_arm", size=10, bold=True))

    # Нижнє плече: субмодулі SM1..SMn
    frags.append(textbox(165, 320, "Субмодуль SM 1", size=11, pad=4, fill="#ffffff", stroke=NEG)[0])
    frags.append(text(165, 348, "⋮ (N субмодулів)", size=11, color=MUTED))
    frags.append(textbox(165, 375, "Субмодуль SM N", size=11, pad=4, fill="#ffffff", stroke=NEG)[0])

    # Шина −V_dc / 2
    frags.append(line(50, 410, 280, 410, color=NEG, sw=2.5))
    frags.append(text(250, 425, "−V_dc / 2", size=11, bold=True, color=NEG))

    # --- Середня панель: Внутрішня будова напівмостового субмодуля ---
    frags.append(rect(315, 65, 240, 380, fill="#edf7ed", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(435, 88, "Напівмостовий субмодуль (SM)", size=12, bold=True, color="#1b7e43"))

    # Конденсатор C_sm
    frags.append(line(360, 140, 360, 240, color=LINE, sw=1.8))
    frags.append(line(350, 185, 370, 185, color=LINE, sw=2.5))
    frags.append(line(350, 195, 370, 195, color=LINE, sw=2.5))
    frags.append(text(338, 193, "C_sm", size=11, bold=True))

    # Верхній IGBT T1
    frags.append(rect(400, 125, 60, 35, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    frags.append(text(430, 147, "T1 (IGBT)", size=10, bold=True, color=POS))
    # Нижній IGBT T2
    frags.append(rect(400, 220, 60, 35, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(430, 242, "T2 (IGBT)", size=10, bold=True, color=NEG))

    frags.append(line(360, 140, 400, 140, color=LINE, sw=1.5))
    frags.append(line(460, 140, 490, 140, color=LINE, sw=1.5))
    frags.append(line(490, 140, 490, 220, color=LINE, sw=1.5))
    frags.append(line(360, 240, 400, 240, color=LINE, sw=1.5))
    frags.append(line(460, 240, 520, 240, color=LINE, sw=1.5))

    # Виводи субмодуля
    frags.append(circle(490, 180, 4, fill=FIELD, stroke="#1b7e43", sw=1.5))
    frags.append(circle(520, 240, 4, fill=FIELD, stroke="#1b7e43", sw=1.5))

    # Стани субмодуля
    frags.append(textbox(435, 310, "Стан 1 (Увімкнено):\nT1 ВКЛ, T2 ВИКЛ → V_sm = V_c\n(конденсатор підключено)", size=10, pad=4, fill="#ffffff", stroke=FIELD)[0])
    frags.append(textbox(435, 375, "Стан 2 (Байпас):\nT1 ВИКЛ, T2 ВКЛ → V_sm = 0\n(струм оминає ємність)", size=10, pad=4, fill="#ffffff", stroke=MUTED)[0])

    # --- Права панель: Синтез ступінчастої синусоїди ---
    frags.append(rect(575, 65, 210, 380, fill="#fef9e7", stroke="#d4ac0d", sw=1.2, rx=6))
    frags.append(text(680, 88, "Синтез напруги AC", size=12, bold=True, color="#9a7d0a"))

    # Осі графіка напруги
    gx, gy = 600, 240
    frags.append(line(gx, gy, gx + 165, gy, color=MUTED, sw=1.2))
    frags.append(line(gx + 10, gy - 100, gx + 10, gy + 100, color=MUTED, sw=1.2))

    # Сходинки напруги (N рівнів)
    steps = [
        (10, 0), (22, -25), (35, -55), (50, -80), (68, -95), (85, -95),
        (102, -80), (118, -55), (130, -25), (142, 0), (152, 25), (160, 55)
    ]
    for i in range(len(steps) - 1):
        x1, y1 = gx + steps[i][0], gy + steps[i][1]
        x2, y2 = gx + steps[i+1][0], gy + steps[i+1][1]
        frags.append(line(x1, y1, x2, y1, color=POS, sw=2))
        frags.append(line(x2, y1, x2, y2, color=POS, sw=1.2))

    frags.append(textbox(680, 350, "Сотні рівнів напруги (N > 200):\nФорма настільки близька\nдо чистої синусоїди,\nщо масивні фільтри гармонік\nНЕ ПОТРІБНІ взагалі.", size=10, pad=5, fill="#ffffff", stroke="#d4ac0d", color=INK)[0])

    return render(os.path.join(IMG_DIR, "mmc-submodule-chain.svg"), w, h, *frags)


def fig_hybrid_breaker():
    """5. Гібридний вимикач постійного струму HVDC (Hybrid DC Circuit Breaker)."""
    w, h = 820, 460
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 42, "Гібридний HVDC-вимикач: бездугове розмикання постійного струму за 2–3 мс", size=15, bold=True))

    # Вхідний і вихідний полюс DC
    frags.append(circle(65, 230, 7, fill=POS, stroke="#922b21", sw=2))
    frags.append(text(65, 208, "DC Вхід", size=12, bold=True, color=POS))
    frags.append(line(72, 230, 130, 230, color=POS, sw=2.5))

    frags.append(circle(755, 230, 7, fill=POS, stroke="#922b21", sw=2))
    frags.append(text(755, 208, "DC Вихід", size=12, bold=True, color=POS))
    frags.append(line(690, 230, 748, 230, color=POS, sw=2.5))

    # Розгалуження на 3 паралельні гілки
    frags.append(line(130, 120, 130, 340, color=LINE, sw=2))
    frags.append(line(690, 120, 690, 340, color=LINE, sw=2))

    # --- 1. Головна гілка нормального струму (вгорі) ---
    frags.append(line(130, 120, 170, 120, color=FIELD, sw=2.5))
    frags.append(line(650, 120, 690, 120, color=FIELD, sw=2.5))

    frags.append(rect(170, 95, 220, 50, fill="#edf7ed", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(280, 118, "Швидкий механічний роз'єднувач", size=11, bold=True, color="#1b7e43"))
    frags.append(text(280, 134, "(UFD — надшвидкий привід, <2 мс)", size=10, color=MUTED))

    frags.append(line(390, 120, 430, 120, color=FIELD, sw=2))

    frags.append(rect(430, 95, 220, 50, fill="#edf7ed", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(540, 118, "Комутаційний перемикач навантаження", size=11, bold=True, color="#1b7e43"))
    frags.append(text(540, 134, "(LCS — низьковольтні IGBT, втрати <0.01%)", size=10, color=MUTED))

    # --- 2. Головна переривальна гілка (посередині) ---
    frags.append(line(130, 230, 220, 230, color=POS, sw=2))
    frags.append(line(600, 230, 690, 230, color=POS, sw=2))

    frags.append(rect(220, 205, 380, 50, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(410, 228, "Головний напівпровідниковий вимикач (Main Breaker)", size=12, bold=True, color=POS))
    frags.append(text(410, 245, "Стек послідовних високовольтних IGBT-модулів (вимикання струму КЗ)", size=10, color=MUTED))

    # --- 3. Гілка поглинання енергії (внизу) ---
    frags.append(line(130, 340, 250, 340, color="#d35400", sw=2))
    frags.append(line(570, 340, 690, 340, color="#d35400", sw=2))

    frags.append(rect(250, 315, 320, 50, fill="#fef5e7", stroke="#d35400", sw=1.5, rx=6))
    frags.append(text(410, 338, "Блок варисторів (MOV / ОПН)", size=12, bold=True, color="#d35400"))
    frags.append(text(410, 355, "Поглинання магнітної енергії індуктивності лінії: W = ½·L·I²", size=10, color=MUTED))

    # Часова послідовність (внизу)
    frags.append(textbox(410, 415, "Послідовність спрацьовування: (1) LCS закривається → струм перекидається в IGBT Main Breaker;\n(2) Механічний UFD розмикається без струму (без дуги!); (3) IGBT вимикаються → індуктивний струм гаситься у варисторах MOV.", size=10, pad=5, fill="#f4f6f8", stroke="#cbd5e1")[0])

    return render(os.path.join(IMG_DIR, "hybrid-dc-breaker.svg"), w, h, *frags)


def main():
    fig_breakeven()
    fig_skin_and_charging()
    fig_lcc_12_pulse()
    fig_mmc_architecture()
    fig_hybrid_breaker()
    print("All 5 figures generated successfully.")


if __name__ == "__main__":
    main()

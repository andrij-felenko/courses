# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми onovlennia-i-batareia."""

import sys
import os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від root/course/embedded/onovlennia-i-batareia)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_ota_power_phases():
    """Фігура 1: Енергетичний та струмовий профіль чотирьох фаз OTA-процесу."""
    w, h = 820, 360
    frags = []

    # Заголовок осі струму та часу
    frags.append(line(70, 270, 780, 270, color=LINE, sw=1.5)) # Вісь X (час)
    frags.append(line(70, 270, 70, 40, color=LINE, sw=1.5))   # Вісь Y (струм, мА)

    # Стрілки осей
    frags.append(arrow(770, 270, 785, 270, color=LINE, sw=1.5))
    frags.append(arrow(70, 50, 70, 35, color=LINE, sw=1.5))

    frags.append(text(785, 290, "Час (t)", size=12, color=INK, anchor="end", italic=True))
    frags.append(text(75, 30, "Струм I (мА)", size=12, color=INK, anchor="start", bold=True))

    # Позначки шкали Y
    y_200 = 70
    y_100 = 150
    y_40  = 210
    y_0   = 270

    frags.append(line(65, y_200, 70, y_200, color=MUTED, sw=1.0))
    frags.append(line(65, y_100, 70, y_100, color=MUTED, sw=1.0))
    frags.append(line(65, y_40, 70, y_40, color=MUTED, sw=1.0))

    frags.append(text(60, y_200 + 4, "200 мА", size=11, color=MUTED, anchor="end"))
    frags.append(text(60, y_100 + 4, "100 мА", size=11, color=MUTED, anchor="end"))
    frags.append(text(60, y_40 + 4, "40 мА", size=11, color=MUTED, anchor="end"))
    frags.append(text(60, y_0 + 4, "0 мА", size=11, color=MUTED, anchor="end"))

    # Сітка допоміжна (пунктир)
    frags.append(line(70, y_200, 770, y_200, color="#e5e7eb", sw=1.0, dash="3,3"))
    frags.append(line(70, y_100, 770, y_100, color="#e5e7eb", sw=1.0, dash="3,3"))
    frags.append(line(70, y_40, 770, y_40, color="#e5e7eb", sw=1.0, dash="3,3"))

    # Фаза 1: Прийом по радіо (Wi-Fi / BLE / Cellular)
    p1 = rect(80, 90, 190, 180, fill="#fef2f2", stroke="#f87171", sw=1.2, rx=4)
    frags.append(p1)
    frags.append(text(175, 115, "1. Завантаження (Радіо RX/TX)", size=12, color=POS, bold=True))
    frags.append(text(175, 135, "120–200 мА (тривалість 15–90 с)", size=11, color=MUTED))
    frags.append(text(175, 155, "Пакетний прийом + ACK", size=11, color=INK))

    # Фаза 2: Криптографічна валідація (SHA-256 + Ed25519)
    p2 = rect(280, 180, 140, 90, fill="#f0fdf4", stroke="#4ade80", sw=1.2, rx=4)
    frags.append(p2)
    frags.append(text(350, 205, "2. Валідація", size=12, color=FIELD, bold=True))
    frags.append(text(350, 225, "CPU 100% (50–70 мА)", size=11, color=MUTED))
    frags.append(text(350, 245, "SHA-256 + Підпис (1–3 с)", size=10, color=INK))

    # Фаза 3: Секторне стирання та запис Flash
    p3 = rect(430, 140, 200, 130, fill="#eff6ff", stroke="#60a5fa", sw=1.2, rx=4)
    frags.append(p3)
    frags.append(text(530, 165, "3. Запис у Flash-пам'ять", size=12, color=NEG, bold=True))
    frags.append(text(530, 185, "Помпа заряду: піки до 90 мА", size=11, color=POS, bold=True))
    frags.append(text(530, 205, "Стирання блоків (10–45 с)", size=11, color=INK))
    frags.append(text(530, 225, "Найвища небезпека brownout", size=10, color=POS))

    # Фаза 4: Перезапуск та перевірка успіху
    p4 = rect(640, 210, 120, 60, fill="#fefce8", stroke="#facc15", sw=1.2, rx=4)
    frags.append(p4)
    frags.append(text(700, 230, "4. Стрибок Boot", size=12, color="#854d0e", bold=True))
    frags.append(text(700, 248, "Рестарт і верифікація", size=10, color=MUTED))

    # Підписи часу під віссю X
    frags.append(text(175, 310, "Енергія сесії: 60–80%", size=11, color=POS, bold=True))
    frags.append(text(350, 310, "Енергія: 3–5%", size=11, color=FIELD))
    frags.append(text(530, 310, "Енергія: 15–30%", size=11, color=NEG, bold=True))
    frags.append(text(700, 310, "Енергія: < 2%", size=11, color="#854d0e"))

    render(os.path.join(OUT, "ota-power-phases.svg"), w, h, *frags)


def fig_battery_sag_brownout():
    """Фігура 2: Просідання напруги батареї на морозі під час сплесків струму проти порогу BOR."""
    w, h = 820, 370
    frags = []

    # Осі
    frags.append(line(80, 290, 780, 290, color=LINE, sw=1.5)) # X: Профіль навантаження в часі
    frags.append(line(80, 290, 80, 40, color=LINE, sw=1.5))   # Y: Напруга на клемах V_term (В)

    frags.append(arrow(770, 290, 785, 290, color=LINE, sw=1.5))
    frags.append(arrow(80, 50, 80, 35, color=LINE, sw=1.5))

    frags.append(text(785, 310, "Час оновлення (t)", size=12, color=INK, anchor="end", italic=True))
    frags.append(text(75, 30, "Напруга шини живлення (В)", size=12, color=INK, anchor="start", bold=True))

    # Рівні напруги
    y_40 = 60   # 4.0 В
    y_36 = 105  # 3.65 В (OCV батареї у спокої)
    y_30 = 175  # 3.0 В
    y_27 = 210  # 2.7 В (Поріг Brownout Reset / Flash Min)
    y_24 = 250  # 2.4 В (Зона колапсу процесора)

    frags.append(line(75, y_40, 80, y_40, color=MUTED, sw=1.0))
    frags.append(line(75, y_36, 80, y_36, color=MUTED, sw=1.0))
    frags.append(line(75, y_30, 80, y_30, color=MUTED, sw=1.0))
    frags.append(line(75, y_27, 80, y_27, color=POS, sw=1.5))
    frags.append(line(75, y_24, 80, y_24, color=MUTED, sw=1.0))

    frags.append(text(70, y_40 + 4, "4.0 В", size=11, color=MUTED, anchor="end"))
    frags.append(text(70, y_36 + 4, "3.65 В", size=11, color=INK, anchor="end", bold=True))
    frags.append(text(70, y_30 + 4, "3.0 В", size=11, color=MUTED, anchor="end"))
    frags.append(text(70, y_27 + 4, "2.7 В", size=11, color=POS, anchor="end", bold=True))
    frags.append(text(70, y_24 + 4, "2.4 В", size=11, color=MUTED, anchor="end"))

    # Лінія порогу Brownout Reset
    frags.append(line(80, y_27, 770, y_27, color=POS, sw=1.5, dash="5,4"))
    frags.append(text(765, y_27 - 6, "Поріг аварійного скидання (BOR) та збою помпи Flash: 2.70 В", size=11, color=POS, anchor="end", bold=True))

    # Зона аварії нижче 2.7 В
    frags.append(rect(81, y_27, 690, 290 - y_27, fill="#fee2e2", stroke="none"))
    frags.append(text(420, 270, "ЗОНА АВАРІЙНОГО ПЕРЕЗАПУСКУ ТА ПОШКОДЖЕННЯ FLASH (TORN WRITE)", size=11, color=POS, bold=True))

    # Крива 1: Тепла нова батарея (+25°C, R_esr = 80 мОм)
    curve_warm = ('<path d="M 80,105 L 140,105 L 150,135 L 340,135 L 350,120 L 450,120 L 460,130 '
                  'L 620,130 L 630,105 L 750,105" fill="none" stroke="%s" stroke-width="2.5"/>' % FIELD)
    frags.append(curve_warm)
    frags.append(text(240, 115, "Тепла нова батарея (+25°C, R_esr = 80 мОм)", size=11, color=FIELD, bold=True))

    # Крива 2: Холодна або зношена батарея (0°C, R_esr = 480 мОм)
    curve_cold = ('<path d="M 80,105 L 140,105 L 150,225 L 340,225 L 350,185 L 450,185 L 460,235 '
                  'L 540,235 L 545,280 L 560,280 L 570,105 L 750,105" fill="none" stroke="%s" stroke-width="2.5"/>' % POS)
    frags.append(curve_cold)
    frags.append(text(240, 245, "Холодна зношена батарея (0°C, R_esr = 480 мОм)", size=11, color=POS, bold=True))

    # Точка аварії
    frags.append(circle(545, 235, 5, fill=POS, stroke=INK, sw=1.5))
    frags.append(arrow(545, 185, 545, 225, color=POS, sw=1.5))
    frags.append(text(545, 175, "Brownout під час запису Flash!", size=11, color=POS, bold=True))

    # Пояснення просідання Delta V = I * R_esr
    box_calc, _, _ = textbox(660, 80, "ΔU = I_пік · R_esr\n0.2 А · 0.48 Ом = 0.96 В\n3.65 В − 0.96 В = 2.69 В < BOR", size=11, pad=6, fill="#ffffff", stroke=POS)
    frags.append(box_calc)

    render(os.path.join(OUT, "battery-sag-brownout.svg"), w, h, *frags)


def fig_safety_decision_matrix():
    """Фігура 3: Багаторівневий автомат ухвалення рішення про допуск до OTA."""
    w, h = 820, 380
    frags = []

    # Блок 1: Старт перевірки
    b1 = fitbox(30, 160, 110, 60, "Запит на OTA\n(Нова версія)", size=12, fill="#f3f4f6", stroke=INK, bold=True)
    frags.append(b1)
    frags.append(arrow(140, 190, 170, 190))

    # Перевірка 1: Зовнішнє живлення (External Power)
    b_pwr = fitbox(170, 150, 130, 80, "1. Зовнішнє\nживлення?\n(USB / Зарядка)", size=11, fill="#eff6ff", stroke=NEG, bold=True)
    frags.append(b_pwr)

    # Гілка ТАК від живлення -> Прямий старт
    frags.append(arrow(235, 150, 235, 60))
    frags.append(text(245, 105, "ТАК", size=11, color=FIELD, bold=True))
    b_go_pwr = fitbox(190, 20, 190, 40, "СТАРТ: Живлення від мережі", size=11, fill="#dcfce7", stroke=FIELD, bold=True)
    frags.append(b_go_pwr)

    # Гілка НІ від живлення -> Перевірка 2: Температура
    frags.append(arrow(300, 190, 330, 190))
    frags.append(text(315, 180, "НІ", size=10, color=MUTED))

    # Перевірка 2: Температурне вікно (+5..+45°C)
    b_temp = fitbox(330, 150, 130, 80, "2. Температура\n+5°C ≤ T ≤ +45°C?\n(Термістор NTC)", size=11, fill="#fefce8", stroke="#ca8a04", bold=True)
    frags.append(b_temp)

    # Гілка НІ від температури -> Відкласти
    frags.append(arrow(395, 230, 395, 300))
    frags.append(text(405, 265, "НІ", size=11, color=POS, bold=True))
    b_hold_temp = fitbox(320, 300, 150, 50, "ВІДКЛАСТИ:\nХолод / Перегрів (R_esr)", size=11, fill="#fee2e2", stroke=POS, bold=True)
    frags.append(b_hold_temp)

    # Гілка ТАК від температури -> Перевірка 3: Стан заряду SoC
    frags.append(arrow(460, 190, 490, 190))
    frags.append(text(475, 180, "ТАК", size=10, color=FIELD))

    # Перевірка 3: Стан заряду (SoC >= 45%)
    b_soc = fitbox(490, 150, 130, 80, "3. Заряд батареї\nSoC ≥ 45–50%?\n(Fuel Gauge / OCV)", size=11, fill="#f0fdf4", stroke=FIELD, bold=True)
    frags.append(b_soc)

    # Гілка НІ від SoC -> Відхилити / Чекати зарядки
    frags.append(arrow(555, 230, 555, 300))
    frags.append(text(565, 265, "НІ", size=11, color=POS, bold=True))
    b_hold_soc = fitbox(490, 300, 130, 50, "ВІДХИЛИТИ:\nБрак енергії на OTA", size=11, fill="#fee2e2", stroke=POS, bold=True)
    frags.append(b_hold_soc)

    # Гілка ТАК від SoC -> Перевірка 4: Динамічний імпульсний тест
    frags.append(arrow(620, 190, 650, 190))
    frags.append(text(635, 180, "ТАК", size=10, color=FIELD))

    # Перевірка 4: Імпульсний стрес-тест просідання
    b_stress = fitbox(650, 150, 130, 80, "4. Імпульсний тест\nΔU_тест ≤ ΔU_макс?\n(Оцінка R_esr під струмом)", size=10, fill="#faf5ff", stroke="#9333ea", bold=True)
    frags.append(b_stress)

    # Гілка НІ від тесту -> Відхилити
    frags.append(arrow(715, 230, 715, 300))
    frags.append(text(725, 265, "НІ", size=11, color=POS, bold=True))
    b_fail_stress = fitbox(650, 300, 130, 50, "БЛОКУВАТИ:\nВисокий опір комірки", size=11, fill="#fee2e2", stroke=POS, bold=True)
    frags.append(b_fail_stress)

    # Гілка ТАК від тесту -> ДОЗВІЛ
    frags.append(arrow(715, 150, 715, 60))
    frags.append(text(725, 105, "ТАК", size=11, color=FIELD, bold=True))
    b_go_bat = fitbox(620, 20, 180, 40, "СТАРТ: Безпечно на батареї", size=11, fill="#dcfce7", stroke=FIELD, bold=True)
    frags.append(b_go_bat)

    render(os.path.join(OUT, "safety-decision-matrix.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_ota_power_phases()
    fig_battery_sag_brownout()
    fig_safety_decision_matrix()
    print("All figures generated successfully.")

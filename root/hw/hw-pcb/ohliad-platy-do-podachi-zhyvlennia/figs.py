# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Огляд плати до подачі живлення: мікроскоп, дзвінок рейок на КЗ'."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig1_microscope_inspection():
    """Фігура 1: Карта ключових точок мікроскопічної інспекції плати."""
    w, h = 980, 620
    frags = []

    # Заголовок секції А: Орієнтація полярних компонентів
    box_a = fitbox(20, 20, 460, 580, "", fill="#fbfcfd", stroke="#d0d7de", sw=1.5)
    frags.append(box_a)
    frags.append(text(250, 48, "Орієнтація полярних компонентів", size=16, bold=True, color=INK))

    # 1. Мікросхема (Pin 1 IC)
    frags.append(rect(40, 70, 420, 115, fill="#ffffff", stroke="#e1e4e8", rx=6))
    frags.append(text(55, 92, "1. Ключ виводу 1 мікросхеми (Pin 1 IC)", size=13, bold=True, color=INK, anchor="start"))
    # Корпус QFP
    frags.append(rect(65, 105, 60, 60, fill="#2b2d42", stroke="#111111", rx=3))
    frags.append(circle(75, 115, 4, fill="#ffffff", stroke="#ffffff"))  # крапка Pin 1
    frags.append(line(55, 115, 65, 115, color="#8d99ae", sw=2))  # pin 1
    frags.append(line(55, 125, 65, 125, color="#8d99ae", sw=2))
    frags.append(line(55, 135, 65, 135, color="#8d99ae", sw=2))
    frags.append(line(55, 145, 65, 145, color="#8d99ae", sw=2))
    frags.append(text(140, 115, "• Лазерна крапка або фаска кута", size=11, color=INK, anchor="start"))
    frags.append(text(140, 133, "• Скос шовкодруку на платі", size=11, color=INK, anchor="start"))
    frags.append(text(140, 151, "• Збіг з ключем у схемі та на платі", size=11, color=FIELD, bold=True, anchor="start"))

    # 2. Танталовий конденсатор (УВАГА: смуга = АНОД (+))
    frags.append(rect(40, 195, 420, 115, fill="#fff5f5", stroke="#feb2b2", rx=6))
    frags.append(text(55, 217, "2. Танталовий SMD-конденсатор", size=13, bold=True, color=POS, anchor="start"))
    # Тантал корпус
    frags.append(rect(65, 230, 60, 36, fill="#f6ad55", stroke="#dd6b20", rx=2))
    frags.append(rect(65, 230, 14, 36, fill="#c53030", stroke="#9b2c2c", rx=1))  # смуга АНОДА
    frags.append(text(72, 252, "+", size=12, color="#ffffff", bold=True))
    frags.append(text(140, 240, "• СМУГА = АНОД (ПОЗИТИВНИЙ ПОЛЮС +)", size=11, color=POS, bold=True, anchor="start"))
    frags.append(text(140, 258, "• Зворотне вмикання викликає вибух і пробій", size=11, color=INK, anchor="start"))
    frags.append(text(140, 276, "• Протилежно до алюмінієвих електролітів!", size=11, color=MUTED, italic=True, anchor="start"))

    # 3. Алюмінієвий електроліт (смуга = КАТОД (-))
    frags.append(rect(40, 320, 420, 115, fill="#f0f7ff", stroke="#bee3f8", rx=6))
    frags.append(text(55, 342, "3. Алюмінієвий електролітичний конденсатор", size=13, bold=True, color=NEG, anchor="start"))
    # Алюміній корпус
    frags.append(circle(95, 380, 22, fill="#edf2f7", stroke="#4a5568", sw=2))
    frags.append(rect(73, 358, 14, 44, fill="#3182ce", stroke="#2b6cb0"))  # смуга МІНУСА
    frags.append(text(80, 384, "−", size=14, color="#ffffff", bold=True))
    frags.append(text(140, 365, "• СМУГА = КАТОД (НЕГАТИВНИЙ ПОЛЮС −)", size=11, color=NEG, bold=True, anchor="start"))
    frags.append(text(140, 383, "• Скос кутів пластикової платформи = мінус", size=11, color=INK, anchor="start"))
    frags.append(text(140, 401, "• Чітке звірення з маскою полігону GND", size=11, color=MUTED, anchor="start"))

    # 4. Діоди та світлодіоди (LED)
    frags.append(rect(40, 445, 420, 135, fill="#ffffff", stroke="#e1e4e8", rx=6))
    frags.append(text(55, 467, "4. Діоди та SMD-світлодіоди (LED)", size=13, bold=True, color=INK, anchor="start"))
    # Діод корпус
    frags.append(rect(65, 480, 50, 26, fill="#1a202c", stroke="#000000", rx=2))
    frags.append(rect(65, 480, 10, 26, fill="#e2e8f0", stroke="#cbd5e0", rx=1))  # смуга катода
    frags.append(text(130, 492, "• Смуга на діоді = КАТОД (K / −)", size=11, color=INK, bold=True, anchor="start"))
    frags.append(text(130, 510, "• Зелена крапка / риска на дні LED = Катод", size=11, color=FIELD, anchor="start"))
    frags.append(text(130, 528, "• Зріз лінзи або трикутник у шовкодруку", size=11, color=INK, anchor="start"))
    frags.append(text(130, 546, "• Перевірка падіння напруги мультиметром", size=11, color=MUTED, anchor="start"))

    # Заголовок секції Б: Дефекти пайки та монтажні аномалії
    box_b = fitbox(500, 20, 460, 580, "", fill="#fbfcfd", stroke="#d0d7de", sw=1.5)
    frags.append(box_b)
    frags.append(text(730, 48, "Дефекти пайки та монтажні замикання", size=16, bold=True, color=INK))

    # 1. Припоєві перемички (Solder Bridges)
    frags.append(rect(520, 70, 420, 115, fill="#fffaf0", stroke="#feebc8", rx=6))
    frags.append(text(535, 92, "1. Припоєві перемички (Solder Bridges)", size=13, bold=True, color="#c05621", anchor="start"))
    # QFP ніжки: 545, 561, 577, 593, 609
    frags.append(rect(545, 112, 8, 30, fill="#cbd5e0", stroke="#718096"))
    frags.append(rect(561, 112, 8, 30, fill="#cbd5e0", stroke="#718096"))
    # місток у зазорі між ніжками 561 та 577
    frags.append(rect(569, 120, 8, 14, fill="#c05621", stroke="#9c4221", rx=1))
    frags.append(rect(577, 112, 8, 30, fill="#cbd5e0", stroke="#718096"))
    frags.append(rect(593, 112, 8, 30, fill="#cbd5e0", stroke="#718096"))
    frags.append(rect(609, 112, 8, 30, fill="#cbd5e0", stroke="#718096"))

    frags.append(text(640, 115, "• Замикання між виводами з кроком ≤0.5 мм", size=11, color=INK, anchor="start"))
    frags.append(text(640, 133, "• Типово для QFP, TSSOP, SOIC мікросхем", size=11, color=INK, anchor="start"))
    frags.append(text(640, 151, "• Усувається мідним обплетенням і флюсом", size=11, color=FIELD, bold=True, anchor="start"))

    # 2. Припоєві кульки (Solder Beads / Balls)
    frags.append(rect(520, 195, 420, 115, fill="#ffffff", stroke="#e1e4e8", rx=6))
    frags.append(text(535, 217, "2. Припоєві кульки біля пасивних SMD", size=13, bold=True, color=INK, anchor="start"))
    # Резистор 0603 і кулька поруч
    frags.append(rect(545, 238, 12, 20, fill="#a0aec0", stroke="#4a5568"))
    frags.append(rect(557, 238, 26, 20, fill="#2d3748", stroke="#1a202c"))
    frags.append(rect(583, 238, 12, 20, fill="#a0aec0", stroke="#4a5568"))
    frags.append(circle(570, 274, 5, fill="#e53e3e", stroke="#9b2c2c"))  # кулька припою
    frags.append(text(620, 240, "• Вибухове викидання флюсу при нагріві", size=11, color=INK, anchor="start"))
    frags.append(text(620, 258, "• Кулька закорочує сусідні доріжки та віаси", size=11, color=POS, bold=True, anchor="start"))
    frags.append(text(620, 276, "• Видаляється ультразвуком або пензлем", size=11, color=MUTED, anchor="start"))

    # 3. Ефект надгробка (Tombstoning) та зміщення
    frags.append(rect(520, 320, 420, 115, fill="#ffffff", stroke="#e1e4e8", rx=6))
    frags.append(text(535, 342, "3. Надгробок (Tombstoning) та розриви", size=13, bold=True, color=INK, anchor="start"))
    # Піднятий чіп
    frags.append(rect(545, 385, 20, 6, fill="#cbd5e0", stroke="#718096"))
    frags.append(rect(585, 385, 20, 6, fill="#cbd5e0", stroke="#718096"))
    frags.append(rect(547, 360, 16, 25, fill="#2b6cb0", stroke="#2c5282", rx=1))  # стоїть вертикально
    frags.append(text(620, 365, "• Несиметричний натяг розплавленого припою", size=11, color=INK, anchor="start"))
    frags.append(text(620, 383, "• Повний обрив ланцюга живлення чи сигналу", size=11, color=POS, anchor="start"))
    frags.append(text(620, 401, "• Причина: нерівні термобар'єри на полігоні", size=11, color=MUTED, anchor="start"))

    # 4. Тріщини в кераміці MLCC-конденсаторів
    frags.append(rect(520, 445, 420, 135, fill="#fff5f5", stroke="#feb2b2", rx=6))
    frags.append(text(535, 467, "4. Тріщини в кераміці MLCC (Flex Cracks)", size=13, bold=True, color=POS, anchor="start"))
    # Тріснутий MLCC
    frags.append(rect(545, 485, 50, 26, fill="#d69e2e", stroke="#b7791f", rx=2))
    frags.append(line(565, 485, 575, 511, color="#e53e3e", sw=2))  # тріщина
    frags.append(text(615, 492, "• Тріщина виникає при вигині або термоударі", size=11, color=INK, anchor="start"))
    frags.append(text(615, 510, "• Призводить до плаваючого або низькоомного КЗ", size=11, color=POS, bold=True, anchor="start"))
    frags.append(text(615, 528, "• Непомітна без мікроскопа з косим світлом", size=11, color=INK, anchor="start"))
    frags.append(text(615, 546, "• Заміна компонента без повторного перегріву", size=11, color=FIELD, anchor="start"))

    render(os.path.join(OUT_DIR, "pre-power-microscope-inspection-points.svg"), w, h, *frags)


def fig2_power_rail_measurement():
    """Фігура 2: Чотирипровідна схема вимірювання опору та пошук місця КЗ."""
    w, h = 980, 620
    frags = []

    # Верхня секція: Чотирипровідне вимірювання за Кельвіном проти 2-провідного
    box_top = fitbox(20, 20, 940, 270, "", fill="#fbfcfd", stroke="#d0d7de", sw=1.5)
    frags.append(box_top)
    frags.append(text(490, 45, "Чотирипровідне вимірювання за Кельвіном (4-Wire Kelvin) проти звичайного 2-провідного", size=15, bold=True, color=INK))

    # Схема 2-wire (зліва)
    frags.append(rect(40, 65, 420, 210, fill="#ffffff", stroke="#e1e4e8", rx=6))
    frags.append(text(250, 88, "2-провідна схема (Звичайний мультиметр)", size=13, bold=True, color=NEG))
    frags.append(rect(60, 110, 90, 60, fill="#edf2f7", stroke="#4a5568", rx=4))
    frags.append(text(105, 145, "Омметр", size=12, bold=True, color=INK))

    # Лінії щупів з опором проводів
    frags.append(line(150, 125, 230, 125, color=POS, sw=2))
    frags.append(rect(230, 117, 40, 16, fill="#fed7d7", stroke="#e53e3e", rx=2))
    frags.append(text(250, 129, "R_дроту", size=9, color=POS))
    frags.append(line(270, 125, 330, 125, color=POS, sw=2))

    frags.append(line(150, 155, 230, 155, color=NEG, sw=2))
    frags.append(rect(230, 147, 40, 16, fill="#bee3f8", stroke="#3182ce", rx=2))
    frags.append(text(250, 159, "R_дроту", size=9, color=NEG))
    frags.append(line(270, 155, 330, 155, color=NEG, sw=2))

    # Об'єкт вимірювання (R_DUT)
    frags.append(rect(330, 115, 60, 50, fill="#feebc8", stroke="#dd6b20", rx=4))
    frags.append(text(360, 145, "R_рейки", size=11, bold=True, color=INK))

    frags.append(text(250, 195, "R_вим = R_рейки + 2 · R_дроту (похибка 0.2–0.8 Ом!)", size=11, color=POS, bold=True))
    frags.append(text(250, 215, "Зумер пищить при < 50 Ом → хибне КЗ на рейках ядра VCORE (0.5–2 Ом)", size=10, color=MUTED))
    frags.append(text(250, 235, "Не здатний відрізнити нормальний опір чипа від металевого замикання", size=10, color=INK))

    # Схема 4-wire (справа)
    frags.append(rect(480, 65, 480, 210, fill="#ffffff", stroke="#e1e4e8", rx=6))
    frags.append(text(720, 88, "4-провідна схема Кельвіна (Force + Sense)", size=13, bold=True, color=FIELD))

    # Джерело струму та Вольтметр
    frags.append(rect(500, 105, 80, 40, fill="#e6fffa", stroke="#319795", rx=4))
    frags.append(text(540, 128, "I_Force", size=11, bold=True, color="#234e52"))

    frags.append(rect(500, 155, 80, 40, fill="#ebf8ff", stroke="#3182ce", rx=4))
    frags.append(text(540, 178, "V_Sense", size=11, bold=True, color="#2b6cb0"))

    # Force лінії
    frags.append(line(580, 115, 820, 115, color=POS, sw=2))
    frags.append(line(580, 135, 820, 135, color=NEG, sw=2))
    # Sense лінії (вимірюють безпосередньо на контактах)
    frags.append(line(580, 165, 800, 165, color="#805ad5", sw=1.5, dash="4,3"))
    frags.append(line(800, 165, 820, 120, color="#805ad5", sw=1.5))
    frags.append(line(580, 185, 800, 185, color="#d69e2e", sw=1.5, dash="4,3"))
    frags.append(line(800, 185, 820, 130, color="#d69e2e", sw=1.5))

    # Навантаження R_DUT
    frags.append(rect(820, 110, 60, 40, fill="#feebc8", stroke="#dd6b20", rx=4))
    frags.append(text(850, 134, "R_рейки", size=11, bold=True, color=INK))

    frags.append(text(720, 215, "Струм через Sense-лінії ≈ 0 → R_дроту не впливає на вимір напруги", size=11, color=FIELD, bold=True))
    frags.append(text(720, 235, "Точність до міліомів (мОм): чітке розрізнення 0.02 Ом (КЗ) та 0.85 Ом (ядро)", size=10, color=INK))
    frags.append(text(720, 255, "Єдиний надійний метод діагностики сучасних низьковольтних SoC/FPGA", size=10, color=MUTED))

    # Нижня ліва секція: Ієрархія рейок та типовий холодний опір
    box_bl = fitbox(20, 305, 460, 295, "", fill="#fbfcfd", stroke="#d0d7de", sw=1.5)
    frags.append(box_bl)
    frags.append(text(250, 330, "Типовий опір рейок живлення відносно GND", size=14, bold=True, color=INK))

    # Таблиця/Діапазони
    frags.append(rect(35, 345, 430, 45, fill="#ffffff", stroke="#e2e8f0", rx=4))
    frags.append(text(45, 363, "V_IN (12 В / 24 В / 5 В)", size=11, bold=True, color=POS, anchor="start"))
    frags.append(text(45, 381, "Вхідний фільтр, ключі DC-DC", size=10, color=MUTED, anchor="start"))
    frags.append(text(450, 372, "> 10 кОм .. МОм (Норма)", size=11, bold=True, color=FIELD, anchor="end"))

    frags.append(rect(35, 395, 430, 45, fill="#ffffff", stroke="#e2e8f0", rx=4))
    frags.append(text(45, 413, "V_IO / VDD (3.3 В / 1.8 В)", size=11, bold=True, color=NEG, anchor="start"))
    frags.append(text(45, 431, "Периферія, пам'ять, Flash, MCU", size=10, color=MUTED, anchor="start"))
    frags.append(text(450, 422, "100 Ом .. десятки кОм", size=11, bold=True, color=FIELD, anchor="end"))

    frags.append(rect(35, 445, 430, 45, fill="#ffffff", stroke="#e2e8f0", rx=4))
    frags.append(text(45, 463, "VDDQ (1.1 В / 1.2 В / 1.35 В)", size=11, bold=True, color="#d69e2e", anchor="start"))
    frags.append(text(45, 481, "Шина живлення DDR3/DDR4/DDR5", size=10, color=MUTED, anchor="start"))
    frags.append(text(450, 472, "10 Ом .. 100 Ом", size=11, bold=True, color=FIELD, anchor="end"))

    frags.append(rect(35, 495, 430, 50, fill="#fff5f5", stroke="#feb2b2", rx=4))
    frags.append(text(45, 515, "VCORE (0.75 В .. 1.05 В)", size=11, bold=True, color="#c53030", anchor="start"))
    frags.append(text(45, 533, "Ядро процесора, FPGA Fabric, GPU", size=10, color=MUTED, anchor="start"))
    frags.append(text(450, 524, "0.2 Ом .. 5.0 Ом (НЕ КЗ!)", size=11, bold=True, color=POS, anchor="end"))

    frags.append(text(250, 575, "⚠ Пряме металеве КЗ: R < 0.05 Ом (дефект пайки / пробитий MLCC)", size=10.5, color=POS, bold=True))

    # Нижня права секція: Локалізація КЗ методом мілівольтного градієнта
    box_br = fitbox(500, 305, 460, 295, "", fill="#fbfcfd", stroke="#d0d7de", sw=1.5)
    frags.append(box_br)
    frags.append(text(730, 330, "Пошук місця КЗ методом мілівольтного градієнта", size=14, bold=True, color=INK))

    # Полігон живлення на платі
    frags.append(rect(520, 350, 420, 110, fill="#fefcbf", stroke="#d69e2e", sw=2, rx=4))
    frags.append(text(535, 370, "Мідний полігон живлення (Power Plane)", size=11, bold=True, color="#744210", anchor="start"))

    # Подача каліброваного струму I_test (100 мА)
    frags.append(line(540, 390, 580, 390, color=POS, sw=2))
    frags.append(text(545, 415, "I_вхід = 100 мА", size=10, bold=True, color=POS, anchor="start"))

    # Точка КЗ (пробитий конденсатор)
    frags.append(rect(800, 380, 20, 30, fill="#e53e3e", stroke="#9b2c2c", rx=2))
    frags.append(text(810, 425, "Точка КЗ", size=10, bold=True, color=POS))
    frags.append(text(810, 440, "(V_min = 0 мВ)", size=9, color=POS))

    # Градієнт напруги
    frags.append(circle(620, 390, 4, fill=FIELD, stroke=FIELD))
    frags.append(text(620, 375, "4.8 мВ", size=9, bold=True, color=INK))

    frags.append(circle(690, 390, 4, fill=FIELD, stroke=FIELD))
    frags.append(text(690, 375, "2.6 мВ", size=9, bold=True, color=INK))

    frags.append(circle(750, 390, 4, fill=FIELD, stroke=FIELD))
    frags.append(text(750, 375, "0.9 мВ", size=9, bold=True, color=INK))

    frags.append(text(730, 480, "Струм генерує спад напруги V = I · R_міді вздовж доріжки", size=11, bold=True, color=INK))
    frags.append(text(730, 500, "Рухаючись чутливим мікровольтметром у бік ЗМЕНШЕННЯ напруги,", size=10, color=MUTED))
    frags.append(text(730, 518, "ви точно локалізуєте пробитий MLCC або припоєву перемичку", size=10, color=MUTED))
    frags.append(text(730, 540, "без випоювання десятків паралельних компонентів!", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT_DIR, "power-rail-resistance-measurement.svg"), w, h, *frags)


if __name__ == "__main__":
    fig1_microscope_inspection()
    fig2_power_rail_measurement()
    print("SVG figures generated successfully.")

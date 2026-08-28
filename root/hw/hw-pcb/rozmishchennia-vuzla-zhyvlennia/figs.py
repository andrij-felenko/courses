# -*- coding: utf-8 -*-
import sys
import os

# scripts is 4 levels up: root/hw/hw-pcb/rozmishchennia-vuzla-zhyvlennia -> ../../../../scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_hot_loop_buck():
    """Схема гарячої петлі Buck-перетворювача та розподіл di/dt струмів."""
    w, h = 880, 520
    frags = []

    # Заголовок блоків
    frags.append(text(225, 30, "Стан 1: Q1 замкнено (HS ON)", size=15, color=POS, bold=True))
    frags.append(text(655, 30, "Стан 2: Q2 замкнено (LS ON / Freewheeling)", size=15, color=NEG, bold=True))

    # Ліва схема (HS ON)
    # Рамка лівої схеми
    frags.append(rect(20, 50, 410, 240, fill="#fffaf9", stroke="#e0c0bc", sw=1.2, rx=8))

    # Вхідні клеми і Cin
    frags.append(circle(50, 90, 4, fill=POS, stroke=POS))
    frags.append(text(45, 75, "+VIN", size=12, color=POS, bold=True, anchor="start"))
    frags.append(line(50, 90, 100, 90, color=POS, sw=2.5))
    frags.append(line(100, 90, 100, 130, color=POS, sw=2.5))
    # Cin1 box
    frags.append(rect(85, 130, 30, 40, fill="#ffffff", stroke=POS, sw=1.5, rx=3))
    frags.append(text(100, 154, "Cin", size=11, bold=True))
    frags.append(line(100, 170, 100, 220, color=LINE, sw=2.5))
    frags.append(line(100, 220, 50, 220, color=LINE, sw=2.5))
    frags.append(circle(50, 220, 4, fill=LINE, stroke=LINE))
    frags.append(text(45, 240, "GND", size=12, color=MUTED, bold=True, anchor="start"))

    # Q1 (HS)
    frags.append(line(100, 90, 180, 90, color=POS, sw=2.5))
    frags.append(rect(180, 75, 45, 30, fill="#ffebe9", stroke=POS, sw=1.8, rx=4))
    frags.append(text(202, 95, "Q1 (ON)", size=11, color=POS, bold=True))
    frags.append(line(225, 90, 270, 90, color=POS, sw=2.5))

    # Комутаційний вузол SW
    frags.append(circle(270, 90, 4, fill=POS, stroke=POS))
    frags.append(text(270, 75, "SW", size=12, color=POS, bold=True))

    # Q2 (LS - OFF)
    frags.append(line(270, 90, 270, 130, color=LINE, sw=1.5, dash="4,3"))
    frags.append(rect(248, 130, 45, 30, fill="#f4f6f8", stroke=MUTED, sw=1.2, rx=4))
    frags.append(text(270, 150, "Q2 (OFF)", size=11, color=MUTED))
    frags.append(line(270, 160, 270, 220, color=LINE, sw=1.5, dash="4,3"))

    # Дросель L та Cout
    frags.append(line(270, 90, 310, 90, color=POS, sw=2.5))
    frags.append(rect(310, 78, 40, 24, fill="#ffffff", stroke=POS, sw=1.5, rx=3))
    frags.append(text(330, 94, "L", size=12, bold=True))
    frags.append(line(350, 90, 390, 90, color=POS, sw=2.5))
    frags.append(circle(390, 90, 4, fill=POS, stroke=POS))
    frags.append(text(390, 75, "+VOUT", size=12, color=POS, bold=True))

    # Cout
    frags.append(line(380, 90, 380, 130, color=LINE, sw=1.5))
    frags.append(rect(365, 130, 30, 40, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    frags.append(text(380, 154, "Cout", size=10, bold=True))
    frags.append(line(380, 170, 380, 220, color=LINE, sw=1.5))
    frags.append(line(100, 220, 390, 220, color=LINE, sw=2))
    frags.append(circle(390, 220, 4, fill=LINE, stroke=LINE))

    # Стрілка струму HS ON
    frags.append(text(150, 115, "I_in (імпульс)", size=11, color=POS, bold=True))
    frags.append(text(340, 115, "I_L (струм котушки)", size=11, color=POS))

    # Права схема (LS ON)
    frags.append(rect(450, 50, 410, 240, fill="#f6f9ff", stroke="#bccce0", sw=1.2, rx=8))

    # Вхідні клеми і Cin
    frags.append(circle(480, 90, 4, fill=MUTED, stroke=MUTED))
    frags.append(text(475, 75, "+VIN", size=12, color=MUTED, bold=True, anchor="start"))
    frags.append(line(480, 90, 530, 90, color=MUTED, sw=1.5, dash="4,3"))
    frags.append(line(530, 90, 530, 130, color=MUTED, sw=1.5, dash="4,3"))
    frags.append(rect(515, 130, 30, 40, fill="#ffffff", stroke=MUTED, sw=1.2, rx=3))
    frags.append(text(530, 154, "Cin", size=11, color=MUTED, bold=True))
    frags.append(line(530, 170, 530, 220, color=MUTED, sw=1.5, dash="4,3"))
    frags.append(line(530, 220, 480, 220, color=MUTED, sw=1.5, dash="4,3"))
    frags.append(circle(480, 220, 4, fill=MUTED, stroke=MUTED))
    frags.append(text(475, 240, "GND", size=12, color=MUTED, bold=True, anchor="start"))

    # Q1 (OFF)
    frags.append(line(530, 90, 610, 90, color=MUTED, sw=1.5, dash="4,3"))
    frags.append(rect(610, 75, 45, 30, fill="#f4f6f8", stroke=MUTED, sw=1.2, rx=4))
    frags.append(text(632, 95, "Q1 (OFF)", size=11, color=MUTED))
    frags.append(line(655, 90, 700, 90, color=NEG, sw=2.5))

    # Комутаційний вузол SW
    frags.append(circle(700, 90, 4, fill=NEG, stroke=NEG))
    frags.append(text(700, 75, "SW ≈ 0V", size=12, color=NEG, bold=True))

    # Q2 (LS - ON)
    frags.append(line(700, 90, 700, 130, color=NEG, sw=2.5))
    frags.append(rect(678, 130, 45, 30, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    frags.append(text(700, 150, "Q2 (ON)", size=11, color=NEG, bold=True))
    frags.append(line(700, 160, 700, 220, color=NEG, sw=2.5))

    # Дросель L та Cout
    frags.append(line(700, 90, 740, 90, color=NEG, sw=2.5))
    frags.append(rect(740, 78, 40, 24, fill="#ffffff", stroke=NEG, sw=1.5, rx=3))
    frags.append(text(760, 94, "L", size=12, bold=True))
    frags.append(line(780, 90, 820, 90, color=NEG, sw=2.5))
    frags.append(circle(820, 90, 4, fill=NEG, stroke=NEG))
    frags.append(text(820, 75, "+VOUT", size=12, color=NEG, bold=True))

    # Cout
    frags.append(line(810, 90, 810, 130, color=NEG, sw=1.8))
    frags.append(rect(795, 130, 30, 40, fill="#ffffff", stroke=NEG, sw=1.5, rx=3))
    frags.append(text(810, 154, "Cout", size=10, bold=True))
    frags.append(line(810, 170, 810, 220, color=NEG, sw=1.8))
    frags.append(line(700, 220, 820, 220, color=NEG, sw=2.5))
    frags.append(circle(820, 220, 4, fill=NEG, stroke=NEG))

    frags.append(text(760, 115, "I_L (замикання через Q2)", size=11, color=NEG))

    # Нижня частина: порівняння контурів і висновок про гарячу петлю
    frags.append(rect(20, 310, 410, 185, fill="#fff5f5", stroke=POS, sw=1.8, rx=8))
    frags.append(text(225, 335, "ГАРЯЧА ПЕТЛЯ (High di/dt Loop)", size=14, color=POS, bold=True))
    frags.append(text(225, 360, "Контур: Cin → Q1 (HS) → Q2 (LS) → GND Cin", size=12, bold=True))
    frags.append(text(225, 385, "Струм: розривні прямокутні імпульси з di/dt ≈ 10⁹ А/с", size=12, color=INK))
    frags.append(text(225, 410, "Наслідок: V_spike = L_loop · (di/dt) + дзвін на SW", size=12, color=POS, bold=True))
    frags.append(text(225, 435, "EMI: випромінювання магнітного поля H ∝ A_loop · I · f²", size=12, color=INK))
    frags.append(text(225, 465, "→ Вимагає МІНІМАЛЬНОЇ площі контуру та симетрії!", size=12, color=POS, bold=True))

    frags.append(rect(450, 310, 410, 185, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(655, 335, "ХОЛОДНА ПЕТЛЯ (Низький di/dt)", size=14, color=FIELD, bold=True))
    frags.append(text(655, 360, "Контур: SW → Дросель L → Cout → GND", size=12, bold=True))
    frags.append(text(655, 385, "Струм: безперервний трикутний з малою пульсацією ΔI_L", size=12, color=INK))
    frags.append(text(655, 410, "di/dt котушки обмежений індуктивністю: di/dt = V_L / L", size=12, color=INK))
    frags.append(text(655, 435, "Магнітне поле зосереджене в осерді дроселя", size=12, color=INK))
    frags.append(text(655, 465, "→ Не генерує високочастотних імпульсних викидів", size=12, color=FIELD, bold=True))

    return render(os.path.join(OUT_DIR, "hot-loop-buck-commutation.svg"), w, h, *frags)


def fig_dc_dc_layout_topology():
    """Топологія розміщення компонентів та симетричне компенсування полів."""
    w, h = 880, 500
    frags = []

    frags.append(text(440, 25, "Оптимальна топологія розміщення DC-DC перетворювача на платі", size=16, bold=True))

    # Ліва панель: симетричні вхідні конденсатори (Cin1 / Cin2)
    frags.append(rect(20, 50, 410, 430, fill="#fcfdfe", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(225, 75, "Симетричні Cin: компенсація магнітних полів", size=14, color=POS, bold=True))

    # Корпус мікросхеми Power IC в центрі
    frags.append(rect(170, 160, 110, 140, fill="#2c3e50", stroke="#1a252f", sw=2, rx=4))
    frags.append(text(225, 220, "Power IC", size=14, color="#ffffff", bold=True))
    frags.append(text(225, 240, "(HS + LS)", size=11, color="#ecf0f1"))
    frags.append(text(225, 260, "ePad GND", size=10, color="#bdc3c7"))

    # Піни мікросхеми
    # Зліва: VIN1, GND1
    frags.append(rect(145, 180, 25, 20, fill=POS, stroke=POS, rx=2))
    frags.append(text(157, 195, "VIN", size=9, color="#ffffff", bold=True))
    frags.append(rect(145, 240, 25, 20, fill="#34495e", stroke="#34495e", rx=2))
    frags.append(text(157, 255, "GND", size=9, color="#ffffff", bold=True))

    # Справа: VIN2, GND2
    frags.append(rect(280, 180, 25, 20, fill=POS, stroke=POS, rx=2))
    frags.append(text(292, 195, "VIN", size=9, color="#ffffff", bold=True))
    frags.append(rect(280, 240, 25, 20, fill="#34495e", stroke="#34495e", rx=2))
    frags.append(text(292, 255, "GND", size=9, color="#ffffff", bold=True))

    # Знизу: SW
    frags.append(rect(205, 300, 40, 25, fill="#e67e22", stroke="#d35400", rx=2))
    frags.append(text(225, 317, "SW", size=10, color="#ffffff", bold=True))

    # Конденсатор Cin1 зліва
    frags.append(rect(60, 175, 45, 90, fill="#ffffff", stroke=POS, sw=2, rx=4))
    frags.append(text(82, 215, "Cin 1", size=12, color=POS, bold=True))
    frags.append(text(82, 235, "(0603)", size=10, color=MUTED))
    # Доріжки до Cin1
    frags.append(rect(105, 183, 40, 14, fill=POS, stroke=POS))
    frags.append(rect(105, 243, 40, 14, fill="#7f8c8d", stroke="#7f8c8d"))

    # Конденсатор Cin2 справа
    frags.append(rect(345, 175, 45, 90, fill="#ffffff", stroke=POS, sw=2, rx=4))
    frags.append(text(367, 215, "Cin 2", size=12, color=POS, bold=True))
    frags.append(text(367, 235, "(0603)", size=10, color=MUTED))
    # Доріжки до Cin2
    frags.append(rect(305, 183, 40, 14, fill=POS, stroke=POS))
    frags.append(rect(305, 243, 40, 14, fill="#7f8c8d", stroke="#7f8c8d"))

    # Символи циркуляції струмів у петлях
    frags.append(text(125, 225, "B1", size=14, color=POS, bold=True))
    frags.append(text(125, 145, "(в плату)", size=10, color=POS, bold=True))

    frags.append(text(325, 225, "B2", size=14, color=POS, bold=True))
    frags.append(text(325, 145, "(з плати)", size=10, color=POS, bold=True))

    # Підсумок компенсації
    frags.append(rect(40, 365, 370, 95, fill="#fffaf0", stroke="#f39c12", sw=1.2, rx=6))
    frags.append(text(225, 390, "Магнітне поле в дальній зоні:", size=11, bold=True))
    frags.append(text(225, 412, "B_net = B1 + B2 ≈ 0 (взаємне гасіння полів)", size=11, color=POS, bold=True))
    frags.append(text(225, 435, "Зниження випромінюваних завад (EMI) на 15–25 дБ", size=11, color=FIELD, bold=True))

    # Права панель: Комплексна топологія (SW, L, Cout, FB)
    frags.append(rect(450, 50, 410, 430, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(655, 75, "Трасування вузлів SW, FB та котушки L", size=14, color=FIELD, bold=True))

    # Комутаційний полігон SW
    frags.append(rect(540, 110, 70, 45, fill="#fdebd0", stroke="#e67e22", sw=1.8, rx=4))
    frags.append(text(575, 130, "Полігон SW", size=11, color="#d35400", bold=True))
    frags.append(text(575, 146, "Мала площа!", size=9, color=POS))

    # Котушка L
    frags.append(rect(630, 100, 85, 65, fill="#ebf5fb", stroke="#2980b9", sw=2, rx=6))
    frags.append(circle(645, 115, 4, fill="#2980b9", stroke="#2980b9")) # Крапка початку обмотки
    frags.append(text(672, 132, "Дросель L", size=12, color="#1b4f72", bold=True))
    frags.append(text(672, 150, "Екранований", size=10, color=MUTED))

    # Доріжка від SW до L
    frags.append(line(610, 132, 630, 132, color="#e67e22", sw=6))

    # Вихідний конденсатор Cout
    frags.append(rect(745, 105, 40, 55, fill="#ffffff", stroke="#27ae60", sw=1.8, rx=4))
    frags.append(text(765, 132, "Cout", size=11, color="#27ae60", bold=True))
    frags.append(line(715, 132, 745, 132, color="#27ae60", sw=4))

    # VOUT шина
    frags.append(line(785, 132, 830, 132, color="#27ae60", sw=3))
    frags.append(circle(830, 132, 4, fill="#27ae60", stroke="#27ae60"))
    frags.append(text(830, 120, "VOUT", size=10, color="#27ae60", bold=True))

    # Зворотний зв'язок (FB)
    frags.append(line(770, 160, 770, 240, color=NEG, sw=1.5, dash="4,3"))
    frags.append(line(770, 240, 560, 240, color=NEG, sw=1.5, dash="4,3"))
    frags.append(text(670, 230, "Тиха лінія VOUT Sense", size=10, color=NEG))

    # Дільник FB (R1, R2) біля IC
    frags.append(rect(520, 225, 30, 20, fill="#ffffff", stroke=NEG, sw=1.2, rx=2))
    frags.append(text(535, 239, "R1", size=10, bold=True))
    frags.append(rect(520, 260, 30, 20, fill="#ffffff", stroke=NEG, sw=1.2, rx=2))
    frags.append(text(535, 274, "R2", size=10, bold=True))
    frags.append(line(550, 235, 505, 235, color=NEG, sw=1.5))
    frags.append(line(505, 235, 505, 250, color=NEG, sw=1.5))
    frags.append(circle(505, 250, 3, fill=NEG, stroke=NEG))
    frags.append(text(495, 254, "FB пін", size=10, color=NEG, bold=True, anchor="end"))

    # Пояснювальні правила
    frags.append(rect(465, 305, 380, 155, fill="#ffffff", stroke="#bdc3c7", sw=1.2, rx=6))
    frags.append(text(655, 325, "Критичні правила трасування:", size=12, bold=True))
    frags.append(text(475, 350, "1. SW-вузол: високий dv/dt — тримати площу мінімальною", size=10, color=INK, anchor="start"))
    frags.append(text(475, 372, "2. Дросель: підключати початок обмотки (крапку) до SW", size=10, color=INK, anchor="start"))
    frags.append(text(475, 394, "3. Дільник FB: розміщувати ВПРИТУЛ до FB-піна контролера", size=10, color=POS, bold=True, anchor="start"))
    frags.append(text(475, 416, "4. Лінія FB: знімати сигнал ПІСЛЯ Cout, екранувати землею", size=10, color=INK, anchor="start"))
    frags.append(text(475, 438, "5. Шар L2 під DC-DC: суцільна земля без вирізів під SW/L", size=10, color=FIELD, bold=True, anchor="start"))

    return render(os.path.join(OUT_DIR, "dc-dc-layout-topology.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_hot_loop_buck()
    fig_dc_dc_layout_topology()
    print("Generated 2 SVG figures successfully.")

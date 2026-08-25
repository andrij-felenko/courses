#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор фігур для теми «PoE: живлення по витій парі» (book/communications/networks/poe)."""

import os
import sys

# Шлях до svgkit у scripts/ (чотири рівні вгору від book/communications/networks/poe)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def fig_phantom_power():
    """Фігура 1: Інжекція фантомного живлення через середні точки трансформаторів."""
    W, H = 880, 400
    f = []

    # Фон і заголовок
    f.append(rect(0, 0, W, H, fill=BG, stroke=LINE, sw=1, rx=0))
    f.append(text(W / 2, 28, "Фантомне живлення через середні точки сигнальних трансформаторів (Alternative A)", size=15, bold=True))

    # Лівий блок — PSE (Джерело / Switch PHY)
    f.append(rect(20, 50, 230, 325, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(135, 75, "PSE (Комутатор / Джерело)", size=13, bold=True, color=INK))

    # PHY передавач (Tx)
    f.append(rect(35, 100, 70, 75, fill="#e2e8f0", stroke=LINE, sw=1, rx=4))
    f.append(mtext(70, 135, "Ethernet\nPHY Tx", size=11, bold=True))

    # Джерело DC живлення
    f.append(rect(35, 275, 95, 80, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    f.append(mtext(82, 305, "Джерело DC\n+48...57 В\n(PSE Power)", size=11, bold=True, color=POS))

    # Трансформатор PSE (Tx)
    # Первинна обмотка
    f.append(line(105, 120, 140, 120, color=FIELD, sw=2))
    f.append(line(105, 155, 140, 155, color=FIELD, sw=2))
    f.append(rect(140, 110, 12, 55, fill="#cbd5e1", stroke=LINE, sw=1.2, rx=2))
    # Осердя
    f.append(line(157, 105, 157, 170, color=LINE, sw=2))
    f.append(line(161, 105, 161, 170, color=LINE, sw=2))
    # Вторинна обмотка з середньою точкою
    f.append(rect(166, 110, 12, 55, fill="#cbd5e1", stroke=LINE, sw=1.2, rx=2))
    # Виводи вторинної обмотки до кабелю
    f.append(line(178, 120, 250, 120, color=LINE, sw=2))
    f.append(line(178, 155, 250, 155, color=LINE, sw=2))
    # Середня точка (Center Tap)
    f.append(line(172, 137.5, 172, 220, color=POS, sw=2))
    f.append(circle(172, 137.5, 3.5, fill=POS, stroke=POS))
    f.append(line(130, 300, 172, 300, color=POS, sw=2))
    f.append(line(172, 300, 172, 220, color=POS, sw=2))
    f.append(text(188, 225, "I_DC / 2 (вгору і вниз)", size=10, bold=True, color=POS, anchor="start"))

    # Текст про магнітний потік PSE
    f.append(fitbox(35, 190, 120, 65, "Флюси струмів I_DC/2\nнапрямлені зустрічно:\nΦ_DC = Φ1 − Φ2 = 0\n(осердя не насичується)", size=9.5, fill="#ecfdf5", stroke=FIELD))

    # Кабель витої пари (UTP Cat5e/Cat6A)
    f.append(rect(275, 70, 330, 290, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(440, 95, "Кабельна лінія UTP (до 100 м)", size=13, bold=True, color="#475569"))

    # Провід 1 (Tip, Pin 1)
    f.append(line(250, 120, 630, 120, color=LINE, sw=2.5))
    f.append(text(285, 112, "Pin 1 (+)", size=10, bold=True, color=INK, anchor="start"))
    f.append(arrow(340, 120, 390, 120, color=POS, sw=2))
    f.append(text(365, 110, "I_DC / 2", size=10, bold=True, color=POS))
    f.append(arrow(470, 120, 520, 120, color=FIELD, sw=1.8))
    f.append(text(495, 110, "+ I_data(t)", size=10, bold=True, color=FIELD))

    # Провід 2 (Ring, Pin 2)
    f.append(line(250, 155, 630, 155, color=LINE, sw=2.5))
    f.append(text(285, 147, "Pin 2 (−)", size=10, bold=True, color=INK, anchor="start"))
    f.append(arrow(340, 155, 390, 155, color=POS, sw=2))
    f.append(text(365, 172, "I_DC / 2", size=10, bold=True, color=POS))
    f.append(arrow(520, 155, 470, 155, color=FIELD, sw=1.8))
    f.append(text(495, 172, "− I_data(t)", size=10, bold=True, color=FIELD))

    # Пара повернення струму (Pins 3-6)
    f.append(line(250, 320, 630, 320, color=LINE, sw=2.5))
    f.append(text(285, 312, "Pin 3, 6 (Повернення DC)", size=10, bold=True, color=NEG, anchor="start"))
    f.append(arrow(470, 320, 420, 320, color=NEG, sw=2))
    f.append(text(445, 340, "I_DC (зворотний струм)", size=10, bold=True, color=NEG))

    # Правий блок — PD (Живлений пристрій / IP-камера, AP)
    f.append(rect(630, 50, 230, 325, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(745, 75, "PD (Живлений пристрій)", size=13, bold=True, color=INK))

    # Трансформатор PD (Rx)
    # Первинна обмотка з середньою точкою
    f.append(rect(702, 110, 12, 55, fill="#cbd5e1", stroke=LINE, sw=1.2, rx=2))
    f.append(line(630, 120, 702, 120, color=LINE, sw=2))
    f.append(line(630, 155, 702, 155, color=LINE, sw=2))
    # Осердя
    f.append(line(719, 105, 719, 170, color=LINE, sw=2))
    f.append(line(723, 105, 723, 170, color=LINE, sw=2))
    # Вторинна обмотка
    f.append(rect(728, 110, 12, 55, fill="#cbd5e1", stroke=LINE, sw=1.2, rx=2))
    f.append(line(740, 120, 775, 120, color=FIELD, sw=2))
    f.append(line(740, 155, 775, 155, color=FIELD, sw=2))

    # Середня точка PD
    f.append(line(708, 137.5, 708, 220, color=POS, sw=2))
    f.append(circle(708, 137.5, 3.5, fill=POS, stroke=POS))
    f.append(line(708, 220, 708, 280, color=POS, sw=2))
    f.append(line(708, 280, 745, 280, color=POS, sw=2))

    # PHY приймач (Rx)
    f.append(rect(775, 100, 70, 75, fill="#e2e8f0", stroke=LINE, sw=1, rx=4))
    f.append(mtext(810, 135, "Ethernet\nPHY Rx", size=11, bold=True))

    # DC-DC перетворювач PD
    f.append(rect(745, 260, 100, 95, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    f.append(mtext(795, 290, "PD Interface\n+ DC-DC\n(3.3В / 5В / 12В)", size=10.5, bold=True, color=POS))

    # Повернення до PSE
    f.append(line(795, 355, 795, 365, color=NEG, sw=1.5))
    f.append(line(795, 365, 630, 365, color=NEG, sw=1.5))
    f.append(line(630, 365, 630, 320, color=NEG, sw=1.5))
    f.append(line(250, 320, 200, 320, color=NEG, sw=1.5))
    f.append(line(200, 320, 200, 340, color=NEG, sw=1.5))
    f.append(line(200, 340, 130, 340, color=NEG, sw=1.5))

    render(os.path.join(IMG, "phantom-power.svg"), W, H, *f)


def fig_poe_state_machine():
    """Фігура 2: Послідовність станів узгодження PoE (Detection -> Classification -> Startup -> Monitoring)."""
    W, H = 880, 370
    f = []

    f.append(rect(0, 0, W, H, fill=BG, stroke=LINE, sw=1, rx=0))
    f.append(text(W / 2, 28, "Багатоступеневий автомат станів PoE (IEEE 802.3)", size=15, bold=True))

    # 4 основні блоки станів
    # Стан 1: Detection
    f.append(rect(25, 65, 185, 180, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(35, 75, 165, 32, "1. Детекція (Detection)", size=11, bold=True, fill="#e2e8f0"))
    f.append(mtext(117, 130, "Зондування: 2.8...10 В\nКрок ΔV → вимір ΔI\nR_det = ΔV / ΔI\n\nНорма: 19...26.5 кОм\n(номінал 24.9 кОм)\nC_in ≤ 150 нФ", size=10, anchor="middle"))

    # Стрілка 1 -> 2
    f.append(arrow(210, 155, 245, 155, color=LINE, sw=2))
    f.append(text(227, 142, "OK", size=10, bold=True, color=FIELD))

    # Стан 2: Classification
    f.append(rect(245, 65, 185, 180, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(255, 75, 165, 32, "2. Класифікація", size=11, bold=True, fill="#e2e8f0"))
    f.append(mtext(337, 130, "Напруга: 14.5...20.5 В\nВимір струму класу:\nКлас 0...8 (0.44...90 Вт)\n\n1-Event: 802.3af (до 15.4 Вт)\n2-Event: 802.3at (30 Вт)\nMulti-Event: 802.3bt", size=10, anchor="middle"))

    # Стрілка 2 -> 3
    f.append(arrow(430, 155, 465, 155, color=LINE, sw=2))
    f.append(text(447, 142, "OK", size=10, bold=True, color=FIELD))

    # Стан 3: Startup / Inrush
    f.append(rect(465, 65, 185, 180, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(475, 75, 165, 32, "3. Запуск (Power-Up)", size=11, bold=True, fill="#fee2e2", stroke=POS))
    f.append(mtext(557, 130, "Наростання: до 48...57 В\nОбмеження пускового\nструму (Inrush Limit):\nI_inrush ≤ 400...450 мА\n\nЗаряд C_bulk на PD\nUVLO перемикання", size=10, anchor="middle"))

    # Стрілка 3 -> 4
    f.append(arrow(650, 155, 685, 155, color=LINE, sw=2))
    f.append(text(667, 142, "OK", size=10, bold=True, color=FIELD))

    # Стан 4: Normal Operation & Monitoring
    f.append(rect(685, 65, 175, 180, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(fitbox(695, 75, 155, 32, "4. Робота й моніторинг", size=11, bold=True, fill="#ecfdf5", stroke=FIELD))
    f.append(mtext(772, 130, "Повна потужність:\n48...57 В навантаження\n\nКонтроль струму MPS:\nI ≥ 10 мА (802.3af/at)\nабо Short MPS (bt)\nЗахист OCP / SCP", size=10, anchor="middle"))

    # Нижня стрілка повернення / розриву (Disconnect / Fault)
    f.append(line(772, 245, 772, 310, color=NEG, sw=1.8))
    f.append(line(772, 310, 117, 310, color=NEG, sw=1.8))
    f.append(arrow(117, 310, 117, 245, color=NEG, sw=1.8))
    f.append(fitbox(280, 290, 320, 36, "Від'єднання або перевантаження (Disconnect / OCP)\nЗняття напруги за < 10...350 мс → Перехід до детекції", size=10.5, bold=True, fill="#eff6ff", stroke=NEG))

    # Нижній висновок-попередження
    f.append(fitbox(25, 335, 835, 25, "Звичайний мережевий порт ПК не має сигнатури 25 кОм: детекція провалюється, і небезпечні 54 В не подаються.", size=10, bold=True, fill="#fef3c7", stroke="#d97706"))

    render(os.path.join(IMG, "poe-state-machine.svg"), W, H, *f)


def fig_power_modes_pinout():
    """Фігура 3: Порівняння способів подачі напруги (Alternative A, Alternative B, 4PPoE)."""
    W, H = 880, 380
    f = []

    f.append(rect(0, 0, W, H, fill=BG, stroke=LINE, sw=1, rx=0))
    f.append(text(W / 2, 28, "Розподіл сигналів і живлення на контактах 8P8C (RJ-45)", size=15, bold=True))

    cols = [
        ("Alternative A (Endspan)", 25, "Подача по сигнальних парах (1-2 та 3-6)", "#eff6ff", "#3b82f6"),
        ("Alternative B (Midspan)", 310, "Подача по вільних парах (4-5 та 7-8)", "#f0fdf4", "#22c55e"),
        ("4PPoE / 802.3bt (Type 3 & 4)", 595, "Живлення по всіх 4 парах одночасно", "#fef2f2", "#ef4444")
    ]

    mode_a = ["DC + (Data)", "DC + (Data)", "DC − (Data)", "Лише дані", "Лише дані", "DC − (Data)", "Лише дані", "Лише дані"]
    mode_b = ["Лише дані", "Лише дані", "Лише дані", "DC + (Spare)", "DC + (Spare)", "Лише дані", "DC − (Spare)", "DC − (Spare)"]
    mode_4p = ["DC + (Data 1)", "DC + (Data 1)", "DC − (Data 2)", "DC + (Data 3)", "DC + (Data 3)", "DC − (Data 2)", "DC − (Data 4)", "DC − (Data 4)"]

    for col_idx, (title, left_x, subtitle, bg_col, stroke_col) in enumerate(cols):
        f.append(rect(left_x, 50, 260, 315, fill=bg_col, stroke=stroke_col, sw=1.5, rx=8))
        f.append(text(left_x + 130, 72, title, size=12, bold=True, color=INK))
        f.append(text(left_x + 130, 89, subtitle, size=9.5, color=MUTED))

        cur_mode = [mode_a, mode_b, mode_4p][col_idx]

        for p_i in range(8):
            py = 105 + p_i * 26
            val = cur_mode[p_i]

            # Колір комірки
            if "DC +" in val:
                c_fill = "#fee2e2"
                c_text = POS
            elif "DC −" in val:
                c_fill = "#dbeafe"
                c_text = NEG
            else:
                c_fill = "#ffffff"
                c_text = "#64748b"

            f.append(rect(left_x + 12, py, 50, 22, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
            f.append(text(left_x + 37, py + 15, f"Pin {p_i+1}", size=9.5, bold=True, color=INK))

            f.append(rect(left_x + 68, py, 180, 22, fill=c_fill, stroke="#cbd5e1", sw=1, rx=3))
            f.append(text(left_x + 158, py + 15, val, size=9.5, bold=True, color=c_text))

        # Примітка внизу колонки
        if col_idx == 0:
            f.append(text(left_x + 130, 350, "Сумісно з 10/100/1000BASE-T", size=9, italic=True, color=MUTED))
        elif col_idx == 1:
            f.append(text(left_x + 130, 350, "Прості інжектори Midspan", size=9, italic=True, color=MUTED))
        else:
            f.append(text(left_x + 130, 350, "До 90–100 Вт, 4 пари", size=9, italic=True, color=MUTED))

    render(os.path.join(IMG, "power-modes-pinout.svg"), W, H, *f)


def main():
    fig_phantom_power()
    fig_poe_state_machine()
    fig_power_modes_pinout()
    print("Фігури PoE згенеровано успішно.")


if __name__ == '__main__':
    main()

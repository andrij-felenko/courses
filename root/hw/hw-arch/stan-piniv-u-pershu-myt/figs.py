# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Стан пінів у першу мить'."""

import sys
import os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від root/hw/hw-arch/stan-piniv-u-pershu-myt)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")


def make_timing_fig():
    """Фігура 1: Часова діаграма станів піна від подачі VDD до старту main()."""
    w, h = 1060, 560
    frags = []

    # Заголовок фігури
    frags.append(text(w / 2, 28, "Хронологія станів виводів мікроконтролера під час запуску", size=16, bold=True))

    # Рамка зони небезпеки (fill="none" щоб не конфліктувати з внутрішніми блоками)
    hazard_x1, hazard_x2 = 210, 750
    frags.append(rect(hazard_x1, 52, hazard_x2 - hazard_x1, 418, fill="none", stroke="#e74c3c", sw=2.0, rx=6))
    frags.append(textbox((hazard_x1 + hazard_x2) / 2, 72, "Критичне вікно вразливості: пін у стані Hi-Z / Floating (100 µs – 50 ms)", size=12, pad=6, fill="#fde8e8", stroke="#c0392b", color=POS, bold=True)[0])

    # Рамка зони безпечної роботи прошивки
    frags.append(rect(750, 52, 240, 418, fill="none", stroke="#27ae60", sw=2.0, rx=6))
    frags.append(textbox(870, 72, "Штатний контроль прошивки", size=12, pad=6, fill="#e8f8f0", stroke="#27ae60", color=FIELD, bold=True)[0])

    # Ліва колонка назв сигналів
    sig_x = 105
    y_vdd = 125
    y_rst = 195
    y_clk = 265
    y_cpu = 340
    y_pin = 425

    frags.append(textbox(sig_x, y_vdd, "Живлення VDD\n(0В → 3.3В)", size=12, pad=6, fill="#f8f9fa", stroke="#7f8c8d", bold=True)[0])
    frags.append(textbox(sig_x, y_rst, "Скидання RESET_N\n(Внутрішній POR)", size=12, pad=6, fill="#f8f9fa", stroke="#7f8c8d", bold=True)[0])
    frags.append(textbox(sig_x, y_clk, "Тактування Core\n(RC / HSI / PLL)", size=12, pad=6, fill="#f8f9fa", stroke="#7f8c8d", bold=True)[0])
    frags.append(textbox(sig_x, y_cpu, "Стан процесора\n(Фаза виконання)", size=12, pad=6, fill="#f8f9fa", stroke="#7f8c8d", bold=True)[0])
    frags.append(textbox(sig_x, y_pin, "Фізичний стан GPIO\n(Вихідний каскад)", size=12, pad=6, fill="#f8f9fa", stroke="#7f8c8d", bold=True)[0])

    # Часові опорні точки (вертикальні лінії)
    t_coords = [210, 310, 450, 600, 750, 990]
    t_labels = ["t0: Подача VDD", "t1: Поріг V_POR+", "t2: Reset Release", "t3: Bootloader", "t4: SystemInit", "t5: main()"]

    for i, tx in enumerate(t_coords):
        frags.append(line(tx, 90, tx, 475, color="#bdc3c7", sw=1.0, dash="3,3"))
        frags.append(text(tx, 492, t_labels[i], size=11, color="#2c3e50", bold=True))

    # 1. Сигнал VDD
    frags.append(line(210, y_vdd + 18, 310, y_vdd + 2, color=POS, sw=2.5))
    frags.append(line(310, y_vdd + 2, 450, y_vdd - 15, color=POS, sw=2.5))
    frags.append(line(450, y_vdd - 15, 990, y_vdd - 15, color=POS, sw=2.5))
    frags.append(text(380, y_vdd - 20, "Наростання VDD", size=10, color=POS))
    frags.append(text(520, y_vdd - 20, "VDD = 3.3V (стабільно)", size=10, color=POS))

    # 2. Сигнал RESET_N (POR)
    frags.append(line(210, y_rst + 15, 450, y_rst + 15, color=NEG, sw=2.5))
    frags.append(line(450, y_rst + 15, 450, y_rst - 15, color=NEG, sw=2.5))
    frags.append(line(450, y_rst - 15, 990, y_rst - 15, color=NEG, sw=2.5))
    frags.append(text(360, y_rst + 27, "RESET_N = 0 (t_POR утримання)", size=10, color=NEG))
    frags.append(text(540, y_rst - 20, "RESET_N = 1 (Ядро розблоковано)", size=10, color=NEG))

    # 3. Тактування
    frags.append(line(210, y_clk + 15, 450, y_clk + 15, color="#7f8c8d", sw=2.0))
    frags.append(line(450, y_clk + 15, 460, y_clk, color="#e67e22", sw=2.0))
    for k in range(460, 600, 10):
        frags.append(line(k, y_clk + 8, k + 5, y_clk - 8, color="#e67e22", sw=1.5))
        frags.append(line(k + 5, y_clk - 8, k + 10, y_clk + 8, color="#e67e22", sw=1.5))
    frags.append(text(525, y_clk - 14, "HSI RC (~16 МГц)", size=10, color="#d35400"))
    for k in range(600, 990, 8):
        frags.append(line(k, y_clk + 10, k + 4, y_clk - 10, color="#27ae60", sw=1.8))
        frags.append(line(k + 4, y_clk - 10, k + 8, y_clk + 10, color="#27ae60", sw=1.8))
    frags.append(text(795, y_clk - 14, "PLL Locked (Повна тактова частота)", size=10, color="#27ae60"))

    # 4. Процесор (Блоки станів)
    frags.append(fitbox(210, y_cpu - 18, 100, 36, "Живлення OFF", size=11, fill="#ecf0f1", stroke="#95a5a6", bold=True))
    frags.append(fitbox(310, y_cpu - 18, 140, 36, "Апаратне скидання\n(POR Active)", size=10, fill="#fbeee6", stroke="#e67e22", bold=True))
    frags.append(fitbox(450, y_cpu - 18, 150, 36, "ROM Bootloader\n(Опитування шин)", size=10, fill="#fcf3cf", stroke="#f39c12", bold=True))
    frags.append(fitbox(600, y_cpu - 18, 150, 36, "Reset_Handler\n(SystemInit)", size=10, fill="#e8f8f5", stroke="#1abc9c", bold=True))
    frags.append(fitbox(750, y_cpu - 18, 240, 36, "Виконання main() користувача", size=11, fill="#d5f5e3", stroke="#27ae60", color="#1e8449", bold=True))

    # 5. Стан піна
    frags.append(fitbox(210, y_pin - 20, 100, 42, "Суб-пороговий\nхаос (Float)", size=10, fill="#fadbd8", stroke="#e74c3c", color=POS, bold=True))
    frags.append(fitbox(310, y_pin - 20, 140, 42, "Hi-Z / Слабкий Pull\n(Виходи вимкнено)", size=10, fill="#fadbd8", stroke="#e74c3c", color=POS, bold=True))
    frags.append(fitbox(450, y_pin - 20, 150, 42, "Hi-Z / Плаваючий\n(Ризик наводок)", size=10, fill="#fadbd8", stroke="#e74c3c", color=POS, bold=True))
    frags.append(fitbox(600, y_pin - 20, 150, 42, "Конфігурація ODR\nта перемикання MODER", size=10, fill="#fef9e7", stroke="#f1c40f", color="#7d6608", bold=True))
    frags.append(fitbox(750, y_pin - 20, 240, 42, "Активний вихід (Push-Pull Low / High)\nСтабільний визначений рівень", size=10, fill="#d4efdf", stroke="#27ae60", color="#196f3d", bold=True))

    # Нижня шкала часу
    frags.append(arrow(180, 525, 1000, 525, color=LINE, sw=1.8))
    frags.append(text(1020, 529, "Час (t)", size=12, color=INK, bold=True))

    return render(os.path.join(OUT_DIR, "power-on-gpio-timing.svg"), w, h, *frags)


def make_miller_fig():
    """Фігура 2: Схема впливу ємності Міллера та захисту затвора MOSFET."""
    w, h = 1060, 520
    frags = []

    frags.append(text(w / 2, 26, "Апаратний захист затвора MOSFET від помилкового відкриття струмом Міллера", size=16, bold=True))

    # Ліва панель: НЕБЕЗПЕЧНО
    left_x, left_w = 40, 470
    frags.append(rect(left_x, 50, left_w, 440, fill="none", stroke="#e74c3c", sw=2.0, rx=8))
    frags.append(textbox(left_x + left_w / 2, 75, "НЕБЕЗПЕЧНО: Пін MCU у стані Hi-Z або слабка підтяжка 40 кОм", size=12, pad=6, fill="#fadbd8", stroke="#c0392b", color=POS, bold=True)[0])

    # Права панель: БЕЗПЕЧНО
    right_x, right_w = 550, 470
    frags.append(rect(right_x, 50, right_w, 440, fill="none", stroke="#27ae60", sw=2.0, rx=8))
    frags.append(textbox(right_x + right_w / 2, 75, "БЕЗПЕЧНО: Зовнішній жорсткий Pull-Down 4.7 кОм + Clamp", size=12, pad=6, fill="#d4efdf", stroke="#27ae60", color=FIELD, bold=True)[0])

    # Елементи лівої панелі
    # Блок MCU
    frags.append(rect(65, 120, 110, 130, fill="#eaeded", stroke="#7f8c8d", sw=1.5, rx=4))
    frags.append(text(120, 145, "MCU GPIO", size=12, bold=True))
    frags.append(text(120, 170, "Стан: Hi-Z", size=11, color=POS, bold=True))
    frags.append(text(120, 195, "R_int ≈ 40 кОм", size=11, color="#7f8c8d"))
    frags.append(text(120, 220, "(Слабкий pull)", size=10, color="#7f8c8d"))

    # Лінія від MCU до затвора
    frags.append(line(175, 180, 290, 180, color=POS, sw=2.0))
    frags.append(circle(290, 180, 4, fill=POS, stroke=POS))

    # Схема MOSFET ліворуч
    m_x = 330
    # Drain лінія
    frags.append(line(m_x + 30, 120, m_x + 30, 160, color=LINE, sw=2.5))
    frags.append(textbox(m_x + 30, 105, "+48V Швидке наростання (dV/dt)", size=11, pad=5, fill="#fbeee6", stroke="#e67e22", color="#d35400", bold=True)[0])
    # Канал
    frags.append(line(m_x + 10, 160, m_x + 30, 160, color=LINE, sw=2.0))
    frags.append(line(m_x + 10, 200, m_x + 30, 200, color=LINE, sw=2.0))
    frags.append(line(m_x + 10, 155, m_x + 10, 205, color=LINE, sw=3.0))
    frags.append(line(m_x, 160, m_x, 200, color=LINE, sw=2.0))
    frags.append(line(290, 180, m_x, 180, color=LINE, sw=2.0))
    # Source лінія
    frags.append(line(m_x + 30, 200, m_x + 30, 240, color=LINE, sw=2.5))
    frags.append(line(m_x + 20, 240, m_x + 40, 240, color=LINE, sw=2.0))
    frags.append(text(m_x + 30, 255, "GND (Силова земля)", size=10))

    # Ємність Міллера C_gd (паразитна)
    frags.append(rect(m_x - 35, 125, 45, 26, fill="#fde8e8", stroke="#c0392b", sw=1.5, rx=3))
    frags.append(text(m_x - 12, 142, "C_gd", size=11, color=POS, bold=True))
    frags.append(line(m_x + 30, 138, m_x + 10, 138, color=POS, sw=1.5, dash="2,2"))
    frags.append(line(m_x - 35, 138, 290, 138, color=POS, sw=1.5, dash="2,2"))
    frags.append(line(290, 138, 290, 180, color=POS, sw=1.5))

    # Струм Міллера i_Miller стрілка
    frags.append(arrow(m_x + 10, 138, m_x - 35, 138, color=POS, sw=2.0))
    frags.append(text(250, 160, "i_Miller = C_gd · dV/dt", size=10, color=POS, bold=True))

    # Пояснювальний блок ліворуч внизу
    frags.append(fitbox(left_x + 15, 280, left_w - 30, 190,
                        "Механізм аварії:\n"
                        "1. При включенні живлення 48В виникає dV_DS/dt > 5 В/нс.\n"
                        "2. Струм i_Miller протікає через C_gd у затвор.\n"
                        "3. Опір виводу MCU високий (Hi-Z або R_int = 40 кОм).\n"
                        "4. Напруга V_GS = i_Miller · R_int перевищує поріг V_th (2В).\n"
                        "5. MOSFET відкривається → Наскрізний струм (Shoot-Through)\n"
                        "та миттєвий вибух силового напівмоста!",
                        size=11, pad=10, fill="#fdedec", stroke="#e74c3c", color=INK))

    # Елементи правої панелі
    # Блок MCU
    frags.append(rect(575, 120, 110, 130, fill="#eaeded", stroke="#7f8c8d", sw=1.5, rx=4))
    frags.append(text(630, 145, "MCU GPIO", size=12, bold=True))
    frags.append(text(630, 170, "Стан: Hi-Z", size=11, color="#7f8c8d"))
    frags.append(text(630, 195, "До ініціалізації", size=10, color="#7f8c8d"))
    frags.append(text(630, 220, "в SystemInit()", size=10, color="#7f8c8d"))

    # Лінія від MCU до затвора
    frags.append(line(685, 180, 800, 180, color=LINE, sw=2.0))
    frags.append(circle(800, 180, 4, fill=FIELD, stroke=FIELD))

    # Жорсткий Pull-Down резистор (4.7 кОм)
    frags.append(rect(745, 205, 30, 50, fill="#e8f8f0", stroke="#27ae60", sw=2.0, rx=3))
    frags.append(text(760, 235, "R_PD", size=10, color=FIELD, bold=True))
    frags.append(line(760, 180, 760, 205, color=FIELD, sw=2.0))
    frags.append(line(760, 255, 760, 275, color=FIELD, sw=2.0))
    frags.append(line(750, 275, 770, 275, color=LINE, sw=2.0))
    frags.append(text(760, 290, "4.7 кОм (GND)", size=10, color=FIELD, bold=True))

    # Схема MOSFET праворуч
    r_m_x = 840
    # Drain лінія
    frags.append(line(r_m_x + 30, 120, r_m_x + 30, 160, color=LINE, sw=2.5))
    frags.append(textbox(r_m_x + 30, 105, "+48V Швидке наростання (dV/dt)", size=11, pad=5, fill="#fbeee6", stroke="#e67e22", color="#d35400", bold=True)[0])
    # Канал
    frags.append(line(r_m_x + 10, 160, r_m_x + 30, 160, color=LINE, sw=2.0))
    frags.append(line(r_m_x + 10, 200, r_m_x + 30, 200, color=LINE, sw=2.0))
    frags.append(line(r_m_x + 10, 155, r_m_x + 10, 205, color=LINE, sw=3.0))
    frags.append(line(r_m_x, 160, r_m_x, 200, color=LINE, sw=2.0))
    frags.append(line(800, 180, r_m_x, 180, color=LINE, sw=2.0))
    # Source лінія
    frags.append(line(r_m_x + 30, 200, r_m_x + 30, 240, color=LINE, sw=2.5))
    frags.append(line(r_m_x + 20, 240, r_m_x + 40, 240, color=LINE, sw=2.0))
    frags.append(text(r_m_x + 30, 255, "GND (Силова земля)", size=10))

    # Ємність C_gd
    frags.append(rect(r_m_x - 35, 125, 45, 26, fill="#e8f8f0", stroke="#27ae60", sw=1.5, rx=3))
    frags.append(text(r_m_x - 12, 142, "C_gd", size=11, color=FIELD, bold=True))
    frags.append(line(r_m_x + 30, 138, r_m_x + 10, 138, color=FIELD, sw=1.5, dash="2,2"))
    frags.append(line(r_m_x - 35, 138, 800, 138, color=FIELD, sw=1.5, dash="2,2"))
    frags.append(line(800, 138, 800, 180, color=FIELD, sw=1.5))

    # Струм шунтується через R_PD
    frags.append(arrow(800, 145, 760, 200, color=FIELD, sw=2.0))
    frags.append(text(710, 160, "Шунтування струму", size=10, color=FIELD, bold=True))

    # Пояснювальний блок праворуч внизу
    frags.append(fitbox(right_x + 15, 305, right_w - 30, 165,
                        "Фізика надійного захисту:\n"
                        "1. Резистор R_PD = 4.7 кОм розпаяний безпосередньо біля затвора.\n"
                        "2. Струм i_Miller скидається на GND через низький опір R_PD.\n"
                        "3. Напруга на затворі V_GS = i_Miller · R_PD < 0.4В.\n"
                        "4. Напруга суворо нижче порога V_th (2В) за будь-якого стану MCU.\n"
                        "5. Гарантований захист від наскрізного струму при включенні.",
                        size=11, pad=10, fill="#eafaf1", stroke="#27ae60", color=INK))

    return render(os.path.join(OUT_DIR, "miller-effect-gate-safety.svg"), w, h, *frags)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    f1 = make_timing_fig()
    f2 = make_miller_fig()
    print("Generated figures:")
    print(" ", f1)
    print(" ", f2)

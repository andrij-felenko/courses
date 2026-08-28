# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Figure 1: Три методи апаратного кодування Board ID ──────────────────────
def fig_board_id_methods():
    W, H = 960, 420
    p = []

    p.append(text(480, 28, "Способи апаратного кодування ревізії друкованої плати", size=15, bold=True))

    # Стовпець 1: Резистивний дільник на АЦП
    p.append(rect(20, 50, 295, 350, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(textbox(167, 80, "Резистивний дільник АЦП", size=13, bold=True, color=NEG)[0])
    p.append(textbox(167, 115, "1 аналоговий пін MCU\n4..16 ревізій на плату", size=11, color=MUTED)[0])

    p.append(rect(40, 150, 255, 140, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(167, 172, "Схема: R1 (до VDD) + R2 (до GND)", size=10, bold=True))
    p.append(line(167, 185, 167, 205, color=POS, sw=2))
    p.append(text(167, 198, "VDD (3.3 В)", size=9, color=POS, anchor="start"))
    p.append(rect(147, 205, 40, 20, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    p.append(text(167, 219, "R1", size=10, bold=True, color=POS))
    p.append(line(167, 225, 167, 245, color=LINE, sw=2))
    p.append(circle(167, 235, 3, fill=NEG, stroke=NEG))
    p.append(arrow(167, 235, 230, 235, color=NEG, sw=1.8))
    p.append(text(250, 239, "АЦП", size=10, bold=True, color=NEG))
    p.append(rect(147, 245, 40, 20, fill="#e0f2fe", stroke=NEG, sw=1.2, rx=3))
    p.append(text(167, 259, "R2", size=10, bold=True, color=NEG))
    p.append(line(167, 265, 167, 280, color=LINE, sw=2))
    p.append(line(152, 280, 182, 280, color=LINE, sw=2))
    p.append(text(167, 275, "GND", size=9, color=MUTED, anchor="start"))

    p.append(textbox(167, 330, "+ Економія пінів (рівно 1 ніжка)\n- Залежність від допуску резисторів\n- Постійний витік струму (потрібен ключ)", size=10, pad=8, fill="#f1f5f9", stroke="#94a3b8")[0])

    # Стовпець 2: Бітова маска GPIO / Strapping
    p.append(rect(332, 50, 295, 350, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(textbox(479, 80, "Цифрова маска GPIO", size=13, bold=True, color=FIELD)[0])
    p.append(textbox(479, 115, "N пінів MCU (Strapping / Pulls)\n2^N комбінацій (або 3^N із Hi-Z)", size=11, color=MUTED)[0])

    p.append(rect(352, 150, 255, 140, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(479, 172, "Підтяжки VDD / GND на пінах", size=10, bold=True))
    
    # 3 піни
    pins = [("GPIO_0 (Rev.0)", "1", POS, "#fee2e2"), ("GPIO_1 (Rev.1)", "0", MUTED, "#f1f5f9"), ("GPIO_2 (Rev.2)", "1", POS, "#fee2e2")]
    for idx, (plabel, val, col, bg) in enumerate(pins):
        py = 195 + idx * 30
        p.append(rect(365, py - 10, 140, 22, fill=bg, stroke=col, sw=1, rx=4))
        p.append(text(435, py + 5, plabel, size=10, color=col))
        p.append(arrow(505, py + 1, 545, py + 1, color=col, sw=1.5))
        p.append(rect(545, py - 10, 45, 22, fill=col, stroke=col, sw=1, rx=4))
        p.append(text(567, py + 6, "Bit %s" % val, size=10, bold=True, color="#ffffff"))

    p.append(textbox(479, 330, "+ Максимальна завадостійкість (0/1)\n+ Мультиплексування зі strapping-пінами\n- Витрата 2..4 цифрових виводів", size=10, pad=8, fill="#f1f5f9", stroke="#94a3b8")[0])

    # Стовпець 3: Енергонезалежна пам'ять OTP / EEPROM
    p.append(rect(645, 50, 295, 350, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(textbox(792, 80, "Пам'ять OTP / EEPROM", size=13, bold=True, color="#d97706")[0])
    p.append(textbox(792, 115, "I2C / 1-Wire / Внутрішні eFuse\nНеобмежена кількість метаданих", size=11, color=MUTED)[0])

    p.append(rect(665, 150, 255, 140, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(792, 172, "Структурований дескриптор TLV", size=10, bold=True))

    p.append(rect(680, 190, 225, 22, fill="#fef3c7", stroke="#d97706", sw=1, rx=3))
    p.append(text(792, 205, "Magic [0x504342] + Rev [0x0201]", size=9, bold=True, color="#92400e"))
    p.append(rect(680, 218, 225, 22, fill="#fef3c7", stroke="#d97706", sw=1, rx=3))
    p.append(text(792, 233, "Serial No: \"HW-2026-X891\"", size=9, color="#92400e"))
    p.append(rect(680, 246, 225, 22, fill="#fef3c7", stroke="#d97706", sw=1, rx=3))
    p.append(text(792, 261, "CRC-16 / Калібрувальні зміщення", size=9, color="#92400e"))

    p.append(textbox(792, 330, "+ Зберігає ревізію, серійник і калибрування\n+ Не потребує зміни розведення плати\n- Вимагає прошивки під час тесту (ICT)", size=10, pad=8, fill="#f1f5f9", stroke="#94a3b8")[0])

    render(os.path.join(OUT, "board-id-methods.svg"), W, H, *p)


# ── Figure 2: Вікна напруг і розрахунок допусків для АЦП Board ID ───────────
def fig_adc_revision_windows():
    W, H = 940, 440
    p = []

    p.append(text(470, 28, "Діапазони напруг і захисні інтервали АЦП для 8 ревізій плати (3.3 В, 12 біт)", size=14, bold=True))

    # Вісь напруги
    axis_x0 = 80
    axis_x1 = 860
    axis_y = 120
    axis_w = axis_x1 - axis_x0

    p.append(line(axis_x0, axis_y, axis_x1, axis_y, color=LINE, sw=2.5))
    p.append(arrow(axis_x1, axis_y, axis_x1 + 30, axis_y, color=LINE, sw=2.5))
    p.append(text(axis_x1 + 45, axis_y + 4, "Напруга (В)", size=11, bold=True, anchor="start"))

    # Позначки шкали
    ticks = [(0.0, "0 В\n(код 0)"), (0.825, "0.825 В\n(код 1024)"), (1.65, "1.65 В\n(код 2048)"), (2.475, "2.475 В\n(код 3072)"), (3.3, "3.3 В\n(код 4095)")]
    for v, tlabel in ticks:
        tx = axis_x0 + (v / 3.3) * axis_w
        p.append(line(tx, axis_y - 8, tx, axis_y + 8, color=LINE, sw=1.5))
        p.append(mtext(tx, axis_y + 24, tlabel, size=10, color=MUTED))

    # 8 зон ревізій
    rev_data = [
        ("Rev 0", 0.206, "#fee2e2", POS),
        ("Rev 1", 0.619, "#ffedd5", "#ea580c"),
        ("Rev 2", 1.031, "#fef9c3", "#ca8a04"),
        ("Rev 3", 1.444, "#dcfce7", FIELD),
        ("Rev 4", 1.856, "#ccfbf1", "#0d9488"),
        ("Rev 5", 2.269, "#e0e7ff", "#4338ca"),
        ("Rev 6", 2.681, "#fae8ff", "#a21caf"),
        ("Rev 7", 3.094, "#f1f5f9", LINE),
    ]

    bin_width_v = 3.3 / 8.0  # 0.4125 V
    for idx, (rname, v_nom, bg_col, border_col) in enumerate(rev_data):
        v_start = idx * bin_width_v
        v_end = (idx + 1) * bin_width_v
        x_start = axis_x0 + (v_start / 3.3) * axis_w
        x_end = axis_x0 + (v_end / 3.3) * axis_w
        w_box = x_end - x_start
        x_nom = axis_x0 + (v_nom / 3.3) * axis_w

        # Прямокутник зони
        p.append(rect(x_start + 2, 190, w_box - 4, 110, fill=bg_col, stroke=border_col, sw=1.4, rx=4))
        p.append(text(x_nom, 215, rname, size=12, bold=True, color=border_col))
        p.append(text(x_nom, 235, "V_ном ≈ %.2f В" % v_nom, size=10, color=INK))
        p.append(text(x_nom, 255, "ADC: %d" % int(round((v_nom / 3.3) * 4095)), size=9, color=MUTED))
        p.append(text(x_nom, 280, "±%.2f В вікно" % (bin_width_v / 2.0), size=9, color=MUTED))

        # Лінія від шкали до зони
        p.append(line(x_nom, axis_y - 2, x_nom, 190, color=border_col, sw=1.2, dash="3,3"))
        p.append(circle(x_nom, axis_y, 3.5, fill=border_col, stroke=border_col))

        # Межові маркери
        if idx > 0:
            p.append(line(x_start, 185, x_start, 305, color="#94a3b8", sw=1, dash="2,2"))

    # Пояснення допусків унизу
    p.append(rect(50, 325, 840, 95, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(470, 345, "Захисний інтервал розраховано під резистори ряду E24/E96 з допуском 1% та шум АЦП ±15 LSB", size=11, bold=True, color=INK))
    p.append(text(470, 368, "Ширина робочого вікна ревізії: ΔV = 412.5 мВ (512 відліків 12-бітного АЦП)", size=10, color=MUTED))
    p.append(text(470, 390, "Максимальна сумарна похибка дільника + АЦП: < 120 мВ. Запас надійності декодування > 3.4×", size=10, bold=True, color=FIELD))

    render(os.path.join(OUT, "adc-revision-windows.svg"), W, H, *p)


# ── Figure 3: Конвеєр динамічного завантаження та диспетчеризації BSP ────────
def fig_bsp_dynamic_dispatch():
    W, H = 960, 470
    p = []

    p.append(text(480, 26, "Архітектура єдиної прошивки: динамічна диспетчеризація драйверів за Board ID", size=14, bold=True))

    steps = [
        ("Етап 1: Старт", "Power-On Reset\nМінімальна ініціалізація ядра\nТактування системної шини", "#f8fafc", LINE),
        ("Етап 2: Зчитування ID", "Опитування ADC дільника\nАБО зчитування GPIO strapping\nАБО читання eFuse/EEPROM", "#eff6ff", NEG),
        ("Етап 3: Селектор плати", "Пошук ревізії в таблиці дескрипторів\nПеревірка CRC метаданих\nFallback на safe-mode при помилці", "#fef3c7", "#d97706"),
        ("Етап 4: Диспетчеризація", "Конфігурація Pinmux під плату\nРеєстрація таблиць драйверів (VMT)\nПрив'язка калібрувальних коефіцієнтів", "#dcfce7", FIELD),
        ("Етап 5: Застосунок", "Запуск бізнес-логіки та RTOS\nУніфіковані виклики через HAL\nНуль знань про залізо в додатку", "#f5f3ff", "#7c3aed"),
    ]

    card_w = 170
    card_h = 135
    start_x = 25
    step_gap = 22

    for i, (stitle, sbody, bg, col) in enumerate(steps):
        cx = start_x + i * (card_w + step_gap)
        cy = 55
        p.append(rect(cx, cy, card_w, card_h, fill=bg, stroke=col, sw=1.6, rx=6))
        p.append(text(cx + card_w / 2, cy + 22, stitle, size=11, bold=True, color=col))
        p.append(line(cx + 10, cy + 32, cx + card_w - 10, cy + 32, color=col, sw=1, dash="2,2"))
        lines = sbody.split("\n")
        for l_idx, line_txt in enumerate(lines):
            p.append(text(cx + card_w / 2, cy + 52 + l_idx * 24, line_txt, size=9.5, color=INK))

        # Стрілка між кроками
        if i < len(steps) - 1:
            arr_x1 = cx + card_w + 3
            arr_x2 = arr_x1 + step_gap - 6
            p.append(arrow(arr_x1, cy + card_h / 2, arr_x2, cy + card_h / 2, color=LINE, sw=2))

    # Нижня частина: Таблиця дескрипторів і віртуальні інтерфейси
    p.append(rect(25, 215, 430, 235, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(240, 240, "Таблиця дескрипторів плат (Flash const)", size=12, bold=True, color=NEG))

    p.append(rect(45, 255, 390, 50, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=4))
    p.append(text(240, 273, "Board_Rev_A (ID=0x01): SPI1 (PA5..PA7), IMU=BMI270", size=10, bold=True, color=INK))
    p.append(text(240, 293, "Calib: Accel_Gain=1.002, Display_Type=ST7789", size=9, color=MUTED))

    p.append(rect(45, 315, 390, 50, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=4))
    p.append(text(240, 333, "Board_Rev_B (ID=0x02): SPI2 (PB13..PB15), IMU=LSM6DSO", size=10, bold=True, color=INK))
    p.append(text(240, 353, "Calib: Accel_Gain=0.994, Display_Type=ILI9341", size=9, color=MUTED))

    p.append(rect(45, 375, 390, 55, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=4))
    p.append(text(240, 393, "Board_Rev_C (ID=0x03): SPI1 (PA5..PA7), IMU=ICM42688", size=10, bold=True, color=INK))
    p.append(text(240, 413, "Calib: Accel_Gain=1.015, Display_Type=ST7789V3", size=9, color=MUTED))

    # Стрілка між дескриптором і драйверами
    p.append(arrow(455, 332, 505, 332, color=FIELD, sw=2.5))
    p.append(text(480, 320, "Bind", size=11, bold=True, color=FIELD))

    # Блок драйверів
    p.append(rect(505, 215, 430, 235, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(720, 240, "Уніфікований інтерфейс драйвера (HAL / C++ Interface)", size=12, bold=True, color=FIELD))

    p.append(rect(525, 255, 390, 40, fill="#ffffff", stroke="#86efac", sw=1.2, rx=4))
    p.append(text(720, 278, "imu_driver_t -> read_gyro(), read_accel(), self_test()", size=10, bold=True, color=FIELD))

    p.append(rect(525, 305, 390, 40, fill="#ffffff", stroke="#86efac", sw=1.2, rx=4))
    p.append(text(720, 328, "display_driver_t -> draw_pixel(), fill_rect(), flush()", size=10, bold=True, color=FIELD))

    p.append(rect(525, 355, 390, 75, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(720, 375, "Результат для прикладного коду:", size=10, bold=True, color=INK))
    p.append(text(720, 395, "g_imu->read_accel(&data); // Працює на всіх трьох платах", size=10, color=NEG))
    p.append(text(720, 415, "Бінарник прошивки єдиний для всього парку пристроїв", size=9, color=MUTED))

    render(os.path.join(OUT, "bsp-dynamic-dispatch.svg"), W, H, *p)


if __name__ == "__main__":
    fig_board_id_methods()
    fig_adc_revision_windows()
    fig_bsp_dynamic_dispatch()
    print("All figures generated successfully.")

# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. driver-verification-harness: Стенд випробувань драйвера на платі ────────
def fig_verification_harness():
    W, H = 940, 490
    p = []

    p.append(text(W / 2, 26, "Апаратний стенд верифікації та ін'єкції апаратних збоїв (Fault Injection)", size=15, bold=True, color=INK))

    # Ліва частина: Головний контролер (Тест-раннер / MCU)
    p.append(rect(40, 60, 240, 370, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(160, 88, "Головний мікроконтролер (MCU)", size=12, bold=True, color=INK))
    p.append(text(160, 106, "Випробуваний драйвер + Тест-раннер", size=10, color=MUTED))

    mcu_blocks = [
        (135, "Драйвер чипа (FSM & State)", "#ffffff", NEG),
        (190, "Модуль Fault Recovery (Таймаути)", "#ffffff", NEG),
        (245, "Керування комутатором збоїв (GPIO)", "#ffffff", NEG),
        (300, "Обробник переривання (ISR FIFO)", "#ffffff", NEG),
        (355, "Консоль результатів (UART / RTT)", "#ffffff", NEG),
    ]
    for y, title, fill_c, strk_c in mcu_blocks:
        p.append(rect(55, y, 210, 42, fill=fill_c, stroke=strk_c, sw=1.3, rx=4))
        p.append(text(160, y + 25, title, size=10, bold=True, color=INK))

    # Центральна частина: Комутатор апаратних збоїв (Fault Injection Matrix)
    p.append(rect(340, 60, 260, 370, fill="#fef9e7", stroke="#e67e22", sw=1.8, rx=6))
    p.append(text(470, 88, "Комутатор апаратних збоїв", size=12, bold=True, color=INK))
    p.append(text(470, 106, "Аналогові ключі та MOSFET-глітчери", size=10, color=MUTED))

    sw_blocks = [
        (135, "Розмикач шини (SDA / SCL / MISO)\nІмітація обриву та лінійного шуму", "#ffffff", "#e67e22"),
        (210, "Глітчер живлення VDD (MOSFET Low-Side)\nІмпульсне знеструмлення (1–50 мс)", "#ffffff", "#e67e22"),
        (285, "Примусова підтяжка до GND (Bus Lockup)\nІмітація зависання веденого чіпа", "#ffffff", "#e67e22"),
        (355, "Блокатор лінії переривання (INT/DRDY)\nІмітація втрати події та переповнення", "#ffffff", "#e67e22"),
    ]
    for y, desc, fill_c, strk_c in sw_blocks:
        lines = desc.split("\n")
        p.append(rect(355, y, 230, 54, fill=fill_c, stroke=strk_c, sw=1.3, rx=4))
        p.append(text(470, y + 20, lines[0], size=10, bold=True, color=INK))
        p.append(text(470, y + 38, lines[1], size=9, color=MUTED))

    # Права частина зверху: Випробуваний сенсор (DUT)
    p.append(rect(660, 60, 240, 205, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(780, 88, "Випробуваний чип (DUT Sensor)", size=12, bold=True, color=INK))
    p.append(text(780, 106, "IMU / Барометр / АЦП на платі", size=10, color=MUTED))

    dut_blocks = [
        (125, "Регістровий банк & State Machine"),
        (165, "Апаратне FIFO вибірок (32–512 B)"),
        (205, "Аналоговий тракт (MEMS / ADC)"),
    ]
    for y, title in dut_blocks:
        p.append(rect(675, y, 210, 32, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
        p.append(text(780, y + 20, title, size=10, bold=True, color=INK))

    # Права частина знизу: Вимірювач споживання
    p.append(rect(660, 280, 240, 150, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
    p.append(text(780, 306, "Профайлер струму (Power Profiler)", size=12, bold=True, color=INK))
    p.append(text(780, 324, "Шунт + Прецизійний підсилювач", size=10, color=MUTED))
    p.append(rect(675, 342, 210, 72, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(780, 365, "Динамічний замір: 10 нА – 50 мА", size=10, bold=True, color=POS))
    p.append(text(780, 385, "Аудит струмів сну та Wake-up time", size=9, color=MUTED))
    p.append(text(780, 402, "Контроль споживання аналогового тракту", size=9, color=MUTED))

    # Зв'язки між блоками
    p.append(arrow(280, 155, 340, 155, color="#e67e22", sw=1.8))
    p.append(arrow(280, 265, 340, 265, color="#e67e22", sw=1.8))
    p.append(arrow(600, 155, 660, 155, color=FIELD, sw=1.8))
    p.append(arrow(600, 235, 660, 235, color=FIELD, sw=1.8))
    p.append(arrow(780, 280, 780, 265, color=POS, sw=1.8))

    p.append(text(W / 2, 465, "Автоматизована ін'єкція збоїв верифікує відновлення драйвера без перезавантаження мікроконтролера",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "driver-verification-harness.svg"), W, H, *p,
           title="Стенд верифікації та ін'єкції збоїв")


# ── 2. i2c-bus-recovery-sequence: Відновлення шини I2C при зависанні ─────────
def fig_i2c_recovery():
    W, H = 940, 510
    p = []

    p.append(text(W / 2, 26, "Апаратна послідовність відновлення шини I2C при зависанні веденого (Bus Lockup)", size=15, bold=True, color=INK))

    # Етап 1: Зависання
    p.append(rect(40, 65, 260, 385, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
    p.append(text(170, 92, "1. Стан Bus Lockup", size=12, bold=True, color=POS))
    p.append(text(170, 112, "Ведений утримує лінію SDA = 0", size=10, color=MUTED))

    p.append(line(55, 150, 285, 150, color=LINE, sw=1.2, dash="3,3"))
    p.append(text(75, 142, "SCL (Master)", size=9, color=MUTED, anchor="left"))
    p.append(line(55, 160, 285, 160, color=LINE, sw=1.8))

    p.append(line(55, 210, 285, 210, color=LINE, sw=1.2, dash="3,3"))
    p.append(text(75, 202, "SDA (Slave)", size=9, color=MUTED, anchor="left"))
    p.append(line(55, 230, 285, 230, color=POS, sw=2.2))

    p.append(rect(55, 255, 230, 180, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(170, 276, "Причина зависання:", size=10, bold=True, color=INK))
    reasons = [
        "• Збій живлення під час читання",
        "• МК перезавантажився посеред байта",
        "• Ведений очікує ще такти SCL",
        "• Апаратний I2C контролер МК",
        "  блокується, бо шина зайнята",
        "• Нескінченний цикл while(!Ready)",
    ]
    for idx, r_txt in enumerate(reasons):
        p.append(text(65, 300 + idx * 21, r_txt, size=9, color=INK, anchor="left"))

    # Етап 2: Відновлення тактуванням GPIO
    p.append(rect(340, 65, 260, 385, fill="#fef9e7", stroke="#e67e22", sw=1.8, rx=6))
    p.append(text(470, 92, "2. Процедура 9 тактів SCL", size=12, bold=True, color="#e67e22"))
    p.append(text(470, 112, "Перемикання SCL у режим GPIO OD", size=10, color=MUTED))

    p.append(text(355, 142, "SCL (GPIO Output)", size=9, color=MUTED, anchor="left"))
    x_scl = 355
    for k in range(9):
        p.append(line(x_scl, 165, x_scl + 10, 165, color="#e67e22", sw=1.8))
        p.append(line(x_scl + 10, 165, x_scl + 10, 150, color="#e67e22", sw=1.8))
        p.append(line(x_scl + 10, 150, x_scl + 20, 150, color="#e67e22", sw=1.8))
        p.append(line(x_scl + 20, 150, x_scl + 20, 165, color="#e67e22", sw=1.8))
        x_scl += 24
    p.append(line(x_scl, 165, x_scl + 15, 165, color="#e67e22", sw=1.8))

    p.append(text(355, 202, "SDA (Sensor)", size=9, color=MUTED, anchor="left"))
    p.append(line(355, 230, 485, 230, color=POS, sw=2))
    p.append(line(485, 230, 500, 215, color=FIELD, sw=2))
    p.append(line(500, 215, 585, 215, color=FIELD, sw=2))
    p.append(text(540, 203, "SDA звільнено!", size=9, bold=True, color=FIELD))

    p.append(rect(355, 255, 230, 180, fill="#ffffff", stroke="#e67e22", sw=1.2, rx=4))
    p.append(text(470, 276, "Алгоритм прочищення:", size=10, bold=True, color=INK))
    steps = [
        "1. Деініціалізація периферії I2C",
        "2. SCL/SDA переходять у GPIO OD",
        "3. Генерація до 9 тактів SCL (100 кГц)",
        "4. Опитування SDA після кожного такту",
        "5. Формування STOP: SDA 0 → 1 при SCL=1",
        "6. Повернення пінів у режим I2C",
    ]
    for idx, s_txt in enumerate(steps):
        p.append(text(365, 300 + idx * 21, s_txt, size=9, color=INK, anchor="left"))

    # Етап 3: Відновлення та верифікація драйвера
    p.append(rect(640, 65, 260, 385, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(770, 92, "3. Відновлення стану", size=12, bold=True, color=FIELD))
    p.append(text(770, 112, "Переініціалізація регістрів сенсора", size=10, color=MUTED))

    p.append(rect(655, 140, 230, 295, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(770, 162, "Дії драйвера після розблокування:", size=10, bold=True, color=INK))

    rec_steps = [
        "1. Читання Device ID / WHO_AM_I",
        "2. Порівняння з еталонним сигнатурним",
        "   значенням (наприклад, 0x68 / 0x42)",
        "3. Програмне скидання чипа (Soft Reset)",
        "4. Завантаження конфігурації:",
        "   - Діапазони вимірювання (Full Scale)",
        "   - Частота вибірок (ODR / BW)",
        "   - Пороги FIFO та переривання",
        "5. Очищення буферів драйвера",
        "6. Повернення статусу ERR_RECOVERED",
    ]
    for idx, rec_txt in enumerate(rec_steps):
        p.append(text(665, 186 + idx * 22, rec_txt, size=9, color=INK, anchor="left"))

    # Стрілки переходу
    p.append(arrow(300, 250, 340, 250, color="#e67e22", sw=1.8))
    p.append(arrow(600, 250, 640, 250, color=FIELD, sw=1.8))

    p.append(text(W / 2, 480, "Апаратна генерація 9 тактів SCL виводить внутрішній автомат веденого чипа зі стану очікування біта даних",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "i2c-bus-recovery-sequence.svg"), W, H, *p,
           title="Алгоритм відновлення шини I2C при зависанні")


# ── 3. parasitic-powering-gpio: Паразитичне живлення через ESD діоди ────────
def fig_parasitic_powering():
    W, H = 940, 490
    p = []

    p.append(text(W / 2, 26, "Паразитичне фантомне живлення вимкненого чипа через захисні ESD-діоди GPIO", size=15, bold=True, color=INK))

    # Ліва колонка: Мікроконтролер (живлення увімкнене, 3.3 В)
    p.append(rect(40, 65, 240, 375, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(160, 92, "Мікроконтролер (MCU)", size=12, bold=True, color=INK))
    p.append(text(160, 110, "Живлення VDD_MCU = 3.3 В", size=10, bold=True, color=NEG))

    p.append(rect(55, 135, 210, 125, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(160, 155, "Вихідний буфер GPIO", size=10, bold=True, color=INK))
    p.append(text(160, 175, "Стан: Високий рівень (HIGH)", size=9.5, color=POS))
    p.append(text(160, 195, "Шини: SCL, SDA, CS, MOSI", size=9.5, color=MUTED))
    p.append(text(160, 225, "U_out ≈ 3.3 В", size=11, bold=True, color=POS))

    p.append(rect(55, 275, 210, 150, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(160, 298, "Типова помилка прошивки:", size=10, bold=True, color=POS))
    mcu_errs = [
        "• Зняли VDD із сенсора ключем,",
        "  але залишили піни МК у HIGH",
        "• Не вимкнули підтяжки Pull-up",
        "• Не перевели піни в Analog In",
    ]
    for idx, e_txt in enumerate(mcu_errs):
        p.append(text(65, 325 + idx * 24, e_txt, size=9, color=INK, anchor="left"))

    # Центральна частина: Схема витоку через ESD-діод
    p.append(rect(320, 65, 300, 375, fill="#fef9e7", stroke="#e67e22", sw=1.8, rx=6))
    p.append(text(470, 92, "Еквівалентна схема входу чипа", size=12, bold=True, color=INK))
    p.append(text(470, 110, "Шлях струму через верхній діод ESD", size=10, color=MUTED))

    # Малюнок діода та внутрішньої шини
    p.append(line(280, 195, 360, 195, color=POS, sw=2.5))
    p.append(text(315, 185, "I_leak ≈ 0.5–2 мА", size=9, bold=True, color=POS))

    p.append(circle(360, 195, 4, fill=POS, stroke=POS))
    p.append(text(360, 215, "Пін сенсора (SDA/SCL)", size=9, color=MUTED))

    # Верхній діод ESD
    p.append(line(360, 195, 470, 195, color=POS, sw=2))
    p.append(line(470, 195, 470, 230, color=POS, sw=2))
    p.append(rect(455, 230, 30, 25, fill="#fdecea", stroke=POS, sw=1.5, rx=2))
    p.append(text(470, 246, "ESD ▲", size=9.5, bold=True, color=POS))
    p.append(line(470, 255, 470, 290, color=POS, sw=2))

    p.append(rect(340, 290, 260, 48, fill="#ffffff", stroke=POS, sw=1.4, rx=4))
    p.append(text(470, 308, "Внутрішня шина VDD_INT сенсора", size=10, bold=True, color=POS))
    p.append(text(470, 326, "U_sens = 3.3 В − 0.6 В (V_diode) ≈ 2.7 В", size=9.5, bold=True, color=INK))

    p.append(rect(340, 350, 260, 75, fill="#ffffff", stroke="#e67e22", sw=1.2, rx=4))
    p.append(text(470, 370, "Наслідок для енергобюджету:", size=10, bold=True, color=INK))
    p.append(text(470, 390, "Батарея висаджується в 100 разів швидше", size=9, color=POS))
    p.append(text(470, 408, "через напівпровідний стан логіки", size=9, color=MUTED))

    # Права колонка: Випробуваний чіп (стан Brownout / Glitch)
    p.append(rect(660, 65, 240, 375, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
    p.append(text(780, 92, "Сенсор (Вимкнений VDD)", size=12, bold=True, color=INK))
    p.append(text(780, 110, "Зовнішній пін VDD = 0.0 В", size=10, bold=True, color=MUTED))

    p.append(rect(675, 135, 210, 140, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(780, 156, "Аномальний режим чипа:", size=10, bold=True, color=POS))
    chip_states = [
        "• Чип не спить і не працює",
        "• Напруга 2.7 В тримає цифрову",
        "  частину в напівскинутому стані",
        "• Регістри скидаються хаотично",
        "• При поверненні VDD = 3.3 В",
        "  сенсор не відповідає на шині",
    ]
    for idx, cs_txt in enumerate(chip_states):
        p.append(text(685, 178 + idx * 19, cs_txt, size=9, color=INK, anchor="left"))

    p.append(rect(675, 285, 210, 140, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(780, 306, "Правильне рішення в коді:", size=10, bold=True, color=FIELD))
    sol_steps = [
        "1. Перед сном: піни → Analog In",
        "2. Вимкнення Pull-up резисторів",
        "3. Відключення ліній CS/CLK",
        "4. Справжній струм сну < 1 мкА",
    ]
    for idx, sol_txt in enumerate(sol_steps):
        p.append(text(685, 330 + idx * 22, sol_txt, size=9, color=INK, anchor="left"))

    p.append(text(W / 2, 465, "Залишення високого логічного рівня на лініях зв'язку живить чіп через ESD-діоди в обхід вимкненої шини VDD",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "parasitic-powering-gpio.svg"), W, H, *p,
           title="Паразитичне фантомне живлення через ESD діоди")


# ── 4. fault-injection-matrix: Матриця стрес-тестів драйвера ─────────────────
def fig_fault_matrix():
    W, H = 940, 480
    p = []

    p.append(text(W / 2, 26, "Матриця верифікації та граничних випробувань драйвера (Stress Test Matrix)", size=15, bold=True, color=INK))

    p.append(text(130, 58, "Категорія випробування", size=11, bold=True, color=MUTED))
    p.append(text(380, 58, "Механізм апаратного впливу (Fault Injection)", size=11, bold=True, color=MUTED))
    p.append(text(730, 58, "Критерій успішного проходження тесту", size=11, bold=True, color=MUTED))

    tests = [
        ("1. Фізичний обрив\nліній шини\n(SDA/SCL/MISO)",
         "Комутація сигнальних провідників під час\nактивного DMA/IT обміну (Open-Circuit Glitch)",
         "Драйвер повертає ERR_TIMEOUT за ≤ 5 мс,\nне зависає у while(), периферія готова до обміну",
         POS, "#fdecea"),
        ("2. Короткочасний\nBrownout живлення\n(1–50 мс)",
         "Імпульсне зняття живлення VDD сенсора ключем\nпід час зняття вибірок або калібрування",
         "Драйвер фіксує невалідний Device ID, скидає чіп\nта відновлює конфігурацію без рестарту МК",
         "#e67e22", "#fef9e7"),
        ("3. Переповнення FIFO\nта залипання INT\n(Buffer Overrun)",
         "Блокування виклику обробника ISR на 500 мс\nпри безперервному потоці вибірок (500–2000 Гц)",
         "Драйвер детектує прапорець OVERRUN, вичитує\nFIFO до нуля, скидає засувку INT (DRDY = 0)",
         "#8a5fb0", "#f4ecf8"),
        ("4. Аудит глибокого\nсну та струмів\n(Power Audit)",
         "Замір споживання в режимах Sleep/Standby\nта перевірка витоків через цифрові піни",
         "Струм вузла відповідає даташиту (I_sleep ≤ 1.5 мкА),\nчас виходу на робочий режим ≤ t_settling",
         FIELD, "#eafaf1"),
    ]

    py = 105
    for cat_t, mech_t, crit_t, col, fill_c in tests:
        b_cat, w_cat, _ = textbox(130, py, cat_t, size=9.5, bold=True,
                                  fill=fill_c, stroke=col, sw=1.6, pad=6)
        p.append(b_cat)

        b_mech, w_mech, _ = textbox(380, py, mech_t, size=9, bold=False,
                                    fill="#ffffff", stroke=col, sw=1.6, pad=7)
        p.append(b_mech)

        p.append(arrow(130 + w_cat / 2 + 5, py, 380 - w_mech / 2 - 5, py, color=col, sw=1.6))

        b_crit, w_crit, _ = textbox(730, py, crit_t, size=9, bold=False,
                                    fill="#ffffff", stroke=col, sw=1.6, pad=7)
        p.append(b_crit)

        p.append(arrow(380 + w_mech / 2 + 5, py, 730 - w_crit / 2 - 5, py, color=col, sw=1.6))

        py += 85

    p.append(text(W / 2, 455, "Повний цикл випробувань гарантує стабільність прошивки при будь-яких фізичних аномаліях плати",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "fault-injection-matrix.svg"), W, H, *p,
           title="Матриця верифікації та стрес-випробувань драйвера")


if __name__ == "__main__":
    fig_verification_harness()
    fig_i2c_recovery()
    fig_parasitic_powering()
    fig_fault_matrix()
    print("All figures generated successfully.")

# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова гама теми
BUS_COL   = "#1a5276"  # синій — шина та передача
BUS_BG    = "#d6eaf8"
REG_COL   = "#b9770e"  # амбра — регістри та байти
REG_BG    = "#fdf3d6"
MATH_COL  = "#7d3c98"  # фіолетовий — поліноми та калібрування
MATH_BG   = "#f0e6fa"
SI_COL    = "#1e8449"  # зелений — фізичні SI-величини
SI_BG     = "#d5f5e3"
ERR_COL   = "#922b21"  # червоний — помилки та збої
ERR_BG    = "#fadbda"
GRAY_COL  = "#566573"
GRAY_BG   = "#eaeded"


# ── 1. sensor-driver-pipeline: Багатоетапний конвеєр обробки даних від чипа до SI ──
def fig_sensor_driver_pipeline():
    W, H = 840, 520
    p = []

    # Заголовок конвеєра та етапів
    p.append(text(W / 2, 35, "Конвеєр обробки даних: від кремнієвого сенсора до значень у SI", size=15, bold=True))

    stages = [
        ("1. Залізо чипа", "Кремнієвий сенсор\n24-бітний ADC\nNVM / OTP пам'ять", REG_BG, REG_COL),
        ("2. Транзакція шини", "I2C / SPI контролер\nDMA Burst Read\nПакет сирих байтів", BUS_BG, BUS_COL),
        ("3. Розпаковка бітів", "Склеювання байтів\nЗсуви та маски\nTwo's complement", MATH_BG, MATH_COL),
        ("4. Калібрування", "Поліноми NVM\nFixed-point Q-формат\nКрос-компенсація", MATH_BG, MATH_COL),
        ("5. Одиниці SI", "Типобезпечні типи\nПаскалі (Па), °C\nПеревірка меж ODD", SI_BG, SI_COL)
    ]

    bx, by, bw, bh = 25, 75, 140, 110
    gap = 25

    for i, (title, desc, bg, col) in enumerate(stages):
        x = bx + i * (bw + gap)
        p.append(rect(x, by, bw, bh, fill=bg, stroke=col, sw=1.8, rx=6))
        p.append(text(x + bw / 2, by + 22, title, size=11.5, color=col, bold=True))
        p.append(mtext(x + bw / 2, by + 48, desc, size=10.5, color=INK, lh=1.35))

        if i < len(stages) - 1:
            arr_x1 = x + bw + 3
            arr_x2 = x + bw + gap - 3
            p.append(arrow(arr_x1, by + bh / 2, arr_x2, by + bh / 2, color=LINE, sw=1.8))

    # Нижній детальний блок: структури даних на кожному кроці
    p.append(text(W / 2, 225, "Трансформація структур даних у пам'яті мікроконтролера", size=13, bold=True, color=BUS_COL))

    # Блок сирих регістрів
    rx1, ry1, rw1, rh1 = 35, 255, 230, 215
    p.append(rect(rx1, ry1, rw1, rh1, fill=REG_BG, stroke=REG_COL, sw=1.5, rx=5))
    p.append(text(rx1 + rw1 / 2, ry1 + 20, "Сирий буфер DMA (uint8_t[6])", size=11, color=REG_COL, bold=True))
    regs_demo = [
        "buf[0]: 0x5C (PRESS_MSB, біти 19..12)",
        "buf[1]: 0x8A (PRESS_LSB, біти 11..4)",
        "buf[2]: 0x40 (PRESS_XLSB, біти 3..0)",
        "buf[3]: 0x81 (TEMP_MSB, біти 19..12)",
        "buf[4]: 0x96 (TEMP_LSB, біти 11..4)",
        "buf[5]: 0x00 (TEMP_XLSB, біти 3..0)"
    ]
    for idx, rline in enumerate(regs_demo):
        p.append(rect(rx1 + 10, ry1 + 35 + idx * 28, rw1 - 20, 24, fill="#ffffff", stroke=MUTED, sw=1.0, rx=3))
        p.append(text(rx1 + 15, ry1 + 51 + idx * 28, rline, size=9.5, color=INK, anchor="start"))

    p.append(arrow(rx1 + rw1 + 5, ry1 + rh1 / 2, rx1 + rw1 + 25, ry1 + rh1 / 2, color=LINE, sw=1.8))

    # Блок некомпенсованих цілих чисел
    rx2, ry2, rw2, rh2 = 300, 255, 235, 215
    p.append(rect(rx2, ry2, rw2, rh2, fill=MATH_BG, stroke=MATH_COL, sw=1.5, rx=5))
    p.append(text(rx2 + rw2 / 2, ry2 + 20, "Некомпенсовані коди ADC", size=11, color=MATH_COL, bold=True))
    raw_demo = [
        "int32_t raw_press = 379044;",
        "// (buf[0]<<12)|(buf[1]<<4)|(buf[2]>>4)",
        "int32_t raw_temp = 530784;",
        "// (buf[3]<<12)|(buf[4]<<4)|(buf[5]>>4)",
        "OTP Коефіцієнти (NVM):",
        "dig_T1=27504, dig_T2=-1048...",
        "dig_P1=36477, dig_P2=-10685..."
    ]
    for idx, rline in enumerate(raw_demo):
        p.append(text(rx2 + 15, ry2 + 45 + idx * 23, rline, size=9.5, color=MATH_COL if "dig_" in rline else INK, anchor="start", bold=("int32" in rline)))

    p.append(arrow(rx2 + rw2 + 5, ry2 + rh2 / 2, rx2 + rw2 + 25, ry2 + rh2 / 2, color=LINE, sw=1.8))

    # Блок інженерних SI величин
    rx3, ry3, rw3, rh3 = 570, 255, 235, 215
    p.append(rect(rx3, ry3, rw3, rh3, fill=SI_BG, stroke=SI_COL, sw=1.5, rx=5))
    p.append(text(rx3 + rw3 / 2, ry3 + 20, "Фізичні величини у SI", size=11, color=SI_COL, bold=True))
    si_demo = [
        "struct SensorSample {",
        "  float temperature_c;  // 24.65 °C",
        "  float pressure_pa;    // 101328.4 Па",
        "  uint32_t timestamp_us;// 18492023",
        "  SampleFlags flags;    // VALID",
        "};",
        "// C++20: Pascals{101328.4f}",
        "// C++20: Celsius{24.65f}"
    ]
    for idx, rline in enumerate(si_demo):
        p.append(text(rx3 + 15, ry3 + 45 + idx * 23, rline, size=9.5, color=SI_COL if ("//" in rline or "Sample" in rline) else INK, anchor="start", bold=("float" in rline or "Pascals" in rline)))

    render(os.path.join(OUT, "sensor-driver-pipeline.svg"), W, H, *p,
           title="Конвеєр драйвера датчика: від сирих регістрів до одиниць SI")


# ── 2. register-unpack-to-si: Детальна бітова розпаковка 20-бітного числа ───────
def fig_register_unpack_to_si():
    W, H = 820, 520
    p = []

    p.append(text(W / 2, 32, "Анатомія розпаковки: 3 байти регістра -> 20-бітний знаковий код -> SI", size=14, bold=True))

    # Три байти з адресами та бітами
    bx, by, bw, bh = 40, 70, 220, 95

    # Байт 1: MSB
    p.append(rect(bx, by, bw, bh, fill=REG_BG, stroke=REG_COL, sw=1.6, rx=5))
    p.append(text(bx + bw / 2, by + 18, "Регістр 0xF7 (PRESS_MSB)", size=11, color=REG_COL, bold=True))
    p.append(rect(bx + 10, by + 30, bw - 20, 30, fill="#ffffff", stroke=LINE, sw=1.2, rx=3))
    p.append(text(bx + bw / 2, by + 50, "[ bit 7 | bit 6 | bit 5 | bit 4 | bit 3 | bit 2 | bit 1 | bit 0 ]", size=9.5, color=INK))
    p.append(text(bx + bw / 2, by + 80, "Вага бітів: [19 .. 12] (зсув << 12)", size=10, color=BUS_COL, bold=True))

    # Байт 2: LSB
    bx2 = bx + bw + 35
    p.append(rect(bx2, by, bw, bh, fill=REG_BG, stroke=REG_COL, sw=1.6, rx=5))
    p.append(text(bx2 + bw / 2, by + 18, "Регістр 0xF8 (PRESS_LSB)", size=11, color=REG_COL, bold=True))
    p.append(rect(bx2 + 10, by + 30, bw - 20, 30, fill="#ffffff", stroke=LINE, sw=1.2, rx=3))
    p.append(text(bx2 + bw / 2, by + 50, "[ bit 7 | bit 6 | bit 5 | bit 4 | bit 3 | bit 2 | bit 1 | bit 0 ]", size=9.5, color=INK))
    p.append(text(bx2 + bw / 2, by + 80, "Вага бітів: [11 .. 4] (зсув << 4)", size=10, color=BUS_COL, bold=True))

    # Байт 3: XLSB
    bx3 = bx2 + bw + 35
    p.append(rect(bx3, by, bw, bh, fill=REG_BG, stroke=REG_COL, sw=1.6, rx=5))
    p.append(text(bx3 + bw / 2, by + 18, "Регістр 0xF9 (PRESS_XLSB)", size=11, color=REG_COL, bold=True))
    p.append(rect(bx3 + 10, by + 30, bw - 20, 30, fill="#ffffff", stroke=LINE, sw=1.2, rx=3))
    p.append(rect(bx3 + 10, by + 30, (bw - 20) / 2, 30, fill="#d4efdf", stroke=LINE, sw=1.0, rx=0))
    p.append(text(bx3 + bw / 2, by + 50, "[ b7 | b6 | b5 | b4 ] [ b3 | b2 | b1 | b0 (0) ]", size=9.5, color=INK))
    p.append(text(bx3 + bw / 2, by + 80, "Вага: [3 .. 0] (зсув >> 4, маска 0xF0)", size=10, color=BUS_COL, bold=True))

    # Стрілки злиття
    p.append(line(bx + bw / 2, by + bh, W / 2 - 120, 210, color=LINE, sw=1.5))
    p.append(line(bx2 + bw / 2, by + bh, W / 2, 210, color=LINE, sw=1.5))
    p.append(line(bx3 + bw / 2, by + bh, W / 2 + 120, 210, color=LINE, sw=1.5))
    p.append(arrow(W / 2, 210, W / 2, 235, color=LINE, sw=2.0))

    # 20-бітний сирий вираз у 32-бітному контейнері
    p.append(rect(60, 240, 700, 95, fill=MATH_BG, stroke=MATH_COL, sw=1.8, rx=6))
    p.append(text(W / 2, 260, "Апаратне об'єднання у 32-бітне ціле без Undefined Behavior", size=11.5, color=MATH_COL, bold=True))

    p.append(text(W / 2, 285, "uint32_t raw_u = ((uint32_t)buf[0] << 12) | ((uint32_t)buf[1] << 4) | ((uint32_t)buf[2] >> 4);", size=10.5, color=INK, bold=True))
    p.append(text(W / 2, 312, "Знакове розширення (якщо 20-біт signed): int32_t val = (int32_t)(raw_u << 12) >> 12; // Арифметичний зсув", size=10, color=GRAY_COL))

    # Поліноміальна конвертація
    p.append(arrow(W / 2, 340, W / 2, 365, color=LINE, sw=2.0))

    p.append(rect(60, 370, 700, 125, fill=SI_BG, stroke=SI_COL, sw=1.8, rx=6))
    p.append(text(W / 2, 390, "Калібрувальний поліном у фіксованій комі (Fixed-Point Q24.8)", size=11.5, color=SI_COL, bold=True))

    eq_lines = [
        "var1 = (((int32_t)raw_temp >> 3) - ((int32_t)dig_T1 << 1)) * ((int32_t)dig_T2) >> 11;",
        "var2 = (((((raw_temp >> 4) - dig_T1) * ((raw_temp >> 4) - dig_T1)) >> 12) * dig_T3) >> 14;",
        "t_fine = var1 + var2;   // Q24.8 накопичувач температури",
        "int32_t temp_centidegrees = (t_fine * 5 + 128) >> 8;  // Результат: 2465 -> 24.65 °C"
    ]
    for idx, eline in enumerate(eq_lines):
        p.append(text(80, 412 + idx * 20, eline, size=9.5, color=INK, anchor="start", bold=("temp_centidegrees" in eline)))

    render(os.path.join(OUT, "register-unpack-to-si.svg"), W, H, *p,
           title="Розпаковка 20-бітного значення регістра та знакове розширення")


# ── 3. burst-read-atomicity: Небезпека розриву даних проти атомарного Burst Read ─
def fig_burst_read_atomicity():
    W, H = 840, 520
    p = []

    p.append(text(W / 2, 30, "Атомарність зчитування: Проблема розриву вибірки (Data Tearing)", size=14, bold=True))

    # Ліва половина: Помилковий підхід (Byte-by-byte зчитування з перериванням від АЦП)
    bx1, by1, bw1, bh1 = 30, 60, 370, 425
    p.append(rect(bx1, by1, bw1, bh1, fill=ERR_BG, stroke=ERR_COL, sw=1.8, rx=6))
    p.append(text(bx1 + bw1 / 2, by1 + 22, "ПОМИЛКА: Побайтове зчитування (No Burst)", size=11.5, color=ERR_COL, bold=True))

    steps_bad = [
        ("Час t0", "I2C START -> Read(MSB = 0x5C)", "#ffffff", INK),
        ("Час t1", "МК обробляє інші переривання (15 мкс)", "#fadbd8", ERR_COL),
        ("Час t2", "АЦП завершив оновлення: 0x5C -> 0x5D!\nНове значення тиску в кремнії!", "#f5b7b1", ERR_COL),
        ("Час t3", "I2C START -> Read(LSB = 0x02)", "#ffffff", INK),
        ("Час t4", "I2C START -> Read(XLSB = 0x10)", "#ffffff", INK),
        ("Результат", "Зібрано: MSB(старе 0x5C) + LSB(нове 0x02)\nПомилка: стрибок тиску на 4096 Па (40 гПа)!", "#f2d7d5", ERR_COL)
    ]
    for idx, (t_lab, desc, fill_c, txt_c) in enumerate(steps_bad):
        y_pos = by1 + 45 + idx * 60
        p.append(rect(bx1 + 12, y_pos, bw1 - 24, 52, fill=fill_c, stroke=MUTED, sw=1.0, rx=4))
        p.append(text(bx1 + 20, y_pos + 18, t_lab, size=9.5, color=txt_c, anchor="start", bold=True))
        p.append(mtext(bx1 + 20, y_pos + 34, desc, size=9.5, color=txt_c, anchor="start", lh=1.2))

    # Права половина: Правильний підхід (Burst DMA / Shadow Latch)
    bx2, by2, bw2, bh2 = 440, 60, 370, 425
    p.append(rect(bx2, by2, bw2, bh2, fill=SI_BG, stroke=SI_COL, sw=1.8, rx=6))
    p.append(text(bx2 + bw2 / 2, by2 + 22, "ПРАВИЛЬНО: Атомарний Burst Read (DMA)", size=11.5, color=SI_COL, bold=True))

    steps_good = [
        ("Час t0", "I2C START -> Reg 0xF7 (Auto-increment)", "#ffffff", INK),
        ("Апаратний захист", "Чип фіксує Shadow Latch на час посилки\nАЦП не може змінити тіньові регістри!", "#d5f5e3", SI_COL),
        ("Час t1..t3", "Безперервне вичитування 6 байтів DMA\nMSB -> LSB -> XLSB -> T_MSB -> T_LSB...", "#ffffff", INK),
        ("Час t4", "I2C STOP -> Звільнення Shadow Latch", "#ffffff", INK),
        ("Час t5", "Переривання DMA -> Обчислення в ISR/Task", "#d5f5e3", SI_COL),
        ("Результат", "Гарантована узгодженість вибірки\nПомилка фазового розриву = 0.00 Па", "#abebc6", SI_COL)
    ]
    for idx, (t_lab, desc, fill_c, txt_c) in enumerate(steps_good):
        y_pos = by2 + 45 + idx * 60
        p.append(rect(bx2 + 12, y_pos, bw2 - 24, 52, fill=fill_c, stroke=MUTED, sw=1.0, rx=4))
        p.append(text(bx2 + 20, y_pos + 18, t_lab, size=9.5, color=txt_c, anchor="start", bold=True))
        p.append(mtext(bx2 + 20, y_pos + 34, desc, size=9.5, color=txt_c, anchor="start", lh=1.2))

    render(os.path.join(OUT, "burst-read-atomicity.svg"), W, H, *p,
           title="Порівняння побайтового зчитування та атомарного Burst-трансферу")


# ── 4. driver-state-machine: Відмовостійка машина станів драйвера чипа ────────
def fig_driver_state_machine():
    W, H = 840, 520
    p = []

    p.append(text(W / 2, 30, "Машина станів відмовостійкого драйвера цифрового чипа", size=14, bold=True))

    # Стан 1: UNINITIALIZED
    s1_x, s1_y, s1_w, s1_h = 40, 70, 160, 55
    p.append(rect(s1_x, s1_y, s1_w, s1_h, fill=GRAY_BG, stroke=GRAY_COL, sw=1.6, rx=5))
    p.append(text(s1_x + s1_w / 2, s1_y + 24, "UNINITIALIZED", size=11, color=INK, bold=True))
    p.append(text(s1_x + s1_w / 2, s1_y + 42, "Живлення подано", size=9.5, color=MUTED))

    # Стрілка -> RESETTING
    p.append(arrow(s1_x + s1_w, s1_y + s1_h / 2, s1_x + s1_w + 35, s1_y + s1_h / 2, color=LINE, sw=1.5))
    p.append(text(s1_x + s1_w + 18, s1_y + s1_h / 2 - 8, "Init()", size=9.5, color=BUS_COL))

    # Стан 2: RESET_AND_PROBE
    s2_x, s2_y, s2_w, s2_h = 235, 70, 160, 55
    p.append(rect(s2_x, s2_y, s2_w, s2_h, fill=BUS_BG, stroke=BUS_COL, sw=1.6, rx=5))
    p.append(text(s2_x + s2_w / 2, s2_y + 24, "RESET_AND_PROBE", size=11, color=BUS_COL, bold=True))
    p.append(text(s2_x + s2_w / 2, s2_y + 42, "Soft Reset + Chip ID", size=9.5, color=INK))

    # Стрілка -> READ_CALIBRATION
    p.append(arrow(s2_x + s2_w, s2_y + s2_h / 2, s2_x + s2_w + 35, s2_y + s2_h / 2, color=LINE, sw=1.5))
    p.append(text(s2_x + s2_w + 18, s2_y + s2_h / 2 - 8, "ID OK", size=9.5, color=SI_COL))

    # Стан 3: READ_CALIBRATION
    s3_x, s3_y, s3_w, s3_h = 430, 70, 170, 55
    p.append(rect(s3_x, s3_y, s3_w, s3_h, fill=MATH_BG, stroke=MATH_COL, sw=1.6, rx=5))
    p.append(text(s3_x + s3_w / 2, s3_y + 24, "READ_CALIBRATION", size=11, color=MATH_COL, bold=True))
    p.append(text(s3_x + s3_w / 2, s3_y + 42, "Вичитка NVM + CRC", size=9.5, color=INK))

    # Стрілка -> CONFIGURE
    p.append(arrow(s3_x + s3_w, s3_y + s3_h / 2, s3_x + s3_w + 35, s3_y + s3_h / 2, color=LINE, sw=1.5))
    p.append(text(s3_x + s3_w + 18, s3_y + s3_h / 2 - 8, "CRC OK", size=9.5, color=SI_COL))

    # Стан 4: CONFIGURE
    s4_x, s4_y, s4_w, s4_h = 635, 70, 160, 55
    p.append(rect(s4_x, s4_y, s4_w, s4_h, fill=BUS_BG, stroke=BUS_COL, sw=1.6, rx=5))
    p.append(text(s4_x + s4_w / 2, s4_y + 24, "CONFIGURE", size=11, color=BUS_COL, bold=True))
    p.append(text(s4_x + s4_w / 2, s4_y + 42, "OSR, IIR, ODR, Mode", size=9.5, color=INK))

    # Стрілка вниз до IDLE / READY
    p.append(arrow(s4_x + s4_w / 2, s4_y + s4_h, s4_x + s4_w / 2, 200, color=LINE, sw=1.8))
    p.append(text(s4_x + s4_w / 2 + 30, 170, "Cfg Done", size=9.5, color=SI_COL))

    # Стан 5: READY / IDLE
    s5_x, s5_y, s5_w, s5_h = 580, 205, 215, 60
    p.append(rect(s5_x, s5_y, s5_w, s5_h, fill=SI_BG, stroke=SI_COL, sw=2.0, rx=6))
    p.append(text(s5_x + s5_w / 2, s5_y + 25, "READY / IDLE", size=12, color=SI_COL, bold=True))
    p.append(text(s5_x + s5_w / 2, s5_y + 46, "Очікування таймера / тригера", size=9.5, color=INK))

    # Стрілка READY -> TRIGGER_SAMPLING
    p.append(arrow(s5_x + 30, s5_y + s5_h, s5_x + 30, 330, color=LINE, sw=1.6))
    p.append(text(s5_x + 10, 300, "Tick / DRDY", size=9.5, color=BUS_COL, anchor="end"))

    # Стан 6: BURST_DMA_READ
    s6_x, s6_y, s6_w, s6_h = 500, 335, 295, 60
    p.append(rect(s6_x, s6_y, s6_w, s6_h, fill=BUS_BG, stroke=BUS_COL, sw=1.8, rx=6))
    p.append(text(s6_x + s6_w / 2, s6_y + 25, "BURST_DMA_READING", size=12, color=BUS_COL, bold=True))
    p.append(text(s6_x + s6_w / 2, s6_y + 46, "Неблокуючий трансфер шини", size=9.5, color=INK))

    # Стрілка BURST -> PROCESS_COMPENSATION
    p.append(arrow(s6_x, s6_y + s6_h / 2, 380, s6_y + s6_h / 2, color=LINE, sw=1.6))
    p.append(text(440, s6_y + s6_h / 2 - 8, "DMA Complete", size=9.5, color=SI_COL))

    # Стан 7: PROCESS_COMPENSATION
    s7_x, s7_y, s7_w, s7_h = 160, 335, 220, 60
    p.append(rect(s7_x, s7_y, s7_w, s7_h, fill=MATH_BG, stroke=MATH_COL, sw=1.8, rx=6))
    p.append(text(s7_x + s7_w / 2, s7_y + 25, "CALC_COMPENSATION", size=11.5, color=MATH_COL, bold=True))
    p.append(text(s7_x + s7_w / 2, s7_y + 46, "Fixed-point -> Push to Queue", size=9.5, color=INK))

    # Повернення в READY
    p.append(line(s7_x + s7_w / 2, s7_y, s7_x + s7_w / 2, 235, color=SI_COL, sw=1.5))
    p.append(arrow(s7_x + s7_w / 2, 235, s5_x, 235, color=SI_COL, sw=1.5))
    p.append(text(440, 225, "Вибірка готова -> Callback/Queue", size=9.5, color=SI_COL))

    # Стан 8: RECOVERY & ERROR HANDLING
    err_x, err_y, err_w, err_h = 60, 195, 230, 95
    p.append(rect(err_x, err_y, err_w, err_h, fill=ERR_BG, stroke=ERR_COL, sw=2.0, rx=6))
    p.append(text(err_x + err_w / 2, err_y + 24, "BUS_RECOVERY (Відновлення)", size=11.5, color=ERR_COL, bold=True))
    p.append(mtext(err_x + err_w / 2, err_y + 48, "1. Генерація 9 імпульсів SCL\n2. Апаратний NACK + STOP\n3. Переініціалізація шини / LDO", size=9.5, color=INK, lh=1.3))

    # Стрілки збоїв в RECOVERY
    p.append(line(s2_x + 50, s2_y + s2_h, s2_x + 50, err_y, color=ERR_COL, sw=1.3, dash="4 3"))
    p.append(text(s2_x + 55, 160, "ID Mismatch", size=9.5, color=ERR_COL, anchor="start"))

    p.append(line(s6_x + 40, s6_y, s6_x + 40, 430, color=ERR_COL, sw=1.3, dash="4 3"))
    p.append(line(s6_x + 40, 430, err_x + err_w / 2, 430, color=ERR_COL, sw=1.3, dash="4 3"))
    p.append(arrow(err_x + err_w / 2, 430, err_x + err_w / 2, err_y + err_h, color=ERR_COL, sw=1.3))
    p.append(text(350, 420, "Timeout / NACK / CRC Fail (Retries > 3)", size=9.5, color=ERR_COL))

    # Вихід з Recovery назад в RESETTING
    p.append(line(err_x + 30, err_y, err_x + 30, 100, color=ERR_COL, sw=1.4))
    p.append(arrow(err_x + 30, 100, s1_x + s1_w / 2, 100, color=ERR_COL, sw=1.4))
    p.append(text(err_x + 35, 150, "Auto-restart", size=9.5, color=ERR_COL, anchor="start"))

    render(os.path.join(OUT, "driver-state-machine.svg"), W, H, *p,
           title="Повна машина станів драйвера з контуром аварійного відновлення")


if __name__ == "__main__":
    fig_sensor_driver_pipeline()
    fig_register_unpack_to_si()
    fig_burst_read_atomicity()
    fig_driver_state_machine()
    print("All 4 figures generated successfully in img/")

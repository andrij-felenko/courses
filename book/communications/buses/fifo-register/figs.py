# -*- coding: utf-8 -*-
"""Фігури теми «FIFO-регістри в давачах» (book/communications/buses/fifo-register).
Чистий Python без залежностей; svgkit імпортуємо зі scripts/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Апаратна топологія FIFO у кристалі давача ───────────────────────────
def fig_architecture():
    W, H = 900, 460
    p = []
    p.append(text(W/2, 28, "Апаратна структура буфера FIFO всередині давача", size=18, bold=True))
    p.append(text(W/2, 48, "тракт оцифрування · SRAM-пам'ять · вказівники · поріг заповнення · шинний порт",
                  size=12, color=MUTED, italic=True))

    # Ліва колонка: Тракт вимірювання (домен тактування ADC/DSP)
    p.append(rect(40, 75, 200, 310, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(140, 100, "Тракт вимірювання", size=13, bold=True))
    p.append(text(140, 118, "домен такту ADC / DSP", size=10.5, color=MUTED))

    p.append(rect(55, 135, 170, 42, fill=BG, stroke=POS, sw=1.5, rx=5))
    p.append(text(140, 160, "MEMS Акселерометр", size=11, bold=True, color=POS))

    p.append(rect(55, 190, 170, 42, fill=BG, stroke=POS, sw=1.5, rx=5))
    p.append(text(140, 215, "MEMS Гіроскоп", size=11, bold=True, color=POS))

    p.append(rect(55, 245, 170, 42, fill=BG, stroke=POS, sw=1.5, rx=5))
    p.append(text(140, 270, "АЦП та цифровий фільтр", size=11, bold=True, color=POS))

    p.append(rect(55, 305, 170, 55, fill="#fff5f5", stroke=POS, sw=1.5, rx=5))
    p.append(text(140, 328, "FIFO_EN (маска)", size=11, bold=True, color=POS))
    p.append(text(140, 346, "селектор потоків осей", size=10, color=MUTED))

    # Стрілка з тракту в SRAM
    p.append(arrow(240, 332, 290, 332, color=POS, sw=2))
    p.append(text(265, 322, "push", size=10, bold=True, color=POS))

    # Центральна секція: Апаратний буфер SRAM (FIFO)
    p.append(rect(290, 75, 300, 310, fill="#f0f9ff", stroke=NEG, sw=1.5, rx=8))
    p.append(text(440, 100, "Кільцевий буфер SRAM (FIFO)", size=13, bold=True, color=NEG))
    p.append(text(440, 118, "512–4096 байтів / апаратні комірки", size=10.5, color=MUTED))

    # Комірки пам'яті
    cells = [
        ("Слот 0 (найстаріший)", FIELD),
        ("Слот 1", FIELD),
        ("Слот 2", FIELD),
        ("...", MUTED),
        ("Слот N-1 (найновіший)", POS),
    ]
    cy = 135
    for lbl, col in cells:
        p.append(rect(310, cy, 260, 26, fill=BG, stroke=col, sw=1.2, rx=4))
        p.append(text(440, cy+18, lbl, size=10.5, color=col, bold=True))
        cy += 30

    # Вказівники та лічильник
    p.append(rect(310, 295, 125, 65, fill=BG, stroke=LINE, sw=1.2, rx=4))
    p.append(text(372, 316, "Write Pointer", size=10.5, bold=True))
    p.append(text(372, 334, "автоінкремент", size=9.5, color=MUTED))
    p.append(text(372, 349, "по запису АЦП", size=9.5, color=MUTED))

    p.append(rect(445, 295, 125, 65, fill=BG, stroke=LINE, sw=1.2, rx=4))
    p.append(text(507, 316, "Read Pointer", size=10.5, bold=True))
    p.append(text(507, 334, "автоінкремент", size=9.5, color=MUTED))
    p.append(text(507, 349, "по вичитці SPI", size=9.5, color=MUTED))

    # Права колонка: Керування, статус і шинний інтерфейс
    p.append(rect(610, 75, 250, 310, fill="#fdfbf7", stroke="#b07a00", sw=1.2, rx=8))
    p.append(text(735, 100, "Регістри та логіка", size=13, bold=True, color="#b07a00"))
    p.append(text(735, 118, "домен SPI / I2C шини", size=10.5, color=MUTED))

    # Порівнювач Вотермарка
    p.append(rect(625, 135, 220, 52, fill=BG, stroke="#b07a00", sw=1.2, rx=5))
    p.append(text(735, 155, "Порівнювач Watermark", size=11, bold=True, color="#b07a00"))
    p.append(text(735, 173, "FIFO_COUNT >= WTM_THS", size=10, color=MUTED))

    # Регістри стану
    p.append(rect(625, 195, 220, 52, fill=BG, stroke="#b07a00", sw=1.2, rx=5))
    p.append(text(735, 215, "FIFO_STATUS / COUNT", size=11, bold=True, color="#b07a00"))
    p.append(text(735, 233, "кількість незчитаних байтів", size=10, color=MUTED))

    # Регістр даних FIFO
    p.append(rect(625, 255, 220, 52, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(735, 275, "FIFO_DATA_OUT (0x78)", size=11, bold=True, color=FIELD))
    p.append(text(735, 293, "вікно пакетного читання", size=10, color=MUTED))

    # Виводи переривання та шини
    p.append(rect(625, 318, 105, 45, fill=BG, stroke=POS, sw=1.2, rx=4))
    p.append(text(677, 337, "INT Pin", size=10.5, bold=True, color=POS))
    p.append(text(677, 352, "WTM / OVR", size=9.5, color=MUTED))

    p.append(rect(740, 318, 105, 45, fill=BG, stroke=NEG, sw=1.2, rx=4))
    p.append(text(792, 337, "SPI / I2C", size=10.5, bold=True, color=NEG))
    p.append(text(792, 352, "Burst DMA", size=9.5, color=MUTED))

    # Стрілка з SRAM у шинний порт
    p.append(arrow(570, 281, 625, 281, color=FIELD, sw=2))
    p.append(text(597, 271, "pop", size=10, bold=True, color=FIELD))

    # Нижній висновок
    p.append(rect(40, 400, 820, 42, fill="#f2f4f6", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(W/2, 426,
                  "FIFO розв'язує тактові домени: АЦП пише у пам'ять стабільно за власним таймером, а мікроконтролер вичитує пакетами коли зручно.",
                  size=11, bold=True))

    render(os.path.join(OUT, "fifo-architecture.svg"), W, H, *p)


# ── 2. Чотири апаратні режими роботи FIFO ────────────────────────────────────
def fig_modes():
    W, H = 920, 440
    p = []
    p.append(text(W/2, 28, "Режими роботи FIFO-буфера", size=18, bold=True))
    p.append(text(W/2, 48, "Bypass · FIFO (Stop-on-Full) · Stream (Continuous) · Continuous-to-FIFO (Trigger)",
                  size=12, color=MUTED, italic=True))

    cards = [
        ("1. Bypass (Обхід)", "#64748b", [
            "FIFO вимкнено",
            "Дані йдуть прямо в",
            "визначені вихідні регістри",
            "Кожен новий відлік АЦП",
            "перезаписує попередній",
            "Використання: опитування",
            "в реальному часі",
        ]),
        ("2. FIFO (Stop-on-Full)", NEG, [
            "Запис до заповнення",
            "Буфер заповнюється до 100%",
            "Нові відліки блокуються,",
            "старі надійно збережено",
            "Прапорець: FIFO_FULL",
            "Використання: запис серії",
            "фіксованої довжини",
        ]),
        ("3. Stream (Кільцевий)", FIELD, [
            "Безперервний потік",
            "При 100% заповненні нові",
            "відліки витісняють найстаріші",
            "У пам'яті завжди лишається",
            "найсвіжіше вікно вимірів",
            "Використання: фоновий буфер",
            "для системної телеметрії",
        ]),
        ("4. Trigger (Подія)", POS, [
            "Вікно навколо тригера",
            "Постійний Stream до події",
            "Після апаратного тригера",
            "дописує N вибірок і зупиняє",
            "Зберігає передісторію удару",
            "та наслідок події (crash-log)",
            "Використання: аналіз ударів",
        ]),
    ]

    card_w = 195
    spacing = 18
    start_x = 42

    for i, (title, col, lines) in enumerate(cards):
        cx = start_x + i * (card_w + spacing)
        # Карточка
        p.append(rect(cx, 75, card_w, 310, fill=BG, stroke=col, sw=1.5, rx=8))
        # Заголовок
        p.append(rect(cx, 75, card_w, 38, fill=col, stroke=col, sw=1, rx=0))
        p.append(text(cx + card_w/2, 100, title, size=11.5, color=BG, bold=True))

        # Рядки тексту
        ly = 135
        for line_txt in lines:
            if "Використання:" in line_txt:
                p.append(text(cx + card_w/2, ly, line_txt, size=10, color=col, bold=True))
            else:
                p.append(text(cx + card_w/2, ly, line_txt, size=10.5, color=INK))
            ly += 24

        # Маленька схема буфера внизу картки
        by = 310
        p.append(rect(cx + 15, by, card_w - 30, 55, fill="#f8fafc", stroke=MUTED, sw=1, rx=4))
        if i == 0:
            p.append(text(cx + card_w/2, by + 24, "ADC -> OUT_REG", size=10, bold=True, color=MUTED))
            p.append(text(cx + card_w/2, by + 42, "FIFO байпас", size=9, color=MUTED))
        elif i == 1:
            p.append(text(cx + card_w/2, by + 24, "[1][2][3][4] STOP", size=10, bold=True, color=NEG))
            p.append(text(cx + card_w/2, by + 42, "втрата нових даних", size=9, color=MUTED))
        elif i == 2:
            p.append(text(cx + card_w/2, by + 24, "<- [3][4][5][6] <-", size=10, bold=True, color=FIELD))
            p.append(text(cx + card_w/2, by + 42, "витіснення старих", size=9, color=MUTED))
        elif i == 3:
            p.append(text(cx + card_w/2, by + 24, "До удару | Подія | Після", size=9.5, bold=True, color=POS))
            p.append(text(cx + card_w/2, by + 42, "зафіксоване вікно", size=9, color=MUTED))

    # Нижній висновок
    p.append(rect(40, 398, 840, 34, fill="#f2f4f6", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(W/2, 420,
                  "Вибір режиму визначає долю даних: зберегти минуле (FIFO), мати завжди свіже сьогодення (Stream) чи зловити момент аварії (Trigger).",
                  size=11, bold=True))

    render(os.path.join(OUT, "fifo-modes.svg"), W, H, *p)


# ── 3. Часова діаграма та механізм переривання Watermark ───────────────────────
def fig_watermark_timing():
    W, H = 880, 420
    p = []
    p.append(text(W/2, 28, "Спустошення FIFO по перериванню Watermark та сон CPU", size=18, bold=True))
    p.append(text(W/2, 48, "накопичення вибірок · поріг WTM · пробудження мікроконтролера · пакетний вичит SPI DMA",
                  size=12, color=MUTED, italic=True))

    # Графік рівня заповнення FIFO
    gx0, gy0, gw, gh = 100, 85, 720, 130
    p.append(rect(gx0, gy0, gw, gh, fill="#fafbfc", stroke="#cbd5e1", sw=1, rx=4))

    # Осі
    p.append(line(gx0, gy0+gh, gx0+gw, gy0+gh, color=LINE, sw=1.5))
    p.append(line(gx0, gy0, gx0, gy0+gh, color=LINE, sw=1.5))
    p.append(text(gx0-12, gy0+15, "Рівень FIFO", size=10, bold=True, anchor="end"))
    p.append(text(gx0+gw+10, gy0+gh+15, "Час t", size=10, bold=True, anchor="start"))

    # Рівні Full і WTM
    p.append(line(gx0, gy0+20, gx0+gw, gy0+20, color=POS, sw=1.2, dash="4,4"))
    p.append(text(gx0-8, gy0+24, "FULL (100%)", size=9.5, color=POS, anchor="end", bold=True))

    p.append(line(gx0, gy0+60, gx0+gw, gy0+60, color="#b07a00", sw=1.2, dash="4,4"))
    p.append(text(gx0-8, gy0+64, "WTM (напр. 80%)", size=9.5, color="#b07a00", anchor="end", bold=True))

    # Пилоподібний графік заповнення і скидання
    curve_points = [
        (100, gy0+gh), (380, gy0+60), (410, gy0+gh),
        (690, gy0+60), (720, gy0+gh), (800, gy0+gh - 35)
    ]
    pts_str = " ".join(f"{x},{y}" for x, y in curve_points)
    p.append(f'<polyline points="{pts_str}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')

    # Сигнал INT (лінія переривання)
    iy0 = 240
    p.append(text(gx0-12, iy0+18, "INT Pin", size=10.5, bold=True, anchor="end", color=POS))
    p.append(line(gx0, iy0+25, 380, iy0+25, color=POS, sw=1.5))
    p.append(line(380, iy0+25, 380, iy0+5, color=POS, sw=1.5))
    p.append(line(380, iy0+5, 410, iy0+5, color=POS, sw=1.5))
    p.append(line(410, iy0+5, 410, iy0+25, color=POS, sw=1.5))
    p.append(line(410, iy0+25, 690, iy0+25, color=POS, sw=1.5))
    p.append(line(690, iy0+25, 690, iy0+5, color=POS, sw=1.5))
    p.append(line(690, iy0+5, 720, iy0+5, color=POS, sw=1.5))
    p.append(line(720, iy0+5, 820, iy0+25, color=POS, sw=1.5))

    p.append(text(395, iy0-2, "WTM Active", size=9, color=POS, bold=True))
    p.append(text(705, iy0-2, "WTM Active", size=9, color=POS, bold=True))

    # Стан MCU
    my0 = 295
    p.append(text(gx0-12, my0+20, "Стан MCU", size=10.5, bold=True, anchor="end", color=FIELD))

    # Блок сну 1
    p.append(rect(100, my0, 280, 36, fill="#e2e8f0", stroke=MUTED, sw=1, rx=4))
    p.append(text(240, my0+22, "Глибокий сон (Deep Sleep ~2–10 мкА)", size=10.5, color=MUTED, bold=True))

    # Блок активності DMA 1
    p.append(rect(380, my0, 30, 36, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(395, my0+22, "DMA", size=9.5, color=FIELD, bold=True))

    # Блок сну 2
    p.append(rect(410, my0, 280, 36, fill="#e2e8f0", stroke=MUTED, sw=1, rx=4))
    p.append(text(550, my0+22, "Глибокий сон (Deep Sleep ~2–10 мкА)", size=10.5, color=MUTED, bold=True))

    # Блок активності DMA 2
    p.append(rect(690, my0, 30, 36, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(705, my0+22, "DMA", size=9.5, color=FIELD, bold=True))

    # Блок сну 3
    p.append(rect(720, my0, 100, 36, fill="#e2e8f0", stroke=MUTED, sw=1, rx=4))
    p.append(text(770, my0+22, "Сон...", size=10.5, color=MUTED))

    # Пояснення енергозбереження
    p.append(rect(60, 355, 780, 48, fill="#eff6ff", stroke=NEG, sw=1.2, rx=8))
    p.append(text(W/2, 375,
                  "Коефіцієнт заповнення активності CPU (Duty Cycle) падає з 100% до менш ніж 1%.",
                  size=11, bold=True, color=NEG))
    p.append(text(W/2, 393,
                  "Замість 1000 пробуджень на секунду процесор прокидається 10–20 разів, вичитуючи дані пакетом DMA на повній швидкості SPI.",
                  size=10.5, color=INK))

    render(os.path.join(OUT, "watermark-timing.svg"), W, H, *p)


# ── 4. Формати пакетів даних у FIFO ──────────────────────────────────────────
def fig_packet_formats():
    W, H = 880, 400
    p = []
    p.append(text(W/2, 28, "Формати пакування кадрів у пам'яті FIFO", size=18, bold=True))
    p.append(text(W/2, 48, "фіксовані кадри (старі IMU) проти тегованих пакетів із заголовком (сучасні IMU)",
                  size=12, color=MUTED, italic=True))

    # 1. Фіксований формат (MPU-6050 / ICM-20600)
    p.append(rect(40, 75, 800, 130, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=8))
    p.append(text(60, 98, "А. Фіксований нетегований кадр (наприклад, MPU-6050: 12 байтів / кадр)",
                  size=12, bold=True, anchor="start"))
    p.append(text(60, 115, "Жорсткий порядок байтів. Збій одного байта на шині зміщує всі подальші осі.",
                  size=10.5, color=MUTED, anchor="start"))

    fixed_bytes = [
        ("AccX_H", POS), ("AccX_L", POS),
        ("AccY_H", POS), ("AccY_L", POS),
        ("AccZ_H", POS), ("AccZ_L", POS),
        ("GyrX_H", NEG), ("GyrX_L", NEG),
        ("GyrY_H", NEG), ("GyrY_L", NEG),
        ("GyrZ_H", NEG), ("GyrZ_L", NEG),
    ]
    bx0, by0, bw, bh = 60, 130, 60, 38
    for i, (name, col) in enumerate(fixed_bytes):
        x = bx0 + i * (bw + 3)
        p.append(rect(x, by0, bw, bh, fill=BG, stroke=col, sw=1.2, rx=4))
        p.append(text(x + bw/2, by0 + 23, name, size=9.5, bold=True, color=col))
        p.append(text(x + bw/2, by0 - 6, f"B{i}", size=9.5, color=MUTED))

    p.append(text(60 + 6*63, by0 + 52, "6 байтів Акселерометр | 6 байтів Гіроскоп",
                  size=9.5, color=MUTED, bold=True))

    # 2. Тегований формат (LSM6DSO / ICM-42688 / BMA400)
    p.append(rect(40, 220, 800, 160, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(60, 243, "Б. Тегований пакетний формат (наприклад, ST LSM6DSO: 7 байтів / пакет)",
                  size=12, bold=True, anchor="start", color=FIELD))
    p.append(text(60, 260, "Кожен пакет має байт тегу TAG (ідентифікатор сенсора + лічильник). Самовідновлення синхронізації.",
                  size=10.5, color=MUTED, anchor="start"))

    # Пакет 1: Аксель
    p.append(rect(60, 275, 340, 48, fill=BG, stroke=POS, sw=1.2, rx=5))
    p.append(rect(65, 281, 60, 36, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    p.append(text(95, 303, "TAG: ACC", size=9, bold=True, color=POS))

    for j, ax in enumerate(["X_H/L", "Y_H/L", "Z_H/L"]):
        px = 132 + j * 68
        p.append(rect(px, 281, 64, 36, fill=BG, stroke=POS, sw=1, rx=3))
        p.append(text(px + 32, 303, ax, size=9.5, color=POS))
    p.append(text(230, 338, "Пакет акселерометра (7 байтів)", size=9.5, color=POS, bold=True))

    # Пакет 2: Гіроскоп
    p.append(rect(420, 275, 340, 48, fill=BG, stroke=NEG, sw=1.2, rx=5))
    p.append(rect(425, 281, 60, 36, fill="#dbeafe", stroke=NEG, sw=1.2, rx=3))
    p.append(text(455, 303, "TAG: GYRO", size=9, bold=True, color=NEG))

    for j, ax in enumerate(["X_H/L", "Y_H/L", "Z_H/L"]):
        px = 492 + j * 68
        p.append(rect(px, 281, 64, 36, fill=BG, stroke=NEG, sw=1, rx=3))
        p.append(text(px + 32, 303, ax, size=9.5, color=NEG))
    p.append(text(590, 338, "Пакет гіроскопа (7 байтів)", size=9.5, color=NEG, bold=True))

    p.append(text(W/2, 365,
                  "Теги дозволяють змішувати різні частоти опитування (ODR) акселерометра і гіроскопа в одному FIFO без плутанини.",
                  size=10.5, bold=True, color=FIELD))

    render(os.path.join(OUT, "packet-formats.svg"), W, H, *p)


if __name__ == "__main__":
    fig_architecture()
    fig_modes()
    fig_watermark_timing()
    fig_packet_formats()
    print("Всі фігури згенеровано успішно.")

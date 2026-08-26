# -*- coding: utf-8 -*-
"""Фігури до теми «Перша відповідь чипа».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (scripts/svgkit.py)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Семантичні кольори
COLOR_OK = FIELD       # #27ae60 - успіх, валідний стан
COLOR_WARN = "#d35400"  # попередження, зміщення бітів
COLOR_ERR = POS        # #c0392b - помилка, 0x00/0xFF, КЗ
COLOR_INFO = NEG       # #2457d6 - такт, шина, дані
COLOR_MUTED = MUTED    # #6b7280

# ── 1. Алгоритм валідації та діагностики (bringup-flowchart.svg) ─────────────
def fig_bringup_flowchart():
    W, H = 820, 520
    f = [text(W / 2, 26, "Алгоритм первинної валідації та діагностики чипа", size=16, bold=True)]
    f.append(text(W / 2, 46, "послідовність кроків від подачі живлення до перевірки цілісності регістрів",
                  size=11, color=MUTED, italic=True))

    # Стовпчик 1: Головна лінія успіху (x = 220)
    # Блок 1: Старт і живлення
    f.append(rect(100, 70, 240, 48, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(220, 90, "1. Подача VDD / Скидання", size=12, bold=True))
    f.append(text(220, 107, "Пауза t_POR (1..10 мс)", size=10.5, color=MUTED))

    # Стрілка 1 -> 2
    f.append(arrow(220, 118, 220, 148, color=INK, sw=1.8))

    # Блок 2: Зчитування ID
    f.append(rect(100, 148, 240, 48, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(220, 168, "2. Читання WHO_AM_I / ID", size=12, bold=True))
    f.append(text(220, 185, "Отримано значення байта", size=10.5, color=COLOR_INFO))

    # Стрілка 2 -> 3
    f.append(arrow(220, 196, 220, 226, color=INK, sw=1.8))

    # Блок 3: Перевірка валідності
    f.append(rect(100, 226, 240, 54, fill="#eaf2f8", stroke=COLOR_INFO, sw=1.8))
    f.append(text(220, 246, "3. Аналіз відповіді", size=12, bold=True))
    f.append(text(220, 263, "Звірка з еталоном даташиту", size=10.5, color=MUTED))

    # Розгалуження вправо: несправності
    # Стрілка на 0x00 / 0xFF
    f.append(arrow(340, 240, 490, 150, color=COLOR_ERR, sw=1.8))
    f.append(text(400, 180, "0x00 / 0xFF", size=11, color=COLOR_ERR, bold=True))

    # Блок діагностики 0x00 / 0xFF
    f.append(rect(490, 120, 300, 60, fill="#fdf2e9", stroke=COLOR_ERR, sw=1.5))
    f.append(text(640, 140, "Аварія ліній зв'язку або живлення", size=11.5, color=COLOR_ERR, bold=True))
    f.append(text(640, 157, "Обрив MISO/SDA, КЗ на GND,", size=10.5, color=INK))
    f.append(text(640, 171, "немає VDD, чип у RESET або хибна I2C-адреса", size=10, color=MUTED))

    # Стрілка на зміщений біт
    f.append(arrow(340, 255, 490, 255, color=COLOR_WARN, sw=1.8))
    f.append(text(415, 247, "Зсув (<<1, >>1)", size=11, color=COLOR_WARN, bold=True))

    # Блок діагностики зсуву бітів
    f.append(rect(490, 226, 300, 60, fill="#fef9e7", stroke=COLOR_WARN, sw=1.5))
    f.append(text(640, 246, "Невідповідність SPI CPOL / CPHA", size=11.5, color=COLOR_WARN, bold=True))
    f.append(text(640, 263, "Зчитування на хибному фронті SCK", size=10.5, color=INK))
    f.append(text(640, 277, "Замість 0x68 отримано 0xD0 або 0x34", size=10, color=MUTED))

    # Стрілка на невідомий ID
    f.append(arrow(340, 270, 490, 360, color=COLOR_ERR, sw=1.8))
    f.append(text(405, 330, "Чужий ID", size=11, color=COLOR_ERR, bold=True))

    # Блок діагностики чужого ID
    f.append(rect(490, 332, 300, 56, fill="#fdf2e9", stroke=COLOR_ERR, sw=1.5))
    f.append(text(640, 352, "Невідповідна ревізія чи підробка", size=11.5, color=COLOR_ERR, bold=True))
    f.append(text(640, 369, "Перемаркований чип або інша модель лінійки", size=10, color=MUTED))

    # Стрілка 3 -> 4 (ID збігся)
    f.append(arrow(220, 280, 220, 320, color=COLOR_OK, sw=2.0))
    f.append(text(255, 305, "ID збігся", size=11, color=COLOR_OK, bold=True))

    # Блок 4: Тест Scratchpad
    f.append(rect(100, 320, 240, 64, fill="#eafaf1", stroke=COLOR_OK, sw=1.8))
    f.append(text(220, 340, "4. Тест Scratchpad R/W", size=12, bold=True, color=COLOR_OK))
    f.append(text(220, 357, "Запис/читання 0x55, 0xAA", size=10.5, color=INK))
    f.append(text(220, 372, "Перевірка повнодуплексного тракту", size=9.5, color=MUTED))

    # Стрілка 4 -> 5
    f.append(arrow(220, 384, 220, 424, color=COLOR_OK, sw=2.0))

    # Блок 5: Готовність до конфігурації
    f.append(rect(100, 424, 240, 54, fill=COLOR_OK, stroke=COLOR_OK, sw=1.8))
    f.append(text(220, 446, "5. Чип валідовано!", size=13, bold=True, color=BG))
    f.append(text(220, 464, "Перехід до налаштування драйвера", size=10.5, color="#d5f5e3"))

    render(os.path.join(IMG, "bringup-flowchart.svg"), W, H, *f)


# ── 2. Часова діаграма зсуву бітів SPI (spi-bit-shift.svg) ───────────────────
def fig_spi_bit_shift():
    W, H = 820, 440
    f = [text(W / 2, 26, "Пастка SPI CPOL / CPHA: механізм зсуву бітів на одиницю", size=16, bold=True)]
    f.append(text(W / 2, 46, "чому зчитування на неправильному фронті такту множить ідентифікатор на 2",
                  size=11, color=MUTED, italic=True))

    # Ліва колонка: мітки сигналів
    x_lbl = 90
    f.append(text(x_lbl, 95, "CS (вибір)", size=12, bold=True, anchor="end"))
    f.append(text(x_lbl, 160, "SCK (такт)", size=12, bold=True, anchor="end"))
    f.append(text(x_lbl, 230, "MISO (слейв)", size=12, bold=True, anchor="end"))
    f.append(text(x_lbl, 310, "Mode 0 (CPHA=0)", size=11, color=COLOR_OK, bold=True, anchor="end"))
    f.append(text(x_lbl, 370, "Mode 1 (CPHA=1)", size=11, color=COLOR_WARN, bold=True, anchor="end"))

    # Часова вісь X: початок 130, кінець 780
    x0 = 130
    bit_w = 75

    # Сигнал CS
    f.append(line(x0, 80, x0 + 30, 80, color=INK, sw=2))
    f.append(line(x0 + 30, 80, x0 + 40, 110, color=INK, sw=2))
    f.append(line(x0 + 40, 110, x0 + 640, 110, color=INK, sw=2))

    # Сигнал SCK: 8 періодів (CPOL=0)
    sck_y_hi = 145
    sck_y_lo = 175
    f.append(line(x0, sck_y_lo, x0 + 50, sck_y_lo, color=COLOR_INFO, sw=2))

    for i in range(8):
        bx = x0 + 50 + i * bit_w
        # Фронт вгору
        f.append(line(bx, sck_y_lo, bx, sck_y_hi, color=COLOR_INFO, sw=2))
        # Високий рівень
        f.append(line(bx, sck_y_hi, bx + bit_w / 2, sck_y_hi, color=COLOR_INFO, sw=2))
        # Спад вниз
        f.append(line(bx + bit_w / 2, sck_y_hi, bx + bit_w / 2, sck_y_lo, color=COLOR_INFO, sw=2))
        # Низький рівень
        f.append(line(bx + bit_w / 2, sck_y_lo, bx + bit_w, sck_y_lo, color=COLOR_INFO, sw=2))
        # Номер такту
        f.append(text(bx + bit_w / 4, 136, f"#{i+1}", size=9.5, color=COLOR_INFO))

    # MISO дані: передається 0x68 = 0b01101000
    # Біти: b7=0, b6=1, b5=1, b4=0, b3=1, b2=0, b1=0, b0=0
    bits = [0, 1, 1, 0, 1, 0, 0, 0]
    data_y_hi = 215
    data_y_lo = 245

    f.append(line(x0, data_y_lo, x0 + 40, data_y_lo, color=INK, sw=1.5, dash="3,3"))

    for i, b in enumerate(bits):
        bx = x0 + 50 + i * bit_w
        by = data_y_hi if b == 1 else data_y_lo
        prev_by = data_y_lo if i == 0 else (data_y_hi if bits[i-1] == 1 else data_y_lo)

        if i > 0 and prev_by != by:
            f.append(line(bx, prev_by, bx, by, color=INK, sw=2))
        f.append(line(bx, by, bx + bit_w, by, color=INK, sw=2))
        f.append(text(bx + bit_w / 2, (data_y_hi + data_y_lo) / 2 + 4, f"b{7-i}={b}", size=11, bold=True))

    # Стробування Mode 0 (вибірка на передньому фронті ↑)
    # Зразки: b7(0), b6(1), b5(1), b4(0), b3(1), b2(0), b1(0), b0(0) -> 0x68
    f.append(rect(x0 + 40, 292, 630, 36, fill="#eafaf1", stroke=COLOR_OK, sw=1.2, rx=4))
    f.append(text(x0 + 48, 314, "Вибірка ↑ (передній фронт):", size=10.5, color=COLOR_OK, anchor="start", bold=True))
    f.append(text(x0 + 260, 314, "0  1  1  0  1  0  0  0  →  0x68 (Еталонний WHO_AM_I)", size=11, color=COLOR_OK, anchor="start", bold=True))

    for i in range(8):
        bx = x0 + 50 + i * bit_w
        f.append(arrow(bx, 280, bx, 292, color=COLOR_OK, sw=1.5))

    # Стробування Mode 1 (вибірка на задньому спаді ↓)
    # Зразки: b6(1), b5(1), b4(0), b3(1), b2(0), b1(0), b0(0), 0 -> 0xD0
    f.append(rect(x0 + 40, 352, 630, 36, fill="#fef9e7", stroke=COLOR_WARN, sw=1.2, rx=4))
    f.append(text(x0 + 48, 374, "Вибірка ↓ (задній спад):", size=10.5, color=COLOR_WARN, anchor="start", bold=True))
    f.append(text(x0 + 260, 374, "1  1  0  1  0  0  0  0  →  0xD0 (Зсув вліво на 1 біт = 0x68 << 1)", size=11, color=COLOR_WARN, anchor="start", bold=True))

    for i in range(8):
        bx = x0 + 50 + i * bit_w + bit_w / 2
        f.append(arrow(bx, 340, bx, 352, color=COLOR_WARN, sw=1.5))

    # Підсумок знизу
    f.append(text(W / 2, 418, "Слейв виставив b7 до такту; зчитувач Mode 1 запізнився і замість b7 захопив наступний b6!", size=11, color=INK, italic=True))

    render(os.path.join(IMG, "spi-bit-shift.svg"), W, H, *f)


# ── 3. Фізичні рівні та матриця дефектів (bus-fault-levels.svg) ───────────────
def fig_bus_fault_levels():
    W, H = 820, 380
    f = [text(W / 2, 26, "Матриця фізичних станів шини та зчитаних кодів", size=16, bold=True)]
    f.append(text(W / 2, 46, "як фізичний стан лінії MISO/SDA відображається у значеннях першого байта",
                  size=11, color=MUTED, italic=True))

    col_w = 230
    y_top = 70
    box_h = 270

    # Колонка 1: Стан 0xFF (Підтяжка до VCC / Обрив)
    x1 = 35
    f.append(rect(x1, y_top, col_w, box_h, fill="#fdf2e9", stroke=COLOR_ERR, sw=1.8))
    f.append(rect(x1, y_top, col_w, 36, fill=COLOR_ERR, stroke=COLOR_ERR, sw=1.8, rx=6))
    f.append(text(x1 + col_w / 2, y_top + 23, "Код 0xFF (0b11111111)", size=12.5, color=BG, bold=True))

    f.append(text(x1 + 16, y_top + 60, "Фізичний стан лінії:", size=11, bold=True, anchor="start", color=COLOR_ERR))
    f.append(text(x1 + 16, y_top + 80, "• Лінія постійно у стані HIGH (+3.3V)", size=10, anchor="start"))
    f.append(text(x1 + 16, y_top + 98, "• Підтяжка до VCC через pull-up", size=10, anchor="start"))

    f.append(text(x1 + 16, y_top + 130, "Типові причини:", size=11, bold=True, anchor="start"))
    f.append(text(x1 + 16, y_top + 150, "1. Чип не впаяний або обрив MISO/SDA", size=9.5, anchor="start"))
    f.append(text(x1 + 16, y_top + 168, "2. Немає живлення VDD чи VDDIO", size=9.5, anchor="start"))
    f.append(text(x1 + 16, y_top + 186, "3. Чип утримується в стані RESET", size=9.5, anchor="start"))
    f.append(text(x1 + 16, y_top + 204, "4. CS не опустився в LOW (SPI)", size=9.5, anchor="start"))
    f.append(text(x1 + 16, y_top + 222, "5. Хибна 7-біт адреса (NACK на I2C)", size=9.5, anchor="start"))

    f.append(rect(x1 + 10, y_top + 236, col_w - 20, 24, fill="#fadbd8", stroke="none", rx=3))
    f.append(text(x1 + col_w / 2, y_top + 252, "Перевірка: вольтметр на VDD та CS", size=9.5, color=COLOR_ERR, bold=True))

    # Колонка 2: Стан 0x00 (Замикання на GND)
    x2 = x1 + col_w + 30
    f.append(rect(x2, y_top, col_w, box_h, fill="#fdf2e9", stroke=COLOR_ERR, sw=1.8))
    f.append(rect(x2, y_top, col_w, 36, fill=COLOR_ERR, stroke=COLOR_ERR, sw=1.8, rx=6))
    f.append(text(x2 + col_w / 2, y_top + 23, "Код 0x00 (0b00000000)", size=12.5, color=BG, bold=True))

    f.append(text(x2 + 16, y_top + 60, "Фізичний стан лінії:", size=11, bold=True, anchor="start", color=COLOR_ERR))
    f.append(text(x2 + 16, y_top + 80, "• Лінія постійно у стані LOW (0V)", size=10, anchor="start"))
    f.append(text(x2 + 16, y_top + 98, "• Притиснута до GND або зависла", size=10, anchor="start"))

    f.append(text(x2 + 16, y_top + 130, "Типові причини:", size=11, bold=True, anchor="start"))
    f.append(text(x2 + 16, y_top + 150, "1. Коротке замикання MISO/SDA на GND", size=9.5, anchor="start"))
    f.append(text(x2 + 16, y_top + 168, "2. Зависла I2C шина (слейв тримає 0)", size=9.5, anchor="start"))
    f.append(text(x2 + 16, y_top + 186, "3. MISO у Z-стані без підтяжки", size=9.5, anchor="start"))
    f.append(text(x2 + 16, y_top + 204, "4. Чип перезавантажується в циклі", size=9.5, anchor="start"))
    f.append(text(x2 + 16, y_top + 222, "5. Хибний номер регістра ID", size=9.5, anchor="start"))

    f.append(rect(x2 + 10, y_top + 236, col_w - 20, 24, fill="#fadbd8", stroke="none", rx=3))
    f.append(text(x2 + col_w / 2, y_top + 252, "Перевірка: продзвонка на GND", size=9.5, color=COLOR_ERR, bold=True))

    # Колонка 3: Валідний ID (0x68 / 0x60 / 0xE5)
    x3 = x2 + col_w + 30
    f.append(rect(x3, y_top, col_w, box_h, fill="#eafaf1", stroke=COLOR_OK, sw=1.8))
    f.append(rect(x3, y_top, col_w, 36, fill=COLOR_OK, stroke=COLOR_OK, sw=1.8, rx=6))
    f.append(text(x3 + col_w / 2, y_top + 23, "Валідний ID (напр. 0x68)", size=12.5, color=BG, bold=True))

    f.append(text(x3 + 16, y_top + 60, "Фізичний стан лінії:", size=11, bold=True, anchor="start", color=COLOR_OK))
    f.append(text(x3 + 16, y_top + 80, "• Активна комутація 0 та 1", size=10, anchor="start"))
    f.append(text(x3 + 16, y_top + 98, "• Асиметричний бітовий патерн", size=10, anchor="start"))

    f.append(text(x3 + 16, y_top + 130, "Що підтверджено:", size=11, bold=True, anchor="start"))
    f.append(text(x3 + 16, y_top + 150, "1. Живлення та опорне джерело в нормі", size=9.5, anchor="start"))
    f.append(text(x3 + 16, y_top + 168, "2. Лінії SCK, MOSI, MISO/SDA цілі", size=9.5, anchor="start"))
    f.append(text(x3 + 16, y_top + 186, "3. Адресація та протокол узгоджені", size=9.5, anchor="start"))
    f.append(text(x3 + 16, y_top + 204, "4. Кремній розпізнав команду читання", size=9.5, anchor="start"))
    f.append(text(x3 + 16, y_top + 222, "5. Готовий до тесту Scratchpad R/W", size=9.5, anchor="start"))

    f.append(rect(x3 + 10, y_top + 236, col_w - 20, 24, fill="#d5f5e3", stroke="none", rx=3))
    f.append(text(x3 + col_w / 2, y_top + 252, "Статус: зв'язок встановлено!", size=9.5, color=COLOR_OK, bold=True))

    render(os.path.join(IMG, "bus-fault-levels.svg"), W, H, *f)


# ── 4. Тест читання-запису Scratchpad (scratchpad-test.svg) ───────────────────
def fig_scratchpad_test():
    W, H = 820, 360
    f = [text(W / 2, 26, "Тест Scratchpad: перевірка повнодуплексного обміну", size=16, bold=True)]
    f.append(text(W / 2, 46, "чому WHO_AM_I доводить лише читання, а тестовий запис підтверджує обидва напрямки",
                  size=11, color=MUTED, italic=True))

    # Схема: MCU ліворуч, Чип праворуч
    mcu_x, mcu_y = 60, 80
    mcu_w, mcu_h = 200, 230

    chip_x, chip_y = 560, 80
    chip_w, chip_h = 200, 230

    # MCU Box
    f.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 30, "Мікроконтролер", size=13, bold=True))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 48, "(Master)", size=11, color=MUTED))

    # Chip Box
    f.append(rect(chip_x, chip_y, chip_w, chip_h, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(chip_x + chip_w / 2, chip_y + 30, "Сенсор / Пам'ять", size=13, bold=True))
    f.append(text(chip_x + chip_w / 2, chip_y + 48, "(Slave)", size=11, color=MUTED))

    # Регістри всередині чипа
    f.append(rect(chip_x + 20, chip_y + 70, chip_w - 40, 42, fill="#f0f3f4", stroke=MUTED, sw=1))
    f.append(text(chip_x + chip_w / 2, chip_y + 88, "WHO_AM_I (0x75)", size=10.5, bold=True))
    f.append(text(chip_x + chip_w / 2, chip_y + 103, "Тільки читання (ROM 0x68)", size=9, color=COLOR_ERR))

    f.append(rect(chip_x + 20, chip_y + 124, chip_w - 40, 78, fill="#eafaf1", stroke=COLOR_OK, sw=1.5))
    f.append(text(chip_x + chip_w / 2, chip_y + 144, "Scratchpad / Config", size=10.5, bold=True, color=COLOR_OK))
    f.append(text(chip_x + chip_w / 2, chip_y + 160, "Читання та запис (RAM)", size=9.5, color=INK))
    f.append(text(chip_x + chip_w / 2, chip_y + 178, "Тригери: 0x55, 0xAA", size=10, bold=True, color=COLOR_OK))

    # Стрілки передачі:
    # 1. MOSI (Запис 0x55)
    f.append(arrow(mcu_x + mcu_w, 190, chip_x, 190, color=COLOR_INFO, sw=2))
    f.append(rect(310, 172, 200, 36, fill="#eaf2f8", stroke=COLOR_INFO, sw=1.2, rx=4))
    f.append(text(410, 188, "1. Запис MOSI: 0x55", size=11, bold=True, color=COLOR_INFO))
    f.append(text(410, 201, "0b01010101 (чергування 0 та 1)", size=9, color=MUTED))

    # 2. MISO (Зворотне читання)
    f.append(arrow(chip_x, 250, mcu_x + mcu_w, 250, color=COLOR_OK, sw=2))
    f.append(rect(310, 232, 200, 36, fill="#eafaf1", stroke=COLOR_OK, sw=1.2, rx=4))
    f.append(text(410, 248, "2. Читання MISO: 0x55", size=11, bold=True, color=COLOR_OK))
    f.append(text(410, 261, "Звірка: значення збіглося!", size=9, color=COLOR_OK, bold=True))

    # Підсумок знизу
    f.append(rect(60, 320, 700, 30, fill="#fef9e7", stroke=COLOR_WARN, sw=1, rx=4))
    f.append(text(410, 340, "Тест інверсним патерном 0xAA (0b10101010) гарантує відсутність залипання кожного окремого біта!", size=10.5, color=INK, bold=True))

    render(os.path.join(IMG, "scratchpad-test.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bringup_flowchart()
    fig_spi_bit_shift()
    fig_bus_fault_levels()
    fig_scratchpad_test()
    print("All figures generated successfully in ./img/")

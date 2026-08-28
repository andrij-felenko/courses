# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра для архітектурних та апаратних рівнів
COLOR_APP   = "#2c3e50"   # Застосунок / алгоритми
COLOR_APP_F = "#eaeded"
COLOR_DEV   = "#1e8449"   # Логіка чипа / сенсора (зелений)
COLOR_DEV_F = "#d5f5e3"
COLOR_TRX   = "#2471a3"   # Рівень транзакцій (синій)
COLOR_TRX_F = "#d4e6f1"
COLOR_HAL   = "#b9770e"   # Апаратний HAL / шина (амбра)
COLOR_HAL_F = "#fdf3d6"
COLOR_HW    = "#7d3c98"   # Фізичні мікросхеми / піни (фіолетовий)
COLOR_HW_F  = "#f4ecf7"
COLOR_WARN  = "#c0392b"
COLOR_WARNF = "#fdecea"


def fig_three_layer_driver_architecture():
    """
    Трирівнева архітектура драйверів:
    1) Device Logic (Логіка чипа)
    2) Transaction Layer (Рівень транзакцій — абстракція reg_read/reg_write, CS, блокування)
    3) Bus Physical Layer (HAL I2C / SPI / DMA / Mock)
    """
    W, H = 880, 680
    p = []

    bx, bw = 50, 780

    # Рівень 0: Застосунок
    y_app = 35
    h_app = 65
    p.append(rect(bx, y_app, bw, h_app, fill=COLOR_APP_F, stroke=COLOR_APP, sw=2.0, rx=6))
    p.append(text(bx + bw / 2, y_app + 26, "Застосунок / Системна логіка (Application Layer)", size=14, color=COLOR_APP, bold=True))
    p.append(text(bx + bw / 2, y_app + 48, "Отримує фізичні величини у SI (м/с², рад/с, Па, °C), стан FIFO, готовність даних", size=11, color=INK))

    # Стрілка вниз
    p.append(arrow(bx + bw / 2, y_app + h_app, bx + bw / 2, y_app + h_app + 20, color=LINE, sw=2.0))

    # Рівень 3: Драйвер чипа (Device Logic)
    y_dev = 120
    h_dev = 110
    p.append(rect(bx, y_dev, bw, h_dev, fill=COLOR_DEV_F, stroke=COLOR_DEV, sw=2.0, rx=6))
    p.append(text(bx + bw / 2, y_dev + 26, "Рівень 3: Логіка чипа / Драйвер пристрою (Device Logic)", size=14, color=COLOR_DEV, bold=True))
    p.append(text(bx + bw / 2, y_dev + 50, "Регістрова карта · Математика перетворення сирих відліків у SI · Калібрування", size=11.5, color=INK))
    p.append(text(bx + bw / 2, y_dev + 72, "Послідовність ініціалізації (Power-on, Soft Reset) · Робота з перериваннями та FIFO", size=11.5, color=INK))
    p.append(text(bx + bw / 2, y_dev + 94, "НЕ знає деталей шини — викликає виключно: bus->read_reg() та bus->write_reg()", size=11, color=COLOR_DEV, bold=True))

    # Стрілка вниз
    p.append(arrow(bx + bw / 2, y_dev + h_dev, bx + bw / 2, y_dev + h_dev + 20, color=LINE, sw=2.0))

    # Рівень 2: Рівень транзакцій (Transaction Layer)
    y_trx = 250
    h_trx = 135
    p.append(rect(bx, y_trx, bw, h_trx, fill=COLOR_TRX_F, stroke=COLOR_TRX, sw=2.5, rx=6))
    p.append(text(bx + bw / 2, y_trx + 26, "Рівень 2: Рівень транзакцій (Bus Transaction Layer) — Уніфікована межа", size=15, color=COLOR_TRX, bold=True))
    p.append(text(bx + bw / 2, y_trx + 52, "Уніфікований інтерфейс: reg_read(), reg_write(), read_modify_write(), burst_transfer()", size=12, color=INK, bold=True))
    p.append(text(bx + bw / 2, y_trx + 76, "Кадрування протоколу: прапорці R/W, автоінкремент адрес, dummy-байти, 8/16-біт регістри", size=11, color=INK))
    p.append(text(bx + bw / 2, y_trx + 98, "Керування доступом: м'ютекси шини (FreeRTOS / потокобезпечність), таймінги CS (t_CSS, t_CSH)", size=11, color=INK))
    p.append(text(bx + bw / 2, y_trx + 120, "Обробка помилок: таймаути шини, I2C NACK, втрата арбітражу, повторні спроби (retries)", size=11, color=COLOR_TRX))

    # Розгалуження стрілок до адаптерів
    p.append(arrow(bx + 130, y_trx + h_trx, bx + 130, y_trx + h_trx + 24, color=LINE, sw=1.8))
    p.append(arrow(bx + 390, y_trx + h_trx, bx + 390, y_trx + h_trx + 24, color=LINE, sw=1.8))
    p.append(arrow(bx + 650, y_trx + h_trx, bx + 650, y_trx + h_trx + 24, color=LINE, sw=1.8))

    # Рівень 1: Апаратні адаптери шин (Bus Physical HAL)
    y_hal = 409
    h_hal = 115
    w_card = 240
    gap_card = 30

    # Адаптер I2C
    x_i2c = bx
    p.append(rect(x_i2c, y_hal, w_card, h_hal, fill=COLOR_HAL_F, stroke=COLOR_HAL, sw=1.8, rx=6))
    p.append(text(x_i2c + w_card / 2, y_hal + 24, "I2C Bus Adapter", size=13, color=COLOR_HAL, bold=True))
    p.append(text(x_i2c + w_card / 2, y_hal + 46, "7-біт / 10-біт адресація", size=11, color=INK))
    p.append(text(x_i2c + w_card / 2, y_hal + 66, "Repeated START без STOP", size=11, color=INK))
    p.append(text(x_i2c + w_card / 2, y_hal + 86, "Clock stretching та обробка ACK", size=10.5, color=INK))
    p.append(text(x_i2c + w_card / 2, y_hal + 104, "I2C HAL / Драйвер ядра", size=10, color=MUTED))

    # Адаптер SPI
    x_spi = bx + w_card + gap_card
    p.append(rect(x_spi, y_hal, w_card, h_hal, fill=COLOR_HAL_F, stroke=COLOR_HAL, sw=1.8, rx=6))
    p.append(text(x_spi + w_card / 2, y_hal + 24, "SPI Bus Adapter", size=13, color=COLOR_HAL, bold=True))
    p.append(text(x_spi + w_card / 2, y_hal + 46, "Керування піном CS (GPIO/HW)", size=11, color=INK))
    p.append(text(x_spi + w_card / 2, y_hal + 66, "Режими CPOL / CPHA (0..3)", size=11, color=INK))
    p.append(text(x_spi + w_card / 2, y_hal + 86, "Full-Duplex DMA / FIFO буфери", size=10.5, color=INK))
    p.append(text(x_spi + w_card / 2, y_hal + 104, "SPI HAL / spidev", size=10, color=MUTED))

    # Mock / Тестовий адаптер
    x_mock = bx + 2 * (w_card + gap_card)
    p.append(rect(x_mock, y_hal, w_card, h_hal, fill=COLOR_APP_F, stroke=COLOR_APP, sw=1.8, rx=6))
    p.append(text(x_mock + w_card / 2, y_hal + 24, "Mock / Loopback Adapter", size=13, color=COLOR_APP, bold=True))
    p.append(text(x_mock + w_card / 2, y_hal + 46, "Пам'ять регістрів у RAM хоста", size=11, color=INK))
    p.append(text(x_mock + w_card / 2, y_hal + 66, "Моделювання збоїв та NACK", size=11, color=INK))
    p.append(text(x_mock + w_card / 2, y_hal + 86, "Unit-тести без заліза (CI/CD)", size=10.5, color=INK))
    p.append(text(x_mock + w_card / 2, y_hal + 104, "POSIX / Windows x86", size=10, color=MUTED))

    # Стрілки до заліза
    p.append(arrow(x_i2c + w_card / 2, y_hal + h_hal, x_i2c + w_card / 2, y_hal + h_hal + 24, color=LINE, sw=1.8))
    p.append(arrow(x_spi + w_card / 2, y_hal + h_hal, x_spi + w_card / 2, y_hal + h_hal + 24, color=LINE, sw=1.8))
    p.append(arrow(x_mock + w_card / 2, y_hal + h_hal, x_mock + w_card / 2, y_hal + h_hal + 24, color=LINE, sw=1.8))

    # Фізичне залізо / Цільові пристрої
    y_hw = 548
    h_hw = 88

    # I2C чіп
    p.append(rect(x_i2c, y_hw, w_card, h_hw, fill=COLOR_HW_F, stroke=COLOR_HW, sw=1.8, rx=6))
    p.append(text(x_i2c + w_card / 2, y_hw + 24, "Фізичний чіп на I2C", size=12.5, color=COLOR_HW, bold=True))
    p.append(text(x_i2c + w_card / 2, y_hw + 46, "Лінії SCL, SDA (відкритий стік)", size=11, color=INK))
    p.append(text(x_i2c + w_card / 2, y_hw + 68, "Підтяжки Pull-Up до VDD", size=11, color=INK))

    # SPI чіп
    p.append(rect(x_spi, y_hw, w_card, h_hw, fill=COLOR_HW_F, stroke=COLOR_HW, sw=1.8, rx=6))
    p.append(text(x_spi + w_card / 2, y_hw + 24, "Фізичний чіп на SPI", size=12.5, color=COLOR_HW, bold=True))
    p.append(text(x_spi + w_card / 2, y_hw + 46, "Лінії SCK, MOSI, MISO, CS", size=11, color=INK))
    p.append(text(x_spi + w_card / 2, y_hw + 68, "Двотактний Push-Pull, висока швидкість", size=11, color=INK))

    # Host Memory Mock
    p.append(rect(x_mock, y_hw, w_card, h_hw, fill=COLOR_APP_F, stroke=COLOR_APP, sw=1.8, rx=6))
    p.append(text(x_mock + w_card / 2, y_hw + 24, "Емулятор регістрів", size=12.5, color=COLOR_APP, bold=True))
    p.append(text(x_mock + w_card / 2, y_hw + 46, "uint8_t mock_regs[256]", size=11, color=INK))
    p.append(text(x_mock + w_card / 2, y_hw + 68, "Перевірка логіки перетворення", size=11, color=INK))

    render(os.path.join(OUT, "three-layer-driver-architecture.svg"), W, H, *p)


def fig_spi_vs_i2c_transaction_framing():
    """
    Порівняння кадрування транзакції блокового читання регістрів (Burst Read)
    на шинах I2C та SPI для того самого датчика.
    """
    W, H = 940, 650
    p = []

    # Заголовок діаграми
    p.append(text(W / 2, 30, "Анатомія транзакції Burst Read (читання 2 байтів із регістра 0x1F)", size=15, color=INK, bold=True))

    # ── БЛОК I2C ────────────────────────────────────────────────────────────
    y_i2c = 60
    p.append(rect(30, y_i2c, 880, 260, fill="#fdfefe", stroke=COLOR_HAL, sw=1.8, rx=6))
    p.append(text(50, y_i2c + 24, "Шина I2C (Half-Duplex, 2 дроти: SCL/SDA, 7-біт адреса пристрою 0x68)", size=13, color=COLOR_HAL, bold=True, anchor="start"))

    cards_i2c = [
        ("S", "START", 36, COLOR_WARNF, COLOR_WARN),
        ("0xD0", "Dev 0x68+W", 82, COLOR_HAL_F, COLOR_HAL),
        ("A", "ACK", 34, COLOR_DEV_F, COLOR_DEV),
        ("0x1F", "Reg Addr", 80, COLOR_TRX_F, COLOR_TRX),
        ("A", "ACK", 34, COLOR_DEV_F, COLOR_DEV),
        ("Sr", "Rep.START", 76, COLOR_WARNF, COLOR_WARN),
        ("0xD1", "Dev 0x68+R", 82, COLOR_HAL_F, COLOR_HAL),
        ("A", "ACK", 34, COLOR_DEV_F, COLOR_DEV),
        ("0x4A", "Data[0]", 76, COLOR_DEV_F, COLOR_DEV),
        ("A", "ACK (M)", 68, COLOR_APP_F, COLOR_APP),
        ("0x02", "Data[1]", 76, COLOR_DEV_F, COLOR_DEV),
        ("N", "NACK", 36, COLOR_WARNF, COLOR_WARN),
        ("P", "STOP", 36, COLOR_WARNF, COLOR_WARN)
    ]

    cur_x = 48
    y_blocks_i2c = y_i2c + 45
    h_block = 54

    for code, label, width, fill, stroke in cards_i2c:
        p.append(rect(cur_x, y_blocks_i2c, width, h_block, fill=fill, stroke=stroke, sw=1.5, rx=4))
        p.append(text(cur_x + width / 2, y_blocks_i2c + 23, code, size=12, color=stroke, bold=True))
        p.append(text(cur_x + width / 2, y_blocks_i2c + 43, label, size=10, color=INK))
        cur_x += width + 6

    # Пояснення специфіки I2C
    y_exp_i2c = y_i2c + 115
    p.append(rect(48, y_exp_i2c, 844, 125, fill=COLOR_HAL_F, stroke=COLOR_HAL, sw=1.2, rx=4))
    p.append(text(65, y_exp_i2c + 24, "• Фаза запису вказівника:", size=11, color=COLOR_HAL, bold=True, anchor="start"))
    p.append(text(255, y_exp_i2c + 24, "Майстер надсилає 0xD0 (адреса чіпа + біт Write=0) та адресу регістра 0x1F.", size=11, color=INK, anchor="start"))
    p.append(text(65, y_exp_i2c + 50, "• Repeated START (Sr):", size=11, color=COLOR_WARN, bold=True, anchor="start"))
    p.append(text(255, y_exp_i2c + 50, "Формується без сигналу STOP — утримує шину від перехоплення іншим майстром.", size=11, color=INK, anchor="start"))
    p.append(text(65, y_exp_i2c + 76, "• Фаза зчитування байтів:", size=11, color=COLOR_DEV, bold=True, anchor="start"))
    p.append(text(255, y_exp_i2c + 76, "0xD1 (біт Read=1). Датчик повертає байти з автоінкрементом внутрішнього лічильника.", size=11, color=INK, anchor="start"))
    p.append(text(65, y_exp_i2c + 102, "• Завершення читання:", size=11, color=COLOR_APP, bold=True, anchor="start"))
    p.append(text(255, y_exp_i2c + 102, "Майстер підтверджує всі проміжні байти (ACK) і шле NACK на останньому байті перед STOP.", size=11, color=INK, anchor="start"))

    # ── БЛОК SPI ────────────────────────────────────────────────────────────
    y_spi = 335
    p.append(rect(30, y_spi, 880, 290, fill="#fdfefe", stroke=COLOR_TRX, sw=1.8, rx=6))
    p.append(text(50, y_spi + 24, "Шина SPI (Full-Duplex, 4 дроти: SCK/MOSI/MISO/CS, тактування до 10-20 МГц)", size=13, color=COLOR_TRX, bold=True, anchor="start"))

    # Рівні сигналів CS, MOSI, MISO
    y_sig = y_spi + 42

    # Сигнал CS
    p.append(text(50, y_sig + 18, "CS (NSS):", size=11, color=COLOR_WARN, bold=True, anchor="start"))
    p.append(line(125, y_sig + 6, 155, y_sig + 6, color=COLOR_WARN, sw=2))      # HIGH
    p.append(line(155, y_sig + 6, 168, y_sig + 26, color=COLOR_WARN, sw=2))     # Фронт спаду
    p.append(line(168, y_sig + 26, 820, y_sig + 26, color=COLOR_WARN, sw=2))    # LOW (Active)
    p.append(line(820, y_sig + 26, 833, y_sig + 6, color=COLOR_WARN, sw=2))     # Фронт наростання
    p.append(line(833, y_sig + 6, 875, y_sig + 6, color=COLOR_WARN, sw=2))      # HIGH
    p.append(text(168, y_sig + 38, "t_CSS", size=10, color=MUTED, anchor="middle"))
    p.append(text(825, y_sig + 38, "t_CSH", size=10, color=MUTED, anchor="middle"))

    # Байти MOSI та MISO
    y_bytes = y_sig + 50

    cards_spi_mosi = [
        ("0x9F (0x80 | 0x1F)", "MOSI: Read Flag (MSB=1) + Reg 0x1F", 230, COLOR_TRX_F, COLOR_TRX),
        ("0x00 (Dummy TX)", "MOSI: Тактування Data[0]", 210, COLOR_APP_F, COLOR_APP),
        ("0x00 (Dummy TX)", "MOSI: Тактування Data[1]", 210, COLOR_APP_F, COLOR_APP),
    ]

    cur_x = 175
    for code, label, width, fill, stroke in cards_spi_mosi:
        p.append(rect(cur_x, y_bytes, width, 40, fill=fill, stroke=stroke, sw=1.5, rx=4))
        p.append(text(cur_x + width / 2, y_bytes + 17, code, size=11, color=stroke, bold=True))
        p.append(text(cur_x + width / 2, y_bytes + 32, label, size=10, color=INK))
        cur_x += width + 15

    y_miso = y_bytes + 48
    cards_spi_miso = [
        ("0xFF / High-Z", "MISO: Turnaround / Ігнорується", 230, COLOR_APP_F, MUTED),
        ("0x4A", "MISO: Зчитаний байт Data[0]", 210, COLOR_DEV_F, COLOR_DEV),
        ("0x02", "MISO: Зчитаний байт Data[1]", 210, COLOR_DEV_F, COLOR_DEV),
    ]

    cur_x = 175
    for code, label, width, fill, stroke in cards_spi_miso:
        p.append(rect(cur_x, y_miso, width, 40, fill=fill, stroke=stroke, sw=1.5, rx=4))
        p.append(text(cur_x + width / 2, y_miso + 17, code, size=11, color=stroke, bold=True))
        p.append(text(cur_x + width / 2, y_miso + 32, label, size=10, color=INK))
        cur_x += width + 15

    # Пояснення SPI
    y_exp_spi = y_miso + 52
    p.append(rect(48, y_exp_spi, 844, 86, fill=COLOR_TRX_F, stroke=COLOR_TRX, sw=1.2, rx=4))
    p.append(text(65, y_exp_spi + 22, "• Прапорець читання (R/W Bit):", size=11, color=COLOR_TRX, bold=True, anchor="start"))
    p.append(text(295, y_exp_spi + 22, "У SPI немає адреси чіпа; біт 7 байта адреси (0x80) вказує читання: 0x80 | 0x1F = 0x9F.", size=10.5, color=INK, anchor="start"))
    p.append(text(65, y_exp_spi + 46, "• Повнодуплексний обмін (Full-Duplex):", size=11, color=COLOR_DEV, bold=True, anchor="start"))
    p.append(text(295, y_exp_spi + 46, "Щоб отримати байти на лінії MISO, майстер мусить передавати фіктивні нулі (0x00) на MOSI.", size=10.5, color=INK, anchor="start"))
    p.append(text(65, y_exp_spi + 70, "• Атомарність через лінію CS:", size=11, color=COLOR_WARN, bold=True, anchor="start"))
    p.append(text(295, y_exp_spi + 70, "Транзакція обмежена спадом і підйомом CS. Весь пакет читається в єдиній сесії вибору чіпа.", size=10.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "spi-vs-i2c-transaction-framing.svg"), W, H, *p)


if __name__ == "__main__":
    fig_three_layer_driver_architecture()
    fig_spi_vs_i2c_transaction_framing()
    print("Фігури успішно згенеровано.")

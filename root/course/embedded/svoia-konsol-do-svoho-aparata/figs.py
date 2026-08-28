# -*- coding: utf-8 -*-
"""figs.py — ілюстрації до теми «Своя консоль до свого апарата: мінімальний пульт».
svgkit імпортується зі scripts/, вивід у ./img/."""
import sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(SCRIPT_DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(SCRIPT_DIR, '..', '..', '..', '..', 'scripts'))
from svgkit import *

def path(d, fill="none", stroke=LINE, sw=1.5):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'

# ── Фігура 1: Апаратна архітектура кастомного пульта ────────────────────────
def fig_console_hardware_architecture():
    W, H = 1040, 580
    P = []
    P.append(text(W / 2, 28, "Апаратна архітектура портативного пульта керування",
                  size=16, bold=True))

    # Ліва колонка: Живлення та Аналогове введення
    # Блок 1.1: Підсистема живлення (верхній лівий)
    pwr_x, pwr_y, pwr_w, pwr_h = 20, 55, 280, 240
    P.append(rect(pwr_x, pwr_y, pwr_w, pwr_h, fill="#fffbf5", stroke="#e67e22", sw=1.5, rx=8))
    P.append(text(pwr_x + pwr_w / 2, pwr_y + 22, "Підсистема живлення (PMIC)", size=12.5, color="#d35400", bold=True))
    
    P.append(rect(pwr_x + 12, pwr_y + 36, 120, 44, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    P.append(text(pwr_x + 72, pwr_y + 54, "Li-Ion 1S (3.7V)", size=10.5, bold=True))
    P.append(text(pwr_x + 72, pwr_y + 69, "18650 / 3500 mAh", size=9.5, color=MUTED))

    P.append(rect(pwr_x + 144, pwr_y + 36, 124, 44, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    P.append(text(pwr_x + 206, pwr_y + 54, "USB-C + TP4056", size=10.5, bold=True))
    P.append(text(pwr_x + 206, pwr_y + 69, "CC/CV Заряд 1.0 A", size=9.5, color=MUTED))

    P.append(rect(pwr_x + 12, pwr_y + 90, 256, 52, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    P.append(text(pwr_x + 140, pwr_y + 110, "Low-Iq LDO 3.3V (AP2112K / XC6206)", size=10.5, bold=True))
    P.append(text(pwr_x + 140, pwr_y + 128, "Iq = 55 µA, Imax = 600 mA, Vdrop = 250 mV", size=9.5, color=MUTED))

    P.append(rect(pwr_x + 12, pwr_y + 152, 256, 72, fill="#ffffff", stroke="#e67e22", sw=1.2, rx=4))
    P.append(text(pwr_x + 140, pwr_y + 172, "Ключ живлення периферії (P-MOS)", size=10.5, color="#d35400", bold=True))
    P.append(text(pwr_x + 140, pwr_y + 190, "AO3401 / TPS22918 Load Switch", size=9.5, color=MUTED))
    P.append(text(pwr_x + 140, pwr_y + 208, "Дільник Vbat + N-MOS затвор для АЦП", size=9.5, color=MUTED))

    # Блок 1.2: Органи введення (нижній лівий)
    inp_x, inp_y, inp_w, inp_h = 20, 310, 280, 250
    P.append(rect(inp_x, inp_y, inp_w, inp_h, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    P.append(text(inp_x + inp_w / 2, inp_y + 22, "Органи керування (HMI)", size=12.5, color=FIELD, bold=True))

    P.append(rect(inp_x + 12, inp_y + 36, 256, 72, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    P.append(text(inp_x + 140, inp_y + 56, "2x Стіки Холла (AG01 Mini)", size=10.5, bold=True))
    P.append(text(inp_x + 140, inp_y + 74, "Осі: Roll, Pitch, Throttle, Yaw", size=9.5, color=MUTED))
    P.append(text(inp_x + 140, inp_y + 92, "0.33–3.0V ratiometric, нульовий дрейф", size=9.5, color=MUTED))

    P.append(rect(inp_x + 12, inp_y + 118, 256, 56, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    P.append(text(inp_x + 140, inp_y + 138, "Антиаліасингові RC-фільтри", size=10.5, bold=True))
    P.append(text(inp_x + 140, inp_y + 156, "R = 100 Ω, C = 10 nF (fc ≈ 159 кГц)", size=9.5, color=MUTED))

    P.append(rect(inp_x + 12, inp_y + 184, 256, 52, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    P.append(text(inp_x + 140, inp_y + 204, "Тумблери та кнопка Arm", size=10.5, bold=True))
    P.append(text(inp_x + 140, inp_y + 222, "2x 3-поз. перемикачі + 2x кнопки", size=9.5, color=MUTED))

    # Центральна колонка: Мікроконтролер (MCU Core)
    mcu_x, mcu_y, mcu_w, mcu_h = 345, 55, 350, 505
    P.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#f8f9fb", stroke=INK, sw=2, rx=10))
    P.append(text(mcu_x + mcu_w / 2, mcu_y + 24, "Обчислювальне ядро (MCU)", size=13.5, bold=True))
    P.append(text(mcu_x + mcu_w / 2, mcu_y + 42, "ESP32-S3 (240 MHz) / STM32G4 (170 MHz)", size=10.5, color=MUTED, bold=True))

    mcu_blocks = [
        ("DMA Injected ADC Engine (12-bit)", "Опитування 4 осей Холла за 15 µs\nКільцевий Ping-Pong буфер, нуль CPU", 65),
        ("Цифрова фільтрація та Expo LUT", "IIR фільтр 1-го порядку + мертва зона\nНелінійна експоненційна крива відгуку", 148),
        ("Диспетчер радіокадру (1 kHz TDD)", "Пакування 11-bit каналів + CRC-16\nСинхронізація слотів TX/RX за таймером", 231),
        ("Апаратний Watchdog (IWDG)", "Таймаут 15 мс від незалежного LSI\nЗахист від зависань та дедлоків", 314),
        ("Контролер дисплея (SPI DMA)", "Часткове оновлення смугами (Strip Buffer)\nРендеринг HUD без мерехтіння", 397)
    ]

    for title, desc, off_y in mcu_blocks:
        by = mcu_y + off_y
        P.append(rect(mcu_x + 15, by, mcu_w - 30, 72, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
        P.append(text(mcu_x + mcu_w / 2, by + 22, title, size=11, bold=True))
        lines = desc.split("\n")
        P.append(text(mcu_x + mcu_w / 2, by + 40, lines[0], size=9.5, color=MUTED))
        P.append(text(mcu_x + mcu_w / 2, by + 56, lines[1], size=9.5, color=MUTED))

    # Права колонка: Радіомодуль, Дисплей, Вібромотор
    # Блок 3.1: Радіотрансивер (верхній правий)
    rf_x, rf_y, rf_w, rf_h = 740, 55, 280, 240
    P.append(rect(rf_x, rf_y, rf_w, rf_h, fill="#f5f7fc", stroke=NEG, sw=1.5, rx=8))
    P.append(text(rf_x + rf_w / 2, rf_y + 22, "Радіомодуль (SX1280 / E220)", size=12.5, color=NEG, bold=True))

    P.append(rect(rf_x + 12, rf_y + 36, 256, 58, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    P.append(text(rf_x + 140, rf_y + 54, "Semtech SX1280 (2.4 GHz)", size=10.5, bold=True))
    P.append(text(rf_x + 140, rf_y + 70, "FLRC (1.3 Mbps) / LoRa, 150–500 Hz", size=9.5, color=MUTED))
    P.append(text(rf_x + 140, rf_y + 84, "Шина SPI DMA @ 18 MHz + IRQ/BUSY", size=9.5, color=MUTED))

    P.append(rect(rf_x + 12, rf_y + 102, 256, 58, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    P.append(text(rf_x + 140, rf_y + 120, "RF Front-End / Підсилювач", size=10.5, bold=True))
    P.append(text(rf_x + 140, rf_y + 136, "PA/LNA (+20 dBm / 100 mW вихід)", size=9.5, color=MUTED))
    P.append(text(rf_x + 140, rf_y + 150, "RF-перемикач антени + смуговий фільтр", size=9.5, color=MUTED))

    P.append(rect(rf_x + 12, rf_y + 168, 256, 56, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    P.append(text(rf_x + 140, rf_y + 188, "Антена 2.4 GHz / 868 MHz", size=10.5, color=NEG, bold=True))
    P.append(text(rf_x + 140, rf_y + 206, "Узгоджена лінія 50 Ω, роз'єм IPEX/SMA", size=9.5, color=MUTED))

    # Блок 3.2: Дисплей і Тактильний зв'язок (нижній правий)
    out_x, out_y, out_w, out_h = 740, 310, 280, 250
    P.append(rect(out_x, out_y, out_w, out_h, fill="#faf5fc", stroke="#8e44ad", sw=1.5, rx=8))
    P.append(text(out_x + out_w / 2, out_y + 22, "Індикація та Haptic Feedback", size=12.5, color="#8e44ad", bold=True))

    P.append(rect(out_x + 12, out_y + 36, 256, 92, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    P.append(text(out_x + 140, out_y + 56, "OLED / IPS Графічний дисплей", size=10.5, bold=True))
    P.append(text(out_x + 140, out_y + 74, "128x64 SSD1306 / 240x240 ST7789", size=9.5, color=MUTED))
    P.append(text(out_x + 140, out_y + 92, "Шина SPI DMA + ШІМ яскравості", size=9.5, color=MUTED))
    P.append(text(out_x + 140, out_y + 110, "HUD: напруга, RSSI, LQ, режим", size=9.5, color=MUTED))

    P.append(rect(out_x + 12, out_y + 138, 256, 96, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    P.append(text(out_x + 140, out_y + 158, "Вібромотор зворотного зв'язку", size=10.5, bold=True))
    P.append(text(out_x + 140, out_y + 176, "ERM / LRA тактильний драйвер", size=9.5, color=MUTED))
    P.append(text(out_x + 140, out_y + 194, "N-MOS AO3400 + діод Шотткі BAT54", size=9.5, color=MUTED))
    P.append(text(out_x + 140, out_y + 212, "Сигнали: розряд, втрата зв'язку, Arm", size=9.5, color=MUTED))

    # Стрілки зв'язків між блоками
    # Органи введення -> MCU
    P.append(arrow(inp_x + inp_w, inp_y + 72, mcu_x, mcu_y + 95, color=FIELD, sw=2))
    P.append(text(318, 360, "4x АЦП\nDMA", size=9.5, color=FIELD, bold=True))

    P.append(arrow(inp_x + inp_w, inp_y + 204, mcu_x, mcu_y + 345, color=INK, sw=1.5))
    P.append(text(318, 490, "GPIO\nIRQ", size=9.5, color=INK, bold=True))

    # Живлення -> MCU
    P.append(arrow(pwr_x + pwr_w, pwr_y + 116, mcu_x, mcu_y + 60, color="#d35400", sw=2))
    P.append(text(318, 150, "3.3V\nMain", size=9.5, color="#d35400", bold=True))

    # MCU -> Radio
    P.append(arrow(mcu_x + mcu_w, mcu_y + 265, rf_x, rf_y + 65, color=NEG, sw=2))
    P.append(text(718, 195, "SPI DMA\n18 MHz", size=9.5, color=NEG, bold=True))

    # MCU -> Display & Haptic
    P.append(arrow(mcu_x + mcu_w, mcu_y + 425, out_x, out_y + 80, color="#8e44ad", sw=1.8))
    P.append(text(718, 420, "SPI/PWM\nDMA", size=9.5, color="#8e44ad", bold=True))

    P.append(arrow(mcu_x + mcu_w, mcu_y + 345, out_x, out_y + 185, color=INK, sw=1.5))
    P.append(text(718, 500, "PWM\nGate", size=9.5, color=INK, bold=True))

    render(os.path.join(IMG_DIR, "console-hardware-architecture.svg"), W, H, *P)


# ── Фігура 2: Часова діаграма детермінованого циклу 1 кГц ───────────────────
def fig_timing_dma_adc_rf_cycle():
    W, H = 1000, 430
    P = []
    P.append(text(W / 2, 28, "Часова діаграма детермінованого циклу керування 1 кГц (1.0 мс)",
                  size=16, bold=True))

    # Вісь часу
    ox = 110
    oy = 345
    gw = 840
    P.append(line(ox, oy, ox + gw, oy, color=INK, sw=2))
    P.append(arrow(ox + gw - 5, oy, ox + gw + 20, oy, color=INK, sw=2))
    P.append(text(ox + gw + 25, oy + 4, "t (мс)", size=12, bold=True, anchor="start"))

    # Позначки на осі часу: 0.0, 0.1, 0.2, ..., 1.0 мс
    ticks = [
        (0.0, "0.00"),
        (0.1, "0.10"),
        (0.2, "0.20"),
        (0.4, "0.40"),
        (0.6, "0.60"),
        (0.8, "0.80"),
        (1.0, "1.00")
    ]
    for frac, lbl in ticks:
        tx = ox + frac * gw
        P.append(line(tx, oy - 6, tx, oy + 6, color=INK, sw=1.5))
        P.append(text(tx, oy + 22, lbl, size=10.5, bold=True))
        P.append(line(tx, 60, tx, oy - 6, color="#e5e7eb", sw=1, dash="3,3"))

    # Доріжки процесів
    # Доріжка 1: Апаратний таймер і АЦП DMA
    y1 = 75
    P.append(text(ox - 12, y1 + 20, "Таймер / АЦП", size=11, bold=True, anchor="end"))
    # Імпульс таймера на t=0
    P.append(rect(ox, y1, 20, 40, fill="#e74c3c", stroke="#c0392b", sw=1.5, rx=3))
    P.append(text(ox + 10, y1 - 8, "Тік 1 кГц", size=9.5, color="#c0392b", bold=True))
    # АЦП DMA перетворення 4 каналів (0.00 - 0.02 мс)
    P.append(rect(ox + 20, y1, 55, 40, fill="#2ecc71", stroke="#27ae60", sw=1.5, rx=3))
    P.append(text(ox + 47, y1 + 18, "DMA ADC", size=9.5, color="#ffffff", bold=True))
    P.append(text(ox + 47, y1 + 32, "4 осі (15 µs)", size=9, color="#ffffff", bold=True))

    # Доріжка 2: Обробка ядра (CPU Pipeline)
    y2 = 142
    P.append(text(ox - 12, y2 + 20, "Ядро MCU (CPU)", size=11, bold=True, anchor="end"))
    # Фільтрація + Expo (0.02 - 0.05 мс)
    P.append(rect(ox + 75, y2, 60, 40, fill="#3498db", stroke="#2980b9", sw=1.5, rx=3))
    P.append(text(ox + 105, y2 + 18, "IIR + Expo", size=9.5, color="#ffffff", bold=True))
    P.append(text(ox + 105, y2 + 32, "(25 µs)", size=9, color="#ffffff", bold=True))

    # Пакування кадру + CRC16 (0.05 - 0.08 мс)
    P.append(rect(ox + 135, y2, 65, 40, fill="#9b59b6", stroke="#8e44ad", sw=1.5, rx=3))
    P.append(text(ox + 167, y2 + 18, "Frame+CRC", size=9.5, color="#ffffff", bold=True))
    P.append(text(ox + 167, y2 + 32, "(20 µs)", size=9, color="#ffffff", bold=True))

    # Запуск SPI DMA (0.08 - 0.10 мс)
    P.append(rect(ox + 200, y2, 50, 40, fill="#e67e22", stroke="#d35400", sw=1.5, rx=3))
    P.append(text(ox + 225, y2 + 18, "SPI TX", size=9.5, color="#ffffff", bold=True))
    P.append(text(ox + 225, y2 + 32, "(15 µs)", size=9, color="#ffffff", bold=True))

    # CPU вільне для UI/Display
    P.append(rect(ox + 255, y2, 580, 40, fill="#f8f9fa", stroke="#bdc3c7", sw=1.2, rx=4))
    P.append(text(ox + 545, y2 + 24, "Ядро вільне: фоновий рендеринг графіки HUD / SPI DMA дисплея (750 µs)", size=10.5, color=MUTED, bold=True))

    # Доріжка 3: Радіоефір SX1280 (RF Over-The-Air)
    y3 = 210
    P.append(text(ox - 12, y3 + 20, "Радіо SX1280", size=11, bold=True, anchor="end"))
    # TX Uplink (0.10 - 0.55 мс = 378 px)
    tx_w = 0.45 * gw
    P.append(rect(ox + 0.10 * gw, y3, tx_w, 40, fill="#ffebee", stroke=POS, sw=1.5, rx=4))
    P.append(text(ox + 0.10 * gw + tx_w / 2, y3 + 24, "ПЕРЕДАЧА КАДРУ КЕРУВАННЯ (TX Uplink 14 B, 450 µs, +12 dBm)", size=10.5, color=POS, bold=True))

    # TDD перемикання (0.55 - 0.60 мс)
    tdd_w = 0.05 * gw
    P.append(rect(ox + 0.55 * gw, y3, tdd_w, 40, fill="#fff3e0", stroke="#e67e22", sw=1.2, rx=3))
    P.append(text(ox + 0.55 * gw + tdd_w / 2, y3 + 24, "TDD (50 µs)", size=9.5, color="#d35400", bold=True))

    # RX Downlink Telemetry (0.60 - 0.80 мс)
    rx_w = 0.20 * gw
    P.append(rect(ox + 0.60 * gw, y3, rx_w, 40, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=4))
    P.append(text(ox + 0.60 * gw + rx_w / 2, y3 + 24, "ПРИЙОМ ТЕЛЕМЕТРІЇ (RX 8 B, 200 µs)", size=10, color=FIELD, bold=True))

    # Warm Sleep (0.80 - 1.00 мс)
    sleep_w = 0.20 * gw
    P.append(rect(ox + 0.80 * gw, y3, sleep_w, 40, fill="#f3e5f5", stroke="#8e44ad", sw=1.5, rx=4))
    P.append(text(ox + 0.80 * gw + sleep_w / 2, y3 + 24, "Warm-Sleep (1.2 µA, 200 µs)", size=9.5, color="#8e44ad", bold=True))

    # Доріжка 4: Стан споживання струму
    y4 = 278
    P.append(text(ox - 12, y4 + 18, "Струм I_bat", size=11, bold=True, anchor="end"))
    P.append(rect(ox + 0.10 * gw, y4, tx_w, 32, fill="#fadbd8", stroke=POS, sw=1, rx=3))
    P.append(text(ox + 0.10 * gw + tx_w / 2, y4 + 20, "TX Пік: ~55–95 мА", size=10, color=POS, bold=True))

    P.append(rect(ox + 0.60 * gw, y4, rx_w, 32, fill="#d4efdf", stroke=FIELD, sw=1, rx=3))
    P.append(text(ox + 0.60 * gw + rx_w / 2, y4 + 20, "RX: ~10 мА", size=10, color=FIELD, bold=True))

    P.append(rect(ox + 0.80 * gw, y4, sleep_w, 32, fill="#e8daef", stroke="#8e44ad", sw=1, rx=3))
    P.append(text(ox + 0.80 * gw + sleep_w / 2, y4 + 20, "Базовий струм: ~18 мА (MCU+OLED)", size=9.5, color="#8e44ad", bold=True))

    # Підсумок
    P.append(rect(ox, oy + 42, gw, 30, fill="#edf2f7", stroke="#4a5568", sw=1, rx=4))
    P.append(text(ox + gw / 2, oy + 61, "Затримка «рух пальця → радіохвиля»: < 0.10 мс (100 µs)  •  Середнє споживання пульта: ~28 мА",
                  size=11.5, color="#2d3748", bold=True))

    render(os.path.join(IMG_DIR, "timing-dma-adc-rf-cycle.svg"), W, H, *P)


# ── Фігура 3: Домени живлення та енергозбереження ────────────────────────────
def fig_power_management_domains():
    W, H = 1000, 480
    P = []
    P.append(text(W / 2, 28, "Архітектура доменів живлення та стани енергоспоживання",
                  size=16, bold=True))

    # Ліва частина: Структура доменів живлення
    P.append(rect(20, 55, 460, 405, fill="#fdfefe", stroke=INK, sw=1.5, rx=8))
    P.append(text(250, 80, "Апаратна ізоляція доменів живлення", size=13.5, bold=True))

    # Батарея
    P.append(rect(38, 100, 424, 52, fill="#fffbf5", stroke="#e67e22", sw=1.5, rx=6))
    P.append(text(250, 122, "Li-Ion Акумулятор (3.0 – 4.2 V)", size=11.5, color="#d35400", bold=True))
    P.append(text(250, 140, "1S 18650 (3500 mAh) / Контролер TP4056 USB-C", size=10, color=MUTED))

    # Домен 1: Завжди увімкнений (Always-On Domain)
    P.append(rect(38, 164, 424, 110, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=6))
    P.append(text(250, 186, "ДОМЕН 1: ЗАВЖДИ УВІМКНЕНИЙ (Always-On 3.3V)", size=11.5, color=FIELD, bold=True))
    P.append(text(250, 206, "• Low-Iq LDO регулятор (Iq = 55 µA)", size=10, color=INK))
    P.append(text(250, 224, "• MCU RTC та контролер пробудження (Wakeup GPIO)", size=10, color=INK))
    P.append(text(250, 242, "• Кнопка ввімкнення / Power Latch схема", size=10, color=INK))
    P.append(text(250, 260, "Струм у режимі очікування (Deep Sleep): 12–15 µA", size=10, color=FIELD, bold=True))

    # Домен 2: Комутований домен периферії (Switched Peripheral Domain)
    P.append(rect(38, 286, 424, 155, fill="#fdf7f6", stroke=POS, sw=1.5, rx=6))
    P.append(text(250, 310, "ДОМЕН 2: КОМУТОВАНИЙ (Switched 3.3V Domain)", size=11.5, color=POS, bold=True))
    P.append(text(250, 330, "Ключ розриву живлення: P-MOSFET (AO3401 / TPS22918)", size=10, color=POS, bold=True))
    P.append(text(250, 350, "• 2x Стіки Холла (AG01 Mini) — економія 15 мА", size=10, color=INK))
    P.append(text(250, 368, "• Графічний дисплей OLED/IPS — економія 10–35 мА", size=10, color=INK))
    P.append(text(250, 386, "• Радіотрансивер SX1280 (RF VDD) — економія 10–95 мА", size=10, color=INK))
    P.append(text(250, 406, "• Резистивний дільник напруги Vbat (N-MOS затвор)", size=10, color=INK))

    # Права частина: Стани енергоспоживання та автономність
    P.append(rect(505, 55, 475, 405, fill="#f8f9fb", stroke=INK, sw=1.5, rx=8))
    P.append(text(742, 80, "Режими роботи та профіль споживання", size=13.5, bold=True))

    states = [
        ("Глибокий сон (Deep Sleep)", "12–15 µA", "Вимкнено все, крім RTC та кнопки ввімкнення.\nСаморозряд акумулятора швидший за споживання.\nАвтономність: > 10 років без підзарядки.", "#27ae60", "#e8f8f0"),
        ("Очікування / Пауза (Standby)", "6–8 мА", "MCU на 80 MHz, дисплей приглушено до 10%,\nрадіо в Warm-Sleep (періодичний пінг 10 Гц),\nстіки на низькій частоті опитування (50 Гц).", "#2980b9", "#ebf5fb"),
        ("Активне керування (1 kHz Active)", "26–32 мА", "Повний 1 кГц TDD цикл, дисплей 100% яскравості,\nSX1280 чергує TX (+12 dBm), RX та Warm-Sleep.\nАвтономність від 1S 3500 mAh: ~110–135 годин.", "#e67e22", "#fef9e7"),
        ("Піковий сплеск (Burst TX + Haptic)", "110–140 мА", "Максимальна потужність TX (+20 dBm з PA)\n+ вібромоторчик тактильної тривоги (ERM).\nТривалість: короткі імпульси по 50–200 мс.", "#c0392b", "#fdebd0")
    ]

    sy = 100
    for title, current, desc, stroke_c, fill_c in states:
        P.append(rect(520, sy, 445, 78, fill=fill_c, stroke=stroke_c, sw=1.2, rx=6))
        P.append(text(535, sy + 20, title, size=11.5, color=stroke_c, bold=True, anchor="start"))
        P.append(text(950, sy + 20, current, size=11.5, color=stroke_c, bold=True, anchor="end"))
        lines = desc.split("\n")
        for idx, ln in enumerate(lines):
            P.append(text(535, sy + 38 + idx * 14, ln, size=9.5, color=INK, anchor="start"))
        sy += 86

    render(os.path.join(IMG_DIR, "power-management-domains.svg"), W, H, *P)


if __name__ == "__main__":
    fig_console_hardware_architecture()
    fig_timing_dma_adc_rf_cycle()
    fig_power_management_domains()
    print("Всі 3 фігури успішно згенеровано у теці img/.")

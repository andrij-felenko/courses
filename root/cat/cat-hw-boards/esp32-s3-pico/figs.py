# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: анатомія плати — чистий потік ліворуч→праворуч ─────────────────
def anatomy():
    W, H = 880, 430
    f = []

    # Колонка 1: USB-C
    usb, uw, uh = textbox(95, 215, "USB-C\nживлення\n+ дані", size=13, min_w=130,
                          fill="#eaf0fd", stroke=NEG)
    f.append(usb)

    # Колонка 2: два мости (дані) + DC-DC (живлення) — рознесені по вертикалі
    hub = textbox(305, 120, "CH334\nUSB-хаб", size=12, min_w=140, fill=FILL)
    f.append(hub[0])
    uart = textbox(305, 215, "CH343\nUSB ↔ UART", size=12, min_w=140, fill=FILL)
    f.append(uart[0])
    dc = textbox(305, 330, "MP28164\nDC-DC → 3.3 В", size=12, min_w=150,
                 fill="#eafaf1", stroke=FIELD)
    f.append(dc[0])

    # Колонка 3: ESP32-S3R2
    esp, ew, eh = textbox(575, 190, "ESP32-S3R2\n2 ядра LX7 · 240 МГц\n512 КБ SRAM · 2 МБ PSRAM\nWi-Fi + Bluetooth LE",
                          size=13, min_w=260, fill="#fdf6e3", stroke=POS, sw=2)
    f.append(esp)
    fl = textbox(575, 330, "Flash 16 МБ (W25Q128)", size=12, min_w=210, fill=FILL)
    f.append(fl[0])

    # Колонка 4: антена та світлодіод
    ant = textbox(805, 120, "антена\n2.4 ГГц", size=12, min_w=110, fill="#eafaf1", stroke=FIELD)
    f.append(ant[0])
    led = textbox(805, 265, "RGB-LED\nWS2812\nGPIO21", size=11, min_w=110, fill="#fdecea", stroke=POS)
    f.append(led[0])

    # Стрілки даних (горизонтальні, не перетинають написи)
    f.append(arrow(160, 190, 232, 130, color=NEG))     # USB → hub
    f.append(arrow(160, 215, 232, 210, color=NEG))     # USB → CH343
    f.append(arrow(378, 120, 442, 165, color=INK))     # hub → USB-OTG
    f.append(arrow(378, 215, 442, 195, color=INK))     # CH343 → UART
    f.append(text(415, 138, "USB-OTG", size=10, color=MUTED))
    f.append(text(415, 235, "UART", size=10, color=MUTED))

    # Стрілки живлення (зелені, окремим низом)
    f.append(arrow(160, 240, 232, 320, color=FIELD))   # USB → DC-DC
    f.append(arrow(378, 330, 468, 330, color=FIELD))   # DC-DC → flash rail (power)
    f.append(text(423, 320, "3.3 В", size=10, color=FIELD))
    f.append(arrow(575, 306, 575, 232, color=FIELD))   # power up to ESP
    f.append(arrow(672, 330, 672, 222, color=INK))     # flash ↔ ESP (QSPI)
    f.append(text(700, 285, "QSPI", size=10, color=MUTED, anchor="start"))

    # ESP → антена / LED
    f.append(arrow(706, 165, 748, 130, color=FIELD))
    f.append(arrow(706, 205, 748, 255, color=POS))

    render(os.path.join(OUT, 'anatomy.svg'), W, H, *f)


# ── Фігура 2: фізична розводка — Pico-сумісний ряд контактів ─────────────────
# Порядок за реальними виведеними нетами плати (IO0..IO21, IO33..IO46 + живлення).
def pinout():
    W, H = 760, 700
    f = []
    bw, bh = 300, 600
    bx0, by0 = (W - bw) / 2, 46
    f.append(rect(bx0, by0, bw, bh, fill="#eef2f7", stroke=INK, sw=2, rx=14))
    # USB-C зверху
    f.append(rect(W/2 - 34, by0 - 16, 68, 20, fill="#d5dbe3", stroke=INK, sw=1.5, rx=5))
    f.append(text(W/2, by0 - 22, "USB-C", size=11, color=MUTED))
    f.append(text(W/2, by0 + 34, "ESP32-S3-Pico", size=14, bold=True))
    f.append(text(W/2, by0 + 54, "51 × 21 мм · формат RPi Pico", size=10, color=MUTED))
    # мітки на платі
    f.append(circle(W/2 - 46, by0 + 86, 7, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(W/2 - 46, by0 + 106, "RGB", size=9, color=POS))
    f.append(rect(W/2 + 6, by0 + 78, 22, 14, fill="#e5e7eb", stroke=INK, sw=1, rx=3))
    f.append(text(W/2 + 17, by0 + 104, "BOOT", size=9, color=MUTED))
    f.append(rect(W/2 + 44, by0 + 78, 22, 14, fill="#e5e7eb", stroke=INK, sw=1, rx=3))
    f.append(text(W/2 + 55, by0 + 104, "RST", size=9, color=MUTED))

    # Ліва сторона зверху-вниз, потім права знизу-вгору — як у ряду контактів.
    left = [
        ("GPIO0 · BOOT", POS), ("GPIO1", INK), ("GPIO2", INK), ("GPIO3", INK),
        ("GPIO4", INK), ("GPIO5", INK), ("GPIO6", INK), ("GPIO7", INK),
        ("GND", NEG), ("GPIO8", INK), ("GPIO9", INK), ("GPIO10", INK),
        ("GPIO11", INK), ("GPIO12", INK), ("GPIO13", INK), ("GPIO14", INK),
        ("GND", NEG), ("GPIO18", INK), ("GPIO19 · USB D−", INK), ("GPIO20 · USB D+", INK),
    ]
    right = [
        ("VBUS · 5 В з USB", FIELD), ("VSYS · вхід 3.7–6 В", FIELD), ("GND", NEG),
        ("3V3_EN", FIELD), ("3V3 · вихід", FIELD), ("GPIO46", INK), ("GPIO45", INK),
        ("GPIO44 · RX", INK), ("GPIO43 · TX", INK), ("GND", NEG), ("GPIO42", INK),
        ("GPIO41", INK), ("GPIO40", INK), ("GPIO39", INK), ("GPIO38", INK),
        ("GPIO37", MUTED), ("GPIO36", MUTED), ("GPIO35", MUTED), ("GPIO34", MUTED),
        ("GPIO21 · RGB", POS),
    ]

    n = len(left)
    top = by0 + 132
    step = (bh - 156) / (n - 1)
    dot = 6
    for i in range(n):
        y = top + i * step
        f.append(circle(bx0 + 8, y, dot, fill="#c9a94b", stroke=INK, sw=1))
        lbl, col = left[i]
        f.append(text(bx0 - 12, y + 4, lbl, size=11, color=col, anchor="end"))
        f.append(circle(bx0 + bw - 8, y, dot, fill="#c9a94b", stroke=INK, sw=1))
        rlbl, rcol = right[i]
        f.append(text(bx0 + bw + 12, y + 4, rlbl, size=11, color=rcol, anchor="start"))

    # легенда знизу — рознесена, щоб не накладалась
    ly = by0 + bh + 34
    f.append(circle(120, ly, 6, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(134, ly + 4, "GND", size=11, color=NEG, anchor="start"))
    f.append(circle(220, ly, 6, fill="#eafaf1", stroke=FIELD, sw=1.5))
    f.append(text(234, ly + 4, "живлення", size=11, color=FIELD, anchor="start"))
    f.append(circle(370, ly, 6, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(384, ly + 4, "спец-вивід", size=11, color=POS, anchor="start"))
    f.append(circle(520, ly, 6, fill=FILL, stroke=MUTED, sw=1.5))
    f.append(text(534, ly + 4, "обережно (див. текст)", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'pinout.svg'), W, H, *f)


# ── Фігура 3: GPIO matrix — сигнал периферії йде на ДОВІЛЬНУ ногу ────────────
# Показує центральну ідею: I2C/SPI/UART комутуються на будь-який GPIO,
# а USB прибитий до IOMUX (GPIO19/20) і через матрицю НЕ ходить.
def gpio_matrix():
    W, H = 900, 470
    f = []

    # Ліворуч — блоки периферії
    per = [
        ("I2C0", 90, "#eaf0fd", NEG),
        ("SPI2", 175, "#eaf0fd", NEG),
        ("UART1", 260, "#eaf0fd", NEG),
    ]
    for name, y, fill, st in per:
        b = textbox(90, y, name, size=13, min_w=120, fill=fill, stroke=st, bold=True)
        f.append(b[0])

    # USB окремо — не заходить у матрицю
    ub = textbox(90, 385, "USB-OTG\n(рідний)", size=12, min_w=120, fill="#fdecea", stroke=POS, bold=True)
    f.append(ub[0])

    # Центр — комутатор (GPIO matrix)
    mx = rect(330, 60, 150, 260, fill="#fdf6e3", stroke=POS, sw=2, rx=12)
    f.append(mx)
    f.append(text(405, 88, "GPIO matrix", size=14, bold=True))
    f.append(text(405, 108, "комутатор", size=11, color=MUTED))
    # «перехрестя» всередині — натяк на будь-який→будь-який
    for gy in (150, 200, 250):
        f.append(line(345, gy, 465, gy, color=MUTED, sw=1, dash="4,4"))
    for gx in (360, 405, 450):
        f.append(line(gx, 130, gx, 300, color=MUTED, sw=1, dash="4,4"))

    # Праворуч — фізичні ноги
    pins = [
        ("GPIO8", 95), ("GPIO9", 140), ("GPIO12", 185),
        ("GPIO13", 230), ("GPIO43", 275), ("GPIO44", 320),
    ]
    for name, y in pins:
        b = textbox(760, y, name, size=12, min_w=110, fill=FILL)
        f.append(b[0])

    # Ноги IOMUX для USB (фіксовані)
    for name, y in (("GPIO19 · D−", 360), ("GPIO20 · D+", 405)):
        b = textbox(760, y, name, size=12, min_w=140, fill="#fdecea", stroke=POS)
        f.append(b[0])

    # Стрілки: периферія → матриця
    f.append(arrow(150, 90, 328, 120, color=NEG))
    f.append(arrow(150, 175, 328, 190, color=NEG))
    f.append(arrow(150, 260, 328, 250, color=NEG))

    # Матриця → будь-яка нога (кілька прикладів, розведені)
    f.append(arrow(482, 150, 702, 95, color=FIELD))    # → GPIO8
    f.append(arrow(482, 160, 702, 140, color=FIELD))   # → GPIO9
    f.append(arrow(482, 200, 702, 185, color=FIELD))   # → GPIO12
    f.append(arrow(482, 210, 702, 230, color=FIELD))   # → GPIO13
    f.append(arrow(482, 250, 702, 275, color=FIELD))   # → GPIO43
    f.append(arrow(482, 260, 702, 320, color=FIELD))   # → GPIO44

    # USB — прямий, повз матрицю (пунктир до фіксованих ніг)
    f.append(line(150, 375, 702, 360, color=POS, sw=2))
    f.append(line(150, 395, 702, 405, color=POS, sw=2))
    f.append(text(430, 350, "в обхід матриці — жорстко на IOMUX", size=11, color=POS))

    # Підписи країв
    f.append(text(90, 44, "периферійні блоки", size=11, color=MUTED))
    f.append(text(760, 44, "фізичні виводи", size=11, color=MUTED))

    render(os.path.join(OUT, 'gpio-matrix.svg'), W, H, *f)


# ── Фігура 4: карта пам'яті — куди лягає malloc vs ps_malloc ─────────────────
def memory_map():
    W, H = 820, 420
    f = []

    # SRAM — швидка, мала, на кристалі
    sx, sy, sw_, sh = 70, 80, 300, 250
    f.append(rect(sx, sy, sw_, sh, fill="#eafaf1", stroke=FIELD, sw=2, rx=10))
    f.append(text(sx + sw_/2, sy - 14, "SRAM на кристалі", size=13, bold=True))
    f.append(text(sx + sw_/2, sy + 24, "512 КБ · швидка", size=12, color=FIELD))
    f.append(text(sx + sw_/2, sy + 44, "доступ за такти CPU", size=11, color=MUTED))
    # що тут живе
    for i, s in enumerate(["стек, .bss, .data", "малі об'єкти", "malloc() за замовч.",
                           "DMA-буфери"]):
        f.append(text(sx + 20, sy + 84 + i*34, "• " + s, size=12, anchor="start"))

    # PSRAM — велика, повільніша, зовні (в корпусі), через кеш/QSPI
    px, py, pw, ph = 450, 80, 300, 250
    f.append(rect(px, py, pw, ph, fill="#fdf6e3", stroke=POS, sw=2, rx=10))
    f.append(text(px + pw/2, py - 14, "PSRAM (у корпусі R2)", size=13, bold=True))
    f.append(text(px + pw/2, py + 24, "2 МБ · quad-SPI", size=12, color=POS))
    f.append(text(px + pw/2, py + 44, "через кеш, повільніша", size=11, color=MUTED))
    for i, s in enumerate(["ps_malloc() сюди", "кадри з камери", "буфер дисплея",
                           "великі масиви / JSON"]):
        f.append(text(px + 20, py + 84 + i*34, "• " + s, size=12, anchor="start"))

    # Міст — кеш/QSPI між ними
    f.append(arrow(370, 205, 448, 205, color=INK))
    f.append(arrow(448, 235, 370, 235, color=INK))
    f.append(text(410, 190, "кеш", size=10, color=MUTED))
    f.append(text(410, 262, "QSPI", size=10, color=MUTED))

    # Приклад унизу: скільки важить кадр
    ey = 372
    f.append(rect(70, ey - 24, 680, 40, fill=FILL, stroke=MUTED, sw=1, rx=8))
    f.append(text(410, ey + 2, "кадр RGB565 320×240 = 320 · 240 · 2 = 153 600 Б ≈ 150 КБ — влазить у SRAM; 640×480 ≈ 600 КБ — лише в PSRAM",
                  size=11, color=INK))

    render(os.path.join(OUT, 'memory-map.svg'), W, H, *f)


if __name__ == '__main__':
    anatomy()
    pinout()
    gpio_matrix()
    memory_map()
    print("ok")

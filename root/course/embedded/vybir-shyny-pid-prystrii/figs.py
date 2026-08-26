# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. bus-space-speed-pins.svg: Карта шин за швидкістю та кількістю пінів ──────
def fig_bus_space():
    W, H = 940, 520
    p = []

    x0, y0 = 100, 420
    xw, yh = 780, 340

    import math
    min_speed, max_speed = 10, 1000000  # в кбіт/с (10 кбіт/с до 1 Гбіт/с)
    lo_x, hi_x = math.log10(min_speed), math.log10(max_speed)

    def sx(v_kbps):
        return x0 + (math.log10(v_kbps) - lo_x) / (hi_x - lo_x) * xw

    def sy(pin_count):
        norm = (pin_count - 1) / 7.0
        return y0 - norm * yh

    # Засічки на осі X (швидкість)
    speed_ticks = [
        (10, "10 кбіт/с"),
        (100, "100 кбіт/с"),
        (1000, "1 Мбіт/с"),
        (10000, "10 Мбіт/с"),
        (100000, "100 Мбіт/с"),
        (800000, "100 МБайт/с"),
    ]
    for spd, lab in speed_ticks:
        xx = sx(spd)
        p.append(line(xx, y0 - 4, xx, y0 + 6, color=LINE, sw=1.2))
        p.append(text(xx, y0 + 20, lab, size=10, color=MUTED, anchor="middle"))

    # Засічки на осі Y (піни)
    y_lines = [
        (1, "1 сигнальна"),
        (2, "2 лінії"),
        (4, "3–4 лінії"),
        (6, "5–6 ліній"),
        (8, "8–11 ліній"),
    ]
    for pc, lab in y_lines:
        yy = sy(pc)
        p.append(line(x0 - 6, yy, x0 + 4, yy, color=LINE, sw=1.2))
        p.append(text(x0 - 10, yy + 4, lab, size=10, color=MUTED, anchor="end"))

    # Осі
    p.append(line(x0, y0, x0 + xw, y0, color=INK, sw=1.8))
    p.append(line(x0, y0, x0, y0 - yh, color=INK, sw=1.8))
    p.append(text(x0 + xw, y0 + 36, "Пропускна здатність (лог) →", size=11, color=INK, anchor="end", bold=True))
    p.append(text(x0 - 8, y0 - yh - 12, "Витрата пінів МК ↑", size=11, color=INK, anchor="start", bold=True))

    # Блоки шин (всі строго всередині координатного поля)
    buses = [
        (185, 370, "1-Wire", "16.3–142 кбіт/с\n(1 сигнальний пін, ROM ID)", "#8e44ad"),
        (300, 290, "I2C", "100–400 кбіт/с, 1 Мбіт/с\n(2 піни, відкритий стік)", "#2980b9"),
        (430, 370, "UART", "115.2 кбіт/с – 3 Мбод\n(точка-точка, 2 піни)", "#27ae60"),
        (510, 290, "CAN / CAN FD", "1–5 Мбіт/с (диференціал)\n(авто/дрони, надійність)", "#d35400"),
        (610, 210, "I2S", "1.5–12+ Мбіт/с\n(потоковий звук PCM, DMA)", "#16a085"),
        (700, 130, "SPI", "10–50+ Мбіт/с (Full-duplex)\n(дисплеї, швидкі IMU, CS[N])", "#c0392b"),
        (800, 60, "QSPI / OSPI", "50–200+ МБайт/с (XIP Flash)\n(4–8 ліній даних, DDR)", "#4b5563"),
    ]

    for cx, cy, name, sub, col in buses:
        txt = name + "\n" + sub
        box_svg, bw, bh = textbox(cx, cy, txt, size=9.5, pad=6, fill="#ffffff", stroke=col, sw=1.8, color=INK, bold=True)
        p.append(box_svg)

    render(os.path.join(OUT, "bus-space-speed-pins.svg"), W, H, *p)


# ── 2. topology-comparison.svg: Топологія підключення 4 ключових родин ─────────
def fig_topology():
    W, H = 940, 460
    p = []

    panels = [
        (25, 20, 215, 415, "I2C: Спільна шина", [
            ("МК", "SDA, SCL", 132, 65),
            ("R_pullup", "4.7 кОм до VDD", 132, 145),
            ("Чип 1 (IMU)", "Адреса 0x68", 132, 225),
            ("Чип 2 (Барометр)", "Адреса 0x76", 132, 305),
            ("Чип 3 (EEPROM)", "Адреса 0x50", 132, 385),
        ]),
        (255, 20, 215, 415, "SPI: Зірка вибірок CS", [
            ("МК", "SCK / MOSI / MISO\n+ CS0, CS1, CS2", 362, 65),
            ("Чип 1 (Дисплей TFT)", "Вибірка CS0", 362, 185),
            ("Чип 2 (Швидкий IMU)", "Вибірка CS1", 362, 275),
            ("Чип 3 (Flash-пам'ять)", "Вибірка CS2", 362, 365),
        ]),
        (485, 20, 215, 415, "UART: Точка-точка", [
            ("МК", "UART1: TX1 / RX1\nUART2: TX2 / RX2", 592, 65),
            ("Модуль 1 (GPS)", "Порт UART1", 592, 205),
            ("Модуль 2 (BLE)", "Порт UART2", 592, 325),
        ]),
        (715, 20, 205, 415, "1-Wire: Дерево адрес", [
            ("МК", "1 GPIO (DQ)", 817, 65),
            ("R_pull", "4.7 кОм", 817, 145),
            ("Термометр 1", "64-bit ROM #1", 817, 225),
            ("Термометр 2", "64-bit ROM #2", 817, 305),
            ("Термометр 3", "64-bit ROM #3", 817, 385),
        ]),
    ]

    for px, py, pw, ph, title, items in panels:
        p.append(rect(px, py, pw, ph, fill="#fafbfc", stroke="#d1d5db", sw=1.2, rx=8))
        p.append(text(px + pw / 2, py + 20, title, size=11, color=INK, bold=True))

        for idx, (head, sub, cx, cy) in enumerate(items):
            box_fill = "#eef2ff" if idx == 0 else "#ffffff"
            box_stroke = "#4f46e5" if idx == 0 else (MUTED if "pull" in head.lower() else "#2563eb")
            txt = head + "\n" + sub
            bsvg, bw, bh = textbox(cx, cy, txt, size=9, pad=5, fill=box_fill, stroke=box_stroke, sw=1.3, color=INK, bold=(idx == 0))
            p.append(bsvg)

        if "I2C" in title:
            p.append(line(132, 95, 132, 125, color="#2563eb", sw=1.8))
            p.append(line(132, 165, 132, 205, color="#2563eb", sw=1.8))
            p.append(line(132, 245, 132, 285, color="#2563eb", sw=1.8))
            p.append(line(132, 325, 132, 365, color="#2563eb", sw=1.8))
        elif "SPI" in title:
            p.append(line(362, 95, 362, 165, color="#c0392b", sw=1.8))
            p.append(line(362, 205, 362, 255, color="#c0392b", sw=1.8))
            p.append(line(362, 295, 362, 345, color="#c0392b", sw=1.8))
        elif "UART" in title:
            p.append(line(592, 95, 592, 185, color="#27ae60", sw=1.8))
            p.append(line(592, 225, 592, 305, color="#27ae60", sw=1.8))
        elif "1-Wire" in title:
            p.append(line(817, 95, 817, 125, color="#8e44ad", sw=1.8))
            p.append(line(817, 165, 817, 205, color="#8e44ad", sw=1.8))
            p.append(line(817, 245, 817, 285, color="#8e44ad", sw=1.8))
            p.append(line(817, 325, 817, 365, color="#8e44ad", sw=1.8))

    render(os.path.join(OUT, "topology-comparison.svg"), W, H, *p)


# ── 3. distance-vs-bandwidth.svg: Дистанція проти швидкості та фізика середовища ─
def fig_distance_bandwidth():
    W, H = 940, 480
    p = []

    x0, y0 = 90, 400
    xw, yh = 790, 320

    import math
    lo_d, hi_d = math.log10(0.1), math.log10(1200)
    def sdx(d_m):
        return x0 + (math.log10(d_m) - lo_d) / (hi_d - lo_d) * xw

    lo_s, hi_s = math.log10(10), math.log10(100000)
    def sdy(s_kbps):
        return y0 - (math.log10(s_kbps) - lo_s) / (hi_s - lo_s) * yh

    # Засічки дистанцій
    dist_ticks = [
        (0.1, "10 см (плата)"),
        (1.0, "1 м (шлейф)"),
        (10.0, "10 м (кабель)"),
        (100.0, "100 м (цех)"),
        (1000.0, "1 км (поле)"),
    ]
    for d, lab in dist_ticks:
        xx = sdx(d)
        p.append(line(xx, y0 - 4, xx, y0 + 6, color=LINE, sw=1.2))
        p.append(text(xx, y0 + 18, lab, size=10, color=MUTED, anchor="middle"))

    # Засічки швидкостей
    speed_ticks = [
        (10, "10 кбіт/с"),
        (100, "100 кбіт/с"),
        (1000, "1 Мбіт/с"),
        (10000, "10 Мбіт/с"),
        (100000, "100 Мбіт/с"),
    ]
    for spd, lab in speed_ticks:
        yy = sdy(spd)
        p.append(line(x0 - 6, yy, x0 + 4, yy, color=LINE, sw=1.2))
        p.append(text(x0 - 8, yy + 4, lab, size=10, color=MUTED, anchor="end"))

    # Осі
    p.append(line(x0, y0, x0 + xw, y0, color=INK, sw=1.8))
    p.append(line(x0, y0, x0, y0 - yh, color=INK, sw=1.8))
    p.append(text(x0 + xw, y0 + 36, "Фізична дистанція лінії (лог) →", size=11, color=INK, anchor="end", bold=True))
    p.append(text(x0 - 8, y0 - yh - 12, "Максимальна швидкість ↑", size=11, color=INK, anchor="start", bold=True))

    # Зони / криві інтерфейсів
    # 1. SPI / QSPI
    spi_pts = [(0.1, 80000), (0.2, 50000), (0.4, 10000), (0.8, 1000), (1.5, 100)]
    pts_str = " ".join("%.1f,%.1f" % (sdx(d), sdy(s)) for d, s in spi_pts)
    p.append('<polyline points="%s" fill="none" stroke="#c0392b" stroke-width="2.5"/>' % pts_str)
    p.append(text(sdx(0.11), sdy(80000) - 12, "SPI / QSPI (Push-Pull, тільки на платі)", size=10, color="#c0392b", anchor="start", bold=True))

    # 2. I2C
    i2c_pts = [(0.1, 1000), (0.3, 400), (1.0, 100), (2.0, 20)]
    pts_str = " ".join("%.1f,%.1f" % (sdx(d), sdy(s)) for d, s in i2c_pts)
    p.append('<polyline points="%s" fill="none" stroke="#2980b9" stroke-width="2.2" stroke-dasharray="4,3"/>' % pts_str)
    p.append(text(sdx(0.12), sdy(1000) + 14, "I2C (Open-Drain, C_bus ≤ 400 пФ)", size=10, color="#2980b9", anchor="start", bold=True))

    # 3. I2C + Буфери
    i2c_buf_pts = [(1.0, 400), (5.0, 400), (20.0, 100), (50.0, 20)]
    pts_str = " ".join("%.1f,%.1f" % (sdx(d), sdy(s)) for d, s in i2c_buf_pts)
    p.append('<polyline points="%s" fill="none" stroke="#16a085" stroke-width="2.0" stroke-dasharray="2,2"/>' % pts_str)
    p.append(text(sdx(4.0), sdy(400) - 10, "I2C + P82B715 / PCA9615 (буфери)", size=9, color="#16a085", anchor="start"))

    # 4. CAN / CAN FD
    can_pts = [(1.0, 5000), (40.0, 1000), (100.0, 500), (500.0, 125), (1000.0, 50)]
    pts_str = " ".join("%.1f,%.1f" % (sdx(d), sdy(s)) for d, s in can_pts)
    p.append('<polyline points="%s" fill="none" stroke="#d35400" stroke-width="2.5"/>' % pts_str)
    p.append(text(sdx(35.0), sdy(1000) - 10, "CAN / CAN FD (диференціал 120 Ом)", size=10, color="#d35400", anchor="start", bold=True))

    # 5. RS-485
    rs485_pts = [(12.0, 10000), (100.0, 2000), (500.0, 500), (1200.0, 100)]
    pts_str = " ".join("%.1f,%.1f" % (sdx(d), sdy(s)) for d, s in rs485_pts)
    p.append('<polyline points="%s" fill="none" stroke="#8e44ad" stroke-width="2.5"/>' % pts_str)
    p.append(text(sdx(14.0), sdy(8000) - 10, "RS-485 (диференційний UART до 1.2 км)", size=10, color="#8e44ad", anchor="start", bold=True))

    render(os.path.join(OUT, "distance-vs-bandwidth.svg"), W, H, *p)


# ── 4. decision-tree.svg: Інженерне дерево прийняття рішень ─────────────────────
def fig_decision_tree():
    W, H = 940, 540
    p = []

    # Кореневий вузол
    bsvg, _, _ = textbox(470, 40, "Вибір шини для периферійного чипа", size=12, pad=7, fill="#eef2ff", stroke="#4f46e5", sw=2, bold=True)
    p.append(bsvg)

    # Рівень 1: Запитання 1
    bsvg, _, _ = textbox(230, 130, "Дистанція > 1–2 м або\nпотрібна завадостійкість?", size=10, pad=6, fill="#fff7ed", stroke="#ea580c", sw=1.5, bold=True)
    p.append(bsvg)
    p.append(arrow(470, 60, 230, 105, color=LINE))

    # Гілка ТАК від Запитання 1
    bsvg, _, _ = textbox(130, 250, "Мережа авто/дрона → CAN\nТочка-точка / Modbus → RS-485\nДерево термометрів → 1-Wire", size=9, pad=6, fill="#ffffff", stroke="#ea580c", sw=1.8)
    p.append(bsvg)
    p.append(arrow(230, 160, 130, 215, color="#ea580c"))
    p.append(text(165, 180, "ТАК", size=9, color="#ea580c", bold=True))

    # Гілка НІ від Запитання 1: Зв'язок у межах плати
    bsvg, _, _ = textbox(630, 130, "Робота в межах однієї плати\nЯкий характер даних і темп?", size=10, pad=6, fill="#f0fdf4", stroke="#16a34a", sw=1.5, bold=True)
    p.append(bsvg)
    p.append(arrow(470, 60, 630, 105, color=LINE))
    p.append(text(410, 115, "НІ", size=9, color="#16a34a", bold=True))

    # Рівень 2: 4 категорії плати
    cats = [
        (380, 250, "Аудіопотік PCM?", "I2S (DMA)\n(ЦАП, АЦП, мікрофон)", "#0d9488"),
        (540, 250, "Flash-пам'ять / XIP?", "QSPI / OSPI\n(пам'ять 50+ МБ/с)", "#4b5563"),
        (700, 250, "Швидкий потік (дисплей,\nIMU > 1 кГц, АЦП)?", "SPI (Push-Pull, CS)\n(10–50 Мбіт/с)", "#dc2626"),
        (855, 250, "Повільні давачі, RTC,\nмало вільних пінів?", "I2C (Open-Drain)\n(100–400 кбіт/с, 2 піни)", "#2563eb"),
    ]

    for cx, cy, q_txt, ans_txt, col in cats:
        bsvg_q, _, _ = textbox(cx, cy, q_txt, size=9, pad=5, fill="#fafafa", stroke=col, sw=1.2, bold=True)
        p.append(bsvg_q)
        p.append(arrow(630, 160, cx, cy - 25, color=LINE))

        bsvg_a, _, _ = textbox(cx, cy + 120, ans_txt, size=9, pad=6, fill="#ffffff", stroke=col, sw=1.8, bold=True)
        p.append(bsvg_a)
        p.append(arrow(cx, cy + 25, cx, cy + 85, color=col))

    # Спеціальна виноска для UART
    bsvg_u, _, _ = textbox(470, 480, "Готовий автономний модуль (GPS, BLE, стільниковий модем, консоль) → UART (з RTS/CTS)", size=10, pad=7, fill="#fefce8", stroke="#ca8a04", sw=1.5, bold=True)
    p.append(bsvg_u)

    render(os.path.join(OUT, "decision-tree.svg"), W, H, *p)


if __name__ == "__main__":
    fig_bus_space()
    fig_topology()
    fig_distance_bandwidth()
    fig_decision_tree()
    print("All figures generated successfully.")

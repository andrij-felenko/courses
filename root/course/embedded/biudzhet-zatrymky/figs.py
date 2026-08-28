# -*- coding: utf-8 -*-
"""Фігури до теми «Бюджет затримки: від ручки до картинки».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Контур керування: Stick-to-Motor ──────────────────────────────────────
def fig_stick_to_motor():
    W, H = 820, 370
    f = [text(W / 2, 28, "Контур керування Stick-to-Motor: послідовність накопичення затримки", size=15, bold=True)]

    ox, oy = 35, 75
    span = 750
    bh = 72

    stages = [
        ("АЦП стіка", 0.11, "#eef1f4", MUTED, "0.5–1.5 мс", "DMA / фільтр"),
        ("UART / CRSF", 0.12, "#eaf0fd", NEG, "0.8–2.0 мс", "пульт → TX"),
        ("Радіоканал", 0.18, "#fef9e7", "#b7791f", "1.0–4.0 мс", "ELRS 500 Гц / ефір"),
        ("Приймач RX", 0.10, "#eef1f4", MUTED, "0.5–1.0 мс", "декодування"),
        ("PID-контур", 0.11, "#eafaf1", FIELD, "0.25–1.0 мс", "4 кГц FC loop"),
        ("Шина DShot", 0.10, "#eaf0fd", NEG, "0.03–0.05 мс", "DShot600 DMA"),
        ("ESC та мотор", 0.28, "#fdecea", POS, "15.0–35.0 мс", "L/R + інерція ротора"),
    ]

    x = ox
    for name, frac, fill, stroke, lat, sub in stages:
        w = span * frac
        f.append(rect(x, oy, w, bh, fill=fill, stroke=stroke, sw=1.8))
        fs = fit_font(name, w - 8, 12, bold=True)
        f.append(text(x + w / 2, oy + 22, name, size=fs, bold=True, color=INK))
        lfs = fit_font(lat, w - 6, 11, bold=True)
        f.append(text(x + w / 2, oy + 42, lat, size=lfs, bold=True, color=stroke))
        sfs = fit_font(sub, w - 6, 9.5)
        f.append(text(x + w / 2, oy + 60, sub, size=sfs, color=MUTED))
        x += w

    # Підсумкові блоки під схемою
    f.append(line(ox, oy + bh + 25, ox + span * 0.72, oy + bh + 25, color=NEG, sw=2))
    f.append(text(ox + (span * 0.72) / 2, oy + bh + 42, "Електронна затримка: 3.1 – 9.6 мс", size=12, bold=True, color=NEG))

    mx = ox + span * 0.72
    mw = span * 0.28
    f.append(line(mx, oy + bh + 25, mx + mw, oy + bh + 25, color=POS, sw=2))
    f.append(text(mx + mw / 2, oy + bh + 42, "Механічний відгук: 15 – 35 мс", size=12, bold=True, color=POS))

    # Рамка з головним висновком
    b, _, _ = textbox(W / 2, 290,
                      "Повна затримка Stick-to-Motor = T_електроніка (~5 мс) + T_механіка (~25 мс) ≈ 30 мс.\n"
                      "Швидкий радіолінк та DShot скорочують електронну частину до мінімуму.",
                      size=11.5, fill="#f8fafc", stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "stick-to-motor-pipeline.svg"), W, H, *f)


# ── 2. Відеотракт: Glass-to-Glass ────────────────────────────────────────────
def fig_glass_to_glass():
    W, H = 820, 390
    f = [text(W / 2, 28, "Відеоконтур Glass-to-Glass: від фотона на сенсорі до пікселя на дисплеї", size=15, bold=True)]

    ox, oy = 35, 75
    span = 750
    bh = 72

    stages = [
        ("Експозиція", 0.16, "#eef1f4", MUTED, "4.0–8.3 мс", "120 fps сенсор"),
        ("ISP / зрізи", 0.15, "#eafaf1", FIELD, "1.5–3.5 мс", "slice H.265"),
        ("OFDM ефір", 0.16, "#fef9e7", "#b7791f", "2.0–5.0 мс", "RF передача"),
        ("Декодер VPU", 0.16, "#eaf0fd", NEG, "2.5–6.0 мс", "ASIC зрізів"),
        ("V-Sync буфер", 0.17, "#fdecea", POS, "4.0–8.3 мс", "120 Гц окуляри"),
        ("Дисплей", 0.20, "#eef1f4", MUTED, "0.1–3.0 мс", "OLED мікропанель"),
    ]

    x = ox
    for name, frac, fill, stroke, lat, sub in stages:
        w = span * frac
        f.append(rect(x, oy, w, bh, fill=fill, stroke=stroke, sw=1.8))
        fs = fit_font(name, w - 8, 12, bold=True)
        f.append(text(x + w / 2, oy + 22, name, size=fs, bold=True, color=INK))
        lfs = fit_font(lat, w - 6, 11, bold=True)
        f.append(text(x + w / 2, oy + 42, lat, size=lfs, bold=True, color=stroke))
        sfs = fit_font(sub, w - 6, 9.5)
        f.append(text(x + w / 2, oy + 60, sub, size=sfs, color=MUTED))
        x += w

    # Пояснення построкового кодування проти кадрового
    f.append(rect(ox, oy + bh + 25, span, 80, fill="#f4f6f8", stroke=LINE, sw=1.2))
    f.append(text(ox + 20, oy + bh + 48, "Построкове (Slice-based) кодування проти кадрового (Frame-based):", size=11.5, bold=True, color=INK, anchor="start"))
    f.append(text(ox + 20, oy + bh + 70, "• Кадровий стиск чекає повного зчитування матриці (+16.7 мс на 60 fps) до початку кодування.", size=10.5, color=MUTED, anchor="start"))
    f.append(text(ox + 20, oy + bh + 88, "• Зрізовий стиск передає перші 16 рядків в ефір, поки сенсор ще експонує нижню частину кадру.", size=10.5, color=FIELD, anchor="start"))

    b, _, _ = textbox(W / 2, 335,
                      "Підсумковий бюджет Glass-to-Glass у цифровому HD = 15 – 35 мс.\n"
                      "Ключ до низького лагу — передача частинами (slices) без очікування повного кадру.",
                      size=11.5, fill="#f8fafc", stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "glass-to-glass-pipeline.svg"), W, H, *f)


# ── 3. Порівняльний баланс трьох стеків ──────────────────────────────────────
def fig_latency_comparison():
    W, H = 820, 420
    f = [text(W / 2, 28, "Порівняльний баланс затримок відео: Аналог vs Цифрове HD vs LTE/IP", size=15, bold=True)]

    ox = 190
    oy = 70
    max_w = 580
    bar_h = 32

    stacks = [
        ("Аналог FPV\n(NTSC / PAL)", 18, FIELD, [
            ("Сенсор", 8.0, "#a7f3d0"),
            ("ЧМ ефір", 0.5, "#fef08a"),
            ("CRT / LCD", 9.5, "#bae6fd"),
        ]),
        ("Цифрове HD\n(Slice H.265)", 36, NEG, [
            ("Сенсор", 8.3, "#a7f3d0"),
            ("ISP/Slice", 4.5, "#fed7aa"),
            ("OFDM", 4.0, "#fef08a"),
            ("VPU декод", 5.2, "#bfdbfe"),
            ("V-Sync/Disp", 14.0, "#bae6fd"),
        ]),
        ("LTE / IP-стрім\n(RTSP / WebRTC)", 185, POS, [
            ("Кадр 30fps", 33.3, "#a7f3d0"),
            ("Кодек GOP", 25.0, "#fed7aa"),
            ("IP / Сокет", 45.0, "#fecaca"),
            ("Буфер джитера", 50.0, "#fde047"),
            ("ОС рендер", 31.7, "#bae6fd"),
        ]),
    ]

    scale = max_w / 200.0

    for idx, (label, total, col, parts) in enumerate(stacks):
        cy = oy + idx * 95
        lines = label.split("\n")
        f.append(text(ox - 15, cy + 10, lines[0], size=12, bold=True, anchor="end", color=INK))
        if len(lines) > 1:
            f.append(text(ox - 15, cy + 26, lines[1], size=10, color=MUTED, anchor="end"))

        bx = ox
        for pname, pms, pcol in parts:
            pw = pms * scale
            f.append(rect(bx, cy, pw, bar_h, fill=pcol, stroke=LINE, sw=1))
            if pw > 38:
                pfs = fit_font(f"{pms:.1f}", pw - 4, 10, bold=True)
                f.append(text(bx + pw / 2, cy + 19, f"{pms:.1f}", size=pfs, bold=True, color=INK))
            bx += pw

        f.append(text(bx + 10, cy + 20, f"~{total} мс", size=13, bold=True, color=col, anchor="start"))

    ax_y = oy + 3 * 95 - 10
    f.append(line(ox, ax_y, ox + max_w, ax_y, color=MUTED, sw=1.5))
    for t_val in [0, 50, 100, 150, 200]:
        tx = ox + t_val * scale
        f.append(line(tx, ax_y, tx, ax_y + 5, color=MUTED, sw=1.2))
        f.append(text(tx, ax_y + 18, f"{t_val} мс", size=10, color=MUTED))

    b, _, _ = textbox(W / 2, 385,
                      "Аналог виграє у швидкості за рахунок растрової розгортки без буферів.\n"
                      "IP-відео платить високу данину сокетним чергам та буферу джитера мережі.",
                      size=11, fill="#f8fafc", stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "latency-balance-comparison.svg"), W, H, *f)


# ── 4. Апаратний стенд вимірювання затримки ──────────────────────────────────
def fig_measurement_rig():
    W, H = 820, 390
    f = [text(W / 2, 28, "Апаратний стенд вимірювання затримки: оптико-електронний метод", size=15, bold=True)]

    f.append(rect(40, 75, 200, 160, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(140, 102, "Вимірювальний MCU", size=13, bold=True, color=NEG))
    f.append(text(140, 122, "STM32 / RP2040", size=11, color=MUTED))
    f.append(text(140, 152, "32-біт таймер (1 мкс)", size=10.5, color=INK))
    f.append(text(140, 172, "Генератор спалаху", size=10.5, color=INK))
    f.append(text(140, 192, "EXTI компаратора", size=10.5, color=INK))
    f.append(text(140, 215, "USB CDC телеметрія", size=10.5, color=FIELD, bold=True))

    f.append(rect(280, 85, 110, 50, fill="#fef9e7", stroke="#b7791f", sw=1.5))
    f.append(text(335, 107, "Тестовий LED", size=11, bold=True, color="#b7791f"))
    f.append(text(335, 123, "спалах T0", size=10, color=MUTED))

    f.append(rect(430, 85, 130, 50, fill="#f4f6f8", stroke=LINE, sw=1.5))
    f.append(text(495, 107, "FPV Камера + VTX", size=11, bold=True, color=INK))
    f.append(text(495, 123, "об'єкт тестування", size=10, color=MUTED))

    f.append(rect(600, 85, 170, 50, fill="#f4f6f8", stroke=LINE, sw=1.5))
    f.append(text(685, 107, "Дисплей окулярів", size=11, bold=True, color=INK))
    f.append(text(685, 123, "VRX + екран", size=10, color=MUTED))

    f.append(rect(615, 175, 140, 60, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(685, 198, "Фотодіод + ОП", size=11.5, bold=True, color=POS))
    f.append(text(685, 218, "поріг яскравості T1", size=10, color=MUTED))

    f.append(line(240, 110, 280, 110, color=NEG, sw=1.8))
    f.append(text(260, 100, "START", size=10, bold=True, color=NEG))

    f.append(line(390, 110, 430, 110, color=MUTED, sw=1.5, dash="3,3"))
    f.append(text(410, 100, "оптика", size=10, color=MUTED))

    f.append(line(560, 110, 600, 110, color=MUTED, sw=1.5, dash="3,3"))
    f.append(text(580, 100, "радіо", size=10, color=MUTED))

    f.append(line(685, 135, 685, 175, color=POS, sw=1.8))
    f.append(text(692, 155, "світло", size=10, color=POS, anchor="start"))

    f.append(line(615, 205, 240, 205, color=POS, sw=1.8))
    f.append(text(430, 195, "STOP (EXTI переривання)", size=10, bold=True, color=POS))

    f.append(rect(40, 255, 740, 65, fill="#ffffff", stroke=LINE, sw=1.2))
    f.append(text(55, 275, "Сигнал LED (T0):", size=10, bold=True, color=NEG, anchor="start"))
    f.append(line(160, 275, 240, 275, color=NEG, sw=2))
    f.append(line(240, 275, 240, 263, color=NEG, sw=2))
    f.append(line(240, 263, 340, 263, color=NEG, sw=2))
    f.append(line(340, 263, 340, 275, color=NEG, sw=2))
    f.append(line(340, 275, 750, 275, color=NEG, sw=2))

    f.append(text(55, 305, "Сигнал фотодіода (T1):", size=10, bold=True, color=POS, anchor="start"))
    f.append(line(160, 305, 480, 305, color=POS, sw=2))
    f.append(line(480, 305, 500, 293, color=POS, sw=2))
    f.append(line(500, 293, 620, 293, color=POS, sw=2))
    f.append(line(620, 293, 640, 305, color=POS, sw=2))
    f.append(line(640, 305, 750, 305, color=POS, sw=2))

    f.append(line(240, 255, 240, 315, color=MUTED, sw=1, dash="2,2"))
    f.append(line(480, 255, 480, 315, color=MUTED, sw=1, dash="2,2"))
    f.append(line(240, 285, 480, 285, color="#1a1a1a", sw=1.5))
    f.append(text(360, 280, "Δt = T1 − T0 (наскрізна затримка)", size=10.5, bold=True, color=INK))

    b, _, _ = textbox(W / 2, 355,
                      "Апаратний стенд усуває похибки несинхронних годинників.\n"
                      "Вимірювання охоплює всі ланки: від датчика камери до фотонів на екрані.",
                      size=11, fill="#f8fafc", stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "hardware-measurement-rig.svg"), W, H, *f)


if __name__ == "__main__":
    fig_stick_to_motor()
    fig_glass_to_glass()
    fig_latency_comparison()
    fig_measurement_rig()
    print("All figures generated successfully.")

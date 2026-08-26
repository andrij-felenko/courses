# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Деградація сигналу в довгій лінії ───────────────────────────────
def fig_long_line_degradation():
    W, H = 940, 380
    f = []
    f.append(text(W / 2, 26, "Деградація сигналу в довгій лінії: однопровідний зв'язок проти диференційного", size=16, bold=True))

    pw, ph = 420, 245
    y_top = 55

    # ── Ліва панель: Однопровідна лінія (I2C / 1-Wire / АЦП)
    x1 = 35
    f.append(rect(x1, y_top, pw, ph, fill="#fffaf5", stroke="#b9770e", sw=1.6))
    f.append(text(x1 + pw / 2, y_top + 20, "Однопровідний зв'язок (I2C / 1-Wire / напруга)", size=13, bold=True, color="#b9770e"))

    # Сітка та осі для лівої панелі
    gy0 = y_top + 205
    f.append(line(x1 + 30, gy0, x1 + pw - 20, gy0, color=LINE, sw=1.4)) # вісь X
    f.append(line(x1 + 30, y_top + 45, x1 + 30, gy0, color=LINE, sw=1.4)) # вісь Y
    f.append(text(x1 + 24, gy0 + 4, "0 В", size=10, color=MUTED, anchor="end"))
    f.append(text(x1 + 24, y_top + 60, "3.3 В", size=10, color=MUTED, anchor="end"))

    # Поріг VIH (2.3 В)
    vy_vih = gy0 - (2.3 / 3.3) * 140
    f.append(line(x1 + 30, vy_vih, x1 + pw - 20, vy_vih, color="#c0392b", sw=1, dash="4 4"))
    f.append(text(x1 + pw - 24, vy_vih - 4, "Поріг VIH (2.3 В)", size=9.5, color="#c0392b", anchor="end"))

    # Вхідний прямокутний імпульс (на платі передавача)
    pts_tx = [(x1 + 40, gy0), (x1 + 40, gy0 - 140), (x1 + 100, gy0 - 140), (x1 + 100, gy0), (x1 + 130, gy0)]
    p_tx_str = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts_tx)
    f.append(f'<polyline points="{p_tx_str}" fill="none" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="3 3"/>')
    f.append(text(x1 + 70, gy0 - 145, "Імпульс на виході МК", size=9.5, color=MUTED))

    # Спотворений сигнал на кінці 30 м кабелю (RC-затягування фронту + шум)
    pts_rx = []
    for i in range(160):
        t = i / 30.0
        v_base = 3.3 * (1.0 - math.exp(-t / 1.8)) if t < 2.5 else 3.3 * (1.0 - math.exp(-2.5 / 1.8)) * math.exp(-(t - 2.5) / 1.8)
        noise = 0.28 * math.sin(t * 7.0) + (0.55 if 1.2 < t < 1.6 else 0.0)
        v_tot = max(0.0, v_base + noise)
        py = gy0 - (v_tot / 3.3) * 140
        px = x1 + 150 + i * 1.5
        pts_rx.append(f"{px:.1f},{py:.1f}")
    f.append(f'<polyline points="{" ".join(pts_rx)}" fill="none" stroke="{POS}" stroke-width="2.2"/>')
    f.append(text(x1 + 260, y_top + 90, "Сигнал на 30 м:", size=11, bold=True, color=POS))
    f.append(text(x1 + 260, y_top + 106, "RC-спадання + завади", size=10, color=POS))

    # Пояснення знизу лівої панелі
    f.append(text(x1 + pw / 2, y_top + 228, "Фронт не встигає піднятися до VIH → втрата даних", size=10.5, color=POS, bold=True))

    # ── Права панель: Диференційна пара RS-485
    x2 = 485
    f.append(rect(x2, y_top, pw, ph, fill="#f5fcf7", stroke=FIELD, sw=1.6))
    f.append(text(x2 + pw / 2, y_top + 20, "Диференційна лінія RS-485 (Звита пара)", size=13, bold=True, color=FIELD))

    # Графіки ліній A і B із синфазною завадою
    gy_diff = y_top + 110
    f.append(line(x2 + 30, gy_diff, x2 + pw - 20, gy_diff, color=MUTED, sw=1, dash="3 3"))

    pts_a = []
    pts_b = []
    for i in range(120):
        t = i / 18.0
        sig = 1.2 if (int(t) % 2 == 0) else -1.2
        v_cm_noise = 0.6 * math.sin(t * 5.0) + (0.8 if 1.8 < t < 2.3 else 0.0)
        va = 2.5 + sig + v_cm_noise
        vb = 2.5 - sig + v_cm_noise
        px = x2 + 40 + i * 2.8
        pya = gy_diff - (va - 2.5) * 22
        pyb = gy_diff - (vb - 2.5) * 22
        pts_a.append(f"{px:.1f},{pya:.1f}")
        pts_b.append(f"{px:.1f},{pyb:.1f}")

    f.append(f'<polyline points="{" ".join(pts_a)}" fill="none" stroke="{POS}" stroke-width="1.6"/>')
    f.append(f'<polyline points="{" ".join(pts_b)}" fill="none" stroke="{NEG}" stroke-width="1.6"/>')
    f.append(text(x2 + pw - 24, gy_diff - 32, "Лінія A (D+)", size=10, bold=True, color=POS, anchor="end"))
    f.append(text(x2 + pw - 24, gy_diff + 38, "Лінія B (D-)", size=10, bold=True, color=NEG, anchor="end"))

    # Результуючий вихід після віднімання (V_A - V_B)
    gy_res = y_top + 195
    f.append(line(x2 + 30, gy_res, x2 + pw - 20, gy_res, color=LINE, sw=1.2))
    f.append(text(x2 + 24, gy_res + 4, "0 В", size=9.5, color=MUTED, anchor="end"))

    pts_res = []
    for i in range(120):
        t = i / 18.0
        sig_diff = 2.4 if (int(t) % 2 == 0) else -2.4
        px = x2 + 40 + i * 2.8
        py = gy_res - sig_diff * 12
        pts_res.append(f"{px:.1f},{py:.1f}")
    f.append(f'<polyline points="{" ".join(pts_res)}" fill="none" stroke="{FIELD}" stroke-width="2.2"/>')
    f.append(text(x2 + pw - 24, gy_res - 26, "V_diff = V_A − V_B (чистий сигнал)", size=10.5, bold=True, color=FIELD, anchor="end"))

    f.append(text(x2 + pw / 2, y_top + 228, "Синфазна завада повністю віднімається приймачем", size=10.5, color=FIELD, bold=True))

    # ── Підсумкова смуга
    f.append(fitbox(35, 312, W - 70, 56,
        "Паразитна ємність 30 м кабелю (1.5–3 нФ) руйнує прямокутні фронти однопровідних шин.\n"
        "Диференційна лінія RS-485 передає протифазні сигнали по звитій парі, віднімаючи наведений шум.",
        size=12.5, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, "long-line-degradation.svg"), W, H, *f)


# ── Фігура 2: Триступеневий захист RS-485 ─────────────────────────────────────
def fig_rs485_transceiver_protection():
    W, H = 960, 400
    f = []
    f.append(text(W / 2, 26, "Схемотехніка вузла RS-485 із триступеневим захистом і термінацією", size=16, bold=True))

    yc = 150
    ya = yc - 45
    yb = yc + 45

    # Головні шини A і B
    f.append(line(70, ya, 880, ya, color=POS, sw=2.2))
    f.append(line(70, yb, 880, yb, color=NEG, sw=2.2))
    f.append(text(75, ya - 10, "A (D+)", size=12, bold=True, color=POS, anchor="start"))
    f.append(text(75, yb + 20, "B (D−)", size=12, bold=True, color=NEG, anchor="start"))

    # Кабель з правого боку
    f.append(fitbox(770, yc - 40, 160, 80, "Довга лінія зв'язку\n(Звита пара STP\nZ₀ = 120 Ом)", size=11, fill="#fffaf5", stroke="#b9770e"))

    # Ступінь 1: Газорозрядники (GDT)
    x_gdt = 680
    f.append(rect(x_gdt - 25, ya - 18, 50, 36, fill="#fdf3ea", stroke="#b9770e", sw=1.6))
    f.append(text(x_gdt, ya + 4, "GDT", size=11, bold=True, color="#b9770e"))
    f.append(rect(x_gdt - 25, yb - 18, 50, 36, fill="#fdf3ea", stroke="#b9770e", sw=1.6))
    f.append(text(x_gdt, yb + 4, "GDT", size=11, bold=True, color="#b9770e"))
    # Заземлення GDT на PE
    f.append(line(x_gdt, ya + 18, x_gdt, yb - 18, color=LINE, sw=1.4))
    f.append(line(x_gdt, yb + 18, x_gdt, yb + 60, color=LINE, sw=1.4))
    f.append(line(x_gdt - 15, yb + 60, x_gdt + 15, yb + 60, color=LINE, sw=2))
    f.append(line(x_gdt - 10, yb + 65, x_gdt + 10, yb + 65, color=LINE, sw=1.6))
    f.append(line(x_gdt - 5, yb + 70, x_gdt + 5, yb + 70, color=LINE, sw=1.2))
    f.append(text(x_gdt + 20, yb + 64, "PE (Захисна земля)", size=10, color=MUTED, anchor="start"))
    f.append(text(x_gdt, ya - 28, "Ступінь 1: GDT", size=11, bold=True, color="#b9770e"))
    f.append(text(x_gdt, ya - 42, "Скидання струму до 10 кА", size=9.5, color=MUTED))

    # Ступінь 2: Самовідновні запобіжники PTC
    x_ptc = 550
    f.append(rect(x_ptc - 28, ya - 14, 56, 28, fill="#eaf0fd", stroke=NEG, sw=1.6))
    f.append(text(x_ptc, ya + 4, "PTC 10Ω", size=10.5, bold=True, color=NEG))
    f.append(rect(x_ptc - 28, yb - 14, 56, 28, fill="#eaf0fd", stroke=NEG, sw=1.6))
    f.append(text(x_ptc, yb + 4, "PTC 10Ω", size=10.5, bold=True, color=NEG))
    f.append(text(x_ptc, ya - 28, "Ступінь 2: PTC", size=11, bold=True, color=NEG))
    f.append(text(x_ptc, ya - 42, "Обмеження струму", size=9.5, color=MUTED))

    # Ступінь 3: Супресори TVS (SM712)
    x_tvs = 420
    f.append(rect(x_tvs - 25, ya - 18, 50, 36, fill="#eafaf0", stroke=FIELD, sw=1.6))
    f.append(text(x_tvs, ya + 4, "TVS", size=11, bold=True, color=FIELD))
    f.append(rect(x_tvs - 25, yb - 18, 50, 36, fill="#eafaf0", stroke=FIELD, sw=1.6))
    f.append(text(x_tvs, yb + 4, "TVS", size=11, bold=True, color=FIELD))
    # Заземлення TVS на сигнальну землю ISO_GND
    f.append(line(x_tvs, ya + 18, x_tvs, yb - 18, color=LINE, sw=1.4))
    f.append(line(x_tvs, yb + 18, x_tvs, yb + 60, color=LINE, sw=1.4))
    f.append(line(x_tvs - 12, yb + 60, x_tvs + 12, yb + 60, color=LINE, sw=1.8))
    f.append(text(x_tvs + 16, yb + 64, "ISO_GND (Сигнальна земля)", size=10, color=MUTED, anchor="start"))
    f.append(text(x_tvs, ya - 28, "Ступінь 3: TVS", size=11, bold=True, color=FIELD))
    f.append(text(x_tvs, ya - 42, "Затискання -7V / +12V (<1 нс)", size=9.5, color=MUTED))

    # Термінатор 120 Ом + Зміщення Fail-Safe
    x_term = 300
    f.append(line(x_term, ya, x_term, ya + 28, color=LINE, sw=1.4))
    f.append(rect(x_term - 16, ya + 28, 32, 34, fill=FILL, stroke=LINE, sw=1.4))
    f.append(text(x_term, ya + 50, "120 Ω", size=10, bold=True))
    f.append(line(x_term, ya + 62, x_term, yb, color=LINE, sw=1.4))
    f.append(text(x_term, ya - 12, "Термінація R_t", size=10.5, bold=True))

    # Fail-Safe підтяжка (A до 5V, B до GND)
    x_fs = 210
    f.append(line(x_fs, ya - 35, x_fs, ya, color=LINE, sw=1.4))
    f.append(rect(x_fs - 16, ya - 35, 32, 24, fill=FILL, stroke=POS, sw=1.2))
    f.append(text(x_fs, ya - 20, "680 Ω", size=9.5, color=POS, bold=True))
    f.append(text(x_fs, ya - 42, "+5V (ISO)", size=10, color=POS, bold=True))

    f.append(line(x_fs, yb, x_fs, yb + 35, color=LINE, sw=1.4))
    f.append(rect(x_fs - 16, yb + 11, 32, 24, fill=FILL, stroke=NEG, sw=1.2))
    f.append(text(x_fs, yb + 26, "680 Ω", size=9.5, color=NEG, bold=True))
    f.append(text(x_fs, yb + 46, "GND (ISO)", size=10, color=NEG, bold=True))
    f.append(text(x_fs, ya - 60, "Fail-Safe зміщення", size=10.5, bold=True))

    # Трансивер RS-485 (мікросхема)
    x_ic = 125
    f.append(rect(x_ic - 45, yc - 65, 90, 130, fill="#fdfefe", stroke=LINE, sw=1.8))
    f.append(text(x_ic, yc - 45, "Трансивер", size=11, bold=True))
    f.append(text(x_ic, yc - 32, "RS-485", size=11, bold=True))
    f.append(text(x_ic - 38, ya + 4, "A", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(x_ic - 38, yb + 4, "B", size=10, bold=True, color=NEG, anchor="start"))
    f.append(text(x_ic + 38, yc - 20, "RO (RX)", size=9.5, anchor="end"))
    f.append(text(x_ic + 38, yc + 5, "DI (TX)", size=9.5, anchor="end"))
    f.append(text(x_ic + 38, yc + 30, "DE/RE", size=9.5, anchor="end"))

    # Нижня смуга-висновок
    f.append(fitbox(35, 325, W - 70, 60,
        "Каскадний захист поєднує швидкість TVS-діодів (<1 нс) і струмову потужність розрядників GDT (>10 кА).\n"
        "Резистори Fail-Safe утримують різницю напруг > +200 мВ у моменти, коли шина вільна (Hi-Z).",
        size=12.5, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, "rs485-transceiver-protection.svg"), W, H, *f)


# ── Фігура 3: Струмова петля 4–20 мА та NAMUR NE 43 ───────────────────────────
def fig_current_loop_namur43():
    W, H = 940, 380
    f = []
    f.append(text(W / 2, 26, "Аналогова струмова петля 4–20 мА та діагностика за стандартом NAMUR NE 43", size=16, bold=True))

    y_top = 55
    ph = 250

    # ── Ліва панель: Топологія кола струмової петлі
    pw_l = 440
    x1 = 35
    f.append(rect(x1, y_top, pw_l, ph, fill="#fffaf5", stroke="#b9770e", sw=1.6))
    f.append(text(x1 + pw_l / 2, y_top + 20, "Топологія дводротової петлі (Loop-Powered)", size=13, bold=True, color="#b9770e"))

    # Блоки: Джерело 24V, Давач-перетворювач, Шунт
    f.append(rect(x1 + 25, y_top + 50, 90, 60, fill="#fdf3ea", stroke=POS, sw=1.5))
    f.append(text(x1 + 70, y_top + 76, "Джерело", size=11, bold=True, color=POS))
    f.append(text(x1 + 70, y_top + 94, "+24 В DC", size=11, bold=True, color=POS))

    # Давач на відстані 30 метрів
    f.append(rect(x1 + 280, y_top + 75, 130, 90, fill="#eafaf0", stroke=FIELD, sw=1.6))
    f.append(text(x1 + 345, y_top + 102, "Давач 4–20 мА", size=11.5, bold=True, color=FIELD))
    f.append(text(x1 + 345, y_top + 120, "(Регулятор струму)", size=10, color=MUTED))
    f.append(text(x1 + 345, y_top + 145, "I_петлі = f(P, T, Q)", size=10, bold=True, color=FIELD))

    # Приймальний шунт на боці контролера
    f.append(rect(x1 + 25, y_top + 160, 90, 60, fill="#eaf0fd", stroke=NEG, sw=1.5))
    f.append(text(x1 + 70, y_top + 185, "Шунт R_ш", size=11, bold=True, color=NEG))
    f.append(text(x1 + 70, y_top + 204, "250 Ω (0.1%)", size=10.5, color=NEG))

    # Дроти струмової петлі
    f.append(line(x1 + 115, y_top + 80, x1 + 280, y_top + 95, color=POS, sw=2))
    f.append(text(x1 + 195, y_top + 72, "Кабель 30 м (+)", size=10, color=POS, bold=True))

    f.append(line(x1 + 280, y_top + 145, x1 + 115, y_top + 190, color=NEG, sw=2))
    f.append(text(x1 + 195, y_top + 182, "Кабель 30 м (−)", size=10, color=NEG, bold=True))

    # З'єднання між джерелом і шунтом
    f.append(line(x1 + 70, y_top + 110, x1 + 70, y_top + 160, color=LINE, sw=1.4))

    # Вихід до АЦП (з шунта)
    f.append(line(x1 + 115, y_top + 175, x1 + 175, y_top + 175, color=FIELD, sw=1.6))
    f.append(text(x1 + 180, y_top + 179, "U_вх = 1.0…5.0 В → до АЦП", size=10.5, color=FIELD, bold=True, anchor="start"))

    f.append(text(x1 + pw_l / 2, y_top + 235, "Струм I однаковий у кожній точці кола (I_кабелю = I_шунта)", size=10.5, color=LINE, bold=True))

    # ── Права панель: Шкала NAMUR NE 43
    pw_r = 410
    x2 = 495
    f.append(rect(x2, y_top, pw_r, ph, fill="#fdfefe", stroke=LINE, sw=1.6))
    f.append(text(x2 + pw_r / 2, y_top + 20, "Діагностичні зони за стандартом NAMUR NE 43", size=12.5, bold=True))

    # Вертикальна або горизонтальна шкала діапазонів
    zones = [
        ("0.0 … 3.6 мА", "Обрив лінії / Аварія живлення", "#fadbd8", POS),
        ("3.8 … 4.0 мА", "Нижнє зашкалювання / Дрейф нуля", "#fef9e7", "#b9770e"),
        ("4.0 … 20.0 мА", "Робочий діапазон вимірювання (0…100%)", "#d5f5e3", FIELD),
        ("20.0 … 20.5 мА", "Верхнє зашкалювання шкали", "#fef9e7", "#b9770e"),
        ("> 21.0 мА", "Коротке замикання / Аварія сенсора", "#fadbd8", POS),
    ]

    zy0 = y_top + 45
    zh = 34
    for i, (rng, desc, bg_c, border_c) in enumerate(zones):
        zy = zy0 + i * (zh + 6)
        f.append(rect(x2 + 20, zy, pw_r - 40, zh, fill=bg_c, stroke=border_c, sw=1.4))
        f.append(text(x2 + 30, zy + 21, rng, size=11, bold=True, color=border_c, anchor="start"))
        f.append(text(x2 + 155, zy + 21, desc, size=10, color=INK, anchor="start"))

    # Нижня смуга
    f.append(fitbox(35, 318, W - 70, 52,
        "«Живий нуль» (4 мА) дозволяє однозначно відрізнити нульове значення вимірюваної величини від обриву дроту.\n"
        "Спад напруги на опорі довгих жил кабелю не вносить жодної похибки у виміряний струм.",
        size=12.5, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, "current-loop-namur43.svg"), W, H, *f)


# ── Фігура 4: Гальванічна розв'язка вузла ─────────────────────────────────────
def fig_galvanic_isolation_topology():
    W, H = 940, 380
    f = []
    f.append(text(W / 2, 26, "Повна гальванічна розв'язка вузла зв'язку та захист від перекосу земель", size=16, bold=True))

    y_top = 55
    ph = 250

    # Ліва частина: Неізольована зона МК
    pw_mcu = 280
    x_mcu = 35
    f.append(rect(x_mcu, y_top, pw_mcu, ph, fill="#eaf0fd", stroke=NEG, sw=1.6))
    f.append(text(x_mcu + pw_mcu / 2, y_top + 22, "Мікроконтролер (Зона МК)", size=13, bold=True, color=NEG))

    f.append(rect(x_mcu + 30, y_top + 55, 140, 90, fill="#fdfefe", stroke=NEG, sw=1.4))
    f.append(text(x_mcu + 100, y_top + 85, "MCU", size=14, bold=True, color=NEG))
    f.append(text(x_mcu + 100, y_top + 105, "STM32 / ESP32", size=10, color=MUTED))
    f.append(text(x_mcu + 100, y_top + 125, "UART + GPIO_DE", size=9.5, color=LINE))

    f.append(text(x_mcu + pw_mcu / 2, y_top + 195, "Живлення: +3.3 В (VCC1)", size=10.5, color=LINE, bold=True))
    f.append(text(x_mcu + pw_mcu / 2, y_top + 220, "Земля: GND1 (Локальна)", size=10.5, color=LINE, bold=True))

    # Центральна частина: Бар'єр ізоляції (Ізолятори + DC-DC)
    x_iso = 330
    w_iso = 280
    f.append(rect(x_iso, y_top, w_iso, ph, fill="#fffdf5", stroke="#b9770e", sw=1.6))
    f.append(text(x_iso + w_iso / 2, y_top + 22, "Гальванічний бар'єр (2.5–5 кВ)", size=12.5, bold=True, color="#b9770e"))

    # Цифровий ізолятор
    f.append(rect(x_iso + 25, y_top + 45, w_iso - 50, 75, fill="#fdfefe", stroke=LINE, sw=1.5))
    f.append(text(x_iso + w_iso / 2, y_top + 68, "Цифровий ізолятор сигналів", size=11, bold=True))
    f.append(text(x_iso + w_iso / 2, y_top + 86, "(ISO7721 / ADuM1201 / Оптопари)", size=9.5, color=MUTED))
    f.append(text(x_iso + w_iso / 2, y_top + 105, "TXD, RXD, DE (CMTI > 100 кВ/мкс)", size=9.5, bold=True, color=FIELD))

    # Ізольований DC-DC перетворювач
    f.append(rect(x_iso + 25, y_top + 135, w_iso - 50, 75, fill="#fdfefe", stroke=LINE, sw=1.5))
    f.append(text(x_iso + w_iso / 2, y_top + 158, "Ізольований DC-DC (B0505S)", size=11, bold=True))
    f.append(text(x_iso + w_iso / 2, y_top + 176, "Трансформаторна розв'язка 1 Вт", size=9.5, color=MUTED))
    f.append(text(x_iso + w_iso / 2, y_top + 195, "+5V / 3.3V → ISO_5V (Плаваюче)", size=9.5, bold=True, color=POS))

    # Права частина: Ізольована зона трансивера
    x_rs = 625
    pw_rs = 280
    f.append(rect(x_rs, y_top, pw_rs, ph, fill="#eafaf0", stroke=FIELD, sw=1.6))
    f.append(text(x_rs + pw_rs / 2, y_top + 22, "Ізольований трансивер RS-485", size=12.5, bold=True, color=FIELD))

    f.append(rect(x_rs + 25, y_top + 55, 120, 90, fill="#fdfefe", stroke=FIELD, sw=1.4))
    f.append(text(x_rs + 85, y_top + 85, "RS-485", size=13, bold=True, color=FIELD))
    f.append(text(x_rs + 85, y_top + 105, "SN65HVD / MAX485", size=9.5, color=MUTED))
    f.append(text(x_rs + 85, y_top + 125, "Драйвер лінії", size=9.5, color=LINE))

    # Лінії в кабель
    f.append(line(x_rs + 145, y_top + 80, x_rs + 250, y_top + 80, color=POS, sw=2))
    f.append(line(x_rs + 145, y_top + 110, x_rs + 250, y_top + 110, color=NEG, sw=2))
    f.append(text(x_rs + 255, y_top + 84, "A (D+)", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(x_rs + 255, y_top + 114, "B (D−)", size=10, bold=True, color=NEG, anchor="start"))

    f.append(text(x_rs + pw_rs / 2, y_top + 195, "Живлення: ISO_5V (Ізольоване)", size=10.5, color=LINE, bold=True))
    f.append(text(x_rs + pw_rs / 2, y_top + 220, "Земля: ISO_GND (Ізольована)", size=10.5, color=LINE, bold=True))

    # Знизу покажчик різниці потенціалів ΔV_GND
    f.append(fitbox(35, 318, W - 70, 52,
        "Гальванічна розв'язка розриває земляні петлі та витримує перекіс потенціалів між будівлями (ΔV_GND до кількох кіловольт),\n"
        "захищаючи мікроконтролер від вигорання портів та фатальних синфазних перенапруг.",
        size=12.5, fill=FILL, stroke=MUTED))

    render(os.path.join(OUT, "galvanic-isolation-topology.svg"), W, H, *f)


if __name__ == '__main__':
    fig_long_line_degradation()
    fig_rs485_transceiver_protection()
    fig_current_loop_namur43()
    fig_galvanic_isolation_topology()
    print("All figures generated successfully.")

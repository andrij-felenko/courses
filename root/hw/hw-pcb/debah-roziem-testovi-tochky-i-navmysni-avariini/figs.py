# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# ── 1. Розпіновка 10-pin Cortex Debug та топологія Tag-Connect TC2030 ─────────
def fig_swd_tag_connect():
    W, H = 880, 480
    f = []

    # Заголовок фігури
    f.append(text(W / 2, 24, "Стандарти налагоджувальних інтерфейсів: 10-pin Cortex Debug та Tag-Connect TC2030", size=15, bold=True))

    # ── Ліва частина: 10-pin Cortex Debug (1.27 мм) ──────────────────────────
    lx, ly = 30, 52
    lw, lh = 395, 410
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(lx + lw / 2, ly + 22, "10-pin Cortex Debug (1.27 мм / 50 mil)", size=13, bold=True, color=INK))

    # Корпус роз'єму (Shrouded Header)
    hx, hy = lx + 35, ly + 46
    hw, hh = 325, 200
    f.append(rect(hx, hy, hw, hh, fill="#f8fafc", stroke="#475569", sw=1.5, rx=4))
    f.append(text(hx + hw / 2, hy + 18, "Роз'єм Samtec FTSH-105 (вигляд згори на штирі)", size=11, color=MUTED, italic=True))

    # Ключ орієнтації (виріз поляризатора зверху)
    f.append(rect(hx + hw / 2 - 25, hy, 50, 10, fill="#e2e8f0", stroke="#475569", sw=1.2, rx=2))
    f.append(text(hx + hw / 2, hy + 8, "Ключ", size=9, color="#64748b", bold=True))

    # Матриця пінів 2x5
    pins_left = [
        ("1", "VCC / VTref (1.8–3.3V)", POS),
        ("3", "GND (Опорна земля)", NEG),
        ("5", "GND (Опорна земля)", NEG),
        ("7", "Ключ (Key / NC)", MUTED),
        ("9", "GNDDetect (Детект)", NEG),
    ]
    pins_right = [
        ("2", "SWDIO / TMS (Дані)", "#d97706"),
        ("4", "SWCLK / TCK (Такт)", "#2563eb"),
        ("6", "SWO / TDO (Трасування)", "#059669"),
        ("8", "NC / TDI (Вхід JTAG)", MUTED),
        ("10", "nRESET (Скидання MCU)", POS),
    ]

    sy = hy + 40
    row_h = 30
    for idx, (num, name, col) in enumerate(pins_left):
        py_row = sy + idx * row_h
        # Пін колонка 1 (ліва)
        px_pin1 = hx + 40
        f.append(circle(px_pin1, py_row, 7, fill="#ffffff", stroke=col, sw=1.8))
        f.append(text(px_pin1, py_row + 3.5, num, size=9.5, color=col, bold=True))
        f.append(text(px_pin1 + 14, py_row + 3.5, name, size=10, color=INK, anchor="start"))

    for idx, (num, name, col) in enumerate(pins_right):
        py_row = sy + idx * row_h
        # Пін колонка 2 (права)
        px_pin2 = hx + 195
        f.append(circle(px_pin2, py_row, 7, fill="#ffffff", stroke=col, sw=1.8))
        f.append(text(px_pin2, py_row + 3.5, num, size=9.5, color=col, bold=True))
        f.append(text(px_pin2 + 14, py_row + 3.5, name, size=10, color=INK, anchor="start"))

    # Пояснювальний блок під роз'ємом
    by = ly + 258
    f.append(rect(lx + 15, by, lw - 30, 138, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    f.append(text(lx + 25, by + 18, "Вимоги до трасування на платі:", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(lx + 25, by + 38, "• Підтяжка nRESET: 10–100 кОм до VCC + 100 нФ на GND", size=10, color=LINE, anchor="start"))
    f.append(text(lx + 25, by + 56, "• SWD лінії: прямий маршрут без перехідних отворів", size=10, color=LINE, anchor="start"))
    f.append(text(lx + 25, by + 74, "• Паразитна ємність ліній SWDIO/SWCLK: < 15–20 пФ", size=10, color=LINE, anchor="start"))
    f.append(text(lx + 25, by + 92, "• ESD-захист: TVS-діодні збірки (C_diode < 1.0 пФ)", size=10, color=LINE, anchor="start"))
    f.append(text(lx + 25, by + 110, "• Габарити на платі: 6.35 × 5.08 мм, висота 5.0 мм", size=10, color=MUTED, anchor="start"))

    # ── Права частина: Tag-Connect TC2030 (Безроз'ємний) ─────────────────────
    rx_b, ry_b = 445, 52
    rw_b, rh_b = 405, 410
    f.append(rect(rx_b, ry_b, rw_b, rh_b, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(rx_b + rw_b / 2, ry_b + 22, "Tag-Connect TC2030-IDC (Нульовий BOM)", size=13, bold=True, color=INK))

    # Футпринт на платі
    fx, fy = rx_b + 35, ry_b + 46
    fw, fh = 335, 200
    f.append(rect(fx, fy, fw, fh, fill="#f8fafc", stroke="#475569", sw=1.5, rx=4))
    f.append(text(fx + fw / 2, fy + 18, "Топологія контактних площадок і отворів на PCB", size=11, color=MUTED, italic=True))

    # Центральні 6 контактних площадок (Pogo Pin Pads, 1.27 мм крок)
    tc_pads = [
        (fx + 130, fy + 70, "1", "VCC", POS),
        (fx + 175, fy + 70, "2", "SWDIO", "#d97706"),
        (fx + 220, fy + 70, "3", "nRESET", POS),
        (fx + 130, fy + 105, "4", "SWCLK", "#2563eb"),
        (fx + 175, fy + 105, "5", "GND", NEG),
        (fx + 220, fy + 105, "6", "SWO", "#059669"),
    ]

    for px_p, py_p, num, sig, col in tc_pads:
        f.append(circle(px_p, py_p, 8, fill="#fef3c7", stroke="#d97706", sw=1.2))
        f.append(circle(px_p, py_p, 3, fill=col, stroke=col, sw=1))
        f.append(text(px_p, py_p - 11, f"{num}:{sig}", size=9.5, color=INK, bold=True))

    # Напрямні отвори зі сталевими штирями (Alignment Holes - 3 отвори d=0.99 мм)
    align_holes = [
        (fx + 90, fy + 87.5, "Отвор 1 (0.99 мм)"),
        (fx + 260, fy + 70, "Отвор 2"),
        (fx + 260, fy + 105, "Отвор 3"),
    ]
    for hx_a, hy_a, lbl in align_holes:
        f.append(circle(hx_a, hy_a, 6.5, fill="#cbd5e1", stroke="#334155", sw=1.5))
        f.append(text(hx_a, hy_a + 16, lbl, size=9, color="#475569"))

    # Фіксуючі отвори для ніжок (Legged Version - 4 отвори d=2.36 мм)
    leg_holes = [
        (fx + 45, fy + 55, "Фіксатор"),
        (fx + 45, fy + 120, "Фіксатор"),
        (fx + 300, fy + 55, "Фіксатор"),
        (fx + 300, fy + 120, "Фіксатор"),
    ]
    for lx_h, ly_h, lbl in leg_holes:
        f.append(circle(lx_h, ly_h, 11, fill="#e2e8f0", stroke="#64748b", sw=1.2))
        f.append(text(lx_h, ly_h + 3.5, "Ніжка", size=9, color="#64748b"))

    f.append(text(fx + fw / 2, fy + 178, "Зона заборони SMD-компонентів: 8.5 × 5.5 мм навколо", size=10, color="#b91c1c", bold=True))

    # Пояснювальний блок для Tag-Connect
    r_by = ry_b + 258
    f.append(rect(rx_b + 15, r_by, rw_b - 30, 138, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    f.append(text(rx_b + 25, r_by + 18, "Переваги та особливості використання:", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(rx_b + 25, r_by + 38, "• Вартість у BOM: 0 $ (на платі лише мідь та отвори)", size=10, color=POS, anchor="start", bold=True))
    f.append(text(rx_b + 25, r_by + 56, "• Висота Z: 0.0 мм (ідеально для герметичних корпусів)", size=10, color=LINE, anchor="start"))
    f.append(text(rx_b + 25, r_by + 74, "• Покриття контактів: тільки ENIG (HASL створює горби)", size=10, color=LINE, anchor="start"))
    f.append(text(rx_b + 25, r_by + 92, "• Версія 'No-Legs' займає лише 3.5 × 1.8 мм площі плати", size=10, color=LINE, anchor="start"))
    f.append(text(rx_b + 25, r_by + 110, "• Ресурс кабелю TC2030: понад 50 000 циклів стикування", size=10, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "swd-tag-connect-pinout.svg"), W, H, *f)


# ── 2. Секціонування шин живлення, перемички та ізоляція КЗ ───────────────────
def fig_power_domain_sectioning():
    W, H = 880, 480
    f = []

    # Заголовок фігури
    f.append(text(W / 2, 24, "Секціонування шин живлення, паяльні перемички та ізоляція аварійних вузлів", size=15, bold=True))

    # Джерело живлення / Головний DC-DC перетворювач
    bx, by = 30, 60
    bw, bh = 140, 390
    f.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke="#475569", sw=1.5, rx=6))
    f.append(text(bx + bw / 2, by + 24, "Первинний блок", size=12.5, bold=True, color=INK))
    f.append(text(bx + bw / 2, by + 42, "Вхід VIN = 12–24V", size=10.5, color=MUTED))

    # Головний перетворювач Buck
    f.append(rect(bx + 12, by + 75, bw - 24, 90, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=4))
    f.append(text(bx + bw / 2, by + 102, "Step-Down DC/DC", size=11, bold=True, color="#1d4ed8"))
    f.append(text(bx + bw / 2, by + 120, "Вихід +3.3V_SYS", size=10.5, color="#1d4ed8", bold=True))
    f.append(text(bx + bw / 2, by + 138, "I_max = 3.0 A", size=10, color=MUTED))

    # Силовий вхід на мотори
    f.append(rect(bx + 12, by + 235, bw - 24, 90, fill="#fef2f2", stroke="#ef4444", sw=1.2, rx=4))
    f.append(text(bx + bw / 2, by + 262, "Силова шина", size=11, bold=True, color=POS))
    f.append(text(bx + bw / 2, by + 280, "+12V_MOTOR", size=10.5, color=POS, bold=True))
    f.append(text(bx + bw / 2, by + 298, "I_peak = 15 A", size=10, color=MUTED))

    # Тестова точка на головній шині TP_SYS
    f.append(circle(bx + bw + 20, by + 120, 6, fill="#fef08a", stroke="#ca8a04", sw=1.2))
    f.append(text(bx + bw + 20, by + 104, "TP_SYS", size=9, bold=True, color="#854d0e"))

    # Доріжка головної шини +3.3V
    f.append(line(bx + bw, by + 120, bx + bw + 55, by + 120, color="#2563eb", sw=3))
    f.append(line(bx + bw + 55, by + 65, bx + bw + 55, by + 205, color="#2563eb", sw=3))

    # ── Гілка 1: Цифрове ядро MCU (через Solder Jumper NC + Амперметр) ───────
    g1_y = by + 65
    f.append(line(bx + bw + 55, g1_y, bx + bw + 90, g1_y, color="#2563eb", sw=2.5))

    # Паяльна перемичка SJ1
    f.append(rect(bx + bw + 90, g1_y - 12, 45, 24, fill="#fef9c3", stroke="#ca8a04", sw=1.2, rx=3))
    f.append(circle(bx + bw + 102, g1_y, 4, fill="#ca8a04", stroke="#ca8a04", sw=1))
    f.append(circle(bx + bw + 123, g1_y, 4, fill="#ca8a04", stroke="#ca8a04", sw=1))
    f.append(line(bx + bw + 102, g1_y, bx + bw + 123, g1_y, color="#ca8a04", sw=1.5)) # перемичка
    f.append(text(bx + bw + 112, g1_y - 17, "SJ1 (NC)", size=9.5, bold=True, color="#854d0e"))

    f.append(line(bx + bw + 135, g1_y, bx + bw + 195, g1_y, color="#2563eb", sw=2.5))
    # Тестова точка TP_MCU
    f.append(circle(bx + bw + 165, g1_y, 6, fill="#fef08a", stroke="#ca8a04", sw=1.2))
    f.append(text(bx + bw + 165, g1_y - 10, "TP_MCU", size=9, bold=True, color="#854d0e"))

    # Блок MCU
    f.append(rect(bx + bw + 195, g1_y - 30, 185, 60, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=5))
    f.append(text(bx + bw + 287, g1_y - 8, "Цифрове ядро (MCU Core)", size=11, bold=True, color="#15803d"))
    f.append(text(bx + bw + 287, g1_y + 12, "VDD = 3.3V (25–120 мА)", size=10, color=MUTED))

    # Виносний амперметр для вимірювання струму
    f.append(rect(bx + bw + 410, g1_y - 28, 180, 56, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=4))
    f.append(text(bx + bw + 500, g1_y - 10, "Вимірювання струму:", size=10, bold=True, color="#1d4ed8"))
    f.append(text(bx + bw + 500, g1_y + 10, "Розрізати SJ1 → щупи mA", size=9.5, color=LINE))

    # ── Гілка 2: Аналоговий домен VDDA (через 0-Ом резистор + Фільтр) ────────
    g2_y = by + 135
    f.append(line(bx + bw + 55, g2_y, bx + bw + 90, g2_y, color="#2563eb", sw=2.5))

    # Резистор 0 Ом R_JUMP
    f.append(rect(bx + bw + 90, g2_y - 10, 45, 20, fill="#ffffff", stroke="#0284c7", sw=1.2, rx=2))
    f.append(text(bx + bw + 112, g2_y + 4, "0 Ω", size=9.5, bold=True, color="#0369a1"))
    f.append(text(bx + bw + 112, g2_y - 15, "R_JUMP", size=9, color="#0369a1"))

    f.append(line(bx + bw + 135, g2_y, bx + bw + 195, g2_y, color="#0284c7", sw=2.5))
    # Тестова точка TP_VDDA
    f.append(circle(bx + bw + 165, g2_y, 6, fill="#fef08a", stroke="#ca8a04", sw=1.2))
    f.append(text(bx + bw + 165, g2_y - 10, "TP_VDDA", size=9, bold=True, color="#854d0e"))

    # Блок Аналогового АЦП
    f.append(rect(bx + bw + 195, g2_y - 30, 185, 60, fill="#faf5ff", stroke="#9333ea", sw=1.5, rx=5))
    f.append(text(bx + bw + 287, g2_y - 8, "Аналогова частина (VDDA)", size=11, bold=True, color="#7e22ce"))
    f.append(text(bx + bw + 287, g2_y + 12, "АЦП / Джерело опори (5 мА)", size=10, color=MUTED))

    # Пояснення про ізоляцію шумів
    f.append(rect(bx + bw + 410, g2_y - 28, 180, 56, fill="#fdf4ff", stroke="#c084fc", sw=1.2, rx=4))
    f.append(text(bx + bw + 500, g2_y - 10, "Ізоляція шумів живлення:", size=10, bold=True, color="#7e22ce"))
    f.append(text(bx + bw + 500, g2_y + 10, "Заміна 0 Ω на Ferrite Bead", size=9.5, color=LINE))

    # ── Гілка 3: Периферія та радіомодуль (через Аварійний розріз Trace Cut) ──
    g3_y = by + 205
    f.append(line(bx + bw + 55, g3_y, bx + bw + 90, g3_y, color="#2563eb", sw=2.5))

    # Аварійний розріз (Звуження доріжки 0.2 мм + мітка ножиць)
    f.append(rect(bx + bw + 90, g3_y - 10, 45, 20, fill="#fff1f2", stroke="#e11d48", sw=1.2, rx=2))
    f.append(line(bx + bw + 90, g3_y, bx + bw + 135, g3_y, color="#e11d48", sw=1.2)) # тонка лінія
    f.append(text(bx + bw + 112, g3_y + 4, "✂ CUT", size=9.5, bold=True, color="#be123c"))
    f.append(text(bx + bw + 112, g3_y - 15, "Розріз", size=9.5, color="#be123c"))

    f.append(line(bx + bw + 135, g3_y, bx + bw + 195, g3_y, color="#2563eb", sw=2.5))
    # Тестова точка TP_PERIPH
    f.append(circle(bx + bw + 165, g3_y, 6, fill="#fef08a", stroke="#ca8a04", sw=1.2))
    f.append(text(bx + bw + 165, g3_y - 10, "TP_RF", size=9.5, bold=True, color="#854d0e"))

    # Блок Радіомодуля
    f.append(rect(bx + bw + 195, g3_y - 30, 185, 60, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=5))
    f.append(text(bx + bw + 287, g3_y - 8, "Периферія / Wi-Fi / BLE", size=11, bold=True, color="#b45309"))
    f.append(text(bx + bw + 287, g3_y + 12, "Струм передачі (до 350 мА)", size=10, color=MUTED))

    # Пояснення про ізоляцію КЗ
    f.append(rect(bx + bw + 410, g3_y - 28, 180, 56, fill="#fff1f2", stroke="#fda4af", sw=1.2, rx=4))
    f.append(text(bx + bw + 500, g3_y - 10, "Аварійна ізоляція КЗ:", size=10, bold=True, color="#be123c"))
    f.append(text(bx + bw + 500, g3_y + 10, "Скальпель при блокуванні DC/DC", size=9.5, color=LINE))

    # ── Гілка 4: Силовий драйвер мотора (Шунт Кельвіна 10 мОм) ───────────────
    g4_y = by + 280
    f.append(line(bx + bw, g4_y, bx + bw + 70, g4_y, color=POS, sw=3.5))

    # Шунт Кельвіна R_SHUNT
    f.append(rect(bx + bw + 70, g4_y - 14, 65, 28, fill="#ffffff", stroke=POS, sw=1.5, rx=3))
    f.append(text(bx + bw + 102, g4_y + 4, "10 mΩ", size=10, bold=True, color=POS))
    f.append(text(bx + bw + 102, g4_y - 18, "R_SHUNT (1%)", size=9.5, color=POS))

    # Кельвінівські відводи
    f.append(circle(bx + bw + 80, g4_y - 26, 4.5, fill="#fef08a", stroke="#ca8a04", sw=1))
    f.append(circle(bx + bw + 124, g4_y - 26, 4.5, fill="#fef08a", stroke="#ca8a04", sw=1))
    f.append(text(bx + bw + 80, g4_y - 36, "Kelvin+", size=9, bold=True, color="#854d0e"))
    f.append(text(bx + bw + 124, g4_y - 36, "Kelvin−", size=9, bold=True, color="#854d0e"))
    f.append(line(bx + bw + 80, g4_y - 14, bx + bw + 80, g4_y - 22, color="#ca8a04", sw=1))
    f.append(line(bx + bw + 124, g4_y - 14, bx + bw + 124, g4_y - 22, color="#ca8a04", sw=1))

    f.append(line(bx + bw + 135, g4_y, bx + bw + 195, g4_y, color=POS, sw=3.5))

    # Блок H-Bridge Мотора
    f.append(rect(bx + bw + 195, g4_y - 30, 185, 60, fill="#fef2f2", stroke=POS, sw=1.5, rx=5))
    f.append(text(bx + bw + 287, g4_y - 8, "Силовий міст (H-Bridge)", size=11, bold=True, color=POS))
    f.append(text(bx + bw + 287, g4_y + 12, "Драйвер мотора / MOSFET", size=10, color=MUTED))

    # Пояснення про захист від надструму
    f.append(rect(bx + bw + 410, g4_y - 28, 180, 56, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=4))
    f.append(text(bx + bw + 500, g4_y - 10, "Моніторинг пускових струмів:", size=10, bold=True, color=POS))
    f.append(text(bx + bw + 500, g4_y + 10, "Точний контроль I = ΔV / 0.01", size=9.5, color=LINE))

    # ── Нижній підсумковий блок правил Bring-up ──────────────────────────────
    iy = by + 340
    f.append(rect(bx, iy, W - 60, 50, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(bx + 15, iy + 20, "Стратегія першого увімкнення (Bring-up):", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(bx + 15, iy + 38, "1. Дзвінок усіх шин на GND → 2. Увімкнення тільки DC-DC (SJ1/0Ω розімкнені) → 3. Послідовне замикання підсистем", size=9.5, color=LINE, anchor="start"))

    return render(os.path.join(IMG, "power-domain-sectioning-jumpers.svg"), W, H, *f)


if __name__ == "__main__":
    fig_swd_tag_connect()
    fig_power_domain_sectioning()
    print("All figures generated successfully.")

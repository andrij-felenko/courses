# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми «Шпаруватість роботи: коли вмикатися і як рідко».
Використовує спільний svgkit із scripts/.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# ── 1. Декомпозиція фаз активності та струму (duty-cycle-phases.svg) ─────────
def make_duty_cycle_phases():
    w, h = 880, 420
    frags = []

    # Фон графіка
    gx, gy, gw, gh = 80, 60, 740, 240
    frags.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=4))

    # Сітка та осі
    for y_val, label in [(gy + 30, "100 мА"), (gy + 90, "30 мА"), (gy + 160, "5 мА"), (gy + gh - 15, "0 мА")]:
        frags.append(line(gx, y_val, gx + gw, y_val, color="#e1e4e8", sw=1, dash="4,4"))
        frags.append(text(gx - 10, y_val + 4, label, size=11, color=MUTED, anchor="end"))

    frags.append(arrow(gx, gy + gh, gx + gw + 30, gy + gh, color=INK, sw=1.8))
    frags.append(arrow(gx, gy + gh, gx, gy - 25, color=INK, sw=1.8))
    frags.append(text(gx + gw + 35, gy + gh + 4, "t", size=13, bold=True, anchor="start"))
    frags.append(text(gx - 10, gy - 30, "I (струм)", size=13, bold=True, anchor="end"))

    y_base = gy + gh
    poly_pts = [
        f"{gx},{y_base - 3}",
        f"{gx + 20},{y_base - 3}",
        f"{gx + 20},{y_base - 45}",   # старт пробудження
        f"{gx + 60},{y_base - 45}",
        f"{gx + 60},{y_base - 35}",   # давач
        f"{gx + 120},{y_base - 35}",
        f"{gx + 120},{y_base - 100}", # CPU
        f"{gx + 170},{y_base - 100}",
        f"{gx + 170},{y_base - 210}", # TX Радіо
        f"{gx + 250},{y_base - 210}",
        f"{gx + 250},{y_base - 30}",  # Засинання
        f"{gx + 280},{y_base - 30}",
        f"{gx + 280},{y_base - 3}",   # Сон
        f"{gx + gw},{y_base - 3}",
        f"{gx + gw},{y_base}",
        f"{gx},{y_base}"
    ]
    frags.append(f'<polygon points="{" ".join(poly_pts)}" fill="#fee2e2" stroke="{POS}" stroke-width="2"/>')

    # Виділення радіо TX іншим кольором
    tx_pts = [
        f"{gx + 170},{y_base}",
        f"{gx + 170},{y_base - 210}",
        f"{gx + 250},{y_base - 210}",
        f"{gx + 250},{y_base}"
    ]
    frags.append(f'<polygon points="{" ".join(tx_pts)}" fill="#fca5a5" stroke="{POS}" stroke-width="2"/>')

    # Лінія сплячого режиму
    frags.append(line(gx + 280, y_base - 3, gx + gw, y_base - 3, color=NEG, sw=3))

    # Підписи підфаз t_on
    frags.append(text(gx + 40, y_base - 55, "Старт", size=10, color=INK, bold=True))
    frags.append(text(gx + 90, y_base - 45, "Давач", size=10, color=INK, bold=True))
    frags.append(text(gx + 145, y_base - 110, "MCU", size=10, color=INK, bold=True))
    frags.append(text(gx + 210, y_base - 220, "Радіо TX (85 мА)", size=11, color=POS, bold=True))

    # Стрілки розмірів t_on та t_off
    frags.append(line(gx + 20, gy + gh + 22, gx + 280, gy + gh + 22, color=POS, sw=1.5))
    frags.append(line(gx + 20, gy + gh + 15, gx + 20, gy + gh + 29, color=POS, sw=1.5))
    frags.append(line(gx + 280, gy + gh + 15, gx + 280, gy + gh + 29, color=POS, sw=1.5))
    frags.append(text(gx + 150, gy + gh + 38, "Активний час t_on (наприклад, 15 мс)", size=12, color=POS, bold=True))

    frags.append(line(gx + 280, gy + gh + 22, gx + gw, gy + gh + 22, color=NEG, sw=1.5))
    frags.append(line(gx + gw, gy + gh + 15, gx + gw, gy + gh + 29, color=NEG, sw=1.5))
    frags.append(text(gx + 500, gy + gh + 38, "Глибокий сон t_off (наприклад, 60 с або 15 хв)", size=12, color=NEG, bold=True))

    frags.append(line(gx + 20, gy + gh + 60, gx + gw, gy + gh + 60, color=INK, sw=1.5))
    frags.append(line(gx + 20, gy + gh + 53, gx + 20, gy + gh + 67, color=INK, sw=1.5))
    frags.append(line(gx + gw, gy + gh + 53, gx + gw, gy + gh + 67, color=INK, sw=1.5))
    frags.append(text(gx + 380, gy + gh + 77, "Повний період циклу: T_period = t_on + t_off", size=13, color=INK, bold=True))

    box_act = fitbox(gx + 340, gy + 15, 185, 48, "Активний заряд:\nQ_on = ∫ I_on(t) dt", size=12, fill="#fff1f2", stroke=POS)
    frags.append(box_act)

    box_slp = fitbox(gx + 540, gy + 15, 185, 48, "Сплячий заряд:\nQ_off = I_sleep · t_off", size=12, fill="#eff6ff", stroke=NEG)
    frags.append(box_slp)

    return render(os.path.join(IMG_DIR, "duty-cycle-phases.svg"), w, h, *frags)


# ── 2. Подійне пробудження проти періодичного опитування (event-vs-polling.svg) ─
def make_event_vs_polling():
    w, h = 880, 400
    frags = []

    # Верхня панель: Періодичне опитування
    p1_y = 50
    frags.append(rect(40, p1_y, 800, 140, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(55, p1_y + 25, "1. Періодичне опитування (Periodic Polling за RTC таймером)", size=13, color=INK, bold=True, anchor="start"))

    t1_y = p1_y + 95
    frags.append(arrow(60, t1_y, 820, t1_y, color=LINE, sw=1.5))
    frags.append(text(825, t1_y + 4, "t", size=12, bold=True, anchor="start"))

    polling_ticks = [120, 260, 400, 540, 680]
    for i, tx in enumerate(polling_ticks):
        frags.append(rect(tx, t1_y - 35, 16, 35, fill="#fee2e2", stroke=POS, sw=1.2, rx=2))
        frags.append(text(tx + 8, t1_y - 42, f"T{i+1}", size=10, color=POS, bold=True))
        if i in [0, 1, 3, 4]:
            frags.append(text(tx + 8, t1_y + 16, "без змін", size=9, color=MUTED))

    ev_x = 310
    frags.append(line(ev_x, t1_y - 50, ev_x, t1_y + 5, color=FIELD, sw=2, dash="3,3"))
    frags.append(circle(ev_x, t1_y, 4, fill=FIELD, stroke=FIELD))
    frags.append(text(ev_x, t1_y - 55, "Подія (удар / поріг)", size=11, color=FIELD, bold=True))

    frags.append(arrow(ev_x, t1_y - 20, 400, t1_y - 20, color="#d97706", sw=1.5))
    frags.append(text((ev_x + 400) / 2, t1_y - 26, "Затримка доставки (Latency)", size=10, color="#d97706", bold=True))
    frags.append(text(408, t1_y + 16, "передача!", size=9, color=FIELD, bold=True))


    # Нижня панель: Подійне пробудження
    p2_y = 215
    frags.append(rect(40, p2_y, 800, 150, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(55, p2_y + 25, "2. Асинхронне подійне пробудження (Asynchronous EXTI / Threshold Interrupt)", size=13, color=INK, bold=True, anchor="start"))

    t2_y = p2_y + 95
    frags.append(arrow(60, t2_y, 820, t2_y, color=LINE, sw=1.5))
    frags.append(text(825, t2_y + 4, "t", size=12, bold=True, anchor="start"))

    frags.append(text(180, t2_y - 15, "Глибокий сон (I_sleep ~ 2 мкА)", size=11, color=NEG, bold=True))
    frags.append(line(60, t2_y - 2, ev_x, t2_y - 2, color=NEG, sw=2.5))

    frags.append(line(ev_x, t2_y - 50, ev_x, t2_y + 5, color=FIELD, sw=2, dash="3,3"))
    frags.append(circle(ev_x, t2_y, 4, fill=FIELD, stroke=FIELD))
    frags.append(text(ev_x, t2_y - 55, "Подія (EXTI пін)", size=11, color=FIELD, bold=True))

    frags.append(rect(ev_x + 2, t2_y - 45, 20, 45, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=2))
    frags.append(text(ev_x + 12, t2_y - 52, "Миттєва передача", size=10, color=FIELD, bold=True))
    frags.append(text(ev_x + 12, t2_y + 18, "Затримка < 5 мс", size=10, color=FIELD))

    hb_x = 680
    frags.append(rect(hb_x, t2_y - 25, 14, 25, fill="#e0e7ff", stroke=NEG, sw=1.2, rx=2))
    frags.append(text(hb_x + 7, t2_y - 32, "Heartbeat", size=10, color=NEG, bold=True))
    frags.append(text(hb_x + 7, t2_y + 18, "контроль зв'язку (1 раз на добу)", size=9, color=MUTED))

    frags.append(line(ev_x + 22, t2_y - 2, 820, t2_y - 2, color=NEG, sw=2.5))

    return render(os.path.join(IMG_DIR, "event-vs-polling.svg"), w, h, *frags)


# ── 3. Крива насичення закону шпаруватості (saturation-curve.svg) ─────────────
def make_saturation_curve():
    w, h = 880, 440
    frags = []

    gx, gy, gw, gh = 90, 50, 730, 310
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=4))

    # Осі
    frags.append(arrow(gx, gy + gh, gx + gw + 30, gy + gh, color=INK, sw=1.8))
    frags.append(arrow(gx, gy + gh, gx, gy - 25, color=INK, sw=1.8))
    frags.append(text(gx + gw + 35, gy + gh + 4, "Період циклу T (секунди / хвилини)", size=12, bold=True, anchor="start"))
    frags.append(text(gx - 10, gy - 30, "Середній струм I_avg", size=12, bold=True, anchor="end"))

    # Сітка по Y
    y_1000 = gy + 30
    y_100  = gy + 110
    y_10   = gy + 200
    y_floor = gy + gh - 40 # 2 мкА (I_sleep)

    frags.append(line(gx, y_1000, gx + gw, y_1000, color="#f1f5f9", sw=1, dash="3,3"))
    frags.append(text(gx - 10, y_1000 + 4, "1000 мкА", size=11, color=MUTED, anchor="end"))

    frags.append(line(gx, y_100, gx + gw, y_100, color="#f1f5f9", sw=1, dash="3,3"))
    frags.append(text(gx - 10, y_100 + 4, "100 мкА", size=11, color=MUTED, anchor="end"))

    frags.append(line(gx, y_10, gx + gw, y_10, color="#f1f5f9", sw=1, dash="3,3"))
    frags.append(text(gx - 10, y_10 + 4, "10 мкА", size=11, color=MUTED, anchor="end"))

    # Асимптотична підлога I_sleep
    frags.append(line(gx, y_floor, gx + gw, y_floor, color=NEG, sw=2, dash="5,5"))
    frags.append(text(gx - 10, y_floor + 4, "I_sleep = 2 мкА", size=11, color=NEG, bold=True, anchor="end"))
    frags.append(text(gx + gw - 10, y_floor - 8, "Асимптотична межа: I_avg → I_sleep при T → ∞", size=11, color=NEG, anchor="end"))

    # Мітки по X
    x_1s   = gx + 50
    x_10s  = gx + 170
    x_1m   = gx + 300
    x_15m  = gx + 460
    x_1h   = gx + 590
    x_24h  = gx + 700

    x_ticks = [(x_1s, "1 с"), (x_10s, "10 с"), (x_1m, "1 хв"), (x_15m, "15 хв"), (x_1h, "1 год"), (x_24h, "24 год")]
    for tx, lbl in x_ticks:
        frags.append(line(tx, gy + gh - 5, tx, gy + gh + 5, color=LINE, sw=1.2))
        frags.append(text(tx, gy + gh + 20, lbl, size=11, color=INK))

    # Зони
    frags.append(rect(gx + 30, gy + 10, 420, gh - 20, fill="#ecfdf5", stroke="none"))
    frags.append(text(gx + 210, gy + 30, "ЗОНА СТРІМКОЇ ЕКОНОМІЇ", size=12, color=FIELD, bold=True))
    frags.append(text(gx + 210, gy + 48, "ΔT дає падіння I_avg у десятки разів", size=10, color=FIELD))

    frags.append(rect(gx + 450, gy + 10, 270, gh - 20, fill="#fef2f2", stroke="none"))
    frags.append(text(gx + 585, gy + 30, "ЗОНА НАСИЧЕННЯ (НЕМІЧНИЙ ВИГРАШ)", size=12, color=POS, bold=True))
    frags.append(text(gx + 585, gy + 48, "Струм сну I_sleep домінує (90–99% заряду)", size=10, color=POS))

    # Точка перегину
    knee_x = gx + 450
    knee_y = y_floor - 15
    frags.append(circle(knee_x, knee_y, 6, fill=POS, stroke=INK, sw=2))
    frags.append(line(knee_x, gy + 10, knee_x, gy + gh, color=POS, sw=1.5, dash="4,4"))
    frags.append(text(knee_x, gy + 75, "Точка перегину T_sat (~15 хв)", size=11, color=POS, bold=True))

    # Крива
    path_d = f"M {gx+40} {gy+20} Q {gx+120} {gy+130} {gx+250} {gy+220} T {knee_x} {knee_y} Q {gx+580} {y_floor-5} {gx+710} {y_floor-2}"
    frags.append(f'<path d="{path_d}" fill="none" stroke="{POS}" stroke-width="3.5"/>')

    # Підписи точок
    frags.append(circle(x_1s, gy + 30, 4, fill=POS, stroke=LINE))
    frags.append(text(x_1s + 15, gy + 30, "1500 мкА", size=10, color=INK, anchor="start"))

    frags.append(circle(x_1m, gy + 180, 4, fill=POS, stroke=LINE))
    frags.append(text(x_1m + 15, gy + 175, "27 мкА", size=10, color=INK, anchor="start"))

    frags.append(circle(x_15m, knee_y, 4, fill=POS, stroke=LINE))
    frags.append(text(x_15m + 15, knee_y - 12, "3.6 мкА", size=10, color=INK, anchor="start"))

    frags.append(circle(x_24h, y_floor - 2, 4, fill=POS, stroke=LINE))
    frags.append(text(x_24h - 15, y_floor - 12, "2.02 мкА", size=10, color=INK, anchor="end"))

    return render(os.path.join(IMG_DIR, "saturation-curve.svg"), w, h, *frags)


if __name__ == "__main__":
    print("Генерація SVG-фігур для теми shparuvatist-roboty...")
    make_duty_cycle_phases()
    make_event_vs_polling()
    make_saturation_curve()
    print("Усі фігури згенеровано успішно.")

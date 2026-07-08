# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «Програмований DC-DC buck-boost (DPS/DPH)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Чотириключовий buck-boost: H-міст із котушкою ─────────────────────────
def fig_topology():
    W, H = 900, 470
    f = [text(W / 2, 30, "Чотири ключі й одна котушка: як модуль і знижує, і підвищує",
              size=16, bold=True)]

    # рейки живлення
    top_y = 110          # плюсова рейка входу/виходу зверху
    bot_y = 360          # спільна земля знизу
    f.append(line(70, bot_y, W - 70, bot_y, color=INK, sw=2.2))
    f.append(text(80, bot_y + 22, "спільна земля (GND)", size=11, color=MUTED, anchor="start"))

    # ліве плече: вхід + ключі S1 (верх), S2 (низ)
    lx = 250
    # вхідні клеми
    f.append(text(140, top_y - 10, "ВХІД 6–50 В", size=12, bold=True, color=POS, anchor="middle"))
    f.append(line(96, top_y, lx, top_y, color=POS, sw=2.2))
    f.append(plus(96, top_y))
    # S1 верхній ключ лівого плеча
    s1y = 165
    b, bw, bh = textbox(lx, s1y, "S1", size=13, bold=True, fill="#fdecea", stroke=POS, min_w=54)
    f.append(b)
    # S2 нижній ключ лівого плеча
    s2y = 300
    b, bw, bh = textbox(lx, s2y, "S2", size=13, bold=True, fill="#eef2f8", stroke=INK, min_w=54)
    f.append(b)

    # котушка посередині (між серединами плечей)
    midL = (lx, (s1y + s2y) / 2)     # вузол лівого плеча (між S1 і S2)
    rx = 650
    s3y = 165
    s4y = 300
    midR = (rx, (s3y + s4y) / 2)     # вузол правого плеча
    # горизонтальна лінія з котушкою
    coil_y = midL[1]
    f.append(line(lx, coil_y, 400, coil_y, color=INK, sw=2.0))
    # символ котушки — три дуги
    cxs = 410
    arcs = ""
    for i in range(4):
        cx0 = cxs + i * 26
        arcs += ('<path d="M %.0f %.0f q 13 -22 26 0" fill="none" stroke="%s" '
                 'stroke-width="2.2"/>' % (cx0, coil_y, INK))
    f.append(arcs)
    f.append(text((cxs + 52), coil_y - 26, "L", size=14, bold=True))
    f.append(text((cxs + 52), coil_y - 10, "котушка", size=10, color=MUTED))
    f.append(line(cxs + 4 * 26, coil_y, rx, coil_y, color=INK, sw=2.0))

    # праве плече: ключі S3 (верх), S4 (низ) + вихід
    b, bw, bh = textbox(rx, s3y, "S3", size=13, bold=True, fill="#eef2f8", stroke=INK, min_w=54)
    f.append(b)
    b, bw, bh = textbox(rx, s4y, "S4", size=13, bold=True, fill="#fdecea", stroke=POS, min_w=54)
    f.append(b)
    # вихідні клеми (лінія кінчається ДО «+», щоб не різати його напис)
    f.append(text(W - 130, top_y - 10, "ВИХІД 0–50 В", size=12, bold=True, color=POS, anchor="middle"))
    f.append(line(rx, top_y, W - 108, top_y, color=POS, sw=2.2))
    f.append(plus(W - 96, top_y))

    # верхня рейка з'єднує входи ключів S1 (до входу) і S3 (до виходу)
    f.append(line(lx, top_y, lx, s1y - bh / 2, color=POS, sw=2.0))
    f.append(line(rx, top_y, rx, s3y - bh / 2, color=POS, sw=2.0))
    # нижні ключі до землі
    f.append(line(lx, s2y + bh / 2, lx, bot_y, color=INK, sw=2.0))
    f.append(line(rx, s4y + bh / 2, rx, bot_y, color=INK, sw=2.0))
    # плечі до котушкового вузла
    f.append(line(lx, s1y + bh / 2, lx, coil_y, color=INK, sw=2.0))
    f.append(line(rx, s3y + bh / 2, rx, coil_y, color=INK, sw=2.0))

    # дві підписані рамки-режими внизу (рознесені, не перекривають схему)
    b, bw, bh = textbox(250, H - 42,
                        "ЗНИЖУЄ: ліве плече комутує (S1↔S2),\nправе тримає S3 замкнутим — звичайний buck",
                        size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    b, bw, bh = textbox(650, H - 42,
                        "ПІДВИЩУЄ: ліве плече тримає S1 замкнутим,\nправе плече комутує (S3↔S4) — boost",
                        size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "topology.svg"), W, H, *f)


# ── 2. Розводка: джерело → модуль → навантаження, і хост по UART ──────────────
def fig_wiring():
    W, H = 920, 500
    f = [text(W / 2, 30, "Що куди: живлення на ВХІД, споживач на ВИХІД, керування по UART",
              size=15.5, bold=True)]

    # ── модуль у центрі ──
    mx, my, mw, mh = 350, 90, 220, 300
    f.append(rect(mx, my, mw, mh, fill="#fafbfc", stroke=INK, sw=1.9, rx=12))
    f.append(text(mx + mw / 2, my + 26, "DPS / DPH", size=14, bold=True))
    f.append(text(mx + mw / 2, my + 44, "модуль", size=10.5, color=MUTED))
    # кольоровий LCD-натяк
    f.append(rect(mx + 30, my + 58, mw - 60, 54, fill="#0b1f3a", stroke=MUTED, sw=1.2, rx=4))
    f.append(text(mx + mw / 2, my + 80, "12.00 V", size=13, bold=True, color="#39d98a"))
    f.append(text(mx + mw / 2, my + 98, "0.512 A", size=11, color="#f6c453"))

    # клеми входу (ліворуч зверху)
    in_p_y = my + 150
    in_n_y = my + 178
    f.append(text(mx + 10, in_p_y - 16, "IN", size=11, bold=True, color=POS, anchor="start"))
    f.append(plus(mx + 16, in_p_y))
    f.append(text(mx + 30, in_p_y + 4, "IN+", size=10.5, bold=True, color=POS, anchor="start"))
    f.append(minus(mx + 16, in_n_y))
    f.append(text(mx + 30, in_n_y + 4, "IN−", size=10.5, bold=True, color=NEG, anchor="start"))

    # клеми виходу (праворуч зверху)
    out_p_y = my + 150
    out_n_y = my + 178
    f.append(text(mx + mw - 10, out_p_y - 16, "OUT", size=11, bold=True, color=POS, anchor="end"))
    f.append(plus(mx + mw - 16, out_p_y))
    f.append(text(mx + mw - 30, out_p_y + 4, "OUT+", size=10.5, bold=True, color=POS, anchor="end"))
    f.append(minus(mx + mw - 16, out_n_y))
    f.append(text(mx + mw - 30, out_n_y + 4, "OUT−", size=10.5, bold=True, color=NEG, anchor="end"))

    # гребінка зв'язку знизу модуля (TTL UART): три площадки, підписи — ЛІВОРУЧ від блоку,
    # щоб дроти до хоста йшли вниз повз написи, а не крізь них
    com_y = my + mh - 30
    f.append(text(mx + 8, com_y + 4, "TX", size=9, color=INK, bold=True, anchor="end"))
    f.append(text(mx + 8, com_y + 18, "RX", size=9, color=INK, bold=True, anchor="end"))
    f.append(text(mx + 8, com_y + 32, "GND", size=9, color=INK, bold=True, anchor="end"))
    f.append(text(mx + mw / 2, com_y - 12, "гребінка UART · TTL 3.3 В", size=9.5, color=MUTED))
    pad_x = []
    for i in range(3):
        cxp = mx + mw / 2 - 34 + i * 34
        pad_x.append(cxp)
        f.append(circle(cxp, com_y + 10, 6, fill="#fdf6e3", stroke=INK, sw=1.4))

    # ── джерело ліворуч ──
    sx, sy, sw_, sh = 60, 120, 150, 120
    f.append(rect(sx, sy, sw_, sh, fill="#fdecea", stroke=POS, sw=1.7, rx=10))
    f.append(text(sx + sw_ / 2, sy + 30, "ДЖЕРЕЛО", size=12, bold=True, color=POS))
    f.append(text(sx + sw_ / 2, sy + 52, "БЖ / акумулятор", size=10, color=INK))
    f.append(text(sx + sw_ / 2, sy + 74, "6–50 В, ≥ вхідний струм", size=9.5, color=MUTED))
    f.append(text(sx + sw_ / 2, sy + 96, "!! вище виходу для DPS", size=9.5, color=POS, bold=True))
    # дроти джерело → IN
    f.append(line(sx + sw_, sy + 40, mx + 6, in_p_y, color=POS, sw=2.2))
    f.append(line(sx + sw_, sy + 88, mx + 6, in_n_y, color=NEG, sw=2.2))

    # ── навантаження праворуч ──
    ldx, ldy, ldw, ldh = W - 210, 120, 150, 120
    f.append(rect(ldx, ldy, ldw, ldh, fill="#eef6ef", stroke=FIELD, sw=1.7, rx=10))
    f.append(text(ldx + ldw / 2, ldy + 30, "НАВАНТАЖЕННЯ", size=11.5, bold=True, color=FIELD))
    f.append(text(ldx + ldw / 2, ldy + 52, "плата / мотор /", size=10, color=INK))
    f.append(text(ldx + ldw / 2, ldy + 70, "заряд акумулятора", size=10, color=INK))
    f.append(text(ldx + ldw / 2, ldy + 96, "струм ≤ ліміту CC", size=9.5, color=MUTED))
    # дроти OUT → навантаження
    f.append(line(mx + mw - 6, out_p_y, ldx, ldy + 40, color=POS, sw=2.2))
    f.append(line(mx + mw - 6, out_n_y, ldx, ldy + 88, color=NEG, sw=2.2))

    # ── хост-МК знизу (по UART/USB) ──
    hx, hy, hw, hh = mx + mw / 2 - 95, H - 74, 190, 56
    f.append(rect(hx, hy, hw, hh, fill="#eef2f8", stroke=NEG, sw=1.7, rx=10))
    f.append(text(hx + hw / 2, hy + 23, "ХОСТ по Modbus RTU", size=11, bold=True, color=NEG))
    f.append(text(hx + hw / 2, hy + 41, "ПК-USB / ESP32 / Arduino", size=9.5, color=INK))
    # три лінії від площадок униз до хоста (перехрест TX↔RX)
    f.append(line(pad_x[0], com_y + 16, hx + hw / 2 + 14, hy, color=INK, sw=1.8))
    f.append(line(pad_x[1], com_y + 16, hx + hw / 2 - 14, hy, color=INK, sw=1.8))
    f.append(line(pad_x[2], com_y + 16, hx + hw / 2, hy, color=MUTED, sw=1.6, dash="4 3"))
    f.append(text(hx + hw + 8, (com_y + hy) / 2 + 14, "TX↔RX", size=9, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 3. Мапа регістрів: дві ролі комірок (пиши накази / читай вимір) ──────────
def fig_registers():
    W, H = 900, 470
    f = [text(W / 2, 32, "Регістри = таблиця комірок: у ліві ПИШЕШ наказ, з правих ЧИТАЄШ стан",
              size=15, bold=True)]

    # прилад-коробка по центру
    mx, my, mw, mh = 360, 78, 180, 320
    f.append(rect(mx, my, mw, mh, fill="#fafbfc", stroke=INK, sw=1.9, rx=12))
    f.append(text(mx + mw / 2, my + 26, "DPS / DPH", size=13.5, bold=True))
    f.append(text(mx + mw / 2, my + 44, "таблиця регістрів", size=10, color=MUTED))

    # ── ліва колонка: комірки-накази (WRITE у прилад) ──
    write_rows = [
        ("0x00", "U-SET", "задати U"),
        ("0x01", "I-SET", "задати I"),
        ("0x09", "ON/OFF", "вмикач"),
    ]
    lx = 70
    ly0 = 120
    dy = 74
    f.append(text(lx + 90, ly0 - 34, "ПИШЕШ (наказ)", size=12, bold=True, color=POS))
    for k, (addr, name, note) in enumerate(write_rows):
        cy = ly0 + k * dy
        b, bw, bh = textbox(lx + 90, cy, "%s  %s\n%s" % (addr, name, note),
                            size=11, bold=False, fill="#fdecea", stroke=POS, min_w=180)
        f.append(b)
        # стрілка від комірки У прилад
        f.append(arrow(lx + 90 + bw / 2, cy, mx, cy, color=POS, sw=1.9))

    # ── права колонка: комірки-вимір (READ з приладу) ──
    read_rows = [
        ("0x02", "U-OUT", "виміряна U"),
        ("0x03", "I-OUT", "виміряний I"),
        ("0x08", "CV/CC", "режим"),
    ]
    rx = W - 70 - 180
    f.append(text(rx + 90, ly0 - 34, "ЧИТАЄШ (стан)", size=12, bold=True, color=NEG))
    for k, (addr, name, note) in enumerate(read_rows):
        cy = ly0 + k * dy
        b, bw, bh = textbox(rx + 90, cy, "%s  %s\n%s" % (addr, name, note),
                            size=11, bold=False, fill="#eef2f8", stroke=NEG, min_w=180)
        f.append(b)
        # стрілка З приладу У комірку
        f.append(arrow(mx + mw, cy, rx + 90 - bw / 2, cy, color=NEG, sw=1.9))

    # підпис-нагадування про кодування внизу (рознесено, без накладань)
    b, bw, bh = textbox(W / 2, H - 34,
                        "кодування: U × 100  (12.00 В → 1200)     I × 1000  (0.500 А → 500)",
                        size=11, bold=True, fill="#eef6ef", stroke=FIELD, min_w=560)
    f.append(b)

    render(os.path.join(IMG, "registers.svg"), W, H, *f)


if __name__ == "__main__":
    fig_topology()
    fig_wiring()
    fig_registers()
    print("OK: 3 figures ->", IMG)

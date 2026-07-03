# -*- coding: utf-8 -*-
"""Фігури об'єкта «ESP-01S» (catalog/boards/mcu). Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: розпіновка ESP-01S — гребінка 2×4 ──────────────────────────────
# Плата виводить лише 8 ніжок: живлення, скидання, вмикання чипа, дві GPIO
# та пару UART. Показуємо, яка ніжка за що і що вбудовано (12К підтяжки, LED).
def fig_pinout():
    W, H = 760, 470
    parts = []

    # корпус плати по центру
    bx, by, bw, bh = 300, 90, 160, 250
    parts.append(rect(bx, by, bw, bh, fill="#eef2f7", stroke=INK, sw=1.8, rx=8))
    parts.append(text(bx + bw / 2, by - 40, "ESP-01S", 15, INK, "middle", bold=True))
    parts.append(text(bx + bw / 2, by - 22, "чорна плата · 1 МБ флеш", 11, MUTED, "middle"))
    # антена-«меандр» угорі плати (символічно)
    parts.append(text(bx + bw / 2, by + 20, "PCB-антена", 10, FIELD, "middle", bold=True))
    parts.append(line(bx + 18, by + 34, bx + bw - 18, by + 34, color=FIELD, sw=2.0))

    # два стовпці ніжок: ліворуч і праворуч від плати
    # (пари, як на реальній гребінці 2×4)
    left = [
        ("GND",  INK,   "спільна земля"),
        ("GPIO2", NEG,  "GPIO2 + синій LED\n(підтяжка 12К)"),
        ("GPIO0", NEG,  "GPIO0 — вибір режиму\n(підтяжка 12К)"),
        ("RX",   MUTED, "прийом UART (в чип)"),
    ]
    right = [
        ("VCC",  POS,   "живлення 3.3 В\n(НЕ 5 В!)"),
        ("RST",  MUTED, "скидання, активне 0\n(підтяжка 12К)"),
        ("CH_PD", FIELD,"увімкнення чипа\n= 1 завжди (підтяжка 12К)"),
        ("TX",   MUTED, "передача UART (з чипа)"),
    ]
    n = 4
    y0 = by + 70
    step = (bh - 90) / (n - 1)

    for i, (pin, col, desc) in enumerate(left):
        y = y0 + i * step
        parts.append(line(bx, y, bx - 20, y, color=col, sw=2.4))
        parts.append(circle(bx - 20, y, 4, fill=col, stroke=INK, sw=1))
        parts.append(text(bx + 10, y + 4, pin, 12, col, "start", bold=True))
        parts.append(mtext(bx - 30, y - (desc.count("\n")) * 6, desc, 10, INK, "end"))

    for i, (pin, col, desc) in enumerate(right):
        y = y0 + i * step
        parts.append(line(bx + bw, y, bx + bw + 20, y, color=col, sw=2.4))
        parts.append(circle(bx + bw + 20, y, 4, fill=col, stroke=INK, sw=1))
        parts.append(text(bx + bw - 10, y + 4, pin, 12, col, "end", bold=True))
        parts.append(mtext(bx + bw + 30, y - (desc.count("\n")) * 6, desc, 10, INK, "start"))

    render(os.path.join(IMG, "pinout.svg"), W, H, *parts,
           title="ESP-01S: вісім виводів гребінки 2×4")


# ── Фігура 2: як зайти в режим прошивки (стан ніжок при скиданні) ────────────
# Крихта всієї плати: GPIO0 у момент скидання вирішує — бігти прошивку чи
# приймати нову. GPIO0=0 при RST → завантажувач; GPIO0=1 → звичайний старт.
def fig_bootmode():
    W, H = 760, 340
    parts = []

    # дві колонки-режими
    def mode(cx, title, g0, tint, edge, note):
        col = []
        col.append(rect(cx - 150, 70, 300, 210, fill=tint, stroke=edge, sw=1.8, rx=10))
        col.append(text(cx, 96, title, 14, edge, "middle", bold=True))
        col.append(mtext(cx, 128,
                         "у момент RST↓:\nGPIO0 = %s\nCH_PD = 1  ·  GPIO2 = 1" % g0,
                         11, INK))
        col.append(mtext(cx, 210, note, 11, INK))
        return col

    parts += mode(220, "Прошивка (bootloader)", "0", "#fdecea", POS,
                  "GPIO0 на землю ПЕРЕД\nскиданням → чип чекає\nнову прошивку по UART")
    parts += mode(560, "Звичайний старт", "1 (вільно)", "#eafaf1", FIELD,
                  "GPIO0 не чіпаємо (підтяжка\n12К тримає 1) → чип біжить\nвашу прошивку з флеші")

    # підказка знизу
    parts.append(fitbox(230, 296, 300, 34,
                        "GPIO2 має лишатися 1 в обох режимах",
                        size=11, fill="#fff8e1", stroke="#f0b429", sw=1.2, color=INK))
    render(os.path.join(IMG, "bootmode.svg"), W, H, *parts,
           title="Що вирішує GPIO0 у мить скидання")


# ── Фігура 3: підключення до USB-UART для прошивки + пастка живлення ─────────
# Мінімальна схема заливки прошивки. Головна пастка — живлення: 3.3 В-вихід
# перехідника не тягне пік Wi-Fi (~300 мА) → бро́унаут; треба окреме 3.3 В
# і конденсатор біля плати.
def fig_wiring():
    W, H = 820, 470
    parts = []

    # два блоки: перехідник (зліва) і плата (справа), на одному рівні
    Lx, Ly, Lw, Lh = 50, 120, 160, 100
    Rx, Ry, Rw, Rh = 590, 110, 180, 120
    parts.append(fitbox(Lx, Ly, Lw, Lh, "USB-UART\nперехідник\n(на 3.3 В!)",
                        size=12, fill="#eef2f7", stroke=INK, sw=1.6, color=INK, bold=True))
    parts.append(fitbox(Rx, Ry, Rw, Rh,
                        "ESP-01S\nпік Wi-Fi ≈ 300 мА\n(короткі сплески)",
                        size=11, fill="#eafaf1", stroke=FIELD, sw=1.8, color=INK, bold=True))

    # ── UART: дві перехрещені лінії між блоками, підписи ПОЗА лініями ─────────
    parts.append(text(400, 108, "TX перехідника → RX плати", 10, NEG, "middle"))
    parts.append(arrow(Lx + Lw, 132, Rx, 132, color=NEG, sw=2.0))
    parts.append(arrow(Rx, 160, Lx + Lw, 160, color=NEG, sw=2.0))
    parts.append(text(400, 182, "TX плати → RX перехідника", 10, NEG, "middle"))

    # ── живлення 3.3 В: рампа знизу до VCC/CH_PD, підпис над лінією з відступом ─
    yPWR = 300
    parts.append(fitbox(320, 380, 190, 62, "окреме 3.3 В\n(≥ 500 мА, напр. AMS1117)",
                        size=11, fill="#fdecea", stroke=POS, sw=1.6, color=INK, bold=True))
    parts.append(text(430, 288, "VCC + CH_PD → 3.3 В", 11, POS, "middle", bold=True))
    parts.append(line(415, 380, 415, yPWR, color=POS, sw=2.2))       # вгору від блока
    parts.append(line(415, yPWR, 660, yPWR, color=POS, sw=2.2))      # горизонталь під підписом
    parts.append(arrow(660, yPWR, 660, Ry + Rh, color=POS, sw=2.2))  # вгору в плату

    # ── конденсатор осторонь праворуч, підпис поза його ніжками ──────────────
    cx = 720
    parts.append(line(660, yPWR, cx, yPWR, color=INK, sw=1.4))
    parts.append(text(cx, yPWR - 14, "‖", 20, INK, "middle", bold=True))
    parts.append(line(cx, yPWR - 4, cx, yPWR + 16, color=INK, sw=1.6))
    parts.append(line(cx, yPWR + 16, 660, yPWR + 16, color=INK, sw=1.6))
    parts.append(mtext(cx + 16, yPWR - 6, "10–100 мкФ\nбіля VCC", 10, INK, "start"))

    # ── спільна земля: нижній контур, підпис у ВІЛЬНОМУ полі під контуром ─────
    yGND = 340
    parts.append(line(130, Ly + Lh, 130, yGND, color=INK, sw=1.8))
    parts.append(line(130, yGND, 680, yGND, color=INK, sw=1.8))
    parts.append(line(680, yGND, 680, Ry + Rh, color=INK, sw=1.8))
    parts.append(text(230, yGND + 20, "спільна земля всіх трьох", 10, INK, "middle"))

    render(os.path.join(IMG, "wiring.svg"), W, H, *parts,
           title="Прошивка ESP-01S: UART + окреме живлення")


# ── Фігура 4 (для proj-blink-wifi): життєвий цикл заливки в часі ─────────────
# Не статичні стани, а ПОСЛІДОВНІСТЬ у часі: три фази (вхід у завантажувач →
# esptool пише → запуск), а під ними — «доріжка» рівня GPIO0, щоб видно було,
# коли ніжка на землі, а коли вільна.
def fig_flashcycle():
    W, H = 860, 380
    parts = []

    # три фази як смуги на осі часу
    phases = [
        (60,  250, "#fdecea", POS,   "1 · Вхід у завантажувач",
         "GPIO0 → земля,\nкоротко RST → земля\nй відпустити"),
        (330, 230, "#eef2f7", NEG,   "2 · esptool пише флеш",
         "esptool write_flash\n0x0 firmware.bin\n@ 115200 бод"),
        (580, 220, "#eafaf1", FIELD, "3 · Запуск прошивки",
         "GPIO0 вільно,\nще одне RST →\nчип біжить код"),
    ]
    py, ph = 70, 120
    for px, pw, tint, edge, title, note in phases:
        parts.append(rect(px, py, pw, ph, fill=tint, stroke=edge, sw=1.8, rx=10))
        parts.append(text(px + pw / 2, py + 26, title, 13, edge, "middle", bold=True))
        parts.append(mtext(px + pw / 2, py + 52, note, 11, INK))

    # вісь часу зі стрілкою під смугами
    ty = py + ph + 46
    parts.append(arrow(50, ty, W - 30, ty, color=INK, sw=2.0))
    parts.append(text(W - 30, ty - 12, "час", 11, MUTED, "end", italic=True))

    # доріжка GPIO0: рівень 0 під фазами 1–2, 1 під фазою 3
    gy0, gy1 = ty + 70, ty + 34   # низ = «0», верх = «1»
    parts.append(text(40, (gy0 + gy1) / 2, "GPIO0", 11, INK, "end", bold=True))
    # 0 (притиснуто) від початку фази 1 до кінця фази 2
    x_lo_a, x_lo_b = 60, 330 + 230
    parts.append(line(x_lo_a, gy0, x_lo_b, gy0, color=POS, sw=3.0))
    parts.append(text((x_lo_a + x_lo_b) / 2, gy0 + 18, "0 (на землі)", 10, POS, "middle", bold=True))
    # фронт угору й рівень 1 під фазою 3
    parts.append(line(x_lo_b, gy0, x_lo_b, gy1, color=INK, sw=2.0, dash="4,3"))
    x_hi_a, x_hi_b = x_lo_b, 580 + 220
    parts.append(line(x_hi_a, gy1, x_hi_b, gy1, color=FIELD, sw=3.0))
    parts.append(text((x_hi_a + x_hi_b) / 2, gy1 - 8, "1 (вільно)", 10, FIELD, "middle", bold=True))

    render(os.path.join(IMG, "flashcycle.svg"), W, H, *parts,
           title="Заливка ESP-01S у часі: три фази й рівень GPIO0")


if __name__ == "__main__":
    fig_pinout()
    fig_bootmode()
    fig_wiring()
    fig_flashcycle()
    print("OK: fig_pinout, fig_bootmode, fig_wiring, fig_flashcycle ->", IMG)

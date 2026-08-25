# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «TOF10120 — лазерний далекомір».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Що всередині: Sharp-давач (VCSEL+SPAD+таймер) + власний МК → два канали ──
def fig_inside():
    W, H = 940, 500
    f = [text(W / 2, 32, "Усередині TOF10120: давач Sharp + власний мікроконтролер",
              size=17, bold=True)]

    # блок оптики Sharp зліва
    ox, oy, ow, oh = 55, 96, 220, 320
    f.append(rect(ox, oy, ow, oh, fill="#fafbfc", stroke=MUTED, sw=1.7, rx=12))
    f.append(text(ox + ow / 2, oy + 26, "давач Sharp (GP2AP)", size=12, bold=True))
    # VCSEL
    f.append(rect(ox + 26, oy + 56, ow - 52, 64, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    f.append(text(ox + ow / 2, oy + 82, "VCSEL-лазер 940 нм", size=11, color=POS, bold=True))
    f.append(text(ox + ow / 2, oy + 100, "невидимий спалах", size=9.5, color=MUTED))
    # SPAD
    f.append(rect(ox + 26, oy + 138, ow - 52, 64, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=8))
    f.append(text(ox + ow / 2, oy + 164, "матриця SPAD", size=11, color=NEG, bold=True))
    f.append(text(ox + ow / 2, oy + 182, "лічить окремі фотони", size=9.5, color=MUTED))
    # таймер
    f.append(rect(ox + 26, oy + 220, ow - 52, 68, fill=BG, stroke=INK, sw=1.5, rx=8))
    f.append(text(ox + ow / 2, oy + 246, "таймер: час туди й назад", size=10, bold=True))
    f.append(text(ox + ow / 2, oy + 266, "→ сира відстань", size=9.5, color=MUTED))

    # МК у центрі
    cx, cy, cw2, ch2 = 360, 156, 200, 200
    f.append(rect(cx, cy, cw2, ch2, fill="#eef6ef", stroke=FIELD, sw=1.9, rx=12))
    f.append(text(cx + cw2 / 2, cy + 32, "власний МК модуля", size=12, bold=True, color=FIELD))
    f.append(text(cx + cw2 / 2, cy + 74, "фільтрує й усереднює,", size=10, color=INK))
    f.append(text(cx + cw2 / 2, cy + 94, "перекладає в міліметри,", size=10, color=INK))
    f.append(text(cx + cw2 / 2, cy + 114, "тримає налаштування,", size=10, color=INK))
    f.append(text(cx + cw2 / 2, cy + 134, "розуміє ASCII-команди", size=10, color=INK))
    # стрілка оптика → МК
    f.append(arrow(ox + ow, oy + oh / 2, cx, cy + ch2 / 2, color=INK, sw=2.0))

    # два канали виводу праворуч
    i2c_y = 168
    uart_y = 320
    f.append(rect(650, i2c_y - 36, 240, 72, fill=BG, stroke=NEG, sw=1.7, rx=10))
    f.append(text(770, i2c_y - 14, "I2C  (адреса 0x52)", size=11.5, bold=True, color=NEG))
    f.append(text(770, i2c_y + 6, "регістр 0x00 → 2 байти", size=10, color=INK))
    f.append(text(770, i2c_y + 24, "старший · молодший = мм", size=9, color=MUTED))

    f.append(rect(650, uart_y - 36, 240, 72, fill=BG, stroke=POS, sw=1.7, rx=10))
    f.append(text(770, uart_y - 14, "UART  9600 8N1", size=11.5, bold=True, color=POS))
    f.append(text(770, uart_y + 6, "текст ASCII: «748mm»", size=10, color=INK))
    f.append(text(770, uart_y + 24, "сам шле + приймає команди", size=9, color=MUTED))

    f.append(arrow(cx + cw2, cy + 44, 650, i2c_y, color=NEG, sw=2.0))
    f.append(arrow(cx + cw2, cy + ch2 - 44, 650, uart_y, color=POS, sw=2.0))

    b, bw, bh = textbox(W / 2, H - 26,
                        "МК ховає фізику: назовні — готові міліметри двома каналами, і UART ще й слухає команди налаштування",
                        size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "inside.svg"), W, H, *f)


# ── 2. Розводка пін-у-пін: порядок ніжок як у даташиті ────────────────────────
def fig_wiring():
    W, H = 940, 520
    f = [text(W / 2, 30, "Шість контактів: живлення + два способи спілкування",
              size=17, bold=True)]

    # модуль ліворуч із шістьма кольоровими виводами (порядок даташита)
    mx, my, mw, mh = 60, 92, 210, 356
    f.append(rect(mx, my, mw, mh, fill="#fafbfc", stroke=INK, sw=1.8, rx=12))
    f.append(text(mx + mw / 2, my + 26, "TOF10120", size=13, bold=True))
    f.append(text(mx + mw / 2, my + 44, "6-піновий роз'єм", size=9.5, color=MUTED))

    pins = [
        ("① GND", "чорний", INK, my + 84),
        ("② VDD", "червоний", POS, my + 128),
        ("③ RXD", "жовтий", "#b8860b", my + 172),
        ("④ TXD", "білий", MUTED, my + 216),
        ("⑤ SDA", "синій", NEG, my + 260),
        ("⑥ SCL", "зелений", FIELD, my + 304),
    ]
    for nm, colour, col, y in pins:
        f.append(circle(mx + mw - 18, y, 7, fill=col, stroke=col, sw=1))
        f.append(text(mx + mw - 36, y + 5, nm, size=11.5, bold=True, color=col, anchor="end"))
        f.append(text(mx + 16, y + 5, colour, size=9.5, color=MUTED, anchor="start"))

    # МК праворуч
    kx, ky, kw, kh = 660, 92, 220, 356
    f.append(rect(kx, ky, kw, kh, fill="#eef2f8", stroke=INK, sw=1.8, rx=12))
    f.append(text(kx + kw / 2, ky + 26, "Мікроконтролер", size=12.5, bold=True))
    f.append(text(kx + kw / 2, ky + 44, "ESP32 / Arduino / STM32", size=9, color=MUTED))
    mk = [
        ("GND", INK, ky + 84),
        ("3V3 / 5V", POS, ky + 128),
        ("TX →", "#b8860b", ky + 172),
        ("← RX", MUTED, ky + 216),
        ("SDA", NEG, ky + 260),
        ("SCL", FIELD, ky + 304),
    ]
    for nm, col, y in mk:
        f.append(text(kx + 18, y + 5, nm, size=11.5, bold=True, color=col, anchor="start"))

    # проводка: живлення (2)
    f.append(line(mx + mw, my + 84, kx, ky + 84, color=INK, sw=1.6, dash="5 4"))    # GND→GND
    f.append(line(mx + mw, my + 128, kx, ky + 128, color=POS, sw=2.2))              # VDD→3V3/5V

    # UART-хрест: RXD модуля ← TX МК; TXD модуля → RX МК
    f.append(line(mx + mw, my + 172, kx, ky + 172, color="#b8860b", sw=2.2))        # RXD(мод)–TX(МК)
    f.append(line(mx + mw, my + 216, kx, ky + 216, color=MUTED, sw=2.2))            # TXD(мод)–RX(МК)
    f.append(text((mx + mw + kx) / 2, my + 150, "UART: навхрест TX↔RX", size=11, color="#b8860b", bold=True))

    # I2C-пара
    f.append(line(mx + mw, my + 260, kx, ky + 260, color=NEG, sw=2.2))
    f.append(line(mx + mw, my + 304, kx, ky + 304, color=FIELD, sw=2.2))
    f.append(text((mx + mw + kx) / 2, my + 336, "I2C: SDA↔SDA, SCL↔SCL", size=11, color=NEG, bold=True))

    b, bw, bh = textbox(W / 2, H - 24,
                        "живлення завжди; далі ОБИРАЙ одне — або пара UART (TX↔RX навхрест), або пара I2C (SDA/SCL прямо)",
                        size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 3. ASCII-протокол: команда «r/s + число + #» → відповідь ───────────────────
def fig_commands():
    W, H = 940, 500
    f = [text(W / 2, 30, "UART-команди: питаєш рядком, модуль відповідає рядком",
              size=17, bold=True)]

    # рядок команди по центру як стрічка символів
    cells = [("s", "set", FIELD), ("3", "№ параметра", INK),
             ("-", "роздільник", MUTED), ("1", "значення", NEG), ("#", "кінець", POS)]
    n = len(cells)
    cw, ch = 96, 62
    x0 = (W - n * cw) / 2
    y0 = 80
    f.append(text(W / 2, y0 - 14, "МК шле у ніжку RXD модуля  →", size=11, color=MUTED))
    for i, (ch_s, role, col) in enumerate(cells):
        x = x0 + i * cw
        f.append(rect(x, y0, cw - 8, ch, fill=BG, stroke=col, sw=1.8, rx=8))
        f.append(text(x + (cw - 8) / 2, y0 + 32, ch_s, size=22, bold=True, color=col))
        f.append(text(x + (cw - 8) / 2, y0 + 52, role, size=9, color=MUTED))
    # підпис під стрічкою — що означає ця команда
    f.append(text(W / 2, y0 + ch + 26, "«s3-1#» = встав режим 1 (сира, миттєва відстань)",
                  size=12, bold=True, color=INK))
    # стрілка вниз до відповіді
    f.append(arrow(W / 2, y0 + ch + 40, W / 2, y0 + ch + 70, color=INK, sw=2))
    f.append(text(W / 2, y0 + ch + 92, "модуль повертає у ніжку TXD:  ok", size=12, bold=True, color=FIELD))

    # таблиця найкорисніших команд (двома колонками рамок)
    ty = 300
    left = [
        ("r6#", "→ L=0748", "прочитати відстань (мм)"),
        ("s3-1#", "→ ok", "0 = згладжена · 1 = сира"),
        ("s5-1#", "→ ok", "0 = сам шле · 1 = лише на запит"),
    ]
    right = [
        ("s1+05#", "→ ok", "зсув +5 мм (юстування нуля)"),
        ("s2-500#", "→ ok", "інтервал видачі 500 мс"),
        ("s7-085#", "→ ok", "нова I2C-адреса (тут 0x55)"),
    ]
    cwid, chei, gap = 400, 44, 12
    lx = 60
    rx = W - 60 - cwid
    for j, (cmd, resp, note) in enumerate(left):
        y = ty + j * (chei + gap)
        f.append(rect(lx, y, cwid, chei, fill=BG, stroke=LINE, sw=1.3, rx=7))
        f.append(text(lx + 14, y + 27, cmd, size=13, bold=True, color=NEG, anchor="start"))
        f.append(text(lx + 118, y + 27, resp, size=11, color=FIELD, anchor="start"))
        f.append(text(lx + 210, y + 27, note, size=9.5, color=MUTED, anchor="start"))
    for j, (cmd, resp, note) in enumerate(right):
        y = ty + j * (chei + gap)
        f.append(rect(rx, y, cwid, chei, fill=BG, stroke=LINE, sw=1.3, rx=7))
        f.append(text(rx + 14, y + 27, cmd, size=13, bold=True, color=NEG, anchor="start"))
        f.append(text(rx + 120, y + 27, resp, size=11, color=FIELD, anchor="start"))
        f.append(text(rx + 210, y + 27, note, size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "commands.svg"), W, H, *f)


# ── 4. UART-потік у число: синхронізація по кінцю рядка ────────────────────────
def fig_uart_parse():
    W, H = 940, 470
    f = [text(W / 2, 30, "Розбір UART-потоку: цифри збирай, «\\n» завершує число",
              size=17, bold=True)]

    # стрічка байтів, що прилітають (кожен — своя клітинка)
    seq = [("7", NEG), ("4", NEG), ("8", NEG), ("m", MUTED), ("m", MUTED),
           ("\\r", FIELD), ("\\n", POS), ("7", NEG), ("5", NEG), ("1", NEG)]
    n = len(seq)
    cw, ch = 66, 56
    x0 = (W - n * cw) / 2
    y0 = 74
    f.append(text(W / 2, y0 - 14, "байти летять зліва направо, один по одному", size=11, color=MUTED))
    for i, (chs, col) in enumerate(seq):
        x = x0 + i * cw
        f.append(rect(x, y0, cw - 8, ch, fill=BG, stroke=col, sw=1.7, rx=7))
        f.append(text(x + (cw - 8) / 2, y0 + 35, chs, size=20, bold=True, color=col))

    # три ролі байтів — підписи ПІД стрічкою, кожен під своєю групою, з розведенням
    yb = y0 + ch + 26
    f.append(text(x0 + 1.5 * cw, yb, "цифри → у буфер", size=11, color=NEG, bold=True))
    f.append(text(x0 + 4.0 * cw, yb, "«mm» — ігнор", size=11, color=MUTED, bold=True))
    f.append(text(x0 + 6.0 * cw, yb, "кінець рядка", size=11, color=POS, bold=True))
    f.append(text(x0 + 8.5 * cw, yb, "нове число почалось", size=11, color=NEG, bold=True))

    # два стани скінченного автомата
    sy = 300
    b1, w1, h1 = textbox(300, sy,
                         ["ЗБИРАЮ", "'7''4''8' → буфер \"748\"",
                          "нецифрове пропускаю"],
                         size=12, fill="#eaf0fd", stroke=NEG, bold=False)
    f.append(b1)
    b2, w2, h2 = textbox(650, sy,
                         ["ЗАВЕРШУЮ по '\\n'", "буфер \"748\" → число 748",
                          "буфер очищаю під наступне"],
                         size=12, fill="#fdecea", stroke=POS, bold=False)
    f.append(b2)
    f.append(arrow(300 + w1 / 2, sy, 650 - w2 / 2, sy, color=INK, sw=2))
    f.append(text((300 + 650) / 2, sy - 14, "'\\n'", size=13, bold=True, color=POS))

    b, bw, bh = textbox(W / 2, H - 26,
                        "чекай ПОВНОГО рядка до «\\n» — інакше зловиш пів-числа й дістанеш «7» чи «74» замість 748",
                        size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "uart-parse.svg"), W, H, *f)


# ── 5. Мапа I2C-регістрів: що де лежить і що можна писати ──────────────────────
def fig_registers():
    W, H = 940, 520
    f = [text(W / 2, 30, "Мапа I2C-регістрів TOF10120 (адреса 0x52)",
              size=17, bold=True)]

    rows = [
        ("0x00", "миттєва відстань", "2 байти, MSB→LSB, мм", "R", NEG),
        ("0x04", "згладжена відстань", "2 байти, MSB→LSB, мм", "R", FIELD),
        ("0x06", "зсув нуля", "2 байти, ±99 мм, юстування", "R/W", INK),
        ("0x08", "режим даних", "1 байт: 0 = згладж., 1 = сира", "R/W", INK),
        ("0x09", "режим видачі", "1 байт: 0 = сам шле, 1 = на запит", "R/W", INK),
        ("0x0C", "стеля дальності", "1 байт, обмеження max, мм", "R/W", MUTED),
        ("0x0F", "I2C-адреса", "1 байт, зміна адреси модуля", "R/W", POS),
    ]
    # колонки з ЗАПАСОМ, щоб написи не терлись
    cA, cB, cC, cD = 90, 250, 560, 828   # центри колонок
    ytop = 66
    rh = 58
    # шапка
    f.append(text(cA, ytop, "регістр", size=12, bold=True, color=MUTED))
    f.append(text(cB, ytop, "що зберігає", size=12, bold=True, color=MUTED))
    f.append(text(cC, ytop, "формат", size=12, bold=True, color=MUTED))
    f.append(text(cD, ytop, "дост.", size=12, bold=True, color=MUTED))
    f.append(line(50, ytop + 12, W - 50, ytop + 12, color=MUTED, sw=1.2))

    for j, (reg, what, fmt, rw, col) in enumerate(rows):
        yc = ytop + 40 + j * rh
        f.append(rect(50, yc - rh / 2 + 6, W - 100, rh - 10, fill=BG, stroke=LINE, sw=1.1, rx=6))
        f.append(text(cA, yc + 5, reg, size=15, bold=True, color=col, anchor="middle"))
        f.append(text(cB, yc + 5, what, size=12.5, bold=True, color=INK, anchor="middle"))
        f.append(text(cC, yc + 5, fmt, size=11, color=MUTED, anchor="middle"))
        f.append(text(cD, yc + 5, rw, size=12, bold=True,
                      color=(POS if "W" in rw else NEG), anchor="middle"))

    b, bw, bh = textbox(W / 2, H - 24,
                        "0x00 сира · 0x04 згладжена — читаєш два байти; решта R/W — юстування, режими й адреса без жодної UART-команди",
                        size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "registers.svg"), W, H, *f)


if __name__ == "__main__":
    fig_inside()
    fig_wiring()
    fig_commands()
    fig_uart_parse()
    fig_registers()
    print("OK: 5 figures ->", IMG)

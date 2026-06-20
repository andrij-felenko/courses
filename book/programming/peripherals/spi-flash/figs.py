# -*- coding: utf-8 -*-
"""Фігури до теми «SPI-флеш».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Чому окремий чип: крихітна вбудована флеш vs зовнішня по SPI ──────────
def fig_why_chip():
    W, H = 760, 380
    f = [text(W / 2, 28, "Чому окремий чип: один малий кристал не вміщає все", size=16, bold=True)]

    # МК ліворуч
    f.append(rect(70, 80, 230, 230, fill="#eef2f7", stroke=LINE, sw=2))
    f.append(text(185, 104, "Мікроконтролер", size=14, bold=True))
    # ядро
    b, _, _ = textbox(140, 150, "ядро\n+ SRAM\n(кБ)", size=12, fill="#eaf0fd", stroke=NEG)
    f.append(b)
    # крихітна вбудована флеш
    b, _, _ = textbox(245, 150, "вбуд.\nфлеш\nсотні кБ", size=11, fill="#fdecea", stroke=POS)
    f.append(b)
    f.append(text(185, 232, "усе на одному кристалі", size=12, color=MUTED))
    f.append(text(185, 252, "дорогий процес логіки", size=12, color=MUTED))
    f.append(text(185, 286, "місця під дані — обмаль", size=12, bold=True, color=POS))

    # шина SPI посередині
    f.append(arrow(300, 175, 470, 175, color=INK, sw=2.2))
    f.append(arrow(470, 205, 300, 205, color=INK, sw=2.2))
    f.append(text(385, 165, "SPI", size=13, bold=True))
    f.append(text(385, 230, "4 проводи", size=11, color=MUTED))

    # зовнішня флеш праворуч
    f.append(rect(470, 110, 220, 170, fill="#fef7e9", stroke=POS, sw=2))
    f.append(text(580, 134, "Окремий чип флеші", size=13, bold=True))
    b, _, _ = textbox(580, 185, "масив комірок\nплаваючого затвора\nМіБ за копійки", size=12,
                      fill="#fdf0d5", stroke="#caa53d")
    f.append(b)
    f.append(text(580, 248, "дешевий «оптовий» процес", size=11, color=MUTED))
    f.append(text(580, 266, "ємність на порядки більша", size=11, bold=True, color=FIELD))

    # підсумок-стрічка
    b, _, _ = textbox(W / 2, 344, "Логіку й пам'ять роблять різні процеси → дешевше тримати "
                                  "їх двома кристалами, з'єднаними тонкою шиною", size=12,
                      fill="#eef6ef", stroke=FIELD, min_w=W - 80)
    f.append(b)
    render(os.path.join(IMG, "why-chip.svg"), W, H, *f)


# ── 2. Анатомія обміну: команда + 24-бітна адреса + дані по одній лінії ──────
def fig_command_bytes():
    W, H = 780, 400
    f = [text(W / 2, 28, "Один обмін: CS вниз → байти команди → дані → CS вгору", size=16, bold=True)]

    # лінія CS
    f.append(text(70, 70, "CS#", size=13, bold=True, anchor="start", color=NEG))
    f.append(line(120, 60, 150, 60, color=NEG, sw=2))          # high
    f.append(line(150, 60, 150, 78, color=NEG, sw=2))          # fall
    f.append(line(150, 78, 690, 78, color=NEG, sw=2))          # low (активний)
    f.append(line(690, 78, 690, 60, color=NEG, sw=2))          # rise
    f.append(line(690, 60, 720, 60, color=NEG, sw=2))          # high
    f.append(text(160, 54, "↓ обрали чип", size=10, anchor="start", color=NEG))
    f.append(text(680, 54, "↑ кінець", size=10, anchor="end", color=NEG))

    # байтова стрічка по MOSI/MISO
    x0, y0, bw, bh = 150, 110, 67.5, 56
    cells = [
        ("MOSI", "0x03", "команда\nREAD", "#fdecea", POS),
        ("MOSI", "A23..16", "адреса\n(стар.)", "#eef2f7", LINE),
        ("MOSI", "A15..8", "адреса\n(сер.)", "#eef2f7", LINE),
        ("MOSI", "A7..0", "адреса\n(мол.)", "#eef2f7", LINE),
        ("MISO", "D0", "байт\nданих", "#eaf0fd", NEG),
        ("MISO", "D1", "байт\nданих", "#eaf0fd", NEG),
        ("MISO", "…", "потік\nдалі", "#eaf0fd", NEG),
    ]
    for i, (lane, val, note, fill, stroke) in enumerate(cells):
        x = x0 + i * bw
        f.append(rect(x, y0, bw - 6, bh, fill=fill, stroke=stroke, sw=1.8))
        f.append(text(x + (bw - 6) / 2, y0 + 24, val, size=13, bold=True, color=INK))
        f.append(mtext(x + (bw - 6) / 2, y0 + 40, note, size=9.5, color=MUTED, lh=1.15))
        # хто веде цей байт
        tag = "ведучий →" if lane == "MOSI" else "← флеш"
        tagcol = POS if lane == "MOSI" else NEG
        f.append(text(x + (bw - 6) / 2, y0 - 8, tag, size=9, color=tagcol))

    # дужка «адреса 24 біти»
    ax1, ax2 = x0 + bw, x0 + 4 * bw - 6
    f.append(line(ax1, y0 + bh + 14, ax2, y0 + bh + 14, color=INK, sw=1.4))
    f.append(line(ax1, y0 + bh + 10, ax1, y0 + bh + 18, color=INK, sw=1.4))
    f.append(line(ax2, y0 + bh + 10, ax2, y0 + bh + 18, color=INK, sw=1.4))
    f.append(text((ax1 + ax2) / 2, y0 + bh + 30, "24-бітна адреса = 3 байти", size=11, bold=True))

    # пояснення півдуплексу
    b, _, _ = textbox(W / 2, 250, "Спершу ведучий висуває команду й адресу (MOSI),\n"
                                  "потім флеш у відповідь висуває байти даних (MISO).\n"
                                  "Та сама рамка CS# тримає весь обмін як одне ціле.",
                      size=12, fill="#eef2f7", stroke=LINE, min_w=440)
    f.append(b)

    # три типові команди
    f.append(text(W / 2, 312, "Кожна операція починається зі свого коду-команди:", size=12, bold=True))
    cmds = [("0x03", "READ — читати"), ("0x02", "PAGE PROGRAM — писати сторінку"),
            ("0x20", "SECTOR ERASE — стерти сектор")]
    cy = 344
    cx = 110
    for code, name in cmds:
        b, w, _ = textbox(cx + 60, cy, code + "  " + name, size=11, fill="#fdf0d5", stroke="#caa53d")
        f.append(b)
        cx += w + 16
    render(os.path.join(IMG, "command-bytes.svg"), W, H, *f)


# ── 3. Асиметрія операцій + знос: писати дрібно, стирати блоком ──────────────
def fig_erase_wear():
    W, H = 780, 420
    f = [text(W / 2, 28, "Несиметрія: пишемо сторінками, стираємо блоками — звідси знос", size=15.5, bold=True)]

    # масив: блок із сторінок
    bx, by = 70, 70
    pw, ph = 84, 30
    cols, rows = 4, 4
    # рамка блоку (сектора)
    f.append(rect(bx - 8, by - 8, cols * pw + 16, rows * ph + 16, fill="#fef7e9",
                  stroke=POS, sw=2.2))
    f.append(text(bx + cols * pw / 2, by - 16, "сектор / блок — найменша одиниця СТИРАННЯ",
                  size=11, bold=True, color=POS))
    for r in range(rows):
        for c in range(cols):
            x = bx + c * pw
            y = by + r * ph
            f.append(rect(x, y, pw - 4, ph - 4, fill="#eef2f7", stroke=LINE, sw=1.2))
            f.append(text(x + (pw - 4) / 2, y + (ph - 4) / 2 + 4, "сторінка", size=10, color=MUTED))
    f.append(text(bx + cols * pw / 2, by + rows * ph + 18,
                  "сторінка — найменша одиниця ЗАПИСУ", size=11, bold=True, color=NEG))

    # правило «1→0 дешево, 0→1 лише стиранням»
    rx = 430
    b, _, _ = textbox(rx + 150, 95, "Фізика комірки:", size=12, bold=True,
                      fill=BG, stroke=BG)
    f.append(b)
    b, _, _ = textbox(rx + 150, 130, "запис лише гасить біти: 1 → 0", size=12,
                      fill="#eaf0fd", stroke=NEG, min_w=290)
    f.append(b)
    b, _, _ = textbox(rx + 150, 168, "повернути 0 → 1 можна лише\nстиранням цілого блоку", size=12,
                      fill="#fdecea", stroke=POS, min_w=290)
    f.append(b)
    b, _, _ = textbox(rx + 150, 214, "тому правило завжди:\nстерти блок → потім писати", size=12,
                      bold=True, fill="#eef6ef", stroke=FIELD, min_w=290)
    f.append(b)

    # знос: лічильник циклів
    wy = 300
    f.append(text(W / 2, wy, "Кожне стирання трохи зношує комірку:", size=12.5, bold=True))
    # шкала
    sx0, sx1 = 130, 650
    f.append(line(sx0, wy + 34, sx1, wy + 34, color=LINE, sw=2))
    for frac, lab, col in [(0.0, "новий", FIELD), (0.5, "~50 тис.", MUTED),
                           (1.0, "~100 тис. циклів → знос", POS)]:
        x = sx0 + frac * (sx1 - sx0)
        f.append(line(x, wy + 28, x, wy + 40, color=LINE, sw=1.6))
        f.append(circle(x, wy + 34, 5, fill=col, stroke=col))
        anch = "start" if frac == 0 else ("end" if frac == 1 else "middle")
        f.append(text(x, wy + 56, lab, size=10.5, color=col, anchor=anch))
    b, _, _ = textbox(W / 2, wy + 92, "Звідси вирівнювання зносу: не довбати один сектор, "
                                      "а розмазувати записи по всьому чипу", size=11.5,
                      fill="#eef6ef", stroke=FIELD, min_w=W - 120)
    f.append(b)
    render(os.path.join(IMG, "erase-wear.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_chip()
    fig_command_bytes()
    fig_erase_wear()
    print("OK: 3 фігури у", IMG)

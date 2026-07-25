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


# ── 4. Комірка з плаваючим затвором: біт — це заряд на острівці ──────────────
def fig_cell():
    W, H = 820, 470
    f = [text(W / 2, 28, "Комірка флеші: біт — це заряд на замкненому острівці", size=16, bold=True)]

    def draw_cell(cx, title, bit, caption, charged, chan_open):
        p = []
        p.append(text(cx, 62, title, size=13, bold=True))
        # керувальний затвор
        p.append(rect(cx - 90, 78, 180, 28, fill="#eef2f7", stroke=LINE, sw=1.6))
        p.append(text(cx, 96, "керувальний затвор", size=10.5))
        # підпис плаваючого затвора (у проміжку між шарами)
        p.append(text(cx, 120, "плаваючий затвор", size=10, color="#caa53d", bold=True))
        # плаваючий затвор — острівець
        p.append(rect(cx - 70, 126, 140, 38, fill="#fdf0d5", stroke="#caa53d", sw=2))
        if charged:
            for ex in (cx - 42, cx - 14, cx + 14, cx + 42):
                p.append(minus(ex, 145, 7))
        else:
            p.append(text(cx, 149, "порожній", size=11, color=MUTED))
        # тонкий оксид
        p.append(rect(cx - 90, 170, 180, 16, fill="#f6e6e6", stroke=POS, sw=1.2))
        p.append(text(cx, 182, "тонкий оксид", size=9.5, color=POS))
        # канал
        chan_fill = "#eef6ef" if chan_open else "#fdecea"
        chan_col = FIELD if chan_open else POS
        p.append(rect(cx - 90, 190, 180, 32, fill=chan_fill, stroke=chan_col, sw=1.6))
        p.append(text(cx, 210, "канал " + ("відкритий" if chan_open else "затиснутий"),
                      size=11, color=chan_col))
        # біт і підпис читання
        p.append(text(cx, 262, bit, size=32, bold=True,
                      color=(FIELD if chan_open else POS)))
        p.append(text(cx, 292, caption, size=11, color=MUTED))
        return p

    f += draw_cell(210, "Стерта комірка", "1", "проводить → читається 1",
                   charged=False, chan_open=True)
    f += draw_cell(610, "Записана комірка", "0", "не проводить → читається 0",
                   charged=True, chan_open=False)

    # перехід між станами (у проміжку між комірками)
    f.append(arrow(330, 118, 490, 118, color=NEG, sw=2.2))
    f.append(text(410, 108, "запис: 1 → 0", size=11, bold=True, color=NEG))
    f.append(text(410, 138, "електрони на острівець", size=10, color=NEG))
    f.append(arrow(490, 200, 330, 200, color=POS, sw=2.2))
    f.append(text(410, 190, "стирання: → 1", size=11, bold=True, color=POS))
    f.append(text(410, 220, "електрони геть, цілим блоком", size=10, color=POS))

    # підсумкова стрічка про знос
    b, _, _ = textbox(W / 2, 440,
                      "І запис, і стирання щоразу проганяють електрони крізь тонкий оксид\n"
                      "і трохи його псують — тому кожна комірка витримує скінченне число циклів.",
                      size=11.5, fill="#eef6ef", stroke=FIELD, min_w=W - 80)
    f.append(b)
    render(os.path.join(IMG, "cell.svg"), W, H, *f)


# ── 5. Одна / дві / чотири лінії даних: ширший тракт, а не вищий такт ─────────
def fig_quad_spi():
    W, H = 820, 430
    f = [text(W / 2, 28, "Швидше — це більше ліній даних одразу", size=16, bold=True)]

    rows = [
        ("Single SPI", "1 біт / такт", 1, "×1", "0x03 READ"),
        ("Dual SPI", "2 біти / такт", 2, "×2", "0x3B / 0xBB"),
        ("Quad SPI", "4 біти / такт", 4, "×4", "0x6B / 0xEB"),
    ]
    ys = [100, 215, 330]
    for (name, bits, n, mult, opc), cy in zip(rows, ys):
        # назва режиму ліворуч
        b, _, _ = textbox(120, cy, name + "\n" + bits, size=12, bold=True,
                          fill="#eef2f7", stroke=LINE, min_w=180)
        f.append(b)
        # лінії даних посередині
        maxoff = (n - 1) / 2.0 * 13
        for i in range(n):
            ly = cy + (i - (n - 1) / 2.0) * 13
            f.append(arrow(255, ly, 510, ly, color=NEG, sw=2))
        f.append(text(382, cy - maxoff - 12,
                      ("%d лінія даних" % n) if n == 1 else ("%d лінії даних" % n),
                      size=10, color=MUTED))
        f.append(text(382, cy + maxoff + 22, opc, size=10, color=MUTED))
        # прискорення праворуч
        b, _, _ = textbox(640, cy, mult, size=20, bold=True,
                          fill="#fdf0d5", stroke="#caa53d", min_w=80)
        f.append(b)

    b, _, _ = textbox(W / 2, 402,
                      "Ширший тракт, а не вищий такт: піни WP# і HOLD# стають лініями IO2/IO3,\n"
                      "і за один такт із чипа виходить 2 або 4 біти замість одного.",
                      size=11.5, fill="#eef6ef", stroke=FIELD, min_w=W - 80)
    f.append(b)
    render(os.path.join(IMG, "quad-spi.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why_chip()
    fig_command_bytes()
    fig_erase_wear()
    fig_cell()
    fig_quad_spi()
    print("OK: 5 фігур у", IMG)

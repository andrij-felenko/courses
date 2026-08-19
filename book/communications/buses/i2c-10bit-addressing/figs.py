# -*- coding: utf-8 -*-
"""Фігури до теми «10-бітна адресація I2C».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Формат двох байтів 10-бітної адреси ───────────────────────────────────
def fig_addr_format():
    W, H = 840, 360
    f = [text(W / 2, 28, "Формат двох байтів 10-бітної адреси I2C", size=16, bold=True)]

    # Перший байт
    f.append(text(80, 62, "1-й байт (префікс + старші біти + напрямок):", size=12, bold=True, anchor="start"))
    p_bits = [("bit 7", "1"), ("bit 6", "1"), ("bit 5", "1"), ("bit 4", "1"), ("bit 3", "0")]
    a_bits = [("bit 2", "A9"), ("bit 1", "A8")]
    bw, bx, by = 82, 80, 74

    # Префікс 11110 (5 бітів)
    for i, (lab, val) in enumerate(p_bits):
        x = bx + i * bw
        f.append(rect(x, by, bw - 6, 50, fill="#fdecea", stroke=POS, sw=1.8, rx=4))
        f.append(text(x + (bw - 6) / 2, by + 18, lab, size=10, color=MUTED))
        f.append(text(x + (bw - 6) / 2, by + 38, val, size=14, bold=True, color=POS))

    # A9, A8 (2 біти)
    for i, (lab, val) in enumerate(a_bits):
        x = bx + (5 + i) * bw
        f.append(rect(x, by, bw - 6, 50, fill="#e9eefb", stroke=NEG, sw=1.8, rx=4))
        f.append(text(x + (bw - 6) / 2, by + 18, lab, size=10, color=MUTED))
        f.append(text(x + (bw - 6) / 2, by + 38, val, size=14, bold=True, color=NEG))

    # R/W (1 біт)
    xr = bx + 7 * bw
    f.append(rect(xr, by, bw - 6, 50, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(xr + (bw - 6) / 2, by + 18, "bit 0", size=10, color=MUTED))
    f.append(text(xr + (bw - 6) / 2, by + 38, "R/W", size=13, bold=True, color=FIELD))

    # Пояснення першого байта
    f.append(text(bx + 2.5 * bw - 3, by + 68, "зарезервований префікс 11110 (0x78..0x7B)", size=11, bold=True, color=POS))
    f.append(text(bx + 6 * bw - 3, by + 68, "біти A9..A8", size=11, bold=True, color=NEG))
    f.append(text(xr + (bw - 6) / 2, by + 68, "0=W, 1=R", size=11, bold=True, color=FIELD))

    # Другий байт
    by2 = 172
    f.append(text(80, by2 - 12, "2-й байт (молодші вісім бітів адреси):", size=12, bold=True, anchor="start"))
    low_bits = [("bit 7", "A7"), ("bit 6", "A6"), ("bit 5", "A5"), ("bit 4", "A4"),
                ("bit 3", "A3"), ("bit 2", "A2"), ("bit 1", "A1"), ("bit 0", "A0")]
    for i, (lab, val) in enumerate(low_bits):
        x = bx + i * bw
        f.append(rect(x, by2, bw - 6, 50, fill="#e9eefb", stroke=NEG, sw=1.8, rx=4))
        f.append(text(x + (bw - 6) / 2, by2 + 18, lab, size=10, color=MUTED))
        f.append(text(x + (bw - 6) / 2, by2 + 38, val, size=14, bold=True, color=NEG))

    f.append(text(W / 2, by2 + 68, "повна 10-бітна адреса: [A9 A8 A7 A6 A5 A4 A3 A2 A1 A0] — діапазон 0x000…0x3FF (1024 адреси)",
                  size=12, bold=True, color=NEG))

    b = fitbox(60, H - 46, W - 120, 34,
               "Префікс 11110 виключає конфлікти з 7-бітними веденими: вони бачать зарезервовану адресу й не озиваються",
               size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "addr-10bit-format.svg"), W, H, *f)


# ── 2. Послідовність Master Write ───────────────────────────────────────────
def fig_write_sequence():
    W, H = 840, 320
    f = [text(W / 2, 28, "Послідовність сигналів при 10-бітному записі (Master Write)", size=16, bold=True)]

    # Блоки транзакції
    blocks = [
        ("S", 40, "#eef6ef", FIELD, "START"),
        ("1-й байт адреси\n11110 + A9..A8 + W(0)", 150, "#fdecea", POS, "ведучий"),
        ("ACK", 45, "#eef6ef", FIELD, "ведені A9..A8"),
        ("2-й байт адреси\nA7..A0", 140, "#e9eefb", NEG, "ведучий"),
        ("ACK", 45, "#eef6ef", FIELD, "ведений чіп"),
        ("Байт даних 1\nD7..D0", 120, FILL, INK, "ведучий"),
        ("ACK", 45, "#eef6ef", FIELD, "ведений чіп"),
        ("Байт даних 2\nD7..D0", 120, FILL, INK, "ведучий"),
        ("ACK", 45, "#eef6ef", FIELD, "ведений чіп"),
        ("P", 40, "#fdecea", POS, "STOP"),
    ]

    tot_w = sum(b[1] for b in blocks) + (len(blocks) - 1) * 6
    start_x = (W - tot_w) / 2
    cur_x = start_x
    by = 70

    for lab, bw, fill_c, strk_c, src in blocks:
        lines = lab.split("\n")
        f.append(rect(cur_x, by, bw, 64, fill=fill_c, stroke=strk_c, sw=1.8, rx=5))
        if len(lines) == 1:
            f.append(text(cur_x + bw / 2, by + 37, lines[0], size=13, bold=True, color=strk_c if strk_c != INK else INK))
        else:
            f.append(text(cur_x + bw / 2, by + 26, lines[0], size=11, bold=True))
            f.append(text(cur_x + bw / 2, by + 48, lines[1], size=10, color=MUTED))
        f.append(text(cur_x + bw / 2, by + 84, src, size=9.5, color=MUTED))
        cur_x += bw + 6

    # Пояснювальні стрілки й стан ведених
    sy = 190
    f.append(rect(start_x, sy, tot_w, 62, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(start_x + 15, sy + 22, "1. На 1-й байт відгукуються всі 10-бітні ведені з однаковими старшими бітами A9..A8",
                  size=11, anchor="start", color=INK))
    f.append(text(start_x + 15, sy + 44, "2. На 2-й байт відгукується лише один цільовий ведений (збіг A7..A0); решта відпадає",
                  size=11, anchor="start", color=FIELD, bold=True))

    b = fitbox(60, H - 44, W - 120, 32,
               "Запис виконується в один прохід: два байти адреси поспіль обирають чіп, після чого йдуть байти даних",
               size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "write-10bit-sequence.svg"), W, H, *f)


# ── 3. Послідовність Master Read ────────────────────────────────────────────
def fig_read_sequence():
    W, H = 840, 380
    f = [text(W / 2, 26, "Послідовність сигналів при 10-бітному читанні (Master Read)", size=16, bold=True)]

    # Фаза 1: Адресація (запис)
    f.append(text(50, 56, "Фаза 1: Адресація та вибір веденого (напрямок R/W = 0)", size=11.5, bold=True, anchor="start", color=POS))
    blocks1 = [
        ("S", 36, "#eef6ef", FIELD, "START"),
        ("1-й байт: 11110 + A9..A8 + W(0)", 180, "#fdecea", POS, "ведучий"),
        ("ACK", 40, "#eef6ef", FIELD, "ведені"),
        ("2-й байт: A7..A0", 130, "#e9eefb", NEG, "ведучий"),
        ("ACK", 40, "#eef6ef", FIELD, "ведений"),
    ]
    cur_x = 50
    by1 = 68
    for lab, bw, fill_c, strk_c, src in blocks1:
        f.append(rect(cur_x, by1, bw, 46, fill=fill_c, stroke=strk_c, sw=1.6, rx=4))
        f.append(text(cur_x + bw / 2, by1 + 28, lab, size=10.5, bold=True))
        cur_x += bw + 5
    f.append(text(cur_x + 10, by1 + 28, "→ ведений розпізнає себе й фіксує вибір", size=10.5, anchor="start", color=MUTED))

    # Фаза 2: Зміна напрямку на читання через Repeated START
    f.append(text(50, 142, "Фаза 2: Повторний старт і запит читання (напрямок R/W = 1)", size=11.5, bold=True, anchor="start", color=NEG))
    blocks2 = [
        ("Sr", 36, "#eef6ef", FIELD, "Repeated START"),
        ("1-й байт: 11110 + A9..A8 + R(1)", 180, "#e9eefb", NEG, "ведучий"),
        ("ACK", 40, "#eef6ef", FIELD, "ведений"),
        ("Дані 1 (D7..D0)", 110, FILL, INK, "ведений чіп"),
        ("ACK", 40, "#eef6ef", FIELD, "ведучий"),
        ("Дані 2 (останній)", 120, FILL, INK, "ведений чіп"),
        ("NACK", 45, "#fdecea", POS, "ведучий"),
        ("P", 36, "#fdecea", POS, "STOP"),
    ]
    cur_x = 50
    by2 = 154
    for lab, bw, fill_c, strk_c, src in blocks2:
        f.append(rect(cur_x, by2, bw, 46, fill=fill_c, stroke=strk_c, sw=1.6, rx=4))
        f.append(text(cur_x + bw / 2, by2 + 28, lab, size=10.5, bold=True))
        cur_x += bw + 5

    # Пояснення чому 2-й байт не повторюється
    ey = 224
    f.append(rect(50, ey, W - 100, 84, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(65, ey + 24, "• Чому 2-й байт адреси не передається вдруге?", size=11.5, bold=True, anchor="start", color=INK))
    f.append(text(65, ey + 46, "  Ведений уже зафіксував свій стан адресації у Фазі 1. На повторний старт із R/W=1",
                  size=11, anchor="start", color=MUTED))
    f.append(text(65, ey + 66, "  відгукується лише той єдиний чіп, який був щойно обраний, і негайно починає передачу даних.",
                  size=11, anchor="start", color=MUTED))

    b = fitbox(50, H - 44, W - 100, 32,
               "Читання вимагає Repeated START: спочатку повна адресація із R/W=0, потім рестарт із R/W=1 без 2-го байта",
               size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "read-10bit-sequence.svg"), W, H, *f)


# ── 4. Співіснування 7-бітних і 10-бітних пристроїв ──────────────────────────
def fig_coexistence():
    W, H = 840, 350
    f = [text(W / 2, 28, "Співіснування 7-бітних та 10-бітних ведених на одній шині", size=16, bold=True)]

    # Спільна лінія шини I2C
    bx, ex, ly = 80, W - 80, 110
    f.append(line(bx, ly, ex, ly, color=POS, sw=3))
    f.append(text(bx, ly - 14, "SDA / SCL  (ведучий шле 1-й байт: 1111 001 0)", size=12, bold=True, anchor="start", color=INK))

    nodes = [
        (190, "7-бітний", "0x48 (1001000b)", False, "11110xx ≠ 0x48\n→ мовчить (NACK)"),
        (390, "7-бітний", "0x68 (1101000b)", False, "11110xx ≠ 0x68\n→ мовчить (NACK)"),
        (610, "10-бітний", "0x248 (10 0100 1000b)", True, "A9..A8 збіглися → ACK 1\nA7..A0 збіглися → ACK 2\n→ приймає дані"),
    ]

    for nx, dev_type, addr_str, hit, status_str in nodes:
        f.append(line(nx, ly, nx, ly + 40, color=INK, sw=1.8))
        col = FIELD if hit else MUTED
        fill_c = "#eef6ef" if hit else FILL
        bw_box = 180 if hit else 160
        f.append(rect(nx - bw_box / 2, ly + 40, bw_box, 120, fill=fill_c, stroke=col, sw=2, rx=8))
        f.append(text(nx, ly + 62, dev_type, size=11, bold=True, color=col if hit else INK))
        f.append(text(nx, ly + 80, addr_str, size=10, color=MUTED))

        st_lines = status_str.split("\n")
        for j, sl in enumerate(st_lines):
            f.append(text(nx, ly + 102 + j * 16, sl, size=9.5, bold=hit, color=FIELD if hit else MUTED))

    b = fitbox(60, H - 46, W - 120, 34,
               "7-бітні чіпи ігнорують префікс 11110 і другий байт адреси, тому обидва стандарти безпечно ділять спільну пару дротів",
               size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "coexistence-7bit-10bit.svg"), W, H, *f)


# ── 5. Арбітраж між двома 10-бітними ведучими ────────────────────────────────
def fig_arbitration():
    W, H = 840, 350
    f = [text(W / 2, 28, "Порозрядний арбітраж між двома 10-бітними ведучими", size=16, bold=True)]

    # Ведучий 1
    f.append(rect(60, 60, 340, 180, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    f.append(text(230, 84, "Ведучий 1 (адресує 0x248)", size=13, bold=True, color=POS))
    f.append(text(80, 112, "1-й байт: 1111 0 10 0  (збіг із шиною ✓)", size=10.5, anchor="start"))
    f.append(text(80, 134, "2-й байт: 0 1 0 0 1 0 0 0", size=11, bold=True, anchor="start"))
    f.append(text(80, 156, "На біті 6 хоче видати «1» (відпускає SDA)", size=10, anchor="start", color=MUTED))
    f.append(text(80, 176, "Але шина притягнута до «0»!", size=10.5, bold=True, anchor="start", color=POS))
    f.append(text(80, 204, "→ Програв арбітраж і вимикає передавач", size=11, bold=True, anchor="start", color=POS))

    # Ведучий 2
    f.append(rect(440, 60, 340, 180, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(610, 84, "Ведучий 2 (адресує 0x215)", size=13, bold=True, color=FIELD))
    f.append(text(460, 112, "1-й байт: 1111 0 10 0  (збіг із шиною ✓)", size=10.5, anchor="start"))
    f.append(text(460, 134, "2-й байт: 0 0 0 1 0 1 0 1", size=11, bold=True, anchor="start"))
    f.append(text(460, 156, "На біті 6 видає «0» (притягує SDA до GND)", size=10, anchor="start", color=MUTED))
    f.append(text(460, 176, "Стан шини збігається з його бітом «0» ✓", size=10.5, bold=True, anchor="start", color=FIELD))
    f.append(text(460, 204, "→ Виграв арбітраж і безперешкодно пише", size=11, bold=True, anchor="start", color=FIELD))

    # Пояснення посередині між ними
    f.append(arrow(400, 150, 440, 150, color=LINE, sw=1.5))
    f.append(arrow(440, 150, 400, 150, color=LINE, sw=1.5))
    f.append(text(420, 142, "SDA", size=10, bold=True))

    b = fitbox(60, H - 46, W - 120, 34,
               "Арбітраж за принципом «монтажного І» триває на 2-му байті адреси: перемагає ведучий із меншим числовим значенням бітів",
               size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "arbitration-10bit.svg"), W, H, *f)


if __name__ == "__main__":
    fig_addr_format()
    fig_write_sequence()
    fig_read_sequence()
    fig_coexistence()
    fig_arbitration()
    print("All figures generated successfully.")

# -*- coding: utf-8 -*-
"""Фігури до теми «Адресація I2C».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Перший байт: 7 біт адреси + біт напрямку R/W ──────────────────────────
def fig_addr_byte():
    W, H = 820, 300
    f = [text(W / 2, 30, "Перший байт після старту: 7 біт адреси й біт напрямку",
              size=16, bold=True)]

    bits = [("A6", "1"), ("A5", "1"), ("A4", "0"), ("A3", "1"),
            ("A2", "0"), ("A1", "0"), ("A0", "0")]
    bw, bx, by = 80, 90, 90
    for i, (lab, val) in enumerate(bits):
        x = bx + i * bw
        f.append(rect(x, by, bw - 6, 56, fill="#e9eefb", stroke=NEG, sw=1.8, rx=4))
        f.append(text(x + (bw - 6) / 2, by - 8, lab, size=11, bold=True, color=NEG))
        f.append(text(x + (bw - 6) / 2, by + 36, val, size=15, bold=True))
    # біт R/W — зелений
    xr = bx + 7 * bw
    f.append(rect(xr, by, bw - 6, 56, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=4))
    f.append(text(xr + (bw - 6) / 2, by - 8, "R/W", size=11, bold=True, color=FIELD))
    f.append(text(xr + (bw - 6) / 2, by + 36, "0", size=15, bold=True))

    # фігурна дужка адреси
    yb = by + 80
    f.append(arrow(bx + 3.5 * bw, yb, bx, yb, color=NEG, sw=1.6))
    f.append(arrow(bx + 3.5 * bw, yb, bx + 7 * bw - 6, yb, color=NEG, sw=1.6))
    f.append(text(bx + 3.5 * bw, yb + 20, "7 біт адреси = 0x68", size=13, bold=True, color=NEG))
    f.append(text(xr + (bw - 6) / 2, yb + 20, "напрямок", size=11, bold=True, color=FIELD))

    f.append(text(W / 2, yb + 52, "0 — ведучий пише   ·   1 — ведучий читає", size=12.5, bold=True))

    b = fitbox(70, H - 46, W - 140, 34,
               "7 біт → 2⁷ = 128 можливих адрес; кілька зарезервовано, придатних близько 112",
               size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "addr-byte.svg"), W, H, *f)


# ── 2. Адресу чують усі — відгукується лише збіг ─────────────────────────────
def fig_select():
    W, H = 820, 340
    f = [text(W / 2, 30, "Адресу чують усі, відгукується лише збіг", size=16, bold=True)]

    # спільна лінія
    bx, ex, ly = 110, W - 90, 120
    f.append(line(bx, ly, ex, ly, color=POS, sw=3))
    f.append(text(bx + 4, ly - 12, "ведучий шле 0x68 →", size=12, bold=True, anchor="start"))

    nodes = [(220, "0x3C", False), (400, "0x68", True),
             (560, "0x76", False), (700, "0x50", False)]
    for nx, addr, hit in nodes:
        f.append(line(nx, ly, nx, ly + 70, color=INK, sw=1.8))
        col = FIELD if hit else MUTED
        fill = "#eef6ef" if hit else FILL
        f.append(rect(nx - 55, ly + 70, 110, 70, fill=fill, stroke=col, sw=2, rx=8))
        f.append(text(nx, ly + 96, "адреса " + addr, size=11.5, bold=True))
        if hit:
            f.append(text(nx, ly + 120, "це я → ACK", size=11.5, bold=True, color=FIELD))
        else:
            f.append(text(nx, ly + 120, "не я → мовчу", size=10.5, color=MUTED))

    b = fitbox(70, H - 44, W - 140, 32,
               "адреса — це фільтр: на спільній лінії кожен слухає, та реагує лише власник адреси",
               size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "select.svg"), W, H, *f)


# ── 3. Біт R/W: одна адреса, два напрямки ────────────────────────────────────
def fig_rw():
    W, H = 800, 340
    f = [text(W / 2, 30, "Біт R/W: одна адреса, два напрямки обміну", size=16, bold=True)]

    # ліворуч — запис
    f.append(rect(60, 70, 320, 120, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    f.append(text(220, 96, "R/W = 0 : запис", size=13.5, bold=True, color=FIELD))
    f.append(rect(95, 116, 90, 50, fill=BG, stroke=INK, sw=2, rx=8))
    f.append(text(140, 146, "ведучий", size=11, bold=True))
    f.append(rect(265, 116, 90, 50, fill=BG, stroke=INK, sw=2, rx=8))
    f.append(text(310, 146, "0x68", size=11, bold=True))
    f.append(arrow(185, 141, 263, 141, color=NEG, sw=2.4))
    f.append(text(224, 132, "дані →", size=10, bold=True, color=NEG))

    # праворуч — читання
    f.append(rect(W - 380, 70, 320, 120, fill="#e9eefb", stroke=NEG, sw=2, rx=12))
    f.append(text(W - 220, 96, "R/W = 1 : читання", size=13.5, bold=True, color=NEG))
    f.append(rect(W - 345, 116, 90, 50, fill=BG, stroke=INK, sw=2, rx=8))
    f.append(text(W - 300, 146, "ведучий", size=11, bold=True))
    f.append(rect(W - 175, 116, 90, 50, fill=BG, stroke=INK, sw=2, rx=8))
    f.append(text(W - 130, 146, "0x68", size=11, bold=True))
    f.append(arrow(W - 175, 141, W - 253, 141, color=POS, sw=2.4))
    f.append(text(W - 214, 158, "← дані", size=10, bold=True, color=POS))

    f.append(text(W / 2, 232, "Адреса вибирає, з ким говорити; біт R/W — у який бік ідуть дані.",
                  size=12.5, bold=True))
    b = fitbox(70, H - 64, W - 140, 50,
               ["0x68 із R/W=0 → байт 0xD0 на лінії;  0x68 із R/W=1 → байт 0xD1.",
                "це та сама адреса — лише по-різному записана"],
               size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "rw.svg"), W, H, *f)


# ── 4. 7-біт проти 8-біт: 0x68 чи 0xD0 ───────────────────────────────────────
def fig_seven_vs_eight():
    W, H = 820, 380
    f = [text(W / 2, 30, "Та сама адреса у двох записах: 7-бітна й 8-бітна", size=16, bold=True)]

    def row(y, label, bits7, rw, result, accent):
        f.append(text(180, y + 26, label, size=12, bold=True, color=accent, anchor="end"))
        cells = list(bits7)
        bx, bw = 196, 54
        for i, val in enumerate(cells):
            x = bx + i * bw
            f.append(rect(x, y, bw - 4, 44, fill="#e9eefb", stroke=NEG, sw=1.6, rx=4))
            f.append(text(x + (bw - 4) / 2, y + 30, val, size=14, bold=True))
        if rw is not None:
            x = bx + 7 * bw
            f.append(rect(x, y, bw - 4, 44, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=4))
            f.append(text(x + (bw - 4) / 2, y - 8, "R/W", size=10, bold=True, color=FIELD))
            f.append(text(x + (bw - 4) / 2, y + 30, rw, size=14, bold=True))
            rx = x + bw + 6
        else:
            rx = bx + 7 * bw + 6
        f.append(text(rx, y + 30, "= " + result, size=14, bold=True, color=accent, anchor="start"))

    b7 = ["1", "1", "0", "1", "0", "0", "0"]
    row(80, "7-біт адреса", b7, None, "0x68", NEG)
    f.append(text(W / 2, 156, "зсув ліворуч на 1 + біт R/W ↓", size=11, color=MUTED))
    row(176, "8-біт (запис)", b7, "0", "0xD0", FIELD)
    row(244, "8-біт (читання)", b7, "1", "0xD1", FIELD)

    b = fitbox(70, H - 56, W - 140, 42,
               ["Бібліотека зазвичай хоче 7-бітну (0x68) і сама додає R/W;",
                "даташит інколи дає 8-бітну (0xD0). Це одна адреса."],
               size=11.5, fill="#fbecec", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "seven-vs-eight.svg"), W, H, *f)


# ── 5. Кілька однакових чіпів: ніжки адреси A0/A1/A2 ─────────────────────────
def fig_addr_pins():
    W, H = 820, 360
    f = [text(W / 2, 30, "Кілька однакових чіпів на шині: ніжки адреси", size=16, bold=True)]

    # лівий чіп: A0=GND → 0x68
    f.append(rect(120, 80, 160, 120, fill=BG, stroke=INK, sw=2, rx=10))
    f.append(text(200, 108, "той самий тип чіпа", size=10.5, color=MUTED))
    f.append(text(200, 138, "адреса 0x68", size=13.5, bold=True, color=FIELD))
    f.append(text(200, 176, "A0 = GND (0)", size=11.5, bold=True, color=NEG))

    # правий чіп: A0=VCC → 0x69
    f.append(rect(W - 280, 80, 160, 120, fill=BG, stroke=INK, sw=2, rx=10))
    f.append(text(W - 200, 108, "той самий тип чіпа", size=10.5, color=MUTED))
    f.append(text(W - 200, 138, "адреса 0x69", size=13.5, bold=True, color=FIELD))
    f.append(text(W - 200, 176, "A0 = VCC (1)", size=11.5, bold=True, color=POS))

    # посередині — як змінюється молодший біт
    f.append(text(W / 2, 122, "база 0x68", size=12, bold=True))
    f.append(text(W / 2, 144, "+ A0 → 0x68 / 0x69", size=11.5, color=MUTED))
    f.append(line(284, 140, W - 284, 140, color=MUTED, sw=1.6, dash="4,3"))

    b = fitbox(70, H - 110, W - 140, 96,
               ["Так два-чотири однакові давачі живуть на одній шині: кожному дають свою адресу ніжками.",
                "Бракує ніжок — ставлять I2C-мультиплексор, що розводить шину на кілька гілок.",
                "Дві однакові адреси на одній шині без цього — конфлікт: обидва відгукнуться разом."],
               size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "addr-pins.svg"), W, H, *f)


# ── 6. Карта 7-бітних адрес і зарезервовані діапазони ────────────────────────
def fig_addr_map():
    cell = 44
    cols = 16
    gx, gy = 120, 90
    grid_w = cols * cell
    examples = {0x3C, 0x50, 0x68, 0x76}
    reserved = set(range(0x00, 0x08)) | set(range(0x78, 0x80))

    W = gx + grid_w + 60
    H = gy + 8 * cell + 120
    f = [text(W / 2, 32, "Карта 7-бітних адрес: 0x00…0x7F", size=16, bold=True)]
    f.append(text(W / 2, 54, "кілька діапазонів зарезервовано, лишається ≈112 придатних адрес",
                  size=12, color=MUTED, italic=False))

    for addr in range(0x00, 0x80):
        r, c = addr // cols, addr % cols
        x, y = gx + c * cell, gy + r * cell
        if addr in reserved:
            fill, stroke, tcol, bold = "#f4dada", POS, POS, False
        elif addr in examples:
            fill, stroke, tcol, bold = "#dfe7fb", NEG, INK, True
        else:
            fill, stroke, tcol, bold = BG, MUTED, INK, False
        f.append(rect(x, y, cell, cell, fill=fill, stroke=stroke, sw=1, rx=0))
        f.append(text(x + cell / 2, y + cell / 2 + 4, "%02X" % addr,
                      size=11, color=tcol, bold=bold))

    # легенда
    leg_y = gy + 8 * cell + 16
    f.append(rect(gx, leg_y, 16, 16, fill="#f4dada", stroke=POS, sw=1, rx=0))
    f.append(text(gx + 24, leg_y + 13, "зарезервовано (0x00–0x07, 0x78–0x7F)",
                  size=11.5, anchor="start"))
    f.append(rect(gx + 360, leg_y, 16, 16, fill="#dfe7fb", stroke=NEG, sw=1, rx=0))
    f.append(text(gx + 384, leg_y + 13, "приклади реальних давачів", size=11.5, anchor="start"))

    b = fitbox(gx - 40, leg_y + 36, grid_w + 80, 32,
               "128 клітин − 16 зарезервованих = 112 придатних адрес на одну шину",
               size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "addr-map.svg"), W, H, *f)


# ── 7. I2C-сканер: перебрати адреси й знайти, хто відгукується ───────────────
def fig_scanner():
    W, H = 840, 360
    f = [text(W / 2, 30, "I2C-сканер: гукнути кожну адресу й глянути, хто відгукнеться",
              size=16, bold=True)]

    # «термінал» зліва
    tx, ty, tw, th = 90, 70, 350, 220
    f.append(rect(tx, ty, tw, th, fill="#1e2330", stroke="#111", sw=2, rx=10))
    f.append(text(tx + 20, ty + 32, "Scanning I2C bus...", size=12.5, bold=True,
                  color="#7fd0ff", anchor="start"))
    for i, addr in enumerate(("0x3C", "0x68", "0x76")):
        f.append(text(tx + 20, ty + 62 + i * 26, "found device at " + addr,
                      size=12, color="#9be39b", anchor="start"))
    f.append(text(tx + 20, ty + 150, "3 devices found.", size=12.5, bold=True,
                  color="#e8e8e8", anchor="start"))
    f.append(text(tx + 20, ty + 178, "_", size=13, bold=True, color="#7fd0ff", anchor="start"))

    # «як це працює» справа
    rx, ry, rw, rh = 480, 70, 280, 220
    f.append(rect(rx, ry, rw, rh, fill=FILL, stroke=MUTED, sw=1.4, rx=10))
    f.append(text(rx + rw / 2, ry + 26, "як це працює", size=12.5, bold=True))
    steps = [
        ("1. для кожної адреси —", INK, False),
        ("   старт + адреса + W", MUTED, False),
        ("2. є ACK → пристрій є", FIELD, True),
        ("3. NACK → нікого нема", POS, True),
        ("4. стоп, наступна адреса", INK, False),
    ]
    for i, (s, col, bold) in enumerate(steps):
        f.append(text(rx + 18, ry + 56 + i * 26, s, size=11, color=col,
                      bold=bold, anchor="start"))
    f.append(text(rx + 18, ry + 200, "(нічого не пишемо в чіп)", size=10,
                  color=MUTED, anchor="start", italic=True))

    b = fitbox(70, H - 46, W - 140, 34,
               "не знаєш адресу давача чи лінія мовчить? запусти сканер — це перший крок налагодження",
               size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "scanner.svg"), W, H, *f)


if __name__ == "__main__":
    fig_addr_byte()
    fig_select()
    fig_rw()
    fig_seven_vs_eight()
    fig_addr_pins()
    fig_addr_map()
    fig_scanner()
    print("OK: 7 figures ->", IMG)

# -*- coding: utf-8 -*-
"""Фігури до теми «Транзакція I2C».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── спільний помічник: рамка-байт на «стрічці» обміну ────────────────────────
def cell(f, x, y, w, h, label, sub, fill, stroke, tcol=INK):
    f.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=6))
    f.append(text(x + w / 2, y + h / 2 - 2, label, size=13, bold=True, color=tcol))
    if sub:
        f.append(text(x + w / 2, y + h + 16, sub, size=10.5, color=MUTED))


# ── 1. Чіп зсередини — набір пронумерованих регістрів ────────────────────────
def fig_registers():
    W, H = 820, 360
    f = [text(W / 2, 30, "I2C-пристрій зсередини — набір пронумерованих регістрів",
              size=16, bold=True)]

    regs = [("0x6B", "PWR_MGMT", "налаштування", FIELD, "#eef6ef"),
            ("0x1C", "CONFIG",   "налаштування", FIELD, "#eef6ef"),
            ("0x3B", "DATA_XH",  "дані",          NEG,   "#e9eefb"),
            ("0x3C", "DATA_XL",  "дані",          NEG,   "#e9eefb"),
            ("0x3A", "STATUS",   "стан",          MUTED, FILL),
            ("0x75", "WHO_AM_I", "це справді він", POS,   "#fbecec")]

    bw, bh, bx, by, gap = 116, 64, 70, 90, 8
    perrow = 3
    for i, (num, name, role, col, fill) in enumerate(regs):
        r, c = i // perrow, i % perrow
        x = bx + c * (bw + gap)
        y = by + r * (bh + 56)
        f.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.8, rx=6))
        f.append(text(x + bw / 2, y + 24, num, size=13, bold=True, color=col))
        f.append(text(x + bw / 2, y + 46, name, size=12, bold=True))
        f.append(text(x + bw / 2, y + bh + 16, role, size=10.5, color=MUTED))

    b = fitbox(70, H - 60, W - 140, 46,
               ["Доступ до кожної комірки — за її НОМЕРОМ, точно як до комірки пам'яті за адресою.",
                "Одні регістри керують давачем, інші віддають виміри, ще інші кажуть про стан."],
               size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "registers.svg"), W, H, *f)


# ── 2. Запис у регістр: номер регістра, потім дані ──────────────────────────
def fig_write():
    W, H = 880, 280
    f = [text(W / 2, 30, "Запис у регістр: спершу номер, тоді дані", size=16, bold=True)]

    y, h = 90, 56
    seq = [("S", "старт", FIELD, "#eef6ef"),
           ("0x68 +W", "адреса, пишемо", NEG, "#e9eefb"),
           ("ACK", "", MUTED, FILL),
           ("0x6B", "номер регістра", POS, "#fbecec"),
           ("ACK", "", MUTED, FILL),
           ("0x01", "дані", NEG, "#e9eefb"),
           ("ACK", "", MUTED, FILL),
           ("P", "стоп", FIELD, "#eef6ef")]
    widths = [50, 110, 56, 84, 56, 72, 56, 50]
    x = 60
    for (lab, sub, col, fill), w in zip(seq, widths):
        cell(f, x, y, w, h, lab, sub, fill, col, tcol=col if lab in ("S", "P") else INK)
        x += w + 10
    end = x - 10

    f.append(line(60, y + h + 40, end, y + h + 40, color=MUTED, sw=1.4))
    f.append(text(60, y + h + 56, "напрямок у часі →", size=10.5, color=MUTED, anchor="start"))

    b = fitbox(60, H - 56, W - 120, 42,
               ['Читається як «у пристрій 0x68, у регістр 0x6B, поклади 0x01».',
                "Так, наприклад, давач виводять зі сну, увімкнувши його регістр живлення."],
               size=11.5, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "write.svg"), W, H, *f)


# ── 3. Читання з регістра: дві фази й повторний старт ───────────────────────
def fig_read():
    W, H = 900, 340
    f = [text(W / 2, 30, "Читання з регістра: дві фази, зшиті повторним стартом",
              size=16, bold=True)]

    y, h = 96, 56
    # фаза 1 — холостий запис
    f.append(rect(54, y - 24, 372, h + 56, fill="none", stroke=FIELD, sw=1.4, rx=10))
    f.append(text(240, y - 32, "Фаза 1 — вказати регістр (запис)", size=11.5, bold=True, color=FIELD))
    p1 = [("S", "старт", FIELD, "#eef6ef"), ("0x68 +W", "адреса, пишемо", NEG, "#e9eefb"),
          ("ACK", "", MUTED, FILL), ("0x3B", "номер регістра", POS, "#fbecec"),
          ("ACK", "", MUTED, FILL)]
    w1 = [50, 110, 50, 76, 50]
    x = 70
    for (lab, sub, col, fill), w in zip(p1, w1):
        cell(f, x, y, w, h, lab, sub, fill, col, tcol=col if lab == "S" else INK)
        x += w + 8

    # шов — повторний старт
    sr_x = x + 6
    f.append(rect(sr_x, y - 6, 56, h + 12, fill="#fff4e0", stroke="#c87f0a", sw=2.2, rx=8))
    f.append(text(sr_x + 28, y + h / 2 - 2, "Sr", size=14, bold=True, color="#c87f0a"))
    f.append(text(sr_x + 28, y + h + 18, "повт. старт", size=10, bold=True, color="#c87f0a"))
    f.append(text(sr_x + 28, y - 16, "БЕЗ стопу", size=10, bold=True, color="#c87f0a"))
    x = sr_x + 56 + 8

    # фаза 2 — читання
    f.append(rect(x - 8, y - 24, W - (x - 8) - 40, h + 56, fill="none", stroke=NEG, sw=1.4, rx=10))
    f.append(text((x - 8 + W - 40) / 2, y - 32, "Фаза 2 — читати дані", size=11.5, bold=True, color=NEG))
    p2 = [("0x68 +R", "адреса, читаємо", NEG, "#e9eefb"), ("ACK", "", MUTED, FILL),
          ("дані", "байт із регістра", NEG, "#dfe7fb"), ("NACK", "", MUTED, FILL),
          ("P", "стоп", FIELD, "#eef6ef")]
    w2 = [110, 50, 90, 56, 50]
    for (lab, sub, col, fill), w in zip(p2, w2):
        cell(f, x, y, w, h, lab, sub, fill, col, tcol=col if lab == "P" else INK)
        x += w + 8

    b = fitbox(60, H - 58, W - 120, 44,
               ["Між фазами немає стопу — лише Sr, тож «вказав регістр» і «читаю» зшиті в одне неподільне ціле.",
                "Стоп на мить звільнив би шину, і чужий ведучий міг би вклинитися й збити покажчик регістра."],
               size=11.5, fill="#fff4e0", stroke="#c87f0a")
    f.append(b)
    render(os.path.join(IMG, "read.svg"), W, H, *f)


# ── 4. Пакетне читання: авто-інкремент покажчика ────────────────────────────
def fig_burst():
    W, H = 860, 360
    f = [text(W / 2, 30, "Пакетне читання: вказав регістр раз — покажчик сам росте",
              size=16, bold=True)]

    # стовпчик регістрів у чіпі
    rx, ry, rw, rh = 90, 80, 150, 36
    names = [("0x3B", "X_H"), ("0x3C", "X_L"), ("0x3D", "Y_H"),
             ("0x3E", "Y_L"), ("0x3F", "Z_H"), ("0x40", "Z_L")]
    for i, (num, nm) in enumerate(names):
        y = ry + i * (rh + 6)
        f.append(rect(rx, y, rw, rh, fill="#e9eefb", stroke=NEG, sw=1.6, rx=5))
        f.append(text(rx + 40, y + rh / 2 + 4, num, size=11.5, bold=True, color=NEG))
        f.append(text(rx + 108, y + rh / 2 + 4, nm, size=11.5, bold=True))

    # покажчик і авто-інкремент
    px = rx + rw + 30
    f.append(text(px, ry - 16, "покажчик +1", size=11, bold=True, color=POS, anchor="start"))
    for i in range(len(names)):
        y = ry + i * (rh + 6) + rh / 2
        f.append(arrow(px + 70, y, px + 6, y, color=POS, sw=1.8))
    f.append(line(px + 70, ry + rh / 2, px + 70, ry + 5 * (rh + 6) + rh / 2, color=POS, sw=1.6, dash="4,3"))

    # права частина — один обмін на 6 байтів
    bx = px + 130
    f.append(text(bx, ry - 16, "один обмін:", size=12, bold=True, anchor="start"))
    lines = ["S · 0x68+W · 0x3B · ACK", "Sr · 0x68+R", "→ X_H X_L Y_H Y_L Z_H Z_L", "NACK · P"]
    for i, ln in enumerate(lines):
        f.append(text(bx, ry + 16 + i * 26, ln, size=12, anchor="start",
                      color=POS if i == 2 else INK, bold=(i == 2)))

    b = fitbox(60, H - 78, W - 120, 64,
               ["Більшість чіпів збільшують покажчик на 1 після кожного прочитаного байта.",
                "Шість байтів трьох осей знято фактично з одного моменту — не «розмазано» паузами.",
                "Одне читання замість шести: швидше Й узгоджено в часі. Шукай у даташиті «burst»/«auto-increment»."],
               size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "burst.svg"), W, H, *f)


# ── 5. 16-бітне значення з двох байтів ──────────────────────────────────────
def fig_multibyte():
    W, H = 820, 320
    f = [text(W / 2, 30, "16-бітне значення з двох регістрів: зібрати в одне число",
              size=16, bold=True)]

    # два байти
    y, bw, bh = 90, 150, 54
    f.append(rect(120, y, bw, bh, fill="#e9eefb", stroke=NEG, sw=1.8, rx=6))
    f.append(text(120 + bw / 2, y - 10, "регістр 0x3B", size=11, bold=True, color=NEG))
    f.append(text(120 + bw / 2, y + bh / 2 + 5, "0x12", size=16, bold=True))
    f.append(text(120 + bw / 2, y + bh + 18, "старший байт", size=10.5, color=MUTED))

    f.append(rect(360, y, bw, bh, fill="#e9eefb", stroke=NEG, sw=1.8, rx=6))
    f.append(text(360 + bw / 2, y - 10, "регістр 0x3C", size=11, bold=True, color=NEG))
    f.append(text(360 + bw / 2, y + bh / 2 + 5, "0x34", size=16, bold=True))
    f.append(text(360 + bw / 2, y + bh + 18, "молодший байт", size=10.5, color=MUTED))

    # операція збирання
    f.append(text(120 + bw / 2, y + bh + 56, "<< 8", size=12.5, bold=True, color=POS))
    f.append(text(280, y + bh + 56, "|", size=18, bold=True))
    f.append(arrow(195, y + bh + 78, 560, y + bh + 78, color=INK, sw=1.8))

    f.append(rect(595, y, 150, bh, fill="#eef6ef", stroke=FIELD, sw=2, rx=6))
    f.append(text(595 + 75, y + bh / 2 + 5, "0x1234", size=16, bold=True, color=FIELD))
    f.append(text(595 + 75, y + bh + 18, "= 4660", size=11, color=MUTED))

    b = fitbox(60, H - 96, W - 120, 82,
               ["value = (старший << 8) | молодший = (0x12 << 8) | 0x34 = 0x1234.",
                "Пастка 1 — ПОРЯДОК байтів: інші чіпи дають молодший першим (дістанеш 0x3412).",
                "Пастка 2 — ЗНАК: виміри часто від'ємні, тож це int16 у доповняльному коді, не uint16."],
               size=11.5, fill="#fbecec", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "multibyte.svg"), W, H, *f)


# ── 6. Рядок коду ↔ фаза на шині ────────────────────────────────────────────
def fig_code_phases():
    W, H = 900, 320
    f = [text(W / 2, 30, "Кожен рядок коду — це фаза на шині", size=16, bold=True)]

    rows = [("i2c_write(0x68, 0x3B)", "S · 0x68+W · 0x3B", "вказати покажчик", NEG),
            ("repeated start (без STOP)", "Sr", "не відпускати шину", "#c87f0a"),
            ("i2c_read(0x68, buf, 2)", "0x68+R · дані · дані · NACK · P", "читати 2 байти", FIELD)]
    y0, rh = 86, 64
    for i, (code, bus, note, col) in enumerate(rows):
        y = y0 + i * (rh + 10)
        f.append(rect(60, y, 360, rh, fill="#1e2330", stroke="#111", sw=1.6, rx=8))
        f.append(text(78, y + rh / 2 + 5, code, size=13, color="#9be39b", anchor="start"))
        f.append(arrow(430, y + rh / 2, 486, y + rh / 2, color=col, sw=2.2))
        f.append(rect(492, y, W - 492 - 50, rh, fill="#f4f6f8", stroke=col, sw=1.8, rx=8))
        f.append(text(492 + (W - 492 - 50) / 2, y + rh / 2 - 4, bus, size=12, bold=True))
        f.append(text(492 + (W - 492 - 50) / 2, y + rh / 2 + 16, note, size=10.5, color=MUTED))

    b = fitbox(60, H - 50, W - 120, 36,
               "Та «відсутність стопу» між фазами (Sr) і є серце читання регістра: прибери її — і чіп губить покажчик.",
               size=11.5, fill="#fff4e0", stroke="#c87f0a")
    f.append(b)
    render(os.path.join(IMG, "code-phases.svg"), W, H, *f)


# ── 7. Таймінг і частота опитування ─────────────────────────────────────────
def fig_timing():
    W, H = 860, 320
    f = [text(W / 2, 30, "Скільки триває читання й як часто можна опитувати",
              size=16, bold=True)]

    # «бюджет тактів» однією стрічкою
    y, h = 86, 44
    parts = [("S", 1, FIELD), ("0x68+W", 9, NEG), ("0x3B", 9, POS),
             ("Sr", 1, "#c87f0a"), ("0x68+R", 9, NEG), ("дані", 9, "#27ae60"), ("дані", 9, "#27ae60")]
    total = sum(p[1] for p in parts)
    x, scale = 70, (W - 140) / total
    for lab, w9, col in parts:
        ww = w9 * scale
        fill = {FIELD: "#eef6ef", NEG: "#e9eefb", POS: "#fbecec",
                "#c87f0a": "#fff4e0", "#27ae60": "#eef6ef"}.get(col, FILL)
        f.append(rect(x, y, ww - 3, h, fill=fill, stroke=col, sw=1.6, rx=4))
        f.append(text(x + ww / 2, y + h / 2 + 4, lab, size=10.5, bold=True, color=col))
        x += ww
    f.append(text(W / 2, y + h + 22, "≈ %d тактів на читання двобайтового виміру (5 байтів × 9 + старти)" % total,
                  size=12, bold=True))

    # дві частоти
    yy = y + h + 56
    f.append(rect(90, yy, 320, 56, fill=FILL, stroke=LINE, sw=1.6, rx=8))
    f.append(text(250, yy + 22, "100 кГц: 50 × 10 мкс ≈ 0.50 мс", size=12, bold=True))
    f.append(text(250, yy + 42, "→ до ~2000 читань/с (теоретично)", size=11, color=MUTED))
    f.append(rect(W - 410, yy, 320, 56, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(W - 250, yy + 22, "400 кГц: 50 × 2.5 мкс ≈ 0.13 мс", size=12, bold=True, color=FIELD))
    f.append(text(W - 250, yy + 42, "→ до ~8000 читань/с (теоретично)", size=11, color=MUTED))

    b = fitbox(60, H - 44, W - 120, 32,
               "Навіть скромні 100 кГц легко тягнуть сотні опитувань давача за секунду — для більшості задач удосталь.",
               size=11.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "timing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_registers()
    fig_write()
    fig_read()
    fig_burst()
    fig_multibyte()
    fig_code_phases()
    fig_timing()
    print("OK: 7 фігур у", IMG)

# -*- coding: utf-8 -*-
"""Фігури до теми «CMOS-матриця».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Активний піксель: підсилювач у кожній комірці ─────────────────────────
def fig_active_pixel():
    W, H = 760, 420
    f = [text(W / 2, 26, "Активний піксель: підсилювач у самій комірці", size=16, bold=True)]

    # рамка пікселя
    px, py, pw, ph = 70, 70, 470, 270
    f.append(rect(px, py, pw, ph, fill="#fbfbfd", stroke=INK, sw=1.8, rx=12))
    f.append(text(px + pw / 2, py + 22, "один піксель", size=11, color=MUTED, italic=True))

    # фотодіод (відерце)
    f.append(circle(px + 95, py + 150, 46, fill="#dbeafe", stroke=NEG, sw=2))
    f.append(mtext(px + 95, py + 146, ["фото-", "діод"], size=11, color=NEG, lh=1.25))
    f.append(text(px + 95, py + 210, "накопичує заряд", size=9.5, color=MUTED))

    # транзистор скидання (зверху)
    f.append(rect(px + 60, py + 52, 110, 30, fill="#fef3c7", stroke="#d98a00", sw=1.5, rx=5))
    f.append(text(px + 115, py + 71, "скидання", size=9.5, color="#b06b00", bold=True))
    f.append(line(px + 95, py + 104, px + 95, py + 82, color="#d98a00", sw=1.5))

    # повторювач
    f.append(rect(px + 215, py + 110, 120, 78, fill="#eafaef", stroke=FIELD, sw=1.8, rx=8))
    f.append(mtext(px + 275, py + 140, ["витоковий", "повторювач"], size=10.5,
                   color="#15803d", bold=True, lh=1.3))
    f.append(text(px + 275, py + 178, "заряд → напруга", size=9, color=MUTED))
    # від фотодіода на затвор повторювача
    f.append(arrow(px + 141, py + 150, px + 213, py + 150, color=INK, sw=1.6))
    f.append(text(px + 178, py + 138, "читає,", size=9, color=MUTED))
    f.append(text(px + 178, py + 167, "не виливає", size=9, color=MUTED))

    # транзистор вибору рядка
    f.append(rect(px + 360, py + 124, 90, 50, fill="white", stroke=POS, sw=1.6, rx=6))
    f.append(mtext(px + 405, py + 144, ["вибір", "рядка"], size=9.5, color=POS, bold=True, lh=1.25))
    f.append(arrow(px + 335, py + 149, px + 358, py + 149, color=INK, sw=1.6))

    # вихід у стовпцеву лінію
    f.append(arrow(px + 450, py + 149, px + pw + 30, py + 149, color=POS, sw=2))
    f.append(text(px + pw + 38, py + 144, "у стовпцеву", size=9.5, color=POS, anchor="start"))
    f.append(text(px + pw + 38, py + 160, "лінію", size=9.5, color=POS, anchor="start"))

    f.append(text(W / 2, H - 14,
                  "Підсилювач у кожному пікселі читає заряд як напругу, не чіпаючи його, — це й робить піксель «активним».",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "active-pixel.svg"), W, H, *f)


# ── 2. Рядково-стовпцеве зчитування крізь стовпцеві АЦП ──────────────────────
def fig_row_column_readout():
    W, H = 780, 470
    f = [text(W / 2, 26, "Зчитування рядок за рядком крізь стовпцеві перетворювачі",
              size=15.5, bold=True)]

    # сітка пікселів
    cols, rows = 6, 5
    cell = 46
    gx, gy = 150, 70
    active = 2  # активний рядок (індекс)

    for r in range(rows):
        for c in range(cols):
            x = gx + c * cell
            y = gy + r * cell
            fill = "#fdecea" if r == active else "white"
            stroke = POS if r == active else "#d1d5db"
            sw = 1.6 if r == active else 1.0
            f.append(rect(x, y, cell - 4, cell - 4, fill=fill, stroke=stroke, sw=sw, rx=3))

    # лінії вибору рядків (ліворуч)
    for r in range(rows):
        y = gy + r * cell + (cell - 4) / 2
        col = POS if r == active else "#cbd5e1"
        sw = 2.2 if r == active else 1.1
        f.append(line(gx - 56, y, gx, y, color=col, sw=sw))
    f.append(text(gx - 60, gy - 16, "вибір", size=10, color=INK, anchor="end"))
    f.append(text(gx - 60, gy - 2, "рядка", size=10, color=INK, anchor="end"))
    f.append(text(gx - 58, gy + active * cell + (cell - 4) / 2 - 8,
                  "увімк", size=9, color=POS, anchor="end", bold=True))

    # стовпцеві лінії вниз до АЦП
    grid_bottom = gy + rows * cell
    for c in range(cols):
        x = gx + c * cell + (cell - 4) / 2
        f.append(line(x, grid_bottom - 4, x, grid_bottom + 20, color="#94a3b8", sw=1.3))

    # ряд стовпцевих перетворювачів
    ay = grid_bottom + 20
    for c in range(cols):
        x = gx + c * cell
        f.append(rect(x, ay, cell - 4, 34, fill="#eafaef", stroke=FIELD, sw=1.4, rx=4))
        f.append(text(x + (cell - 4) / 2, ay + 22, "АЦП", size=9.5, color="#15803d", bold=True))
    f.append(text(gx + cols * cell + 14, ay + 19,
                  "по одному на стовпець", size=10, color="#15803d", anchor="start"))

    # вихід — потік чисел
    f.append(arrow(gx + cols * cell / 2, ay + 38, gx + cols * cell / 2, ay + 64, color=INK, sw=2))
    f.append(text(gx + cols * cell / 2, ay + 80, "рядок чисел (паралельно)", size=10.5,
                  color=INK, bold=True))

    f.append(text(W / 2, H - 12,
                  "Увімкнули рядок → усі його пікселі віддали напругу в стовпці → стовпцеві АЦП оцифрували рядок воднораз. Тоді наступний рядок.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "row-column-readout.svg"), W, H, *f)


# ── 3. 3T проти 4T: затвор переносу розв'язує накопичення й зчитування ───────
def fig_pixel_3t_4t():
    W, H = 880, 410
    f = [text(W / 2, 26, "3T проти 4T: розв'язати накопичення від зчитування", size=15.5, bold=True)]

    by, bh = 66, 264

    # ── 3T ──
    x, bw = 40, 360
    f.append(rect(x, by, bw, bh, fill="#fff5e6", stroke="#d98a00", sw=1.8, rx=12))
    f.append(text(x + bw / 2, by + 26, "3T-піксель", size=13, color="#b06b00", bold=True))
    # одне відерце = і накопичення, і зчитування
    f.append(circle(x + 100, by + 128, 50, fill="#fde68a", stroke="#d98a00", sw=2))
    f.append(mtext(x + 100, by + 120, ["фотодіод", "= вузол", "зчитування"], size=9.5,
                   color="#b06b00", lh=1.3))
    f.append(rect(x + 210, by + 98, 115, 64, fill="white", stroke=MUTED, sw=1.4, rx=6))
    f.append(mtext(x + 267, by + 124, ["повто-", "рювач"], size=9.5, color=MUTED, lh=1.25))
    f.append(arrow(x + 152, by + 128, x + 208, by + 128, color=INK, sw=1.5))
    f.append(mtext(x + bw / 2, by + bh - 34,
                   ["скидання лишає випадкову зернинку —", "шум скидання змішаний із сигналом"],
                   size=9.5, color="#b06b00", lh=1.35))

    # ── 4T ──
    x, bw = 480, 360
    f.append(rect(x, by, bw, bh, fill="#eafaef", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(x + bw / 2, by + 26, "4T-піксель", size=13, color="#15803d", bold=True))
    yc = by + 138
    # фотодіод (пінований)
    f.append(circle(x + 62, yc, 38, fill="#bbf7d0", stroke=FIELD, sw=2))
    f.append(mtext(x + 62, yc - 4, ["пінований", "фотодіод"], size=9, color="#15803d", lh=1.25))
    # затвор переносу
    f.append(rect(x + 116, yc - 18, 36, 36, fill="#fef3c7", stroke=POS, sw=1.8, rx=4))
    f.append(text(x + 134, yc + 4, "TG", size=10, color=POS, bold=True))
    f.append(mtext(x + 134, yc + 40, ["затвор", "переносу"], size=9, color=POS, lh=1.2))
    # плавуча дифузія
    f.append(circle(x + 192, yc, 17, fill="#dbeafe", stroke=NEG, sw=1.8))
    f.append(text(x + 192, yc + 4, "FD", size=10, color=NEG, bold=True))
    f.append(mtext(x + 192, yc - 44, ["плавуча", "дифузія"], size=9, color=NEG, lh=1.2))
    # повторювач
    f.append(rect(x + 232, yc - 28, 105, 56, fill="white", stroke=MUTED, sw=1.4, rx=6))
    f.append(mtext(x + 284, yc - 4, ["повто-", "рювач"], size=9.5, color=MUTED, lh=1.25))
    # стрілки потоку
    f.append(arrow(x + 102, yc, x + 115, yc, color=INK, sw=1.4))
    f.append(arrow(x + 153, yc, x + 174, yc, color=INK, sw=1.4))
    f.append(arrow(x + 210, yc, x + 231, yc, color=INK, sw=1.4))
    f.append(mtext(x + bw / 2, by + bh - 34,
                   ["накопичення (фотодіод) відділене", "від зчитування (FD) — можна відняти шум"],
                   size=9.5, color="#15803d", lh=1.35))

    f.append(text(W / 2, H - 12,
                  "Затвор переносу переливає заряд із фотодіода у плавучу дифузію лише в мить зчитування — і це уможливлює CDS.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "pixel-3t-4t.svg"), W, H, *f)


# ── 4. Корельована подвійна вибірка: відняти шум скидання ────────────────────
def fig_cds_timing():
    W, H = 800, 420
    f = [text(W / 2, 26, "Корельована подвійна вибірка: відняти шум скидання", size=15.5, bold=True)]

    base = 250          # рівень осі
    lx, rx = 90, 710

    # вісь
    f.append(line(lx, base, rx, base, color=INK, sw=1.5))
    f.append(arrow(lx, base, lx, 80, color=INK, sw=1.4))
    f.append(text(lx - 10, 90, "рівень", size=10, color=INK, anchor="end"))
    f.append(text(rx, base + 22, "час →", size=10, color=MUTED, anchor="end"))

    noise = 28          # «зернинка» шуму скидання (однакова в обох відліках)
    sig = 90            # сигнал

    # фаза 1: скидання
    f.append(text(170, 70, "1. скидання", size=11, bold=True, color="#b06b00"))
    f.append(line(120, base, 230, base, color="#cbd5e1", sw=2, dash="4,3"))
    # рівень після скидання = база - noise (трохи "брудний")
    y_reset = base - noise
    f.append(line(230, y_reset, 360, y_reset, color="#d98a00", sw=3))
    f.append(text(295, y_reset - 12, "порожній рівень", size=9.5, color="#b06b00"))
    f.append(text(295, y_reset + 18, "(лише шум скидання)", size=9, color=MUTED))
    # перша вибірка
    f.append(circle(300, y_reset, 6, fill=POS, stroke="white", sw=1.4))
    f.append(text(300, base + 18, "вибірка A", size=9.5, color=POS, bold=True))
    f.append(line(300, y_reset, 300, base, color=POS, sw=1, dash="3,3"))

    # фаза 2: перенос заряду
    f.append(text(520, 70, "2. перенос + сигнал", size=11, bold=True, color="#15803d"))
    f.append(arrow(370, y_reset, 430, y_reset - sig, color=FIELD, sw=2))
    f.append(text(400, y_reset - sig / 2, "перелив", size=9, color="#15803d", anchor="start"))
    # рівень із сигналом = той самий шум + сигнал
    y_sig = base - noise - sig
    f.append(line(430, y_sig, 600, y_sig, color=FIELD, sw=3))
    f.append(text(515, y_sig - 12, "рівень із сигналом", size=9.5, color="#15803d"))
    f.append(text(515, y_sig + 18, "(той самий шум + сигнал)", size=9, color=MUTED))
    # друга вибірка
    f.append(circle(520, y_sig, 6, fill=POS, stroke="white", sw=1.4))
    f.append(text(520, base + 18, "вибірка B", size=9.5, color=POS, bold=True))
    f.append(line(520, y_sig, 520, base, color=POS, sw=1, dash="3,3"))

    # різниця = чистий сигнал
    f.append(rect(lx + 20, base + 40, rx - lx - 40, 48, fill="#f4f4f5", stroke=INK, sw=1.4, rx=10))
    f.append(text(W / 2, base + 60, "B − A = чистий сигнал  (зернинка шуму скидання однакова → вираховується)",
                  size=12, bold=True))
    f.append(text(W / 2, base + 79,
                  "заразом прибирається й сталий зсув повторювача та повільний 1/f-дрейф",
                  size=10, color=MUTED))

    render(os.path.join(IMG, "cds-timing.svg"), W, H, *f)


# ════════════════ ДЕТАЛЬНА ВЕРСІЯ (cmos-matrix-d.md) ════════════════

# ── D1. Транзистори 4T-пікселя поіменно ──────────────────────────────────────
def fig_pixel_4t_transistors():
    W, H = 820, 430
    f = [text(W / 2, 26, "Транзистори 4T-пікселя поіменно", size=16, bold=True)]

    # лінія живлення зверху
    f.append(line(120, 70, 700, 70, color=POS, sw=2))
    f.append(text(708, 74, "V_DD", size=11, color=POS, anchor="start", bold=True))

    yc = 220   # вісь основного ланцюга

    # пінований фотодіод
    f.append(circle(150, yc, 48, fill="#bbf7d0", stroke=FIELD, sw=2.2))
    f.append(mtext(150, yc - 4, ["пінований", "фотодіод", "(PPD)"], size=10, color="#15803d", lh=1.25))
    f.append(text(150, yc + 70, "накопичує заряд", size=9.5, color=MUTED))

    # затвор переносу TG
    f.append(rect(228, yc - 22, 40, 44, fill="#fef3c7", stroke=POS, sw=1.8, rx=5))
    f.append(text(248, yc + 4, "TG", size=11, color=POS, bold=True))
    f.append(mtext(248, yc + 50, ["затвор", "переносу"], size=9.5, color=POS, lh=1.2))

    # плавуча дифузія FD
    f.append(circle(330, yc, 20, fill="#dbeafe", stroke=NEG, sw=2))
    f.append(text(330, yc + 4, "FD", size=11, color=NEG, bold=True))
    f.append(mtext(330, yc - 52, ["плавуча", "дифузія"], size=9.5, color=NEG, lh=1.2))

    # скидання RST (вгору до VDD)
    f.append(rect(300, yc - 120, 60, 34, fill="white", stroke="#d98a00", sw=1.6, rx=6))
    f.append(text(330, yc - 99, "RST", size=10.5, color="#b06b00", bold=True))
    f.append(line(330, yc - 20, 330, yc - 86, color="#d98a00", sw=1.5))
    f.append(line(330, yc - 120, 330, 70, color="#d98a00", sw=1.5))
    f.append(text(366, yc - 103, "скидання FD", size=9.5, color="#b06b00", anchor="start"))

    # витоковий повторювач SF
    f.append(rect(420, yc - 30, 110, 60, fill="#eafaef", stroke=FIELD, sw=1.8, rx=8))
    f.append(mtext(475, yc - 6, ["витоковий", "повторювач (SF)"], size=10, color="#15803d", bold=True, lh=1.25))
    # затвор SF під'єднано до FD
    f.append(line(350, yc, 420, yc, color=INK, sw=1.4))
    f.append(text(385, yc - 8, "затвор", size=9, color=MUTED))
    # стік SF до VDD
    f.append(line(475, yc - 30, 475, 70, color=POS, sw=1.3))

    # вибір рядка SEL
    f.append(rect(560, yc - 25, 90, 50, fill="white", stroke=POS, sw=1.6, rx=6))
    f.append(mtext(605, yc - 2, ["вибір", "рядка (SEL)"], size=9.5, color=POS, bold=True, lh=1.2))
    f.append(arrow(530, yc, 558, yc, color=INK, sw=1.5))

    # вихід у стовпцеву лінію
    f.append(arrow(650, yc, 715, yc, color=POS, sw=2))
    f.append(mtext(720, yc - 4, ["у стовпцеву", "лінію"], size=9.5, color=POS, anchor="start", lh=1.2))

    # стрілки потоку заряду
    f.append(arrow(198, yc, 226, yc, color=INK, sw=1.5))
    f.append(arrow(270, yc, 308, yc, color=INK, sw=1.5))
    f.append(text(289, yc - 9, "перенос", size=9, color=POS))

    f.append(text(W / 2, H - 14,
                  "Затвор переносу на мить відчиняється й переливає весь заряд PPD у FD — лише тоді повторювач його й читає.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "pixel-4t-transistors.svg"), W, H, *f)


# ── D2. Послідовність зчитування рядка: сигнали за тактами ───────────────────
def fig_readout_sequence():
    W, H = 820, 440
    f = [text(W / 2, 26, "Один цикл зчитування рядка (4T): сигнали за тактами", size=15.5, bold=True)]

    lx, rx = 150, 760
    rows = [("SEL", 80), ("RST", 140), ("TG", 200)]
    # три цифрові доріжки з імпульсами
    # SEL: увесь цикл високий
    f.append(text(lx - 12, 84, "SEL", size=11, bold=True, color=POS, anchor="end"))
    f.append('<polyline points="%d,%d %d,%d %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (lx, 96, 175, 96, 175, 72, 735, 72, 735, 96, POS))
    # RST: короткий імпульс на початку
    f.append(text(lx - 12, 144, "RST", size=11, bold=True, color="#b06b00", anchor="end"))
    f.append('<polyline points="%d,%d %d,%d %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (lx, 156, 210, 156, 210, 132, 250, 132, 250, 156, "#d98a00"))
    f.append('<polyline points="250,156 760,156" fill="none" stroke="#d98a00" stroke-width="2.2"/>')
    # TG: короткий імпульс посередині
    f.append(text(lx - 12, 204, "TG", size=11, bold=True, color=FIELD, anchor="end"))
    f.append('<polyline points="%d,%d %d,%d %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (lx, 216, 430, 216, 430, 192, 470, 192, 470, 216, FIELD))
    f.append('<polyline points="470,216 760,216" fill="none" stroke="%s" stroke-width="2.2"/>' % FIELD)

    # дві миті вибірки — вертикальні лінії
    sa_x, sb_x = 300, 540
    for sx, lab, col in ((sa_x, "вибірка A", POS), (sb_x, "вибірка B", POS)):
        f.append(line(sx, 60, sx, 300, color=col, sw=1.3, dash="4,4"))
        f.append(circle(sx, 96, 5, fill=col, stroke="white", sw=1.3))
    f.append(mtext(sa_x, 280, ["опорний рівень", "(порожній: лише шум)"], size=9.5, color=POS, lh=1.25))
    f.append(mtext(sb_x, 280, ["рівень сигналу", "(той самий шум + сигнал)"], size=9.5, color=POS, lh=1.25))

    # підписи фаз під доріжками
    f.append(text(230, 250, "1. скидання FD", size=9.5, color="#b06b00"))
    f.append(text(450, 168, "2. перенос заряду", size=9.5, color="#15803d"))

    # підсумкова формула
    f.append(rect(lx - 40, 330, rx - lx + 50, 56, fill="#f4f4f5", stroke=INK, sw=1.4, rx=10))
    f.append(text(W / 2, 352, "між A і B немає скидання → теплова зернинка kTC однакова → B − A її вираховує",
                  size=11.5, bold=True))
    f.append(text(W / 2, 372, "той самий порядок «рядок за рядком» і породжує рядкову заслінку",
                  size=10, color=MUTED))

    f.append(text(W / 2, H - 12,
                  "Спершу беруть порожній відлік FD, тоді переливають заряд і беруть сигнальний — і віднімають один від одного.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "readout-sequence.svg"), W, H, *f)


# ── D3. Де ставлять АЦП + одинарно-нахилений АЦП ─────────────────────────────
def fig_column_adc():
    W, H = 840, 430
    f = [text(W / 2, 26, "Де ставлять АЦП і як працює стовпцевий", size=16, bold=True)]

    # ── ЛІВА ПОЛОВИНА: три розміщення ──
    f.append(text(210, 56, "Три розміщення АЦП", size=12.5, bold=True))

    # а) один на чіп
    ay = 78
    f.append(rect(60, ay, 130, 46, fill="white", stroke="#d1d5db", sw=1.2, rx=5))
    f.append(text(125, ay + 20, "матриця", size=9.5, color=MUTED))
    f.append(text(125, ay + 36, "пікселів", size=9.5, color=MUTED))
    f.append(rect(210, ay + 8, 70, 30, fill="#fff5e6", stroke="#d98a00", sw=1.6, rx=5))
    f.append(text(245, ay + 27, "1 АЦП", size=9.5, color="#b06b00", bold=True))
    f.append(arrow(190, ay + 23, 208, ay + 23, color=INK, sw=1.4))
    f.append(text(300, ay + 27, "вузьке місце", size=9.5, color=NEG, anchor="start"))

    # б) стовпцево-паралельний (стандарт)
    by = 150
    cols = 6
    cw = 21
    gx = 60
    for c in range(cols):
        f.append(rect(gx + c * cw, by, cw - 3, 30, fill="white", stroke="#d1d5db", sw=1))
    for c in range(cols):
        f.append(rect(gx + c * cw, by + 38, cw - 3, 24, fill="#eafaef", stroke=FIELD, sw=1.3))
    f.append(text(gx + cols * cw + 16, by + 18, "стовпці пікселів", size=9.5, color=MUTED, anchor="start"))
    f.append(text(gx + cols * cw + 16, by + 54, "АЦП на КОЖЕН стовпець", size=9.5, color="#15803d",
                  anchor="start", bold=True))
    f.append(text(gx, by - 8, "стовпцево-паралельний — стандарт", size=10, color="#15803d", bold=True))

    # в) у кожному пікселі
    py = 250
    for r in range(3):
        for c in range(5):
            f.append(rect(gx + c * 24, py + r * 24, 21, 21, fill="#fde68a", stroke="#d98a00", sw=1))
    f.append(text(gx + 5 * 24 + 16, py + 24, "АЦП у кожному пікселі —", size=9.5, color="#b06b00",
                  anchor="start"))
    f.append(text(gx + 5 * 24 + 16, py + 40, "задорого по площі", size=9.5, color="#b06b00",
                  anchor="start"))

    # розділювач
    f.append(line(430, 60, 430, 360, color="#e5e7eb", sw=1.5))

    # ── ПРАВА ПОЛОВИНА: одинарно-нахилений АЦП ──
    f.append(text(640, 56, "Одинарно-нахилений АЦП", size=12.5, bold=True))
    # осі
    ox, oy = 480, 250
    f.append(line(ox, oy, ox + 280, oy, color=INK, sw=1.4))
    f.append(arrow(ox, oy, ox, 90, color=INK, sw=1.4))
    f.append(text(ox - 8, 100, "напруга", size=9.5, color=INK, anchor="end"))
    f.append(text(ox + 280, oy + 18, "час", size=9.5, color=MUTED, anchor="end"))
    # пила
    f.append(line(ox, oy, ox + 250, 110, color="#d98a00", sw=2.2))
    f.append(text(ox + 200, 130, "спільна пила", size=9.5, color="#b06b00"))
    # рівень пікселя
    f.append(line(ox, 180, ox + 250, 180, color=NEG, sw=1.6, dash="5,4"))
    f.append(text(ox + 6, 174, "рівень пікселя", size=9, color=NEG))
    # мить рівності
    cross_x = ox + (oy - 180) / (oy - 110) * 250
    f.append(circle(cross_x, 180, 6, fill=POS, stroke="white", sw=1.4))
    f.append(line(cross_x, 180, cross_x, oy, color=POS, sw=1.2, dash="3,3"))
    f.append(text(cross_x, oy + 18, "компаратор спрацював", size=9, color=POS))
    f.append(mtext(640, 300, ["лічильник рахує, поки росте пила;", "його значення в мить рівності — код пікселя"],
                   size=9.5, color=MUTED, lh=1.35))

    f.append(text(W / 2, H - 12,
                  "Стовпцево-паралельні АЦП оцифровують рядок воднораз — звідси час рядка, а з нього перекіс рядкової заслінки.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "column-adc.svg"), W, H, *f)


# ── D4. Глобальна заслінка: вузол зберігання в кожному пікселі ───────────────
def fig_global_shutter():
    W, H = 820, 410
    f = [text(W / 2, 26, "Глобальна заслінка: вузол зберігання в кожному пікселі", size=15.5, bold=True)]

    # крок 1 — спільний імпульс переносить заряд усіх PPD у сховки
    f.append(text(210, 60, "1. усі воднораз: PPD → сховок", size=11.5, bold=True, color="#15803d"))
    # три пікселі-приклади
    for i in range(3):
        x = 70 + i * 130
        yc = 150
        f.append(circle(x, yc, 28, fill="#bbf7d0", stroke=FIELD, sw=2))
        f.append(text(x, yc + 4, "PPD", size=9, color="#15803d"))
        f.append(rect(x + 48, yc - 19, 60, 38, fill="#fef3c7", stroke=POS, sw=1.8, rx=5))
        f.append(mtext(x + 78, yc - 2, ["вузол", "зберіг."], size=9, color=POS, lh=1.15))
        f.append(arrow(x + 28, yc, x + 49, yc, color=INK, sw=1.4))
    # спільна лінія глобального переносу
    f.append(line(70, 100, 590, 100, color=POS, sw=2))
    for i in range(3):
        x = 70 + i * 130 + 78
        f.append(line(x, 100, x, 132, color=POS, sw=1.2))
    f.append(text(598, 104, "спільний імпульс", size=9.5, color=POS, anchor="start"))
    f.append(text(210, 200, "усі пікселі замикаються в ОДНУ мить", size=9.5, color=MUTED))

    # крок 2 — далі читають рядок за рядком зі сховків
    f.append(text(210, 250, "2. далі читають сховки рядок за рядком", size=11.5, bold=True, color=NEG))
    f.append(arrow(300, 215, 300, 240, color=INK, sw=1.8))

    # рамка-ціна
    f.append(rect(60, 268, 700, 86, fill="#fff5e6", stroke="#d98a00", sw=1.6, rx=10))
    f.append(text(W / 2, 290, "Ціна: вузол зберігання в КОЖНОМУ пікселі", size=11.5, bold=True, color="#b06b00"))
    f.append(mtext(W / 2, 312,
                   ["зайві транзистори (5T+) · екранування сховку від паразитного світла · менша площа фотодіода",
                    "→ нижча чутливість і вища ціна, тому масові сенсори лишаються рядковими"],
                   size=10, color="#b06b00", lh=1.45))

    f.append(text(W / 2, H - 12,
                  "Заморозити весь кадр в одну мить можна — але сховок на кожен піксель з'їдає площу фотодіода й гроші.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "global-shutter.svg"), W, H, *f)


if __name__ == "__main__":
    fig_active_pixel()
    fig_row_column_readout()
    fig_pixel_3t_4t()
    fig_cds_timing()
    fig_pixel_4t_transistors()
    fig_readout_sequence()
    fig_column_adc()
    fig_global_shutter()
    print("OK base: active-pixel, row-column-readout, pixel-3t-4t, cds-timing")
    print("OK detailed: pixel-4t-transistors, readout-sequence, column-adc, global-shutter")

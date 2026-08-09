# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

OCC_FILL, OCC_LINE = "#e8f6ee", FIELD
DEV_FILL, DEV_LINE = "#fdecea", POS
BAD_FILL = "#fdecea"


# ─────────────────────────────────────────────────────────────
# 1. Життєвий цикл області CMA: заселена → смугу виселено → смуга в пристрої
# ─────────────────────────────────────────────────────────────
def fig_lifecycle():
    W, H = 900, 350
    X0, X1 = 250, 870
    N = 20
    CW = (X1 - X0) / float(N)
    CH = 40
    LO, HI = 6, 14           # смуга під запит: комірки [6..13]

    def strip(cy, occupied, block=None, block_text=""):
        out = ""
        y = cy - CH / 2.0
        for i in range(N):
            if block and block[0] <= i < block[1]:
                continue
            f = OCC_FILL if i in occupied else BG
            s = OCC_LINE if i in occupied else "#b9c0c8"
            out += rect(X0 + i * CW, y, CW - 2, CH, fill=f, stroke=s, sw=1.2, rx=3)
        if block:
            bx = X0 + block[0] * CW
            bw = (block[1] - block[0]) * CW - 2
            out += fitbox(bx, y, bw, CH, block_text, size=13,
                          fill=DEV_FILL, stroke=DEV_LINE, sw=2)
        return out

    full = set(range(N)) - {3, 11, 17}
    rest = set(i for i in full if not (LO <= i < HI))

    body = ""
    b, _, _ = textbox(128, 100, ["Між запитами:", "у області живуть", "рухомі сторінки"], size=13)
    body += b
    body += strip(100, full)
    body += text(X0, 148, "кеш файлів, анонімні сторінки процесів — усе, що ядро вміє перенести",
                 size=12, color=MUTED, anchor="start")

    b, _, _ = textbox(128, 210, ["Запит пристрою:", "смугу ізольовано", "й виселено"], size=13)
    body += b
    body += strip(210, rest)
    bx0, bx1 = X0 + LO * CW, X0 + HI * CW - 2
    body += line(bx0, 238, bx0, 248, color=MUTED)
    body += line(bx1, 238, bx1, 248, color=MUTED)
    body += line(bx0, 248, bx1, 248, color=MUTED)
    body += text((bx0 + bx1) / 2.0, 266, "32 МіБ поспіль", size=12, color=MUTED)

    b, _, _ = textbox(128, 305, ["Буфер віддано:", "решта області", "працює далі"], size=13)
    body += b
    body += strip(305, rest, block=(LO, HI), block_text="буфер пристрою")

    return render(os.path.join(IMG, 'cma-lifecycle.svg'), W, H, body,
                  title="Область CMA у трьох станах")


# ─────────────────────────────────────────────────────────────
# 2. Шлях виділення й точка зриву
# ─────────────────────────────────────────────────────────────
def fig_alloc_path():
    W, H = 900, 510
    CX = 300
    steps = [
        ("Знайти вільну смугу", "у бітовій мапі області"),
        ("Ізолювати блоки", "нові мешканці більше не в'їжджають"),
        ("Спорожнити кеші процесорів", "вільні кадри стають видимими"),
        ("Виселити мешканців", "перенос + скидання кешу адрес"),
        ("Забрати смугу цілком", "віддати драйверові"),
    ]
    ys = [95, 175, 255, 340, 425]
    body = ""
    for (head, sub), y in zip(steps, ys):
        fill = OCC_FILL if head.startswith("Забрати") else FILL
        stroke = OCC_LINE if head.startswith("Забрати") else LINE
        b, w, h = textbox(CX, y, [head, sub], size=13, fill=fill, stroke=stroke, min_w=340)
        body += b
    for a, b2 in zip(ys[:-1], ys[1:]):
        body += arrow(CX, a + 24, CX, b2 - 24)

    bx, by = 700, 340
    b, w, h = textbox(bx, by, ["Сторінку закріплено —", "перенести не можна"], size=13,
                      fill=BAD_FILL, stroke=DEV_LINE, sw=2)
    body += b
    body += arrow(CX + 172, by, bx - w / 2.0 - 4, by, color=DEV_LINE)
    body += line(bx, by - h / 2.0 - 4, bx, 52, color=DEV_LINE, dash="6 4")
    body += line(bx, 52, CX, 52, color=DEV_LINE, dash="6 4")
    body += arrow(CX, 52, CX, 70, color=DEV_LINE)
    body += text((CX + bx) / 2.0, 42, "відкат ізоляції, наступна смуга", size=12, color=DEV_LINE)

    return render(os.path.join(IMG, 'cma-alloc-path.svg'), W, H, body,
                  title="Виділення з CMA: п'ять кроків і єдине місце зриву")


# ─────────────────────────────────────────────────────────────
# 3. Кому доступна яка частина зони
# ─────────────────────────────────────────────────────────────
def fig_zone_split():
    W, H = 900, 330
    X0, X1, SPLIT = 60, 840, 560
    Y0, BH = 90, 58
    body = ""
    body += fitbox(X0, Y0, SPLIT - X0, BH, "звичайна пам'ять зони", size=14)
    body += fitbox(SPLIT, Y0, X1 - SPLIT, BH, "область CMA", size=14,
                   fill=OCC_FILL, stroke=OCC_LINE, sw=2)

    y1 = Y0 + BH + 55
    body += line(X0, y1, SPLIT - 10, y1, color=DEV_LINE, sw=2)
    body += line(SPLIT - 16, y1 - 9, SPLIT - 4, y1 + 9, color=DEV_LINE, sw=2.5)
    body += line(SPLIT - 16, y1 + 9, SPLIT - 4, y1 - 9, color=DEV_LINE, sw=2.5)
    body += text((X0 + SPLIT) / 2.0, y1 + 30,
                 "нерухомі виділення: структури ядра, таблиці сторінок, слаб",
                 size=13, color=DEV_LINE)

    y2 = y1 + 75
    body += line(X0, y2, X1, y2, color=FIELD, sw=2)
    body += text((X0 + X1) / 2.0, y2 + 30,
                 "рухомі виділення: кеш файлів, анонімні сторінки — користуються всім",
                 size=13, color=FIELD)

    body += text((X0 + SPLIT) / 2.0, Y0 - 18,
                 "тут закінчиться пам'ять ядра", size=12, color=MUTED)
    body += text((SPLIT + X1) / 2.0, Y0 - 18,
                 "а CmaFree буде великий", size=12, color=MUTED)
    return render(os.path.join(IMG, 'cma-zone-split.svg'), W, H, body,
                  title="Чому велика область CMA дорога")


# ─────────────────────────────────────────────────────────────
# 4. Де в драйвері стоїть виділення: раз на відкритті проти кожного кадру
# ─────────────────────────────────────────────────────────────
def fig_where_alloc():
    W, H = 900, 330
    X0, X1 = 235, 875
    SLOT = 70.0
    BH = 46

    body = ""

    # — смуга A: виділення один раз, до першого кадру
    yA = 96
    b, _, _ = textbox(115, yA, ["Виділення", "на відкритті"], size=13)
    body += b
    body += text(X1, 56, "час →", size=12, color=MUTED, anchor="end")
    body += fitbox(X0, yA - BH / 2.0, 150, BH, "виділення", size=12,
                   fill=DEV_FILL, stroke=DEV_LINE, sw=2)
    fx = X0 + 160
    n = int((X1 - fx) // SLOT)
    for i in range(n):
        body += fitbox(fx + i * SLOT, yA - BH / 2.0, SLOT - 4, BH, "кадр", size=11,
                       fill=OCC_FILL, stroke=OCC_LINE)
    body += text(X0, yA + BH / 2.0 + 26,
                 "ціну сплачено раз, до першого кадру — у гарячому шляху виділень немає",
                 size=12, color=MUTED, anchor="start")

    # — смуга B: виділення на кожен кадр
    yB = 232
    b, _, _ = textbox(115, yB, ["Виділення", "на кожен кадр"], size=13)
    body += b
    ty = yB - BH / 2.0
    k = 0
    while X0 + k * SLOT <= X1 + 0.5:
        body += line(X0 + k * SLOT, ty - 15, X0 + k * SLOT, ty - 3,
                     color=MUTED, dash="3 3")
        k += 1
    body += text(X0, ty - 24, "бюджети кадрів по 16.7 мс", size=12,
                 color=MUTED, anchor="start")

    AW, FW = 84.0, 44.0
    for i in range(5):
        bx = X0 + i * (AW + FW)
        body += fitbox(bx, ty, AW - 2, BH, "виділення" if i == 0 else "",
                       size=11, fill=DEV_FILL, stroke=DEV_LINE, sw=2)
        body += fitbox(bx + AW, ty, FW - 2, BH, "кадр" if i == 0 else "",
                       size=10, fill=OCC_FILL, stroke=OCC_LINE)
    body += text(X0, yB + BH / 2.0 + 26,
                 "дев'ять бюджетів — п'ять кадрів: решту з'їли переноси сторінок",
                 size=12, color=MUTED, anchor="start")

    return render(os.path.join(IMG, 'cma-where-alloc.svg'), W, H, body,
                  title="Де в драйвері стоїть виділення з CMA")


if __name__ == '__main__':
    for f in (fig_lifecycle, fig_alloc_path, fig_zone_split, fig_where_alloc):
        print(f())

# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «ULN2003 — драйвер (плата для 28BYJ-48)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Що всередині одного каналу: ключ до землі + діод-запобіжник до COM ──────
def fig_channel():
    W, H = 900, 470
    f = [text(W / 2, 30, "Один із семи каналів ULN2003: вхід керує ключем, що притягує вихід до землі",
              size=15, bold=True)]

    # шина живлення +5В (мотор) — угорі
    vy = 78
    f.append(line(120, vy, W - 60, vy, color=POS, sw=3))
    f.append(text(150, vy - 10, "+5 В (живлення мотора)", size=11, color=POS, bold=True, anchor="start"))
    f.append(plus(120, vy, 8))

    # шина землі — унизу схеми
    gy = 372
    f.append(line(120, gy, W - 60, gy, color=INK, sw=2.5))
    f.append(text(150, gy + 22, "GND (спільна земля з мікроконтролером)", size=11, bold=True, anchor="start"))

    # ── ЛІВОРУЧ: вхід INx і база через 2.7к ──
    inx_x = 175
    f.append(text(inx_x, 150, "INx", size=13, bold=True, color=NEG))
    f.append(text(inx_x, 168, "з виводу МК", size=9, color=MUTED))
    # вивід МК → лінія праворуч до резистора
    f.append(line(inx_x + 30, 150, 250, 150, color=NEG, sw=2))
    # резистор бази 2.7к (прямокутник)
    f.append(rect(250, 138, 70, 24, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=4))
    f.append(text(285, 154, "2.7 кОм", size=10, color=NEG, bold=True))
    f.append(text(285, 124, "вбудований", size=9, color=MUTED))
    f.append(line(320, 150, 380, 150, color=NEG, sw=2))

    # ── ЦЕНТР: пара Дарлінгтона як «великий ключ» (спрощено — блок) ──
    tx, ty, tw, th = 380, 118, 130, 150
    f.append(rect(tx, ty, tw, th, fill="#f4f6f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(tx + tw / 2, ty + 24, "пара", size=12, bold=True))
    f.append(text(tx + tw / 2, ty + 42, "Дарлінгтона", size=12, bold=True))
    f.append(text(tx + tw / 2, ty + 66, "(два транзистори", size=9, color=MUTED))
    f.append(text(tx + tw / 2, ty + 80, "великий підсил.)", size=9, color=MUTED))
    f.append(text(tx + tw / 2, ty + 108, "як вимикач", size=10, color=INK, italic=True))
    f.append(text(tx + tw / 2, ty + 126, "на землю", size=10, color=INK, italic=True))
    # колектор угору до OUTx, емітер униз до GND
    coll_x = tx + tw / 2
    f.append(line(coll_x, ty, coll_x, 118, color=INK, sw=2))          # до вузла OUTx
    f.append(line(coll_x, ty + th, coll_x, gy, color=INK, sw=2))      # емітер → GND

    # ── OUTx вузол і котушка мотора зверху ──
    outx_y = 118
    f.append(circle(coll_x, outx_y, 3.5, fill=INK, stroke=INK))
    # підпис OUTx — НАД лінією, щоб дріт не перетинав напис
    f.append(text(coll_x + 100, outx_y - 8, "OUTx", size=13, bold=True, color=INK, anchor="middle"))
    # лінія OUTx праворуч до котушки
    f.append(line(coll_x, outx_y, 640, outx_y, color=INK, sw=2))
    # котушка мотора (одна обмотка) між +5В і OUTx
    coil_x = 640
    f.append(line(coil_x, vy, coil_x, 150, color=INK, sw=2))          # від +5В униз
    # символ котушки (дужки)
    for i in range(4):
        cy = 150 + i * 16
        f.append('<path d="M%.0f %.0f q 14 8 0 16" fill="none" stroke="%s" stroke-width="2"/>' % (coil_x, cy, INK))
    f.append(line(coil_x, 150 + 4 * 16, coil_x, outx_y, color=INK, sw=2))
    f.append(text(coil_x + 66, 176, "обмотка", size=11, bold=True, anchor="middle"))
    f.append(text(coil_x + 66, 194, "мотора", size=11, bold=True, anchor="middle"))
    f.append(text(coil_x + 66, 214, "(індуктивність)", size=9, color=MUTED, anchor="middle"))

    # ── діод-запобіжник: від OUTx угору до шини COM (=+5В) ──
    dx = 770
    # вивід від OUTx праворуч до діода
    f.append(line(coil_x, outx_y, dx, outx_y, color=FIELD, sw=2))
    f.append(line(dx, outx_y, dx, vy, color=FIELD, sw=2))
    # трикутник діода (катод угору, до COM/+5В — діод НЕ проводить у нормі)
    f.append('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f z" fill="#eafaf0" stroke="%s" stroke-width="1.8"/>'
             % (dx - 9, 250, dx + 9, 250, dx, 232, FIELD))
    f.append(line(dx - 10, 232, dx + 10, 232, color=FIELD, sw=2.4))    # смужка катода
    f.append(text(dx + 74, 236, "діод до COM", size=10.5, bold=True, color=FIELD, anchor="middle"))
    f.append(text(dx + 74, 254, "(гасить кидок,", size=9, color=FIELD, anchor="middle"))
    f.append(text(dx + 74, 268, "коли ключ рве струм)", size=9, color=FIELD, anchor="middle"))
    # позначка COM на шині
    f.append(circle(dx, vy, 3.5, fill=POS, stroke=POS))
    f.append(text(dx, vy - 10, "COM", size=11, bold=True, color=POS, anchor="middle"))

    # підсумкова рамка
    b, _, _ = textbox(W / 2, 438,
                      "INx у «1» → ключ відкрито → OUTx притягнуто до землі → крізь обмотку тече струм. INx у «0» → ключ закрито, обмотка знеструмлена.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "channel.svg"), W, H, *f)


# ── 2. Розводка пін-у-пін: МК → плата ULN2003 → 5-дротовий роз'єм мотора ──────
def fig_wiring():
    W, H = 940, 560
    f = [text(W / 2, 30, "Підключення пін-у-пін: чотири виводи МК, спільна земля, окреме +5 В на мотор",
              size=15, bold=True)]

    # ── МК ліворуч ──
    mx, my, mw, mh = 40, 90, 175, 250
    f.append(rect(mx, my, mw, mh, fill="#eef2f8", stroke=INK, sw=1.8, rx=10))
    f.append(text(mx + mw / 2, my + 28, "мікроконтролер", size=12.5, bold=True))
    f.append(text(mx + mw / 2, my + 46, "(будь-які 4 цифрові", size=9, color=MUTED))
    f.append(text(mx + mw / 2, my + 60, "виводи + GND)", size=9, color=MUTED))
    mcu_pins = [("D8", NEG), ("D9", NEG), ("D10", NEG), ("D11", NEG), ("GND", INK)]
    mcu_y = {}
    for i, (lb, col) in enumerate(mcu_pins):
        yy = my + 96 + i * 30
        mcu_y[lb] = yy
        f.append(rect(mx + mw - 66, yy - 12, 54, 22, fill=BG, stroke=col, sw=1.4, rx=4))
        f.append(text(mx + mw - 66 + 27, yy + 3, lb, size=10.5, bold=True, color=col))

    # ── Плата ULN2003 у центрі ──
    bx, by, bw, bh = 380, 78, 220, 300
    f.append(rect(bx, by, bw, bh, fill="#eef6ef", stroke=FIELD, sw=2, rx=12))
    f.append(text(bx + bw / 2, by + 26, "плата ULN2003", size=13, bold=True, color=FIELD))
    f.append(text(bx + bw / 2, by + 44, "(мікросхема + роз'єм", size=9, color=MUTED))
    f.append(text(bx + bw / 2, by + 58, "+ 4 світлодіоди)", size=9, color=MUTED))

    # входи IN1..IN4 і GND — ЛІВИЙ край плати
    in_labels = ["IN1", "IN2", "IN3", "IN4"]
    in_y = {}
    for i, lb in enumerate(in_labels):
        yy = by + 96 + i * 30
        in_y[lb] = yy
        f.append(rect(bx + 12, yy - 12, 52, 22, fill=BG, stroke=NEG, sw=1.4, rx=4))
        f.append(text(bx + 12 + 26, yy + 3, lb, size=10.5, bold=True, color=NEG))
    gnd_in_y = by + 96 + 4 * 30
    f.append(rect(bx + 12, gnd_in_y - 12, 52, 22, fill=BG, stroke=INK, sw=1.4, rx=4))
    f.append(text(bx + 12 + 26, gnd_in_y + 3, "−", size=12, bold=True, color=INK))

    # клема живлення +/− на платі — ВЕРХ праворуч
    pw_x = bx + bw - 74
    f.append(rect(pw_x, by + 92, 62, 46, fill="#fdecea", stroke=POS, sw=1.6, rx=6))
    f.append(text(pw_x + 31, by + 108, "+  −", size=12, bold=True, color=POS))
    f.append(text(pw_x + 31, by + 128, "5 В на", size=9, color=INK))
    f.append(text(pw_x + 31, by + 140, "мотор", size=9, color=INK))

    # роз'єм мотора OUT — ПРАВИЙ край плати (біла колодка 5 пінів)
    f.append(rect(bx + bw - 30, by + 168, 22, 120, fill="#fafbfc", stroke=MUTED, sw=1.6, rx=4))
    f.append(text(bx + bw - 19, by + 300, "роз'єм", size=9, color=MUTED, anchor="middle"))

    # ── лінії МК → входи плати (у власному коридорі, без перетину написів) ──
    for a, b2 in [("D8", "IN1"), ("D9", "IN2"), ("D10", "IN3"), ("D11", "IN4")]:
        f.append(line(mx + mw - 12, mcu_y[a], bx + 12, in_y[b2], color=NEG, sw=1.8))
    # спільна земля
    f.append(line(mx + mw - 12, mcu_y["GND"], bx + 12, gnd_in_y, color=INK, sw=2))
    f.append(text((mx + mw + bx) / 2, my + mh + 6, "4 сигнали + спільна земля", size=10, color=NEG, italic=True))

    # ── зовнішні 5 В у клему плати (окреме джерело!) ──
    src_x = pw_x + 31
    top_y = by + 24
    end_x = src_x + 168
    # напис — НАД горизонтальним дротом, зсунуто ліворуч від «+», щоб не накладалось
    f.append(text(src_x + 60, top_y - 12, "окреме джерело 5 В / USB", size=10.5, bold=True, color=POS, anchor="middle"))
    f.append(line(src_x, by + 92, src_x, top_y, color=POS, sw=2.2))
    f.append(line(src_x, top_y, end_x, top_y, color=POS, sw=2.2))
    f.append(plus(end_x, top_y, 7))
    f.append(text(src_x + 6, by + 60, "живлення мотора — НЕ з піна 5 В плати МК", size=9, color=POS, anchor="start"))

    # ── Мотор 28BYJ-48 праворуч ──
    ox, oy, ow, oh = 760, 150, 150, 200
    f.append(rect(ox, oy, ow, oh, fill="#f4f8f5", stroke=INK, sw=1.8, rx=12))
    f.append(text(ox + ow / 2, oy + 28, "28BYJ-48", size=12.5, bold=True))
    f.append(text(ox + ow / 2, oy + 46, "кроковий мотор", size=9, color=MUTED))
    # 5-дротовий шлейф кольорами
    wires = [("синій", NEG), ("рожевий", POS), ("жовтий", "#c9a227"), ("помаранч.", "#d35400"), ("черв. +5В", POS)]
    wy = {}
    for i, (lb, col) in enumerate(wires):
        yy = oy + 74 + i * 22
        wy[i] = (yy, col)
        f.append(circle(ox + 14, yy, 5, fill=col, stroke=INK, sw=1))
        f.append(text(ox + 26, yy + 4, lb, size=9.5, color=INK, anchor="start"))
    # шлейф від роз'єму плати до мотора (5 ліній кольорами)
    for i in range(5):
        yy, col = wy[i]
        f.append(line(bx + bw - 8, by + 180 + i * 22, ox, yy, color=col, sw=2))
    f.append(text((bx + bw + ox) / 2, oy + oh - 4, "білий 5-контактний роз'єм — одна орієнтація", size=9, color=MUTED, italic=True))

    # підсумок
    b, _, _ = textbox(W / 2, 528,
                      "Логіка й живлення розділені: 4 тонкі сигнали з МК керують ключами, а силу для обмоток бере ОКРЕМЕ 5 В; спільна лише земля.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 3. Половинний крок: 8 станів входів IN1..IN4, що ганяють обмотки по колу ──
def fig_halfstep():
    W, H = 900, 470
    f = [text(W / 2, 30, "Половинний крок: вісім станів входів IN1…IN4 женуть точку живлення по обмотках",
              size=15, bold=True)]

    cols = ["IN1", "IN2", "IN3", "IN4"]
    # таблиця 8 кроків × 4 входи
    x0, y0 = 250, 74
    cw, rh = 90, 40
    # заголовки стовпців
    for c, lb in enumerate(cols):
        f.append(text(x0 + c * cw + cw / 2, y0, lb, size=13, bold=True, color=NEG))
    f.append(text(x0 - 60, y0, "крок", size=12, bold=True, color=MUTED))

    seq = [
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 1],
        [1, 0, 0, 1],
    ]
    for r, row in enumerate(seq):
        ry = y0 + 22 + r * rh
        f.append(text(x0 - 60, ry + rh / 2 + 4, str(r + 1), size=12, color=INK))
        for c, v in enumerate(row):
            cx = x0 + c * cw + cw / 2
            cy = ry + rh / 2
            if v:
                f.append(circle(cx, cy, 13, fill="#fdecea", stroke=POS, sw=2))
                f.append(text(cx, cy + 4, "1", size=13, bold=True, color=POS))
            else:
                f.append(circle(cx, cy, 13, fill="#f4f6f8", stroke=MUTED, sw=1.4))
                f.append(text(cx, cy + 4, "0", size=12, color=MUTED))

    # рамка таблиці
    f.append(rect(x0 - 10, y0 + 8, 4 * cw + 20, 8 * rh + 6, fill="none", stroke=LINE, sw=1.4, rx=8))

    # ліворуч — пояснення «1 = обмотка під струмом»
    lb1, _, _ = textbox(120, 150, "«1» на вході\n= ключ ON\n= ця обмотка\nпід струмом",
                        size=11, fill="#fdecea", stroke=POS, color=INK)
    f.append(lb1)
    lb2, _, _ = textbox(120, 300, "пари 1-2-3-4\nзагоряються\nвнахлест —\nвіссю тягне\nплавно",
                        size=11, fill=FILL, stroke=LINE)
    f.append(lb2)

    # праворуч — стрілка «по колу» й напрям
    ax = 720
    f.append(text(ax + 30, 90, "8 станів = один", size=11, bold=True, anchor="middle"))
    f.append(text(ax + 30, 108, "півкроковий цикл", size=11, bold=True, anchor="middle"))
    # кругова стрілка
    f.append('<path d="M%.0f %.0f a 60 60 0 1 1 -1 0" fill="none" stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>'
             % (ax + 30, 150, FIELD))
    f.append(text(ax + 30, 218, "далі — знову", size=10, color=FIELD, anchor="middle"))
    f.append(text(ax + 30, 234, "крок 1", size=10, color=FIELD, anchor="middle"))
    f.append(text(ax + 30, 268, "звороти цикл", size=10, color=INK, anchor="middle"))
    f.append(text(ax + 30, 284, "у зворотному", size=10, color=INK, anchor="middle"))
    f.append(text(ax + 30, 300, "порядку →", size=10, color=INK, anchor="middle"))
    f.append(text(ax + 30, 316, "мотор назад", size=10, color=INK, italic=True, anchor="middle"))

    b, _, _ = textbox(W / 2, 442,
                      "Ці вісім рядків — усе, що шле мікроконтролер: по одному «слову» на такт. Швидше міняєш рядки — швидше крутиться, до межі.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "halfstep.svg"), W, H, *f)


# ── 4. (hist) Родовід кремнію ULN: Sprague → Sanken/Allegro + другоджерела ─────
def fig_lineage():
    W, H = 940, 470
    f = [text(W / 2, 30, "Родовід ULN2003: хто виплавляв кремній і хто його підхопив",
              size=15, bold=True)]

    # горизонтальна вісь часу
    ay = 150
    f.append(line(70, ay, W - 60, ay, color=INK, sw=2.5))
    for yr, xx in [(1926, 90), (1966, 300), (1976, 470), (1990, 660), ("нині", 850)]:
        f.append(line(xx, ay - 6, xx, ay + 6, color=INK, sw=2))
        f.append(text(xx, ay - 14, str(yr), size=11, bold=True, color=MUTED))

    # головна гілка Sprague: три віхи-рамки НАД віссю
    b1, _, _ = textbox(150, 92, "Sprague Electric\nзаснов. 1926\n(Норт-Адамс, Массач.)",
                       size=10.5, fill="#eef2f8", stroke=NEG, color=INK)
    f.append(b1)
    b2, _, _ = textbox(385, 92, "власний фаб ІС\n1966 (Вустер);\nсерія 2000 —\nмасив Дарлінгтона",
                       size=10.5, fill="#eef2f8", stroke=NEG, color=INK)
    f.append(b2)
    b3, _, _ = textbox(575, 250, "ULN2003 у серії:\nсім пар, 500 мА,\nдіоди в COM",
                       size=10.5, fill="#eef6ef", stroke=FIELD, color=INK)
    f.append(b3)
    # тонкі виноски від рамок до відповідних років на осі
    f.append(line(150, 118, 90, ay - 6, color=NEG, sw=1.2, dash="3,3"))
    f.append(line(385, 126, 300, ay - 6, color=NEG, sw=1.2, dash="3,3"))
    f.append(line(575, 224, 470, ay + 6, color=FIELD, sw=1.2, dash="3,3"))

    # 1990: напівпровідникову гілку купує Sanken → Allegro
    b4, _, _ = textbox(660, 300, "1990: підрозділ\nкупує Sanken (Яп.)\n→ Allegro MicroSystems",
                       size=10.5, fill="#fdf3e6", stroke=POS, color=INK)
    f.append(b4)
    f.append(line(660, 274, 660, ay + 6, color=POS, sw=1.2, dash="3,3"))

    # другоджерела праворуч — окремим блоком
    b5, _, _ = textbox(850, 250, "другоджерела:\nTI · ST · onsemi\n· Toshiba · Diodes",
                       size=10.5, fill=FILL, stroke=LINE, color=INK)
    f.append(b5)
    f.append(line(850, 224, 850, ay + 6, color=INK, sw=1.2, dash="3,3"))

    b, _, _ = textbox(W / 2, 442,
                      "Кремній народила Sprague; сама марка «ULN» — її ж номенклатура. Пізніше плату вже штампують по чужих фабах — той самий рядок паяно скрізь.",
                      size=11, fill=FILL, stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "lineage.svg"), W, H, *f)


# ── 5. (proj) Пастка порядку пінів: дроти 1-2-3-4, а в конструктор — 1-3-2-4 ───
def fig_pinorder():
    import math
    W, H = 900, 470
    f = [text(W / 2, 30, "Дроти йдуть по-порядку 1-2-3-4, а в конструктор піни заходять як 1-3-2-4",
              size=15, bold=True)]

    # ── ЛІВОРУЧ: фізичні дроти D8..D11 → IN1..IN4 (просто, по-порядку) ──
    lx = 90
    f.append(text(lx + 70, 78, "фізичні дроти на платі", size=12.5, bold=True, color=NEG, anchor="middle"))
    f.append(text(lx + 70, 96, "(природно, по-порядку)", size=9.5, color=MUTED, anchor="middle"))
    pairs = [("D8", "IN1"), ("D9", "IN2"), ("D10", "IN3"), ("D11", "IN4")]
    for i, (a, b2) in enumerate(pairs):
        yy = 142 + i * 54
        f.append(rect(lx, yy - 15, 52, 30, fill=BG, stroke=NEG, sw=1.5, rx=5))
        f.append(text(lx + 26, yy + 5, a, size=12, bold=True, color=NEG))
        f.append(rect(lx + 108, yy - 15, 52, 30, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=5))
        f.append(text(lx + 108 + 26, yy + 5, b2, size=12, bold=True, color=FIELD))
        f.append(line(lx + 52, yy, lx + 108, yy, color=INK, sw=2))
    f.append(text(lx + 70, 142 + 4 * 54 + 6, "1 → 2 → 3 → 4", size=12, bold=True, color=INK, anchor="middle"))

    # ── СЕРЕДИНА: магнітне коло обмоток (порядок 1-3-2-4) ──
    ccx, ccy, cr = W / 2 - 4, 258, 74
    f.append(text(ccx, 78, "магнітне коло обмоток", size=12.5, bold=True, color=POS, anchor="middle"))
    f.append(text(ccx, 96, "усередині мотора", size=9.5, color=MUTED, anchor="middle"))
    f.append(circle(ccx, ccy, cr, fill="none", stroke=MUTED, sw=1.4))
    ring = [("IN1", 0), ("IN3", 90), ("IN2", 180), ("IN4", 270)]  # по колу за годинником
    node = {}
    for lb, ang in ring:
        rad = math.radians(ang - 90)   # 0° угору
        nx = ccx + cr * math.cos(rad)
        ny = ccy + cr * math.sin(rad)
        node[lb] = (nx, ny)
        f.append(circle(nx, ny, 19, fill="#fdecea", stroke=POS, sw=1.8))
        f.append(text(nx, ny + 5, lb, size=11.5, bold=True, color=POS))
    order = ["IN1", "IN3", "IN2", "IN4", "IN1"]
    for i in range(4):
        x1, y1 = node[order[i]]
        x2, y2 = node[order[i + 1]]
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        f.append(arrow(x1 + ux * 22, y1 + uy * 22, x2 - ux * 22, y2 - uy * 22, color=FIELD, sw=2.2))
    f.append(text(ccx, ccy + cr + 42, "поле обходить: 1 → 3 → 2 → 4", size=11, bold=True, color=FIELD, anchor="middle"))

    # ── ПРАВОРУЧ: рядок конструктора ──
    rx = 720
    b, _, _ = textbox(rx + 78, 150,
                      "у КОДІ піни\nперелічуємо\nв цьому колі:\n1-3-2-4",
                      size=11, fill=FILL, stroke=LINE, color=INK)
    f.append(b)
    code_y = 262
    f.append(rect(rx - 22, code_y - 22, 200, 48, fill="#f4f6f8", stroke=NEG, sw=1.6, rx=6))
    f.append(text(rx + 78, code_y - 3, "Stepper(2038,", size=12, bold=True, color=INK, anchor="middle"))
    f.append(text(rx + 78, code_y + 16, "8, 10, 9, 11)", size=13, bold=True, color=POS, anchor="middle"))
    f.append(text(rx + 78, code_y + 44, "8,10,9,11 = IN1,IN3,IN2,IN4", size=9, color=MUTED, anchor="middle"))
    f.append(text(rx + 78, code_y + 62, "а НЕ 8,9,10,11", size=10, bold=True, color=POS, anchor="middle"))

    b2, _, _ = textbox(W / 2, 442,
                       "Дроти не чіпай — вони по-порядку. Переставлений лише перелік у дужках конструктора: 1-3-2-4, бо магнітно IN3 стоїть між IN1 та IN2.",
                       size=11, fill=FILL, stroke=LINE)
    f.append(b2)
    render(os.path.join(IMG, "pinorder.svg"), W, H, *f)


if __name__ == "__main__":
    fig_channel()
    fig_wiring()
    fig_halfstep()
    fig_lineage()
    fig_pinorder()
    print("OK: 5 figures ->", IMG)

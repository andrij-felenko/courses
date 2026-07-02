# -*- coding: utf-8 -*-
"""Фігури до теми «Надійність даних» (book/communications/coding-theory/data-reliability).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Сходи надійності: від найдешевшого виявлення до виправлення пакетів ──────
# Ідея, яку важко передати словами: усі коди шикуються в один ряд за зростанням
# сили й ціни, і вибір — це спуск цими сходами рівно настільки, скільки вимагає
# канал. Праворуч у кожної сходинки — що саме вона робить (виявлення/виправлення).
def fig_decision():
    W = 880
    rows = [
        ("Парність  ·  1 біт", "бачить 1 помилку, не виправляє",
         "UART-кадр, простий регістр", "виявлення", "#caa24a"),
        ("Контрольна сума  ·  сума / Флетчер", "дешеве програмне виявлення",
         "легкі протоколи, файли без заліза CRC", "виявлення", "#caa24a"),
        ("CRC", "потужне виявлення пакетів, апаратно майже задарма",
         "CAN, Ethernet, SD, USB, серйозний кадр", "виявлення (сильне)", POS),
        ("ECC  ·  Геммінг / SECDED, BCH", "виправляє на льоту, платить зайвими бітами",
         "RAM серверів, Flash, пам'ять у радіації", "виправлення", FIELD),
        ("Рід–Соломон  ·  каскад", "виправляє пакети символів",
         "носії, супутник, далекий космос", "виправлення (пакети)", FIELD),
    ]
    box_w, box_h, gap = 560, 86, 18
    top = 86
    H = top + len(rows) * (box_h + gap) + 40
    f = []
    f.append(text(W / 2, 34, "Сходи надійності: від найдешевшого виявлення до виправлення пакетів",
                  16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 56, "три питання вибирають інструмент: виправляти чи виявити? поодинокі чи пакетні? скільки платити?",
                  11.5, MUTED, "middle", italic=True))

    x_left = 60
    for i, (name, what, where, tag, col) in enumerate(rows):
        y = top + i * (box_h + gap)
        x = x_left + i * 8                      # легкий каскад управо — відчуття «сходів»
        f.append(rect(x, y, box_w, box_h, fill=BG, stroke=col, sw=2.2, rx=9))
        f.append(text(x + 18, y + 28, name, 15.5, col, "start", bold=True))
        f.append(text(x + 18, y + 50, what, 11.8, INK, "start"))
        f.append(text(x + 18, y + 70, "де: " + where, 11.5, MUTED, "start"))
        # ярлик «виявлення / виправлення» праворуч
        tag_w = text_width(tag, 12.5, bold=True) + 24
        tx = x + box_w + 14
        f.append(rect(tx, y + box_h / 2 - 18, tag_w, 36, fill="#fbfbfb", stroke=col, sw=1.6, rx=8))
        f.append(text(tx + tag_w / 2, y + box_h / 2 + 5, tag, 12.5, col, "middle", bold=True))
        # стрілка-сходинка вниз
        if i < len(rows) - 1:
            ax = x + 26
            f.append(arrow(ax, y + box_h, ax + 8, y + box_h + gap, color=MUTED, sw=2))

    f.append(text(W / 2, H - 16,
                  "Стрілка вниз — «треба більше надійності й готовий платити дорожче». Більшість систем поєднує кілька рівнів разом.",
                  11.5, INK, "middle", italic=True))
    render(os.path.join(IMG, "decision-ladder.svg"), W, H, *f)


# ── 2. Коди складаються в шари, а не змагаються ────────────────────────────────
# Ідея: різні рівні захисту працюють одночасно на різних рубежах одного пакета;
# кожен ловить те, проти чого він найсильніший, і прикриває слабкість сусіда.
def fig_layers():
    W, H = 760, 360
    f = []
    f.append(text(W / 2, 32, "Коди складаються в шари, а не змагаються",
                  16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 54, "кожен шар ловить те, що пропустив попередній; разом дають надійність, недосяжну поодинці",
                  11.5, MUTED, "middle", italic=True))

    layers = [
        ("байт у пам'яті / комірці", "ловить: поодинокі біт-фліпи в RAM і Flash",
         "ECC  (Геммінг / BCH)", FIELD),
        ("символи на носії / в радіоканалі", "ловить: пакети, завмирання, подряпини",
         "Рід–Соломон  (FEC)", "#7a3da8"),
        ("кадр на шині / у протоколі", "ловить: усе, що проскочило крізь канал",
         "CRC", POS),
        ("логічний пакет (заголовок + дані)", "ловить: груба перевірка структури, дешево",
         "контрольна сума / парність полів", "#caa24a"),
    ]
    bx, bw, bh, gap = 70, 620, 56, 14
    y0 = 86
    for i, (title_l, catch, code, col) in enumerate(layers):
        y = y0 + i * (bh + gap)
        f.append(rect(bx, y, bw, bh, fill=BG, stroke=col, sw=2, rx=8))
        f.append(text(bx + 18, y + 24, title_l, 13.5, INK, "start", bold=True))
        f.append(text(bx + 18, y + 44, catch, 11.5, MUTED, "start"))
        # ярлик коду праворуч
        tag_w = text_width(code, 13, bold=True) + 22
        tx = bx + bw - tag_w - 12
        f.append(rect(tx, y + bh / 2 - 16, tag_w, 32, fill="#fbfbfb", stroke=col, sw=1.6, rx=7))
        f.append(text(tx + tag_w / 2, y + bh / 2 + 5, code, 13, col, "middle", bold=True))

    f.append(text(W / 2, H - 14,
                  "Кожен рівень бере загрозу, проти якої найсильніший, і прикриває слабкість сусіда.",
                  11.5, INK, "middle", italic=True))
    render(os.path.join(IMG, "protection-layers.svg"), W, H, *f)


# ── 3. Геометрія куль: одна відстань керує виявленням і виправленням ────────────
# Ідея, важка на словах: дозволені слова — точки; кулі радіуса t навколо них;
# виправлення з'їдає ПІВ відстані з обох боків, виявлення — всю d−1. Показуємо
# два центри на відстані d, їхні кулі, нейтральну смугу між ними й підписи меж.
def fig_sphere():
    W, H = 820, 400
    f = []
    f.append(text(W / 2, 30, "Одна відстань d керує і виявленням, і виправленням",
                  16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "кулі радіуса t навколо дозволених слів; виправлення бере половину відстані, виявлення — всю",
                  11.5, MUTED, "middle", italic=True))

    cyc = 220
    cxA, cxB = 250, 570
    t_r = 74                                   # радіус кулі (t перевертів)
    # осьова лінія відстані між словами
    f.append(line(cxA, cyc, cxB, cyc, color=MUTED, sw=1.4, dash="4 4"))
    # кулі виправлення
    f.append(circle(cxA, cyc, t_r, fill="#eaf7ef", stroke=FIELD, sw=2))
    f.append(circle(cxB, cyc, t_r, fill="#eaf7ef", stroke=FIELD, sw=2))
    # центри — дозволені слова
    for cx, lbl in ((cxA, "слово A"), (cxB, "слово B")):
        f.append(circle(cx, cyc, 6.5, fill=INK, stroke=INK, sw=1))
        f.append(text(cx, cyc - t_r - 12, lbl, 12.5, INK, "middle", bold=True))
    # радіус t всередині кулі A
    f.append(arrow(cxA, cyc, cxA + t_r, cyc, color=FIELD, sw=1.8))
    f.append(text(cxA + t_r / 2, cyc - 8, "t", 13, FIELD, "middle", bold=True))
    # відстань d між центрами
    f.append(text((cxA + cxB) / 2, cyc + 26, "відстань d", 12.5, MUTED, "middle", italic=True))
    # точка-помилка у нейтральній смузі
    ex = (cxA + cxB) / 2 + 14
    f.append(circle(ex, cyc, 4.5, fill=POS, stroke=POS, sw=1))
    f.append(text(ex, cyc - 14, "e", 11.5, POS, "middle", bold=True))

    # підписи-висновки внизу
    b1, w1, _ = textbox(cxA + 40, 350, "виправлення: e ≤ t = ⌊(d−1)/2⌋\n(точка в кулі → найближче слово правильне)",
                        11.5, pad=10, fill="#eaf7ef", stroke=FIELD, color=INK)
    f.append(b1)
    b2, w2, _ = textbox(cxB - 10, 350, "виявлення: e ≤ d−1\n(точка поза словом → видно, що хибне)",
                        11.5, pad=10, fill="#fbfbfb", stroke=POS, color=INK)
    f.append(b2)
    render(os.path.join(IMG, "sphere-packing.svg"), W, H, *f)


# ── 4. Перемежування: пакет у каналі → розсип поодиноких у словах ──────────────
# Ідея: пишемо слова рядками, читаємо стовпцями; пакет б'є один стовпець, після
# зворотної перестановки — по одному биту на слово. Дві таблиці й стрілка між.
def fig_interleave():
    W, H = 860, 430
    f = []
    f.append(text(W / 2, 30, "Перемежування: пакет у каналі стає розсипом поодиноких у словах",
                  16, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "пишемо кодові слова рядками, у канал шлемо стовпцями — пакет б'є один стовпець",
                  11.5, MUTED, "middle", italic=True))

    rows, cols = 4, 6
    cell = 34
    # ── ліва таблиця: як лежить у пам'яті (рядок = слово) ──
    gx, gy = 70, 110
    for r in range(rows):
        for c in range(cols):
            x, y = gx + c * cell, gy + r * cell
            f.append(rect(x, y, cell, cell, fill=BG, stroke=MUTED, sw=1))
            f.append(text(x + cell / 2, y + cell / 2 + 4, "%d" % (r + 1), 11, MUTED, "middle"))
    for r in range(rows):
        f.append(text(gx - 10, gy + r * cell + cell / 2 + 4, "слово %d" % (r + 1), 10.5, INK, "end"))
    f.append(text(gx + cols * cell / 2, gy - 12, "у пам'яті: рядок = слово", 12, INK, "middle", bold=True))
    # пакет б'є один СТОВПЕЦЬ (бо в канал ідемо стовпцями)
    pc = 3
    f.append(rect(gx + pc * cell - 2, gy - 2, cell + 4, rows * cell + 4, fill="none", stroke=POS, sw=2.4))
    for r in range(rows):
        f.append(circle(gx + pc * cell + cell / 2, gy + r * cell + cell / 2, 5, fill=POS, stroke=POS, sw=1))
    f.append(text(gx + pc * cell + cell / 2, gy + rows * cell + 18, "пакет", 11, POS, "middle", bold=True))
    f.append(text(gx + cols * cell / 2, gy + rows * cell + 40,
                  "↓ у канал читаємо стовпцями: пакет = суміжні біти ефіру", 11, MUTED, "middle", italic=True))

    # стрілка «зворотна перестановка на прийомі»
    ax = gx + cols * cell + 24
    f.append(arrow(ax, gy + rows * cell / 2, ax + 70, gy + rows * cell / 2, color=INK, sw=2))
    f.append(text(ax + 35, gy + rows * cell / 2 - 12, "прийом:", 10.5, INK, "middle"))
    f.append(text(ax + 35, gy + rows * cell / 2 + 22, "читаємо рядками", 10.5, INK, "middle"))

    # ── права таблиця: після зворотної перестановки — по 1 биту на слово ──
    hx = ax + 94
    for r in range(rows):
        for c in range(cols):
            x, y = hx + c * cell, gy + r * cell
            hit = (c == pc)
            f.append(rect(x, y, cell, cell, fill="#fdecea" if hit else BG,
                          stroke=POS if hit else MUTED, sw=1.6 if hit else 1))
            if hit:
                f.append(circle(x + cell / 2, y + cell / 2, 5, fill=POS, stroke=POS, sw=1))
    f.append(text(hx + cols * cell / 2, gy - 12, "у кожному слові — 1 помилка", 12, INK, "middle", bold=True))
    for r in range(rows):
        f.append(text(hx + cols * cell + 8, gy + r * cell + cell / 2 + 4, "✓ бере", 10.5, FIELD, "start", bold=True))

    f.append(text(W / 2, H - 20, "Глибина D ≥ B / t: пакет B, код виправляє t на слово — таблиця з D рядків його розмаже.",
                  12, INK, "middle", italic=True))
    render(os.path.join(IMG, "interleaving.svg"), W, H, *f)


# ── 5. ARQ проти FEC: криві корисної швидкості й крапка перетину ────────────────
# Ідея: ARQ спадає лінійно з p (повтори), FEC — стала горизонталь (сталий надлишок);
# перетин у p* = 1 − R_code ділить площину на «виграє ARQ» / «виграє FEC».
def fig_crossover():
    W, H = 780, 470
    f = []
    f.append(text(W / 2, 30, "ARQ проти FEC: де перепит програє прямому виправленню",
                  16.5, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "корисна швидкість залежно від частки битих кадрів p; перетин у p* = 1 − R_code",
                  11.5, MUTED, "middle", italic=True))

    # осі
    ox, oy = 90, 380          # початок координат
    axw, axh = 600, 300
    f.append(arrow(ox, oy, ox + axw + 10, oy, color=INK, sw=1.8))        # вісь p
    f.append(arrow(ox, oy, ox, oy - axh - 10, color=INK, sw=1.8))        # вісь швидкості
    f.append(text(ox + axw + 4, oy + 22, "частка битих кадрів p →", 11.5, INK, "end"))
    f.append(text(ox - 8, oy - axh - 14, "корисна швидкість", 11.5, INK, "middle"))
    f.append(text(ox - 12, oy + 4, "0", 10.5, MUTED, "end"))
    f.append(text(ox - 12, oy - axh + 6, "R₀", 11.5, INK, "end", bold=True))
    f.append(text(ox + axw, oy + 20, "1", 10.5, MUTED, "middle"))

    R0y = oy - axh                                   # рівень R0 (p=0)
    Rc = 0.62                                         # R_code для картинки
    Rcy = oy - axh * Rc                               # горизонталь FEC
    pstar = 1 - Rc                                    # крапка перетину по осі p
    psx = ox + axw * pstar

    # FEC — горизонталь
    f.append(line(ox, Rcy, ox + axw, Rcy, color=FIELD, sw=2.6))
    f.append(text(ox + axw - 6, Rcy - 8, "FEC = R_code·R₀ (стала)", 12, FIELD, "end", bold=True))
    # ARQ — похила від (0,R0) до (1,0)
    f.append(line(ox, R0y, ox + axw, oy, color=POS, sw=2.6))
    f.append(text(ox + 150, R0y + 30, "ARQ = (1−p)·R₀", 12, POS, "start", bold=True))

    # крапка перетину
    f.append(line(psx, oy, psx, Rcy, color=MUTED, sw=1.3, dash="4 4"))
    f.append(circle(psx, Rcy, 5.5, fill=INK, stroke=INK, sw=1))
    f.append(text(psx, oy + 20, "p* = 1 − R_code", 11.5, INK, "middle", bold=True))

    # зони
    f.append(text((ox + psx) / 2, oy - 40, "виграє ARQ", 12.5, POS, "middle", bold=True))
    f.append(text((ox + psx) / 2, oy - 24, "(тихий канал)", 10.5, MUTED, "middle"))
    f.append(text((psx + ox + axw) / 2, Rcy - 40, "виграє FEC", 12.5, FIELD, "middle", bold=True))
    f.append(text((psx + ox + axw) / 2, Rcy - 24, "(шумний канал)", 10.5, MUTED, "middle"))
    render(os.path.join(IMG, "arq-fec-crossover.svg"), W, H, *f)


# ── 6. Наскрізний багатошаровий стек: чому залишкові ймовірності перемножуються ─
# Ідея: чотири рубежі від комірки до кадру, перемежування-клей між канальними,
# і фінальна формула добутку пропусків, недосяжного жодному коду поодинці.
def fig_stack():
    W, H = 820, 470
    f = []
    f.append(text(W / 2, 30, "Наскрізний захист: незалежні шари ПЕРЕМНОЖУЮТЬ залишкові ймовірності",
                  15.5, INK, "middle", bold=True))
    f.append(text(W / 2, 52, "дані від давача до контролера проходять чотири рубежі; перемежування тримає їх незалежними",
                  11.3, MUTED, "middle", italic=True))

    layers = [
        ("Flash-комірка", "BCH проти поодиноких біт-фліпів", "пропускає q₁", FIELD),
        ("радіоканал", "Рід–Соломон проти пакетів і завмирань", "пропускає q₂", "#7a3da8"),
        ("кадр на шині", "CRC проти всього, що прорвалось", "пропускає q₃", POS),
        ("заголовок пакета", "контрольна сума: груба перевірка структури", "пропускає q₄", "#caa24a"),
    ]
    bx, bw, bh, gap = 90, 470, 62, 16
    y0 = 92
    for i, (name, catch, q, col) in enumerate(layers):
        y = y0 + i * (bh + gap)
        f.append(rect(bx, y, bw, bh, fill=BG, stroke=col, sw=2, rx=8))
        f.append(text(bx + 16, y + 25, name, 13.5, col, "start", bold=True))
        f.append(text(bx + 16, y + 45, catch, 11.3, INK, "start"))
        # ярлик пропуску праворуч
        f.append(text(bx + bw - 14, y + bh / 2 + 4, q, 12, MUTED, "end", italic=True))
        # клей-перемежування між канальними шарами (між 0 і 1)
        if i == 0:
            f.append(text(bx + bw + 18, y + bh + gap / 2 + 4, "⇄ перемежування (клей незалежності)",
                          10.8, "#7a3da8", "start", bold=True))
        if i < len(layers) - 1:
            ax = bx + 30
            f.append(arrow(ax, y + bh, ax, y + bh + gap, color=MUTED, sw=1.8))

    # фінальна формула
    fy = y0 + len(layers) * (bh + gap) + 6
    b, bwd, _ = textbox(W / 2, fy + 18,
                        "разом пропускає  q = q₁ · q₂ · q₃ · q₄   ←  добуток, недосяжний жодному коду поодинці",
                        12, pad=12, fill="#eef7f1", stroke=FIELD, color=INK, bold=True)
    f.append(b)
    render(os.path.join(IMG, "layered-stack.svg"), W, H, *f)


if __name__ == "__main__":
    fig_decision()
    fig_layers()
    fig_sphere()
    fig_interleave()
    fig_crossover()
    fig_stack()
    print("OK: figures written to", IMG)

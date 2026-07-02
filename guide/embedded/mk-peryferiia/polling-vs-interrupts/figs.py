# -*- coding: utf-8 -*-
"""Фігури до теми «Polling vs переривання».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Два інструменти: дві колонки сильних боків + ціна ─────────────────────
def fig_two_tools():
    W, H = 940, 392
    f = [text(W / 2, 30, "Два інструменти, не суперники: кожен сильний у своєму", size=17, bold=True)]
    f.append(text(W / 2, 52, "опитування й переривання доповнюють одне одного — інженер володіє обома",
                  size=12, color=MUTED, italic=True))

    # ── ліва колонка: опитування ──
    f.append(rect(50, 88, 400, 268, fill="#fdf2f2", stroke=POS, sw=1.8, rx=12))
    f.append(text(250, 116, "Опитування", size=15, color=POS, bold=True))
    f.append(text(250, 138, "сильне, коли:", size=11, color=MUTED))
    poll = ["події часті й очікувані",
            "темп рівномірний",
            "важить простота й передбачуваність",
            "реакція «в межах циклу» влаштовує"]
    for i, s in enumerate(poll):
        y = 172 + i * 30
        f.append(text(74, y, "+", size=15, color=POS, bold=True, anchor="start"))
        f.append(text(96, y, s, size=11.5, anchor="start"))
    f.append(text(250, 322, "ціна: марнує час циклу, може проґавити коротке",
                  size=10.5, color=MUTED, italic=True))

    # ── права колонка: переривання ──
    f.append(rect(490, 88, 400, 268, fill="#f3faf4", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(690, 116, "Переривання", size=15, color=FIELD, bold=True))
    f.append(text(690, 138, "сильне, коли:", size=11, color=MUTED))
    irq = ["події рідкісні чи випадкові",
           "реагувати треба вмить",
           "не можна проґавити подію",
           "процесор має лишатися вільним"]
    for i, s in enumerate(irq):
        y = 172 + i * 30
        f.append(text(514, y, "+", size=15, color=FIELD, bold=True, anchor="start"))
        f.append(text(536, y, s, size=11.5, anchor="start"))
    f.append(text(690, 322, "ціна: складніший код (ISR, volatile, гонки)",
                  size=10.5, color=MUTED, italic=True))

    f.append(text(W / 2, 380, "Питання не «що краще взагалі», а «що краще для ЦІЄЇ задачі».",
                  size=12, bold=True))
    render(os.path.join(IMG, "two-tools.svg"), W, H, *f)


# ── 2. Блок-схема рішення: два питання → інструмент ──────────────────────────
def fig_decision_flow():
    W, H = 880, 470
    f = [text(W / 2, 30, "Три питання поспіль ведуть до інструмента", size=17, bold=True)]
    f.append(text(W / 2, 52, "хоч одне «так» — переривання; обидва «ні» — досить опитування",
                  size=12, color=MUTED, italic=True))

    cx = W / 2

    # питання 1 (ромб через прямокутник зі скосом — лишаємо прямокутник для чіткості)
    q1, w1, h1 = textbox(cx, 110, "Подія рідкісна чи\nвипадкова в часі?", size=13, bold=True,
                         fill="#f4f6f8", stroke=INK, min_w=300)
    f.append(q1)

    # питання 2
    q2, w2, h2 = textbox(cx, 230, "Реагувати вмить\nабо не можна проґавити?", size=13, bold=True,
                         fill="#f4f6f8", stroke=INK, min_w=340)
    f.append(q2)

    # стрілка q1 → q2 («ні»)
    f.append(arrow(cx, 110 + h1 / 2, cx, 230 - h2 / 2, color=INK))
    f.append(text(cx + 12, 175, "ні", size=12, color=NEG, bold=True, anchor="start"))

    # переривання (праворуч від обох питань — «так»)
    box_irq, wi, hi = textbox(740, 170, "ПЕРЕРИВАННЯ", size=14, bold=True,
                              color=FIELD, fill="#eef6ef", stroke=FIELD, min_w=200)
    f.append(box_irq)
    # q1 «так» → переривання
    f.append(arrow(cx + w1 / 2, 110, 740 - wi / 2, 160, color=FIELD))
    f.append(text(cx + w1 / 2 + 10, 100, "так", size=12, color=FIELD, bold=True, anchor="start"))
    # q2 «так» → переривання
    f.append(arrow(cx + w2 / 2, 230, 740 - wi / 2, 182, color=FIELD))
    f.append(text(cx + w2 / 2 + 10, 224, "так", size=12, color=FIELD, bold=True, anchor="start"))

    # опитування (під q2 — обидва «ні»)
    box_poll, wp, hp = textbox(cx, 350, "ОПИТУВАННЯ", size=14, bold=True,
                               color=POS, fill="#fdf2f2", stroke=POS, min_w=200)
    f.append(box_poll)
    f.append(arrow(cx, 230 + h2 / 2, cx, 350 - hp / 2, color=POS))
    f.append(text(cx + 12, 295, "ні", size=12, color=POS, bold=True, anchor="start"))

    f.append(text(W / 2, 430, "Безпека (аварія, перегрів) — переривання поза чергою, хай там що.",
                  size=11.5, bold=True))
    f.append(text(W / 2, 452, "Саму обробку події майже завжди виносять у loop() через прапорець.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "decision-flow.svg"), W, H, *f)


# ── 3. П'ять критеріїв: вісь опитування ↔ переривання ───────────────────────
def fig_criteria():
    W, H = 940, 392
    f = [text(W / 2, 30, "П'ять осей рішення", size=17, bold=True)]
    f.append(text(W / 2, 52, "кожна хилить у свій бік; дивляться на загальну картину",
                  size=12, color=MUTED, italic=True))

    # підписи полюсів
    f.append(text(250, 86, "← ОПИТУВАННЯ", size=12, color=POS, bold=True))
    f.append(text(690, 86, "ПЕРЕРИВАННЯ →", size=12, color=FIELD, bold=True))

    rows = [
        ("Частота",          "потік подій",        "поодинокі"),
        ("Терміновість",     "можна зачекати",     "вмить"),
        ("Передбачуваність", "рівномірні",         "випадкові"),
        ("Ціна пропуску",    "не страшно",         "неприпустимо"),
        ("Складність",       "важить простота",    "готові до ISR"),
    ]
    x_lo, x_hi = 230, 710
    y0 = 116
    for i, (name, lo, hi) in enumerate(rows):
        y = y0 + i * 50
        f.append(text(40, y + 4, name, size=12.5, bold=True, anchor="start"))
        f.append(line(x_lo, y, x_hi, y, color=MUTED, sw=1.4))
        # полюси
        f.append(circle(x_lo, y, 5, fill="#fdecea", stroke=POS, sw=2))
        f.append(circle(x_hi, y, 5, fill="#eef6ef", stroke=FIELD, sw=2))
        f.append(text(x_lo - 12, y + 4, lo, size=10.5, color=POS, anchor="end"))
        f.append(text(x_hi + 12, y + 4, hi, size=10.5, color=FIELD, anchor="start"))

    f.append(text(W / 2, 378, "Тягнуть у різні боки (часта, але критична)? — сигнал брати ГІБРИД.",
                  size=11.5, bold=True))
    render(os.path.join(IMG, "criteria.svg"), W, H, *f)


# ── 4. Гібрид: ISR ловить і відмічає, loop обробляє ─────────────────────────
def fig_hybrid():
    W, H = 900, 392
    f = [text(W / 2, 30, "Гібрид: переривання ловить, опитування прапорця обробляє", size=16, bold=True)]
    f.append(text(W / 2, 52, "миттєвість — від переривання, простота обробки — від опитування",
                  size=12, color=MUTED, italic=True))

    # подія
    ev, we, he = textbox(120, 150, "подія\n(вмить)", size=12, bold=True,
                         fill="#fff6e0", stroke="#caa24a", min_w=120)
    f.append(ev)

    # ISR
    isr, wisr, hisr = textbox(380, 150, "ISR:\nflag = true", size=13, bold=True,
                              color=FIELD, fill="#eef6ef", stroke=FIELD, min_w=180)
    f.append(isr)
    f.append(arrow(120 + we / 2, 150, 380 - wisr / 2, 150, color=FIELD))
    f.append(text(250, 138, "ловить", size=10.5, color=FIELD, anchor="middle"))

    # прапорець (спільна змінна)
    flag, wf, hf = textbox(380, 250, "volatile flag", size=12, bold=True,
                           fill="#f4f6f8", stroke=INK, min_w=180)
    f.append(flag)
    f.append(arrow(380, 150 + hisr / 2, 380, 250 - hf / 2, color=INK))
    f.append(text(396, 205, "ставить", size=10, color=MUTED, anchor="start"))

    # loop
    loop, wl, hl = textbox(700, 250, "loop():\nбачить flag →\nробить роботу", size=12, bold=True,
                           color=POS, fill="#fdf2f2", stroke=POS, min_w=200)
    f.append(loop)
    f.append(arrow(380 + wf / 2, 250, 700 - wl / 2, 250, color=POS))
    f.append(text(540, 238, "опитує", size=10.5, color=POS, anchor="middle"))

    f.append(rect(60, 320, W - 120, 48, fill="#fbfcff", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(W / 2, 340, "Прапорець РОЗВ'ЯЗУЄ в часі «коли впіймано» і «коли оброблено»:",
                  size=11.5, bold=True))
    f.append(text(W / 2, 358, "реакція лишається миттєвою, а складна обробка — вільною від обмежень ISR.",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "hybrid.svg"), W, H, *f)


# ── 5. Типові задачі на осі опитування ↔ переривання ────────────────────────
def fig_examples():
    W, H = 940, 392
    f = [text(W / 2, 30, "Типові задачі на осі опитування ↔ переривання", size=17, bold=True)]
    f.append(text(W / 2, 52, "де лягає кожна — і чому", size=12, color=MUTED, italic=True))

    # вісь
    x_lo, x_hi = 90, 850
    y = 100
    f.append(line(x_lo, y, x_hi, y, color=INK, sw=2))
    f.append(text(x_lo, 84, "ОПИТУВАННЯ", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(x_hi, 84, "ПЕРЕРИВАННЯ", size=12, color=FIELD, bold=True, anchor="end"))
    f.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2" '
             'marker-end="url(#arrow)"/>' % (x_lo, y, x_hi + 6, y, INK))

    # позиції (0..1) уздовж осі: ліворуч опитування, праворуч переривання
    items = [
        (0.06, "Навігація меню",          POS,   "спокійно — опитуванням"),
        (0.30, "Кнопка під палець",       POS,   "будь-як; усунути брязкіт"),
        (0.50, "Читання давача 100 мс",   "#8a5a00", "найкраще — апаратним таймером"),
        (0.74, "Лічильник імпульсів",     FIELD, "інакше проґавиш між перевірками"),
        (0.94, "Аварійний стоп",          FIELD, "вмить + не можна проґавити"),
    ]
    up = True
    for pos, name, col, note in items:
        x = x_lo + pos * (x_hi - x_lo)
        f.append(circle(x, y, 6, fill=BG, stroke=col, sw=2.4))
        if up:
            ty = y - 26
            f.append(line(x, y - 6, x, ty + 6, color=col, sw=1.2, dash="3 3"))
            f.append(text(x, ty, name, size=12, color=col, bold=True))
            f.append(text(x, ty - 18, note, size=9.5, color=MUTED))
        else:
            ty = y + 38
            f.append(line(x, y + 6, x, ty - 14, color=col, sw=1.2, dash="3 3"))
            f.append(text(x, ty, name, size=12, color=col, bold=True))
            f.append(text(x, ty + 16, note, size=9.5, color=MUTED))
        up = not up

    f.append(rect(60, 300, W - 120, 66, fill="#fbfcff", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(W / 2, 324, "Прийом по UART і енкодер — посередині: ГІБРИД",
                  size=12, bold=True))
    f.append(text(W / 2, 346, "(залізо ловить перериванням у буфер, ви спокійно опитуєте буфер).",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "examples.svg"), W, H, *f)


# ── (вставка math) 6. Бюджет: U = f · t(ISR), приклади від 1% до 120% ────────
def fig_budget_formula():
    W, H = 900, 360
    f = [text(W / 2, 30, "Частка CPU = частота × тривалість ISR", size=17, bold=True)]
    f.append(text(W / 2, 52, "не тривалість однієї ISR вирішує, а її ДОБУТОК на частоту",
                  size=12, color=MUTED, italic=True))

    # формула в рамці
    fb = fitbox(330, 78, 240, 46, "U = f · t(ISR)", size=20, bold=True,
                fill="#f4f6f8", stroke=INK)
    f.append(fb)

    rows = [
        ("1 кГц",   "10 мкс", "1 %",   "дрібниця",  FIELD, "+"),
        ("10 кГц",  "5 мкс",  "5 %",   "норма",     FIELD, "+"),
        ("50 кГц",  "8 мкс",  "40 %",  "важко",     "#8a5a00", "±"),
        ("200 кГц", "6 мкс",  "120 %", "неможливо", POS,   "−"),
    ]
    y0 = 158
    # шапка
    f.append(text(120, y0 - 14, "частота", size=11, color=MUTED, anchor="middle"))
    f.append(text(300, y0 - 14, "× ISR", size=11, color=MUTED, anchor="middle"))
    f.append(text(470, y0 - 14, "= частка", size=11, color=MUTED, anchor="middle"))
    for i, (fr, ti, u, note, col, sign) in enumerate(rows):
        y = y0 + i * 42
        f.append(rect(60, y - 22, 600, 36, fill="#fbfcff", stroke=col, sw=1.4, rx=8))
        f.append(text(120, y, fr, size=13, bold=True, anchor="middle"))
        f.append(text(300, y, ti, size=13, bold=True, anchor="middle"))
        f.append(text(470, y, u, size=14, color=col, bold=True, anchor="middle"))
        f.append(text(600, y, note, size=11, color=col, anchor="middle"))
    f.append(text(W / 2, 340, "Кілька джерел — додай їхні частки: U(сума) = Σ fᵢ · t(ISR)ᵢ.",
                  size=12, bold=True))
    render(os.path.join(IMG, "budget-formula.svg"), W, H, *f)


# ── (вставка math) 7. Обрив: при f·t ≥ 1 переривання наздоганяють себе ───────
def fig_overrun():
    W, H = 900, 380
    f = [text(W / 2, 30, "Обрив: коли f · t(ISR) сягає 1", size=17, bold=True)]
    f.append(text(W / 2, 52, "ISR не встигає завершитися до наступного спрацювання — події губляться",
                  size=12, color=MUTED, italic=True))

    # три стани шкалою заповнення
    cols = [
        (150, 0.25, FIELD, "f·t = 25 %", "ISR і main\nуміщаються"),
        (450, 0.85, "#8a5a00", "f·t = 85 %", "main голодує —\nмало часу лишилось"),
        (750, 1.15, POS, "f·t ≥ 100 %", "overrun:\nподії губляться"),
    ]
    bar_w, bar_h, base = 140, 180, 110
    for cx, frac, col, lab, note in cols:
        x = cx - bar_w / 2
        # повна труба (бюджет = 1 секунда)
        f.append(rect(x, base, bar_w, bar_h, fill=BG, stroke=MUTED, sw=1.5, rx=8))
        fill_h = min(1.0, frac) * bar_h
        f.append(rect(x, base + bar_h - fill_h, bar_w, fill_h,
                      fill="#eef6ef" if frac < 1 else "#fdecea", stroke="none", sw=0, rx=8))
        # лінія 100%
        f.append(line(x - 6, base, x + bar_w + 6, base, color=INK, sw=1.4, dash="4 3"))
        f.append(text(cx, lab and base - 12, lab, size=12, color=col, bold=True))
        if frac > 1:
            # «переповнення» над трубою
            over_h = (frac - 1) * bar_h
            f.append(rect(x, base - over_h, bar_w, over_h, fill="#fdecea",
                          stroke=POS, sw=1.4, rx=4))
            f.append(text(cx, base - over_h - 8, "↑ не вміщається", size=10, color=POS, bold=True))
        f.append(mtext(cx, base + bar_h + 22, note, size=10.5, color=MUTED))

    f.append(text(W / 2, 366,
                  "Лік один із трьох: коротша ISR · менша частота · віддати потік залізу/DMA.",
                  size=12, bold=True))
    render(os.path.join(IMG, "overrun.svg"), W, H, *f)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  ДЕТАЛЬНА версія (polling-vs-interrupts-d.md) — глибші фігури             ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# ── D1. Ланцюг латентності переривання: від фронту до першого рядка ISR ──────
def fig_latency_chain():
    W, H = 940, 360
    f = [text(W / 2, 30, "Ланцюг латентності: від фронту на ніжці до першого рядка ISR", size=16, bold=True)]
    f.append(text(W / 2, 52, "«12 тактів» ARM — лише ядро; повна затримка складається з ланок",
                  size=12, color=MUTED, italic=True))

    # шість ланок як стрічка зліва направо; стрілки між ними
    seg = [
        ("детекція\n+ синхро",    "1–2 такти",   "#8a5a00"),
        ("дотягти\nінструкцію",   "0–кілька",    POS),
        ("запис\nконтексту",      "8 слів",      FIELD),
        ("вибірка\nвектора",      "з таблиці",   NEG),
        ("пролог\nкомпілятора",   "регістри",    "#8a5a00"),
        ("ПЕРШИЙ рядок\nISR",     "почалося",    FIELD),
    ]
    n = len(seg)
    x0, x1 = 40, 900
    gap = 12
    bw = ((x1 - x0) - gap * (n - 1)) / n
    cy = 150
    bh = 56
    f.append(text(x0, 100, "фронт на ніжці", size=11, color=MUTED, anchor="start", bold=True))
    f.append(text(x1, 100, "час →", size=11, color=MUTED, anchor="end"))
    for i, (lab, cyc, col) in enumerate(seg):
        bx = x0 + i * (bw + gap)
        f.append(rect(bx, cy, bw, bh, fill="#fbfcff", stroke=col, sw=1.6, rx=8))
        f.append(mtext(bx + bw / 2, cy + 22, lab, size=11.5, color=col, bold=True))
        f.append(text(bx + bw / 2, cy + bh + 18, cyc, size=10, color=MUTED))
        if i < n - 1:
            ax = bx + bw
            f.append(arrow(ax + 1, cy + bh / 2, ax + gap - 1, cy + bh / 2, color=INK, sw=1.6))

    # довідка: числа для типових ядер
    f.append(rect(40, 258, W - 80, 66, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(W / 2, 282, "Вхід у переривання (без очікувань пам'яті):", size=11.5, bold=True))
    f.append(text(W / 2, 302, "AVR ≈ 4 такти · Cortex-M0 = 16 · M0+ = 15 · M3/M4 = 12 · тейл-чейн M3/M4 = 6",
                  size=11.5, color=INK, bold=True))
    f.append(text(W / 2, 320, "Cortex-M — фіксоване число тактів (детерміновано); на AVR довша інструкція дотягується до кінця.",
                  size=10.5, color=MUTED))
    render(os.path.join(IMG, "latency-chain.svg"), W, H, *f)


# ── D2. Часова діаграма опитування: період, гірша латентність, вікно пропуску ─
def fig_polling_timing():
    W, H = 940, 430
    f = [text(W / 2, 30, "Опитування в часі: період, найгірша затримка, вікно сліпоти", size=16, bold=True)]
    f.append(text(W / 2, 52, "подія коротша за період падає в проміжок між перевірками — і зникає",
                  size=12, color=MUTED, italic=True))

    x0, x1 = 70, 880
    span = x1 - x0
    # верхня лінія: моменти перевірки (тики циклу)
    yc = 120
    f.append(text(x0 - 8, yc + 4, "перевірки", size=11, color=NEG, anchor="end", bold=True))
    n = 6
    xs = [x0 + i * span / (n - 1) for i in range(n)]
    f.append(line(x0, yc, x1, yc, color=MUTED, sw=1.2))
    for i, x in enumerate(xs):
        f.append(line(x, yc - 10, x, yc + 10, color=NEG, sw=2.2))
    # позначка періоду T між двома тиками
    xa, xb = xs[1], xs[2]
    f.append(line(xa, yc + 22, xb, yc + 22, color=INK, sw=1.2))
    f.append(line(xa, yc + 17, xa, yc + 27, color=INK, sw=1.2))
    f.append(line(xb, yc + 17, xb, yc + 27, color=INK, sw=1.2))
    f.append(text((xa + xb) / 2, yc + 38, "період T", size=11, bold=True))

    # середня лінія: довга подія — буде впіймана, але із запізненням
    yl = 220
    f.append(text(x0 - 8, yl + 4, "довга подія", size=11, color=FIELD, anchor="end", bold=True))
    ev_a, ev_b = xs[0] + 18, xs[3] + 10
    f.append(rect(ev_a, yl - 12, ev_b - ev_a, 24, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=5))
    f.append(text((ev_a + ev_b) / 2, yl + 5, "триває > T", size=10.5, color=FIELD, bold=True))
    # впіймана на першій перевірці ВСЕРЕДИНІ події (xs[1])
    f.append(circle(xs[1], yl, 5, fill=BG, stroke=INK, sw=2))
    f.append(line(xs[1], yl - 20, xs[1], yl - 12, color=INK, sw=1))
    f.append(text(xs[1], yl - 26, "впіймана", size=10, color=INK, bold=True))
    # затримка від початку події до впіймання
    f.append(line(ev_a, yl + 22, xs[1], yl + 22, color=POS, sw=1.4))
    f.append(text((ev_a + xs[1]) / 2, yl + 38, "затримка ≤ T", size=10, color=POS, bold=True))

    # нижня лінія: коротка подія — падає між перевірками, пропала
    ys = 320
    f.append(text(x0 - 8, ys + 4, "коротка подія", size=11, color=POS, anchor="end", bold=True))
    sa = (xs[2] + xs[3]) / 2 - 10
    sb = sa + 22
    f.append(rect(sa, ys - 12, sb - sa, 24, fill="#fdecea", stroke=POS, sw=1.6, rx=5))
    f.append(text((sa + sb) / 2, ys + 32, "триває < T", size=10, color=POS, anchor="middle", bold=True))
    f.append(text((sa + sb) / 2, ys - 20, "✗ пропала", size=10.5, color=POS, bold=True))
    # показати, що обидві сусідні перевірки її не бачать
    for x in (xs[2], xs[3]):
        f.append(line(x, ys - 14, x, ys + 14, color=NEG, sw=1, dash="2 2"))

    f.append(rect(60, 370, W - 120, 46, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(W / 2, 391, "Умова захоплення опитуванням: тривалість події ≥ T. Найгірша затримка реакції = T.",
                  size=11.5, bold=True))
    f.append(text(W / 2, 409, "Надійно (з полем на джитер): T ≤ (тривалість події) / 2 — «Найквіст для подій».",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "polling-timing.svg"), W, H, *f)


# ── D3. Порвате читання: 16-бітна змінна на 8-бітному ядрі ───────────────────
def fig_race_torn():
    W, H = 900, 400
    f = [text(W / 2, 30, "Порвате читання: чому спільна змінна потребує захисту", size=16, bold=True)]
    f.append(text(W / 2, 52, "16-бітне число на 8-бітному ядрі читається двома тактами — між ними влазить ISR",
                  size=12, color=MUTED, italic=True))

    # змінна з двох байтів
    def byte(x, y, lab, val, col):
        return (rect(x, y, 90, 40, fill="#fbfcff", stroke=col, sw=1.6, rx=6) +
                text(x + 45, y + 17, lab, size=10, color=MUTED) +
                text(x + 45, y + 34, val, size=13, color=col, bold=True))

    # крок 1
    f.append(text(150, 100, "1) loop() читає старший байт", size=12, bold=True, anchor="start"))
    f.append(byte(150, 112, "hi", "0x01", FIELD))
    f.append(byte(250, 112, "lo", "0xFF", MUTED))
    f.append(text(360, 137, "значення = 0x01FF (511)", size=11, color=MUTED, anchor="start"))

    # крок 2 — влазить ISR
    f.append(text(150, 192, "2) тут спрацьовує ISR: turns++  →  0x01FF стає 0x0200", size=12, bold=True, color=POS, anchor="start"))
    f.append(byte(150, 204, "hi", "0x02", POS))
    f.append(byte(250, 204, "lo", "0x00", POS))
    f.append(text(360, 229, "у пам'яті вже 0x0200 (512)", size=11, color=POS, anchor="start"))

    # крок 3 — loop дочитує молодший
    f.append(text(150, 284, "3) loop() дочитує молодший байт — уже НОВИЙ", size=12, bold=True, anchor="start"))
    f.append(byte(150, 296, "hi (стар.)", "0x01", FIELD))
    f.append(byte(250, 296, "lo (нов.)", "0x00", POS))

    # результат
    res, wr, hr = textbox(650, 320, "склеїлось 0x0100 = 256\n— НЕ 511 і НЕ 512", size=12, bold=True,
                          color=POS, fill="#fdecea", stroke=POS, min_w=230)
    f.append(res)
    f.append(text(650, 250, "Лік: читати під критичною секцією", size=11, bold=True))
    f.append(text(650, 270, "(коротко заборонити переривання)", size=10.5, color=MUTED))
    render(os.path.join(IMG, "race-torn.svg"), W, H, *f)


# ── D4. Кільцевий буфер SPSC: ISR-виробник, loop-споживач ───────────────────
def fig_spsc_ring():
    W, H = 900, 430
    f = [text(W / 2, 30, "Кільцевий буфер: ISR кладе (head), loop бере (tail)", size=16, bold=True)]
    f.append(text(W / 2, 52, "один виробник, один споживач — по одному індексу на кожного, без замка",
                  size=12, color=MUTED, italic=True))

    cx, cy, R = W / 2, 235, 96
    N = 8
    import math
    # комірки по колу
    filled = {5, 6, 7, 0}  # зайняті: від tail до head
    for i in range(N):
        ang = -math.pi / 2 + i * 2 * math.pi / N
        x = cx + R * math.cos(ang)
        y = cy + R * math.sin(ang)
        is_f = i in filled
        f.append(circle(x, y, 22, fill="#eef6ef" if is_f else BG,
                        stroke=FIELD if is_f else MUTED, sw=2 if is_f else 1.4))
        f.append(text(x, y + 5, str(i), size=13, color=INK if is_f else MUTED, bold=is_f))

    # head (куди ISR покладе наступне) — після 0 → 1
    ah = -math.pi / 2 + 1 * 2 * math.pi / N
    hx, hy = cx + (R + 46) * math.cos(ah), cy + (R + 46) * math.sin(ah)
    f.append(text(hx, hy, "head", size=12, color=POS, bold=True))
    f.append(text(hx, hy + 16, "ISR пише сюди", size=9.5, color=POS))
    f.append(arrow(hx, hy + 22, cx + (R + 6) * math.cos(ah), cy + (R + 6) * math.sin(ah), color=POS))

    # tail (звідки loop візьме) — 5
    at = -math.pi / 2 + 5 * 2 * math.pi / N
    tx, ty = cx + (R + 52) * math.cos(at), cy + (R + 52) * math.sin(at)
    f.append(text(tx, ty, "tail", size=12, color=NEG, bold=True))
    f.append(text(tx, ty + 16, "loop() читає", size=9.5, color=NEG))
    f.append(arrow(tx - 4, ty - 6, cx + (R + 6) * math.cos(at), cy + (R + 6) * math.sin(at), color=NEG))

    # ролі по боках
    f.append(rect(30, 100, 200, 70, fill="#fdecea", stroke=POS, sw=1.5, rx=10))
    f.append(text(130, 124, "ISR (виробник)", size=12, color=POS, bold=True))
    f.append(text(130, 144, "пише buf[head],", size=10.5))
    f.append(text(130, 160, "потім head++", size=10.5))

    f.append(rect(670, 100, 200, 70, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=10))
    f.append(text(770, 124, "loop() (споживач)", size=12, color=NEG, bold=True))
    f.append(text(770, 144, "читає buf[tail],", size=10.5))
    f.append(text(770, 160, "потім tail++", size=10.5))

    f.append(rect(60, 372, W - 120, 46, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(W / 2, 393, "Кожен індекс змінює ЛИШЕ свій власник → запис одного не рве іншого (порядок важливий).",
                  size=11.5, bold=True))
    f.append(text(W / 2, 411, "Порожньо: head == tail. Повно: наступний head наздогнав tail (одна комірка — жертва).",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "spsc-ring.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_tools()
    fig_decision_flow()
    fig_criteria()
    fig_hybrid()
    fig_examples()
    fig_budget_formula()
    fig_overrun()
    # детальна версія
    fig_latency_chain()
    fig_polling_timing()
    fig_race_torn()
    fig_spsc_ring()
    print("OK: figures written to", IMG)

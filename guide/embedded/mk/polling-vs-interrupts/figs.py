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


if __name__ == "__main__":
    fig_two_tools()
    fig_decision_flow()
    fig_criteria()
    fig_hybrid()
    fig_examples()
    fig_budget_formula()
    fig_overrun()
    print("OK: figures written to", IMG)

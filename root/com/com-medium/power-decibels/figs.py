# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: величезний діапазон потужностей радіо (чому логарифм) ───────────

def fig_range():
    W, H = 760, 300
    ax, axw, ay = 80, 600, 150
    p = []
    p.append(line(ax, ay, ax + axw, ay, color=INK, sw=2))
    p.append(arrow(ax + axw - 20, ay, ax + axw, ay, color=INK, sw=2))

    # рівномірні позиції логарифмічних поділок (бо лінійно вони б злиплися)
    marks = [
        (0.00, "10⁻¹³ Вт", "приймач", FIELD),
        (0.31, "10⁻⁹",     None,       MUTED),
        (0.46, "10⁻⁶",     "1 мкВт",  MUTED),
        (0.69, "10⁻³",     "1 мВт",   MUTED),
        (1.00, "1 Вт",     "передавач", POS),
    ]
    for frac, lo, hi, col in marks:
        x = ax + frac * axw
        p.append(line(x, ay - 7, x, ay + 7, color=INK, sw=1.4))
        p.append(text(x, ay + 22, lo, size=11, color=MUTED))
        if hi:
            p.append(text(x, ay - 14, hi, size=11, color=col, bold=True))

    p.append(text(ax + axw / 2, ay + 56, "розмах ≈ 13 порядків  (× 10 000 000 000 000)",
                  size=13, color=POS, bold=True))

    b = fitbox(ax - 20, ay + 76, axw + 40, 56,
               "Лінійно «0.000000000001 Вт» писати незручно й легко помилитися.\n"
               "Логарифм стискає кожне «×10» в однаковий крок — числа стають охайними.",
               size=12, color=INK, fill="#eafaf0", stroke=FIELD)
    p.append(b)

    render(os.path.join(OUT, "range.svg"), W, H, *p,
           title="Потужності радіо різняться в трильйони разів")


# ── Фігура 2: децибел = логарифмічне відношення (орієнтири) ───────────────────

def fig_db_ratio():
    W, H = 760, 320
    p = []
    b, bw, bh = textbox(W / 2, 78, "dB = 10 · log₁₀( P₂ / P₁ )",
                        size=20, color=INK, bold=True, min_w=360)
    p.append(b)
    p.append(text(W / 2, 116, "відношення двох потужностей у логарифмічній шкалі — не абсолютна величина",
                  size=12, color=MUTED, italic=True))

    rows = [
        ("0 dB",   "× 1",  "без зміни", INK),
        ("+3 dB",  "≈ × 2", "удвічі більше", POS),
        ("+10 dB", "× 10",  "удесятеро", POS),
        ("+20 dB", "× 100", "усто", POS),
        ("−3 dB",  "≈ ÷ 2", "удвічі менше", NEG),
        ("−10 dB", "÷ 10",  "удесятеро менше", NEG),
    ]
    x0, y0, rw, rh, gap = 90, 150, 270, 34, 14
    for i, (a, b2, c, col) in enumerate(rows):
        col_i = i // 3
        row_i = i % 3
        x = x0 + col_i * (rw + 40)
        y = y0 + row_i * (rh + gap)
        p.append(rect(x, y, rw, rh, fill=FILL, stroke=col, sw=1.6))
        p.append(text(x + 52, y + rh / 2 + 5, a, size=14, color=col, bold=True))
        p.append(text(x + 130, y + rh / 2 + 5, b2, size=14, color=INK, bold=True))
        p.append(text(x + 210, y + rh / 2 + 5, c, size=10.5, color=MUTED))

    render(os.path.join(OUT, "db-ratio.svg"), W, H, *p,
           title="Децибел — це відношення в логарифмічній шкалі")


# ── Фігура 3: множення стає додаванням (серце зручності) ──────────────────────

def fig_mult_to_add():
    W, H = 780, 320
    p = []
    cy_top, cy_bot = 130, 240
    stages = [
        ("підсилювач", "×10", "+10 dB", POS),
        ("кабель",     "÷2",  "−3 dB",  NEG),
        ("антена",     "×4",  "+6 dB",  POS),
    ]
    x = 70
    bw, gap = 150, 60
    centers = []
    for name, lin, db, col in stages:
        p.append(rect(x, cy_top - 30, bw, 60, fill=FILL, stroke=col, sw=2))
        p.append(text(x + bw / 2, cy_top - 6, name, size=13, color=INK, bold=True))
        p.append(text(x + bw / 2, cy_top + 16, lin + "   →   " + db, size=13, color=col, bold=True))
        centers.append(x + bw / 2)
        x_next = x + bw + gap
        if x_next < 70 + 3 * (bw + gap) - gap:
            p.append(text(x + bw + gap / 2, cy_top + 4, "·", size=26, color=MUTED, bold=True))
        x = x_next

    # підсумок: у разах vs у децибелах
    p.append(line(60, cy_bot - 18, W - 60, cy_bot - 18, color=MUTED, sw=1, dash="4 4"))
    p.append(text(W / 2, cy_bot + 6,
                  "у разах:  × 10 · ÷ 2 · × 4  =  × 20      (морочливе множення)",
                  size=13.5, color=MUTED))
    b = fitbox(150, cy_bot + 20, W - 300, 40,
               "у децибелах:  +10 − 3 + 6  =  +13 dB   (а +13 dB = ×20)",
               size=14, color=INK, bold=True, fill="#eafaf0", stroke=FIELD)
    p.append(b)

    render(os.path.join(OUT, "mult-to-add.svg"), W, H, *p,
           title="У логарифмі множення ланцюга стає простим додаванням")


# ── Фігура 4: dBm — абсолютна потужність відносно 1 мВт ───────────────────────

def fig_dbm():
    W, H = 760, 300
    ax, axw, ay = 90, 580, 150
    p = []
    p.append(line(ax, ay, ax + axw, ay, color=INK, sw=2))
    p.append(arrow(ax + axw - 20, ay, ax + axw, ay, color=INK, sw=2))

    marks = [
        (0.00, "−90 dBm", "1 пВт", FIELD, True),
        (0.20, "−60",     "1 нВт", MUTED, False),
        (0.40, "−30",     "1 мкВт", MUTED, False),
        (0.60, "0 dBm",   "1 мВт", INK,   True),
        (0.80, "+20",     "100 мВт", MUTED, False),
        (1.00, "+30",     "1 Вт",  POS,   True),
    ]
    for frac, lo, hi, col, strong in marks:
        x = ax + frac * axw
        p.append(line(x, ay - 7, x, ay + 7, color=INK, sw=1.4))
        p.append(text(x, ay + 22, lo, size=11, color=(col if strong else MUTED), bold=strong))
        p.append(text(x, ay - 14, hi, size=10.5, color=col, bold=strong))

    p.append(text(ax + 0.60 * axw, ay + 46, "точка відліку: 0 dBm = 1 мВт",
                  size=12, color=INK, bold=True))
    b = fitbox(ax - 10, ay + 64, axw + 20, 52,
               "Маленька «m» = «відносно 1 мВт». Від'ємні dBm — слабші за 1 мВт сигнали;\n"
               "чим глибше в мінус, тим слабший. Уся «трильйонність» лягає в +30…−110 dBm.",
               size=11.5, color=INK, fill=FILL, stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "dbm.svg"), W, H, *p,
           title="dBm — абсолютна потужність відносно 1 мілівата")


# ── Фігура 5: правило трійок і десяток ───────────────────────────────────────

def fig_three_ten():
    W, H = 740, 300
    p = []
    # дві цеглинки
    b1, w1, h1 = textbox(W / 2 - 130, 90, "+3 dB  =  × 2", size=18, color=POS, bold=True, min_w=200)
    b2, w2, h2 = textbox(W / 2 + 130, 90, "+10 dB  =  × 10", size=18, color=POS, bold=True, min_w=200)
    p.append(b1); p.append(b2)
    p.append(text(W / 2, 130, "дві цеглинки, з яких складається будь-яке відношення",
                  size=12, color=MUTED, italic=True))

    rows = [
        ("+13 dB", "= +10 +3", "= ×10 ×2", "= × 20", POS),
        ("+23 dB", "= +10 +10 +3", "= ×10 ×10 ×2", "= × 200", POS),
        ("−7 dB",  "= −10 +3", "= ÷10 ×2", "= ÷ 5", NEG),
    ]
    y = 165
    for a, b_, c, d, col in rows:
        p.append(text(150, y + 14, a, size=14, color=col, bold=True, anchor="start"))
        p.append(text(255, y + 14, b_, size=13, color=MUTED, anchor="start"))
        p.append(text(420, y + 14, c, size=13, color=INK, anchor="start"))
        p.append(text(580, y + 14, d, size=14, color=col, bold=True, anchor="start"))
        y += 34

    render(os.path.join(OUT, "three-ten.svg"), W, H, *p,
           title="Правило трійок і десяток: розклади dB — і прикинеш рази в умі")


# ── Фігура 6: децибели скрізь (спільна мова тракту) ──────────────────────────

def fig_db_everywhere():
    W, H = 780, 300
    p = []
    cards = [
        ("Підсилення", "+ dB", "додає потужності", POS),
        ("Втрати",     "− dB", "кабель, стіна, шлях", NEG),
        ("SNR",        "dB",   "сигнал до шуму", INK),
        ("Виграш антени", "dBi", "понад всебічну", FIELD),
    ]
    cw, ch, gap = 170, 110, 18
    total = 4 * cw + 3 * gap
    x = (W - total) / 2
    y = 80
    for title_, unit, sub, col in cards:
        p.append(rect(x, y, cw, ch, fill=FILL, stroke=col, sw=2))
        p.append(text(x + cw / 2, y + 30, title_, size=14, color=col, bold=True))
        p.append(text(x + cw / 2, y + 60, unit, size=20, color=INK, bold=True))
        p.append(fitbox(x + 8, y + 74, cw - 16, 28, sub, size=10.5, color=MUTED, fill=BG, stroke=BG, sw=0))
        x += cw + gap

    p.append(text(W / 2, y + ch + 40,
                  "Усе це — відношення, тож усе говорить однією мовою децибел і просто складається.",
                  size=13, color=INK, bold=True))

    render(os.path.join(OUT, "db-everywhere.svg"), W, H, *p,
           title="Децибел — спільна мова всього радіотракту")


# ── Фігура 7: читаємо специфікацію — запас лінії ─────────────────────────────

def fig_spec_read():
    W, H = 760, 300
    ax, axw, ay = 110, 560, 150
    p = []
    p.append(line(ax, ay, ax + axw, ay, color=INK, sw=2))
    p.append(arrow(ax + axw - 20, ay, ax + axw, ay, color=INK, sw=2))
    p.append(text(ax + axw + 4, ay + 5, "dBm", size=12, color=MUTED, anchor="start"))

    # дві точки: чутливість RX (−95) і потужність TX (+20)
    x_rx = ax + 0.10 * axw
    x_tx = ax + 0.92 * axw
    p.append(line(x_rx, ay - 7, x_rx, ay + 7, color=NEG, sw=2))
    p.append(text(x_rx, ay + 24, "−95 dBm", size=12, color=NEG, bold=True))
    p.append(text(x_rx, ay - 14, "чутливість RX", size=11, color=NEG, bold=True))
    p.append(line(x_tx, ay - 7, x_tx, ay + 7, color=POS, sw=2))
    p.append(text(x_tx, ay + 24, "+20 dBm", size=12, color=POS, bold=True))
    p.append(text(x_tx, ay - 14, "потужність TX", size=11, color=POS, bold=True))

    # дужка-різниця між ними
    p.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
             'stroke-width="1.8" marker-end="url(#arrow)" marker-start="url(#arrow)"/>'
             % (x_rx, ay - 40, (x_rx + x_tx) / 2, ay - 78, x_tx, ay - 40, INK))
    p.append(text((x_rx + x_tx) / 2, ay - 86, "запас на всі втрати = 115 дБ",
                  size=13, color=INK, bold=True))

    b = fitbox(ax - 30, ay + 56, axw + 60, 60,
               "Різниця двох чисел даташита — твій бюджет у децибелах:\n"
               "(+20) − (−95) = 115 дБ. Стільки можна «втратити» на дорозі, поки зв'язок живий.",
               size=12, color=INK, fill="#eafaf0", stroke=FIELD)
    p.append(b)

    render(os.path.join(OUT, "spec-read.svg"), W, H, *p,
           title="Читаємо даташит: запас лінії — різниця TX і чутливості RX")


if __name__ == "__main__":
    fig_range()
    fig_db_ratio()
    fig_mult_to_add()
    fig_dbm()
    fig_three_ten()
    fig_db_everywhere()
    fig_spec_read()
    print("OK: figures written to", OUT)

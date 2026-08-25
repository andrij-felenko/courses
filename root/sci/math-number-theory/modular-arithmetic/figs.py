# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── clock: годинник як арифметика mod 12 ─────────────────────────────────────
# Ідея: циферблат — наочна модель лишків. Та сама точка кола = той самий лишок
# (15 і 3); рух назад теж лишається на колі, тож −1 має додатного двійника 11.
def fig_clock():
    W, H = 900, 540
    cx, cy, R = 250, 300, 165
    p = []

    # циферблат
    p.append(circle(cx, cy, R, fill="#fcfcff", stroke=INK, sw=2.5))
    for n in range(12):
        ang = math.radians(-90 + n * 30)          # 12 угорі, за годинниковою
        label = 12 if n == 0 else n
        lx, ly = cx + R * math.cos(ang), cy + R * math.sin(ang)
        tx, ty = cx + (R - 28) * math.cos(ang), cy + (R - 28) * math.sin(ang)
        p.append(line(cx + (R - 8) * math.cos(ang), cy + (R - 8) * math.sin(ang),
                      lx, ly, color=MUTED, sw=1.5))
        col, bold, size = INK, False, 14
        if label == 3:   col, bold, size = FIELD, True, 16
        if label == 11:  col, bold, size = POS, True, 16
        p.append(text(tx, ty + size * 0.35, label, size=size, color=col, bold=bold))

    # вісь годин: стрілка вперед на 3 (зелена), стрілка назад на 11≡−1 (червона)
    p.append(circle(cx, cy, 4, fill=INK, stroke=INK, sw=1))
    a3 = math.radians(-90 + 3 * 30)
    p.append(arrow(cx, cy, cx + (R - 40) * math.cos(a3), cy + (R - 40) * math.sin(a3),
                   color=FIELD, sw=3))
    a11 = math.radians(-90 + 11 * 30)
    p.append(arrow(cx, cy, cx + (R - 40) * math.cos(a11), cy + (R - 40) * math.sin(a11),
                   color=POS, sw=3))
    p.append(text(cx, cy + R + 34, "повний оберт = +12 → нічого не змінює",
                  size=12.5, color=MUTED, italic=True))

    # права колонка: те саме мовою лишків
    xL = 520
    p.append(text(xL, 128, "Те саме мовою лишків:", size=15, color=INK, anchor="start", bold=True))
    rows = [
        ("15 год = 3 год",   "15 = 1·12 + 3",     "15 ≡ 3 (mod 12)",  FIELD),
        ("27 год = 3 год",   "27 = 2·12 + 3",     "27 ≡ 3 (mod 12)",  FIELD),
        ("«за годину до 12»", "−1 = (−1)·12 + 11", "−1 ≡ 11 (mod 12)", POS),
        ("«дві години тому»", "−2 = (−1)·12 + 10", "−2 ≡ 10 (mod 12)", POS),
    ]
    y = 166
    for head, mid, cong, col in rows:
        p.append(text(xL, y, head, size=13.5, color=INK, anchor="start", bold=True))
        p.append(text(xL + 8, y + 22, mid, size=13, color=MUTED, anchor="start"))
        p.append(text(xL + 8, y + 44, cong, size=14.5, color=col, anchor="start", bold=True))
        y += 78

    p.append(fitbox(xL - 10, 478, 360, 50,
                    "Від'ємне число має додатного «двійника»\nу тому самому колі: −1 ↔ 11",
                    size=12, fill="#f3f5fb", stroke=NEG, sw=2, bold=False))

    render(os.path.join(OUT, "clock.svg"), W, H, *p,
           title="Годинник — це арифметика за модулем 12")


# ── residue-classes: числова пряма складається у m класів ────────────────────
# Ідея: нескінченна пряма «складається» у m кошиків за лишком; усі числа з одним
# лишком потрапляють в один клас і за модулем вважаються рівними.
def fig_residue_classes():
    W, H = 760, 360
    m = 5
    p = []

    # верх: фрагмент числової прямої −2..12 з підписами
    ax = 60
    ay = 90
    aw = W - 120
    lo, hi = -2, 12
    span = hi - lo
    sx = aw / span
    p.append(arrow(ax - 18, ay, ax + aw + 18, ay, color=INK, sw=1.6))
    cols = [POS, FIELD, NEG, "#8a5fb0", MUTED]      # колір за класом 0..4
    for v in range(lo, hi + 1):
        x = ax + (v - lo) * sx
        cls = v % m
        p.append(circle(x, ay, 4, fill=cols[cls], stroke=cols[cls], sw=1))
        p.append(text(x, ay - 12, v, size=11, color=INK))
        # тонка напрямна вниз до свого кошика
        p.append(line(x, ay + 6, x, ay + 22, color=cols[cls], sw=1.0, dash="2 3"))

    p.append(text(ax - 30, ay + 4, "ℤ", size=14, color=INK, anchor="end", bold=True))

    # низ: п'ять кошиків-класів
    by = 200
    bw, bh = 118, 110
    gap = (W - 2 * 40 - m * bw) / (m - 1)
    members = {0: "…  0,  5,  10  …", 1: "…  1,  6,  11  …", 2: "… −2, 2, 7, 12 …",
               3: "…  3,  8,  13  …", 4: "… −1, 4, 9, 14 …"}
    bx = 40
    for cls in range(m):
        p.append(rect(bx, by, bw, bh, fill="#fbfbff", stroke=cols[cls], sw=2))
        p.append(text(bx + bw / 2, by + 26, "клас %d" % cls, size=13, color=cols[cls], bold=True))
        p.append(text(bx + bw / 2, by + 52, "лишок %d" % cls, size=10.5, color=MUTED))
        p.append(text(bx + bw / 2, by + 84, members[cls], size=10, color=INK))
        bx += bw + gap

    p.append(text(W / 2, H - 22,
                  "усі числа з однаковим лишком — один клас: 2 ≡ 7 ≡ 12 (mod 5), а −1 ≡ 4",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "residue-classes.svg"), W, H, *p,
           title="Числова пряма складається у 5 класів лишків за модулем 5")


# ── reduce-anytime: звести можна до або після дії ────────────────────────────
# Ідея: дві стежки до одної відповіді — додати сирі числа й узяти лишок, або
# спершу звести, тоді додати малі. Результат збігається: це й робить ≡ робочою.
def fig_reduce_anytime():
    W, H = 760, 320
    p = []
    yT, yB = 96, 224
    x0 = 70

    def node(x, y, s, col=INK, fill=FILL):
        b, w, h = textbox(x, y, s, size=13, bold=True, color=col, fill=fill, stroke=col, sw=1.8, pad=10)
        return b, w

    # верхня стежка: 13 + 14 = 27 → mod 8 → 3
    p.append(text(x0 - 30, yT, "сирі", size=11, color=MUTED, anchor="end", italic=True))
    b, w1 = node(x0 + 40, yT, "13 + 14"); p.append(b)
    p.append(arrow(x0 + 40 + w1 / 2, yT, 300, yT, color=INK, sw=1.6))
    b, w2 = node(345, yT, "= 27"); p.append(b)
    p.append(arrow(345 + w2 / 2, yT, 470, yT, color=INK, sw=1.6))
    p.append(text(470 + 35, yT - 10, "mod 8", size=11, color=MUTED, anchor="middle"))
    b, w3 = node(545, yT, "3", col=FIELD, fill="#eafaf0"); p.append(b)

    # нижня стежка: 13≡5, 14≡6 → 5+6=11 → mod 8 → 3
    p.append(text(x0 - 30, yB, "спершу\nзвести", size=11, color=MUTED, anchor="end", italic=True))
    b, w1b = node(x0 + 40, yB, "5 + 6", col=NEG, fill="#eef4ff"); p.append(b)
    p.append(text(x0 + 40, yB - 30, "13≡5,  14≡6 (mod 8)", size=10.5, color=MUTED))
    p.append(arrow(x0 + 40 + w1b / 2, yB, 300, yB, color=INK, sw=1.6))
    b, w2b = node(345, yB, "= 11"); p.append(b)
    p.append(arrow(345 + w2b / 2, yB, 470, yB, color=INK, sw=1.6))
    p.append(text(470 + 35, yB - 10, "mod 8", size=11, color=MUTED, anchor="middle"))
    b, w3b = node(545, yB, "3", col=FIELD, fill="#eafaf0"); p.append(b)

    # обидві стежки сходяться → велика рівність праворуч
    p.append(line(545 + w3 / 2, yT, 660, yT, color=FIELD, sw=1.6))
    p.append(line(545 + w3b / 2, yB, 660, yB, color=FIELD, sw=1.6))
    p.append(line(660, yT, 660, yB, color=FIELD, sw=1.6))
    p.append(text(680, (yT + yB) / 2 + 5, "=", size=26, color=FIELD, anchor="start", bold=True))

    p.append(text(W / 2, H - 18,
                  "(a + b) mod m = ((a mod m) + (b mod m)) mod m — зводити можна будь-коли",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "reduce-anytime.svg"), W, H, *p,
           title="Дві стежки, одна відповідь: звести до чи після дії")


# ── applications: один циферблат — багато задач ──────────────────────────────
# Ідея: та сама арифметика mod m обслуговує кільцевий буфер, контрольну суму й
# доповняльний код — змінюється лише модуль і що ми домовилися робити з лишком.
def fig_applications():
    W, H = 760, 300
    p = []
    cards = [
        ("кільцевий буфер", "i = (i + 1) mod N",
         "індекс «загортається»\nна початок", FIELD, "#eafaf0"),
        ("контрольна сума", "s = (s + байт) mod 256",
         "лишок ловить\nспотворення", NEG, "#eef4ff"),
        ("доповняльний код", "−B ≡ 2ⁿ − B (mod 2ⁿ)",
         "віднімання стає\nдодаванням", POS, "#fdecea"),
    ]
    cw, ch = 220, 150
    gap = (W - 2 * 30 - 3 * cw) / 2
    x = 30
    for head, formula, note, col, fill in cards:
        y = 70
        p.append(rect(x, y, cw, ch, fill=fill, stroke=col, sw=2))
        p.append(text(x + cw / 2, y + 30, head, size=14, color=col, bold=True))
        p.append(fitbox(x + 16, y + 48, cw - 32, 34, formula, size=13, bold=True,
                        fill=BG, stroke=col, sw=1.2, color=INK))
        p.append(mtext(x + cw / 2, y + 108, note, size=11, color=INK))
        x += cw + gap

    p.append(text(W / 2, H - 20,
                  "один апарат лишків, різний модуль m — від кільцевого індексу до знакових чисел",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "applications.svg"), W, H, *p,
           title="Та сама арифметика за модулем — у різних задачах")


if __name__ == "__main__":
    fig_clock()
    fig_residue_classes()
    fig_reduce_anytime()
    fig_applications()
    print("OK: figures written to", OUT)

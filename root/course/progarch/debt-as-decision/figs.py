# -*- coding: utf-8 -*-
"""Фігури до кроку «Технічний борг як свідоме рішення, не аварія».
Дві фігури: (A) чотири брами, що відрізняють рішення від аварії;
(B) обмежено проти розмазано — шов збирає борг в одне місце."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')

GREEN_FILL = "#eafaf1"
RED_FILL = "#fdecea"


# ── Фігура A: чотири брами ───────────────────────────────────────────────────
def fig_gates():
    W, H = 900, 402
    parts = []

    x0, w0 = 24, 208          # колонка «властивість»
    x1, w1 = 244, 306         # колонка «Рішення»
    x2, w2 = 562, 316         # колонка «Аварія»

    # шапка
    yh, hh = 46, 46
    parts.append(fitbox(x0, yh, w0, hh, "Властивість\nборгу", size=13, bold=True,
                        fill=FILL, stroke=LINE))
    parts.append(fitbox(x1, yh, w1, hh, "Рішення\n(керований борг)", size=13, bold=True,
                        fill=GREEN_FILL, stroke=FIELD, color=FIELD))
    parts.append(fitbox(x2, yh, w2, hh, "Аварія\n(некерований борг)", size=13, bold=True,
                        fill=RED_FILL, stroke=POS, color=POS))

    rows = [
        ("Названо?",
         "записано в журнал —\nборг видно й можна зважити",
         "ніхто не записав —\nборг тихо стає ерозією"),
        ("Обмежено?",
         "увесь борг за одним швом —\nвідсоток в одному місці",
         "розмазано по коду —\nвідсоток капає скрізь"),
        ("Має строк?",
         "тригер погашення:\nнастане умова — гасимо",
         "строку немає —\n«тимчасове» живе роками"),
        ("Погашуваний?",
         "тести тримають поведінку —\nвідкотити дешево",
         "коду без тестів не чіпають —\nборг не віддати"),
    ]

    y = yh + hh + 6
    rh, gap = 66, 6
    for prop, dec, acc in rows:
        parts.append(fitbox(x0, y, w0, rh, prop, size=14, bold=True, fill=FILL, stroke=LINE))
        parts.append(fitbox(x1, y, w1, rh, dec, size=12, fill=GREEN_FILL, stroke=FIELD))
        parts.append(fitbox(x2, y, w2, rh, acc, size=12, fill=RED_FILL, stroke=POS))
        y += rh + gap

    render(os.path.join(IMG, 'gates.svg'), W, H, *parts,
           title="Що робить борг рішенням, а не аварією")


# ── Фігура B: обмежено проти розмазано ───────────────────────────────────────
def fig_seam():
    W, H = 900, 430
    parts = []

    # роздільник між панелями
    parts.append(line(450, 52, 450, 400, color=MUTED, sw=1, dash="4,4"))

    # ── ліва панель: аварія (розмазано) ──
    parts.append(text(230, 70, "Аварія: борг розмазано", size=15, color=POS, bold=True))
    cons_l = [("звіт", 50, 96), ("панель", 245, 96),
              ("експорт", 50, 182), ("лог", 245, 182)]
    bw, bh = 155, 66
    for label, bx, by in cons_l:
        parts.append(rect(bx, by, bw, bh, fill=FILL, stroke=LINE))
        parts.append(text(bx + bw / 2, by + bh / 2 - 4, label, size=13))
        # червона копія боргу всередині кожного виклику
        parts.append(circle(bx + bw - 20, by + bh - 18, 7, fill=POS, stroke=POS))
        parts.append(text(bx + bw / 2, by + bh / 2 + 15, "наївний підрахунок", size=9, color=MUTED))
    parts.append(fitbox(44, 274, 362, 62,
                        "підрахунок вписано в кожен виклик —\nпоказати ні на що, погасити нема як",
                        size=12, fill=RED_FILL, stroke=POS))

    # ── права панель: рішення (за швом) ──
    parts.append(text(676, 70, "Рішення: борг за швом", size=15, color=FIELD, bold=True))
    cons_r = [("звіт", 96), ("панель", 148), ("експорт", 200), ("лог", 252)]
    cw, ch = 96, 42
    cx = 478
    for label, cy in cons_r:
        parts.append(rect(cx, cy, cw, ch, fill=FILL, stroke=LINE))
        parts.append(text(cx + cw / 2, cy + ch / 2 + 4, label, size=12))

    # шов у центрі
    sx, sy, sw, sh = 648, 150, 190, 96
    parts.append(rect(sx, sy, sw, sh, fill=GREEN_FILL, stroke=FIELD, sw=2))
    parts.append(text(sx + sw / 2, sy + 32, "EnergyRollup (шов)", size=13, bold=True))
    parts.append(text(sx + sw / 2, sy + 58, "наївна реалізація", size=12, color=INK))
    parts.append(circle(sx + sw - 22, sy + sh - 20, 8, fill=POS, stroke=POS))
    parts.append(text(sx + sw / 2, sy + 80, "весь борг — тут", size=10, color=POS))

    # стрілки від кожного виклику до шва (у порожньому коридорі)
    for _, cy in cons_r:
        parts.append(arrow(cx + cw + 2, cy + ch / 2, sx - 4, sy + sh / 2, color=MUTED, sw=1.4))

    parts.append(fitbox(486, 274, 366, 62,
                        "весь борг — один клас за інтерфейсом;\nпогасити = підмінити одну реалізацію",
                        size=12, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'seam.svg'), W, H, *parts,
           title="Обмежено проти розмазано: шов збирає борг в одне місце")


# ── Фігура C: id зшиває маркер у коді із записом у журналі ────────────────────
def fig_debtgate():
    W, H = 940, 512
    parts = []

    # шапки колонок
    parts.append(text(200, 74, "Код: маркери DEBT(id)", size=15, bold=True))
    parts.append(text(740, 74, "Журнал боргу: записи", size=15, bold=True))

    lx, lw = 70, 260          # ліва колонка (маркери)
    rx, rw = 610, 260         # права колонка (записи)
    rows_y = [98, 196, 294]   # три рядки
    ch = 62

    left = [
        ("DEBT(DH-014)", FILL, LINE),
        ("DEBT(DH-022)", RED_FILL, POS),   # маркер-сирота
        ("DEBT(DH-007)", RED_FILL, POS),   # маркер на закритому
    ]
    right = [
        ("DH-014 · open",   FILL, LINE),
        ("DH-019 · open",   RED_FILL, POS),   # запис-сирота
        ("DH-007 · closed", FILL, LINE),
    ]
    for (lt, lf, ls), y in zip(left, rows_y):
        parts.append(fitbox(lx, y, lw, ch, lt, size=15, bold=True, fill=lf, stroke=ls))
    for (rt, rf, rs), y in zip(right, rows_y):
        parts.append(fitbox(rx, y, rw, ch, rt, size=15, bold=True, fill=rf, stroke=rs))

    # зʼєднання по id у центральному коридорі (lx+lw=330 .. rx=610)
    x_from, x_to = lx + lw, rx
    # рядок 1: збіг маркера й відкритого запису — зелена суцільна лінія
    parts.append(line(x_from, rows_y[0] + ch / 2, x_to, rows_y[0] + ch / 2, color=FIELD, sw=2.5))
    # рядок 2: обидва — сироти; два червоні обрубки, кожен у нікуди (✗)
    cy2 = rows_y[1] + ch / 2
    parts.append(line(x_from, cy2, 430, cy2, color=POS, sw=2.5))
    parts.append(text(446, cy2 + 6, "✗", size=20, color=POS, bold=True))
    parts.append(text(494, cy2 + 6, "✗", size=20, color=POS, bold=True))
    parts.append(line(510, cy2, x_to, cy2, color=POS, sw=2.5))
    # рядок 3: id збігається, та запис закритий — маркер протух; червона лінія
    parts.append(line(x_from, rows_y[2] + ch / 2, x_to, rows_y[2] + ch / 2, color=POS, sw=2.5))

    # легенда — кожен рядок у своїй рамці (текст не лягає на лінії)
    parts.append(fitbox(70, 372, 800, 44,
                        "рядок 1 — збіг маркера й відкритого запису: борг задокументовано, гейт мовчить",
                        size=13, fill=GREEN_FILL, stroke=FIELD))
    parts.append(fitbox(70, 424, 800, 64,
                        "три розходження валять CI:\n"
                        "маркер без запису · запис без маркера · маркер на закритому записі",
                        size=14, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, 'debtgate.svg'), W, H, *parts,
           title="id зшиває два світи: маркер у коді ↔ запис у журналі")


if __name__ == '__main__':
    fig_gates()
    fig_seam()
    fig_debtgate()
    print("ok")

# -*- coding: utf-8 -*-
"""Фігури до теми «membarrier: примусовий бар'єр пам'яті на всіх ядрах процесу»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

CODEFILL = "#eef2f7"
HOTFILL = "#fdecea"
COLDFILL = "#eaf0fd"
OKFILL = "#e8f6ee"


# ── 1. Симетричний бар'єр проти асиметричного ────────────────────────────────
def fig_asymmetry():
    W, H = 960, 470
    PW = 440
    body = ""

    def panel(px, header, hot_lines, cold_lines, summary, hotfill):
        s = rect(px, 20, PW, 420, fill="#ffffff", stroke=MUTED, sw=1.5, rx=10)
        cx = px + PW / 2
        s += text(cx, 52, header, size=16, bold=True)

        s += text(cx, 92, "гарячий шлях — 10 000 000 разів за секунду", size=13, color=MUTED)
        s += fitbox(px + 34, 104, PW - 68, 96, hot_lines, size=15, fill=hotfill, stroke=POS)

        s += text(cx, 240, "рідкісний шлях — 1 раз за секунду", size=13, color=MUTED)
        s += fitbox(px + 34, 252, PW - 68, 96, cold_lines, size=15, fill=CODEFILL, stroke=NEG)

        s += line(px + 40, 374, px + PW - 40, 374, color=MUTED, sw=1, dash="4,4")
        s += mtext(cx, 400, summary, size=14, bold=True)
        return s

    body += panel(
        20,
        "Симетрично — бар'єр з обох боків",
        ["active = 1;", "smp_mb();        ~20 нс", "p = table;"],
        ["table = new;", "smp_mb();        ~20 нс", "перевіряє active[]"],
        ["10⁷ × 20 нс ≈ 0.2 секунди", "накладних витрат щосекунди"],
        HOTFILL,
    )

    body += panel(
        500,
        "Асиметрично — вся ціна рідкому боку",
        ["active = 1;", "лише бар'єр компілятора", "p = table;"],
        ["table = new;", "membarrier();    ~40 мкс", "перевіряє active[]"],
        ["1 × 40 мкс ≈ 0.00004 секунди", "накладних витрат щосекунди"],
        OKFILL,
    )

    render(os.path.join(IMG, 'asymmetry.svg'), W, H, body,
           title="Симетричний бар'єр проти асиметричного")


# ── 2. Кому ядро шле IPI ─────────────────────────────────────────────────────
def fig_targets():
    W, H = 960, 440
    CW, GAP = 210, 18
    X0 = 25
    xs = [X0 + i * (CW + GAP) for i in range(4)]
    cxs = [x + CW / 2 for x in xs]
    body = ""

    heads = ["ядро 0", "ядро 1", "ядро 2", "ядро 3"]
    runs = [
        ("потік A\nнашого процесу", HOTFILL, POS),
        ("потік B\nнашого процесу", HOTFILL, POS),
        ("потік\nчужого процесу", COLDFILL, NEG),
        ("нічого\n(idle)", "#f4f6f8", MUTED),
    ]
    verdict = [
        ("він і викликав", OKFILL, FIELD),
        ("шлемо IPI", OKFILL, FIELD),
        ("IPI не треба", CODEFILL, MUTED),
        ("IPI не треба", CODEFILL, MUTED),
    ]
    why = [
        ["smp_mb() виконується", "прямо в тілі виклику", "перед розсиланням"],
        ["ipi_mb() негайно", "робить smp_mb()", "на цьому ядрі"],
        ["щоб торкнутись нашої", "пам'яті, воно спершу", "перемкнеться в наш mm —", "а перемикання вже бар'єр"],
        ["ядро не виконує коду,", "тож і переставляти", "нічого"],
    ]

    for i in range(4):
        body += fitbox(xs[i], 26, CW, 34, heads[i], size=15, bold=True,
                       fill="#ffffff", stroke=MUTED)
        lines, fill, stroke = runs[i]
        body += fitbox(xs[i], 76, CW, 62, lines, size=14, fill=fill, stroke=stroke)

    body += fitbox(X0, 168, xs[3] + CW - X0, 50,
                   "ядро системи перебирає онлайн-CPU: rq->curr->mm == наш mm?",
                   size=15, fill="#ffffff", stroke=INK)

    for i in range(4):
        body += arrow(cxs[i], 220, cxs[i], 250)
        lines, fill, stroke = verdict[i]
        body += fitbox(xs[i], 252, CW, 40, lines, size=14, bold=True, fill=fill, stroke=stroke)
        body += arrow(cxs[i], 294, cxs[i], 322)
        body += fitbox(xs[i], 324, CW, 90, why[i], size=12, fill="#ffffff", stroke=MUTED)

    render(os.path.join(IMG, 'who-gets-ipi.svg'), W, H, body,
           title="Кому ядро розсилає IPI при membarrier")


# ── 3. Вікно гарантії ────────────────────────────────────────────────────────
def fig_window():
    W, H = 960, 410
    L0, L1 = 120, 262
    XA, XB = 340, 580
    body = ""

    body += fitbox(XA, 40, XB - XA, 32, "вікно гарантії", size=14, bold=True,
                   fill=OKFILL, stroke=FIELD)
    body += line(XA, 74, XA, L0 - 22, color=FIELD, sw=1.2, dash="4,4")
    body += line(XB, 74, XB, L0 - 22, color=FIELD, sw=1.2, dash="4,4")

    body += text(24, L0 + 5, "ядро 0 — викликач", size=13, color=MUTED, anchor="start")
    body += text(24, L1 + 5, "ядро 1 — потік-побратим", size=13, color=MUTED, anchor="start")

    body += arrow(180, L0, 910, L0, color=INK, sw=1.6)
    body += arrow(180, L1, 910, L1, color=INK, sw=1.6)

    def tick(x, y, color=INK):
        return line(x, y - 20, x, y + 20, color=color, sw=2.4)

    # ядро 0
    body += tick(XA, L0, FIELD)
    body += tick(XB, L0, FIELD)
    body += text(250, L0 - 34, "запис X", size=13)
    body += text(XA, L0 + 44, "smp_mb() на вході", size=13, color=FIELD)
    body += text(XB, L0 + 44, "smp_mb() на виході", size=13, color=FIELD)
    body += text(720, L0 - 34, "читання Y", size=13)

    # ядро 1
    body += tick(460, L1, POS)
    body += text(340, L1 - 34, "запис Y", size=13)
    body += text(460, L1 + 44, "ipi_mb(): smp_mb()", size=13, color=POS)
    body += text(650, L1 - 34, "читання X", size=13)

    body += mtext(480, 344, [
        "усе, що ядро 0 записало ДО виклику, ядро 1 побачить ПІСЛЯ своєї точки",
        "усе, що ядро 1 записало ДО своєї точки, ядро 0 побачить ПІСЛЯ повернення",
    ], size=13, lh=1.5)

    render(os.path.join(IMG, 'guarantee-window.svg'), W, H, body,
           title="Вікно гарантії membarrier")


# ── 4. Слово стану читача очима письменника (вставка proj-asymmetric-rcu) ────
def fig_reader_word():
    W, H = 960, 470
    body = ""

    BX, BY, BW, BH = 140, 66, 680, 54
    SPLIT = BX + 500
    body += rect(BX, BY, SPLIT - BX, BH, fill=COLDFILL, stroke=NEG, sw=1.6)
    body += rect(SPLIT, BY, BX + BW - SPLIT, BH, fill=HOTFILL, stroke=POS, sw=1.6)
    body += text(BX + (SPLIT - BX) / 2, BY + 34, "покоління — знімок gp", size=15, bold=True)
    body += text(SPLIT + (BX + BW - SPLIT) / 2, BY + 34, "глибина, 7 біт", size=15, bold=True)
    body += text(BX, BY - 14, "біт 63", size=12, color=MUTED)
    body += text(BX + BW, BY - 14, "біт 0", size=12, color=MUTED)

    body += text(W / 2, 152, "письменник підняв gp з 7 до 8 і зробив обидва виклики membarrier",
                 size=14, color=MUTED)

    cards = [
        ("ctr = 7 | 0",
         ["глибина нульова —", "читач зараз не в секції"],
         "можна звільняти", OKFILL, "#1f8a4c"),
        ("ctr = 8 | 1",
         ["покоління свіже: зайшов", "після виклику, отже", "читає вже нову таблицю"],
         "можна звільняти", OKFILL, "#1f8a4c"),
        ("ctr = 7 | 2",
         ["старе покоління,", "дві вкладені секції —", "тримає стару таблицю"],
         "чекаємо далі", HOTFILL, POS),
    ]
    CW, GAP = 296, 14
    X0 = (W - 3 * CW - 2 * GAP) / 2
    for i, (val, why, verdict, fill, col) in enumerate(cards):
        x = X0 + i * (CW + GAP)
        body += rect(x, 186, CW, 240, fill="#ffffff", stroke=MUTED, sw=1.5, rx=10)
        body += text(x + CW / 2, 222, val, size=17, bold=True)
        body += mtext(x + CW / 2, 268, why, size=13, lh=1.5, color=MUTED)
        frag, _w, _h = textbox(x + CW / 2, 388, verdict, size=15, bold=True,
                               fill=fill, stroke=col, color=col)
        body += frag

    render(os.path.join(IMG, 'reader-word.svg'), W, H, body,
           title="Слово стану читача очима письменника")


if __name__ == '__main__':
    fig_asymmetry()
    fig_targets()
    fig_window()
    fig_reader_word()
    print("ok")

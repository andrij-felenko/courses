# -*- coding: utf-8 -*-
"""Фігури до теми «Контролер пам'яті».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
PURPLE = "#6a3fb5"   # контролер / команди
AMBER  = "#b9770e"   # precharge / закриття ряду


# ── 1. Контролер як перекладач: проста мова ↔ протокол DRAM ──────────────────
def fig_controller_role():
    W, H = 800, 360
    f = [text(W / 2, 26, "Контролер — перекладач між «дай слово» і протоколом DRAM", size=14, bold=True)]

    # Ядро
    f.append(rect(46, 150, 150, 96, fill="#eef2fb", stroke=NEG, sw=2))
    f.append(text(121, 182, "ядро / шина", size=12.5, color=NEG, bold=True))
    f.append(text(121, 206, "проста мова:", size=10.5, color=MUTED))
    f.append(text(121, 224, "«дай слово", size=10.5, color=NEG))
    f.append(text(121, 238, "за адресою A»", size=10.5, color=NEG))

    # Контролер (центр)
    f.append(rect(296, 96, 250, 200, fill="#f1ecfa", stroke=PURPLE, sw=2.4))
    f.append(text(421, 120, "контролер пам'яті", size=13, color=PURPLE, bold=True))
    f.append(line(312, 132, 530, 132, color=PURPLE, sw=1.2))
    duties = [
        "розкласти адресу: банк / ряд / стовпець",
        "мультиплексувати: RAS-ряд, тоді CAS-стовпець",
        "видати ACT → RD/WR із паузами",
        "витримати таймінги (tRCD, CL, tRP)",
        "слати REFRESH усім рядам",
        "провести ініціалізацію при старті",
    ]
    yy = 152
    for d in duties:
        f.append(text(314, yy, "• " + d, size=9.6, anchor="start"))
        yy += 23

    # DRAM-чіп
    f.append(rect(646, 150, 150, 96, fill="#fdeef0", stroke=POS, sw=2))
    f.append(text(721, 182, "DRAM-чіп", size=12.5, color=POS, bold=True))
    f.append(text(721, 206, "складна мова:", size=10.5, color=MUTED))
    f.append(text(721, 224, "команди +", size=10.5, color=POS))
    f.append(text(721, 238, "жорсткі таймінги", size=10.5, color=POS))

    # Стрілки ядро ↔ контролер
    f.append(arrow(196, 184, 294, 184, color=NEG, sw=2))
    f.append(text(245, 175, "запит", size=10, color=NEG, bold=True))
    f.append(arrow(294, 216, 196, 216, color=FIELD, sw=2))
    f.append(text(245, 232, "дані", size=10, color=FIELD, bold=True))
    # Стрілки контролер ↔ чіп
    f.append(arrow(548, 184, 644, 184, color=PURPLE, sw=2))
    f.append(text(596, 175, "команди", size=10, color=PURPLE, bold=True))
    f.append(arrow(644, 216, 548, 216, color=POS, sw=2))
    f.append(text(596, 232, "слова", size=10, color=POS, bold=True))

    f.append(text(W / 2, 332,
                  "Між ядром і чіпом мусить стояти контролер, що знає весь протокол, — тому DDR не чіпляють до простих ніжок GPIO.",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "controller-role.svg"), W, H, *f)


# ── 2. Таймінги одного читання: чому між командами потрібні паузи ─────────────
def fig_read_timing():
    W, H = 760, 360
    f = [text(W / 2, 26, "Одне читання: між командами обов'язкові паузи", size=14, bold=True)]

    x0, step = 110, 64
    n = 9
    # такти CLK (меандр)
    pts = []
    for i in range(n):
        x = x0 + i * step
        pts += [(x, 132), (x, 108), (x + step / 2, 108), (x + step / 2, 132)]
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (poly, INK))
    f.append(text(x0 - 24, 124, "CLK", size=10.5, color=INK, anchor="end", bold=True))
    for i in range(n):
        f.append(text(x0 + i * step, 148, "T%d" % i, size=9, color=MUTED))

    def cmd_box(ti, label, col):
        cx = x0 + ti * step
        f.append(rect(cx - 28, 168, 56, 30, fill=BG, stroke=col, sw=1.6))
        f.append(text(cx, 188, label, size=11, color=col, bold=True))

    f.append(text(x0 - 24, 188, "CMD", size=10.5, color=INK, anchor="end", bold=True))
    cmd_box(0, "ACT", PURPLE)
    cmd_box(3, "RD", PURPLE)
    cmd_box(8, "PRE", AMBER)

    def dq_box(ti, label):
        cx = x0 + ti * step
        f.append(rect(cx - 28, 224, 56, 28, fill="#eef6ef", stroke=FIELD, sw=1.4))
        f.append(text(cx, 243, label, size=10.5, color=FIELD, bold=True))

    f.append(text(x0 - 24, 242, "DQ", size=10.5, color=INK, anchor="end", bold=True))
    for k, ti in enumerate((5, 6, 7, 8)):
        dq_box(ti, "D%d" % k)

    def span(ya, ti0, ti1, label, col):
        xa = x0 + ti0 * step
        xb = x0 + ti1 * step
        f.append(line(xa, ya, xb, ya, color=col, sw=1.5))
        f.append(line(xa, ya - 5, xa, ya + 5, color=col, sw=1.5))
        f.append(line(xb, ya - 5, xb, ya + 5, color=col, sw=1.5))
        f.append(text((xa + xb) / 2, ya - 7, label, size=10, color=col, bold=True))

    span(86, 0, 3, "tRCD — ряд готовий", PURPLE)
    span(280, 3, 5, "CL — затримка даних", FIELD)
    span(86, 8, 8, "", AMBER)
    f.append(text(x0 + 8 * step, 79, "PRE + tRP:", size=9.5, color=AMBER, anchor="middle", bold=True))
    f.append(text(x0 + 8 * step, 92, "закрити ряд", size=9, color=AMBER, anchor="middle"))

    f.append(text(W / 2, 318,
                  "Кожен інтервал — фізика чіпа: час, поки буфер-підсилювач розгойдає крихітний заряд комірки.",
                  size=10, color=MUTED, italic=True))
    f.append(text(W / 2, 338,
                  "Відлічиш замало — прочитаєш сміття; тому числа таймінгів (як «CL22» на модулі) контролер знає наперед.",
                  size=10, color=FIELD, italic=True))
    render(os.path.join(IMG, "read-timing.svg"), W, H, *f)


# ── 3. Ініціалізація: розбудити чіп, далі вічна регенерація ───────────────────
def fig_init_sequence():
    W, H = 820, 330
    f = [text(W / 2, 26, "Ініціалізація: розбудити чіп, потім вічно регенерувати", size=14, bold=True)]

    steps = [
        ("живлення +\nстабільний CLK", NEG),
        ("витримати\nпаузу ~100 мкс", MUTED),
        ("PRECHARGE\nусіх банків", AMBER),
        ("кілька циклів\nREFRESH", FIELD),
        ("Mode Register\n(CL, burst)", PURPLE),
        ("ГОТОВО:\nчитати й писати", FIELD),
    ]
    bw, bh, gap = 122, 70, 13
    x = 20
    y = 78
    centers = []
    for i, (label, col) in enumerate(steps):
        fill = "#eef6ef" if i == len(steps) - 1 else BG
        f.append(fitbox(x, y, bw, bh, label, size=11, color=col, bold=True, fill=fill, stroke=col, sw=2))
        centers.append((x + bw / 2, y + bh))
        if i < len(steps) - 1:
            f.append(arrow(x + bw, y + bh / 2, x + bw + gap, y + bh / 2, color=INK, sw=1.8))
        x += bw + gap

    # фонова регенерація
    by = 210
    f.append(rect(22, by, W - 44, 64, fill="#f4fbf5", stroke=FIELD, sw=2, rx=10))
    f.append('<rect x="22" y="%.0f" width="%.0f" height="64" rx="10" fill="none" '
             'stroke="%s" stroke-width="2" stroke-dasharray="6,4"/>' % (by, W - 44, FIELD))
    f.append(text(W / 2, by + 26, "…і паралельно, поки чіп живий — контролер сам шле REFRESH кожному ряду кожні ~64 мс",
                  size=11, color=FIELD, bold=True))
    f.append(text(W / 2, by + 48, "Ваш код цього не бачить: для нього зовнішня DRAM — просто ще один діапазон адрес.",
                  size=10, color=INK))
    # з'єднання «готово» → фонова регенерація
    cx, cyb = centers[-1]
    f.append(arrow(cx, cyb, cx, by, color=FIELD, sw=1.6))
    render(os.path.join(IMG, "init-sequence.svg"), W, H, *f)


if __name__ == "__main__":
    fig_controller_role()
    fig_read_timing()
    fig_init_sequence()
    print("OK: 3 figures ->", IMG)

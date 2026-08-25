# -*- coding: utf-8 -*-
# Фігура для вставки proj-gcc-bootstrap.md (окремий файл, щоб не колідувати з figs.py).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_gcc_three_stage():
    """Потік GCC: host → stage1 → stage2 → stage3; звіряють stage2 і stage3."""
    W, H = 780, 500
    parts = []
    bx = 60           # ліва межа коробок
    bw, bh = 300, 62  # розмір коробки
    ys = [30, 132, 234, 336]  # верхи чотирьох коробок

    boxes = [
        ("Host-компілятор (stage 0)", "наявний gcc / clang — «чужий»", "#f4f6f8", LINE, MUTED),
        ("stage 1", "зібраний host-ом — чужого впливу", "#fdecea", POS, INK),
        ("stage 2", "зібраний stage 1 — «народив себе»", "#eaf0fd", NEG, INK),
        ("stage 3", "зібраний stage 2 — для звірки", "#eafaf0", FIELD, INK),
    ]
    for i, (title, sub, fill, stroke, tc) in enumerate(boxes):
        y = ys[i]
        parts.append(rect(bx, y, bw, bh, fill=fill, stroke=stroke, sw=1.9))
        parts.append(text(bx + bw / 2, y + 26, title, size=15, bold=True, color=tc))
        parts.append(text(bx + bw / 2, y + 47, sub, size=11.5, color=MUTED))

    # Вертикальні стрілки «збирає» між сусідніми коробками
    for i in range(3):
        y1 = ys[i] + bh
        y2 = ys[i + 1]
        parts.append(arrow(bx + bw / 2, y1 + 2, bx + bw / 2, y2 - 2, color=INK, sw=2.2))
        parts.append(text(bx + bw / 2 + 54, (y1 + y2) / 2 + 4, "збирає",
                          size=11.5, color=MUTED, italic=True, anchor="start"))

    # Фігурна дужка праворуч, що обіймає stage2 і stage3
    ytop = ys[2]
    ybot = ys[3] + bh
    xbr = bx + bw + 20
    ymid = (ytop + ybot) / 2
    brace = ('<path d="M%d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d" '
             'fill="none" stroke="%s" stroke-width="2.4"/>'
             % (xbr, ytop,
                xbr + 14, ytop, xbr + 14, ymid - 6, xbr + 22, ymid,
                xbr + 14, ymid + 6, xbr + 14, ybot, xbr, ybot,
                FIELD))
    parts.append(brace)

    # Підпис звірки праворуч від дужки
    cb, cbw, cbh = textbox(xbr + 118, ymid,
                           ["ЗВІРКА байт-у-байт", "stage 2 .o == stage 3 .o ?",
                            "різні → БАГ у stage 2"],
                           size=11.5, fill="#eafaf0", stroke=FIELD)
    parts.append(cb)

    # Нижній акцент: чому саме ці дві
    nb, nbw, nbh = textbox(W / 2, ybot + 52,
                           ["stage 1 і stage 2 — різні збирачі, тож МУСЯТЬ різнитися.",
                            "stage 2 і stage 3 — один збирач, одне джерело → мусять збігтися."],
                           size=12, fill="#f4f6f8", stroke=LINE)
    parts.append(nb)

    render(os.path.join(OUT, 'gcc-three-stage.svg'), W, H, *parts,
           title="Триетапна збірка GCC: host, stage1, stage2, stage3; звірка 2 і 3")


if __name__ == '__main__':
    fig_gcc_three_stage()
    print("figure written to", OUT)

# -*- coding: utf-8 -*-
"""Фігури до теми «Обмін значеннями: swap, ADL-пошук і зобов'язання не кидати»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Обмін переставляє представлення, а не значення ───────────────────────
def fig_representation():
    W, H = 1000, 430
    f = []

    f.append(fitbox(120, 70, 260, 70, "об'єкт vec a\nbegin · end · capacity", size=13))
    f.append(fitbox(620, 70, 260, 70, "об'єкт vec b\nbegin · end · capacity", size=13))

    f.append(fitbox(410, 76, 180, 58, "штрихове — до\nсуцільне — після",
                    size=11, fill=BG, stroke=MUTED, color=MUTED))

    f.append(fitbox(120, 280, 260, 80, "блок у купі\n1 000 000 чисел",
                    size=13, fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(620, 280, 260, 80, "блок у купі\n1 000 000 чисел",
                    size=13, fill="#eaf0fd", stroke=NEG))

    f.append(line(180, 142, 180, 278, color=MUTED, sw=1.2, dash="5 4"))
    f.append(line(820, 142, 820, 278, color=MUTED, sw=1.2, dash="5 4"))

    f.append(arrow(300, 142, 700, 278, color=POS))
    f.append(arrow(700, 142, 300, 278, color=NEG))

    f.append(text(500, 400,
                  "переставлено три машинні слова — жодного числа не скопійовано "
                  "й жодної пам'яті не виділено", size=13))

    return render(os.path.join(OUT, 'swap-representation.svg'), W, H, *f)


# ── 2. Двокроковий пошук: один набір кандидатів із двох джерел ──────────────
def fig_lookup():
    W, H = 1040, 500
    f = []

    f.append(fitbox(60, 50, 340, 66, "using std::swap;\nзвичайний пошук імені", size=13))
    f.append(fitbox(640, 50, 340, 66, "swap(a, b) без кваліфікації\nADL за простором імен Point", size=13))

    f.append(arrow(230, 118, 230, 156))
    f.append(arrow(810, 118, 810, 156))

    f.append(fitbox(60, 160, 340, 66, "std::swap<Point>\nшаблон, три переміщення", size=13))
    f.append(fitbox(640, 160, 340, 66, "geo::swap(Point&, Point&)\nнешаблонна, точний збіг",
                    size=13, fill="#eaf7ee", stroke=FIELD))

    f.append(arrow(230, 228, 430, 276))
    f.append(arrow(810, 228, 610, 276))

    f.append(fitbox(340, 280, 360, 56, "спільний набір кандидатів", size=13))

    f.append(arrow(520, 338, 520, 372))

    f.append(fitbox(280, 376, 480, 66,
                    "за рівних перетворень нешаблонна перемагає\n→ викликано geo::swap",
                    size=13, fill="#eaf7ee", stroke=FIELD, bold=True))

    f.append(text(520, 474,
                  "кваліфікований std::swap(a, b) відсікає правий стовпчик — кандидат лишається один",
                  size=12, color=MUTED))

    return render(os.path.join(OUT, 'swap-lookup.svg'), W, H, *f)


# ── 3. Куди дивиться посилання після обміну ────────────────────────────────
def fig_references():
    W, H = 1040, 390
    f = []

    f.append(line(520, 30, 520, 372, color=MUTED, sw=1.2, dash="6 5"))

    # ── ліворуч: вектор ──
    f.append(text(260, 40, "std::vector — переставляють вказівники", size=14, bold=True))

    f.append(fitbox(60, 70, 170, 48, "vec a", size=13))
    f.append(fitbox(310, 70, 170, 48, "vec b", size=13))

    for i, v in enumerate(("7", "8", "9")):
        f.append(fitbox(60 + i * 56, 230, 56, 44, v, size=15, fill="#eaf0fd", stroke=NEG))
    for i, v in enumerate(("1", "2", "3")):
        f.append(fitbox(310 + i * 56, 230, 56, 44, v, size=15, fill="#eaf0fd", stroke=NEG))

    f.append(arrow(145, 120, 394, 228, color=POS))
    f.append(arrow(394, 120, 145, 228, color=NEG))

    f.append(circle(88, 194, 13, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(88, 199, "r", size=13, color=POS, bold=True))
    f.append(arrow(88, 208, 88, 226, color=POS))

    f.append(mtext(260, 306, ["r лишилася на тому самому числі —",
                              "тепер це елемент b",
                              "O(1): переставлено вказівники"], size=12))

    # ── праворуч: масив ──
    f.append(text(780, 40, "std::array — переставляють самі числа", size=14, bold=True))

    for i, v in enumerate(("7", "8", "9")):
        f.append(fitbox(600 + i * 56, 70, 56, 44, v, size=15, fill="#eaf0fd", stroke=NEG))
    for i, v in enumerate(("1", "2", "3")):
        f.append(fitbox(600 + i * 56, 200, 56, 44, v, size=15, fill="#eaf0fd", stroke=NEG))

    f.append(text(790, 98, "arr a", size=13, anchor="start"))
    f.append(text(790, 228, "arr b", size=13, anchor="start"))

    for i in range(3):
        f.append(arrow(628 + i * 56, 120, 628 + i * 56, 196, color=MUTED))
    f.append(text(790, 162, "n обмінів", size=12, color=MUTED, anchor="start"))

    f.append(circle(572, 92, 13, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(572, 97, "r", size=13, color=POS, bold=True))
    f.append(arrow(586, 92, 598, 92, color=POS))

    f.append(mtext(780, 306, ["r лишилася в a[0] —",
                              "але число в ній уже з b",
                              "O(n): переставлено n значень"], size=12))

    return render(os.path.join(OUT, 'swap-references.svg'), W, H, *f)


if __name__ == '__main__':
    for fn in (fig_representation, fig_lookup, fig_references):
        print(fn())

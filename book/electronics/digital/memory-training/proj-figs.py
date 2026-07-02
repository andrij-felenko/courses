# -*- coding: utf-8 -*-
"""Фігури до ВСТАВКИ «Ядро тренування як пошук» (proj-training-search).
Окремо від figs.py теми, щоб не плутати вивід. Пише SVG у ./img/.
Помічники — зі спільного svgkit (НЕ переписувати)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GOOD = "#eafaf1"   # заливка P
BAD  = "#fdecea"   # заливка F
HOLE = "#fff3cd"   # заливка одиничного F-провалу (шум)


def _cellrow(frags, x0, y, cell, res, marks=None):
    """Малює рядок P/F за рядком res; marks — dict {i: (fill,stroke,txtcolor)}."""
    for i, c in enumerate(res):
        x = x0 + i * cell
        if marks and i in marks:
            fill, stroke, tc = marks[i]
        elif c == 'P':
            fill, stroke, tc = GOOD, FIELD, FIELD
        else:
            fill, stroke, tc = BAD, "#e8b4ae", POS
        frags.append(rect(x, y, cell - 4, cell - 4, fill=fill, stroke=stroke, sw=1.4, rx=4))
        frags.append(text(x + (cell - 4) / 2, y + cell * 0.60, c, size=13, color=tc, bold=True))
        frags.append(text(x + (cell - 4) / 2, y - 7, str(i), size=9, color=MUTED))


def bracket(frags, xl, xr, y, color, label, up=True):
    off = -20 if up else 20
    tip = -6 if up else 6
    ty = y + (off - 8 if up else off + 14)
    frags.append(line(xl, y + off, xr, y + off, color=color, sw=1.8))
    frags.append(line(xl, y + off, xl, y + off - tip, color=color, sw=1.8))
    frags.append(line(xr, y + off, xr, y + off - tip, color=color, sw=1.8))
    frags.append(text((xl + xr) / 2, ty, label, size=10.5, color=color, bold=up))


# ── Три пастки карти P/F: край, два вікна, шумовий провал ─────────────────────
def fig_map():
    W, H = 900, 470
    frags = []
    cell = 40
    x0 = 70

    # --- рядок A: вікно впирається у ЛІВИЙ край діапазону ---
    yA = 95
    resA = "PPPPPFFFFFFFFFFF"
    _cellrow(frags, x0, yA, cell, resA)
    xl = x0
    xr = x0 + 4 * cell + (cell - 4)
    bracket(frags, xl, xr, yA, FIELD, "вікно впирається у край: істинний центр за межею", up=True)
    # обраний центр — затиснутий у край
    cAmid = 2
    xc = x0 + cAmid * cell + (cell - 4) / 2
    frags.append(arrow(xc, yA + cell + 2, xc, yA + cell + 26, color=NEG, sw=2.2))
    frags.append(text(xc, yA + cell + 40, "центр видимого вікна (край недо­бачено)", size=10, color=NEG))
    frags.append(text(x0 - 12, yA + cell * 0.60, "A", size=13, anchor="end", color=INK, bold=True))

    # --- рядок B: ДВА окремі вікна — беремо ширше ---
    yB = 225
    resB = "FFPPPFFFPPPPPPPFF"
    _cellrow(frags, x0, yB, cell, resB)
    # вузьке вікно 2..4
    bracket(frags, x0 + 2 * cell, x0 + 4 * cell + (cell - 4), yB, MUTED, "вузьке (3)", up=True)
    # широке вікно 8..14
    bracket(frags, x0 + 8 * cell, x0 + 14 * cell + (cell - 4), yB, FIELD, "широке (7) — беремо його", up=True)
    cBmid = 11
    xc = x0 + cBmid * cell + (cell - 4) / 2
    frags.append(arrow(xc, yB + cell + 2, xc, yB + cell + 26, color=NEG, sw=2.2))
    frags.append(text(xc, yB + cell + 40, "центр найширшого", size=10, color=NEG, bold=True))
    frags.append(text(x0 - 12, yB + cell * 0.60, "B", size=13, anchor="end", color=INK, bold=True))

    # --- рядок C: шумовий провал — одиничний F усередині вікна ---
    yC = 355
    resC = "FFPPPPPFPPPPPPFFF"
    _cellrow(frags, x0, yC, cell, resC,
             marks={7: (HOLE, "#caa300", "#8a6d00")})
    # наївно: два вузькі вікна 2..6 і 8..13; після згладжування — одне 2..13
    bracket(frags, x0 + 2 * cell, x0 + 13 * cell + (cell - 4), yC, FIELD,
            "справжнє вікно (12) — якщо не спіткнутись об шумовий F", up=True)
    frags.append(arrow(x0 + 7 * cell + (cell - 4) / 2, yC - 2,
                       x0 + 7 * cell + (cell - 4) / 2, yC - 2, color="#caa300", sw=0))
    frags.append(text(x0 + 7 * cell + (cell - 4) / 2, yC + cell + 16,
                     "одиничний F: шум на межі,", size=9.5, color="#8a6d00"))
    frags.append(text(x0 + 7 * cell + (cell - 4) / 2, yC + cell + 30,
                     "а не справжній край", size=9.5, color="#8a6d00"))
    frags.append(text(x0 - 12, yC + cell * 0.60, "C", size=13, anchor="end", color=INK, bold=True))

    render(os.path.join(IMG, "pf-map-cases.svg"), W, H, *frags,
           title="Три пастки карти P/F, які мусить пережити код пошуку")


if __name__ == "__main__":
    fig_map()
    print("OK: 1 SVG у", IMG)

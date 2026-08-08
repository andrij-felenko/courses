# -*- coding: utf-8 -*-
"""Фігури до теми «Ізотопи» (book/chemistry/radiochemistry/isotopes)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)

PROTON_FILL = "#fbe3e0"
NEUTRON_FILL = "#e7e9ec"
ELECTRON_FILL = "#dfe7fb"


def nucleon(cx, cy, kind, r=19):
    """Протон («+», червоний) або нейтрон («n», сірий)."""
    if kind == 'p':
        return (circle(cx, cy, r, fill=PROTON_FILL, stroke=POS, sw=2) +
                text(cx, cy + 7, "+", size=20, bold=True, color=POS))
    return (circle(cx, cy, r, fill=NEUTRON_FILL, stroke=MUTED, sw=2) +
            text(cx, cy + 6, "n", size=16, bold=True, color=MUTED))


# ── Фігура 1: три ізотопи Гідрогену ─────────────────────────────────────────
def fig_hydrogen_isotopes():
    W, H = 1000, 430
    frags = [text(500, 36, "Один і той самий Гідроген — три різні ядра",
                  size=19, bold=True)]

    panels = [
        (60, "протій", ['p'], "1 протон, 0 нейтронів", "майже весь Гідроген світу"),
        (365, "дейтерій", ['p', 'n'], "1 протон, 1 нейтрон", "≈ 1 атом на 6000"),
        (670, "тритій", ['p', 'n', 'n'], "1 протон, 2 нейтрони", "ядро довго не тримається"),
    ]

    for px, name, parts, comp, note in panels:
        cx = px + 135
        frags.append(rect(px, 62, 270, 300, fill=BG))

        # електрон — його всюди рівно один, бо протон один
        frags.append(circle(cx - 62, 96, 9, fill=ELECTRON_FILL, stroke=NEG, sw=2))
        frags.append(text(cx + 14, 101, "1 електрон", size=14, color=NEG))

        # ядро
        frags.append(circle(cx, 190, 56, fill=FILL, stroke=LINE, sw=1.5))
        if len(parts) == 1:
            spots = [(cx, 190)]
        elif len(parts) == 2:
            spots = [(cx - 21, 190), (cx + 21, 190)]
        else:
            spots = [(cx - 21, 175), (cx + 21, 175), (cx, 213)]
        for (sx, sy), kind in zip(spots, parts):
            frags.append(nucleon(sx, sy, kind))

        frags.append(text(cx, 288, name, size=21, bold=True))
        frags.append(text(cx, 318, comp, size=15))
        frags.append(text(cx, 346, note, size=13, color=MUTED))

    frags.append(text(500, 400,
                      "Протон усюди один — отже, всюди Гідроген; нейтрони лише додають ваги",
                      size=15, color=MUTED))

    render(os.path.join(IMG, 'hydrogen-isotopes.svg'), W, H, *frags)


# ── Фігура 2: природний Хлор — суміш, і звідки в таблиці 35.45 ──────────────
def fig_chlorine_mix():
    W, H = 960, 430
    frags = [text(480, 36, "Природний Хлор: із кожної сотні атомів",
                  size=19, bold=True)]

    x0, y0, bw, bh = 70, 66, 800, 96
    wl = int(bw * 0.76)

    frags.append(rect(x0, y0, wl, bh, fill=PROTON_FILL, stroke=POS, sw=2))
    frags.append(rect(x0 + wl, y0, bw - wl, bh, fill=ELECTRON_FILL, stroke=NEG, sw=2))

    cl, cr = x0 + wl / 2, x0 + wl + (bw - wl) / 2
    frags.append(text(cl, y0 + 42, "Хлор-35", size=22, bold=True, color=POS))
    frags.append(text(cl, y0 + 74, "76 атомів зі ста", size=16))
    frags.append(text(cr, y0 + 42, "Хлор-37", size=20, bold=True, color=NEG))
    frags.append(text(cr, y0 + 74, "24 зі ста", size=16))

    frags.append(text(cl, 196, "17 протонів і 18 нейтронів", size=14, color=MUTED))
    frags.append(text(cr, 196, "17 протонів і 20 нейтронів", size=13, color=MUTED))

    frags.append(arrow(480, 224, 480, 268))

    box, _, _ = textbox(480, 306, "середнє по суміші — 35.45",
                        size=19, pad=14, fill=FILL)
    frags.append(box)

    frags.append(text(480, 372,
                      "саме це число стоїть у клітинці таблиці;",
                      size=15, color=MUTED))
    frags.append(text(480, 398,
                      "жоден окремий атом стільки не важить",
                      size=15, color=MUTED))

    render(os.path.join(IMG, 'chlorine-mix.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_hydrogen_isotopes()
    fig_chlorine_mix()
    print("ok")

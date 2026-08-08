# -*- coding: utf-8 -*-
"""Фігури до теми «Ізомери» (book/chemistry/organic-chemistry/isomers)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── спільні дрібнички ───────────────────────────────────────────────────────
def bond(x1, y1, r1, x2, y2, r2, sw=2.0, color=LINE):
    """Зв'язок між двома кружками: лінія обривається на їхніх межах,
    тож ніколи не перетинає літеру всередині кружка."""
    d = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    return line(x1 + ux * (r1 + 1.5), y1 + uy * (r1 + 1.5),
                x2 - ux * (r2 + 1.5), y2 - uy * (r2 + 1.5), color=color, sw=sw)


def atom(cx, cy, label, r=26, color=INK, size=20):
    return (circle(cx, cy, r, fill="#ffffff", stroke=color, sw=2) +
            text(cx, cy + size * 0.35, label, size=size, bold=True, color=color))


def hyd(cx, cy, r=14):
    return atom(cx, cy, "H", r=r, color=MUTED, size=13)


# ── Фігура 1: одна формула — дві речовини ───────────────────────────────────
def fig_two_ways():
    W, H = 1000, 570
    R, RH = 26, 14
    frags = [text(500, 36, "Ті самі атоми: 2 Карбони, 6 Гідрогенів, 1 Оксиген — C₂H₆O",
                  size=18, bold=True)]

    def molecule(heavy, hydrogens):
        """heavy: [(x, y, знак, колір)], hydrogens: [(x, y, індекс важкого атома)]"""
        out = []
        for i in range(len(heavy) - 1):          # зв'язки спершу — вони під кружками
            x1, y1, _, _ = heavy[i]
            x2, y2, _, _ = heavy[i + 1]
            out.append(bond(x1, y1, R, x2, y2, R))
        for hx, hy, k in hydrogens:
            x1, y1, _, _ = heavy[k]
            out.append(bond(x1, y1, R, hx, hy, RH, sw=1.6, color=MUTED))
        for hx, hy, _ in hydrogens:
            out.append(hyd(hx, hy, RH))
        for x, y, lab, col in heavy:
            out.append(atom(x, y, lab, r=R, color=col, size=20))
        return out

    # ── ліворуч: етанол, ланцюг C–C–O ───────────────────────────────────────
    frags.append(rect(60, 62, 400, 320, fill="#ffffff"))
    frags += molecule(
        [(160, 215, "C", INK), (265, 215, "C", INK), (370, 215, "O", NEG)],
        [(105, 150, 0), (85, 215, 0), (105, 280, 0),
         (265, 140, 1), (265, 290, 1),
         (425, 150, 2)])
    frags.append(text(260, 430, "етанол", size=22, bold=True))
    frags.append(text(260, 464, "рідина, кипить при +78 °C", size=16))
    frags.append(text(260, 496, "спирт — той, що в антисептику", size=14, color=MUTED))

    # ── праворуч: диметиловий етер, ланцюг C–O–C ────────────────────────────
    frags.append(rect(540, 62, 400, 320, fill="#ffffff"))
    frags += molecule(
        [(640, 215, "C", INK), (745, 215, "O", NEG), (850, 215, "C", INK)],
        [(585, 150, 0), (565, 215, 0), (585, 280, 0),
         (905, 150, 2), (925, 215, 2), (905, 280, 2)])
    frags.append(text(740, 430, "диметиловий етер", size=22, bold=True))
    frags.append(text(740, 464, "газ, кипить при −24 °C", size=16))
    frags.append(text(740, 496, "горючий газ, у балончиках", size=14, color=MUTED))

    frags.append(text(500, 540, "Різниця одна: у якому порядку атоми з'єднані між собою",
                      size=15, color=MUTED))

    render(os.path.join(IMG, 'formula-two-ways.svg'), W, H, *frags)


# ── Фігура 2: ті самі зв'язки, різне розташування ───────────────────────────
def fig_cis_trans():
    W, H = 980, 510
    R, RH = 24, 14
    frags = [text(490, 36, "Ті самі зв'язки — різне розташування в просторі",
                  size=18, bold=True)]

    def alkene(cx1, cx2, cy, chain_left, chain_right, h_left, h_right):
        out = []
        # подвійний зв'язок — дві паралельні лінії між кружками
        for dy in (-9, 9):
            out.append(line(cx1 + R, cy + dy, cx2 - R, cy + dy, sw=2))
        # хвости-ланцюги
        for start, pts in ((cx1, chain_left), (cx2, chain_right)):
            prev = None
            for p in pts:
                if prev is None:
                    out.append(bond(start, cy, R, p[0], p[1], 0, sw=2.4))
                else:
                    out.append(line(prev[0], prev[1], p[0], p[1], sw=2.4))
                prev = p
        # по одному Гідрогену на кожен Карбон
        for (hx, hy), cx in ((h_left, cx1), (h_right, cx2)):
            out.append(bond(cx, cy, R, hx, hy, RH, sw=1.6, color=MUTED))
        out.append(hyd(*h_left, r=RH))
        out.append(hyd(*h_right, r=RH))
        out.append(atom(cx1, cy, "C", r=R, size=19))
        out.append(atom(cx2, cy, "C", r=R, size=19))
        return out

    # ── ліворуч: цис, обидва хвости вгору ───────────────────────────────────
    frags.append(rect(50, 62, 420, 300, fill="#ffffff"))
    frags += alkene(200, 320, 215,
                    [(158, 152), (103, 172), (66, 122)],
                    [(362, 152), (417, 172), (454, 122)],
                    (167, 259), (353, 259))
    frags.append(text(260, 402, "цис: обидва хвости з одного боку", size=17, bold=True))
    frags.append(text(260, 434, "ланцюг заламується", size=15, color=MUTED))
    frags.append(text(260, 466, "так побудовані природні олії", size=14, color=MUTED))

    # ── праворуч: транс, хвости в різні боки ────────────────────────────────
    frags.append(rect(510, 62, 420, 300, fill="#ffffff"))
    frags += alkene(660, 780, 215,
                    [(618, 152), (563, 172), (526, 122)],
                    [(822, 278), (877, 258), (914, 308)],
                    (627, 259), (813, 171))
    frags.append(text(720, 402, "транс: хвости з різних боків", size=17, bold=True))
    frags.append(text(720, 434, "ланцюг лишається прямим", size=15, color=MUTED))
    frags.append(text(720, 466, "такі з'являються при затвердінні олії", size=14, color=MUTED))

    render(os.path.join(IMG, 'cis-trans.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_two_ways()
    fig_cis_trans()
    print("ok")

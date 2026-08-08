# -*- coding: utf-8 -*-
"""Фігури теми «Напрямок реакції»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

COLD_BG = "#eaf0fd"
COLD_ED = "#8fa8dd"
WARM_BG = "#e4f4ea"
WARM_ED = "#9cc3a6"
HOT_BG = "#fdecea"
HOT_ED = "#dd9c96"


def two_pulls():
    W, H = 1000, 440
    g = []
    g.append(text(W / 2, 36, "дві тяги вирішують, куди піде перетворення",
                  size=17, bold=True))

    # ── ліва панель: униз по енергії ────────────────────────────────────────
    g.append(rect(50, 70, 430, 280, fill=COLD_BG, stroke=COLD_ED))
    g.append(text(265, 104, "тяга перша: униз по енергії", size=15,
                  color=NEG, bold=True))
    # східець: висока полиця → схил → низька полиця
    g.append(line(100, 180, 205, 180, color=LINE, sw=2.5))
    g.append(line(205, 180, 330, 268, color=LINE, sw=2.5))
    g.append(line(330, 268, 435, 268, color=LINE, sw=2.5))
    g.append(circle(150, 168, 12, fill="#ffffff", stroke=NEG, sw=2))
    g.append(circle(390, 256, 12, fill=NEG, stroke=NEG, sw=2))
    g.append(text(150, 148, "старі зв'язки", size=12, color=MUTED))
    g.append(text(390, 300, "нові, міцніші", size=12, color=MUTED))
    g.append(text(265, 332, "різниця виходить теплом", size=12.5, color=INK))

    # ── права панель: угору по розкиданості ─────────────────────────────────
    g.append(rect(520, 70, 430, 280, fill=WARM_BG, stroke=WARM_ED))
    g.append(text(735, 104, "тяга друга: угору по розкиданості", size=15,
                  color=FIELD, bold=True))
    g.append(rect(555, 150, 130, 120, fill="#ffffff", stroke=WARM_ED, sw=1.2))
    for cx, cy in [(590, 185), (620, 180), (650, 190),
                   (595, 220), (625, 225), (655, 218)]:
        g.append(circle(cx, cy, 8, fill=FIELD, stroke=LINE, sw=1.0))
    g.append(arrow(700, 210, 760, 210, color=LINE, sw=2.2))
    g.append(rect(780, 150, 150, 120, fill="#ffffff", stroke=WARM_ED, sw=1.2))
    for cx, cy in [(797, 165), (860, 172), (918, 162),
                   (812, 216), (884, 208), (805, 256), (905, 252)]:
        g.append(circle(cx, cy, 8, fill=FIELD, stroke=LINE, sw=1.0))
    g.append(text(620, 300, "складено докупи", size=12, color=MUTED))
    g.append(text(855, 300, "розкидано", size=12, color=MUTED))
    g.append(text(735, 332, "розкиданих станів більше — вони й випадають",
                  size=12.5, color=INK))

    # ── підсумковий рядок ───────────────────────────────────────────────────
    g.append(text(W / 2, 396,
                  "дивляться в один бік — перетворення йде саме;",
                  size=14, color=INK))
    g.append(text(W / 2, 420,
                  "сперечаються — вибір робить температура",
                  size=14, color=INK))
    render(os.path.join(OUT, 'two-pulls.svg'), W, H, *g)


def water_direction():
    W, H = 1000, 400
    g = []
    g.append(text(W / 2, 36, "та сама вода — і два протилежні напрямки",
                  size=17, bold=True))

    boxes = [
        (80, COLD_BG, COLD_ED, "ЛІД", "молекули на місцях", "порядок, енергії мінімум"),
        (400, "#eef4fb", "#9fb4c0", "ВОДА", "тримаються купи,", "але ковзають одна повз одну"),
        (720, HOT_BG, HOT_ED, "ПАРА", "розлетілися врізнобіч", "розкиданості максимум"),
    ]
    for x, bg, ed, name, l1, l2 in boxes:
        g.append(rect(x, 96, 200, 140, fill=bg, stroke=ed))
        g.append(text(x + 100, 130, name, size=16, bold=True))
        g.append(text(x + 100, 165, l1, size=12, color=INK))
        g.append(text(x + 100, 190, l2, size=11.5, color=MUTED))

    g.append(arrow(95, 292, 905, 292, color=POS, sw=2.6))
    g.append(text(W / 2, 276, "нагріваємо — перемагає розкиданість",
                  size=13.5, color=POS))
    g.append(arrow(905, 344, 95, 344, color=NEG, sw=2.6))
    g.append(text(W / 2, 372, "охолоджуємо — перемагає енергія",
                  size=13.5, color=NEG))
    render(os.path.join(OUT, 'water-direction.svg'), W, H, *g)


if __name__ == '__main__':
    two_pulls()
    water_direction()
    print('ok')

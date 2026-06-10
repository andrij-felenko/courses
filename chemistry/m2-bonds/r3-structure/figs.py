# -*- coding: utf-8 -*-
"""Фігури Розділу 2.3 «Як влаштовані тверді речовини». Чистий Python без залежностей → SVG у ./img/."""
from pathlib import Path

IMG = Path(__file__).resolve().parent / "img"
IMG.mkdir(exist_ok=True)

FONT = 'font-family="Segoe UI, Arial, sans-serif"'


def svg_open(w, h):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '<defs>\n'
            '<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#444"/></marker>\n'
            '</defs>\n'
            '<rect width="%d" height="%d" fill="white"/>\n' % (w, h, w, h, w, h))


def text(x, y, s, size=15, anchor="middle", weight="normal", fill="#222"):
    return ('<text x="%s" y="%s" %s font-size="%s" text-anchor="%s" font-weight="%s" fill="%s">%s</text>\n'
            % (x, y, FONT, size, anchor, weight, fill, s))


def circle(x, y, r, fill, stroke="#555", sw=1.2):
    return '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="%s"/>\n' % (x, y, r, fill, stroke, sw)


def line(x1, y1, x2, y2, color="#888", w=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    return '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"%s/>\n' % (x1, y1, x2, y2, color, w, d)


OXRED = "#e05545"
WHITEH = "#f4f4f4"
VIOLET = "#9b8ac4"
GREEN = "#7cb87a"


def water(cx, cy):
    s = circle(cx, cy, 13, OXRED, stroke="#a83c30", sw=1.3)
    s += circle(cx - 17, cy + 13, 7.5, WHITEH, stroke="#888", sw=1.1)
    s += circle(cx + 17, cy + 13, 7.5, WHITEH, stroke="#888", sw=1.1)
    return s


def fig_molecules_vs_lattice():
    s = svg_open(940, 430)

    # ── зліва: молекулярна речовина ──
    s += text(240, 36, "окремі молекули: міцно всередині, слабко між", size=14.5, weight="bold")
    pts = ((120, 100), (300, 90), (200, 170), (360, 175), (120, 250), (280, 255))
    for (px, py) in pts:
        s += water(px, py)
    pairs = ((0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5))
    for (i, j) in pairs:
        s += line(pts[i][0], pts[i][1] + 8, pts[j][0], pts[j][1] + 8, color="#bbb", w=1.3, dash="4,5")
    s += text(240, 312, "нагрівання рве лише пунктир —", size=13, fill="#2f7d4f")
    s += text(240, 329, "молекули виходять цілими (лід → вода)", size=13, fill="#2f7d4f")

    # ── справа: суцільна ґратка ──
    s += text(700, 36, "ґратка: все — один кристал", size=14.5, weight="bold")
    for r in range(4):
        for c in range(4):
            x, y = 560 + c * 64, 80 + r * 60
            if c < 3:
                s += line(x, y, x + 64, y, color="#777", w=2.2)
            if r < 3:
                s += line(x, y, x, y + 60, color="#777", w=2.2)
    for r in range(4):
        for c in range(4):
            x, y = 560 + c * 64, 80 + r * 60
            if (r + c) % 2 == 0:
                s += circle(x, y, 13, VIOLET, stroke="#6f5fa0", sw=1.2)
                s += text(x, y + 4, "+", size=11, fill="white", weight="bold")
            else:
                s += circle(x, y, 16, GREEN, stroke="#4e8a4c", sw=1.2)
                s += text(x, y + 4, "−", size=11, fill="white", weight="bold")
    s += text(700, 312, "плавити — значить рвати самі зв'язки:", size=13, fill="#a83c30")
    s += text(700, 329, "тому сіль тримається до 801 °C", size=13, fill="#a83c30")

    # ── знизу: шкала температур плавлення ──
    s += line(80, 385, 880, 385, color="#444", w=2)
    marks = ((120, "лід", "0 °C"), (330, "цукор", "≈186 °C"), (570, "сіль", "801 °C"), (810, "алмаз", "≈3550 °C"))
    for (mx, name, t) in marks:
        s += line(mx, 378, mx, 392, color="#444", w=2)
        s += text(mx, 372, name, size=12.5, fill="#444", weight="bold")
        s += text(mx, 410, t, size=12.5, fill="#666")
    s += text(205, 410, "молекулярні", size=11.5, fill="#2f7d4f")
    s += text(690, 410, "ґраткові", size=11.5, fill="#a83c30")

    s += "</svg>\n"
    (IMG / "fig-2-3-1-1-molecules-vs-lattice.svg").write_text(s, encoding="utf-8")


DARKC = "#4a4a4a"


def carbon(x, y, r=9):
    return circle(x, y, r, DARKC, stroke="#222", sw=1.1)


def fig_diamond_graphite():
    s = svg_open(940, 400)
    s += text(470, 34, "той самий Карбон — дві різні конструкції", size=16, weight="bold")

    # ── зліва: алмаз — каркас на всі боки ──
    s += text(240, 64, "алмаз: кожен атом тримає чотирьох", size=14, fill="#444", weight="bold")
    nodes = {}
    for r in range(3):
        for c in range(4):
            x = 110 + c * 86 + (43 if r % 2 else 0)
            y = 110 + r * 86
            nodes[(r, c)] = (x, y)
    for r in range(3):
        for c in range(4):
            x, y = nodes[(r, c)]
            if c < 3:
                s += line(x, y, nodes[(r, c + 1)][0], nodes[(r, c + 1)][1], color="#555", w=2.2)
            if r < 2:
                s += line(x, y, nodes[(r + 1, c)][0], nodes[(r + 1, c)][1], color="#555", w=2.2)
                if (c > 0 and r % 2 == 0) or (c < 3 and r % 2):
                    cc = c - 1 if r % 2 == 0 else c + 1
                    s += line(x, y, nodes[(r + 1, cc)][0], nodes[(r + 1, cc)][1], color="#555", w=2.2)
    for key in nodes:
        s += carbon(*nodes[key])
    s += text(240, 360, "суцільний каркас: зрушити нікого не можна —", size=12.5, fill="#a83c30")
    s += text(240, 377, "найтвердіша річ, яку ми знаємо", size=12.5, fill="#a83c30")

    # ── справа: графіт — міцні листи, слабко між ними ──
    s += text(700, 64, "графіт: міцні листи, слабко між ними", size=14, fill="#444", weight="bold")
    for (layer, base_y, shift) in ((0, 120, 38), (1, 210, 0), (2, 300, 0)):
        xs = list(range(540 + shift, 880 + shift, 48))
        for i, x in enumerate(xs):
            y = base_y + (14 if i % 2 else -14)
            if i < len(xs) - 1:
                x2 = xs[i + 1]
                y2 = base_y + (14 if (i + 1) % 2 else -14)
                s += line(x, y, x2, y2, color="#555", w=2.2)
        for i, x in enumerate(xs):
            y = base_y + (14 if i % 2 else -14)
            s += carbon(x, y, r=8)
        if layer < 2:
            for x in range(580, 860, 70):
                s += line(x, base_y + 22, x, base_y + 62, color="#bbb", w=1.3, dash="4,5")
    s += '<line x1="560" y1="92" x2="660" y2="92" stroke="#2f7d4f" stroke-width="2" marker-end="url(#arr)"/>\n'
    s += text(640, 80, "верхній лист зісковзує — слід на папері", size=12, fill="#2f7d4f")
    s += text(700, 360, "усередині листа зв'язки справжні,", size=12.5, fill="#2f7d4f")
    s += text(700, 377, "між листами — лише пунктирне зчеплення", size=12.5, fill="#2f7d4f")

    s += "</svg>\n"
    (IMG / "fig-2-3-2-1-diamond-graphite.svg").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    fig_molecules_vs_lattice()
    fig_diamond_graphite()
    print("OK:", *(p.name for p in sorted(IMG.glob("*.svg"))))

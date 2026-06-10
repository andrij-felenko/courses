# -*- coding: utf-8 -*-
"""Фігури Розділу 1.3 «Періодична таблиця». Чистий Python без залежностей → SVG у ./img/."""
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


def arrow(x1, y1, x2, y2, double=False, color="#444", w=2):
    start = ' marker-start="url(#arr)"' if double else ''
    return ('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" '
            'marker-end="url(#arr)"%s/>\n' % (x1, y1, x2, y2, color, w, start))


CELLS = [
    (1, 1, 1, "H"), (1, 8, 2, "He"),
    (2, 1, 3, "Li"), (2, 2, 4, "Be"), (2, 3, 5, "B"), (2, 4, 6, "C"),
    (2, 5, 7, "N"), (2, 6, 8, "O"), (2, 7, 9, "F"), (2, 8, 10, "Ne"),
    (3, 1, 11, "Na"), (3, 2, 12, "Mg"), (3, 3, 13, "Al"), (3, 4, 14, "Si"),
    (3, 5, 15, "P"), (3, 6, 16, "S"), (3, 7, 17, "Cl"), (3, 8, 18, "Ar"),
]

X0, Y0, CW, CH = 60, 80, 54, 56


def cell_xy(row, col):
    return X0 + (col - 1) * CW, Y0 + (row - 1) * CH


def fig_reading_the_map():
    s = svg_open(940, 420)
    s += text(300, 38, "таблиця — це карта: позиція клітинки = характер атома", size=16, weight="bold")

    # смуги-підсвітки: рядок 2 (дві полички) і стовпчик 1 (один зовнішній електрон)
    s += '<rect x="%d" y="%d" width="%d" height="%d" fill="#fff3cd"/>\n' % (X0 - 3, Y0 + CH - 3, 8 * CW + 6, CH + 4)
    s += '<rect x="%d" y="%d" width="%d" height="%d" fill="#e3f0e6"/>\n' % (X0 - 3, Y0 - 3, CW + 4, 3 * CH + 6)

    for (r, c, num, sym) in CELLS:
        x, y = cell_xy(r, c)
        s += '<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#9fb4c0" stroke-width="1.2"/>\n' % (x, y, CW, CH)
        s += text(x + 8, y + 16, str(num), size=10.5, anchor="start", fill="#777")
        s += text(x + CW / 2, y + 40, sym, size=17, weight="bold")

    s += text(X0 - 12, Y0 + CH * 0.5 + 5, "1 поличка", size=11.5, anchor="end", fill="#777")
    s += text(X0 - 12, Y0 + CH * 1.5 + 5, "2 полички", size=11.5, anchor="end", fill="#9a7b1a")
    s += text(X0 - 12, Y0 + CH * 2.5 + 5, "3 полички", size=11.5, anchor="end", fill="#777")
    s += text(X0 + CW / 2, Y0 + 3 * CH + 24, "на зовнішній — 1 електрон:", size=11.5, fill="#3c7a4e")
    s += text(X0 + CW / 2, Y0 + 3 * CH + 40, "один стовпчик — одна сім'я", size=11.5, fill="#3c7a4e")
    s += text(X0 + 7.5 * CW, Y0 + 3 * CH + 24, "зовнішня заповнена:", size=11.5, fill="#777")
    s += text(X0 + 7.5 * CW, Y0 + 3 * CH + 40, "нічого не треба", size=11.5, fill="#777")
    s += text(X0 + 4 * CW, Y0 + 3 * CH + 70, "уздовж рядка зліва направо: +1 протон, +1 електрон на зовнішню поличку →", size=12.5, fill="#555")

    # ── праворуч: збільшена клітинка Натрію ──
    s += text(745, 78, "одна клітинка каже багато", size=15, weight="bold")
    s += '<rect x="640" y="95" width="210" height="180" rx="10" fill="#f7fafc" stroke="#b9c6cf" stroke-width="1.6"/>\n'
    s += text(660, 125, "11", size=18, anchor="start", fill="#444", weight="bold")
    s += text(745, 185, "Na", size=44, weight="bold")
    s += text(745, 218, "Натрій", size=15, fill="#555")
    s += text(745, 248, "маса ≈ 23", size=14, fill="#777")

    s += arrow(656, 132, 600, 170, color="#888", w=1.5)
    s += text(596, 188, "протонів у ядрі", size=12.5, anchor="end", fill="#a83c30")
    s += text(596, 204, "(і електронів навколо)", size=12.5, anchor="end", fill="#a83c30")
    s += arrow(800, 252, 870, 300, color="#888", w=1.5)
    s += text(872, 318, "середня вага атома", size=12.5, anchor="end", fill="#555")
    s += text(872, 334, "(дробова — згадай ізотопи)", size=12.5, anchor="end", fill="#555")

    s += "</svg>\n"
    (IMG / "fig-1-3-1-1-reading-the-map.svg").write_text(s, encoding="utf-8")


def fig_families():
    s = svg_open(940, 430)
    s += text(300, 38, "стовпчик = сім'я з однією стратегією", size=16, weight="bold")

    # підсвітки родин: лужні (стовпчик 1, рядки 2–3), галогени (7), інертні (8)
    x1, y1 = cell_xy(2, 1)
    s += '<rect x="%d" y="%d" width="%d" height="%d" fill="#e0f1e3"/>\n' % (x1 - 2, y1 - 2, CW + 4, 2 * CH + 4)
    x7, y7 = cell_xy(2, 7)
    s += '<rect x="%d" y="%d" width="%d" height="%d" fill="#ecdff2"/>\n' % (x7 - 2, y7 - 2, CW + 4, 2 * CH + 4)
    x8, y8 = cell_xy(1, 8)
    s += '<rect x="%d" y="%d" width="%d" height="%d" fill="#e9e9e9"/>\n' % (x8 - 2, y8 - 2, CW + 4, 3 * CH + 4)

    for (r, c, num, sym) in CELLS:
        x, y = cell_xy(r, c)
        s += '<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#9fb4c0" stroke-width="1.2"/>\n' % (x, y, CW, CH)
        s += text(x + 8, y + 16, str(num), size=10.5, anchor="start", fill="#777")
        s += text(x + CW / 2, y + 40, sym, size=17, weight="bold")

    fy = Y0 + 3 * CH
    s += text(X0 + CW / 2 + 4, fy + 24, "лужні:", size=12.5, fill="#2f7d4f", weight="bold")
    s += text(X0 + CW / 2 + 4, fy + 40, "легко віддають", size=11.5, fill="#2f7d4f")
    s += text(X0 + CW / 2 + 4, fy + 55, "свій 1 зовнішній", size=11.5, fill="#2f7d4f")
    s += text(X0 + 6.5 * CW, fy + 24, "галогени:", size=12.5, fill="#7a4694", weight="bold")
    s += text(X0 + 6.5 * CW, fy + 40, "жадібно беруть —", size=11.5, fill="#7a4694")
    s += text(X0 + 6.5 * CW, fy + 55, "бракує 1 до повної", size=11.5, fill="#7a4694")
    s += text(X0 + 7.85 * CW, fy + 80, "інертні: поличка повна,", size=11.5, fill="#666", anchor="end")
    s += text(X0 + 7.85 * CW, fy + 95, "нічого не треба", size=11.5, fill="#666", anchor="end")
    s += text(X0 + 1.6 * CW, Y0 + 28, "H — особливий, сам по собі", size=11, anchor="start", fill="#888")

    s += text(300, fy + 130, "← що лівіше й нижче — то активніший метал (легше віддає)", size=13, fill="#2f7d4f")
    s += text(300, fy + 150, "що правіше й вище (крім інертних) — то активніший неметал (легше бере) →", size=13, fill="#7a4694")

    # праворуч: сімейний портрет лужних
    s += text(745, 80, "одна сім'я — один характер", size=14.5, weight="bold")
    for (i, (sym, note)) in enumerate((("Li", "з водою — жваво"), ("Na", "бурхливо, аж бігає"), ("K", "спалахує"))):
        yy = 110 + i * 64
        s += '<rect x="660" y="%d" width="200" height="52" rx="8" fill="#e0f1e3" stroke="#9cc3a6"/>\n' % yy
        s += text(692, yy + 33, sym, size=18, weight="bold", fill="#2f7d4f")
        s += text(770, yy + 33, note, size=12.5, fill="#444")
    s += text(760, 320, "той самий «зайвий» електрон —", size=12.5, fill="#555")
    s += text(760, 336, "та сама поведінка, дедалі сміливіша", size=12.5, fill="#555")

    s += "</svg>\n"
    (IMG / "fig-1-3-2-1-families.svg").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    fig_reading_the_map()
    fig_families()
    print("OK:", *(p.name for p in sorted(IMG.glob("*.svg"))))

# -*- coding: utf-8 -*-
"""Фігури Розділу 6.2 «Масова частка». Чистий Python без залежностей → SVG у ./img/."""
from pathlib import Path

IMG = Path(__file__).resolve().parent / "img"
IMG.mkdir(exist_ok=True)

FONT = 'font-family="Segoe UI, Arial, sans-serif"'


def svg_open(w, h):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '<rect width="%d" height="%d" fill="white"/>\n' % (w, h, w, h, w, h))


def text(x, y, s, size=15, anchor="middle", weight="normal", fill="#222"):
    return ('<text x="%s" y="%s" %s font-size="%s" text-anchor="%s" font-weight="%s" fill="%s">%s</text>\n'
            % (x, y, FONT, size, anchor, weight, fill, s))


def rect(x, y, w, h, fill, stroke="#9fb4c0", sw=1.4, rx=0):
    return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="%s"/>\n' % (x, y, w, h, rx, fill, stroke, sw)


ORANGE = "#f0a93c"   # розчинена речовина (сіль)
BLUE = "#bfe0ef"     # вода / решта
OXRED = "#e05545"
WHITEH = "#eeeeee"


def fig_mass_fraction():
    s = svg_open(940, 360)
    s += text(470, 36, "масова частка: яку частину всієї маси становить речовина", size=16, weight="bold")

    # стовпчик-склянка: 30 г солі + 170 г води = 200 г
    bx, by, bw, bh = 120, 80, 130, 240
    salt_h = bh * 30.0 / 200.0
    s += rect(bx, by, bw, bh - salt_h, BLUE)
    s += rect(bx, by + bh - salt_h, bw, salt_h, ORANGE)
    s += text(bx + bw / 2, by + (bh - salt_h) / 2 + 5, "вода", size=13.5, fill="#3b6f88")
    s += text(bx + bw / 2, by + (bh - salt_h) / 2 + 24, "170 г", size=12.5, fill="#3b6f88")
    s += text(bx + bw / 2, by + bh - salt_h / 2 + 5, "сіль 30 г", size=12.5, fill="#7a5512")
    s += text(bx + bw / 2, by + bh + 22, "увесь розчин = 200 г", size=13, fill="#444")

    # формула й обрахунок
    s += rect(330, 110, 540, 180, "#f7fafc", rx=12)
    s += text(600, 145, "ω = m(речовини) / m(розчину) · 100%", size=18, weight="bold", fill="#1f6f9e")
    s += text(360, 200, "m(розчину) = 30 + 170 = 200 г", size=15, anchor="start")
    s += text(360, 232, "ω(солі) = 30 / 200 · 100% = 15%", size=16, anchor="start", weight="bold", fill="#2f7d4f")
    s += text(360, 268, "× 100 — щоб дріб 0,15 став зручними 15%", size=12.5, anchor="start", fill="#888")

    s += "</svg>\n"
    (IMG / "fig-6-2-1-1-mass-fraction.svg").write_text(s, encoding="utf-8")


def fig_element_fraction():
    s = svg_open(940, 360)
    s += text(470, 36, "масова частка елемента: з чого складена маса молекули", size=16, weight="bold")

    # смуга маси води 18 на дві частини: O=16, H=2
    bx, by, bw, bh = 110, 90, 560, 70
    o_w = bw * 16.0 / 18.0
    s += rect(bx, by, o_w, bh, OXRED)
    s += rect(bx + o_w, by, bw - o_w, bh, WHITEH)
    s += text(bx + o_w / 2, by + 30, "Оксиген", size=14, fill="white", weight="bold")
    s += text(bx + o_w / 2, by + 50, "16 з 18", size=12.5, fill="white")
    s += text(bx + o_w + (bw - o_w) / 2, by + 42, "H: 2", size=12, fill="#555")
    s += text(bx + bw / 2, by + bh + 24, "уся маса молекули води Mᵣ(H₂O) = 18", size=13, fill="#444")

    # формула й обрахунок
    s += rect(150, 200, 640, 130, "#f7fafc", rx=12)
    s += text(470, 232, "ω(Е) = n · Aᵣ / Mᵣ · 100%", size=18, weight="bold", fill="#1f6f9e")
    s += text(470, 268, "ω(O) у воді = 1 · 16 / 18 · 100% ≈ 89%", size=16, weight="bold", fill="#a83c30")
    s += text(470, 300, "ω(H) = 2 · 1 / 18 · 100% ≈ 11%    (разом 100%)", size=14, fill="#555")

    s += "</svg>\n"
    (IMG / "fig-6-2-2-1-element-fraction.svg").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    fig_mass_fraction()
    fig_element_fraction()
    print("OK:", *(p.name for p in sorted(IMG.glob("*.svg"))))

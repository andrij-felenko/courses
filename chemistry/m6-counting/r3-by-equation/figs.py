# -*- coding: utf-8 -*-
"""Фігури Розділу 6.3 «Розрахунки за рівнянням». Чистий Python без залежностей → SVG у ./img/."""
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


def rect(x, y, w, h, fill, stroke="#9fb4c0", sw=1.4, rx=10):
    return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="%s"/>\n' % (x, y, w, h, rx, fill, stroke, sw)


def arrow(x1, y1, x2, y2, color="#444", w=2):
    return ('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" '
            'marker-end="url(#arr)"/>\n' % (x1, y1, x2, y2, color, w))


def fig_mole_ratio():
    s = svg_open(940, 320)
    s += text(470, 38, "коефіцієнти рівняння — це відношення молів", size=16, weight="bold")

    # рівняння великим
    s += text(470, 110, "2H₂  +  O₂  →  2H₂O", size=30, weight="bold")
    # підписи молів під кожним
    s += text(150, 150, "2 молі", size=15, fill="#2f6f9e", weight="bold")
    s += text(360, 150, "1 моль", size=15, fill="#a83c30", weight="bold")
    s += text(640, 150, "2 молі", size=15, fill="#2f7d4f", weight="bold")

    s += rect(180, 190, 580, 100, "#f7fafc")
    s += text(470, 222, "читаємо як рецепт у молях:", size=13.5, fill="#666")
    s += text(470, 252, "на 1 моль O₂ припадає 2 молі H₂O", size=17, weight="bold", fill="#1f6f9e")
    s += text(470, 278, "тож із 2 молів O₂ вийде 2 · 2 = 4 молі H₂O", size=14, fill="#2f7d4f")

    s += "</svg>\n"
    (IMG / "fig-6-3-1-1-mole-ratio.svg").write_text(s, encoding="utf-8")


def fig_pipeline():
    s = svg_open(960, 340)
    s += text(480, 36, "розрахунок за рівнянням: грами → молі → молі → грами", size=16, weight="bold")

    def box(x, title, sub, fill):
        b = rect(x, 90, 190, 92, fill)
        b += text(x + 95, 124, title, size=15, weight="bold")
        b += text(x + 95, 152, sub, size=12.5, fill="#666")
        return b

    s += box(40, "маса даного", "8 г H₂", "#fdeee4")
    s += box(290, "молі даного", "n = m/M = 4", "#eef4fb")
    s += box(540, "молі шуканого", "за рівнянням = 4", "#eef4fb")
    s += box(770, "маса шуканого", "m = n·M = 72 г", "#e4f4ea")

    s += arrow(230, 136, 288, 136); s += text(259, 122, "÷ M", size=12.5, fill="#2f6f9e", weight="bold")
    s += arrow(480, 136, 538, 136); s += text(509, 118, "× відно-", size=11.5, fill="#a83c30"); s += text(509, 130, "шення", size=11.5, fill="#a83c30")
    s += arrow(730, 136, 768, 136); s += text(749, 122, "× M", size=12.5, fill="#2f7d4f", weight="bold")

    s += text(480, 232, "приклад: скільки грамів води з 8 г водню?   2H₂ + O₂ → 2H₂O", size=14, weight="bold")
    s += text(480, 262, "M(H₂)=2, M(H₂O)=18 · n(H₂)=8/2=4 · відношення H₂:H₂O=2:2 → n(H₂O)=4", size=13, fill="#555")
    s += text(480, 288, "m(H₂O) = 4 · 18 = 72 г", size=16, weight="bold", fill="#2f7d4f")

    s += "</svg>\n"
    (IMG / "fig-6-3-2-1-pipeline.svg").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    fig_mole_ratio()
    fig_pipeline()
    print("OK:", *(p.name for p in sorted(IMG.glob("*.svg"))))

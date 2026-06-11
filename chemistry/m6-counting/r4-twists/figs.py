# -*- coding: utf-8 -*-
"""Фігури Розділу 6.4 «Складніші задачі». Чистий Python без залежностей → SVG у ./img/."""
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


def rect(x, y, w, h, fill, stroke="#9fb4c0", sw=1.4, rx=8):
    return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="%s"/>\n' % (x, y, w, h, rx, fill, stroke, sw)


def circle(x, y, r, fill, stroke="#666", sw=1):
    return '<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="%s"/>\n' % (x, y, r, fill, stroke, sw)


BLUE = "#9fd6ef"
GREEN = "#7cb87a"
ORANGE = "#f0a93c"
RED = "#e07a5a"
GREY = "#cfcfcf"


def fig_molar_volume():
    s = svg_open(940, 340)
    s += text(470, 36, "однаковий об'єм газу — однакове число молекул (тож 1 моль = 22,4 л)", size=15, weight="bold")

    # три однакові коробки різних газів, у кожній однакова кількість «молекул»
    labels = (("кисень O₂", BLUE), ("водень H₂", GREEN), ("вуглекислий CO₂", ORANGE))
    import math
    for i, (lab, col) in enumerate(labels):
        x = 70 + i * 290
        s += rect(x, 80, 230, 150, "#fbfdfe")
        # 6 «молекул» розкидані
        pts = ((40, 40), (110, 30), (180, 50), (60, 95), (130, 100), (190, 110))
        for (px, py) in pts:
            s += circle(x + px, 80 + py, 11, col)
        s += text(x + 115, 252, lab, size=13.5, fill="#444")
        s += text(x + 115, 274, "1 моль · 22,4 л · 6·10²³ молекул", size=11, fill="#888")

    s += text(470, 312, "V = n · Vₘ        Vₘ = 22,4 л/моль (за нормальних умов)", size=17, weight="bold", fill="#1f6f9e")
    s += "</svg>\n"
    (IMG / "fig-6-4-1-1-molar-volume.svg").write_text(s, encoding="utf-8")


def fig_limiting():
    s = svg_open(940, 360)
    s += text(470, 36, "реакція йде по тому, чого менше: решта лишається в надлишку", size=15.5, weight="bold")
    s += text(470, 62, "рецепт: 2 яйця + 1 склянка борошна → 1 партія", size=13, fill="#666")

    # маємо: 6 яєць, 2 склянки борошна
    s += text(230, 100, "є 6 яєць", size=14, weight="bold")
    for i in range(6):
        s += '<ellipse cx="%d" cy="135" rx="14" ry="18" fill="#f3e3b0" stroke="#caa84a"/>\n' % (120 + i * 42)
    s += text(700, 100, "є 2 склянки борошна", size=14, weight="bold")
    for i in range(2):
        s += rect(610 + i * 70, 116, 50, 40, "#efe6d2", stroke="#b9a86a")

    # підрахунок «на скільки партій вистачить»
    s += rect(120, 185, 700, 130, "#f7fafc")
    s += text(470, 215, "на скільки партій вистачить кожного?", size=13.5, fill="#666")
    s += text(300, 248, "яйця: 6 ÷ 2 = 3 партії", size=15, anchor="middle")
    s += text(640, 248, "борошно: 2 ÷ 1 = 2 партії", size=15, anchor="middle", weight="bold", fill="#a83c30")
    s += text(470, 284, "менше — борошно: вийде 2 партії, а 2 яйця лишаться зайвими (надлишок)", size=14, weight="bold", fill="#2f7d4f")

    s += "</svg>\n"
    (IMG / "fig-6-4-2-1-limiting.svg").write_text(s, encoding="utf-8")


def fig_yield():
    s = svg_open(940, 320)
    s += text(470, 38, "вихід: скільки вийшло насправді проти того, що обіцяла теорія", size=15.5, weight="bold")

    base = 250
    # теоретичний стовпчик 72 г
    th = 150
    s += rect(220, base - th, 120, th, "#cfe0ef")
    s += text(280, base - th - 12, "теорія", size=13.5, fill="#3b6f88")
    s += text(280, base - th + 28, "72 г", size=16, weight="bold", fill="#3b6f88")
    s += text(280, base + 22, "скільки мало б", size=12, fill="#666")

    # практичний стовпчик 63 г (87.5%)
    ph = th * 63.0 / 72.0
    s += rect(420, base - ph, 120, ph, "#bfe3c8")
    s += text(480, base - ph - 12, "практика", size=13.5, fill="#2f7d4f")
    s += text(480, base - ph + 28, "63 г", size=16, weight="bold", fill="#2f7d4f")
    s += text(480, base + 22, "скільки вийшло", size=12, fill="#666")

    s += '<line x1="200" y1="%d" x2="560" y2="%d" stroke="#bbb" stroke-width="1.5"/>\n' % (base, base)

    s += rect(620, base - th, 260, th, "#f7fafc")
    s += text(750, base - th + 34, "η = m(практ)/m(теор)·100%", size=14.5, weight="bold", fill="#1f6f9e")
    s += text(750, base - th + 70, "η = 63 / 72 · 100%", size=15)
    s += text(750, base - th + 102, "= 87,5 %", size=18, weight="bold", fill="#2f7d4f")

    s += "</svg>\n"
    (IMG / "fig-6-4-3-1-yield.svg").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    fig_molar_volume()
    fig_limiting()
    fig_yield()
    print("OK:", *(p.name for p in sorted(IMG.glob("*.svg"))))

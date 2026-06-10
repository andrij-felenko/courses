# -*- coding: utf-8 -*-
"""Фігури Розділу 1.1 «Хімія і речовини». Чистий Python без залежностей → SVG у ./img/."""
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


def arrow(x1, y1, x2, y2, double=False, color="#444", w=2):
    start = ' marker-start="url(#arr)"' if double else ''
    return ('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" '
            'marker-end="url(#arr)"%s/>\n' % (x1, y1, x2, y2, color, w, start))


def box(x, y, w, h, label):
    s = '<rect x="%s" y="%s" width="%s" height="%s" rx="10" fill="#f7fafc" stroke="#b9c6cf"/>\n' % (x, y, w, h)
    s += text(x + w / 2, y + h - 9, label, size=13.5, fill="#445")
    return s


BLUE = "#9fd6ef"     # частинки води (ті самі в льоду, воді й парі)
GRAY = "#b8b8b8"     # частинки паперу
DARK = "#8a8a8a"     # попіл
RED = "#e05545"      # частинки кисню з повітря
ORANGE = "#f0a93c"   # частинки солі


def fig_two_changes():
    s = svg_open(940, 330)

    # ── ліва панель: фізичне перетворення ──
    s += text(250, 34, "Фізичне: частинки ТІ САМІ", size=16, weight="bold")
    s += box(40, 60, 120, 160, "лід")
    for gx in (70, 100, 130):
        for gy in (90, 120, 150):
            s += circle(gx, gy, 9, BLUE)
    s += box(190, 60, 120, 160, "вода")
    for (px, py) in ((212, 162), (238, 150), (265, 164), (290, 152),
                     (220, 188), (248, 176), (276, 190), (296, 178), (230, 134)):
        s += circle(px, py, 9, BLUE)
    s += box(340, 60, 120, 160, "пара")
    for (px, py) in ((355, 95), (395, 80), (435, 100), (370, 130), (415, 125),
                     (445, 152), (360, 168), (400, 172), (438, 188)):
        s += circle(px, py, 9, BLUE)
    s += arrow(163, 140, 187, 140, double=True)
    s += arrow(313, 140, 337, 140, double=True)
    s += text(250, 266, "⇄  можна повернути назад: інша лише «упаковка»", size=14, fill="#2f7d4f")

    s += '<line x1="490" y1="22" x2="490" y2="300" stroke="#ddd" stroke-width="1.5"/>\n'

    # ── права панель: хімічне перетворення ──
    s += text(715, 34, "Хімічне: частинки склалися ІНАКШЕ", size=16, weight="bold")
    s += box(520, 60, 150, 160, "папір + повітря")
    for px in (540, 562, 584, 606, 628, 650):          # ланцюжок частинок паперу
        s += circle(px, 170, 9, GRAY)
    for (px, py) in ((555, 95), (573, 95), (615, 88), (633, 88), (588, 125), (606, 125)):
        s += circle(px, py, 8, RED)                     # пари частинок кисню
    s += arrow(676, 140, 744, 140)
    s += text(710, 128, "горіння", size=13, fill="#b3541e")
    s += box(750, 60, 150, 160, "дим + попіл")
    for (cx, cy) in ((785, 95), (845, 122), (800, 157)):   # нові зчіпки: сіра + дві червоні
        s += circle(cx - 18, cy, 8, RED)
        s += circle(cx + 18, cy, 8, RED)
        s += circle(cx, cy, 9, GRAY)
    for (px, py) in ((772, 192), (800, 197), (828, 190)):  # попіл
        s += circle(px, py, 6, DARK)
    s += text(715, 266, "→  з'явилась нова речовина, назад не повернеться", size=14, fill="#b3413a")

    s += "</svg>\n"
    (IMG / "fig-1-1-1-1-two-changes.svg").write_text(s, encoding="utf-8")


def fig_mixture():
    s = svg_open(940, 320)

    s += box(40, 55, 190, 175, "чиста вода: один сорт")
    for (px, py) in ((75, 90), (120, 80), (170, 95), (90, 125), (140, 120),
                     (190, 130), (70, 160), (115, 155), (165, 165), (200, 95), (95, 190), (150, 192)):
        s += circle(px, py, 9, BLUE)

    s += box(290, 55, 190, 175, "суміш: два сорти впереміш")
    for (px, py) in ((325, 90), (370, 82), (420, 95), (340, 125), (440, 128),
                     (320, 162), (365, 158), (415, 165), (450, 90), (345, 195), (430, 195)):
        s += circle(px, py, 9, BLUE)
    for (px, py) in ((395, 118), (333, 144), (445, 158), (375, 192), (412, 86)):
        s += circle(px, py, 8, ORANGE)

    s += arrow(488, 142, 612, 142)
    s += text(550, 130, "нагрій", size=14, fill="#b3541e")

    s += box(620, 55, 280, 175, "вода полетіла — сіль лишилась")
    for (px, py) in ((660, 120), (705, 100), (750, 125), (800, 105), (850, 122)):
        s += circle(px, py, 9, BLUE)
        s += arrow(px, py - 16, px, py - 38, color="#7fb6d0", w=1.6)
    for px in (700, 718, 736, 754, 772):
        s += '<rect x="%d" y="196" width="11" height="11" fill="%s" stroke="#b07a17" stroke-width="1"/>\n' % (px, ORANGE)
    s += text(737, 188, "кристали солі", size=12.5, fill="#8a6512", anchor="middle")

    s += "</svg>\n"
    (IMG / "fig-1-1-2-1-mixture-evaporation.svg").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    fig_two_changes()
    fig_mixture()
    print("OK:", *(p.name for p in sorted(IMG.glob("*.svg"))))

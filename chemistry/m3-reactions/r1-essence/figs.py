# -*- coding: utf-8 -*-
"""Фігури Розділу 3.1 «Що таке реакція насправді». Чистий Python без залежностей → SVG у ./img/."""
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


def arrow(x1, y1, x2, y2, color="#444", w=2):
    return ('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" '
            'marker-end="url(#arr)"/>\n' % (x1, y1, x2, y2, color, w))


IRON = "#8a8f98"   # атоми Феруму
OXRED = "#e05545"  # атоми Оксигену


def flask(s, x, y, w, h):
    """Закрита колба: корпус + горло з пробкою."""
    s += '<rect x="%d" y="%d" width="%d" height="%d" rx="18" fill="#f4fafd" stroke="#8fb6c9" stroke-width="2"/>\n' % (x, y + 40, w, h - 40)
    s += '<rect x="%d" y="%d" width="44" height="46" fill="#f4fafd" stroke="#8fb6c9" stroke-width="2"/>\n' % (x + w / 2 - 22, y)
    s += '<rect x="%d" y="%d" width="52" height="14" rx="4" fill="#c9a36a" stroke="#9a7a44" stroke-width="1.5"/>\n' % (x + w / 2 - 26, y - 10)
    return s


def o2pair(s, x, y, r=7):
    s += circle(x, y, r, OXRED, stroke="#a83c30", sw=1.1)
    s += circle(x + 2 * r - 2, y, r, OXRED, stroke="#a83c30", sw=1.1)
    return s


def fig_lavoisier_flask():
    s = svg_open(960, 420)
    s += text(480, 34, "закрита колба: до і після реакції", size=16, weight="bold")

    # ── колба «до»: метал + кисень окремо ──
    s = flask(s, 100, 70, 280, 240)
    for (px, py) in ((170, 270), (205, 278), (240, 270), (275, 278), (310, 270), (222, 252)):
        s += circle(px, py, 11, IRON, stroke="#5d646e", sw=1.2)
    s = o2pair(s, 170, 160)
    s = o2pair(s, 250, 140)
    s = o2pair(s, 300, 185)
    s += text(240, 350, "метал + кисень повітря", size=13, fill="#555")
    s += '<rect x="160" y="365" width="160" height="32" rx="6" fill="#1d2b36"/>\n'
    s += text(240, 386, "маса: 100.00 г", size=14, fill="#9fe0a8", weight="bold")

    s += arrow(420, 200, 530, 200, color="#b3541e", w=2.2)
    s += text(475, 184, "реакція", size=13.5, fill="#b3541e")
    s += text(475, 226, "(нічого не впускали", size=11.5, fill="#888")
    s += text(475, 241, "і не випускали)", size=11.5, fill="#888")

    # ── колба «після»: ті самі атоми, інші партнери ──
    s = flask(s, 580, 70, 280, 240)
    for (px, py) in ((650, 270), (700, 276), (750, 268), (795, 276)):
        s += circle(px, py, 11, IRON, stroke="#5d646e", sw=1.2)
        s += circle(px - 11, py - 13, 7, OXRED, stroke="#a83c30", sw=1.1)
        s += circle(px + 11, py - 13, 7, OXRED, stroke="#a83c30", sw=1.1)
    s += circle(688, 252, 11, IRON, stroke="#5d646e", sw=1.2)
    s += circle(760, 250, 11, IRON, stroke="#5d646e", sw=1.2)
    s = o2pair(s, 700, 150)
    s += text(720, 350, "іржа: ті САМІ атоми, інші партнери", size=13, fill="#555")
    s += '<rect x="640" y="365" width="160" height="32" rx="6" fill="#1d2b36"/>\n'
    s += text(720, 386, "маса: 100.00 г", size=14, fill="#9fe0a8", weight="bold")

    s += "</svg>\n"
    (IMG / "fig-3-1-1-1-lavoisier-flask.svg").write_text(s, encoding="utf-8")


DARKC = "#4a4a4a"
WHITEH = "#f4f4f4"


def methane(s, cx, cy):
    for (dx, dy) in ((0, -26), (0, 26), (-26, 0), (26, 0)):
        s += circle(cx + dx, cy + dy, 8, WHITEH, stroke="#888", sw=1.1)
    s += circle(cx, cy, 13, DARKC, stroke="#222", sw=1.3)
    s += text(cx, cy + 5, "C", size=11, fill="white", weight="bold")
    return s


def o2(s, cx, cy):
    s += circle(cx, cy, 9, OXRED, stroke="#a83c30", sw=1.1)
    s += circle(cx + 16, cy, 9, OXRED, stroke="#a83c30", sw=1.1)
    return s


def co2(s, cx, cy):
    s += circle(cx, cy, 12, DARKC, stroke="#222", sw=1.3)
    s += text(cx, cy + 4, "C", size=10, fill="white", weight="bold")
    s += circle(cx - 26, cy, 10, OXRED, stroke="#a83c30", sw=1.1)
    s += circle(cx + 26, cy, 10, OXRED, stroke="#a83c30", sw=1.1)
    return s


def h2o(s, cx, cy):
    s += circle(cx, cy, 11, OXRED, stroke="#a83c30", sw=1.1)
    s += circle(cx - 15, cy + 12, 7, WHITEH, stroke="#888", sw=1.1)
    s += circle(cx + 15, cy + 12, 7, WHITEH, stroke="#888", sw=1.1)
    return s


def fig_balanced_methane():
    s = svg_open(960, 400)
    s += text(480, 34, "CH₄ + 2O₂ → CO₂ + 2H₂O — і бухгалтерія сходиться", size=16, weight="bold")

    # ── молекули ──
    y = 130
    s = methane(s, 110, y)
    s += text(110, 190, "CH₄", size=15, weight="bold")
    s += text(185, y + 6, "+", size=24, fill="#444")
    s += text(238, y + 6, "2", size=22, weight="bold", fill="#2f7d4f")
    s = o2(s, 270, y - 22)
    s = o2(s, 270, y + 22)
    s += text(280, 190, "2O₂", size=15, weight="bold")
    s += '<line x1="350" y1="%d" x2="430" y2="%d" stroke="#b3541e" stroke-width="2.5" marker-end="url(#arr)"/>\n' % (y, y)
    s = co2(s, 510, y)
    s += text(510, 190, "CO₂", size=15, weight="bold")
    s += text(580, y + 6, "+", size=24, fill="#444")
    s += text(630, y + 6, "2", size=22, weight="bold", fill="#2f7d4f")
    s = h2o(s, 680, y - 26)
    s = h2o(s, 680, y + 22)
    s += text(690, 190, "2H₂O", size=15, weight="bold")

    # ── бухгалтерія атомів ──
    s += '<rect x="180" y="230" width="600" height="130" rx="10" fill="#f7fafc" stroke="#b9c6cf"/>\n'
    s += text(480, 258, "перелік атомів зліва і справа", size=13.5, fill="#445", weight="bold")
    rows = (("Карбон C", "1", "1"), ("Гідроген H", "4", "4"), ("Оксиген O", "4", "4"))
    for i, (name, l, r) in enumerate(rows):
        yy = 288 + i * 26
        s += text(280, yy, name, size=13.5, anchor="start", fill="#444")
        s += text(520, yy, l, size=14, weight="bold")
        s += text(560, yy, "=", size=14, fill="#888")
        s += text(600, yy, r, size=14, weight="bold")
        s += text(660, yy, "✓", size=15, fill="#2f7d4f", weight="bold")

    s += "</svg>\n"
    (IMG / "fig-3-1-2-1-balanced-methane.svg").write_text(s, encoding="utf-8")


VIOLET = "#9b8ac4"
GREEN = "#7cb87a"
GRAYA = "#9aa1ab"


def ball(s, x, y, fill, label=""):
    s += circle(x, y, 13, fill, stroke="#666", sw=1.2)
    if label:
        s += text(x, y + 5, label, size=11, fill="white", weight="bold")
    return s


def epill(s, x, y):
    s += '<rect x="%d" y="%d" width="34" height="20" rx="10" fill="#fff1d6" stroke="#d8a23c"/>\n' % (x, y)
    s += text(x + 17, y + 14, "e⁻", size=12, fill="#9a6a10", weight="bold")
    return s


def fig_four_plots():
    s = svg_open(960, 470)
    s += text(480, 32, "чотири сюжети всіх реакцій", size=16, weight="bold")

    panels = (
        (40, 60, "СПОЛУЧЕННЯ: двоє стали одним", "іржавіння цвяха", True),
        (500, 60, "РОЗКЛАД: одне розпалось", "сода в гарячій духовці", True),
        (40, 250, "ЗАМІЩЕННЯ: витіснив із пари", "цвях у розчині мідної солі", True),
        (500, 250, "ОБМІН: помінялись партнерами", "сода + оцет", False),
    )
    for (px, py, title, example, redox) in panels:
        s += '<rect x="%d" y="%d" width="420" height="165" rx="12" fill="#f9fbfd" stroke="#b9c6cf"/>\n' % (px, py)
        s += text(px + 210, py + 26, title, size=13.5, weight="bold", fill="#334")
        s += text(px + 210, py + 150, example, size=12.5, fill="#777")
        if redox:
            s = epill(s, px + 370, py + 12)
        cy = py + 85
        if title.startswith("СПОЛУЧЕННЯ"):
            s = ball(s, px + 70, cy, GRAYA, "А")
            s += text(px + 105, cy + 6, "+", size=18, fill="#444")
            s = ball(s, px + 140, cy, OXRED, "Б")
            s += arrow(px + 180, cy, px + 250, cy)
            s = ball(s, px + 295, cy, GRAYA, "А")
            s = ball(s, px + 320, cy, OXRED, "Б")
        elif title.startswith("РОЗКЛАД"):
            s = ball(s, px + 85, cy, GRAYA, "А")
            s = ball(s, px + 110, cy, OXRED, "Б")
            s += arrow(px + 155, cy, px + 225, cy)
            s = ball(s, px + 270, cy, GRAYA, "А")
            s += text(px + 305, cy + 6, "+", size=18, fill="#444")
            s = ball(s, px + 340, cy, OXRED, "Б")
        elif title.startswith("ЗАМІЩЕННЯ"):
            s = ball(s, px + 55, cy, GRAYA, "А")
            s += text(px + 88, cy + 6, "+", size=18, fill="#444")
            s = ball(s, px + 120, cy, VIOLET, "Б")
            s = ball(s, px + 145, cy, OXRED, "В")
            s += arrow(px + 185, cy, px + 240, cy)
            s = ball(s, px + 280, cy, GRAYA, "А")
            s = ball(s, px + 305, cy, OXRED, "В")
            s += text(px + 338, cy + 6, "+", size=18, fill="#444")
            s = ball(s, px + 370, cy, VIOLET, "Б")
        else:
            s = ball(s, px + 55, cy, GRAYA, "А")
            s = ball(s, px + 80, cy, OXRED, "Б")
            s += text(px + 113, cy + 6, "+", size=18, fill="#444")
            s = ball(s, px + 145, cy, VIOLET, "В")
            s = ball(s, px + 170, cy, GREEN, "Г")
            s += arrow(px + 205, cy, px + 250, cy)
            s = ball(s, px + 285, cy, GRAYA, "А")
            s = ball(s, px + 310, cy, GREEN, "Г")
            s += text(px + 340, cy + 6, "+", size=18, fill="#444")
            s = ball(s, px + 370, cy, VIOLET, "В")
            s = ball(s, px + 395, cy, OXRED, "Б")

    s = epill(s, 285, 432)
    s += text(620, 446, "= тут хтось віддав електрони, а хтось забрав (окисно-відновна)", size=13, fill="#9a6a10")

    s += "</svg>\n"
    (IMG / "fig-3-1-3-1-four-plots.svg").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    fig_lavoisier_flask()
    fig_balanced_methane()
    fig_four_plots()
    print("OK:", *(p.name for p in sorted(IMG.glob("*.svg"))))

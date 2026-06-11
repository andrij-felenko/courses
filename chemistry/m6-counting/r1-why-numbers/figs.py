# -*- coding: utf-8 -*-
"""Фігури Розділу 6.1 «Чому хімія взагалі рахує». Чистий Python без залежностей → SVG у ./img/."""
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


def hand(x1, y1, x2, y2, color="#777", w=3):
    return '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-linecap="round"/>\n' % (x1, y1, x2, y2, color, w)


def arrow(x1, y1, x2, y2, color="#444", w=2):
    return ('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" '
            'marker-end="url(#arr)"/>\n' % (x1, y1, x2, y2, color, w))


OXRED = "#e05545"
WHITEH = "#f4f4f4"
GREEN = "#2f9e54"
REDX = "#d9533c"


def fig_fixed_ratio():
    s = svg_open(940, 420)
    s += text(470, 34, "чому склад сталий: руки цілі, тож відношення завжди те саме", size=15.5, weight="bold")

    # ── зліва: вода H₂O — дві руки Оксигену зайняті двома Гідрогенами ──
    s += text(250, 80, "вода: 2 Гідрогени на 1 Оксиген", size=14, weight="bold", fill=GREEN)
    ox, oy = 250, 200
    s += circle(ox, oy, 30, OXRED, stroke="#a83c30", sw=1.5)
    s += text(ox, oy + 6, "O", size=18, fill="white", weight="bold")
    # дві руки оксигену, зайняті
    s += hand(ox - 18, oy + 18, ox - 70, oy + 64)
    s += hand(ox + 18, oy + 18, ox + 70, oy + 64)
    hx1, hy1 = ox - 80, oy + 74
    hx2, hy2 = ox + 80, oy + 74
    s += circle(hx1, hy1, 15, WHITEH, stroke="#888", sw=1.3)
    s += text(hx1, hy1 + 5, "H", size=13, weight="bold")
    s += circle(hx2, hy2, 15, WHITEH, stroke="#888", sw=1.3)
    s += text(hx2, hy2 + 5, "H", size=13, weight="bold")
    s += text(ox - 95, oy - 6, "2 руки", size=12, anchor="end", fill="#a83c30")
    s += text(250, 320, "обидві руки Оксигену зайняті —", size=12.5, fill="#444")
    s += text(250, 338, "усі задоволені, склад замкнено", size=12.5, fill="#444")

    s += '<line x1="490" y1="60" x2="490" y2="360" stroke="#ddd" stroke-width="1.5"/>\n'

    # ── справа: третій Гідроген зайвий — немає руки ──
    s += text(710, 80, "а «H₃O» не буває", size=14, weight="bold", fill=REDX)
    ox2, oy2 = 690, 200
    s += circle(ox2, oy2, 30, OXRED, stroke="#a83c30", sw=1.5)
    s += text(ox2, oy2 + 6, "O", size=18, fill="white", weight="bold")
    s += hand(ox2 - 18, oy2 + 18, ox2 - 64, oy2 + 60)
    s += hand(ox2 + 18, oy2 + 18, ox2 + 64, oy2 + 60)
    s += circle(ox2 - 74, oy2 + 70, 15, WHITEH, stroke="#888", sw=1.3)
    s += text(ox2 - 74, oy2 + 75, "H", size=13, weight="bold")
    s += circle(ox2 + 74, oy2 + 70, 15, WHITEH, stroke="#888", sw=1.3)
    s += text(ox2 + 74, oy2 + 75, "H", size=13, weight="bold")
    # третій водень тулиться зверху — руки нема
    tx, ty = ox2, oy2 - 64
    s += circle(tx, ty, 15, WHITEH, stroke="#888", sw=1.3)
    s += text(tx, ty + 5, "H", size=13, weight="bold")
    s += arrow(tx, ty + 18, ox2, oy2 - 34, color=REDX, w=2)
    s += text(tx + 70, ty, "третьому Гідрогену", size=12, fill=REDX)
    s += text(tx + 70, ty + 17, "нема за яку руку взятись", size=12, fill=REDX)
    # знак «відскакує»
    s += text(ox2 + 150, oy2 - 30, "✕", size=24, fill=REDX, weight="bold")
    s += text(710, 320, "вільних рук в Оксигену більше нема —", size=12.5, fill="#444")
    s += text(710, 338, "тож відношення намертво лишається 2 : 1", size=12.5, fill="#444")

    s += text(470, 392, "ось чому в кожній молекулі — ціле, незмінне число атомів, і саме тому хімію можна РАХУВАТИ",
              size=13, fill="#555", weight="bold")

    s += "</svg>\n"
    (IMG / "fig-6-1-1-1-fixed-ratio.svg").write_text(s, encoding="utf-8")


def fig_triangle():
    s = svg_open(940, 380)
    s += text(470, 34, "трикутник m–n–M: закрий те, що шукаєш, — решта покаже формулу", size=15.5, weight="bold")

    # великий трикутник
    ax, ay = 470, 80      # вершина (m)
    bx, by = 320, 300     # лівий низ (n)
    cx, cy = 620, 300     # правий низ (M)
    s += '<path d="M %d %d L %d %d L %d %d Z" fill="#f3f8fb" stroke="#7fa8c0" stroke-width="2.5"/>\n' % (ax, ay, bx, by, cx, cy)
    # горизонтальна риска (ділення) і вертикальна (множення)
    s += '<line x1="355" y1="210" x2="585" y2="210" stroke="#7fa8c0" stroke-width="2"/>\n'
    s += '<line x1="470" y1="210" x2="470" y2="300" stroke="#7fa8c0" stroke-width="2"/>\n'
    s += text(470, 165, "m", size=34, weight="bold", fill="#a83c30")
    s += text(400, 270, "n", size=30, weight="bold", fill="#2f6f9e")
    s += text(545, 270, "M", size=30, weight="bold", fill="#2f7d4f")
    s += text(470, 330, "маса (г)   =   молі × молярна маса", size=13, fill="#555")

    # три підказки збоку
    s += '<rect x="690" y="90" width="220" height="210" rx="10" fill="#fbfdfe" stroke="#cdd8e0"/>\n'
    rows = (("закрий m", "m = n · M", "#a83c30"),
            ("закрий n", "n = m / M", "#2f6f9e"),
            ("закрий M", "M = m / n", "#2f7d4f"))
    for i, (lab, frm, col) in enumerate(rows):
        yy = 130 + i * 56
        s += text(710, yy, lab, size=13.5, anchor="start", fill="#777")
        s += text(710, yy + 24, frm, size=18, anchor="start", weight="bold", fill=col)

    s += "</svg>\n"
    (IMG / "fig-6-1-2-1-triangle.svg").write_text(s, encoding="utf-8")


def fig_bridge():
    s = svg_open(940, 300)
    s += text(470, 36, "моль — міст між тим, що зважуєш, і тим, що лічиш", size=15.5, weight="bold")

    def box(x, y, w, title, sub, fill):
        b = '<rect x="%d" y="%d" width="%d" height="86" rx="12" fill="%s" stroke="#9fb4c0" stroke-width="1.6"/>\n' % (x, y, w, fill)
        b += text(x + w / 2, y + 34, title, size=15, weight="bold")
        b += text(x + w / 2, y + 62, sub, size=12.5, fill="#666")
        return b

    yb = 110
    s += box(60, yb, 220, "маса", "грами (терези)", "#fdeee4")
    s += box(360, yb, 220, "кількість речовини", "молі (n)", "#eef4fb")
    s += box(680, yb, 200, "число частинок", "штуки (N)", "#e4f4ea")

    # стрілки вперед
    s += arrow(285, yb + 30, 355, yb + 30, color="#444", w=2)
    s += text(320, yb + 18, "÷ M", size=13, fill="#2f6f9e", weight="bold")
    s += arrow(585, yb + 30, 675, yb + 30, color="#444", w=2)
    s += text(630, yb + 18, "× Nₐ", size=13, fill="#2f7d4f", weight="bold")
    # стрілки назад
    s += arrow(355, yb + 62, 285, yb + 62, color="#999", w=1.8)
    s += text(320, yb + 80, "× M", size=12.5, fill="#888")
    s += arrow(675, yb + 62, 585, yb + 62, color="#999", w=1.8)
    s += text(630, yb + 80, "÷ Nₐ", size=12.5, fill="#888")

    s += text(470, 250, "Nₐ ≈ 6·10²³ (розмір «пачки»-моля) · M береш із таблиці", size=13, fill="#555")

    s += "</svg>\n"
    (IMG / "fig-6-1-2-2-bridge.svg").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    fig_fixed_ratio()
    fig_triangle()
    fig_bridge()
    print("OK:", *(p.name for p in sorted(IMG.glob("*.svg"))))

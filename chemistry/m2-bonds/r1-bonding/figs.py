# -*- coding: utf-8 -*-
"""Фігури Розділу 2.1 «Хімічний зв'язок». Чистий Python без залежностей → SVG у ./img/."""
import math
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


EBLUE = "#2e6fbb"   # електрони
RED = "#e05545"     # ядро


def shell_atom(cx, cy, outer_dots, r_out=52, dot_offset_deg=-90):
    """Атом схемою: ядро, повна внутрішня поличка (суцільне кільце), зовнішня пунктиром із крапками."""
    s = circle(cx, cy, 6, RED, stroke="#a83c30", sw=1)
    s += '<circle cx="%s" cy="%s" r="26" fill="none" stroke="#cfe3d4" stroke-width="7"/>\n' % (cx, cy)
    s += '<circle cx="%s" cy="%s" r="%s" fill="none" stroke="#999" stroke-width="1.4" stroke-dasharray="5,4"/>\n' % (cx, cy, r_out)
    pts = []
    for i in range(outer_dots):
        a = math.radians(dot_offset_deg + i * 360.0 / max(outer_dots, 1))
        px, py = cx + r_out * math.cos(a), cy + r_out * math.sin(a)
        s += circle(px, py, 5.5, EBLUE, stroke="#1b4a82", sw=1)
        pts.append((px, py))
    return s, pts


def fig_three_strategies():
    s = svg_open(960, 380)
    s += text(480, 36, "мета одна — повна зовнішня поличка (як в інертних)", size=16, weight="bold")
    s += text(480, 56, "суцільне кільце — нижча, уже повна поличка", size=12, fill="#7c9a85")

    # (а) ВІДДАТИ
    a, _ = shell_atom(170, 190, 1)
    s += a
    s += arrow(170, 132, 170, 86, color=EBLUE, w=2)
    s += text(170, 296, "віддати самотній зайвий —", size=13.5, fill="#2f7d4f")
    s += text(170, 313, "повною стане нижча поличка", size=13.5, fill="#2f7d4f")
    s += text(170, 340, "так робить Натрій", size=12, fill="#888")

    # (б) ЗАБРАТИ
    b, _ = shell_atom(480, 190, 7)
    s += b
    s += circle(480, 138, 5.5, "white", stroke="#1b4a82", sw=1.2)   # вільне місце
    s += arrow(480, 92, 480, 126, color=EBLUE, w=2)
    s += circle(480, 84, 5.5, EBLUE, stroke="#1b4a82", sw=1)
    s += text(480, 296, "добрати один до повної", size=13.5, fill="#7a4694")
    s += text(480, 340, "так робить Хлор", size=12, fill="#888")

    # (в) ПОДІЛИТИСЬ
    c1, _ = shell_atom(750, 190, 0, r_out=46)
    c2, _ = shell_atom(840, 190, 0, r_out=46)
    s += c1 + c2
    s += circle(795, 178, 5.5, EBLUE, stroke="#1b4a82", sw=1)
    s += circle(795, 202, 5.5, EBLUE, stroke="#1b4a82", sw=1)
    s += text(795, 296, "скластися в спільну пару —", size=13.5, fill="#b3541e")
    s += text(795, 313, "вона рахується обом одразу", size=13.5, fill="#b3541e")
    s += text(795, 340, "так роблять два Гідрогени", size=12, fill="#888")

    s += "</svg>\n"
    (IMG / "fig-2-1-1-1-three-strategies.svg").write_text(s, encoding="utf-8")


VIOLET = "#9b8ac4"   # іон Натрію
GREEN = "#7cb87a"    # іон Хлору
WHITEH = "#f4f4f4"   # Гідроген
OXRED = "#e05545"    # Оксиген


def fig_ionic():
    s = svg_open(960, 330)

    # кадр 1: крадіжка
    s += text(170, 36, "1. електрон переходить", size=14.5, weight="bold")
    a, _ = shell_atom(110, 150, 1, r_out=44)
    s += a
    b, _ = shell_atom(255, 150, 7, r_out=44)
    s += b
    s += arrow(110, 98, 215, 112, color=EBLUE, w=2)
    s += text(110, 215, "Натрій", size=12.5, fill="#666")
    s += text(255, 215, "Хлор", size=12.5, fill="#666")

    # кадр 2: готові іони притягуються
    s += text(520, 36, "2. іони притягуються", size=14.5, weight="bold")
    s += circle(450, 150, 26, VIOLET, stroke="#6f5fa0", sw=1.6)
    s += text(450, 157, "Na⁺", size=15, fill="white", weight="bold")
    s += circle(600, 150, 34, GREEN, stroke="#4e8a4c", sw=1.6)
    s += text(600, 157, "Cl⁻", size=15, fill="white", weight="bold")
    s += arrow(485, 150, 555, 150, color="#e05545", w=2)
    s += arrow(560, 170, 492, 170, color="#2e6fbb", w=2)
    s += text(525, 215, "протилежні заряди", size=12.5, fill="#666")
    s += text(525, 231, "тримають міцно", size=12.5, fill="#666")

    # кадр 3: ґратка солі
    s += text(810, 36, "3. виростає ґратка", size=14.5, weight="bold")
    for r in range(3):
        for c in range(3):
            x, y = 740 + c * 56, 95 + r * 56
            if (r + c) % 2 == 0:
                s += circle(x, y, 17, VIOLET, stroke="#6f5fa0", sw=1.2)
                s += text(x, y + 5, "+", size=13, fill="white", weight="bold")
            else:
                s += circle(x, y, 23, GREEN, stroke="#4e8a4c", sw=1.2)
                s += text(x, y + 5, "−", size=13, fill="white", weight="bold")
    s += text(796, 265, "кухонна сіль: не молекули,", size=12.5, fill="#666")
    s += text(796, 281, "а нескінченні обійми іонів", size=12.5, fill="#666")

    s += "</svg>\n"
    (IMG / "fig-2-1-2-1-ionic.svg").write_text(s, encoding="utf-8")


def fig_covalent_polar():
    s = svg_open(960, 340)

    # зліва: чесна спільна пара (молекула водню)
    s += text(240, 36, "чесний поділ: пара рівно посередині", size=14.5, weight="bold")
    s += '<circle cx="180" cy="170" r="52" fill="none" stroke="#999" stroke-width="1.4" stroke-dasharray="5,4"/>\n'
    s += '<circle cx="300" cy="170" r="52" fill="none" stroke="#999" stroke-width="1.4" stroke-dasharray="5,4"/>\n'
    s += circle(180, 170, 13, WHITEH, stroke="#888", sw=1.4)
    s += circle(300, 170, 13, WHITEH, stroke="#888", sw=1.4)
    s += circle(240, 156, 5.5, EBLUE, stroke="#1b4a82", sw=1)
    s += circle(240, 184, 5.5, EBLUE, stroke="#1b4a82", sw=1)
    s += text(180, 250, "Гідроген", size=12, fill="#666")
    s += text(300, 250, "Гідроген", size=12, fill="#666")
    s += text(240, 285, "молекула водню: обидва атоми", size=12.5, fill="#555")
    s += text(240, 301, "рахують пару своєю", size=12.5, fill="#555")

    # справа: вода — пару перетягнуто до Оксигену
    s += text(700, 36, "нечесний поділ: вода-«магнітик»", size=14.5, weight="bold")
    ox, oy = 700, 150
    s += circle(ox, oy, 30, OXRED, stroke="#a83c30", sw=1.6)
    s += text(ox, oy + 6, "O", size=16, fill="white", weight="bold")
    hx1, hy1 = ox - 78, oy + 62
    hx2, hy2 = ox + 78, oy + 62
    s += circle(hx1, hy1, 14, WHITEH, stroke="#888", sw=1.4)
    s += circle(hx2, hy2, 14, WHITEH, stroke="#888", sw=1.4)
    s += text(hx1, hy1 + 5, "H", size=12, weight="bold")
    s += text(hx2, hy2 + 5, "H", size=12, weight="bold")
    # спільні пари, зміщені до Оксигену
    for (px, py) in ((ox - 32, oy + 30), (ox - 44, oy + 20), (ox + 32, oy + 30), (ox + 44, oy + 20)):
        s += circle(px, py, 5, EBLUE, stroke="#1b4a82", sw=1)
    s += text(ox, oy - 48, "−", size=22, fill="#2e6fbb", weight="bold")
    s += text(hx1 - 26, hy1 + 10, "+", size=20, fill="#e05545", weight="bold")
    s += text(hx2 + 26, hy2 + 10, "+", size=20, fill="#e05545", weight="bold")
    s += text(700, 285, "Оксиген перетягує спільні пари до себе:", size=12.5, fill="#555")
    s += text(700, 301, "молекула ціла, але кінці заряджені", size=12.5, fill="#555")

    s += "</svg>\n"
    (IMG / "fig-2-1-2-2-covalent-polar.svg").write_text(s, encoding="utf-8")


def fig_metal_sea():
    s = svg_open(960, 360)

    # ── зліва: ґратка плюсів у морі електронів ──
    s += text(240, 36, "метал: ґратка плюсів у морі електронів", size=15, weight="bold")
    for r in range(3):
        for c in range(4):
            x, y = 90 + c * 80, 90 + r * 80
            s += circle(x, y, 20, VIOLET, stroke="#6f5fa0", sw=1.4)
            s += text(x, y + 6, "+", size=15, fill="white", weight="bold")
    for (px, py) in ((130, 70), (210, 105), (290, 70), (62, 130), (170, 150), (250, 140),
                     (330, 120), (110, 215), (190, 195), (270, 225), (350, 200), (75, 250),
                     (155, 265), (235, 250), (315, 270)):
        s += circle(px, py, 4.5, EBLUE, stroke="#1b4a82", sw=0.8)
    s += arrow(60, 300, 360, 300, color=EBLUE, w=1.8)
    s += text(210, 322, "море вільне: штовхни — потече (це і є струм)", size=12.5, fill="#1b4a82")

    # ── справа: чому метал гнеться, а сіль тріскає ──
    s += text(700, 36, "удар молотком: два різні фінали", size=15, weight="bold")

    # метал: шар зсунувся, море перетекло
    s += text(700, 66, "метал — шар ковзнув, море тримає далі", size=12.5, fill="#2f7d4f")
    for c in range(4):
        s += circle(580 + c * 56, 95, 16, VIOLET, stroke="#6f5fa0", sw=1.2)
        s += text(580 + c * 56, 100, "+", size=12, fill="white", weight="bold")
    for c in range(4):
        s += circle(608 + c * 56, 135, 16, VIOLET, stroke="#6f5fa0", sw=1.2)
        s += text(608 + c * 56, 140, "+", size=12, fill="white", weight="bold")
    for (px, py) in ((600, 115), (656, 118), (712, 113), (768, 117)):
        s += circle(px, py, 4, EBLUE, stroke="#1b4a82", sw=0.8)
    s += arrow(520, 135, 560, 135, color="#888", w=1.6)

    # сіль: зсув ставить однакові заряди поруч — тріщина
    s += text(700, 196, "сіль — зсув ставить + проти +, кристал тріскає", size=12.5, fill="#a83c30")
    seq1 = (VIOLET, GREEN, VIOLET, GREEN)
    seq2 = (GREEN, VIOLET, GREEN, VIOLET)
    for c in range(4):
        s += circle(580 + c * 56, 230, 16, seq1[c], stroke="#777", sw=1.2)
        s += text(580 + c * 56, 235, "+" if seq1[c] is VIOLET else "−", size=12, fill="white", weight="bold")
    for c in range(4):
        s += circle(608 + c * 56, 290, 16, seq2[c], stroke="#777", sw=1.2)
        s += text(608 + c * 56, 295, "+" if seq2[c] is VIOLET else "−", size=12, fill="white", weight="bold")
    # зсунутий нижній ряд ставить однакові заряди майже впритул → розлом
    s += '<path d="M 560 258 L 620 252 L 680 262 L 740 252 L 800 260" fill="none" stroke="#e05545" stroke-width="2.5" stroke-dasharray="7,5"/>\n'
    s += arrow(520, 290, 560, 290, color="#888", w=1.6)

    s += "</svg>\n"
    (IMG / "fig-2-1-3-1-metal-sea.svg").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    fig_three_strategies()
    fig_ionic()
    fig_covalent_polar()
    fig_metal_sea()
    print("OK:", *(p.name for p in sorted(IMG.glob("*.svg"))))

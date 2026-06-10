# -*- coding: utf-8 -*-
"""Фігури Розділу 3.3 «Швидкість і рівновага». Чистий Python без залежностей → SVG у ./img/."""
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


def line(x1, y1, x2, y2, color="#888", w=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    return '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"%s/>\n' % (x1, y1, x2, y2, color, w, d)


BLUE = "#5a9bd4"
RED = "#e07a5a"
GREEN = "#7cb87a"


def fig_three_knobs():
    s = svg_open(960, 400)
    s += text(480, 32, "реакція йде через зіткнення — три способи зробити їх частішими", size=15.5, weight="bold")

    # ── панель 1: ТЕМПЕРАТУРА ──
    x0 = 60
    s += '<rect x="%d" y="60" width="260" height="300" rx="12" fill="#f9fbfd" stroke="#cdd8e0"/>\n' % x0
    s += text(x0 + 130, 86, "ТЕПЛІШЕ", size=14.5, weight="bold", fill=RED)
    s += text(x0 + 130, 106, "удари частіші й сильніші", size=12, fill="#666")
    # холодна коробка (мало, короткі стрілки)
    s += '<rect x="%d" y="120" width="110" height="100" rx="6" fill="#eef4fb" stroke="#9fb4c0"/>\n' % (x0 + 15)
    s += text(x0 + 70, 138, "холод", size=11.5, fill="#1f6f9e")
    for (px, py) in ((x0 + 40, 170), (x0 + 95, 160), (x0 + 60, 200), (x0 + 100, 200)):
        s += circle(px, py, 7, BLUE)
        s += line(px, py, px + 8, py - 6, color="#aaa", w=1.4)
    # гаряча коробка (швидкі довгі стрілки)
    s += '<rect x="%d" y="120" width="110" height="100" rx="6" fill="#fdeee4" stroke="#e0a98c"/>\n' % (x0 + 135)
    s += text(x0 + 190, 138, "жар", size=11.5, fill=RED)
    for (px, py) in ((x0 + 160, 175), (x0 + 210, 162), (x0 + 175, 205), (x0 + 215, 198)):
        s += circle(px, py, 7, RED)
        s += line(px, py, px + 18, py - 13, color=RED, w=1.8)
    s += text(x0 + 130, 250, "тому холодильник", size=12.5, fill="#444")
    s += text(x0 + 130, 268, "сповільнює псування їжі:", size=12.5, fill="#444")
    s += text(x0 + 130, 286, "на холоді зустрічі рідші", size=12.5, fill="#444")

    # ── панель 2: ПОВЕРХНЯ ──
    x0 = 350
    s += '<rect x="%d" y="60" width="260" height="300" rx="12" fill="#f9fbfd" stroke="#cdd8e0"/>\n' % x0
    s += text(x0 + 130, 86, "ДРІБНІШЕ", size=14.5, weight="bold", fill=GREEN)
    s += text(x0 + 130, 106, "більша поверхня зустрічі", size=12, fill="#666")
    # грудка
    s += '<rect x="%d" y="135" width="70" height="70" rx="6" fill="#d8b878" stroke="#a8884a" stroke-width="1.6"/>\n' % (x0 + 30)
    s += text(x0 + 65, 224, "грудка:", size=12, fill="#444")
    s += text(x0 + 65, 240, "працює лише край", size=11, fill="#777")
    # порошок
    for i in range(7):
        for j in range(5):
            px = x0 + 150 + i * 13
            py = 138 + j * 13
            s += '<rect x="%d" y="%d" width="8" height="8" rx="1.5" fill="#d8b878" stroke="#a8884a"/>\n' % (px, py)
    s += text(x0 + 192, 224, "порошок:", size=12, fill="#444")
    s += text(x0 + 192, 240, "уся поверхня в ділі", size=11, fill="#777")
    s += text(x0 + 130, 280, "цукор-пісок розчиняється", size=12.5, fill="#444")
    s += text(x0 + 130, 298, "швидше за грудку рафінаду", size=12.5, fill="#444")

    # ── панель 3: КОНЦЕНТРАЦІЯ ──
    x0 = 640
    s += '<rect x="%d" y="60" width="260" height="300" rx="12" fill="#f9fbfd" stroke="#cdd8e0"/>\n' % x0
    s += text(x0 + 130, 86, "ГУСТІШЕ", size=14.5, weight="bold", fill="#7a5fb0")
    s += text(x0 + 130, 106, "більше зустрічей за мить", size=12, fill="#666")
    # рідко
    s += '<rect x="%d" y="120" width="110" height="100" rx="6" fill="#f3eefa" stroke="#b9a8d4"/>\n' % (x0 + 15)
    s += text(x0 + 70, 138, "рідко", size=11.5, fill="#7a5fb0")
    for (px, py) in ((x0 + 40, 175), (x0 + 95, 195), (x0 + 60, 205)):
        s += circle(px, py, 7, "#9b8ac4")
    # густо
    s += '<rect x="%d" y="120" width="110" height="100" rx="6" fill="#ece2f7" stroke="#9b8ac4"/>\n' % (x0 + 135)
    s += text(x0 + 190, 138, "густо", size=11.5, fill="#7a5fb0")
    pts = []
    for i in range(4):
        for j in range(3):
            pts.append((x0 + 152 + i * 22, 158 + j * 20))
    for (px, py) in pts:
        s += circle(px, py, 7, "#9b8ac4")
    s += text(x0 + 130, 250, "у чистому кисні реакції", size=12.5, fill="#444")
    s += text(x0 + 130, 268, "йдуть бурхливіше, ніж", size=12.5, fill="#444")
    s += text(x0 + 130, 286, "у звичайному повітрі", size=12.5, fill="#444")

    s += "</svg>\n"
    (IMG / "fig-3-3-1-1-three-knobs.svg").write_text(s, encoding="utf-8")


def path(d, stroke="#444", w=3, fill="none"):
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%s"/>\n' % (d, fill, stroke, w)


def fig_catalyst_barrier():
    s = svg_open(960, 430)
    s += text(480, 32, "каталізатор знижує бар'єр — і сам виходить цілим", size=16, weight="bold")

    # осі
    s += arrow(90, 350, 90, 70, color="#444", w=2)
    s += text(70, 82, "енергія", size=13, anchor="end", fill="#444")
    s += arrow(90, 350, 720, 350, color="#444", w=2)
    s += text(700, 372, "хід реакції →", size=13, anchor="end", fill="#444")

    # рівні старту й фінішу однакові для обох шляхів
    sy = 250   # старт
    fy = 300   # фініш
    s += line(110, sy, 180, sy, color="#888", w=1.2, dash="5,4")
    s += text(150, sy - 8, "початок", size=11.5, fill="#555")
    s += line(560, fy, 700, fy, color="#888", w=1.2, dash="5,4")
    s += text(640, fy + 20, "продукти", size=11.5, fill="#555")

    # високий бар'єр — без каталізатора
    s += path("M 150 %d C 280 %d, 300 110, 400 110 C 500 110, 520 %d, 660 %d" % (sy, sy, fy, fy),
              stroke="#d9533c", w=3)
    s += text(400, 96, "без каталізатора", size=13, fill="#d9533c", weight="bold")
    s += text(400, 80, "високий бар'єр", size=11.5, fill="#d9533c")

    # низький бар'єр — з каталізатором
    s += path("M 150 %d C 260 %d, 300 200, 400 200 C 500 200, 540 %d, 660 %d" % (sy, sy, fy, fy),
              stroke="#2f9e54", w=3)
    s += text(400, 224, "з каталізатором: бар'єр нижчий —", size=13, fill="#2f9e54", weight="bold")
    s += text(400, 242, "через горб перескакує набагато більше зустрічей", size=11.5, fill="#2f9e54")

    # позначка: початок і кінець НЕ змінилися
    s += text(150, sy + 22, "однакові", size=10.5, fill="#888")
    s += line(660, sy - 60, 660, fy, color="#ccc", w=1)

    # каталізатор виходить цілим
    s += '<rect x="760" y="120" width="160" height="210" rx="12" fill="#f9fbfd" stroke="#cdd8e0"/>\n'
    s += text(840, 146, "каталізатор", size=13.5, weight="bold", fill="#334")
    s += circle(840, 185, 22, "#e0b54a", stroke="#a8884a", sw=1.6)
    s += text(840, 191, "К", size=16, fill="white", weight="bold")
    s += text(840, 225, "до реакції", size=11.5, fill="#777")
    s += arrow(840, 238, 840, 262, color="#666", w=1.8)
    s += circle(840, 292, 22, "#e0b54a", stroke="#a8884a", sw=1.6)
    s += text(840, 298, "К", size=16, fill="white", weight="bold")
    s += text(840, 323, "після — той самий!", size=11.5, fill="#2f9e54")

    s += "</svg>\n"
    (IMG / "fig-3-3-2-1-catalyst-barrier.svg").write_text(s, encoding="utf-8")


def fig_dynamic_equilibrium():
    s = svg_open(960, 380)
    s += text(480, 32, "рівновага — це не «зупинилось», а «туди = назад»", size=16, weight="bold")

    # два резервуари, між ними дві зустрічні стрілки
    s += '<rect x="110" y="90" width="220" height="180" rx="12" fill="#eef4fb" stroke="#9fb4c0"/>\n'
    s += text(220, 114, "реагенти", size=13.5, weight="bold", fill="#1f6f9e")
    for (px, py) in ((150, 150), (200, 140), (260, 155), (175, 195), (240, 200), (290, 175), (210, 235)):
        s += circle(px, py, 9, BLUE)

    s += '<rect x="630" y="90" width="220" height="180" rx="12" fill="#e4f4ea" stroke="#9cc3a6"/>\n'
    s += text(740, 114, "продукти", size=13.5, weight="bold", fill="#2f9e54")
    for (px, py) in ((670, 150), (720, 140), (780, 155), (695, 195), (760, 200), (810, 175), (730, 235)):
        s += circle(px, py, 9, GREEN)

    # дві зустрічні стрілки, однакова товщина = однакова швидкість
    s += arrow(340, 150, 620, 150, color="#b3541e", w=3)
    s += text(480, 138, "туди", size=13, fill="#b3541e")
    s += arrow(620, 210, 340, 210, color="#7a5fb0", w=3)
    s += text(480, 232, "назад", size=13, fill="#7a5fb0")
    s += text(480, 180, "однакова швидкість", size=12, fill="#888")

    s += text(480, 300, "рівні більше не міняються — але обидва процеси тривають,", size=13.5, fill="#444")
    s += text(480, 320, "просто рівно гасять один одного (динамічна рівновага)", size=13.5, fill="#444")
    s += text(480, 348, "знак ⇄ замість → саме про це", size=12.5, fill="#777")

    s += "</svg>\n"
    (IMG / "fig-3-3-3-1-dynamic-equilibrium.svg").write_text(s, encoding="utf-8")


def fig_fizzy():
    s = svg_open(960, 400)
    s += text(480, 32, "газована вода: CO₂ у воді ⇄ CO₂ над водою", size=16, weight="bold")

    def bottle(x, y, w, h, cap_closed):
        b = '<rect x="%d" y="%d" width="%d" height="%d" rx="14" fill="#dff0f7" stroke="#8fb6c9" stroke-width="2"/>\n' % (x, y + 34, w, h - 34)
        b += '<rect x="%d" y="%d" width="30" height="40" fill="#dff0f7" stroke="#8fb6c9" stroke-width="2"/>\n' % (x + w / 2 - 15, y)
        if cap_closed:
            b += '<rect x="%d" y="%d" width="38" height="14" rx="3" fill="#c9a36a" stroke="#9a7a44"/>\n' % (x + w / 2 - 19, y - 8)
        return b

    # ── закрита: рівновага, вода лишається газованою ──
    s += bottle(120, 70, 150, 290, True)
    s += text(195, 100, "закрита", size=13, weight="bold", fill="#1f6f9e")
    # бульбашки в воді + газ над водою
    for (px, py) in ((155, 250), (185, 290), (225, 260), (170, 320), (210, 310), (240, 300)):
        s += circle(px, py, 5, "#bfe0ef", stroke="#8fb6c9", sw=1)
    s += arrow(195, 200, 195, 165, color="#7a5fb0", w=1.6)   # назад: газ розчиняється
    s += arrow(180, 165, 180, 200, color="#b3541e", w=1.6)   # туди: виходить
    s += text(195, 345, "⇄ зрівноважено: лишається газованою", size=11, fill="#2f9e54")

    # ── відкрита: газ тікає, вода видихається ──
    s += bottle(405, 70, 150, 290, False)
    s += text(480, 100, "відкрита", size=13, weight="bold", fill="#b3541e")
    for (px, py) in ((440, 300), (470, 320), (505, 305)):
        s += circle(px, py, 4, "#bfe0ef", stroke="#8fb6c9", sw=1)
    for (px, py, d) in ((465, 60, 30), (480, 45, 40), (495, 58, 28)):
        s += arrow(px, py + d, px, py, color="#b3541e", w=1.8)
    s += text(480, 345, "газ тікає — рівновага зсунулась,", size=11, fill="#b3541e")
    s += text(480, 360, "вода видихається", size=11, fill="#b3541e")

    # ── тепла: тікає швидше ──
    s += bottle(690, 70, 150, 290, False)
    s += text(765, 100, "тепла й відкрита", size=12.5, weight="bold", fill="#c23b2a")
    for (px, py, d) in ((735, 52, 44), (755, 38, 52), (775, 50, 46), (795, 44, 50)):
        s += arrow(px, py + d, px, py, color="#c23b2a", w=2.2)
    s += text(765, 345, "тепло жене ⇄ убік газу —", size=11, fill="#c23b2a")
    s += text(765, 360, "вивітрюється ще швидше", size=11, fill="#c23b2a")

    s += "</svg>\n"
    (IMG / "fig-3-3-3-2-fizzy.svg").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    fig_three_knobs()
    fig_catalyst_barrier()
    fig_dynamic_equilibrium()
    fig_fizzy()
    print("OK:", *(p.name for p in sorted(IMG.glob("*.svg"))))

# -*- coding: utf-8 -*-
"""Фігури Розділу 1.2 «Атом». Чистий Python без залежностей → SVG у ./img/."""
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


BLUE = "#9fd6ef"   # атоми сорту А
RED = "#e05545"    # атоми сорту Б


def pair(x, y, c1, c2, r=9):
    """Двоатомна молекула: два дотичні кружечки."""
    return circle(x, y, r, c1) + circle(x + 2 * r - 2, y, r, c2)


def triple(x, y, r=9):
    """Триатомна молекула на кшталт води: Б у центрі, два А знизу по боках."""
    s = circle(x, y, r, RED)
    s += circle(x - 14, y + 12, r - 1, BLUE)
    s += circle(x + 14, y + 12, r - 1, BLUE)
    return s


def fig_atoms_to_substances():
    s = svg_open(940, 340)

    # колонка 1: окремі атоми двох сортів
    s += text(120, 38, "атоми", size=16, weight="bold")
    for (px, py) in ((85, 80), (145, 70), (105, 125), (160, 115)):
        s += circle(px, py, 10, BLUE)
    s += text(120, 160, "сорт А", size=13, fill="#3b7da0")
    for (px, py) in ((90, 205), (150, 195), (115, 250)):
        s += circle(px, py, 10, RED)
    s += text(120, 285, "сорт Б", size=13, fill="#a83c30")

    s += arrow(205, 165, 255, 165)
    s += text(230, 152, "зчепились", size=12.5, fill="#666")

    # колонка 2: молекули
    s += text(370, 38, "молекули — зчіпки атомів", size=16, weight="bold")
    s += pair(305, 90, BLUE, BLUE)
    s += text(330, 122, "два однакові", size=12.5, fill="#666")
    s += pair(415, 90, RED, RED)
    s += text(440, 122, "теж однакові", size=12.5, fill="#666")
    s += triple(370, 195)
    s += text(370, 240, "різні сорти в одній зчіпці", size=12.5, fill="#666")

    s += arrow(495, 165, 530, 165)

    # колонка 3: з молекул складаються речовини
    s += text(715, 38, "речовини", size=16, weight="bold")
    s += box(545, 60, 112, 200, "проста")
    for (px, py) in ((565, 95), (600, 130), (565, 170), (600, 210)):
        s += pair(px, py, BLUE, BLUE, r=8)
    s += box(672, 60, 112, 200, "складна")
    for (px, py) in ((705, 100), (745, 150), (705, 200)):
        s += triple(px, py, r=8)
    s += box(799, 60, 112, 200, "суміш")
    s += pair(815, 95, BLUE, BLUE, r=8)
    s += pair(865, 120, RED, RED, r=8)
    s += triple(835, 165, r=8)
    s += pair(820, 215, BLUE, BLUE, r=8)

    s += "</svg>\n"
    (IMG / "fig-1-2-1-1-atoms-to-substances.svg").write_text(s, encoding="utf-8")


GRAYN = "#9a9a9a"   # нейтрони
EBLUE = "#2e6fbb"   # електрони


def fig_atom_inside():
    s = svg_open(940, 380)

    # ── зліва: будова атома з поличками ──
    cx, cy = 250, 195
    s += '<circle cx="%d" cy="%d" r="75" fill="none" stroke="#bbb" stroke-width="1.4" stroke-dasharray="5,4"/>\n' % (cx, cy)
    s += '<circle cx="%d" cy="%d" r="130" fill="none" stroke="#bbb" stroke-width="1.4" stroke-dasharray="5,4"/>\n' % (cx, cy)
    # ядро: протони (+) і нейтрони впереміш
    for (px, py, f) in ((cx - 7, cy - 5, RED), (cx + 7, cy - 6, GRAYN), (cx, cy + 7, RED),
                        (cx - 9, cy + 6, GRAYN), (cx + 9, cy + 5, RED), (cx + 1, cy - 9, GRAYN)):
        s += circle(px, py, 7, f, sw=1)
    s += text(cx - 4, cy - 1, "+", size=11, fill="white", weight="bold")
    # електрони: 2 на першій поличці, 4 на другій
    for (ex, ey) in ((cx - 75, cy), (cx + 75, cy)):
        s += circle(ex, ey, 6, EBLUE, stroke="#1b4a82")
    for (ex, ey) in ((cx, cy - 130), (cx + 113, cy + 65), (cx - 113, cy + 65), (cx, cy + 130)):
        s += circle(ex, ey, 6, EBLUE, stroke="#1b4a82")
    s += text(cx, 38, "полички для електронів (−)", size=14, fill="#1b4a82")
    s += text(cx - 100, 355, "1-ша поличка: місць лише 2", size = 12.5, fill="#666", anchor="start")
    s += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#888" stroke-width="1"/>\n' % (cx + 14, cy + 2, cx + 95, cy + 78)
    s += text(cx + 100, cy + 88, "ядро: протони (+) і нейтрони,", size=12.5, anchor="start", fill="#a83c30")
    s += text(cx + 100, cy + 104, "майже вся маса атома тут", size=12.5, anchor="start", fill="#a83c30")

    # ── справа: масштаб порожнечі ──
    s += text(700, 38, "а тепер чесний масштаб", size=15, weight="bold")
    s += '<circle cx="700" cy="205" r="135" fill="#f3f9fc" stroke="#9fc3d8" stroke-width="1.6"/>\n'
    s += circle(700, 205, 2.5, RED, stroke="#a83c30", sw=1)
    s += '<line x1="700" y1="200" x2="700" y2="120" stroke="#888" stroke-width="1"/>\n'
    s += text(700, 110, "ядро", size=12.5, fill="#a83c30")
    s += text(700, 365, "якби атом був стадіоном, ядро було б мухою в центрі поля", size=13.5, fill="#555")

    s += "</svg>\n"
    (IMG / "fig-1-2-2-1-atom-inside.svg").write_text(s, encoding="utf-8")


def fig_rutherford():
    s = svg_open(940, 310)

    s += text(120, 40, "потік частинок", size=13.5, fill="#555")
    s += '<rect x="60" y="60" width="60" height="200" rx="6" fill="#e8e8e8" stroke="#aaa"/>\n'
    s += text(90, 165, "джерело", size=12, fill="#555")

    # золота фольга
    s += '<rect x="556" y="50" width="9" height="220" fill="#e8c84a" stroke="#b89a1f"/>\n'
    s += text(560, 290, "золота фольга — завтовшки лише в тисячі атомів", size=12.5, fill="#8a6512")

    # більшість частинок пролітає наскрізь
    for y in (90, 130, 250):
        s += arrow(130, y, 548, y, color="#888", w=1.8)
        s += arrow(566, y, 880, y, color="#888", w=1.8)
    # одна ледь відхилилась
    s += arrow(130, 170, 548, 170, color="#888", w=1.8)
    s += arrow(566, 170, 880, 148, color="#888", w=1.8)
    # одна відскочила назад
    s += arrow(130, 210, 552, 210, color=RED, w=2.2)
    s += arrow(556, 210, 200, 282, color=RED, w=2.2)

    s += text(720, 78, "майже всі — наскрізь:", size=13, fill="#444", anchor="middle")
    s += text(720, 94, "атом переважно порожній", size=13, fill="#444", anchor="middle")
    s += text(330, 268, "1 із тисяч відскакує: у центрі є щось", size=13, fill="#a83c30", anchor="middle")
    s += text(330, 284, "крихітне, щільне і з «плюсом»", size=13, fill="#a83c30", anchor="middle")

    s += "</svg>\n"
    (IMG / "fig-1-2-2-2-rutherford.svg").write_text(s, encoding="utf-8")


def nucleus_card(s, x, y, num, name, sym):
    """Картка елемента: ядро-кружок із числом протонів + ім'я."""
    s += box(x, y, 170, 150, "%s · %s" % (name, sym))
    s += circle(x + 85, y + 60, 26, RED, stroke="#a83c30", sw=1.5)
    s += text(x + 85, y + 66, str(num), size=17, fill="white", weight="bold")
    s += text(x + 85, y + 112, "протонів у ядрі", size=12.5, fill="#666")
    return s


def fig_element_is_number():
    s = svg_open(940, 350)

    s += text(330, 36, "сорт атома задає одне число — скільки протонів у ядрі", size=15.5, weight="bold")
    s = nucleus_card(s, 40, 60, 1, "Гідроген", "H")
    s = nucleus_card(s, 240, 60, 8, "Оксиген", "O")
    s = nucleus_card(s, 440, 60, 26, "Ферум", "Fe")

    # ізотопи: нейтрони сорт не міняють
    s += text(770, 36, "а нейтрони сорт не міняють", size=15.5, weight="bold")
    s += box(660, 60, 220, 150, "обидва — Гідроген (ізотопи)")
    s += circle(715, 120, 16, RED, stroke="#a83c30", sw=1.5)
    s += text(715, 126, "1", size=13, fill="white", weight="bold")
    s += circle(805, 112, 16, RED, stroke="#a83c30", sw=1.5)
    s += text(805, 118, "1", size=13, fill="white", weight="bold")
    s += circle(825, 132, 16, GRAYN, stroke="#777", sw=1.5)
    s += text(715, 165, "1 протон", size=12, fill="#666")
    s += text(810, 175, "1 протон + нейтрон", size=12, fill="#666")

    s += arrow(330, 280, 610, 280, color="#a83c30", w=2)
    s += text(470, 265, "змінити число протонів хімія не вміє", size=13.5, fill="#a83c30")
    s += text(470, 305, "тому в реакціях елементи не перетворюються одне на одного", size=13.5, fill="#555")

    s += "</svg>\n"
    (IMG / "fig-1-2-3-1-element-is-number.svg").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    fig_atoms_to_substances()
    fig_atom_inside()
    fig_rutherford()
    fig_element_is_number()
    print("OK:", *(p.name for p in sorted(IMG.glob("*.svg"))))

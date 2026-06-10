# -*- coding: utf-8 -*-
"""Фігури Розділу 2.2 «Формули, валентність і моль». Чистий Python без залежностей → SVG у ./img/."""
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


def arrow(x1, y1, x2, y2, color="#444", w=1.6):
    return ('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" '
            'marker-end="url(#arr)"/>\n' % (x1, y1, x2, y2, color, w))


OXRED = "#e05545"
WHITEH = "#f4f4f4"
GRAYC = "#6e6e6e"


def water_molecule(cx, cy, scale=1.0):
    s = circle(cx, cy, 16 * scale, OXRED, stroke="#a83c30", sw=1.4)
    s += circle(cx - 22 * scale, cy + 16 * scale, 9 * scale, WHITEH, stroke="#888", sw=1.2)
    s += circle(cx + 22 * scale, cy + 16 * scale, 9 * scale, WHITEH, stroke="#888", sw=1.2)
    return s


def fig_formula_anatomy():
    s = svg_open(940, 430)

    # ── рядок 1: H₂O по частинах ──
    s += text(170, 80, "H₂O", size=52, weight="bold")
    s += arrow(120, 95, 95, 140)
    s += text(95, 162, "символ:", size=13, fill="#1b4a82", weight="bold")
    s += text(95, 178, "ЯКІ атоми", size=13, fill="#1b4a82")
    s += arrow(163, 100, 163, 140)
    s += text(170, 162, "індекс: СКІЛЬКИ", size=13, fill="#2f7d4f", weight="bold")
    s += text(170, 178, "їх в одній молекулі", size=13, fill="#2f7d4f")
    s += text(330, 60, "читається:", size=12.5, fill="#888")
    s += text(330, 80, "«2 Гідрогени + 1 Оксиген»", size=14, fill="#444")
    s += water_molecule(330, 125)

    # ── рядок 2: CaCO₃ ──
    s += text(170, 270, "CaCO₃", size=40, weight="bold")
    s += text(420, 250, "1 Кальцій · 1 Карбон · 3 Оксигени", size=15, fill="#444")
    s += text(420, 274, "це крейда, вапняк і накип у чайнику — одна речовина", size=13, fill="#888")
    s += text(420, 296, "формула каже СКЛАД, але не спосіб з'єднання", size=13, fill="#a83c30")

    # ── рядок 3: коефіцієнт проти індексу ──
    s += '<rect x="96" y="330" width="34" height="48" rx="8" fill="none" stroke="#2f7d4f" stroke-width="2"/>\n'
    s += text(170, 368, "2H₂O", size=40, weight="bold")
    s += text(113, 400, "коефіцієнт:", size=13, fill="#2f7d4f", weight="bold")
    s += text(113, 416, "скільки МОЛЕКУЛ", size=13, fill="#2f7d4f")
    s += water_molecule(300, 360, scale=0.85)
    s += water_molecule(380, 360, scale=0.85)
    s += text(620, 355, "індекс — начинка «слова»,", size=14, fill="#555")
    s += text(620, 377, "коефіцієнт — кількість «слів»", size=14, fill="#555")

    s += "</svg>\n"
    (IMG / "fig-2-2-1-1-formula-anatomy.svg").write_text(s, encoding="utf-8")


DARKC = "#4a4a4a"


def hand_line(x1, y1, x2, y2):
    return '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#777" stroke-width="2.4"/>\n' % (x1, y1, x2, y2)


def fig_valence_hands():
    s = svg_open(960, 380)

    # ── зліва: збираємо воду з «рук» ──
    s += text(220, 36, "вода: дві руки Оксигену + два однорукі Гідрогени", size=14.5, weight="bold")
    # деталі до збирання
    s += circle(90, 120, 20, OXRED, stroke="#a83c30", sw=1.4)
    s += text(90, 126, "O", size=14, fill="white", weight="bold")
    s += hand_line(76, 136, 60, 158)
    s += hand_line(104, 136, 120, 158)
    s += text(90, 185, "2 руки", size=12, fill="#a83c30")
    s += circle(190, 130, 12, WHITEH, stroke="#888", sw=1.2)
    s += text(190, 135, "H", size=11, weight="bold")
    s += hand_line(190, 142, 190, 162)
    s += circle(250, 130, 12, WHITEH, stroke="#888", sw=1.2)
    s += text(250, 135, "H", size=11, weight="bold")
    s += hand_line(250, 142, 250, 162)
    s += text(220, 185, "по 1 руці", size=12, fill="#666")
    s += arrow(300, 130, 350, 130, color="#444", w=1.8)
    # зібрана молекула: всі руки зайняті
    s += circle(430, 110, 20, OXRED, stroke="#a83c30", sw=1.4)
    s += text(430, 116, "O", size=14, fill="white", weight="bold")
    s += hand_line(416, 126, 398, 148)
    s += hand_line(444, 126, 462, 148)
    s += circle(392, 158, 12, WHITEH, stroke="#888", sw=1.2)
    s += text(392, 163, "H", size=11, weight="bold")
    s += circle(468, 158, 12, WHITEH, stroke="#888", sw=1.2)
    s += text(468, 163, "H", size=11, weight="bold")
    s += text(430, 205, "усі руки зайняті: H₂O", size=13, fill="#2f7d4f")

    # ── посередині: CO₂ — Карбон тримає кожен Оксиген двома руками ──
    s += text(430, 268, "Карбон чотирирукий: O ═ C ═ O", size=14.5, weight="bold")
    cx, cy = 430, 320
    s += circle(cx, cy, 18, DARKC, stroke="#222", sw=1.4)
    s += text(cx, cy + 6, "C", size=13, fill="white", weight="bold")
    for dy in (-6, 6):
        s += hand_line(cx - 18, cy + dy, cx - 70, cy + dy)
        s += hand_line(cx + 18, cy + dy, cx + 70, cy + dy)
    s += circle(cx - 90, cy, 17, OXRED, stroke="#a83c30", sw=1.4)
    s += text(cx - 90, cy + 6, "O", size=13, fill="white", weight="bold")
    s += circle(cx + 90, cy, 17, OXRED, stroke="#a83c30", sw=1.4)
    s += text(cx + 90, cy + 6, "O", size=13, fill="white", weight="bold")

    # ── праворуч: пам'ятка валентностей ──
    s += '<rect x="660" y="70" width="240" height="250" rx="10" fill="#f7fafc" stroke="#b9c6cf"/>\n'
    s += text(780, 100, "скільки «рук» у кого", size=14.5, weight="bold")
    rows = (("Гідроген H", "1"), ("Хлор Cl", "1"), ("Оксиген O", "2"),
            ("Кальцій Ca", "2"), ("Карбон C", "4"))
    for i, (name, v) in enumerate(rows):
        yy = 135 + i * 34
        s += text(685, yy, name, size=13.5, anchor="start", fill="#444")
        s += text(875, yy, v, size=14.5, anchor="end", weight="bold", fill="#1b4a82")
    s += text(780, 308, "у деяких металів буває по-різному", size=11.5, fill="#888")

    s += "</svg>\n"
    (IMG / "fig-2-2-2-1-valence-hands.svg").write_text(s, encoding="utf-8")


def pack(s, x, y, w, title, mass):
    s += '<rect x="%d" y="%d" width="%d" height="110" rx="10" fill="#fdf6ec" stroke="#cfa86a" stroke-width="1.6"/>\n' % (x, y, w)
    s += text(x + w / 2, y + 30, title, size=15, weight="bold", fill="#7a5a1e")
    s += text(x + w / 2, y + 58, mass, size=17, weight="bold", fill="#222")
    s += text(x + w / 2, y + 86, "усередині 6×10²³ штук", size=11.5, fill="#888")
    return s


def fig_mole_packs():
    s = svg_open(960, 470)

    # ── зверху: число з таблиці = грамів у пачці ──
    s += text(480, 34, "моль — це «пачка» на 6×10²³ частинок", size=16, weight="bold")
    s += '<rect x="60" y="70" width="84" height="92" rx="6" fill="#f1f7fb" stroke="#9fb4c0" stroke-width="1.4"/>\n'
    s += text(72, 90, "8", size=11, anchor="start", fill="#777")
    s += text(102, 122, "O", size=24, weight="bold")
    s += text(102, 148, "16", size=13, fill="#555")
    s += arrow(150, 116, 230, 116, color="#b3541e", w=1.8)
    s += text(190, 100, "число з таблиці =", size=12, fill="#b3541e")
    s += text(190, 114, "грамів у пачці", size=12, fill="#b3541e")
    s = pack(s, 240, 62, 190, "1 моль Оксигену O", "16 г")
    s = pack(s, 460, 62, 190, "1 моль Гідрогену H", "1 г")
    s = pack(s, 680, 62, 220, "1 моль води H₂O", "1+1+16 = 18 г")

    # ── знизу: ланцюжок «грами → молі → штуки» ──
    s += text(480, 230, "склянка води: від грамів до штук", size=15.5, weight="bold")
    s += '<rect x="80" y="260" width="170" height="84" rx="10" fill="#eef4f9" stroke="#9fb4c0"/>\n'
    s += text(165, 296, "склянка води", size=13.5, fill="#444")
    s += text(165, 322, "180 г", size=18, weight="bold")
    s += arrow(258, 302, 348, 302, color="#444", w=1.8)
    s += text(303, 288, "÷ 18 г/моль", size=12.5, fill="#666")
    s += '<rect x="355" y="260" width="150" height="84" rx="10" fill="#eef4f9" stroke="#9fb4c0"/>\n'
    s += text(430, 302, "10 моль", size=18, weight="bold")
    s += arrow(513, 302, 603, 302, color="#444", w=1.8)
    s += text(558, 288, "× 6×10²³", size=12.5, fill="#666")
    s += '<rect x="610" y="260" width="260" height="84" rx="10" fill="#eef4f9" stroke="#9fb4c0"/>\n'
    s += text(740, 296, "молекул у склянці", size=13.5, fill="#444")
    s += text(740, 322, "6×10²⁴", size=19, weight="bold", fill="#a83c30")

    s += text(480, 395, "якби всі люди Землі лічили по молекулі щосекунди —", size=13.5, fill="#555")
    s += text(480, 415, "на одну склянку пішло б близько 24 мільйонів років", size=13.5, fill="#555")

    s += "</svg>\n"
    (IMG / "fig-2-2-3-1-mole-packs.svg").write_text(s, encoding="utf-8")


if __name__ == "__main__":
    fig_formula_anatomy()
    fig_valence_hands()
    fig_mole_packs()
    print("OK:", *(p.name for p in sorted(IMG.glob("*.svg"))))

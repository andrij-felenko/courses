# -*- coding: utf-8 -*-
"""Фігури до вставки «Резервне живлення на суперконденсаторі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def _diode(f, x, y, direction="right", color=INK):
    """Трикутник + риска діода. direction — куди показує трикутник (анод→катод)."""
    if direction == "right":
        f.append('<path d="M %.1f,%.1f L %.1f,%.1f L %.1f,%.1f Z" fill="%s"/>'
                 % (x, y - 12, x, y + 12, x + 20, y, color))
        f.append(line(x + 20, y - 12, x + 20, y + 12, color=color, sw=2.6))


def fig_backup():
    """Схема підхоплення: діодне АБО (D1, D2) + зарядний резистор R + іоністор."""
    W, H = 820, 470
    f = []

    # ── верхня шина: джерело → D1 → схема ──
    f.append(circle(90, 150, 5, fill=INK, stroke=INK, sw=0))
    f.append(text(90, 134, "основне живлення 5 В", size=12, color=INK, anchor="start", bold=True))
    f.append(line(90, 150, 300, 150, color=INK, sw=2.4))
    _diode(f, 300, 150, "right", INK)
    f.append(text(310, 130, "D1 (Шотткі)", size=11, color=INK, bold=True))
    f.append(line(320, 150, 560, 150, color=INK, sw=2.4))
    f.append(circle(520, 150, 4, fill=INK, stroke=INK, sw=0))

    # навантаження
    f.append(rect(560, 118, 150, 64, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(635, 144, "навантаження", size=12, color=INK, bold=True))
    f.append(text(635, 162, "(годинник, логіка)", size=11, color=MUTED))
    # земля під навантаженням
    f.append(line(635, 182, 635, 210, color=INK, sw=2.2))
    f.append(line(619, 212, 651, 212, color=INK, sw=2.4))
    f.append(line(625, 218, 645, 218, color=INK, sw=2.4))
    f.append(line(630, 224, 640, 224, color=INK, sw=2.4))

    # ── гілка заряду: вузол → R → іоністор ──
    f.append(circle(160, 150, 4, fill=INK, stroke=INK, sw=0))
    f.append(line(160, 150, 160, 280, color=INK, sw=2.2))
    # резистор (зиґзаґ)
    f.append('<path d="M 160,280 L 170,271 L 190,289 L 210,271 L 230,289 L 250,271 L 270,289 L 280,280" '
             'fill="none" stroke="%s" stroke-width="2"/>' % INK)
    f.append(text(220, 264, "R заряду", size=14, color=INK, bold=True))
    f.append(line(280, 280, 330, 280, color=INK, sw=2.2))
    f.append(circle(330, 280, 4, fill=INK, stroke=INK, sw=0))

    # іоністор (дві товсті риски) + земля
    f.append(line(330, 280, 330, 320, color=INK, sw=2.2))
    f.append(line(310, 320, 350, 320, color=INK, sw=2.6))
    f.append(line(310, 331, 350, 331, color=INK, sw=2.6))
    f.append(text(360, 332, "іоністор", size=12, color=FIELD, anchor="start", bold=True))
    f.append(line(330, 331, 330, 364, color=INK, sw=2.2))
    f.append(line(314, 366, 346, 366, color=INK, sw=2.4))
    f.append(line(320, 372, 340, 372, color=INK, sw=2.4))
    f.append(line(325, 378, 335, 378, color=INK, sw=2.4))

    # ── гілка розряду: іоністор → D2 → шина навантаження ──
    f.append(line(330, 280, 430, 280, color=INK, sw=2.2))
    _diode(f, 430, 280, "right", INK)
    f.append(text(440, 260, "D2 (Шотткі)", size=11, color=INK, bold=True))
    f.append(line(450, 280, 520, 280, color=INK, sw=2.2))
    f.append(line(520, 280, 520, 150, color=INK, sw=2.2))

    # стрілки-режими
    f.append(arrow(120, 168, 270, 168, color=FIELD, sw=2))
    f.append(text(195, 188, "мережа є: живить через D1,", size=11, color="#1f6e33", bold=True))
    f.append(text(195, 204, "іоністор доряджається через R", size=11, color="#1f6e33", bold=True))
    f.append(arrow(360, 240, 500, 240, color=POS, sw=2))
    f.append(text(430, 228, "мережі нема: підхоплення через D2", size=11, color="#9a2b22", bold=True))

    f.append(text(W / 2, 430,
                  "R обмежує кидок у розряджений іоністор; D1 не пускає запас назад у джерело; D2 оминає R при розряді.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "backup-circuit.svg"), W, H, *f,
           title="Схема резерву: діодне «АБО» плюс зарядний резистор")


def fig_two_modes():
    """Та сама комірка — два режими розряду: пологий годинник vs сходинка ESR + швидкий спад."""
    W, H = 820, 440
    f = []

    f.append(text(W / 2, 56,
                  "мікроампери годинника тягнуться добами; сотні міліампер «подиху» — лічені секунди",
                  size=12, color=MUTED, italic=True))

    # ── лівий графік: годинник ──
    f.append(arrow(80, 340, 80, 126, color=INK, sw=2))
    f.append(arrow(80, 340, 384, 340, color=INK, sw=2))
    f.append(text(388, 344, "доби", size=13, color=INK, anchor="start", bold=True))
    f.append(text(76, 118, "V", size=13, color=INK, bold=True))
    f.append(line(80, 256, 370, 256, color=MUTED, sw=1.4, dash="6 5"))
    f.append(line(80, 164, 370, 256, color=FIELD, sw=2.8))
    f.append(text(225, 184, "годинник: I = мікроампери", size=12, color="#1f6e33", bold=True))
    f.append(text(225, 201, "пологий спад, дні-тижні", size=11, color=MUTED))
    f.append(text(84, 248, "мінімум схеми", size=10, color=MUTED, anchor="start"))

    # ── правий графік: останній подих ──
    f.append(arrow(470, 340, 470, 126, color=INK, sw=2))
    f.append(arrow(470, 340, 774, 340, color=INK, sw=2))
    f.append(text(778, 344, "секунди", size=13, color=INK, anchor="start", bold=True))
    f.append(text(466, 118, "V", size=13, color=INK, bold=True))
    f.append(line(470, 256, 760, 256, color=MUTED, sw=1.4, dash="6 5"))
    # сходинка ESR·I, тоді швидкий спад
    f.append(line(470, 164, 476, 192, color=POS, sw=2.8))
    f.append(line(476, 192, 650, 256, color=POS, sw=2.8))
    f.append(line(650, 256, 650, 340, color=MUTED, sw=1.2, dash="4 4"))
    f.append(arrow(528, 156, 479, 184, color=MUTED, sw=1.4))
    f.append(text(531, 150, "сходинка ESR·I у мить підхоплення", size=11, color="#9a2b22", anchor="start", bold=True))
    f.append(text(620, 286, "«останній подих»:", size=12, color="#9a2b22", bold=True))
    f.append(text(620, 303, "I = сотні мА, лічені секунди", size=11, color=MUTED))

    f.append(text(W / 2, 414,
                  "«монетка» з ESR у десятки ом сотень міліампер не віддасть — для сили беруть низько-ESR серії.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "two-modes.svg"), W, H, *f,
           title="Та сама комірка — два різні режими розряду")


if __name__ == "__main__":
    fig_backup()
    fig_two_modes()
    print("OK: backup-circuit.svg, two-modes.svg")

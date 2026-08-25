# -*- coding: utf-8 -*-
"""Фігури до теми «LDO-стабілізатор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Що навколо чипа: вхідний/вихідний конденсатори і мідь під корпусом ──────
def fig_module():
    W, H = 700, 340
    f = [text(W / 2, 28, "Навколо чипа: два конденсатори й мідь під корпусом",
              size=16, bold=True)]

    # мідний поліґон-тепловідвід під чипом
    f.append(rect(286, 104, 128, 100, fill="#f4dcc4", stroke="#b5732e", sw=1.3, rx=8))
    f.append(text(350, 198, "мідь — тепловідвід", size=9, color="#b5732e"))

    # сам чип
    f.append(rect(300, 116, 100, 60, fill="#eef2f7", stroke="#7f93a8", sw=1.8, rx=6))
    f.append(text(350, 142, "LDO-чип", size=12, color=INK, bold=True))
    f.append(text(350, 161, "весь стабілізатор", size=9, color=MUTED))

    # вхід Vin
    f.append(line(208, 150, 300, 150, color=POS, sw=2))
    f.append(text(202, 154, "Vвх", size=11, color=POS, anchor="end", bold=True))
    f.append(text(294, 136, "IN", size=9, color=POS, anchor="end"))

    # вихід Vout
    f.append(line(400, 150, 540, 150, color=FIELD, sw=2))
    f.append(text(548, 154, "Vвих", size=11, color=FIELD, anchor="start", bold=True))
    f.append(text(406, 136, "OUT", size=9, color=FIELD, anchor="start"))

    # земля
    f.append(line(350, 176, 350, 276, color=INK, sw=1.6))
    f.append(line(178, 276, 562, 276, color=INK, sw=1.6))
    f.append(text(172, 280, "GND", size=9, color=INK, anchor="end"))

    # вхідний конденсатор
    f.append(circle(250, 150, 3, fill=INK, stroke=INK, sw=2))
    f.append(line(250, 150, 250, 214, color=INK, sw=1.6))
    f.append(line(238, 214, 262, 214, color=INK, sw=2.6))
    f.append(line(238, 222, 262, 222, color=INK, sw=2.6))
    f.append(line(250, 222, 250, 276, color=INK, sw=1.6))
    f.append(text(230, 204, "Cвх", size=10, color=INK, anchor="end", bold=True))

    # вихідний конденсатор
    f.append(circle(470, 150, 3, fill=INK, stroke=INK, sw=2))
    f.append(line(470, 150, 470, 214, color=INK, sw=1.6))
    f.append(line(458, 214, 482, 214, color=INK, sw=2.6))
    f.append(line(458, 222, 482, 222, color=INK, sw=2.6))
    f.append(line(470, 222, 470, 276, color=INK, sw=1.6))
    f.append(text(490, 206, "Cвих", size=10, color=POS, anchor="start", bold=True))
    f.append(text(490, 221, "(стійкість)", size=9, color=POS, anchor="start", bold=True))

    f.append(text(W / 2, 322,
                  "Усе складне — у кремнії. Зовні лишаються вхідний і вихідний конденсатори та мідь під корпусом",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "module.svg"), W, H, *f)


# ── 2. Фіксований проти регульованого: де сидить дільник напруги ───────────────
def fig_fixed_vs_adj():
    W, H = 720, 300
    f = [text(W / 2, 26, "Два класи: фіксований і регульований", size=16, bold=True)]

    # ── ліва панель: фіксований ──
    f.append(rect(30, 50, 320, 214, fill=BG, stroke="#c9d3dc", sw=1.4))
    f.append(text(190, 44, "фіксований (AMS1117-клас)", size=12, color=INK, bold=True))
    f.append(rect(110, 104, 160, 64, fill="#eef2f7", stroke="#7f93a8", sw=1.6))
    f.append(text(190, 130, "вихід 3.3 чи 5 В", size=11, color=INK, bold=True))
    f.append(text(190, 150, "дільник — усередині", size=9.5, color=MUTED))
    f.append(text(190, 196, "3 ноги: IN · GND · OUT", size=10, color=INK, bold=True))
    f.append(text(190, 218, "увімкнув — і працює", size=9.5, color=MUTED))
    f.append(text(190, 244, "dropout ~1.1 В, спокій ~5 мА", size=9.5, color=POS))

    # ── права панель: регульований ──
    f.append(rect(370, 50, 320, 214, fill=BG, stroke="#c9d3dc", sw=1.4))
    f.append(text(530, 44, "регульований (LM317-клас)", size=12, color=INK, bold=True))
    f.append(rect(420, 100, 130, 52, fill="#eef2f7", stroke="#7f93a8", sw=1.6))
    f.append(text(485, 130, "ADJ-чип", size=11, color=INK, bold=True))

    # вихід і верхнє плече дільника
    f.append(line(550, 126, 590, 126, color=FIELD, sw=2))
    f.append(text(596, 130, "Vвих", size=9.5, color=FIELD, anchor="start", bold=True))
    f.append(line(590, 126, 590, 150, color=INK, sw=1.5))
    f.append(rect(578, 150, 24, 24, fill=BG, stroke=INK, sw=1.4, rx=3))
    f.append(text(610, 167, "R1", size=10, color=INK, anchor="start", bold=True))
    f.append(line(590, 174, 590, 188, color=INK, sw=1.5))
    f.append(circle(590, 188, 3, fill=INK, stroke=INK, sw=2))

    # вузол ADJ
    f.append(line(485, 188, 590, 188, color=INK, sw=1.4))
    f.append(line(485, 152, 485, 188, color=INK, sw=1.4))
    f.append(text(520, 184, "ADJ", size=9, color=INK))

    # нижнє плече
    f.append(rect(578, 192, 24, 24, fill=BG, stroke=INK, sw=1.4, rx=3))
    f.append(text(610, 209, "R2", size=10, color=INK, anchor="start", bold=True))
    f.append(line(590, 216, 590, 236, color=INK, sw=1.5))
    f.append(text(590, 251, "GND", size=9, color=INK))
    f.append(text(500, 234, "Vвих задають два резистори", size=10, color=INK, bold=True))

    f.append(text(W / 2, 286,
                  "Фіксований дає готову напругу; регульований лишає дільник назовні — Vвих добираєш сам",
                  size=11, color=MUTED, italic=True))
    return render(os.path.join(IMG, "fixed-vs-adj.svg"), W, H, *f)


if __name__ == "__main__":
    fig_module()
    fig_fixed_vs_adj()
    print("OK: figures ->", IMG)

# -*- coding: utf-8 -*-
"""Фігури до теми «Практикум даташитів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED, GRN, BLU = POS, FIELD, NEG


def _legend_row(f, cx, y, color, label):
    f.append(rect(cx, y - 7, 16, 13, fill=color, stroke=color, sw=1, rx=2))
    f.append(text(cx + 22, y + 4, label, size=10.5, color=MUTED, anchor="start"))


def _row(f, x, y, w, name, color, fill, expl, val):
    """Один рядок-параметр: кольорова плашка з назвою + пояснення + значення."""
    f.append(rect(x, y, 120, 40, fill=fill, stroke=color, sw=1.6, rx=6))
    f.append(text(x + 60, y + 18, name, size=12, color=color, bold=True))
    fs = fit_font(expl, 200, 10)
    f.append(text(x + 132, y + 16, expl, size=fs, color=INK, anchor="start"))
    f.append(text(x + 132, y + 32, val, size=10.5, color=MUTED, anchor="start"))


# ── 1. Даташит діода: критичні рядки ─────────────────────────────────────────
def fig_diode():
    W, H = 720, 300
    f = [text(W / 2, 28, "Даташит діода: рядки, що вирішують вибір", size=16, bold=True)]
    _legend_row(f, 60, 50, RED, "абсолютний максимум")
    _legend_row(f, 300, 50, GRN, "робоча межа")
    _legend_row(f, 520, 50, BLU, "параметр")
    x, y, dy = 50, 72, 44
    _row(f, x, y + 0 * dy, W, "VRRM", RED, "#fdecea",
         "найбільша зворотна напруга до пробою", "беруть із запасом ≥ 2× до шини")
    _row(f, x, y + 1 * dy, W, "IFSM", RED, "#fdecea",
         "піковий одиничний струм-кидок", "важить при ввімкненні на ємність")
    _row(f, x, y + 2 * dy, W, "IF(av)", GRN, "#eafaf1",
         "тривалий прямий струм без перегріву", "має перекривати робочий струм")
    _row(f, x, y + 3 * dy, W, "VF", BLU, "#eaf0fd",
         "пряме падіння при заданому струмі", "втрати й нагрів P ≈ VF·IF, колонка max")
    _row(f, x, y + 4 * dy, W, "trr", BLU, "#eaf0fd",
         "час відновлення (швидкість)", "вирішальний лише у швидкій комутації")
    render(os.path.join(IMG, "diode.svg"), W, H, *f)


# ── 2. Даташит MOSFET: критичні рядки + дві пастки ───────────────────────────
def fig_mosfet():
    W, H = 720, 330
    f = [text(W / 2, 28, "Даташит MOSFET: рядки керування й силові межі", size=16, bold=True)]
    _legend_row(f, 60, 50, RED, "абсолютний максимум")
    _legend_row(f, 300, 50, GRN, "робоча межа")
    _legend_row(f, 520, 50, BLU, "параметр")
    x, y, dy = 50, 72, 38
    _row(f, x, y + 0 * dy, W, "VDS", RED, "#fdecea",
         "макс. напруга стік–витік (блокування)", "запас до напруги шини")
    _row(f, x, y + 1 * dy, W, "VGS", RED, "#fdecea",
         "макс. напруга затвора, часто ±20 В", "перевищиш — пробій ізолятора")
    _row(f, x, y + 2 * dy, W, "ID", GRN, "#eafaf1",
         "тривалий струм стоку", "прив'язаний до температури кристала")
    _row(f, x, y + 3 * dy, W, "Rds(on)", BLU, "#eaf0fd",
         "опір відкритого каналу, втрати I²·R", "дають за великого VGS і холодним")
    _row(f, x, y + 4 * dy, W, "VGS(th)", BLU, "#eaf0fd",
         "поріг: канал лише починає текти", "це НЕ напруга повного відкриття")
    _row(f, x, y + 5 * dy, W, "Qg", BLU, "#eaf0fd",
         "заряд затвора на одне відкриття", "задає драйвер і втрати перемикання")
    render(os.path.join(IMG, "mosfet.svg"), W, H, *f)


# ── 3. Даташит ОП: критичний рядок залежить від задачі ───────────────────────
def fig_opamp():
    W, H = 720, 340
    f = [text(W / 2, 28, "Даташит ОП: який рядок критичний — диктує задача", size=16, bold=True)]

    # верхня плашка: спільний для всіх перший крок
    b, _, _ = textbox(W / 2, 64, "Спершу для будь-якої задачі — діапазон живлення: чи влізе ОП у твою шину",
                      size=12, fill=FILL, stroke=LINE)
    f.append(b)

    # дві колонки задач
    colw, top = 320, 96
    lx, rx = 40, 40 + colw + 20
    f.append(rect(lx, top, colw, 196, fill="#eafaf1", stroke=GRN, sw=1.8, rx=10))
    f.append(rect(rx, top, colw, 196, fill="#eaf0fd", stroke=BLU, sw=1.8, rx=10))
    f.append(text(lx + colw / 2, top + 24, "Точний вимірювач (постійний сигнал)", size=12.5, bold=True, color=GRN))
    f.append(text(rx + colw / 2, top + 24, "Швидкий сигнал (звук, відео)", size=12.5, bold=True, color=BLU))

    left = [("Vos", "зсув — паразитна похибка на вході"),
            ("Ib", "вхідний струм — б'є по високоомному"),
            ("дрейф", "як зсув повзе з температурою")]
    right = [("GBW", "добуток підсилення на смугу"),
             ("SR", "швидкість наростання виходу"),
             ("на спокої", "Vos і Ib майже байдужі")]
    for i, (nm, ex) in enumerate(left):
        yy = top + 50 + i * 44
        f.append(rect(lx + 16, yy, 78, 32, fill=BG, stroke=GRN, sw=1.4, rx=5))
        f.append(text(lx + 55, yy + 21, nm, size=12, color=GRN, bold=True))
        fs = fit_font(ex, colw - 112, 10, min_size=9)
        f.append(text(lx + 104, yy + 20, ex, size=fs, color=INK, anchor="start"))
    for i, (nm, ex) in enumerate(right):
        yy = top + 50 + i * 44
        f.append(rect(rx + 16, yy, 78, 32, fill=BG, stroke=BLU, sw=1.4, rx=5))
        f.append(text(rx + 55, yy + 21, nm, size=12, color=BLU, bold=True))
        fs = fit_font(ex, colw - 112, 10, min_size=9)
        f.append(text(rx + 104, yy + 20, ex, size=fs, color=INK, anchor="start"))

    f.append(text(W / 2, top + 222, "RRIO — розмах від рейки до рейки: критичний на низькій напрузі живлення",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "opamp.svg"), W, H, *f)


# ── 4. Єдиний маршрут читання даташита ───────────────────────────────────────
def fig_workflow():
    W, H = 720, 300
    f = [text(W / 2, 28, "Один маршрут для діода, MOSFET чи ОП", size=16, bold=True)]
    steps = [
        ("1", "Перша сторінка", "це взагалі потрібний клас приладу?", "#fdf1dc"),
        ("2", "Absolute Maximum", "мої напруги, струми, піки не вб'ють?", "#fdecea"),
        ("3", "Recommended", "робоча точка всередині, із запасом?", "#fff3e0"),
        ("4", "Electrical Char.", "критичний параметр — по гарантованому краю", "#eafaf1"),
        ("5", "Графіки", "як він попливе саме в моїх умовах?", "#eaf0fd"),
        ("6", "Дрібний шрифт", "виноски, умови тестів, errata", "#f3e9f3"),
    ]
    x, y0, bh, gap = 50, 54, 32, 6
    for i, (n, name, q, fill) in enumerate(steps):
        y = y0 + i * (bh + gap)
        f.append(rect(x, y, 34, bh, fill=BG, stroke="#9bb0c2", sw=1.4, rx=6))
        f.append(text(x + 17, y + bh / 2 + 5, n, size=14, color=INK, bold=True))
        f.append(rect(x + 40, y, 200, bh, fill=fill, stroke="#9bb0c2", sw=1.3, rx=6))
        f.append(text(x + 52, y + bh / 2 + 4, name, size=11.5, color=INK, anchor="start", bold=True))
        f.append(rect(x + 248, y, 372, bh, fill=BG, stroke="#c9d3dc", sw=1.2, rx=6))
        fs = fit_font(q, 348, 11)
        f.append(text(x + 262, y + bh / 2 + 4, q, size=fs, color=INK, anchor="start"))
        if i < len(steps) - 1:
            f.append(line(x + 17, y + bh, x + 17, y + bh + gap, color=MUTED, sw=1.4))
    f.append(text(W / 2, y0 + 6 * (bh + gap) + 8,
                  "Змінюється лише, який параметр критичний на кроці 4.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "workflow.svg"), W, H, *f)


if __name__ == "__main__":
    fig_diode()
    fig_mosfet()
    fig_opamp()
    fig_workflow()
    print("OK: 4 figures ->", IMG)

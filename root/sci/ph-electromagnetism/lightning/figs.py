# -*- coding: utf-8 -*-
"""Фігури до вставки «Іскровий проміжок і GDT».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

import math


# ── Фігура 1: вольт-амперна крива GDT — обрив напруги при пробої ───────────────
def fig_crowbar():
    W, H = 820, 480
    f = [text(W / 2, 28, "Що бачить лінія: GDT тримає напругу, аж поки не «впаде» в дугу",
              size=15, bold=True)]

    ox, oy = 95, 400          # початок осей (низ-ліво)
    top = 70                  # верх осі напруги
    right = ox + 620          # права межа осі струму

    # осі
    f.append(line(ox, oy, right, oy, color=MUTED, sw=1.5))            # струм →
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.5))             # напруга ↑
    f.append(text(right, oy + 26, "струм крізь розрядник →", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 12, top + 4, "U", size=13, color=MUTED, anchor="end", italic=True))
    f.append(text(ox - 10, oy + 4, "0", size=11, color=MUTED, anchor="end"))

    # рівень напруги пробою (sparkover) і рівень дуги (arc)
    y_spark = 110
    y_arc = 340
    f.append(line(ox, y_spark, right, y_spark, color=MUTED, sw=1.0, dash="4 5"))
    f.append(text(right - 4, y_spark - 8, "напруга пробою ≈ 90…600 В", size=10.5, color=MUTED, anchor="end"))
    f.append(line(ox, y_arc, right, y_arc, color=MUTED, sw=1.0, dash="4 5"))
    f.append(text(right - 4, y_arc - 8, "напруга дуги ≈ 10…35 В", size=10.5, color=MUTED, anchor="end"))

    # 1) високий опір: майже нуль струму, напруга вільно росте знизу вгору
    f.append(line(ox, oy, ox + 3, y_spark, color=NEG, sw=3.2))
    # стрілка-підказка росту напруги
    f.append(text(ox + 70, 250, "вимкнено:", size=11, color=NEG, anchor="start", bold=True))
    f.append(text(ox + 70, 266, ">1 ГОм, майже", size=10.5, color=NEG, anchor="start"))
    f.append(text(ox + 70, 281, "нуль струму", size=10.5, color=NEG, anchor="start"))

    # 2) пробій: різкий обрив напруги вниз (від'ємний нахил) — стрілкою
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="3.4" '
             'marker-end="url(#arrow)"/>' % (ox + 3, y_spark + 6, ox + 120, y_arc - 8, POS))
    f.append(text(ox + 150, 215, "пробій:", size=11, color=POS, anchor="start", bold=True))
    f.append(text(ox + 150, 231, "газ іонізується,", size=10.5, color=POS, anchor="start"))
    f.append(text(ox + 150, 246, "напруга обвалюється", size=10.5, color=POS, anchor="start"))

    # 3) дуга: майже горизонтальна полиця — крізь неї тече весь сплеск
    f.append(line(ox + 120, y_arc, right - 30, y_arc + 6, color=POS, sw=3.4))
    f.append(text(right - 30, y_arc + 26, "увімкнено: майже коротке,", size=10.5, color=POS, anchor="end"))
    f.append(text(right - 30, y_arc + 41, "сплеск стікає на землю", size=10.5, color=POS, anchor="end"))

    # підпис «від'ємний опір» біля спадної ділянки
    f.append(text(ox + 8, 150, "від'ємний нахил", size=10, color=MUTED, anchor="start", italic=True))

    return render(os.path.join(IMG, "gdt-crowbar.svg"), W, H, *f)


# ── Фігура 2: каскад захисту — грубий GDT, розв'язка, тонкий TVS ───────────────
def fig_cascade():
    W, H = 860, 430
    f = [text(W / 2, 28, "Каскад: GDT приймає удар, розв'язка створює різницю, TVS дочищає",
              size=15, bold=True)]

    yline = 150               # верхній (сигнальний/гарячий) провід
    ygnd = 330                # земля
    xin = 70                  # вхід (з вулиці)
    xout = 800                # вихід (до апаратури)

    # провід лінії
    f.append(line(xin, yline, xout, yline, color=INK, sw=2.2))
    f.append(line(xin, ygnd, xout, ygnd, color=INK, sw=2.2))
    f.append(text(xin - 4, yline - 12, "з лінії/антени", size=11, color=MUTED, anchor="start", bold=True))
    f.append(text(xin - 4, yline + 22, "(удар приходить сюди)", size=10, color=MUTED, anchor="start"))
    f.append(text(xout + 4, yline - 12, "до апаратури", size=11, color=MUTED, anchor="end", bold=True))
    # символ землі
    f.append(line(xout - 30, ygnd, xout - 30, ygnd + 16, color=INK, sw=2))
    for i, wdt in enumerate((24, 15, 7)):
        f.append(line(xout - 30 - wdt / 2, ygnd + 16 + i * 5, xout - 30 + wdt / 2, ygnd + 16 + i * 5, color=INK, sw=2))
    f.append(text(xout - 30, ygnd + 48, "земля", size=10, color=MUTED))

    # 1) GDT — груба ступінь, перший вузол між лінією і землею
    x1 = 230
    f.append(line(x1, yline, x1, ygnd, color=POS, sw=2.2))
    gb = rect(x1 - 30, yline + 48, 60, 36, fill="#fdecea", stroke=POS, sw=2)
    f.append(gb)
    f.append(text(x1, yline + 71, "GDT", size=13, color=POS, bold=True))
    f.append(text(x1, yline - 16, "груба ступінь", size=11, color=POS, bold=True))
    f.append(text(x1, ygnd + 26, "10 кА, але пізно й грубо", size=10, color=MUTED))

    # 2) розв'язка — послідовний R/L у проводі лінії
    x2 = 470
    f.append(rect(x2 - 42, yline - 13, 84, 26, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(x2, yline + 5, "R / L", size=12, color=INK, bold=True))
    f.append(text(x2, yline - 26, "розв'язка", size=11, color=INK, bold=True))
    f.append(text(x2, yline + 40, "тримає різницю напруг,", size=10, color=MUTED))
    f.append(text(x2, yline + 55, "поки GDT ще спить", size=10, color=MUTED))

    # 3) TVS — тонка швидка ступінь біля апаратури
    x3 = 690
    f.append(line(x3, yline, x3, ygnd, color=FIELD, sw=2.2))
    # символ діода-обмежувача (трикутник + риска)
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#eafaf0" stroke="%s" stroke-width="2"/>'
             % (x3 - 14, yline + 52, x3 + 14, yline + 52, x3, yline + 78, FIELD))
    f.append(line(x3 - 16, yline + 78, x3 + 16, yline + 78, color=FIELD, sw=2.4))
    f.append(text(x3, yline - 16, "тонка ступінь", size=11, color=FIELD, bold=True))
    f.append(text(x3, ygnd + 26, "швидкий TVS, низький поріг", size=10, color=MUTED))

    # порядок спрацювання — підпис унизу
    f.append(text(W / 2, H - 18,
                  "Послідовність у часі: спершу спрацьовує швидкий TVS (тримає кидок сам), "
                  "напруга на ньому росте на R/L → GDT пробиває й бере на себе кілоампери.",
                  size=10.5, color=MUTED))

    return render(os.path.join(IMG, "protection-cascade.svg"), W, H, *f)


if __name__ == "__main__":
    fig_crowbar()
    fig_cascade()
    print("ok: gdt-crowbar.svg, protection-cascade.svg")

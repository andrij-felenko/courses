# -*- coding: utf-8 -*-
"""Фігури до теми «Диференціальна сигналізація LVDS».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_currentloop():
    """Струмова петля: джерело 3.5 мА, пара проводів, 100 Ом + приймач.
    Показує, що біт — це НАПРЯМОК струму через резистор, а не рівень напруги."""
    W, H = 720, 380
    p = []
    p.append(text(W/2, 28, "Струмова петля LVDS: 3.5 мА крутиться колом", size=17, bold=True))

    # Драйвер (ліворуч)
    dx, dy, dw, dh = 40, 90, 150, 200
    p.append(rect(dx, dy, dw, dh, fill="#eef4ff", stroke=NEG, sw=2))
    p.append(text(dx+dw/2, dy+24, "Драйвер", size=14, bold=True, color=NEG))
    p.append(text(dx+dw/2, dy+46, "джерело струму", size=12, color=MUTED))
    # символ джерела струму
    cxs, cys = dx+dw/2, dy+120
    p.append(circle(cxs, cys, 26, fill=BG, stroke=INK, sw=2))
    p.append(text(cxs, cys-4, "3.5", size=14, bold=True))
    p.append(text(cxs, cys+13, "мА", size=11, color=MUTED))
    # два ключі-стрілки, що перекидають струм
    p.append(text(dx+dw/2, dy+dh-14, "перемикач напрямку", size=11, color=MUTED))

    # Приймач (праворуч)
    rx, ry, rw, rh = 530, 90, 150, 200
    p.append(rect(rx, ry, rw, rh, fill="#eefaf0", stroke=FIELD, sw=2))
    p.append(text(rx+rw/2, ry+24, "Приймач", size=14, bold=True, color=FIELD))
    p.append(text(rx+rw/2, ry+46, "високий опір", size=12, color=MUTED))
    # резистор 100 Ом між входами
    resx = rx+rw/2
    p.append(line(resx, ry+70, resx, ry+150, color=INK, sw=2))
    p.append(rect(resx-16, ry+92, 32, 46, fill=BG, stroke=INK, sw=2))
    p.append(text(resx+40, ry+112, "100 Ом", size=13, bold=True))
    p.append(text(resx+40, ry+130, "350 мВ", size=12, color=POS))

    # Верхній провід D+ (струм туди)
    yTop = dy+80
    p.append(line(dx+dw, yTop, rx, yTop, color=POS, sw=3))
    p.append(text((dx+dw+rx)/2, yTop-10, "D+", size=13, bold=True, color=POS))
    p.append(arrow((dx+dw+rx)/2-16, yTop, (dx+dw+rx)/2+16, yTop, color=POS, sw=3))
    # з'єднання до резистора
    p.append(line(rx, yTop, resx, yTop, color=POS, sw=3))
    p.append(line(resx, yTop, resx, ry+70, color=POS, sw=3))
    p.append(line(dx+dw, yTop, cxs, yTop, color=POS, sw=3))
    p.append(line(cxs, yTop, cxs, cys-26, color=POS, sw=3))

    # Нижній провід D− (струм назад)
    yBot = dy+160
    p.append(line(rx, yBot, dx+dw, yBot, color=NEG, sw=3))
    p.append(text((dx+dw+rx)/2, yBot+22, "D−", size=13, bold=True, color=NEG))
    p.append(arrow((dx+dw+rx)/2+16, yBot, (dx+dw+rx)/2-16, yBot, color=NEG, sw=3))
    p.append(line(resx, ry+150, resx, yBot, color=NEG, sw=3))
    p.append(line(resx, yBot, rx, yBot, color=NEG, sw=3))
    p.append(line(dx+dw, yBot, cxs, yBot, color=NEG, sw=3))
    p.append(line(cxs, cys+26, cxs, yBot, color=NEG, sw=3))

    # підпис під низом
    p.append(text(W/2, H-16,
                  "Струм тече колом; біт — це НАПРЯМОК струму крізь резистор.",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'current-loop.svg'), W, H, *p)


def fig_common_mode():
    """Дві напруги навколо 1.2 В + завада, що додається до ОБОХ однаково,
    і різниця, де завада зникає. Показує, чому синфазний шум не заважає."""
    W, H = 720, 430
    p = []
    p.append(text(W/2, 28, "Завада б'є по обох лініях однаково — різниця її не бачить", size=16, bold=True))

    # осі
    x0, x1 = 90, 560
    # верхня панель: D+ і D−
    baseY = 150
    scale = 60        # px на 1 В (для наочності стиснуто умовно)
    cm = 1.2
    def yv(v):
        return baseY - (v-cm)*scale
    # рівень спільного режиму 1.2 В
    p.append(line(x0, yv(cm), x1, yv(cm), color=MUTED, sw=1, dash="4 4"))
    p.append(text(x1+8, yv(cm)+4, "1.2 В", size=12, color=MUTED))
    p.append(text(x1+8, yv(cm)+20, "спільн.", size=11, color=MUTED))

    # квадрати сигналу: D+ = 1.4/1.0, D- = дзеркально; додаємо горб-заваду посередині
    seg = (x1-x0)/6
    hiP, loP = 1.375, 1.025
    noise = 0.5   # синфазна завада, що піднімає ОБИДВІ лінії
    # D+ : hi, lo, hi (з завадою на середньому сегменті)
    def stepwave(hi, lo, color, label, ny):
        pts = []
        lv = [hi, lo, hi, lo, hi, lo]
        y_prev = None
        segX = x0
        parts = []
        for i, v in enumerate(lv):
            vv = v + (noise if 2 <= i <= 3 else 0)
            y = yv(vv)
            x_a = x0 + i*seg
            x_b = x0 + (i+1)*seg
            if y_prev is not None:
                parts.append(line(x_a, y_prev, x_a, y, color=color, sw=2.5))
            parts.append(line(x_a, y, x_b, y, color=color, sw=2.5))
            y_prev = y
        for s in parts:
            p.append(s)
        p.append(text(x0-10, yv(hi)+4, label, size=13, bold=True, color=color, anchor="end"))
    stepwave(hiP, loP, POS, "D+", 0)
    stepwave(loP, hiP, NEG, "D−", 0)  # дзеркальна

    # позначка зони завади
    zx0, zx1 = x0+2*seg, x0+4*seg
    p.append(rect(zx0, 60, zx1-zx0, 150, fill="#fff6e5", stroke="#e0a63a", sw=1.2, rx=4))
    p.append(text((zx0+zx1)/2, 78, "тут завада", size=12, bold=True, color="#b9791f"))
    p.append(text((zx0+zx1)/2, 96, "обидві лінії ↑", size=11, color="#b9791f"))

    # нижня панель: різниця D+ − D−
    base2 = 350
    scale2 = 55
    def yd(v):
        return base2 - v*scale2
    p.append(line(x0, yd(0), x1, yd(0), color=MUTED, sw=1, dash="4 4"))
    p.append(text(x1+8, yd(0)+4, "0", size=12, color=MUTED))
    p.append(text(x0-10, yd(0)+4, "D+ − D−", size=13, bold=True, anchor="end"))
    # різниця: +0.35 / -0.35, і в зоні завади вона НЕ змінюється
    lv = [1, -1, 1, -1, 1, -1]
    y_prev = None
    for i, s in enumerate(lv):
        vv = 0.35*s
        y = yd(vv)
        x_a = x0 + i*seg
        x_b = x0 + (i+1)*seg
        if y_prev is not None:
            p.append(line(x_a, y_prev, x_a, y, color=INK, sw=3))
        p.append(line(x_a, y, x_b, y, color=INK, sw=3))
        y_prev = y
    p.append(rect(zx0, base2-24, zx1-zx0, 48, fill="none", stroke="#e0a63a", sw=1.2, rx=4))
    p.append(text((zx0+zx1)/2, base2+42, "різниця чиста — завада зникла", size=12, bold=True, color=FIELD))

    p.append(text(W/2, H-14,
                  "Приймач слухає лише РІЗНИЦЮ, тож синфазна завада (та зсув землі) випадають.",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'common-mode.svg'), W, H, *p)


def fig_swing():
    """Крупний план: поріг ±100 мВ навколо нуля різниці й запас 350 мВ.
    Показує, наскільки далеко корисний сигнал від межі рішення."""
    W, H = 640, 340
    p = []
    p.append(text(W/2, 28, "Запас рішення: 350 мВ проти порога ±100 мВ", size=16, bold=True))
    cx = W/2
    axX = 150
    top, bot = 70, 280
    mid = (top+bot)/2
    scale = 0.30   # px на мВ
    def y(mv):
        return mid - mv*scale
    # вісь
    p.append(line(axX, top, axX, bot, color=INK, sw=1.5))
    p.append(text(axX-10, mid+4, "0", size=12, anchor="end", color=MUTED))
    # рівні
    for mv, lab, col in [(350, "+350 мВ  «1»", POS), (-350, "−350 мВ  «0»", NEG)]:
        p.append(line(axX, y(mv), axX+330, y(mv), color=col, sw=2.5))
        p.append(text(axX+336, y(mv)+4, lab, size=13, bold=True, color=col, anchor="start"))
    # смуга невизначеності ±100
    p.append(rect(axX, y(100), 330, y(-100)-y(100), fill="#f0f0f0", stroke="#bbb", sw=1, rx=3))
    p.append(text(axX+165, mid-2, "±100 мВ — сюди приймач не пускають", size=12, color="#555"))
    p.append(text(axX+165, mid+16, "(зона невизначеності)", size=11, color=MUTED))
    # стрілки запасу
    p.append(arrow(axX+300, y(100), axX+300, y(350), color=FIELD, sw=2))
    p.append(text(axX+312, (y(100)+y(350))/2, "запас", size=12, bold=True, color=FIELD, anchor="start"))
    p.append(text(W/2, H-16,
                  "Корисний сигнал у ~3.5 раза більший за поріг — рішення надійне.",
                  size=12, color=MUTED))
    render(os.path.join(OUT, 'swing-margin.svg'), W, H, *p)


if __name__ == '__main__':
    fig_currentloop()
    fig_common_mode()
    fig_swing()
    print("OK: 3 SVG у", OUT)

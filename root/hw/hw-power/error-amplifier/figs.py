# -*- coding: utf-8 -*-
"""Фігури до статті «Операційний підсилювач в контурі зворотного зв'язку»
(book/electronics/analog/error-amplifier).
Три фігури:
  loop.svg      — модель: контур регулювання (уставка → похибка → силовий вузол → вихід → давач)
  regulator.svg — приклад: лінійний стабілізатор (ОП-похибки, прохідний транзистор, дільник)
  correct.svg   — реакція: стрибок навантаження просів вихід → похибка зросла → ОП дотиснув → відновлення
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Контур регулювання: уставка → похибка → силовий вузол → вихід → давач ──
def fig_loop():
    W, H = 760, 360
    f = []
    f.append(text(W/2, 26, "Підсилювач похибки замикає контур регулювання", size=17, bold=True))

    # Вузол похибки (суматор): уставка «+», давач «−»
    sx, sy = 200, 150
    f.append(circle(sx, sy, 26, fill="#f4f6f8"))
    f.append(text(sx, sy+8, "Σ", size=20, bold=True, color=INK))
    f.append(text(sx-18, sy-14, "+", size=15, bold=True, color=POS))
    f.append(text(sx-19, sy+30, "−", size=15, bold=True, color=NEG))

    # Уставка (опорна) — входить ліворуч у «+»
    eb = textbox(80, sy, "уставка Vref", size=13, fill="#fdecea", stroke=POS)
    f.append(eb[0])
    f.append(arrow(80+eb[1]/2, sy, sx-26, sy, color=POS))

    # Підсилювач похибки (трикутник ОП) праворуч від суматора
    ax = 360
    f.append(arrow(sx+26, sy, ax-46, sy))
    f.append(text((sx+26+ax-46)/2, sy-12, "похибка ε", size=13, italic=True, color=MUTED))
    # трикутник
    tri = 'M %.0f %.0f L %.0f %.0f L %.0f %.0f Z' % (ax-46, sy-40, ax-46, sy+40, ax+46, sy)
    f.append('<path d="%s" fill="#eef2f7" stroke="%s" stroke-width="2"/>' % (tri, LINE))
    f.append(text(ax-14, sy+5, "ОП", size=15, bold=True))
    f.append(text(ax, sy+62, "підсилювач похибки", size=13, anchor="middle", color=INK))

    # Силовий вузол (керований елемент)
    px, py = 560, 150
    pb = fitbox(px-60, py-32, 120, 64, "силовий\nелемент", size=14, fill="#eef7ef", stroke=FIELD, bold=True)
    f.append(pb)
    f.append(arrow(ax+46, sy, px-60, py))
    f.append(text((ax+46+px-60)/2, py-12, "керування", size=12, italic=True, color=MUTED))

    # Вихід праворуч
    f.append(arrow(px+60, py, 720, py))
    f.append(text(700, py-14, "вихід", size=14, bold=True))
    # точка відгалуження давача
    bx, by = 690, py
    f.append(circle(bx, by, 4, fill=INK, stroke=INK))

    # Давач (зворотний зв'язок) — вниз і назад у «−»
    fy = 300
    f.append(line(bx, by, bx, fy, color=NEG, sw=2))
    sb = textbox(420, fy, "давач: міряємо вихід", size=13, fill="#eaf0fd", stroke=NEG)
    f.append(sb[0])
    f.append(line(bx, fy, 420+sb[1]/2, fy, color=NEG, sw=2))
    f.append(arrow(420-sb[1]/2, fy, sx, fy, color=NEG))
    f.append(line(sx, fy, sx, sy+26, color=NEG, sw=2))
    f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s"/>' %
             (sx-5, sy+34, sx+5, sy+34, sx, sy+26, NEG))

    render(os.path.join(IMG, 'loop.svg'), W, H, *f)


# ── 2. Лінійний стабілізатор: ОП-похибки + прохідний транзистор + дільник ──
def fig_regulator():
    W, H = 740, 400
    f = []
    f.append(text(W/2, 26, "Стабілізатор напруги: ОП тримає вихід рівним опорі", size=17, bold=True))

    # Верхня шина живлення Vin
    rail = 70
    f.append(line(60, rail, 680, rail, color=INK, sw=2))
    f.append(text(60, rail-10, "Vin (нестабільна)", size=13, anchor="start", color=MUTED))

    # Прохідний транзистор (силовий) угорі праворуч
    tx, ty = 560, 130
    f.append(line(tx, rail, tx, ty-22))                      # колектор від шини
    f.append(circle(tx, ty, 24, fill="#eef7ef", stroke=FIELD, sw=2))
    f.append(text(tx, ty+5, "Q", size=15, bold=True, color=INK))
    f.append(text(tx+30, ty-6, "прохідний", size=12, anchor="start", color=MUTED))
    f.append(text(tx+30, ty+10, "транзистор", size=12, anchor="start", color=MUTED))

    # ОП похибки ліворуч
    ax, ay = 300, 175
    tri = 'M %.0f %.0f L %.0f %.0f L %.0f %.0f Z' % (ax-44, ay-42, ax-44, ay+42, ax+50, ay)
    f.append('<path d="%s" fill="#eef2f7" stroke="%s" stroke-width="2"/>' % (tri, LINE))
    f.append(text(ax-44+14, ay-20, "+", size=16, bold=True, color=POS))
    f.append(text(ax-44+14, ay+26, "−", size=16, bold=True, color=NEG))
    f.append(text(ax-2, ay+5, "ОП", size=13, bold=True))

    # Вихід ОП → база Q
    f.append(arrow(ax+50, ay, tx-24, ty+12))
    f.append(text((ax+50+tx-24)/2-6, (ay+ty)/2+30, "керує", size=12, italic=True, color=MUTED))

    # Вихідний вузол Vout (емітер транзистора вниз)
    vox = tx
    f.append(line(vox, ty+24, vox, 260))
    f.append(circle(vox, 260, 4, fill=INK, stroke=INK))
    f.append(line(vox, 260, 680, 260))
    f.append(text(685, 256, "Vout", size=14, bold=True, anchor="start"))

    # Навантаження праворуч
    f.append(line(680, 260, 680, 320))
    f.append(rect(670, 280, 20, 26, fill=FILL, stroke=LINE))
    f.append(text(700, 296, "наван-", size=11, anchor="start", color=MUTED))
    f.append(text(700, 310, "таження", size=11, anchor="start", color=MUTED))
    f.append(line(680, 320, 680, 340))
    f.append(line(665, 340, 695, 340, color=INK, sw=2))      # земля

    # Дільник зворотного зв'язку від Vout
    dx = 470
    f.append(line(vox, 260, dx, 260))
    f.append(line(dx, 260, dx, 285))
    f.append(rect(dx-10, 285, 20, 26, fill=FILL, stroke=LINE))  # Rtop
    f.append(text(dx+16, 300, "R1", size=12, anchor="start", color=MUTED))
    tap = 325
    f.append(line(dx, 311, dx, tap))
    f.append(circle(dx, tap, 4, fill=INK, stroke=INK))          # відвід Vfb
    f.append(line(dx, tap, dx, 350))
    f.append(rect(dx-10, 350, 20, 26, fill=FILL, stroke=LINE))  # Rbot
    f.append(text(dx+16, 366, "R2", size=12, anchor="start", color=MUTED))
    f.append(line(dx, 376, dx, 392))
    f.append(line(dx-15, 392, dx+15, 392, color=INK, sw=2))     # земля

    # Vfb → «−» вхід ОП
    f.append(line(dx, tap, 210, tap, color=NEG, sw=2))
    f.append(line(210, tap, 210, ay+22, color=NEG, sw=2))
    f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s"/>' %
             (205, ay+30, 215, ay+30, 210, ay+22, NEG))
    f.append(text(150, tap+4, "Vfb (зразок)", size=12, anchor="start", color=NEG))

    # Опора Vref → «+» вхід ОП
    refx, refy = 150, ay-22
    rb = textbox(refx-58, refy, "Vref", size=13, fill="#fdecea", stroke=POS, min_w=70)
    f.append(rb[0])
    f.append(line(refx-58+rb[1]/2, refy, 210, refy, color=POS, sw=2))
    f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="%s"/>' %
             (213, refy-5, 213, refy+5, 221, refy, POS))
    f.append(line(213, refy, ax-44, ay-20, color=POS, sw=2))

    render(os.path.join(IMG, 'regulator.svg'), W, H, *f)


# ── 3. Реакція на стрибок навантаження: просів → похибка → дотиск → відновлення ──
def fig_correct():
    W, H = 740, 330
    f = []
    f.append(text(W/2, 26, "Як контур гасить просідання виходу", size=17, bold=True))

    # Осі
    ox, oy = 80, 250          # початок координат
    axw, axh = 600, 180
    f.append(line(ox, oy, ox+axw, oy, color=INK, sw=1.5))      # вісь часу
    f.append(line(ox, oy, ox, oy-axh, color=INK, sw=1.5))      # вісь
    f.append(text(ox+axw, oy+22, "час", size=13, anchor="end", color=MUTED))

    # Рівень уставки (пунктир)
    setY = oy - 120
    f.append(line(ox, setY, ox+axw, setY, color=MUTED, sw=1.2, dash="5 4"))
    f.append(text(ox+axw+4, setY+4, "уставка", size=12, anchor="start", color=MUTED))

    # Момент стрибка навантаження
    t0 = ox + 230
    f.append(line(t0, oy, t0, oy-axh+8, color=POS, sw=1.2, dash="3 3"))
    f.append(text(t0, oy-axh-2, "стрибок навантаження", size=12, anchor="middle", color=POS))

    # Крива виходу: рівно на уставці → провал → відновлення до уставки
    pts = []
    for i in range(0, 231, 10):
        pts.append((ox+i, setY))                              # рівна полиця
    # провал і експоненційне відновлення
    import math
    for i in range(0, 261, 8):
        x = t0 + i
        dip = 70 * math.exp(-i/70.0)                          # глибина просідання, що тане
        pts.append((x, setY + dip))
    path = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, FIELD))
    f.append(text(ox+90, setY-10, "вихід тримається", size=12, anchor="middle", color=FIELD))

    # Стрілка вниз — просів
    f.append(text(t0+30, setY+58, "↓ просів", size=13, color=POS, anchor="start"))
    # Стрілка вгору — контур повертає
    f.append(text(t0+150, setY+8, "контур піднімає назад", size=12, color=INK, anchor="start"))

    # Підпис ланцюжка причинності внизу
    chain = "вихід просів  →  Vfb < Vref  →  похибка зросла  →  ОП дотиснув транзистор  →  вихід піднявся"
    cb = fitbox(ox, oy+34, axw, 34, chain, size=12.5, fill="#eef2f7", stroke=LINE)
    f.append(cb)

    render(os.path.join(IMG, 'correct.svg'), W, H, *f)


if __name__ == '__main__':
    fig_loop()
    fig_regulator()
    fig_correct()
    print("OK: loop.svg, regulator.svg, correct.svg ->", IMG)

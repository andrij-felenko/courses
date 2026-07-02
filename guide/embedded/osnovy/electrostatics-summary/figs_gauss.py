# -*- coding: utf-8 -*-
"""Фігури до вставки «Закон Гаусса: від підрахунку ліній до Q/ε₀»
(guide/embedded/osnovy/electrostatics-summary/math-gauss-flux.md).

Окремий генератор поряд із figs.py тієї ж теми (щоб не конфліктувати з
паралельним письмом інших вставок). Стиль і помічники — зі спільного svgkit
(НЕ переписувати тут).

Фігури:
  solid-angle.svg  — тілесний кут: чому r скорочується й годиться БУДЬ-ЯКА поверхня
  pillbox.svg      — гаусова «таблетка» на симетрії: площина σ/2ε₀ проти провідника σ/ε₀
Запуск:  python figs_gauss.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Тілесний кут: чому r скорочується й годиться будь-яка поверхня ─────────
def fig_solid_angle():
    W, H = 760, 430
    els = []
    cx, cy = 130, H / 2 + 6
    els.append(plus(cx, cy, r=13))
    # один «конус» ліній із заряду
    a_hi, a_lo = -0.42, 0.42          # розхил конуса (рад)
    L = 490
    for a in (a_hi, a_lo):
        els.append(line(cx, cy, cx + L * math.cos(a), cy + L * math.sin(a),
                        color=MUTED, sw=1.4, dash="2 4"))
    # кілька променів поля всередині конуса
    for a in (a_hi + 0.13, 0.0, a_lo - 0.13):
        x2, y2 = cx + 250 * math.cos(a), cy + 250 * math.sin(a)
        els.append(arrow(cx + 22 * math.cos(a), cy + 22 * math.sin(a),
                         x2, y2, color=FIELD, sw=1.7))
    # ближня «латка» (радіус r) і дальня (2r): дуги, що перетинають той самий конус
    def cap(rad, color, label):
        pts = []
        aa = a_hi
        while aa <= a_lo + 1e-6:
            pts.append("%.1f,%.1f" % (cx + rad * math.cos(aa), cy + rad * math.sin(aa)))
            aa += 0.03
        els.append('<polyline points="%s" fill="none" stroke="%s" '
                   'stroke-width="3"/>' % (" ".join(pts), color))
        els.append(text(cx + rad + 4, cy - 6, label, size=13, color=color,
                        bold=True, anchor="start"))
    cap(175, POS, "латка на r")
    cap(345, NEG, "латка на 2r")
    # позначки площ і поля
    els.append(text(cx + 150, cy + 120, "площа ×4,  E ×¼", size=13,
                    color=INK, anchor="middle"))
    els.append(text(cx + 150, cy + 142, "→ потік однаковий", size=13,
                    color=INK, anchor="middle", italic=True))
    # висновок праворуч-угорі
    els.append(fitbox(486, 60, 256, 120,
                      "Скільки ліній у конусі —\nстільки протне БУДЬ-ЯКУ\nлатку впоперек нього.\n\nE ~ 1/r², площа ~ r² —\nдобуток не залежить від r.",
                      size=12, fill=FILL, stroke=LINE))
    return render(os.path.join(IMG, 'solid-angle.svg'), W, H, *els,
                  title="Тілесний кут: чому r скорочується")


# ── 2. Гаусова «таблетка» на симетрії: площина σ/2ε₀ проти провідника σ/ε₀ ────
def fig_pillbox():
    W, H = 780, 440
    els = []

    def panel(x0, title, two_sided, formula):
        e = []
        midx = x0 + 150
        top, bot = 74, 320
        my = (top + bot) / 2
        e.append(text(midx, top - 16, title, size=15, bold=True))
        if two_sided:
            # заряджена площина: тонка лінія із зарядами, поле в обидва боки
            e.append(line(midx, top + 8, midx, bot - 8, color=POS, sw=2.4))
            for yy in range(top + 26, bot - 16, 34):
                e.append(plus(midx, yy, r=6))
            # таблетка охоплює площину: прямокутник поперек
            e.append(rect(midx - 60, my - 42, 120, 84, fill="none",
                          stroke=NEG, sw=2, rx=4))
            # поле виходить ЛІВОРУЧ і ПРАВОРУЧ (обидва торці «працюють»)
            e.append(arrow(midx - 60, my, midx - 118, my, color=FIELD, sw=2.4))
            e.append(arrow(midx + 60, my, midx + 118, my, color=FIELD, sw=2.4))
            e.append(text(midx - 92, my - 12, "E", size=13, color=FIELD))
            e.append(text(midx + 92, my - 12, "E", size=13, color=FIELD))
            e.append(text(midx, bot + 10, "два торці → 2·E·A", size=12, color=MUTED))
        else:
            # провідник: заповнений блок ліворуч, поле лише праворуч
            e.append(rect(x0 + 8, top, midx - x0 - 8, bot - top,
                          fill="#dfe6f2", stroke=NEG, sw=1.6))
            e.append(text(x0 + 72, my - 6, "провідник", size=13, color=NEG))
            e.append(text(x0 + 72, my + 16, "E = 0", size=13, color=INK, italic=True))
            for yy in range(top + 20, bot - 10, 30):
                e.append(plus(midx, yy, r=6))
            # таблетка: один торець у металі (E=0), другий — назовні
            e.append(rect(midx - 55, my - 42, 110, 84, fill="none",
                          stroke=NEG, sw=2, rx=4))
            e.append(arrow(midx + 55, my, midx + 118, my, color=FIELD, sw=2.4))
            e.append(text(midx + 92, my - 12, "E", size=13, color=FIELD))
            e.append(text(midx + 4, bot + 10, "один торець → E·A", size=12,
                          color=MUTED, anchor="start"))
        e.append(fitbox(x0 + 20, bot + 28, 260, 42, formula, size=15,
                        bold=True, fill=FILL, stroke=LINE))
        return e

    els += panel(20, "Нескінченна площина", True,  "E = σ / 2ε₀")
    els.append(line(W / 2, 60, W / 2, H - 16, color="#cfd6df", sw=1.4, dash="3 5"))
    els += panel(400, "Поверхня провідника", False, "E = σ / ε₀")
    return render(os.path.join(IMG, 'pillbox.svg'), W, H, *els,
                  title="Та сама таблетка, удвічі різне поле: куди «дивляться» торці")


if __name__ == '__main__':
    fig_solid_angle()
    fig_pillbox()
    print("OK:", [f for f in os.listdir(IMG) if f in ('solid-angle.svg', 'pillbox.svg')])

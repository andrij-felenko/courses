# -*- coding: utf-8 -*-
"""Фігури до теми «Стратегія виходу як частина вибору».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def fig_exit_cost_breakdown():
    W, H = 880, 460
    f = [rect(0, 0, W, H, fill=BG, stroke="none")]
    f.append(text(W / 2, 34, "Анатомія евакуаційного бюджету (Exit Cost)", size=16, bold=True))

    blocks = [
        ("1. Data Gravity & Egress", "Мережевий тариф виведення даних,\nконвертація форматів, ETL-пайплайни", NEG),
        ("2. Code & API Refactoring", "Переписування SDK, заміна API,\nадаптація ORM та моделей запитів", POS),
        ("3. Ops & Infrastructure", "Перенавчання команди, новий IaC,\nналаштування CI/CD та спостережуваності", FIELD),
        ("4. Dual-Running & Opportunity", "Паралельне утримання двох систем,\nризик виклику та затримка фіч", INK),
    ]

    bx, by, bw, bh = 60, 80, 360, 75
    for i, (title, desc, color) in enumerate(blocks):
        x = bx + (i % 2) * (bw + 40)
        y = by + (i // 2) * (bh + 30)
        f.append(rect(x, y, bw, bh, fill="#f8fafc", stroke=color, sw=2, rx=6))
        f.append(text(x + 15, y + 25, title, size=13, bold=True, color=color, anchor="start"))
        lines = desc.split("\n")
        for j, line_txt in enumerate(lines):
            f.append(text(x + 15, y + 45 + j * 16, line_txt, size=11, color=MUTED, anchor="start"))

    fy = 310
    f.append(rect(60, fy, 760, 110, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=8))
    f.append(text(W / 2, fy + 30, "Формула повного евакуаційного бюджету:", size=13, bold=True, color=INK))
    f.append(text(W / 2, fy + 60, "Total Exit Cost = C_egress + C_rewrite + C_ops + C_dual_run + C_opportunity", size=14, bold=True, color=POS))
    f.append(text(W / 2, fy + 88, "Якщо Total Exit Cost перевищує економію від міграції за 3 роки — міграція збиткова", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "exit-cost-breakdown.svg"), W, H, *f)


def fig_abstraction_tradeoff():
    W, H = 880, 480
    f = [rect(0, 0, W, H, fill=BG, stroke="none")]
    f.append(text(W / 2, 34, "Сумарна вартість володіння (TCO) та ціна абстракції", size=16, bold=True))

    L, R, TOP, BOT = 100, 780, 90, 390
    def X(t): return L + t / 10.0 * (R - L)
    def Y(v): return BOT - v / 100.0 * (BOT - TOP)

    pts_a = [(X(t), Y(10 + 1.2 * t * t)) for t in [0, 1, 2, 3, 4, 5, 6, 7, 8]]
    pts_b = [(X(t), Y(45 + 3.5 * t)) for t in range(11)]
    pts_c = [(X(t), Y(20 + 4.5 * t)) for t in range(11)]

    f.append(arrow(L, BOT, R + 20, BOT, color=INK, sw=1.8))
    f.append(arrow(L, BOT, L, TOP - 20, color=INK, sw=1.8))
    f.append(text(L - 10, TOP - 25, "Сумарна вартість (TCO), €", size=11, color=MUTED, anchor="start"))
    f.append(text(R + 25, BOT + 20, "Час / Масштаб продукту ->", size=11, color=MUTED, anchor="end"))

    def polyline_str(pts, color, sw=2.5, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)

    f.append(polyline_str(pts_a, POS, sw=3.0))
    f.append(polyline_str(pts_b, NEG, sw=2.5, dash="6,4"))
    f.append(polyline_str(pts_c, FIELD, sw=3.0))

    f.append(text(X(7.2), Y(75), "Пряма прив'язка (Прямий Lock-in)", size=11, bold=True, color=POS, anchor="start"))
    f.append(text(X(9.2), Y(78), "Важка абстракція з Day 1", size=11, bold=True, color=NEG, anchor="start"))
    f.append(text(X(9.2), Y(62), "Прагматичний адаптер", size=11, bold=True, color=FIELD, anchor="start"))

    f.append(line(X(4.5), BOT, X(4.5), Y(35), color=MUTED, sw=1.2, dash="3,3"))
    f.append(circle(X(4.5), Y(34.3), 5, fill=POS, stroke=INK, sw=1.5))
    f.append(textbox(X(4.5), Y(35) - 30, "Точка зламу (Break-even): lock-in стає пасткою", size=10, fill="#fff5f5", stroke=POS, color=POS, bold=True)[0])

    f.append(text(W / 2, BOT + 50, "Пряма прив'язка дешевша на старті, але вибухає при міграції. Прагматичний адаптер дає баланс.", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "abstraction-tradeoff.svg"), W, H, *f)


if __name__ == "__main__":
    fig_exit_cost_breakdown()
    fig_abstraction_tradeoff()
    print("SVG figures generated successfully.")

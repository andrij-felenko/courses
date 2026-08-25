# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-ілюстрацій для теми «Діаграма Вороного».
Використовує спільну бібліотеку svgkit із scripts/."""

import sys
import os
import math

# Підключення svgkit із scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig1_voronoi_concept():
    """Фігура 1: Концепція діаграми Вороного — сайти, опуклі комірки, ребра та вершини."""
    w, h = 900, 500
    frags = []

    # Тло
    frags.append(rect(15, 15, w - 30, h - 30, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))

    # Заголовок
    frags.append(text(w / 2, 45, "Анатомія діаграми Вороного: генератори, комірки та серединні перпендикуляри", size=16, color=INK, bold=True))

    # Полігони комірок із м'якою заливкою
    cell_s1 = '<polygon points="60,120 330,65 343,219 80,350 40,240" fill="#e0f2fe" stroke="none"/>'
    cell_s2 = '<polygon points="330,65 550,65 516,218 448,252 343,219" fill="#fef3c7" stroke="none"/>'
    cell_s3 = '<polygon points="550,65 840,130 860,250 820,350 516,218" fill="#dcfce7" stroke="none"/>'
    cell_s4 = '<polygon points="80,350 343,219 448,252 450,380 80,380" fill="#f3e8ff" stroke="none"/>'
    cell_s5 = '<polygon points="448,252 516,218 820,350 820,380 450,380" fill="#ffe4e6" stroke="none"/>'

    frags.extend([cell_s1, cell_s2, cell_s3, cell_s4, cell_s5])

    # Ребра Вороного (сині, чіткі лінії)
    vor_edges = [
        (330, 65, 343, 219),    # між S1 і S2
        (550, 65, 516, 218),    # між S2 і S3
        (343, 219, 448, 252),   # між S2 і S4
        (516, 218, 448, 252),   # між S2 і S5
        (448, 252, 450, 380),   # між S4 і S5
        (60, 120, 330, 65),     # зовнішнє S1
        (840, 130, 550, 65),    # зовнішнє S3
        (80, 350, 343, 219),    # між S1 і S4
        (516, 218, 820, 350),   # між S3 і S5
    ]
    for x1, y1, x2, y2 in vor_edges:
        frags.append(line(x1, y1, x2, y2, color="#1e40af", sw=2.2))

    # Штрихові лінії відрізків між сайтами (показати серединний перпендикуляр для S1-S2)
    frags.append(line(240, 160, 440, 140, color="#94a3b8", sw=1.5, dash="4 4"))
    # Прямий кут на перпендикулярі
    frags.append('<path d="M 335 155 L 343 147 L 351 155" fill="none" stroke="#64748b" stroke-width="1.2"/>')

    # Описане коло для V1 навколо S1, S2, S4 (показати властивість вершини Вороного)
    frags.append('<circle cx="343.0" cy="219.0" r="118.7" fill="none" stroke="#dc2626" stroke-width="1.4" stroke-dasharray="5 4"/>')

    # Сайти (генератори)
    sites = [
        (240, 160, "p₁", "#0284c7"),
        (440, 140, "p₂", "#d97706"),
        (640, 170, "p₃", "#16a34a"),
        (320, 310, "p₄", "#9333ea"),
        (560, 320, "p₅", "#e11d48")
    ]
    for sx, sy, slab, scol in sites:
        frags.append(circle(sx, sy, 7, fill=scol, stroke="#ffffff", sw=2))
        frags.append(text(sx + 16, sy - 10, slab, size=15, color=INK, bold=True))

    # Вершини Вороного (центри кіл)
    v_nodes = [
        (343, 219, "v₁"),
        (516, 218, "v₂"),
        (448, 252, "v₃")
    ]
    for vx, vy, vlab in v_nodes:
        frags.append(circle(vx, vy, 5, fill="#ffffff", stroke="#1e40af", sw=2.2))
        frags.append(text(vx - 14, vy - 10, vlab, size=13, color="#1e40af", bold=True))

    # Пояснювальні плашки знизу (вільні від ліній)
    frags.append(rect(40, 410, 380, 60, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(230, 433, "Комірка V(p₁):", size=12.5, color=INK, bold=True))
    frags.append(text(230, 455, "dist(x, p₁) < dist(x, pⱼ)  для всіх j ≠ 1", size=12, color="#0284c7", bold=True))

    frags.append(rect(480, 410, 380, 60, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=6))
    frags.append(text(670, 433, "Вершина v₁ (центр кола):", size=12.5, color=POS, bold=True))
    frags.append(text(670, 455, "dist(v₁, p₁) = dist(v₁, p₂) = dist(v₁, p₄)", size=12, color=INK, bold=True))

    render(os.path.join(OUT, "voronoi-concept-cells.svg"), w, h, *frags)


def fig2_voronoi_delaunay():
    """Фігура 2: Дуальність між діаграмою Вороного та тріангуляцією Делоне."""
    w, h = 920, 480
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(w / 2, 45, "Топологічна дуальність: діаграма Вороного (синя) та тріангуляція Делоне (помаранчева)", size=16, color=INK, bold=True))

    # Координати сайтів
    p1 = (220, 160)
    p2 = (440, 120)
    p3 = (680, 150)
    p4 = (310, 330)
    p5 = (570, 340)
    p6 = (450, 440)

    # Вершини Вороного
    v1 = (335, 205)  # коло p1, p2, p4
    v2 = (485, 215)  # коло p2, p3, p5
    v3 = (435, 275)  # коло p2, p4, p5
    v4 = (445, 375)  # коло p4, p5, p6

    # 1. Тріангуляція Делоне (грані з легкою заливкою та помаранчеві штрихові ребра)
    del_triangles = [
        f'<polygon points="{p1[0]},{p1[1]} {p2[0]},{p2[1]} {p4[0]},{p4[1]}" fill="#fff7ed" stroke="none"/>',
        f'<polygon points="{p2[0]},{p2[1]} {p3[0]},{p3[1]} {p5[0]},{p5[1]}" fill="#fff7ed" stroke="none"/>',
        f'<polygon points="{p2[0]},{p2[1]} {p4[0]},{p4[1]} {p5[0]},{p5[1]}" fill="#ffedd5" stroke="none"/>',
        f'<polygon points="{p4[0]},{p4[1]} {p5[0]},{p5[1]} {p6[0]},{p6[1]}" fill="#fff7ed" stroke="none"/>'
    ]
    frags.extend(del_triangles)

    del_edges = [
        (p1, p2), (p2, p3), (p1, p4), (p2, p4), (p2, p5),
        (p3, p5), (p4, p5), (p4, p6), (p5, p6)
    ]
    for (xa, ya), (xb, yb) in del_edges:
        frags.append(line(xa, ya, xb, yb, color="#ea580c", sw=2.2, dash="6 4"))

    # 2. Ребра Вороного (суцільні сині лінії)
    vor_edges = [
        (v1[0], v1[1], v3[0], v3[1]),  # дуальне до p2-p4
        (v2[0], v2[1], v3[0], v3[1]),  # дуальне до p2-p5
        (v3[0], v3[1], v4[0], v4[1]),  # дуальне до p4-p5
        (v1[0], v1[1], 330, 50),       # дуальне до p1-p2
        (v2[0], v2[1], 560, 50),       # дуальне до p2-p3
        (v1[0], v1[1], 60, 310),       # дуальне до p1-p4
        (v2[0], v2[1], 860, 290),      # дуальне до p3-p5
        (v4[0], v4[1], 230, 465),      # дуальне до p4-p6
        (v4[0], v4[1], 670, 465)       # дуальне до p5-p6
    ]
    for x1, y1, x2, y2 in vor_edges:
        frags.append(line(x1, y1, x2, y2, color="#2563eb", sw=2.5))

    # Порожнє описане коло для трикутника p2-p4-p5 навколо v3
    r_v3 = math.hypot(v3[0] - p2[0], v3[1] - p2[1])
    frags.append(f'<circle cx="{v3[0]:.1f}" cy="{v3[1]:.1f}" r="{r_v3:.1f}" fill="none" stroke="#059669" stroke-width="1.6" stroke-dasharray="4 3"/>')

    # Сайти
    all_sites = [
        (p1, "p₁"), (p2, "p₂"), (p3, "p₃"),
        (p4, "p₄"), (p5, "p₅"), (p6, "p₆")
    ]
    for (sx, sy), slab in all_sites:
        frags.append(circle(sx, sy, 6.5, fill="#ea580c", stroke="#ffffff", sw=2))
        frags.append(text(sx + 15, sy - 10, slab, size=15, color="#9a3412", bold=True))

    # Вершини Вороного
    all_v = [(v1, "v₁"), (v2, "v₂"), (v3, "v₃"), (v4, "v₄")]
    for (vx, vy), vlab in all_v:
        frags.append(circle(vx, vy, 5, fill="#ffffff", stroke="#2563eb", sw=2.2))
        frags.append(text(vx - 14, vy - 8, vlab, size=13, color="#1e40af", bold=True))

    # Пояснювальна легенда
    frags.append(rect(40, 395, 340, 60, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=5))
    frags.append(line(55, 415, 95, 415, color="#2563eb", sw=2.5))
    frags.append(text(195, 419, "Ребро Вороного e* (ортогональний поділ)", size=11.5, color=INK))
    frags.append(line(55, 438, 95, 438, color="#ea580c", sw=2.2, dash="5 4"))
    frags.append(text(185, 442, "Ребро Делоне e (зв'язок суміжних сайтів)", size=11.5, color=INK))

    frags.append(rect(580, 395, 300, 60, fill="#f0fdf4", stroke="#86efac", sw=1, rx=5))
    frags.append('<circle cx="600.0" cy="425.0" r="6.0" fill="none" stroke="#059669" stroke-width="1.6" stroke-dasharray="3 2"/>')
    frags.append(text(745, 418, "Властивість порожнього кола:", size=11.5, color="#166534", bold=True))
    frags.append(text(745, 438, "Описане коло Δp₂p₄p₅ не містить інших точок", size=11, color=INK))

    render(os.path.join(OUT, "voronoi-delaunay-duality.svg"), w, h, *frags)


def fig3_fortune_beach_line():
    """Фігура 3: Алгоритм Форчуна — замітальна пряма, параболи, пляжна лінія та точки зламу."""
    w, h = 940, 520
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(w / 2, 45, "Замітальна пряма Форчуна: формування пляжної лінії з параболічних дуг", size=16, color=INK, bold=True))

    sweep_y = 380

    # Область над замітальною прямою (світло-сіра)
    frags.append(f'<rect x="30" y="70" width="{w - 60}" height="{sweep_y - 70}" fill="#f8fafc" stroke="none"/>')

    # Замітальна пряма L: y = sweep_y
    frags.append(line(30, sweep_y, w - 30, sweep_y, color=POS, sw=2.2, dash="7 4"))
    frags.append(rect(w - 240, sweep_y - 30, 200, 24, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(w - 140, sweep_y - 14, "Замітальна пряма L (y = y_L)", size=11.5, color=POS, bold=True))

    # Стрілка напрямку руху прямої L
    frags.append(arrow(w / 2, sweep_y + 10, w / 2, sweep_y + 45, color=POS, sw=2))
    frags.append(text(w / 2 + 50, sweep_y + 32, "Рух L (↓)", size=12, color=POS, bold=True))

    # Сайти
    p1 = (220, 160)
    p2 = (460, 240)
    p3 = (720, 180)

    def get_parabola_y(x, focus, dy):
        fx, fy = focus
        return (dy + fy) / 2.0 - ((x - fx) ** 2) / (2.0 * (dy - fy))

    bp1_x, bp1_y = 344, 235
    bp2_x, bp2_y = 596, 244

    # 1. Тонкі пунктирні повні параболи
    for pt, col in [(p1, "#38bdf8"), (p2, "#fbbf24"), (p3, "#4ade80")]:
        pts = []
        for x_val in range(int(pt[0] - 220), int(pt[0] + 221), 10):
            y_val = get_parabola_y(x_val, pt, sweep_y)
            if 70 <= y_val <= sweep_y:
                pts.append(f"{x_val:.1f},{y_val:.1f}")
        if pts:
            frags.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="1.2" stroke-dasharray="3 3"/>')

    # 2. Пляжна лінія (нижня обвідна - жирна суцільна лінія)
    beach_pts = []
    for x_val in range(40, bp1_x + 1, 6):
        y_val = get_parabola_y(x_val, p1, sweep_y)
        beach_pts.append(f"{x_val:.1f},{y_val:.1f}")
    for x_val in range(bp1_x, bp2_x + 1, 6):
        y_val = get_parabola_y(x_val, p2, sweep_y)
        beach_pts.append(f"{x_val:.1f},{y_val:.1f}")
    for x_val in range(bp2_x, 901, 6):
        y_val = get_parabola_y(x_val, p3, sweep_y)
        beach_pts.append(f"{x_val:.1f},{y_val:.1f}")

    frags.append(f'<polyline points="{" ".join(beach_pts)}" fill="none" stroke="#059669" stroke-width="3"/>')

    # Траєкторії точок зламу (сформовані ребра Вороного над пляжною лінією)
    frags.append(line(325, 100, bp1_x, bp1_y, color="#2563eb", sw=2.5))
    frags.append(line(620, 90, bp2_x, bp2_y, color="#2563eb", sw=2.5))

    # Точки зламу (Breakpoints)
    for bx, by, blab in [(bp1_x, bp1_y, "b₁ (злам)"), (bp2_x, bp2_y, "b₂ (злам)")]:
        frags.append(circle(bx, by, 5, fill="#ffffff", stroke="#059669", sw=2.5))
        frags.append(text(bx, by - 12, blab, size=12, color="#065f46", bold=True))

    # Сайти
    for sx, sy, slab, scol in [(p1[0], p1[1], "p₁ (фокус)", "#0284c7"), (p2[0], p2[1], "p₂ (фокус)", "#d97706"), (p3[0], p3[1], "p₃ (фокус)", "#16a34a")]:
        frags.append(circle(sx, sy, 6, fill=scol, stroke="#ffffff", sw=2))
        frags.append(text(sx, sy - 12, slab, size=13, color=INK, bold=True))

    # Відрізки рівновіддаленості для однієї точки пляжної лінії
    test_x = 220
    test_y = get_parabola_y(test_x, p1, sweep_y)
    frags.append(line(test_x, p1[1], test_x, test_y, color="#dc2626", sw=1.4, dash="3 2"))
    frags.append(line(test_x, test_y, test_x, sweep_y, color="#dc2626", sw=1.4, dash="3 2"))
    frags.append(text(test_x + 8, (p1[1] + test_y) / 2, "d", size=12, color=POS, bold=True))
    frags.append(text(test_x + 8, (test_y + sweep_y) / 2, "d", size=12, color=POS, bold=True))

    # Пояснювальні плашки внизу
    frags.append(rect(40, 445, 410, 55, fill="#f0fdf4", stroke="#86efac", sw=1, rx=5))
    frags.append(text(245, 467, "Пляжна лінія (Beach Line):", size=12, color="#166534", bold=True))
    frags.append(text(245, 487, "Нижня обвідна парабол з фокусами в сайтах pᵢ та директрисою L", size=11, color=INK))

    frags.append(rect(490, 445, 410, 55, fill="#eff6ff", stroke="#bfdbfe", sw=1, rx=5))
    frags.append(text(695, 467, "Точки зламу (Breakpoints):", size=12, color="#1e40af", bold=True))
    frags.append(text(695, 487, "Перетини суміжних дуг креслять ребра Вороного при русі L", size=11, color=INK))

    render(os.path.join(OUT, "fortune-beach-line.svg"), w, h, *frags)


def fig4_fortune_events():
    """Фігура 4: Два типи подій алгоритму Форчуна — сайт-подія та коло-подія."""
    w, h = 920, 440
    frags = []

    frags.append(rect(15, 15, w - 30, h - 30, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(w / 2, 45, "Динаміка алгоритму Форчуна: обробка подій у черзі Q", size=16, color=INK, bold=True))

    # Ліва панель: Сайт-подія (Site Event)
    frags.append(rect(30, 70, 415, 345, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(237, 98, "1. Сайт-подія (Site Event)", size=14, color="#1e40af", bold=True))

    # Схема сайт-події
    s_p1 = (140, 160)
    s_p2 = (240, 260)  # новий сайт, якого торкається пряма
    s_sw_y = 260       # замітальна пряма в момент сайт-події

    frags.append(line(45, s_sw_y, 430, s_sw_y, color=POS, sw=1.8, dash="5 3"))
    frags.append(text(370, s_sw_y - 8, "L (досягла p₂)", size=11, color=POS, bold=True))

    # Стара дуга параболи p1
    frags.append('<path d="M 60 170 Q 140 250 220 258 Q 300 250 380 170" fill="none" stroke="#059669" stroke-width="2.5"/>')
    frags.append(text(100, 220, "дуга α(p₁)", size=11, color="#059669", bold=True))

    # Новий сайт p2 породжує вертикальний промінь-вироджену дугу, яка розщеплює α(p1) на дві
    frags.append(circle(s_p1[0], s_p1[1], 6, fill="#0284c7", stroke="#ffffff", sw=2))
    frags.append(text(s_p1[0], s_p1[1] - 12, "p₁", size=13, color=INK, bold=True))

    frags.append(circle(s_p2[0], s_p2[1], 6.5, fill=POS, stroke="#ffffff", sw=2))
    frags.append(text(s_p2[0] + 16, s_p2[1] + 4, "p₂ (новий)", size=12.5, color=POS, bold=True))

    # Стрілка розщеплення
    frags.append(arrow(s_p2[0], s_p2[1] - 30, s_p2[0], s_p2[1] - 6, color=POS, sw=1.8))

    frags.append(text(237, 340, "Новий сайт розщеплює наявну дугу:", size=12, color=INK, bold=True))
    frags.append(text(237, 365, "Послідовність дуг:  α(p₁) → α(p₁) · α(p₂) · α(p₁)", size=11.5, color="#1e40af", bold=True))
    frags.append(text(237, 390, "З'являються дві нові точки зламу", size=11, color=MUTED))


    # Права панель: Коло-подія (Circle Event)
    frags.append(rect(475, 70, 415, 345, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(682, 98, "2. Коло-подія (Circle Event)", size=14, color="#166534", bold=True))

    c_p1 = (560, 160)
    c_p2 = (680, 180)
    c_p3 = (800, 150)
    c_v = (680, 225)   # центр описаного кола (вершина Вороного)
    c_r = 138          # радіус
    c_sw_y = c_v[1] + c_r  # найнижча точка кола = 363

    # Описане коло трьох сайтів
    frags.append(f'<circle cx="{c_v[0]}" cy="{c_v[1]}" r="{c_r}" fill="#ecfdf5" stroke="#10b981" stroke-width="1.8" stroke-dasharray="4 3"/>')

    # Замітальна пряма в найнижчій точці кола
    frags.append(line(490, c_sw_y, 875, c_sw_y, color=POS, sw=1.8, dash="5 3"))
    frags.append(text(810, c_sw_y - 8, "L (y = y_v + R)", size=11, color=POS, bold=True))

    # Три сайти
    for cx, cy, clab in [(c_p1[0], c_p1[1], "p₁"), (c_p2[0], c_p2[1], "p₂"), (c_p3[0], c_p3[1], "p₃")]:
        frags.append(circle(cx, cy, 6, fill="#0284c7", stroke="#ffffff", sw=2))
        frags.append(text(cx, cy - 12, clab, size=13, color=INK, bold=True))

    # Зникаюча дуга p2 стискається в точку у вершині Вороного
    frags.append(circle(c_v[0], c_v[1], 5.5, fill="#ffffff", stroke="#dc2626", sw=2.2))
    frags.append(text(c_v[0] + 18, c_v[1] - 4, "v (вершина)", size=12, color=POS, bold=True))

    # Стрілка від нижньої точки кола до центру
    frags.append(arrow(c_v[0], c_sw_y, c_v[0], c_v[1] + 10, color="#10b981", sw=1.6))

    frags.append(text(682, 340, "Середня дуга α(p₂) стискається в нуль:", size=12, color=INK, bold=True))
    frags.append(text(682, 365, "Фіксується вершина v = circumcenter(p₁, p₂, p₃)", size=11.5, color="#166534", bold=True))
    frags.append(text(682, 390, "Дуга α(p₂) видаляється, сусіди p₁ та p₃ змикаються", size=11, color=MUTED))

    render(os.path.join(OUT, "fortune-circle-event.svg"), w, h, *frags)


if __name__ == '__main__':
    fig1_voronoi_concept()
    fig2_voronoi_delaunay()
    fig3_fortune_beach_line()
    fig4_fortune_events()
    print("Всі 4 фігури успішно згенеровано у img/")

# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_trapezoidal_vs_boustrophedon():
    W, H = 840, 420
    p = []

    # Заголовок лівої панелі
    tb_l, _, _ = textbox(215, 35, "Трапецієподібний розклад (6 комірок)", size=13, bold=True, fill="#fff3f0", stroke="#e74c3c")
    p.append(tb_l)
    p.append(text(215, 68, "Розрізи через кожну вершину перешкоди", size=11, color=MUTED, anchor="middle", italic=True))

    # Заголовок правої панелі
    tb_r, _, _ = textbox(635, 35, "Бустрофедонний розклад (4 комірки)", size=13, bold=True, fill="#f0fdf4", stroke=FIELD)
    p.append(tb_r)
    p.append(text(635, 68, "Розрізи лише у точках зміни зв'язності", size=11, color=MUTED, anchor="middle", italic=True))

    # Розділювач між панелями
    p.append(line(420, 20, 420, 395, color="#e5e7eb", sw=1.5, dash="4,4"))

    # Ліва панель
    poly_outer_l = [(60, 95), (370, 95), (370, 325), (60, 325)]
    poly_obs_l = [(160, 210), (220, 145), (270, 210), (220, 275)]

    p_pts_l = " ".join("%.1f,%.1f" % pt for pt in poly_outer_l)
    p.append('<polygon points="%s" fill="#f8fafc" stroke="%s" stroke-width="2.0"/>' % (p_pts_l, LINE))

    # Розрізи трапецієподібного розкладу
    p.append(line(160, 95, 160, 325, color="#e74c3c", sw=1.5, dash="4,3"))
    p.append(line(220, 95, 220, 145, color="#e74c3c", sw=1.5, dash="4,3"))
    p.append(line(220, 275, 220, 325, color="#e74c3c", sw=1.5, dash="4,3"))
    p.append(line(270, 95, 270, 325, color="#e74c3c", sw=1.5, dash="4,3"))

    p_obs_pts_l = " ".join("%.1f,%.1f" % pt for pt in poly_obs_l)
    p.append('<polygon points="%s" fill="#cbd5e1" stroke="%s" stroke-width="1.8"/>' % (p_obs_pts_l, LINE))
    p.append(text(218, 215, "Перешкода", size=10, color=INK, anchor="middle", bold=True))

    p.append(text(110, 210, "C1", size=12, color=INK, anchor="middle", bold=True))
    p.append(text(190, 120, "C2", size=11, color=INK, anchor="middle", bold=True))
    p.append(text(190, 300, "C3", size=11, color=INK, anchor="middle", bold=True))
    p.append(text(245, 120, "C4", size=11, color=INK, anchor="middle", bold=True))
    p.append(text(245, 300, "C5", size=11, color=INK, anchor="middle", bold=True))
    p.append(text(320, 210, "C6", size=12, color=INK, anchor="middle", bold=True))

    p.append(text(215, 360, "Дрібні комірки = надмірні розвороти", size=11, color=POS, anchor="middle", bold=True))

    # Права панель (Бустрофедон)
    poly_outer_r = [(480, 95), (790, 95), (790, 325), (480, 325)]
    poly_obs_r = [(580, 210), (640, 145), (690, 210), (640, 275)]

    p_pts_r = " ".join("%.1f,%.1f" % pt for pt in poly_outer_r)
    p.append('<polygon points="%s" fill="#f8fafc" stroke="%s" stroke-width="2.0"/>' % (p_pts_r, LINE))

    # Розрізи бустрофедонного розкладу ТІЛЬКИ через 580 (SPLIT) та 690 (MERGE)
    p.append(line(580, 95, 580, 325, color=FIELD, sw=2.0, dash="5,3"))
    p.append(line(690, 95, 690, 325, color=FIELD, sw=2.0, dash="5,3"))

    p_obs_pts_r = " ".join("%.1f,%.1f" % pt for pt in poly_obs_r)
    p.append('<polygon points="%s" fill="#cbd5e1" stroke="%s" stroke-width="1.8"/>' % (p_obs_pts_r, LINE))
    p.append(text(638, 215, "Перешкода", size=10, color=INK, anchor="middle", bold=True))

    p.append(text(530, 210, "C1", size=13, color=INK, anchor="middle", bold=True))
    p.append(text(635, 120, "C2", size=12, color=INK, anchor="middle", bold=True))
    p.append(text(635, 300, "C3", size=12, color=INK, anchor="middle", bold=True))
    p.append(text(740, 210, "C4", size=13, color=INK, anchor="middle", bold=True))

    p.append(circle(580, 210, 4, fill=FIELD, stroke=INK, sw=1.5))
    p.append(circle(690, 210, 4, fill=FIELD, stroke=INK, sw=1.5))
    p.append(text(580, 195, "SPLIT", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(text(690, 195, "MERGE", size=10, color=FIELD, anchor="middle", bold=True))

    p.append(text(635, 360, "Великі монотонні смуги = суцільні галси", size=11, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(OUT, "trapezoidal-vs-boustrophedon.svg"), W, H, *p)


def fig_critical_points_classification():
    W, H = 840, 430
    p = []

    p.append(rect(40, 16, 760, 34, fill="#f1f5f9", stroke="#cbd5e1", rx=4))
    p.append(text(370, 38, "Напрямок руху прямої замітання (Sweep Line)  x →", size=12, color=INK, anchor="middle", bold=True))
    p.append(arrow(550, 33, 610, 33, color=LINE, sw=1.8))

    xs = [40, 235, 430, 625]
    box_w = 175
    box_h = 345
    y_top = 65

    events = [
        ("Подія IN", "Локальний мінімум", "0 → 1 інтервал", "#2457d6"),
        ("Подія SPLIT", "Зустріч перешкоди", "1 → 2 інтервали", "#c0392b"),
        ("Подія MERGE", "Кінець перешкоди", "2 → 1 інтервал", "#d97706"),
        ("Подія OUT", "Локальний максимум", "1 → 0 інтервалів", "#27ae60"),
    ]

    for idx, (title_str, sub_str, delta_str, col) in enumerate(events):
        bx = xs[idx]
        p.append(rect(bx, y_top, box_w, box_h, fill="#fafafa", stroke="#e2e8f0", rx=6))
        tb, _, _ = textbox(bx + box_w / 2, y_top + 26, title_str, size=12, bold=True, fill="#ffffff", stroke=col)
        p.append(tb)
        p.append(text(bx + box_w / 2, y_top + 58, sub_str, size=11, color=MUTED, anchor="middle"))
        p.append(text(bx + box_w / 2, y_top + 78, delta_str, size=12, color=col, anchor="middle", bold=True))

        cy = y_top + 185
        cx = bx + box_w / 2

        p.append(line(cx, y_top + 105, cx, y_top + 270, color="#94a3b8", sw=1.5, dash="4,3"))

        if idx == 0:
            poly = [(cx + 45, cy - 50), (cx, cy), (cx + 45, cy + 50), (cx + 60, cy + 50), (cx + 60, cy - 50)]
            p.append('<polygon points="%s" fill="#e2e8f0" stroke="%s" stroke-width="1.8"/>' % (" ".join("%.1f,%.1f" % pt for pt in poly), LINE))
            p.append(circle(cx, cy, 5, fill=col, stroke=INK, sw=1.5))
            p.append(text(cx, cy + 75, "Початок простору", size=10, color=INK, anchor="middle"))
            p.append(text(cx, cy + 95, "Δb₀ = +1", size=11, color=col, anchor="middle", bold=True))

        elif idx == 1:
            poly_obs = [(cx, cy), (cx + 45, cy - 40), (cx + 45, cy + 40)]
            p.append('<polygon points="%s" fill="#cbd5e1" stroke="%s" stroke-width="1.8"/>' % (" ".join("%.1f,%.1f" % pt for pt in poly_obs), LINE))
            p.append(circle(cx, cy, 5, fill=col, stroke=INK, sw=1.5))
            p.append(text(cx, cy + 75, "Розподіл смуги на дві", size=10, color=INK, anchor="middle"))
            p.append(text(cx, cy + 95, "Δb₀ = +1", size=11, color=col, anchor="middle", bold=True))

        elif idx == 2:
            poly_obs = [(cx - 45, cy - 40), (cx, cy), (cx - 45, cy + 40)]
            p.append('<polygon points="%s" fill="#cbd5e1" stroke="%s" stroke-width="1.8"/>' % (" ".join("%.1f,%.1f" % pt for pt in poly_obs), LINE))
            p.append(circle(cx, cy, 5, fill=col, stroke=INK, sw=1.5))
            p.append(text(cx, cy + 75, "Злиття двох смуг в одну", size=10, color=INK, anchor="middle"))
            p.append(text(cx, cy + 95, "Δb₀ = −1", size=11, color=col, anchor="middle", bold=True))

        elif idx == 3:
            poly = [(cx - 45, cy - 50), (cx, cy), (cx - 45, cy + 50), (cx - 60, cy + 50), (cx - 60, cy - 50)]
            p.append('<polygon points="%s" fill="#e2e8f0" stroke="%s" stroke-width="1.8"/>' % (" ".join("%.1f,%.1f" % pt for pt in poly), LINE))
            p.append(circle(cx, cy, 5, fill=col, stroke=INK, sw=1.5))
            p.append(text(cx, cy + 75, "Кінець простору", size=10, color=INK, anchor="middle"))
            p.append(text(cx, cy + 95, "Δb₀ = −1", size=11, color=col, anchor="middle", bold=True))

    render(os.path.join(OUT, "critical-points-classification.svg"), W, H, *p)


def fig_cell_adjacency_coverage_tour():
    W, H = 840, 480
    p = []

    tb_main, _, _ = textbox(420, 26, "Граф суміжності комірок та маршрут повного покриття", size=13, bold=True, fill="#f8fafc", stroke=LINE)
    p.append(tb_main)

    poly_ext = [(50, 60), (790, 60), (790, 410), (50, 410)]
    p_ext_str = " ".join("%.1f,%.1f" % pt for pt in poly_ext)
    p.append('<polygon points="%s" fill="#fcfcfc" stroke="%s" stroke-width="2.0"/>' % (p_ext_str, LINE))

    obs1 = [(200, 235), (270, 165), (340, 235), (270, 305)]
    p_obs1_str = " ".join("%.1f,%.1f" % pt for pt in obs1)
    p.append('<polygon points="%s" fill="#cbd5e1" stroke="%s" stroke-width="1.8"/>' % (p_obs1_str, LINE))
    p.append(text(270, 240, "Перешкода A", size=10, color=INK, anchor="middle", bold=True))

    obs2 = [(490, 235), (555, 165), (620, 235), (555, 305)]
    p_obs2_str = " ".join("%.1f,%.1f" % pt for pt in obs2)
    p.append('<polygon points="%s" fill="#cbd5e1" stroke="%s" stroke-width="1.8"/>' % (p_obs2_str, LINE))
    p.append(text(555, 240, "Перешкода B", size=10, color=INK, anchor="middle", bold=True))

    cuts = [200, 340, 490, 620]
    for cx in cuts:
        p.append(line(cx, 60, cx, 410, color="#94a3b8", sw=1.4, dash="4,3"))

    cell_labels = [
        (125, 80, "C1"),
        (270, 80, "C2"),
        (270, 390, "C3"),
        (415, 80, "C4"),
        (555, 80, "C5"),
        (555, 390, "C6"),
        (705, 80, "C7")
    ]
    for lx, ly, ltxt in cell_labels:
        tb_c, _, _ = textbox(lx, ly, ltxt, size=11, bold=True, fill="#e2e8f0", stroke="#64748b")
        p.append(tb_c)

    for gx in [80, 110, 140, 170]:
        p.append(line(gx, 80, gx, 390, color="#3b82f6", sw=1.2))
    p.append(line(80, 390, 110, 390, color="#3b82f6", sw=1.2))
    p.append(line(110, 80, 140, 80, color="#3b82f6", sw=1.2))
    p.append(line(140, 390, 170, 390, color="#3b82f6", sw=1.2))

    for gx in [230, 270, 310]:
        p.append(line(gx, 80, gx, 145, color="#3b82f6", sw=1.2))
    p.append(line(230, 145, 270, 145, color="#3b82f6", sw=1.2))
    p.append(line(270, 80, 310, 80, color="#3b82f6", sw=1.2))

    nodes = {
        "C1": (125, 235),
        "C2": (270, 120),
        "C3": (270, 350),
        "C4": (415, 235),
        "C5": (555, 120),
        "C6": (555, 350),
        "C7": (705, 235),
    }

    edges = [
        ("C1", "C2"), ("C1", "C3"),
        ("C2", "C4"), ("C3", "C4"),
        ("C4", "C5"), ("C4", "C6"),
        ("C5", "C7"), ("C6", "C7"),
    ]

    for u, v in edges:
        x1, y1 = nodes[u]
        x2, y2 = nodes[v]
        p.append(line(x1, y1, x2, y2, color=FIELD, sw=3.0))

    for name, (nx, ny) in nodes.items():
        p.append(circle(nx, ny, 10, fill=POS, stroke="#ffffff", sw=2.0))
        p.append(text(nx, ny + 4, name, size=10, color="#ffffff", anchor="middle", bold=True))

    p.append(rect(50, 428, 740, 36, fill="#f8fafc", stroke="#e2e8f0", rx=4))
    p.append(line(70, 446, 105, 446, color="#3b82f6", sw=1.8))
    p.append(text(115, 450, "Локальні галси", size=11, color=INK, anchor="start"))

    p.append(circle(260, 446, 7, fill=POS, stroke="#ffffff", sw=1.5))
    p.append(text(275, 450, "Вузол графа (комірка)", size=11, color=INK, anchor="start"))

    p.append(line(460, 446, 495, 446, color=FIELD, sw=3.0))
    p.append(text(505, 450, "Ребро суміжності (перехід)", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "cell-adjacency-coverage-tour.svg"), W, H, *p)


def fig_sweep_direction_turns():
    W, H = 840, 420
    p = []

    tb_b, _, _ = textbox(215, 32, "Невигідний напрямок замітання", size=12, bold=True, fill="#fff3f0", stroke="#e74c3c")
    p.append(tb_b)
    p.append(text(215, 68, "Багато коротких проходів (11 розворотів)", size=11, color=POS, anchor="middle", bold=True))

    tb_g, _, _ = textbox(625, 32, "Оптимальний напрямок замітання", size=12, bold=True, fill="#f0fdf4", stroke=FIELD)
    p.append(tb_g)
    p.append(text(625, 68, "Мало довгих проходів (3 розвороти)", size=11, color=FIELD, anchor="middle", bold=True))

    p.append(line(420, 20, 420, 395, color="#e5e7eb", sw=1.5, dash="4,4"))

    p_l = [(60, 110), (370, 110), (370, 320), (60, 320)]
    p.append('<polygon points="%s" fill="#f8fafc" stroke="%s" stroke-width="2.0"/>' % (" ".join("%.1f,%.1f" % pt for pt in p_l), LINE))

    xs_bad = [85, 110, 135, 160, 185, 210, 235, 260, 285, 310, 335]
    for i, x in enumerate(xs_bad):
        p.append(line(x, 120, x, 310, color=POS, sw=1.5))
        if i < len(xs_bad) - 1:
            nxt = xs_bad[i + 1]
            y_turn = 310 if i % 2 == 0 else 120
            p.append(line(x, y_turn, nxt, y_turn, color=POS, sw=1.5))
            p.append(circle(x, y_turn, 3, fill=POS, stroke="none"))

    p.append(text(215, 355, "Час на розворотах: 11 · T_turn (витрати часу й пального)", size=11, color=MUTED, anchor="middle"))

    p_r = [(470, 110), (780, 110), (780, 320), (470, 320)]
    p.append('<polygon points="%s" fill="#f8fafc" stroke="%s" stroke-width="2.0"/>' % (" ".join("%.1f,%.1f" % pt for pt in p_r), LINE))

    ys_good = [140, 190, 240, 290]
    for i, y in enumerate(ys_good):
        p.append(line(485, y, 765, y, color=FIELD, sw=2.0))
        if i < len(ys_good) - 1:
            nxt = ys_good[i + 1]
            x_turn = 765 if i % 2 == 0 else 485
            p.append(line(x_turn, y, x_turn, nxt, color=FIELD, sw=2.0))
            p.append(circle(x_turn, y, 3.5, fill=FIELD, stroke="none"))

    p.append(text(625, 355, "Час на розворотах: 3 · T_turn (економія до 70% на розворотах)", size=11, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(OUT, "sweep-direction-turns.svg"), W, H, *p)


if __name__ == "__main__":
    fig_trapezoidal_vs_boustrophedon()
    fig_critical_points_classification()
    fig_cell_adjacency_coverage_tour()
    fig_sweep_direction_turns()
    print("OK: generated 4 figures")

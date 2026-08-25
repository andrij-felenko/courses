# -*- coding: utf-8 -*-
"""Фігури до статті «Фігури Ліссажу».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/. svgkit береться зі scripts/ у корені репо.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def lissajous_pts(cx, cy, Ax, Ay, fx, fy, delta, n=600):
    """Генерує точки (x, y) для фігури Ліссажу."""
    pts = []
    for i in range(n + 1):
        t = 2.0 * math.pi * (i / n)
        x = cx + Ax * math.sin(fx * t + delta)
        y = cy - Ay * math.sin(fy * t)
        pts.append("%.1f,%.1f" % (x, y))
    return " ".join(pts)


def polyline(pts_str, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<polyline fill="none" stroke="%s" stroke-width="%.1f"%s points="%s"/>' % (color, sw, d, pts_str)


# ── 1. Концепція X-Y режиму ───────────────────────────────────────────────
def fig_xy_concept():
    W, H = 880, 480
    cx, cy = 540, 250
    Ax, Ay = 170, 130

    out = []
    # Задній фон осцилографічної сітки
    out.append(rect(cx - Ax - 30, cy - Ay - 30, 2 * Ax + 60, 2 * Ay + 60, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Сітка всередині екрана
    for dx in range(-int(Ax), int(Ax) + 1, 45):
        out.append(line(cx + dx, cy - Ay - 20, cx + dx, cy + Ay + 20, color="#e2e8f0", sw=1.0, dash="2,4"))
    for dy in range(-int(Ay), int(Ay) + 1, 35):
        out.append(line(cx - Ax - 20, cy + dy, cx + Ax + 20, cy + dy, color="#e2e8f0", sw=1.0, dash="2,4"))

    # Осі X та Y
    out.append(line(cx - Ax - 20, cy, cx + Ax + 30, cy, color=MUTED, sw=1.2))
    out.append(line(cx, cy + Ay + 20, cx, cy - Ay - 30, color=MUTED, sw=1.2))
    out.append(text(cx + Ax + 40, cy + 5, "X(t)", size=14, color=INK, bold=True, anchor="start"))
    out.append(text(cx - 5, cy - Ay - 38, "Y(t)", size=14, color=INK, bold=True, anchor="end"))

    # Траєкторія Ліссажу (1:1, delta = pi/4)
    pts = lissajous_pts(cx, cy, Ax, Ay, 1.0, 1.0, math.pi / 4)
    out.append(polyline(pts, color=NEG, sw=2.8))

    # Вхідні блоки ліворуч (x = 30..280, екран починається з x = 340)
    box_x = fitbox(30, 50, 250, 95, "Сигнал каналу X:\nX(t) = A_x · sin(ω_x · t + δ)", size=13, fill="#eaf0fd", stroke=NEG, sw=1.5)
    out.append(box_x)

    box_y = fitbox(30, 165, 250, 95, "Сигнал каналу Y:\nY(t) = A_y · sin(ω_y · t)", size=13, fill="#fdecea", stroke=POS, sw=1.5)
    out.append(box_y)

    box_res = fitbox(30, 280, 250, 110, "Результуючий рух:\nТочка (X(t), Y(t))\nвимальовує траєкторію\nна площині екрана", size=13, fill="#f4f6f8", stroke=INK, sw=1.5)
    out.append(box_res)

    # Стрілки вказують на екран
    out.append(arrow(280, 97, cx - Ax - 30, cy - Ay / 2, color=NEG, sw=1.8))
    out.append(arrow(280, 212, cx - Ax - 30, cy + Ay / 2, color=POS, sw=1.8))

    # Підпис заголовка
    out.append(text(W / 2, 25, "Перпендикулярне додавання коливань у режимі X-Y", size=16, color=INK, bold=True))

    render(os.path.join(IMG, "xy-mode-concept.svg"), W, H, *out)


# ── 2. Галерея фазових еліпсів (1:1) ──────────────────────────────────────
def fig_phase_gallery():
    W, H = 880, 260
    phases = [
        (0.0, "0° (0 rad)", "Пряма (I, III)"),
        (math.pi / 4, "45° (π/4)", "Нахилений еліпс"),
        (math.pi / 2, "90° (π/2)", "Коло / Еліпс"),
        (3 * math.pi / 4, "135° (3π/4)", "Нахилений еліпс"),
        (math.pi, "180° (π)", "Пряма (II, IV)")
    ]

    out = []
    out.append(text(W / 2, 25, "Зміна форми траєкторії при зміні різниці фаз δ (співвідношення частот 1:1)", size=15, color=INK, bold=True))

    for i, (delta, label_deg, label_shape) in enumerate(phases):
        cx = 90 + i * 175
        cy = 130
        r = 55

        # Рамка для кожного еліпса
        out.append(rect(cx - 70, cy - 70, 140, 140, fill="#fafafa", stroke="#e2e8f0", sw=1.2, rx=6))
        # Осі
        out.append(line(cx - 60, cy, cx + 60, cy, color="#cbd5e1", sw=1.0, dash="2,3"))
        out.append(line(cx, cy - 60, cx, cy + 60, color="#cbd5e1", sw=1.0, dash="2,3"))

        # Траєкторія
        pts = lissajous_pts(cx, cy, r, r, 1.0, 1.0, delta)
        col = POS if delta in (0.0, math.pi) else (FIELD if delta == math.pi / 2 else NEG)
        out.append(polyline(pts, color=col, sw=2.2))

        # Підписи
        out.append(text(cx, cy + 85, label_deg, size=13, color=INK, bold=True))
        out.append(text(cx, cy + 105, label_shape, size=11, color=MUTED))

    render(os.path.join(IMG, "phase-ellipse-gallery.svg"), W, H, *out)


# ── 3. Метод вимірювання фази ─────────────────────────────────────────────
def fig_phase_measurement():
    W, H = 780, 420
    cx, cy = 230, 220
    Ax, Ay = 150, 130
    delta = math.pi / 6  # 30 degrees

    out = []
    out.append(text(W / 2, 25, "Визначення різниці фаз δ за еліпсом на осцилографі", size=16, color=INK, bold=True))

    # Сітка екрана (x = 50 .. 410)
    out.append(rect(cx - Ax - 30, cy - Ay - 30, 2 * Ax + 60, 2 * Ay + 60, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Осі X та Y
    out.append(line(cx - Ax - 20, cy, cx + Ax + 20, cy, color=INK, sw=1.5))
    out.append(line(cx, cy + Ay + 20, cx, cy - Ay - 20, color=INK, sw=1.5))

    # Еліпс
    pts = lissajous_pts(cx, cy, Ax, Ay, 1.0, 1.0, delta)
    out.append(polyline(pts, color=NEG, sw=2.6))

    # Точка перетину з віссю Y при x=0: y = Ay * sin(delta)
    y0_offset = Ay * math.sin(delta)
    y_cut_top = cy - y0_offset
    y_cut_bot = cy + y0_offset

    # Позначки Y0 (перетин осі Y)
    out.append(circle(cx, y_cut_top, 4.5, fill=POS, stroke=POS))
    out.append(circle(cx, y_cut_bot, 4.5, fill=POS, stroke=POS))

    # Лінії виносні для Y0
    out.append(line(cx, y_cut_top, cx + Ax + 40, y_cut_top, color=POS, sw=1.2, dash="3,3"))
    out.append(line(cx, cy, cx + Ax + 40, cy, color=MUTED, sw=1.0, dash="2,2"))
    out.append(line(cx + Ax + 35, cy, cx + Ax + 35, y_cut_top, color=POS, sw=1.5))
    out.append(text(cx + Ax + 45, (cy + y_cut_top) / 2 + 4, "Y₀", size=14, color=POS, bold=True, anchor="start"))

    # Позначки Y_max (максимальний розмах по Y)
    y_max_top = cy - Ay
    out.append(line(cx - Ax - 40, y_max_top, cx, y_max_top, color=FIELD, sw=1.2, dash="3,3"))
    out.append(line(cx - Ax - 35, cy, cx - Ax - 35, y_max_top, color=FIELD, sw=1.5))
    out.append(text(cx - Ax - 45, (cy + y_max_top) / 2 + 4, "Y_max", size=14, color=FIELD, bold=True, anchor="end"))

    # Текстові блоки праворуч (x = 450 .. 750)
    box_formula = fitbox(450, 50, 300, 180,
                         "Формула розрахунку:\n"
                         "При X = 0:  Y₀ = Y_max · sin(δ)\n\n"
                         "sin(δ) = Y₀ / Y_max\n\n"
                         "δ = arcsin( Y₀ / Y_max )",
                         size=14, fill="#f4f6f8", stroke=INK, sw=1.8, bold=True)
    out.append(box_formula)

    box_note = fitbox(450, 260, 300, 80,
                      "Примітка: вимірюються відстані\nміж перетинами Y-осі (2Y₀) та\nповна висота еліпса (2Y_max).",
                      size=12, fill="#fffbeb", stroke="#f59e0b", sw=1.2)
    out.append(box_note)

    render(os.path.join(IMG, "phase-measurement.svg"), W, H, *out)


# ── 4. Галерея співвідношень частот ───────────────────────────────────────
def fig_ratio_gallery():
    W, H = 880, 260
    ratios = [
        (1.0, 1.0, math.pi / 2, "f_x : f_y = 1 : 1", "1 коло / еліпс"),
        (1.0, 2.0, math.pi / 4, "f_x : f_y = 1 : 2", "«Вісімка» / 2 петлі"),
        (2.0, 3.0, math.pi / 4, "f_x : f_y = 2 : 3", "3 верт. / 2 гор. петлі"),
        (3.0, 4.0, math.pi / 4, "f_x : f_y = 3 : 4", "4 верт. / 3 гор. петлі")
    ]

    out = []
    out.append(text(W / 2, 25, "Фігури Ліссажу для різних співвідношень частот f_x : f_y", size=15, color=INK, bold=True))

    for i, (fx, fy, delta, label_ratio, label_loops) in enumerate(ratios):
        cx = 110 + i * 220
        cy = 130
        Ax, Ay = 75, 60

        # Рамка екрана
        out.append(rect(cx - 90, cy - 70, 180, 140, fill="#fafafa", stroke="#e2e8f0", sw=1.2, rx=6))
        # Осі
        out.append(line(cx - 80, cy, cx + 80, cy, color="#cbd5e1", sw=1.0, dash="2,3"))
        out.append(line(cx, cy - 60, cx, cy + 60, color="#cbd5e1", sw=1.0, dash="2,3"))

        # Траєкторія
        pts = lissajous_pts(cx, cy, Ax, Ay, fx, fy, delta, n=800)
        out.append(polyline(pts, color=NEG, sw=2.2))

        # Підписи
        out.append(text(cx, cy + 85, label_ratio, size=13, color=INK, bold=True))
        out.append(text(cx, cy + 105, label_loops, size=11, color=MUTED))

    render(os.path.join(IMG, "ratio-gallery-xy.svg"), W, H, *out)


# ── 5. Оптичний прилад Ліссажу ────────────────────────────────────────────
def fig_lissajous_pendulum_light():
    W, H = 820, 360
    out = []

    out.append(text(W / 2, 25, "Історична оптична установка Ліссажу (1857 рік)", size=16, color=INK, bold=True))

    # Джерело світла (ліхтар)
    box_light = fitbox(70, 180, 100, 70, "Джерело\nсвітла", size=13, fill="#fef08a", stroke="#eab308", sw=1.5)
    out.append(box_light)

    # Промінь світла 1
    out.append(arrow(120, 180, 230, 180, color="#eab308", sw=2.5))

    # Камертон 1 (вертикальні коливання)
    box_tf1 = fitbox(280, 180, 100, 100, "Камертон 1\n(дзеркало Y)\nВертикальні\nколивання", size=12, fill="#e2e8f0", stroke=INK, sw=1.5)
    out.append(box_tf1)

    # Промінь світла 2 (відбитий убік второго камертона)
    out.append(arrow(330, 180, 470, 180, color="#eab308", sw=2.5))

    # Камертон 2 (горизонтальні коливання)
    box_tf2 = fitbox(520, 180, 100, 100, "Камертон 2\n(дзеркало X)\nГоризонтальні\nколивання", size=12, fill="#e2e8f0", stroke=INK, sw=1.5)
    out.append(box_tf2)

    # Промінь світла 3 (на екран)
    out.append(arrow(570, 180, 680, 180, color="#eab308", sw=2.5))

    # Екран із фігурою
    out.append(rect(680, 100, 110, 160, fill="#1e293b", stroke="#0f172a", sw=2.0, rx=4))
    # Маленька фігура Ліссажу на екрані (1:2)
    pts = lissajous_pts(735, 180, 35, 45, 1.0, 2.0, math.pi / 4)
    out.append(polyline(pts, color="#38bdf8", sw=2.0))
    out.append(text(735, 280, "Проекційний\nекран", size=12, color=INK, bold=True))

    # Пояснення знизу
    box_exp = fitbox(W / 2, 320, 680, 50,
                     "Світловий промінь послідовно відбивається від двох дзеркалець, прикріплених до ніжних камертонів.\n"
                     "Результувальний світловий відблиск малює фігуру Ліссажу на екрані.", size=12, fill="#f4f6f8", stroke=MUTED, sw=1.0)
    out.append(box_exp)

    render(os.path.join(IMG, "lissajous-pendulum-light.svg"), W, H, *out)


if __name__ == "__main__":
    fig_xy_concept()
    fig_phase_gallery()
    fig_phase_measurement()
    fig_ratio_gallery()
    fig_lissajous_pendulum_light()
    print("Всі фігури успішно згенеровано у ./img/")

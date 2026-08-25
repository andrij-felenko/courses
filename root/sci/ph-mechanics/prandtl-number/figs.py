# -*- coding: utf-8 -*-
"""Фігури до теми «Число Прандтля».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def path_fill(pts, fill, stroke='none', sw=0):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for (x, y) in pts) + " Z"
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)


def head_at(x, y, dx, dy, color=INK, size=9):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.5, by + ny * size * 0.5,
               bx - nx * size * 0.5, by - ny * size * 0.5, color))


def varrow(x1, y1, x2, y2, color=LINE, sw=2.0, head=9):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)


def hatch_below(x0, x1, y, dh=8, step=12, color=MUTED):
    out = [line(x0, y, x1, y, color=INK, sw=2.2)]
    x = x0
    while x < x1:
        out.append(line(x, y, x - dh, y + dh, color=color, sw=1.2))
        x += step
    return "".join(out)


# ── Фігура 1: Порівняння примежових шарів при різних Pr ──────────────────────
def fig_boundary_layer_comparison(filepath):
    W, H = 940, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Порівняння гідродинамічного та теплового примежових шарів", size=18, bold=True))
    f.append(text(W / 2, 54, "Відношення товщин шарів δ_v та δ_t залежить від числа Прандтля (Pr = ν / α)",
                  size=12.5, color=MUTED))

    wall_y = 440
    top_y = 140
    umax = 190

    def draw_panel(ax, pr_text, title, desc, v_factor, t_factor):
        g = []
        # Заголовок панелі
        g.append(rect(ax - 10, top_y - 65, 270, 48, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
        g.append(text(ax + 125, top_y - 48, title, size=15, bold=True, color=INK))
        g.append(text(ax + 125, top_y - 28, desc, size=11.5, color=MUTED))

        # Лінії межі шарів
        y_dv = wall_y - (wall_y - top_y) * v_factor
        y_dt = wall_y - (wall_y - top_y) * t_factor

        # Стінка з штрихуванням
        g.append(hatch_below(ax - 10, ax + umax + 50, wall_y))
        g.append(text(ax + umax + 20, wall_y + 24, "стінка", size=11, color=MUTED))

        # Вісь y
        g.append(varrow(ax, wall_y + 4, ax, top_y - 75, color=INK, sw=1.5, head=8))
        g.append(text(ax - 12, top_y - 72, "y", size=13, italic=True))

        # Профіль швидкості (синій)
        v_pts = []
        for i in range(31):
            e = i / 30.0
            y = wall_y - e * (wall_y - top_y) * v_factor
            u = math.sin(math.pi / 2 * min(1.0, e)) * umax
            v_pts.append((ax + u, y))
        v_pts.append((ax + umax, top_y - 10))
        g.append(polyline([(ax, wall_y)] + v_pts, color=NEG, sw=2.5))
        g.append(line(ax, y_dv, ax + umax + 20, y_dv, color=NEG, sw=1.4, dash="5 4"))
        g.append(text(ax + umax + 36, y_dv + 4, "δ_v", size=14, italic=True, bold=True, color=NEG))

        # Профіль температури (червоний)
        t_pts = []
        for i in range(31):
            e = i / 30.0
            y = wall_y - e * (wall_y - top_y) * t_factor
            t_val = math.sin(math.pi / 2 * min(1.0, e)) * umax
            t_pts.append((ax + t_val, y))
        t_pts.append((ax + umax, top_y - 10))
        g.append(polyline([(ax, wall_y)] + t_pts, color=POS, sw=2.5, dash="7 3"))
        g.append(line(ax, y_dt, ax + umax + 20, y_dt, color=POS, sw=1.4, dash="3 3"))
        g.append(text(ax + umax + 36, y_dt + 4, "δ_t", size=14, italic=True, bold=True, color=POS))

        # Позначки профілів
        g.append(text(ax + umax * 0.4, wall_y - (wall_y - y_dv) * 0.5 - 12, "u(y)", size=12, italic=True, color=NEG, bold=True))
        g.append(text(ax + umax * 0.7, wall_y - (wall_y - y_dt) * 0.5 + 14, "T(y)", size=12, italic=True, color=POS, bold=True))

        # Співвідношення внизу
        g.append(text(ax + 125, wall_y + 48, pr_text, size=13, bold=True, color=INK))

        return "".join(g)

    # Три панелі
    f.append(draw_panel(40, "δ_t ≫ δ_v  (Pr ≪ 1)", "Pr ≪ 1 (Рідкі метали)", "Швидка температуропровідність", 0.35, 0.95))
    f.append(draw_panel(340, "δ_t ≈ δ_v  (Pr ≈ 1)", "Pr ≈ 1 (Гази: повітря)", "Однаковий темп переносу", 0.75, 0.78))
    f.append(draw_panel(640, "δ_t ≪ δ_v  (Pr ≫ 1)", "Pr ≫ 1 (В'язкі оливи)", "В'язкість домінує над теплом", 0.95, 0.30))

    return render(filepath, W, H, "".join(f))


# ── Фігура 2: Спектр чисел Прандтля ──────────────────────────────────────────
def fig_prandtl_spectrum(filepath):
    W, H = 920, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Спектр чисел Прандтля для різних речовин (при 20 °C)", size=18, bold=True))
    f.append(text(W / 2, 54, "Логарифмічна шкала охоплює понад 7 порядків величини: від 0.005 до 100 000",
                  size=12.5, color=MUTED))

    axis_y = 230
    x_min, x_max = 70, 850

    # Головна лінія шкали
    f.append(line(x_min - 10, axis_y, x_max + 10, axis_y, color=INK, sw=2.2))

    def val_to_x(val):
        log_v = math.log10(val)
        return x_min + (log_v - (-3.0)) / (5.0 - (-3.0)) * (x_max - x_min)

    exp_ticks = [-3, -2, -1, 0, 1, 2, 3, 4, 5]
    exp_labels = ["10⁻³", "10⁻²", "10⁻¹", "10⁰", "10¹", "10²", "10³", "10⁴", "10⁵"]

    for exp, lbl in zip(exp_ticks, exp_labels):
        x = val_to_x(10**exp)
        f.append(line(x, axis_y - 8, x, axis_y + 8, color=INK, sw=1.8))
        f.append(text(x, axis_y + 26, lbl, size=13, bold=True, color=INK))

    substances = [
        ("Рідкий натрій", 0.005, "Pr = 0.005", 110, POS, True),
        ("Ртуть", 0.025, "Pr = 0.025", 155, POS, True),
        ("Гелій", 0.66, "Pr = 0.66", 110, FIELD, True),
        ("Повітря", 0.71, "Pr = 0.71", 155, FIELD, True),
        ("Вода", 7.0, "Pr = 7.0", 310, NEG, False),
        ("Етанол", 16.0, "Pr = 16", 355, NEG, False),
        ("Моторна олива", 1000.0, "Pr ≈ 1000", 110, INK, True),
        ("Гліцерин", 10000.0, "Pr ≈ 10 000", 310, INK, False),
        ("Розплав полімеру", 100000.0, "Pr ≈ 100 000", 355, INK, False),
    ]

    for name, val, pr_str, box_y, col, is_top in substances:
        x = val_to_x(val)
        f.append(circle(x, axis_y, 5, fill=col, stroke=INK, sw=1.2))
        target_y = box_y + 14 if is_top else box_y - 14
        f.append(line(x, axis_y, x, target_y, color=col, sw=1.4, dash="3 3"))
        box_str = "%s\n%s" % (name, pr_str)
        box_w = max(text_width(name, 12, True), text_width(pr_str, 11, False)) + 16
        f.append(fitbox(x - box_w / 2, box_y - 15, box_w, 32, box_str, size=11.5, pad=4, fill="#ffffff", stroke=col, sw=1.4, rx=4))

    return render(filepath, W, H, "".join(f))


# ── Фігура 3: Перенос імпульсу та тепла ──────────────────────────────────────
def fig_heat_transfer_analogy(filepath):
    W, H = 880, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Перенос імпульсу та тепла на нагрітій плоскій пластині", size=18, bold=True))
    f.append(text(W / 2, 54, "Напруження тертя τ_w визначається ν, а стінковий тепловий потік q_w — коефіцієнтом α",
                  size=12.5, color=MUTED))

    wall_y = 380
    start_x = 120
    end_x = 800

    f.append(hatch_below(start_x - 30, end_x + 30, wall_y))
    f.append(text(start_x - 50, wall_y + 20, "Нагріта стінка (T_w > T_∞)", size=12, bold=True, color=POS))

    f.append(varrow(start_x - 80, 220, start_x - 20, 220, color=NEG, sw=2.2))
    f.append(text(start_x - 50, 195, "Потік U_∞, T_∞", size=13, bold=True, color=NEG))

    pts_v = []
    pts_t = []
    for i in range(41):
        x = start_x + (end_x - start_x) * (i / 40.0)
        dx = x - start_x
        y_v = wall_y - 15.0 * math.sqrt(max(0.0, dx))
        y_t = wall_y - 11.0 * math.sqrt(max(0.0, dx))
        pts_v.append((x, y_v))
        pts_t.append((x, y_t))

    f.append(path_fill([(start_x, wall_y)] + pts_v + [(end_x, wall_y)], "#eef2ff"))
    f.append(polyline(pts_v, color=NEG, sw=2.4))
    f.append(text(end_x + 30, pts_v[-1][1] - 4, "δ_v (імпульс)", size=12.5, bold=True, color=NEG))

    f.append(path_fill([(start_x, wall_y)] + pts_t + [(end_x, wall_y)], "#ffedd5"))
    f.append(polyline(pts_t, color=POS, sw=2.2, dash="6 3"))
    f.append(text(end_x + 30, pts_t[-1][1] + 12, "δ_t (тепло)", size=12.5, bold=True, color=POS))

    f.append(fitbox(240, 120, 220, 54, "Дифузія імпульсу (ν)\nτ_w = μ · (∂u/∂y)_(y=0)", size=12, fill="#ffffff", stroke=NEG, sw=1.5))
    f.append(fitbox(520, 120, 220, 54, "Дифузія тепла (α)\nq_w = -k · (∂T/∂y)_(y=0)", size=12, fill="#ffffff", stroke=POS, sw=1.5))

    for qx in [300, 450, 600, 720]:
        f.append(varrow(qx, wall_y - 4, qx, wall_y - 45, color=POS, sw=2.0))
        f.append(text(qx, wall_y - 52, "q_w", size=11, bold=True, color=POS))

    return render(filepath, W, H, "".join(f))


# ── Фігура 4: Залежність числа Прандтля від температури ─────────────────────
def fig_prandtl_temperature_dependence(filepath):
    W, H = 880, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Залежність числа Прандтля від температури", size=18, bold=True))
    f.append(text(W / 2, 54, "Різниця в поведінці рідин (вода) та газів (повітря) від 0 °C до 100 °C",
                  size=12.5, color=MUTED))

    ax_x0, ax_y0 = 100, 390
    graph_w, graph_h = 700, 280

    f.append(varrow(ax_x0, ax_y0, ax_x0 + graph_w + 30, ax_y0, color=INK, sw=2.0))
    f.append(text(ax_x0 + graph_w + 15, ax_y0 + 26, "Температура, °C", size=13, bold=True))

    f.append(varrow(ax_x0, ax_y0, ax_x0, ax_y0 - graph_h - 20, color=INK, sw=2.0))
    f.append(text(ax_x0 - 20, ax_y0 - graph_h - 15, "Pr", size=15, italic=True, bold=True))

    temps = [0, 20, 40, 60, 80, 100]
    for t in temps:
        x = ax_x0 + (t / 100.0) * graph_w
        f.append(line(x, ax_y0, x, ax_y0 + 6, color=INK, sw=1.5))
        f.append(text(x, ax_y0 + 22, str(t), size=12))

    def pr_to_y(pr):
        return ax_y0 - (pr / 14.0) * graph_h

    for pr_v in [0, 2, 4, 6, 8, 10, 12, 14]:
        y = pr_to_y(pr_v)
        f.append(line(ax_x0 - 6, y, ax_x0, y, color=INK, sw=1.5))
        f.append(text(ax_x0 - 20, y + 4, str(pr_v), size=12, anchor="end"))
        f.append(line(ax_x0, y, ax_x0 + graph_w, y, color="#f1f5f9", sw=1.0))

    water_pts_data = [(0, 13.7), (10, 9.5), (20, 7.0), (30, 5.4), (40, 4.3), (50, 3.5), (60, 3.0), (70, 2.55), (80, 2.2), (90, 1.95), (100, 1.75)]
    water_screen_pts = [(ax_x0 + (t / 100.0) * graph_w, pr_to_y(pr)) for t, pr in water_pts_data]
    f.append(polyline(water_screen_pts, color=NEG, sw=3.0))

    air_pts_data = [(0, 0.72), (20, 0.71), (40, 0.71), (60, 0.70), (80, 0.70), (100, 0.69)]
    air_screen_pts = [(ax_x0 + (t / 100.0) * graph_w, pr_to_y(pr)) for t, pr in air_pts_data]
    f.append(polyline(air_screen_pts, color=FIELD, sw=3.0, dash="6 3"))

    f.append(fitbox(520, 100, 260, 68, "Вода (рідина):\nPr стрімко падає з 13.7 до 1.75\nчерез експоненційне зниження в'язкості μ", size=11.5, fill="#eff6ff", stroke=NEG, sw=1.5))
    f.append(fitbox(520, 290, 260, 60, "Повітря (газ):\nPr майже не змінюється (≈ 0.71)\nчерез однакове масштабування ν і α", size=11.5, fill="#f0fdf4", stroke=FIELD, sw=1.5))

    return render(filepath, W, H, "".join(f))


if __name__ == '__main__':
    fig_boundary_layer_comparison(os.path.join(IMG, 'boundary-layer-comparison.svg'))
    fig_prandtl_spectrum(os.path.join(IMG, 'prandtl-spectrum.svg'))
    fig_heat_transfer_analogy(os.path.join(IMG, 'heat-transfer-analogy.svg'))
    fig_prandtl_temperature_dependence(os.path.join(IMG, 'prandtl-temperature-dependence.svg'))
    print("Фігури успішно згенеровано у ./img/")

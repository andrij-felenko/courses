# -*- coding: utf-8 -*-
"""Фігури до теми «Фазовий портрет».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

MAIN = "#2457d6"
ACCENT = "#c0392b"
BORDER = "#d0d7de"


def head_at(x, y, dx, dy, color=INK, size=8):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.4, by + ny * size * 0.4,
               bx - nx * size * 0.4, by - ny * size * 0.4, color))


def varrow(x1, y1, x2, y2, color=LINE, sw=2.0, head=9):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)


def polyline_arrow(pts, color=INK, sw=2.0, head=8):
    if len(pts) < 2:
        return ""
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    out = ['<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (p, color, sw)]
    x2, y2 = pts[-1]
    x1, y1 = pts[-2]
    out.append(head_at(x2, y2, x2 - x1, y2 - y1, color, head))
    return "".join(out)


# ── Фігура 1: Перехід від координати x(t) до фазового простору (q, p) ──────────
def fig_phase_space_concept():
    W, H = 840, 440
    f = []

    # Заголовок
    f.append(text(W / 2, 28, "Перехід від часової координати до фазового простору", size=17, bold=True))

    # Ліва панель: часові графіки x(t) та v(t)
    x0, y0 = 60, 75
    w_p, h_p = 320, 320
    f.append(rect(x0, y0, w_p, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(x0 + w_p / 2, y0 + 26, "Часове розгортання: q(t) та p(t)", size=14, bold=True))

    # Вісь часу t
    f.append(varrow(x0 + 35, y0 + 170, x0 + w_p - 15, y0 + 170, color=MUTED, sw=1.5))
    f.append(text(x0 + w_p - 20, y0 + 195, "час t", size=12, color=MUTED, anchor="end"))

    # Вісь амплітуди
    f.append(varrow(x0 + 45, y0 + 295, x0 + 45, y0 + 55, color=MUTED, sw=1.5))
    f.append(text(x0 + 40, y0 + 52, "величина", size=11, color=MUTED, anchor="end"))

    # Синусоїди
    pts_x = []
    pts_v = []
    for i in range(120):
        t = i / 119.0 * 2.5 * math.pi
        px = x0 + 45 + (i / 119.0) * 240
        py_x = y0 + 170 - 90 * math.sin(t)
        py_v = y0 + 170 - 90 * math.cos(t)
        pts_x.append((px, py_x))
        pts_v.append((px, py_v))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_x), MAIN))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="5,4"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_v), ACCENT))

    # Легенда зліва
    f.append(line(x0 + 55, y0 + 290, x0 + 85, y0 + 290, color=MAIN, sw=2.5))
    f.append(text(x0 + 92, y0 + 294, "координата q(t)", size=12, color=INK, anchor="start"))

    f.append(line(x0 + 185, y0 + 290, x0 + 215, y0 + 290, color=ACCENT, sw=2.0, dash="5,4"))
    f.append(text(x0 + 222, y0 + 294, "імпульс p(t)", size=12, color=INK, anchor="start"))

    # Пояснювальний шарнір (стрілка між панелями)
    f.append(varrow(x0 + w_p + 15, y0 + h_p / 2, x0 + w_p + 55, y0 + h_p / 2, color=ACCENT, sw=3.0, head=12))
    f.append(text(x0 + w_p + 35, y0 + h_p / 2 - 14, "згортання", size=11, color=ACCENT, bold=True))
    f.append(text(x0 + w_p + 35, y0 + h_p / 2 + 20, "часу t", size=11, color=ACCENT, bold=True))

    # Права панель: фазовий простір (q, p)
    x1, y1 = 460, 75
    f.append(rect(x1, y1, w_p, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(x1 + w_p / 2, y1 + 26, "Фазовий простір: траєкторія (q, p)", size=14, bold=True))

    cx, cy = x1 + w_p / 2, y1 + 170

    # Осі q та p
    f.append(varrow(x1 + 25, cy, x1 + w_p - 25, cy, color=MUTED, sw=1.5))
    f.append(text(x1 + w_p - 20, cy + 22, "координата q", size=12, color=MUTED, anchor="end"))

    f.append(varrow(cx, y1 + h_p - 25, cx, y1 + 55, color=MUTED, sw=1.5))
    f.append(text(cx + 12, y1 + 55, "імпульс p", size=12, color=MUTED, anchor="start"))

    # Фазова траєкторія (еліпс/коло)
    rx_e, ry_e = 100, 85
    pts_e = []
    for i in range(61):
        ang = i / 60.0 * 2 * math.pi
        px = cx + rx_e * math.cos(ang)
        py = cy - ry_e * math.sin(ang)
        pts_e.append((px, py))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_e), MAIN))

    # Стрілки напряму руху на фазовій траєкторії
    f.append(head_at(cx + 15, cy - ry_e, 1, 0, color=MAIN, size=10))
    f.append(head_at(cx - 15, cy + ry_e, -1, 0, color=MAIN, size=10))

    # Точка стану M(q, p) та фазова швидкість V
    mx, my = cx + rx_e * math.cos(math.pi / 4), cy - ry_e * math.sin(math.pi / 4)
    f.append(circle(mx, my, 5, fill=ACCENT, stroke=INK, sw=1.5))
    f.append(text(mx + 15, my - 12, "стан M(q, p)", size=12, color=INK, bold=True, anchor="start"))

    # Вектор фазової швидкості V = (q̇, ṗ)
    f.append(varrow(mx, my, mx - 35, my - 35, color=ACCENT, sw=2.2, head=9))
    f.append(text(mx - 42, my - 40, "V = (q̇, ṗ)", size=12, color=ACCENT, bold=True, anchor="end"))

    render(os.path.join(IMG, 'phase-space-concept.svg'), W, H, *f)


# ── Фігура 2: Фазовий портрет математичного маятника ──────────────────────────
def fig_pendulum_phase_portrait():
    W, H = 840, 500
    f = []

    f.append(text(W / 2, 28, "Фазовий портрет нелінійного математичного маятника", size=17, bold=True))

    cx, cy = W / 2, H / 2 + 10
    w_box, h_box = 780, 400
    x_min, x_max = cx - 360, cx + 360
    y_min, y_max = cy - 180, cy + 180

    f.append(rect(cx - w_box / 2, cy - h_box / 2, w_box, h_box, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))

    # Осі θ та p_θ
    f.append(varrow(x_min + 20, cy, x_max - 20, cy, color=MUTED, sw=1.5))
    f.append(text(x_max - 25, cy + 22, "кут θ (рад)", size=12, color=MUTED, anchor="end"))

    f.append(varrow(cx, y_max - 15, cx, y_min + 15, color=MUTED, sw=1.5))
    f.append(text(cx + 12, y_min + 20, "імпульс p_θ", size=12, color=MUTED, anchor="start"))

    dx_pi = 160
    labels = [("-2π", cx - 2 * dx_pi), ("-π", cx - dx_pi), ("0", cx), ("π", cx + dx_pi), ("2π", cx + 2 * dx_pi)]

    # Закриті овал-коливання навколо центрів (0, ±2π)
    for c_x in [cx - 2 * dx_pi, cx, cx + 2 * dx_pi]:
        for r_factor in [0.25, 0.55, 0.82]:
            rx = dx_pi * r_factor
            ry = 110 * r_factor
            pts = []
            for i in range(61):
                ang = i / 60.0 * 2 * math.pi
                px = c_x + rx * math.sin(ang)
                py = cy - ry * math.cos(ang)
                pts.append((px, py))
            f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' %
                     (" ".join("%.1f,%.1f" % p for p in pts), MAIN))

    # Сепаратриси (з'єднують сідлові точки -π, π)
    pts_sep_top = []
    pts_sep_bot = []
    for i in range(121):
        th = (i / 120.0 - 0.5) * 4 * math.pi
        px = cx + (th / (2 * math.pi)) * (2 * dx_pi)
        p_val = 145 * math.cos(th / 2.0)
        pts_sep_top.append((px, cy - abs(p_val)))
        pts_sep_bot.append((px, cy + abs(p_val)))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_sep_top), ACCENT))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_sep_bot), ACCENT))

    # Хвилясті траєкторії обертання (поза сепаратрисою)
    for shift_y in [165, 195]:
        pts_rot_top = []
        pts_rot_bot = []
        for i in range(121):
            th = (i / 120.0 - 0.5) * 4 * math.pi
            px = cx + (th / (2 * math.pi)) * (2 * dx_pi)
            p_val = shift_y + 20 * math.cos(th)
            pts_rot_top.append((px, cy - p_val))
            pts_rot_bot.append((px, cy + p_val))
        if y_min + 20 < cy - shift_y < y_max - 20:
            f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,3"/>' %
                     (" ".join("%.1f,%.1f" % p for p in pts_rot_top), LINE))
        if y_min + 20 < cy + shift_y < y_max - 20:
            f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,3"/>' %
                     (" ".join("%.1f,%.1f" % p for p in pts_rot_bot), LINE))

    # Позначення точок
    for lbl, lx in labels:
        f.append(line(lx, cy - 5, lx, cy + 5, color=INK, sw=1.5))
        f.append(text(lx, cy + 22, lbl, size=11, color=INK))

        is_saddle = (lbl in ["-π", "π"])
        if is_saddle:
            f.append(circle(lx, cy, 5.5, fill=ACCENT, stroke=INK, sw=1.5))
            f.append(text(lx, cy - 14, "сідло", size=11, color=ACCENT, bold=True))
        else:
            f.append(circle(lx, cy, 5.5, fill=MAIN, stroke=INK, sw=1.5))
            f.append(text(lx, cy - 14, "центр", size=11, color=MAIN, bold=True))

    f.append(text(cx, cy - 45, "Коливання (коливальні петлі)", size=12, color=MAIN, bold=True))
    f.append(text(cx + dx_pi, cy - 160, "Обертання (необмежений рух)", size=12, color=LINE, bold=True))
    f.append(text(cx - dx_pi + 45, cy - 95, "сепаратриса E = mgl", size=11, color=ACCENT, bold=True))

    render(os.path.join(IMG, 'pendulum-phase-portrait.svg'), W, H, *f)


# ── Фігура 3: Класифікація особливих точок (6 панелей) ──────────────────────────
def fig_singular_points_types():
    W, H = 840, 560
    f = []

    f.append(text(W / 2, 26, "Класифікація особливих точок у двовимірному фазовому просторі", size=17, bold=True))

    panels = [
        ("Сідло (нестійке)", "λ₁ > 0 > λ₂", "saddle"),
        ("Центр (консервативний)", "λ = ±iω", "center"),
        ("Стійкий фокус", "λ = α ± iω (α < 0)", "focus_stable"),
        ("Нестійкий фокус", "λ = α ± iω (α > 0)", "focus_unstable"),
        ("Стійкий вузол", "λ₂ < λ₁ < 0", "node_stable"),
        ("Нестійкий вузол", "λ₂ > λ₁ > 0", "node_unstable"),
    ]

    pw, ph = 240, 220
    cols = 3
    margin_x, margin_y = 30, 48
    gap_x, gap_y = 35, 30

    for idx, (title, math_str, ptype) in enumerate(panels):
        r_idx = idx // cols
        c_idx = idx % cols
        px0 = margin_x + c_idx * (pw + gap_x)
        py0 = margin_y + r_idx * (ph + gap_y)

        f.append(rect(px0, py0, pw, ph, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
        f.append(text(px0 + pw / 2, py0 + 20, title, size=13, bold=True))
        f.append(text(px0 + pw / 2, py0 + 36, math_str, size=11, color=MUTED))

        pcx, pcy = px0 + pw / 2, py0 + 130

        f.append(line(px0 + 20, pcy, px0 + pw - 20, pcy, color='#D0D7DE', sw=1.0))
        f.append(line(pcx, py0 + 50, pcx, py0 + ph - 20, color='#D0D7DE', sw=1.0))

        if ptype == "saddle":
            for sgn_x in [-1, 1]:
                for sgn_y in [-1, 1]:
                    pts = []
                    for t in range(25):
                        x_val = 15 + t * 3.5
                        y_val = 1500.0 / x_val
                        if x_val < 90 and y_val < 70:
                            pts.append((pcx + sgn_x * x_val, pcy - sgn_y * y_val))
                    if len(pts) > 2:
                        f.append(polyline_arrow(pts, color=LINE, sw=1.4))

            f.append(varrow(px0 + 25, py0 + ph - 25, pcx - 4, pcy + 4, color=ACCENT, sw=2.0))
            f.append(varrow(px0 + pw - 25, py0 + 55, pcx + 4, pcy - 4, color=ACCENT, sw=2.0))
            f.append(varrow(pcx + 4, pcy + 4, px0 + pw - 25, py0 + ph - 25, color=ACCENT, sw=2.0))
            f.append(varrow(pcx - 4, pcy - 4, px0 + 25, py0 + 55, color=ACCENT, sw=2.0))

        elif ptype == "center":
            for r in [25, 48, 70]:
                pts = []
                for i in range(41):
                    ang = i / 40.0 * 2 * math.pi
                    pts.append((pcx + r * 1.1 * math.cos(ang), pcy - r * 0.8 * math.sin(ang)))
                f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5"/>' %
                         (" ".join("%.1f,%.1f" % p for p in pts), MAIN))
                f.append(head_at(pcx, pcy - r * 0.8, 1, 0, color=MAIN, size=7))

        elif ptype == "focus_stable":
            pts = []
            for i in range(120):
                t = i / 120.0 * 4 * math.pi
                r = 75 * math.exp(-0.25 * t)
                pts.append((pcx + r * math.cos(t), pcy - r * math.sin(t)))
            f.append(polyline_arrow(pts, color=MAIN, sw=1.6))

        elif ptype == "focus_unstable":
            pts = []
            for i in range(120):
                t = i / 120.0 * 4 * math.pi
                r = 8 * math.exp(0.22 * t)
                if r < 78:
                    pts.append((pcx + r * math.cos(t), pcy - r * math.sin(t)))
            f.append(polyline_arrow(pts, color=ACCENT, sw=1.6))

        elif ptype == "node_stable":
            for angle in [0.3, 1.1, 2.2, 3.5, 4.4, 5.5]:
                pts = []
                for step in range(25):
                    t = 1.0 - step / 24.0
                    r = 75 * (t ** 1.3)
                    ang = angle + 0.2 * (1.0 - t)
                    pts.append((pcx + r * math.cos(ang), pcy - r * math.sin(ang)))
                f.append(polyline_arrow(pts, color=MAIN, sw=1.5))

        elif ptype == "node_unstable":
            for angle in [0.3, 1.1, 2.2, 3.5, 4.4, 5.5]:
                pts = []
                for step in range(25):
                    t = step / 24.0
                    r = 75 * (t ** 1.3)
                    ang = angle + 0.2 * t
                    pts.append((pcx + r * math.cos(ang), pcy - r * math.sin(ang)))
                f.append(polyline_arrow(pts, color=ACCENT, sw=1.5))

        pt_color = ACCENT if "unstable" in ptype or ptype == "saddle" else MAIN
        f.append(circle(pcx, pcy, 4.5, fill=pt_color, stroke=INK, sw=1.2))

    render(os.path.join(IMG, 'singular-points-types.svg'), W, H, *f)


# ── Фігура 4: Граничний цикл генератора Ван дер Поля ───────────────────────────
def fig_van_der_pol_limit_cycle():
    W, H = 840, 480
    f = []

    f.append(text(W / 2, 28, "Стійкий граничний цикл у генераторі Ван дер Поля", size=17, bold=True))

    cx, cy = W / 2, H / 2 + 15
    w_box, h_box = 760, 390

    f.append(rect(cx - w_box / 2, cy - h_box / 2, w_box, h_box, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))

    # Осі
    f.append(varrow(cx - 340, cy, cx + 340, cy, color=MUTED, sw=1.5))
    f.append(text(cx + 335, cy + 22, "зміщення x", size=12, color=MUTED, anchor="end"))

    f.append(varrow(cx, cy + 175, cx, cy - 175, color=MUTED, sw=1.5))
    f.append(text(cx + 12, cy - 170, "швидкість v = ẋ", size=12, color=MUTED, anchor="start"))

    # Граничний цикл
    pts_lc = []
    for i in range(101):
        ang = i / 100.0 * 2 * math.pi
        rx = 200 * math.cos(ang)
        ry = 135 * math.sin(ang) + 40 * math.sin(ang) * (math.cos(ang) ** 2)
        pts_lc.append((cx + rx, cy - ry))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.5"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_lc), ACCENT))

    f.append(head_at(cx + 10, cy - 175, 1, 0, color=ACCENT, size=11))
    f.append(head_at(cx - 10, cy + 175, -1, 0, color=ACCENT, size=11))

    # Внутрішня траєкторія
    pts_in = []
    for i in range(150):
        t = i / 149.0 * 5 * math.pi
        r_scale = (0.08 + 0.92 * (i / 149.0))
        rx = 195 * r_scale * math.cos(t)
        ry = (130 * r_scale + 38 * r_scale * (math.cos(t) ** 2)) * math.sin(t)
        pts_in.append((cx + rx, cy - ry))

    f.append(polyline_arrow(pts_in, color=MAIN, sw=1.6))

    # Зовнішня траєкторія
    pts_out = []
    for i in range(120):
        t = i / 119.0 * 3.5 * math.pi
        r_scale = (1.6 - 0.58 * (i / 119.0))
        rx = 198 * r_scale * math.cos(t + 0.5)
        ry = (132 * r_scale + 40 * r_scale * (math.cos(t + 0.5) ** 2)) * math.sin(t + 0.5)
        pts_out.append((cx + rx, cy - ry))

    f.append(polyline_arrow(pts_out, color=LINE, sw=1.6))

    f.append(circle(cx, cy, 5.5, fill=MAIN, stroke=INK, sw=1.5))
    f.append(text(cx + 12, cy + 16, "нестійкий фокус", size=11, color=MAIN, bold=True, anchor="start"))

    f.append(text(cx + 215, cy - 90, "стійкий граничний цикл", size=12, color=ACCENT, bold=True))
    f.append(text(cx + 80, cy - 50, "зростання зсередини", size=11, color=MAIN))
    f.append(text(cx - 240, cy - 140, "згасання ззовні", size=11, color=LINE))

    render(os.path.join(IMG, 'van-der-pol-limit-cycle.svg'), W, H, *f)


if __name__ == '__main__':
    fig_phase_space_concept()
    fig_pendulum_phase_portrait()
    fig_singular_points_types()
    fig_van_der_pol_limit_cycle()
    print("Фігури фазового портрета успішно згенеровано.")

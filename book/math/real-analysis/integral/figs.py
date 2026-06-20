# -*- coding: utf-8 -*-
"""Фігури для book/math/real-analysis/integral/integral.md
Генерує 5 SVG у ./img/  Запуск: python figs.py
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# F1: Стала швидкість → площа прямокутника  /  змінна → площа під кривою
# Три панелі: прямокутник, трикутник, крива
# ─────────────────────────────────────────────────────────────
def fig_f1():
    W, H = 660, 220
    frags = []

    def axes(ox, oy, aw, ah, lx, ly):
        out = []
        out.append(arrow(ox, oy, ox + aw, oy, color=MUTED))
        out.append(arrow(ox, oy, ox, oy - ah, color=MUTED))
        out.append(text(ox + aw + 4, oy + 4, lx, size=12, color=MUTED, anchor="start"))
        out.append(text(ox - 4, oy - ah - 4, ly, size=12, color=MUTED, anchor="end"))
        return "".join(out)

    # ── Панель 1: прямокутник (стала v)
    ox1, oy = 45, 185
    aw, ah = 130, 130
    v = 80   # висота прямокутника
    t_end = 110
    frags.append(axes(ox1, oy, aw, ah, "t", "v"))
    # заповнений прямокутник
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#dbeafe" stroke="#2457d6" stroke-width="1.5"/>'
                 % (ox1, oy - v, t_end, v))
    # горизонтальна лінія v=const
    frags.append(line(ox1, oy - v, ox1 + t_end, oy - v, color=NEG, sw=2.2))
    # підпис площі
    frags.append(text(ox1 + t_end / 2, oy - v / 2, "v·t = шлях", size=11, color=NEG))
    frags.append(text(ox1 + aw / 2, oy + 18, "стала v", size=12, color=MUTED))

    # ── Панель 2: трикутник (v = a·t)
    ox2 = 220
    frags.append(axes(ox2, oy, aw, ah, "t", "v"))
    t2 = 110
    v2_top = 90
    pts = f"{ox2},{oy} {ox2},{oy - 0} {ox2 + t2},{oy - v2_top} {ox2 + t2},{oy}"
    frags.append('<polygon points="%s" fill="#dbeafe" stroke="#2457d6" stroke-width="1.5"/>' % pts)
    frags.append(line(ox2, oy, ox2 + t2, oy - v2_top, color=NEG, sw=2.2))
    frags.append(text(ox2 + t2 / 2 + 10, oy - v2_top / 3, "½·v·t", size=11, color=NEG))
    frags.append(text(ox2 + aw / 2, oy + 18, "лінійне v", size=12, color=MUTED))

    # ── Панель 3: довільна крива
    ox3 = 395
    frags.append(axes(ox3, oy, aw, ah, "t", "v"))
    # точки кривої (щось хвилясте)
    pts_c = [(0, 30), (18, 55), (35, 90), (55, 70), (75, 100), (95, 80), (110, 95)]
    # побудуємо полігон заповнення під кривою
    poly_pts = f"{ox3},{oy} "
    poly_pts += " ".join(f"{ox3 + px},{oy - py}" for px, py in pts_c)
    poly_pts += f" {ox3 + 110},{oy}"
    frags.append('<polygon points="%s" fill="#dbeafe"/>' % poly_pts)
    # сама крива (polyline)
    curve_pts = " ".join(f"{ox3 + px},{oy - py}" for px, py in pts_c)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>'
                 % (curve_pts, NEG))
    frags.append(text(ox3 + 55, oy - 40, "∫v dt", size=13, color=NEG))
    frags.append(text(ox3 + aw / 2, oy + 18, "довільна v(t)", size=12, color=MUTED))

    # Заголовок
    frags.append(text(W / 2, 20, "Площа під графіком швидкості = пройдений шлях", size=14, bold=True))

    render(os.path.join(OUT, "f1-area-is-distance.svg"), W, H, *frags)

# ─────────────────────────────────────────────────────────────
# F2: Драбинка прямокутників — груба й дрібна (сума Рімана)
# ─────────────────────────────────────────────────────────────
def fig_f2():
    W, H = 640, 230
    frags = []

    def curve_y(x, scale=1.0):
        return 40 + 70 * math.sin(x * 0.045 * scale) * math.exp(-x * 0.003 * scale)

    def draw_panel(ox, oy, aw, ah, n_bars, label):
        out = []
        out.append(arrow(ox, oy, ox + aw + 10, oy, color=MUTED))
        out.append(arrow(ox, oy, ox, oy - ah - 10, color=MUTED))
        out.append(text(ox + aw + 14, oy + 4, "t", size=12, color=MUTED, anchor="start"))
        out.append(text(ox - 4, oy - ah - 14, "v", size=12, color=MUTED, anchor="end"))
        dx = aw / n_bars
        # прямокутники (ліво-кутні суми)
        for i in range(n_bars):
            x0 = i * dx
            cv = curve_y(x0 + dx / 2)
            bar_fill = "#dbeafe"
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="%s" stroke-width="0.8"/>'
                       % (ox + x0, oy - cv, dx, cv, bar_fill, "#2457d6"))
        # крива поверх
        n_pts = 80
        pts = []
        for i in range(n_pts + 1):
            xv = i * aw / n_pts
            pts.append((ox + xv, oy - curve_y(xv)))
        pts_str = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
                   % (pts_str, NEG))
        out.append(text(ox + aw / 2, oy + 20, label, size=12, color=MUTED))
        return "".join(out)

    # Ліва панель: 6 товстих прямокутників
    frags.append(draw_panel(45, 195, 240, 130, 6, "6 широких — груба «драбинка»"))
    # Права панель: 24 вузьких
    frags.append(draw_panel(355, 195, 240, 130, 24, "24 вузьких — ближче до кривої"))

    frags.append(text(W / 2, 20, "Сума Рімана: дрібніший крок → похибка менша", size=14, bold=True))
    render(os.path.join(OUT, "f2-riemann-sum.svg"), W, H, *frags)

# ─────────────────────────────────────────────────────────────
# F3: Площа з мінусом — від'ємна швидкість
# ─────────────────────────────────────────────────────────────
def fig_f3():
    W, H = 520, 240
    frags = []

    ox, oy = 60, 130
    aw, ah = 390, 100

    frags.append(arrow(ox, oy, ox + aw + 10, oy, color=MUTED))
    frags.append(arrow(ox, oy, ox, oy - ah - 10, color=MUTED))
    frags.append(arrow(ox, oy, ox, oy + ah + 10, color=MUTED))
    frags.append(text(ox + aw + 14, oy + 4, "t", size=12, color=MUTED, anchor="start"))
    frags.append(text(ox - 4, oy - ah - 14, "v", size=12, color=MUTED, anchor="end"))

    # крива: спочатку позитивна, потім негативна
    def v_curve(t):
        return 70 * math.sin(t * math.pi / 190)

    n = 200
    # заповнення позитивної зони (0..190)
    plus_pts = f"{ox},{oy}"
    for i in range(100):
        t = i * 190.0 / 99
        y = v_curve(t)
        plus_pts += f" {ox + t:.1f},{oy - y:.1f}"
    plus_pts += f" {ox + 190},{oy}"
    frags.append('<polygon points="%s" fill="#d1fae5" stroke="none"/>' % plus_pts)

    # заповнення негативної зони (190..380)
    minus_pts = f"{ox + 190},{oy}"
    for i in range(100):
        t = 190 + i * 190.0 / 99
        y = v_curve(t)
        minus_pts += f" {ox + t:.1f},{oy - y:.1f}"
    minus_pts += f" {ox + 380},{oy}"
    frags.append('<polygon points="%s" fill="#fee2e2" stroke="none"/>' % minus_pts)

    # крива
    curve_pts = " ".join(f"{ox + i * aw / n:.1f},{oy - v_curve(i * aw / n):.1f}" for i in range(n + 1))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (curve_pts, INK))

    # підписи зон
    frags.append(text(ox + 95, oy - 38, "+площа", size=13, color=FIELD))
    frags.append(text(ox + 285, oy + 42, "−площа", size=13, color=POS))
    frags.append(text(ox + 190, oy + 20, "v=0", size=11, color=MUTED))

    frags.append(text(W / 2, 20, "Від'ємна швидкість → від'ємна площа = від'ємне зміщення", size=13, bold=True))
    render(os.path.join(OUT, "f3-signed-area.svg"), W, H, *frags)

# ─────────────────────────────────────────────────────────────
# F4: Похідна й інтеграл — обернені стрілки
# ─────────────────────────────────────────────────────────────
def fig_f4():
    W, H = 460, 160
    frags = []

    # Ліва рамка — шлях s(t)
    b1, w1, h1 = 90, 140, 54
    box1, _, _ = textbox(b1, H // 2, "шлях  s(t)", size=15, fill="#dbeafe", stroke=NEG, sw=2, min_w=w1)
    frags.append(box1)

    # Права рамка — швидкість v(t)
    b2 = 370
    box2, _, _ = textbox(b2, H // 2, "швидкість  v(t)", size=15, fill="#d1fae5", stroke=FIELD, sw=2, min_w=w1)
    frags.append(box2)

    # Стрілка вправо: похідна d/dt
    x_left = b1 + w1 // 2 + 10
    x_right = b2 - w1 // 2 - 10
    mid_x = (x_left + x_right) / 2
    y_up = H // 2 - 28
    y_dn = H // 2 + 28
    frags.append(arrow(x_left, y_up, x_right, y_up, color=INK, sw=2.0))
    frags.append(text(mid_x, y_up - 10, "похідна   d/dt", size=13, color=INK))

    # Стрілка вліво: інтеграл ∫dt
    frags.append(arrow(x_right, y_dn, x_left, y_dn, color=NEG, sw=2.0))
    frags.append(text(mid_x, y_dn + 17, "інтеграл  ∫ dt", size=13, color=NEG))

    render(os.path.join(OUT, "f4-ftc-arrows.svg"), W, H, *frags)

# ─────────────────────────────────────────────────────────────
# F5: Один шаблон ∫ — три приклади накопичення
# ─────────────────────────────────────────────────────────────
def fig_f5():
    W, H = 580, 200
    frags = []

    # Центральна рамка — формула ∫
    cx = W // 2
    cy = H // 2
    center_box, cw, ch = textbox(cx, cy, "∫ (швидкість) dt\n= накопичена величина",
                                  size=14, fill="#f0fdf4", stroke=FIELD, sw=2.5, min_w=200)
    frags.append(center_box)

    half_cw = cw / 2

    # Ліво-верхній приклад
    lx, ly = 95, 55
    b1, _, _ = textbox(lx, ly, "v(t)  →  s", size=13, fill="#dbeafe", stroke=NEG, sw=1.5, min_w=110)
    frags.append(b1)
    frags.append(arrow(lx + 60, ly + 18, cx - half_cw - 4, cy - 10, color=MUTED, sw=1.4))

    # Ліво-нижній приклад
    lx2, ly2 = 95, H - 55
    b2, _, _ = textbox(lx2, ly2, "i(t)  →  q", size=13, fill="#dbeafe", stroke=NEG, sw=1.5, min_w=110)
    frags.append(b2)
    frags.append(arrow(lx2 + 60, ly2 - 18, cx - half_cw - 4, cy + 10, color=MUTED, sw=1.4))

    # Право-верхній приклад
    rx, ry = W - 95, 55
    b3, _, _ = textbox(rx, ry, "P(t)  →  E", size=13, fill="#d1fae5", stroke=FIELD, sw=1.5, min_w=110)
    frags.append(b3)
    frags.append(arrow(rx - 60, ry + 18, cx + half_cw + 4, cy - 10, color=MUTED, sw=1.4))

    # Право-нижній приклад
    rx2, ry2 = W - 95, H - 55
    b4, _, _ = textbox(rx2, ry2, "Q(t)  →  V", size=13, fill="#d1fae5", stroke=FIELD, sw=1.5, min_w=110)
    frags.append(b4)
    frags.append(arrow(rx2 - 60, ry2 - 18, cx + half_cw + 4, cy + 10, color=MUTED, sw=1.4))

    # Підписи малим шрифтом під прикладами
    frags.append(text(lx, ly + 32, "швидкість → шлях", size=10, color=MUTED))
    frags.append(text(lx2, ly2 + 32, "струм → заряд", size=10, color=MUTED))
    frags.append(text(rx, ry + 32, "потужність → енергія", size=10, color=MUTED))
    frags.append(text(rx2, ry2 + 32, "витрата → об'єм", size=10, color=MUTED))

    render(os.path.join(OUT, "f5-integral-template.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_f1()
    fig_f2()
    fig_f3()
    fig_f4()
    fig_f5()
    print("Done — 5 SVG written to", OUT)

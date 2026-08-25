# -*- coding: utf-8 -*-
"""Фігури до теми «Закон Гаусса».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_BLUE = "#2457d6"
COLOR_RED = "#c0392b"
COLOR_GREEN = "#27ae60"
COLOR_ORANGE = "#d35400"
COLOR_PURPLE = "#8e44ad"

def helper_polygon(points, fill=FILL, stroke=LINE, sw=1.5):
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts, fill, stroke, sw)

def helper_path(d, color=None, stroke=None, sw=1.5, fill="none", dash=None):
    c = stroke or color or LINE
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d, c, sw, fill, d_attr)

def helper_ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (cx, cy, rx, ry, fill, stroke, sw, d))

def helper_dashed_circle(cx, cy, r, fill=FILL, stroke=LINE, sw=1.5, dash="6,4"):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"/>' % (cx, cy, r, fill, stroke, sw, dash))

polygon = helper_polygon
path = helper_path
ellipse = helper_ellipse
dashed_circle = helper_dashed_circle


# ── Фігура 1: Потік електричного поля через майданчик ───────────────────────
def fig_flux_concept():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Потік векторного поля E через похилений майданчик dA", size=16, bold=True))

    cx, cy = 320, 190
    f.append(polygon([(cx - 100, cy + 50), (cx + 40, cy + 50), (cx + 100, cy - 50), (cx - 40, cy - 50)],
                     fill="#eef6ff", stroke=COLOR_BLUE, sw=2))
    f.append(text(cx - 30, cy + 30, "Майданчик dA", size=13, bold=True, color=COLOR_BLUE))

    f.append(arrow(cx, cy, cx + 70, cy - 110, color=COLOR_RED, sw=2.2))
    f.append(text(cx + 80, cy - 115, "n̂ (орт нормалі)", size=13, bold=True, color=COLOR_RED, anchor="start"))

    for x_off in [-60, 0, 60]:
        f.append(arrow(cx + x_off, cy + 80, cx + x_off, cy - 120, color=COLOR_GREEN, sw=2))
    f.append(text(cx + 5, cy - 130, "E (вектор поля)", size=13, bold=True, color=COLOR_GREEN))

    f.append(path("M %d %d A 45 45 0 0 1 %d %d" % (cx, cy - 45, cx + 28, cy - 40), color=COLOR_ORANGE, sw=1.8, fill="none"))
    f.append(text(cx + 22, cy - 55, "θ", size=14, bold=True, color=COLOR_ORANGE))

    b, w, h = textbox(585, 190,
                      "Проекція поля на нормаль:\nE_n = E · cos(θ)\n\nЕлементарний потік:\ndΦ_E = E · dA\n    = E · n̂ · dA\n    = E · cos(θ) · dA",
                      size=12, pad=10, fill="#eafaf1", stroke="#a3e4d7", sw=1.4)
    f.append(b)

    return render(os.path.join(IMG, "flux-concept.svg"), W, H, *f)


# ── Фігура 2: Тілесний кут і незалежність потоку від поверхні ──────────────
def fig_solid_angle():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Тілесний кут dΩ та збереження потоку для закону 1/r²", size=16, bold=True))

    ox, oy = 80, 190
    f.append(circle(ox, oy, 14, fill="#fdecea", stroke=COLOR_RED, sw=2))
    f.append(text(ox, oy + 5, "+q", size=13, bold=True, color=COLOR_RED))

    f.append(line(ox, oy, ox + 370, oy - 120, color=MUTED, sw=1.2, dash="4,3"))
    f.append(line(ox, oy, ox + 370, oy + 100, color=MUTED, sw=1.2, dash="4,3"))

    r1 = 150
    f.append(path("M %d %d A %d %d 0 0 1 %d %d" % (ox + 136, oy - 45, r1, r1, ox + 143, oy + 39),
                  color=COLOR_BLUE, sw=2.5, fill="none"))
    f.append(text(ox + 155, oy - 55, "dA1 (відстань r1)", size=12, bold=True, color=COLOR_BLUE, anchor="start"))

    f.append(path("M %d %d L %d %d" % (ox + 260, oy - 90, ox + 285, oy + 75),
                  color=COLOR_PURPLE, sw=2.5, fill="none"))
    f.append(text(ox + 275, oy - 100, "dA2 (відстань r2, кут θ)", size=12, bold=True, color=COLOR_PURPLE, anchor="start"))

    f.append(path("M %d %d A 50 50 0 0 1 %d %d" % (ox + 48, oy - 15, ox + 50, oy + 13), color=COLOR_ORANGE, sw=1.8, fill="none"))
    f.append(text(ox + 65, oy + 3, "dΩ", size=13, bold=True, color=COLOR_ORANGE))

    b, w, h = textbox(575, 190,
                      "Площа сферичного майданчика:\ndA1 = r1² · dΩ\n\nПотік Кулонівського поля:\ndΦ_E = (q / 4πε₀r1²) · dA1\n     = (q / 4πε₀) · dΩ\n\nПотік однаковий через будь-який\nпереріз конуса!",
                      size=12, pad=10, fill="#eef6ff", stroke="#99ccff", sw=1.4)
    f.append(b)

    return render(os.path.join(IMG, "solid-angle.svg"), W, H, *f)


# ── Фігура 3: Сферична симетрія (точковий заряд і куля) ───────────────────
def fig_spherical_symmetry():
    W, H = 740, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Закон Гаусса для сферично симетричних систем", size=16, bold=True))

    midx = W / 2
    f.append(line(midx, 50, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    cx1, cy1 = 180, 200
    f.append(dashed_circle(cx1, cy1, 100, fill="#f4f8ff", stroke=COLOR_BLUE, sw=2, dash="6,4"))
    f.append(text(cx1 + 10, cy1 - 108, "Гауссова сфера S (радіус r)", size=11, bold=True, color=COLOR_BLUE, anchor="middle"))

    f.append(circle(cx1, cy1, 12, fill="#fdecea", stroke=COLOR_RED, sw=2))
    f.append(text(cx1, cy1 + 4, "+Q", size=12, bold=True, color=COLOR_RED))

    for ang in [0, 45, 90, 135, 180, 225, 270, 315]:
        dx = 100 * (1 if ang in [0, 45, 315] else (-1 if ang in [135, 180, 225] else 0))
        dy = 100 * (1 if ang in [90, 45, 135] else (-1 if ang in [270, 225, 315] else 0))
        if ang in [45, 135, 225, 315]:
            dx, dy = dx * 0.707, dy * 0.707
        f.append(arrow(cx1 + dx * 0.3, cy1 + dy * 0.3, cx1 + dx * 1.3, cy1 + dy * 1.3, color=COLOR_GREEN, sw=1.8))
    f.append(text(cx1 + 122, cy1 + 15, "E ⊥ S", size=12, bold=True, color=COLOR_GREEN, anchor="start"))

    b1, w1, h1 = textbox(cx1, 335, "∮ E · dA = E · (4πr²) = Q / ε₀\nE(r) = Q / (4πε₀r²)",
                          size=12, pad=7, fill="#eafaf1", stroke="#a3e4d7", sw=1.2)
    f.append(b1)

    cx2, cy2 = 540, 200
    f.append(circle(cx2, cy2, 60, fill="#fff4e6", stroke=COLOR_ORANGE, sw=2))
    f.append(text(cx2, cy2 - 25, "Заряджена куля (R, ρ)", size=11, bold=True, color=COLOR_ORANGE))

    f.append(dashed_circle(cx2, cy2, 35, fill="none", stroke=COLOR_BLUE, sw=1.8, dash="4,3"))
    f.append(text(cx2 - 25, cy2 + 10, "r < R", size=10, bold=True, color=COLOR_BLUE))

    f.append(dashed_circle(cx2, cy2, 95, fill="none", stroke=COLOR_BLUE, sw=1.8, dash="6,4"))
    f.append(text(cx2 + 10, cy2 - 102, "r > R", size=10, bold=True, color=COLOR_BLUE, anchor="middle"))

    b2, w2, h2 = textbox(cx2, 335, "Зовні (r > R): E = Q / (4πε₀r²)\nВсередині (r < R): E = Q·r / (4πε₀R³)",
                          size=12, pad=7, fill="#eef6ff", stroke="#99ccff", sw=1.2)
    f.append(b2)

    return render(os.path.join(IMG, "spherical-symmetry.svg"), W, H, *f)


# ── Фігура 4: Циліндрична симетрія (нитка та циліндр) ─────────────────────
def fig_cylindrical_symmetry():
    W, H = 740, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Гауссовий циліндр для нескінченної зарядженої нитки", size=16, bold=True))

    cx, cy = 270, 190

    # Заряджена нитка уздовж осі Z
    f.append(line(cx, 55, cx, 315, color=COLOR_RED, sw=3))
    f.append(text(cx - 110, 48, "Нитка (густина λ)", size=12, bold=True, color=COLOR_RED, anchor="start"))
    for y_p in range(90, 300, 35):
        f.append(text(cx + 10, y_p, "+", size=12, bold=True, color=COLOR_RED, anchor="start"))

    rx_cyl, ry_cyl = 110, 28
    h_cyl = 160
    top_y = cy - h_cyl / 2
    bot_y = cy + h_cyl / 2

    f.append(line(cx - rx_cyl, top_y, cx - rx_cyl, bot_y, color=COLOR_BLUE, sw=1.8, dash="5,4"))
    f.append(line(cx + rx_cyl, top_y, cx + rx_cyl, bot_y, color=COLOR_BLUE, sw=1.8, dash="5,4"))

    f.append(ellipse(cx, top_y, rx_cyl, ry_cyl, fill="#eef6ff", stroke=COLOR_BLUE, sw=1.8))
    f.append(ellipse(cx, bot_y, rx_cyl, ry_cyl, fill="#eef6ff", stroke=COLOR_BLUE, sw=1.8, dash="5,4"))

    f.append(arrow(cx + rx_cyl, cy - 20, cx + rx_cyl + 60, cy - 20, color=COLOR_GREEN, sw=2.2))
    f.append(text(cx + rx_cyl + 65, cy - 20, "E (радіальне)", size=11, bold=True, color=COLOR_GREEN, anchor="start"))

    f.append(arrow(cx - rx_cyl, cy - 20, cx - rx_cyl - 60, cy - 20, color=COLOR_GREEN, sw=2.2))
    f.append(text(cx - rx_cyl - 65, cy - 20, "E (радіальне)", size=11, bold=True, color=COLOR_GREEN, anchor="end"))

    f.append(arrow(cx + 50, top_y, cx + 50, top_y - 30, color=COLOR_RED, sw=1.6))
    f.append(text(cx + 58, top_y - 20, "n̂_top (E ⊥ n̂ → Φ=0)", size=10, bold=True, color=COLOR_RED, anchor="start"))

    f.append(line(cx, cy + 20, cx + rx_cyl, cy + 20, color=LINE, sw=1.4, dash="3,3"))
    f.append(text(cx + rx_cyl / 2, cy + 34, "r", size=12, bold=True, color=INK))

    f.append(line(cx + rx_cyl + 20, top_y, cx + rx_cyl + 20, bot_y, color=LINE, sw=1.4))
    f.append(text(cx + rx_cyl + 26, cy, "L", size=12, bold=True, color=INK))

    b, w, h = textbox(585, 190,
                      "Потік через кришки:\nΦ_caps = 0  (бо E ⊥ n̂)\n\nПотік через бічну стінку:\nΦ_side = E · (2πrL)\n\nВнутрішній заряд:\nQ_enclosed = λ · L\n\nЕлектричне поле:\nE = λ / (2πε₀r)",
                      size=12, pad=10, fill="#eafaf1", stroke="#a3e4d7", sw=1.4)
    f.append(b)

    return render(os.path.join(IMG, "cylindrical-symmetry.svg"), W, H, *f)


# ── Фігура 5: Плоска симетрія (заряджена площина) ──────────────────────────
def fig_planar_symmetry():
    W, H = 740, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Гауссовий циліндрик («таблетка») для нескінченної площини", size=16, bold=True))

    cx, cy = 250, 190

    f.append(polygon([(cx, 60), (cx + 50, 100), (cx + 50, 310), (cx, 270)],
                     fill="#fff4e6", stroke=COLOR_ORANGE, sw=2))
    f.append(text(cx + 60, 75, "Площина (густина σ)", size=12, bold=True, color=COLOR_ORANGE, anchor="start"))
    for y_p in range(120, 270, 40):
        f.append(text(cx + 20, y_p, "+", size=13, bold=True, color=COLOR_RED))

    w_pill = 160
    h_pill = 50
    left_x = cx + 25 - w_pill / 2
    right_x = cx + 25 + w_pill / 2

    f.append(line(left_x, cy - h_pill / 2, right_x, cy - h_pill / 2, color=COLOR_BLUE, sw=1.6, dash="5,4"))
    f.append(line(left_x, cy + h_pill / 2, right_x, cy + h_pill / 2, color=COLOR_BLUE, sw=1.6, dash="5,4"))

    f.append(ellipse(left_x, cy, 16, h_pill / 2, fill="#eef6ff", stroke=COLOR_BLUE, sw=1.8))
    f.append(ellipse(right_x, cy, 16, h_pill / 2, fill="#eef6ff", stroke=COLOR_BLUE, sw=1.8))

    f.append(arrow(right_x, cy, right_x + 45, cy, color=COLOR_GREEN, sw=2.2))
    f.append(text(right_x + 50, cy + 4, "E (вправо)", size=11, bold=True, color=COLOR_GREEN, anchor="start"))

    f.append(arrow(left_x, cy, left_x - 45, cy, color=COLOR_GREEN, sw=2.2))
    f.append(text(left_x - 50, cy + 4, "E (вліво)", size=11, bold=True, color=COLOR_GREEN, anchor="end"))

    f.append(text(cx + 25, cy - h_pill / 2 - 14, "Φ_wall = 0 (E ∥ стінці)", size=11, bold=True, color=MUTED, anchor="middle"))

    b, w, h = textbox(585, 190,
                      "Потік через два денця:\nΦ_E = E · A + E · A\n    = 2 · E · A\n\nЗаряд усередині:\nQ_enclosed = σ · A\n\nРівняння Гаусса:\n2 · E · A = (σ · A) / ε₀\n\nЕлектричне поле:\nE = σ / (2ε₀)  (однорідне!)",
                      size=12, pad=10, fill="#eafaf1", stroke="#a3e4d7", sw=1.4)
    f.append(b)

    return render(os.path.join(IMG, "planar-symmetry.svg"), W, H, *f)


# ── Фігура 6: Провідник в електростатичній рівновазі та клітка Фарадея ─────
def fig_conductor_charge():
    W, H = 740, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Розподіл заряду та екранування у провіднику (E = 0 у товщі)", size=16, bold=True))

    midx = W / 2
    f.append(line(midx, 50, midx, H - 20, color="#d6dde6", sw=1.4, dash="5,5"))

    cx1, cy1 = 180, 195
    f.append(path("M 70 180 Q 110 100 200 110 T 290 200 T 210 280 T 90 250 Z",
                  fill="#eaeded", stroke="#7f8c8d", sw=2))
    f.append(text(cx1, cy1 - 10, "Провідник\nE = 0 усередині", size=12, bold=True, color=INK, anchor="middle"))

    for px, py in [(95, 115), (145, 105), (200, 115), (250, 150), (280, 200), (235, 265), (170, 275), (105, 245), (75, 195)]:
        f.append(text(px, py, "+", size=13, bold=True, color=COLOR_RED))

    f.append(path("M 100 180 Q 125 130 180 135 T 240 195 T 190 245 T 115 220 Z",
                  color=COLOR_BLUE, sw=1.8, fill="none", dash="4,3"))
    f.append(text(cx1, cy1 + 35, "S_int (Q_enc = 0)", size=10, bold=True, color=COLOR_BLUE, anchor="middle"))

    b1, w1, h1 = textbox(cx1, 335, "У товщі провідника E = 0\nЗаряд витісняється на поверхню!",
                          size=11, pad=7, fill="#eef6ff", stroke="#99ccff", sw=1.2)
    f.append(b1)

    cx2, cy2 = 540, 195
    f.append(rect(430, 100, 220, 170, fill="#eaeded", stroke="#7f8c8d", sw=2, rx=20))
    f.append(rect(470, 130, 140, 110, fill="#ffffff", stroke="#7f8c8d", sw=1.8, rx=12))

    f.append(text(cx2, cy2 - 10, "Порожнина\nE_cavity = 0", size=12, bold=True, color=COLOR_GREEN, anchor="middle"))

    for y_line in [120, 160, 200, 240]:
        f.append(arrow(385, y_line, 425, y_line, color=COLOR_BLUE, sw=1.8))
    f.append(text(405, 95, "Зовнішнє поле E₀", size=11, bold=True, color=COLOR_BLUE))

    b2, w2, h2 = textbox(cx2, 335, "Електростатичне екранування:\nПоле не проникає в порожнину",
                          size=11, pad=7, fill="#eafaf1", stroke="#a3e4d7", sw=1.2)
    f.append(b2)

    return render(os.path.join(IMG, "conductor-charge.svg"), W, H, *f)


# ── Фігура 7: Диференціальна форма та елемент об'єму dx dy dz ─────────────
def fig_divergence_box():
    W, H = 740, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Дивергенція ∇ · E як локальна густина джерел поля у кубику dV", size=16, bold=True))

    cx, cy = 270, 200
    dx, dy, dz = 120, 70, 90

    f.append(rect(cx - dx / 2 + 30, cy - dz / 2 - 30, dx, dz, fill="none", stroke=MUTED, sw=1, rx=0))
    f.append(rect(cx - dx / 2, cy - dz / 2, dx, dz, fill="#eef6ff", stroke=COLOR_BLUE, sw=2, rx=0))

    f.append(line(cx - dx / 2, cy - dz / 2, cx - dx / 2 + 30, cy - dz / 2 - 30, color=COLOR_BLUE, sw=1.5))
    f.append(line(cx + dx / 2, cy - dz / 2, cx + dx / 2 + 30, cy - dz / 2 - 30, color=COLOR_BLUE, sw=1.5))
    f.append(line(cx - dx / 2, cy + dz / 2, cx - dx / 2 + 30, cy + dz / 2 - 30, color=COLOR_BLUE, sw=1.5))
    f.append(line(cx + dx / 2, cy + dz / 2, cx + dx / 2 + 30, cy + dz / 2 - 30, color=COLOR_BLUE, sw=1.5))

    f.append(arrow(cx - dx / 2 - 60, cy, cx - dx / 2, cy, color=COLOR_GREEN, sw=2))
    f.append(text(cx - dx / 2 - 65, cy - 8, "Ex(x)", size=11, bold=True, color=COLOR_GREEN, anchor="end"))

    f.append(arrow(cx + dx / 2, cy, cx + dx / 2 + 65, cy, color=COLOR_GREEN, sw=2))
    f.append(text(cx + dx / 2 + 70, cy - 8, "Ex(x + dx)", size=11, bold=True, color=COLOR_GREEN, anchor="start"))

    f.append(circle(cx + 15, cy - 15, 10, fill="#fdecea", stroke=COLOR_RED, sw=1.5))
    f.append(text(cx + 15, cy - 11, "+ρ", size=11, bold=True, color=COLOR_RED))

    b, w, h = textbox(585, 190,
                      "Різниця потоків по X:\nΔΦ_x = (∂Ex / ∂x) · dx dy dz\n\nСумарний потік з кубика:\ndΦ_E = (∇ · E) · dV\n\nЗаряд у кубику:\ndQ = ρ · dV\n\nРівняння Максвелла I:\n∇ · E = ρ / ε₀",
                      size=12, pad=10, fill="#eafaf1", stroke="#a3e4d7", sw=1.4)
    f.append(b)

    return render(os.path.join(IMG, "divergence-box.svg"), W, H, *f)


# ── Фігура 8: Закон Гаусса у діелектрику (вектор зсуву D) ──────────────────
def fig_dielectric_polarization():
    W, H = 740, 380
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Поляризація діелектрика, зв'язані заряди та вектор зсуву D", size=16, bold=True))

    cx, cy = 290, 195

    f.append(rect(cx - 150, cy - 90, 300, 180, fill="#fff9db", stroke="#f59f00", sw=2, rx=8))
    f.append(text(cx, cy - 100, "Діелектричне середовище (ε_r)", size=12, bold=True, color=COLOR_ORANGE, anchor="middle"))

    f.append(circle(cx, cy, 18, fill="#fdecea", stroke=COLOR_RED, sw=2))
    f.append(text(cx, cy + 5, "+Q_free", size=11, bold=True, color=COLOR_RED))

    for ang in [0, 60, 120, 180, 240, 300]:
        px = cx + 38 * (1 if ang in [0, 60, 300] else (-1 if ang in [120, 180, 240] else 0))
        py = cy + 38 * (1 if ang in [60, 120] else (-1 if ang in [240, 300] else 0))
        if ang in [60, 120, 240, 300]:
            px, py = cx + 38 * 0.5 * (1 if ang in [60, 300] else -1), cy + 38 * 0.866 * (1 if ang in [60, 120] else -1)
        f.append(circle(px, py, 8, fill="#eaf0fd", stroke=COLOR_BLUE, sw=1.2))
        f.append(text(px, py + 3, "−", size=10, bold=True, color=COLOR_BLUE))

    f.append(dashed_circle(cx, cy, 80, fill="none", stroke=COLOR_PURPLE, sw=2, dash="6,4"))
    f.append(text(cx + 60, cy - 62, "Поверхня S", size=11, bold=True, color=COLOR_PURPLE, anchor="start"))

    b, w, h = textbox(585, 190,
                      "Вектор поляризації P:\nЗв'язаний заряд Q_bound\n\nВектор зсуву D:\nD = ε₀ · E + P\n   = ε₀ · ε_r · E\n\nЗакон Гаусса в речовині:\n∮ D · dA = Q_free\n\nЗв'язаний заряд випадає!",
                      size=12, pad=10, fill="#eef6ff", stroke="#99ccff", sw=1.4)
    f.append(b)

    return render(os.path.join(IMG, "dielectric-polarization.svg"), W, H, *f)


if __name__ == '__main__':
    fig_flux_concept()
    fig_solid_angle()
    fig_spherical_symmetry()
    fig_cylindrical_symmetry()
    fig_planar_symmetry()
    fig_conductor_charge()
    fig_divergence_box()
    fig_dielectric_polarization()
    print("Усі 8 фігур згенеровано успішно у ./img/")

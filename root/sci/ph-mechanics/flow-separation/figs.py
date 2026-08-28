# -*- coding: utf-8 -*-
"""Фігури до теми «Відрив потоку».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── дрібні помічники ─────────────────────────────────────────────────────────
def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def path_fill(pts, fill, stroke='none', sw=0):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for (x, y) in pts) + " Z"
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)


def smooth(pts, fill='none', stroke=INK, sw=2.4, dash=None):
    """Гладка крива (квадратичні сегменти) через список точок."""
    if len(pts) < 3:
        return polyline(pts, stroke, sw, dash)
    d = "M %.1f %.1f" % pts[0]
    for i in range(1, len(pts) - 1):
        mx = (pts[i][0] + pts[i + 1][0]) / 2
        my = (pts[i][1] + pts[i + 1][1]) / 2
        d += " Q %.1f %.1f %.1f %.1f" % (pts[i][0], pts[i][1], mx, my)
    d += " L %.1f %.1f" % pts[-1]
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, stroke, sw, da)


def head_at(x, y, dx, dy, color=INK, size=10):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.5, by + ny * size * 0.5,
               bx - nx * size * 0.5, by - ny * size * 0.5, color))


def varrow(x1, y1, x2, y2, color=LINE, sw=2.4, head=11):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)


def hatch_below(x0, x1, y, color=MUTED, dh=9, step=13):
    out = [line(x0, y, x1, y, color=INK, sw=2.4)]
    x = x0
    while x < x1:
        out.append(line(x, y, x - dh, y + dh, color=color, sw=1.2))
        x += step
    return "".join(out)


def dcircle(cx, cy, r, fill='none', stroke=LINE, sw=1.5, dash=None):
    da = (' stroke-dasharray="%s"' % dash) if dash else ''
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (cx, cy, r, fill, stroke, sw, da))


# ── Фігура 1: пагорб тиску як гірка потенціальної енергії ─────────────────────
def fig_pressure_hill():
    W, H = 940, 540
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Пагорб тиску — гірка, яку долає лише запас руху ½·ρ·u²",
                  size=18, bold=True))

    xL, xR = 150, 812
    yB, yT = 380, 210

    def hy(t):
        return yB - (yB - yT) * (1.0 - math.cos(math.pi * t)) / 2.0

    hill = [(xL + t * (xR - xL), hy(t)) for t in [i / 80.0 for i in range(81)]]
    f.append(path_fill(hill + [(xR, yB + 6), (xL, yB + 6)], "#f3f5f8", stroke="#c8ced8", sw=1.6))
    f.append(hatch_below(xL - 25, xR + 25, yB + 6))

    f.append(varrow(xL - 25, yB + 6, xL - 25, yT - 40, color=INK, sw=1.8, head=10))
    f.append(text(xL - 45, yT - 30, "тиск p", size=13, anchor="middle", bold=True))
    f.append(line(xL - 32, yB, xL - 18, yB, color=MUTED, sw=1.4))
    f.append(text(xL - 38, yB + 4, "p₀", size=12, color=MUTED, anchor="end"))
    f.append(line(xL - 32, yT, xL - 18, yT, color=MUTED, sw=1.4))
    f.append(text(xL - 38, yT + 4, "p₀ + Δp", size=12, color=MUTED, anchor="end"))

    f.append(varrow(xL - 25, yB + 6, xR + 40, yB + 6, color=INK, sw=1.8, head=10))
    f.append(text(xR + 35, yB + 28, "шлях вздовж стінки x", size=13, anchor="end"))

    f.append(circle(xR - 10, yT - 22, 14, fill="#dbeafe", stroke=NEG, sw=2.2))
    f.append(varrow(xR - 10, yT - 22, xR + 50, yT - 22, color=NEG, sw=2.2, head=9))
    f.append(text(xR + 55, yT - 22, "540 Па > 100 Па  (вибрався)", size=12, color=NEG, anchor="start", bold=True))

    t_stop = 0.35
    xs, ys = xL + t_stop * (xR - xL), hy(t_stop)
    f.append(circle(xs, ys - 14, 14, fill="#fee2e2", stroke=POS, sw=2.2))
    f.append(varrow(xs, ys - 14, xs - 45, ys - 4, color=POS, sw=2.2, head=9))
    f.append(text(xs - 10, ys - 35, "21.6 Па < 100 Па (скочується назад)", size=12, color=POS, anchor="end", bold=True))

    b, w, h = textbox(W / 2, H - 42,
                      "Зовнішній потік проходить пагорб тиску завдяки великій швидкості U∞;\n"
                      "пристінний шар, загальмований тертям, зупиняється й розвертається назад.",
                      size=13, pad=10, fill="#f8fafc", stroke="#94a3b8", sw=1.2)
    f.append(b)
    return render(os.path.join(IMG, "pressure-hill.svg"), W, H, *f)


# ── Фігура 2: зміна профілю швидкості ─────────────────────────────────────────
def fig_profile_progression():
    W, H = 1000, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Трансформація профілю швидкості під дією несприятливого градієнта",
                  size=18, bold=True))

    stations = [
        (130, 0.45, NEG, "1. Сприятливий dp/dx < 0", "τ_w > 0, профіль наповнений"),
        (350, 0.20, NEG, "2. Початок гальмування", "dp/dx > 0, профіль випрямляється"),
        (570, 0.00, POS, "3. Точка відриву", "τ_w = 0, (∂u/∂y)₀ = 0"),
        (790, -0.22, POS, "4. Зворотна течія", "τ_w < 0, вихрова застійна зона"),
    ]

    y0 = 380
    h_prof = 200
    w_prof = 140

    for (x_base, slope_w, col, title_st, desc_st) in stations:
        f.append(hatch_below(x_base - 30, x_base + w_prof + 20, y0))
        f.append(varrow(x_base, y0, x_base, y0 - h_prof - 25, color=INK, sw=1.5, head=8))
        f.append(text(x_base - 10, y0 - h_prof - 15, "y", size=12, italic=True))
        f.append(varrow(x_base, y0, x_base + w_prof + 25, y0, color=INK, sw=1.5, head=8))
        f.append(text(x_base + w_prof + 20, y0 + 20, "u", size=12, italic=True))

        pts = []
        for i in range(41):
            eta = i / 40.0
            if slope_w >= 0:
                u_val = slope_w * eta + (1.0 - slope_w) * (2 * eta - eta**2)
            else:
                u_val = slope_w * eta * (1.0 - eta) + (2 * eta - eta**2)
            px = x_base + u_val * w_prof
            py = y0 - eta * h_prof
            pts.append((px, py))

        f.append(polyline(pts, color=col, sw=3.0))

        for (px, py) in pts[::8]:
            if abs(px - x_base) > 2:
                f.append(varrow(x_base, py, px, py, color=col, sw=1.2, head=6))

        f.append(text(x_base + w_prof / 2, 75, title_st, size=13, bold=True, color=col))
        f.append(text(x_base + w_prof / 2, 95, desc_st, size=11, color=MUTED))

    b, w, h = textbox(W / 2, H - 35,
                      "Знак дотичного напруження τ_w = μ·(∂u/∂y)₀ визначає поведінку шару: "
                      "при нульовому нахилі потік сходить із поверхні.",
                      size=12.5, pad=10, fill="#f8fafc", stroke="#94a3b8", sw=1.2)
    f.append(b)
    return render(os.path.join(IMG, "profile-progression.svg"), W, H, *f)


# ── Фігура 3: універсальність ────────────────────────────────────────────────
def fig_universality():
    W, H = 1000, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Універсальність відриву: три прояви одного фізичного закону",
                  size=18, bold=True))

    panels = [
        (60, 310, "1. Тупе тіло (куля / циліндр)", "Широкий турбулентний слід, високий опір форми"),
        (380, 310, "2. Крило на великому куті атаки", "Аеродинамічний зрив (Stall), втрата підйомної сили"),
        (700, 310, "3. Розтрубний канал (дифузор)", "Зрив зі стінок при куті розкриття > 7°"),
    ]

    for (x0, w_p, head, desc) in panels:
        f.append(rect(x0, 60, w_p, 340, fill="#fbfcfd", stroke="#d1d5db", sw=1.4, rx=6))
        f.append(text(x0 + w_p / 2, 85, head, size=13, bold=True))
        f.append(text(x0 + w_p / 2, 105, desc, size=10.5, color=MUTED))

    # Слід за кулею
    f.append(circle(160, 240, 40, fill="#e2e8f0", stroke=INK, sw=2.0))
    f.append(smooth([(160, 200), (220, 190), (340, 160)], stroke=NEG, sw=2.0))
    f.append(smooth([(160, 280), (220, 290), (340, 320)], stroke=NEG, sw=2.0))
    f.append(dcircle(250, 220, 15, fill="none", stroke=POS, sw=1.5, dash="4 3"))
    f.append(dcircle(280, 260, 18, fill="none", stroke=POS, sw=1.5, dash="4 3"))
    f.append(text(270, 245, "застійний слід", size=11, color=POS, bold=True))

    # Зрив на крилі
    pts_airfoil = [(430, 270), (470, 220), (550, 200), (630, 210), (430, 270)]
    f.append(smooth(pts_airfoil, fill="#e2e8f0", stroke=INK, sw=2.0))
    f.append(smooth([(470, 220), (520, 160), (660, 140)], stroke=POS, sw=2.2))
    f.append(dcircle(550, 180, 16, fill="none", stroke=POS, sw=1.5, dash="4 3"))
    f.append(dcircle(600, 175, 20, fill="none", stroke=POS, sw=1.5, dash="4 3"))
    f.append(text(570, 235, "зрив потоку", size=11, color=POS, bold=True))

    # Дифузор
    f.append(line(730, 210, 800, 210, color=INK, sw=2.0))
    f.append(line(800, 210, 970, 160, color=INK, sw=2.0))
    f.append(line(730, 270, 800, 270, color=INK, sw=2.0))
    f.append(line(800, 270, 970, 320, color=INK, sw=2.0))
    f.append(smooth([(800, 210), (840, 230), (960, 230)], stroke=POS, sw=2.0))
    f.append(dcircle(890, 190, 15, fill="none", stroke=POS, sw=1.5, dash="4 3"))
    f.append(text(890, 280, "відрив у розтрубі", size=11, color=POS, bold=True))

    b, w, h = textbox(W / 2, H - 35,
                      "В усіх випадках фізична першопричина єдина: розширення ліній течії спричиняє зростання тиску dp/dx > 0.",
                      size=12.5, pad=10, fill="#f8fafc", stroke="#94a3b8", sw=1.2)
    f.append(b)
    return render(os.path.join(IMG, "universality.svg"), W, H, *f)


# ── Фігура 4: знак градієнта тиску ───────────────────────────────────────────
def _fs_profile(beta):
    pts = []
    if beta > 0:
        tg = 1.6
        for i in range(41):
            t = i / 40.0
            u = 2 * t - t**2
            pts.append((u, t))
        return pts, tg, None
    elif beta == 0:
        tg = 1.0
        for i in range(41):
            t = i / 40.0
            u = 1.5 * t - 0.5 * t**3
            pts.append((u, t))
        return pts, tg, None
    else:
        tg = 0.35
        infl = (0.22, 0.45)
        for i in range(41):
            t = i / 40.0
            u = 0.35 * t + 1.8 * t**2 - 1.15 * t**3
            pts.append((u, t))
        return pts, tg, infl


def fig_wall_curvature_sign():
    W, H = 1040, 680
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "μ·(∂²u/∂y²)₀ = dp/dx — градієнт тиску диктує кривину профілю на стінці",
                  size=17.5, bold=True))
    f.append(line(W / 2 - 196, 56, W / 2 - 160, 56, color=MUTED, sw=1.8, dash="6 5"))
    f.append(text(W / 2 - 152, 60, "— дотична до профілю на стінці (нахил τ_w ⁄ μ);  ○ — точка перегину",
                  size=12, color=MUTED, anchor="start"))

    PW, PH = 230.0, 300.0
    PY0 = 470.0
    panels = [
        (105.0, 0.5, NEG, "розгін:  dp/dx < 0",
         "u″(0) < 0\nкрива йде ЛІВОРУЧ від дотичної\nнахил найбільший на самій стінці"),
        (425.0, 0.0, MUTED, "рівний тиск:  dp/dx = 0",
         "u″(0) = 0  (і u‴(0) = 0)\nколо стінки профіль — пряма\nперегин сидить на самій стінці"),
        (745.0, -0.18, POS, "гальмування:  dp/dx > 0",
         "u″(0) > 0\nкрива йде ПРАВОРУЧ від дотичної\nнахил на стінці — найменший"),
    ]

    for (PX0, beta, col, head, note) in panels:
        pts, tg, infl = _fs_profile(beta)
        f.append(text(PX0 + PW / 2, 85, head, size=15, bold=True, color=col))

        def sx(u):
            return PX0 + u * PW

        def sy(t):
            return PY0 - t * PH

        f.append(hatch_below(PX0 - 22, PX0 + PW + 26, PY0))
        f.append(varrow(PX0, PY0, PX0, PY0 - PH - 26, color=INK, sw=1.6, head=9))
        f.append(text(PX0 - 16, PY0 - PH - 24, "y", size=13, italic=True, anchor="middle"))
        f.append(varrow(PX0, PY0, PX0 + PW + 26, PY0, color=INK, sw=1.6, head=9))
        f.append(text(PX0 + PW + 20, PY0 + 26, "u ⁄ U", size=12, anchor="middle"))
        f.append(line(PX0 - 6, sy(1.0), PX0 + 6, sy(1.0), color=MUTED, sw=1.6))
        f.append(text(PX0 - 14, sy(1.0) + 5, "δ", size=12.5, color=MUTED, anchor="end"))

        t_end = min(1.02, 1.02 / tg) if tg > 0 else 1.02
        tx1, ty1 = sx(min(1.02, tg * t_end)), sy(t_end)
        f.append(line(sx(0), sy(0), tx1, ty1, color=MUTED, sw=1.8, dash="6 5"))

        band = [(sx(u), sy(t)) for (u, t) in pts if t <= t_end]
        if band:
            back = [(sx(min(1.02, tg * t)), sy(t)) for t in
                    [i / 40.0 * t_end for i in range(41)]][::-1]
            shade = "#eaf0fd" if beta > 0 else ("#fdecea" if beta < 0 else "#f0f0f0")
            f.append(path_fill(band + back, shade))

        f.append(polyline([(sx(u), sy(t)) for (u, t) in pts], color=col, sw=2.8))

        if infl:
            f.append(circle(sx(infl[0]), sy(infl[1]), 5.5, fill=BG, stroke=POS, sw=2.4))
            f.append(text(PX0 + 10, sy(infl[1]) - 12, "перегин u″=0", size=11,
                          color=POS, anchor="start", bold=True))
        elif beta == 0.0:
            f.append(circle(sx(0.0), sy(0.0), 5.5, fill=BG, stroke=INK, sw=2.4))

        f.append(fitbox(PX0 - 22, PY0 + 38, PW + 48, 68, note, size=11, pad=6,
                        fill="#fbfbfc", stroke=col, sw=1.3))

    b, w, h = textbox(W / 2, H - 32,
                      "Профілі Фолкнера–Скан. Сприятливий градієнт вигинає профіль до стінки, несприятливий — від неї,\n"
                      "і тоді кривина мусить десь усередині шару змінити знак: там і сидить точка перегину",
                      size=12.5, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "wall-curvature-sign.svg"), W, H, *f)


# ── Фігура 5: відривна парабола ──────────────────────────────────────────────
def fig_separation_parabola():
    W, H = 840, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Квадратичний профіль швидкості в точці відриву (τ_w = 0)",
                  size=17.5, bold=True))

    x0, y0 = 180, 380
    pw, ph = 480, 280

    f.append(hatch_below(x0 - 40, x0 + pw + 40, y0))
    f.append(varrow(x0, y0, x0, y0 - ph - 25, color=INK, sw=1.8, head=9))
    f.append(text(x0 - 15, y0 - ph - 15, "y", size=13, italic=True))
    f.append(varrow(x0, y0, x0 + pw + 35, y0, color=INK, sw=1.8, head=9))
    f.append(text(x0 + pw + 25, y0 + 22, "u ⁄ U", size=13))

    pts = []
    for i in range(51):
        eta = i / 50.0
        u = eta**2
        pts.append((x0 + u * pw, y0 - eta * ph))

    f.append(polyline(pts, color=POS, sw=3.2))

    for (px, py) in pts[::6]:
        if px > x0 + 2:
            f.append(varrow(x0, py, px, py, color=POS, sw=1.4, head=6))

    f.append(line(x0, y0, x0, y0 - 100, color=MUTED, sw=2.0, dash="6 4"))
    f.append(text(x0 + 15, y0 - 50, "(∂u/∂y)₀ = 0 (вертикальна дотична)", size=11.5, color=POS, anchor="start", bold=True))

    b, w, h = textbox(W / 2, H - 35,
                      "В точці відриву профіль стартує від стінки вертикально: u(y) ≈ ½μ·(dp/dx)·y².",
                      size=12.5, pad=10, fill="#f8fafc", stroke="#94a3b8", sw=1.2)
    f.append(b)
    return render(os.path.join(IMG, "separation-parabola.svg"), W, H, *f)


# ── Фігура 6: спад тертя до кореневого нуля ───────────────────────────────────
def fig_tau_sqrt_approach():
    W, H = 840, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Сингулярність Ґольдштейна: τ_w ∝ √(x_sep − x)",
                  size=17.5, bold=True))

    x0, y0 = 120, 360
    pw, ph = 600, 260

    f.append(varrow(x0, y0, x0, y0 - ph - 25, color=INK, sw=1.8, head=9))
    f.append(text(x0 - 20, y0 - ph - 15, "τ_w", size=13, italic=True))
    f.append(varrow(x0, y0, x0 + pw + 35, y0, color=INK, sw=1.8, head=9))
    f.append(text(x0 + pw + 25, y0 + 22, "x", size=13, italic=True))

    x_sep = x0 + pw - 60
    pts = []
    for i in range(101):
        x = x0 + i * (x_sep - x0) / 100.0
        xi = (x_sep - x) / (x_sep - x0)
        tau = math.sqrt(max(0.0, xi))
        pts.append((x, y0 - tau * ph))

    f.append(polyline(pts, color=POS, sw=3.0))
    f.append(circle(x_sep, y0, 6, fill=POS, stroke=POS, sw=1.5))
    f.append(text(x_sep, y0 + 22, "x_sep", size=12, color=POS, bold=True))
    f.append(text(x_sep - 10, y0 - 80, "нескінченний нахил dτ_w/dx → −∞", size=11.5, color=POS, anchor="end"))

    b, w, h = textbox(W / 2, H - 35,
                      "Рівняння примежового шару Прандтля мають неінтегровну особливість у точці відриву.",
                      size=12.5, pad=10, fill="#f8fafc", stroke="#94a3b8", sw=1.2)
    f.append(b)
    return render(os.path.join(IMG, "tau-sqrt-approach.svg"), W, H, *f)


# ── Фігура 7: марш Твейтса ───────────────────────────────────────────────────
def _lam_howarth(xi):
    if xi >= 0.1231: return -0.09
    return -0.075 * (1.0 - (1.0 - xi)**6) / ((1.0 - xi)**6)

def _lam_cylinder(phi):
    if phi < 1e-6: return 0.075
    c = math.cos(phi)
    I = -c + (2.0 / 3.0) * c**3 - 0.2 * c**5 + (1.0 - 2.0 / 3.0 + 0.2)
    return 0.45 * c * I / math.sin(phi)**6

def fig_thwaites_march():
    W, H = 1010, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    LAM_TOP, LAM_BOT = 0.10, -0.13
    PY0, PY1 = 96.0, 352.0
    PW = 366.0

    def ymap(lam):
        return PY0 + (LAM_TOP - lam) / (LAM_TOP - LAM_BOT) * (PY1 - PY0)

    panels = [
        dict(x0=96.0, head="Гальмівна течія   U = U₀·(1 − x/L)",
             sub="по вертикалі λ, по горизонталі x/L",
             xmax=0.14, ticks=[(0.0, "0"), (0.05, "0.05"), (0.10, "0.10")],
             fn=lambda t: _lam_howarth(t), cross=0.1231, clabel="0.1231",
             note="Твейтс 0.1231  ·  точний розв'язок 0.1198  →  завищення на 2.8 %"),
        dict(x0=548.0, head="Циліндр   U = 2·U∞·sin φ",
             sub="по вертикалі λ, по горизонталі φ, градуси",
             xmax=115.0, ticks=[(0.0, "0"), (30.0, "30"), (60.0, "60"), (90.0, "90")],
             fn=lambda t: _lam_cylinder(math.radians(t)), cross=103.1, clabel="103.1°",
             note="Твейтс 103.1°  ·  дослід ≈ 80°  →  винна нев'язка крива на вході"),
    ]

    for p in panels:
        x0, xmax = p["x0"], p["xmax"]
        xm = lambda t: x0 + t / xmax * PW

        f.append(text(x0 + PW / 2, 52, p["head"], size=14.5, bold=True))
        f.append(text(x0 + PW / 2, 74, p["sub"], size=11.5, color=MUTED))
        f.append(rect(x0, PY0, PW, PY1 - PY0, fill="#fbfcfd", stroke="#c9ced6", sw=1.2, rx=4))

        f.append(line(x0, ymap(0.0), x0 + PW, ymap(0.0), color=MUTED, sw=1.3, dash="6 5"))
        f.append(line(x0, ymap(-0.09), x0 + PW, ymap(-0.09), color=POS, sw=1.8, dash="7 5"))

        for lam, lab, col in ((0.075, "0.075", MUTED), (0.0, "0", MUTED), (-0.09, "−0.09", POS)):
            f.append(line(x0 - 6, ymap(lam), x0, ymap(lam), color=col, sw=1.3))
            f.append(text(x0 - 11, ymap(lam) + 4, lab, size=11.5, color=col, anchor="end",
                          bold=(lam == -0.09)))

        pts = []
        for i in range(241):
            t = xmax * i / 240.0
            lam = p["fn"](t)
            if lam < LAM_BOT + 0.002:
                break
            pts.append((xm(t), ymap(min(lam, LAM_TOP))))
        f.append(polyline(pts, color=NEG, sw=3.0))

        cx = xm(p["cross"])
        f.append(line(cx, ymap(-0.09), cx, PY1, color=POS, sw=1.3, dash="4 4"))
        f.append(circle(cx, ymap(-0.09), 5.5, fill=POS, stroke=POS, sw=1.4))

        for tv, lab in p["ticks"]:
            f.append(line(xm(tv), PY1, xm(tv), PY1 + 6, color=MUTED, sw=1.3))
            f.append(text(xm(tv), PY1 + 21, lab, size=11.5, color=MUTED))
        f.append(text(cx, PY1 + 21, p["clabel"], size=11.5, color=POS, bold=True))

        b, w, h = textbox(x0 + PW / 2, 412, p["note"], size=12, pad=9,
                          fill="#f8f2f1", stroke=POS, sw=1.3)
        f.append(b)

    f.append(text(panels[0]["x0"] + 10, ymap(-0.09) - 11, "поріг відриву:  S(λ) = 0",
                  size=11.5, color=POS, anchor="start"))

    b, w, h = textbox(W / 2, H - 32,
                      "Одна процедура на будь-якому тілі: інтеграл ∫U⁵ds → θ² → λ → перший перетин −0.09",
                      size=12.5, pad=10, fill="#eef6ef", stroke=FIELD, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "thwaites-march.svg"), W, H, *f)


# ── Фігура 8: детальний профіль відриву та лінії течії ────────────────────────
def fig_boundary_layer_separation_profile():
    W, H = 1060, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Анатомія відриву примежового шару: від безвідривної течії до вихрового сходу",
                  size=18, bold=True))

    y_wall = 440
    f.append(hatch_below(50, 1010, y_wall, dh=10, step=14))

    for y_st in [120, 160, 200]:
        f.append(smooth([(60, y_st), (400, y_st + 10), (550, y_st - 15), (1000, y_st - 45)],
                        stroke="#93c5fd", sw=1.4, dash="6 4"))

    stations = [
        (120, "1. dp/dx < 0 (розгін)", "τ_w > 0\n(∂²u/∂y²)₀ < 0\nопуклий профіль", NEG, 1.4, 0.0),
        (320, "2. dp/dx > 0 (початок)", "τ_w > 0\n(∂²u/∂y²)₀ > 0\nточка перегину ○", NEG, 0.7, 0.25),
        (520, "3. Точка відриву xs", "τ_w = 0\n(∂u/∂y)₀ = 0\nсхід лінії ψ = 0", POS, 0.0, 0.5),
        (720, "4. Зворотна течія", "τ_w < 0\nu(y) < 0 коло стінки\nлінія u=0 відійшла", POS, -0.4, 0.65),
        (920, "5. Вільний шар зсуву", "розвинений вихор\nрециркуляція\nнестійкість К-Г", POS, -0.6, 0.8),
    ]

    h_prof = 220
    w_prof = 110

    sep_streamline = [(520, y_wall), (600, y_wall - 35), (720, y_wall - 85), (850, y_wall - 140), (1000, y_wall - 180)]
    f.append(smooth(sep_streamline, stroke=POS, sw=2.6, dash="7 4"))
    f.append(text(780, y_wall - 105, "розділова лінія струменя ψ = 0", size=11, color=POS, bold=True))

    f.append(dcircle(820, y_wall - 40, 28, fill="none", stroke=POS, sw=1.6, dash="4 3"))
    f.append(varrow(820, y_wall - 68, 795, y_wall - 68, color=POS, sw=1.6, head=7))
    f.append(varrow(820, y_wall - 12, 845, y_wall - 12, color=POS, sw=1.6, head=7))
    f.append(text(820, y_wall - 38, "зворотна течія", size=10.5, color=POS, bold=True))

    for (x_base, title_st, desc_st, col, slope_w, infl_y) in stations:
        f.append(varrow(x_base, y_wall, x_base, y_wall - h_prof - 20, color=INK, sw=1.4, head=7))
        f.append(text(x_base - 10, y_wall - h_prof - 12, "y", size=11.5, italic=True))
        f.append(varrow(x_base, y_wall, x_base + w_prof + 20, y_wall, color=INK, sw=1.4, head=7))
        f.append(text(x_base + w_prof + 16, y_wall + 18, "u", size=11.5, italic=True))

        pts = []
        for i in range(41):
            eta = i / 40.0
            if slope_w >= 0:
                u_val = slope_w * eta + (1.0 - slope_w) * (2 * eta - eta**2)
            else:
                u_val = slope_w * eta * (1.0 - eta)**2 + (1.0 - math.exp(-3 * eta)) * 0.9
            px = x_base + u_val * w_prof
            py = y_wall - eta * h_prof
            pts.append((px, py))

        f.append(polyline(pts, color=col, sw=2.6))

        for (px, py) in pts[::7]:
            if abs(px - x_base) > 2:
                f.append(varrow(x_base, py, px, py, color=col, sw=1.1, head=5))

        if infl_y > 0.05:
            py_inf = y_wall - infl_y * h_prof
            f.append(circle(x_base + (infl_y * 0.5) * w_prof, py_inf, 4.5, fill=BG, stroke=POS, sw=2.0))

        f.append(text(x_base + w_prof / 2 - 10, 68, title_st, size=12, bold=True, color=col))
        f.append(fitbox(x_base - 22, y_wall + 26, w_prof + 44, 52, desc_st, size=10.5, pad=5,
                        fill="#fcfdfd", stroke=col, sw=1.1))

    b, w, h = textbox(W / 2, H - 24,
                      "Гальмування потоку вигинає профіль, породжує точку перегину, обнуляє тертя τ_w = 0 "
                      "і змушує пристінну рідину текти у зворотному напрямку.",
                      size=12, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "boundary-layer-separation-profile.svg"), W, H, *f)


# ── Фігура 9: зрив потоку на крилі та вихори Кармана ─────────────────────────
def fig_airfoil_stall_vortices():
    W, H = 1060, 580
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Аеродинамічний зрив крила (Stall) та вихрова доріжка фон Кармана",
                  size=18, bold=True))

    PW = 460.0
    PH = 300.0

    # Ліва панель: α = 6°
    xL = 50.0
    f.append(rect(xL, 60, PW, PH, fill="#fbfcfd", stroke="#cbd5e1", sw=1.4, rx=6))
    f.append(text(xL + PW / 2, 88, "Помірний кут атаки: α = 6° (безвідривне обтікання)", size=14, bold=True, color=NEG))
    f.append(text(xL + PW / 2, 108, "Висока підйомна сила CL ≈ 0.85, мінімальний опір CD ≈ 0.01", size=11, color=MUTED))

    # Профіль при 6°
    f.append(smooth([(xL + 80, 260), (xL + 140, 215), (xL + 250, 200), (xL + 360, 225), (xL + 80, 260)],
                    fill="#e2e8f0", stroke=INK, sw=2.2))

    # Лінії течії без відриву
    for dy in [-60, -30, 0, 30, 60]:
        f.append(smooth([(xL + 20, 240 + dy), (xL + 140, 190 + dy * 0.7),
                         (xL + 260, 175 + dy * 0.7), (xL + 440, 215 + dy)],
                        stroke=NEG, sw=1.6))

    # Вектори L і D
    f.append(varrow(xL + 200, 210, xL + 200, 120, color=FIELD, sw=3.0, head=11))
    f.append(text(xL + 215, 130, "Підйомна сила L", size=12, color=FIELD, bold=True))
    f.append(varrow(xL + 200, 210, xL + 260, 210, color=POS, sw=2.0, head=8))
    f.append(text(xL + 265, 215, "Опір D (малий)", size=11, color=POS))

    bL, _, _ = textbox(xL + PW / 2, 425,
                       "Примежовий шар залишається притиснутим до спинки крила;\n"
                       "тиск на верхній поверхні низький, створюється повноцінна підйомна сила.",
                       size=11.5, pad=8, fill="#f0fdf4", stroke=FIELD, sw=1.2)
    f.append(bL)

    # Права панель: α = 18° (Stall)
    xR = 550.0
    f.append(rect(xR, 60, PW, PH, fill="#fbfcfd", stroke="#cbd5e1", sw=1.4, rx=6))
    f.append(text(xR + PW / 2, 88, "Закритичний кут атаки: α = 18° (звалювання / Stall)", size=14, bold=True, color=POS))
    f.append(text(xR + PW / 2, 108, "Обвал підйомної сили CL ↓ 60%, сплеск опору тиску CD ↑ 500%", size=11, color=POS, bold=True))

    # Профіль при 18° (сильно нахилений)
    f.append(smooth([(xR + 80, 290), (xR + 130, 190), (xR + 240, 155), (xR + 340, 215), (xR + 80, 290)],
                    fill="#e2e8f0", stroke=INK, sw=2.2))

    # Відривний зсувний шар та вихори
    f.append(smooth([(xR + 80, 290), (xR + 120, 140), (xR + 220, 110), (xR + 360, 120), (xR + 440, 140)],
                    stroke=POS, sw=2.6))
    f.append(text(xR + 200, 100, "відірваний вільний шар зсуву", size=11, color=POS, bold=True))

    # Вихори Кармана за крилом
    vortices = [
        (xR + 190, 180, 18, "+"),
        (xR + 260, 200, 22, "−"),
        (xR + 330, 165, 25, "+"),
        (xR + 400, 210, 28, "−"),
    ]
    for (vx, vy, vr, sign) in vortices:
        f.append(dcircle(vx, vy, vr, fill="#fee2e2", stroke=POS, sw=1.6, dash="4 3"))
        f.append(text(vx, vy + 4, sign, size=14, color=POS, bold=True))

    # Вектори L і D при звалюванні
    f.append(varrow(xR + 200, 240, xR + 200, 190, color=MUTED, sw=2.0, head=8))
    f.append(text(xR + 215, 195, "L (обвалена)", size=11, color=MUTED))
    f.append(varrow(xR + 200, 240, xR + 320, 240, color=POS, sw=3.2, head=11))
    f.append(text(xR + 325, 245, "Опір D (колосальний)", size=11.5, color=POS, bold=True))

    bR, _, _ = textbox(xR + PW / 2, 425,
                       "Зрив потоку з передньої кромки руйнує розрідження на спинці;\n"
                       "утворюється широкий вихровий слід, частота зриву задається числом Струхаля St.",
                       size=11.5, pad=8, fill="#fef2f2", stroke=POS, sw=1.2)
    f.append(bR)

    b, w, h = textbox(W / 2, H - 24,
                      "Звалювання супроводжується динамічним зривом вихорів та небезпекою аеропружного резонансу.",
                      size=12, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "airfoil-stall-vortices.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [
        fig_pressure_hill(),
        fig_profile_progression(),
        fig_universality(),
        fig_wall_curvature_sign(),
        fig_separation_parabola(),
        fig_tau_sqrt_approach(),
        fig_thwaites_march(),
        fig_boundary_layer_separation_profile(),
        fig_airfoil_stall_vortices(),
    ]
    print("written:")
    for p in ps:
        print("  ", p)

# -*- coding: utf-8 -*-
"""Фігури до теми «Потенціальна течія».
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


def dash_circle(cx, cy, r, fill="none", stroke=LINE, sw=1.5, dash="6 4"):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>'
            % (cx, cy, r, fill, stroke, sw, dash))


# ── Фігура 1: Суперпозиція елементарних потоків ───────────────────────────────
def fig_elementary_flows():
    W, H = 860, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Суперпозиція елементарних потенціальних течій", size=17, bold=True))
    f.append(text(W / 2, 48, "Лінійність рівняння Лапласа дозволяє додавати потенціали та функції течії",
                  size=12, color=MUTED))

    panels = [
        ("1. Рівномірний потік", "ψ = U·y", 80, 75, 360, 235),
        ("2. Джерело / Стік", "ψ = (Q / 2π)·θ", 460, 75, 740, 235),
        ("3. Точковий вихір", "ψ = −(Γ / 2π)·ln r", 80, 255, 360, 415),
        ("4. Диполь (дублет)", "ψ = −(μ·sin θ) / r", 460, 255, 740, 415)
    ]

    for title, formula, x1, y1, x2, y2 in panels:
        f.append(rect(x1, y1, x2 - x1, y2 - y1, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
        f.append(text(x1 + 16, y1 + 22, title, size=13, bold=True, color=INK, anchor="start"))
        f.append(text(x2 - 16, y1 + 22, formula, size=11.5, bold=True, color=NEG, anchor="end"))

        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2 + 8

        if "Рівномірний" in title:
            for y_off in [-40, -20, 0, 20, 40]:
                py = cy + y_off
                f.append(varrow(x1 + 30, py, x2 - 30, py, color=NEG, sw=1.8))
            f.append(text(cx, cy + 62, "паралельні лінії течії", size=11, color=MUTED))

        elif "Джерело" in title:
            f.append(circle(cx, cy, 5, fill=POS, stroke=POS))
            f.append(text(cx, cy - 10, "Q", size=11.5, bold=True, color=POS))
            for angle_deg in range(0, 360, 45):
                rad = math.radians(angle_deg)
                dx = math.cos(rad)
                dy = math.sin(rad)
                f.append(varrow(cx + dx * 12, cy + dy * 12, cx + dx * 60, cy + dy * 60, color=POS, sw=1.6))
            f.append(text(cx, cy + 62, "радіальні лінії течії", size=11, color=MUTED))

        elif "Вихір" in title:
            f.append(circle(cx, cy, 5, fill=FIELD, stroke=FIELD))
            f.append(text(cx + 12, cy + 4, "Γ", size=12.5, bold=True, color=FIELD))
            for r in [22, 40, 56]:
                f.append(circle(cx, cy, r, fill="none", stroke=FIELD, sw=1.5))
                f.append(head_at(cx - r, cy, 0, 1, color=FIELD, size=8))
                f.append(head_at(cx + r, cy, 0, -1, color=FIELD, size=8))
            f.append(text(cx, cy + 62, "концентричні кола течії", size=11, color=MUTED))

        elif "Диполь" in title:
            f.append(circle(cx - 8, cy, 4, fill=POS, stroke=POS))
            f.append(circle(cx + 8, cy, 4, fill=NEG, stroke=NEG))
            f.append(varrow(cx - 8, cy - 10, cx + 8, cy - 10, color=INK, sw=1.5))
            f.append(text(cx, cy - 16, "μ", size=11.5, bold=True, color=INK))
            for R in [16, 30, 46]:
                f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="1.4"/>'
                         % (cx, cy - R, R, R, NEG))
                f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="1.4"/>'
                         % (cx, cy + R, R, R, NEG))
            f.append(text(cx, cy + 62, "дотичні кола течії", size=11, color=MUTED))

    render(os.path.join(IMG, 'fig-elementary-flows-superposition.svg'), W, H, *f)


# ── Фігура 2: Потенціальне обтікання циліндра без циркуляції ──────────────────
def fig_flow_past_cylinder():
    W, H = 860, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Безвихрове потенціальне обтікання циліндра (Γ = 0)", size=17, bold=True))
    f.append(text(W / 2, 48, "Ортогональна сітка ліній течії (сині) та ізопотенціалів (зелені пунктири)",
                  size=12, color=MUTED))

    cx, cy = 430, 245
    R = 82

    f.append(circle(cx, cy, R, fill="#e2e8f0", stroke=INK, sw=2.5))
    f.append(text(cx, cy, "Циліндр R", size=13, bold=True, color=INK))

    f.append(circle(cx - R, cy, 6, fill=POS, stroke=POS))
    f.append(circle(cx + R, cy, 6, fill=POS, stroke=POS))
    f.append(textbox(cx - R - 75, cy - 25, "Переднє гальмування\n(v = 0, p = p_max)", size=10.5, pad=6, fill="#fef2f2", stroke=POS)[0])
    f.append(textbox(cx + R + 75, cy - 25, "Заднє гальмування\n(v = 0, p = p_max)", size=10.5, pad=6, fill="#fef2f2", stroke=POS)[0])

    psi_values = [0.25, 0.6, 1.0, 1.5, 2.1, 2.8]
    for psi_val in psi_values:
        for sgn in [-1, 1]:
            pts = []
            for x in range(60, 801, 15):
                dx = x - cx
                r_approx = math.hypot(dx, sgn * psi_val * 55)
                if r_approx < R + 2:
                    continue
                y_guess = sgn * (psi_val * 55 + 15 * sgn)
                for _ in range(8):
                    r2 = dx*dx + y_guess*y_guess
                    if r2 <= R*R:
                        r2 = R*R + 1.0
                    f_val = y_guess * (1.0 - (R*R)/r2) - sgn * psi_val * 45
                    df_val = 1.0 - (R*R)/r2 + 2.0 * (R*R) * y_guess * y_guess / (r2*r2)
                    y_guess -= f_val / df_val
                dy = y_guess
                pts.append((x, cy + dy))
            if len(pts) > 5:
                f.append(polyline(pts, color=NEG, sw=1.6))
                mid_i = len(pts) // 2
                if mid_i + 1 < len(pts):
                    p1 = pts[mid_i]
                    p2 = pts[mid_i + 1]
                    f.append(head_at(p2[0], p2[1], p2[0] - p1[0], p2[1] - p1[1], color=NEG, size=7))

    phi_values = [-2.5, -1.8, -1.2, -0.6, 0.0, 0.6, 1.2, 1.8, 2.5]
    for phi_val in phi_values:
        pts = []
        for y in range(85, 405, 15):
            dy = y - cy
            x_guess = cx + phi_val * 85
            for _ in range(8):
                dx = x_guess - cx
                r2 = dx*dx + dy*dy
                if r2 <= R*R:
                    continue
                f_val = dx * (1.0 + (R*R)/r2) - phi_val * 85
                df_val = 1.0 + (R*R)/r2 - 2.0 * (R*R) * dx * dx / (r2*r2)
                x_guess -= f_val / df_val
            dx = x_guess - cx
            if math.hypot(dx, dy) >= R - 1:
                pts.append((x_guess, y))
        if len(pts) > 3:
            f.append(polyline(pts, color=FIELD, sw=1.3, dash="4 3"))

    f.append(varrow(cx - 30, cy - R - 20, cx + 30, cy - R - 20, color=POS, sw=2.2))
    f.append(text(cx, cy - R - 32, "v_max = 2·U (мінімум тиску)", size=11.5, bold=True, color=POS))

    f.append(varrow(cx - 30, cy + R + 20, cx + 30, cy + R + 20, color=POS, sw=2.2))
    f.append(text(cx, cy + R + 34, "v_max = 2·U (мінімум тиску)", size=11.5, bold=True, color=POS))

    f.append(rect(60, 415, 740, 45, fill="#f1f5f9", stroke="#cbd5e1", sw=1.0, rx=6))
    f.append(line(80, 437, 120, 437, color=NEG, sw=2.0))
    f.append(text(130, 441, "Лінії течії (ψ = const)", size=11.5, bold=True, color=NEG, anchor="start"))
    f.append(line(320, 437, 360, 437, color=FIELD, sw=2.0, dash="4 3"))
    f.append(text(370, 441, "Ізопотенціали (ϕ = const)", size=11.5, bold=True, color=FIELD, anchor="start"))
    f.append(text(620, 441, "Парадокс Д'Аламбера: Опір = 0", size=11.5, bold=True, color=POS, anchor="start"))

    render(os.path.join(IMG, 'fig-flow-past-cylinder.svg'), W, H, *f)


# ── Фігура 3: Обтікання циліндра з циркуляцією та виникнення підйомної сили ────
def fig_cylinder_circulation():
    W, H = 860, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 24, "Течія з циркуляцією (Γ > 0) та ефект Магнуса", size=17, bold=True))
    f.append(text(W / 2, 44, "Асиметрія швидкості створює перепад тиску та підйомну силу (Теорема Жуковського)",
                  size=12, color=MUTED))

    cx, cy = 400, 260
    R = 75

    f.append(circle(cx, cy, R, fill="#e2e8f0", stroke=INK, sw=2.5))
    f.append(text(cx, cy - 8, "Циліндр", size=13, bold=True, color=INK))
    f.append(text(cx, cy + 12, "з обертанням", size=11.5, color=MUTED))

    f.append(dash_circle(cx, cy, R + 18, fill="none", stroke=FIELD, sw=2.0, dash="6 4"))
    f.append(head_at(cx, cy - R - 18, -1, 0, color=FIELD, size=10))
    f.append(text(cx + R + 45, cy - 45, "Циркуляція Γ > 0\n(проти годинника)", size=11.5, bold=True, color=FIELD, anchor="start"))

    # Тільки 6 ліній течії, розведених далі одна від одної
    psi_list = [-2.4, -1.6, -0.8, 0.4, 1.2, 2.0]
    for psi_val in psi_list:
        pts = []
        for x in range(60, 741, 20):
            dx = x - cx
            gamma_shift = -24.0
            y_guess = cy + psi_val * 48 + gamma_shift / (1.0 + (dx/130.0)**2)
            if math.hypot(dx, y_guess - cy) < R + 4:
                continue
            pts.append((x, y_guess))
        if len(pts) > 4:
            f.append(polyline(pts, color=NEG, sw=1.6))
            mid_i = len(pts) // 2
            if mid_i + 1 < len(pts):
                p1 = pts[mid_i]
                p2 = pts[mid_i + 1]
                f.append(head_at(p2[0], p2[1], p2[0] - p1[0], p2[1] - p1[1], color=NEG, size=7))

    f.append(circle(cx - R * 0.85, cy + R * 0.52, 5, fill=POS, stroke=POS))
    f.append(circle(cx + R * 0.85, cy + R * 0.52, 5, fill=POS, stroke=POS))
    f.append(text(cx - R * 0.85 - 15, cy + R * 0.52 + 22, "зміщені точки гальмування", size=11, bold=True, color=POS, anchor="end"))

    # Позначення швидкості та тиску з достатніми відступами
    f.append(varrow(cx - 40, cy - R - 55, cx + 40, cy - R - 55, color=POS, sw=2.5))
    f.append(text(cx, cy - R - 68, "Висока швидкість v_top = U + v_Γ", size=11.5, bold=True, color=POS))
    f.append(textbox(cx, cy - R + 22, "Низький тиск p_top", size=11, pad=4, fill="#fef2f2", stroke=POS)[0])

    f.append(varrow(cx - 20, cy + R + 48, cx + 20, cy + R + 48, color=NEG, sw=1.8))
    f.append(text(cx, cy + R + 64, "Низька швидкість v_bot = U − v_Γ", size=11.5, bold=True, color=NEG))
    f.append(textbox(cx, cy + R - 22, "Високий тиск p_bot", size=11, pad=4, fill="#eff6ff", stroke=NEG)[0])

    f.append(varrow(cx, cy, cx, cy - 175, color=POS, sw=4.0, head=14))
    f.append(textbox(cx + 110, cy - 140, "Підйомна сила Кутти-Жуковського\nL' = ρ · U · Γ", size=12, pad=8, fill="#fff1f2", stroke=POS, bold=True)[0])

    render(os.path.join(IMG, 'fig-cylinder-circulation-lift.svg'), W, H, *f)


# ── Фігура 4: Конформне перетворення Жуковського ──────────────────────────────
def fig_joukowsky_transform():
    W, H = 860, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Конформне перетворення Жуковського: z = ζ + a² / ζ", size=17, bold=True))
    f.append(text(W / 2, 48, "Перетворення кола з площини ζ у криловий профіль площини z",
                  size=12, color=MUTED))

    lx1, ly1, lw, lh = 50, 80, 350, 335
    f.append(rect(lx1, ly1, lw, lh, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    f.append(text(lx1 + 20, ly1 + 24, "Площина ζ = ξ + i·η", size=13.5, bold=True, color=INK, anchor="start"))

    lcx, lcy = lx1 + lw / 2, ly1 + lh / 2 + 10
    f.append(line(lx1 + 30, lcy, lx1 + lw - 30, lcy, color=MUTED, sw=1.2))
    f.append(line(lcx, ly1 + 40, lcx, ly1 + lh - 30, color=MUTED, sw=1.2))
    f.append(text(lx1 + lw - 25, lcy - 8, "ξ", size=13, italic=True))
    f.append(text(lcx + 10, ly1 + 48, "η", size=13, italic=True))

    mu_x, mu_y = -12, 14
    R_circle = 88
    f.append(circle(lcx + mu_x, lcy - mu_y, R_circle, fill="#eff6ff", stroke=NEG, sw=2.0))
    f.append(circle(lcx + mu_x, lcy - mu_y, 4, fill=NEG, stroke=NEG))
    f.append(text(lcx + mu_x - 15, lcy - mu_y - 10, "центр ζ₀", size=10.5, color=NEG))

    a_val = 76
    f.append(circle(lcx + a_val, lcy, 5, fill=POS, stroke=POS))
    f.append(text(lcx + a_val, lcy + 18, "+a", size=12, bold=True, color=POS))
    f.append(circle(lcx - a_val, lcy, 5, fill=MUTED, stroke=MUTED))
    f.append(text(lcx - a_val, lcy + 18, "−a", size=12, bold=True, color=MUTED))

    f.append(varrow(415, 245, 465, 245, color=POS, sw=3.0, head=11))
    f.append(text(440, 225, "z = ζ + a²/ζ", size=12, bold=True, color=POS))

    rx1, ry1, rw, rh = 480, 80, 330, 335
    f.append(rect(rx1, ry1, rw, rh, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    f.append(text(rx1 + 20, ry1 + 24, "Площина z = x + i·y", size=13.5, bold=True, color=INK, anchor="start"))

    rcx, rcy = rx1 + rw / 2 - 10, ry1 + rh / 2 + 10
    f.append(line(rx1 + 25, rcy, rx1 + rw - 25, rcy, color=MUTED, sw=1.2))
    f.append(line(rcx, ry1 + 40, rcx, ry1 + rh - 30, color=MUTED, sw=1.2))
    f.append(text(rx1 + rw - 20, rcy - 8, "x", size=13, italic=True))
    f.append(text(rcx + 10, ry1 + 48, "y", size=13, italic=True))

    airfoil_pts = []
    N_pts = 90
    for i in range(N_pts + 1):
        theta = 2.0 * math.pi * i / N_pts
        zeta_x = mu_x + R_circle * math.cos(theta)
        zeta_y = mu_y + R_circle * math.sin(theta)
        r2 = zeta_x * zeta_x + zeta_y * zeta_y
        zx = zeta_x * (1.0 + (a_val * a_val) / r2)
        zy = zeta_y * (1.0 - (a_val * a_val) / r2)
        airfoil_pts.append((rcx + zx * 0.95, rcy - zy * 0.95))

    f.append(path_fill(airfoil_pts, "#fef3c7", stroke=POS, sw=2.2))

    te_x = rcx + 2 * a_val * 0.95
    te_y = rcy
    f.append(circle(te_x, te_y, 5, fill=POS, stroke=POS))
    f.append(text(te_x + 12, te_y + 16, "Задня кромка (z = 2a)\nУмова Кутти", size=10.5, bold=True, color=POS, anchor="start"))

    render(os.path.join(IMG, 'fig-joukowsky-transform.svg'), W, H, *f)


if __name__ == '__main__':
    fig_elementary_flows()
    fig_flow_past_cylinder()
    fig_cylinder_circulation()
    fig_joukowsky_transform()
    print("Усі 4 фігури згенеровано у ./img/")

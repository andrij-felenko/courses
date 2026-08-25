# -*- coding: utf-8 -*-
"""Фігури до теми «Природна конвекція».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED = POS
BLUE = NEG
GREEN = FIELD
ACCENT = POS


def ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (cx, cy, rx, ry, fill, stroke, sw))


def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def path_fill(pts, fill, stroke='none', sw=0):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for (x, y) in pts) + " Z"
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)


def head_at(x, y, dx, dy, color=INK, size=10):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.5, by + ny * size * 0.5,
               bx - nx * size * 0.5, by - ny * size * 0.5, color))


def varrow(x1, y1, x2, y2, color=LINE, sw=2.4, head=10):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)


def hatch_left(x, y0, y1, dh=9, step=13, color=MUTED):
    """Штрихування вертикальної стінки зліва від x."""
    out = [line(x, y0, x, y1, color=INK, sw=2.8)]
    y = y0
    while y < y1:
        out.append(line(x, y, x - dh, y + dh, color=color, sw=1.2))
        y += step
    return "".join(out)


def text_rot(x, y, s, deg=-90, size=13, color=INK, bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<g transform="rotate(%d %.1f %.1f)"><text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" text-anchor="middle"%s>%s</text></g>'
            % (deg, x, y, x, y, FONT, size, color, w, esc(s)))


# ── Фігура 1: Примежовий шар природної конвекції на вертикальній пластині ─────
def fig_boundary_layer():
    W, H = 880, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Примежовий шар природної конвекції біля вертикальної нагрітої пластини", size=17, bold=True))
    f.append(text(W / 2, 52, "Швидкість досягає максимуму всередині шару, перетворюючись на нуль на стінці й у довкіллі", size=12.5, color=MUTED))

    x_wall = 140
    y_bot, y_top = 440, 90
    f.append(hatch_left(x_wall, y_top, y_bot))
    f.append(text_rot(x_wall - 45, (y_bot + y_top) / 2, "Нагріта пластина (Tw)", deg=-90, size=13, color=RED, bold=True))

    delta_pts = []
    for i in range(50):
        t = i / 49.0
        y = y_bot - t * (y_bot - y_top)
        dx = 180 * math.pow(t, 0.6) + 15
        delta_pts.append((x_wall + dx, y))

    bg_pts = [(x_wall, y_bot)] + delta_pts + [(x_wall, y_top)]
    f.append(path_fill(bg_pts, fill="#FFF8E7", stroke='none'))

    f.append(polyline(delta_pts, color=RED, sw=2.0, dash="5,4"))
    f.append(text(delta_pts[35][0] + 50, delta_pts[35][1], "Межа примежового шару δ(y)", size=12, color=RED))

    f.append(varrow(70, 110, 70, 170, color=BLUE, sw=2.5))
    f.append(text(70, 185, "g (гравітація)", size=12.5, bold=True, color=BLUE))

    f.append(varrow(x_wall + 35, y_bot - 20, x_wall + 35, y_bot - 100, color=RED, sw=2.2))
    f.append(text(x_wall + 45, y_bot - 60, "Підйомна сила F_b", size=12, color=RED))

    y_slice = 210
    dx_max = 180 * math.pow((y_bot - y_slice)/(y_bot - y_top), 0.6) + 15
    f.append(line(x_wall, y_slice, x_wall + dx_max + 220, y_slice, color=MUTED, sw=1.2, dash="3,3"))
    f.append(text(x_wall - 10, y_slice - 8, "y", size=12, color=MUTED))

    u_pts = []
    r_max = dx_max
    scale_u = 1.4
    for i in range(30):
        eta = i / 29.0
        r = eta * r_max
        u = 4.0 * eta * math.pow(1.0 - eta, 2) * (r_max * 1.1)
        u_pts.append((x_wall + r, y_slice - u * scale_u))

    f.append(polyline(u_pts, color=BLUE, sw=2.8))
    for i in range(1, 29, 4):
        eta = i / 29.0
        r = eta * r_max
        u = 4.0 * eta * math.pow(1.0 - eta, 2) * (r_max * 1.1)
        y_u = y_slice - u * scale_u
        f.append(line(x_wall + r, y_slice, x_wall + r, y_u, color=BLUE, sw=1.2))
        f.append(head_at(x_wall + r, y_u, 0, -1, color=BLUE, size=6))

    eta_m = 1.0 / 3.0
    r_m = eta_m * r_max
    u_m = 4.0 * eta_m * math.pow(1.0 - eta_m, 2) * (r_max * 1.1)
    f.append(circle(x_wall + r_m, y_slice - u_m * scale_u, 4, fill=BLUE, stroke=INK, sw=1))
    f.append(text(x_wall + r_m + 15, y_slice - u_m * scale_u - 15, "u_max", size=12.5, bold=True, color=BLUE))
    f.append(text(x_wall + r_max / 2 + 10, y_slice + 25, "Профіль швидкості u(y, x)", size=13, bold=True, color=BLUE))

    x_temp_origin = 520
    f.append(line(x_temp_origin, y_top - 20, x_temp_origin, y_bot + 20, color=INK, sw=2.0))
    f.append(text(x_temp_origin, y_bot + 40, "Стінка x=0", size=12, color=MUTED))
    f.append(line(x_temp_origin, y_slice, x_temp_origin + 280, y_slice, color=MUTED, sw=1.2, dash="3,3"))

    T_pts = []
    width_T = 240
    height_T = 160
    for i in range(30):
        eta = i / 29.0
        r = eta * width_T
        theta = math.pow(1.0 - eta, 2)
        T_pts.append((x_temp_origin + r, y_slice - theta * height_T))

    f.append(polyline(T_pts, color=RED, sw=2.8))
    f.append(circle(x_temp_origin, y_slice - height_T, 4, fill=RED, stroke=INK, sw=1))
    f.append(text(x_temp_origin + 10, y_slice - height_T - 10, "Tw (температура стінки)", size=12.5, bold=True, color=RED))
    f.append(circle(x_temp_origin + width_T, y_slice, 4, fill=RED, stroke=INK, sw=1))
    f.append(text(x_temp_origin + width_T + 10, y_slice + 15, "T_inf (довкілля)", size=12.5, bold=True, color=MUTED))

    for i in range(0, 30, 5):
        eta = i / 29.0
        r = eta * width_T
        theta = math.pow(1.0 - eta, 2)
        f.append(line(x_temp_origin + r, y_slice, x_temp_origin + r, y_slice - theta * height_T, color=RED, sw=1.0, dash="2,2"))

    f.append(text(x_temp_origin + width_T / 2, y_slice + 25, "Профіль температури T(y, x)", size=13, bold=True, color=RED))

    f.append(text(x_wall, y_bot + 25, "u=0, T=Tw", size=12, color=RED))
    f.append(text(x_wall + dx_max + 10, y_slice + 45, "у довкіллі u->0, T->T_inf", size=12, color=MUTED))

    render(os.path.join(IMG, "boundary-layer.svg"), W, H, "".join(f))


# ── Фігура 2: Осередки конвекції Рейле — Бенара ──────────────────────────────
def fig_rayleigh_benard():
    W, H = 880, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Конвективна нестійкість Рейле — Бенара", size=17, bold=True))
    f.append(text(W / 2, 52, "При перевищенні критичного числа Релея (Ra > 1708) виникає самоорганізація у вихорові комірки", size=12.5, color=MUTED))

    top_y, bot_y = 110, 360
    x_left, x_right = 90, 790
    H_layer = bot_y - top_y

    f.append(rect(x_left, top_y - 20, x_right - x_left, 20, fill="#E6F2FF", stroke=BLUE, sw=2))
    f.append(text(W / 2, top_y - 30, "Верхня холодна пластина (T_cold)", size=13, bold=True, color=BLUE))

    f.append(rect(x_left, bot_y, x_right - x_left, 20, fill="#FFE6E6", stroke=RED, sw=2))
    f.append(text(W / 2, bot_y + 40, "Нижня нагріта пластина (T_hot > T_cold)", size=13, bold=True, color=RED))

    f.append(line(x_left - 30, top_y, x_left - 30, bot_y, color=INK, sw=1.8))
    f.append(line(x_left - 36, top_y, x_left - 24, top_y, color=INK, sw=1.8))
    f.append(line(x_left - 36, bot_y, x_left - 24, bot_y, color=INK, sw=1.8))
    f.append(text_rot(x_left - 45, (top_y + bot_y) / 2, "Товщина шару d", deg=-90, size=13, bold=True))

    cell_w = (x_right - x_left) / 4.0
    centers_x = [x_left + (i + 0.5) * cell_w for i in range(4)]
    dirs = [1, -1, 1, -1]

    for i in range(4):
        cx = centers_x[i]
        cy = (top_y + bot_y) / 2.0
        rx = cell_w * 0.42
        ry = H_layer * 0.38
        d = dirs[i]

        ellipse_fill = "#FFF5E6" if d == 1 else "#EBF5FF"
        f.append(ellipse(cx, cy, rx, ry, fill=ellipse_fill, stroke=MUTED, sw=1.5))

        if i % 2 == 0 and d == 1:
            f.append(varrow(cx - rx, cy + ry * 0.5, cx - rx, cy - ry * 0.5, color=RED, sw=2.5))
            f.append(varrow(cx + rx, cy - ry * 0.5, cx + rx, cy + ry * 0.5, color=BLUE, sw=2.5))
        elif i % 2 == 1 and d == -1:
            f.append(varrow(cx - rx, cy - ry * 0.5, cx - rx, cy + ry * 0.5, color=BLUE, sw=2.5))
            f.append(varrow(cx + rx, cy + ry * 0.5, cx + rx, cy - ry * 0.5, color=RED, sw=2.5))

    f.append(text_rot(centers_x[0] - cell_w*0.4, cy, "Гарячий плюм", deg=-90, size=11.5, color=RED, bold=True))
    f.append(text_rot(centers_x[1], cy, "Холодний опуск", deg=-90, size=11.5, color=BLUE, bold=True))
    f.append(text_rot(centers_x[2], cy, "Гарячий плюм", deg=-90, size=11.5, color=RED, bold=True))

    f.append(text(W / 2, H - 20, "Умова виникнення конвекції: Ra = (g β ΔT d³) / (ν α) > Ra_критичне ≈ 1708", size=13.5, bold=True, color=RED))

    render(os.path.join(IMG, "rayleigh-benard.svg"), W, H, "".join(f))


# ── Фігура 3: Орієнтація ребер радіатора (вертикальна vs горизонтальна) ──────
def fig_heatsink_orientation():
    W, H = 880, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Вплив орієнтації радіатора на природну конвекцію", size=17, bold=True))
    f.append(text(W / 2, 52, "Вертикальне розташування каналів створює димаровий ефект; горизонтальне — застоює повітря", size=12.5, color=MUTED))

    cx1 = 230
    y_base = 350
    f.append(text(cx1, 95, "А. Вертикальна орієнтація (Ефективна)", size=14, bold=True, color=GREEN))

    f.append(rect(cx1 - 120, y_base, 240, 18, fill="#555555", stroke=INK, sw=1.5))
    f.append(rect(cx1 - 60, y_base + 18, 120, 20, fill="#FF6666", stroke=RED, sw=1.5))
    f.append(text(cx1, y_base + 32, "Чип / Джерело тепла", size=11, color=BG, bold=True))

    n_fins = 6
    fin_w = 8
    fin_h = 160
    spacing = (220 - n_fins * fin_w) / (n_fins - 1)
    x_start = cx1 - 110
    for i in range(n_fins):
        fx = x_start + i * (fin_w + spacing)
        f.append(rect(fx, y_base - fin_h, fin_w, fin_h, fill="#888888", stroke=INK, sw=1.2))

        if i < n_fins - 1:
            channel_x = fx + fin_w + spacing / 2.0
            f.append(varrow(channel_x, y_base - 10, channel_x, y_base - fin_h - 25, color=RED, sw=2.2))

    f.append(text(cx1, y_base - fin_h - 45, "Вільний вертикальний потік (тяга)", size=12, bold=True, color=RED))
    f.append(text(cx1, y_base + 65, "Високий коефіцієнт тепловіддачі h", size=12.5, bold=True, color=GREEN))

    f.append(line(W / 2, 80, W / 2, H - 40, color=MUTED, sw=1.5, dash="4,4"))

    cx2 = 650
    f.append(text(cx2, 95, "Б. Горизонтальна орієнтація (Неефективна)", size=14, bold=True, color=RED))

    f.append(rect(cx2 - 110, y_base - fin_h, 18, fin_h, fill="#555555", stroke=INK, sw=1.5))
    f.append(rect(cx2 - 130, y_base - fin_h + 30, 20, 100, fill="#FF6666", stroke=RED, sw=1.5))
    f.append(text_rot(cx2 - 120, y_base - fin_h / 2, "Чип", deg=-90, size=11, color=BG, bold=True))

    n_hfins = 6
    hfin_h = 8
    hfin_w = 160
    hspacing = (fin_h - n_hfins * hfin_h) / (n_hfins - 1)
    y_hstart = y_base - fin_h
    for i in range(n_hfins):
        fy = y_hstart + i * (hfin_h + hspacing)
        f.append(rect(cx2 - 92, fy, hfin_w, hfin_h, fill="#888888", stroke=INK, sw=1.2))

        if i < n_hfins - 1:
            cy_h = fy + hfin_h + hspacing / 2.0
            cx_h = cx2 - 92 + hfin_w / 2.0
            f.append(ellipse(cx_h, cy_h, 25, hspacing * 0.4, fill="#FFE6E6", stroke=RED, sw=1.0))
            f.append(text(cx_h, cy_h + 3, "застій", size=10, color=RED))

    f.append(varrow(cx2 - 92 + hfin_w + 15, y_base - 10, cx2 - 92 + hfin_w + 35, y_base - fin_h, color=MUTED, sw=2.0))
    f.append(text(cx2 + 40, y_base - fin_h - 45, "Потік обходить ребра збоку", size=12, color=MUTED))
    f.append(text(cx2, y_base + 65, "Втрата 30-50% ефективності через застій", size=12.5, bold=True, color=RED))

    render(os.path.join(IMG, "heatsink-orientation.svg"), W, H, "".join(f))


if __name__ == '__main__':
    fig_boundary_layer()
    fig_rayleigh_benard()
    fig_heatsink_orientation()
    print("Усі фігури згенеровано у ./img/")

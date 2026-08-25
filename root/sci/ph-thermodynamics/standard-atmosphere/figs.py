# -*- coding: utf-8 -*-
"""Фігури до теми «Стандартна атмосфера ISA».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

ACCENT = "#d97706"
WARN   = "#b45309"

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))

def varrow(x1, y1, x2, y2, color=LINE, sw=2.4, head=11):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)

def head_at(x, y, dx, dy, color=INK, size=10):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.5, by + ny * size * 0.5,
               bx - nx * size * 0.5, by - ny * size * 0.5, color))

# ── Фігура 1: Вертикальна шар з температурою ────────────────────────────────
def fig_isa_layer_structure():
    W, H = 860, 560
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Вертикальна структура стандартної атмосфери ISA", size=18, bold=True))
    f.append(text(W / 2, 48, "Розподіл температури T(h) та температурні градієнти L_i по шарах", size=12.5, color=MUTED))

    x_min, x_max = 130, 580
    y_min, y_max = 490, 80
    T_min, T_max = 175, 305
    h_min, h_max = 0, 86

    def map_T(T):
        return x_min + (T - T_min) / (T_max - T_min) * (x_max - x_min)

    def map_h(h):
        return y_min - (h - h_min) / (h_max - h_min) * (y_min - y_max)

    layers = [
        (0, 11, "Тропосфера", "-6.5 K/км", "#eef2ff"),
        (11, 20, "Тропопауза / Нижня стратосфера", "0.0 K/км (Ізотерма)", "#e0e7ff"),
        (20, 32, "Середня стратосфера 1", "+1.0 K/км", "#f0fdf4"),
        (32, 47, "Середня стратосфера 2", "+2.8 K/км", "#dcfce7"),
        (47, 51, "Стратопауза / Нижня мезосфера", "0.0 K/км (Ізотерма)", "#fef9c3"),
        (51, 71, "Середня мезосфера", "-2.8 K/км", "#fff7ed"),
        (71, 84.852, "Верхня мезосфера / Мезопауза", "-2.0 K/км", "#ffedd5"),
    ]

    for h_b, h_t, name, grad, fill_c in layers:
        y1 = map_h(h_b)
        y2 = map_h(h_t)
        f.append(rect(100, y2, 490, y1 - y2, fill=fill_c, stroke="#cbd5e1", sw=1, rx=0))
        tb, w_b, h_b_box = textbox(720, (y1 + y2)/2, "%s\n%s" % (name, grad), size=10.5, pad=6, fill="#f8fafc", stroke="#cbd5e1", color=INK)
        f.append(tb)

    f.append(varrow(100, y_min, 100, y_max - 20, color=INK, sw=2))
    f.append(text(100, y_max - 28, "h (км)", size=12, bold=True, anchor="middle", color=INK))

    for h_val in [0, 11, 20, 32, 47, 51, 71, 85]:
        y_p = map_h(h_val)
        f.append(line(95, y_p, 100, y_p, color=INK, sw=1.5))
        f.append(text(88, y_p + 4, "%d" % h_val, size=11, bold=True, anchor="end", color=INK))

    f.append(varrow(100, y_min, x_max + 20, y_min, color=INK, sw=2))
    f.append(text(x_max + 25, y_min + 4, "T (K)", size=12, bold=True, anchor="start", color=INK))

    for T_val in [180, 200, 220, 240, 260, 280, 300]:
        x_p = map_T(T_val)
        f.append(line(x_p, y_min, x_p, y_min + 5, color=INK, sw=1.5))
        f.append(line(x_p, y_min, x_p, y_max, color="#e2e8f0", sw=1, dash="2 2"))
        f.append(text(x_p, y_min + 18, "%d" % T_val, size=11, anchor="middle", color=INK))

    pts_hT = [
        (0, 288.15),
        (11, 216.65),
        (20, 216.65),
        (32, 228.65),
        (47, 270.65),
        (51, 270.65),
        (71, 214.65),
        (84.852, 186.87)
    ]

    pts_px = [(map_T(T), map_h(h)) for h, T in pts_hT]
    f.append(polyline(pts_px, color=POS, sw=3.5))

    for h, T in pts_hT:
        px, py = map_T(T), map_h(h)
        f.append(circle(px, py, 4.5, fill=BG, stroke=POS, sw=2))

    f.append(text(map_T(288.15) - 20, map_h(0) + 25, "288.15 K (+15 °C)", size=10, bold=True, color=POS, anchor="end"))
    f.append(text(map_T(216.65) + 12, map_h(11) - 10, "216.65 K (-56.5 °C)", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(map_T(270.65) - 12, map_h(47) - 10, "270.65 K (-2.5 °C)", size=10, bold=True, color=POS, anchor="end"))

    return "".join(f), W, H

# ── Фігура 2: Профілі тиску та густини ─────────────────────────────────────
def fig_barometric_pressure_density():
    W, H = 840, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Профілі атмосферного тиску P(h) та густини ρ(h)", size=18, bold=True))
    f.append(text(W / 2, 48, "Нормоване падіння величин (1.0 = 101325 Па / 1.225 кг/м³) з висотою", size=12.5, color=MUTED))

    x_min, x_max = 100, 720
    y_min, y_max = 410, 80

    def map_h(h):
        return x_min + h / 50.0 * (x_max - x_min)

    def map_val(val):
        return y_min - val * (y_min - y_max)

    f.append(varrow(x_min, y_min, x_max + 20, y_min, color=INK, sw=2))
    f.append(text(x_max + 25, y_min + 4, "h (км)", size=12, bold=True, anchor="start", color=INK))

    f.append(varrow(x_min, y_min, x_min, y_max - 20, color=INK, sw=2))
    f.append(text(x_min + 10, y_max - 28, "Відносне значення (P / P₀ , ρ / ρ₀)", size=12, bold=True, anchor="start", color=INK))

    for h in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]:
        px = map_h(h)
        f.append(line(px, y_min, px, y_min + 5, color=INK, sw=1.5))
        f.append(line(px, y_min, px, y_max, color="#f1f5f9", sw=1, dash="2 2"))
        f.append(text(px, y_min + 18, "%d" % h, size=11, anchor="middle", color=INK))

    for val in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        py = map_val(val)
        f.append(line(x_min - 5, py, x_min, py, color=INK, sw=1.5))
        f.append(line(x_min, py, x_max, py, color="#f1f5f9", sw=1, dash="2 2"))
        f.append(text(x_min - 10, py + 4, "%.1f" % val, size=11, anchor="end", color=INK))

    def get_P_rho_norm(h_km):
        h_m = h_km * 1000.0
        g0 = 9.80665
        R = 287.05287
        if h_m <= 11000:
            T = 288.15 - 0.0065 * h_m
            P_rel = (T / 288.15) ** (g0 / (R * 0.0065))
            rho_rel = (T / 288.15) ** (g0 / (R * 0.0065) - 1.0)
        elif h_m <= 20000:
            T11 = 216.65
            P11_rel = (T11 / 288.15) ** (g0 / (R * 0.0065))
            rho11_rel = P11_rel / (T11 / 288.15)
            dh = h_m - 11000
            P_rel = P11_rel * math.exp(-g0 * dh / (R * T11))
            rho_rel = rho11_rel * math.exp(-g0 * dh / (R * T11))
        else:
            T20 = 216.65
            P11_rel = (T20 / 288.15) ** (g0 / (R * 0.0065))
            P20_rel = P11_rel * math.exp(-g0 * 9000 / (R * T20))
            T = T20 + 0.001 * (h_m - 20000)
            P_rel = P20_rel * ((T / T20) ** (-g0 / (R * 0.001)))
            rho_rel = P_rel / (T / 288.15)
        return P_rel, rho_rel

    pts_P = []
    pts_rho = []
    for step in range(101):
        h = step * 0.5
        Pr, rhor = get_P_rho_norm(h)
        pts_P.append((map_h(h), map_val(Pr)))
        pts_rho.append((map_h(h), map_val(rhor)))

    f.append(polyline(pts_P, color=NEG, sw=3))
    f.append(polyline(pts_rho, color=FIELD, sw=3, dash="6 3"))

    px_55, py_55 = map_h(5.5), map_val(0.5)
    f.append(circle(px_55, py_55, 4, fill=BG, stroke=NEG, sw=2))
    tb_half, _, _ = textbox(px_55 + 75, py_55 - 15, "h ≈ 5.5 км (P = 0.5 P₀)", size=10.5, pad=5, fill="#fff", stroke=NEG, color=NEG)
    f.append(tb_half)

    f.append(rect(460, 100, 240, 75, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(line(475, 122, 505, 122, color=NEG, sw=3))
    f.append(text(515, 126, "Тиск P(h) / P₀", size=12, bold=True, color=INK, anchor="start"))

    f.append(line(475, 152, 505, 152, color=FIELD, sw=3, dash="6 3"))
    f.append(text(515, 156, "Густина ρ(h) / ρ₀", size=12, bold=True, color=INK, anchor="start"))

    return "".join(f), W, H

# ── Фігура 3: Геопотенціальна vs Геометрична висота ────────────────────────
def fig_geopotential_vs_geometric():
    W, H = 840, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Геометрична висота Z проти геопотенціальної h", size=18, bold=True))
    f.append(text(W / 2, 48, "Зменшення прискорення вільного падіння g(Z) та еквівалентний потенціал g₀·h", size=12.5, color=MUTED))

    tb_earth, _, _ = textbox(180, 360, "Поверхня Землі (R_E = 6356.766 км)\ng = g₀ = 9.80665 м/с²", size=11, pad=10, fill="#f1f5f9", stroke=INK, color=INK)
    f.append(tb_earth)

    f.append(varrow(180, 480, 180, 415, color=INK, sw=1.8))
    f.append(varrow(180, 305, 180, 140, color=ACCENT, sw=2.5))
    f.append(text(190, 220, "Z (геометрична висота)", size=11.5, bold=True, color=ACCENT, anchor="start"))

    tb1, w1, h1 = textbox(560, 120,
        "Геометрична висота Z:\n"
        "Реальна фізична відстань від рівня моря (м).\n"
        "g(Z) = g₀ · ( R_E / (R_E + Z) )²\n"
        "Прискорення g спадає з висотою Z.",
        size=11.5, pad=10, fill="#fffbe6", stroke="#ffe58f", color=INK)
    f.append(tb1)

    tb2, w2, h2 = textbox(560, 260,
        "Геопотенціальна висота h:\n"
        "h = ( R_E · Z ) / ( R_E + Z )\n"
        "Шкала висоти при сталому g₀:\n"
        "g₀ · dh = g(Z) · dZ\n"
        "Спрощує рівняння гідростатики!",
        size=11.5, pad=10, fill="#e6f7ff", stroke="#91caff", color=INK)
    f.append(tb2)

    f.append(varrow(560, 180, 560, 200, color=NEG, sw=2))

    tb3, w3, h3 = textbox(560, 410,
        "Приклад на Z = 80.0 км:\n"
        "h = (6356.766 · 80) / (6356.766 + 80) = 79.006 км\n"
        "Похибка без геопотенціалу: ~1.24% (падіння g на 2.5%)",
        size=11, pad=10, fill="#f6ffed", stroke="#b7eb8f", color=INK)
    f.append(tb3)

    return "".join(f), W, H

# ── Фігура 4: Барометрична висота та висота за густиною ─────────────────────
def fig_altimetry_barometric():
    W, H = 880, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Принцип барометричної альтиметрії та висота за густиною", size=18, bold=True))
    f.append(text(W / 2, 48, "Вплив відхилення температури ΔT_ISA на барометричну та висоту за густиною", size=12.5, color=MUTED))

    x_min, x_max = 120, 560
    y_min, y_max = 410, 100

    f.append(varrow(x_min, y_min, x_max + 20, y_min, color=INK, sw=2))
    f.append(text(x_max + 25, y_min + 4, "Тиск P (гПа)", size=12, bold=True, anchor="start", color=INK))

    f.append(varrow(x_min, y_min, x_min, y_max - 20, color=INK, sw=2))
    f.append(text(x_min, y_max - 28, "Висота h (м / фути)", size=12, bold=True, anchor="middle", color=INK))

    pts_isa = [(x_min + (1.0 - math.exp(-h/8000))*400, y_min - h/3000*280) for h in range(0, 3100, 100)]
    f.append(polyline(pts_isa, color=INK, sw=2.5))

    pts_hot = [(x_min + (1.0 - math.exp(-h/8500))*400, y_min - h/3000*280) for h in range(0, 3100, 100)]
    f.append(polyline(pts_hot, color=POS, sw=2.5, dash="6 3"))

    pts_cold = [(x_min + (1.0 - math.exp(-h/7500))*400, y_min - h/3000*280) for h in range(0, 3100, 100)]
    f.append(polyline(pts_cold, color=NEG, sw=2.5, dash="6 3"))

    P_meas_x = x_min + (1.0 - math.exp(-2000/8000))*400
    f.append(line(P_meas_x, y_min, P_meas_x, y_max, color=WARN, sw=1.8, dash="3 3"))
    f.append(text(P_meas_x, y_min + 20, "Виміряний P", size=11, bold=True, color=WARN, anchor="middle"))

    h_isa_y = y_min - 2000/3000*280
    f.append(circle(P_meas_x, h_isa_y, 5, fill=BG, stroke=INK, sw=2))

    h_hot_y = y_min - 2125/3000*280
    f.append(circle(P_meas_x, h_hot_y, 5, fill=BG, stroke=POS, sw=2))

    h_cold_y = y_min - 1875/3000*280
    f.append(circle(P_meas_x, h_cold_y, 5, fill=BG, stroke=NEG, sw=2))

    tb_marks, _, _ = textbox(720, 260,
        "Показання приладу: h_p = 2000 м\n\n"
        "Гарячий день (ISA+15 °C):\n"
        "h_real > h_p\n\n"
        "Холодний день (ISA-15 °C):\n"
        "h_real < h_p (НЕБЕЗПЕКА!)",
        size=11, pad=10, fill="#f8fafc", stroke="#cbd5e1", color=INK)
    f.append(tb_marks)

    tb, w, h = textbox(720, 100,
        "Правило безпеки:\n"
        "«From High to Low, Look Out Below!»\n"
        "У холоді прилад завищує висоту!",
        size=11, pad=8, fill="#fff1f0", stroke="#ffa39e", color=POS)
    f.append(tb)

    return "".join(f), W, H

def main():
    figs = [
        ("isa-layer-structure.svg", fig_isa_layer_structure),
        ("barometric-pressure-density.svg", fig_barometric_pressure_density),
        ("geopotential-vs-geometric.svg", fig_geopotential_vs_geometric),
        ("altimetry-barometric.svg", fig_altimetry_barometric),
    ]

    for fname, func in figs:
        path = os.path.join(IMG, fname)
        svg_content, w, h = func()
        full_svg = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
            '<defs>\n'
            '  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
            '    <path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/>\n'
            '  </marker>\n'
            '</defs>\n'
            '%s\n'
            '</svg>\n' % (w, h, w, h, LINE, svg_content)
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(full_svg)
        print("Згенеровано: %s" % path)

if __name__ == "__main__":
    main()

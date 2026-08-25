# -*- coding: utf-8 -*-
"""Фігури до теми «Випромінювання абсолютно чорного тіла (закон Планка)».
Запуск із теки теми: python figs.py -> SVG у ./img/
"""
import sys, os, math

# Чотири рівні вгору від book/physics/thermodynamics/black-body-radiation до кореня репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Колірна палітра
BLUE_DARK   = "#1e3a8a"
BLUE_LIGHT  = "#dbeafe"
RED_HOT     = "#dc2626"
RED_LIGHT   = "#fee2e2"
ORANGE_WARM = "#ea580c"
YELLOW_SUN  = "#ca8a04"
GREEN_OK    = "#16a34a"
PURPLE      = "#9333ea"
MUTED_GRAY  = "#6b7280"
BORDER_GRAY = "#d1d5db"
FILL_BG     = "#f9fafb"


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


def polygon(pts, fill=FILL_BG, stroke="none", sw=0):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" '
            'stroke-width="%.1f"/>' % (p, fill, stroke, sw))


# ── Фігура 1: Модель порожнини абсолютно чорного тіла ─────────────────────
def fig_blackbody_cavity():
    W, H = 800, 480
    frags = []

    frags.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))

    cx, cy, r_outer, r_inner = 320, 240, 170, 130
    
    frags.append(circle(cx, cy, r_outer, fill="#374151", stroke=INK, sw=2))
    frags.append(circle(cx, cy, r_inner, fill="#111827", stroke=INK, sw=2))

    hole_y1, hole_y2 = cy - 18, cy + 18
    hole_x_in = cx + math.sqrt(r_inner**2 - 18**2)
    hole_x_out = cx + math.sqrt(r_outer**2 - 18**2) + 20

    hole_pts = [
        (hole_x_in - 5, hole_y1),
        (hole_x_out, hole_y1),
        (hole_x_out, hole_y2),
        (hole_x_in - 5, hole_y2)
    ]
    frags.append(polygon(hole_pts, fill="#111827", stroke="none"))

    for angle in range(30, 330, 30):
        rad = math.radians(angle)
        hx = cx + (r_outer + 18) * math.cos(rad)
        hy = cy + (r_outer + 18) * math.sin(rad)
        frags.append(circle(hx, hy, 8, fill=RED_HOT, stroke=INK, sw=1.5))

    ray_pts = [
        (hole_x_out + 120, cy - 10),
        (cx + 40, cy - 100),
        (cx - 100, cy + 50),
        (cx + 80, cy + 90),
        (cx - 40, cy - 110),
        (cx - 110, cy - 20),
        (cx + 20, cy + 115)
    ]

    for i in range(len(ray_pts) - 1):
        x1, y1 = ray_pts[i]
        x2, y2 = ray_pts[i+1]
        col = YELLOW_SUN if i == 0 else ORANGE_WARM if i < 3 else RED_HOT
        sw_val = 3.0 - i * 0.35
        frags.append(line(x1, y1, x2, y2, color=col, sw=sw_val))
        if i < 4:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            frags.append(arrow(x1, y1, mx, my, color=col, sw=sw_val))

    tb1, _, _ = textbox(hole_x_out + 130, cy - 40, "Вхідне проміння", size=13, fill="#fef3c7", stroke=YELLOW_SUN, bold=True)
    frags.append(tb1)
    frags.append(arrow(hole_x_out + 140, cy - 10, hole_x_out + 40, cy - 10, color=YELLOW_SUN, sw=2))

    tb2, _, _ = textbox(hole_x_out + 40, cy + 60, "Малий отвір d ≪ R", size=12, fill="#f3f4f6", stroke=BORDER_GRAY, bold=True)
    frags.append(tb2)

    tb3, _, _ = textbox(cx, cy - 210, "Поглинальні нерівні стінки порожнини (T = const)", size=13, fill="#fee2e2", stroke=RED_HOT, bold=True)
    frags.append(tb3)

    tb4, _, _ = textbox(cx, cy + 200, "Багаторазове відбиття та повне поглинання (a = 1)", size=13, fill="#e0e7ff", stroke=BLUE_DARK, bold=True)
    frags.append(tb4)

    svg_body = "\n".join(frags)
    doc = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n{svg_body}\n</svg>'
    with open(os.path.join(IMG, "blackbody-cavity.svg"), "w", encoding="utf-8") as f:
        f.write(doc)


# ── Фігура 2: Спектральні криві Планка для різних температур ──────────────
def fig_planck_spectrum_curves():
    W, H = 840, 560
    frags = []

    frags.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))

    ox, oy = 90, 460
    gw, gh = 700, 390

    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2))

    frags.append(text(ox + gw / 2, oy + 55, "Довжина хвилі λ (мкм)", size=15, bold=True))
    frags.append(text(ox + 10, oy - gh - 15, "Спектральна випромінювальна здатність R(λ, T)", size=14, bold=True, anchor="start"))

    max_lambda = 3.0
    for l_val in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        cx = ox + (l_val / max_lambda) * (gw - 40)
        frags.append(line(cx, oy, cx, oy + 6, color=LINE, sw=1.5))
        frags.append(text(cx, oy + 24, "%.1f" % l_val, size=13))

    h = 6.626e-34
    c = 3.0e8
    kB = 1.38e-23

    def planck_r(lam_um, T):
        if lam_um <= 0: return 0
        lam = lam_um * 1e-6
        x = (h * c) / (lam * kB * T)
        if x > 100: return 0
        val = (1.0 / (lam_um**5)) / (math.exp(x) - 1.0)
        return val

    max_val_5500 = planck_r(2.898e3 / 5500.0, 5500)
    scale_y = (gh - 50) / max_val_5500

    curves_data = [
        (5500, RED_HOT, "5500 K (Сонце)"),
        (4500, ORANGE_WARM, "4500 K"),
        (3500, YELLOW_SUN, "3500 K"),
        (2500, BLUE_DARK, "2500 K")
    ]

    wien_pts = []

    for T, color_val, label_text in curves_data:
        pts = []
        for i in range(1, 151):
            lam_um = (i / 150.0) * max_lambda
            r_val = planck_r(lam_um, T)
            cx = ox + (lam_um / max_lambda) * (gw - 40)
            cy = oy - r_val * scale_y
            cy = max(cy, oy - gh + 10)
            pts.append((cx, cy))

        frags.append(polyline(pts, color=color_val, sw=3.0))

        lam_max = 2.898e3 / T
        r_max = planck_r(lam_max, T)
        peak_x = ox + (lam_max / max_lambda) * (gw - 40)
        peak_y = oy - r_max * scale_y
        wien_pts.append((peak_x, peak_y))

        frags.append(circle(peak_x, peak_y, 5, fill=color_val, stroke=INK, sw=1.5))
        frags.append(text(peak_x + 12, peak_y - 8, label_text, color=color_val, size=13, bold=True, anchor="start"))

    frags.append(polyline(wien_pts, color=PURPLE, sw=2.2, dash="5,4"))
    frags.append(text(wien_pts[0][0] - 50, wien_pts[0][1] - 20, "Закон зсуву Віна: λ_max · T = b", color=PURPLE, size=13, bold=True))

    v_x1 = ox + (0.38 / max_lambda) * (gw - 40)
    v_x2 = ox + (0.75 / max_lambda) * (gw - 40)
    frags.append(rect(v_x1, oy - gh + 30, v_x2 - v_x1, gh - 30, fill="#fef08a", stroke="none"))
    frags.append(line(v_x1, oy, v_x1, oy - gh + 30, color=MUTED_GRAY, sw=1, dash="3,3"))
    frags.append(line(v_x2, oy, v_x2, oy - gh + 30, color=MUTED_GRAY, sw=1, dash="3,3"))
    frags.append(text((v_x1 + v_x2) / 2, oy - gh + 48, "Видиме світло", size=12, bold=True))

    svg_body = "\n".join(frags)
    doc = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n{svg_body}\n</svg>'
    with open(os.path.join(IMG, "planck-spectrum-curves.svg"), "w", encoding="utf-8") as f:
        f.write(doc)


# ── Фігура 3: Порівняння законів Релея-Джинса, Віна та Планка ─────────────
def fig_ultraviolet_catastrophe():
    W, H = 840, 540
    frags = []

    frags.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))

    ox, oy = 90, 440
    gw, gh = 700, 370

    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2))

    frags.append(text(ox + gw / 2, oy + 55, "Частота ν (УФ ← Висока частота | Низька частота → ІЧ)", size=14, bold=True))
    frags.append(text(ox + 10, oy - gh - 15, "Густина енергії випромінювання u(ν, T)", size=14, bold=True, anchor="start"))

    rj_pts = []
    for i in range(0, 85):
        nu = (i / 100.0) * 3.0
        val = 35.0 * (nu**2)
        cx = ox + (nu / 3.0) * (gw - 40)
        cy = oy - val
        if cy < oy - gh + 20:
            cy = oy - gh + 20
        rj_pts.append((cx, cy))

    wien_pts = []
    for i in range(0, 101):
        nu = (i / 100.0) * 3.0
        val = 140.0 * (nu**3) * math.exp(-1.4 * nu)
        cx = ox + (nu / 3.0) * (gw - 40)
        cy = oy - val
        wien_pts.append((cx, cy))

    planck_pts = []
    for i in range(0, 101):
        nu = (i / 100.0) * 3.0
        denom = math.exp(1.2 * nu) - 1.0 if nu > 0 else 1.0
        val = (120.0 * (nu**3) / denom) if nu > 0 else 0
        cx = ox + (nu / 3.0) * (gw - 40)
        cy = oy - val
        planck_pts.append((cx, cy))

    frags.append(polyline(rj_pts, color=RED_HOT, sw=3.0, dash="6,4"))
    frags.append(polyline(wien_pts, color=BLUE_DARK, sw=2.5, dash="4,3"))
    frags.append(polyline(planck_pts, color=GREEN_OK, sw=3.5))

    tb1, _, _ = textbox(ox + 280, oy - gh + 50, "Класичний закон Релея-Джинса (ν → ∞, u → ∞)\n«Ультрафіолетова катастрофа»", size=12, fill="#fee2e2", stroke=RED_HOT, bold=True)
    frags.append(tb1)
    frags.append(arrow(ox + 230, oy - gh + 80, ox + 200, oy - gh + 140, color=RED_HOT, sw=2))

    tb2, _, _ = textbox(ox + 550, oy - 140, "Емпіричний закон Віна\n(відхилення при низьких ν)", size=12, fill="#dbeafe", stroke=BLUE_DARK, bold=True)
    frags.append(tb2)

    tb3, _, _ = textbox(ox + 330, oy - 230, "Квантовий закон Планка (1900)\nТочний опис для всіх частот", size=13, fill="#dcfce7", stroke=GREEN_OK, bold=True)
    frags.append(tb3)

    svg_body = "\n".join(frags)
    doc = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n{svg_body}\n</svg>'
    with open(os.path.join(IMG, "ultraviolet-catastrophe.svg"), "w", encoding="utf-8") as f:
        f.write(doc)


if __name__ == "__main__":
    fig_blackbody_cavity()
    fig_planck_spectrum_curves()
    fig_ultraviolet_catastrophe()
    print("Всі SVG фігури згенеровано успішно.")

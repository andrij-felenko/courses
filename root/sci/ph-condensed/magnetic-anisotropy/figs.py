# -*- coding: utf-8 -*-
"""Фігури до теми «Магнітна анізотропія».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

BORDER = "#cbd5e1"

def save_svg(name, content):
    path = os.path.join(IMG_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# ── Фігура 1: Чотири типи анізотропії ─────────────────────────────────────────
def fig_anisotropy_types():
    W, H = 840, 420
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H))
    out.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))
    
    out.append(text(W / 2, 28, "Чотири фундаментальні джерела магнітної анізотропії", size=16, bold=True, color=INK))
    
    panels = [
        ("Магнітокристалічна", "Спін-орбітальний зв'язок\nта симетрія ґратки", "#eff6ff", "#1d4ed8", "cryst"),
        ("Анізотропія форми", "Магнітостатичне поле\nрозмагнічування Hd", "#f0fdf4", "#15803d", "shape"),
        ("Поверхнева / інтерфейсна", "Порушення симетрії\nна межі поділу (PMA)", "#fff7ed", "#c2410c", "surf"),
        ("Магнітопружна", "Механічні напруги σ\nта магнітострикція λs", "#faf5ff", "#7e22ce", "elastic")
    ]
    
    pw = 190
    ph = 330
    y0 = 55
    
    for idx, (title_str, desc_str, bg_color, main_color, ptype) in enumerate(panels):
        x0 = 16 + idx * 204
        out.append(rect(x0, y0, pw, ph, fill=bg_color, stroke=BORDER, rx=8))
        out.append(text(x0 + pw / 2, y0 + 24, title_str, size=13, bold=True, color=main_color))
        out.append(mtext(x0 + pw / 2, y0 + 44, desc_str, size=11, color=MUTED))
        
        cx = x0 + pw / 2
        cy = y0 + 190
        
        if ptype == "cryst":
            # Crystal lattice with orbital and spin arrows
            out.append(rect(cx - 50, cy - 50, 100, 100, fill="#ffffff", stroke="#94a3b8", sw=1.5))
            # Grid dots
            for dx_i in [-40, 0, 40]:
                for dy_i in [-40, 0, 40]:
                    out.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s"/>' % (cx + dx_i, cy + dy_i, main_color))
            # Easy axis arrow
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="3" stroke-dasharray="4,3"/>' % (cx, cy + 65, cx, cy - 65, main_color))
            out.append(arrow(cx, cy + 30, cx, cy - 35, color=POS, sw=2.5))
            out.append(text(cx + 15, cy - 10, "M", size=13, bold=True, color=POS, anchor="start"))
            out.append(text(cx, y0 + 295, "Ось легкого намагнічення", size=10, bold=True, color=main_color))

        elif ptype == "shape":
            # Ellipsoid showing demagnetizing field
            out.append('<ellipse cx="%.1f" cy="%.1f" rx="30" ry="65" fill="#ffffff" stroke="%s" stroke-width="2"/>' % (cx, cy, main_color))
            # Magnetization vector M
            out.append(arrow(cx, cy + 40, cx, cy - 40, color=POS, sw=2.5))
            out.append(text(cx + 14, cy - 5, "M", size=12, bold=True, color=POS, anchor="start"))
            # Charges
            out.append(text(cx, cy - 50, "+++", size=11, bold=True, color=POS))
            out.append(text(cx, cy + 56, "−−−", size=11, bold=True, color=NEG))
            # Demagnetizing field arrows (opposite to M)
            out.append(arrow(cx - 15, cy - 30, cx - 15, cy + 30, color=NEG, sw=1.5))
            out.append(text(cx - 20, cy + 2, "Hd", size=11, bold=True, color=NEG, anchor="end"))
            out.append(text(cx, y0 + 295, "Nz < Nx = Ny", size=11, bold=True, color=main_color))

        elif ptype == "surf":
            # Layered structure (interface)
            out.append(rect(cx - 70, cy - 55, 140, 50, fill="#dbeafe", stroke="#3b82f6", sw=1.5))
            out.append(rect(cx - 70, cy - 5, 140, 50, fill="#fee2e2", stroke="#ef4444", sw=1.5))
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>' % (cx - 70, cy - 5, cx + 70, cy - 5, main_color))
            # Perpendicular anisotropy arrow
            out.append(arrow(cx, cy + 35, cx, cy - 45, color=POS, sw=2.5))
            out.append(text(cx + 15, cy - 25, "M ⊥", size=12, bold=True, color=POS, anchor="start"))
            out.append(text(cx, y0 + 295, "Ефект інтерфейсу (PMA)", size=10, bold=True, color=main_color))

        elif ptype == "elastic":
            # Strained crystal lattice
            out.append(rect(cx - 65, cy - 35, 130, 70, fill="#ffffff", stroke="#a855f7", sw=1.5, rx=4))
            # Tension arrows σ
            out.append(arrow(cx - 65, cy, cx - 83, cy, color=main_color, sw=2))
            out.append(arrow(cx + 65, cy, cx + 83, cy, color=main_color, sw=2))
            out.append(text(cx - 88, cy + 4, "σ", size=12, bold=True, color=main_color, anchor="end"))
            out.append(text(cx + 88, cy + 4, "σ", size=12, bold=True, color=main_color, anchor="start"))
            # Magnetization vector aligned with tension
            out.append(arrow(cx - 40, cy, cx + 40, cy, color=POS, sw=2.5))
            out.append(text(cx, cy - 12, "M (λs > 0)", size=11, bold=True, color=POS))
            out.append(text(cx, y0 + 295, "Eme = -3/2 λs σ cos²θ", size=10, bold=True, color=main_color))

    out.append("</svg>")
    save_svg("anisotropy-types-overview.svg", "".join(out))

# ── Фігура 2: Осі легкого намагнічування у кристалах ──────────────────────────
def fig_easy_hard_axes():
    W, H = 840, 380
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H))
    out.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))

    out.append(text(W / 2, 28, "Геометрія осей легкого та важкого намагнічування у кристалах", size=16, bold=True, color=INK))

    panels = [
        ("Гексагональна (Co)", "Одноосна анізотропія\nЛегка вісь: [0001]", 20, "#eff6ff", "#1d4ed8"),
        ("ОЦК кристали (Fe)", "Кубічна (K1 > 0)\nЛегкі осі: <100>", 290, "#f0fdf4", "#15803d"),
        ("ГЦК кристали (Ni)", "Кубічна (K1 < 0)\nЛегкі осі: <111>", 560, "#fff7ed", "#c2410c")
    ]

    pw = 260
    ph = 300
    y0 = 55

    for title_str, desc_str, x0, bg_color, main_color in panels:
        out.append(rect(x0, y0, pw, ph, fill=bg_color, stroke=BORDER, rx=8))
        out.append(text(x0 + pw / 2, y0 + 22, title_str, size=13, bold=True, color=main_color))
        out.append(mtext(x0 + pw / 2, y0 + 42, desc_str, size=11, color=MUTED))

    # Panel 1: Hexagonal Co
    cx1 = 20 + pw / 2
    cy1 = y0 + 180
    # Draw cylinder / hexagonal prism representation
    out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#ffffff" stroke="%s" stroke-width="1.5"/>' %
               (cx1-30, cy1-40, cx1+30, cy1-40, cx1+50, cy1, cx1+30, cy1+40, cx1-30, cy1+40, cx1-50, cy1, main_color))
    # Easy axis z [0001]
    out.append(arrow(cx1, cy1 + 65, cx1, cy1 - 65, color=POS, sw=3))
    out.append(text(cx1 + 15, cy1 - 50, "c-вісь [0001]", size=11, bold=True, color=POS, anchor="start"))
    out.append(text(cx1 + 15, cy1 - 35, "(Легка вісь)", size=10, italic=True, color=POS, anchor="start"))
    # Hard plane
    out.append('<ellipse cx="%.1f" cy="%.1f" rx="55" ry="18" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' % (cx1, cy1, NEG))
    out.append(text(cx1 + 60, cy1 + 5, "Важка площина", size=10, bold=True, color=NEG, anchor="start"))

    # Panel 2: bcc Fe
    cx2 = 290 + pw / 2
    cy2 = y0 + 180
    # Cube
    out.append(rect(cx2 - 40, cy2 - 40, 80, 80, fill="#ffffff", stroke="#15803d", sw=1.5))
    # Axes <100> (Easy)
    out.append(arrow(cx2, cy2, cx2 + 60, cy2, color=POS, sw=2.5))
    out.append(arrow(cx2, cy2, cx2, cy2 - 60, color=POS, sw=2.5))
    out.append(text(cx2 + 65, cy2 + 4, "[100] Легка", size=10, bold=True, color=POS, anchor="start"))
    out.append(text(cx2, cy2 - 65, "[010] Легка", size=10, bold=True, color=POS))
    # Diagonal <111> (Hard)
    out.append(arrow(cx2, cy2, cx2 - 50, cy2 + 50, color=NEG, sw=2))
    out.append(text(cx2 - 55, cy2 + 60, "[111] Важка", size=10, bold=True, color=NEG, anchor="end"))

    # Panel 3: fcc Ni
    cx3 = 560 + pw / 2
    cy3 = y0 + 180
    # Cube
    out.append(rect(cx3 - 40, cy3 - 40, 80, 80, fill="#ffffff", stroke="#c2410c", sw=1.5))
    # Axes <100> (Hard)
    out.append(arrow(cx3, cy3, cx3 + 60, cy3, color=NEG, sw=2))
    out.append(arrow(cx3, cy3, cx3, cy3 - 60, color=NEG, sw=2))
    out.append(text(cx3 + 65, cy3 + 4, "[100] Важка", size=10, bold=True, color=NEG, anchor="start"))
    out.append(text(cx3, cy3 - 65, "[010] Важка", size=10, bold=True, color=NEG))
    # Diagonal <111> (Easy)
    out.append(arrow(cx3, cy3, cx3 - 50, cy3 + 50, color=POS, sw=2.5))
    out.append(text(cx3 - 55, cy3 + 60, "[111] Легка", size=10, bold=True, color=POS, anchor="end"))

    out.append("</svg>")
    save_svg("easy-hard-axes-geometry.svg", "".join(out))

# ── Фігура 3: Анізотропія форми та фактор розмагнічування ────────────────────
def fig_shape_demagnetization():
    W, H = 840, 360
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H))
    out.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))

    out.append(text(W / 2, 26, "Анізотропія форми та розмагнічувальне поле в зразках різної геометрії", size=15, bold=True, color=INK))

    panels = [
        ("Сфера", "Ізотропна форма\nNx = Ny = Nz = 1/3", 20),
        ("Витягнутий еліпсоїд / Дріт", "Легка вісь вздовж довжини\nNz < 1/3, Nx = Ny > 1/3", 290),
        ("Тонка плівка", "Легка площина в шарі\nNz = 1, Nx = Ny = 0", 560)
    ]

    pw = 260
    ph = 280
    y0 = 50

    for title_str, desc_str, x0 in panels:
        out.append(rect(x0, y0, pw, ph, fill="#f8fafc", stroke=BORDER, rx=8))
        out.append(text(x0 + pw / 2, y0 + 22, title_str, size=13, bold=True, color=INK))
        out.append(mtext(x0 + pw / 2, y0 + 40, desc_str, size=11, color=MUTED))

    # 1. Sphere
    cx1 = 20 + pw / 2
    cy1 = y0 + 175
    out.append('<circle cx="%.1f" cy="%.1f" r="45" fill="#ffffff" stroke="#0284c7" stroke-width="2"/>' % (cx1, cy1))
    out.append(arrow(cx1, cy1 + 30, cx1, cy1 - 30, color=POS, sw=2.5))
    out.append(text(cx1 + 12, cy1, "M", size=12, bold=True, color=POS, anchor="start"))
    out.append(arrow(cx1 - 18, cy1 - 20, cx1 - 18, cy1 + 20, color=NEG, sw=1.5))
    out.append(text(cx1 - 22, cy1, "Hd", size=11, bold=True, color=NEG, anchor="end"))
    out.append(text(cx1, y0 + 250, "K_shape = 0", size=11, bold=True, color="#0284c7"))

    # 2. Prolate Ellipsoid / Cylinder
    cx2 = 290 + pw / 2
    cy2 = y0 + 175
    out.append('<ellipse cx="%.1f" cy="%.1f" rx="22" ry="60" fill="#ffffff" stroke="#16a34a" stroke-width="2"/>' % (cx2, cy2))
    out.append(arrow(cx2, cy2 + 45, cx2, cy2 - 45, color=POS, sw=2.5))
    out.append(text(cx2 + 12, cy2, "M", size=12, bold=True, color=POS, anchor="start"))
    # Small charges on small surface
    out.append(text(cx2, cy2 - 48, "++", size=10, bold=True, color=POS))
    out.append(text(cx2, cy2 + 54, "--", size=10, bold=True, color=NEG))
    out.append(text(cx2, y0 + 250, "Легка вісь z", size=11, bold=True, color="#16a34a"))

    # 3. Thin Film
    cx3 = 560 + pw / 2
    cy3 = y0 + 175
    out.append(rect(cx3 - 75, cy3 - 15, 150, 30, fill="#ffffff", stroke="#ea580c", sw=2))
    # In-plane M (easy)
    out.append(arrow(cx3 - 50, cy3, cx3 + 50, cy3, color=POS, sw=2.5))
    out.append(text(cx3 - 15, cy3 - 25, "Легка площина (M in-plane)", size=11, bold=True, color=POS, anchor="end"))
    # Out-of-plane M (hard due to high Hd = Ms)
    out.append(arrow(cx3, cy3 + 10, cx3, cy3 - 40, color=NEG, sw=1.5))
    out.append(text(cx3 + 15, cy3 - 40, "Важка вісь (Hd = Ms)", size=10, bold=True, color=NEG, anchor="start"))

    out.append("</svg>")
    save_svg("shape-demagnetization-field.svg", "".join(out))

# ── Фігура 4: Астроїда Стонера — Вольфарта ──────────────────────────────────
def fig_stoner_wohlfarth():
    W, H = 840, 400
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H))
    out.append(rect(0, 0, W, H, fill="#ffffff", stroke="none"))

    out.append(text(W / 2, 26, "Астроїда Стонера — Вольфарта та петлі гістерезису при різних кутах поля", size=15, bold=True, color=INK))

    # Left Panel: Astroid Curve
    x0, y0, pw, ph = 20, 50, 380, 330
    out.append(rect(x0, y0, pw, ph, fill="#fafafa", stroke=BORDER, rx=8))
    out.append(text(x0 + pw / 2, y0 + 22, "Критична поверхня (Астроїда)", size=13, bold=True, color=INK))

    cx, cy = x0 + pw / 2, y0 + 175
    scale = 100

    # Axes
    out.append(arrow(cx - 130, cy, cx + 130, cy, color=LINE, sw=1.5))
    out.append(arrow(cx, cy + 130, cx, cy - 130, color=LINE, sw=1.5))
    out.append(text(cx + 135, cy + 4, "hx = Hx/HA", size=11, bold=True, color=INK, anchor="start"))
    out.append(text(cx, cy - 135, "hy = Hy/HA", size=11, bold=True, color=INK))

    # Astroid plot points: x = cos^3(t), y = sin^3(t)
    pts = []
    for i in range(101):
        t = 2 * math.pi * i / 100
        x_val = math.cos(t)**3
        y_val = math.sin(t)**3
        px = cx + x_val * scale
        py = cy - y_val * scale
        pts.append("%.1f,%.1f" % (px, py))

    out.append('<polygon points="%s" fill="#eff6ff" stroke="#1d4ed8" stroke-width="2.5"/>' % " ".join(pts))

    # Annotations on astroid
    out.append(text(cx + scale + 15, cy + 14, "1.0", size=10, color=MUTED, anchor="start"))
    out.append(text(cx + 10, cy - scale - 5, "1.0", size=10, color=MUTED, anchor="start"))
    out.append(text(cx + 35, cy - 35, "Оборотне\nобертання", size=10, color="#1e40af"))
    out.append(text(cx + 90, cy - 90, "Незворотне\nперемагнічення", size=10, bold=True, color=POS, anchor="start"))

    # Right Panel: Hysteresis loops at 0, 45, 90 deg
    rx0, ry0, rpw, rph = 420, 50, 400, 330
    out.append(rect(rx0, ry0, rpw, rph, fill="#ffffff", stroke=BORDER, rx=8))
    out.append(text(rx0 + rpw / 2, ry0 + 22, "Петлі гістерезису m(h) для кутів θH", size=13, bold=True, color=INK))

    # Sub-panels for 0°, 45°, 90°
    loops = [
        ("θH = 0° (Уздовж легкої осі)", "Прямокутна петля, Hc = HA", 0, POS),
        ("θH = 45° (Похиле поле)", "Похила петля, Hc = 0.5 HA", 90, "#2563eb"),
        ("θH = 90° (Перпендикулярно)", "Безгістерезисна лінія (Hc = 0)", 180, NEG)
    ]

    for title_l, desc_l, offset_y, lcolor in loops:
        lx = rx0 + 20
        ly = ry0 + 55 + offset_y
        out.append(rect(lx, ly, 360, 75, fill="#f8fafc", stroke="#e2e8f0", rx=4))
        out.append(text(lx + 10, ly + 18, title_l, size=11, bold=True, color=lcolor, anchor="start"))
        out.append(text(lx + 350, ly + 18, desc_l, size=10, color=MUTED, anchor="end"))

        # Mini graph inside subpanel
        mcx = lx + 180
        mcy = ly + 46
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#cbd5e1" stroke-width="1"/>' % (mcx - 120, mcy, mcx + 120, mcy))
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#cbd5e1" stroke-width="1"/>' % (mcx, mcy - 20, mcx, mcy + 20))

        if offset_y == 0:
            # Square loop
            out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="2"/>' %
                       (mcx-60, mcy+18, mcx+60, mcy+18, mcx+60, mcy-18, mcx-60, mcy-18, lcolor))
        elif offset_y == 90:
            # Tilted loop
            out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="2"/>' %
                       (mcx-90, mcy+18, mcx+30, mcy-18, mcx+90, mcy-18, mcx-30, mcy+18, lcolor))
        else:
            # Straight reversible line
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>' %
                       (mcx-80, mcy+18, mcx+80, mcy-18, lcolor))

    out.append("</svg>")
    save_svg("stoner-wohlfarth-astroid.svg", "".join(out))

if __name__ == "__main__":
    fig_anisotropy_types()
    fig_easy_hard_axes()
    fig_shape_demagnetization()
    fig_stoner_wohlfarth()
    print("Всі 4 фігури згенеровано у ./img/")

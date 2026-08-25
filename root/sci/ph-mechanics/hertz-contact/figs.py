# -*- coding: utf-8 -*-
"""Фігури до теми «Контакт Герца».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

PUSH  = "#c0392b"   # притискальна сила / напруження — червоне
PRESS = "#2457d6"   # тиск — синє
SHEAR = "#e67e22"   # зсув — помаранчеве
STEEL = "#7f8c8d"   # метал / опора — сіре
BG_FILL = "#f8f9fa"

def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, stroke, sw, da)

def poly(pts, fill="none", stroke=LINE, sw=1.5, dash=None, close=False):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    if close:
        d += " Z"
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, stroke, sw, da)

def render_svg(filename, width, height, elements):
    svg_defs = '''<defs>
<marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
  <path d="M 0 1 L 10 5 L 0 9 z" fill="%s"/>
</marker>
</defs>''' % LINE

    content = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" style="background-color:%s;">' % (width, height, width, height, BG),
        svg_defs,
        rect(0, 0, width, height, fill=BG, stroke="none", rx=0)
    ]
    content.extend(elements)
    content.append('</svg>')
    
    filepath = os.path.join(IMG, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))
    print(f"Generated {filepath}")

# ── Фігура 1: Геометрія контакту Герца (Сфера на площині) ────────────────────
def fig_hertz_geometry():
    W, H = 920, 540
    els = []

    # Заголовок
    els.append(text(W / 2, 30, "Геометрія деформації при герцівському контакті сфери з площиною", size=16, bold=True))

    cx, cy = 460, 175
    R = 135
    
    # Сила F вгорі
    els.append(arrow(cx, 40, cx, 105, color=PUSH, sw=2.5))
    els.append(text(cx + 100, 75, "Сила стискання F", size=14, color=PUSH, bold=True, anchor="start"))

    # Площина опори (низу)
    y_plane = cy + R # 310
    els.append(rect(140, y_plane + 2, 640, 95, fill="#eaeded", stroke=STEEL, sw=2, rx=4))
    
    # Штриховка опори
    for x_h in range(160, 760, 30):
        els.append(line(x_h, y_plane + 95, x_h + 18, y_plane + 2, color="#bdc3c7", sw=1.5))

    # Недеформоване коло сфери (пунктир)
    els.append(circle(cx, cy, R, fill="none", stroke="#95a5a6", sw=1.5))
    
    # Пляма контакту радіусом a
    a = 85

    # Сплющена сфера (деформована)
    flat_y = y_plane
    sphere_path = (f"M {cx - R:.1f} {cy:.1f} "
                   f"A {R} {R} 0 0 1 {cx - a:.1f} {flat_y:.1f} "
                   f"L {cx + a:.1f} {flat_y:.1f} "
                   f"A {R} {R} 0 0 1 {cx + R:.1f} {cy:.1f} "
                   f"A {R} {R} 0 0 1 {cx - R:.1f} {cy:.1f}")
    els.append(path(sphere_path, fill="rgba(36, 87, 214, 0.08)", stroke=NEG, sw=2.2))

    # Лінія контакту 2a
    els.append(line(cx - a, flat_y, cx + a, flat_y, color=PUSH, sw=3))
    
    # Розміри 2a внизу під опорою
    y_dim = y_plane + 140
    els.append(line(cx - a, y_dim, cx + a, y_dim, color=INK, sw=1.2))
    els.append(line(cx - a, y_plane + 97, cx - a, y_dim + 10, color=INK, sw=1.2, dash="3,3"))
    els.append(line(cx + a, y_plane + 97, cx + a, y_dim + 10, color=INK, sw=1.2, dash="3,3"))
    els.append(text(cx, y_dim + 25, "Ширина поверхні контакту 2a", size=13, color=INK, bold=True))

    # Напис для радіуса a
    els.append(text(cx, flat_y - 15, "Площина дотику (радіус a)", size=12, color=PUSH, bold=True))

    # Втискання delta (глибина) ліворуч — безпечна позиція
    y_orig_bottom = cy + R
    x_delta_line = 110
    els.append(line(x_delta_line, y_orig_bottom, x_delta_line, flat_y, color=PUSH, sw=1.8))
    els.append(line(x_delta_line - 8, y_orig_bottom, x_delta_line + 8, y_orig_bottom, color=PUSH, sw=1.2))
    els.append(line(x_delta_line - 8, flat_y, x_delta_line + 8, flat_y, color=PUSH, sw=1.2))
    els.append(text(x_delta_line - 12, (y_orig_bottom + flat_y)/2 + 4, "Глибина δ", size=13, color=PUSH, bold=True, anchor="end"))

    # Радіус кривини R
    els.append(arrow(cx, cy, cx - R * 0.707, cy - R * 0.707, color=INK, sw=1.8))
    els.append(text(cx - 100, cy - 80, "Радіус кривини R", size=13, bold=True, anchor="end"))

    # Інформаційні блоки збоку
    txt_box1 = "Зведена кривина:\n1/R* = 1/R₁ + 1/R₂"
    txt_box2 = "Зведений модуль:\n1/E* = (1-ν₁²)/E₁ + (1-ν₂²)/E₂"
    els.append(textbox(730, 130, txt_box1, size=12, pad=8, fill="#ebf5fb", stroke=NEG, sw=1.5)[0])
    els.append(textbox(730, 210, txt_box2, size=12, pad=8, fill="#ebf5fb", stroke=NEG, sw=1.5)[0])

    render_svg("hertz-contact-geometry.svg", W, H, els)

# ── Фігура 2: Напівкульовий розподіл тиску Герца ────────────────────────────
def fig_hertz_pressure():
    W, H = 880, 480
    els = []

    els.append(text(W / 2, 30, "Розподіл контактного тиску p(r) за теорією Герца", size=16, bold=True))

    # Вісь координат
    cx, cy = 440, 360  # Базова лінія (поверхня контакту)
    a_px = 220
    p0_px = 200

    # Вісь X (радіус r)
    els.append(arrow(120, cy, 760, cy, color=INK, sw=1.8))
    els.append(text(775, cy + 5, "r", size=15, bold=True, italic=True))
    
    # Вісь Y (тиск p)
    els.append(arrow(cx, cy + 20, cx, cy - p0_px - 40, color=PRESS, sw=1.8))
    els.append(text(cx - 25, cy - p0_px - 40, "p", size=15, color=PRESS, bold=True, italic=True))

    # Позначки -a, 0, +a
    els.append(line(cx - a_px, cy - 8, cx - a_px, cy + 8, color=INK, sw=1.5))
    els.append(line(cx + a_px, cy - 8, cx + a_px, cy + 8, color=INK, sw=1.5))
    els.append(text(cx - a_px, cy + 28, "−a", size=14, bold=True))
    els.append(text(cx + a_px, cy + 28, "+a", size=14, bold=True))
    els.append(text(cx, cy + 28, "0 (центр контакту)", size=13, color=MUTED))

    # Еліптична дуга тиску p(r) = p0 * sqrt(1 - (r/a)^2)
    pts = []
    n_steps = 60
    for i in range(n_steps + 1):
        t = -1.0 + 2.0 * i / n_steps
        x = cx + t * a_px
        y = cy - p0_px * math.sqrt(max(0.0, 1.0 - t * t))
        pts.append((x, y))
    
    # Заповнена зона тиску
    poly_pts = [(cx - a_px, cy)] + pts + [(cx + a_px, cy)]
    els.append(poly(poly_pts, fill="rgba(36, 87, 214, 0.15)", stroke=PRESS, sw=2.5, close=True))

    # Максимальний тиск p0
    els.append(line(cx - 20, cy - p0_px, cx + 20, cy - p0_px, color=PUSH, sw=1.8, dash="4,3"))
    els.append(text(cx + 120, cy - p0_px + 4, "Пік тиску p₀ = 3F / (2πa²)", size=13, color=PUSH, bold=True))

    # Середній тиск p_mean = 2/3 p0
    y_mean = cy - (2.0 / 3.0) * p0_px
    els.append(line(cx - a_px + 20, y_mean, cx + a_px - 20, y_mean, color=FIELD, sw=1.8, dash="6,4"))
    els.append(text(cx - 160, y_mean - 8, "Середній тиск p_сер = (2/3)p₀", size=12, color=FIELD, bold=True))

    # Пояснювальний блок праворуч вгорі
    txt_formula = "Параболічний розподіл тиску:\np(r) = p₀ · √(1 − r²/a²)"
    els.append(textbox(680, 100, txt_formula, size=13, pad=10, fill="#f4f6f8", stroke=PRESS, sw=1.5)[0])

    render_svg("hertz-pressure-distribution.svg", W, H, els)

# ── Фігура 3: Підповерхневі зсувні напруження та глибина піку ───────────────
def fig_subsurface_shear():
    W, H = 900, 540
    els = []

    els.append(text(W / 2, 30, "Розподіл напружень по глибині z під центром контакту (r = 0)", size=16, bold=True))

    # Осі: X — напруження/p0 (0 до 1.0), Y — глибина z/a (0 до 2.5)
    ox, oy = 180, 100
    scale_x = 420  # 1.0 p0 = 420px
    scale_y = 150  # 1.0 z/a = 150px

    # Вісь Х (напруження σ/p0, τ/p0)
    els.append(arrow(ox, oy, ox + scale_x + 60, oy, color=INK, sw=1.8))
    els.append(text(ox + scale_x + 90, oy + 5, "Напруження / p₀", size=14, bold=True))

    # Вісь Y (глибина z/a спрямована донизу)
    els.append(arrow(ox, oy, ox, oy + int(2.4 * scale_y) + 30, color=INK, sw=1.8))
    els.append(text(ox - 50, oy + int(2.4 * scale_y) + 30, "Глибина z / a", size=14, bold=True))

    # Позначки на осі X (0.2, 0.4, 0.6, 0.8, 1.0)
    for tick in [0.2, 0.4, 0.6, 0.8, 1.0]:
        tx = ox + tick * scale_x
        els.append(line(tx, oy - 5, tx, oy + 5, color=INK, sw=1.2))
        els.append(text(tx, oy - 12, "%.1f" % tick, size=12))

    # Позначки на осі Y (0.5a, 1.0a, 1.5a, 2.0a)
    for tick in [0.5, 1.0, 1.5, 2.0]:
        ty = oy + tick * scale_y
        els.append(line(ox - 5, ty, ox + 5, ty, color=INK, sw=1.2))
        els.append(text(ox - 30, ty + 4, "%.1fa" % tick, size=12))

    # Розрахунок точок напружень вздовж осі z (для ν = 0.3)
    pts_sz, pts_sx, pts_tau = [], [], []
    steps = 50
    nu = 0.3

    for i in range(steps + 1):
        za = 2.3 * i / steps
        y_pos = oy + za * scale_y
        
        # sigma_z
        sz = 1.0 / (1.0 + za * za)
        pts_sz.append((ox + sz * scale_x, y_pos))
        
        # sigma_x (радіальне)
        if za < 1e-4:
            sx = 0.5 + nu
        else:
            sx = (1.0 + nu) * (1.0 - za * math.atan(1.0 / za)) - 0.5 / (1.0 + za * za)
        pts_sx.append((ox + sx * scale_x, y_pos))

        # tau_max
        tau = 0.5 * abs(sz - sx)
        pts_tau.append((ox + tau * scale_x, y_pos))

    # Лінії кривих
    els.append(poly(pts_sz, fill="none", stroke=PRESS, sw=2.2))
    els.append(poly(pts_sx, fill="none", stroke=STEEL, sw=2.0, dash="5,3"))
    els.append(poly(pts_tau, fill="none", stroke=SHEAR, sw=2.8))

    # Виділення піку tau_max ≈ 0.31 p0 при z ≈ 0.48 a
    z_peak = 0.48
    tau_peak = 0.31
    px_peak = ox + tau_peak * scale_x
    py_peak = oy + z_peak * scale_y

    els.append(circle(px_peak, py_peak, 6, fill=SHEAR, stroke=INK, sw=1.5))
    els.append(line(ox, py_peak, px_peak, py_peak, color=SHEAR, sw=1.5, dash="4,3"))
    els.append(line(px_peak, oy, px_peak, py_peak, color=SHEAR, sw=1.5, dash="4,3"))

    # Пояснювальний блок для піку
    txt_peak = "Пік зсувного напруження!\nτ_макс ≈ 0.31·p₀ на глибині z ≈ 0.48a\n(Осереддя втомного викришування)"
    els.append(textbox(px_peak + 150, py_peak, txt_peak, size=12, pad=10, fill="#fef9e7", stroke=SHEAR, sw=1.8)[0])

    # Легенда графіків
    els.append(line(650, 110, 680, 110, color=PRESS, sw=2.2))
    els.append(text(690, 114, "Осьове стиснення σ_z", size=13, anchor="start"))

    els.append(line(650, 140, 680, 140, color=STEEL, sw=2.0, dash="5,3"))
    els.append(text(690, 144, "Радіальне стиснення σ_x = σ_y", size=13, anchor="start"))

    els.append(line(650, 170, 680, 170, color=SHEAR, sw=2.8))
    els.append(text(690, 174, "Макс. зсувне напруження τ_макс", size=13, color=SHEAR, anchor="start", bold=True))

    render_svg("subsurface-shear-stress.svg", W, H, els)

# ── Фігура 4: Порівняння точкового (сфера) та лінійного (циліндр) контакту ───
def fig_sphere_vs_cylinder():
    W, H = 920, 460
    els = []

    els.append(text(W / 2, 30, "Порівняння точкового (сфера) та лінійного (циліндр) герцівського контакту", size=16, bold=True))

    # Скляний поділ на дві секції
    els.append(line(W / 2, 60, W / 2, H - 40, color="#d5dbdb", sw=1.5, dash="6,4"))

    # ── Ліворуч: Точковий контакт (Сфера) ──
    lc_x = 230
    els.append(text(lc_x, 70, "Точковий контакт (Сфера на площині)", size=15, color=NEG, bold=True))

    # Схема кругової плями
    els.append(circle(lc_x, 180, 70, fill="rgba(36, 87, 214, 0.1)", stroke=NEG, sw=2))
    els.append(text(lc_x, 175, "Кругова пляма", size=13, bold=True))
    els.append(text(lc_x, 195, "радіуса a", size=13, color=NEG))

    txt_left = ("Площа контакту: A = π · a²\n"
                "Залежність радіуса: a ∝ F¹/³\n"
                "Максимальний тиск: p₀ ∝ F¹/³\n"
                "Застосування: шарикопідшипники,\n"
                "індентування, конформні сфери")
    els.append(textbox(lc_x, 340, txt_left, size=12, pad=10, fill="#ebf5fb", stroke=NEG, sw=1.5)[0])

    # ── Праворуч: Лінійний контакт (Циліндр) ──
    rc_x = 690
    els.append(text(rc_x, 70, "Лінійний контакт (Циліндр на площині)", size=15, color=PUSH, bold=True))

    # Схема прямокутної плями
    w_rect, h_rect = 65, 140
    els.append(rect(rc_x - w_rect/2, 180 - h_rect/2, w_rect, h_rect, fill="rgba(192, 57, 43, 0.1)", stroke=PUSH, sw=2, rx=4))
    els.append(text(rc_x, 173, "Прямокутник", size=13, color=PUSH, bold=True))
    els.append(text(rc_x, 193, "2b × L", size=13, color=PUSH))

    txt_right = ("Площа контакту: A = 2b · L\n"
                 "Залежність півширини: b ∝ F¹/²\n"
                 "Максимальний тиск: p₀ ∝ F¹/²\n"
                 "Застосування: роликопідшипники,\n"
                 "зубчасті колеса (шестерні), рейки")
    els.append(textbox(rc_x, 340, txt_right, size=12, pad=10, fill="#fadbd8", stroke=PUSH, sw=1.5)[0])

    render_svg("sphere-vs-cylinder-contact.svg", W, H, els)

if __name__ == '__main__':
    fig_hertz_geometry()
    fig_hertz_pressure()
    fig_subsurface_shear()
    fig_sphere_vs_cylinder()
    print("Всі фігури успішно згенеровано!")

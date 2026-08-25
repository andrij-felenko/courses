# -*- coding: utf-8 -*-
"""Фігури до теми «Тривимірна діаграма спрямованості».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

MAIN_COLOR = "#2563eb"   # акцентний синій (головний промінь)
SIDE_COLOR = "#d97706"   # бурштиновий (бічні пелюстки)
NULL_COLOR = "#dc2626"   # червоний (нуль)
GRID_COLOR = "#94a3b8"   # сірий для сітки координат
CARD       = FILL        # картка
BORDER     = LINE        # межа


# Локальні допоміжні фігури SVG
def ellipse(cx, cy, rx, ry, fill="none", stroke=INK, sw=1.5, opacity=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    op = f' opacity="{opacity}"' if opacity != 1.0 else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d}{op}/>'

def circle(cx, cy, r, fill="none", stroke=INK, sw=1.5, opacity=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    op = f' opacity="{opacity}"' if opacity != 1.0 else ''
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{d}{op}/>'

def path(d, fill="none", stroke=INK, sw=1.5, opacity=1.0, stroke_linejoin="miter"):
    op = f' opacity="{opacity}"' if opacity != 1.0 else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}" stroke-linejoin="{stroke_linejoin}"{op}/>'



# ── 1. Сферична система координат антени ─────────────────────────────────────
def fig_spherical_coords():
    W, H = 720, 380
    f = [text(W / 2, 24, "Сферична система координат для 3D-діаграми", size=16, bold=True)]

    # Центр системи координат
    cx, cy = 260, 210

    # Вісі координат (аксонометрія)
    # Z — вертикально вгору
    f.append(arrow(cx, cy, cx, cy - 140, color=INK, sw=2))
    f.append(text(cx, cy - 152, "Z (полярна вісь)", size=13, bold=True, color=INK))

    # Y — праворуч з невеликим підйомом
    f.append(arrow(cx, cy, cx + 180, cy - 40, color=INK, sw=2))
    f.append(text(cx + 195, cy - 40, "Y", size=13, bold=True, color=INK))

    # X — ліворуч-вниз (перспектива)
    f.append(arrow(cx, cy, cx - 130, cy + 100, color=INK, sw=2))
    f.append(text(cx - 142, cy + 112, "X", size=13, bold=True, color=INK))

    # Меридіональний та екваторіальний еліпси сфери
    f.append(ellipse(cx, cy, 140, 50, stroke=GRID_COLOR, sw=1.2, opacity=0.6))
    f.append(ellipse(cx, cy, 60, 140, stroke=GRID_COLOR, sw=1.2, opacity=0.4))

    # Точка P(r, θ, ϕ) у просторі
    px, py = cx + 90, cy - 90
    # Вектор r
    f.append(line(cx, cy, px, py, color=MAIN_COLOR, sw=2.5))
    f.append(circle(px, py, 5, fill=MAIN_COLOR, stroke=MAIN_COLOR, sw=1))
    f.append(text(px + 45, py - 10, "P(r, θ, ϕ)", size=13, bold=True, color=MAIN_COLOR))

    # Проекція точки P на площину XY (точка P')
    p_proj_x, p_proj_y = cx + 50, cy + 30
    f.append(line(px, py, p_proj_x, p_proj_y, color=MUTED, sw=1.2, dash="4,4"))
    f.append(line(cx, cy, p_proj_x, p_proj_y, color=MUTED, sw=1.5, dash="4,4"))
    f.append(circle(p_proj_x, p_proj_y, 3, fill=MUTED, stroke=MUTED))

    # Кут θ (зенітний / полярний від вісі Z)
    f.append(path("M %d %d A 50 50 0 0 1 %d %d" % (cx, cy - 50, cx + 25, cy - 35),
                  stroke=SIDE_COLOR, sw=2, fill="none"))
    f.append(text(cx + 35, cy - 60, "θ (кут місця)", size=12, bold=True, color=SIDE_COLOR))

    # Кут ϕ (азимутальний від вісі X у площині XY)
    f.append(path("M %d %d A 40 25 0 0 1 %d %d" % (cx - 25, cy + 20, cx + 25, cy + 15),
                  stroke=FIELD, sw=2, fill="none"))
    f.append(text(cx + 5, cy + 42, "ϕ (азимут)", size=12, bold=True, color=FIELD))

    # Антена в центрі координат
    f.append(circle(cx, cy, 6, fill=POS, stroke=INK, sw=1.5))
    f.append(text(cx - 35, cy - 10, "Антена", size=11, bold=True, color=POS))

    # Права текстова картка з поясненнями (fitbox)
    lines_info = [
        "• r — відстань до точки виміру",
        "• θ — зенітний кут від вісі Z (0°..180°)",
        "• ϕ — азимутальний кут у площині XY",
        "• U(θ, ϕ) — інтенсивність хвилі",
        "• Площина XY (θ=90°) — екватор",
        "• Переріз ϕ=const — меридіан",
    ]
    f.append(fitbox(470, 60, 230, 280, "\n".join(lines_info), title="Параметри координат"))


    render(os.path.join(IMG, "spherical-coords.svg"), W, H, *f)


# ── 2. 2D-зрізи проти повної 3D-поверхні ───────────────────────────────────
def fig_cuts_vs_3d():
    W, H = 740, 360
    f = [text(W / 2, 24, "Чому двох 2D-зрізів недостатньо для повної картини", size=16, bold=True)]

    # Ліва панель: 2D-перерізи (азимут + кут місця)
    f.append(rect(20, 55, 335, 280, rx=8, fill=CARD, stroke=BORDER, sw=1))
    f.append(text(187, 80, "Плоскі 2D-зрізи (E- та H-площини)", size=13, bold=True, color=INK))

    cx1, cy1 = 110, 180
    cx2, cy2 = 265, 180
    r_max = 60

    # 2D полярна сітка 1 (E-площина)
    f.append(circle(cx1, cy1, r_max, stroke=BORDER, sw=1, dash="2,2"))
    f.append(line(cx1 - r_max - 10, cy1, cx1 + r_max + 10, cy1, color=GRID_COLOR, sw=1))
    f.append(line(cx1, cy1 - r_max - 10, cx1, cy1 + r_max + 10, color=GRID_COLOR, sw=1))
    path_e = f"M {cx1} {cy1} C {cx1+20} {cy1-55}, {cx1-20} {cy1-55}, {cx1} {cy1} C {cx1+15} {cy1+25}, {cx1-15} {cy1+25}, {cx1} {cy1} Z"
    f.append(path(path_e, fill="#93c5fd", stroke=MAIN_COLOR, sw=2, opacity=0.7))
    f.append(text(cx1, cy1 + 80, "Зріз ϕ=0° (E-plane)", size=11, bold=True, color=INK))

    # 2D полярна сітка 2 (H-площина)
    f.append(circle(cx2, cy2, r_max, stroke=BORDER, sw=1, dash="2,2"))
    f.append(line(cx2 - r_max - 10, cy2, cx2 + r_max + 10, cy2, color=GRID_COLOR, sw=1))
    f.append(line(cx2, cy2 - r_max - 10, cx2, cy2 + r_max + 10, color=GRID_COLOR, sw=1))
    path_h = f"M {cx2} {cy2} C {cx2+35} {cy2-50}, {cx2-35} {cy2-50}, {cx2} {cy2} Z"
    f.append(path(path_h, fill="#fde68a", stroke=SIDE_COLOR, sw=2, opacity=0.7))

    f.append(text(cx2, cy2 + 80, "Зріз θ=90° (H-plane)", size=11, bold=True, color=INK))

    f.append(text(187, 290, "⚠️ Не видно діагональних витоків між площинами", size=10, color=POS, bold=True))

    # Права панель: Повна 3D-поверхня
    f.append(rect(380, 55, 340, 280, rx=8, fill=CARD, stroke=BORDER, sw=1))
    f.append(text(550, 80, "Повна 3D-діаграма спрямованості", size=13, bold=True, color=INK))

    cx3, cy3 = 550, 200
    f.append(ellipse(cx3, cy3 - 40, 45, 75, fill="#3b82f6", stroke=MAIN_COLOR, sw=2, opacity=0.6))
    f.append(ellipse(cx3, cy3 - 40, 30, 75, fill="none", stroke="#1d4ed8", sw=1, dash="3,3"))
    f.append(circle(cx3 - 50, cy3 + 20, 22, fill="#f59e0b", stroke=SIDE_COLOR, sw=1.5, opacity=0.6))
    f.append(circle(cx3 + 50, cy3 + 20, 22, fill="#f59e0b", stroke=SIDE_COLOR, sw=1.5, opacity=0.6))
    f.append(circle(cx3, cy3 + 45, 18, fill="#ef4444", stroke=NULL_COLOR, sw=1.5, opacity=0.6))

    f.append(circle(cx3, cy3, 5, fill=INK, stroke=INK))
    f.append(text(cx3, cy3 - 125, "Головний 3D-промінь", size=11, bold=True, color=MAIN_COLOR))
    f.append(text(cx3 - 75, cy3 + 50, "Паразитний витік", size=10, bold=True, color=SIDE_COLOR))
    f.append(text(cx3 + 75, cy3 + 50, "Паразитний витік", size=10, bold=True, color=SIDE_COLOR))

    f.append(text(550, 290, "✓ Повний облік інтегральної потужності P_rad", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG, "cuts-vs-3d.svg"), W, H, *f)


# ── 3. 3D-діаграма диполя («бублик») ─────────────────────────────────────────
def fig_dipole_3d_torus():
    W, H = 720, 360
    f = [text(W / 2, 24, "3D-діаграма напівхвильового диполя (тор / «бублик»)", size=16, bold=True)]

    cx, cy = 250, 190

    f.append(line(cx, cy - 140, cx, cy + 140, color=INK, sw=4))
    f.append(circle(cx, cy, 6, fill=POS, stroke=INK, sw=1.5))
    f.append(text(cx - 55, cy + 5, "Диполь (вісь Z)", size=11, bold=True, color=INK))

    f.append(ellipse(cx, cy, 170, 90, fill="#60a5fa", stroke=MAIN_COLOR, sw=2, opacity=0.35))
    f.append(ellipse(cx, cy, 30, 90, fill=BG, stroke=NULL_COLOR, sw=2))

    f.append(ellipse(cx, cy, 170, 30, stroke="#1d4ed8", sw=1.2, dash="3,3"))
    f.append(ellipse(cx, cy, 120, 60, stroke="#1d4ed8", sw=1, dash="2,2"))

    f.append(arrow(cx, cy, cx + 170, cy, color=FIELD, sw=2))
    f.append(text(cx + 90, cy - 12, "Максимум U_max (θ=90°)", size=11, bold=True, color=FIELD))

    f.append(arrow(cx, cy - 60, cx, cy - 110, color=NULL_COLOR, sw=1.8))
    f.append(text(cx + 40, cy - 115, "Нуль випромінювання (θ=0°)", size=11, bold=True, color=NULL_COLOR))

    f.append(arrow(cx, cy + 60, cx, cy + 110, color=NULL_COLOR, sw=1.8))
    f.append(text(cx + 45, cy + 115, "Нуль випромінювання (θ=180°)", size=11, bold=True, color=NULL_COLOR))

    lines_dipole = [
        "• Форма: симетричний тор (бублик)",
        "• U(θ) = U_max · sin²(θ)",
        "• Азимутальна симетрія",
        "• Нулі: уздовж дроту (θ=0°, 180°)",
        "• Максимум: впоперек (θ=90°)",
        "• Підсилення: D_max = 1.64 (2.15 дБі)",
    ]
    f.append(fitbox(460, 60, 240, 270, "\n".join(lines_dipole), title="Параметри 3D-тора"))

    render(os.path.join(IMG, "dipole-3d-torus.svg"), W, H, *f)


# ── 4. Гострий 3D-промінь та тілесний кут Ω_A ───────────────────────────────
def fig_pencil_beam_3d():
    W, H = 720, 360
    f = [text(W / 2, 24, "3D-промінь високонаправленої антени та тілесний кут Ω_A", size=16, bold=True)]

    cx, cy = 120, 190
    f.append(circle(cx, cy, 8, fill=POS, stroke=INK, sw=2))
    f.append(text(cx, cy + 25, "Антена", size=12, bold=True, color=INK))

    p_top_x, p_top_y = 420, 90
    p_bot_x, p_bot_y = 420, 290
    f.append(path("M %d %d L %d %d A 40 100 0 0 0 %d %d Z" %
                  (cx, cy, p_top_x, p_top_y, p_bot_x, p_bot_y),
                  fill="#93c5fd", stroke=MAIN_COLOR, sw=2, opacity=0.5))
    f.append(ellipse(420, 190, 40, 100, fill="#3b82f6", stroke=MAIN_COLOR, sw=2, opacity=0.4))

    f.append(ellipse(310, 190, 25, 60, stroke=SIDE_COLOR, sw=2, dash="4,4"))
    f.append(text(310, 115, "Контур HPBW (-3 дБ)", size=11, bold=True, color=SIDE_COLOR))

    f.append(ellipse(210, 190, 18, 45, fill="#fde68a", stroke=SIDE_COLOR, sw=1.5, opacity=0.5))
    f.append(text(210, 255, "3D бічні кільця", size=10, bold=True, color=SIDE_COLOR))

    f.append(arrow(cx, cy, 420, 190, color=MAIN_COLOR, sw=1.5))

    f.append(text(435, 195, "U_max", size=12, bold=True, color=MAIN_COLOR))
    f.append(text(350, 215, "Тілесний кут Ω_A (стерадіани)", size=11, bold=True, color=INK))

    lines_beam = [
        "• D_max = 4π / Ω_A",
        "• Ω_A — тілесний кут пучка",
        "• Вужчий конус → менший Ω_A",
        "• Оцінка Крауса:",
        "  D_max ≈ 41253 / (HPBW_θ° · HPBW_ϕ°)",
        "• Підсилення росте як 1/Ω_A",
    ]
    f.append(fitbox(460, 60, 240, 270, "\n".join(lines_beam), title="Кут і спрямованість"))

    render(os.path.join(IMG, "pencil-beam-3d.svg"), W, H, *f)


# ── 5. Сітка чисельного інтегрування на сфері ────────────────────────────────
def fig_spherical_integration_grid():
    W, H = 720, 360
    f = [text(W / 2, 24, "Дискретизація сфери та вагова функція sin(θ)", size=16, bold=True)]

    cx, cy = 240, 190
    R = 130

    f.append(circle(cx, cy, R, stroke=GRID_COLOR, sw=1.5))
    f.append(ellipse(cx, cy, R, 40, stroke=GRID_COLOR, sw=1.2, dash="3,3"))
    f.append(line(cx, cy - R - 15, cx, cy + R + 15, color=INK, sw=1.5))
    f.append(text(cx, cy - R - 25, "Z (полярна вісь)", size=11, bold=True, color=INK))

    f.append(rect(cx + 60, cy - 15, 30, 30, rx=2, fill="#86efac", stroke=FIELD, sw=2))
    f.append(text(cx + 75, cy - 25, "dA_max (sin(90°) = 1)", size=11, bold=True, color=FIELD, anchor="middle"))

    f.append(rect(cx + 20, cy - 115, 12, 12, rx=1, fill="#fca5a5", stroke=NULL_COLOR, sw=2))
    f.append(text(cx + 26, cy - 128, "dA_pole (sin(15°) → 0)", size=11, bold=True, color=NULL_COLOR, anchor="middle"))


    for y_off in (-90, -50, 50, 90):
        rx_curr = math.sqrt(max(0, R*R - y_off*y_off))
        f.append(ellipse(cx, cy + y_off, rx_curr, rx_curr * 0.3, stroke=BORDER, sw=1, dash="2,2"))

    lines_grid = [
        "• Елемент площі сфери:",
        "  dA = r² · sin(θ) · dθ · dϕ",
        "• Повна потужність P_rad:",
        "  ∫ ∫ U(θ,ϕ)·sin(θ) dθ dϕ",
        "• sin(θ) стискає площу біля полюсів",
        "• Рівновіддалена сітка вимагає",
        "  вагових коефіцієнтів sin(θ_i)",
    ]
    f.append(fitbox(450, 60, 250, 270, "\n".join(lines_grid), title="Формула площі сфери"))

    render(os.path.join(IMG, "spherical-integration-grid.svg"), W, H, *f)



if __name__ == '__main__':
    fig_spherical_coords()
    fig_cuts_vs_3d()
    fig_dipole_3d_torus()
    fig_pencil_beam_3d()
    fig_spherical_integration_grid()
    print("Generated 5 SVG figures into ./img/")

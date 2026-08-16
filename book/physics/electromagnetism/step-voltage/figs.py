# -*- coding: utf-8 -*-
"""Фігури до теми «Крокова й дотикова напруга».
Запуск: python figs.py -> пише SVG у ./img/
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
COLOR_DARK = "#2c3e50"
COLOR_SOIL = "#8d6e63"
COLOR_GRAVEL = "#cfd8dc"


def draw_path(d, fill='none', stroke=LINE, sw=1.5, dash=None, opacity=1.0):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    op_attr = f' opacity="{opacity}"' if opacity < 1.0 else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}{op_attr}/>'


# ── Фігура 1: Воронка потенціалу та крокова напруга ───────────────────────────
def fig_step_potential_cone():
    W, H = 780, 460
    f = []
    
    ground_y = 310
    axis_x = 390
    
    # Ґрунт
    f.append(rect(40, ground_y, 700, 110, fill='#f4ebe1', stroke='#d7ccc8', sw=1.5, rx=0))
    f.append(text(160, ground_y + 90, "Однорідний ґрунт (питомий опір ρ)", size=12, italic=True, color=COLOR_SOIL))

    # Вертикальна вісь
    f.append(line(axis_x, 60, axis_x, ground_y + 80, color=COLOR_RED, sw=3))
    f.append(circle(axis_x, ground_y, 6, fill=COLOR_RED, stroke='#900', sw=1.5))
    f.append(text(axis_x, ground_y - 12, "Точка витоку струму I", size=12, bold=True, color=COLOR_RED))

    # Лінія поверхні землі
    f.append(line(40, ground_y, 740, ground_y, color='#5d4037', sw=2.5))
    f.append(text(120, ground_y - 10, "Поверхня землі", size=11, bold=True, color='#5d4037'))

    # Крива воронки потенціалу V(r)
    curve_pts = []
    for px in range(50, axis_x - 15, 5):
        r = abs(axis_x - px)
        v = min(220, 3500 / (r + 12))
        py = ground_y - v
        curve_pts.append((px, py))
    curve_pts.append((axis_x - 15, ground_y - 220))
    curve_pts.append((axis_x, ground_y - 235))
    curve_pts.append((axis_x + 15, ground_y - 220))
    for px in range(axis_x + 15, 735, 5):
        r = abs(axis_x - px)
        v = min(220, 3500 / (r + 12))
        py = ground_y - v
        curve_pts.append((px, py))

    curve_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in curve_pts)
    f.append(draw_path(curve_d, fill='none', stroke=COLOR_RED, sw=2.5))
    f.append(text(axis_x + 120, ground_y - 190, "Крива потенціалу V(r)", size=13, bold=True, color=COLOR_RED))

    # Концентричні півкола еквіпотенціальних ліній
    for rad in [35, 75, 125, 185, 250]:
        f.append(draw_path(f"M {axis_x - rad},{ground_y} A {rad},{rad} 0 0,0 {axis_x + rad},{ground_y}",
                           fill='none', stroke=COLOR_BLUE, sw=1.2, dash="4,4", opacity=0.6))

    # Дві ноги людини
    x_foot1 = axis_x + 130
    x_foot2 = axis_x + 210
    v1_y = ground_y - (3500 / (130 + 12))
    v2_y = ground_y - (3500 / (210 + 12))

    f.append(circle(x_foot1, ground_y, 4, fill=COLOR_PURPLE, stroke='#000', sw=1))
    f.append(circle(x_foot2, ground_y, 4, fill=COLOR_PURPLE, stroke='#000', sw=1))
    f.append(text(x_foot1, ground_y + 18, "Нога 1 (r₁)", size=11, bold=True, color=COLOR_PURPLE))
    f.append(text(x_foot2, ground_y + 18, "Нога 2 (r₂)", size=11, bold=True, color=COLOR_PURPLE))

    # Відстань кроку s
    f.append(line(x_foot1, ground_y + 35, x_foot2, ground_y + 35, color=COLOR_DARK, sw=1.5))
    f.append(line(x_foot1, ground_y + 28, x_foot1, ground_y + 42, color=COLOR_DARK, sw=1.5))
    f.append(line(x_foot2, ground_y + 28, x_foot2, ground_y + 42, color=COLOR_DARK, sw=1.5))
    f.append(text((x_foot1 + x_foot2) / 2, ground_y + 52, "Крок s = 0.8 м", size=11, bold=True, color=COLOR_DARK))

    # Проекції потенціалів
    f.append(line(x_foot1, ground_y, x_foot1, v1_y, color=COLOR_PURPLE, sw=1.5, dash="3,3"))
    f.append(line(x_foot2, ground_y, x_foot2, v2_y, color=COLOR_PURPLE, sw=1.5, dash="3,3"))
    f.append(circle(x_foot1, v1_y, 4, fill=COLOR_PURPLE, stroke='#fff', sw=1.5))
    f.append(circle(x_foot2, v2_y, 4, fill=COLOR_PURPLE, stroke='#fff', sw=1.5))

    f.append(line(x_foot1, v1_y, x_foot2 + 60, v1_y, color=COLOR_PURPLE, sw=1.2, dash="3,3"))
    f.append(line(x_foot2, v2_y, x_foot2 + 60, v2_y, color=COLOR_PURPLE, sw=1.2, dash="3,3"))

    f.append(arrow(x_foot2 + 45, v2_y, x_foot2 + 45, v1_y, color=COLOR_RED, sw=2))
    f.append(text(x_foot2 + 105, (v1_y + v2_y) / 2 + 4, "V_step = V₁ - V₂", size=12, bold=True, color=COLOR_RED))

    # Пояснювальний бокс
    f.append(fitbox(50, 75, 230, 85, "Особливості воронки:\n• Крутий градієнт біля витоку\n• V(r) спадає пропорційно 1/r\n• Що ближче крок, то більша V_step",
                    size=11, fill='#ffffff', stroke='#cbd5e1', sw=1.4, color=COLOR_DARK, bold=False))

    render(os.path.join(IMG, 'step-potential-cone.svg'), W, H, *f, title="Розподіл потенціалу ґрунту та виникнення крокової напруги")


# ── Фігура 2: Порівняння шляхів струму та еквівалентних схем ───────────────────
def fig_touch_vs_step_body():
    W, H = 780, 440
    f = []

    midx = W / 2
    f.append(line(midx, 45, midx, H - 15, color="#cbd5e1", sw=1.4, dash="5,5"))

    # ── ЛІВА СТОРОНА: Напруга дотику V_touch ──
    f.append(text(midx / 2, 55, "Напруга дотику (V_touch)", size=14, bold=True, color=COLOR_RED))

    f.append(rect(40, 110, 35, 160, fill='#fee2e2', stroke=COLOR_RED, sw=2, rx=4))
    f.append(text(57, 190, "Корпус V_m", size=11, bold=True, color=COLOR_RED))

    f.append(line(75, 130, 140, 130, color=COLOR_DARK, sw=3))
    f.append(circle(140, 100, 16, fill='#ffedd5', stroke=COLOR_DARK, sw=2))
    f.append(line(140, 116, 140, 190, color=COLOR_DARK, sw=4))
    f.append(circle(140, 145, 6, fill=COLOR_RED, stroke='#fff', sw=1))
    f.append(text(175, 148, "Серце", size=10, bold=True, color=COLOR_RED))
    f.append(line(140, 190, 125, 270, color=COLOR_DARK, sw=3.5))
    f.append(line(140, 190, 155, 270, color=COLOR_DARK, sw=3.5))

    f.append(line(20, 270, 360, 270, color='#5d4037', sw=2.5))
    f.append(rect(20, 270, 340, 20, fill='#f4ebe1', stroke='none', rx=0))

    f.append(draw_path("M 75,130 L 140,130 L 140,190 L 125,270", fill='none', stroke=COLOR_RED, sw=2, dash="3,3"))
    f.append(draw_path("M 140,190 L 155,270", fill='none', stroke=COLOR_RED, sw=2, dash="3,3"))
    f.append(arrow(140, 160, 140, 175, color=COLOR_RED, sw=2))

    f.append(fitbox(40, 305, 310, 115, "Еквівалентна схема V_touch:\nR_total = R_b + (R_f / 2)\n• Шлях: Рука → Серце → Ступені\n• Ступені ввімкнені паралельно (R_f/2)\n• Пряма загроза фібриляції серця",
                    size=11, fill='#ffffff', stroke='#cbd5e1', sw=1.4, color=COLOR_DARK))

    # ── ПРАВА СТОРОНА: Крокова напруга V_step ──
    f.append(text(midx + midx / 2, 55, "Крокова напруга (V_step)", size=14, bold=True, color=COLOR_BLUE))

    f.append(circle(midx + 190, 100, 16, fill='#ffedd5', stroke=COLOR_DARK, sw=2))
    f.append(line(midx + 190, 116, midx + 190, 190, color=COLOR_DARK, sw=4))
    f.append(line(midx + 190, 135, midx + 165, 175, color=COLOR_DARK, sw=2.5))
    f.append(line(midx + 190, 135, midx + 215, 175, color=COLOR_DARK, sw=2.5))
    f.append(line(midx + 190, 190, midx + 145, 270, color=COLOR_DARK, sw=3.5))
    f.append(line(midx + 190, 190, midx + 235, 270, color=COLOR_DARK, sw=3.5))

    f.append(line(midx + 20, 270, W - 20, 270, color='#5d4037', sw=2.5))
    f.append(rect(midx + 20, 270, 340, 20, fill='#f4ebe1', stroke='none', rx=0))

    f.append(draw_path(f"M {midx + 145},270 L {midx + 190},190 L {midx + 235},270", fill='none', stroke=COLOR_BLUE, sw=2.5, dash="3,3"))
    f.append(arrow(midx + 145, 270, midx + 165, 235, color=COLOR_BLUE, sw=2))
    f.append(arrow(midx + 190, 190, midx + 210, 225, color=COLOR_BLUE, sw=2))
    f.append(text(midx + 250, 215, "Струм крізь ноги", size=10, bold=True, color=COLOR_BLUE))

    f.append(fitbox(midx + 40, 305, 310, 115, "Еквівалентна схема V_step:\nR_total = R_b + 2 · R_f\n• Шлях: Ступня 1 → Ноги/Таз → Ступня 2\n• Ступені ввімкнені послідовно (2·R_f)\n• Ризик: судоми ніг → падіння → V_touch",
                    size=11, fill='#ffffff', stroke='#cbd5e1', sw=1.4, color=COLOR_DARK))

    render(os.path.join(IMG, 'touch-vs-step-body.svg'), W, H, *f, title="Шляхи струму в тілі людини та еквівалентні схеми заміщення")


# ── Фігура 3: Контур заземлення підстанції та вирівнювання потенціалів ────────
def fig_substation_potential_grading():
    W, H = 780, 420
    f = []

    ground_y = 230

    f.append(rect(40, ground_y, 700, 20, fill=COLOR_GRAVEL, stroke='#b0bec5', sw=1, rx=0))
    f.append(text(180, ground_y + 14, "Шар гравію (щебеню) ρ_s ≈ 3000 Ом·м", size=10, bold=True, color='#455a64'))

    f.append(rect(40, ground_y + 20, 700, 95, fill='#f4ebe1', stroke='#d7ccc8', sw=1, rx=0))
    f.append(text(180, ground_y + 110, "Грунтовий масив (ρ ≈ 100 Ом·м)", size=11, italic=True, color=COLOR_SOIL))

    f.append(line(40, ground_y, 740, ground_y, color='#37474f', sw=2))

    grid_y = ground_y + 50
    grid_x1, grid_x2 = 180, 600
    
    f.append(line(grid_x1, grid_y, grid_x2, grid_y, color=COLOR_GREEN, sw=3.5))
    f.append(text((grid_x1 + grid_x2) / 2, grid_y + 18, "Підземна сітка заземлення (Mesh earthing)", size=11, bold=True, color=COLOR_GREEN))

    for gx in range(grid_x1, grid_x2 + 1, 70):
        f.append(line(gx, grid_y, gx, grid_y + 60, color=COLOR_GREEN, sw=2.5))
        f.append(circle(gx, grid_y, 4, fill=COLOR_GREEN, stroke='#fff', sw=1))

    f.append(line(grid_x1 - 45, grid_y + 15, grid_x1, grid_y + 15, color=COLOR_GREEN, sw=2, dash="4,4"))
    f.append(line(grid_x1 - 90, grid_y + 35, grid_x1 - 45, grid_y + 35, color=COLOR_GREEN, sw=2, dash="4,4"))
    f.append(circle(grid_x1 - 45, grid_y + 15, 3.5, fill=COLOR_GREEN, stroke='#fff', sw=1))
    f.append(circle(grid_x1 - 90, grid_y + 35, 3.5, fill=COLOR_GREEN, stroke='#fff', sw=1))

    f.append(line(grid_x2, grid_y + 15, grid_x2 + 45, grid_y + 15, color=COLOR_GREEN, sw=2, dash="4,4"))
    f.append(line(grid_x2 + 45, grid_y + 35, grid_x2 + 90, grid_y + 35, color=COLOR_GREEN, sw=2, dash="4,4"))
    f.append(circle(grid_x2 + 45, grid_y + 15, 3.5, fill=COLOR_GREEN, stroke='#fff', sw=1))
    f.append(circle(grid_x2 + 90, grid_y + 35, 3.5, fill=COLOR_GREEN, stroke='#fff', sw=1))

    f.append(text(grid_x1 - 100, grid_y - 8, "Вирівнювальні кільця", size=10, bold=True, color=COLOR_GREEN))

    # Без сітки
    f.append(draw_path(f"M 50,{ground_y - 20} Q 390,{ground_y - 190} 730,{ground_y - 20}",
                       fill='none', stroke=COLOR_RED, sw=1.8, dash="4,4"))
    f.append(text(160, ground_y - 110, "Без сітки: крутий спад V(r) (небезпечно)", size=11, bold=True, color=COLOR_RED))

    # Із сіткою
    grid_curve = [
        (50, ground_y - 15),
        (grid_x1 - 90, ground_y - 30),
        (grid_x1 - 45, ground_y - 65),
        (grid_x1, ground_y - 130),
        (grid_x2, ground_y - 130),
        (grid_x2 + 45, ground_y - 65),
        (grid_x2 + 90, ground_y - 30),
        (730, ground_y - 15)
    ]
    grid_curve_d = "M " + " L ".join(f"{x},{y}" for x, y in grid_curve)
    f.append(draw_path(grid_curve_d, fill='none', stroke=COLOR_GREEN, sw=3))

    f.append(text((grid_x1 + grid_x2) / 2, ground_y - 145, "Потенціальне плато над сіткою (V_step ≈ 0)", size=12, bold=True, color=COLOR_GREEN))

    f.append(line(350, ground_y - 130, 430, ground_y - 130, color=COLOR_GREEN, sw=2))
    f.append(text(390, ground_y - 112, "ΔV ≈ 0", size=11, bold=True, color=COLOR_GREEN))

    f.append(fitbox(50, 355, 680, 50, "Як сітка захищає підстанцію:\n1. Створює еквіпотенціальну поверхню (плато).  2. Кільця по краях згладжують спад V(x).  3. Гравій підвищує опір R_f.",
                    size=10.5, fill='#ffffff', stroke='#cbd5e1', sw=1.2, color=COLOR_DARK))

    render(os.path.join(IMG, 'substation-potential-grading.svg'), W, H, *f, title="Вирівнювання потенціалів за допомогою сітки заземлення підстанції")


# ── Фігура 4: Поведінка та евакуація із зони розтікання струму ─────────────────
def fig_shuffle_walk_escape():
    W, H = 780, 400
    f = []

    midx = W / 2
    f.append(line(midx, 45, midx, H - 15, color="#cbd5e1", sw=1.4, dash="5,5"))

    # ── ЛІВА СТОРОНА: НЕБЕЗПЕЧНО ──
    f.append(text(midx / 2, 55, "СМЕРТЕЛЬНО НЕБЕЗПЕЧНО: Звичайний крок / Біг", size=13, bold=True, color=COLOR_RED))

    f.append(line(40, 65, 90, 240, color=COLOR_RED, sw=3))
    f.append(circle(90, 240, 6, fill=COLOR_RED, stroke='#900', sw=1.5))
    f.append(text(140, 235, "Обрив 110 кВ", size=11, bold=True, color=COLOR_RED))

    for r in [40, 80, 120, 160]:
        f.append(draw_path(f"M {90-r},240 A {r},{r} 0 0,1 {90+r},240", fill='none', stroke=COLOR_RED, sw=1, dash="3,3", opacity=0.5))

    f.append(line(20, 240, 360, 240, color='#5d4037', sw=2.5))

    f.append(circle(260, 130, 14, fill='#ffedd5', stroke=COLOR_DARK, sw=2))
    f.append(line(260, 144, 260, 200, color=COLOR_DARK, sw=3.5))
    f.append(line(260, 200, 220, 240, color=COLOR_DARK, sw=3))
    f.append(line(260, 200, 300, 240, color=COLOR_DARK, sw=3))

    f.append(arrow(220, 255, 300, 255, color=COLOR_RED, sw=2))
    f.append(text(260, 272, "Великий крок s ⇒ Велика V_step!", size=11, bold=True, color=COLOR_RED))

    f.append(fitbox(30, 285, 330, 100, "Чому бігти або стрибати небезпечно:\n• Широкий крок створює високу різницю V1 - V2.\n• Судоми м'язів ніг викликають падіння на землю.\n• При падінні виникне V_touch через серце і смерть!",
                    size=10.5, fill='#fff5f5', stroke='#feb2b2', sw=1.4, color=COLOR_RED))

    # ── ПРАВА СТОРОНА: БЕЗПЕЧНО ──
    f.append(text(midx + midx / 2, 55, "БЕЗПЕЧНО: «Гусячий крок» (Shuffling feet)", size=13, bold=True, color=COLOR_GREEN))

    f.append(line(midx + 20, 240, W - 20, 240, color='#5d4037', sw=2.5))

    f.append(circle(midx + 190, 130, 14, fill='#ffedd5', stroke=COLOR_DARK, sw=2))
    f.append(line(midx + 190, 144, midx + 190, 200, color=COLOR_DARK, sw=3.5))
    f.append(line(midx + 190, 200, midx + 185, 240, color=COLOR_DARK, sw=3))
    f.append(line(midx + 190, 200, midx + 195, 240, color=COLOR_DARK, sw=3))

    f.append(rect(midx + 175, 236, 18, 6, fill=COLOR_GREEN, stroke='#fff', sw=1, rx=2))
    f.append(rect(midx + 192, 236, 18, 6, fill=COLOR_GREEN, stroke='#fff', sw=1, rx=2))

    f.append(line(midx + 175, 255, midx + 210, 255, color=COLOR_GREEN, sw=2))
    f.append(text(midx + 192, 272, "Крок s ≈ 0 ⇒ V_step ≈ 0 B!", size=11, bold=True, color=COLOR_GREEN))

    f.append(fitbox(midx + 30, 285, 330, 100, "Техніка безпечного виходу (R ≥ 8 м):\n1. Стопи притиснуті одна до одної (носок до п'яти).\n2. Пересувайтеся не відриваючи стоп від землі.\n3. Рухайтеся повільно до виходу за радіус 8 метрів.",
                    size=10.5, fill='#f0fdf4', stroke='#86efac', sw=1.4, color=COLOR_GREEN))

    render(os.path.join(IMG, 'shuffle-walk-escape.svg'), W, H, *f, title="Правила безпечної евакуації із зони розтікання струму землі")


if __name__ == '__main__':
    fig_step_potential_cone()
    fig_touch_vs_step_body()
    fig_substation_potential_grading()
    fig_shuffle_walk_escape()
    print("Усі 4 фігури згенеровано у ./img/")

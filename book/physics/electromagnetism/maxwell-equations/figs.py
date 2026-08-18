# -*- coding: utf-8 -*-
"""Фігури до теми «Рівняння Максвелла».
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
COLOR_GRID = "#e2e8f0"


# ── Фігура 1: Чотири фундаментальні рівняння Максвелла ──────────────────────
def fig_maxwell_4_equations():
    W, H = 820, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Чотири фундаментальні рівняння Максвелла в диференціальній формі", size=16, bold=True, color=INK))

    cards = [
        {
            "x": 30, "y": 55, "w": 365, "h": 185,
            "title": "1. Закон Гаусса для електричного поля",
            "eq": "∇ · E = ρ / ε₀",
            "desc": "Джерелом електричного поля є електричний заряд.\nЛінії полів починаються на позитивних\nі закінчуються на негативних зарядах.",
            "color": COLOR_BLUE, "bg": "#f0f4ff"
        },
        {
            "x": 425, "y": 55, "w": 365, "h": 185,
            "title": "2. Закон Гаусса для магнітного поля",
            "eq": "∇ · B = 0",
            "desc": "У природі відсутні магнітні монополі.\nЛінії магнітної індукції завжди замкнені\nй не мають джерел або стоків.",
            "color": COLOR_RED, "bg": "#fff5f5"
        },
        {
            "x": 30, "y": 260, "w": 365, "h": 195,
            "title": "3. Закон електромагнітної індукції Фарадея",
            "eq": "∇ × E = -∂B / ∂t",
            "desc": "Зміна магнітного поля у часі породжує\nвихрове електричне поле. Основа роботи\nгенераторів та трансформаторів.",
            "color": COLOR_PURPLE, "bg": "#fcf4ff"
        },
        {
            "x": 425, "y": 260, "w": 365, "h": 195,
            "title": "4. Закон Ампера — Максвелла",
            "eq": "∇ × H = J + ∂D / ∂t",
            "desc": "Вихрове магнітне поле створюється як струмом\nпровідності J, так і струмом зміщення ∂D/∂t\n(зміною електричного поля).",
            "color": COLOR_GREEN, "bg": "#f0fff4"
        }
    ]

    for c in cards:
        f.append(rect(c["x"], c["y"], c["w"], c["h"], fill=c["bg"], stroke=c["color"], sw=1.8, rx=8))
        f.append(text(c["x"] + 15, c["y"] + 26, c["title"], size=13, bold=True, color=c["color"], anchor="start"))
        
        f.append(rect(c["x"] + 15, c["y"] + 40, c["w"] - 30, 42, fill="#ffffff", stroke=c["color"], sw=1.2, rx=5))
        f.append(text(c["x"] + c["w"] / 2, c["y"] + 66, c["eq"], size=16, bold=True, color=INK))
        
        f.append(fitbox(c["x"] + 15, c["y"] + 92, c["w"] - 30, c["h"] - 100, c["desc"], size=11, color=INK, fill='none', stroke='none'))

    return render(os.path.join(IMG, 'maxwell-4-equations.svg'), W, H, *f)


# ── Фігура 2: Поширення поперечної електромагнітної хвилі ────────────────────
def fig_em_wave_propagation():
    W, H = 800, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Структура плоскої поперечної електромагнітної хвилі у вакуумі", size=16, bold=True, color=INK))

    ox, oy = 80, 200
    f.append(line(ox, oy, 740, oy, color=COLOR_DARK, sw=2))
    f.append(arrow(730, oy, 755, oy, color=COLOR_DARK, sw=2))
    f.append(text(765, oy + 4, "z", size=14, bold=True, color=COLOR_DARK))

    f.append(line(ox, oy, ox, 50, color=COLOR_DARK, sw=2))
    f.append(arrow(ox, 60, ox, 40, color=COLOR_DARK, sw=2))
    f.append(text(ox - 15, 45, "E (x)", size=14, bold=True, color=COLOR_BLUE))

    f.append(line(ox, oy, 25, 275, color=COLOR_DARK, sw=2))
    f.append(arrow(35, 268, 20, 280, color=COLOR_DARK, sw=2))
    f.append(text(15, 295, "B (y)", size=14, bold=True, color=COLOR_RED))

    f.append(arrow(ox + 40, oy - 110, ox + 140, oy - 110, color=COLOR_ORANGE, sw=2.5))
    f.append(text(ox + 90, oy - 125, "Швидкість поширення c = 1/√(μ₀ε₀)", size=12, bold=True, color=COLOR_ORANGE))
    f.append(text(ox + 90, oy - 95, "Вектор Пойнтінга S = E × H", size=11, bold=True, color=COLOR_DARK))

    import math
    steps = 180
    z_start = ox
    z_end = 710
    wavelength = 280

    points_E = []
    points_B = []

    for i in range(steps + 1):
        t = i / float(steps)
        z = z_start + t * (z_end - z_start)
        phase = (z - z_start) / wavelength * 2 * math.pi
        
        amp_E = math.sin(phase) * 80
        amp_B = math.sin(phase) * 50

        ex, ey = z, oy - amp_E
        points_E.append((ex, ey))

        bx = z - amp_B * 0.5
        by = oy + amp_B * 0.6
        points_B.append((bx, by))

    for i in range(0, steps + 1, 6):
        z_curr = points_E[i][0]
        ey_curr = points_E[i][1]
        bx_curr = points_B[i][0]
        by_curr = points_B[i][1]

        if abs(ey_curr - oy) > 3:
            f.append(line(z_curr, oy, z_curr, ey_curr, color=COLOR_BLUE, sw=1.2))

        if abs(by_curr - oy) > 3:
            f.append(line(z_curr, oy, bx_curr, by_curr, color=COLOR_RED, sw=1.2))

    for i in range(len(points_E) - 1):
        f.append(line(points_E[i][0], points_E[i][1], points_E[i+1][0], points_E[i+1][1], color=COLOR_BLUE, sw=2.2))
        f.append(line(points_B[i][0], points_B[i][1], points_B[i+1][0], points_B[i+1][1], color=COLOR_RED, sw=2.2))

    f.append(rect(480, 50, 240, 50, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    f.append(line(490, 65, 520, 65, color=COLOR_BLUE, sw=2))
    f.append(text(530, 69, "Електричне поле E", size=11, bold=True, color=COLOR_BLUE, anchor='start'))
    f.append(line(490, 85, 520, 85, color=COLOR_RED, sw=2))
    f.append(text(530, 89, "Магнітне поле B", size=11, bold=True, color=COLOR_RED, anchor='start'))

    return render(os.path.join(IMG, 'em-wave-propagation.svg'), W, H, *f)


# ── Фігура 3: Шахова сітка Йі (Yee Grid) для FDTD ───────────────────────────
def fig_fdtd_yee_grid():
    W, H = 780, 350
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Просторово-часова сітка Йі (Yee Grid) для 1D FDTD розрахунку", size=16, bold=True, color=INK))

    ox, oy = 80, 270
    grid_w = 640
    grid_h = 190

    f.append(line(ox, oy, ox, oy - grid_h - 20, color=COLOR_DARK, sw=2))
    f.append(arrow(ox, oy - grid_h - 10, ox, oy - grid_h - 25, color=COLOR_DARK, sw=2))
    f.append(text(ox - 20, oy - grid_h - 20, "Час (n)", size=13, bold=True, color=COLOR_DARK))

    f.append(line(ox, oy, ox + grid_w + 20, oy, color=COLOR_DARK, sw=2))
    f.append(arrow(ox + grid_w + 10, oy, ox + grid_w + 30, oy, color=COLOR_DARK, sw=2))
    f.append(text(ox + grid_w + 25, oy + 20, "Простір (i)", size=13, bold=True, color=COLOR_DARK))

    dx_step = 100
    dt_step = 60

    x_nodes = [ox + k * dx_step for k in range(6)]
    x_labels = ["i-1", "i-1/2", "i", "i+1/2", "i+1", "i+3/2"]

    for idx, (x_pos, lbl) in enumerate(zip(x_nodes, x_labels)):
        f.append(line(x_pos, oy - 5, x_pos, oy + 5, color=COLOR_DARK, sw=1.5))
        f.append(text(x_pos, oy + 20, lbl, size=11, bold=True, color=COLOR_DARK))

    t_nodes = [oy - k * dt_step for k in range(3)]
    t_labels = ["n", "n+1/2", "n+1"]

    for idx, (t_pos, lbl) in enumerate(zip(t_nodes, t_labels)):
        f.append(line(ox - 5, t_pos, ox + 5, t_pos, color=COLOR_DARK, sw=1.5))
        f.append(text(ox - 30, t_pos + 4, lbl, size=11, bold=True, color=COLOR_DARK))

    for t_pos in t_nodes:
        f.append(line(ox, t_pos, ox + grid_w, t_pos, color=COLOR_GRID, sw=1, dash="4,4"))
    for x_pos in x_nodes:
        f.append(line(x_pos, oy, x_pos, oy - grid_h, color=COLOR_GRID, sw=1, dash="4,4"))

    for n_idx, t_pos in enumerate(t_nodes):
        for i_idx, x_pos in enumerate(x_nodes):
            is_E_pos = (i_idx % 2 == 0)
            is_E_time = (n_idx % 2 == 0)

            if is_E_pos and is_E_time:
                f.append(circle(x_pos, t_pos, 8, fill="#eef2ff", stroke=COLOR_BLUE, sw=2))
                f.append(text(x_pos, t_pos + 3, "E", size=10, bold=True, color=COLOR_BLUE))
            elif (not is_E_pos) and (not is_E_time):
                f.append(rect(x_pos - 8, t_pos - 8, 16, 16, fill="#ffefef", stroke=COLOR_RED, sw=2, rx=3))
                f.append(text(x_pos, t_pos + 3, "H", size=10, bold=True, color=COLOR_RED))

    f.append(arrow(x_nodes[2], t_nodes[0] - 10, x_nodes[3] - 10, t_nodes[1] + 10, color=COLOR_PURPLE, sw=2))
    f.append(arrow(x_nodes[4], t_nodes[0] - 10, x_nodes[3] + 10, t_nodes[1] + 10, color=COLOR_PURPLE, sw=2))
    f.append(text(x_nodes[3] + 45, t_nodes[1] + 25, "Оновлення H за похідною E", size=10, bold=True, color=COLOR_PURPLE))

    f.append(rect(460, 45, 290, 75, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(circle(480, 67, 7, fill="#eef2ff", stroke=COLOR_BLUE, sw=2))
    f.append(text(480, 70, "E", size=9, bold=True, color=COLOR_BLUE))
    f.append(text(495, 71, "Електричне поле E(i, n)", size=11, bold=True, color=COLOR_BLUE, anchor='start'))

    f.append(rect(473, 93, 14, 14, fill="#ffefef", stroke=COLOR_RED, sw=2, rx=2))
    f.append(text(480, 103, "H", size=9, bold=True, color=COLOR_RED))
    f.append(text(495, 104, "Магнітне поле H(i+1/2, n+1/2)", size=11, bold=True, color=COLOR_RED, anchor='start'))

    return render(os.path.join(IMG, 'fdtd-yee-grid.svg'), W, H, *f)


def main():
    fig_maxwell_4_equations()
    fig_em_wave_propagation()
    fig_fdtd_yee_grid()
    print("Згенеровано фігури у", IMG)

if __name__ == '__main__':
    main()

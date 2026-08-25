# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, arrow, textbox, fitbox, POS, NEG, FIELD, INK, MUTED, FILL, BG
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)


def generate_rasterization_error_fig():
    w, h = 840, 480
    frags = []
    
    grid_ox, grid_oy = 40, 380
    cell_w, cell_h = 55, 55
    cols, rows = 8, 5

    for r in range(rows):
        for c in range(cols):
            x = grid_ox + c * cell_w
            y = grid_oy - (r + 1) * cell_h
            frags.append(rect(x, y, cell_w, cell_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=0))

    start_x, start_y = grid_ox, grid_oy
    end_x, end_y = grid_ox + 7 * cell_w, grid_oy - 3 * cell_h
    frags.append(line(start_x, start_y, end_x, end_y, color=POS, sw=2.5, dash="6,4"))

    raster_points = [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2), (6, 3), (7, 3)]
    for px, py in raster_points:
        cx = grid_ox + px * cell_w + cell_w / 2
        cy = grid_oy - py * cell_h - cell_h / 2
        frags.append(circle(cx, cy, 12, fill="#e0f2fe", stroke=NEG, sw=2.0))
        frags.append(text(cx, cy + 4, "%d,%d" % (px, py), size=10, color=NEG, bold=True))

    x_col4 = grid_ox + 4 * cell_w
    y_line_at_4 = grid_oy - 4 * (3.0 / 7.0) * cell_h
    mid_y = grid_oy - 1.5 * cell_h

    frags.append(line(x_col4 - 20, mid_y, x_col4 + 20, mid_y, color=FIELD, sw=2.0, dash="3,3"))
    frags.append(text(x_col4 + 45, mid_y + 4, "M (x+1, y+1/2)", size=11, color=FIELD, bold=True))

    frags.append(line(x_col4, grid_oy - 1 * cell_h, x_col4, y_line_at_4, color=POS, sw=2.0))
    frags.append(text(x_col4 - 26, (grid_oy - 1 * cell_h + y_line_at_4) / 2 + 4, "d1", size=12, color=POS, bold=True))

    frags.append(line(x_col4, y_line_at_4, x_col4, grid_oy - 2 * cell_h, color=NEG, sw=2.0))
    frags.append(text(x_col4 - 26, (y_line_at_4 + grid_oy - 2 * cell_h) / 2 + 4, "d2", size=12, color=NEG, bold=True))

    frags.append(arrow(grid_ox - 15, grid_oy, grid_ox + cols * cell_w + 20, grid_oy, color=INK, sw=2.0))
    frags.append(text(grid_ox + cols * cell_w + 30, grid_oy + 5, "X", size=14, bold=True))

    frags.append(arrow(grid_ox, grid_oy + 15, grid_ox, grid_oy - rows * cell_h - 20, color=INK, sw=2.0))
    frags.append(text(grid_ox - 15, grid_oy - rows * cell_h - 25, "Y", size=14, bold=True))

    info_box = fitbox(500, 40, 310, 140,
                      "Оцінка похибки d1 - d2:\n"
                      "• Якщо d1 - d2 < 0 → Схід (E)\n"
                      "• Якщо d1 - d2 ≥ 0 → Північний Схід (NE)\n"
                      "Растеризація у цілих числах!",
                      size=10, fill="#f0fdf4", stroke=FIELD, sw=1.5)
    frags.append(info_box)

    os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
    render(os.path.join(os.path.dirname(__file__), 'img', 'fig-rasterization-error.svg'), w, h, *frags, title="Вибір пікселя у дискретному алгоритмі Брезенгема")


def generate_octant_symmetry_fig():
    w, h = 720, 520
    frags = []

    cx, cy = 360, 260
    radius = 180

    frags.append(line(cx - radius - 30, cy, cx + radius + 30, cy, color=INK, sw=2.0))
    frags.append(line(cx, cy - radius - 30, cx, cy + radius + 30, color=INK, sw=2.0))
    frags.append(text(cx + radius + 40, cy + 5, "+X", size=13, bold=True))
    frags.append(text(cx - radius - 55, cy + 5, "-X", size=13, bold=True))
    frags.append(text(cx - 10, cy - radius - 40, "+Y", size=13, bold=True))
    frags.append(text(cx - 10, cy + radius + 45, "-Y", size=13, bold=True))

    frags.append(line(cx - radius, cy + radius, cx + radius, cy - radius, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(cx - radius, cy - radius, cx + radius, cy + radius, color=MUTED, sw=1.5, dash="4,4"))

    octants = [
        (1, 22.5, "Октант 1", "0 ≤ dy ≤ dx", "sx=+1, sy=+1, swap=0", POS),
        (2, 67.5, "Октант 2", "0 ≤ dx < dy", "sx=+1, sy=+1, swap=1", NEG),
        (3, 112.5, "Октант 3", "0 ≤ -dx < dy", "sx=-1, sy=+1, swap=1", NEG),
        (4, 157.5, "Октант 4", "0 ≤ dy ≤ -dx", "sx=-1, sy=+1, swap=0", POS),
        (5, 202.5, "Октант 5", "0 ≤ -dy ≤ -dx", "sx=-1, sy=-1, swap=0", POS),
        (6, 247.5, "Октант 6", "0 ≤ -dx < -dy", "sx=-1, sy=-1, swap=1", NEG),
        (7, 292.5, "Октант 7", "0 ≤ dx < -dy", "sx=+1, sy=-1, swap=1", NEG),
        (8, 337.5, "Октант 8", "0 ≤ -dy ≤ dx", "sx=+1, sy=-1, swap=0", POS),
    ]

    import math
    for num, angle_deg, name, cond, code_transform, col in octants:
        rad = math.radians(angle_deg)
        tx = cx + (radius * 0.72) * math.cos(rad)
        ty = cy - (radius * 0.72) * math.sin(rad)
        box = fitbox(tx - 60, ty - 22, 120, 44, "%s\n%s" % (name, cond), size=10, fill="#ffffff", stroke=col, sw=1.5, bold=True)
        frags.append(box)

    frags.append(circle(cx, cy, 28, fill="#fffbebe6", stroke="#f59e0b", sw=2.0))
    frags.append(text(cx, cy + 4, "8-fold", size=10, color="#b45309", bold=True))

    os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
    render(os.path.join(os.path.dirname(__file__), 'img', 'fig-octant-symmetry.svg'), w, h, *frags, title="Симетрія 8 октантів площини та редукція до канонічного випадку")


def generate_midpoint_circle_fig():
    w, h = 740, 500
    frags = []

    grid_ox, grid_oy = 340, 270
    cell_size = 28
    grid_r = 7

    for i in range(-grid_r - 1, grid_r + 2):
        frags.append(line(grid_ox + i * cell_size, grid_oy - (grid_r + 1) * cell_size,
                          grid_ox + i * cell_size, grid_oy + (grid_r + 1) * cell_size, color="#f1f5f9", sw=1.0))
        frags.append(line(grid_ox - (grid_r + 1) * cell_size, grid_oy + i * cell_size,
                          grid_ox + (grid_r + 1) * cell_size, grid_oy + i * cell_size, color="#f1f5f9", sw=1.0))

    frags.append(line(grid_ox - (grid_r + 1.5) * cell_size, grid_oy, grid_ox + (grid_r + 1.5) * cell_size, grid_oy, color=INK, sw=1.8))
    frags.append(line(grid_ox, grid_oy + (grid_r + 1.5) * cell_size, grid_ox, grid_oy - (grid_r + 1.5) * cell_size, color=INK, sw=1.8))

    r_px = 6 * cell_size
    frags.append(circle(grid_ox, grid_oy, r_px, fill="none", stroke=POS, sw=2.0))

    base_points = [(0, 6), (1, 6), (2, 6), (3, 5), (4, 4)]

    all_sym_points = set()
    for x, y in base_points:
        for sx in [1, -1]:
            for sy in [1, -1]:
                all_sym_points.add((sx * x, sy * y))
                all_sym_points.add((sx * y, sy * x))

    for px, py in all_sym_points:
        cx_p = grid_ox + px * cell_size
        cy_p = grid_oy - py * cell_size
        is_base = (abs(px), abs(py)) in base_points or (abs(py), abs(px)) in base_points
        fill_col = "#dbeafe" if is_base else "#f3f4f6"
        stroke_col = NEG if is_base else MUTED
        frags.append(circle(cx_p, cy_p, cell_size * 0.38, fill=fill_col, stroke=stroke_col, sw=1.5))

    ann_box = fitbox(500, 80, 210, 130,
                     "Алгоритм кола Брезенгема:\n"
                     "• D_initial = 3 - 2R\n"
                     "• Якщо D < 0 → E (x+1, y)\n"
                     "  ΔD = 4x + 6\n"
                     "• Якщо D ≥ 0 → SE (x+1, y-1)\n"
                     "  ΔD = 4(x - y) + 10\n"
                     "8-бічна дзеркальна симетрія",
                     size=10, fill="#eff6ff", stroke=NEG, sw=1.5)
    frags.append(ann_box)

    os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
    render(os.path.join(os.path.dirname(__file__), 'img', 'fig-midpoint-circle.svg'), w, h, *frags, title="Растеризація кола Брезенгема на дискретній ґратці з 8-бічною симетрією")


if __name__ == '__main__':
    generate_rasterization_error_fig()
    generate_octant_symmetry_fig()
    generate_midpoint_circle_fig()
    print("All figures generated successfully.")

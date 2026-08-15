# -*- coding: utf-8 -*-
import sys
import os

# Four steps up to repo root scripts directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def build_figure_1():
    """Малюнок 1: Двійкова ієрархія та інтервальне розбиття масиву."""
    W, H = 960, 480
    frags = []

    y_levels = [60, 160, 260, 360]
    leaf_xs = [80 + i * 110 for i in range(8)]

    nodes_l3 = []
    leaves_val = [2, 1, 5, 3, 4, 8, 7, 6]
    for i in range(8):
        cx = leaf_xs[i]
        cy = y_levels[3]
        box = fitbox(cx - 45, cy - 25, 90, 50, f"[{i}]\nval={leaves_val[i]}", size=13, fill="#eef6ff", stroke=LINE)
        frags.append(box)
        nodes_l3.append((cx, cy))

    nodes_l2 = []
    l2_ranges = [(0, 1, 3), (2, 3, 8), (4, 5, 12), (6, 7, 13)]
    for i in range(4):
        cx = (nodes_l3[2 * i][0] + nodes_l3[2 * i + 1][0]) / 2
        cy = y_levels[2]
        r1, r2, s = l2_ranges[i]
        box = fitbox(cx - 50, cy - 25, 100, 50, f"[{r1}..{r2}]\nsum={s}", size=13, fill=FILL, stroke=LINE)
        frags.append(box)
        nodes_l2.append((cx, cy))

        frags.append(line(cx, cy + 25, nodes_l3[2 * i][0], nodes_l3[2 * i][1] - 25, color=LINE, sw=1.5))
        frags.append(line(cx, cy + 25, nodes_l3[2 * i + 1][0], nodes_l3[2 * i + 1][1] - 25, color=LINE, sw=1.5))

    nodes_l1 = []
    l1_ranges = [(0, 3, 11), (4, 7, 25)]
    for i in range(2):
        cx = (nodes_l2[2 * i][0] + nodes_l2[2 * i + 1][0]) / 2
        cy = y_levels[1]
        r1, r2, s = l1_ranges[i]
        box = fitbox(cx - 55, cy - 25, 110, 50, f"[{r1}..{r2}]\nsum={s}", size=13, fill=FILL, stroke=LINE)
        frags.append(box)
        nodes_l1.append((cx, cy))

        frags.append(line(cx, cy + 25, nodes_l2[2 * i][0], nodes_l2[2 * i][1] - 25, color=LINE, sw=1.5))
        frags.append(line(cx, cy + 25, nodes_l2[2 * i + 1][0], nodes_l2[2 * i + 1][1] - 25, color=LINE, sw=1.5))

    cx_root = (nodes_l1[0][0] + nodes_l1[1][0]) / 2
    cy_root = y_levels[0]
    root_box = fitbox(cx_root - 60, cy_root - 25, 120, 50, "[0..7]\nsum=36", size=14, bold=True, fill="#e8f8f5", stroke=LINE)
    frags.append(root_box)

    frags.append(line(cx_root, cy_root + 25, nodes_l1[0][0], nodes_l1[0][1] - 25, color=LINE, sw=1.8))
    frags.append(line(cx_root, cy_root + 25, nodes_l1[1][0], nodes_l1[1][1] - 25, color=LINE, sw=1.8))

    render(os.path.join(OUT, "fig-segment-tree-structure.svg"), W, H, *frags)


def build_figure_2():
    """Малюнок 2: Канонічна декомпозиція інтервального запиту query(1, 6)."""
    W, H = 960, 480
    frags = []

    y_levels = [60, 160, 260, 360]
    leaf_xs = [80 + i * 110 for i in range(8)]

    nodes_l3 = []
    leaves_val = [2, 1, 5, 3, 4, 8, 7, 6]
    selected_l3 = {1, 6}
    for i in range(8):
        cx = leaf_xs[i]
        cy = y_levels[3]
        is_sel = i in selected_l3
        bg_col = "#d4efdf" if is_sel else "#f4f6f8"
        st_col = FIELD if is_sel else LINE
        sw_val = 2.5 if is_sel else 1.5
        box = fitbox(cx - 45, cy - 25, 90, 50, f"[{i}]\nval={leaves_val[i]}", size=13, fill=bg_col, stroke=st_col, sw=sw_val)
        frags.append(box)
        nodes_l3.append((cx, cy))

    nodes_l2 = []
    l2_ranges = [(0, 1, 3), (2, 3, 8), (4, 5, 12), (6, 7, 13)]
    selected_l2 = {1, 2}
    for i in range(4):
        cx = (nodes_l3[2 * i][0] + nodes_l3[2 * i + 1][0]) / 2
        cy = y_levels[2]
        r1, r2, s = l2_ranges[i]
        is_sel = i in selected_l2
        bg_col = "#d4efdf" if is_sel else "#f4f6f8"
        st_col = FIELD if is_sel else LINE
        sw_val = 2.5 if is_sel else 1.5
        box = fitbox(cx - 50, cy - 25, 100, 50, f"[{r1}..{r2}]\nsum={s}", size=13, fill=bg_col, stroke=st_col, sw=sw_val)
        frags.append(box)
        nodes_l2.append((cx, cy))

        frags.append(line(cx, cy + 25, nodes_l3[2 * i][0], nodes_l3[2 * i][1] - 25, color=LINE, sw=1.5))
        frags.append(line(cx, cy + 25, nodes_l3[2 * i + 1][0], nodes_l3[2 * i + 1][1] - 25, color=LINE, sw=1.5))

    nodes_l1 = []
    l1_ranges = [(0, 3, 11), (4, 7, 25)]
    for i in range(2):
        cx = (nodes_l2[2 * i][0] + nodes_l2[2 * i + 1][0]) / 2
        cy = y_levels[1]
        r1, r2, s = l1_ranges[i]
        box = fitbox(cx - 55, cy - 25, 110, 50, f"[{r1}..{r2}]\nsum={s}", size=13, fill=FILL, stroke=LINE)
        frags.append(box)
        nodes_l1.append((cx, cy))

        frags.append(line(cx, cy + 25, nodes_l2[2 * i][0], nodes_l2[2 * i][1] - 25, color=LINE, sw=1.5))
        frags.append(line(cx, cy + 25, nodes_l2[2 * i + 1][0], nodes_l2[2 * i + 1][1] - 25, color=LINE, sw=1.5))

    cx_root = (nodes_l1[0][0] + nodes_l1[1][0]) / 2
    cy_root = y_levels[0]
    root_box = fitbox(cx_root - 60, cy_root - 25, 120, 50, "[0..7]\nsum=36", size=14, bold=True, fill=FILL, stroke=LINE)
    frags.append(root_box)

    frags.append(line(cx_root, cy_root + 25, nodes_l1[0][0], nodes_l1[0][1] - 25, color=LINE, sw=1.8))
    frags.append(line(cx_root, cy_root + 25, nodes_l1[1][0], nodes_l1[1][1] - 25, color=LINE, sw=1.8))

    leg_box = fitbox(60, 30, 220, 40, "Зелений = Канонічний вузол", size=12, fill="#d4efdf", stroke=FIELD, sw=2)
    frags.append(leg_box)

    render(os.path.join(OUT, "fig-range-query-decomposition.svg"), W, H, *frags)


def build_figure_3():
    """Малюнок 3: Механізм відкладеної пропогації (Lazy Propagation)."""
    W, H = 840, 440
    frags = []

    parent_box = fitbox(420 - 90, 60 - 30, 180, 65, "[L..R]\nval = 50\nlazy = +5", size=14, bold=True, fill="#fdecea", stroke=POS, sw=2)
    frags.append(parent_box)

    # Стрілка вниз push_down
    frags.append(arrow(420, 130, 420, 210, color=POS, sw=2.5))
    frags.append(fitbox(530 - 60, 170 - 15, 120, 30, "push_down()", size=13, fill="#ffffff", stroke=POS, sw=1.5))

    # Ліва і права дитини
    left_child = fitbox(210 - 85, 270 - 30, 170, 65, "[L..M]\nval = 25 -> 35\nlazy = +5", size=13, fill="#eaf0fd", stroke=NEG, sw=2)
    right_child = fitbox(630 - 85, 270 - 30, 170, 65, "[M+1..R]\nval = 25 -> 35\nlazy = +5", size=13, fill="#eaf0fd", stroke=NEG, sw=2)
    frags.append(left_child)
    frags.append(right_child)

    # Стрілки розгалуження від push_down
    frags.append(arrow(380, 210, 260, 235, color=LINE, sw=1.8))
    frags.append(arrow(460, 210, 580, 235, color=LINE, sw=1.8))

    # Підпис результату для батька після очищення lazy
    parent_after = fitbox(420 - 80, 370 - 20, 160, 40, "Батько: lazy = 0", size=12, fill="#e8f8f5", stroke=FIELD, sw=1.5)
    frags.append(parent_after)

    render(os.path.join(OUT, "fig-lazy-propagation.svg"), W, H, *frags)


if __name__ == "__main__":
    build_figure_1()
    build_figure_2()
    build_figure_3()
    print("Figures generated successfully.")

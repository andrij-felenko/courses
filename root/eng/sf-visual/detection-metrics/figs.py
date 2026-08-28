# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Метрики детектора'.
Вивід у ./img/
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def dashed_rect(x, y, w, h, fill="none", stroke=LINE, sw=1.5, rx=4, dash="4,3"):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
            'fill="%s" stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>' % (x, y, w, h, rx, fill, stroke, sw, dash))


def fig_pr_curve_interpolation():
    """Ілюстрація монотонної інтерполяції кривої Precision-Recall та інтеграції AP."""
    w, h = 960, 420
    frags = []

    card_w = 430
    card_h = 360
    top_y = 35

    # Panel 1: Left
    p1_x = 35
    frags.append(rect(p1_x, top_y, card_w, card_h, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    frags.append(rect(p1_x, top_y, card_w, 36, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    frags.append(text(p1_x + card_w / 2, top_y + 23, "Монотонна інтерполяція кривої PR", size=13, bold=True, color=INK))

    ax_x = p1_x + 55
    ax_y = top_y + 300
    ax_w = 340
    ax_h = 230

    frags.append(arrow(ax_x, ax_y, ax_x + ax_w + 15, ax_y, color=LINE, sw=1.5))
    frags.append(arrow(ax_x, ax_y, ax_x, ax_y - ax_h - 15, color=LINE, sw=1.5))

    frags.append(text(ax_x + ax_w + 10, ax_y + 20, "Recall (r)", size=11, bold=True, color=INK, anchor="end"))
    frags.append(text(ax_x - 10, ax_y - ax_h - 5, "Precision (p)", size=11, bold=True, color=INK, anchor="end"))

    # Grid ticks
    for i in range(1, 6):
        gx = ax_x + i * (ax_w / 5)
        val = f"{i * 0.2:.1f}"
        frags.append(line(gx, ax_y, gx, ax_y + 4, color=MUTED, sw=1.0))
        frags.append(text(gx, ax_y + 16, val, size=10, color=MUTED))
        frags.append(line(gx, ax_y, gx, ax_y - ax_h, color="#e5e7eb", sw=1.0, dash="3,3"))

    for i in range(1, 6):
        gy = ax_y - i * (ax_h / 5)
        val = f"{i * 0.2:.1f}"
        frags.append(line(ax_x - 4, gy, ax_x, gy, color=MUTED, sw=1.0))
        frags.append(text(ax_x - 8, gy + 4, val, size=10, color=MUTED, anchor="end"))
        frags.append(line(ax_x, gy, ax_x + ax_w, gy, color="#e5e7eb", sw=1.0, dash="3,3"))

    frags.append(text(ax_x - 8, ax_y + 14, "0.0", size=10, color=MUTED, anchor="end"))

    raw_pts = [
        (0.0, 1.0),
        (0.12, 1.0),
        (0.18, 0.85),
        (0.28, 0.85),
        (0.35, 0.68),
        (0.48, 0.76),
        (0.55, 0.58),
        (0.68, 0.62),
        (0.78, 0.42),
        (0.88, 0.44),
        (0.95, 0.25),
        (1.0, 0.15)
    ]

    def to_canvas(r_val, p_val):
        cx = ax_x + r_val * ax_w
        cy = ax_y - p_val * ax_h
        return cx, cy

    raw_path_d = []
    for idx, (rv, pv) in enumerate(raw_pts):
        cx, cy = to_canvas(rv, pv)
        if idx == 0:
            raw_path_d.append(f"M {cx:.1f} {cy:.1f}")
        else:
            raw_path_d.append(f"L {cx:.1f} {cy:.1f}")
    frags.append(f'<path d="{" ".join(raw_path_d)}" fill="none" stroke="{NEG}" stroke-width="2" stroke-dasharray="4,3"/>')

    interp_steps = [
        (0.0, 1.0),
        (0.12, 1.0),
        (0.12, 0.85),
        (0.28, 0.85),
        (0.28, 0.76),
        (0.48, 0.76),
        (0.48, 0.62),
        (0.68, 0.62),
        (0.68, 0.44),
        (0.88, 0.44),
        (0.88, 0.25),
        (0.95, 0.25),
        (0.95, 0.15),
        (1.0, 0.15)
    ]
    interp_d = []
    for idx, (rv, pv) in enumerate(interp_steps):
        cx, cy = to_canvas(rv, pv)
        if idx == 0:
            interp_d.append(f"M {cx:.1f} {cy:.1f}")
        else:
            interp_d.append(f"L {cx:.1f} {cy:.1f}")
    frags.append(f'<path d="{" ".join(interp_d)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    frags.append(line(p1_x + 65, top_y + 52, p1_x + 95, top_y + 52, color=NEG, sw=2, dash="4,3"))
    frags.append(text(p1_x + 102, top_y + 56, "Сира крива (зубці від FP)", size=11, color=INK, anchor="start"))

    frags.append(line(p1_x + 235, top_y + 52, p1_x + 265, top_y + 52, color=POS, sw=2.5))
    frags.append(text(p1_x + 272, top_y + 56, "Огинаюча p_interp(r)", size=11, color=INK, anchor="start", bold=True))

    # Panel 2: Right
    p2_x = 495
    frags.append(rect(p2_x, top_y, card_w, card_h, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    frags.append(rect(p2_x, top_y, card_w, 36, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    frags.append(text(p2_x + card_w / 2, top_y + 23, "Розрахунок Average Precision (AUC)", size=13, bold=True, color=INK))

    ax2_x = p2_x + 55
    ax2_y = top_y + 300

    def to_canvas2(r_val, p_val):
        cx = ax2_x + r_val * ax_w
        cy = ax2_y - p_val * ax_h
        return cx, cy

    poly_d = [f"M {ax2_x:.1f} {ax2_y:.1f}"]
    for rv, pv in interp_steps:
        cx, cy = to_canvas2(rv, pv)
        poly_d.append(f"L {cx:.1f} {cy:.1f}")
    poly_d.append(f"L {ax2_x + ax_w:.1f} {ax2_y:.1f} Z")
    frags.append(f'<path d="{" ".join(poly_d)}" fill="#e8f5e9" stroke="none"/>')

    interp_d2 = []
    for idx, (rv, pv) in enumerate(interp_steps):
        cx, cy = to_canvas2(rv, pv)
        if idx == 0:
            interp_d2.append(f"M {cx:.1f} {cy:.1f}")
        else:
            interp_d2.append(f"L {cx:.1f} {cy:.1f}")
    frags.append(f'<path d="{" ".join(interp_d2)}" fill="none" stroke="{FIELD}" stroke-width="2"/>')

    frags.append(arrow(ax2_x, ax2_y, ax2_x + ax_w + 15, ax2_y, color=LINE, sw=1.5))
    frags.append(arrow(ax2_x, ax2_y, ax2_x, ax2_y - ax_h - 15, color=LINE, sw=1.5))
    frags.append(text(ax2_x + ax_w + 10, ax2_y + 20, "Recall (r)", size=11, bold=True, color=INK, anchor="end"))
    frags.append(text(ax2_x - 10, ax2_y - ax_h - 5, "Precision (p)", size=11, bold=True, color=INK, anchor="end"))

    for i in range(1, 6):
        gx = ax2_x + i * (ax_w / 5)
        val = f"{i * 0.2:.1f}"
        frags.append(line(gx, ax2_y, gx, ax_y + 4, color=MUTED, sw=1.0))
        frags.append(text(gx, ax2_y + 16, val, size=10, color=MUTED))
        frags.append(line(gx, ax2_y, gx, ax2_y - ax_h, color="#e5e7eb", sw=1.0, dash="3,3"))

    for i in range(1, 6):
        gy = ax2_y - i * (ax_h / 5)
        val = f"{i * 0.2:.1f}"
        frags.append(line(ax2_x - 4, gy, ax2_x, gy, color=MUTED, sw=1.0))
        frags.append(text(ax2_x - 8, gy + 4, val, size=10, color=MUTED, anchor="end"))
        frags.append(line(ax2_x, gy, ax2_x + ax_w, gy, color="#e5e7eb", sw=1.0, dash="3,3"))

    frags.append(text(ax2_x - 8, ax2_y + 14, "0.0", size=10, color=MUTED, anchor="end"))

    p_11 = [1.0, 1.0, 0.85, 0.76, 0.76, 0.62, 0.62, 0.44, 0.44, 0.25, 0.15]
    for idx, (r_idx, p_val) in enumerate(zip([i * 0.1 for i in range(11)], p_11)):
        cx, cy = to_canvas2(r_idx, p_val)
        frags.append(circle(cx, cy, 4.0, fill=POS, stroke=BG, sw=1.5))

    frags.append(rect(p2_x + 60, top_y + 48, 14, 10, fill="#e8f5e9", stroke=FIELD, sw=1.2, rx=2))
    frags.append(text(p2_x + 80, top_y + 57, "COCO All-Point AUC (інтеграл)", size=11, color=INK, anchor="start"))

    frags.append(circle(p2_x + 270, top_y + 53, 4.0, fill=POS, stroke=BG, sw=1.2))
    frags.append(text(p2_x + 280, top_y + 57, "VOC 2007 (11 точок)", size=11, color=INK, anchor="start"))

    frags.append(text(p1_x + card_w / 2, top_y + card_h - 15, "Огинаюча знімає випадкові коливання ранжування", size=11, color=MUTED))
    frags.append(text(p2_x + card_w / 2, top_y + card_h - 15, "AP дорівнює площі під східчастою інтерпольованою кривою", size=11, color=MUTED))

    render(os.path.join(OUT_DIR, "pr-curve-interpolation.svg"), w, h, *frags)


def fig_iou_matching_matrix():
    """Ілюстрація зіставлення детекцій із еталоном (IoU Matching) та присвоєння TP/FP/FN."""
    w, h = 960, 430
    frags = []

    top_y = 35
    card_h = 370

    # Column 1
    c1_x = 25
    c1_w = 280
    frags.append(rect(c1_x, top_y, c1_w, card_h, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    frags.append(rect(c1_x, top_y, c1_w, 36, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    frags.append(text(c1_x + c1_w / 2, top_y + 23, "1. Просторове розташування", size=13, bold=True, color=INK))

    fx0, fy0, fw, fh = c1_x + 20, top_y + 55, 240, 240
    frags.append(rect(fx0, fy0, fw, fh, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=4))

    # Ground Truth boxes
    gt1_x, gt1_y, gt1_w, gt1_h = fx0 + 30, fy0 + 35, 75, 75
    frags.append(rect(gt1_x, gt1_y, gt1_w, gt1_h, fill="none", stroke=FIELD, sw=2.5, rx=3))
    frags.append(text(gt1_x + 5, gt1_y - 6, "GT1 (Авто)", size=11, bold=True, color=FIELD, anchor="start"))

    gt2_x, gt2_y, gt2_w, gt2_h = fx0 + 135, fy0 + 120, 80, 80
    frags.append(rect(gt2_x, gt2_y, gt2_w, gt2_h, fill="none", stroke=FIELD, sw=2.5, rx=3))
    frags.append(text(gt2_x + 5, gt2_y - 6, "GT2 (Авто)", size=11, bold=True, color=FIELD, anchor="start"))

    gt3_x, gt3_y, gt3_w, gt3_h = fx0 + 35, fy0 + 165, 55, 55
    frags.append(rect(gt3_x, gt3_y, gt3_w, gt3_h, fill="none", stroke=FIELD, sw=2.5, rx=3))
    frags.append(text(gt3_x + 5, gt3_y - 6, "GT3 (Людина)", size=11, bold=True, color=FIELD, anchor="start"))

    # Predictions
    p1_x, p1_y, p1_w, p1_h = fx0 + 38, fy0 + 40, 72, 74
    frags.append(dashed_rect(p1_x, p1_y, p1_w, p1_h, fill="none", stroke=POS, sw=1.8, rx=3, dash="4,3"))
    frags.append(text(p1_x + p1_w - 5, p1_y + 16, "P1 (0.95)", size=10, bold=True, color=POS, anchor="end"))

    p2_x, p2_y, p2_w, p2_h = fx0 + 140, fy0 + 125, 78, 82
    frags.append(dashed_rect(p2_x, p2_y, p2_w, p2_h, fill="none", stroke=POS, sw=1.8, rx=3, dash="4,3"))
    frags.append(text(p2_x + p2_w - 5, p2_y + 16, "P2 (0.88)", size=10, bold=True, color=POS, anchor="end"))

    p3_x, p3_y, p3_w, p3_h = fx0 + 20, fy0 + 25, 80, 80
    frags.append(dashed_rect(p3_x, p3_y, p3_w, p3_h, fill="none", stroke=NEG, sw=1.8, rx=3, dash="4,3"))
    frags.append(text(p3_x + 5, p3_y + p3_h - 6, "P3 (0.82)", size=10, bold=True, color=NEG, anchor="start"))

    p4_x, p4_y, p4_w, p4_h = fx0 + 175, fy0 + 155, 60, 65
    frags.append(dashed_rect(p4_x, p4_y, p4_w, p4_h, fill="none", stroke=NEG, sw=1.8, rx=3, dash="4,3"))
    frags.append(text(p4_x + 5, p4_y + p4_h - 6, "P4 (0.60)", size=10, bold=True, color=NEG, anchor="start"))

    frags.append(text(c1_x + c1_w / 2, top_y + 325, "Зелений — еталонні рамки GT", size=11, color=FIELD, bold=True))
    frags.append(text(c1_x + c1_w / 2, top_y + 345, "Пунктир — прогнози нейромережі", size=11, color=MUTED))

    # Column 2: IoU Matrix
    c2_x = 320
    c2_w = 295
    frags.append(rect(c2_x, top_y, c2_w, card_h, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    frags.append(rect(c2_x, top_y, c2_w, 36, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    frags.append(text(c2_x + c2_w / 2, top_y + 23, "2. Матриця перекриття IoU", size=13, bold=True, color=INK))

    tx0 = c2_x + 20
    ty0 = top_y + 60
    cell_w = 55
    cell_h = 32

    frags.append(text(tx0 + 40, ty0 + 18, "Прогноз", size=11, bold=True, color=MUTED))
    frags.append(text(tx0 + 95 + 0 * cell_w, ty0 + 18, "GT1", size=11, bold=True, color=FIELD))
    frags.append(text(tx0 + 95 + 1 * cell_w, ty0 + 18, "GT2", size=11, bold=True, color=FIELD))
    frags.append(text(tx0 + 95 + 2 * cell_w, ty0 + 18, "GT3", size=11, bold=True, color=FIELD))

    matrix_data = [
        ("P1 (0.95)", [("0.78", True), ("0.00", False), ("0.00", False)]),
        ("P2 (0.88)", [("0.00", False), ("0.72", True), ("0.00", False)]),
        ("P3 (0.82)", [("0.65", True), ("0.00", False), ("0.00", False)]),
        ("P4 (0.60)", [("0.00", False), ("0.32", False), ("0.00", False)]),
    ]

    for row_idx, (p_lbl, vals) in enumerate(matrix_data):
        cy = ty0 + 35 + row_idx * cell_h
        frags.append(rect(tx0, cy - 20, c2_w - 40, cell_h, fill="#fafafa" if row_idx % 2 == 0 else "#ffffff", stroke="#e5e7eb", sw=1.0, rx=2))
        frags.append(text(tx0 + 38, cy, p_lbl, size=11, bold=True, color=INK))
        for col_idx, (val_str, is_pass) in enumerate(vals):
            cx = tx0 + 95 + col_idx * cell_w
            if is_pass:
                frags.append(rect(cx - 22, cy - 14, 44, 24, fill="#e8f5e9", stroke=FIELD, sw=1.2, rx=3))
                frags.append(text(cx, cy + 2, val_str, size=11, bold=True, color=FIELD))
            else:
                frags.append(text(cx, cy + 2, val_str, size=11, color=MUTED if val_str == "0.00" else POS))

    frags.append(rect(tx0, ty0 + 195, c2_w - 40, 65, fill=FILL, stroke=LINE, sw=1.0, rx=4))
    frags.append(text(c2_x + c2_w / 2, ty0 + 215, "Поріг збігу t_iou = 0.50", size=11, bold=True, color=INK))
    frags.append(text(c2_x + c2_w / 2, ty0 + 232, "P1 перекриває GT1 (0.78 >= 0.50)", size=10, color=MUTED))
    frags.append(text(c2_x + c2_w / 2, ty0 + 247, "P3 перекриває GT1 (0.65 >= 0.50)", size=10, color=MUTED))

    # Column 3: Greedy Matcher Results
    c3_x = 630
    c3_w = 305
    frags.append(rect(c3_x, top_y, c3_w, card_h, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    frags.append(rect(c3_x, top_y, c3_w, 36, fill=FILL, stroke=LINE, sw=1.2, rx=8))
    frags.append(text(c3_x + c3_w / 2, top_y + 23, "3. Жадібне зіставлення (Match)", size=13, bold=True, color=INK))

    rx0 = c3_x + 15
    ry0 = top_y + 55

    steps = [
        ("1. P1 (0.95)", "Зіставляється з GT1", "TP", "#27ae60", "#e8f5e9"),
        ("2. P2 (0.88)", "Зіставляється з GT2", "TP", "#27ae60", "#e8f5e9"),
        ("3. P3 (0.82)", "GT1 вже зайнято P1", "FP", "#c0392b", "#fde8e8"),
        ("4. P4 (0.60)", "IoU(GT2)=0.32 < 0.5", "FP", "#c0392b", "#fde8e8"),
        ("5. GT3", "Не виявлено детектором", "FN", "#2457d6", "#eff6ff"),
    ]

    for s_idx, (p_name, desc, tag, tag_col, tag_bg) in enumerate(steps):
        sy = ry0 + s_idx * 48
        frags.append(rect(rx0, sy, c3_w - 30, 42, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=4))
        frags.append(text(rx0 + 10, sy + 18, p_name, size=11, bold=True, color=INK, anchor="start"))
        frags.append(text(rx0 + 10, sy + 33, desc, size=10, color=MUTED, anchor="start"))

        frags.append(rect(rx0 + c3_w - 75, sy + 8, 35, 24, fill=tag_bg, stroke=tag_col, sw=1.2, rx=4))
        frags.append(text(rx0 + c3_w - 58, sy + 24, tag, size=11, bold=True, color=tag_col))

    frags.append(rect(rx0, ry0 + 250, c3_w - 30, 50, fill=FILL, stroke=LINE, sw=1.0, rx=4))
    frags.append(text(c3_x + c3_w / 2, ry0 + 270, "Підсумок: TP = 2,  FP = 2,  FN = 1", size=11, bold=True, color=INK))
    frags.append(text(c3_x + c3_w / 2, ry0 + 288, "Precision = 2/4 = 0.50 | Recall = 2/3 = 0.67", size=10, color=MUTED))

    render(os.path.join(OUT_DIR, "iou-matching-matrix.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_pr_curve_interpolation()
    fig_iou_matching_matrix()
    print("Згенеровано фігури в img/")

# -*- coding: utf-8 -*-
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

img_dir = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(img_dir, exist_ok=True)

# 1. Comparison: 2-probe vs 4-probe measurement
def gen_two_vs_four_probe():
    w, h = 760, 400
    frags = []

    frags.append(text(w / 2, 28, "Порівняння двозондового та чотирьохзондового методів вимірювання опору", size=16, bold=True))

    # --- LEFT PANEL: 2-probe method ---
    frags.append(rect(20, 55, 350, 325, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(195, 80, "Двозондовий метод (2-wire)", size=14, color=NEG, bold=True))

    frags.append(rect(140, 180, 110, 60, fill="#eaecee", stroke=LINE, sw=2, rx=4))
    frags.append(text(195, 215, "Зразок R_x", size=13, color=INK, bold=True))

    frags.append(line(50, 210, 80, 210, color=LINE, sw=2))
    frags.append(rect(80, 198, 25, 24, fill="#fadbd8", stroke=NEG, sw=1.5, rx=2))
    frags.append(text(92, 214, "R_c1", size=10, color=NEG, bold=True))
    frags.append(line(105, 210, 140, 210, color=LINE, sw=2))

    frags.append(line(250, 210, 285, 210, color=LINE, sw=2))
    frags.append(rect(285, 198, 25, 24, fill="#fadbd8", stroke=NEG, sw=1.5, rx=2))
    frags.append(text(297, 214, "R_c2", size=10, color=NEG, bold=True))
    frags.append(line(310, 210, 340, 210, color=LINE, sw=2))

    frags.append(line(50, 130, 50, 210, color=LINE, sw=2))
    frags.append(line(340, 130, 340, 210, color=LINE, sw=2))
    frags.append(line(50, 130, 150, 130, color=LINE, sw=2))
    frags.append(line(240, 130, 340, 130, color=LINE, sw=2))

    frags.append(rect(150, 110, 90, 40, fill="#ebf5fb", stroke=POS, sw=2, rx=4))
    frags.append(text(195, 134, "Омметр", size=12, color=POS, bold=True))

    frags.append(rect(40, 280, 310, 80, fill="#fdf2e9", stroke="#e67e22", sw=1.5, rx=4))
    frags.append(text(195, 302, "Паразитне падіння напруги:", size=11, color="#d35400", bold=True))
    frags.append(text(195, 324, "V_meas = I · (R_x + 2R_lead + 2R_contact)", size=11, color=INK, bold=True))
    frags.append(text(195, 346, "Помилка сягає 100%+ для низьких R_x", size=10, color=NEG, italic=True))


    # --- RIGHT PANEL: 4-probe Kelvin method ---
    frags.append(rect(390, 55, 350, 325, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(565, 80, "Чотирьохзондовий метод (4-wire / Кельвін)", size=14, color=POS, bold=True))

    frags.append(rect(510, 180, 110, 60, fill="#eaecee", stroke=LINE, sw=2, rx=4))
    frags.append(text(565, 215, "Зразок R_x", size=13, color=INK, bold=True))

    frags.append(line(410, 210, 510, 210, color=LINE, sw=2))
    frags.append(line(620, 210, 720, 210, color=LINE, sw=2))
    frags.append(circle(510, 210, 4, fill=NEG))
    frags.append(circle(620, 210, 4, fill=NEG))

    frags.append(line(410, 110, 410, 210, color=LINE, sw=2))
    frags.append(line(720, 110, 720, 210, color=LINE, sw=2))
    frags.append(line(410, 110, 520, 110, color=LINE, sw=2))
    frags.append(line(610, 110, 720, 110, color=LINE, sw=2))

    frags.append(rect(520, 95, 90, 30, fill="#fdecea", stroke=NEG, sw=1.8, rx=4))
    frags.append(text(565, 114, "Струм I", size=11, color=NEG, bold=True))

    frags.append(circle(540, 210, 4, fill=POS))
    frags.append(circle(590, 210, 4, fill=POS))

    frags.append(line(540, 210, 540, 160, color=POS, sw=1.5, dash="3,3"))
    frags.append(line(590, 210, 590, 160, color=POS, sw=1.5, dash="3,3"))
    frags.append(line(540, 160, 520, 160, color=POS, sw=1.5))
    frags.append(line(590, 160, 610, 160, color=POS, sw=1.5))

    frags.append(rect(520, 145, 90, 30, fill="#e8f8f5", stroke=POS, sw=1.8, rx=4))
    frags.append(text(565, 164, "Вольтметр V (R_v→∞)", size=10, color=POS, bold=True))

    frags.append(rect(410, 280, 310, 80, fill="#eafaf1", stroke=POS, sw=1.5, rx=4))
    frags.append(text(565, 302, "Струм вольтметра I_v ≈ 0  =>  I_contact · R_c ≈ 0", size=11, color=POS, bold=True))
    frags.append(text(565, 324, "Точне вимірювання: R_x = V / I", size=12, color=INK, bold=True))
    frags.append(text(565, 346, "Опори дротів та переходів не впливають!", size=10, color=POS, italic=True))

    render(os.path.join(img_dir, "two-vs-four-probe.svg"), w, h, *frags)


# 2. Collinear 4-point probe configuration on wafer
def gen_collinear_four_probe():
    w, h = 760, 420
    frags = []

    frags.append(text(w / 2, 28, "Колінеарне зондування: струмові лінії та потенціал на пластині", size=16, bold=True))

    bx, by, bw, bh = 80, 160, 600, 130
    frags.append(rect(bx, by, bw, bh, fill="#f2f4f4", stroke=LINE, sw=2, rx=4))
    frags.append(text(bx + bw - 70, by + bh / 2, "Зразок (товщина w)", size=11, color=MUTED, bold=True))

    frags.append(arrow(bx - 30, by, bx - 30, by + bh, color=LINE, sw=1.5))
    frags.append(arrow(bx - 30, by + bh, bx - 30, by, color=LINE, sw=1.5))
    frags.append(text(bx - 45, by + bh / 2 + 4, "w", size=13, bold=True))

    probe_x = [bx + 110, bx + 230, bx + 350, bx + 470]
    probe_labels = ["1 (+I)", "2 (+V)", "3 (-V)", "4 (-I)"]
    probe_colors = [NEG, POS, POS, NEG]

    for i in range(3):
        x1, x2 = probe_x[i], probe_x[i+1]
        frags.append(line(x1, by - 60, x2, by - 60, color=MUTED, sw=1.2))
        frags.append(line(x1, by - 65, x1, by - 55, color=MUTED, sw=1.2))
        frags.append(line(x2, by - 65, x2, by - 55, color=MUTED, sw=1.2))
        frags.append(text((x1 + x2) / 2, by - 70, "s", size=12, color=MUTED, bold=True))

    for i in range(4):
        px = probe_x[i]
        col = probe_colors[i]
        frags.append(line(px, by - 40, px, by, color=col, sw=3))
        frags.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s" />' % (px - 5, by - 12, px + 5, by - 12, px, by + 4, col))
        frags.append(text(px, by - 48, probe_labels[i], size=11, color=col, bold=True))

    for r in range(40, 200, 35):
        frags.append('<path d="M %d,%d A %d,%d 0 0,0 %d,%d" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,4" opacity="0.6"/>' %
                     (probe_x[0], by, r*1.3, r*0.7, probe_x[3], by, NEG))

    frags.append(line(probe_x[0], by - 40, probe_x[0], by - 100, color=NEG, sw=1.8))
    frags.append(line(probe_x[3], by - 40, probe_x[3], by - 100, color=NEG, sw=1.8))
    frags.append(line(probe_x[0], by - 100, bx + 270, by - 100, color=NEG, sw=1.8))
    frags.append(line(probe_x[3], by - 100, bx + 310, by - 100, color=NEG, sw=1.8))
    frags.append(rect(bx + 270, by - 115, 40, 30, fill="#fdecea", stroke=NEG, sw=1.5, rx=3))
    frags.append(text(bx + 290, by - 96, "I", size=13, color=NEG, bold=True))

    frags.append(line(probe_x[1], by - 40, probe_x[1], by - 130, color=POS, sw=1.5))
    frags.append(line(probe_x[2], by - 40, probe_x[2], by - 130, color=POS, sw=1.5))
    frags.append(line(probe_x[1], by - 130, bx + 270, by - 130, color=POS, sw=1.5))
    frags.append(line(probe_x[2], by - 130, bx + 310, by - 130, color=POS, sw=1.5))
    frags.append(rect(bx + 270, by - 145, 40, 30, fill="#e8f8f5", stroke=POS, sw=1.5, rx=3))
    frags.append(text(bx + 290, by - 126, "V", size=13, color=POS, bold=True))

    frags.append(fitbox(80, 315, 600, 80,
                        "3D напівнескінченний об'єм (w >> s):  ρ = 2π·s·(V / I)\n2D тонкий шар (w << s):  R_s = (π / ln 2)·(V / I) ≈ 4.532·(V / I)   [Ом/квадрат]",
                        size=12, fill="#fcf3cf", stroke="#f39c12", bold=True))

    render(os.path.join(img_dir, "collinear-four-probe.svg"), w, h, *frags)


# 3. Van der Pauw Method Geometry
def gen_van_der_pauw_geometry():
    w, h = 760, 430
    frags = []

    frags.append(text(w / 2, 28, "Метод Ван дер Пау: контактні конфігурації на довільному 2D зразку", size=16, bold=True))

    # --- LEFT SUBPANEL: Configuration A (R_A = V_DC / I_AB) ---
    frags.append(rect(30, 55, 335, 300, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(197, 82, "Конфігурація A: R_A = V_DC / I_AB", size=13, color=POS, bold=True))

    shape_a = "M 100,160 Q 150,120 220,130 T 290,180 Q 300,240 240,280 T 130,270 Q 80,220 100,160 Z"
    frags.append('<path d="%s" fill="#eaf2f8" stroke="%s" stroke-width="2"/>' % (shape_a, LINE))
    frags.append(text(195, 205, "Плоский зразок\nдовільної форми", size=11, color=MUTED, bold=True))

    cA = (105, 160)
    cB = (210, 132)
    cC = (280, 200)
    cD = (150, 275)

    contacts = [("A", cA, NEG), ("B", cB, NEG), ("C", cC, POS), ("D", cD, POS)]
    for label, pt, col in contacts:
        frags.append(circle(pt[0], pt[1], 7, fill=col, stroke="#ffffff", sw=1.5))
        frags.append(text(pt[0] - 14 if pt[0] < 195 else pt[0] + 14, pt[1] + 4, label, size=12, color=col, bold=True))

    frags.append(arrow(65, 160, cA[0], cA[1], color=NEG, sw=2))
    frags.append(arrow(cB[0], cB[1], 210, 85, color=NEG, sw=2))
    frags.append(text(45, 164, "I+", size=11, color=NEG, bold=True))
    frags.append(text(210, 75, "I-", size=11, color=NEG, bold=True))

    frags.append(line(cD[0], cD[1], cD[0], 310, color=POS, sw=1.5, dash="3,3"))
    frags.append(line(cC[0], cC[1], cC[0], 310, color=POS, sw=1.5, dash="3,3"))
    frags.append(rect(170, 298, 60, 26, fill="#e8f8f5", stroke=POS, sw=1.5, rx=3))
    frags.append(text(200, 315, "V_DC", size=11, color=POS, bold=True))


    # --- RIGHT SUBPANEL: Configuration B (R_B = V_AD / I_BC) ---
    frags.append(rect(395, 55, 335, 300, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(562, 82, "Конфігурація B: R_B = V_AD / I_BC", size=13, color=FIELD, bold=True))

    shape_b = "M 465,160 Q 515,120 585,130 T 655,180 Q 665,240 605,280 T 495,270 Q 445,220 465,160 Z"
    frags.append('<path d="%s" fill="#eaf2f8" stroke="%s" stroke-width="2"/>' % (shape_b, LINE))
    frags.append(text(560, 205, "Поворот вимірювань\nна 90°", size=11, color=MUTED, bold=True))

    cA2 = (470, 160)
    cB2 = (575, 132)
    cC2 = (645, 200)
    cD2 = (515, 275)

    contacts2 = [("A", cA2, POS), ("B", cB2, NEG), ("C", cC2, NEG), ("D", cD2, POS)]
    for label, pt, col in contacts2:
        frags.append(circle(pt[0], pt[1], 7, fill=col, stroke="#ffffff", sw=1.5))
        frags.append(text(pt[0] - 14 if pt[0] < 560 else pt[0] + 14, pt[1] + 4, label, size=12, color=col, bold=True))

    frags.append(arrow(cB2[0], cB2[1], 575, 85, color=NEG, sw=2))
    frags.append(arrow(cC2[0], cC2[1], 690, 200, color=NEG, sw=2))
    frags.append(text(575, 75, "I+", size=11, color=NEG, bold=True))
    frags.append(text(705, 204, "I-", size=11, color=NEG, bold=True))

    frags.append(line(cA2[0], cA2[0], cA2[0], 310, color=POS, sw=1.5, dash="3,3"))
    frags.append(line(cD2[0], cD2[1], cD2[0], 310, color=POS, sw=1.5, dash="3,3"))
    frags.append(rect(460, 298, 60, 26, fill="#e8f8f5", stroke=POS, sw=1.5, rx=3))
    frags.append(text(490, 315, "V_AD", size=11, color=POS, bold=True))

    frags.append(rect(100, 370, 560, 45, fill="#fcf3cf", stroke="#f39c12", sw=1.5, rx=4))
    frags.append(text(380, 397, "Рівняння Ван дер Пау:  exp(-π·R_A / R_s) + exp(-π·R_B / R_s) = 1", size=12, color=INK, bold=True))

    render(os.path.join(img_dir, "van-der-pauw-geometry.svg"), w, h, *frags)


# 4. Geometric Correction Factors F(s/w) plot
def gen_geometric_correction_factors():
    w, h = 760, 420
    frags = []

    frags.append(text(w / 2, 28, "Геометричний поправочний коефіцієнт F(w/s) для пластин скінченної товщини", size=16, bold=True))

    ox, oy = 90, 340
    ax_w, ax_h = 600, 260

    # Axes
    frags.append(line(ox, oy, ox + ax_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - ax_h, color=LINE, sw=2))

    # Axis Labels
    frags.append(text(ox + ax_w / 2, oy + 42, "Відношення товщини до відстані між зондами (w / s)", size=13, bold=True))
    frags.append(text(ox - 55, oy - ax_h / 2, "Поправочний коефіцієнт F", size=13, bold=True, anchor="middle"))

    # Grid & Ticks
    for val in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        tx = ox + (val / 3.0) * ax_w
        frags.append(line(tx, oy, tx, oy + 5, color=MUTED))
        frags.append(text(tx, oy + 20, "%.1f" % val, size=11, color=MUTED))
        frags.append(line(tx, oy - 2, tx, oy - ax_h + 2, color="#eaeded", sw=1, dash="2,2"))

    for f_val in [0.2, 0.4, 0.6, 0.8, 1.0]:
        ty = oy - (f_val / 1.0) * ax_h
        frags.append(line(ox - 5, ty, ox, ty, color=MUTED))
        frags.append(text(ox - 12, ty + 4, "%.1f" % f_val, size=11, color=MUTED, anchor="end"))
        frags.append(line(ox + 2, ty, ox + ax_w - 2, ty, color="#eaeded", sw=1, dash="2,2"))

    # Asymptote F = 1 (Bulk 3D limit)
    frags.append(line(ox, oy - ax_h, ox + ax_w, oy - ax_h, color=POS, sw=1.5, dash="4,4"))
    frags.append(text(ox + ax_w - 120, oy - ax_h + 18, "Границя 3D (w >> s): F → 1", size=11, color=POS, bold=True))

    # 2D Thin Film limit curve F(w/s)
    pts = []
    for i in range(101):
        ws = 0.05 + (i / 100.0) * 2.95
        if ws < 0.5:
            f_norm = ws * (math.log(2) / math.pi) * 4.53236
            f_norm = min(f_norm, 1.0)
        else:
            f_norm = 1.0 - math.exp(-1.8 * ws)

        cx = ox + (ws / 3.0) * ax_w
        cy = oy - (f_norm / 1.0) * ax_h
        pts.append((cx, cy))

    path_d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_d, NEG))

    # Annotations - placed at (350, 260) in the open area below asymptote & curve
    frags.append(textbox(350, 260, "Область тонкої плівки (w << s):\nρ = (π / ln 2) · w · (V / I)\nЛінійна залежність від товщини", size=10, fill="#fdecea", stroke=NEG)[0])
    frags.append(textbox(540, 140, "Область масиву (w >> s):\nρ = 2π · s · (V / I)\nНе залежить від товщини w", size=10, fill="#eafaf1", stroke=POS)[0])

    render(os.path.join(img_dir, "geometric-correction-factors.svg"), w, h, *frags)


if __name__ == '__main__':
    gen_two_vs_four_probe()
    gen_collinear_four_probe()
    gen_van_der_pauw_geometry()
    gen_geometric_correction_factors()
    print("All 4 figures generated successfully.")

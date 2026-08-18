# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/ from book/physics/condensed-matter-physics/sheet-resistance/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

img_dir = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(img_dir, exist_ok=True)

# 1. Sheet Resistance Square Independence
def gen_sheet_resistance_square():
    w, h = 680, 390
    frags = []

    frags.append(text(w / 2, 26, "Незалежність опору квадрата тонкої плівки від його геометричних розмірів", size=15, bold=True))

    # Left Panel: 1x1 Square
    frags.append(rect(40, 55, 270, 265, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(175, 78, "Одиничний квадрат 1×1 (L × L)", size=13, color=POS, bold=True))

    # 1x1 Square graphic
    sq1_x, sq1_y, sq1_s = 100, 100, 150
    frags.append(rect(sq1_x, sq1_y, sq1_s, sq1_s, fill="#eaf2f8", stroke=POS, sw=2))

    # Electrodes left and right
    frags.append(rect(sq1_x - 12, sq1_y, 12, sq1_s, fill="#bdc3c7", stroke=LINE, sw=1.5))
    frags.append(rect(sq1_x + sq1_s, sq1_y, 12, sq1_s, fill="#bdc3c7", stroke=LINE, sw=1.5))

    # Dimension arrows
    frags.append(arrow(sq1_x, sq1_y - 12, sq1_x + sq1_s, sq1_y - 12, color=POS, sw=1.5))
    frags.append(arrow(sq1_x + sq1_s, sq1_y - 12, sq1_x, sq1_y - 12, color=POS, sw=1.5))
    frags.append(text(sq1_x + sq1_s / 2, sq1_y - 20, "Довжина L", size=11, color=POS, bold=True))

    frags.append(arrow(sq1_x - 22, sq1_y, sq1_x - 22, sq1_y + sq1_s, color=POS, sw=1.5))
    frags.append(arrow(sq1_x - 22, sq1_y + sq1_s, sq1_x - 22, sq1_y, color=POS, sw=1.5))
    frags.append(text(sq1_x - 28, sq1_y + sq1_s / 2, "W = L", size=11, color=POS, bold=True, anchor="end"))

    # Current flow arrow inside
    frags.append(arrow(sq1_x + 20, sq1_y + sq1_s / 2, sq1_x + sq1_s - 20, sq1_y + sq1_s / 2, color=NEG, sw=2))
    frags.append(text(sq1_x + sq1_s / 2, sq1_y + sq1_s / 2 - 10, "Струм I", size=11, color=NEG, bold=True))

    # Formula bottom left
    frags.append(text(175, 275, "R = ρ · L / (L · d) = ρ / d = R_s", size=12, color=INK, bold=True))
    frags.append(text(175, 298, "Опір = R_s Ом/квадрат", size=11, color=MUTED))

    # Right Panel: 2x2 Square
    frags.append(rect(345, 55, 295, 265, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(492, 78, "Збільшений квадрат 2×2 (2L × 2L)", size=13, color=FIELD, bold=True))

    # 2x2 Square graphic (divided into 4 sub-squares)
    sq2_x, sq2_y, sq2_s = 415, 100, 150
    half_s = sq2_s / 2
    # 4 sub-squares
    frags.append(rect(sq2_x, sq2_y, half_s, half_s, fill="#ebf5fb", stroke=FIELD, sw=1.5))
    frags.append(rect(sq2_x + half_s, sq2_y, half_s, half_s, fill="#ebf5fb", stroke=FIELD, sw=1.5))
    frags.append(rect(sq2_x, sq2_y + half_s, half_s, half_s, fill="#ebf5fb", stroke=FIELD, sw=1.5))
    frags.append(rect(sq2_x + half_s, sq2_y + half_s, half_s, half_s, fill="#ebf5fb", stroke=FIELD, sw=1.5))

    # Electrodes left and right
    frags.append(rect(sq2_x - 12, sq2_y, 12, sq2_s, fill="#bdc3c7", stroke=LINE, sw=1.5))
    frags.append(rect(sq2_x + sq2_s, sq2_y, 12, sq2_s, fill="#bdc3c7", stroke=LINE, sw=1.5))

    # Dimension labels
    frags.append(arrow(sq2_x, sq2_y - 12, sq2_x + sq2_s, sq2_y - 12, color=FIELD, sw=1.5))
    frags.append(arrow(sq2_x + sq2_s, sq2_y - 12, sq2_x, sq2_y - 12, color=FIELD, sw=1.5))
    frags.append(text(sq2_x + sq2_s / 2, sq2_y - 20, "2L", size=11, color=FIELD, bold=True))

    frags.append(arrow(sq2_x - 22, sq2_y, sq2_x - 22, sq2_y + sq2_s, color=FIELD, sw=1.5))
    frags.append(arrow(sq2_x - 22, sq2_y + sq2_s, sq2_x - 22, sq2_y, color=FIELD, sw=1.5))
    frags.append(text(sq2_x - 28, sq2_y + sq2_s / 2, "2L", size=11, color=FIELD, bold=True, anchor="end"))

    # Equivalent circuit inside right box
    frags.append(text(sq2_x + half_s / 2, sq2_y + half_s / 2 + 4, "R_s", size=11, color=FIELD))
    frags.append(text(sq2_x + 3 * half_s / 2, sq2_y + half_s / 2 + 4, "R_s", size=11, color=FIELD))
    frags.append(text(sq2_x + half_s / 2, sq2_y + 3 * half_s / 2 + 4, "R_s", size=11, color=FIELD))
    frags.append(text(sq2_x + 3 * half_s / 2, sq2_y + 3 * half_s / 2 + 4, "R_s", size=11, color=FIELD))

    # Formula bottom right
    frags.append(text(492, 275, "R = (2R_s · 2R_s) / (2R_s + 2R_s) = R_s", size=12, color=INK, bold=True))
    frags.append(text(492, 298, "Паралельні вітки подвоюють провідність", size=11, color=MUTED))

    # Bottom summary box
    frags.append(fitbox(40, 332, 600, 46, "Фундаментальна властивість: R = ρ · L / (W · d) = R_s · (L / W). Для будь-якого квадрата L = W, тому R ≡ R_s [Ом/□]", size=11, fill="#fcf3cf", stroke="#f39c12", bold=True))

    render(os.path.join(img_dir, "sheet-resistance-square.svg"), w, h, *frags)


# 2. Four Probe Geometry
def gen_four_probe_geometry():
    w, h = 680, 420
    frags = []

    frags.append(text(w / 2, 26, "Колонеарна чотиризондова методика вимірювання поверхневого опору", size=15, bold=True))

    # Substrate & Thin Film layer
    bx, by, bw, bh = 70, 200, 540, 70
    # Substrate
    frags.append(rect(bx, by + 25, bw, bh - 25, fill="#eaeded", stroke=LINE, sw=1.5, rx=3))
    frags.append(text(bx + 60, by + 55, "Підкладка (ізолятор)", size=11, color=MUTED))

    # Thin conductive film
    frags.append(rect(bx, by, bw, 25, fill="#a9cce3", stroke=POS, sw=2, rx=2))
    frags.append(text(bx + 60, by + 16, "Тонка плівка (товщина d ≪ s)", size=11, color=POS, bold=True))

    # 4 Probes (needles)
    probe_xs = [bx + 110, bx + 220, bx + 330, bx + 440]

    # Draw probes
    for idx, px in enumerate(probe_xs, 1):
        # Needle body
        frags.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.5"/>' %
                     (px - 8, by - 80, px + 8, by - 80, px, by, "#7f8c8d", LINE))
        frags.append(line(px, by - 80, px, by - 110, color=LINE, sw=2.5))
        # Label probe 1, 2, 3, 4
        frags.append(circle(px, by - 120, 14, fill="#ffffff", stroke=LINE, sw=1.5))
        frags.append(text(px, by - 116, str(idx), size=12, bold=True))

    # Probe Spacing s arrows
    for i in range(3):
        x1, x2 = probe_xs[i], probe_xs[i + 1]
        frags.append(arrow(x1, by - 45, x2, by - 45, color=FIELD, sw=1.2))
        frags.append(arrow(x2, by - 45, x1, by - 45, color=FIELD, sw=1.2))
        frags.append(text((x1 + x2) / 2, by - 52, "s", size=11, color=FIELD, bold=True))

    # Wiring: Current Source to Probes 1 and 4
    # Probe 1 wire
    frags.append(line(probe_xs[0], by - 134, probe_xs[0], by - 165, color=NEG, sw=2))
    frags.append(line(probe_xs[0], by - 165, 140, by - 165, color=NEG, sw=2))
    # Probe 4 wire
    frags.append(line(probe_xs[3], by - 134, probe_xs[3], by - 165, color=NEG, sw=2))
    frags.append(line(probe_xs[3], by - 165, 540, by - 165, color=NEG, sw=2))

    # Current Source Box top
    frags.append(rect(290, 48, 100, 36, fill="#fadbd8", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(340, 70, "Джерело I", size=12, color=NEG, bold=True))
    frags.append(line(140, by - 165, 140, 66, color=NEG, sw=2))
    frags.append(line(140, 66, 290, 66, color=NEG, sw=2))
    frags.append(line(540, by - 165, 540, 66, color=NEG, sw=2))
    frags.append(line(540, 66, 390, 66, color=NEG, sw=2))

    # Wiring: Voltmeter to Probes 2 and 3
    frags.append(line(probe_xs[1], by - 134, probe_xs[1], by - 145, color=POS, sw=2))
    frags.append(line(probe_xs[1], by - 145, 235, by - 145, color=POS, sw=2))
    frags.append(line(probe_xs[2], by - 134, probe_xs[2], by - 145, color=POS, sw=2))
    frags.append(line(probe_xs[2], by - 145, 445, by - 145, color=POS, sw=2))

    # Voltmeter Box middle
    frags.append(rect(290, 127, 100, 36, fill="#d4efdf", stroke=POS, sw=1.5, rx=4))
    frags.append(text(340, 149, "Вольтметр V", size=12, color=POS, bold=True))
    frags.append(line(235, by - 145, 235, 145, color=POS, sw=2))
    frags.append(line(235, 145, 290, 145, color=POS, sw=2))
    frags.append(line(445, by - 145, 445, 145, color=POS, sw=2))
    frags.append(line(445, 145, 390, 145, color=POS, sw=2))

    # Current spreading lines in film (arcs)
    frags.append('<path d="M %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4,3"/>' %
                 (probe_xs[0], by + 5, (probe_xs[0] + probe_xs[3]) / 2, by + 22, probe_xs[3], by + 5, NEG))
    frags.append('<path d="M %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>' %
                 (probe_xs[0], by + 5, (probe_xs[0] + probe_xs[2]) / 2, by + 18, probe_xs[2], by + 5, NEG))

    # Bottom Formula Banner
    frags.append(fitbox(70, 340, 540, 60, "Для тонкої нескінченної плівки (d ≪ s):  R_s = (π / ln 2) · (V / I) ≈ 4.5324 · (V / I)\nУсунення впливу контактного опору зондів R_c завдяки розділенню струму й напруги", size=11, fill="#fcf3cf", stroke="#f39c12", bold=True))

    render(os.path.join(img_dir, "four-probe-geometry.svg"), w, h, *frags)


# 3. Van der Pauw Geometry
def gen_van_der_pauw_geometry():
    w, h = 680, 390
    frags = []

    frags.append(text(w / 2, 26, "Метод Ван дер Пау для вимірювання зразків довільної геометричної форми", size=15, bold=True))

    # Left Configuration R_A
    frags.append(rect(30, 55, 295, 265, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(177, 78, "Конфігурація 1: Опір R_A = V_DC / I_AB", size=12, color=POS, bold=True))

    # Arbitrary 2D Domain shape (Left)
    vdp1_path = "M 80,140 C 100,100 170,90 230,120 C 270,140 280,210 250,250 C 210,280 130,275 90,240 C 70,210 60,170 80,140 Z"
    frags.append('<path d="%s" fill="#eaf2f8" stroke="%s" stroke-width="2"/>' % (vdp1_path, POS))

    # Contacts A, B, C, D on perimeter
    cA = (85, 130)
    cB = (235, 125)
    cC = (245, 245)
    cD = (95, 235)

    for pt, name in [(cA, "A"), (cB, "B"), (cC, "C"), (cD, "D")]:
        frags.append(circle(pt[0], pt[1], 9, fill="#f39c12", stroke="#ffffff", sw=1.5))
        frags.append(text(pt[0], pt[1] + 3.5, name, size=10, bold=True, color="#ffffff"))

    # Current injected A -> B
    frags.append(arrow(cA[0] - 25, cA[1], cA[0], cA[1], color=NEG, sw=2))
    frags.append(text(cA[0] - 30, cA[1] - 8, "+I", size=10, color=NEG, bold=True))
    frags.append(arrow(cB[0], cB[1], cB[0] + 25, cB[1], color=NEG, sw=2))
    frags.append(text(cB[0] + 15, cB[1] - 8, "-I", size=10, color=NEG, bold=True))

    # Voltage measured D -> C
    frags.append(line(cD[0] - 15, cD[1], cD[0], cD[1], color=POS, sw=1.5))
    frags.append(line(cC[0], cC[1], cC[0] + 15, cC[1], color=POS, sw=1.5))
    frags.append(line(cD[0] - 15, cD[1], cD[0] - 15, cD[1] + 25, color=POS, sw=1.5))
    frags.append(line(cC[0] + 15, cC[1], cC[0] + 15, cC[1] + 25, color=POS, sw=1.5))
    frags.append(rect(130, cD[1] + 10, 80, 30, fill="#d4efdf", stroke=POS, sw=1.5, rx=3))
    frags.append(text(170, cD[1] + 29, "V_DC", size=11, color=POS, bold=True))
    frags.append(line(cD[0] - 15, cD[1] + 25, 130, cD[1] + 25, color=POS, sw=1.5))
    frags.append(line(cC[0] + 15, cC[1] + 25, 210, cC[1] + 25, color=POS, sw=1.5))

    # Right Configuration R_B
    frags.append(rect(350, 55, 295, 265, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(497, 78, "Конфігурація 2: Опір R_B = V_AD / I_BC", size=12, color=FIELD, bold=True))

    # Arbitrary 2D Domain shape (Right)
    vdp2_path = "M 400,140 C 420,100 490,90 550,120 C 590,140 600,210 570,250 C 530,280 450,275 410,240 C 390,210 380,170 400,140 Z"
    frags.append('<path d="%s" fill="#ebf5fb" stroke="%s" stroke-width="2"/>' % (vdp2_path, FIELD))

    cA2 = (405, 130)
    cB2 = (555, 125)
    cC2 = (565, 245)
    cD2 = (415, 235)

    for pt, name in [(cA2, "A"), (cB2, "B"), (cC2, "C"), (cD2, "D")]:
        frags.append(circle(pt[0], pt[1], 9, fill="#f39c12", stroke="#ffffff", sw=1.5))
        frags.append(text(pt[0], pt[1] + 3.5, name, size=10, bold=True, color="#ffffff"))

    # Current injected B -> C
    frags.append(arrow(cB2[0], cB2[1] - 25, cB2[0], cB2[1], color=NEG, sw=2))
    frags.append(text(cB2[0] + 8, cB2[1] - 15, "+I", size=10, color=NEG, bold=True))
    frags.append(arrow(cC2[0], cC2[1], cC2[0], cC2[1] + 25, color=NEG, sw=2))
    frags.append(text(cC2[0] + 8, cC2[1] + 20, "-I", size=10, color=NEG, bold=True))

    # Voltage measured A -> D
    frags.append(line(cA2[0] - 15, cA2[1], cA2[0], cA2[1], color=FIELD, sw=1.5))
    frags.append(line(cD2[0] - 15, cD2[1], cD2[0], cD2[1], color=FIELD, sw=1.5))
    frags.append(rect(360, 165, 30, 50, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(375, 194, "V_AD", size=10, color=FIELD, bold=True))
    frags.append(line(cA2[0] - 15, cA2[1], 375, cA2[1], color=FIELD, sw=1.5))
    frags.append(line(375, cA2[1], 375, 165, color=FIELD, sw=1.5))
    frags.append(line(cD2[0] - 15, cD2[1], 375, cD2[1], color=FIELD, sw=1.5))
    frags.append(line(375, cD2[1], 375, 215, color=FIELD, sw=1.5))

    # Bottom Formula Banner
    frags.append(fitbox(30, 332, 615, 46, "Рівняння Ван дер Пау:  exp(-π · R_A / R_s) + exp(-π · R_B / R_s) = 1\nДля симетричного зразка (R_A = R_B = R): R_s = (π / ln 2) · R ≈ 4.5324 · R", size=11, fill="#fcf3cf", stroke="#f39c12", bold=True))

    render(os.path.join(img_dir, "van-der-pauw-geometry.svg"), w, h, *frags)


# 4. TCO Tradeoff Transmission vs Sheet Resistance
def gen_tco_tradeoff_transmission_resistance():
    w, h = 680, 420
    frags = []

    frags.append(text(w / 2, 26, "Оптико-електричний компроміс у прозорих провідних оксидах (TCO)", size=15, bold=True))

    ox, oy = 80, 330
    ax_w, ax_h = 520, 250

    # Axes
    frags.append(line(ox, oy, ox + ax_w, oy, color=LINE, sw=2))
    frags.append(line(ox, oy, ox, oy - ax_h, color=LINE, sw=2))
    frags.append(line(ox + ax_w, oy, ox + ax_w, oy - ax_h, color=LINE, sw=2))

    # X axis label
    frags.append(text(ox + ax_w / 2, oy + 42, "Товщина плівки d (нм) / Концентрація носіїв n", size=12, bold=True))

    # Left Y axis label (Transmittance)
    frags.append(text(ox - 50, oy - ax_h / 2, "Прозорість T (%)", size=12, color=POS, bold=True, anchor="middle"))

    # Right Y axis label (Sheet Resistance)
    frags.append(text(ox + ax_w + 50, oy - ax_h / 2, "Поверхневий опір R_s (Ом/□)", size=12, color=NEG, bold=True, anchor="middle"))

    # Ticks
    frags.append(text(ox - 15, oy - ax_h + 10, "100%", size=10, color=POS))
    frags.append(text(ox - 15, oy - ax_h / 2, "80%", size=10, color=POS))
    frags.append(text(ox - 15, oy - 10, "0%", size=10, color=POS))

    frags.append(text(ox + ax_w + 15, oy - ax_h + 10, "100", size=10, color=NEG))
    frags.append(text(ox + ax_w + 15, oy - ax_h / 2, "20", size=10, color=NEG))
    frags.append(text(ox + ax_w + 15, oy - 10, "5", size=10, color=NEG))

    # Curve 1: Transmittance T (drops as thickness/doping grows)
    pts_T = [(ox + 20, oy - ax_h + 15), (ox + 120, oy - ax_h + 25), (ox + 240, oy - ax_h + 55), (ox + 360, oy - ax_h + 120), (ox + 480, oy - ax_h + 200)]
    path_T = "M " + " L ".join("%d,%d" % (x, y) for x, y in pts_T)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_T, POS))
    frags.append(text(ox + 40, oy - ax_h + 35, "Оптична прозорість T (%)", size=11, color=POS, bold=True, anchor="start"))

    # Curve 2: Sheet Resistance R_s (drops as thickness/doping grows)
    pts_R = [(ox + 20, oy - ax_h + 20), (ox + 100, oy - ax_h + 80), (ox + 200, oy - ax_h + 160), (ox + 320, oy - ax_h + 215), (ox + 480, oy - ax_h + 235)]
    path_R = "M " + " L ".join("%d,%d" % (x, y) for x, y in pts_R)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_R, NEG))
    frags.append(text(ox + 460, oy - ax_h + 225, "Поверхневий опір R_s (Ом/□)", size=11, color=NEG, bold=True, anchor="end"))

    # Optimal Tradeoff Window (shaded region)
    opt_x1, opt_x2 = ox + 220, ox + 330
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="#fcf3cf" stroke="#f39c12" stroke-width="1.5" stroke-dasharray="4,4"/>' % (opt_x1, oy - ax_h + 10, opt_x2 - opt_x1, ax_h - 20))
    frags.append(text((opt_x1 + opt_x2) / 2, oy - ax_h + 32, "Вікно TCO", size=11, color="#b7950b", bold=True))
    frags.append(text((opt_x1 + opt_x2) / 2, oy - ax_h + 48, "R_s ≈ 10-15 Ом/□", size=10, color=INK))
    frags.append(text((opt_x1 + opt_x2) / 2, oy - ax_h + 64, "T ≈ 85-90%", size=10, color=INK))

    # Callout Box for Haacke Figure of Merit
    frags.append(textbox(470, 100, "Фактор якості Хааке:\nF_TC = T¹⁰ / R_s\nМаксимізація прозорості", size=10, fill="#f4f6f7", stroke=FIELD)[0])

    render(os.path.join(img_dir, "tco-tradeoff-transmission-resistance.svg"), w, h, *frags)


if __name__ == '__main__':
    gen_sheet_resistance_square()
    gen_four_probe_geometry()
    gen_van_der_pauw_geometry()
    gen_tco_tradeoff_transmission_resistance()
    print("All sheet-resistance figures generated successfully.")

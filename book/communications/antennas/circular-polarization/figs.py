# -*- coding: utf-8 -*-
import os
import sys
import math

# Add root scripts/ to sys.path (4 levels up from topic dir)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def make_polarization_ellipse(path):
    w, h = 600, 360
    frags = []
    
    # Background grid & axes
    cx, cy = 250, 190
    frags.append(line(50, cy, 450, cy, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(line(cx, 40, cx, 340, color=MUTED, sw=1.2, dash="4 4"))
    
    # Bounding rectangle for E0x, E0y
    ex, ey = 140, 90
    frags.append(rect(cx - ex, cy - ey, 2 * ex, 2 * ey, fill="none", stroke=MUTED, sw=1.0, rx=0))
    frags.append(text(cx + ex + 15, cy + 5, "E₀x", size=13, color=MUTED, bold=True))
    frags.append(text(cx + 5, cy - ey - 10, "E₀y", size=13, color=MUTED, bold=True))
    
    # Rotated Ellipse (tau = 28 deg)
    tau_deg = 28.0
    tau_rad = math.radians(tau_deg)
    a, b = 150, 65 # Major and minor semi-axes
    
    # Generate path points for ellipse
    pts = []
    for i in range(73):
        t = i * 2 * math.pi / 72
        x_raw = a * math.cos(t)
        y_raw = b * math.sin(t)
        xr = cx + x_raw * math.cos(tau_rad) - y_raw * math.sin(tau_rad)
        yr = cy - (x_raw * math.sin(tau_rad) + y_raw * math.cos(tau_rad))
        pts.append("%.1f,%.1f" % (xr, yr))
    
    path_d = "M " + " L ".join(pts) + " Z"
    frags.append('<path d="%s" fill="#eaf0fd" fill-opacity="0.4" stroke="%s" stroke-width="2.5"/>' % (path_d, NEG))
    
    # Major axis line (a)
    ax_x = a * math.cos(tau_rad)
    ax_y = a * math.sin(tau_rad)
    frags.append(line(cx - ax_x, cy + ax_y, cx + ax_x, cy - ax_y, color=POS, sw=2.0))
    
    # Minor axis line (b)
    bx_x = -b * math.sin(tau_rad)
    bx_y = b * math.cos(tau_rad)
    frags.append(line(cx - bx_x, cy - bx_y, cx + bx_x, cy + bx_y, color=FIELD, sw=2.0))
    
    # Angle tau arc
    frags.append(line(cx, cy, cx + 110, cy, color=LINE, sw=1.0))
    frags.append('<path d="M %d %d A 70 70 0 0 0 %d %d" fill="none" stroke="%s" stroke-width="1.8"/>' % 
                 (cx + 70, cy, cx + 70 * math.cos(tau_rad), cy - 70 * math.sin(tau_rad), POS))
    frags.append(text(cx + 82, cy - 18, "τ", size=15, color=POS, bold=True))
    
    # Rotating vector E(t) at instantaneous point
    t_inst = math.radians(50)
    x_inst_raw = a * math.cos(t_inst)
    y_inst_raw = b * math.sin(t_inst)
    x_inst = cx + x_inst_raw * math.cos(tau_rad) - y_inst_raw * math.sin(tau_rad)
    y_inst = cy - (x_inst_raw * math.sin(tau_rad) + y_inst_raw * math.cos(tau_rad))
    
    frags.append(arrow(cx, cy, x_inst, y_inst, color=LINE, sw=2.5))
    frags.append(circle(x_inst, y_inst, 4, fill=LINE, stroke=BG, sw=1.0))
    frags.append(text(x_inst + 15, y_inst - 10, "E(t)", size=14, color=LINE, bold=True))
    
    # Rotation arrow on ellipse
    frags.append('<path d="M %d %d A 150 65 0 0 1 %d %d" fill="none" stroke="%s" stroke-width="2.0" marker-end="url(#arrow)"/>' %
                 (cx + ax_x, cy - ax_y, cx + ax_x - 30, cy - ax_y - 25, LINE))
    
    # Labels box on the right
    box_str = "Осьове відношення:\nAR = E_major / E_minor\nAR_dB = 20·log₁₀(a / b)\n\nКут нахилу: τ\nРізниця фаз: δ"
    b_html, _, _ = textbox(510, 190, box_str, size=12, pad=10, fill=FILL, stroke=LINE, sw=1.5)
    frags.append(b_html)
    
    render(path, w, h, *frags, title="Геометрія поляризаційного еліпса")

def make_rhcp_lhcp_helix(path):
    w, h = 680, 320
    frags = []
    
    # Panel 1: RHCP (Left side)
    p1_cx = 170
    frags.append(rect(20, 50, 300, 240, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(p1_cx, 75, "Права колова (RHCP)", size=15, color=POS, bold=True))
    
    # Propagation axis Z
    frags.append(arrow(40, 215, 300, 215, color=MUTED, sw=1.5))
    frags.append(text(295, 230, "+z", size=12, color=MUTED, bold=True))
    
    # Helix vectors for RHCP
    for idx, z_pos in enumerate(range(60, 270, 35)):
        angle = (idx * 45) % 360
        rad = math.radians(angle)
        length = 40
        ex = z_pos
        ey = 160 - length * math.sin(rad)
        frags.append(line(z_pos, 160, ex, ey, color=POS, sw=1.8))
        frags.append(circle(ex, ey, 3, fill=POS, stroke=BG, sw=1))
    
    frags.append(fitbox(30, 240, 280, 40, "Вектор E обертається за годинниковою\n(правило правої руки уздовж z)", size=11, fill="none", stroke="none"))
    
    # Panel 2: LHCP (Right side)
    p2_cx = 510
    frags.append(rect(360, 50, 300, 240, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(p2_cx, 75, "Ліва колова (LHCP)", size=15, color=NEG, bold=True))
    
    # Propagation axis Z
    frags.append(arrow(380, 215, 640, 215, color=MUTED, sw=1.5))
    frags.append(text(635, 230, "+z", size=12, color=MUTED, bold=True))
    
    # Helix vectors for LHCP (opposite phase progression)
    for idx, z_pos in enumerate(range(400, 610, 35)):
        angle = (-idx * 45) % 360
        rad = math.radians(angle)
        length = 40
        ex = z_pos
        ey = 160 - length * math.sin(rad)
        frags.append(line(z_pos, 160, ex, ey, color=NEG, sw=1.8))
        frags.append(circle(ex, ey, 3, fill=NEG, stroke=BG, sw=1))
        
    frags.append(fitbox(370, 240, 280, 40, "Вектор E обертається проти годинникової\n(правило лівої руки уздовж z)", size=11, fill="none", stroke="none"))
    
    render(path, w, h, *frags, title="Права (RHCP) та ліва (LHCP) колова поляризація")

def make_poincare_sphere(path):
    w, h = 620, 360
    frags = []
    
    cx, cy = 250, 195
    r = 130
    
    # Sphere outer boundary
    frags.append(circle(cx, cy, r, fill="#f8fafd", stroke=LINE, sw=2.0))
    # Equator ellipse
    frags.append('<ellipse cx="%d" cy="%d" rx="%d" ry="35" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4 4"/>' %
                 (cx, cy, r, MUTED))
    
    # Axes S1, S2, S3
    frags.append(arrow(cx, cy + r + 15, cx, cy - r - 20, color=LINE, sw=1.8)) # S3 axis (Poles)
    frags.append(text(cx + 15, cy - r - 10, "S₃ (RHCP / LHCP)", size=12, color=LINE, bold=True))
    
    frags.append(line(cx - r - 20, cy, cx + r + 20, cy, color=MUTED, sw=1.2)) # S1 axis
    frags.append(text(cx + r + 25, cy + 4, "S₁ (H / V)", size=11, color=MUTED))
    
    # North Pole (RHCP)
    frags.append(circle(cx, cy - r, 6, fill=POS, stroke=BG, sw=1.5))
    frags.append(text(cx + 35, cy - r + 5, "+S₃: Північний полюс (RHCP)", size=12, color=POS, bold=True))
    
    # South Pole (LHCP)
    frags.append(circle(cx, cy + r, 6, fill=NEG, stroke=BG, sw=1.5))
    frags.append(text(cx + 35, cy + r + 5, "−S₃: Південний полюс (LHCP)", size=12, color=NEG, bold=True))
    
    # Equator points (Linear polarizations)
    frags.append(circle(cx - r, cy, 4, fill=FIELD, stroke=BG, sw=1.0))
    frags.append(text(cx - r - 15, cy - 10, "0° (H)", size=11, color=FIELD, bold=True))
    
    frags.append(circle(cx + r, cy, 4, fill=FIELD, stroke=BG, sw=1.0))
    frags.append(text(cx + r - 15, cy - 10, "90° (V)", size=11, color=FIELD, bold=True))
    
    # Arbitrary state P on upper hemisphere
    px, py = cx + 70, cy - 70
    frags.append(line(cx, cy, px, py, color=LINE, sw=2.0))
    frags.append(circle(px, py, 5, fill=LINE, stroke=BG, sw=1.5))
    frags.append(text(px + 15, py - 5, "P(S₁, S₂, S₃)", size=12, color=LINE, bold=True))
    frags.append(text(px + 15, py + 12, "Еліптична справа", size=11, color=MUTED))
    
    # Legend Box on right
    legend_str = "Параметри Стокса:\nS₀: Повна інтенсивність\nS₁: Лінійна 0° / 90°\nS₂: Лінійна +45° / −45°\nS₃: Колова RHCP / LHCP\n\nСфера Пуанкаре:\nЕкватор → Лінійні\nПолюси → Кругові\nПоверхня → Чисті стани"
    b_html, _, _ = textbox(490, 195, legend_str, size=11, pad=10, fill=FILL, stroke=LINE, sw=1.5)
    frags.append(b_html)
    
    render(path, w, h, *frags, title="Сфера Пуанкаре для станів поляризації")

def make_reflection_reversal(path):
    w, h = 620, 300
    frags = []
    
    # Metal reflector plate at bottom
    ref_y = 220
    frags.append(rect(80, ref_y, 460, 20, fill="#d1d5db", stroke=LINE, sw=1.8, rx=2))
    frags.append(text(310, ref_y + 14, "Металевий відбивач (Провідник)", size=12, color=INK, bold=True))
    
    # Incident Wave (Left down)
    inc_x1, inc_y1 = 120, 70
    inc_x2, inc_y2 = 310, ref_y
    frags.append(arrow(inc_x1, inc_y1, inc_x2, inc_y2, color=POS, sw=2.5))
    
    # Incident RHCP Helix icon
    frags.append(circle(200, 130, 22, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(text(200, 134, "RHCP", size=12, color=POS, bold=True))
    frags.append(text(150, 90, "Падаюча хвиля", size=12, color=POS))
    
    # Reflected Wave (Right up)
    ref_x1, ref_y1 = 310, ref_y
    ref_x2, ref_y2 = 500, 70
    frags.append(arrow(ref_x1, ref_y1, ref_x2, ref_y2, color=NEG, sw=2.5))
    
    # Reflected LHCP Helix icon
    frags.append(circle(420, 130, 22, fill="#eaf0fd", stroke=NEG, sw=1.5))
    frags.append(text(420, 134, "LHCP", size=12, color=NEG, bold=True))
    frags.append(text(470, 90, "Відбита хвиля", size=12, color=NEG))
    
    # Phase inversion explanation
    info_str = "При дзеркальному відбитті дотична складова поля E перевертає фазу на 180°.\nВектор напрямку k змінює знак → RHCP перетворюється на LHCP!"
    frags.append(fitbox(110, 250, 400, 40, info_str, size=11, fill=FILL, stroke=LINE))
    
    render(path, w, h, *frags, title="Інверсія напрямку обертання при відбитті")

def make_cp_feed_methods(path):
    w, h = 720, 320
    frags = []
    
    # Method A: Dual-Feed Patch
    frags.append(rect(20, 50, 215, 240, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(127, 75, "а) Квадратурне живлення", size=13, color=INK, bold=True))
    
    # Patch square
    frags.append(rect(67, 100, 120, 100, fill="#feecd8", stroke="#d97706", sw=2.0, rx=4))
    # Feeds
    frags.append(arrow(127, 230, 127, 200, color=POS, sw=2.0))
    frags.append(text(127, 245, "Порт 0°", size=11, color=POS, bold=True))
    
    frags.append(arrow(30, 150, 67, 150, color=NEG, sw=2.0))
    frags.append(text(48, 138, "Порт 90°", size=11, color=NEG, bold=True))
    
    frags.append(fitbox(30, 260, 195, 24, "Фазовий зсув 90° через\nмост або λ/4 лінію", size=10, fill="none", stroke="none"))
    
    # Method B: Truncated Corners Patch
    frags.append(rect(252, 50, 215, 240, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(359, 75, "б) Зрізані кути (Patch)", size=13, color=INK, bold=True))
    
    # Patch with cut corners (polygon)
    poly_pts = "299,100 399,100 419,120 419,200 319,200 299,180"
    frags.append('<polygon points="%s" fill="#e0f2fe" stroke="%s" stroke-width="2.0"/>' % (poly_pts, NEG))
    
    # Single Feed Pin
    frags.append(circle(339, 170, 5, fill=POS, stroke=BG, sw=1.5))
    frags.append(arrow(339, 230, 339, 175, color=POS, sw=1.8))
    frags.append(text(359, 245, "Один фідер", size=11, color=POS, bold=True))
    
    frags.append(fitbox(262, 260, 195, 24, "Збудження двох модифікованих\nортогональних мод", size=10, fill="none", stroke="none"))
    
    # Method C: Axial Helix
    frags.append(rect(484, 50, 215, 240, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(591, 75, "в) Осьова спіраль", size=13, color=INK, bold=True))
    
    # Reflector backplate
    frags.append(line(510, 100, 510, 210, color=LINE, sw=4.0))
    frags.append(text(505, 225, "Екран", size=10, color=LINE))
    
    # Helix curve
    helix_pts = []
    for i in range(120):
        t = i * 0.1
        hx = 515 + i * 1.3
        hy = 155 + 35 * math.sin(t)
        helix_pts.append("%.1f,%.1f" % (hx, hy))
    frags.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" L ".join(helix_pts), FIELD))
    
    frags.append(arrow(490, 155, 510, 155, color=POS, sw=1.8))
    frags.append(fitbox(494, 260, 195, 24, "Біжуча хвиля вздовж\nвитків з периметром C ≈ λ", size=10, fill="none", stroke="none"))
    
    render(path, w, h, *frags, title="Конструктивні методи формування кругової поляризації")

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    make_polarization_ellipse(os.path.join(img_dir, 'polarization-ellipse.svg'))
    make_rhcp_lhcp_helix(os.path.join(img_dir, 'rhcp-lhcp-helix.svg'))
    make_poincare_sphere(os.path.join(img_dir, 'poincare-sphere.svg'))
    make_reflection_reversal(os.path.join(img_dir, 'reflection-reversal.svg'))
    make_cp_feed_methods(os.path.join(img_dir, 'cp-feed-methods.svg'))
    print("All figures successfully generated!")

if __name__ == '__main__':
    main()

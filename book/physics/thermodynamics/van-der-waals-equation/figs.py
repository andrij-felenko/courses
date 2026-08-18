# -*- coding: utf-8 -*-
import os
import sys
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def make_isotherms_fig():
    w, h = 720, 480
    frags = []
    
    # Title
    frags.append(text(w / 2, 25, "Ізотерми Ван дер Ваальса та петля Максвелла", size=16, bold=True))
    
    # Axes
    ox, oy = 70, 420
    ax_w, ax_h = 580, 350
    
    frags.append(arrow(ox, oy, ox + ax_w, oy, color=LINE, sw=1.8)) # V axis
    frags.append(arrow(ox, oy, ox, oy - ax_h, color=LINE, sw=1.8)) # P axis
    
    frags.append(text(ox + ax_w - 20, oy + 25, "Молярний об'єм V_m", size=13, bold=True, anchor="end"))
    frags.append(text(ox - 15, oy - ax_h + 15, "Тиск P", size=13, bold=True, anchor="end"))
    
    # Critical point coordinates
    vc_x = ox + 220
    pc_y = oy - 200
    
    # Grid / dashed reference lines for Critical Point
    frags.append(line(vc_x, oy, vc_x, pc_y, color=MUTED, sw=1, dash="4,4"))
    frags.append(line(ox, pc_y, vc_x, pc_y, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(vc_x, oy + 18, "V_c", size=12, bold=True))
    frags.append(text(ox - 10, pc_y + 4, "P_c", size=12, bold=True, anchor="end"))
    
    # Binodal dome (coexistence curve) - parabolic dashed curve
    dome_pts = []
    for t in range(0, 101):
        frac = t / 100.0
        # V from 110 to 450
        vx = ox + 90 + frac * 320
        # Peak at vc_x, pc_y
        norm_v = (vx - vc_x) / 160.0
        py = pc_y + 170.0 * (norm_v ** 2)
        if py <= oy:
            dome_pts.append((vx, py))
            
    d_path = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in dome_pts)
    frags.append(f'<path d="{d_path}" fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="5,5"/>')
    
    # Reduced equation: p = 8*t/(3*v - 1) - 3/v^2
    def vdw_p(v_red, t_red):
        if v_red <= 0.35:
            return 10.0
        return 8.0 * t_red / (3.0 * v_red - 1.0) - 3.0 / (v_red ** 2)
    
    def map_coords(v_red, p_red):
        # v_red = 1 -> vc_x, p_red = 1 -> pc_y
        cx = vc_x + (v_red - 1.0) * 160.0
        cy = pc_y - (p_red - 1.0) * 140.0
        return cx, cy

    # T > Tc (t_red = 1.15)
    pts_super = []
    for i in range(40, 320):
        vr = i / 100.0
        pr = vdw_p(vr, 1.15)
        cx, cy = map_coords(vr, pr)
        if ox + 10 <= cx <= ox + ax_w - 20 and oy - ax_h + 10 <= cy <= oy - 10:
            pts_super.append((cx, cy))
    path_super = "M " + " L ".join(f"{cx:.1f} {cy:.1f}" for cx, cy in pts_super)
    frags.append(f'<path d="{path_super}" fill="none" stroke="{NEG}" stroke-width="2"/>')
    frags.append(text(ox + ax_w - 60, oy - 290, "T > T_c (надкритична)", size=12, color=NEG, bold=True))
    
    # T = Tc (t_red = 1.0)
    pts_crit = []
    for i in range(38, 320):
        vr = i / 100.0
        pr = vdw_p(vr, 1.0)
        cx, cy = map_coords(vr, pr)
        if ox + 10 <= cx <= ox + ax_w - 20 and oy - ax_h + 10 <= cy <= oy - 10:
            pts_crit.append((cx, cy))
    path_crit = "M " + " L ".join(f"{cx:.1f} {cy:.1f}" for cx, cy in pts_crit)
    frags.append(f'<path d="{path_crit}" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    frags.append(text(ox + ax_w - 60, oy - 210, "T = T_c (критична)", size=12, color=INK, bold=True))
    
    # T < Tc (t_red = 0.85)
    pts_sub = []
    for i in range(36, 320):
        vr = i / 100.0
        pr = vdw_p(vr, 0.85)
        cx, cy = map_coords(vr, pr)
        if ox + 10 <= cx <= ox + ax_w - 20 and oy - ax_h + 20 <= cy <= oy + 30:
            pts_sub.append((cx, cy))
    path_sub = "M " + " L ".join(f"{cx:.1f} {cy:.1f}" for cx, cy in pts_sub)
    frags.append(f'<path d="{path_sub}" fill="none" stroke="{POS}" stroke-width="2"/>')
    frags.append(text(ox + ax_w - 60, oy - 90, "T < T_c (підкритична)", size=12, color=POS, bold=True))
    
    # Maxwell tie line for t_red = 0.85 (P_sat_red ≈ 0.60)
    vl_r, vg_r = 0.52, 2.22
    p_sat_r = 0.60
    xl, y_sat = map_coords(vl_r, p_sat_r)
    xg, _ = map_coords(vg_r, p_sat_r)
    
    # Shading areas S1 and S2
    xm, _ = map_coords(1.0, p_sat_r)
    
    # Area S1 (above tie-line, between xl and xm)
    pts_s1 = [(xl, y_sat)]
    for i in range(int(vl_r*100), int(1.0*100)+1):
        vr = i / 100.0
        pr = vdw_p(vr, 0.85)
        cx, cy = map_coords(vr, pr)
        pts_s1.append((cx, cy))
    pts_s1.append((xm, y_sat))
    path_s1 = "M " + " L ".join(f"{cx:.1f} {cy:.1f}" for cx, cy in pts_s1) + " Z"
    frags.append(f'<path d="{path_s1}" fill="#fdecea" opacity="0.6" stroke="none"/>')
    
    # Area S2 (below tie-line, between xm and xg)
    pts_s2 = [(xm, y_sat)]
    for i in range(int(1.0*100), int(vg_r*100)+1):
        vr = i / 100.0
        pr = vdw_p(vr, 0.85)
        cx, cy = map_coords(vr, pr)
        pts_s2.append((cx, cy))
    pts_s2.append((xg, y_sat))
    path_s2 = "M " + " L ".join(f"{cx:.1f} {cy:.1f}" for cx, cy in pts_s2) + " Z"
    frags.append(f'<path d="{path_s2}" fill="#eaf0fd" opacity="0.6" stroke="none"/>')
    
    # Tie line (Maxwell construction)
    frags.append(line(xl, y_sat, xg, y_sat, color=FIELD, sw=2.5))
    frags.append(text(ox - 10, y_sat + 4, "P_нас", size=12, color=FIELD, bold=True, anchor="end"))
    frags.append(circle(xl, y_sat, 4, fill=FIELD, stroke=INK, sw=1))
    frags.append(circle(xg, y_sat, 4, fill=FIELD, stroke=INK, sw=1))
    frags.append(line(xl, y_sat, xl, oy, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(xg, y_sat, xg, oy, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(xl, oy + 18, "V_р", size=11, bold=True))
    frags.append(text(xg, oy + 18, "V_п", size=11, bold=True))
    
    # Area labels
    frags.append(text((xl + xm) / 2, y_sat - 14, "S₁", size=13, color=POS, bold=True))
    frags.append(text((xm + xg) / 2, y_sat + 18, "S₂", size=13, color=NEG, bold=True))
    frags.append(text((xl + xg) / 2, y_sat - 28, "Пряма Максвелла (S₁ = S₂)", size=11, color=FIELD, bold=True))
    
    # Critical point marker
    frags.append(circle(vc_x, pc_y, 5, fill=POS, stroke=INK, sw=1.5))
    tb, tw, th = textbox(vc_x + 85, pc_y - 20, "Критична точка\n(∂P/∂V = 0, ∂²P/∂V² = 0)", size=11, fill="#fff8e7", stroke=POS)
    frags.append(tb)
    
    # Phase region labels
    frags.append(text(ox + 45, oy - 260, "Рідина", size=13, color=INK, bold=True))
    frags.append(text(vc_x, oy - 70, "Двофазна область\n(Рідина + Пара)", size=12, color=MUTED, bold=True))
    frags.append(text(ox + ax_w - 90, oy - 150, "Пара / Газ", size=13, color=INK, bold=True))
    
    render(os.path.join(IMG_DIR, "isotherms-and-maxwell.svg"), w, h, *frags)

def make_molecular_corrections_fig():
    w, h = 740, 380
    frags = []
    
    frags.append(text(w / 2, 25, "Мікроскопічний зміст поправок Ван дер Ваальса", size=16, bold=True))
    
    # Left Panel: Co-volume b
    p1_x, p1_y, p1_w, p1_h = 20, 50, 335, 300
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(p1_x + p1_w / 2, p1_y + 24, "a) Власний об'єм (поправка b)", size=14, bold=True))
    
    # Container boundary inside panel 1
    box1_x, box1_y, box1_w, box1_h = p1_x + 25, p1_y + 45, 285, 175
    frags.append(rect(box1_x, box1_y, box1_w, box1_h, fill="#ffffff", stroke=MUTED, sw=1.5, rx=4))
    
    # Spheres in box 1
    c1_x, c1_y = box1_x + 110, box1_y + 90
    r_mol = 18
    frags.append(circle(c1_x, c1_y, 2 * r_mol, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(circle(c1_x - r_mol + 3, c1_y, r_mol, fill="#eaf0fd", stroke=NEG, sw=1.5))
    frags.append(circle(c1_x + r_mol - 3, c1_y, r_mol, fill="#eaf0fd", stroke=NEG, sw=1.5))
    
    frags.append(line(c1_x - r_mol + 3, c1_y, c1_x + r_mol - 3, c1_y, color=INK, sw=1.2))
    frags.append(text(c1_x, c1_y - 6, "2r", size=11, bold=True))
    
    other_mols = [(box1_x + 40, box1_y + 40), (box1_x + 240, box1_y + 50),
                  (box1_x + 50, box1_y + 140), (box1_x + 230, box1_y + 135)]
    for mx, my in other_mols:
        frags.append(circle(mx, my, r_mol, fill="#f4f6f8", stroke=MUTED, sw=1.2))
        
    tb1 = fitbox(p1_x + 15, p1_y + 230, p1_w - 30, 58, 
                 "Об'єм виключення для пари = 8 · v₀\nКо-об'єм b = 4 · N_A · v₀\nДоступний об'єм = V - b", 
                 size=12, fill="#fff8e7", stroke=LINE)
    frags.append(tb1)
    
    # Right Panel: Internal Pressure a/V^2
    p2_x, p2_y, p2_w, p2_h = 385, 50, 335, 300
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(p2_x + p2_w / 2, p2_y + 24, "б) Притягання молекул (поправка a/V²)", size=14, bold=True))
    
    box2_x, box2_y, box2_w, box2_h = p2_x + 25, p2_y + 45, 285, 175
    frags.append(rect(box2_x, box2_y, box2_w, box2_h, fill="#ffffff", stroke=MUTED, sw=1.5, rx=4))
    frags.append(rect(box2_x + box2_w - 12, box2_y, 12, box2_h, fill="#d0d7de", stroke=LINE, sw=1.5, rx=0))
    frags.append(text(box2_x + box2_w - 6, box2_y + box2_h / 2, "Стінка", size=10, bold=True, anchor="middle"))
    
    ax, ay = box2_x + 75, box2_y + 90
    frags.append(circle(ax, ay, 14, fill="#eaf0fd", stroke=NEG, sw=1.5))
    frags.append(text(ax, ay + 4, "A", size=11, bold=True))
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(angle)
        fx1 = ax + 14 * math.cos(rad)
        fy1 = ay + 14 * math.sin(rad)
        fx2 = ax + 32 * math.cos(rad)
        fy2 = ay + 32 * math.sin(rad)
        frags.append(arrow(fx1, fy1, fx2, fy2, color=FIELD, sw=1.2))
        
    bx, by = box2_x + box2_w - 28, box2_y + 90
    frags.append(circle(bx, by, 14, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(text(bx, by + 4, "B", size=11, bold=True))
    for angle in [135, 180, 225]:
        rad = math.radians(angle)
        fx1 = bx + 14 * math.cos(rad)
        fy1 = by + 14 * math.sin(rad)
        fx2 = bx + 38 * math.cos(rad)
        fy2 = by + 38 * math.sin(rad)
        frags.append(arrow(fx1, fy1, fx2, fy2, color=POS, sw=1.8))
        
    frags.append(arrow(bx + 14, by, bx + 24, by, color=INK, sw=1.5))
    
    tb2 = fitbox(p2_x + 15, p2_y + 230, p2_w - 30, 58,
                 "В товщі (A): ∑ F = 0 (рівновага)\nБіля стінки (B): F_внутр тягне назад\nP_ефективний = P_виміряний + a / V_m²",
                 size=12, fill="#fff8e7", stroke=LINE)
    frags.append(tb2)
    
    render(os.path.join(IMG_DIR, "molecular-corrections.svg"), w, h, *frags)

if __name__ == '__main__':
    make_isotherms_fig()
    make_molecular_corrections_fig()
    print("Figures generated successfully.")

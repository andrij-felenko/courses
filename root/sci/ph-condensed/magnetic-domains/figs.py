# -*- coding: utf-8 -*-
import sys
import os

# Four levels up to reach scripts/ folder from book/physics/condensed-matter-physics/magnetic-domains/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# -----------------------------------------------------------------------------
# Figure 1: domain-energy-balance.svg
# Energy minimization leading to magnetic domain formation
# -----------------------------------------------------------------------------
def gen_domain_energy_balance():
    w, h = 820, 360
    frags = []
    
    # Title
    frags.append(text(w / 2, 26, "Мінімізація вільної енергії та формування магнітних доменів", size=16, bold=True))

    # Panel A: Single domain
    x_a = 50
    frags.append(rect(x_a, 60, 200, 230, fill="#fafafa", stroke=LINE, sw=1.5))
    frags.append(text(x_a + 100, 85, "а) Однодоменний кристал", size=13, color=INK, bold=True, anchor="middle"))
    
    # Main domain box
    frags.append(rect(x_a + 40, 115, 120, 110, fill="#fee2e2", stroke=POS, sw=2))
    # Arrow inside pointing UP
    frags.append(arrow(x_a + 100, 210, x_a + 100, 130, color=POS, sw=3.0))
    frags.append(text(x_a + 100, 170, "M = Ms", size=13, color=POS, bold=True, anchor="middle"))
    
    # Stray field lines outside (arcs/lines)
    frags.append(line(x_a + 60, 115, x_a + 20, 75, color=NEG, sw=1.5, dash="4,3"))
    frags.append(line(x_a + 20, 75, x_a + 20, 265, color=NEG, sw=1.5, dash="4,3"))
    frags.append(arrow(x_a + 20, 265, x_a + 60, 225, color=NEG, sw=1.5))
    
    frags.append(line(x_a + 140, 115, x_a + 180, 75, color=NEG, sw=1.5, dash="4,3"))
    frags.append(line(x_a + 180, 75, x_a + 180, 265, color=NEG, sw=1.5, dash="4,3"))
    frags.append(arrow(x_a + 180, 265, x_a + 140, 225, color=NEG, sw=1.5))
    
    frags.append(mtext(x_a + 100, 250, ["Величезне поле", "розсіювання (Ed макс)"], size=11, color=POS, anchor="middle"))

    # Panel B: Two domains
    x_b = 310
    frags.append(rect(x_b, 60, 200, 230, fill="#fafafa", stroke=LINE, sw=1.5))
    frags.append(text(x_b + 100, 85, "б) Дводоменна структура", size=13, color=INK, bold=True, anchor="middle"))
    
    # Box split in 2
    frags.append(rect(x_b + 40, 115, 60, 110, fill="#fee2e2", stroke=POS, sw=1.5))
    frags.append(rect(x_b + 100, 115, 60, 110, fill="#dbeafe", stroke=NEG, sw=1.5))
    # Wall line
    frags.append(line(x_b + 100, 115, x_b + 100, 225, color=LINE, sw=2))
    
    # Arrows inside
    frags.append(arrow(x_b + 70, 210, x_b + 70, 130, color=POS, sw=2.5))
    frags.append(arrow(x_b + 130, 130, x_b + 130, 210, color=NEG, sw=2.5))
    
    # Stray field (smaller)
    frags.append(line(x_b + 70, 115, x_b + 70, 98, color=MUTED, sw=1.2, dash="3,3"))
    frags.append(arrow(x_b + 70, 98, x_b + 130, 98, color=MUTED, sw=1.2))
    frags.append(line(x_b + 130, 98, x_b + 130, 115, color=MUTED, sw=1.2, dash="3,3"))

    frags.append(mtext(x_b + 100, 250, ["Ed зменшено вдвічі,", "виникла стінка (+Edw)"], size=11, color=INK, anchor="middle"))

    # Panel C: Closure domains
    x_c = 570
    frags.append(rect(x_c, 60, 200, 230, fill="#fafafa", stroke=LINE, sw=1.5))
    frags.append(text(x_c + 100, 85, "в) Домени замикання", size=13, color=INK, bold=True, anchor="middle"))
    
    # Internal vertical wall
    frags.append(line(x_c + 100, 145, x_c + 100, 195, color=LINE, sw=1.5))
    # Triangular wall lines
    frags.append(line(x_c + 40, 115, x_c + 100, 145, color=LINE, sw=1.5))
    frags.append(line(x_c + 160, 115, x_c + 100, 145, color=LINE, sw=1.5))
    frags.append(line(x_c + 40, 225, x_c + 100, 195, color=LINE, sw=1.5))
    frags.append(line(x_c + 160, 225, x_c + 100, 195, color=LINE, sw=1.5))
    
    # Fill colors for domains
    # Upper closure
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fef3c7" stroke="%s" stroke-width="1.2"/>' % 
                 (x_c + 40, 115, x_c + 160, 115, x_c + 100, 145, LINE))
    # Lower closure
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fef3c7" stroke="%s" stroke-width="1.2"/>' % 
                 (x_c + 40, 225, x_c + 160, 225, x_c + 100, 195, LINE))
    # Left main
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fee2e2" stroke="%s" stroke-width="1.2"/>' % 
                 (x_c + 40, 115, x_c + 100, 145, x_c + 100, 195, x_c + 40, 225, LINE))
    # Right main
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#dbeafe" stroke="%s" stroke-width="1.2"/>' % 
                 (x_c + 160, 115, x_c + 100, 145, x_c + 100, 195, x_c + 160, 225, LINE))

    # Arrows inside
    frags.append(arrow(x_c + 70, 200, x_c + 70, 140, color=POS, sw=2.2))
    frags.append(arrow(x_c + 130, 140, x_c + 130, 200, color=NEG, sw=2.2))
    frags.append(arrow(x_c + 75, 127, x_c + 125, 127, color=FIELD, sw=2.0))
    frags.append(arrow(x_c + 125, 213, x_c + 75, 213, color=FIELD, sw=2.0))

    frags.append(mtext(x_c + 100, 250, ["Поле розсіювання Ed = 0,", "замкнений магнітний потік"], size=11, color=FIELD, bold=True, anchor="middle"))

    # Bottom summary box
    frags.append(textbox(w / 2, 330, "Повна енергія: E_tot = E_d (магнітостатична) + E_ex (обмінна) + E_a (анізотропія) + E_λ (магнітострикція)", size=12, fill="#f1f5f9", stroke=LINE)[0])

    render(os.path.join(IMG_DIR, "domain-energy-balance.svg"), w, h, *frags)

# -----------------------------------------------------------------------------
# Figure 2: bloch-vs-neel.svg
# Comparison between Bloch wall and Neel wall profiles
# -----------------------------------------------------------------------------
def gen_bloch_vs_neel():
    w, h = 820, 360
    frags = []
    
    frags.append(text(w / 2, 24, "Структура доменних стінок Блоха та Нееля", size=16, bold=True))

    # Panel A: Bloch wall
    x_a = 40
    frags.append(rect(x_a, 60, 350, 270, fill="#fafafa", stroke=LINE, sw=1.5))
    frags.append(text(x_a + 175, 82, "а) Стінка Блоха (об'ємний матеріал)", size=13, bold=True, color=INK, anchor="middle"))
    
    # 3D/Slice view representation
    # Wall thickness region
    frags.append(rect(x_a + 100, 110, 150, 150, fill="#f1f5f9", stroke=FIELD, sw=1.5, rx=0))
    frags.append(line(x_a + 100, 110, x_a + 100, 260, color=FIELD, sw=2, dash="3,3"))
    frags.append(line(x_a + 250, 110, x_a + 250, 260, color=FIELD, sw=2, dash="3,3"))
    
    # Spins across wall (Bloch: rotates in y-z plane parallel to wall surface)
    # Spin 1 (left domain): pointing UP (+y)
    frags.append(arrow(x_a + 40, 230, x_a + 40, 140, color=POS, sw=2.5))
    frags.append(text(x_a + 40, 245, "θ = 0°", size=11, anchor="middle"))

    # Spin 2 (entering wall): rotated 45deg OUT OF PLANE / UP
    frags.append(arrow(x_a + 105, 220, x_a + 125, 150, color=POS, sw=2.2))
    
    # Spin 3 (center of wall): pointing OUT OF PAGE (represented as perspective diagonal or dot)
    frags.append(arrow(x_a + 175, 185, x_a + 205, 185, color=FIELD, sw=3.0))
    frags.append(text(x_a + 175, 172, "θ = 90°", size=11, color=FIELD, bold=True, anchor="middle"))

    # Spin 4 (exiting wall): rotated 135deg
    frags.append(arrow(x_a + 245, 150, x_a + 225, 220, color=NEG, sw=2.2))

    # Spin 5 (right domain): pointing DOWN (180deg)
    frags.append(arrow(x_a + 310, 140, x_a + 310, 230, color=NEG, sw=2.5))
    frags.append(text(x_a + 310, 245, "θ = 180°", size=11, anchor="middle"))

    # Thickness label δ
    frags.append(line(x_a + 100, 275, x_a + 250, 275, color=LINE, sw=1.5))
    frags.append(arrow(x_a + 175, 275, x_a + 100, 275, color=LINE, sw=1.2))
    frags.append(arrow(x_a + 175, 275, x_a + 250, 275, color=LINE, sw=1.2))
    frags.append(text(x_a + 175, 271, "Товщина δ ≈ π√(A/K)", size=11, color=INK, anchor="middle"))

    frags.append(mtext(x_a + 175, 305, ["Вектор M обертається паралельно площині стінки", "(відсутні поверхневі магнітні заряди)"], size=11, color=INK, anchor="middle"))

    # Panel B: Neel wall
    x_b = 430
    frags.append(rect(x_b, 60, 350, 270, fill="#fafafa", stroke=LINE, sw=1.5))
    frags.append(text(x_b + 175, 82, "б) Стінка Нееля (тонка плівка d < δ)", size=13, bold=True, color=INK, anchor="middle"))

    # Wall thickness region
    frags.append(rect(x_b + 100, 110, 150, 150, fill="#f1f5f9", stroke=POS, sw=1.5, rx=0))
    frags.append(line(x_b + 100, 110, x_b + 100, 260, color=POS, sw=2, dash="3,3"))
    frags.append(line(x_b + 250, 110, x_b + 250, 260, color=POS, sw=2, dash="3,3"))

    # Spins across wall (Neel: rotates in x-y plane perpendicular to wall surface)
    # Spin 1 (left domain): UP
    frags.append(arrow(x_b + 40, 230, x_b + 40, 140, color=POS, sw=2.5))

    # Spin 2: tilting right
    frags.append(arrow(x_b + 115, 220, x_b + 145, 150, color=POS, sw=2.2))

    # Spin 3 (center): pointing IN PLANE OF FILM / PERPENDICULAR TO WALL (RIGHT)
    frags.append(arrow(x_b + 160, 185, x_b + 190, 185, color=POS, sw=3.0))
    frags.append(text(x_b + 175, 170, "Полюси + −", size=11, color=POS, bold=True, anchor="middle"))

    # Spin 4: tilting down
    frags.append(arrow(x_b + 235, 150, x_b + 205, 220, color=NEG, sw=2.2))

    # Spin 5 (right domain): DOWN
    frags.append(arrow(x_b + 310, 140, x_b + 310, 230, color=NEG, sw=2.5))

    # Thin film indicator
    frags.append(text(x_b + 175, 271, "Плівка товщиною d < δ", size=11, color=INK, anchor="middle"))

    frags.append(mtext(x_b + 175, 305, ["Вектор M обертається в площині плівки", "(мінімізує демагнетизацію товщини плівки)"], size=11, color=INK, anchor="middle"))

    render(os.path.join(IMG_DIR, "bloch-vs-neel.svg"), w, h, *frags)

# -----------------------------------------------------------------------------
# Figure 3: hysteresis-domain-process.svg
# Hysteresis curve annotated with domain structure changes
# -----------------------------------------------------------------------------
def gen_hysteresis_domain_process():
    w, h = 820, 420
    frags = []
    
    frags.append(text(w / 2, 24, "Еволюція доменної структури вздовж петлі гістерезису", size=16, bold=True))

    # Central Hysteresis Axes
    cx, cy = 410, 220
    frags.append(line(cx - 200, cy, cx + 200, cy, color=LINE, sw=1.5)) # H axis
    frags.append(arrow(cx + 190, cy, cx + 210, cy, color=LINE, sw=1.5))
    frags.append(text(cx + 220, cy + 4, "H", size=14, bold=True))
    
    frags.append(line(cx, cy + 150, cx, cy - 150, color=LINE, sw=1.5)) # M axis
    frags.append(arrow(cx, cy - 140, cx, cy - 160, color=LINE, sw=1.5))
    frags.append(text(cx - 15, cy - 155, "M", size=14, bold=True))

    # Hysteresis curve (S-curve + return)
    # Virgin curve (0,0 -> saturation)
    frags.append('<path d="M %d,%d Q %d,%d %d,%d T %d,%d" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="4,3"/>' %
                 (cx, cy, cx + 50, cy - 40, cx + 100, cy - 100, cx + 170, cy - 130, MUTED))
    
    # Full hysteresis loop
    frags.append('<path d="M %d,%d C %d,%d %d,%d %d,%d C %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.5"/>' %
                 (cx - 170, cy + 130, cx - 20, cy + 130, cx + 60, cy - 70, cx + 170, cy - 130,
                  cx + 20, cy - 130, cx - 60, cy + 70, cx - 170, cy + 130, POS))

    # Annotations & Domain diagrams around loop

    # Point 1: Demagnetized state (0,0)
    p1_x, p1_y = 110, 310
    frags.append(rect(p1_x - 50, p1_y - 45, 100, 90, fill="#ffffff", stroke=LINE, sw=1.5))
    # Domain sketch: 4 domains cancel out
    frags.append(rect(p1_x - 35, p1_y - 35, 70, 50, fill="#f4f6f8", stroke=LINE, sw=1))
    frags.append(line(p1_x, p1_y - 35, p1_x, p1_y + 15, color=LINE, sw=1))
    frags.append(line(p1_x - 35, p1_y - 10, p1_x + 35, p1_y - 10, color=LINE, sw=1))
    frags.append(arrow(p1_x - 17, p1_y + 5, p1_x - 17, p1_y - 25, color=POS, sw=1.5))
    frags.append(arrow(p1_x + 17, p1_y - 25, p1_x + 17, p1_y + 5, color=NEG, sw=1.5))
    frags.append(arrow(p1_x - 30, p1_y - 22, p1_x - 5, p1_y - 22, color=FIELD, sw=1.5))
    frags.append(arrow(p1_x + 30, p1_y + 2, p1_x + 5, p1_y + 2, color=FIELD, sw=1.5))
    frags.append(text(p1_x, p1_y + 30, "1. H=0, M=0", size=10, color=INK, bold=True, anchor="middle"))
    frags.append(arrow(p1_x + 40, p1_y - 20, cx - 15, cy + 10, color=MUTED, sw=1.2))

    # Point 2: Reversible wall motion
    p2_x, p2_y = 210, 110
    frags.append(rect(p2_x - 50, p2_y - 45, 100, 90, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(rect(p2_x - 35, p2_y - 35, 70, 50, fill="#f4f6f8", stroke=LINE, sw=1))
    frags.append(line(p2_x + 15, p2_y - 35, p2_x + 15, p2_y + 15, color=LINE, sw=1.5)) # Wall shifted right
    frags.append(arrow(p2_x - 10, p2_y + 5, p2_x - 10, p2_y - 25, color=POS, sw=2.0)) # Favorable domain grew
    frags.append(arrow(p2_x + 25, p2_y - 25, p2_x + 25, p2_y + 5, color=NEG, sw=1.2))
    frags.append(text(p2_x, p2_y + 30, "2. Звернений зсув", size=10, color=INK, bold=True, anchor="middle"))
    frags.append(arrow(p2_x + 40, p2_y, cx + 45, cy - 35, color=MUTED, sw=1.2))

    # Point 3: Barkhausen jumps (irreversible pinning release)
    p3_x, p3_y = 610, 110
    frags.append(rect(p3_x - 50, p3_y - 45, 100, 90, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(rect(p3_x - 35, p3_y - 35, 70, 50, fill="#fee2e2", stroke=POS, sw=1))
    # Pinning defect dot
    frags.append(circle(p3_x - 10, p3_y - 10, 4, fill=INK, stroke=INK, sw=1))
    frags.append(line(p3_x + 20, p3_y - 35, p3_x + 20, p3_y + 15, color=POS, sw=1.8, dash="2,2")) # Jumped wall
    frags.append(arrow(p3_x - 5, p3_y + 5, p3_x - 5, p3_y - 25, color=POS, sw=2.2))
    frags.append(text(p3_x, p3_y + 30, "3. Баркгаузен", size=10, color=POS, bold=True, anchor="middle"))
    frags.append(arrow(p3_x - 40, p3_y, cx + 110, cy - 90, color=MUTED, sw=1.2))

    # Point 4: Saturation (domain rotation)
    p4_x, p4_y = 710, 310
    frags.append(rect(p4_x - 50, p4_y - 45, 100, 90, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(rect(p4_x - 35, p4_y - 35, 70, 50, fill="#fee2e2", stroke=POS, sw=1.5))
    # Single domain, arrow fully aligned right/up
    frags.append(arrow(p4_x - 20, p4_y + 5, p4_x + 20, p4_y - 25, color=POS, sw=3.0))
    frags.append(text(p4_x, p4_y + 30, "4. Насичення", size=10, color=POS, bold=True, anchor="middle"))
    frags.append(arrow(p4_x - 40, p4_y - 20, cx + 170, cy - 130, color=MUTED, sw=1.2))

    # Hc and Mr labels on axes
    frags.append(circle(cx - 75, cy, 3, fill=POS, stroke=POS, sw=1))
    frags.append(text(cx - 75, cy + 18, "-Hc", size=12, color=POS, bold=True, anchor="middle"))
    frags.append(circle(cx + 75, cy, 3, fill=POS, stroke=POS, sw=1))
    frags.append(text(cx + 75, cy - 12, "+Hc", size=12, color=POS, bold=True, anchor="middle"))

    frags.append(circle(cx, cy - 85, 3, fill=POS, stroke=POS, sw=1))
    frags.append(text(cx + 25, cy - 85, "+Mr", size=12, color=POS, bold=True, anchor="middle"))

    render(os.path.join(IMG_DIR, "hysteresis-domain-process.svg"), w, h, *frags)

# -----------------------------------------------------------------------------
# Figure 4: single-domain-critical-size.svg
# Energy vs radius R graph showing single domain threshold
# -----------------------------------------------------------------------------
def gen_single_domain_critical_size():
    w, h = 820, 360
    frags = []
    
    frags.append(text(w / 2, 24, "Залежність енергії від розміру частинки та критичний радіус R_c", size=16, bold=True))

    # Axes
    ox, oy = 100, 290
    frags.append(line(ox, oy, ox + 650, oy, color=LINE, sw=1.5)) # R axis
    frags.append(arrow(ox + 640, oy, ox + 660, oy, color=LINE, sw=1.5))
    frags.append(text(ox + 675, oy + 4, "Радіус частинки R", size=13, bold=True))

    frags.append(line(ox, oy, ox, oy - 230, color=LINE, sw=1.5)) # Energy axis
    frags.append(arrow(ox, oy - 220, ox, oy - 240, color=LINE, sw=1.5))
    frags.append(text(ox - 15, oy - 245, "Енергія E", size=13, bold=True))

    # Curves:
    # 1. Single domain energy E_1 (pure magnetostatic): E_1 = (1/2) * mu0 * M_s^2 * (4/3)*pi*R^3  (cubic growth R^3)
    frags.append('<path d="M %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.5"/>' %
                 (ox, oy, ox + 200, oy - 20, ox + 450, oy - 220, POS))
    frags.append(text(ox + 350, oy - 225, "E1 ∝ R³ (однодоменний стан, Ed)", size=12, color=POS, bold=True))

    # 2. Multi domain energy E_2 (small magnetostatic + wall energy): E_2 = E_wall (∝ R^2) + small Ed
    frags.append('<path d="M %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.5"/>' %
                 (ox, oy - 60, ox + 250, oy - 90, ox + 600, oy - 170, NEG))
    frags.append(text(ox + 615, oy - 185, "E2 ∝ R² + E'd (дводоменний стан)", size=12, color=NEG, bold=True))

    # Intersection point (R_c)
    # Intersection occurs at around ox + 320, oy - 115
    rc_x = ox + 320
    rc_y = oy - 115
    frags.append(circle(rc_x, rc_y, 5, fill=FIELD, stroke=FIELD, sw=1.5))
    frags.append(line(rc_x, rc_y, rc_x, oy, color=FIELD, sw=1.8, dash="4,3"))
    frags.append(text(rc_x, oy + 18, "Критичний радіус Rc", size=12, color=FIELD, bold=True, anchor="middle"))

    # Region shading / annotations
    # Left region: Single domain stable
    frags.append(rect(ox + 20, oy - 210, 220, 70, fill="#fef2f2", stroke=POS, sw=1.2))
    frags.append(mtext(ox + 130, oy - 175, ["R < Rc : ОДНОДОМЕННІ ЧАСТИНИ", "(Енергетично невигідно", "створювати доменну стінку)"], size=11, color=POS, bold=True, anchor="middle"))

    # Right region: Multi domain stable
    frags.append(rect(ox + 380, oy - 90, 240, 70, fill="#eff6ff", stroke=NEG, sw=1.2))
    frags.append(mtext(ox + 500, oy - 55, ["R > Rc : БАГАТОДОМЕННІ ЧАСТИНИ", "(Утворення доменів зменшує", "повну вільну енергію)"], size=11, color=NEG, bold=True, anchor="middle"))

    # Formula box for Rc
    frags.append(textbox(ox + 180, oy - 50, "Rc ≈ 9 · √(A · K) / (μ₀ · M_s²)", size=13, fill="#ffffff", stroke=LINE, bold=True)[0])

    render(os.path.join(IMG_DIR, "single-domain-critical-size.svg"), w, h, *frags)

# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    gen_domain_energy_balance()
    gen_bloch_vs_neel()
    gen_hysteresis_domain_process()
    gen_single_domain_critical_size()
    print("All magnetic-domains figures generated successfully.")

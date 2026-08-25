# -*- coding: utf-8 -*-
import sys, os

# Path to scripts/ folder from book/math/number-theory/equidistribution/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

def make_fig_concept(out_dir):
    w, h = 800, 320
    path = os.path.join(out_dir, 'fig-equidistribution-concept.svg')
    
    frags = []
    # Title text
    frags.append(text(w / 2, 25, "Типи розподілу послідовностей на відрізку [0, 1)", size=16, bold=True))
    
    # 3 Rows
    y_starts = [80, 160, 240]
    labels = [
        "А. Нерівномірний (скупчення): xₙ = (sin(n) + 1)/2",
        "Б. Раціональний ротатор (α = 3/8): дискретна ґратка з 8 точок",
        "В. Ірраціональний ротатор (α = (√5−1)/2): рівномірний розподіл"
    ]
    
    # Points data
    # Row A: clustered around 0.2..0.4 and 0.7..0.8
    pts_a = [0.05, 0.22, 0.24, 0.27, 0.30, 0.31, 0.33, 0.36, 0.38, 0.42, 0.71, 0.73, 0.76, 0.78, 0.92]
    # Row B: 8 exact points (0, 1/8, 2/8, 3/8, 4/8, 5/8, 6/8, 7/8)
    pts_b = [i / 8.0 for i in range(8)]
    # Row C: fractional parts of n * phi for n=1..30
    phi = (math.sqrt(5) - 1) / 2
    pts_c = sorted([(i * phi) % 1.0 for i in range(1, 35)])
    
    all_pts = [pts_a, pts_b, pts_c]
    colors = [POS, MUTED, FIELD]
    
    x_left, x_right = 260, 760
    axis_w = x_right - x_left
    
    for row in range(3):
        cy = y_starts[row]
        lbl = labels[row]
        col = colors[row]
        pts = all_pts[row]
        
        # Label on left
        frags.append(text(15, cy + 4, lbl, size=12, bold=True, anchor="start", color=INK))
        
        # Axis line [0, 1)
        frags.append(line(x_left, cy, x_right, cy, color=LINE, sw=2))
        # Ticks at 0 and 1
        frags.append(line(x_left, cy - 8, x_left, cy + 8, color=LINE, sw=2))
        frags.append(line(x_right, cy - 8, x_right, cy + 8, color=LINE, sw=2))
        frags.append(text(x_left, cy + 22, "0", size=11, color=MUTED))
        frags.append(text(x_right, cy + 22, "1", size=11, color=MUTED))
        
        # Draw points
        for p in pts:
            px = x_left + p * axis_w
            frags.append(circle(px, cy, 4, fill=col, stroke=INK, sw=1))
            
    render(path, w, h, *frags)
    print("Generated:", path)

def make_fig_weyl_vectors(out_dir):
    w, h = 800, 360
    path = os.path.join(out_dir, 'fig-weyl-criterion-vector.svg')
    
    frags = []
    frags.append(text(w / 2, 25, "Критерій Вейля: скасування комплексних векторів e²ᵖⁱ ⁱ ʰ ˣⁿ", size=16, bold=True))
    
    # Left Panel: Unit circle with vectors
    cx1, cy1, r1 = 220, 190, 100
    frags.append(textbox(cx1, 55, "Вектори е²ᵖⁱ ⁱ ʰ ˣⁿ на одиничному колі", size=13, bold=True, fill="#f0f4f8")[0])
    
    # Unit circle
    frags.append(circle(cx1, cy1, r1, fill="#ffffff", stroke=MUTED, sw=1.5))
    # Axes
    frags.append(line(cx1 - r1 - 15, cy1, cx1 + r1 + 15, cy1, color=MUTED, sw=1, dash="4,4"))
    frags.append(line(cx1, cy1 - r1 - 15, cx1, cy1 + r1 + 15, color=MUTED, sw=1, dash="4,4"))
    frags.append(text(cx1 + r1 + 25, cy1 + 4, "Re", size=12, bold=True, color=MUTED))
    frags.append(text(cx1, cy1 - r1 - 22, "Im", size=12, bold=True, color=MUTED))
    
    # Sample points on circle for n*sqrt(2)
    alpha = math.sqrt(2)
    sample_angles = [2 * math.pi * ((i * alpha) % 1.0) for i in range(1, 9)]
    for i, ang in enumerate(sample_angles):
        vx = cx1 + r1 * math.cos(ang)
        vy = cy1 - r1 * math.sin(ang)
        frags.append(arrow(cx1, cy1, vx, vy, color=NEG if i % 2 == 0 else POS, sw=1.5))
        frags.append(circle(vx, vy, 3.5, fill=INK, stroke=INK, sw=1))
        
    # Right Panel: Cumulative vector walk and center of mass
    cx2, cy2 = 590, 190
    frags.append(textbox(cx2, 55, "Центр мас S₋N / N прямує до (0, 0) при N → ∞", size=13, bold=True, fill="#eafaf1")[0])
    
    # Vector chain (walk)
    curr_x, curr_y = cx2 - 80, cy2 + 60
    frags.append(circle(curr_x, curr_y, 4, fill=POS, stroke=INK, sw=1.5))
    frags.append(text(curr_x - 15, curr_y + 15, "S₀=0", size=11, bold=True, color=POS))
    
    scale = 22
    for n in range(1, 12):
        ang = 2 * math.pi * ((n * alpha) % 1.0)
        nx = curr_x + scale * math.cos(ang)
        ny = curr_y - scale * math.sin(ang)
        frags.append(line(curr_x, curr_y, nx, ny, color=NEG, sw=2))
        curr_x, curr_y = nx, ny
        frags.append(circle(curr_x, curr_y, 2.5, fill=NEG, stroke=INK, sw=1))
        
    frags.append(text(curr_x + 15, curr_y, "S₁₁", size=11, bold=True, color=NEG))
    
    # Arrow to center of mass
    frags.append(arrow(cx2 - 80, cy2 + 60, curr_x, curr_y, color=POS, sw=2))
    frags.append(textbox(cx2 + 40, cy2 + 90, "|S₋N| ≤ M ⇒ |S₋N|/N → 0", size=12, fill="#fef9e7", stroke=POS)[0])
    
    render(path, w, h, *frags)
    print("Generated:", path)

def make_fig_discrepancy(out_dir):
    w, h = 800, 400
    path = os.path.join(out_dir, 'fig-discrepancy-definition.svg')
    
    frags = []
    frags.append(text(w / 2, 25, "Зіркова дискрепантність D*N: максимальне відхилення F_N(x) від y = x", size=16, bold=True))
    
    x0, y0 = 180, 330
    gw, gh = 480, 240
    
    # Coordinate system
    frags.append(rect(x0, y0 - gh, gw, gh, fill="#fafafa", stroke=MUTED, sw=1))
    
    # Ideal CDF: diagonal y = x
    frags.append(line(x0, y0, x0 + gw, y0 - gh, color=FIELD, sw=2.5, dash="6,4"))
    frags.append(text(x0 + gw - 60, y0 - gh + 25, "y = x (ідеальний)", size=12, color=FIELD, bold=True))
    
    # Axis labels
    frags.append(line(x0 - 15, y0, x0 + gw + 25, y0, color=LINE, sw=1.5))
    frags.append(line(x0, y0 + 15, x0, y0 - gh - 25, color=LINE, sw=1.5))
    frags.append(text(x0 + gw + 35, y0 + 4, "x", size=13, bold=True))
    frags.append(text(x0, y0 - gh - 32, "F_N(x)", size=13, bold=True))
    
    frags.append(text(x0, y0 + 20, "0", size=12))
    frags.append(text(x0 + gw, y0 + 20, "1", size=12))
    frags.append(text(x0 - 18, y0, "0", size=12))
    frags.append(text(x0 - 18, y0 - gh, "1", size=12))
    
    # Empirical CDF step function for N=5 points: 0.15, 0.35, 0.48, 0.72, 0.88
    pts = [0.15, 0.35, 0.48, 0.72, 0.88]
    N = len(pts)
    
    curr_x = 0
    curr_y_val = 0
    for i, p in enumerate(pts):
        px = p * gw
        py_prev = y0 - (curr_y_val / N) * gh
        px_curr = x0 + px
        
        # Horizontal step
        frags.append(line(x0 + curr_x * gw, py_prev, px_curr, py_prev, color=NEG, sw=2))
        
        curr_y_val += 1
        py_next = y0 - (curr_y_val / N) * gh
        # Vertical step
        frags.append(line(px_curr, py_prev, px_curr, py_next, color=NEG, sw=2))
        frags.append(circle(px_curr, py_next, 3.5, fill=NEG, stroke=INK, sw=1))
        curr_x = p
        
    # Last horizontal step
    frags.append(line(x0 + curr_x * gw, y0 - gh, x0 + gw, y0 - gh, color=NEG, sw=2))
    
    # Highlight max gap at x = 0.48 (index 2: empirical height 3/5 = 0.6, ideal line is 0.48)
    gap_x = x0 + 0.48 * gw
    gap_y_emp = y0 - (3.0 / 5.0) * gh
    gap_y_ideal = y0 - 0.48 * gh
    
    frags.append(line(gap_x, gap_y_emp, gap_x, gap_y_ideal, color=POS, sw=3))
    frags.append(arrow(gap_x, gap_y_emp, gap_x, gap_y_ideal, color=POS, sw=2))
    frags.append(arrow(gap_x, gap_y_ideal, gap_x, gap_y_emp, color=POS, sw=2))
    
    frags.append(textbox(gap_x + 90, (gap_y_emp + gap_y_ideal) / 2, "D*N = max |F_N(x) − x|", size=12, bold=True, fill="#fdecea", stroke=POS)[0])
    
    render(path, w, h, *frags)
    print("Generated:", path)

def make_fig_qmc(out_dir):
    w, h = 800, 360
    path = os.path.join(out_dir, 'fig-qmc-vs-mc.svg')
    
    frags = []
    frags.append(text(w / 2, 25, "2D вибірка для інтегрування: Стандартний Монте-Карло vs Квазі-Монте-Карло", size=16, bold=True))
    
    # Left Box: Standard Monte Carlo (Pseudo-random)
    cx1, cy1, size = 200, 190, 220
    x1_min, y1_min = cx1 - size / 2, cy1 - size / 2
    frags.append(rect(x1_min, y1_min, size, size, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(textbox(cx1, y1_min - 22, "А. Випадкова вибірка (Псевдовипадкові числа)\nПохибка O(N⁻¹/²), є кластери та порожнечі", size=12, fill="#fdecea", stroke=POS)[0])
    
    # Pseudo-random pseudo-deterministic generator seed
    rnd_state = 123456789
    def pseudo_rnd():
        nonlocal rnd_state
        rnd_state = (rnd_state * 1103515245 + 12345) & 0x7fffffff
        return rnd_state / 2147483648.0
        
    for _ in range(60):
        rx = x1_min + pseudo_rnd() * size
        ry = y1_min + pseudo_rnd() * size
        frags.append(circle(rx, ry, 3, fill=POS, stroke=INK, sw=0.8))
        
    # Right Box: Low-Discrepancy Quasi-Monte Carlo (Halton / Sobol style grid-relaxed)
    cx2, cy2 = 600, 190
    x2_min, y2_min = cx2 - size / 2, cy2 - size / 2
    frags.append(rect(x2_min, y2_min, size, size, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(textbox(cx2, y2_min - 22, "Б. Низькодискрепантна вибірка (Квазі-Монте-Карло)\nПохибка майже O(N⁻¹), рівномірне покриття", size=12, fill="#eafaf1", stroke=FIELD)[0])
    
    # Halton sequence (base 2, base 3) for 60 points
    def van_der_corput(n, base):
        q = 0.0
        bk = 1.0 / base
        while n > 0:
            q += (n % base) * bk
            n //= base
            bk /= base
        return q
        
    for i in range(1, 61):
        hx = x2_min + van_der_corput(i, 2) * size
        hy = y2_min + van_der_corput(i, 3) * size
        frags.append(circle(hx, hy, 3, fill=FIELD, stroke=INK, sw=0.8))
        
    render(path, w, h, *frags)
    print("Generated:", path)

def main():
    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)
    
    make_fig_concept(out_dir)
    make_fig_weyl_vectors(out_dir)
    make_fig_discrepancy(out_dir)
    make_fig_qmc(out_dir)

if __name__ == '__main__':
    main()

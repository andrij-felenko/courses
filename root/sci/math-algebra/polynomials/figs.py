import os
import sys
import math

# Add scripts directory to path to import svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    text, mtext, rect, line, text_width, fit_font, esc,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_weierstrass_approx():
    """
    Generates SVG showing uniform polynomial approximation of a continuous function.
    Target curve vs polynomial approximations of degree 2 and degree 6, plus epsilon-tube.
    Width: 800, Height: 480
    """
    width, height = 800, 480
    margin_left, margin_right = 70, 50
    margin_top, margin_bottom = 60, 80
    
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    
    def map_x(x):
        return margin_left + (x - (-2.0)) / 4.0 * plot_w
        
    def map_y(y):
        return margin_top + (2.2 - y) / 3.4 * plot_h

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<rect width="100%" height="100%" fill="#ffffff" />')
    
    # Title
    svg.append(text(width/2, 32, "Теорема Вейєрштрасса: рівномірне наближення функції поліномами", size=16, bold=True))
    
    # Grid & Axes
    for y_val in [-1.0, 0.0, 1.0, 2.0]:
        py = map_y(y_val)
        color = "#94a3b8" if y_val == 0 else "#e2e8f0"
        stroke_w = 2 if y_val == 0 else 1
        svg.append(f'<line x1="{margin_left}" y1="{py}" x2="{width - margin_right}" y2="{py}" stroke="{color}" stroke-width="{stroke_w}" />')
        svg.append(text(margin_left - 12, py + 4, f"{y_val:g}", size=12, color="#64748b", anchor="end"))
        
    for x_val in [-2.0, -1.0, 0.0, 1.0, 2.0]:
        px = map_x(x_val)
        color = "#94a3b8" if x_val == 0 else "#e2e8f0"
        stroke_w = 2 if x_val == 0 else 1
        svg.append(f'<line x1="{px}" y1="{margin_top}" x2="{px}" y2="{height - margin_bottom}" stroke="{color}" stroke-width="{stroke_w}" />')
        svg.append(text(px, height - margin_bottom + 22, f"{x_val:g}", size=12, color="#64748b", anchor="middle"))

    # Border around plot area
    svg.append(f'<rect x="{margin_left}" y="{margin_top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#cbd5e1" stroke-width="1.5" />')

    def f_target(x):
        return 1.4 * math.exp(-0.8 * x * x) + 0.4 * math.sin(2.5 * x)

    def p_deg2(x):
        return 1.25 - 0.35 * x * x + 0.45 * x

    def p_deg6(x):
        return (1.38 + 0.98 * x - 1.15 * x**2 - 0.28 * x**3 + 0.22 * x**4 + 0.03 * x**5 - 0.015 * x**6)

    n_pts = 120
    xs = [-2.0 + 4.0 * i / (n_pts - 1) for i in range(n_pts)]
    
    eps = 0.25
    tube_upper = [(map_x(x), map_y(f_target(x) + eps)) for x in xs]
    tube_lower = [(map_x(x), map_y(f_target(x) - eps)) for x in reversed(xs)]
    tube_pts = " ".join([f"{px:.1f},{py:.1f}" for px, py in (tube_upper + tube_lower)])
    svg.append(f'<polygon points="{tube_pts}" fill="#ecfdf5" stroke="none" />')

    def make_path(func):
        pts = [f"{map_x(x):.1f},{map_y(func(x)):.1f}" for x in xs]
        return "M " + " L ".join(pts)

    svg.append(f'<path d="{make_path(p_deg2)}" fill="none" stroke="{NEG}" stroke-width="2" stroke-dasharray="5,4" />')
    svg.append(f'<path d="{make_path(p_deg6)}" fill="none" stroke="{FIELD}" stroke-width="2.5" />')
    svg.append(f'<path d="{make_path(f_target)}" fill="none" stroke="{POS}" stroke-width="2.5" />')

    leg_y = height - margin_bottom + 52
    
    svg.append(f'<line x1="50" y1="{leg_y}" x2="80" y2="{leg_y}" stroke="{POS}" stroke-width="2.5" />')
    svg.append(text(88, leg_y + 4, "Цільова неперервна f(x)", size=12, color=INK, anchor="start"))
    
    svg.append(f'<line x1="285" y1="{leg_y}" x2="315" y2="{leg_y}" stroke="{NEG}" stroke-width="2" stroke-dasharray="5,4" />')
    svg.append(text(323, leg_y + 4, "Поліном P₂(x)", size=12, color=INK, anchor="start"))
    
    svg.append(f'<line x1="470" y1="{leg_y}" x2="500" y2="{leg_y}" stroke="{FIELD}" stroke-width="2.5" />')
    svg.append(text(508, leg_y + 4, "Поліном P₆(x) усередині ε-трубки", size=12, color=INK, anchor="start"))

    svg.append("</svg>")
    return "\n".join(svg)

def generate_polynomial_division():
    """
    Generates SVG showing structure of Euclidean division A(x) = Q(x)*B(x) + R(x).
    Width: 800, Height: 360
    """
    width, height = 800, 360
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<rect width="100%" height="100%" fill="#ffffff" />')
    
    svg.append(text(width/2, 32, "Алгебраїчна структура ділення з остачею: A(x) = Q(x) · B(x) + R(x)", size=16, bold=True))

    svg.append(rect(40, 70, 200, 110, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    svg.append(text(140, 100, "Ділене A(x)", size=15, bold=True, color="#1d4ed8"))
    svg.append(text(140, 126, "Степінь: deg A = n", size=13, color=INK))
    svg.append(text(140, 150, "A(x) = 2x³ - 3x² + 4x - 5", size=12, color="#475569"))

    svg.append(text(260, 130, "=", size=24, bold=True, color=INK))

    svg.append(rect(285, 70, 195, 110, fill="#ecfdf5", stroke="#10b981", sw=1.5, rx=8))
    svg.append(text(382, 100, "Частка Q(x)", size=15, bold=True, color="#047857"))
    svg.append(text(382, 126, "deg Q = deg A - deg B", size=13, color=INK))
    svg.append(text(382, 150, "Q(x) = 2x - 7", size=12, color="#475569"))

    svg.append(text(500, 130, "·", size=26, bold=True, color=INK))

    svg.append(rect(525, 70, 195, 110, fill="#fef3c7", stroke="#f59e0b", sw=1.5, rx=8))
    svg.append(text(622, 100, "Дільник B(x)", size=15, bold=True, color="#b45309"))
    svg.append(text(622, 126, "Степінь: deg B = m", size=13, color=INK))
    svg.append(text(622, 150, "B(x) = x² + 2x - 1", size=12, color="#475569"))

    svg.append(text(382, 215, "+", size=24, bold=True, color=INK))

    svg.append(rect(220, 235, 360, 95, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=8))
    svg.append(text(400, 264, "Остача R(x)", size=15, bold=True, color="#b91c1c"))
    svg.append(text(400, 288, "Ключова умова: deg R < deg B (або R = 0)", size=13, bold=True, color="#991b1b"))
    svg.append(text(400, 312, "R(x) = 20x - 12   (deg R = 1 < deg B = 2)", size=12, color="#475569"))

    svg.append("</svg>")
    return "\n".join(svg)

def generate_complex_roots():
    """
    Generates SVG showing complex conjugate roots on the complex plane for real polynomials.
    Width: 800, Height: 440
    """
    width, height = 800, 440
    cx, cy = 360, 220
    scale = 85
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<rect width="100%" height="100%" fill="#ffffff" />')
    
    svg.append(text(width/2, 30, "Основна теорема алгебри: комплексно спряжені корені многочлена над ℝ", size=16, bold=True))

    # Real axis (Horizontal)
    svg.append(f'<line x1="60" y1="{cy}" x2="680" y2="{cy}" stroke="#64748b" stroke-width="2" />')
    svg.append(f'<polygon points="685,{cy} 673,{cy-5} 673,{cy+5}" fill="#64748b" />')
    svg.append(text(695, cy + 4, "Re", size=14, bold=True, color="#1e293b", anchor="start"))

    # Imaginary axis (Vertical)
    svg.append(f'<line x1="{cx}" y1="360" x2="{cx}" y2="65" stroke="#64748b" stroke-width="2" />')
    svg.append(f'<polygon points="{cx},60 {cx-5},72 {cx+5},72" fill="#64748b" />')
    svg.append(text(cx, 52, "Im", size=14, bold=True, color="#1e293b", anchor="middle"))

    # Ticks on axes
    for val, label in [(-2, "-2"), (-1, "-1"), (1, "1"), (2, "2"), (3, "3")]:
        tx = cx + val * scale
        if 60 <= tx <= 660:
            svg.append(f'<line x1="{tx}" y1="{cy-4}" x2="{tx}" y2="{cy+4}" stroke="#94a3b8" stroke-width="1.5" />')
            svg.append(text(tx, cy + 18, label, size=11, color="#64748b", anchor="middle"))

    for val, label in [(-1, "-i"), (1, "i")]:
        ty = cy - val * scale
        svg.append(f'<line x1="{cx-4}" y1="{ty}" x2="{cx+4}" y2="{ty}" stroke="#94a3b8" stroke-width="1.5" />')
        svg.append(text(cx - 10, ty + 4, label, size=11, color="#64748b", anchor="end"))

    # Real roots on real axis
    r1_x = cx + 1.8 * scale
    svg.append(f'<circle cx="{r1_x}" cy="{cy}" r="6" fill="#10b981" stroke="#047857" stroke-width="1.5" />')
    svg.append(text(r1_x, cy + 34, "x₁ (дійсний корінь)", size=12, bold=True, color="#047857", anchor="middle"))

    # Complex conjugate pair: a = -1.2, b = 1.1 -> (-1.2, 1.1)
    z1_x, z1_y = cx - 1.2 * scale, cy - 1.1 * scale
    z1_conj_y = cy + 1.1 * scale

    # Dashed connection between conjugate pair
    svg.append(f'<line x1="{z1_x}" y1="{z1_y}" x2="{z1_x}" y2="{z1_conj_y}" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4,4" />')

    # Points
    svg.append(f'<circle cx="{z1_x}" cy="{z1_y}" r="6" fill="#ef4444" stroke="#b91c1c" stroke-width="1.5" />')
    svg.append(text(z1_x - 14, z1_y - 6, "z = a + bi", size=13, bold=True, color="#b91c1c", anchor="end"))

    svg.append(f'<circle cx="{z1_x}" cy="{z1_conj_y}" r="6" fill="#ef4444" stroke="#b91c1c" stroke-width="1.5" />')
    svg.append(text(z1_x - 14, z1_conj_y + 14, "z̄ = a - bi", size=13, bold=True, color="#b91c1c", anchor="end"))

    # Quadratic factor label card on the right
    svg.append(rect(480, 80, 280, 110, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    svg.append(text(620, 105, "Добуток спряжених факторів:", size=13, bold=True, color="#991b1b"))
    svg.append(text(620, 130, "(x - z)(x - z̄) = x² - 2ax + (a² + b²)", size=12, color=INK))
    svg.append(text(620, 155, "Незвідний квадратний тричлен над ℝ", size=11, color="#475569"))
    svg.append(text(620, 173, "Дискримінант Δ = -4b² < 0", size=11, bold=True, color="#b91c1c"))

    # Explanation banner at bottom
    svg.append(rect(60, 375, 680, 48, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    svg.append(text(400, 404, "Кожен многочлен P(x) ∈ ℝ[x] розкладається суто на лінійні (x - r) та незвідні квадратні фактори", size=12, bold=True, color="#1e293b", anchor="middle"))

    svg.append("</svg>")
    return "\n".join(svg)

def generate_bezier_construction():
    """
    Generates SVG showing cubic Bézier curve as polynomial parametric curve.
    Width: 800, Height: 440
    """
    width, height = 800, 440
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<rect width="100%" height="100%" fill="#ffffff" />')
    
    svg.append(text(width/2, 32, "Поліноміальні параметричні криві: кубічна крива Безьє B(t)", size=16, bold=True))

    p0 = (100, 340)
    p1 = (220, 100)
    p2 = (540, 90)
    p3 = (700, 330)

    svg.append(f'<polyline points="{p0[0]},{p0[1]} {p1[0]},{p1[1]} {p2[0]},{p2[1]} {p3[0]},{p3[1]}" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="6,4" />')

    svg.append(f'<path d="M {p0[0]} {p0[1]} C {p1[0]} {p1[1]}, {p2[0]} {p2[1]}, {p3[0]} {p3[1]}" fill="none" stroke="#2563eb" stroke-width="3.5" />')

    t = 0.5
    def lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    
    q0 = lerp(p0, p1, t)
    q1 = lerp(p1, p2, t)
    q2 = lerp(p2, p3, t)
    
    r0 = lerp(q0, q1, t)
    r1 = lerp(q1, q2, t)
    
    pt = lerp(r0, r1, t)

    svg.append(f'<line x1="{q0[0]}" y1="{q0[1]}" x2="{q1[0]}" y2="{q1[1]}" stroke="#10b981" stroke-width="1.5" />')
    svg.append(f'<line x1="{q1[0]}" y1="{q1[1]}" x2="{q2[0]}" y2="{q2[1]}" stroke="#10b981" stroke-width="1.5" />')

    svg.append(f'<line x1="{r0[0]}" y1="{r0[1]}" x2="{r1[0]}" y2="{r1[1]}" stroke="#f59e0b" stroke-width="2" />')

    svg.append(f'<circle cx="{pt[0]}" cy="{pt[1]}" r="6" fill="#ef4444" stroke="#b91c1c" stroke-width="2" />')
    svg.append(text(pt[0], pt[1] - 14, "B(t = 0.5)", size=13, bold=True, color="#b91c1c", anchor="middle"))

    pts = [(p0, "P₀ (початок)", "middle", 22), 
           (p1, "P₁ (напрямок)", "middle", -14), 
           (p2, "P₂ (напрямок)", "middle", -14), 
           (p3, "P₃ (кінець)", "middle", 22)]
    
    for (px, py), label, anc, dy in pts:
        svg.append(f'<circle cx="{px}" cy="{py}" r="5" fill="#1e293b" stroke="#ffffff" stroke-width="1.5" />')
        svg.append(text(px, py + dy, label, size=12, bold=True, color="#1e293b", anchor=anc))

    svg.append(rect(140, 365, 520, 58, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    svg.append(text(400, 388, "B(t) = (1-t)³ P₀ + 3(1-t)²t P₁ + 3(1-t)t² P₂ + t³ P₃", size=13, bold=True, color="#1d4ed8", anchor="middle"))
    svg.append(text(400, 408, "Базис Бернштейна bᵢ,₃(t) гарантує гладкість кривої при t ∈ [0, 1]", size=11, color="#475569", anchor="middle"))

    svg.append("</svg>")
    return "\n".join(svg)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    ensure_dir(img_dir)
    
    figs = [
        ("polynomial-approximation-weierstrass.svg", generate_weierstrass_approx),
        ("polynomial-long-division.svg", generate_polynomial_division),
        ("complex-roots-conjugate.svg", generate_complex_roots),
        ("bezier-spline-construction.svg", generate_bezier_construction),
    ]
    
    for filename, func in figs:
        filepath = os.path.join(img_dir, filename)
        content = func()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated: {filepath}")

if __name__ == "__main__":
    main()

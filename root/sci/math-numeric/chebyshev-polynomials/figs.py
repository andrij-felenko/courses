import os
import math

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_chebyshev_first_kind():
    """
    Generates SVG showing T_1(x), T_2(x), T_3(x), T_4(x) on [-1, 1].
    Width: 800, Height: 520
    """
    width, height = 800, 520
    margin_left, margin_right = 70, 50
    margin_top, margin_bottom = 55, 85
    
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    
    def map_x(x):
        return margin_left + (x - (-1.0)) / 2.0 * plot_w
        
    def map_y(y):
        return margin_top + (1.2 - y) / 2.4 * plot_h

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<rect width="100%" height="100%" fill="#ffffff" />')
    
    # Title
    svg.append(f'<text x="{width/2}" y="30" font-family="sans-serif" font-size="18" font-weight="bold" fill="#1e293b" text-anchor="middle">Поліноми Чебишова першого роду T_n(x)</text>')
    
    # Grid & Axes
    for y_val in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        py = map_y(y_val)
        color = "#94a3b8" if y_val == 0 else "#e2e8f0"
        stroke_w = 2 if y_val == 0 else 1
        dash = ' stroke-dasharray="4,4"' if y_val in [-1.0, 1.0] else ''
        svg.append(f'<line x1="{margin_left}" y1="{py}" x2="{width - margin_right}" y2="{py}" stroke="{color}" stroke-width="{stroke_w}"{dash} />')
        svg.append(f'<text x="{margin_left - 12}" y="{py + 4}" font-family="sans-serif" font-size="13" fill="#64748b" text-anchor="end">{y_val:g}</text>')
        
    for x_val in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        px = map_x(x_val)
        color = "#94a3b8" if x_val == 0 else "#e2e8f0"
        stroke_w = 2 if x_val == 0 else 1
        svg.append(f'<line x1="{px}" y1="{margin_top}" x2="{px}" y2="{height - margin_bottom}" stroke="{color}" stroke-width="{stroke_w}" />')
        svg.append(f'<text x="{px}" y="{height - margin_bottom + 22}" font-family="sans-serif" font-size="13" fill="#64748b" text-anchor="middle">{x_val:g}</text>')

    # Border around plot area
    svg.append(f'<rect x="{margin_left}" y="{margin_top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#cbd5e1" stroke-width="1.5" />')

    # Functions to plot
    def T1(x): return x
    def T2(x): return 2*x**2 - 1
    def T3(x): return 4*x**3 - 3*x
    def T4(x): return 8*x**4 - 8*x**2 + 1

    funcs = [
        (T1, "T₁(x) = x", "#2563eb"),
        (T2, "T₂(x) = 2x² - 1", "#dc2626"),
        (T3, "T₃(x) = 4x³ - 3x", "#059669"),
        (T4, "T₄(x) = 8x⁴ - 8x² + 1", "#7c3aed"),
    ]

    steps = 300
    for fn, label, color in funcs:
        pts = []
        for i in range(steps + 1):
            x = -1.0 + 2.0 * i / steps
            y = fn(x)
            pts.append(f"{map_x(x):.2f},{map_y(y):.2f}")
        polyline_str = " ".join(pts)
        svg.append(f'<polyline points="{polyline_str}" fill="none" stroke="{color}" stroke-width="2.5" />')

    # Legend at bottom below x-axis labels
    legend_y = height - 25
    legend_positions = [75, 235, 415, 605]
    
    for idx, (fn, label, color) in enumerate(funcs):
        lx = legend_positions[idx]
        svg.append(f'<line x1="{lx}" y1="{legend_y - 4}" x2="{lx + 30}" y2="{legend_y - 4}" stroke="{color}" stroke-width="2.5" />')
        svg.append(f'<text x="{lx + 38}" y="{legend_y}" font-family="sans-serif" font-size="13" font-weight="600" fill="#334155">{label}</text>')

    svg.append('</svg>')
    return "\n".join(svg)


def generate_chebyshev_nodes_projection():
    """
    Generates SVG showing geometric projection of Chebyshev nodes from a semi-circle onto [-1, 1].
    Width: 800, Height: 480
    """
    width, height = 800, 480
    cx, cy = 400, 310
    radius = 210
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<rect width="100%" height="100%" fill="#ffffff" />')
    
    # Title
    svg.append(f'<text x="{width/2}" y="32" font-family="sans-serif" font-size="18" font-weight="bold" fill="#1e293b" text-anchor="middle">Геометрична проєкція вузлів Чебишова (n = 5)</text>')
    
    # Subtitle
    svg.append(f'<text x="{width/2}" y="56" font-family="sans-serif" font-size="13" fill="#64748b" text-anchor="middle">Рівномірний розподіл точок уздовж дуги півкола дає згущення вузлів на краях відрізка [-1, 1]</text>')

    # Upper semi-circle
    path_d = f"M {cx - radius} {cy} A {radius} {radius} 0 0 1 {cx + radius} {cy}"
    svg.append(f'<path d="{path_d}" fill="#f8fafc" stroke="#94a3b8" stroke-width="2" stroke-dasharray="6,6" />')
    
    # Base line [-1, 1]
    svg.append(f'<line x1="{cx - radius - 30}" y1="{cy}" x2="{cx + radius + 30}" y2="{cy}" stroke="#1e293b" stroke-width="2.5" />')

    # Tick marks & labels for -1, 0, 1
    svg.append(f'<line x1="{cx - radius}" y1="{cy - 8}" x2="{cx - radius}" y2="{cy + 8}" stroke="#1e293b" stroke-width="2" />')
    svg.append(f'<text x="{cx - radius}" y="{cy + 28}" font-family="sans-serif" font-size="14" font-weight="bold" fill="#0f172a" text-anchor="middle">-1</text>')
    
    svg.append(f'<line x1="{cx}" y1="{cy - 8}" x2="{cx}" y2="{cy + 8}" stroke="#1e293b" stroke-width="2" />')
    svg.append(f'<text x="{cx}" y="{cy + 28}" font-family="sans-serif" font-size="14" font-weight="bold" fill="#0f172a" text-anchor="middle">0</text>')

    svg.append(f'<line x1="{cx + radius}" y1="{cy - 8}" x2="{cx + radius}" y2="{cy + 8}" stroke="#1e293b" stroke-width="2" />')
    svg.append(f'<text x="{cx + radius}" y="{cy + 28}" font-family="sans-serif" font-size="14" font-weight="bold" fill="#0f172a" text-anchor="middle">1</text>')

    # Chebyshev nodes for n = 5
    n = 5
    colors = ["#dc2626", "#2563eb", "#059669", "#7c3aed", "#d97706"]
    
    for k in range(1, n + 1):
        angle_rad = (2 * k - 1) * math.pi / (2 * n)
        px = cx + radius * math.cos(angle_rad)
        py = cy - radius * math.sin(angle_rad)
        
        bx = px
        by = cy
        
        color = colors[(k-1) % len(colors)]
        
        # Projection line (vertical)
        svg.append(f'<line x1="{px:.2f}" y1="{py:.2f}" x2="{bx:.2f}" y2="{by:.2f}" stroke="{color}" stroke-width="1.5" stroke-dasharray="4,4" />')
        
        # Radius line from center to circle point
        svg.append(f'<line x1="{cx}" y1="{cy}" x2="{px:.2f}" y2="{py:.2f}" stroke="#cbd5e1" stroke-width="1" />')
        
        # Node on circle
        svg.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="5" fill="{color}" />')
        
        # Node on baseline
        svg.append(f'<circle cx="{bx:.2f}" cy="{by:.2f}" r="6" fill="{color}" stroke="#ffffff" stroke-width="1.5" />')
        
        # Label x_k below baseline
        svg.append(f'<text x="{bx:.2f}" y="{cy + 54}" font-family="sans-serif" font-size="13" font-weight="600" fill="{color}" text-anchor="middle">x_{k}</text>')

    svg.append('</svg>')
    return "\n".join(svg)


def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    ensure_dir(img_dir)
    
    f1_path = os.path.join(img_dir, "chebyshev-first-kind.svg")
    with open(f1_path, "w", encoding="utf-8") as f:
        f.write(generate_chebyshev_first_kind())
    print(f"Generated {f1_path}")
    
    f2_path = os.path.join(img_dir, "chebyshev-nodes-projection.svg")
    with open(f2_path, "w", encoding="utf-8") as f:
        f.write(generate_chebyshev_nodes_projection())
    print(f"Generated {f2_path}")

if __name__ == "__main__":
    main()

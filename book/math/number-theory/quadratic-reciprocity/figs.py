import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts"))
try:
    import svgkit
except ImportError:
    svgkit = None

def generate_svg():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig-quadratic-reciprocity.svg")
    
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="-50 0 600 400" width="600" height="400">
    <!-- Тло -->
    <rect x="-50" y="0" width="100%" height="100%" fill="#fafafa" />
    <text x="250" y="30" font-family="sans-serif" font-size="20" font-weight="bold" text-anchor="middle" fill="#333">Геометрія Ейзенштейна для квадратичного закону взаємності</text>
    
    <!-- Осі -->
    <line x1="50" y1="350" x2="450" y2="350" stroke="#000" stroke-width="2" />
    <line x1="50" y1="350" x2="50" y2="50" stroke="#000" stroke-width="2" />
    
    <!-- Підписи осей -->
    <text x="460" y="355" font-family="sans-serif" font-size="16">x</text>
    <text x="45" y="40" font-family="sans-serif" font-size="16">y</text>
    
    <!-- Прямокутник для p/2 та q/2 -->
    <!-- Нехай p=11, q=7. p/2 = 5.5, q/2 = 3.5. -->
    <rect x="50" y="100" width="300" height="250" fill="none" stroke="#666" stroke-width="2" stroke-dasharray="5,5" />
    
    <!-- Діагональ -->
    <line x1="50" y1="350" x2="350" y2="100" stroke="#ff8c00" stroke-width="3" />
    
    <!-- Точки сітки та розфарбування -->
    <!-- p-1/2 = 5 точок по X, q-1/2 = 3 точки по Y -->
    <polygon points="50,350 350,350 350,100" fill="rgba(100,200,255,0.2)" />
    <polygon points="50,350 50,100 350,100" fill="rgba(255,100,100,0.2)" />
    
    <text x="250" y="280" font-family="sans-serif" font-size="14" fill="#006699" text-anchor="middle">m точок під діагоналлю (q/p)</text>
    <text x="150" y="160" font-family="sans-serif" font-size="14" fill="#990000" text-anchor="middle">n точок над діагоналлю (p/q)</text>
    
    <!-- Вузол p/2, q/2 -->
    <circle cx="350" cy="100" r="4" fill="#000" />
    <text x="360" y="95" font-family="sans-serif" font-size="14">A (p/2, q/2)</text>
    <text x="350" y="370" font-family="sans-serif" font-size="14" text-anchor="middle">p/2</text>
    <text x="25" y="105" font-family="sans-serif" font-size="14">q/2</text>
    
    <!-- Точки (приблизно) -->
    <circle cx="110" cy="270" r="3" fill="#333" />
    <circle cx="170" cy="270" r="3" fill="#333" />
    <circle cx="230" cy="270" r="3" fill="#333" />
    <circle cx="290" cy="270" r="3" fill="#333" />
    
    <circle cx="110" cy="190" r="3" fill="#333" />
    <circle cx="170" cy="190" r="3" fill="#333" />
    <circle cx="230" cy="190" r="3" fill="#333" />
    
    <text x="250" y="390" font-family="sans-serif" font-size="12" fill="#555" text-anchor="middle">Загальна кількість точок = ((p-1)/2) * ((q-1)/2) = m + n</text>
</svg>"""
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_svg()

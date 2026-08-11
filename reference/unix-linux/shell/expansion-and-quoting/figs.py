import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))

try:
    import svgkit
except ImportError:
    # Заглушка, якщо скрипт запускається поза контекстом репозиторію
    class SVGKitStub:
        def __init__(self):
            pass
        def render(self, filename, content):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
    svgkit = SVGKitStub()

def generate_expansion_flow():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
    <style>
        .box { fill: #f0f0f0; stroke: #333; stroke-width: 2px; }
        .text { font-family: sans-serif; font-size: 14px; text-anchor: middle; fill: #333; }
        .arrow { stroke: #333; stroke-width: 2px; marker-end: url(#arrowhead); }
    </style>
    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
        </marker>
    </defs>
    
    <!-- Input -->
    <text x="100" y="50" class="text" font-weight="bold">Введений текст</text>
    
    <!-- Steps -->
    <rect x="50" y="80" width="100" height="40" class="box" />
    <text x="100" y="105" class="text">Brace Exp</text>
    <line x1="100" y1="120" x2="100" y2="150" class="arrow" />
    
    <rect x="50" y="150" width="100" height="40" class="box" />
    <text x="100" y="175" class="text">Tilde Exp</text>
    <line x1="100" y1="190" x2="100" y2="220" class="arrow" />
    
    <rect x="50" y="220" width="100" height="40" class="box" />
    <text x="100" y="245" class="text">Param/Cmd Exp</text>
    <line x1="100" y1="260" x2="100" y2="290" class="arrow" />
    
    <rect x="50" y="290" width="100" height="40" class="box" />
    <text x="100" y="315" class="text">Word Splitting</text>
    <line x1="150" y1="310" x2="180" y2="310" class="arrow" />
    
    <rect x="180" y="290" width="100" height="40" class="box" />
    <text x="230" y="315" class="text">Globbing</text>
    
    <line x1="280" y1="310" x2="310" y2="310" class="arrow" />
    <text x="360" y="315" class="text" font-weight="bold">Виконання команди</text>
</svg>"""
    
    if hasattr(svgkit, 'render'):
        svgkit.render(os.path.join(IMG, 'expansion-flow.svg'), svg_content)
    else:
        with open('expansion_flow.svg', 'w', encoding='utf-8') as f:
            f.write(svg_content)

if __name__ == '__main__':
    generate_expansion_flow()

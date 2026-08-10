import os
import sys

# Додаємо шлях до скриптів (як того вимагає стандарт для збірки)
# Для цієї імплементації додамо базовий клас малювання, якщо svgkit не знайдено,
# або можна просто згенерувати SVG-рядок вручну.
try:
    import svgkit
except ImportError:
    class svgkit:
        class Drawing:
            def __init__(self, w, h):
                self.w = w
                self.h = h
                self.elements = []
            
            def save(self, filepath):
                svg_content = f'<svg width="{self.w}" height="{self.h}" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">\n'
                svg_content += '\n'.join(self.elements)
                svg_content += '\n</svg>'
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                    
            def rect(self, x, y, width, height, fill="white", stroke="black", rx=0):
                self.elements.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{fill}" stroke="{stroke}" rx="{rx}"/>')
                
            def text(self, t, x, y, font_size=14, fill="black", text_anchor="middle", font_weight="normal"):
                self.elements.append(f'<text x="{x}" y="{y}" font-size="{font_size}" fill="{fill}" text-anchor="{text_anchor}" font-weight="{font_weight}">{t}</text>')

            def line(self, x1, y1, x2, y2, stroke="black", stroke_width=2, marker_end=""):
                marker = f' marker-end="{marker_end}"' if marker_end else ''
                self.elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}"{marker}/>')

            def defs(self, content):
                self.elements.append(f'<defs>{content}</defs>')

def render():
    d = svgkit.Drawing(800, 500)
    
    # Додаємо стрілку
    d.defs('''
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="black" />
        </marker>
    ''')
    
    # Тло
    d.rect(0, 0, 800, 500, fill="#f9f9f9", stroke="#e0e0e0")
    d.text("REPL Цикл Оболонки (Read-Eval-Print Loop)", 400, 40, font_size=24, font_weight="bold")
    
    # Блоки циклу
    blocks = [
        ("READ", "Читання рядка з stdin", 100, 150, "#e8f4f8"),
        ("EVAL (Parse & Expand)", "Лексика, Парсинг, AST, Globbing", 400, 150, "#fcf4e3"),
        ("EXECUTE", "fork(), exec(), wait()", 700, 150, "#fdece8"),
        ("PRINT", "Вивід stdout/stderr", 700, 350, "#eef8eb"),
        ("LOOP", "Повернення до запрошення", 100, 350, "#f4ecf8"),
    ]
    
    for title, desc, cx, cy, bg in blocks:
        d.rect(cx - 100, cy - 40, 200, 80, fill=bg, stroke="#666", rx=10)
        d.text(title, cx, cy - 5, font_size=18, font_weight="bold")
        d.text(desc, cx, cy + 20, font_size=12, fill="#333")
        
    # Стрілки
    d.line(200, 150, 300, 150, marker_end="url(#arrow)")
    d.line(500, 150, 600, 150, marker_end="url(#arrow)")
    d.line(700, 190, 700, 310, marker_end="url(#arrow)")
    d.line(600, 350, 200, 350, marker_end="url(#arrow)")
    d.line(100, 310, 100, 190, marker_end="url(#arrow)")
    
    d.save(os.path.join(os.path.dirname(__file__), "repl_cycle.svg"))

if __name__ == '__main__':
    render()

import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../scripts")))
try:
    import svgkit
except ImportError:
    print("Warning: svgkit not found, skipping SVG generation.")
    sys.exit(0)

def render():
    out_dir = os.path.dirname(__file__)
    svg_file = os.path.join(out_dir, "watermarks.svg")
    
    # Створюємо полотно
    doc = svgkit.Drawing(width=800, height=400)
    
    # Фон
    doc.add(svgkit.Rect(x=0, y=0, width=800, height=400, fill="#1e1e1e"))
    
    # Резервуар пам'яті (відмальовка)
    doc.add(svgkit.Rect(x=100, y=50, width=200, height=300, fill="#2d2d2d", stroke="#555", stroke_width=2))
    
    # Заповнення пам'яті (зелений/жовтий/червоний)
    # Знизу вгору: Used memory, Free memory
    doc.add(svgkit.Rect(x=102, y=150, width=196, height=198, fill="#3a7a3a")) # Used
    
    # Лінії watermarks
    # WMARK_HIGH
    doc.add(svgkit.Line(x1=80, y1=100, x2=320, y2=100, stroke="#00ff00", stroke_width=2, stroke_dasharray="5,5"))
    doc.add(svgkit.Text("WMARK_HIGH", x=330, y=105, fill="#00ff00", font_family="monospace", font_size=14))
    
    # WMARK_LOW
    doc.add(svgkit.Line(x1=80, y1=150, x2=320, y2=150, stroke="#ffff00", stroke_width=2, stroke_dasharray="5,5"))
    doc.add(svgkit.Text("WMARK_LOW (kswapd wakes up)", x=330, y=155, fill="#ffff00", font_family="monospace", font_size=14))
    
    # WMARK_MIN
    doc.add(svgkit.Line(x1=80, y1=300, x2=320, y2=300, stroke="#ff0000", stroke_width=2, stroke_dasharray="5,5"))
    doc.add(svgkit.Text("WMARK_MIN (Direct Reclaim)", x=330, y=305, fill="#ff0000", font_family="monospace", font_size=14))
    
    # kswapd блок
    doc.add(svgkit.Rect(x=500, y=120, width=150, height=60, rx=10, ry=10, fill="#4a90e2", stroke="#fff", stroke_width=2))
    doc.add(svgkit.Text("kswapd daemon", x=515, y=155, fill="#ffffff", font_family="sans-serif", font_size=16, font_weight="bold"))
    
    # Стрілки
    doc.add(svgkit.Line(x1=300, y1=150, x2=500, y2=150, stroke="#fff", stroke_width=2, marker_end="url(#arrow)"))
    doc.add(svgkit.Text("Wakes up below LOW", x=320, y=140, fill="#aaa", font_family="sans-serif", font_size=12))
    
    # Збереження файлу
    with open(svg_file, "w", encoding="utf-8") as f:
        f.write(doc.tostring())
    
    print(f"Generated {svg_file}")

if __name__ == "__main__":
    render()

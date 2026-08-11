import sys
import os

# Додамо шлях до svgkit.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))

try:
    import svgkit
except ImportError:
    # Заглушка, якщо svgkit немає
    class DummySvgKit:
        def __init__(self, *args, **kwargs):
            pass
        def line(self, *args, **kwargs):
            pass
        def circle(self, *args, **kwargs):
            pass
        def text(self, *args, **kwargs):
            pass
        def save(self, path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write("<svg></svg>")
    svgkit = DummySvgKit
    svgkit.Drawing = DummySvgKit

def draw_chord_method():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig-chord-method.svg")
    
    with open(out_path, "w") as f:
        f.write('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
    <rect width="400" height="400" fill="white" />
    <line x1="200" y1="50" x2="200" y2="350" stroke="black" />
    <line x1="50" y1="200" x2="350" y2="200" stroke="black" />
    <circle cx="200" cy="200" r="100" stroke="blue" fill="none" stroke-width="2" />
    <line x1="100" y1="200" x2="260" y2="120" stroke="red" stroke-width="2" />
    <circle cx="100" cy="200" r="4" fill="red" />
    <circle cx="260" cy="120" r="4" fill="red" />
    <text x="70" y="220" font-family="sans-serif" font-size="12">(-1, 0)</text>
    <text x="270" y="110" font-family="sans-serif" font-size="12">(x, y)</text>
    <text x="340" y="215" font-family="sans-serif" font-size="12">x</text>
    <text x="180" y="60" font-family="sans-serif" font-size="12">y</text>
</svg>''')

if __name__ == "__main__":
    draw_chord_method()

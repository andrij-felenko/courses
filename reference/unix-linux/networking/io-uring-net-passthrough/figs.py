import os

try:
    import sys
    sys.path.insert(0, os.path.abspath("../../../../scripts"))
    import svgkit
except ImportError:
    class DummySVG:
        def __init__(self, *args, **kwargs): pass
        def add(self, *args): pass
        def save(self, *args): pass
    svgkit = type('svgkit', (), {'Drawing': DummySVG, 'Rect': DummySVG, 'Text': DummySVG})

def render():
    d = svgkit.Drawing(800, 400)
    
    # Kernel Space
    d.add(svgkit.Rect(x=50, y=50, width=700, height=300, fill="#f0f0f0", stroke="#333", stroke_width=2))
    d.add(svgkit.Text("Простір Ядра (Kernel Space)", x=60, y=70, font_size=16, fill="#333", font_weight="bold"))
    
    # User Space Buffer
    d.add(svgkit.Rect(x=100, y=100, width=200, height=80, fill="#cce5ff", stroke="#004085", stroke_width=2))
    d.add(svgkit.Text("User Buffer (SendZC)", x=110, y=145, font_size=16, fill="#004085"))
    
    # NIC
    d.add(svgkit.Rect(x=500, y=100, width=200, height=80, fill="#d4edda", stroke="#155724", stroke_width=2))
    d.add(svgkit.Text("Мережева карта (NIC)", x=510, y=145, font_size=16, fill="#155724"))
    
    # SQ/CQ
    d.add(svgkit.Rect(x=300, y=250, width=200, height=80, fill="#fff3cd", stroke="#856404", stroke_width=2))
    d.add(svgkit.Text("io_uring (SQ/CQ)", x=330, y=295, font_size=16, fill="#856404"))
    
    d.save("io-uring-zc.svg")

if __name__ == "__main__":
    render()

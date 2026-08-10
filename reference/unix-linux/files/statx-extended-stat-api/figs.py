import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
try:
    import svgkit
except ImportError:
    # Fallback if svgkit isn't found
    class DummyDoc:
        def __init__(self, **kwargs):
            self.elements = []
        def add(self, *args):
            pass
        def rect(self, **kwargs): return ''
        def text(self, text, **kwargs): return ''
        def line(self, **kwargs): return ''
        def save_svg(self, path):
            with open(path, 'w') as f:
                f.write('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400"><rect width="800" height="400" fill="#f0f0f0"/><text x="400" y="200" text-anchor="middle">SVG Placeholder for statx evolution</text></svg>')
    svgkit = type('svgkit', (), {'Drawing': DummyDoc})

def render():
    doc = svgkit.Drawing(width=800, height=400)
    doc.add(doc.rect(x=50, y=100, width=200, height=150, rx=5, ry=5, fill="#e2f0d9", stroke="#333", stroke_width=2))
    doc.add(doc.text("struct stat", x=150, y=130, text_anchor="middle", font_size="16px", font_weight="bold", fill="#333"))
    doc.add(doc.text("st_mode", x=70, y=160, font_size="14px", fill="#333"))
    doc.add(doc.text("st_size", x=70, y=180, font_size="14px", fill="#333"))
    doc.add(doc.text("st_mtime", x=70, y=200, font_size="14px", fill="#333"))
    doc.add(doc.text("...", x=70, y=220, font_size="14px", fill="#333"))
    doc.add(doc.line(x1=270, y1=175, x2=370, y2=175, stroke="#333", stroke_width=2))
    doc.add(doc.text("evolves to", x=320, y=165, text_anchor="middle", font_size="14px", fill="#666", font_style="italic"))
    doc.add(doc.rect(x=400, y=50, width=350, height=300, rx=5, ry=5, fill="#deebf7", stroke="#333", stroke_width=2))
    doc.add(doc.text("struct statx", x=575, y=80, text_anchor="middle", font_size="16px", font_weight="bold", fill="#333"))
    doc.add(doc.text("stx_mask (valid fields)", x=420, y=110, font_size="14px", fill="#d9534f", font_weight="bold"))
    doc.add(doc.text("stx_mode, stx_size, stx_mtime", x=420, y=140, font_size="14px", fill="#333"))
    doc.add(doc.text("stx_btime (creation time) [NEW]", x=420, y=170, font_size="14px", fill="#5cb85c", font_weight="bold"))
    doc.add(doc.text("stx_attributes (compressed, etc) [NEW]", x=420, y=200, font_size="14px", fill="#5cb85c", font_weight="bold"))
    doc.add(doc.text("stx_attributes_mask", x=420, y=230, font_size="14px", fill="#333"))
    doc.save_svg(os.path.join(os.path.dirname(__file__), "statx_evolution.svg"))

if __name__ == '__main__':
    render()

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
# Fallback simple svg builder if svgkit not present
class SimpleSVG:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.elements = []
    def rect(self, **kwargs):
        attrs = " ".join([f'{k}="{v}"' for k, v in kwargs.items()])
        self.elements.append(f'<rect {attrs} />')
    def text(self, text, **kwargs):
        attrs = " ".join([f'{k}="{v}"' for k, v in kwargs.items() if k != 'text'])
        self.elements.append(f'<text {attrs}>{text}</text>')
    def line(self, **kwargs):
        attrs = " ".join([f'{k}="{v}"' for k, v in kwargs.items()])
        self.elements.append(f'<line {attrs} />')
    def render(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}">\n')
            f.write("\n".join(self.elements))
            f.write('\n</svg>')

def draw_vhost_net_arch():
    d = SimpleSVG(800, 500)
    d.rect(x=50, y=50, width=300, height=400, fill="#f0f0f0", stroke="#333", stroke_width=2)
    d.text("Guest OS", x=150, y=80, font_size=20, font_family="sans-serif", font_weight="bold")
    d.rect(x=100, y=120, width=200, height=80, fill="#cce5ff", stroke="#004085", stroke_width=2)
    d.text("virtio-net Driver", x=125, y=165, font_size=18, font_family="sans-serif")
    
    d.rect(x=450, y=50, width=300, height=400, fill="#f0f0f0", stroke="#333", stroke_width=2)
    d.text("Host OS", x=560, y=80, font_size=20, font_family="sans-serif", font_weight="bold")
    
    d.rect(x=500, y=120, width=200, height=80, fill="#d4edda", stroke="#155724", stroke_width=2)
    d.text("QEMU (Control)", x=530, y=165, font_size=18, font_family="sans-serif")
    
    d.rect(x=500, y=240, width=200, height=80, fill="#f8d7da", stroke="#721c24", stroke_width=2)
    d.text("vhost-net (Data)", x=535, y=285, font_size=18, font_family="sans-serif")
    
    d.rect(x=320, y=150, width=160, height=120, fill="#e2e3e5", stroke="#383d41", stroke_width=2, stroke_dasharray="5,5")
    d.text("vring", x=375, y=210, font_size=16, font_family="sans-serif", font_weight="bold")
    d.text("(Shared Memory)", x=335, y=235, font_size=14, font_family="sans-serif")
    
    d.line(x1=200, y1=200, x2=320, y2=200, stroke="#333", stroke_width=2, stroke_dasharray="4,4")
    d.line(x1=480, y1=280, x2=400, y2=270, stroke="#333", stroke_width=2, stroke_dasharray="4,4")
    
    d.render(os.path.join(script_dir, "vhost-net-arch.svg"))

def render():
    draw_vhost_net_arch()

if __name__ == "__main__":
    render()

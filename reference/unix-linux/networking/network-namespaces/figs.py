import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../scripts"))
try:
    import svgkit
except ImportError:
    # A dummy version for testing if svgkit isn't available
    class dummy_svgkit:
        class Drawing:
            def __init__(self, w, h): self.w, self.h = w, h; self.elements = []
            def add(self, e): self.elements.append(e)
            def save(self, name):
                with open(name, "w") as f:
                    f.write(f'<svg width="{self.w}" height="{self.h}"></svg>')
        def Rect(self, **kwargs): return "rect"
        def Text(self, **kwargs): return "text"
        def Line(self, **kwargs): return "line"
    svgkit = dummy_svgkit()

def render():
    dwg = svgkit.Drawing(600, 400)
    # Background for host
    dwg.add(svgkit.Rect(x=10, y=10, width=580, height=380, fill="#f0f0f0", stroke="#333", stroke_width=2))
    dwg.add(svgkit.Text("Host (Global NetNS)", x=20, y=30, font_size=16, font_weight="bold", fill="#333"))
    
    # Bridge
    dwg.add(svgkit.Rect(x=50, y=180, width=500, height=60, fill="#d0e0ff", stroke="#004488", stroke_width=2))
    dwg.add(svgkit.Text("Bridge (br0)", x=60, y=200, font_size=14, font_weight="bold"))
    
    # Red NetNS
    dwg.add(svgkit.Rect(x=50, y=50, width=200, height=100, fill="#ffeeee", stroke="#cc0000", stroke_width=2))
    dwg.add(svgkit.Text("NetNS: red", x=60, y=70, font_size=14, font_weight="bold", fill="#cc0000"))
    dwg.add(svgkit.Rect(x=100, y=100, width=100, height=30, fill="#ffcccc", stroke="#aa0000"))
    dwg.add(svgkit.Text("veth-red", x=120, y=120, font_size=12))
    
    # Blue NetNS
    dwg.add(svgkit.Rect(x=350, y=50, width=200, height=100, fill="#eeeeff", stroke="#0000cc", stroke_width=2))
    dwg.add(svgkit.Text("NetNS: blue", x=360, y=70, font_size=14, font_weight="bold", fill="#0000cc"))
    dwg.add(svgkit.Rect(x=400, y=100, width=100, height=30, fill="#ccccff", stroke="#0000aa"))
    dwg.add(svgkit.Text("veth-blue", x=420, y=120, font_size=12))
    
    # Veth ends on bridge
    dwg.add(svgkit.Rect(x=100, y=210, width=100, height=30, fill="#eeeeee", stroke="#666"))
    dwg.add(svgkit.Text("veth-red-br", x=110, y=230, font_size=12))
    
    dwg.add(svgkit.Rect(x=400, y=210, width=100, height=30, fill="#eeeeee", stroke="#666"))
    dwg.add(svgkit.Text("veth-blue-br", x=410, y=230, font_size=12))
    
    # Connections
    dwg.add(svgkit.Line(start=(150, 130), end=(150, 210), stroke="#333", stroke_width=4, stroke_dasharray="5,5"))
    dwg.add(svgkit.Line(start=(450, 130), end=(450, 210), stroke="#333", stroke_width=4, stroke_dasharray="5,5"))
    
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    dwg.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "netns-diagram.svg"))

if __name__ == "__main__":
    render()

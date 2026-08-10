import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..", "scripts")))
try:
    import svgkit
except ImportError:
    # Fallback mock for the tool if svgkit is not accessible locally
    class svgkit:
        class SVG:
            def __init__(self):
                self.svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">'
            def add_rect(self, x, y, w, h, fill, stroke="black"):
                self.svg += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>'
            def add_text(self, x, y, text, font_size=16):
                self.svg += f'<text x="{x}" y="{y}" font-size="{font_size}" font-family="sans-serif">{text}</text>'
            def add_line(self, x1, y1, x2, y2, stroke="black"):
                self.svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="2"/>'
            def render(self):
                return self.svg + '</svg>'

def render():
    d = svgkit.SVG() if hasattr(svgkit, 'SVG') else svgkit.Drawing(800, 400)
    
    # Simple architecture diagram
    d.add_rect(100, 50, 200, 100, "#d1e7dd")
    d.add_text(150, 100, "Production Kernel")
    
    d.add_rect(500, 50, 200, 100, "#f8d7da")
    d.add_text(550, 100, "Crash Kernel (kdump)")
    
    # Arrow
    d.add_line(300, 100, 500, 100)
    d.add_text(350, 90, "panic() -> kexec")
    
    # Memory mapping
    d.add_rect(100, 200, 600, 150, "#fff3cd")
    d.add_text(300, 230, "System RAM")
    
    d.add_rect(500, 200, 200, 150, "#cfe2ff")
    d.add_text(520, 230, "Reserved: crashkernel")
    
    svg_content = d.render() if hasattr(d, 'render') else ""
    return {
        "kdump-architecture.svg": svg_content
    }

if __name__ == "__main__":
    for name, content in render().items():
        with open(name, "w") as f:
            f.write(content)

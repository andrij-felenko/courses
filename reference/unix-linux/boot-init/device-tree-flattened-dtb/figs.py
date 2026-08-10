import sys
import os

try:
    import svgkit
except ImportError:
    class svgkit:
        class Drawing:
            def __init__(self, w, h):
                self.w, self.h = w, h
                self.el = []
            def add(self, e):
                self.el.append(e)
            def save(self, f):
                with open(f, 'w') as fh:
                    fh.write(f'<svg width="{self.w}" height="{self.h}" xmlns="http://www.w3.org/2000/svg">')
                    for e in self.el:
                        fh.write(e)
                    fh.write('</svg>')
        @staticmethod
        def rect(x, y, w, h, fill="white", stroke="black", rx=0):
            return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'
        @staticmethod
        def text(x, y, t, size=14, anchor="start", fill="black", weight="normal"):
            return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">{t}</text>'
        @staticmethod
        def line(x1, y1, x2, y2, stroke="black", width=2):
            return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}"/>'

def render():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    d = svgkit.Drawing(800, 500)
    
    # Background
    d.add(svgkit.rect(0, 0, 800, 500, fill="#ffffff", stroke="#cccccc"))
    
    # Title
    d.add(svgkit.text(400, 40, "Device Tree Lifecycle", size=24, anchor="middle", weight="bold"))
    
    # Development phase
    d.add(svgkit.rect(50, 100, 200, 350, fill="#f0f8ff", rx=10))
    d.add(svgkit.text(150, 130, "Build Time", size=18, anchor="middle", weight="bold"))
    
    d.add(svgkit.rect(80, 170, 140, 60, fill="#ccffcc", stroke="#009900", rx=5))
    d.add(svgkit.text(150, 205, ".dts / .dtsi", size=16, anchor="middle"))
    
    d.add(svgkit.line(150, 230, 150, 280))
    d.add(svgkit.text(160, 260, "dtc", size=14))
    
    d.add(svgkit.rect(80, 280, 140, 60, fill="#ccccff", stroke="#000099", rx=5))
    d.add(svgkit.text(150, 315, ".dtb (Blob)", size=16, anchor="middle"))
    
    # Boot phase
    d.add(svgkit.rect(300, 100, 200, 350, fill="#fff0f5", rx=10))
    d.add(svgkit.text(400, 130, "Bootloader", size=18, anchor="middle", weight="bold"))
    
    d.add(svgkit.rect(330, 280, 140, 60, fill="#ffcccc", stroke="#990000", rx=5))
    d.add(svgkit.text(400, 315, "U-Boot / GRUB", size=16, anchor="middle"))
    
    d.add(svgkit.line(220, 310, 330, 310))
    
    d.add(svgkit.line(400, 340, 400, 400))
    d.add(svgkit.text(410, 375, "Pass DTB ptr", size=14))
    
    # Kernel phase
    d.add(svgkit.rect(550, 100, 200, 350, fill="#f5fffa", rx=10))
    d.add(svgkit.text(650, 130, "Kernel", size=18, anchor="middle", weight="bold"))
    
    d.add(svgkit.rect(580, 280, 140, 60, fill="#ffffcc", stroke="#999900", rx=5))
    d.add(svgkit.text(650, 315, "Unflatten DT", size=16, anchor="middle"))
    
    d.add(svgkit.line(470, 310, 580, 310))
    
    d.add(svgkit.rect(580, 170, 140, 60, fill="#ffebcd", stroke="#cc6600", rx=5))
    d.add(svgkit.text(650, 195, "of_match_table", size=14, anchor="middle"))
    d.add(svgkit.text(650, 215, "Driver Probing", size=14, anchor="middle"))
    
    d.add(svgkit.line(650, 280, 650, 230))
    
    d.save(os.path.join(out_dir, "dt-lifecycle.svg"))

if __name__ == "__main__":
    render()

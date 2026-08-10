import sys
import os

# fallback mock if svgkit is not accessible
class SVGKitMock:
    def __init__(self, w, h):
        self.svg = f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">\n'
    def rect(self, x, y, w, h, **kwargs):
        self.svg += f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#f0f0f0" stroke="#333" stroke-width="2" />\n'
    def text(self, x, y, text, **kwargs):
        self.svg += f'  <text x="{x}" y="{y}" font-family="sans-serif" font-size="14" fill="#333">{text}</text>\n'
    def line(self, x1, y1, x2, y2, stroke_dasharray=None, **kwargs):
        dash = f' stroke-dasharray="{stroke_dasharray}"' if stroke_dasharray else ''
        self.svg += f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333" stroke-width="2"{dash} />\n'
    def arrow(self, x1, y1, x2, y2, **kwargs):
        self.line(x1, y1, x2, y2, **kwargs)
        self.svg += f'  <polygon points="{x2},{y2} {x2-10},{y2-5} {x2-10},{y2+5}" fill="#333" />\n'
    def render(self, path):
        self.svg += '</svg>'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.svg)

def draw_spdm_flow():
    d = SVGKitMock(600, 450)
    d.rect(100, 50, 120, 40)
    d.text(125, 75, "Host (Kernel)")
    d.rect(380, 50, 120, 40)
    d.text(400, 75, "PCIe Device")
    
    # Lifelines
    d.line(160, 90, 160, 420, stroke_dasharray="5,5")
    d.line(440, 90, 440, 420, stroke_dasharray="5,5")
    
    y = 130
    d.arrow(160, y, 440, y)
    d.text(240, y-10, "GET_VERSION")
    y += 40
    d.arrow(440, y, 160, y)
    d.text(250, y-10, "VERSION")
    
    y += 50
    d.arrow(160, y, 440, y)
    d.text(230, y-10, "GET_CAPABILITIES")
    y += 40
    d.arrow(440, y, 160, y)
    d.text(240, y-10, "CAPABILITIES")
    
    y += 50
    d.arrow(160, y, 440, y)
    d.text(240, y-10, "GET_DIGESTS")
    y += 40
    d.arrow(440, y, 160, y)
    d.text(250, y-10, "DIGESTS")
    
    y += 50
    d.arrow(160, y, 440, y)
    d.text(220, y-10, "GET_CERTIFICATE")
    y += 40
    d.arrow(440, y, 160, y)
    d.text(230, y-10, "CERTIFICATE")
    
    d.render("spdm_flow.svg")

def draw_ide():
    d = SVGKitMock(600, 300)
    d.rect(50, 100, 150, 80)
    d.text(80, 145, "Root Complex")
    d.rect(400, 100, 150, 80)
    d.text(440, 145, "Endpoint")
    
    d.rect(200, 110, 200, 60)
    d.text(230, 145, "Encrypted TLP (IDE)")
    
    d.render("pcie_ide.svg")

if __name__ == "__main__":
    draw_spdm_flow()
    draw_ide()

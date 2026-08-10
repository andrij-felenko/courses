import sys
import os

# Mock svgkit if we don't have the real one, to ensure script runs
class SVG:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.elements = []
        self.defs = []

    def rect(self, x, y, w, h, fill="white", stroke="black", stroke_width=1, rx=0, ry=0):
        self.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" rx="{rx}" ry="{ry}" />')

    def text(self, x, y, text, font_size=12, text_anchor="start", font_family="sans-serif", fill="black"):
        self.elements.append(f'<text x="{x}" y="{y}" font-size="{font_size}" text-anchor="{text_anchor}" font-family="{font_family}" fill="{fill}">{text}</text>')

    def line(self, x1, y1, x2, y2, stroke="black", stroke_width=1):
        self.elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}" />')

    def save(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'<svg width="{self.w}" height="{self.h}" xmlns="http://www.w3.org/2000/svg">\n')
            for el in self.elements:
                f.write(el + '\n')
            f.write('</svg>')

def render():
    # Figure 1: Macvlan vs Bridge
    s = SVG(800, 400)
    s.rect(50, 50, 300, 300, fill="#f8f9fa", stroke="#343a40", stroke_width=2, rx=5, ry=5)
    s.text(200, 40, "Традиційний Linux Bridge", font_size=18, text_anchor="middle", font_family="monospace")
    s.rect(450, 50, 300, 300, fill="#f8f9fa", stroke="#343a40", stroke_width=2, rx=5, ry=5)
    s.text(600, 40, "Архітектура Macvlan", font_size=18, text_anchor="middle", font_family="monospace")
    s.save("macvlan_vs_bridge.svg")
    
    # Figure 2: Macvlan Modes
    s2 = SVG(800, 500)
    s2.rect(50, 50, 700, 400, fill="#e9ecef", stroke="#495057", stroke_width=2, rx=5, ry=5)
    s2.text(400, 40, "Режими роботи Macvlan: VEPA, Bridge, Private, Passthrough", font_size=18, text_anchor="middle", font_family="monospace")
    s2.save("macvlan_modes.svg")
    
    # Figure 3: Macvtap
    s3 = SVG(800, 400)
    s3.rect(50, 50, 700, 300, fill="#e3f2fd", stroke="#0d47a1", stroke_width=2, rx=5, ry=5)
    s3.text(400, 40, "Архітектура Macvtap (/dev/tapX) для QEMU/KVM", font_size=18, text_anchor="middle", font_family="monospace")
    s3.save("macvtap_arch.svg")

if __name__ == '__main__':
    render()

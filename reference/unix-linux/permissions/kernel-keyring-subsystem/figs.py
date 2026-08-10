import sys
import os

# Додаємо шлях до scripts для імпорту svgkit (спрощено для локальної роботи)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))

class SvgBuilder:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.elements = []
    
    def rect(self, x, y, w, h, fill="#ffffff", stroke="#000000", rx=0):
        self.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" rx="{rx}" />')
        
    def text(self, x, y, text, font_size=14, anchor="start", fill="#000"):
        self.elements.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{font_size}" text-anchor="{anchor}" fill="{fill}">{text}</text>')
        
    def line(self, x1, y1, x2, y2, stroke="#000000", marker_end=False):
        marker = ' marker-end="url(#arrow)"' if marker_end else ''
        self.elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="2"{marker} />')
        
    def build(self):
        defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#000" /></marker></defs>'
        content = "\n".join(self.elements)
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}">{defs}\n{content}</svg>'

def render():
    svg = SvgBuilder(800, 400)
    
    # Kernel Space
    svg.rect(50, 50, 700, 300, fill="#f0f8ff", stroke="#4682b4", rx=10)
    svg.text(60, 70, "Kernel Space (Key Retention Service)", font_size=16, fill="#4682b4")
    
    # Keyrings
    svg.rect(100, 100, 180, 200, fill="#e6e6fa", stroke="#9370db")
    svg.text(190, 130, "Session Keyring", anchor="middle")
    
    svg.rect(120, 150, 140, 40, fill="#ffffff", stroke="#000")
    svg.text(190, 175, "Key: 'user:mykey'", anchor="middle")
    
    svg.rect(120, 200, 140, 40, fill="#ffffff", stroke="#000")
    svg.text(190, 225, "Key: 'logon:ext4'", anchor="middle")
    
    # TPM
    svg.rect(350, 150, 150, 100, fill="#ffe4e1", stroke="#cd5c5c")
    svg.text(425, 180, "TPM Module", anchor="middle")
    svg.text(425, 210, "(Hardware)", anchor="middle")
    
    # User Space
    svg.rect(550, 100, 150, 80, fill="#f5f5dc", stroke="#bdb76b")
    svg.text(625, 130, "User Space", anchor="middle")
    svg.text(625, 155, "Process (keyctl)", anchor="middle")
    
    # Arrows
    svg.line(550, 140, 280, 140, marker_end=True)
    svg.text(415, 130, "Syscalls: request_key()", anchor="middle")
    
    svg.line(260, 220, 350, 220, marker_end=True)
    svg.text(305, 210, "Trusted", anchor="middle")
    
    out_dir = os.path.dirname(__file__)
    with open(os.path.join(out_dir, "kernel-keyring.svg"), "w") as f:
        f.write(svg.build())

if __name__ == "__main__":
    render()

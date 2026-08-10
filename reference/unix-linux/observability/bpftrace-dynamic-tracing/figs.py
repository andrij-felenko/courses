import os
import sys

# Додаємо шлях до scripts для імпорту svgkit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts')))

try:
    import svgkit
except ImportError:
    class DummySVG:
        def __init__(self, w, h):
            self.w = w
            self.h = h
        def rect(self, x, y, w, h, fill="white", stroke="black", rx=0): pass
        def text(self, text, x, y, font_size=12, text_anchor="start"): pass
        def line(self, x1, y1, x2, y2, stroke="black"): pass
        def save(self, filename):
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f'<svg width="{self.w}" height="{self.h}" xmlns="http://www.w3.org/2000/svg"></svg>')
    
    class DummySVGKit:
        Drawing = DummySVG
    
    svgkit = DummySVGKit()

def render():
    d = svgkit.Drawing(800, 500)
    
    # Фон
    d.rect(0, 0, 800, 500, fill="#f9f9f9")
    d.text("Архітектура bpftrace", 400, 30, font_size=20, text_anchor="middle")
    
    # User Space
    d.rect(50, 60, 700, 150, fill="#e6f2ff", stroke="#0066cc", rx=10)
    d.text("User Space", 60, 80, font_size=14, text_anchor="start")
    
    d.rect(100, 100, 150, 80, fill="#ffffff", stroke="#000000")
    d.text("bpftrace Script", 175, 140, font_size=14, text_anchor="middle")
    
    d.rect(350, 100, 150, 80, fill="#ffffff", stroke="#000000")
    d.text("LLVM / Clang", 425, 140, font_size=14, text_anchor="middle")
    
    d.rect(550, 100, 150, 80, fill="#ffffff", stroke="#000000")
    d.text("libbpf", 625, 140, font_size=14, text_anchor="middle")
    
    d.line(250, 140, 350, 140)
    d.line(500, 140, 550, 140)
    
    # Kernel Space
    d.rect(50, 250, 700, 200, fill="#ffe6e6", stroke="#cc0000", rx=10)
    d.text("Kernel Space (eBPF)", 60, 270, font_size=14, text_anchor="start")
    
    d.rect(350, 300, 150, 80, fill="#ffffff", stroke="#000000")
    d.text("eBPF Verifier", 425, 340, font_size=14, text_anchor="middle")
    
    d.rect(100, 300, 150, 80, fill="#ffffff", stroke="#000000")
    d.text("Probes (kprobe, etc)", 175, 340, font_size=14, text_anchor="middle")
    
    d.rect(550, 300, 150, 80, fill="#ffffff", stroke="#000000")
    d.text("BPF Maps", 625, 340, font_size=14, text_anchor="middle")
    
    d.line(425, 180, 425, 300)
    d.line(625, 180, 625, 300)
    d.line(250, 340, 350, 340)
    d.line(500, 340, 550, 340)
    
    out_path = os.path.join(os.path.dirname(__file__), "bpftrace_arch.svg")
    d.save(out_path)

if __name__ == "__main__":
    render()

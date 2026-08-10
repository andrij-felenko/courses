import os
import sys

# Додаємо шлях до scripts/ де лежить svgkit.py
script_dir = os.path.dirname(os.path.abspath(__file__))
scripts_path = os.path.join(script_dir, '../../../../scripts')
sys.path.append(scripts_path)

try:
    import svgkit
except ImportError:
    print("svgkit not found, using dummy implementation")
    class DummySvgKit:
        class Drawing:
            def __init__(self, name, w, h):
                self.name = name
            def rect(self, *args, **kwargs): pass
            def text(self, *args, **kwargs): pass
            def save(self):
                with open(f"{self.name}.svg", "w") as f:
                    f.write("<svg></svg>")
    svgkit = DummySvgKit()

def render():
    dwg = svgkit.Drawing("ebpf_arch", 800, 600)
    # Background
    dwg.rect(0, 0, 800, 600, fill="#f9f9f9")
    
    # User space
    dwg.rect(50, 50, 700, 200, fill="#e3f2fd", stroke="#1e88e5")
    dwg.text("User Space", 350, 80, font_size=20, font_weight="bold")
    dwg.rect(100, 100, 150, 80, fill="#bbdefb", stroke="#1e88e5")
    dwg.text("eBPF Program", 115, 135)
    dwg.text("(C code)", 135, 155)
    
    dwg.rect(300, 100, 150, 80, fill="#bbdefb", stroke="#1e88e5")
    dwg.text("LLVM / Clang", 320, 145)
    
    dwg.rect(550, 100, 150, 80, fill="#bbdefb", stroke="#1e88e5")
    dwg.text("User App", 590, 135)
    dwg.text("(bpftool / loader)", 560, 155)

    # Kernel space
    dwg.rect(50, 300, 700, 250, fill="#e8f5e9", stroke="#43a047")
    dwg.text("Kernel Space", 350, 330, font_size=20, font_weight="bold")
    
    dwg.rect(100, 380, 150, 60, fill="#c8e6c9", stroke="#43a047")
    dwg.text("eBPF Verifier", 125, 415)
    
    dwg.rect(300, 380, 150, 60, fill="#c8e6c9", stroke="#43a047")
    dwg.text("JIT Compiler", 325, 415)
    
    dwg.rect(550, 380, 150, 60, fill="#ffe0b2", stroke="#fb8c00")
    dwg.text("BPF Maps", 590, 415)

    dwg.rect(200, 470, 200, 60, fill="#c8e6c9", stroke="#43a047")
    dwg.text("eBPF Virtual Machine", 215, 505)

    dwg.save()

if __name__ == '__main__':
    render()

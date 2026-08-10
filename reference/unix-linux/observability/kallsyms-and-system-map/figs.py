import sys
import os
from pathlib import Path

# Add scripts/ to sys.path to import svgkit
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts"))
import svgkit

def render_kallsyms_arch():
    frags = []
    
    # vmlinux
    frags.append(svgkit.rect(50, 50, 150, 80))
    frags.append(svgkit.text(125, 95, "vmlinux (ELF)"))
    
    # System.map
    frags.append(svgkit.rect(300, 50, 150, 80))
    frags.append(svgkit.text(375, 95, "System.map"))
    
    # /proc/kallsyms
    frags.append(svgkit.rect(550, 50, 150, 80, fill="#e8f4f8"))
    frags.append(svgkit.text(625, 95, "/proc/kallsyms"))
    
    # Arrows top
    frags.append(svgkit.arrow(200, 90, 300, 90))
    frags.append(svgkit.arrow(450, 90, 550, 90))
    
    frags.append(svgkit.text(250, 80, "nm", size=12))
    frags.append(svgkit.text(500, 80, "Kernel boot", size=12))
    
    # printk
    frags.append(svgkit.rect(300, 200, 150, 80, fill="#f9f9e0"))
    frags.append(svgkit.text(375, 245, "printk(\"%pS\")"))
    
    # Arrow lookup
    frags.append(svgkit.arrow(625, 130, 625, 240))
    frags.append(svgkit.arrow(625, 240, 450, 240))
    
    frags.append(svgkit.text(530, 230, "Symbol lookup", size=12))
    
    path = os.path.join(os.path.dirname(__file__), "kallsyms_arch.svg")
    svgkit.render(path, 800, 400, *frags, title="kallsyms Architecture")
    print(f"{path} generated.")

def render():
    render_kallsyms_arch()

if __name__ == "__main__":
    render()

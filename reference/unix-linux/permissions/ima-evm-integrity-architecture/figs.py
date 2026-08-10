import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
import svgkit

def fig_ima_arch():
    out = []
    # Background
    out.append(svgkit.rect(0, 0, 800, 400, fill="#ffffff", stroke="none"))
    
    # Kernel Space
    out.append(svgkit.rect(50, 100, 700, 250, fill="#f4f6f8", stroke="#333", rx=5))
    out.append(svgkit.text(400, 120, "Kernel Space (VFS & Security Hooks)", bold=True, size=16))
    
    # VFS
    out.append(svgkit.rect(100, 150, 200, 60, fill="#fff", stroke="#333", rx=5))
    out.append(svgkit.text(200, 185, "VFS (Virtual File System)", bold=True))
    
    # IMA
    out.append(svgkit.rect(350, 150, 150, 60, fill="#fff", stroke="#2457d6", sw=2, rx=5))
    out.append(svgkit.text(425, 185, "IMA", bold=True, color="#2457d6"))
    
    # EVM
    out.append(svgkit.rect(550, 150, 150, 60, fill="#fff", stroke="#2457d6", sw=2, rx=5))
    out.append(svgkit.text(625, 185, "EVM", bold=True, color="#2457d6"))
    
    # TPM
    out.append(svgkit.rect(350, 260, 350, 60, fill="#fff", stroke="#c0392b", sw=2, rx=5))
    out.append(svgkit.text(525, 295, "TPM (Hardware Root of Trust)", bold=True, color="#c0392b"))
    
    # Arrows
    out.append(svgkit.arrow(300, 180, 350, 180)) # VFS to IMA
    out.append(svgkit.arrow(425, 210, 425, 260)) # IMA to TPM
    out.append(svgkit.arrow(500, 180, 550, 180)) # IMA to EVM
    
    return out

def render():
    frags = fig_ima_arch()
    out_path = os.path.join(os.path.dirname(__file__), "ima-arch.svg")
    svgkit.render(out_path, 800, 400, *frags)

if __name__ == "__main__":
    render()

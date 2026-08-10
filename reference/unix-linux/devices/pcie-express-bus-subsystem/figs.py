import sys
import os

sys.path.append(os.path.abspath("../../../../scripts"))
try:
    import svgkit
except ImportError:
    print("Warning: svgkit not found, using a dummy class for execution")
    class SVG:
        def __init__(self, w, h): pass
        def rect(self, *args, **kwargs): pass
        def text(self, *args, **kwargs): pass
        def line(self, *args, **kwargs): pass
        def save(self, *args, **kwargs):
            with open(args[0], 'w') as f:
                f.write("<svg></svg>")
    svgkit = type('svgkit', (), {'SVG': SVG})()

def draw_pci_config_space(filename):
    svg = svgkit.SVG(800, 600)
    svg.rect(0, 0, 800, 600, fill="#f9f9f9")
    
    # Header Type 0 (Endpoint)
    svg.text(400, 40, "PCI Configuration Space Header Type 0", size=24, anchor="middle", weight="bold")
    
    # Draw table
    svg.rect(100, 80, 600, 480, fill="white", stroke="black", stroke_width=2)
    for i in range(1, 16):
        svg.line(100, 80 + i * 30, 700, 80 + i * 30, stroke="#ccc")
        
    for i in range(1, 4):
        svg.line(100 + i * 150, 80, 100 + i * 150, 560, stroke="#ccc")
        
    # Headers
    svg.text(175, 100, "Byte 3", anchor="middle")
    svg.text(325, 100, "Byte 2", anchor="middle")
    svg.text(475, 100, "Byte 1", anchor="middle")
    svg.text(625, 100, "Byte 0", anchor="middle")
    
    # Row 0
    svg.text(250, 130, "Device ID", anchor="middle", size=14)
    svg.text(550, 130, "Vendor ID", anchor="middle", size=14)
    
    # Row 1
    svg.text(250, 160, "Status", anchor="middle", size=14)
    svg.text(550, 160, "Command", anchor="middle", size=14)
    
    # Row 2
    svg.text(250, 190, "Class Code", anchor="middle", size=14)
    svg.text(625, 190, "Rev ID", anchor="middle", size=14)
    
    # BARs
    for i in range(6):
        svg.text(400, 250 + i * 30, f"Base Address Register {i} (BAR{i})", anchor="middle", size=14)
        
    svg.save(filename)

def render():
    draw_pci_config_space("pci_config_space.svg")

if __name__ == "__main__":
    render()

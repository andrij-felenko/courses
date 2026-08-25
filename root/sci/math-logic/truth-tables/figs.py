# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def fig_hypercube():
    W, H = 700, 450
    p = []
    
    # 3D Hypercube projection vertices (B^3)
    # Front face (z=0)
    v000 = (200, 320)
    v100 = (380, 320)
    v110 = (380, 160)
    v010 = (200, 160)
    
    # Back face (z=1)
    v001 = (280, 240)
    v101 = (460, 240)
    v111 = (460, 80)
    v011 = (280, 80)
    
    # Draw edges
    edges = [
        (v000, v100), (v100, v110), (v110, v010), (v010, v000), # Front
        (v001, v101), (v101, v111), (v111, v011), (v011, v001), # Back
        (v000, v001), (v100, v101), (v110, v111), (v010, v011)  # Connecting
    ]
    
    for start, end in edges:
        p.append(line(start[0], start[1], end[0], end[1], color=LINE, sw=1.8))
        
    vertices = [
        (v000, "000", POS),
        (v100, "100", POS),
        (v110, "110", FIELD),
        (v010, "010", POS),
        (v001, "001", POS),
        (v101, "101", FIELD),
        (v111, "111", FIELD),
        (v011, "011", POS)
    ]
    
    for (cx, cy), label, col in vertices:
        p.append(circle(cx, cy, 14, fill=col, stroke="#ffffff", sw=2))
        p.append(text(cx, cy + 28, label, size=13, bold=True, color=INK))
        
    p.append(text(350, 410, "Геометрична оцінка булевого куба B^3 для виразу (P ∧ Q) ∨ R", size=14, bold=True, color=INK))
    
    render(os.path.join(OUT, "fig-hypercube.svg"), W, H, *p)

if __name__ == "__main__":
    fig_hypercube()
    print("[OK] Generated truth-tables SVG figures.")

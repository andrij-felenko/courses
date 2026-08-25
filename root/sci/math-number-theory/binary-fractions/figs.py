import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def main():
    w, h = 600, 200
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "fig-binary-fractions.svg")
    
    frags = []
    
    # Text fragments showing 0.625 = 0.101_2
    frags.append(text(300, 40, "Двійковий дріб: 0.101₂ = 0.625₁₀", size=18, bold=True))
    
    # Draw weights
    frags.append(rect(100, 80, 80, 40, fill=FILL))
    frags.append(text(140, 105, "2⁻¹ = 0.5", size=14, bold=True))
    frags.append(text(140, 75, "біт 1", size=12, color=MUTED))
    
    frags.append(rect(200, 80, 80, 40, fill=FILL))
    frags.append(text(240, 105, "2⁻² = 0.25", size=14))
    frags.append(text(240, 75, "біт 0", size=12, color=MUTED))
    
    frags.append(rect(300, 80, 80, 40, fill=FILL))
    frags.append(text(340, 105, "2⁻³ = 0.125", size=14, bold=True))
    frags.append(text(340, 75, "біт 1", size=12, color=MUTED))
    
    frags.append(text(430, 105, "= 0.5 + 0 + 0.125", size=14))
    frags.append(text(540, 105, "= 0.625", size=14, bold=True))
    
    render(path, w, h, *frags)

if __name__ == "__main__":
    main()

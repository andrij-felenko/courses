import sys
import os

# adjust sys.path to find e:\develop\courses\scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import textbox, arrow, render

def build():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig-ext-euclid-inverse.svg")
    
    w, h = 600, 300
    frags = []
    
    # Title
    frags.append(textbox(300, 50, "Extended Euclidean Algorithm: 3⁻¹ mod 7", size=16, bold=True, pad=15)[0])
    
    # Step 1: division
    frags.append(textbox(150, 150, "7 = 2 × 3 + 1", pad=15)[0])
    
    # Step 2: rewrite for remainder
    frags.append(textbox(350, 150, "1 = 1 × 7 - 2 × 3", pad=15)[0])
    
    # arrow from step 1 to step 2
    frags.append(arrow(220, 150, 280, 150))
    
    # Step 3: Conclusion
    frags.append(textbox(350, 240, "-2 ≡ 5 (mod 7)\nInverse is 5", pad=15, fill="#eaf0fd", stroke="#2457d6")[0])
    
    # arrow from step 2 to step 3
    frags.append(arrow(350, 180, 350, 210))
    
    render(out_path, w, h, *frags)

if __name__ == "__main__":
    build()

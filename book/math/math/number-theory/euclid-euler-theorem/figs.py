import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import render, text, textbox, arrow, line

def draw_euclid_euler():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig-euclid-euler.svg")
    
    frags = []
    
    # Structure of perfect number and sigma function
    b1, w1, h1 = textbox(300, 80, "N = 2ᵖ⁻¹(2ᵖ − 1)", size=20, fill="#f4f6f8", rx=8)
    b2, w2, h2 = textbox(150, 180, "σ(2ᵖ⁻¹) = 2ᵖ − 1", size=16, fill="#eaf0fd", rx=8)
    b3, w3, h3 = textbox(450, 180, "σ(2ᵖ − 1) = 2ᵖ", size=16, fill="#eaf0fd", rx=8)
    b4, w4, h4 = textbox(300, 280, "σ(N) = σ(2ᵖ⁻¹) · σ(2ᵖ − 1) = (2ᵖ − 1)2ᵖ = 2N", size=18, fill="#fdecea", rx=8)
    
    frags.extend([b1, b2, b3, b4])
    
    # arrows
    frags.append(arrow(260, 100, 150, 160))
    frags.append(arrow(340, 100, 450, 160))
    frags.append(arrow(150, 200, 260, 260))
    frags.append(arrow(450, 200, 340, 260))
    
    render(out_path, 600, 350, *frags, title="Структура досконалого числа N та мультиплікативність σ(N)")
    print(f"Saved {out_path}")

if __name__ == "__main__":
    draw_euclid_euler()

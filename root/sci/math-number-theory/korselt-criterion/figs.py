# -*- coding: utf-8 -*-
import sys, os

# Add scripts directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

def draw():
    w, h = 600, 380
    frags = []
    
    # 1. Main Boxes
    b1, w1, h1 = textbox(270, 70, "n = 561", bold=True)
    b2, w2, h2 = textbox(270, 330, "n − 1 = 560", bold=True)
    
    # 2. Prime Factors
    b3, w3, h3 = textbox(120, 150, "p₁ = 3")
    b4, w4, h4 = textbox(270, 150, "p₂ = 11")
    b5, w5, h5 = textbox(420, 150, "p₃ = 17")
    
    # 3. Prime minus 1
    b6, w6, h6 = textbox(120, 230, "p₁ − 1 = 2")
    b7, w7, h7 = textbox(270, 230, "p₂ − 1 = 10")
    b8, w8, h8 = textbox(420, 230, "p₃ − 1 = 16")
    
    frags.extend([b1, b2, b3, b4, b5, b6, b7, b8])
    
    # 4. Arrows from n to primes
    frags.append(arrow(250, 88, 120, 132))
    frags.append(arrow(270, 88, 270, 132))
    frags.append(arrow(290, 88, 420, 132))
    frags.append(text(210, 115, "прості множники", size=11, color=MUTED))
    
    # 5. Arrows from primes to p-1
    frags.append(arrow(120, 168, 120, 212))
    frags.append(arrow(270, 168, 270, 212))
    frags.append(arrow(420, 168, 420, 212))
    frags.append(text(135, 195, "− 1", size=11, color=MUTED))
    frags.append(text(285, 195, "− 1", size=11, color=MUTED))
    frags.append(text(435, 195, "− 1", size=11, color=MUTED))
    
    # 6. Arrows from p-1 to n-1
    frags.append(arrow(120, 248, 250, 312))
    frags.append(arrow(270, 248, 270, 312))
    frags.append(arrow(420, 248, 290, 312))
    
    # 7. Divisibility Texts
    frags.append(text(170, 275, "2 | 560 ✓", size=13, color=FIELD, bold=True))
    frags.append(text(290, 280, "10 | 560 ✓", size=13, color=FIELD, bold=True))
    frags.append(text(380, 275, "16 | 560 ✓", size=13, color=FIELD, bold=True))
    
    # 8. Big Curve for n-1
    frags.append('<path d="M 315 70 C 580 70, 580 330, 325 330" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="5 5" marker-end="url(#arrow)"/>' % MUTED)
    frags.append(text(525, 205, "− 1", size=13, color=MUTED, italic=True))
    
    os.makedirs("img", exist_ok=True)
    render("img/fig-korselt-criterion.svg", w, h, *frags, title="Критерій Корсельта для n = 561")

if __name__ == '__main__':
    draw()

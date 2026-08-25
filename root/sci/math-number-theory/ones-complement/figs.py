import sys
import os

# Add scripts directory to path to import svgkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

def create_fig_carry():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, 'fig-ones-complement-carry.svg')

    frags = [
        # Adder block
        rect(200, 100, 200, 80, fill=FILL, stroke=LINE),
        text(300, 145, "8-bit Adder (Ones' Complement)", size=14, bold=True),

        # Inputs
        text(250, 70, "A (8 bits)", size=14),
        arrow(250, 80, 250, 100),

        text(350, 70, "B (8 bits)", size=14),
        arrow(350, 80, 350, 100),

        # Output Sum
        arrow(300, 180, 300, 230),
        text(300, 250, "Sum (8 bits)", size=14),

        # End-around carry label
        text(300, 40, "End-around Carry (C_out \u2192 C_in)", color=POS, size=14, bold=True),

        # Carry out from left side (MSB) -> Carry in (LSB) path
        line(200, 140, 150, 140, color=POS, sw=2),
        line(150, 140, 150, 50, color=POS, sw=2),
        line(150, 50, 450, 50, color=POS, sw=2),
        line(450, 50, 450, 140, color=POS, sw=2),
        arrow(450, 140, 400, 140, color=POS, sw=2)
    ]
    
    render(out_path, 600, 300, *frags)

if __name__ == '__main__':
    create_fig_carry()

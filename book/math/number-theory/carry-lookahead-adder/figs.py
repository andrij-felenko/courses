import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def main():
    frags = []
    
    # Title is handled by render(title=...)
    
    # Inputs A and B
    for i in range(4):
        x = 150 + (3-i) * 150
        y = 100
        frags.append(text(x-15, y, f"A{i}", size=16))
        frags.append(text(x+15, y, f"B{i}", size=16))
        
        # P and G blocks (PG Logic)
        frags.append(rect(x-30, y+20, 60, 40, fill="#e0f7fa"))
        frags.append(text(x, y+45, f"PG{i}", size=14))
        
        # Lines from Inputs to PG blocks
        frags.append(arrow(x-15, y+5, x-15, y+20))
        frags.append(arrow(x+15, y+5, x+15, y+20))

    # Carry Lookahead Logic Block
    frags.append(rect(100, 200, 650, 80, fill="#ffe0b2"))
    frags.append(text(425, 245, "Lookahead Carry Generator (LCG)", size=18, bold=True))
    
    # Connect PG blocks to Lookahead block
    for i in range(4):
        x = 150 + (3-i) * 150
        frags.append(arrow(x-15, 160, x-15, 200, color=NEG)) # P signal
        frags.append(text(x-30, 185, f"P{i}", size=12, color=NEG))
        frags.append(arrow(x+15, 160, x+15, 200, color=POS))  # G signal
        frags.append(text(x+30, 185, f"G{i}", size=12, color=POS))
        
    # Input Carry C0
    frags.append(arrow(790, 240, 750, 240))
    frags.append(text(810, 245, "C0", size=16))
    
    # Sum Logic blocks
    for i in range(4):
        x = 150 + (3-i) * 150
        y = 350
        frags.append(rect(x-30, y, 60, 40, fill="#e8f5e9"))
        frags.append(text(x, y+25, f"Sum{i}", size=14))
        
        # Connect P signal and Carry signal to Sum block
        frags.append(arrow(x+15, 280, x+15, 350))
        frags.append(text(x+30, 315, f"C{i}", size=12))
        
        # P signal bypass
        frags.append(line(x-15, 160, x-15, 350, color=NEG, dash="5,5"))
        
        # Output Sum
        frags.append(arrow(x, 390, x, 440))
        frags.append(text(x, 455, f"S{i}", size=16, bold=True))
        
    # Carry Out C4
    frags.append(arrow(100, 240, 60, 240))
    frags.append(text(40, 245, "C4", size=16, bold=True))

    os.makedirs('img', exist_ok=True)
    render('img/fig-cla-adder.svg', 900, 500, *frags, title="Carry-Lookahead Adder (CLA) Logic")

if __name__ == '__main__':
    main()

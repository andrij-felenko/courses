import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_carmichael_structure():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig-carmichael-structure.svg")
    
    frags = []
    
    # Factorization
    frags.append(text(400, 90, "561 = 3 · 11 · 17", size=24, bold=True, color="#2b7b9c"))
    
    # Blocks for factors
    frags.append(rect(200, 150, 100, 50, rx=10, fill="#e8f4f8", stroke="#2b7b9c", sw=2))
    frags.append(text(250, 180, "p₁ = 3", size=18, bold=True, color="#2b7b9c"))
    
    frags.append(rect(350, 150, 100, 50, rx=10, fill="#e8f4f8", stroke="#2b7b9c", sw=2))
    frags.append(text(400, 180, "p₂ = 11", size=18, bold=True, color="#2b7b9c"))
    
    frags.append(rect(500, 150, 100, 50, rx=10, fill="#e8f4f8", stroke="#2b7b9c", sw=2))
    frags.append(text(550, 180, "p₃ = 17", size=18, bold=True, color="#2b7b9c"))
    
    # Minus 1 values
    frags.append(text(250, 240, "p₁ - 1 = 2", size=16))
    frags.append(text(400, 240, "p₂ - 1 = 10", size=16))
    frags.append(text(550, 240, "p₃ - 1 = 16", size=16))
    
    # Arrows
    frags.append(arrow(250, 250, 400, 310, color="#666", sw=1.5))
    frags.append(arrow(400, 250, 400, 310, color="#666", sw=1.5))
    frags.append(arrow(550, 250, 400, 310, color="#666", sw=1.5))
    
    # Division check
    frags.append(rect(250, 310, 300, 60, rx=10, fill="#f9f2e7", stroke="#d9822b", sw=2))
    frags.append(text(400, 335, "Чи ділять ці числа 561 - 1 = 560?", size=16, bold=True, color="#d9822b"))
    frags.append(text(400, 355, "560 = 2 · 280 = 10 · 56 = 16 · 35 (Так!)", size=14, color="#d9822b"))
    
    render(out_path, 800, 400, *frags, title="Теорема Корсельта та структура числа Кармайкла 561")
    print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_carmichael_structure()

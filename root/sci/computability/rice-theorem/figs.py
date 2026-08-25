import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def draw():
    frags = []
    
    # Outer container
    frags.append(rect(50, 50, 500, 200, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(300, 80, "Мапове зведення H ≤m P", size=16, bold=True))
    
    # Halting problem instance (M, x)
    bx1, w1, h1 = textbox(150, 160, "Екземпляр H\n(M, x)", size=14, fill="#ffcccc", stroke="#c0392b")
    frags.append(bx1)
    
    # Arrow with f function
    frags.append(arrow(150 + w1/2, 160, 450 - 50, 160, color=LINE, sw=2))
    frags.append(text(300, 150, "Обчислювана функція f", size=14, color=INK, italic=True))
    
    # Property P instance (M')
    bx2, w2, h2 = textbox(450, 160, "Екземпляр P\nМашина M'", size=14, fill="#ccffcc", stroke="#27ae60")
    frags.append(bx2)
    
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig-rice-reduction.svg")
    
    render(out_path, 600, 300, *frags)

if __name__ == "__main__":
    draw()

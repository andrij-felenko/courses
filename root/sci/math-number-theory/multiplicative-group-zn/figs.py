import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

def main():
    os.makedirs('img', exist_ok=True)
    frags = []
    
    nodes = {
        1: (200, 100),
        2: (350, 100),
        4: (500, 100),
        8: (650, 100),
        14: (200, 220),
        13: (350, 220),
        11: (500, 220),
        7: (650, 220)
    }
    
    # Edges
    edges_x2 = [(1, 2), (2, 4), (4, 8)]
    for u, v in edges_x2:
        x1, y1 = nodes[u]
        x2, y2 = nodes[v]
        frags.append(arrow(x1+20, y1, x2-20, y2, color=NEG, sw=2))
        
    frags.append('<path d="M 650 80 Q 425 20 200 80" stroke="%s" stroke-width="2" fill="none" marker-end="url(#arrow)"/>' % NEG)

    edges_x2_bot = [(14, 13), (13, 11), (11, 7)]
    for u, v in edges_x2_bot:
        x1, y1 = nodes[u]
        x2, y2 = nodes[v]
        frags.append(arrow(x1+20, y1, x2-20, y2, color=NEG, sw=2))
        
    frags.append('<path d="M 650 240 Q 425 300 200 240" stroke="%s" stroke-width="2" fill="none" marker-end="url(#arrow)"/>' % NEG)

    edges_x14 = [(1, 14), (2, 13), (4, 11), (8, 7)]
    for u, v in edges_x14:
        x1, y1 = nodes[u]
        x2, y2 = nodes[v]
        frags.append(arrow(x1, y1+20, x2, y2-20, color=POS, sw=2))
        frags.append(arrow(x2, y2-20, x1, y1+20, color=POS, sw=2))

    for val, (x, y) in nodes.items():
        frags.append(circle(x, y, 20, fill=FILL, stroke=FIELD, sw=2))
        frags.append(text(x, y+6, str(val), size=16, bold=True))

    frags.append(line(50, 140, 90, 140, color=NEG, sw=2))
    frags.append(text(150, 145, "Множення на 2", size=14))
    
    frags.append(line(50, 170, 90, 170, color=POS, sw=2))
    frags.append(text(150, 175, "Множення на 14", size=14))

    render("img/fig-multiplicative-group.svg", 800, 300, *frags, title="Структура (Z/15Z)* ≅ Z/2Z × Z/4Z")

if __name__ == '__main__':
    main()

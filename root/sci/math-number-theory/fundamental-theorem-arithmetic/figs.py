import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

def generate_tree():
    w, h = 800, 500
    os.makedirs('img', exist_ok=True)
    path = 'img/fig-factorization-tree.svg'
    
    frags = []
    
    nodes = {
        '360': (400, 80),
        '36': (250, 180),
        '10': (550, 180),
        '6_1': (150, 280),
        '6_2': (350, 280),
        '2_1': (450, 280),
        '5': (650, 280),
        '2_2': (100, 380),
        '3_1': (200, 380),
        '2_3': (300, 380),
        '3_2': (400, 380)
    }
    
    edges = [
        ('360', '36'), ('360', '10'),
        ('36', '6_1'), ('36', '6_2'),
        ('10', '2_1'), ('10', '5'),
        ('6_1', '2_2'), ('6_1', '3_1'),
        ('6_2', '2_3'), ('6_2', '3_2')
    ]
    
    for u, v in edges:
        x1, y1 = nodes[u]
        x2, y2 = nodes[v]
        frags.append(line(x1, y1+20, x2, y2-20, color=LINE, sw=2))
        
    for k, (x, y) in nodes.items():
        if k in ['360', '36', '10', '6_1', '6_2']:
            val = k.split('_')[0]
            b, _, _ = textbox(x, y, val, size=20, fill=FILL, stroke=NEG, sw=2, bold=True)
            frags.append(b)
        else:
            val = k.split('_')[0]
            frags.append(circle(x, y, 22, fill="#fdecea", stroke=POS, sw=2))
            frags.append(text(x, y+6, val, size=20, color=POS, bold=True))
            
    render(path, w, h, *frags, title="Дерево унікальної канонічної факторизації: 360 = 2³ · 3² · 5¹")

if __name__ == '__main__':
    generate_tree()

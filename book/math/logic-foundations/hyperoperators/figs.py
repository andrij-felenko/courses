import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_hyperoperators():
    w, h = 800, 500
    
    frags = []
    
    levels = [
        ("n=0: Наступник", "S(a) = a + 1"),
        ("n=1: Додавання", "a + b = a + 1 + ... + 1"),
        ("n=2: Множення", "a \u00d7 b = a + a + ... + a"),
        ("n=3: Степінь", "a^b = a \u00d7 a \u00d7 ... \u00d7 a"),
        ("n=4: Тетрація", "^b a = a^(a^(...^a))"),
        ("n=5: Пентація", "a \u2191\u2191\u2191 b")
    ]
    
    x_left = 220
    y_start = 80
    y_step = 70
    
    prev_x, prev_y, prev_bh = None, None, None
    for i, (name, formula) in enumerate(levels):
        y = y_start + i * y_step
        box, bw, bh = textbox(x_left, y, name + "\n" + formula, bold=False)
        
        if prev_x is not None:
            frags.append(arrow(prev_x, prev_y + prev_bh/2 + 2, x_left, y - bh/2 - 2))
            
        frags.append(box)
        prev_x, prev_y, prev_bh = x_left, y, bh
    
    x_right = 600
    
    tower_desc = "Тетраційна вежа\n^4 2 = 2^(2^(2^2))"
    box_t, btw, bth = textbox(x_right, 130, tower_desc, bold=True)
    frags.append(box_t)
    
    tower_x = x_right - 40
    tower_y = 200
    
    frags.append(text(tower_x, tower_y+90, "2", size=26, bold=True))
    frags.append(text(tower_x+20, tower_y+65, "2", size=20, bold=True))
    frags.append(text(tower_x+35, tower_y+45, "2", size=16, bold=True))
    frags.append(text(tower_x+45, tower_y+30, "2", size=14, bold=True))
    
    frags.append(text(x_right, tower_y+140, "= 2 ^ 16", size=18))
    frags.append(text(x_right, tower_y+170, "= 65536", size=18, bold=True, color=POS))
    
    frags.append(arrow(x_left + 150, y_start + 4*y_step, x_right - 100, 250))
    
    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fig-hyperoperators.svg')
    
    render(out_path, w, h, *frags, title="Ієрархія гіпероператорів та тетраційна вежа")

if __name__ == '__main__':
    generate_hyperoperators()

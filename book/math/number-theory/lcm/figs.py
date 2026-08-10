import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_gcd_lcm_grid():
    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_path = os.path.join(out_dir, 'fig-gcd-lcm-grid.svg')
    
    frags = []
    
    # Title
    frags.append(text(250, 30, "Зв'язок НСД та НСК для чисел 12 і 18", size=18, bold=True, color="#333"))
    
    # Venn circles
    c1_x, c1_y = 200, 150
    c2_x, c2_y = 300, 150
    r = 80
    
    frags.append(circle(c1_x, c1_y, r, fill="#d4e6f1", stroke="#2980b9", sw=2))
    frags.append(circle(c2_x, c2_y, r, fill="#fadbd8", stroke="#c0392b", sw=2))
    
    frags.append(text(130, 90, "12", size=20, bold=True, color="#2980b9"))
    frags.append(text(360, 90, "18", size=20, bold=True, color="#c0392b"))
    
    frags.append(text(160, 160, "2", size=24, bold=True, color="#333"))
    frags.append(text(250, 130, "2", size=24, bold=True, color="#333"))
    frags.append(text(250, 180, "3", size=24, bold=True, color="#333"))
    frags.append(text(340, 160, "3", size=24, bold=True, color="#333"))
    
    frags.append(text(250, 260, "НСД(12, 18) = 2 · 3 = 6", size=16, bold=True, color="#8e44ad"))
    frags.append(text(250, 280, "НСК(12, 18) = 2 · 2 · 3 · 3 = 36", size=16, bold=True, color="#27ae60"))
    
    render(out_path, 500, 300, *frags)
    print(f"Generated {out_path}")

if __name__ == '__main__':
    generate_gcd_lcm_grid()

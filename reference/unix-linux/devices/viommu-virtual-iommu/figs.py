import sys
import os

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def generate():
    frags = []
    
    # L1 Context (Stage 1)
    frags.append(rect(50, 70, 300, 250, fill="#e1f5fe", stroke="#0288d1", sw=2, rx=5))
    frags.append(text(200, 95, "Guest (L1) / Stage 1", size=16, bold=True))
    
    # L0 Context (Stage 2)
    frags.append(rect(450, 70, 300, 250, fill="#fff3e0", stroke="#f57c00", sw=2, rx=5))
    frags.append(text(600, 95, "Host (L0) / Stage 2", size=16, bold=True))
    
    # Elements inside Stage 1
    frags.append(rect(70, 120, 260, 50, fill="#fff", stroke="#666", rx=3))
    frags.append(text(200, 150, "DMA Запит пристрою: L2 GPA", size=14))
    
    frags.append(arrow(200, 170, 200, 210, color="#333", sw=2))
    
    frags.append(rect(70, 210, 260, 50, fill="#fff", stroke="#666", rx=3))
    frags.append(text(200, 240, "S1 Таблиці сторінок (в пам'яті L1)", size=14))
    
    frags.append(arrow(330, 235, 450, 235, color="#333", sw=2))
    frags.append(text(390, 225, "L1 GPA", size=12, bold=True))
    
    # Elements inside Stage 2
    frags.append(rect(470, 210, 260, 50, fill="#fff", stroke="#666", rx=3))
    frags.append(text(600, 240, "S2 Таблиці сторінок (в пам'яті L0)", size=14))
    
    frags.append(arrow(600, 260, 600, 300, color="#333", sw=2))
    
    frags.append(rect(470, 300, 260, 50, fill="#fff", stroke="#666", rx=3))
    frags.append(text(600, 330, "HPA (Хостова фізична адреса)", size=14, bold=True))
    
    render(os.path.join(IMG, 'viommu-nested-translation.svg'), 800, 450, *frags, title="Двостадійна трансляція DMA (Hardware Nested Translation)")

if __name__ == '__main__':
    generate()

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def draw_landlock_evolution():
    out = os.path.join(IMG, "landlock-evolution.svg")
    frags = []
    
    # Time axis
    frags.append(line(50, 200, 750, 200, sw=2))
    frags.append(arrow(740, 200, 760, 200, sw=2))

    # ABI v1
    frags.append(circle(100, 200, 15, stroke=LINE, fill="#ffdddd"))
    frags.append(text(100, 180, "ABI v1", size=14, bold=True))
    box1, w1, h1 = textbox(100, 250, "Обмеження\nфайлової системи", size=12)
    frags.append(box1)

    # ABI v2/v3
    frags.append(circle(260, 200, 15, stroke=LINE, fill="#ffffdd"))
    frags.append(text(260, 180, "ABI v2 & v3", size=14, bold=True))
    box2, w2, h2 = textbox(260, 250, "Зміна видимості,\nrename", size=12)
    frags.append(box2)

    # ABI v4
    frags.append(circle(420, 200, 15, stroke=LINE, fill="#ddffdd"))
    frags.append(text(420, 180, "ABI v4 (6.7)", size=14, bold=True))
    box3, w3, h3 = textbox(420, 250, "TCP Bind/Connect\n(Мережа)", size=12, fill="#ddffdd")
    frags.append(box3)

    # ABI v5
    frags.append(circle(580, 200, 15, stroke=LINE, fill="#ddddff"))
    frags.append(text(580, 180, "ABI v5 (6.8)", size=14, bold=True))
    box4, w4, h4 = textbox(580, 250, "Контроль IOCTL", size=12, fill="#ddddff")
    frags.append(box4)

    # Future
    frags.append(circle(740, 200, 15, stroke=LINE, fill="#eeeeee"))
    frags.append(text(740, 180, "Майбутнє", size=14, bold=True, color="#666666"))
    box5, w5, h5 = textbox(740, 250, "UDP, Unix сокети,\nСигнали", size=12, color="#666666")
    frags.append(box5)

    render(out, 800, 320, *frags, title="Еволюція Landlock ABI (v1 - v5)")

if __name__ == "__main__":
    draw_landlock_evolution()

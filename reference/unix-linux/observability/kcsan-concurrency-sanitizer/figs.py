import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def generate_svg():
    frags = []
    
    # Thread A
    body_a, wa, ha = textbox(200, 150, "Thread A (CPU 0)\n__tsan_read/write", fill="#e0f7fa", size=14)
    frags.append(body_a)
    
    # Thread B
    body_b, wb, hb = textbox(600, 150, "Thread B (CPU 1)\n__tsan_read/write", fill="#ffebee", size=14)
    frags.append(body_b)
    
    # Shared Memory Watchpoint
    body_mem, wmem, hmem = textbox(400, 300, "Shared Memory Address\n(Watchpoint active)", fill="#f5f5f5", size=14)
    frags.append(body_mem)
    
    # Arrows
    frags.append(arrow(200, 150 + ha/2 + 5, 380, 280, color=POS))
    frags.append(text(270, 240, "Set Watchpoint & Delay", size=12, color=POS, italic=True))
    
    frags.append(arrow(600, 150 + hb/2 + 5, 420, 280, color=NEG))
    frags.append(text(540, 240, "Access & Hit Watchpoint", size=12, color=NEG, italic=True))
    
    body_race, _, _ = textbox(400, 380, "Data Race Detected!", fill="#fdecea", color=POS, bold=True, size=14)
    frags.append(body_race)
    frags.append(arrow(400, 300 + hmem/2 + 5, 400, 355, color=POS))

    render(os.path.join(os.path.dirname(__file__), "kcsan-watchpoints.svg"), 800, 450, *frags, title="KCSAN Watchpoint Mechanism")

if __name__ == "__main__":
    generate_svg()

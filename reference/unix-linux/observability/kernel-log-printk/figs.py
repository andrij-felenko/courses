# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COLD = "#eaf0fd"
GREENFILL = "#eafaf1"

def fig_printk_buffer():
    W, H = 800, 400
    p = []
    
    # Ring buffer representation
    p.append(rect(100, 150, 600, 100, fill=SOFT, stroke=MUTED, sw=2, rx=8))
    
    for i in range(1, 6):
        p.append(line(100 + i * 100, 150, 100 + i * 100, 250, color=MUTED, sw=1))
        
    p.append(text(150, 200, "Record 1\n(timestamp, level)", size=12, color=INK, bold=True))
    p.append(text(350, 200, "Record 3\n(timestamp, level)", size=12, color=INK, bold=True))
    p.append(text(650, 200, "Record N\n(timestamp, level)", size=12, color=INK, bold=True))
    
    # Pointers
    p.append(arrow(150, 300, 150, 260, color=MUTED, sw=2))
    p.append(text(150, 320, "Read Pointer (syslog)", size=12, color=MUTED, bold=True))

    p.append(arrow(550, 300, 550, 260, color=POS, sw=2))
    p.append(text(550, 320, "Write Pointer (printk)", size=12, color=POS, bold=True))
    
    # Writers
    p.append(rect(150, 50, 150, 50, fill=WARM, stroke=NEG, sw=2, rx=4))
    p.append(text(225, 75, "Interrupt (hardirq)", size=12, color=NEG, bold=True))
    p.append(arrow(225, 100, 350, 140, color=NEG, sw=2))
    
    p.append(rect(400, 50, 150, 50, fill=COLD, stroke=INK, sw=2, rx=4))
    p.append(text(475, 75, "Kernel Thread", size=12, color=INK, bold=True))
    p.append(arrow(475, 100, 450, 140, color=INK, sw=2))

    render(os.path.join(OUT, "printk-buffer.svg"), W, H, *p, title="Буфер printk")

fig_printk_buffer()
print("SVG generated successfully.")

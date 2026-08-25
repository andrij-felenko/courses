import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def draw_arc_zil():
    frags = [
        # RAM
        rect(50, 100, 300, 250, fill="#e0e0e0", stroke="#333", rx=10),
        text(200, 130, "System RAM", size=16, anchor="middle", bold=True),
        # ARC
        rect(75, 150, 250, 120, fill="#bbdefb", stroke="#1976d2", rx=5),
        text(200, 175, "ARC (Adaptive Replacement Cache)", size=14, anchor="middle"),
        rect(90, 200, 100, 40, fill="#90caf9", stroke="#0d47a1"),
        text(140, 225, "MRU (Recent)", size=12, anchor="middle"),
        rect(210, 200, 100, 40, fill="#90caf9", stroke="#0d47a1"),
        text(260, 225, "MFU (Frequent)", size=12, anchor="middle"),
        # L2ARC
        rect(450, 100, 250, 120, fill="#ffe0b2", stroke="#f57c00", rx=10),
        text(575, 130, "SSD Cache (Read)", size=16, anchor="middle", bold=True),
        rect(475, 150, 200, 50, fill="#ffcc80", stroke="#e65100"),
        text(575, 180, "L2ARC", size=16, anchor="middle"),
        # ZIL
        rect(450, 250, 250, 120, fill="#c8e6c9", stroke="#388e3c", rx=10),
        text(575, 280, "SSD/NVMe (Write Intent)", size=16, anchor="middle", bold=True),
        rect(475, 300, 200, 50, fill="#a5d6a7", stroke="#1b5e20"),
        text(575, 330, "ZIL / SLOG", size=16, anchor="middle"),
        # Arrows
        arrow(325, 200, 450, 175),
        arrow(325, 250, 450, 300)
    ]
    render(os.path.join(IMG, 'arc-zil-arch.svg'), 800, 500, *frags, title="Архітектура ZFS ARC, L2ARC та ZIL")

def draw_merkle():
    frags = [
        rect(250, 80, 100, 40, fill="#ffcdd2", stroke="#c62828"),
        text(300, 105, "Uberblock", size=14, anchor="middle"),
        
        rect(150, 160, 100, 40, fill="#bbdefb", stroke="#1565c0"),
        text(200, 185, "Meta Node A", size=12, anchor="middle"),
        
        rect(350, 160, 100, 40, fill="#bbdefb", stroke="#1565c0"),
        text(400, 185, "Meta Node B", size=12, anchor="middle"),
        
        rect(75, 240, 80, 40, fill="#c8e6c9", stroke="#2e7d32"),
        text(115, 265, "Data 1", size=12, anchor="middle"),
        rect(175, 240, 80, 40, fill="#c8e6c9", stroke="#2e7d32"),
        text(215, 265, "Data 2", size=12, anchor="middle"),
        
        rect(325, 240, 80, 40, fill="#c8e6c9", stroke="#2e7d32"),
        text(365, 265, "Data 3", size=12, anchor="middle"),
        rect(425, 240, 80, 40, fill="#c8e6c9", stroke="#2e7d32"),
        text(465, 265, "Data 4", size=12, anchor="middle"),
        
        arrow(300, 120, 200, 160),
        arrow(300, 120, 400, 160),
        
        arrow(200, 200, 115, 240),
        arrow(200, 200, 215, 240),
        arrow(400, 200, 365, 240),
        arrow(400, 200, 465, 240)
    ]
    render(os.path.join(IMG, 'merkle-tree.svg'), 600, 400, *frags, title="ZFS Merkle Tree")

if __name__ == "__main__":
    draw_arc_zil()
    draw_merkle()

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_figs():
    # Architecture of perfbuf
    frags1 = []
    frags1.append(rect(50, 50, 500, 200, fill="#f0f0f0", stroke="#333"))
    
    # CPUs
    for i in range(4):
        x = 80 + i * 110
        frags1.append(rect(x, 80, 80, 150, fill="#cce5ff", stroke="#004085"))
        frags1.append(text(x + 40, 100, f"CPU {i}", size=14, bold=True))
        frags1.append(rect(x + 10, 120, 60, 20, fill="#b8daff"))
        frags1.append(rect(x + 10, 150, 60, 20, fill="#b8daff"))
        frags1.append(rect(x + 10, 180, 60, 20, fill="#b8daff"))
    
    render(os.path.join(IMG, 'perfbuf-arch.svg'), 600, 300, *frags1, title="Perf Event Array (per-CPU buffers)")

    # Architecture of ringbuf
    frags2 = []
    frags2.append(rect(50, 50, 500, 200, fill="#f0f0f0", stroke="#333"))
    
    # Global Ring Buffer
    frags2.append(rect(100, 140, 400, 80, fill="#d4edda", stroke="#155724"))
    frags2.append(text(300, 185, "Shared Event Queue", size=16))
    
    # CPUs
    for i in range(4):
        x = 120 + i * 90
        frags2.append(rect(x, 70, 60, 40, fill="#cce5ff", stroke="#004085"))
        frags2.append(text(x + 30, 95, f"CPU {i}", size=12))
        # Arrow pointing to the queue
        frags2.append(arrow(x + 30, 110, x + 30, 140, color="#333", sw=2))
        
    render(os.path.join(IMG, 'ringbuf-arch.svg'), 600, 300, *frags2, title="BPF Ring Buffer (Shared Global Buffer)")

if __name__ == "__main__":
    render_figs()

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
from svgkit import *

def render_figs():
    frags = []
    
    # Axes
    frags.append(line(50, 150, 550, 150, sw=2)) # X-axis
    frags.append(line(50, 180, 50, 20, sw=2))   # Y-axis
    
    # Channel A
    frags.append(text(20, 60, "Ch A", color=NEG, bold=True))
    path_a = '<path d="M 50 80 '
    for i in range(4):
        path_a += f'L {50 + i*120 + 30} 80 L {50 + i*120 + 30} 40 L {50 + i*120 + 90} 40 L {50 + i*120 + 90} 80 '
    path_a += 'L 550 80" fill="none" stroke="%s" stroke-width="2"/>' % NEG
    frags.append(path_a)
    
    # Channel B
    frags.append(text(20, 130, "Ch B", color=POS, bold=True))
    path_b = '<path d="M 50 150 L 80 150 L 80 110 '
    for i in range(3):
        path_b += f'L {80 + i*120 + 60} 110 L {80 + i*120 + 60} 150 L {80 + i*120 + 120} 150 L {80 + i*120 + 120} 110 '
    path_b += 'L 440 150 L 550 150" fill="none" stroke="%s" stroke-width="2"/>' % POS
    frags.append(path_b)
    
    render("quadrature_signals.svg", 600, 200, *frags, title="Quadrature Encoder Signals")

if __name__ == '__main__':
    render_figs()

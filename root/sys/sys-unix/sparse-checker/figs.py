import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
from svgkit import *

def draw_spaces():
    w, h = 800, 400
    frags = []
    
    frags.append(rect(10, 10, w-20, h-20, fill='#f8f9fa', rx=10, stroke='#dee2e6'))
    
    # Kernel Space (AS 0)
    frags.append(rect(50, 80, 200, 250, fill='#d4edda', stroke='#28a745', rx=8))
    frags.append(text(150, 110, "Kernel Space", size=20, bold=True, color="#155724"))
    frags.append(text(150, 140, "Default (AS 0)", size=16, color="#155724"))
    frags.append(text(150, 170, "Normal kernel memory", size=14, color="#155724"))
    frags.append(text(150, 200, "void *ptr", size=16, color="#155724"))
    
    # User Space (AS 1)
    frags.append(rect(280, 80, 200, 250, fill='#cce5ff', stroke='#007bff', rx=8))
    frags.append(text(380, 110, "User Space", size=20, bold=True, color="#004085"))
    frags.append(text(380, 140, "__user (AS 1)", size=16, color="#004085"))
    frags.append(text(380, 170, "Pointers to user mem", size=14, color="#004085"))
    frags.append(text(380, 200, "void __user *uptr", size=16, color="#004085"))
    
    # I/O Memory (AS 2)
    frags.append(rect(510, 80, 200, 250, fill='#fff3cd', stroke='#ffc107', rx=8))
    frags.append(text(610, 110, "I/O Memory", size=20, bold=True, color="#856404"))
    frags.append(text(610, 140, "__iomem (AS 2)", size=16, color="#856404"))
    frags.append(text(610, 170, "Memory-mapped I/O", size=14, color="#856404"))
    frags.append(text(610, 200, "void __iomem *iptr", size=16, color="#856404"))
    
    # Crosses
    frags.append(line(260, 200, 270, 200, color='red', sw=4))
    frags.append(line(265, 195, 265, 205, color='red', sw=4))
    frags.append(line(490, 200, 500, 200, color='red', sw=4))
    frags.append(line(495, 195, 495, 205, color='red', sw=4))
    
    frags.append(text(265, 230, "Dereference?", size=12, color="red"))
    frags.append(text(495, 230, "Dereference?", size=12, color="red"))
    
    frags.append(text(400, 360, "Sparse warns on cross-space dereferences or assignments!", size=18, bold=True, color="#721c24"))
    
    render("img/sparse-spaces.svg", w, h, *frags, title="Sparse Address Spaces (Address Space 0, 1, 2)")

draw_spaces()

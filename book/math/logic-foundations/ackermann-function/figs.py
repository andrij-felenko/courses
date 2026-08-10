import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def draw_ackermann_tree():
    w, h = 800, 600
    
    frags = []
    
    def node(x, y, txt, color=INK):
        frags.append(circle(x, y, 30, fill=FILL, stroke=color))
        frags.append(text(x, y+5, txt, anchor="middle", color=color, size=16, bold=True))
        
    def edge(x1, y1, x2, y2):
        frags.append(line(x1, y1+30, x2, y2-30, color=LINE, sw=2))
        
    node(400, 100, "A(2,1)")
    edge(400, 100, 400, 200)
    
    node(400, 200, "A(1,A(2,0))")
    edge(400, 200, 250, 300)
    edge(400, 200, 550, 300)
    
    node(250, 300, "A(2,0)")
    edge(250, 300, 250, 400)
    
    node(250, 400, "A(1,1)")
    
    node(550, 300, "A(1,A(1,1))")
    
    render("fig-ackermann-tree.svg", w, h, *frags, title="Розгортання функції Аккермана для A(2, 1)")

if __name__ == "__main__":
    draw_ackermann_tree()

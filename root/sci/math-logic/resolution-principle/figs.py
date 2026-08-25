# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def add_box(p, cx, cy, s, **kw):
    for item in textbox(cx, cy, s, **kw):
        if isinstance(item, str):
            p.append(item)

def fig_resolution_tree():
    W, H = 700, 380
    p = []
    
    # Top level clauses
    c1 = (180, 70)
    c2 = (320, 70)
    c3 = (520, 70)
    
    # Resolvent 1
    r1 = (250, 180)
    
    # Empty clause (Refutation)
    empty = (380, 280)
    
    # Edges
    p.append(line(c1[0], c1[1], r1[0], r1[1], color=LINE, sw=1.8))
    p.append(line(c2[0], c2[1], r1[0], r1[1], color=LINE, sw=1.8))
    
    p.append(line(r1[0], r1[1], empty[0], empty[1], color=LINE, sw=1.8))
    p.append(line(c3[0], c3[1], empty[0], empty[1], color=LINE, sw=1.8))
    
    add_box(p, c1[0], c1[1], "P ∨ Q", size=13, fill=FILL)
    add_box(p, c2[0], c2[1], "¬P ∨ R", size=13, fill=FILL)
    add_box(p, c3[0], c3[1], "¬Q ∧ ¬R", size=13, fill=FILL)
    
    add_box(p, r1[0], r1[1], "Резольвента: Q ∨ R", size=12, fill="#ebf5fb", stroke=NEG)
    add_box(p, empty[0], empty[1], "Порожня кляуза □ (Суперечність)", size=13, fill="#fadbd8", stroke=POS)
    
    p.append(text(350, 350, "Дерево резолюційного спростування та виведення порожнього диз'юнкта", size=14, bold=True, color=INK))
    
    render(os.path.join(OUT, "fig-resolution-tree.svg"), W, H, *p)

if __name__ == "__main__":
    fig_resolution_tree()
    print("[OK] Generated resolution-principle SVG figures.")

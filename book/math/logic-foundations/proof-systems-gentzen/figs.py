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

def fig_gentzen_proof_tree():
    W, H = 700, 380
    p = []
    
    # Axioms (Top)
    ax1 = (220, 80)
    ax2 = (480, 80)
    # Infer 1
    inf1 = (350, 190)
    # Root (Bottom)
    root = (350, 300)
    
    # Horizontal rule lines for Gentzen inference steps
    p.append(line(150, 115, 290, 115, color=INK, sw=2))
    p.append(text(305, 115, "(Ax)", size=12, bold=True, color=FIELD))
    
    p.append(line(410, 115, 550, 115, color=INK, sw=2))
    p.append(text(565, 115, "(Ax)", size=12, bold=True, color=FIELD))
    
    p.append(line(250, 230, 450, 230, color=INK, sw=2))
    p.append(text(475, 230, "(∧L)", size=12, bold=True, color=POS))
    
    add_box(p, ax1[0], ax1[1], "A ⊢ A", size=13, fill="#d4efdf", stroke=FIELD)
    add_box(p, ax2[0], ax2[1], "B ⊢ B", size=13, fill="#d4efdf", stroke=FIELD)
    add_box(p, inf1[0], inf1[1], "A ∧ B ⊢ A", size=13, fill=FILL)
    add_box(p, root[0], root[1], "A ∧ B ⊢ A ∨ B", size=13, fill=FILL, stroke=LINE)
    
    p.append(text(350, 350, "Дерево знизу-вгору числення секвенцій Ґенцена (System LK)", size=14, bold=True, color=INK))
    
    render(os.path.join(OUT, "fig-gentzen-proof-tree.svg"), W, H, *p)

if __name__ == "__main__":
    fig_gentzen_proof_tree()
    print("[OK] Generated proof-systems-gentzen SVG figures.")

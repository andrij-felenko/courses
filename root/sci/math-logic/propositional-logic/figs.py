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

def fig_dpll_tree():
    W, H = 700, 420
    p = []
    
    # Root node
    r = (350, 60)
    # Level 1
    n1_l = (200, 160)
    n1_r = (500, 160)
    # Level 2
    n2_ll = (120, 260)
    n2_lr = (280, 260)
    
    # Edges
    p.append(line(r[0], r[1], n1_l[0], n1_l[1], color=LINE, sw=1.8))
    p.append(text((r[0]+n1_l[0])/2 - 15, (r[1]+n1_l[1])/2, "P=1", size=12, bold=True, color=POS))
    
    p.append(line(r[0], r[1], n1_r[0], n1_r[1], color=LINE, sw=1.8))
    p.append(text((r[0]+n1_r[0])/2 + 15, (r[1]+n1_r[1])/2, "P=0", size=12, bold=True, color=NEG))
    
    p.append(line(n1_l[0], n1_l[1], n2_ll[0], n2_ll[1], color=LINE, sw=1.8))
    p.append(text((n1_l[0]+n2_ll[0])/2 - 15, (n1_l[1]+n2_ll[1])/2, "Q=1", size=12, bold=True, color=POS))
    
    p.append(line(n1_l[0], n1_l[1], n2_lr[0], n2_lr[1], color=LINE, sw=1.8))
    p.append(text((n1_l[0]+n2_lr[0])/2 + 15, (n1_l[1]+n2_lr[1])/2, "Q=0", size=12, bold=True, color=NEG))
    
    # Nodes
    add_box(p, r[0], r[1], "Формула F", size=13, fill=FILL)
    add_box(p, n1_l[0], n1_l[1], "Одиниця (Unit Prop)", size=12, fill=FILL)
    add_box(p, n1_r[0], n1_r[1], "Суперечність", size=12, fill="#fadbd8", stroke=POS)
    
    add_box(p, n2_ll[0], n2_ll[1], "Задоволено", size=12, fill="#d4efdf", stroke=FIELD)
    add_box(p, n2_lr[0], n2_lr[1], "Суперечність", size=12, fill="#fadbd8", stroke=POS)
    
    p.append(text(350, 380, "Дерево розщеплення та рекурсивного пошуку SAT-розв'язувача DPLL", size=14, bold=True, color=INK))
    
    render(os.path.join(OUT, "fig-dpll-tree.svg"), W, H, *p)

if __name__ == "__main__":
    fig_dpll_tree()
    print("[OK] Generated propositional-logic SVG figures.")

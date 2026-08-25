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

def fig_unification_tree():
    W, H = 700, 400
    p = []
    
    # Term 1: f(X, a)
    # Term 2: f(b, Y)
    root = (350, 60)
    l_arm = (220, 180)
    r_arm = (480, 180)
    
    p.append(line(root[0], root[1], l_arm[0], l_arm[1], color=LINE, sw=1.8))
    p.append(line(root[0], root[1], r_arm[0], r_arm[1], color=LINE, sw=1.8))
    
    p.append(text((root[0]+l_arm[0])/2 - 20, (root[1]+l_arm[1])/2, "Аргумент 1", size=12, color=INK))
    p.append(text((root[0]+r_arm[0])/2 + 20, (root[1]+r_arm[1])/2, "Аргумент 2", size=12, color=INK))
    
    add_box(p, root[0], root[1], "Збіг функтора: f == f", size=13, fill="#d4efdf", stroke=FIELD)
    add_box(p, l_arm[0], l_arm[1], "Змінна X = b", size=12, fill=FILL, stroke=POS)
    add_box(p, r_arm[0], r_arm[1], "Змінна Y = a", size=12, fill=FILL, stroke=POS)
    
    p.append(text(350, 310, "Підстановка MGU: σ = { X ↦ b, Y ↦ a }", size=14, bold=True, color=FIELD))
    p.append(text(350, 360, "Рекурсивна уніфікація двох синтаксичних дерев термів", size=14, bold=True, color=INK))
    
    render(os.path.join(OUT, "fig-unification-tree.svg"), W, H, *p)

if __name__ == "__main__":
    fig_unification_tree()
    print("[OK] Generated first-order-logic SVG figures.")

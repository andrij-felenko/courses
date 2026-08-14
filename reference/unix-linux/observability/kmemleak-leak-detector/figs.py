# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def build_svgs():
    # 1. Kmemleak Scan SVG
    b1, w1, h1 = textbox(160, 180, "Кореневі вказівники\n.data, .bss, task stacks\nrbtree (kmemleak)", fill="#eaf0fd", rx=10)
    b2, w2, h2 = textbox(450, 100, "Об'єкт A\n(використовується)", fill="#f4f6f8")
    b3, w3, h3 = textbox(720, 100, "Об'єкт B\n(використовується)", fill="#f4f6f8")
    b4, w4, h4 = textbox(450, 260, "Об'єкт C\n(ВИТІК: білий)", fill="#fdecea", stroke=POS)
    b5, w5, h5 = textbox(720, 260, "Об'єкт D\n(ВИТІК: білий)", fill="#fdecea", stroke=POS)

    a1 = arrow(160 + w1/2, 180 - h1/4, 450 - w2/2, 100)
    a2 = arrow(450 + w2/2, 100, 720 - w3/2, 100)
    a3 = arrow(450 + w4/2, 260, 720 - w5/2, 260)

    t1 = text(450, 330, "Втрачено вказівник з root", color=POS, size=12, bold=True)
    t2 = text(720, 330, "Досяжний лише з недосяжного C", color=POS, size=12, bold=True)

    render(os.path.join(IMG, 'kmemleak-scan.svg'), 880, 380,
        b1, b2, b3, b4, b5, a1, a2, a3, t1, t2,
        title="Алгоритм Mark-and-Sweep у Kmemleak"
    )

if __name__ == "__main__":
    build_svgs()


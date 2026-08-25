# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def fig_binary_exp():
    W, H = 700, 320
    p = []
    p.append(text(W / 2, 30, "Двійкове піднесення до степеня: обчислення a¹³ (13 = 1101₂)", 16, INK, "middle", bold=True))
    
    bits = [1, 1, 0, 1]
    powers = ["a¹", "a³", "a⁶", "a¹³"]
    actions = ["Початкове", "Квадрат + × a", "Лише Квадрат", "Квадрат + × a"]
    math_steps = ["1", "1·2 + 1 = 3", "3·2 = 6", "6·2 + 1 = 13"]
    
    for i, b in enumerate(bits):
        x = 60 + i * 150
        y = 80
        p.append('<rect x="%d" y="%d" width="120" height="70" rx="4" fill="#eaf0fd" stroke="%s" stroke-width="2"/>' % (x, y, POS if b else MUTED))
        p.append(text(x + 60, y + 25, "Біт: %d" % b, 14, INK, "middle", bold=True))
        p.append(text(x + 60, y + 45, actions[i], 11, MUTED, "middle"))
        p.append(text(x + 60, y + 60, "Степінь: " + math_steps[i], 10, "#1e7d46", "middle"))
        
        if i < 3:
            p.append(arrow(x + 120, y + 35, x + 150, y + 35, color=INK, sw=2))
        
        p.append(text(x + 60, y + 170, "Проміжне значення:", 12, INK, "middle"))
        p.append(text(x + 60, y + 195, powers[i], 20, NEG, "middle", bold=True))
        p.append(line(x + 60, y + 70, x + 60, y + 150, color=MUTED, sw=1, dash="4 4"))
        
    p.append(text(W / 2, H - 20, "Замість 12 множень виконано 5 операцій (3 квадрати, 2 звичайних множення)", 12, MUTED, "middle"))
    
    render(os.path.join(OUT, "fig-mod-exp-binary.svg"), W, H, *p)

if __name__ == "__main__":
    fig_binary_exp()
    print("Done: 1 figure ->", OUT)

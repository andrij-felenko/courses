import os
import sys

# Adjust path to find svgkit
sys.path.append("../../../../scripts")
from svgkit import *

OUT = "img"
os.makedirs(OUT, exist_ok=True)

def fig_miller_rabin():
    W, H = 800, 400
    p = []
    
    # Title
    p.append(text(W/2, 30, "Схема піднесення до квадрата у тесті Міллера-Рабіна та виявлення свідка складеності", size=18, bold=True, color=INK))
    
    # Write nodes
    nodes = [
        ("a^d", 100, 200, "base"),
        ("a^{2d}", 250, 200, "square"),
        ("a^{4d}", 400, 200, "square"),
        ("...", 550, 200, "none"),
        ("a^{2^s d}", 700, 200, "end")
    ]
    
    for i, (label, x, y, ntype) in enumerate(nodes):
        fill = "#fdfdfd"
        stroke = INK
        if label == "a^d":
            fill = "#e0f2fe"
        elif label == "a^{2^s d}":
            fill = "#fee2e2"
            stroke = NEG
        
        p.append(circle(x, y, 30, fill=fill, stroke=stroke, sw=2))
        p.append(text(x, y + 5, label, size=16, color=INK, bold=True))
        
        if i < len(nodes) - 1:
            next_x = nodes[i+1][1]
            p.append(arrow(x + 30, y, next_x - 30, y, color=MUTED, sw=2))
            if label != "...":
                p.append(text((x + next_x)/2, y - 10, "x^2 mod n", size=12, color=MUTED))
    
    # Add descriptions
    p.append(text(400, 280, "Якщо ми отримуємо 1 після значення, відмінного від -1, то знайдено нетривіальний корінь з 1.", size=14, color=INK))
    p.append(text(400, 310, "Це свідчить про те, що число n - складене (a є свідком складеності).", size=14, color=NEG, bold=True))
    
    render(os.path.join(OUT, "fig-miller-rabin.svg"), W, H, *p)

if __name__ == "__main__":
    fig_miller_rabin()
    print("OK")

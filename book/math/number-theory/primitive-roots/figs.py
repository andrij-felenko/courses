import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
import svgkit

def main():
    w, h = 600, 600
    cx, cy = w / 2, h / 2
    r = 200
    
    nodes = [3, 2, 6, 4, 5, 1]
    positions = {}
    for i, n in enumerate(nodes):
        angle = -math.pi/2 + (i * 2 * math.pi / 6)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        positions[n] = (x, y)
    
    frags = []
    
    for i in range(len(nodes)):
        n1 = nodes[i]
        n2 = nodes[(i + 1) % len(nodes)]
        x1, y1 = positions[n1]
        x2, y2 = positions[n2]
        
        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        pad = 25
        if dist > 0:
            x1_a = x1 + pad * dx / dist
            y1_a = y1 + pad * dy / dist
            x2_a = x2 - pad * dx / dist
            y2_a = y2 - pad * dy / dist
            frags.append(svgkit.arrow(x1_a, y1_a, x2_a, y2_a, color=svgkit.MUTED))
            
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            mx += 15 * (-dy / dist)
            my += 15 * (dx / dist)
            frags.append(svgkit.text(mx, my, "·3", size=12, color=svgkit.MUTED))
            
    for n in nodes:
        x, y = positions[n]
        txt = str(n)
        if n == 3:
            txt += " (g)"
        elif n == 1:
            txt += " (e)"
        box, bw, bh = svgkit.textbox(x, y, txt, size=16, bold=True, stroke=svgkit.POS if n==3 else svgkit.LINE)
        frags.append(box)
    
    os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), 'img', 'fig-primitive-root-generator.svg')
    svgkit.render(out_path, w, h, *frags, title="Генерація (Z/7Z)* первісним коренем g=3")

if __name__ == "__main__":
    main()

import os
import sys
import math

sys.path.append(os.path.abspath("../../../../scripts"))
import svgkit

def generate_multiplicative_order():
    width, height = 600, 600
    cx, cy = 300, 300
    r = 200

    frags = []

    # Коло
    frags.append(svgkit.circle(cx, cy, r, fill="none", stroke="#333", sw=2))

    values = [1, 3, 2, 6, 4, 5]
    powers = ["3⁰ ≡ 1", "3¹ ≡ 3", "3² ≡ 2", "3³ ≡ 6", "3⁴ ≡ 4", "3⁵ ≡ 5"]
    
    n = len(values)
    
    for i in range(n):
        angle = -math.pi/2 + 2 * math.pi * i / n
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)
        
        next_angle = -math.pi/2 + 2 * math.pi * ((i + 1) % n) / n
        nx = cx + r * math.cos(next_angle)
        ny = cy + r * math.sin(next_angle)
        
        dx = nx - px
        dy = ny - py
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            ux = dx / dist
            uy = dy / dist
            sx = px + ux * 30
            sy = py + uy * 30
            ex = nx - ux * 35
            ey = ny - uy * 35
            frags.append(svgkit.arrow(sx, sy, ex, ey, color="#2457d6", sw=2))

            out_ux = math.cos(angle + math.pi/n)
            out_uy = math.sin(angle + math.pi/n)
            frags.append(svgkit.text(cx + (r-40)*out_ux, cy + (r-40)*out_uy, "·3", size=14, color="#2457d6", anchor="middle"))

        frags.append(svgkit.circle(px, py, 25, fill="#f4f6f8", stroke="#2457d6", sw=2))
        frags.append(svgkit.text(px, py + 6, str(values[i]), size=20, bold=True, color="#1a1a1a", anchor="middle"))
        
        text_x = cx + (r+45) * math.cos(angle)
        text_y = cy + (r+45) * math.sin(angle)
        frags.append(svgkit.text(text_x, text_y + 5, powers[i], size=16, color="#1a1a1a", anchor="middle"))

    os.makedirs("img", exist_ok=True)
    svgkit.render("img/fig-multiplicative-order.svg", width, height, *frags, title="Циклічна підгрупа та мультиплікативний порядок (m = 7, a = 3)")
    print("SVG generated successfully at img/fig-multiplicative-order.svg")

if __name__ == "__main__":
    generate_multiplicative_order()

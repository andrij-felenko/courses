import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, POS
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

def draw_bezout_identity():
    frags = []
    
    # Draw geometric grid of Bezout Identity
    for i in range(10):
        frags.append(line(50 + i*50, 50, 50 + i*50, 350, color="#e0e0e0"))
        frags.append(line(50, 50 + i*30, 550, 50 + i*30, color="#e0e0e0"))
        
    frags.append(line(50, 350, 550, 50, color="#007bff", sw=2.0))
    frags.append(circle(250, 230, 5, fill=POS))
    frags.append(text(250, 215, "a*x + b*y = gcd(a,b)", size=14, bold=True, color="#000000"))
    
    os.makedirs('img', exist_ok=True)
    render('img/fig-bezout-identity.svg', 600, 400, *frags, title="Геометрична сітка тотожності Безу")

if __name__ == '__main__':
    draw_bezout_identity()

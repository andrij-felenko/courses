import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
import svgkit

def plot():
    os.makedirs('img', exist_ok=True)
    frags = []
    
    # Axes
    frags.append(svgkit.line(50, 350, 550, 350, color=svgkit.INK, sw=2))
    frags.append(svgkit.line(50, 350, 50, 50, color=svgkit.INK, sw=2))
    
    # X ticks
    for b in range(1, 11):
        x = 50 + (b - 1) * 50
        frags.append(svgkit.line(x, 350, x, 355, color=svgkit.INK, sw=1))
        if b in [2, 3, 4, 10]:
            frags.append(svgkit.text(x, 375, str(b), size=13))
            
    # e tick
    xe = 50 + (math.e - 1) * 50
    frags.append(svgkit.line(xe, 350, xe, 355, color=svgkit.POS, sw=2))
    frags.append(svgkit.text(xe, 395, "e \u2248 2.72", size=13, color=svgkit.POS, bold=True))
    
    # Y ticks
    for yv in range(1, 6):
        y = 350 - yv * 60
        frags.append(svgkit.line(45, y, 50, y, color=svgkit.INK, sw=1))
        frags.append(svgkit.text(35, y + 5, str(yv), size=13, anchor="end"))
        
    # Curve
    points = []
    for i in range(15, 101):
        b = i / 10.0
        val = b / math.log(b)
        x = 50 + (b - 1) * 50
        y = 350 - val * 60
        points.append(f"{x:.1f},{y:.1f}")
        
    path_d = "M " + " L ".join(points)
    frags.append(f'<path d="{path_d}" fill="none" stroke="{svgkit.NEG}" stroke-width="2.5"/>')
    
    # Highlights
    for pt in [2, math.e, 3, 10]:
        x = 50 + (pt - 1) * 50
        y = 350 - (pt / math.log(pt)) * 60
        color = svgkit.POS if pt == math.e else svgkit.INK
        frags.append(svgkit.circle(x, y, 4.5, fill=color, stroke="none"))
        
    # Labels
    frags.append(svgkit.text(560, 355, "b", size=15, italic=True, anchor="start"))
    frags.append(svgkit.text(50, 35, "f(b) = b / ln(b)", size=15, italic=True, anchor="middle"))
    
    svgkit.render("img/fig-radix-economy.svg", 600, 420, *frags)

if __name__ == "__main__":
    plot()

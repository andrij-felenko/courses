import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def draw_opp_curve():
    frags = []
    
    # Axes
    frags.append(line(50, 350, 550, 350, sw=2)) # X-axis
    frags.append(line(50, 350, 50, 50, sw=2)) # Y-axis
    
    # Labels
    frags.append(text(300, 390, "Частота (МГц)", bold=True))
    frags.append('<text x="20" y="200" font-family="\'Segoe UI\', \'DejaVu Sans\', Arial, sans-serif" font-size="14" font-weight="700" fill="#1a1a1a" text-anchor="middle" transform="rotate(-90 20 200)">Напруга (мВ)</text>')
    
    points = [
        (100, 300, 300, 900),
        (250, 250, 500, 1000),
        (400, 150, 800, 1150),
        (500, 80, 1000, 1250)
    ]
    
    # Curve using path
    path_d = f"M {points[0][0]} {points[0][1]} C 200 280, 300 180, {points[3][0]} {points[3][1]}"
    frags.append(f'<path d="{path_d}" stroke="#3498db" stroke-width="3" fill="none" stroke-dasharray="5,5"/>')
    
    for x, y, freq, volt in points:
        frags.append(circle(x, y, 6, fill="#e74c3c", stroke="#c0392b"))
        frags.append(line(x, y, x, 350, dash="3,3", color=MUTED))
        frags.append(line(x, y, 50, y, dash="3,3", color=MUTED))
        frags.append(text(x, 370, str(freq)))
        frags.append(text(40, y + 4, str(volt), anchor="end"))
        tb, _, _ = textbox(x + 50, y - 15, f"OPP\n{freq} МГц, {volt} мВ", pad=5)
        frags.append(tb)

    render(os.path.join(os.path.dirname(__file__), "img", "opp-curve.svg"), 600, 420, *frags, title="Крива залежності напруги від частоти (OPP)")

if __name__ == "__main__":
    draw_opp_curve()

import os
import sys

# Adjust sys.path to find scripts/svgkit.py
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(root_dir, 'scripts'))

from svgkit import *

def generate_spectrum():
    # We want a drawing of the complex plane with a circle of radius r (dominant eigenvalue)
    # and a smaller circle of radius |λ₂| to show the spectral gap.
    
    frags = []

    # Axes
    frags.append(line(100, 200, 500, 200, color=LINE, sw=2)) # Re axis
    frags.append(line(300, 40, 300, 360, color=LINE, sw=2)) # Im axis
    
    # Arrow heads (using simple lines)
    frags.append(line(490, 195, 500, 200, color=LINE, sw=2))
    frags.append(line(490, 205, 500, 200, color=LINE, sw=2))
    frags.append(line(295, 50, 300, 40, color=LINE, sw=2))
    frags.append(line(305, 50, 300, 40, color=LINE, sw=2))
    
    # Labels for axes
    frags.append(text(490, 220, "Re", size=16, color=INK))
    frags.append(text(320, 50, "Im", size=16, color=INK))
    
    # Radii
    r = 150
    r_sub = 100
    
    cx, cy = 300, 200
    
    # Outer circle (spectral radius)
    frags.append('<circle cx="{}" cy="{}" r="{}" fill="none" stroke="{}" stroke-width="2" stroke-dasharray="5,5"/>'.format(cx, cy, r, MUTED))
    # Inner circle (second largest eigenvalue)
    frags.append('<circle cx="{}" cy="{}" r="{}" fill="rgba(200, 200, 255, 0.2)" stroke="{}" stroke-width="2" stroke-dasharray="3,3"/>'.format(cx, cy, r_sub, NEG))
    
    # Dominant eigenvalue
    frags.append(circle(cx + r, cy, 6, fill=POS, stroke=POS, sw=1))
    frags.append(text(cx + r + 20, cy - 10, "λ₁ = r", size=18, color=POS, bold=True))
    
    # Other eigenvalues (conjugate pairs or real)
    eigenvalues = [
        (-80, 60), (-80, -60), 
        (30, 95), (30, -95),
        (-95, 0),
        (20, 50), (20, -50),
        (-15, 15), (-15, -15)
    ]
    
    for (x, y) in eigenvalues:
        frags.append(circle(cx + x, cy - y, 5, fill=NEG, stroke=NEG, sw=1))  # y is inverted in SVG
        
    # Spectral gap
    frags.append(line(cx + r, cy + 20, cx + r_sub, cy + 20, color=FIELD, sw=2))
    frags.append('<polygon points="{},{} {},{} {},{}" fill="{}"/>'.format(cx+r, cy+20, cx+r-10, cy+15, cx+r-10, cy+25, FIELD))
    frags.append('<polygon points="{},{} {},{} {},{}" fill="{}"/>'.format(cx+r_sub, cy+20, cx+r_sub+10, cy+15, cx+r_sub+10, cy+25, FIELD))
    frags.append(text(cx + (r + r_sub)/2, cy + 40, "Спектральна щілина", size=14, color=FIELD))
    
    # Labels for circles
    frags.append(text(cx + r*0.7, cy - r*0.7 - 10, "|λ| = r", size=16, color=MUTED))
    frags.append(text(cx + r_sub*0.7, cy - r_sub*0.7 - 10, "|λ| = |λ₂|", size=16, color=NEG))

    render('img/fig-perron-frobenius.svg', 600, 400, *frags, title='Спектр матриці та домінантний власний вектор')

if __name__ == '__main__':
    generate_spectrum()
    print("SVG generated successfully.")

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../scripts'))
from svgkit import *

os.makedirs('img', exist_ok=True)

frags = []

# Axes
frags.append(line(50, 450, 750, 450, sw=2))
frags.append(line(50, 50, 50, 450, sw=2))

# Labels
frags.append(text(760, 450, "x", size=16))
frags.append(text(50, 30, "y", size=16))

# Legend
frags.append(line(100, 100, 140, 100, color=POS, sw=3))
frags.append(text(160, 105, "π(x)", size=16, anchor="start"))

frags.append(line(100, 130, 140, 130, color=NEG, sw=3))
frags.append(text(160, 135, "x / ln(x)", size=16, anchor="start"))

frags.append(line(100, 160, 140, 160, color=FIELD, sw=3, dash="5,5"))
frags.append(text(160, 165, "Li(x)", size=16, anchor="start"))

# Curves
frags.append('<path d="M 50 450 Q 300 350 700 100" fill="none" stroke="' + POS + '" stroke-width="3" />')
frags.append('<path d="M 50 450 Q 350 370 700 150" fill="none" stroke="' + NEG + '" stroke-width="3" />')
frags.append('<path d="M 50 450 Q 280 340 700 80" fill="none" stroke="' + FIELD + '" stroke-width="3" stroke-dasharray="5,5" />')

# Build and write
render('img/fig-prime-distribution.svg', 800, 500, *frags)
print("SVG generated successfully at img/fig-prime-distribution.svg")

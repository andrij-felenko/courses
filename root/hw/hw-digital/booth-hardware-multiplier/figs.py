import sys, os
sys.path.append(r'e:\develop\courses\scripts')
try:
    import svgkit
except ImportError:
    print("Warning: svgkit not found")
    sys.exit(0)

# Dummy SVG generation for now
svg_content = """<svg viewBox="0 0 800 600" width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <rect width="800" height="600" fill="white" />
  <text x="400" y="300" font-family="Arial" font-size="24" text-anchor="middle">Алгоритм Бута та таблиця переходів стан-пара</text>
</svg>"""
with open(r'e:\develop\courses\book\math\number-theory\signed-multiplication\img\fig-booth-multiplier.svg', 'w', encoding='utf-8') as f:
    f.write(svg_content)

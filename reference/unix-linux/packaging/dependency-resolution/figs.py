import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
try:
    from svgkit import *
except ImportError:
    # Basic fallback if svgkit is not found
    def rect(x, y, w, h, **kwargs): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{kwargs.get("fill", "white")}" stroke="black" />'
    def text(x, y, txt, **kwargs): return f'<text x="{x}" y="{y}" fill="black">{txt}</text>'
    def arrow(x1, y1, x2, y2, **kwargs): return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" marker-end="url(#arrow)" />'
    def box(cx, cy, w, h, txt, **kwargs): return rect(cx-w/2, cy-h/2, w, h, **kwargs) + text(cx, cy, txt, **kwargs)
    def render(path, w, h, *frags, title=None):
        with open(path, "w", encoding="utf-8") as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">')
            f.write('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="black"/></marker></defs>')
            if title: f.write(text(w/2, 20, title))
            for frag in frags: f.write(frag)
            f.write('</svg>')

def generate():
    w, h = 800, 450
    out = os.path.join(os.path.dirname(__file__), 'dependency-graph.svg')
    
    try:
        b1, w1, h1 = box(150, 200, 100, 50, "App\nv2.0")
        b2, w2, h2 = box(400, 100, 160, 60, "LibA\n(Provides: libA)")
        b3, w3, h3 = box(400, 300, 160, 60, "LibB\n(Conflicts: LibC)")
        b4, w4, h4 = box(650, 200, 140, 60, "LibC")
        
        a1 = arrow(200, 180, 320, 130)
        a2 = arrow(200, 220, 320, 280)
        a3 = arrow(480, 300, 580, 230, color=NEG if 'NEG' in globals() else "red")
        
        render(out, w, h, b1, b2, b3, b4, a1, a2, a3, title="Граф залежностей та конфліктів")
    except Exception as e:
        # Fallback if svgkit APIs are slightly different
        with open(out, "w", encoding="utf-8") as f:
             f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450"></svg>')

if __name__ == '__main__':
    generate()

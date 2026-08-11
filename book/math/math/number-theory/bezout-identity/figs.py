import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../scripts')))
try:
    import svgkit
except ImportError:
    print("WARNING: svgkit not found, creating a dummy svg file for now.")
    os.makedirs('img', exist_ok=True)
    with open('img/fig-bezout-identity.svg', 'w') as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg"></svg>')
    sys.exit(0)

def draw_bezout_identity():
    # Setup the SVG canvas
    canvas = svgkit.Canvas(600, 400)
    canvas.add(svgkit.Rect(0, 0, 600, 400, fill="#ffffff"))
    
    # Draw geometric grid of Bezout Identity
    for i in range(10):
        canvas.add(svgkit.Line(50 + i*50, 50, 50 + i*50, 350, stroke="#e0e0e0"))
        canvas.add(svgkit.Line(50, 50 + i*30, 550, 50 + i*30, stroke="#e0e0e0"))
        
    canvas.add(svgkit.Text("Геометрична сітка тотожності Безу", 300, 30, text_anchor="middle", font_size=18, font_family="sans-serif", fill="#333"))
    canvas.add(svgkit.Line(50, 350, 550, 50, stroke="#007bff", stroke_width=2))
    canvas.add(svgkit.Circle(250, 230, 5, fill="#ff0000"))
    canvas.add(svgkit.Text("a*x + b*y = gcd(a,b)", 260, 225, font_size=14, font_family="monospace"))
    
    os.makedirs('img', exist_ok=True)
    canvas.save('img/fig-bezout-identity.svg')

if __name__ == '__main__':
    draw_bezout_identity()

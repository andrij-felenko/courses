import sys
import os

scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
sys.path.insert(0, scripts_dir)
import svgkit

def generate():
    frags = []
    
    # 13 -> 6
    frags.append(svgkit.line(400, 120, 250, 200, color=svgkit.LINE, sw=2))
    frags.append(svgkit.text(325, 150, "sq+mul", size=14, color=svgkit.POS, bold=True))
    
    # 6 -> 3
    frags.append(svgkit.line(250, 220, 400, 300, color=svgkit.LINE, sw=2))
    frags.append(svgkit.text(325, 250, "sq", size=14, color=svgkit.LINE, bold=True))
    
    # 3 -> 1
    frags.append(svgkit.line(400, 320, 550, 400, color=svgkit.LINE, sw=2))
    frags.append(svgkit.text(475, 350, "sq+mul", size=14, color=svgkit.POS, bold=True))
    
    nodes = [
        {"x": 400, "y": 100, "val": "13", "bin": "1101₂"},
        {"x": 250, "y": 200, "val": "6",  "bin": "110₂"},
        {"x": 400, "y": 300, "val": "3",  "bin": "11₂"},
        {"x": 550, "y": 400, "val": "1",  "bin": "1₂"}
    ]
    
    for n in nodes:
        tb, w, h = svgkit.textbox(n["x"], n["y"], f"Показник: {n['val']}\n{n['bin']}", size=14, pad=10, fill=svgkit.FILL, stroke=svgkit.LINE, sw=2, bold=True)
        frags.append(tb)

    os.makedirs('img', exist_ok=True)
    svgkit.render('img/fig-square-and-multiply.svg', 800, 500, *frags, title="Обчислення 3¹³ (показник 13 = 1101 у двійковій системі)")

if __name__ == '__main__':
    generate()

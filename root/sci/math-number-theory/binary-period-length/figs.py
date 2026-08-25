import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def main():
    os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
    out = os.path.join(os.path.dirname(__file__), 'img', 'fig-binary-period.svg')

    frags = []
    
    # Pre-period nodes
    frags.append(circle(100, 200, 20, fill="#f8f9fa"))
    frags.append(text(100, 205, "r₀"))
    frags.append(arrow(120, 200, 180, 200))
    frags.append(text(150, 190, "×2", size=12))

    frags.append(circle(200, 200, 20, fill="#f8f9fa"))
    frags.append(text(200, 205, "r₁"))
    frags.append(arrow(220, 200, 280, 200))
    frags.append(text(250, 190, "×2", size=12))

    # Period nodes
    frags.append(circle(300, 200, 20, fill=FIELD))
    frags.append(text(300, 205, "r₂", color="#ffffff"))
    
    frags.append(arrow(318, 190, 382, 140))
    frags.append(text(350, 155, "×2 mod q", size=12))
    
    frags.append(circle(400, 130, 20, fill=FIELD))
    frags.append(text(400, 135, "r₃", color="#ffffff"))
    
    frags.append(arrow(420, 130, 480, 180))
    frags.append(text(460, 150, "×2", size=12))

    frags.append(circle(500, 200, 20, fill=FIELD))
    frags.append(text(500, 205, "r₄", color="#ffffff"))
    
    frags.append(arrow(485, 212, 420, 260))
    frags.append(text(460, 245, "×2", size=12))

    frags.append(circle(400, 270, 20, fill=FIELD))
    frags.append(text(400, 275, "r₅", color="#ffffff"))

    frags.append(arrow(382, 260, 318, 215))
    frags.append(text(340, 250, "×2", size=12))

    # Labels
    frags.append(text(150, 250, "Передперіод", size=14, italic=True))
    frags.append(text(400, 320, "Період (цикл)", size=14, italic=True))
    frags.append(line(260, 100, 260, 300, dash="5,5", color=MUTED))

    render(out, 600, 400, *frags, title="Діаграма переходів залишків ділення (mod q')")

if __name__ == '__main__':
    main()

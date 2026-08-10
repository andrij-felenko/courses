import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
import svgkit

def make_model_theory_fig():
    os.makedirs("img", exist_ok=True)
    out_path = os.path.join("img", "fig-model-theory.svg")

    frags = []
    
    # Left box: Language L
    frags.append(svgkit.rect(50, 50, 300, 350, fill="#f0f4f8", stroke="#2a4365", sw=2, rx=20))
    frags.append(svgkit.text(200, 85, "Language L", size=24, color="#2a4365", bold=True))
    
    # Right box: Model M (Domain D)
    frags.append(svgkit.rect(450, 50, 300, 350, fill="#fdf0f2", stroke="#9b2c2c", sw=2, rx=20))
    frags.append(svgkit.text(600, 85, "Domain D (Model M)", size=24, color="#9b2c2c", bold=True))

    # Language Elements
    frags.append(svgkit.circle(200, 150, 40, fill="#bee3f8", stroke="#3182ce", sw=2))
    frags.append(svgkit.text(200, 156, "P(x)", size=18, color="#2b6cb0"))
    
    frags.append(svgkit.rect(150, 230, 100, 50, fill="#bee3f8", stroke="#3182ce", sw=2, rx=10))
    frags.append(svgkit.text(200, 260, "f(c)", size=18, color="#2b6cb0"))
    
    frags.append(svgkit.circle(200, 350, 25, fill="#bee3f8", stroke="#3182ce", sw=2))
    frags.append(svgkit.text(200, 356, "c", size=18, color="#2b6cb0"))

    # Domain Elements
    # Relation P^M (represented roughly)
    frags.append('<path d="M 500 150 Q 600 100 700 150 Q 700 200 600 200 Q 500 200 500 150 Z" fill="#fed7d7" stroke="#e53e3e" stroke-width="2"/>')
    frags.append(svgkit.text(600, 156, "Relation P^M", size=18, color="#c53030"))
    
    # Function output f^M(c^M)
    frags.append(svgkit.circle(600, 255, 10, fill="#e53e3e", stroke="#c53030", sw=2))
    frags.append(svgkit.text(600, 285, "f^M(c^M)", size=18, color="#c53030"))
    
    # Constant c^M
    frags.append(svgkit.circle(600, 350, 10, fill="#e53e3e", stroke="#c53030", sw=2))
    frags.append(svgkit.text(600, 380, "c^M", size=18, color="#c53030"))

    # Mapping arrows (Interpretation I) - dashed lines using base svgkit line or custom path
    # I will just use svgkit.arrow and add stroke-dasharray inside if I could, but wait, arrow() doesn't take dash. 
    # I'll use standard custom lines or just straight arrows.
    frags.append(svgkit.arrow(245, 150, 490, 150, color="#a0aec0", sw=3))
    frags.append(svgkit.arrow(255, 255, 580, 255, color="#a0aec0", sw=3))
    frags.append(svgkit.arrow(230, 350, 580, 350, color="#a0aec0", sw=3))
    
    frags.append(svgkit.text(400, 30, "Interpretation I: L \u2192 D", size=20, color="#4a5568", italic=True))

    svgkit.render(out_path, 800, 450, *frags)
    print(f"Generated {out_path}")

if __name__ == "__main__":
    make_model_theory_fig()

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def draw_continuum_hierarchy():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "fig-continuum-hierarchy.svg")
    
    frags = []
    
    # Aleph 0
    frags.append(circle(150, 250, 40, fill="#e1f5fe", stroke="#0288d1"))
    frags.append(text(150, 255, "ℵ₀", size=24, bold=True))
    frags.append(text(150, 310, "Зліченна", size=14))
    
    # Aleph 1
    frags.append(circle(400, 250, 40, fill="#e1f5fe", stroke="#0288d1"))
    frags.append(text(400, 255, "ℵ₁", size=24, bold=True))
    
    # 2^Aleph0 (Continuum)
    frags.append(circle(650, 250, 40, fill="#ffecb3", stroke="#ffa000"))
    frags.append(text(650, 255, "2^(ℵ₀)", size=24, bold=True))
    frags.append(text(650, 310, "Континуум", size=14))
    
    # Arrows and relations
    frags.append(arrow(190, 250, 350, 250))
    frags.append(text(275, 235, "<", size=24, bold=True))
    
    frags.append(arrow(440, 250, 600, 250))
    
    # CH text
    frags.append(text(525, 215, "Гіпотеза континууму", size=12, color="#d32f2f"))
    frags.append(text(525, 235, "2^(ℵ₀) = ℵ₁", size=16, bold=True, color="#d32f2f"))
    frags.append(text(525, 265, "Чи існують кардинали між ними?", size=10, color="#555"))
    
    # Models info
    f_godel, w1, h1 = textbox(200, 400, "Ґедель (1938)\nМодель L: CH не суперечить ZFC\n2^(ℵ₀) = ℵ₁", pad=12, fill="#e8f5e9", stroke="#388e3c")
    frags.append(f_godel)
    
    f_cohen, w2, h2 = textbox(600, 400, "Коен (1963)\nМетод форсингу: ¬CH не суперечить ZFC\n2^(ℵ₀) > ℵ₁", pad=12, fill="#ffebee", stroke="#d32f2f")
    frags.append(f_cohen)
    
    render(out_path, 800, 500, *frags, title="Кардинальна ієрархія та Гіпотеза континууму")
    print(f"Generated {out_path}")

if __name__ == "__main__":
    draw_continuum_hierarchy()

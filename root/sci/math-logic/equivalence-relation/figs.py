import sys
import os

# Add scripts directory to path to import svgkit
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
sys.path.append(scripts_dir)
from svgkit import *

def generate_equivalence_partition():
    frags = []
    
    # Set A boundary
    frags.append('<path d="M 100 250 Q 100 50 400 50 Q 700 50 700 250 Q 700 450 400 450 Q 100 450 100 250 Z" fill="#f8f9fa" stroke="#2c3e50" stroke-width="3"/>')
    
    # Dividers
    frags.append('<path d="M 300 75 Q 350 250 250 425" stroke="#e74c3c" stroke-width="2" stroke-dasharray="5,5" fill="none"/>')
    frags.append('<path d="M 500 75 Q 450 250 550 425" stroke="#e74c3c" stroke-width="2" stroke-dasharray="5,5" fill="none"/>')
    
    # Class 1
    frags.append(text(200, 120, "[x₁]", size=22, bold=True, color="#e74c3c"))
    # Class 2
    frags.append(text(400, 120, "[x₂]", size=22, bold=True, color="#e74c3c"))
    # Class 3
    frags.append(text(600, 120, "[x₃]", size=22, bold=True, color="#e74c3c"))
    
    # Set A label
    frags.append(text(120, 80, "A", size=28, bold=True, italic=True, color="#2c3e50"))
    
    # Elements in Class 1
    frags.append(circle(180, 220, 5, fill="#34495e", stroke="#34495e", sw=1))
    frags.append(text(195, 225, "x₁", size=18, italic=True))
    frags.append(circle(220, 300, 5, fill="#34495e", stroke="#34495e", sw=1))
    frags.append(text(235, 305, "y", size=18, italic=True))
    frags.append(line(185, 225, 215, 295, color="#3498db", sw=1, dash="2,2"))
    
    # Elements in Class 2
    frags.append(circle(400, 250, 5, fill="#34495e", stroke="#34495e", sw=1))
    frags.append(text(415, 255, "x₂", size=18, italic=True))
    frags.append(circle(350, 350, 5, fill="#34495e", stroke="#34495e", sw=1))
    frags.append(text(365, 355, "z", size=18, italic=True))
    frags.append(line(395, 255, 355, 345, color="#3498db", sw=1, dash="2,2"))
    
    # Elements in Class 3
    frags.append(circle(620, 240, 5, fill="#34495e", stroke="#34495e", sw=1))
    frags.append(text(635, 245, "x₃", size=18, italic=True))
    
    os.makedirs('img', exist_ok=True)
    render('img/fig-equivalence-partition.svg', 800, 500, *frags, title="Рис. 1. Розбиття множини A на неперетинні класи еквівалентності")

if __name__ == "__main__":
    generate_equivalence_partition()

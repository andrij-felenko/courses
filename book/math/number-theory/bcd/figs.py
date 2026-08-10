import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import rect, text, line, arrow, render

def generate_bcd_structure():
    frags = []
    
    frags.append(rect(200, 80, 100, 60))
    frags.append(text(250, 115, "9", size=36, bold=True))
    frags.append(rect(350, 80, 100, 60))
    frags.append(text(400, 115, "4", size=36, bold=True))
    frags.append(rect(500, 80, 100, 60))
    frags.append(text(550, 115, "7", size=36, bold=True))
    frags.append(text(620, 115, "₁₀", size=24, bold=True))

    frags.append(arrow(250, 150, 250, 190))
    frags.append(arrow(400, 150, 400, 190))
    frags.append(arrow(550, 150, 550, 190))

    frags.append(rect(200, 200, 100, 60, fill="#e6f7ff", stroke="#0066cc"))
    frags.append(text(250, 235, "1001", size=28, color="#0066cc"))
    frags.append(rect(350, 200, 100, 60, fill="#e6f7ff", stroke="#0066cc"))
    frags.append(text(400, 235, "0100", size=28, color="#0066cc"))
    frags.append(rect(500, 200, 100, 60, fill="#e6f7ff", stroke="#0066cc"))
    frags.append(text(550, 235, "0111", size=28, color="#0066cc"))
    frags.append(text(620, 235, "₂", size=24, bold=True, color="#0066cc"))

    frags.append(text(250, 280, "Тетрада 3", size=16))
    frags.append(text(400, 280, "Тетрада 2", size=16))
    frags.append(text(550, 280, "Тетрада 1", size=16))

    os.makedirs('img', exist_ok=True)
    render('img/fig-bcd-structure.svg', 800, 350, *frags, title="Двійково-десятковий код (BCD): Число 947")

if __name__ == '__main__':
    generate_bcd_structure()

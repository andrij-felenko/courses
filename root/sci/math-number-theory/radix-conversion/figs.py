import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_radix_conversion():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig-radix-conversion.svg")
    
    frags = []
    
    # 1. Horner Scheme (Left part)
    frags.append(text(200, 40, "Схема Горнера: 1101₂ → 13₁₀", size=18, bold=True))
    
    values = ["1", "1", "0", "1"]
    x_start = 80
    y_start = 100
    
    frags.append(circle(x_start, y_start, 20, fill="#e3f2fd", stroke="#1e88e5"))
    frags.append(text(x_start, y_start+5, values[0], size=16))
    
    acc = 1
    for i in range(1, 4):
        x_next = x_start + 80 * i
        frags.append(arrow(x_start + 80*(i-1) + 20, y_start, x_next - 20, y_start))
        frags.append(text(x_start + 80*(i-0.5), y_start - 10, "·2", size=14))
        
        frags.append(text(x_next, y_start + 45, f"+ {values[i]}", size=14))
        frags.append(arrow(x_next, y_start+30, x_next, y_start+20))
        
        acc = acc * 2 + int(values[i])
        
        fill_color = "#e3f2fd" if i < 3 else "#c8e6c9"
        stroke_color = "#1e88e5" if i < 3 else "#43a047"
        frags.append(circle(x_next, y_start, 20, fill=fill_color, stroke=stroke_color))
        frags.append(text(x_next, y_start+5, str(acc), size=16))
    
    frags.append(text(x_start + 240, y_start + 65, "Результат: 13", size=16, color="#2e7d32", bold=True))

    # 2. Direct conversion (Right part)
    frags.append(text(600, 40, "Пряме переведення: 2, 8, 16", size=18, bold=True))
    
    frags.append(text(600, 100, "Двійкова: 0 1 1  0 1 0  1 1 1", size=16))
    
    # Octal grouping
    frags.append(line(525, 110, 525, 120, color="#1565c0"))
    frags.append(line(525, 120, 565, 120, color="#1565c0"))
    frags.append(line(565, 120, 565, 110, color="#1565c0"))
    
    frags.append(line(580, 110, 580, 120, color="#1565c0"))
    frags.append(line(580, 120, 620, 120, color="#1565c0"))
    frags.append(line(620, 120, 620, 110, color="#1565c0"))
    
    frags.append(line(635, 110, 635, 120, color="#1565c0"))
    frags.append(line(635, 120, 675, 120, color="#1565c0"))
    frags.append(line(675, 120, 675, 110, color="#1565c0"))
    
    frags.append(text(600, 140, "Вісімкова: 3 2 7", size=16, color="#1565c0", bold=True))
    
    # Hex grouping
    frags.append(line(505, 75, 505, 65, color="#c62828"))
    frags.append(line(505, 65, 585, 65, color="#c62828"))
    frags.append(line(585, 65, 585, 75, color="#c62828"))
    
    frags.append(line(600, 75, 600, 65, color="#c62828"))
    frags.append(line(600, 65, 675, 65, color="#c62828"))
    frags.append(line(675, 65, 675, 75, color="#c62828"))
    
    frags.append(text(600, 50, "Шістнадцяткова: 6 7", size=16, color="#c62828", bold=True))
    
    # Explanation
    frags.append(text(600, 180, "Триади (3 біти) = 1 вісімкова цифра", size=13, color="#1565c0"))
    frags.append(text(600, 200, "Тетради (4 біти) = 1 шістнадцяткова", size=13, color="#c62828"))
    
    render(out_path, 800, 250, *frags)
    print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_radix_conversion()

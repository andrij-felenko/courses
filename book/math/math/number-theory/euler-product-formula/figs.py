import os
import sys

# Шлях до скриптів
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'scripts')))
from svgkit import *

def draw_euler_product():
    frags = []
    
    # Перший ряд (всі числа)
    frags.append(text(20, 100, "Сума S:", anchor="start", bold=True))
    for i in range(1, 13):
        frags.append(text(120 + i*45, 100, f"1/{i}"))
        if i < 12:
            frags.append(text(120 + i*45 + 22.5, 100, "+"))
    frags.append(text(120 + 13*45 - 20, 100, "..."))
        
    # Другий ряд (без парних)
    frags.append(text(20, 150, "S(1 - 1/2):", anchor="start", bold=True))
    for i in range(1, 13):
        if i % 2 != 0:
            frags.append(text(120 + i*45, 150, f"1/{i}"))
            # plus sign logic: if there is a next odd number
            if i < 11:
                frags.append(text(120 + i*45 + 45, 150, "+"))
    frags.append(text(120 + 12*45, 150, "..."))
            
    # Третій ряд (без кратних 3)
    frags.append(text(20, 200, "S(1 - 1/2)(1 - 1/3):", anchor="start", bold=True))
    for i in range(1, 13):
        if i % 2 != 0 and i % 3 != 0:
            frags.append(text(120 + i*45, 200, f"1/{i}"))
            if i < 11:
                frags.append(text(120 + i*45 + 45, 200, "+")) # just a rough placement
    frags.append(text(120 + 12*45, 200, "..."))
            
    frags.append(text(400, 260, "Залишається лише 1, коли переберемо всі прості", italic=True))
    
    return frags

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), 'img', 'fig-euler-product.svg')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    frags = draw_euler_product()
    render(out_path, 800, 300, *frags, title="Тотожність Ейлера: решето на рядах")
    print("Збережено", out_path)

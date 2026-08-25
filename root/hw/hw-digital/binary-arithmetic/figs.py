import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
from svgkit import *

def make_full_adder_logic():
    out_path = os.path.join(os.path.dirname(__file__), "img", "fig-full-adder-logic.svg")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    frags = []
    
    # Входи A, B, Cin
    frags.append(text(50, 115, "A", bold=True))
    frags.append(text(50, 155, "B", bold=True))
    frags.append(text(50, 235, "Cin", bold=True))
    
    # Вентилі (використовуємо прямокутники з текстом)
    box_w, box_h = 50, 40
    
    # XOR1 (A, B)
    frags.append(rect(150, 115, box_w, box_h, fill="#ecf0f1"))
    frags.append(text(175, 140, "XOR"))
    
    # AND1 (A, B)
    frags.append(rect(150, 180, box_w, box_h, fill="#ecf0f1"))
    frags.append(text(175, 205, "AND"))
    
    # XOR2 (XOR1_out, Cin)
    frags.append(rect(300, 115, box_w, box_h, fill="#ecf0f1"))
    frags.append(text(325, 140, "XOR"))
    
    # AND2 (XOR1_out, Cin)
    frags.append(rect(300, 230, box_w, box_h, fill="#ecf0f1"))
    frags.append(text(325, 255, "AND"))
    
    # OR (AND1_out, AND2_out)
    frags.append(rect(450, 205, box_w, box_h, fill="#ecf0f1"))
    frags.append(text(475, 230, "OR"))
    
    # Виходи S, Cout
    frags.append(text(550, 140, "S", bold=True))
    frags.append(text(550, 230, "Cout", bold=True))
    
    # З'єднання
    # A -> XOR1, AND1
    frags.append(line(70, 115, 150, 125)) # A -> XOR1
    frags.append(line(70, 115, 150, 190)) # A -> AND1
    
    # B -> XOR1, AND1
    frags.append(line(70, 155, 150, 145)) # B -> XOR1
    frags.append(line(70, 155, 150, 210)) # B -> AND1
    
    # XOR1 -> XOR2, AND2
    frags.append(line(200, 135, 300, 125)) # XOR1 -> XOR2
    frags.append(line(200, 135, 300, 240)) # XOR1 -> AND2
    
    # Cin -> XOR2, AND2
    frags.append(line(70, 235, 300, 145)) # Cin -> XOR2
    frags.append(line(70, 235, 300, 260)) # Cin -> AND2
    
    # AND1 -> OR
    frags.append(line(200, 200, 450, 215))
    
    # AND2 -> OR
    frags.append(line(350, 250, 450, 235))
    
    # XOR2 -> S
    frags.append(arrow(350, 135, 530, 135))
    
    # OR -> Cout
    frags.append(arrow(500, 225, 530, 225))
    
    render(out_path, 600, 350, *frags, title="Full Adder Logic Diagram")

if __name__ == "__main__":
    make_full_adder_logic()

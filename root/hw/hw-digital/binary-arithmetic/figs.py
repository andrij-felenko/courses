import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
from svgkit import *

def make_half_full_adder():
    out_path = os.path.join(os.path.dirname(__file__), "img", "fig-half-full-adder.svg")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    frags = []
    
    # Left side: Half Adder
    frags.append(fitbox(20, 30, 260, 260, "", fill="#fbfcfd", stroke=MUTED, rx=8))
    frags.append(text(150, 55, "Напівсуматор (Half Adder)", size=13, bold=True))
    
    frags.append(text(45, 105, "A", size=13, bold=True))
    frags.append(text(45, 155, "B", size=13, bold=True))
    
    # XOR gate
    frags.append(fitbox(110, 90, 60, 32, "XOR", size=12, fill="#eaf2f8", stroke="#2980b9"))
    # AND gate
    frags.append(fitbox(110, 140, 60, 32, "AND", size=12, fill="#fef9e7", stroke="#d4ac0d"))
    
    # Lines for Half Adder
    frags.append(line(60, 105, 110, 100, color=LINE))
    frags.append(line(75, 105, 75, 145, color=LINE))
    frags.append(line(75, 145, 110, 145, color=LINE))
    
    frags.append(line(60, 155, 90, 155, color=LINE))
    frags.append(line(90, 155, 90, 115, color=LINE))
    frags.append(line(90, 115, 110, 115, color=LINE))
    frags.append(line(90, 155, 110, 158, color=LINE))
    
    frags.append(arrow(170, 106, 235, 106, color=LINE))
    frags.append(arrow(170, 156, 235, 156, color=LINE))
    frags.append(text(250, 110, "S", size=13, bold=True, color="#2980b9"))
    frags.append(text(255, 160, "Cout", size=12, bold=True, color="#d4ac0d"))
    
    frags.append(text(150, 215, "S = A ⊕ B", size=12, color="#2980b9"))
    frags.append(text(150, 245, "Cout = A · B", size=12, color="#d4ac0d"))
    
    # Right side: Full Adder
    frags.append(fitbox(300, 30, 440, 260, "", fill="#fbfcfd", stroke=MUTED, rx=8))
    frags.append(text(520, 55, "Повний суматор (Full Adder)", size=13, bold=True))
    
    frags.append(text(320, 95, "A", size=13, bold=True))
    frags.append(text(320, 135, "B", size=13, bold=True))
    frags.append(text(320, 210, "Cin", size=13, bold=True))
    
    # Block HA1
    frags.append(fitbox(360, 85, 80, 65, "HA 1\nXOR+AND", size=11, fill="#edf7ed", stroke="#27ae60"))
    frags.append(line(335, 95, 360, 105, color=LINE))
    frags.append(line(335, 135, 360, 130, color=LINE))
    
    # Block HA2
    frags.append(fitbox(485, 85, 80, 65, "HA 2\nXOR+AND", size=11, fill="#edf7ed", stroke="#27ae60"))
    frags.append(line(440, 105, 485, 105, color=LINE))
    frags.append(text(462, 97, "S1", size=10, color=MUTED))
    
    frags.append(line(335, 210, 465, 210, color=LINE))
    frags.append(line(465, 210, 465, 130, color=LINE))
    frags.append(line(465, 130, 485, 130, color=LINE))
    
    # OR gate for carries
    frags.append(fitbox(605, 155, 55, 40, "OR", size=12, fill="#fef9e7", stroke="#d4ac0d"))
    
    frags.append(line(440, 135, 455, 135, color=LINE))
    frags.append(line(455, 135, 455, 165, color=LINE))
    frags.append(line(455, 165, 605, 165, color=LINE))
    frags.append(text(475, 158, "C1", size=10, color=MUTED))
    
    frags.append(line(565, 135, 580, 135, color=LINE))
    frags.append(line(580, 135, 580, 185, color=LINE))
    frags.append(line(580, 185, 605, 185, color=LINE))
    frags.append(text(585, 158, "C2", size=10, color=MUTED))
    
    frags.append(arrow(565, 105, 700, 105, color=LINE))
    frags.append(text(715, 109, "S", size=13, bold=True, color="#2980b9"))
    
    frags.append(arrow(660, 175, 700, 175, color=LINE))
    frags.append(text(718, 179, "Cout", size=12, bold=True, color="#d4ac0d"))
    
    frags.append(text(520, 255, "S = A ⊕ B ⊕ Cin,   Cout = (A · B) + Cin · (A ⊕ B)", size=11, color=INK))
    
    render(out_path, 760, 310, *frags)

def make_ripple_carry_adder():
    out_path = os.path.join(os.path.dirname(__file__), "img", "fig-ripple-carry-adder.svg")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    frags = []
    
    stages = [
        (3, 70, "FA 3 (MSB)", "A3", "B3", "S3", "C4", "C3"),
        (2, 220, "FA 2", "A2", "B2", "S2", "C3", "C2"),
        (1, 370, "FA 1", "A1", "B1", "S1", "C2", "C1"),
        (0, 520, "FA 0 (LSB)", "A0", "B0", "S0", "C1", "C0")
    ]
    
    for idx, x, label, inA, inB, outS, carryOut, carryIn in stages:
        # FA Box
        frags.append(fitbox(x, 90, 100, 110, f"{label}\n\nПовний\nсуматор", size=11, fill="#f4f6f8", stroke="#2c3e50"))
        
        # Inputs A, B from top
        frags.append(arrow(x + 25, 45, x + 25, 90, color=LINE))
        frags.append(arrow(x + 75, 45, x + 75, 90, color=LINE))
        frags.append(text(x + 25, 38, inA, size=11, bold=True))
        frags.append(text(x + 75, 38, inB, size=11, bold=True))
        
        # Sum S output to bottom
        frags.append(arrow(x + 50, 200, x + 50, 245, color="#2980b9"))
        frags.append(text(x + 50, 260, outS, size=12, bold=True, color="#2980b9"))
    
    # Carry chain connections:
    # C0 in to FA0
    frags.append(arrow(680, 145, 620, 145, color="#c0392b"))
    frags.append(text(655, 135, "C0 (Cin)", size=11, bold=True, color="#c0392b"))
    
    # FA0 to FA1
    frags.append(arrow(520, 145, 470, 145, color="#c0392b"))
    frags.append(text(495, 135, "C1", size=11, bold=True, color="#c0392b"))
    
    # FA1 to FA2
    frags.append(arrow(370, 145, 320, 145, color="#c0392b"))
    frags.append(text(345, 135, "C2", size=11, bold=True, color="#c0392b"))
    
    # FA2 to FA3
    frags.append(arrow(220, 145, 170, 145, color="#c0392b"))
    frags.append(text(195, 135, "C3", size=11, bold=True, color="#c0392b"))
    
    # FA3 to C4 (Cout)
    frags.append(arrow(70, 145, 20, 145, color="#c0392b"))
    frags.append(text(40, 135, "C4", size=11, bold=True, color="#c0392b"))
    
    # Critical path indicator
    frags.append(line(680, 175, 20, 175, color="#c0392b", sw=2, dash="4,4"))
    frags.append(text(350, 290, "Критичний шлях поширення переносу (Ripple Carry): t_delay = N · t_carry", size=12, bold=True, color="#c0392b"))
    
    render(out_path, 720, 320, *frags)

def make_cla_4bit():
    out_path = os.path.join(os.path.dirname(__file__), "img", "fig-cla-4bit.svg")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    frags = []
    
    # Top: 4 bit-level GP generators
    xs = [560, 410, 260, 110]
    for i, x in enumerate(xs):
        frags.append(fitbox(x, 40, 90, 50, f"GP {i}\nPi, Gi", size=11, fill="#e8f8f5", stroke="#16a085"))
        # inputs Ai, Bi
        frags.append(arrow(x + 25, 10, x + 25, 40, color=LINE))
        frags.append(arrow(x + 65, 10, x + 65, 40, color=LINE))
        frags.append(text(x + 25, 8, f"A{i}", size=10, bold=True))
        frags.append(text(x + 65, 8, f"B{i}", size=10, bold=True))
        
        # P and G down to CLA block
        frags.append(arrow(x + 45, 90, x + 45, 135, color="#16a085"))
        frags.append(text(x + 45, 112, f"P{i},G{i}", size=10, color="#16a085"))
    
    # Center: CLA Carry Generator Block (CLAU)
    frags.append(fitbox(80, 135, 600, 60, "Блок паралельного формування переносу (CLAU)\nОбчислення C1, C2, C3, C4 за 2 рівні логіки (AND-OR)", size=12, fill="#fef5e7", stroke="#d35400", bold=True))
    
    # C0 in from right
    frags.append(arrow(730, 165, 680, 165, color="#c0392b"))
    frags.append(text(705, 155, "C0", size=11, bold=True, color="#c0392b"))
    
    # Outputs of CLA down to Sum generators
    for i, x in enumerate(xs):
        # Sum generator box
        frags.append(fitbox(x, 235, 90, 45, f"XOR\nS{i} = P{i} ⊕ C{i}", size=10, fill="#ebf5fb", stroke="#2980b9"))
        
        # Ci arrow from CLAU down to Sum
        frags.append(arrow(x + 45, 195, x + 45, 235, color="#c0392b"))
        frags.append(text(x + 30, 215, f"C{i}", size=10, bold=True, color="#c0392b"))
        
        # Sum output
        frags.append(arrow(x + 45, 280, x + 45, 310, color="#2980b9"))
        frags.append(text(x + 45, 325, f"S{i}", size=12, bold=True, color="#2980b9"))
    
    # C4 out from CLAU to left
    frags.append(arrow(80, 165, 30, 165, color="#c0392b"))
    frags.append(text(50, 155, "C4", size=11, bold=True, color="#c0392b"))
    
    render(out_path, 760, 345, *frags)

def make_adder_subtractor_alu():
    out_path = os.path.join(os.path.dirname(__file__), "img", "fig-adder-subtractor-alu.svg")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    frags = []
    
    # Mode control line (Sub / Add)
    frags.append(text(60, 30, "Sub / Add", size=12, bold=True, color="#8e44ad"))
    frags.append(line(110, 30, 680, 30, color="#8e44ad", sw=2))
    
    # 4 slices
    xs = [540, 400, 260, 120]
    for i, x in enumerate(xs):
        # Slice bounding box
        frags.append(fitbox(x - 20, 55, 125, 180, "", fill="#fcfcfc", stroke="#bdc3c7", rx=6))
        frags.append(text(x + 40, 72, f"Розряд {i}", size=10, color=MUTED))
        
        # Input B XOR with Sub
        frags.append(fitbox(x + 50, 95, 45, 30, "XOR", size=10, fill="#f5eef8", stroke="#8e44ad"))
        frags.append(arrow(x + 72, 55, x + 72, 95, color=LINE))
        frags.append(text(x + 72, 48, f"B{i}", size=10, bold=True))
        
        # Mode connection into XOR
        frags.append(line(x + 55, 30, x + 55, 95, color="#8e44ad"))
        
        # Full Adder box
        frags.append(fitbox(x - 12, 140, 105, 50, f"FA {i}", size=11, fill="#eaf2f8", stroke="#2980b9", bold=True))
        
        # Input A into FA
        frags.append(arrow(x - 2, 55, x - 2, 140, color=LINE))
        frags.append(text(x - 2, 48, f"A{i}", size=10, bold=True))
        
        # B_inv into FA
        frags.append(arrow(x + 72, 125, x + 72, 140, color=LINE))
        
        # Sum out
        frags.append(arrow(x + 40, 190, x + 40, 220, color="#2980b9"))
        frags.append(text(x + 40, 230, f"S{i}", size=11, bold=True, color="#2980b9"))
    
    # Mode line feeds into C0 (Cin of FA0)
    frags.append(line(660, 30, 660, 165, color="#8e44ad"))
    frags.append(arrow(660, 165, 635, 165, color="#8e44ad"))
    frags.append(text(650, 155, "Cin = Sub", size=10, color="#8e44ad"))
    
    # Ripple carry between slices
    frags.append(arrow(528, 165, 495, 165, color="#c0392b"))
    frags.append(arrow(388, 165, 355, 165, color="#c0392b"))
    frags.append(arrow(248, 165, 215, 165, color="#c0392b"))
    
    # Overflow logic: V = C3_in XOR C3_out
    frags.append(fitbox(25, 145, 55, 35, "XOR", size=11, fill="#fadbd8", stroke="#c0392b"))
    frags.append(line(230, 165, 230, 130, color="#c0392b"))
    frags.append(line(230, 130, 45, 130, color="#c0392b"))
    frags.append(arrow(45, 130, 45, 145, color="#c0392b"))
    
    frags.append(arrow(108, 165, 65, 165, color="#c0392b"))
    
    # Flags output
    frags.append(arrow(25, 162, 5, 162, color="#c0392b"))
    frags.append(text(22, 135, "V (Overflow)", size=10, bold=True, color="#c0392b"))
    
    frags.append(arrow(108, 178, 5, 178, color="#c0392b"))
    frags.append(text(25, 202, "C (Carry)", size=10, bold=True, color="#c0392b"))
    
    # NOR for Zero flag
    frags.append(fitbox(180, 255, 380, 45, "Вентиль NOR над усіма бітами S[3:0] ──▶  Прапорець Z (Zero)\nСтарший біт S[3] ──▶  Прапорець N (Negative)", size=11, fill="#fcf3cf", stroke="#b7950b"))
    
    render(out_path, 730, 320, *frags)

if __name__ == "__main__":
    make_half_full_adder()
    make_ripple_carry_adder()
    make_cla_4bit()
    make_adder_subtractor_alu()

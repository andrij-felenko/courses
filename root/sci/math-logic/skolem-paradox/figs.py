import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.abspath(os.path.join(current_dir, "../../../../scripts"))
sys.path.append(scripts_dir)

from svgkit import *

def main():
    img_dir = os.path.join(current_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "fig-skolem-paradox.svg")
    
    frags = []
    
    # V (Зовнішній всесвіт)
    frags.append(rect(10, 10, 780, 420, fill="#f8f9fa", stroke="#6c757d", sw=2, rx=10))
    frags.append(text(400, 35, "Зовнішній всесвіт (V)", size=18, bold=True, color="#343a40"))
    frags.append(text(400, 60, "Тут існують усі функції, включно з бієкцією f", size=14, color="#495057"))

    # M (Зліченна модель)
    frags.append(rect(30, 90, 520, 320, fill="#e9ecef", stroke="#0d6efd", sw=2, rx=10))
    frags.append(text(290, 115, "Зліченна модель (M)", size=16, bold=True, color="#0d6efd"))
    frags.append(text(290, 140, "f ∉ M", size=14, bold=True, color="#dc3545"))
    
    # Множина N
    frags.append(rect(60, 170, 160, 220, fill="#d1e7dd", stroke="#198754", sw=1, rx=5))
    frags.append(text(140, 195, "N", size=18, bold=True, color="#198754"))
    
    frags.append(circle(140, 230, 4, fill="#198754", stroke="#198754"))
    frags.append(circle(140, 270, 4, fill="#198754", stroke="#198754"))
    frags.append(circle(140, 310, 4, fill="#198754", stroke="#198754"))
    frags.append(text(140, 340, "0, 1, 2...", size=14, color="#198754"))

    # Множина X (P_M(N))
    frags.append(rect(350, 170, 160, 220, fill="#fff3cd", stroke="#ffc107", sw=1, rx=5))
    frags.append(text(430, 195, "X = P_M(N)", size=18, bold=True, color="#ffc107"))
    
    frags.append(circle(430, 230, 4, fill="#ffc107", stroke="#ffc107"))
    frags.append(circle(430, 270, 4, fill="#ffc107", stroke="#ffc107"))
    frags.append(circle(430, 310, 4, fill="#ffc107", stroke="#ffc107"))
    frags.append(text(430, 340, "Підмножини", size=14, color="#ffc107"))
    
    # Cross inside M (no bijection)
    frags.append(line(240, 270, 330, 270, color="#dc3545", sw=2, dash="5,5"))
    frags.append(text(285, 260, "Немає бієкції", size=14, color="#dc3545"))
    frags.append(text(285, 277, "X", size=24, bold=True, color="#dc3545"))

    # Bijection f outside M
    frags.append(rect(580, 170, 180, 220, fill="#cfe2ff", stroke="#0a58ca", sw=1, rx=5))
    frags.append(text(670, 195, "f (Бієкція)", size=16, bold=True, color="#0a58ca"))
    frags.append(text(670, 250, "Існує у V", size=14, color="#0a58ca"))
    
    # Path for f
    frags.append(f'<path d="M 140 170 Q 380 70 670 170" stroke="#0a58ca" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
    frags.append(f'<path d="M 670 390 Q 550 450 430 390" stroke="#0a58ca" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
    
    frags.append(text(400, 85, "Функція існує лише ззовні моделі", size=14, color="#0a58ca"))
    
    render(out_path, 800, 450, *frags)
    print(f"Generated {out_path}")

if __name__ == "__main__":
    main()

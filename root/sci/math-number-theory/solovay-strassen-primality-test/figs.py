import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_pipeline():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig-solovay-strassen-pipeline.svg")
    
    frags = []
    
    # Title
    frags.append(text(420, 35, "Алгоритм перевірки простоти Соловея–Штрассена", size=20, bold=True, color="#1a1a1a"))
    
    # Start block
    b_start, w_start, h_start = textbox(420, 85, "Вхід: непарне n ≥ 3, кількість раундів k", size=13, fill="#e8f4f8", stroke="#2b7b9c", sw=2, bold=True)
    frags.append(b_start)
    
    # Arrow to loop
    frags.append(arrow(420, 85 + h_start/2, 420, 140, color="#2b7b9c", sw=1.5))
    
    # Loop block
    b_loop, w_loop, h_loop = textbox(420, 165, "Цикл від i = 1 до k: випадкова основа a ∈ [2, n - 1]", size=13, fill="#f4f6f8", stroke="#333333", sw=1.5)
    frags.append(b_loop)
    
    # Arrow to GCD check
    frags.append(arrow(420, 165 + h_loop/2, 420, 220, color="#333333", sw=1.5))
    
    # Decision 1: gcd(a, n) > 1
    b_gcd, w_gcd, h_gcd = textbox(420, 250, "Обчислення g = НСД(a, n)\nЧи g > 1 ?", size=13, fill="#fff7ed", stroke="#d97706", sw=1.5, bold=True)
    frags.append(b_gcd)
    
    # Branch 1 YES -> Composite
    frags.append(arrow(420 + w_gcd/2, 250, 640, 250, color="#c0392b", sw=1.8))
    frags.append(text(575, 238, "Так (НСД дільник)", size=11, color="#c0392b", bold=True, anchor="middle"))
    b_comp1, w_comp1, h_comp1 = textbox(730, 250, "Складене число\n(знайдено дільник g)", size=12, fill="#fde8e8", stroke="#c0392b", sw=2, color="#c0392b", bold=True)
    frags.append(b_comp1)
    
    # Arrow down NO
    frags.append(arrow(420, 250 + h_gcd/2, 420, 315, color="#27ae60", sw=1.5))
    frags.append(text(430, 290, "Ні", size=11, color="#27ae60", bold=True, anchor="start"))
    
    # Calculation block
    b_calc, w_calc, h_calc = textbox(420, 350, "Обчислити: x = a^((n-1)/2) mod n\nта символ Якобі: J = (a / n) mod n", size=13, fill="#f0fdf4", stroke="#27ae60", sw=1.5)
    frags.append(b_calc)
    
    # Arrow to Decision 2
    frags.append(arrow(420, 350 + h_calc/2, 420, 410, color="#333333", sw=1.5))
    
    # Decision 2: x != J (mod n)
    b_eq, w_eq, h_eq = textbox(420, 440, "Порівняння конгруентності:\nЧи x ≡ J (mod n) ?", size=13, fill="#fff7ed", stroke="#d97706", sw=1.5, bold=True)
    frags.append(b_eq)
    
    # Branch 2 NO -> Composite (Euler witness)
    frags.append(arrow(420 + w_eq/2, 440, 640, 440, color="#c0392b", sw=1.8))
    frags.append(text(575, 428, "Ні (свідок Ейлера)", size=11, color="#c0392b", bold=True, anchor="middle"))
    b_comp2, w_comp2, h_comp2 = textbox(730, 440, "Складене число\n(a — свідок Ейлера)", size=12, fill="#fde8e8", stroke="#c0392b", sw=2, color="#c0392b", bold=True)
    frags.append(b_comp2)
    
    # Arrow down YES -> Next iteration / Success
    frags.append(arrow(420, 440 + h_eq/2, 420, 505, color="#27ae60", sw=1.5))
    frags.append(text(430, 480, "Так (брехун Ейлера)", size=11, color="#27ae60", bold=True, anchor="start"))
    
    # Success block
    b_succ, w_succ, h_succ = textbox(420, 535, "Пройдено k раундів успішно:\nЙмовірно просте число (помилка ≤ 2⁻ᵏ)", size=13, fill="#ecfdf5", stroke="#059669", sw=2, color="#059669", bold=True)
    frags.append(b_succ)
    
    render(out_path, 860, 590, *frags, title="Алгоритм Соловея–Штрассена")
    print(f"Generated {out_path}")

def generate_subgroup():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig-euler-liars-subgroup.svg")
    
    frags = []
    
    # Title
    frags.append(text(400, 35, "Розподіл брехунів та свідків Ейлера в групі (ℤ/nℤ)*", size=20, bold=True, color="#1a1a1a"))
    
    # Outer rectangle: Multiplicative group (Z/nZ)*
    frags.append(rect(60, 70, 680, 280, fill="#f4f6f8", stroke="#4b5563", sw=2, rx=12))
    frags.append(text(80, 95, "Мультиплікативна група (ℤ/nℤ)*  [розмір φ(n)]", size=14, color="#1f2937", bold=True, anchor="start"))
    
    # Left inner box: Subgroup of Euler liars E_n
    frags.append(rect(90, 115, 300, 210, fill="#dbeafe", stroke="#2563eb", sw=2, rx=10))
    frags.append(text(240, 145, "Підгрупа брехунів Ейлера Eₙ", size=14, color="#1e40af", bold=True))
    frags.append(text(240, 175, "Основи a, для яких:", size=12, color="#1e3a8a"))
    frags.append(text(240, 198, "a^((n-1)/2) ≡ (a/n) (mod n)", size=13, color="#1e40af", bold=True))
    frags.append(text(240, 240, "Розмір |Eₙ| ≤ φ(n) / 2", size=13, color="#1d4ed8", bold=True))
    frags.append(text(240, 270, "Ніколи не перевищує 50%", size=11, color="#2563eb", italic=True))
    frags.append(text(240, 290, "елементів групи для складеного n", size=11, color="#2563eb", italic=True))
    
    # Right inner box: Set of Euler witnesses W_n
    frags.append(rect(410, 115, 310, 210, fill="#fef3c7", stroke="#d97706", sw=2, rx=10))
    frags.append(text(565, 145, "Множина свідків Ейлера Wₙ", size=14, color="#92400e", bold=True))
    frags.append(text(565, 175, "Основи a, для яких:", size=12, color="#78350f"))
    frags.append(text(565, 198, "a^((n-1)/2) ≢ (a/n) (mod n)", size=13, color="#92400e", bold=True))
    frags.append(text(565, 240, "Розмір |Wₙ| ≥ φ(n) / 2", size=13, color="#b45309", bold=True))
    frags.append(text(565, 270, "Гарантовано принаймні 50%", size=11, color="#d97706", italic=True))
    frags.append(text(565, 290, "основ є свідками складеності", size=11, color="#d97706", italic=True))
    
    # Bottom explanation box
    b_exp, w_exp, h_exp = textbox(400, 395, "Оскільки Eₙ є ВЛАСНОЮ підгрупою в (ℤ/nℤ)* для складеного n,\nза теоремою Лагранжа її порядок ділить порядок групи: |Eₙ| ≤ φ(n)/2 ≤ (n-1)/2.\nЙмовірність помилки за один раунд ≤ 1/2.", size=12, fill="#ecfdf5", stroke="#059669", sw=1.5, color="#065f46")
    frags.append(b_exp)
    
    render(out_path, 800, 460, *frags, title="Підгрупа брехунів Ейлера")
    print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_pipeline()
    generate_subgroup()

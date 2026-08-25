import sys
import os

# Add scripts directory to path (4 levels up from topic directory)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))

try:
    from svgkit import render, rect, line, text, circle, arrow, mtext, fitbox, POS, NEG, FIELD, INK, MUTED, FILL
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

IMG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))


def draw_hensel_tree():
    frags = []
    
    # Header box
    frags.append(rect(40, 15, 640, 35, rx=6, fill="#f8f9fa", stroke="#343a40", sw=1.5))
    frags.append(text(360, 38, "Дерево підйому розв'язку: f(x) ≡ 0 (mod pᵏ)", size=14, bold=True, color="#212529", anchor="middle"))

    # Level 1: Modulo p
    frags.append(rect(30, 70, 660, 65, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(45, 95, "Модуль p¹:", size=13, bold=True, color="#1864ab", anchor="left"))
    frags.append(text(45, 115, "f'(a₁) ≢ 0 (mod p)", size=11, color="#1c7ed6", anchor="left"))
    
    # Root a1 box
    frags.append(rect(300, 80, 200, 45, rx=6, fill="#ffffff", stroke="#1c7ed6", sw=2.0))
    frags.append(text(400, 107, "a₁ (mod p)", size=13, bold=True, color="#1864ab", anchor="middle"))

    # Arrows level 1 to level 2
    frags.append(arrow(400, 125, 400, 165, color="#1c7ed6", sw=2.0))
    frags.append(text(415, 150, "t₁ ≡ -f(a₁)/p · (f'(a₁))⁻¹ (mod p)", size=10, bold=True, color="#1864ab", anchor="left"))

    # Level 2: Modulo p^2
    frags.append(rect(30, 165, 660, 65, rx=6, fill="#e6fcf5", stroke="#0ca678", sw=1.5))
    frags.append(text(45, 190, "Модуль p²:", size=13, bold=True, color="#099268", anchor="left"))
    frags.append(text(45, 210, "a₂ = a₁ + t₁·p", size=11, color="#0ca678", anchor="left"))
    
    # Root a2 box
    frags.append(rect(280, 175, 240, 45, rx=6, fill="#ffffff", stroke="#0ca678", sw=2.0))
    frags.append(text(400, 202, "a₂ = a₁ + t₁·p (mod p²)", size=13, bold=True, color="#099268", anchor="middle"))

    # Arrows level 2 to level 3
    frags.append(arrow(400, 220, 400, 260, color="#0ca678", sw=2.0))
    frags.append(text(415, 245, "t₂ ≡ -f(a₂)/p² · (f'(a₂))⁻¹ (mod p)", size=10, bold=True, color="#099268", anchor="left"))

    # Level 3: Modulo p^3
    frags.append(rect(30, 260, 660, 65, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(45, 285, "Модуль p³:", size=13, bold=True, color="#e67700", anchor="left"))
    frags.append(text(45, 305, "a₃ = a₂ + t₂·p²", size=11, color="#f59f00", anchor="left"))
    
    # Root a3 box
    frags.append(rect(260, 270, 280, 45, rx=6, fill="#ffffff", stroke="#f59f00", sw=2.0))
    frags.append(text(400, 297, "a₃ = a₂ + t₂·p² (mod p³)", size=13, bold=True, color="#e67700", anchor="middle"))

    # Dotted arrow down to p-adic limit
    frags.append(line(400, 315, 400, 350, color="#868e96", sw=2.0, dash="4,4"))
    frags.append(arrow(400, 350, 400, 360, color="#868e96", sw=2.0))
    
    # Limit box (Z_p)
    frags.append(rect(240, 360, 320, 40, rx=6, fill="#f1f3f5", stroke="#495057", sw=1.5))
    frags.append(text(400, 385, "Границя в Z_p: α = a₁ + t₁·p + t₂·p² + ...", size=12, bold=True, color="#212529", anchor="middle"))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-hensel-tree.svg'), 720, 420, *frags, title="Дерево підйому розв'язку Гензеля за модулями p^k")


def draw_newton_p_adic_analogy():
    frags = []
    
    # Header
    frags.append(rect(30, 15, 680, 35, rx=6, fill="#f8f9fa", stroke="#343a40", sw=1.5))
    frags.append(text(370, 38, "Аналогія: Дійсний метод Ньютона vs p-Адичний підйом Гензеля", size=13, bold=True, color="#212529", anchor="middle"))

    # Left Column: Real Analysis (Newton-Raphson)
    frags.append(rect(30, 65, 330, 280, rx=6, fill="#fff5f5", stroke="#f03e3e", sw=1.5))
    frags.append(text(195, 90, "Дійсний аналіз (R)", size=14, bold=True, color="#c92a2a", anchor="middle"))
    
    # Formula real
    frags.append(rect(50, 105, 290, 45, rx=4, fill="#ffffff", stroke="#f03e3e", sw=1.0))
    frags.append(text(195, 132, "x_{n+1} = x_n - f(x_n) / f'(x_n)", size=12, bold=True, color="#c92a2a", anchor="middle"))
    
    # Properties real
    frags.append(text(50, 170, "• Метрика: |x - y| (евклідова)", size=11, color="#495057", anchor="left"))
    frags.append(text(50, 195, "• Неперервна геометрична пряма", size=11, color="#495057", anchor="left"))
    frags.append(text(50, 220, "• Дотична пряма в точці x_n", size=11, color="#495057", anchor="left"))
    frags.append(text(50, 245, "• Квадратична збіжність за кількістю", size=11, color="#495057", anchor="left"))
    frags.append(text(62, 265, "правильних десяткових цифр", size=11, color="#495057", anchor="left"))
    frags.append(text(50, 295, "Умова: f'(x_n) ≠ 0 на R", size=11, bold=True, color="#c92a2a", anchor="left"))

    # Right Column: p-adic Analysis (Hensel)
    frags.append(rect(380, 65, 330, 280, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(545, 90, "p-Адична арифметика (Z_p)", size=14, bold=True, color="#1864ab", anchor="middle"))
    
    # Formula p-adic
    frags.append(rect(400, 105, 290, 45, rx=4, fill="#ffffff", stroke="#1c7ed6", sw=1.0))
    frags.append(text(545, 132, "a_{k+1} ≡ a_k - f(a_k)·(f'(a_k))⁻¹ (mod p^{k+1})", size=11, bold=True, color="#1864ab", anchor="middle"))
    
    # Properties p-adic
    frags.append(text(400, 170, "• Метрика: |x - y|_p = p⁻ᵛ (арифметична)", size=11, color="#495057", anchor="left"))
    frags.append(text(400, 195, "• Дискретне кільце лишків Z/pᵏZ", size=11, color="#495057", anchor="left"))
    frags.append(text(400, 220, "• Диференціал Тейлора за модулем pᵏ⁺¹", size=11, color="#495057", anchor="left"))
    frags.append(text(400, 245, "• Лінійний / квадратичний підйом", size=11, color="#495057", anchor="left"))
    frags.append(text(412, 265, "p-адичних розрядів числа", size=11, color="#495057", anchor="left"))
    frags.append(text(400, 295, "Умова: f'(a₁) ≢ 0 (mod p)", size=11, bold=True, color="#1864ab", anchor="left"))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-newton-p-adic-analogy.svg'), 740, 360, *frags, title="Порівняння методу Ньютона та підйому Гензеля")


def draw_factorization_lift_pipeline():
    frags = []
    
    # Header
    frags.append(rect(30, 15, 680, 35, rx=6, fill="#f8f9fa", stroke="#343a40", sw=1.5))
    frags.append(text(370, 38, "Конвеєр факторизації многочленів у Z[x] через підйом Гензеля", size=13, bold=True, color="#212529", anchor="middle"))

    # Step 1: Input polynomial f(x) in Z[x]
    frags.append(rect(30, 70, 190, 80, rx=6, fill="#edf2ff", stroke="#4c6ef5", sw=1.5))
    frags.append(text(125, 95, "1. Вхідний багаточлен", size=12, bold=True, color="#364fc7", anchor="middle"))
    frags.append(text(125, 115, "f(x) ∈ Z[x]", size=12, bold=True, color="#364fc7", anchor="middle"))
    frags.append(text(125, 135, "Ступінь n, бесквадратний", size=10, color="#495057", anchor="middle"))

    # Arrow 1 -> 2
    frags.append(arrow(220, 110, 260, 110, color="#4c6ef5", sw=1.8))

    # Step 2: Factorization in F_p
    frags.append(rect(260, 70, 200, 80, rx=6, fill="#e6fcf5", stroke="#0ca678", sw=1.5))
    frags.append(text(360, 95, "2. Розклад у полі F_p", size=12, bold=True, color="#099268", anchor="middle"))
    frags.append(text(360, 115, "f(x) ≡ g₁(x)·h₁(x) (mod p)", size=11, bold=True, color="#099268", anchor="middle"))
    frags.append(text(360, 135, "НСД(g₁, h₁) ≡ 1 (mod p)", size=10, color="#495057", anchor="middle"))

    # Arrow 2 -> 3
    frags.append(arrow(460, 110, 500, 110, color="#0ca678", sw=1.8))

    # Step 3: Hensel Lifting modulo p^k
    frags.append(rect(500, 70, 210, 80, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(605, 95, "3. Підйом Гензеля", size=12, bold=True, color="#e67700", anchor="middle"))
    frags.append(text(605, 115, "f(x) ≡ g_k(x)·h_k(x) (mod pᵏ)", size=11, bold=True, color="#e67700", anchor="middle"))
    frags.append(text(605, 135, "До межі pᵏ > 2·Bound(f)", size=10, color="#495057", anchor="middle"))

    # Down arrow from Step 3 to Step 4
    frags.append(arrow(605, 150, 605, 190, color="#f59f00", sw=1.8))

    # Step 4: Recombination with Mignotte bound
    frags.append(rect(260, 190, 450, 75, rx=6, fill="#fff3bf", stroke="#f59f00", sw=1.5))
    frags.append(text(485, 215, "4. Комбінування множників за межею Міньотта (Mignotte Bound)", size=12, bold=True, color="#d9480f", anchor="middle"))
    frags.append(text(485, 235, "Перевірка комбінацій g_k(x)·h_k(x) mod pᵏ на точне ділення f(x) у Z[x]", size=11, color="#495057", anchor="middle"))
    frags.append(text(485, 252, "Відсікання подібних множників та відновлення справжніх коефіцієнтів", size=10, color="#868e96", anchor="middle"))

    # Down arrow to Step 5
    frags.append(arrow(485, 265, 485, 295, color="#d9480f", sw=1.8))

    # Step 5: Final factorization in Z[x]
    frags.append(rect(330, 295, 310, 45, rx=6, fill="#ebfbee", stroke="#2b8a3e", sw=2.0))
    frags.append(text(485, 322, "Результат: f(x) = P₁(x)·P₂(x)...·P_r(x) у Z[x]", size=13, bold=True, color="#2b8a3e", anchor="middle"))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-factorization-lift-pipeline.svg'), 740, 360, *frags, title="Конвеєр розкладу многочленів на множники за допомогою підйому Гензеля")


if __name__ == '__main__':
    draw_hensel_tree()
    draw_newton_p_adic_analogy()
    draw_factorization_lift_pipeline()

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, arrow
except ImportError:
    print("ERROR: svgkit not found.")
    sys.exit(1)

def draw_gerono_cases():
    frags = []
    
    # Title
    frags.append(rect(10, 10, 780, 40, rx=6, fill="#f8f9fa", stroke="#ced4da", sw=1.5))
    frags.append(text(400, 35, "Класифікація діофантового рівняння xᵃ - yᵇ = 1 та область теореми Жероно", size=14, bold=True, color="#212529", anchor="middle"))

    # Main container x^a - y^b = 1
    frags.append(rect(20, 65, 760, 275, rx=8, fill="#ffffff", stroke="#adb5bd", sw=1.5))

    # Branch 1: Gerono Domain (Quadratic exponents)
    frags.append(rect(40, 85, 340, 235, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(210, 110, "Область теореми Жероно (a = 2 або b = 2)", size=13, bold=True, color="#1864ab", anchor="middle"))

    # Sub-branch 1A: Lebesgue branch (b = 2)
    frags.append(rect(55, 125, 310, 80, rx=5, fill="#ffffff", stroke="#74c0fc", sw=1.2))
    frags.append(text(210, 145, "Випадок b = 2: xᵃ - y² = 1 (a ≥ 2)", size=11, bold=True, color="#1971c2", anchor="middle"))
    frags.append(text(210, 165, "Теорема Лебега (1850)", size=10, bold=True, color="#495057", anchor="middle"))
    frags.append(text(210, 185, "Результат: ЖОДНОГО розв'язку в N (x,y ≥ 2)", size=10, bold=True, color="#e03131", anchor="middle"))

    # Sub-branch 1B: Gerono base branch (a = 2)
    frags.append(rect(55, 225, 310, 80, rx=5, fill="#ffffff", stroke="#74c0fc", sw=1.2))
    frags.append(text(210, 245, "Випадок a = 2: x² - yᵇ = 1 (b ≥ 2)", size=11, bold=True, color="#1971c2", anchor="middle"))
    frags.append(text(210, 265, "Теорема Жероно (1870)", size=10, bold=True, color="#495057", anchor="middle"))
    frags.append(text(210, 285, "Єдиний розв'язок: 3² - 2³ = 1 (x=3, y=2, b=3)", size=10, bold=True, color="#2b8a3e", anchor="middle"))

    # Branch 2: Mihailescu Domain (Higher odd exponents)
    frags.append(rect(420, 85, 340, 235, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(590, 110, "Загальна гіпотеза Каталана (a, b ≥ 3)", size=13, bold=True, color="#f59f00", anchor="middle"))

    frags.append(rect(435, 125, 310, 180, rx=5, fill="#ffffff", stroke="#ffe066", sw=1.2))
    frags.append(text(590, 150, "Рівняння xᵖ - y𝑞 = 1 (p, q — непарні прості)", size=11, bold=True, color="#d9480f", anchor="middle"))
    frags.append(text(590, 175, "Доведено П. Міхайлеску (2002)", size=11, color="#495057", anchor="middle"))
    frags.append(text(590, 205, "Використано кругові поля,", size=10, color="#495057", anchor="middle"))
    frags.append(text(590, 225, "числа класів та модулярні межі", size=10, color="#495057", anchor="middle"))
    frags.append(text(590, 260, "Результат: ЖОДНОГО розв'язку для p,q ≥ 3", size=10, bold=True, color="#e03131", anchor="middle"))

    os.makedirs('img', exist_ok=True)
    render('img/fig-gerono-cases.svg', 800, 350, *frags, title="Класифікація діофантового рівняння xᵃ - yᵇ = 1")

def draw_gcd_split():
    frags = []
    
    # Title
    frags.append(rect(10, 10, 780, 40, rx=6, fill="#f8f9fa", stroke="#ced4da", sw=1.5))
    frags.append(text(400, 35, "Розклад x² - 1 = (x - 1)(x + 1) = yᵇ та дихотомія парності x", size=14, bold=True, color="#212529", anchor="middle"))

    # Top equation node
    frags.append(rect(250, 65, 300, 45, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(400, 92, "x² - 1 = (x - 1)(x + 1) = yᵇ", size=13, bold=True, color="#1864ab", anchor="middle"))

    # Arrows splitting by parity
    frags.append(arrow(320, 110, 200, 150, color="#495057", sw=1.5))
    frags.append(arrow(480, 110, 600, 150, color="#495057", sw=1.5))

    # Left Branch: x is even
    frags.append(rect(30, 150, 340, 170, rx=6, fill="#ffe3e3", stroke="#e03131", sw=1.5))
    frags.append(text(200, 175, "Гілка 1: x — парне число", size=12, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(200, 200, "НСД(x - 1, x + 1) = 1 (взаємно прості)", size=11, color="#495057", anchor="middle"))
    frags.append(text(200, 225, "Обоє множників є b-ми степенями:", size=11, color="#495057", anchor="middle"))
    frags.append(text(200, 245, "x - 1 = uᵇ,   x + 1 = vᵇ", size=11, bold=True, color="#212529", anchor="middle"))
    frags.append(text(200, 270, "Різниця: vᵇ - uᵇ = 2", size=11, bold=True, color="#e03131", anchor="middle"))
    frags.append(text(200, 295, "Для b ≥ 2: vᵇ - uᵇ ≥ 2ᵇ - 1ᵇ ≥ 3 > 2 (суперечність!)", size=10, bold=True, color="#c92a2a", anchor="middle"))

    # Right Branch: x is odd
    frags.append(rect(430, 150, 340, 170, rx=6, fill="#d3f9d8", stroke="#2b8a3e", sw=1.5))
    frags.append(text(600, 175, "Гілка 2: x — непарне (x = 2k + 1)", size=12, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(600, 200, "НСД(x - 1, x + 1) = 2", size=11, color="#495057", anchor="middle"))
    frags.append(text(600, 225, "Перетворення: k(k + 1) = 2ᵇ⁻² · mᵇ", size=11, color="#495057", anchor="middle"))
    frags.append(text(600, 250, "Оскільки НСД(k, k + 1) = 1:", size=11, color="#495057", anchor="middle"))
    frags.append(text(600, 270, "Одне з чисел є степенем, друге — 2 · степінь", size=10, color="#495057", anchor="middle"))
    frags.append(text(600, 295, "При b = 3 маємо єдиний розв'язок x = 3, y = 2", size=10, bold=True, color="#2b8a3e", anchor="middle"))

    os.makedirs('img', exist_ok=True)
    render('img/fig-gcd-split.svg', 800, 340, *frags, title="Дихотомія парності для рівняння Жероно")

def draw_descent_ladder():
    frags = []
    
    # Title
    frags.append(rect(10, 10, 780, 40, rx=6, fill="#f8f9fa", stroke="#ced4da", sw=1.5))
    frags.append(text(400, 35, "Редукційна драбина розв'язання рівняння Ойлера x² - y³ = 1", size=14, bold=True, color="#212529", anchor="middle"))

    # Step 1
    frags.append(rect(200, 65, 400, 45, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(400, 92, "Крок 1: x² - 1 = y³  ⇒  x — непарне (x = 2k + 1)", size=12, bold=True, color="#1864ab", anchor="middle"))

    frags.append(arrow(400, 110, 400, 130, color="#495057", sw=1.5))

    # Step 2
    frags.append(rect(200, 130, 400, 45, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(400, 157, "Крок 2: 4k(k + 1) = y³  ⇒  k(k + 1) = 2 · m³", size=12, bold=True, color="#1864ab", anchor="middle"))

    frags.append(arrow(400, 175, 400, 195, color="#495057", sw=1.5))

    # Step 3
    frags.append(rect(150, 195, 500, 50, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(400, 217, "Крок 3: Оскільки НСД(k, k + 1) = 1, маємо дві підсистеми:", size=11, color="#495057", anchor="middle"))
    frags.append(text(400, 235, "Варіант А: k = u³, k+1 = 2v³   або   Варіант Б: k = 2u³, k+1 = v³", size=11, bold=True, color="#d9480f", anchor="middle"))

    frags.append(arrow(400, 245, 400, 265, color="#495057", sw=1.5))

    # Step 4
    frags.append(rect(150, 265, 500, 55, rx=6, fill="#d3f9d8", stroke="#2b8a3e", sw=1.5))
    frags.append(text(400, 287, "Крок 4: Аналіз варіанта Б: v³ - 2u³ = 1", size=12, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(400, 307, "Найменший розв'язок у натуральних числах: u = 1, v = 1 ⇒ k = 1, k + 1 = 2", size=11, color="#2b8a3e", anchor="middle"))

    frags.append(arrow(400, 320, 400, 340, color="#495057", sw=1.5))

    # Final Output
    frags.append(rect(200, 340, 400, 50, rx=6, fill="#ffe3e3", stroke="#e03131", sw=2.0))
    frags.append(text(400, 362, "Результат: k = 1  ⇒  x = 2(1) + 1 = 3,  y = 2", size=11, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(400, 377, "Єдиний розв'язок: 3² - 2³ = 9 - 8 = 1", size=11, bold=True, color="#c92a2a", anchor="middle"))

    os.makedirs('img', exist_ok=True)
    render('img/fig-descent-ladder.svg', 800, 410, *frags, title="Редукційна драбина для рівняння x² - y³ = 1")

if __name__ == '__main__':
    draw_gerono_cases()
    draw_gcd_split()
    draw_descent_ladder()
    print("Figures generated successfully.")

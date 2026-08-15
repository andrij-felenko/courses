import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, arrow, POS, NEG, INK, MUTED, FIELD, FILL, BG
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

def draw_halls_bound():
    frags = []
    
    # Title box
    frags.append(rect(20, 10, 780, 32, rx=4, fill="#f8f9fa", stroke="#ced4da", sw=1.0))
    frags.append(text(410, 31, "Розподіл різниць |y² - x³| та асимптотичні межі Холла", size=13, bold=True, color="#212529", anchor="middle"))

    # Axes
    # Y-axis (Difference |y^2 - x^3|)
    frags.append(line(70, 55, 70, 240, color="#495057", sw=2.0))
    frags.append(arrow(70, 60, 70, 48, color="#495057", sw=2.0))
    frags.append(text(65, 45, "|y² - x³|", size=11, bold=True, color="#495057", anchor="end"))

    # X-axis (Base x)
    frags.append(line(70, 240, 760, 240, color="#495057", sw=2.0))
    frags.append(arrow(740, 240, 770, 240, color="#495057", sw=2.0))
    frags.append(text(775, 244, "x", size=12, bold=True, color="#495057"))

    # Curve 1: Trivial upper bound O(x^(3/2))
    frags.append(line(80, 70, 710, 105, color="#adb5bd", sw=1.5, dash="4,4"))
    frags.append(text(715, 100, "Тривіальна межа O(x³/²)", size=10, italic=True, color="#6c757d"))

    # Curve 2: Strong Hall bound C * sqrt(x) - Red dashed line
    frags.append(line(80, 125, 710, 175, color="#e03131", sw=2.0, dash="6,3"))
    frags.append(text(715, 170, "Сильна межа C · √x (спростовано)", size=10, bold=True, color="#c92a2a"))

    # Curve 3: Weak Hall bound C(ε) * x^(1/2 - ε) - Green line
    frags.append(line(80, 150, 710, 210, color="#2b8a3e", sw=2.0))
    frags.append(text(715, 210, "Гіпотеза Холла C(ε) · x¹/²⁻ᵉ", size=10, bold=True, color="#2b8a3e"))

    # Danilov's counterexamples (dipping below C * sqrt(x))
    danilov_pts = [(160, 138), (270, 158), (390, 178), (510, 192)]
    for px, py in danilov_pts:
        frags.append(circle(px, py, 4, fill="#ffe066", stroke="#f59f00", sw=1.5))
    frags.append(rect(170, 142, 185, 28, rx=4, fill="#fff9db", stroke="#f59f00", sw=1.0))
    frags.append(text(262, 160, "Послідовність Данилова (1982)", size=9, bold=True, color="#d9480f", anchor="middle"))

    # Elkies record point
    elkies_x, elkies_y = 570, 206
    frags.append(circle(elkies_x, elkies_y, 5, fill="#ff8787", stroke="#e03131", sw=2.0))
    frags.append(rect(460, 175, 140, 34, rx=4, fill="#ffe3e3", stroke="#e03131", sw=1.0))
    frags.append(text(530, 190, "Рекорд Елкіса (1998)", size=9, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(530, 204, "|y² - x³| = 4668", size=9, color="#495057", anchor="middle"))

    # Forbidden region shading / note
    frags.append(rect(80, 246, 680, 20, rx=2, fill="#ebfbee", stroke="#b2f2bb", sw=0.8))
    frags.append(text(420, 260, "Заборонена зона за гіпотезою Холла (жодна точка y² ≠ x³ не падає нижче C(ε) · x¹/²⁻ᵉ)", size=9, italic=True, color="#2b8a3e", anchor="middle"))

    IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-halls-bound.svg'), 890, 275, *frags, title="Межі гіпотези Холла")

def draw_abc_hall_bridge():
    frags = []
    
    # Title box
    frags.append(rect(20, 10, 740, 30, rx=4, fill="#f8f9fa", stroke="#ced4da", sw=1.0))
    frags.append(text(390, 30, "Виведення гіпотези Холла з гіпотези ABC", size=13, bold=True, color="#212529", anchor="middle"))

    # Step 1: Diophantine Equation
    frags.append(rect(30, 55, 210, 60, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(135, 75, "1. Діофантове рівняння", size=11, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(135, 95, "x³ + k = y²  (k = y² - x³)", size=11, color="#212529", anchor="middle"))

    # Arrow 1 -> 2
    frags.append(arrow(240, 85, 270, 85, color="#495057", sw=1.5))

    # Step 2: Radical Bound
    frags.append(rect(275, 55, 220, 60, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(385, 75, "2. Оцінка радикала", size=11, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(385, 95, "rad(x³ · k · y²) ≤ x · y · |k|", size=11, color="#212529", anchor="middle"))

    # Arrow 2 -> 3
    frags.append(arrow(495, 85, 525, 85, color="#495057", sw=1.5))

    # Step 3: ABC Inequality
    frags.append(rect(530, 55, 225, 60, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(642, 75, "3. Нерівність ABC", size=11, bold=True, color="#d9480f", anchor="middle"))
    frags.append(text(642, 95, "y² < C(ε') · (x · y · |k|)^(1+ε')", size=10, bold=True, color="#212529", anchor="middle"))

    # Down Arrow from Step 3 to Step 4
    frags.append(arrow(642, 115, 642, 145, color="#495057", sw=1.5))

    # Step 4: Asymptotic substitution y ~ x^(3/2)
    frags.append(rect(390, 150, 365, 60, rx=6, fill="#ffe3e3", stroke="#e03131", sw=1.5))
    frags.append(text(572, 170, "4. Заміна y ≈ x³/² та підстановка", size=11, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(572, 190, "x³/² ≤ C' · (x⁵/² · |k|)^(1+ε')", size=11, color="#212529", anchor="middle"))

    # Left Arrow from Step 4 to Step 5
    frags.append(arrow(390, 180, 270, 180, color="#495057", sw=1.5))

    # Step 5: Hall's Conjecture Result
    frags.append(rect(30, 150, 235, 60, rx=6, fill="#ebfbee", stroke="#2b8a3e", sw=2.0))
    frags.append(text(147, 170, "5. Гіпотеза Холла", size=12, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(147, 190, "|y² - x³| > C(ε) · x¹/²⁻ᵉ", size=12, bold=True, color="#2b8a3e", anchor="middle"))

    IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-abc-hall-bridge.svg'), 780, 230, *frags, title="Міст від ABC до Холла")

if __name__ == '__main__':
    draw_halls_bound()
    draw_abc_hall_bridge()

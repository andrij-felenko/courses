import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, arrow, POS, NEG
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

def draw_consecutive_powers():
    frags = []
    
    # Title/Header box
    frags.append(rect(20, 15, 720, 35, rx=4, fill="#f8f9fa", stroke="#ced4da", sw=1.0))
    frags.append(text(380, 37, "Розподіл точних степенів u^v (v ≥ 2) на натуральній осі", size=13, bold=True, color="#212529", anchor="middle"))

    # Number Line Axis
    frags.append(line(40, 120, 720, 120, color="#495057", sw=2.0))
    # Axis Arrow
    frags.append(arrow(700, 120, 725, 120, color="#495057", sw=2.0))
    frags.append(text(732, 124, "n", size=12, bold=True, color="#495057"))

    # Numbers and Power Markers
    # Positions mapped onto axis (40 to 700 for numbers 1 to 36)
    # We display 1, 4, 8, 9, 16, 25, 27, 32, 36
    powers_data = [
        (1, "1", "1^v", 60, False),
        (4, "4", "2²", 120, False),
        (8, "8", "2³", 200, True),   # Highlight pair 8 and 9
        (9, "9", "3²", 230, True),   # Highlight pair 8 and 9
        (16, "16", "4²", 340, False),
        (25, "25", "5²", 480, False),
        (27, "27", "3³", 515, False),
        (32, "32", "2⁵", 590, False),
        (36, "36", "6²", 650, False),
    ]

    for num, label_num, label_pow, x, is_pair in powers_data:
        # Tick line
        tick_color = "#e03131" if is_pair else "#1c7ed6"
        frags.append(line(x, 112, x, 128, color=tick_color, sw=2.0 if is_pair else 1.5))
        
        # Circle marker
        fill_c = "#ffe3e3" if is_pair else "#e7f5ff"
        frags.append(circle(x, 120, 5 if is_pair else 4, fill=fill_c, stroke=tick_color, sw=1.5))
        
        # Power label above axis
        frags.append(text(x, 95, label_pow, size=11, bold=is_pair, color=tick_color, anchor="middle"))
        # Number label below axis
        frags.append(text(x, 145, label_num, size=11, bold=is_pair, color="#212529", anchor="middle"))

    # Special callout box for 8 and 9
    frags.append(rect(170, 165, 120, 55, rx=6, fill="#ffe3e3", stroke="#e03131", sw=1.5))
    frags.append(text(230, 185, "9 - 8 = 1", size=13, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(230, 204, "3² - 2³ = 1", size=11, bold=True, color="#e03131", anchor="middle"))

    # Pointer from callout to tick 8 & 9
    frags.append(line(215, 165, 200, 132, color="#e03131", sw=1.2))
    frags.append(line(245, 165, 230, 132, color="#e03131", sw=1.2))

    # Note about larger gaps
    frags.append(rect(420, 170, 280, 50, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.2))
    frags.append(text(560, 190, "Наступний кандидат 27 - 25 = 2", size=11, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(560, 207, "Жодної іншої пари з різницею 1 немає", size=10, color="#1c7ed6", anchor="middle"))

    os.makedirs('img', exist_ok=True)
    render('img/fig-consecutive-powers.svg', 760, 240, *frags, title="Сусідні степені на натуральній осі")

def draw_reduction_roadmap():
    frags = []
    
    # Header
    frags.append(rect(20, 15, 720, 35, rx=4, fill="#f1f3f5", stroke="#ced4da", sw=1.0))
    frags.append(text(380, 37, "Еволюція редукції рівняння Каталана: xᵃ - yᵇ = 1", size=13, bold=True, color="#212529", anchor="middle"))

    # Level 1: General Equation
    frags.append(rect(240, 65, 280, 45, rx=6, fill="#f8f9fa", stroke="#343a40", sw=1.5))
    frags.append(text(380, 87, "Загальне рівняння xᵃ - yᵇ = 1 (a,b ≥ 2)", size=12, bold=True, color="#212529", anchor="middle"))
    frags.append(text(380, 102, "Довільні натуральні показники", size=9, color="#495057", anchor="middle"))

    frags.append(arrow(380, 110, 380, 135, color="#495057", sw=1.5))

    # Level 2: Prime Exponents Reduction
    frags.append(rect(210, 135, 340, 45, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(380, 157, "Зведення до простих показників: xᵖ - y𝑞 = 1", size=12, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(380, 172, "p, q — прості числа, оскільки u^(m·k) = (u^m)^k", size=9, color="#1c7ed6", anchor="middle"))

    # Split into branches
    frags.append(arrow(300, 180, 140, 215, color="#495057", sw=1.5))
    frags.append(arrow(380, 180, 380, 215, color="#495057", sw=1.5))
    frags.append(arrow(460, 180, 620, 215, color="#495057", sw=1.5))

    # Branch 1: Euler (1738)
    frags.append(rect(40, 215, 200, 65, rx=6, fill="#ebfbee", stroke="#2b8a3e", sw=1.5))
    frags.append(text(140, 237, "Ойлер (1738): x² - y³ = 1", size=11, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(140, 254, "Єдиний розв'язок: 3² - 2³ = 1", size=10, color="#2b8a3e", anchor="middle"))
    frags.append(text(140, 270, "Доведено через Z[i√2]", size=9, color="#495057", anchor="middle"))

    # Branch 2: Lebesgue (1850)
    frags.append(rect(270, 215, 220, 65, rx=6, fill="#ebfbee", stroke="#2b8a3e", sw=1.5))
    frags.append(text(380, 237, "Лебег (1850): x² - y𝑞 = 1", size=11, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(380, 254, "Немає розв'язків для q ≥ 2", size=10, color="#2b8a3e", anchor="middle"))
    frags.append(text(380, 270, "Квадрат не перевищує степінь", size=9, color="#495057", anchor="middle"))

    # Branch 3: Chao Ko (1965)
    frags.append(rect(520, 215, 200, 65, rx=6, fill="#ebfbee", stroke="#2b8a3e", sw=1.5))
    frags.append(text(620, 237, "Чао Ко (1965): xᵖ - y² = 1", size=11, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(620, 254, "Немає розв'язків для p ≥ 3", size=10, color="#2b8a3e", anchor="middle"))
    frags.append(text(620, 270, "Степінь не перевищує квадрат", size=9, color="#495057", anchor="middle"))

    # Convergence below branches
    frags.append(arrow(140, 280, 380, 315, color="#495057", sw=1.5))
    frags.append(arrow(380, 280, 380, 315, color="#495057", sw=1.5))
    frags.append(arrow(620, 280, 380, 315, color="#495057", sw=1.5))

    # Main Remaining Target: Odd primes p, q >= 3
    frags.append(rect(180, 315, 400, 50, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(380, 337, "Головний рубіж: p, q ≥ 3 — непарні прості числа", size=12, bold=True, color="#e67700", anchor="middle"))
    frags.append(text(380, 354, "Касселс (1960): p ділить y, q ділить x (числа x, y гігантські)", size=9, color="#d9480f", anchor="middle"))

    # Final Resolution: Mihailescu 2002
    frags.append(arrow(380, 365, 380, 395, color="#495057", sw=1.5))

    frags.append(rect(160, 395, 440, 55, rx=6, fill="#ffe3e3", stroke="#e03131", sw=2.0))
    frags.append(text(380, 417, "Фінал: Преда Міхайлеску (2002)", size=13, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(380, 437, "Кругові поля Q(ζₚ) + Прості Віферіха → p ≡ 1 (mod q) та q ≡ 1 (mod p) — Суперечність!", size=10, bold=True, color="#e03131", anchor="middle"))

    os.makedirs('img', exist_ok=True)
    render('img/fig-reduction-roadmap.svg', 760, 465, *frags, title="Дорожня карта доведення гіпотези Каталана")

def draw_cyclotomic_decomposition():
    frags = []

    # Title
    frags.append(rect(20, 15, 720, 35, rx=4, fill="#f8f9fa", stroke="#ced4da", sw=1.0))
    frags.append(text(380, 37, "Алгебраїчний механізм Міхайлеску: факторизація у круговому полі Z[ζₚ]", size=13, bold=True, color="#212529", anchor="middle"))

    # Block 1: Equation x^p - 1 = y^q
    frags.append(rect(50, 70, 280, 60, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(190, 95, "Рівняння xᵖ - 1 = y𝑞", size=12, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(190, 115, "Розклад у кільці цілих Z[ζₚ]", size=10, color="#1c7ed6", anchor="middle"))

    frags.append(arrow(330, 100, 430, 100, color="#495057", sw=1.5))

    # Block 2: Cyclotomic Factorization
    frags.append(rect(430, 70, 280, 60, rx=6, fill="#ebfbee", stroke="#2b8a3e", sw=1.5))
    frags.append(text(570, 93, "(x - 1) ∏ (x - ζʲ) = y𝑞", size=12, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(570, 115, "Добуток p множників у Z[ζₚ]", size=10, color="#2b8a3e", anchor="middle"))

    # Arrow Down to Ideal Class Group
    frags.append(arrow(570, 130, 570, 165, color="#495057", sw=1.5))
    frags.append(arrow(190, 130, 190, 165, color="#495057", sw=1.5))

    # Block 3: Cassels Divisibility
    frags.append(rect(50, 165, 280, 65, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(190, 188, "Умови Касселса & Віферіха", size=12, bold=True, color="#e67700", anchor="middle"))
    frags.append(text(190, 206, "p || y,  p^(q-1) ≡ 1 (mod q²)", size=10, bold=True, color="#d9480f", anchor="middle"))
    frags.append(text(190, 222, "q || x,  q^(p-1) ≡ 1 (mod p²)", size=10, bold=True, color="#d9480f", anchor="middle"))

    # Block 4: Ideal Class Group & Stickelberger Ideal
    frags.append(rect(430, 165, 280, 65, rx=6, fill="#f3d9fa", stroke="#ae3ec9", sw=1.5))
    frags.append(text(570, 188, "Ідеал Стікельберґера S ⊂ Z[G]", size=12, bold=True, color="#9c36b5", anchor="middle"))
    frags.append(text(570, 206, "Ануляція класу ідеалів (x - ζ)", size=10, color="#ae3ec9", anchor="middle"))
    frags.append(text(570, 222, "(x - ζ) · S = (α)^q (головний ідеал)", size=10, color="#495057", anchor="middle"))

    # Convergence to Final Contradiction
    frags.append(arrow(190, 230, 380, 265, color="#495057", sw=1.5))
    frags.append(arrow(570, 230, 380, 265, color="#495057", sw=1.5))

    # Block 5: Final Contradiction Box
    frags.append(rect(140, 265, 480, 55, rx=6, fill="#ffe3e3", stroke="#e03131", sw=2.0))
    frags.append(text(380, 288, "Оцінка розміру кругових одиниць vs Множники", size=12, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(380, 307, "Векторний простір над F_q не має необхідної вимірності → p > q та q > p (Заперечення)", size=10, bold=True, color="#e03131", anchor="middle"))

    os.makedirs('img', exist_ok=True)
    render('img/fig-cyclotomic-decomposition.svg', 760, 335, *frags, title="Факторизація в круговому полі та ануляція Стікельберґера")

if __name__ == '__main__':
    draw_consecutive_powers()
    draw_reduction_roadmap()
    draw_cyclotomic_decomposition()

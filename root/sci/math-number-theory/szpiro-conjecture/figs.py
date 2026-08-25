import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, arrow, POS, NEG, INK, MUTED, FIELD, FILL, BG
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

def draw_szpiro_structure():
    frags = []
    
    # Title box
    frags.append(rect(20, 12, 720, 32, rx=4, fill="#f8f9fa", stroke="#ced4da", sw=1.0))
    frags.append(text(380, 33, "Анатомія гіпотези Шпіро: |Δ_E| ≤ C(ε) · N_E^(6 + ε)", size=13, bold=True, color="#212529", anchor="middle"))

    # Box 1: Minimal Discriminant Δ_E
    frags.append(rect(40, 60, 320, 85, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(200, 82, "Мінімальний дискримінант Δ_E", size=13, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(200, 102, "Глобальна алгебраїчна складність", size=11, color="#495057", anchor="middle"))
    frags.append(text(200, 122, "Вимірює сингулярність моделі кривої", size=10, italic=True, color="#6c757d", anchor="middle"))

    # Arrow between Δ_E and N_E
    frags.append(arrow(370, 102, 390, 102, color="#1c7ed6", sw=2.0))
    frags.append(text(380, 94, "≤", size=16, bold=True, color="#d9480f", anchor="middle"))

    # Box 2: Conductor N_E
    frags.append(rect(400, 60, 320, 85, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(560, 82, "Провідник (Conductor) N_E", size=13, bold=True, color="#e67700", anchor="middle"))
    frags.append(text(560, 102, "Локальна арифметика поганої редукції", size=11, color="#495057", anchor="middle"))
    frags.append(text(560, 122, "N_E = ∏ p^(v_p(N_E)),  p | Δ_E", size=10, italic=True, color="#6c757d", anchor="middle"))

    # Bottom summary box: Szpiro Index σ(E)
    frags.append(rect(40, 160, 680, 85, rx=6, fill="#ffe3e3", stroke="#e03131", sw=1.5))
    frags.append(text(380, 182, "Індекс Шпіро:  σ(E) = log |Δ_E| / log N_E", size=13, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(380, 205, "Гіпотеза стверджує: limsup σ(E) = 6  (для всіх N_E → ∞)", size=11, bold=True, color="#212529", anchor="middle"))
    frags.append(text(380, 227, "Локальні дільники N_E строго обмежують глобальний дискримінант Δ_E", size=10, italic=True, color="#495057", anchor="middle"))

    IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-szpiro-structure.svg'), 760, 260, *frags, title="Анатомія гіпотези Шпіро")

def draw_frey_bridge():
    frags = []
    
    # Title box
    frags.append(rect(20, 12, 720, 32, rx=4, fill="#f8f9fa", stroke="#ced4da", sw=1.0))
    frags.append(text(380, 33, "Міст Фрея: зв'язок гіпотези Шпіро з гіпотезою ABC", size=13, bold=True, color="#212529", anchor="middle"))

    # Left Box: Integer Triple a + b = c
    frags.append(rect(40, 60, 290, 85, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(185, 82, "Діофантове рівняння", size=12, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(185, 102, "a + b = c,   gcd(a, b) = 1", size=12, bold=True, color="#212529", anchor="middle"))
    frags.append(text(185, 122, "Радикал: rad(abc) = ∏ p", size=10, color="#495057", anchor="middle"))

    # Center Arrow: Frey Construction
    frags.append(arrow(340, 102, 410, 102, color="#d9480f", sw=2.0))
    frags.append(text(375, 92, "Крива", size=10, bold=True, color="#d9480f", anchor="middle"))
    frags.append(text(375, 116, "Фрея", size=10, bold=True, color="#d9480f", anchor="middle"))

    # Right Box: Elliptic Curve E_{a,b}
    frags.append(rect(420, 60, 300, 85, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(570, 82, "Еліптична крива E_(a,b)", size=12, bold=True, color="#e67700", anchor="middle"))
    frags.append(text(570, 102, "y² = x(x - a)(x + b)", size=12, bold=True, color="#212529", anchor="middle"))
    frags.append(text(570, 122, "Δ_E = 16(abc)²,   N_E = rad(abc)", size=10, color="#495057", anchor="middle"))

    # Connecting Arrow Down
    frags.append(arrow(570, 150, 570, 172, color="#c92a2a", sw=2.0))

    # Bottom Box: Szpiro -> ABC Derivation
    frags.append(rect(40, 175, 680, 80, rx=6, fill="#ffe3e3", stroke="#e03131", sw=1.5))
    frags.append(text(380, 195, "Застосування гіпотези Шпіро до кривої Фрея:", size=12, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(380, 215, "16 (abc)² ≤ C · (rad(abc))^(6+ε)  ⇒  c ≤ C' · (rad(abc))^(1+ε')", size=11, bold=True, color="#212529", anchor="middle"))
    frags.append(text(380, 237, "Гіпотеза Шпіро геометрично породжує гіпотезу ABC для цілих чисел", size=10, italic=True, color="#495057", anchor="middle"))

    IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-frey-bridge.svg'), 760, 270, *frags, title="Міст Фрея")

def draw_reduction_types():
    frags = []
    
    # Title box
    frags.append(rect(20, 12, 720, 32, rx=4, fill="#f8f9fa", stroke="#ced4da", sw=1.0))
    frags.append(text(380, 33, "Локальні типи редукції еліптичних кривих mod p", size=13, bold=True, color="#212529", anchor="middle"))

    # Column 1: Good Reduction
    frags.append(rect(35, 60, 220, 185, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(145, 82, "Добра редукція", size=12, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(145, 102, "p ∤ Δ_E", size=11, bold=True, color="#212529", anchor="middle"))
    frags.append(text(145, 130, "Крива гладка mod p", size=10, color="#495057", anchor="middle"))
    frags.append(text(145, 150, "Сингулярності відсутні", size=10, color="#495057", anchor="middle"))
    frags.append(text(145, 185, "v_p(Δ_E) = 0", size=11, bold=True, color="#1c7ed6", anchor="middle"))
    frags.append(text(145, 210, "v_p(N_E) = 0", size=11, bold=True, color="#1c7ed6", anchor="middle"))

    # Column 2: Multiplicative (Semistable)
    frags.append(rect(270, 60, 220, 185, rx=6, fill="#d3f9d8", stroke="#2b8a3e", sw=1.5))
    frags.append(text(380, 82, "Мультиплікативна", size=12, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(380, 102, "(Напівстабільна)", size=10, color="#2b8a3e", anchor="middle"))
    frags.append(text(380, 130, "Вузол (node) mod p", size=10, color="#495057", anchor="middle"))
    frags.append(text(380, 150, "Окрема дотична", size=10, color="#495057", anchor="middle"))
    frags.append(text(380, 185, "v_p(Δ_E) = n ≥ 1", size=11, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(380, 210, "v_p(N_E) = 1", size=11, bold=True, color="#2b8a3e", anchor="middle"))

    # Column 3: Additive (Unstable)
    frags.append(rect(505, 60, 220, 185, rx=6, fill="#ffe3e3", stroke="#e03131", sw=1.5))
    frags.append(text(615, 82, "Адитивна редукція", size=12, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(615, 102, "(Нестабільна)", size=10, color="#c92a2a", anchor="middle"))
    frags.append(text(615, 130, "Касп (cusp) mod p", size=10, color="#495057", anchor="middle"))
    frags.append(text(615, 150, "Точка повернення", size=10, color="#495057", anchor="middle"))
    frags.append(text(615, 185, "v_p(Δ_E) ≥ 2", size=11, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(615, 210, "v_p(N_E) = 2 (p ≥ 5)", size=11, bold=True, color="#c92a2a", anchor="middle"))

    IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-reduction-types.svg'), 760, 270, *frags, title="Типи редукції")

if __name__ == "__main__":
    draw_szpiro_structure()
    draw_frey_bridge()
    draw_reduction_types()
    print("Successfully generated all figures for Szpiro's conjecture.")

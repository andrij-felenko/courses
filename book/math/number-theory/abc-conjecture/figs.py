import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, arrow, POS, NEG, INK, MUTED, FIELD, FILL, BG
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

def draw_abc_structure():
    frags = []
    
    # Title box
    frags.append(rect(20, 12, 720, 32, rx=4, fill="#f8f9fa", stroke="#ced4da", sw=1.0))
    frags.append(text(380, 33, "Анатомія ABC-трійки: 1 + 4374 = 4375 (Решат, 1987)", size=13, bold=True, color="#212529", anchor="middle"))

    # Triple elements (a, b, c)
    # Box A
    frags.append(rect(40, 60, 180, 75, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(130, 80, "a = 1", size=14, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(130, 100, "1 = 1", size=11, color="#495057", anchor="middle"))
    frags.append(text(130, 120, "rad(a) = 1", size=11, bold=True, color="#1c7ed6", anchor="middle"))

    # Plus sign
    frags.append(text(237, 102, "+", size=20, bold=True, color="#495057", anchor="middle"))

    # Box B
    frags.append(rect(255, 60, 210, 75, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(360, 80, "b = 4374", size=14, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(360, 100, "4374 = 2¹ · 3⁷", size=11, color="#495057", anchor="middle"))
    frags.append(text(360, 120, "rad(b) = 2 · 3 = 6", size=11, bold=True, color="#1c7ed6", anchor="middle"))

    # Equals sign
    frags.append(text(482, 102, "=", size=20, bold=True, color="#495057", anchor="middle"))

    # Box C
    frags.append(rect(500, 60, 220, 75, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(610, 80, "c = 4375", size=14, bold=True, color="#f59f00", anchor="middle"))
    frags.append(text(610, 100, "4375 = 5⁴ · 7¹", size=11, color="#495057", anchor="middle"))
    frags.append(text(610, 120, "rad(c) = 5 · 7 = 35", size=11, bold=True, color="#e67700", anchor="middle"))

    # Combining into radical rad(abc)
    frags.append(rect(40, 160, 680, 85, rx=6, fill="#ffe3e3", stroke="#e03131", sw=1.5))
    frags.append(text(380, 182, "Радикал добутку rad(abc) = rad(1 · 4374 · 4375) = 2 · 3 · 5 · 7 = 210", size=13, bold=True, color="#c92a2a", anchor="middle"))
    
    # Comparison and Quality
    frags.append(text(200, 212, "Порівняння: c = 4375  >  rad(abc) = 210", size=12, bold=True, color="#212529", anchor="middle"))
    frags.append(text(540, 212, "Якість: q(a,b,c) = log(4375) / log(210) ≈ 1.568", size=12, bold=True, color="#e03131", anchor="middle"))
    frags.append(text(380, 232, "Компактний сумарний радикал (210) утворює величезне число c (4375)", size=10, italic=True, color="#495057", anchor="middle"))

    IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-abc-structure.svg'), 760, 260, *frags, title="Анатомія ABC-трійки")

def draw_quality_distribution():
    frags = []
    
    # Title box
    frags.append(rect(20, 12, 720, 32, rx=4, fill="#f8f9fa", stroke="#ced4da", sw=1.0))
    frags.append(text(380, 33, "Спектр якості q(a,b,c) = log(c) / log(rad(abc)) для взаємно простих трійок", size=13, bold=True, color="#212529", anchor="middle"))

    # Axis line
    frags.append(line(50, 130, 710, 130, color="#495057", sw=2.0))
    frags.append(arrow(690, 130, 715, 130, color="#495057", sw=2.0))
    frags.append(text(725, 134, "q", size=13, bold=True, color="#495057"))

    # Threshold line q = 1.0
    q10_x = 270
    frags.append(line(q10_x, 60, q10_x, 175, color="#e03131", sw=2.0))
    frags.append(text(q10_x, 52, "Поріг q = 1.0 (c = rad(abc))", size=11, bold=True, color="#c92a2a", anchor="middle"))

    # Zone labels
    frags.append(rect(60, 65, 180, 45, rx=4, fill="#e7f5ff", stroke="#74c0fc", sw=1.0))
    frags.append(text(150, 83, "Звичайна зона (q < 1)", size=11, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(150, 100, "Нескінченна більшість трійок", size=9, color="#495057", anchor="middle"))

    frags.append(rect(290, 65, 410, 45, rx=4, fill="#ffe3e3", stroke="#ffc9c9", sw=1.0))
    frags.append(text(495, 83, "Зона аномалій / ABC-трійок (q > 1)", size=11, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(495, 100, "Рідкісні винятки; при q > 1 + ε їхня кількість скінченна", size=9, color="#495057", anchor="middle"))

    # Points on axis
    # q = 0.75 (x = 195)
    frags.append(circle(195, 130, 4, fill="#1c7ed6", stroke="#1864ab", sw=1.5))
    frags.append(line(195, 122, 195, 138, color="#1c7ed6", sw=1.5))
    frags.append(text(195, 150, "q ≈ 0.75", size=10, color="#495057", anchor="middle"))
    frags.append(text(195, 165, "Типове a+b=c", size=9, italic=True, color="#6c757d", anchor="middle"))

    # Record 1: q = 1.25 (x = 445) -> 1 + 240000 = 240001
    frags.append(circle(445, 130, 5, fill="#ffe066", stroke="#f59f00", sw=1.5))
    frags.append(line(445, 122, 445, 138, color="#f59f00", sw=1.5))
    frags.append(text(445, 150, "q ≈ 1.25", size=10, bold=True, color="#d9480f", anchor="middle"))
    frags.append(text(445, 165, "1+240000=240001", size=9, color="#495057", anchor="middle"))

    # Record 2: q = 1.568 (x = 604) -> Reyssat
    frags.append(circle(604, 130, 5, fill="#ff8787", stroke="#e03131", sw=1.5))
    frags.append(line(604, 122, 604, 138, color="#e03131", sw=1.5))
    frags.append(text(604, 150, "q ≈ 1.568", size=10, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(604, 165, "1+4374=4375", size=9, color="#495057", anchor="middle"))

    # Record 3: q = 1.630 (x = 635) -> de Weger
    frags.append(circle(635, 130, 6, fill="#e03131", stroke="#96f2d7", sw=1.5))
    frags.append(line(635, 122, 635, 138, color="#c92a2a", sw=1.5))
    frags.append(text(635, 195, "q ≈ 1.630 (Рекорд де Вегера)", size=10, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(635, 210, "2 + 3¹⁰·109 = 23⁵", size=9, color="#495057", anchor="middle"))
    frags.append(line(635, 172, 635, 185, color="#c92a2a", sw=1.0))

    # Ticks for axis
    for q_val in [0.5, 1.0, 1.5]:
        tx = 70 + int((q_val - 0.5) * 500)
        frags.append(line(tx, 126, tx, 134, color="#343a40", sw=1.0))
        frags.append(text(tx, 145, "%.1f" % q_val, size=10, color="#343a40", anchor="middle"))

    IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
    render(os.path.join(IMG_DIR, 'fig-quality-distribution.svg'), 760, 240, *frags, title="Спектр якості трійок ABC")

def draw_abc_implications():
    frags = []
    
    # Title box
    frags.append(rect(20, 10, 720, 30, rx=4, fill="#f8f9fa", stroke="#ced4da", sw=1.0))
    frags.append(text(380, 30, "Мережа наслідків гіпотези ABC в теорії чисел", size=13, bold=True, color="#212529", anchor="middle"))

    # Center box: ABC Conjecture
    frags.append(rect(260, 50, 240, 55, rx=8, fill="#ffe3e3", stroke="#e03131", sw=2.0))
    frags.append(text(380, 72, "Гіпотеза ABC", size=14, bold=True, color="#c92a2a", anchor="middle"))
    frags.append(text(380, 93, "c < C(ε) · (rad(abc))¹⁺ᵉ", size=12, bold=True, color="#e03131", anchor="middle"))

    # Top Row: Nodes 1, 2, 3
    # Node 1: Fermat's Last Theorem (Asymptotic)
    frags.append(rect(25, 135, 205, 55, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(127.5, 155, "Велика теорема Ферма", size=12, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(127.5, 175, "xⁿ + yⁿ = zⁿ (асимптотична)", size=10, color="#495057", anchor="middle"))
    frags.append(arrow(300, 105, 127.5, 135, color="#1c7ed6", sw=1.5))

    # Node 2: Catalan Conjecture
    frags.append(rect(277, 135, 205, 55, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(380, 155, "Гіпотеза Каталана", size=12, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(380, 175, "xᵃ - yᵇ = 1 ⇒ 3² - 2³ = 1", size=10, color="#495057", anchor="middle"))
    frags.append(arrow(380, 105, 380, 135, color="#1c7ed6", sw=1.5))

    # Node 3: Mordell Conjecture (Faltings)
    frags.append(rect(530, 135, 205, 55, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(632.5, 155, "Теорема Фальтінгса", size=12, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(632.5, 175, "Скінченність точок при g ≥ 2", size=10, color="#495057", anchor="middle"))
    frags.append(arrow(460, 105, 632.5, 135, color="#1c7ed6", sw=1.5))

    # Bottom Row: Nodes 4, 5, 6
    # Node 4: Szpiro Conjecture
    frags.append(rect(25, 225, 205, 55, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(127.5, 245, "Гіпотеза Шпіро", size=12, bold=True, color="#e67700", anchor="middle"))
    frags.append(text(127.5, 265, "Δ ≤ C(ε) · N⁶⁺ᵉ (еліптичні)", size=10, color="#495057", anchor="middle"))
    frags.append(arrow(127.5, 190, 127.5, 225, color="#f59f00", sw=1.5))

    # Node 5: Roth Theorem
    frags.append(rect(277, 225, 205, 55, rx=6, fill="#f3d9fa", stroke="#ae3ec9", sw=1.5))
    frags.append(text(380, 245, "Теорема Рота", size=12, bold=True, color="#862e9c", anchor="middle"))
    frags.append(text(380, 265, "Діофантові наближення", size=10, color="#495057", anchor="middle"))
    frags.append(arrow(380, 190, 380, 225, color="#ae3ec9", sw=1.5))

    # Node 6: Wieferich Primes
    frags.append(rect(530, 225, 205, 55, rx=6, fill="#ebfbee", stroke="#40c057", sw=1.5))
    frags.append(text(632.5, 245, "Прості Віфериха", size=12, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(632.5, 265, "Нескінченність не-Віферихових", size=10, color="#495057", anchor="middle"))
    frags.append(arrow(632.5, 190, 632.5, 225, color="#40c057", sw=1.5))

    IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
    render(os.path.join(IMG_DIR, 'fig-abc-implications.svg'), 760, 300, *frags, title="Наслідки гіпотези ABC")

if __name__ == '__main__':
    draw_abc_structure()
    draw_quality_distribution()
    draw_abc_implications()
    print("Figures generated successfully.")

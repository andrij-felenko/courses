import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, arrow, POS, NEG
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

def draw_number_classification():
    frags = []
    
    # Root box - All Integers
    frags.append(rect(280, 20, 200, 45, rx=6, fill="#f8f9fa", stroke="#343a40", sw=1.5))
    frags.append(text(380, 47, "Множина цілих чисел N (>1)", size=13, bold=True, color="#212529", anchor="middle"))

    # Connectors to 3 main classes
    frags.append(arrow(330, 65, 120, 110, color="#6c757d", sw=1.5))
    frags.append(arrow(380, 65, 380, 110, color="#6c757d", sw=1.5))
    frags.append(arrow(430, 65, 620, 110, color="#6c757d", sw=1.5))

    # Box 1: Deficient Numbers
    frags.append(rect(30, 110, 180, 75, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(120, 135, "Недостатні числа", size=13, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(120, 155, "I(n) < 2  (s(n) < n)", size=11, color="#1c7ed6", anchor="middle"))
    frags.append(text(120, 172, "Приклади: 2, 3, 4, 5, 8, 9, 10, 16", size=10, color="#495057", anchor="middle"))

    # Box 2: Perfect Numbers
    frags.append(rect(290, 110, 180, 75, rx=6, fill="#ebfbee", stroke="#2b8a3e", sw=2.0))
    frags.append(text(380, 135, "Досконалі числа", size=13, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(380, 155, "I(n) = 2  (s(n) = n)", size=11, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(380, 172, "Приклади: 6, 28, 496, 8128", size=10, color="#495057", anchor="middle"))

    # Box 3: Abundant Numbers
    frags.append(rect(530, 110, 180, 75, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(620, 135, "Надлишкові числа", size=13, bold=True, color="#f59f00", anchor="middle"))
    frags.append(text(620, 155, "I(n) > 2  (s(n) > n)", size=11, color="#e67700", anchor="middle"))
    frags.append(text(620, 172, "Приклади: 12, 18, 20, 24, 30", size=10, color="#495057", anchor="middle"))

    # Connectors from Abundant Numbers to Subclasses
    frags.append(arrow(580, 185, 520, 230, color="#6c757d", sw=1.5))
    frags.append(arrow(660, 185, 680, 230, color="#6c757d", sw=1.5))

    # Subclass 3a: Semiperfect Numbers
    frags.append(rect(430, 230, 170, 75, rx=6, fill="#e6fcf5", stroke="#0ca678", sw=1.5))
    frags.append(text(515, 255, "Напівдосконалі числа", size=12, bold=True, color="#0ca678", anchor="middle"))
    frags.append(text(515, 273, "Сума підмножини d_i = n", size=10, color="#099268", anchor="middle"))
    frags.append(text(515, 290, "Більшість надлишкових (12, 18, 20)", size=9, color="#495057", anchor="middle"))

    # Subclass 3b: Weird Numbers
    frags.append(rect(615, 230, 135, 75, rx=6, fill="#fff0f6", stroke="#e64980", sw=1.5))
    frags.append(text(682, 255, "Дивні числа", size=12, bold=True, color="#c2255c", anchor="middle"))
    frags.append(text(682, 273, "Не є напівдосконалими", size=10, color="#e64980", anchor="middle"))
    frags.append(text(682, 290, "Приклади: 70, 836", size=9, color="#495057", anchor="middle"))

    os.makedirs('img', exist_ok=True)
    render('img/fig-number-classification.svg', 760, 330, *frags, title="Класифікація натуральних чисел за індексом надлишковості")

def draw_aliquot_tree():
    frags = []
    
    # Title / Legend Box
    frags.append(rect(20, 15, 720, 35, rx=4, fill="#f1f3f5", stroke="#ced4da", sw=1.0))
    frags.append(text(380, 37, "Динаміка аліквотних послідовностей a_k+1 = s(a_k)", size=13, bold=True, color="#343a40", anchor="middle"))

    # Sequence 1: Finite convergence to 0 (12 -> 16 -> 15 -> 9 -> 4 -> 3 -> 1 -> 0)
    frags.append(text(30, 80, "Фінітна збіжність до 0:", size=11, bold=True, color="#495057"))
    nodes_1 = [("12", 200), ("16", 260), ("15", 320), ("9", 380), ("4", 440), ("3", 500), ("1", 560), ("0", 620)]
    for i, (val, x) in enumerate(nodes_1):
        color = "#1c7ed6" if val != "0" else "#e03131"
        fill_color = "#e7f5ff" if val != "0" else "#ffe3e3"
        frags.append(rect(x - 18, 65, 36, 25, rx=4, fill=fill_color, stroke=color, sw=1.5))
        frags.append(text(x, 82, val, size=11, bold=True, color=color, anchor="middle"))
        if i < len(nodes_1) - 1:
            next_x = nodes_1[i+1][1]
            frags.append(arrow(x + 18, 77, next_x - 18, 77, color="#868e96", sw=1.2))

    # Sequence 2: Fixed Point / Perfect number (6 -> 6 -> 6)
    frags.append(text(30, 140, "Стаціонарна точка (Досконале):", size=11, bold=True, color="#495057"))
    nodes_2 = [("6", 260), ("6", 360), ("6", 460)]
    for i, (val, x) in enumerate(nodes_2):
        frags.append(rect(x - 18, 125, 36, 25, rx=4, fill="#ebfbee", stroke="#2b8a3e", sw=1.5))
        frags.append(text(x, 142, val, size=11, bold=True, color="#2b8a3e", anchor="middle"))
        if i < len(nodes_2) - 1:
            next_x = nodes_2[i+1][1]
            frags.append(arrow(x + 18, 137, next_x - 18, 137, color="#2b8a3e", sw=1.5))
    frags.append(text(510, 142, "...", size=14, bold=True, color="#2b8a3e"))

    # Sequence 3: 2-Cycle Amicable Pair (220 <-> 284)
    frags.append(text(30, 200, "2-цикл (Дружні числа):", size=11, bold=True, color="#495057"))
    frags.append(rect(250, 185, 45, 25, rx=4, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(272, 202, "220", size=11, bold=True, color="#e67700", anchor="middle"))

    frags.append(rect(360, 185, 45, 25, rx=4, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(382, 202, "284", size=11, bold=True, color="#e67700", anchor="middle"))

    frags.append(arrow(295, 192, 360, 192, color="#f59f00", sw=1.5))
    frags.append(arrow(360, 204, 295, 204, color="#f59f00", sw=1.5))
    frags.append(text(327, 187, "s(220)", size=9, color="#d9480f", anchor="middle"))
    frags.append(text(327, 216, "s(284)", size=9, color="#d9480f", anchor="middle"))

    # Sequence 4: Open Problem / Unbounded (276 -> 396 -> 696 -> ... -> ?)
    frags.append(text(30, 260, "Відкрита проблема (276):", size=11, bold=True, color="#495057"))
    nodes_4 = [("276", 260), ("396", 340), ("696", 420), ("1104", 500)]
    for i, (val, x) in enumerate(nodes_4):
        frags.append(rect(x - 22, 245, 44, 25, rx=4, fill="#f3d9fa", stroke="#ae3ec9", sw=1.5))
        frags.append(text(x, 262, val, size=10, bold=True, color="#9c36b5", anchor="middle"))
        if i < len(nodes_4) - 1:
            next_x = nodes_4[i+1][1]
            frags.append(arrow(x + 22, 257, next_x - 22, 257, color="#ae3ec9", sw=1.5))
    frags.append(text(535, 262, "-> ... -> ?", size=12, bold=True, color="#ae3ec9"))

    os.makedirs('img', exist_ok=True)
    render('img/fig-aliquot-tree.svg', 760, 300, *frags, title="Дерево аліквотних послідовностей та їхні динамічні траєкторії")

if __name__ == '__main__':
    draw_number_classification()
    draw_aliquot_tree()

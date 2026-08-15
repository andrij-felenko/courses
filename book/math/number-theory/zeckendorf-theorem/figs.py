import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, arrow
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

IMG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))

def draw_zeckendorf_greedy():
    frags = []
    
    # Title / Frame
    frags.append(rect(10, 10, 760, 260, rx=8, fill="#f8f9fa", stroke="#ced4da", sw=1.2))
    frags.append(text(390, 35, "Жадібний розклад числа N = 100 у систему Цекендорфа", size=14, bold=True, color="#212529", anchor="middle"))

    # Step 1: N = 100, max F_k <= 100 is F_11 = 89
    frags.append(rect(30, 55, 720, 50, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.2))
    frags.append(text(45, 85, "Крок 1:", size=12, bold=True, color="#1864ab"))
    frags.append(text(110, 85, "N = 100", size=12, bold=True, color="#212529"))
    frags.append(arrow(180, 80, 240, 80, color="#1c7ed6", sw=1.5))
    frags.append(text(250, 85, "Найбільше F_k ≤ 100 це F_11 = 89", size=12, color="#1864ab"))
    frags.append(arrow(510, 80, 570, 80, color="#1c7ed6", sw=1.5))
    frags.append(text(580, 85, "Остача: 100 - 89 = 11", size=12, bold=True, color="#d9480f"))

    # Step 2: Remainder 11, max F_k <= 11 is F_6 = 8
    frags.append(rect(30, 115, 720, 50, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.2))
    frags.append(text(45, 145, "Крок 2:", size=12, bold=True, color="#e67700"))
    frags.append(text(110, 145, "N = 11", size=12, bold=True, color="#212529"))
    frags.append(arrow(180, 140, 240, 140, color="#f59f00", sw=1.5))
    frags.append(text(250, 145, "Найбільше F_k ≤ 11 це F_6 = 8", size=12, color="#e67700"))
    frags.append(arrow(490, 140, 550, 140, color="#f59f00", sw=1.5))
    frags.append(text(560, 145, "Остача: 11 - 8 = 3", size=12, bold=True, color="#d9480f"))

    # Step 3: Remainder 3, max F_k <= 3 is F_4 = 3
    frags.append(rect(30, 175, 720, 50, rx=6, fill="#ebfbee", stroke="#2b8a3e", sw=1.2))
    frags.append(text(45, 205, "Крок 3:", size=12, bold=True, color="#2b8a3e"))
    frags.append(text(110, 205, "N = 3", size=12, bold=True, color="#212529"))
    frags.append(arrow(180, 200, 240, 200, color="#2b8a3e", sw=1.5))
    frags.append(text(250, 205, "Найбільше F_k ≤ 3 це F_4 = 3", size=12, color="#2b8a3e"))
    frags.append(arrow(470, 200, 530, 200, color="#2b8a3e", sw=1.5))
    frags.append(text(540, 205, "Остача: 3 - 3 = 0 (кінець)", size=12, bold=True, color="#2b8a3e"))

    # Summary bitstring representation
    frags.append(text(390, 252, "Запис у фібоначчієвій системі (1000010100_Fib): 89 + 8 + 3 (жодні два розряди не сусідять)", size=12, bold=True, color="#212529", anchor="middle"))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-zeckendorf-greedy.svg'), 780, 280, *frags, title="Жадібний розклад числа у систему Цекендорфа")

def draw_fibonacci_code():
    frags = []
    
    frags.append(rect(10, 10, 760, 230, rx=8, fill="#f8f9fa", stroke="#ced4da", sw=1.2))
    frags.append(text(390, 35, "Самосинхронізовне фібоначчієве кодування bit-stream", size=14, bold=True, color="#212529", anchor="middle"))

    # Word 1: N = 4 -> Zeckendorf 3 + 1 (F_4 + F_2) -> bits 101 -> code 1011
    frags.append(rect(30, 60, 220, 70, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.2))
    frags.append(text(140, 82, "Число N = 4", size=12, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(140, 102, "Запис: F_4 + F_2 (3 + 1)", size=11, color="#495057", anchor="middle"))
    frags.append(text(140, 118, "Код: 1 0 1 1  (маркер 11)", size=11, bold=True, color="#1864ab", anchor="middle"))

    # Word 2: N = 10 -> Zeckendorf 8 + 2 (F_6 + F_3) -> bits 01001 -> code 010011
    frags.append(rect(270, 60, 220, 70, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.2))
    frags.append(text(380, 82, "Число N = 10", size=12, bold=True, color="#e67700", anchor="middle"))
    frags.append(text(380, 102, "Запис: F_6 + F_3 (8 + 2)", size=11, color="#495057", anchor="middle"))
    frags.append(text(380, 118, "Код: 0 1 0 0 1 1  (маркер 11)", size=11, bold=True, color="#e67700", anchor="middle"))

    # Word 3: N = 1 -> Zeckendorf 1 (F_2) -> bits 1 -> code 11
    frags.append(rect(510, 60, 220, 70, rx=6, fill="#ebfbee", stroke="#2b8a3e", sw=1.2))
    frags.append(text(620, 82, "Число N = 1", size=12, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(620, 102, "Запис: F_2 (1)", size=11, color="#495057", anchor="middle"))
    frags.append(text(620, 118, "Код: 1 1  (маркер 11)", size=11, bold=True, color="#2b8a3e", anchor="middle"))

    # Continuous stream
    frags.append(rect(30, 150, 700, 65, rx=6, fill="#212529", stroke="#343a40", sw=1.5))
    frags.append(text(380, 172, "Суцільний потік бітів у мережі / каналі зв'язку:", size=11, color="#f8f9fa", anchor="middle"))

    # Highlight code blocks in stream
    frags.append(text(210, 200, "1 0 1 1", size=14, bold=True, color="#74c0fc"))
    frags.append(text(320, 200, "|", size=14, color="#868e96"))
    frags.append(text(350, 200, "0 1 0 0 1 1", size=14, bold=True, color="#ffd43b"))
    frags.append(text(510, 200, "|", size=14, color="#868e96"))
    frags.append(text(540, 200, "1 1", size=14, bold=True, color="#8ce99a"))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-fibonacci-code.svg'), 780, 250, *frags, title="Фібоначчієве самосинхронізовне кодування потоку даних")

def draw_fibonacci_nim():
    frags = []
    
    frags.append(rect(10, 10, 760, 290, rx=8, fill="#f8f9fa", stroke="#ced4da", sw=1.2))
    frags.append(text(390, 35, "Стратегія виграшу у грі «Фібоначчієвий нім» (купа з N = 11 камінців)", size=14, bold=True, color="#212529", anchor="middle"))

    # Initial state
    frags.append(rect(240, 55, 300, 55, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(390, 78, "Початкова купа: N = 11 камінців", size=13, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(390, 98, "Розклад Цекендорфа: 11 = 8 + 3 (F_6 + F_4)", size=11, color="#495057", anchor="middle"))

    # Player 1 Move (Winning move)
    frags.append(arrow(390, 110, 390, 140, color="#2b8a3e", sw=2.0))
    frags.append(text(400, 128, "Гравець 1 бере найменший доданок: F_4 = 3 камінці", size=11, bold=True, color="#2b8a3e"))

    # State after P1 move
    frags.append(rect(200, 145, 380, 55, rx=6, fill="#ebfbee", stroke="#2b8a3e", sw=1.5))
    frags.append(text(390, 168, "Лишилося: 8 камінців (число Фібоначчі F_6)", size=13, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(390, 188, "Гравець 2 може взяти не більше 2 × 3 = 6 камінців!", size=11, color="#c92a2a", anchor="middle"))

    # Player 2 moves options (All leading to P1 victory)
    frags.append(arrow(390, 200, 390, 230, color="#c92a2a", sw=1.5))
    frags.append(text(400, 218, "Гравець 2 мусить взяти від 1 до 6 камінців", size=11, color="#c92a2a"))

    frags.append(rect(150, 235, 480, 50, rx=6, fill="#fff0f6", stroke="#e64980", sw=1.2))
    frags.append(text(390, 257, "Гравець 2 НЕ може забрати всі 8 камінців за один хід.", size=11, bold=True, color="#c2255c", anchor="middle"))
    frags.append(text(390, 275, "Будь-який його хід розщеплює F_6 і віддає ініціативу Гравцю 1!", size=11, color="#495057", anchor="middle"))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'fig-fibonacci-nim.svg'), 780, 310, *frags, title="Виграшна стратегія у грі Фібоначчієвий нім")

if __name__ == '__main__':
    draw_zeckendorf_greedy()
    draw_fibonacci_code()
    draw_fibonacci_nim()
    print("Figures generated successfully.")

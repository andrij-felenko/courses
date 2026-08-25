import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import render, rect, line, text, circle, arrow, textbox, fitbox

def draw_character_orthogonality():
    w, h = 800, 460
    frags = []
    
    # Background
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="#cbd5e1", sw=1))
    
    # Title
    frags.append(text(w / 2, 32, "Ортогональність характерів Діріхле та проекція на класи залишків (mod 5)", size=16, bold=True, color="#0f172a", anchor="middle"))
    
    # Top box: Character Table mod 5
    frags.append(text(w / 2, 60, "Таблиця характерів група (ℤ/5ℤ)* з генератором g = 2", size=12, color="#475569", anchor="middle"))
    
    table_x, table_y = 60, 80
    cell_w, cell_h = 135, 32
    
    headers = ["n (mod 5)", "1", "2", "3", "4"]
    rows = [
        ["χ₀ (головний)", "1", "1", "1", "1"],
        ["χ₁ (квадратичний)", "1", "-1", "-1", "1"],
        ["χ₂ (комплексний)", "1", "i", "-i", "-1"],
        ["χ₃ (комплексний)", "1", "-i", "i", "-1"]
    ]
    
    # Render table header
    for j, h_text in enumerate(headers):
        x = table_x + j * cell_w
        bg_col = "#e2e8f0" if j == 0 else "#f1f5f9"
        frags.append(rect(x, table_y, cell_w, cell_h, fill=bg_col, stroke="#94a3b8", sw=1))
        frags.append(text(x + cell_w / 2, table_y + 20, h_text, size=12, bold=True, color="#1e293b", anchor="middle"))
        
    # Render table rows
    for i, row in enumerate(rows):
        y = table_y + (i + 1) * cell_h
        row_bg = "#f8fafc" if i % 2 == 0 else "#ffffff"
        for j, val in enumerate(row):
            x = table_x + j * cell_w
            col = "#0f172a"
            font_bold = False
            if j == 0:
                font_bold = True
                col = "#1e3a8a"
            elif val in ["i", "-i"]:
                col = "#2563eb"
                font_bold = True
            elif val == "-1":
                col = "#dc2626"
                font_bold = True
            frags.append(rect(x, y, cell_w, cell_h, fill=row_bg, stroke="#cbd5e1", sw=1))
            frags.append(text(x + cell_w / 2, y + 20, val, size=12, bold=font_bold, color=col, anchor="middle"))

    # Arrow down
    frags.append(arrow(w / 2, 225, w / 2, 260, color="#2563eb", sw=2))
    frags.append(text(w / 2 + 15, 247, "Скалярний добуток ⟨χ_a, χ_b⟩ = ∑_{n (mod q)} χ_a(n) · χ̄_b(n)", size=11, color="#1d4ed8", anchor="start"))

    # Bottom Split: Orthogonality Formula & Projection Mechanism
    b_left, _, _ = textbox(240, 335, "1. Перше співвідношення ортогональності:\n∑_{n (mod q)} χ_a(n) · χ̄_b(n) = φ(q) · δ_{a,b}\n\nХаратери утворюють ортонормований\nбазис у просторі функцій на (ℤ/qℤ)*", size=11.5, fill="#eff6ff", stroke="#3b82f6", color="#1e40af", bold=True)
    frags.append(b_left)
    
    b_right, _, _ = textbox(560, 335, "2. Проекційний фільтр арифметичної прогресії:\n∑_{χ (mod q)} χ̄(a) · χ(n) = φ(q),  якщо n ≡ a (mod q)\n∑_{χ (mod q)} χ̄(a) · χ(n) = 0,     якщо n ≢ a (mod q)\n\nВиділяє елементи потрібного класу a (mod q)!", size=11.5, fill="#ecfdf5", stroke="#10b981", color="#065f46", bold=True)
    frags.append(b_right)

    # Footnote box
    b_foot, _, _ = textbox(w / 2, 422, "Ключовий висновок: Ортогональність характерів перетворює суму за арифметичною прогресією на лінійну комбінацію L-функцій", size=11, fill="#f8fafc", stroke="#64748b", color="#334155", bold=True)
    frags.append(b_foot)

    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fig-character-orthogonality.svg')
    render(out_path, w, h, *frags, title="Ортогональність характерів Діріхле")
    print("Generated fig-character-orthogonality.svg successfully.")

def draw_l_function_zeros():
    w, h = 800, 480
    frags = []
    
    # Background
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="#cbd5e1", sw=1))
    
    # Title
    frags.append(text(w / 2, 32, "Аналітична структура L-функцій L(s, χ) у комплексній площині s = σ + i·t", size=16, bold=True, color="#0f172a", anchor="middle"))
    
    ox, oy = 280, 240
    
    # Regions
    # Re(s) > 1: Absolute convergence
    frags.append(rect(ox + 140, 70, 320, 320, fill="#ecfdf5", stroke="none"))
    # 0 < Re(s) < 1: Critical strip
    frags.append(rect(ox, 70, 140, 320, fill="#fefce8", stroke="none"))
    # Re(s) < 0: Left half-plane (trivial zeros)
    frags.append(rect(50, 70, ox - 50, 320, fill="#f8fafc", stroke="none"))

    # Axes
    frags.append(arrow(40, oy, 760, oy, color="#475569", sw=1.8))
    frags.append(arrow(ox, 410, ox, 55, color="#475569", sw=1.8))
    frags.append(text(765, oy + 18, "σ = Re(s)", size=12, bold=True, color="#334155", anchor="start"))
    frags.append(text(ox + 10, 65, "t = Im(s)", size=12, bold=True, color="#334155", anchor="start"))
    
    # Lines for Re(s) = 0, Re(s) = 1/2, Re(s) = 1
    x_half = ox + 70
    x_one = ox + 140
    
    # Critical line Re(s) = 1/2
    frags.append(line(x_half, 70, x_half, 390, color="#dc2626", sw=2, dash="6,4"))
    frags.append(text(x_half, 410, "σ = 1/2", size=12, bold=True, color="#dc2626", anchor="middle"))
    frags.append(text(x_half, 428, "Критична пряма (УГР / GRH)", size=10, color="#991b1b", anchor="middle"))

    # Line Re(s) = 1
    frags.append(line(x_one, 70, x_one, 390, color="#059669", sw=2, dash="4,4"))
    frags.append(text(x_one, 410, "σ = 1", size=12, bold=True, color="#059669", anchor="middle"))
    
    # Pole at s = 1 for chi_0
    frags.append(circle(x_one, oy, 8, fill="#ef4444", stroke="#991b1b", sw=2))
    frags.append(text(x_one + 12, oy - 15, "Полюс s=1 (лише для χ₀)", size=11, bold=True, color="#991b1b", anchor="start"))
    frags.append(text(x_one + 12, oy + 18, "L(1, χ) ≠ 0 (для χ ≠ χ₀!)", size=11, bold=True, color="#047857", anchor="start"))

    # Trivial zeros on negative real axis (s = -2, -4, -6...)
    for k, neg_x in enumerate([ox - 50, ox - 100, ox - 150]):
        frags.append(circle(neg_x, oy, 5, fill="#64748b", stroke="#334155", sw=1.5))
        frags.append(text(neg_x, oy + 16, f"-{2*(k+1)}", size=10, color="#475569", anchor="middle"))
    frags.append(text(ox - 100, oy - 20, "Тривіальні нулі (парні χ)", size=10, color="#475569", anchor="middle"))

    # Non-trivial zeros on Critical line Re(s) = 1/2
    zeros_y = [oy - 60, oy - 110, oy + 60, oy + 110]
    for zy in zeros_y:
        frags.append(circle(x_half, zy, 5.5, fill="#f59e0b", stroke="#b45309", sw=1.5))
    frags.append(text(x_half + 10, oy - 85, "Нетривіальні нулі (1/2 + i·t)", size=10, bold=True, color="#b45309", anchor="start"))

    # Region labels
    frags.append(text(x_one + 90, 100, "Область абсолютної\nзбіжності ряду та\nЕйлерового добутку\nRe(s) > 1", size=11, color="#065f46", bold=True, anchor="middle"))
    frags.append(text(ox + 35, 100, "Критична смуга\n0 < Re(s) < 1", size=11, color="#92400e", bold=True, anchor="middle"))

    # Bottom summary box
    b_bot, _, _ = textbox(w / 2, 452, "Узагальнена гіпотеза Рімана (GRH): усі нетривіальні нулі L(s, χ) лежать чітко на прямій Re(s) = 1/2", size=11.5, fill="#fef3c7", stroke="#d97706", color="#78350f", bold=True)
    frags.append(b_bot)

    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fig-l-function-zeros.svg')
    render(out_path, w, h, *frags, title="Структура нулів L-функцій")
    print("Generated fig-l-function-zeros.svg successfully.")

def draw_dirichlet_theorem_pipeline():
    w, h = 800, 480
    frags = []
    
    # Background
    frags.append(rect(0, 0, w, h, fill="#ffffff", stroke="#cbd5e1", sw=1))
    
    # Title
    frags.append(text(w / 2, 30, "Аналітичний конвеєр доведення теореми Діріхле про прості числа", size=16, bold=True, color="#0f172a", anchor="middle"))
    
    # Pipeline stages (boxes connected by arrows)
    stages = [
        ("1. Задача розподілу", "Знайти суму ∑_{p ≡ a (mod q)} 1/p\nВиділити прості числа в a + k·q", 120, 80, "#eff6ff", "#3b82f6", "#1e40af"),
        ("2. Харатери Діріхле", "Побудувати ортогональний базис χ (mod q)\nОртогональність знімає прогресію", 380, 80, "#f0fdf4", "#22c55e", "#15803d"),
        ("3. L-ряд та Ейлерів добуток", "L(s, χ) = ∑ χ(n)/nˢ = ∏ (1 - χ(p)/pˢ)⁻¹\nПерехід від дільників до простих чисел", 640, 80, "#faf5ff", "#a855f7", "#7e22ce"),
        
        ("4. Логарифмування ряду", "ln L(s, χ) ≈ ∑_{p} χ(p)/pˢ\nПеретворення добутку на суму", 640, 230, "#fff7ed", "#f97316", "#c2410c"),
        ("5. Проекція за ортогональністю", "∑_{χ} χ̄(a) ln L(s, χ) = φ(q) ∑_{p ≡ a} 1/pˢ\nВиділення суми за потрібним класом", 380, 230, "#fefce8", "#eab308", "#a16207"),
        ("6. Ключова умова L(1, χ) ≠ 0", "Для χ₀: ln L(s, χ₀) ~ ln 1/(s-1) → ∞\nДля χ ≠ χ₀: L(1, χ) ≠ 0 ⇒ ln L(1, χ) скінченне!", 120, 230, "#fef2f2", "#ef4444", "#b91c1c")
    ]

    for title, desc, cx, cy, bg, border, tc in stages:
        box, _, _ = textbox(cx, cy, f"{title}\n{desc}", size=11, fill=bg, stroke=border, color=tc, bold=True)
        frags.append(box)

    # Arrows between stages
    frags.append(arrow(210, 80, 290, 80, color="#3b82f6", sw=2))
    frags.append(arrow(470, 80, 550, 80, color="#22c55e", sw=2))
    frags.append(arrow(640, 130, 640, 180, color="#a855f7", sw=2))
    frags.append(arrow(550, 230, 470, 230, color="#f97316", sw=2))
    frags.append(arrow(290, 230, 210, 230, color="#eab308", sw=2))
    frags.append(arrow(120, 280, 120, 335, color="#ef4444", sw=2))

    # Final result box at bottom
    b_final, _, _ = textbox(w / 2, 395, "ГРАНІЧНИЙ ПЕРЕХІД s → 1⁺:\n∑_{p ≡ a (mod q)} 1/pˢ = (1 / φ(q)) · ln(1 / (s - 1)) + O(1) → ∞\nУ кожному класі a (mod q) з НСД(a, q) = 1 існує нескінченно багатьох простих чисел!", size=12.5, fill="#ecfdf5", stroke="#059669", color="#065f46", bold=True)
    frags.append(b_final)

    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fig-dirichlet-theorem-pipeline.svg')
    render(out_path, w, h, *frags, title="Аналітичний конвеєр теореми Діріхле")
    print("Generated fig-dirichlet-theorem-pipeline.svg successfully.")

if __name__ == "__main__":
    draw_character_orthogonality()
    draw_l_function_zeros()
    draw_dirichlet_theorem_pipeline()

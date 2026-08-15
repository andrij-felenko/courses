import sys
import os

# Add scripts directory to path (4 levels up from book/math/number-theory/roth-theorem)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, mtext, circle, fitbox, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')


def generate_roth_exponent_evolution():
    """Малює порівняльну діаграму еволюції показника діофантова наближення від Діріхле до Рота."""
    width, height = 760, 420
    frags = []

    # Заливка фону
    frags.append(rect(0, 0, width, height, fill=BG, stroke="none"))

    # Заголовок
    frags.append(text(width / 2, 24, "Еволюція показника μ у нерівності |α - p/q| < 1 / q μ", size=15, bold=True, color=INK))

    # Картки етапів
    stages = [
        ("Діріхле (1842)", "μ = 2", "Будь-які ірраціональні", "Некінченно багатьох p/q", "#f1f5f9", "#94a3b8"),
        ("Ліувілль (1844)", "μ = d", "Алгебраїчні ступеня d", "Жодного кращого наближення", "#e2e8f0", "#64748b"),
        ("Тюе (1909)", "μ = d/2 + 1 + ε", "Алгебраїчні d ≥ 3", "Скінченно багатьох розв'язків", "#dbeafe", "#3b82f6"),
        ("Зігель (1921)", "μ = 2√d + ε", "Покращення степеня", "Скінченно багатьох розв'язків", "#bfdbfe", "#2563eb"),
        ("Ґельфонд–Дайсон (1947)", "μ = √(2d) + ε", "Наближення до межі 2", "Скінченно багатьох розв'язків", "#93c5fd", "#1d4ed8"),
        ("Рот (1955)", "μ = 2 + ε", "Оптимальна межа для всіх d!", "Філдсівська премія 1958 року", "#dcfce7", "#16a34a"),
    ]

    y_start = 55
    card_h = 52
    gap = 8

    for idx, (author, exponent, applies_to, status, fill_col, border_col) in enumerate(stages):
        cy = y_start + idx * (card_h + gap)
        
        # Основна плашка
        frags.append(rect(30, cy, 700, card_h, fill=fill_col, stroke=border_col, rx=6, sw=1.5))
        
        # Автор та рік
        frags.append(fitbox(45, cy + 12, 170, 28, author, fill="none", border="none", color=INK, size=12, bold=True))
        
        # Показник (акцентний блок)
        frags.append(fitbox(225, cy + 10, 140, 32, exponent, fill="#ffffff", border=border_col, color=INK, size=13, bold=True))
        
        # Область застосування
        frags.append(fitbox(380, cy + 12, 160, 28, applies_to, fill="none", border="none", color=MUTED, size=11))
        
        # Результат / Висновок
        frags.append(fitbox(550, cy + 12, 165, 28, status, fill="none", border="none", color=INK, size=11, bold=True))

    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, 'roth-exponent-evolution.svg')
    render(out_path, width, height, *frags)
    print("Generated roth-exponent-evolution.svg")


def generate_roth_proof_architecture():
    """Малює схему структури доведення теореми Рота (суперечність між лемою Зігеля та лемою Рота)."""
    width, height = 760, 360
    frags = []

    # Заливка фону
    frags.append(rect(0, 0, width, height, fill=BG, stroke="none"))

    # Заголовок
    frags.append(text(width / 2, 22, "Архітектура суперечності у доведенні теореми Рота", size=15, bold=True, color=INK))

    # Блоки доведення
    boxes = [
        ("1. Припущення", "Існує m дуже хороших\nнаближень pᵢ/qᵢ\nq₁ ≪ q₂ ≪ ... ≪ q➬", 40, 65, 190, 85, "#fee2e2", "#ef4444"),
        ("2. Лема Зігеля", "Побудова многочлена P\nз цілими коефіцієнтами\nВисокий індекс у (α,...,α)", 285, 65, 190, 85, "#dbeafe", "#3b82f6"),
        ("3. Оцінка наближень", "Перенесення нуля:\nОбнулення похідних P\nу раціональних точках", 530, 65, 190, 85, "#f3e8ff", "#a855f7"),
    ]

    for title, desc, x, y, w, h, fill_c, border_c in boxes:
        frags.append(fitbox(x, y, w, h, f"{title}\n{desc}", fill=fill_c, border=border_c, color=INK, size=11))

    # Стрілки між верхніми блоками
    frags.append(line(230, 107, 285, 107, color=LINE, sw=2.0))
    frags.append(line(280, 103, 285, 107, color=LINE, sw=2.0))
    frags.append(line(280, 111, 285, 107, color=LINE, sw=2.0))

    frags.append(line(475, 107, 530, 107, color=LINE, sw=2.0))
    frags.append(line(525, 103, 530, 107, color=LINE, sw=2.0))
    frags.append(line(525, 111, 530, 107, color=LINE, sw=2.0))

    # Нижній блок 4: Лема Рота (бар'єр)
    frags.append(fitbox(285, 200, 435, 75, "4. Лема Рота (Арифметика многочленів)\nМногочлен з обмеженими коефіцієнтами НЕ може мати\nвисокого індексу в точках з q₁ ≪ q₂ ≪ ... ≪ q➬", fill="#fff7ed", border="#f97316", color=INK, size=11))

    # Стрілка вниз від блоку 3 до блоку 4
    frags.append(line(625, 150, 625, 237, color=LINE, sw=2.0))
    frags.append(line(625, 237, 720, 237, color=LINE, sw=2.0))
    frags.append(line(715, 233, 720, 237, color=LINE, sw=2.0))
    frags.append(line(715, 241, 720, 237, color=LINE, sw=2.0))

    # Блок суперечності
    frags.append(fitbox(40, 200, 190, 75, "СУПЕРЕЧНІСТЬ!\nОтже, m хороших\nнаближень не існує", fill="#fef2f2", border="#dc2626", color="#b91c1c", size=12, bold=True))

    # Стрілка від Леми Рота до Суперечності
    frags.append(line(285, 237, 230, 237, color="#dc2626", sw=2.0))
    frags.append(line(235, 233, 230, 237, color="#dc2626", sw=2.0))
    frags.append(line(235, 241, 230, 237, color="#dc2626", sw=2.0))

    # Нижня примітка
    frags.append(rect(40, 300, 680, 45, fill="#f8fafc", stroke="#cbd5e1", rx=4))
    frags.append(text(width / 2, 327, "Наслідок неефективності: суперечність виникає лише за припущення існування m розв'язків", size=11, color=MUTED))

    os.makedirs(IMG_DIR, exist_ok=True)
    out_path = os.path.join(IMG_DIR, 'roth-proof-architecture.svg')
    render(out_path, width, height, *frags)
    print("Generated roth-proof-architecture.svg")


if __name__ == '__main__':
    generate_roth_exponent_evolution()
    generate_roth_proof_architecture()

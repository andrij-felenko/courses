# -*- coding: utf-8 -*-
"""Фігури до статті «Множення за Монтгомері».
Генерує векторні схеми SVG у теці ./img/:
1. classical-vs-montgomery-pipeline.svg — порівняння конвеєрів: класичне ділення проти простору Монтгомері
2. montgomery-reduction-mechanism.svg — механізм REDC: обнулення молодших лімбів та точний зсув праворуч
3. cios-interleaved-loop.svg — архітектура інтегрованого сканування операндів CIOS (Coarsely Integrated Operand Scanning)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Порівняння класичного модулярного множення та множення за Монтгомері
# ─────────────────────────────────────────────────────────────────────────────
def fig_classical_vs_montgomery():
    W, H = 840, 360
    parts = []
    
    parts.append(rect(15, 15, 810, 330, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 42, "Порівняння конвеєрів: класичне ділення та простір Монтгомері", size=15, color=INK, bold=True))

    # Ліва колонка: Класичний підхід (Knuth Division)
    x1, y1 = 35, 70
    w1, h1 = 365, 255
    parts.append(rect(x1, y1, w1, h1, fill="#ffffff", stroke="#f87171", sw=1.2, rx=6))
    parts.append(rect(x1, y1, w1, 32, fill="#fef2f2", stroke="#f87171", sw=1, rx=6))
    parts.append(text(x1 + w1/2, y1 + 21, "Класичний підхід: довге ділення", size=13, color="#991b1b", bold=True))

    steps_left = [
        ("Операнди A, B ∈ [0, N-1]", "k лімбів (звичайний вигляд)"),
        ("Повне множення: T = A · B", "2k лімбів (наприклад, 4096 біт)"),
        ("Довге ділення: T mod N", "Оцінка q̂, нормалізація, віднімання"),
        ("Результат C = (A · B) mod N", "Складність ділення O(k²), гілкування")
    ]
    
    cur_y = y1 + 45
    for i, (title, sub) in enumerate(steps_left):
        box_color = "#fee2e2" if i == 2 else "#f1f5f9"
        border_color = "#ef4444" if i == 2 else "#cbd5e1"
        text_color = "#991b1b" if i == 2 else "#1e293b"
        
        parts.append(rect(x1 + 20, cur_y, w1 - 40, 38, fill=box_color, stroke=border_color, sw=1, rx=4))
        parts.append(text(x1 + w1/2, cur_y + 16, title, size=11, color=text_color, bold=True))
        parts.append(text(x1 + w1/2, cur_y + 30, sub, size=9.5, color="#64748b"))
        
        if i < len(steps_left) - 1:
            parts.append(arrow(x1 + w1/2, cur_y + 38, x1 + w1/2, cur_y + 48, color="#94a3b8", sw=1.5))
        cur_y += 50

    # Права колонка: Простір Монтгомері (Montgomery Domain)
    x2, y2 = 440, 70
    w2, h2 = 365, 255
    parts.append(rect(x2, y2, w2, h2, fill="#ffffff", stroke="#4ade80", sw=1.2, rx=6))
    parts.append(rect(x2, y2, w2, 32, fill="#f0fdf4", stroke="#4ade80", sw=1, rx=6))
    parts.append(text(x2 + w2/2, y2 + 21, "Простір Монтгомері: редукція REDC", size=13, color="#166534", bold=True))

    steps_right = [
        ("Вхід у простір: Ā = A·R mod N", "Один раз перед циклом множень"),
        ("Множення: T = Ā · B̄", "Звичайне множення поліномів/лімбів"),
        ("Редукція REDC: (T + m·N) / R", "Обнулення молодших біт + зсув праворуч"),
        ("Вихід із простору: C = REDC(C̄)", "Один раз наприкінці піднесення до степеня")
    ]
    
    cur_y = y2 + 45
    for i, (title, sub) in enumerate(steps_right):
        box_color = "#dcfce7" if i == 2 else "#f1f5f9"
        border_color = "#22c55e" if i == 2 else "#cbd5e1"
        text_color = "#166534" if i == 2 else "#1e293b"
        
        parts.append(rect(x2 + 20, cur_y, w2 - 40, 38, fill=box_color, stroke=border_color, sw=1, rx=4))
        parts.append(text(x2 + w2/2, cur_y + 16, title, size=11, color=text_color, bold=True))
        parts.append(text(x2 + w2/2, cur_y + 30, sub, size=9.5, color="#64748b"))
        
        if i < len(steps_right) - 1:
            parts.append(arrow(x2 + w2/2, cur_y + 38, x2 + w2/2, cur_y + 48, color="#94a3b8", sw=1.5))
        cur_y += 50

    out_file = os.path.join(OUT, "classical-vs-montgomery-pipeline.svg")
    render(out_file, W, H, *parts)
    print(f"Generated {out_file}")

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Механізм редукції REDC: додавання m·N та зсув на R
# ─────────────────────────────────────────────────────────────────────────────
def fig_montgomery_reduction_mechanism():
    W, H = 840, 370
    parts = []
    
    parts.append(rect(15, 15, 810, 340, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 42, "Механізм REDC: обнулення молодших розрядів та точне ділення на R", size=15, color=INK, bold=True))

    y1 = 80
    parts.append(text(125, y1 + 22, "Добуток T = Ā · B̄:", size=12, color="#1e293b", anchor="end", bold=True))
    parts.append(rect(140, y1, 280, 36, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=4))
    parts.append(text(280, y1 + 23, "Молодша частина T mod R", size=11, color="#991b1b", bold=True))
    parts.append(rect(430, y1, 280, 36, fill="#e0e7ff", stroke="#6366f1", sw=1.2, rx=4))
    parts.append(text(570, y1 + 23, "Старша частина ⌊T / R⌋", size=11, color="#3730a3", bold=True))

    parts.append(text(125, y1 + 65, "+  m · N :", size=12, color="#1e293b", anchor="end", bold=True))
    parts.append(rect(140, y1 + 48, 280, 36, fill="#fef3c7", stroke="#f59e0b", sw=1.2, rx=4))
    parts.append(text(280, y1 + 71, "m · N mod R = (-T) mod R", size=11, color="#92400e", bold=True))
    parts.append(rect(430, y1 + 48, 280, 36, fill="#fef3c7", stroke="#f59e0b", sw=1.2, rx=4))
    parts.append(text(570, y1 + 71, "Старші лімби m · N", size=11, color="#92400e"))

    parts.append(line(140, y1 + 94, 710, y1 + 94, color="#334155", sw=2))

    y3 = y1 + 104
    parts.append(text(125, y3 + 22, "Сума T + m · N :", size=12, color="#1e293b", anchor="end", bold=True))
    parts.append(rect(140, y3, 280, 36, fill="#dcfce7", stroke="#22c55e", sw=1.5, rx=4))
    parts.append(text(280, y3 + 23, "0000...0000  (k нульових лімбів)", size=11, color="#166534", bold=True))
    parts.append(rect(430, y3, 280, 36, fill="#dbeafe", stroke="#3b82f6", sw=1.5, rx=4))
    parts.append(text(570, y3 + 23, "Ненульова частина U · R", size=11, color="#1e40af", bold=True))

    parts.append(arrow(570, y3 + 36, 570, y3 + 68, color="#2563eb", sw=2))
    parts.append(text(590, y3 + 54, "Зсув праворуч на k слів (÷ R)", size=11, color="#2563eb", anchor="start", bold=True))

    y4 = y3 + 75
    parts.append(text(125, y4 + 22, "Результат U :", size=12, color="#1e293b", anchor="end", bold=True))
    parts.append(rect(430, y4, 280, 36, fill="#bbf7d0", stroke="#16a34a", sw=1.5, rx=4))
    parts.append(text(570, y4 + 23, "U = (T + m · N) / R < 2N", size=12, color="#14532d", bold=True))

    parts.append(rect(140, y4 + 48, 570, 30, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    parts.append(text(425, y4 + 68, "Фінальна корекція: якщо U ≥ N, повернути U - N; інакше повернути U (рівно 1 віднімання)", size=11, color="#334155"))

    out_file = os.path.join(OUT, "montgomery-reduction-mechanism.svg")
    render(out_file, W, H, *parts)
    print(f"Generated {out_file}")

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Архітектура CIOS (Coarsely Integrated Operand Scanning)
# ─────────────────────────────────────────────────────────────────────────────
def fig_cios_interleaved_loop():
    W, H = 840, 380
    parts = []
    
    parts.append(rect(15, 15, 810, 350, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 42, "Архітектура CIOS: чергування множення та редукції в єдиному циклі", size=15, color=INK, bold=True))

    x0, y0 = 40, 68
    w0, h0 = 760, 275
    parts.append(rect(x0, y0, w0, h0, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=6))
    parts.append(rect(x0, y0, w0, 30, fill="#e0f2fe", stroke="#0284c7", sw=1, rx=6))
    parts.append(text(x0 + 20, y0 + 20, "Зовнішній цикл: для кожного лімба A[i] (від i = 0 до k-1)", size=12, color="#0369a1", anchor="start", bold=True))

    b1_x, b1_y, b1_w, b1_h = x0 + 25, y0 + 45, 335, 105
    parts.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#f8fafc", stroke="#94a3b8", sw=1, rx=4))
    parts.append(text(b1_x + b1_w/2, b1_y + 22, "1. Накопичення: T = T + A[i] · B", size=12, color="#0f172a", bold=True))
    parts.append(line(b1_x + 15, b1_y + 32, b1_x + b1_w - 15, b1_y + 32, color="#e2e8f0", sw=1))
    parts.append(text(b1_x + 15, b1_y + 52, "Внутрішній цикл j від 0 до k-1:", size=10.5, color="#475569", anchor="start"))
    parts.append(text(b1_x + 15, b1_y + 72, "(C, S) = T[j] + A[i] · B[j] + C", size=11, color="#1e293b", anchor="start", bold=True))
    parts.append(text(b1_x + 15, b1_y + 92, "T[j] = S;  T[k] = C", size=10.5, color="#475569", anchor="start"))

    parts.append(arrow(b1_x + b1_w, b1_y + 52, b1_x + b1_w + 35, b1_y + 52, color="#0284c7", sw=1.5))

    b2_x, b2_y, b2_w, b2_h = b1_x + b1_w + 35, b1_y, 340, 105
    parts.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#fef3c7", stroke="#f59e0b", sw=1, rx=4))
    parts.append(text(b2_x + b2_w/2, b2_y + 22, "2. Коефіцієнт редукції m", size=12, color="#92400e", bold=True))
    parts.append(line(b2_x + 15, b2_y + 32, b2_x + b2_w - 15, b2_y + 32, color="#fde68a", sw=1))
    parts.append(text(b2_x + b2_w/2, b2_y + 55, "m = (T[0] · n0') mod 2⁶⁴", size=13, color="#b45309", bold=True))
    parts.append(text(b2_x + b2_w/2, b2_y + 80, "Потребує лише 1 множення машинних слів!", size=10.5, color="#78350f"))

    parts.append(arrow(b2_x + b2_w/2, b2_y + b2_h, b2_x + b2_w/2, b2_y + b2_h + 18, color="#0284c7", sw=1.5))

    b3_x, b3_y, b3_w, b3_h = x0 + 25, y0 + 168, 710, 92
    parts.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=4))
    parts.append(text(b3_x + b3_w/2, b3_y + 20, "3. Редукція поточного розряду: T = (T + m · N) / 2⁶⁴", size=12, color="#166534", bold=True))
    parts.append(line(b3_x + 15, b3_y + 30, b3_x + b3_w - 15, b3_y + 30, color="#bbf7d0", sw=1))
    
    parts.append(text(b3_x + 20, b3_y + 50, "Додавання m · N: (C, S) = T[j] + m · N[j] + C;", size=11, color="#1e293b", anchor="start"))
    parts.append(text(b3_x + 20, b3_y + 70, "Миттєвий зсув: T[j-1] = S;  T[0] стає 0 і відкидається на кожній ітерації i", size=11, color="#15803d", anchor="start", bold=True))
    parts.append(text(b3_x + b3_w - 20, b3_y + 60, "Пам'ять: лише k + 2 лімби в регістрах L1!", size=11, color="#0369a1", anchor="end", bold=True))

    out_file = os.path.join(OUT, "cios-interleaved-loop.svg")
    render(out_file, W, H, *parts)
    print(f"Generated {out_file}")

if __name__ == "__main__":
    fig_classical_vs_montgomery()
    fig_montgomery_reduction_mechanism()
    fig_cios_interleaved_loop()

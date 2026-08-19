# -*- coding: utf-8 -*-
import os
import sys

# Підключаємо scripts/ з кореня репозиторію
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

IMG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
os.makedirs(IMG_DIR, exist_ok=True)

def generate_dpll_t_architecture():
    path = os.path.join(IMG_DIR, 'dpll-t-lia-architecture.svg')
    w, h = 760, 420
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    # Header
    frags.append(text(w / 2, 35, "Архітектура DPLL(T): Взаємодія CDCL-рушія та LIA-сольвера", size=16, bold=True))
    frags.append(text(w / 2, 55, "Ліниве поєднання булевого пошуку та теорії лінійної цілочисельної арифметики", size=12, color=MUTED))
    
    # Left container: SAT Engine (CDCL)
    frags.append(rect(30, 80, 290, 290, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(175, 105, "Булевий CDCL-рушій", size=15, bold=True, color="#1e293b"))
    frags.append(text(175, 123, "(Булева абстракція формули)", size=11, color=MUTED))
    
    b_dec, _, _ = textbox(175, 160, "Прийняття рішень\nта евристика VSIDS", size=12, fill="#ffffff", stroke="#cbd5e1", min_w=240)
    frags.append(b_dec)
    
    b_bcp, _, _ = textbox(175, 225, "Булеве поширення (BCP)\nчерез списки спостереження", size=12, fill="#ffffff", stroke="#cbd5e1", min_w=240)
    frags.append(b_bcp)
    
    b_learn, _, _ = textbox(175, 305, "Аналіз конфліктів 1-UIP\nта вивчення диз'юнктів", size=12, fill="#eff6ff", stroke="#3b82f6", min_w=240)
    frags.append(b_learn)
    
    # Right container: LIA Theory Solver
    frags.append(rect(440, 80, 290, 290, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(585, 105, "LIA-сольвер теорії", size=15, bold=True, color="#1e293b"))
    frags.append(text(585, 123, "(Перевірка кон'юнкцій обмежень)", size=11, color=MUTED))
    
    b_tbl, _, _ = textbox(585, 160, "Симплекс-табло (LRA)\nІнкрементальні шарніри (pivoting)", size=12, fill="#ffffff", stroke="#cbd5e1", min_w=250)
    frags.append(b_tbl)
    
    b_bb, _, _ = textbox(585, 225, "Цілочисельне розгалуження\nBranch & Bound / Gomory Cuts", size=12, fill="#ffffff", stroke="#cbd5e1", min_w=250)
    frags.append(b_bb)
    
    b_expl, _, _ = textbox(585, 305, "Генерація пояснень конфлікту\n(Infeasibility Explanation)", size=12, fill="#fef2f2", stroke="#ef4444", min_w=250)
    frags.append(b_expl)
    
    # Interaction arrows in middle
    # Top arrow: Literal assignments (CDCL -> Theory)
    frags.append(arrow(320, 155, 440, 155, color="#2563eb", sw=2))
    b_a1, _, _ = textbox(380, 135, "Присвоєння T-атомів\n{a₁x + a₂y ≤ c}", size=10, fill="#eff6ff", stroke="#93c5fd", pad=4)
    frags.append(b_a1)
    
    # Middle arrow: Theory Propagation (Theory -> CDCL)
    frags.append(arrow(440, 225, 320, 225, color="#16a34a", sw=2))
    b_a2, _, _ = textbox(380, 205, "T-поширення\n(виведені наслідки)", size=10, fill="#f0fdf4", stroke="#86efac", pad=4)
    frags.append(b_a2)
    
    # Bottom arrow: Conflict Clause / Lemma (Theory -> CDCL)
    frags.append(arrow(440, 305, 320, 305, color="#dc2626", sw=2))
    b_a3, _, _ = textbox(380, 285, "Лема конфлікту (UNSAT)\n¬(l₁ ∧ l₂ ∧ ... ∧ l_k)", size=10, fill="#fef2f2", stroke="#fca5a5", pad=4)
    frags.append(b_a3)
    
    # Footer explanatory note
    frags.append(text(w / 2, 395, "CDCL керує комбінаторним перебором булевої структури, а LIA-сольвер перевіряє геометричну сумісність у просторі Zⁿ", size=11, color="#475569"))
    
    render(path, w, h, *frags)

def generate_simplex_branch_and_bound():
    path = os.path.join(IMG_DIR, 'simplex-branch-and-bound-lia.svg')
    w, h = 720, 430
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    # Header
    frags.append(text(w / 2, 35, "Геометрія LIA: Релаксація, розгалуження та площини відтинання", size=16, bold=True))
    frags.append(text(w / 2, 55, "Пошук цілочисельного розв'язку в неперервному многограннику обмежень", size=12, color=MUTED))
    
    # Coordinate system area on Left (cx=220, cy=240, scale=45 px per unit)
    ox, oy = 90, 350
    
    # Grid lines & integer lattice points
    for i in range(1, 6):
        frags.append(line(ox + i * 50, oy, ox + i * 50, oy - 260, color="#f1f5f9", sw=1, dash="2,2"))
        frags.append(text(ox + i * 50, oy + 18, str(i), size=11, color=MUTED))
    for j in range(1, 6):
        frags.append(line(ox, oy - j * 50, ox + 280, oy - j * 50, color="#f1f5f9", sw=1, dash="2,2"))
        frags.append(text(ox - 15, oy - j * 50 + 4, str(j), size=11, color=MUTED))
        
    # Axes
    frags.append(arrow(ox, oy, ox + 300, oy, color=LINE, sw=1.5))
    frags.append(text(ox + 310, oy + 4, "x₁", size=13, bold=True))
    frags.append(arrow(ox, oy, ox, oy - 275, color=LINE, sw=1.5))
    frags.append(text(ox - 4, oy - 285, "x₂", size=13, bold=True))
    
    # Continuous Polytope (LRA relaxation)
    # Vertices in coords: (1.2, 1.0), (4.5, 1.2), (3.6, 4.4), (1.5, 3.8)
    poly_pts = [
        (ox + 1.2 * 50, oy - 1.0 * 50),
        (ox + 4.5 * 50, oy - 1.2 * 50),
        (ox + 3.4 * 50, oy - 4.2 * 50),
        (ox + 1.5 * 50, oy - 3.8 * 50)
    ]
    poly_path = "M %g %g L %g %g L %g %g L %g %g Z" % (
        poly_pts[0][0], poly_pts[0][1],
        poly_pts[1][0], poly_pts[1][1],
        poly_pts[2][0], poly_pts[2][1],
        poly_pts[3][0], poly_pts[3][1]
    )
    frags.append(f'<path d="{poly_path}" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>')
    frags.append(text(ox + 2.5 * 50, oy - 2.3 * 50, "Многогранник LRA", size=11, color="#1e40af", bold=True))
    
    # Integer points inside / near polytope
    int_points = [
        (2, 2, True), (2, 3, True), (3, 2, True), (3, 3, True), (4, 2, True),
        (1, 1, False), (1, 2, False), (1, 3, False), (2, 1, False), (2, 4, False),
        (3, 1, False), (3, 4, False), (4, 1, False), (4, 3, False), (4, 4, False)
    ]
    for px, py, inside in int_points:
        col = "#16a34a" if inside else "#94a3b8"
        r = 3.5 if inside else 2.5
        frags.append(circle(ox + px * 50, oy - py * 50, r, fill=col, stroke=col))
        
    # Non-integer LP optimal vertex (e.g. x1 = 2.6, x2 = 4.0)
    fx, fy = ox + 2.6 * 50, oy - 4.0 * 50
    frags.append(circle(fx, fy, 5, fill="#ef4444", stroke="#991b1b", sw=1.5))
    frags.append(text(fx + 10, fy - 8, "x* = (2.6, 4.0)", size=11, bold=True, color="#b91c1c", anchor="start"))
    
    # Branching lines: x1 <= 2 and x1 >= 3
    bx1 = ox + 2 * 50
    bx2 = ox + 3 * 50
    frags.append(line(bx1, oy, bx1, oy - 260, color="#d97706", sw=1.8, dash="4,3"))
    frags.append(line(bx2, oy, bx2, oy - 260, color="#d97706", sw=1.8, dash="4,3"))
    frags.append(text(bx1 - 6, oy - 245, "x₁ ≤ 2", size=10, bold=True, color="#b45309", anchor="end"))
    frags.append(text(bx2 + 6, oy - 245, "x₁ ≥ 3", size=10, bold=True, color="#b45309", anchor="start"))
    
    # Right panel: Explanatory blocks
    rx = 550
    b_step1, _, _ = textbox(rx, 115, "1. Неперервна релаксація (LRA)\nСимплекс знаходить дробовий\nрозв'язок вершини x* = (2.6, 4.0)", size=11, fill="#f8fafc", stroke="#cbd5e1", min_w=280)
    frags.append(b_step1)
    
    b_step2, _, _ = textbox(rx, 205, "2. Розгалуження (Branch & Bound)\nСтворення леми розщеплення:\n(x₁ ≤ 2 ∨ x₁ ≥ 3)\nВилучає смугу 2 < x₁ < 3 без Z-точок", size=11, fill="#fffbeb", stroke="#f59e0b", min_w=280)
    frags.append(b_step2)
    
    b_step3, _, _ = textbox(rx, 305, "3. Відтинання Гоморі (Cutting Plane)\nДодавання нерівності Σ cⱼ xⱼ ≤ d,\nяка відсікає дробову вершину x*,\nзберігаючи всі цілі точки (зелені)", size=11, fill="#f0fdf4", stroke="#22c55e", min_w=280)
    frags.append(b_step3)
    
    # Footer
    frags.append(text(w / 2, 405, "Цілочисельні розв'язки LIA утворюють ґратку в Zⁿ. Симплекс звужує многогранник відтинаннями доти, доки вершина не стане цілою", size=10, color="#64748b"))
    
    render(path, w, h, *frags)

def generate_omega_test_shadows():
    path = os.path.join(IMG_DIR, 'omega-test-shadows.svg')
    w, h = 720, 390
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    # Header
    frags.append(text(w / 2, 35, "Омега-тест Вільяма П'ю: Проекції та тіні обмежень", size=16, bold=True))
    frags.append(text(w / 2, 55, "Елімінація цілочисельних змінних через дійсну, темну та сіру тіні", size=12, color=MUTED))
    
    # Diagram layout: Projection axis at bottom
    cx = 360
    
    # Box 1: Real Shadow (Дійсна тінь)
    frags.append(rect(80, 95, 560, 65, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(text(100, 125, "Дійсна тінь (Real Shadow)", size=13, bold=True, color="#1d4ed8", anchor="start"))
    frags.append(text(100, 145, "Неперервна проекція Фур'є-Моцкіна. Якщо тут немає дійсного розв'язку → формула UNSAT", size=11, color="#1e40af", anchor="start"))
    
    # Box 2: Dark Shadow (Темна тінь)
    frags.append(rect(160, 175, 400, 65, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(text(180, 205, "Темна тінь (Dark Shadow)", size=13, bold=True, color="#15803d", anchor="start"))
    frags.append(text(180, 225, "Звужена проекція: кожна ціла точка гарантовано має цілий прообраз → SAT", size=11, color="#166534", anchor="start"))
    
    # Box 3 & 4: Gray Shadow (Сіра тінь - бічні інтервали)
    frags.append(rect(80, 255, 75, 60, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(117, 282, "Сіра тінь", size=11, bold=True, color="#b45309"))
    frags.append(text(117, 298, "Перебір", size=10, color="#92400e"))
    
    frags.append(rect(565, 255, 75, 60, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(602, 282, "Сіра тінь", size=11, bold=True, color="#b45309"))
    frags.append(text(602, 298, "Перебір", size=10, color="#92400e"))
    
    frags.append(rect(165, 255, 390, 60, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=6))
    frags.append(text(360, 282, "Область гарантованої цілочисельності (Dark Shadow)", size=11, color="#475569"))
    frags.append(text(360, 298, "Розв'язок знайдено безпосередньо без перебору гілок", size=10, color=MUTED))
    
    # Bottom projection arrows
    frags.append(arrow(80, 335, 640, 335, color=LINE, sw=1.5))
    frags.append(text(360, 355, "Вісь спроектованих змінних z = Σ cᵢ xᵢ", size=11, color=MUTED))
    
    # Explanatory caption
    frags.append(text(w / 2, 375, "Омега-тест працює точно: темна тінь дає швидкий SAT, відсутність дійсної — UNSAT, а сіра тінь вимагає вичерпного тестування скінченного набору точок", size=10, color="#475569"))
    
    render(path, w, h, *frags)

def generate_presburger_quantifier_elimination():
    path = os.path.join(IMG_DIR, 'presburger-quantifier-elimination.svg')
    w, h = 740, 400
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    # Header
    frags.append(text(w / 2, 35, "Елімінація кванторів у теорії Пресбургера (Алгоритм Купера)", size=16, bold=True))
    frags.append(text(w / 2, 55, "Зведення ∃x. F(x) до скінченної диз'юнкції безкванторних формул за періодичністю конгруенцій", size=12, color=MUTED))
    
    # Formula transformation box at top
    b_form, _, _ = textbox(w / 2, 105, "Початкова кванторна формула: ∃x. ( ∧ᵢ (aᵢ ≤ x)  ∧  ∧ⱼ (x ≤ bⱼ)  ∧  ∧ₖ (dₖ | (x + cₖ)) )\n↓ Еквівалентне розгортання через найменше спільне кратне δ = НСК(d₁, ..., dₘ)", size=11, fill="#f8fafc", stroke="#94a3b8", min_w=680)
    frags.append(b_form)
    
    # Number line representation
    py = 230
    frags.append(line(50, py, 690, py, color=LINE, sw=2))
    frags.append(arrow(680, py, 700, py, color=LINE, sw=2))
    frags.append(text(705, py + 4, "x", size=13, bold=True))
    
    # Lower bound point a_i
    frags.append(circle(160, py, 6, fill="#ef4444", stroke="#991b1b", sw=1.5))
    frags.append(text(160, py - 14, "Нижня межа aᵢ", size=11, bold=True, color="#b91c1c"))
    frags.append(line(160, py - 6, 160, py + 20, color="#ef4444", sw=1.5))
    
    # Periodic test points a_i + 1, a_i + 2, ..., a_i + δ
    delta_w = 260
    frags.append(rect(160, py - 35, delta_w, 70, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=4))
    frags.append(text(160 + delta_w / 2, py - 42, "Інтервал тестових точок: aᵢ + j, де j ∈ {1, 2, ..., δ}", size=11, bold=True, color="#15803d"))
    
    # Dots representing test points
    for j in range(1, 6):
        tx = 160 + j * (delta_w / 6)
        frags.append(circle(tx, py, 4, fill="#16a34a", stroke="#14532d"))
        frags.append(text(tx, py + 18, f"aᵢ+{j}", size=9, color="#166534"))
        
    frags.append(circle(160 + delta_w, py, 6, fill="#16a34a", stroke="#14532d", sw=1.5))
    frags.append(text(160 + delta_w, py + 18, "aᵢ+δ", size=10, bold=True, color="#166534"))
    
    # Upper bound b_j
    frags.append(circle(600, py, 6, fill="#3b82f6", stroke="#1d4ed8", sw=1.5))
    frags.append(text(600, py - 14, "Верхня межа bⱼ", size=11, bold=True, color="#1d4ed8"))
    frags.append(line(600, py - 6, 600, py + 20, color="#3b82f6", sw=1.5))
    
    # Elimination result box at bottom
    b_res, _, _ = textbox(w / 2, 330, "Результат елімінації: F_elim ≡ ∨ᵢ ∨ⱼ₌₁^δ F(aᵢ + j)  ∨  F_{-∞}\n(Формула стає безкванторною з предикатами конгруенцій d | term)", size=12, bold=True, fill="#eff6ff", stroke="#3b82f6", min_w=680)
    frags.append(b_res)
    
    # Explanatory footer
    frags.append(text(w / 2, 385, "Оскільки конгруенції dₖ | (x + cₖ) повторюються з періодом δ, достатньо перевірити перші δ цілих значень вище кожної нижньої межі", size=10, color="#475569"))
    
    render(path, w, h, *frags)

if __name__ == "__main__":
    generate_dpll_t_architecture()
    generate_simplex_branch_and_bound()
    generate_omega_test_shadows()
    generate_presburger_quantifier_elimination()
    print("All figures generated successfully.")

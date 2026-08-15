# -*- coding: utf-8 -*-
import os
import sys

# Підключаємо scripts/ з кореня репозиторію
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

IMG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
os.makedirs(IMG_DIR, exist_ok=True)

def generate_ast_variables():
    path = os.path.join(IMG_DIR, 'tseytin-ast-variables.svg')
    w, h = 600, 360
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    # Заголовок схеми
    frags.append(text(w / 2, 35, "Синтаксичне дерево формули F = (A ∧ B) ∨ ¬C", size=16, bold=True))
    frags.append(text(w / 2, 55, "Призначення допоміжних змінних x₁, x₂ для внутрішніх вузлів", size=12, color=MUTED))
    
    # Корінь (OR) -> x₂
    # Вузол 1: x₂ = x₁ ∨ ¬C
    b_root, _, _ = textbox(300, 110, "Корінь (∨)\nЗмінна x₂", size=13, fill="#eaf0fd", stroke=NEG, sw=2)
    frags.append(b_root)
    
    # Лівий вузол (AND) -> x₁
    b_left, _, _ = textbox(180, 210, "Підвузол (∧)\nЗмінна x₁", size=13, fill="#eaf0fd", stroke=NEG, sw=2)
    frags.append(b_left)
    
    # Правий вузол (NOT) -> x₃ (або ¬C)
    b_right, _, _ = textbox(420, 210, "Підвузол (¬)\nЗмінна x₃", size=13, fill="#eaf0fd", stroke=NEG, sw=2)
    frags.append(b_right)
    
    # Листя (A, B, C)
    b_a, _, _ = textbox(110, 300, "Листок A\n(вхідна)", size=12, fill="#f4f6f8", stroke=LINE)
    b_b, _, _ = textbox(250, 300, "Листок B\n(вхідна)", size=12, fill="#f4f6f8", stroke=LINE)
    b_c, _, _ = textbox(420, 300, "Листок C\n(вхідна)", size=12, fill="#f4f6f8", stroke=LINE)
    
    frags.extend([b_a, b_b, b_c])
    
    # Зв'язки (стрілки)
    frags.append(arrow(260, 130, 200, 190, color=LINE, sw=1.5))
    frags.append(arrow(340, 130, 400, 190, color=LINE, sw=1.5))
    
    frags.append(arrow(155, 230, 125, 280, color=LINE, sw=1.5))
    frags.append(arrow(205, 230, 235, 280, color=LINE, sw=1.5))
    frags.append(arrow(420, 230, 420, 280, color=LINE, sw=1.5))
    
    # Виділення еквівалентностей
    frags.append(text(80, 170, "x₁ ↔ (A ∧ B)", size=12, color=FIELD, bold=True, anchor="start"))
    frags.append(text(460, 170, "x₃ ↔ ¬C", size=12, color=FIELD, bold=True, anchor="start"))
    frags.append(text(340, 110, "x₂ ↔ (x₁ ∨ x₃)", size=12, color=POS, bold=True, anchor="start"))

    render(path, w, h, *frags)

def generate_growth_comparison():
    path = os.path.join(IMG_DIR, 'exponential-vs-tseytin-growth.svg')
    w, h = 640, 380
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    frags.append(text(w / 2, 35, "Зростання розміру КНФ залежно від кількості операцій N", size=16, bold=True))
    frags.append(text(w / 2, 55, "Порівняння наївного дистрибутивного перетворення та методу Цейтіна", size=12, color=MUTED))
    
    # Вісі координат
    ox, oy = 80, 320
    length_x, length_y = 500, 240
    
    frags.append(arrow(ox, oy, ox + length_x, oy, color=LINE, sw=2))
    frags.append(arrow(ox, oy, ox, oy - length_y, color=LINE, sw=2))
    
    frags.append(text(ox + length_x - 10, oy + 25, "Розмір вхідної формули N (кількість вентилів / вузлів)", size=12, anchor="end"))
    frags.append(text(ox - 15, oy - length_y + 10, "Кількість диз'юнктів у КНФ", size=12, anchor="start"))
    
    # Експоненційна крива (дистрибутивне)
    path_exp = "M 80 320 Q 220 315 280 270 T 360 80"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_exp, POS))
    frags.append(text(330, 95, "Наївне розкриття (Дистрибутивність): O(2ⁿ)", size=13, color=POS, bold=True, anchor="start"))
    
    # Лінійна крива (Цейтін)
    path_tseytin = "M 80 320 L 530 230"
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (path_tseytin, FIELD))
    frags.append(text(460, 215, "Перетворення Цейтіна: O(N)", size=13, color=FIELD, bold=True, anchor="start"))
    
    # Позначки на осі N
    for i, val in enumerate(["5", "10", "20", "30", "50"]):
        px = ox + (i + 1) * 90
        frags.append(line(px, oy - 4, px, oy + 4, color=LINE, sw=1))
        frags.append(text(px, oy + 20, val, size=11, color=MUTED))
        
    # Легенда / підписи точок
    frags.append(circle(280, 270, 4, fill=POS, stroke=POS))
    frags.append(text(285, 290, "При N=50 дистрибутивне > 10¹⁵ клауз", size=11, color=POS))
    
    frags.append(circle(440, 248, 4, fill=FIELD, stroke=FIELD))
    frags.append(text(420, 275, "При N=50 Цейтін ≈ 150 клауз", size=11, color=FIELD))

    render(path, w, h, *frags)

def generate_gate_mapping():
    path = os.path.join(IMG_DIR, 'gate-to-cnf-mapping.svg')
    w, h = 680, 360
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    frags.append(text(w / 2, 35, "Локальне кодування логічних елементів у диз'юнкти КНФ", size=16, bold=True))
    frags.append(text(w / 2, 55, "Кожен вентиль еквівалентний тотожності p ↔ f(q, r) і дає 2-4 диз'юнкти", size=12, color=MUTED))
    
    # Блок AND
    b_and, _, _ = textbox(120, 120, "Вентиль AND\np ↔ (q ∧ r)", size=13, fill="#eaf0fd", stroke=NEG, sw=2)
    frags.append(b_and)
    frags.append(textbox(120, 220, "Диз'юнкти КНФ:\n(¬p ∨ q)\n(¬p ∨ r)\n(p ∨ ¬q ∨ ¬r)", size=12, fill="#f4f6f8", stroke=LINE)[0])
    
    # Блок OR
    b_or, _, _ = textbox(340, 120, "Вентиль OR\np ↔ (q ∨ r)", size=13, fill="#eaf0fd", stroke=NEG, sw=2)
    frags.append(b_or)
    frags.append(textbox(340, 220, "Диз'юнкти КНФ:\n(p ∨ ¬q)\n(p ∨ ¬r)\n(¬p ∨ q ∨ r)", size=12, fill="#f4f6f8", stroke=LINE)[0])
    
    # Блок XOR
    b_xor, _, _ = textbox(560, 120, "Вентиль XOR\np ↔ (q ⊕ r)", size=13, fill="#fdecea", stroke=POS, sw=2)
    frags.append(b_xor)
    frags.append(textbox(560, 220, "Диз'юнкти КНФ:\n(¬p ∨ ¬q ∨ ¬r)\n(¬p ∨ q ∨ r)\n(p ∨ ¬q ∨ r)\n(p ∨ q ∨ ¬r)", size=12, fill="#f4f6f8", stroke=LINE)[0])
    
    # Нижня висновок-примітка
    frags.append(text(w / 2, 320, "Загальний розмір КНФ = Кон'юнкція КНФ-блоків усіх вентилів + Одиничний диз'юнкт кореня (x_root)", size=12, color=FIELD, bold=True))

    render(path, w, h, *frags)

def generate_sat_pipeline():
    path = os.path.join(IMG_DIR, 'sat-solver-pipeline.svg')
    w, h = 680, 280
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    frags.append(text(w / 2, 35, "Конвеєр обробки формули у сучасних SAT-системах", size=16, bold=True))
    
    # Блоки конвеєра
    b1, _, _ = textbox(90, 130, "Вхідна формула F\n(AST / Дерево)", size=12, fill="#f4f6f8", stroke=LINE)
    b2, _, _ = textbox(250, 130, "Перетворення\nЦейтіна", size=12, fill="#eaf0fd", stroke=NEG, sw=2)
    b3, _, _ = textbox(410, 130, "Формат DIMACS\n(КНФ формула F')", size=12, fill="#f4f6f8", stroke=LINE)
    b4, _, _ = textbox(570, 130, "CDCL SAT Solver\n(Z3 / MiniSAT)", size=12, fill="#eaf2ea", stroke=FIELD, sw=2)
    
    frags.extend([b1, b2, b3, b4])
    
    frags.append(arrow(150, 130, 190, 130, color=LINE, sw=2))
    frags.append(arrow(310, 130, 340, 130, color=LINE, sw=2))
    frags.append(arrow(470, 130, 500, 130, color=LINE, sw=2))
    
    # Виходи SAT розв'язувача
    frags.append(arrow(570, 175, 510, 230, color=FIELD, sw=1.5))
    frags.append(arrow(570, 175, 630, 230, color=POS, sw=1.5))
    
    frags.append(textbox(510, 240, "SAT + Модель", size=11, fill="#eaf2ea", stroke=FIELD)[0])
    frags.append(textbox(630, 240, "UNSAT (Нездійсненна)", size=11, fill="#fdecea", stroke=POS)[0])

    render(path, w, h, *frags)

if __name__ == '__main__':
    generate_ast_variables()
    generate_growth_comparison()
    generate_gate_mapping()
    generate_sat_pipeline()
    print("All Tseytin figures generated successfully.")

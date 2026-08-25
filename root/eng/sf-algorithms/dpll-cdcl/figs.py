# -*- coding: utf-8 -*-
import os
import sys

# Add scripts/ directory from workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

IMG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
os.makedirs(IMG_DIR, exist_ok=True)

def generate_dpll_search_tree():
    path = os.path.join(IMG_DIR, 'dpll-search-tree.svg')
    w, h = 680, 400
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    frags.append(text(w / 2, 35, "Дерево пошуку алгоритму DPLL з хронологічним вертанням", size=15, bold=True))
    frags.append(text(w / 2, 55, "Послідовність прийняття рішень, BCP-поширення та виявлення конфліктів", size=12, color=MUTED))
    
    # Root
    b_root, _, _ = textbox(340, 90, "Формула F\nРівень 0", size=12, fill="#f4f6f8", stroke=LINE)
    frags.append(b_root)
    
    # Decision x₁=1
    b_x1_t, _, _ = textbox(200, 170, "Прийняття x₁ = 1\nРівень 1", size=12, fill="#eaf0fd", stroke=FIELD, sw=1.5)
    frags.append(b_x1_t)
    
    # BCP after x₁=1 -> x₂=0
    b_bcp1, _, _ = textbox(200, 240, "BCP: x₂ = 0\n(одиничний диз'юнкт)", size=11, fill="#fef9c3", stroke="#ca8a04")
    frags.append(b_bcp1)
    
    # Decision x₃=1 -> Conflict!
    b_conf1, _, _ = textbox(110, 320, "x₃ = 1 @ 2\nКонфлікт (⊥)\n[¬x₁ ∨ x₂ ∨ ¬x₃]", size=11, fill="#fde8e8", stroke=NEG, sw=1.5)
    frags.append(b_conf1)
    
    # Backtrack x₃=0 -> Conflict!
    b_conf2, _, _ = textbox(270, 320, "x₃ = 0 @ 2\nКонфлікт (⊥)\n[x₁ ∨ ¬x₂ ∨ x₃]", size=11, fill="#fde8e8", stroke=NEG, sw=1.5)
    frags.append(b_conf2)
    
    # Decision x₁=0 (Backtrack to level 1)
    b_x1_f, _, _ = textbox(480, 170, "Вертання x₁ = 0\nРівень 1", size=12, fill="#eaf0fd", stroke=POS, sw=1.5)
    frags.append(b_x1_f)
    
    # BCP after x₁=0 -> x₄=1, x₅=1 -> SAT!
    b_sat, _, _ = textbox(480, 280, "BCP: x₄ = 1, x₅ = 1\nРозв'язок знайдено!\n(SAT)", size=12, fill="#def7ec", stroke=POS, sw=2)
    frags.append(b_sat)
    
    # Connectors
    frags.append(arrow(300, 105, 220, 150, color=LINE, sw=1.5))
    frags.append(text(240, 120, "x₁ = 1", size=11, color=FIELD, bold=True))
    
    frags.append(arrow(380, 105, 460, 150, color=LINE, sw=1.5))
    frags.append(text(440, 120, "x₁ = 0", size=11, color=POS, bold=True))
    
    frags.append(arrow(200, 190, 200, 220, color=LINE, sw=1.5))
    frags.append(arrow(200, 260, 130, 300, color=LINE, sw=1.5))
    frags.append(text(145, 275, "x₃ = 1", size=10, color=NEG))
    
    frags.append(arrow(200, 260, 270, 300, color=LINE, sw=1.5))
    frags.append(text(250, 275, "x₃ = 0", size=10, color=NEG))
    
    frags.append(arrow(480, 190, 480, 260, color=LINE, sw=1.5))
    
    # Chronological Backtrack curve
    frags.append('<path d="M 270 340 C 270 370, 440 370, 460 200" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="4,4"/>' % NEG)
    frags.append(text(370, 375, "Хронологічне вертання (Backtrack до рів. 1)", size=11, color=NEG, bold=True))

    render(path, w, h, *frags)

def generate_cdcl_implication_graph():
    path = os.path.join(IMG_DIR, 'cdcl-implication-graph.svg')
    w, h = 740, 430
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    frags.append(text(w / 2, 35, "Граф імплікацій CDCL, 1UIP та виведення конфліктного диз'юнкта", size=15, bold=True))
    frags.append(text(w / 2, 55, "Побудова зрізу конфлікту та формування вивченого диз'юнкта", size=12, color=MUTED))
    
    # Decision literals from earlier levels
    b_x1, _, _ = textbox(70, 120, "x₁ = 1\n(Рівень 1)", size=11, fill="#eaf0fd", stroke=FIELD)
    b_x2, _, _ = textbox(70, 260, "x₂ = 1\n(Рівень 2)", size=11, fill="#eaf0fd", stroke=FIELD)
    
    # Decision literal at current level (level 3)
    b_x3, _, _ = textbox(210, 190, "x₃ = 1 @ 3\n(Decision)", size=11, fill="#fef9c3", stroke="#ca8a04", sw=2)
    
    # Intermediate BCP nodes at level 3
    b_x4, _, _ = textbox(360, 140, "x₄ = 1 @ 3\n(C₁: ¬x₁ ∨ ¬x₃ ∨ x₄)", size=11, fill="#ffffff", stroke=LINE)
    b_x5, _, _ = textbox(360, 240, "x₅ = 1 @ 3\n(C₂: ¬x₂ ∨ ¬x₃ ∨ x₅)", size=11, fill="#ffffff", stroke=LINE)
    
    # 1UIP node (x₆)
    b_x6, _, _ = textbox(490, 190, "1UIP: x₆ = 1 @ 3\n(C₃: ¬x₄ ∨ ¬x₅ ∨ x₆)", size=11, fill="#def7ec", stroke=POS, sw=2)
    
    # Conflict literals
    b_x7, _, _ = textbox(600, 120, "x₇ = 1 @ 3\n(C₄)", size=10, fill="#ffffff", stroke=LINE)
    b_not_x7, _, _ = textbox(600, 260, "¬x₇ = 1 @ 3\n(C₅)", size=10, fill="#ffffff", stroke=LINE)
    
    # Conflict Node
    b_conf, _, _ = textbox(680, 190, "Конфлікт\n(⊥)", size=12, fill="#fde8e8", stroke=NEG, sw=2)
    
    frags.extend([b_x1, b_x2, b_x3, b_x4, b_x5, b_x6, b_x7, b_not_x7, b_conf])
    
    # Implication edges
    frags.append(arrow(115, 120, 310, 140, color=LINE, sw=1.5))
    frags.append(arrow(260, 190, 310, 150, color=LINE, sw=1.5))
    
    frags.append(arrow(115, 260, 310, 240, color=LINE, sw=1.5))
    frags.append(arrow(260, 190, 310, 230, color=LINE, sw=1.5))
    
    frags.append(arrow(410, 140, 440, 180, color=LINE, sw=1.5))
    frags.append(arrow(410, 240, 440, 200, color=LINE, sw=1.5))
    
    frags.append(arrow(540, 190, 560, 130, color=LINE, sw=1.5))
    frags.append(arrow(540, 190, 560, 250, color=LINE, sw=1.5))
    
    frags.append(arrow(635, 130, 650, 175, color=NEG, sw=1.5))
    frags.append(arrow(635, 250, 650, 205, color=NEG, sw=1.5))
    
    # 1UIP Conflict Cut Line
    frags.append('<line x1="440" y1="80" x2="440" y2="330" stroke="%s" stroke-width="2.5" stroke-dasharray="6,4"/>' % NEG)
    frags.append(text(440, 350, "Зріз конфлікту (1UIP Cut)", size=12, color=NEG, bold=True))
    frags.append(text(440, 370, "Вивчений диз'юнкт C_learn = ¬x₁ ∨ ¬x₂ ∨ ¬x₆", size=12, color=FIELD, bold=True))
    frags.append(text(440, 395, "Нехронологічний стрибок на Рівень 2 (max(1, 2))", size=11, color=MUTED))

    render(path, w, h, *frags)

def generate_watched_literals():
    path = os.path.join(IMG_DIR, 'watched-literals-scheme.svg')
    w, h = 660, 350
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    frags.append(text(w / 2, 35, "Схема двоспостережуваних літералів (2-Watched Literals)", size=15, bold=True))
    frags.append(text(w / 2, 55, "Структура диз'юнкта C = (x₁ ∨ x₂ ∨ ¬x₃ ∨ x₄) та динаміка вказівників w₁, w₂", size=12, color=MUTED))
    
    # Clause Box Array
    lits = ["x₁", "x₂", "¬x₃", "x₄"]
    states = ["Невизначено", "Хибно (x₂=0)", "Невизначено", "Невизначено"]
    colors = ["#eaf0fd", "#fde8e8", "#eaf0fd", "#eaf0fd"]
    
    for i, (lit, st, clr) in enumerate(zip(lits, states, colors)):
        bx = 100 + i * 120
        b_cell, _, _ = textbox(bx, 140, f"Літерал {i}\n{lit}\n[{st}]", size=12, fill=clr, stroke=LINE, sw=1.5)
        frags.append(b_cell)
        
    # Pointers w1 and w2 before update
    frags.append(arrow(100, 240, 100, 185, color=FIELD, sw=2))
    frags.append(text(100, 260, "w₁ (Спостережуваний 1)", size=11, color=FIELD, bold=True))
    
    # Initial w2 pointed to index 1 (x₂), which became FALSE!
    frags.append('<line x1="220" y1="240" x2="220" y2="185" stroke="%s" stroke-width="2" stroke-dasharray="4,4"/>' % NEG)
    frags.append(text(220, 260, "Старий w₂ (x₂ стало 0!)", size=11, color=NEG))
    
    # Curved arrow moving w2 from index 1 to index 3 (x₄)
    frags.append('<path d="M 220 275 C 220 320, 460 320, 460 185" fill="none" stroke="%s" stroke-width="2.5"/>' % POS)
    frags.append(arrow(455, 195, 460, 185, color=POS, sw=2.5))
    frags.append(text(340, 315, "Пошук нового не-хибного літерала → новий w₂ на x₄", size=11, color=POS, bold=True))

    render(path, w, h, *frags)

def generate_cdcl_pipeline():
    path = os.path.join(IMG_DIR, 'cdcl-solver-pipeline.svg')
    w, h = 760, 430
    
    frags = []
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e5e7eb", sw=1))
    
    frags.append(text(w / 2, 30, "Конвеєр виконання сучасного CDCL SAT-солвера", size=15, bold=True))
    frags.append(text(w / 2, 50, "Цикл прийняття рішень, BCP, аналізу конфліктів та перезапусків", size=12, color=MUTED))
    
    # Nodes layout:
    # Row 1 (y=120): Start (80) -> BCP (230) -> Conflict? (390) -> SAT Check (540) -> SAT (680)
    # Row 2 (y=230): UNSAT (80) <- Level 0? (230) <- Analysis (390)
    # Row 3 (y=340): Restart (230) <- Learn & Backjump (390) <- Decide (540)
    
    b_start, _, _ = textbox(80, 120, "Вхід: КНФ F", size=11, fill="#f4f6f8", stroke=LINE)
    b_bcp, _, _ = textbox(230, 120, "Поширення (BCP)\n[2WL Scheme]", size=11, fill="#eaf0fd", stroke=FIELD, sw=1.5)
    b_conf_chk, _, _ = textbox(390, 120, "Є конфлікт\n(порожній диз'юнкт)?", size=11, fill="#fff7ed", stroke="#c2410c")
    b_sat_chk, _, _ = textbox(540, 120, "Усі змінні\nпризначено?", size=11, fill="#fff7ed", stroke="#c2410c")
    b_sat, _, _ = textbox(680, 120, "Результат: SAT\n(Модель)", size=11, fill="#def7ec", stroke=POS, sw=2)
    
    b_anal, _, _ = textbox(390, 230, "Аналіз конфлікту\n[1UIP Cut]", size=11, fill="#fde8e8", stroke=NEG, sw=1.5)
    b_lvl0, _, _ = textbox(230, 230, "Рівень 0?", size=11, fill="#fff7ed", stroke="#c2410c")
    b_unsat, _, _ = textbox(80, 230, "Результат: UNSAT\n(Доведення)", size=11, fill="#fde8e8", stroke=NEG, sw=2)
    
    b_learn, _, _ = textbox(390, 340, "Вивчення диз'юнкта\nта Backjump", size=11, fill="#eaf0fd", stroke=FIELD)
    b_restart, _, _ = textbox(230, 340, "Оновлення VSIDS\nПерезапуск / Очищення", size=11, fill="#fef9c3", stroke="#ca8a04")
    b_decide, _, _ = textbox(540, 340, "Прийняття рішення\n[VSIDS + Phase Save]", size=11, fill="#eaf0fd", stroke=FIELD)
    
    frags.extend([b_start, b_bcp, b_conf_chk, b_sat_chk, b_sat, b_anal, b_lvl0, b_unsat, b_learn, b_restart, b_decide])
    
    # Arrows Row 1
    frags.append(arrow(125, 120, 175, 120, color=LINE, sw=1.5))
    frags.append(arrow(285, 120, 335, 120, color=LINE, sw=1.5))
    
    # Conflict check: No -> SAT Check
    frags.append(arrow(445, 120, 485, 120, color=POS, sw=1.5))
    frags.append(text(465, 110, "Ні", size=10, color=POS, bold=True))
    
    # SAT Check: Yes -> SAT
    frags.append(arrow(595, 120, 635, 120, color=POS, sw=1.5))
    frags.append(text(615, 110, "Так", size=10, color=POS, bold=True))
    
    # SAT Check: No -> Decide
    frags.append(arrow(540, 155, 540, 305, color=LINE, sw=1.5))
    frags.append(text(555, 230, "Ні", size=10, color=LINE))
    
    # Conflict check: Yes -> Analysis
    frags.append(arrow(390, 155, 390, 195, color=NEG, sw=1.5))
    frags.append(text(405, 175, "Так", size=10, color=NEG, bold=True))
    
    # Analysis -> Level 0 check
    frags.append(arrow(340, 230, 275, 230, color=LINE, sw=1.5))
    
    # Level 0 check: Yes -> UNSAT
    frags.append(arrow(185, 230, 135, 230, color=NEG, sw=1.5))
    frags.append(text(160, 220, "Так", size=10, color=NEG, bold=True))
    
    # Level 0 check: No -> Learn
    frags.append(arrow(390, 265, 390, 305, color=FIELD, sw=1.5))
    frags.append(text(405, 285, "Ні", size=10, color=FIELD))
    
    # Learn -> Restart
    frags.append(arrow(335, 340, 285, 340, color=FIELD, sw=1.5))
    
    # Restart -> BCP loop
    frags.append('<path d="M 230 305 L 230 160" fill="none" stroke="%s" stroke-width="1.5"/>' % FIELD)
    frags.append(arrow(230, 170, 230, 160, color=FIELD, sw=1.5))
    
    # Decide -> BCP loop
    frags.append('<path d="M 540 375 C 540 410, 230 410, 230 375" fill="none" stroke="%s" stroke-width="1.5"/>' % LINE)

    render(path, w, h, *frags)

if __name__ == '__main__':
    generate_dpll_search_tree()
    generate_cdcl_implication_graph()
    generate_watched_literals()
    generate_cdcl_pipeline()
    print("All DPLL/CDCL figures generated successfully.")

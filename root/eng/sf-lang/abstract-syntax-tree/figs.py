# -*- coding: utf-8 -*-
"""Фігури до статті «Абстрактне синтаксичне дерево (AST)».
Генерує SVG-діаграми для пояснення парсингу, CST проти AST, інфіксних операторів та конвеєра компілятора.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра
ACCENT_BLUE  = "#2457d6"
ACCENT_GREEN = FIELD
ACCENT_RED   = POS
FILL_CARD    = "#f8fafc"
STROKE_CARD  = "#cbd5e1"
FILL_AST     = "#e0f2fe"
STROKE_AST   = "#0284c7"
FILL_CST     = "#fef3c7"
STROKE_CST   = "#d97706"
FILL_OP      = "#fce7f3"
STROKE_OP    = "#db2777"


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 1 — Порівняння конкретного (CST) та абстрактного (AST) синтаксичного дерева
# ─────────────────────────────────────────────────────────────────────────────
def fig_cst_vs_ast():
    W, H = 860, 480
    p = []

    # Заголовок лівої частини — CST
    p.append(text(210, 40, "Конкретне дерево (CST / Parse Tree)", size=15, color=STROKE_CST, bold=True))
    p.append(text(210, 60, "Містить усю синтаксичну сировину: дужки, крапки, правила", size=12, color=MUTED))

    # CST вузли для виразу (a + b) * 3
    cst_nodes = [
        (210, 95, "Expr", FILL_CST, STROKE_CST),
        (110, 160, "Term", FILL_CST, STROKE_CST),
        (210, 160, "Op: '*'", FILL_OP, STROKE_OP),
        (320, 160, "Factor", FILL_CST, STROKE_CST),
        (35, 230, "'('", FILL, LINE),
        (110, 230, "Expr: a+b", FILL_CST, STROKE_CST),
        (185, 230, "')'", FILL, LINE),
        (320, 230, "Num: 3", FILL_AST, STROKE_AST),
        (50, 300, "Ident: a", FILL_AST, STROKE_AST),
        (110, 300, "Op: '+'", FILL_OP, STROKE_OP),
        (170, 300, "Ident: b", FILL_AST, STROKE_AST),
    ]

    # Ребра CST
    cst_edges = [
        (210, 95, 110, 160), (210, 95, 210, 160), (210, 95, 320, 160),
        (110, 160, 35, 230), (110, 160, 110, 230), (110, 160, 185, 230),
        (320, 160, 320, 230),
        (110, 230, 50, 300), (110, 230, 110, 300), (110, 230, 170, 300),
    ]

    for x1, y1, x2, y2 in cst_edges:
        p.append(line(x1, y1, x2, y2, color="#cbd5e1", sw=1.5))

    for x, y, lbl, f, s in cst_nodes:
        b, w_box, h_box = textbox(x, y, lbl, size=11.5, pad=4.5, fill=f, stroke=s, sw=1.4)
        p.append(b)

    # Розділювальна лінія
    p.append(line(430, 30, 430, 440, color="#cbd5e1", sw=1.5, dash="4,4"))

    # Заголовок правої частини — AST
    p.append(text(640, 40, "Абстрактне дерево (AST)", size=15, color=ACCENT_BLUE, bold=True))
    p.append(text(640, 60, "Лише суть: операції та операнди, без шуму", size=12, color=MUTED))

    # AST вузли для виразу (a + b) * 3
    ast_nodes = [
        (640, 110, "BinaryOp: '*'", FILL_OP, STROKE_OP),
        (560, 200, "BinaryOp: '+'", FILL_OP, STROKE_OP),
        (720, 200, "Literal: 3", FILL_AST, STROKE_AST),
        (510, 290, "Var: a", FILL_AST, STROKE_AST),
        (610, 290, "Var: b", FILL_AST, STROKE_AST),
    ]

    ast_edges = [
        (640, 110, 560, 200), (640, 110, 720, 200),
        (560, 200, 510, 290), (560, 200, 610, 290),
    ]

    for x1, y1, x2, y2 in ast_edges:
        p.append(line(x1, y1, x2, y2, color=ACCENT_BLUE, sw=2.0))

    for x, y, lbl, f, s in ast_nodes:
        b, w_box, h_box = textbox(x, y, lbl, size=13, pad=8, fill=f, stroke=s, sw=1.8, bold=True)
        p.append(b)

    # Пояснення знизу
    p.append(text(210, 370, "11 вузлів (з дужками та нетерміналами)", size=12, color=MUTED, bold=True))
    p.append(text(640, 370, "5 вузлів (чисте семантичне дерево)", size=12, color=ACCENT_BLUE, bold=True))

    render(os.path.join(OUT, "cst-vs-ast.svg"), W, H, *p,
           title="Порівняння конкретного (CST) та абстрактного (AST) синтаксичного дерева")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 2 — Пріоритет операторів у геометрії AST (2 + 3 * 4)
# ─────────────────────────────────────────────────────────────────────────────
def fig_ast_precedence():
    W, H = 820, 450
    p = []

    # Код виразу
    p.append(text(410, 35, "Вираз:  2 + 3 × 4", size=18, color=INK, bold=True))
    p.append(text(410, 58, "Множення має вищий пріоритет за додавання — воно занурюється глибше в дерево", size=13, color=MUTED))

    # Дерево для 2 + 3 * 4
    edges = [
        (340, 130, 220, 220),
        (340, 130, 460, 220),
        (460, 220, 390, 310),
        (460, 220, 530, 310),
    ]

    for x1, y1, x2, y2 in edges:
        p.append(line(x1, y1, x2, y2, color=LINE, sw=2.0))

    # Вузли
    nodes_data = [
        (340, 130, "BinaryOp: +", FILL_OP, STROKE_OP),
        (220, 220, "Literal: 2", FILL_AST, STROKE_AST),
        (460, 220, "BinaryOp: ×", FILL_OP, STROKE_OP),
        (390, 310, "Literal: 3", FILL_AST, STROKE_AST),
        (530, 310, "Literal: 4", FILL_AST, STROKE_AST),
    ]

    for x, y, lbl, f, s in nodes_data:
        b, w_box, h_box = textbox(x, y, lbl, size=13, pad=8, fill=f, stroke=s, sw=1.8, bold=True)
        p.append(b)

    # Панель обчислення (Post-order) праворуч
    panel_x, panel_y, panel_w, panel_h = 610, 120, 180, 230
    p.append(rect(panel_x, panel_y, panel_w, panel_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(text(panel_x + panel_w/2, panel_y + 25, "Порядок обчислення", size=13, color=INK, bold=True))
    p.append(text(panel_x + panel_w/2, panel_y + 45, "(Post-order traversal)", size=11, color=MUTED))

    p.append(text(panel_x + 15, panel_y + 80, "Крок 1:  3 × 4 = 12", size=12, color=ACCENT_RED, anchor="start", bold=True))
    p.append(text(panel_x + 15, panel_y + 105, "(піддерево «×» обчислюється першим)", size=10.5, color=MUTED, anchor="start"))

    p.append(text(panel_x + 15, panel_y + 145, "Крок 2:  2 + 12 = 14", size=12, color=ACCENT_GREEN, anchor="start", bold=True))
    p.append(text(panel_x + 15, panel_y + 170, "(корінь «+» чекає на результат)", size=10.5, color=MUTED, anchor="start"))

    # Підсвітка кроків на дереві
    p.append(text(575, 275, "① Спочатку", size=11, color=ACCENT_RED, bold=True))
    p.append(text(160, 160, "② Потім", size=11, color=ACCENT_GREEN, bold=True))

    render(os.path.join(OUT, "ast-precedence.svg"), W, H, *p,
           title="Пріоритет операторів у геометрії AST")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 3 — Обхід дерева за шаблоном Visitor (Відвідувач)
# ─────────────────────────────────────────────────────────────────────────────
def fig_visitor_pattern():
    W, H = 840, 440
    p = []

    # Заголовок
    p.append(text(420, 35, "Шаблон Visitor: Відокремлення структури дерева від алгоритмів", size=15, color=INK, bold=True))

    # Ліва частина — Вузли AST
    p.append(text(200, 75, "Структура даних AST (Вузли)", size=13, color=ACCENT_BLUE, bold=True))

    p.append(line(200, 120, 130, 200, color=LINE, sw=1.8))
    p.append(line(200, 120, 270, 200, color=LINE, sw=1.8))

    b1, _, _ = textbox(200, 120, "BinaryOpNode (+)", size=12, pad=7, fill=FILL_OP, stroke=STROKE_OP, bold=True)
    b2, _, _ = textbox(130, 200, "NumNode (5)", size=12, pad=7, fill=FILL_AST, stroke=STROKE_AST, bold=True)
    b3, _, _ = textbox(270, 200, "NumNode (10)", size=12, pad=7, fill=FILL_AST, stroke=STROKE_AST, bold=True)
    p.extend([b1, b2, b3])

    p.append(text(200, 260, "accept(visitor)", size=12, color=ACCENT_BLUE, italic=True))
    p.append(text(200, 280, "Кожен вузол викликає відповідний метод візитора", size=11, color=MUTED))

    # Права частина — Модульні Візитори
    p.append(text(620, 75, "Операції над AST (Візитори)", size=13, color=ACCENT_GREEN, bold=True))

    v1_box, _, _ = textbox(620, 130, "EvaluatorVisitor\nvisit_binary() → a + b\nvisit_num() → val", size=11, pad=8, fill="#eafaf0", stroke=FIELD, bold=True)
    v2_box, _, _ = textbox(620, 220, "CodeGeneratorVisitor (LLVM / JS)\nvisit_binary() → emit_add()\nvisit_num() → emit_const()", size=11, pad=8, fill="#f4f6f8", stroke=LINE, bold=True)
    v3_box, _, _ = textbox(620, 310, "LinterVisitor (Static Analysis)\nvisit_binary() → check_overflow()\nvisit_num() → check_range()", size=11, pad=8, fill="#fdf2f0", stroke=POS, bold=True)

    p.extend([v1_box, v2_box, v3_box])

    # Стрілки Double Dispatch між вузлом і візитором
    p.append(arrow(290, 120, 480, 120, color=ACCENT_BLUE, sw=2.0))
    p.append(text(385, 105, "1. node.accept(v)", size=11, color=ACCENT_BLUE, bold=True))

    p.append(arrow(480, 140, 290, 140, color=ACCENT_GREEN, sw=2.0))
    p.append(text(385, 155, "2. v.visit_binary(this)", size=11, color=ACCENT_GREEN, bold=True))

    render(os.path.join(OUT, "visitor-pattern.svg"), W, H, *p,
           title="Шаблон Visitor для обходу та обробки AST")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 4 — Конвеєр компіляції через AST (Compiler Pipeline)
# ─────────────────────────────────────────────────────────────────────────────
def fig_compiler_pipeline():
    W, H = 880, 400
    p = []

    p.append(text(440, 35, "Роль AST у конвеєрі обробки вихідного коду", size=15, color=INK, bold=True))

    stages = [
        (80, 140, "Текст коду\n\"x = 5 + 3;\"", FILL, LINE),
        (230, 140, "Лексер\n(Lexer)", "#fef3c7", "#d97706"),
        (380, 140, "Парсер\n(Parser)", "#e0f2fe", "#0284c7"),
        (540, 140, "AST\n(Дерево)", "#fce7f3", "#db2777"),
        (690, 140, "Оптимізатор /\nЛінтер", "#eafaf0", FIELD),
        (820, 140, "Генератор\nкоду", FILL, LINE),
    ]

    for i in range(len(stages) - 1):
        x1, y1 = stages[i][0] + 45, stages[i][1]
        x2, y2 = stages[i+1][0] - 45, stages[i+1][1]
        p.append(arrow(x1, y1, x2, y2, color=LINE, sw=2.0))

    for x, y, lbl, f, s in stages:
        b, _, _ = textbox(x, y, lbl, size=11, pad=8, fill=f, stroke=s, sw=1.6, bold=True)
        p.append(b)

    # Проміжні дані під стрілками
    p.append(text(155, 190, "Потік символів", size=10, color=MUTED))
    p.append(text(305, 190, "Токени (Tokens)", size=10, color=MUTED))
    p.append(text(460, 190, "Конкретне дерево", size=10, color=MUTED))
    p.append(text(615, 190, "Оптимізоване AST", size=10, color=MUTED))
    p.append(text(755, 190, "Байткод / IR", size=10, color=MUTED))

    # Рамка центральної ролі AST
    p.append(rect(340, 240, 360, 110, fill="#f8fafc", stroke=ACCENT_BLUE, sw=1.5, rx=8))
    p.append(text(520, 265, "Абстрактне синтаксичне дерево (AST)", size=13, color=ACCENT_BLUE, bold=True))
    p.append(text(520, 290, "• Єдине джерело правди про семантику програми", size=11.5, color=INK))
    p.append(text(520, 310, "• На ньому працюють Babel, Clang AST, ESLint, IDE", size=11.5, color=INK))
    p.append(text(520, 330, "• Ізолює синтаксис мови від цільової платформи", size=11.5, color=INK))

    render(os.path.join(OUT, "compiler-pipeline.svg"), W, H, *p,
           title="Роль AST у конвеєрі компілятора")


if __name__ == "__main__":
    fig_cst_vs_ast()
    fig_ast_precedence()
    fig_visitor_pattern()
    fig_compiler_pipeline()
    print("AST figures generated successfully in", OUT)

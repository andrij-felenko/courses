# -*- coding: utf-8 -*-
"""Фігури до статті «Сортувальна станція Дейкстри».
Генерує SVG-діаграми для залізничної аналогії, простеження стека, асоціативності,
стекового обчислення RPN та прямої побудови синтаксичного дерева AST.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра
ACCENT_BLUE   = "#2457d6"
ACCENT_GREEN  = FIELD
ACCENT_RED    = POS
FILL_CARD     = "#f8fafc"
STROKE_CARD   = "#cbd5e1"
FILL_NUM      = "#e0f2fe"
STROKE_NUM    = "#0284c7"
FILL_OP       = "#fef3c7"
STROKE_OP     = "#d97706"
FILL_FUNC     = "#fce7f3"
STROKE_FUNC   = "#db2777"
FILL_PAREN    = "#f1f5f9"
STROKE_PAREN  = "#64748b"


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 1 — Залізнична сортувальна станція Дейкстри
# ─────────────────────────────────────────────────────────────────────────────
def fig_shunting_railway_analogy():
    W, H = 880, 440
    p = []

    # Заголовок
    p.append(text(440, 30, "Залізнична аналогія сортувальної станції (Shunting Yard)", size=16, color=INK, bold=True))

    # Схема колій
    # Вхідна колія (ліворуч)
    p.append(line(50, 180, 340, 180, color=LINE, sw=3.5))
    p.append(line(50, 200, 340, 200, color=LINE, sw=3.5))
    # Шпали вхідної колії
    for x in range(60, 330, 20):
        p.append(line(x, 172, x, 208, color="#94a3b8", sw=2.0))

    # Вихідна колія (праворуч)
    p.append(line(540, 180, 830, 180, color=LINE, sw=3.5))
    p.append(line(540, 200, 830, 200, color=LINE, sw=3.5))
    # Шпали вихідної колії
    for x in range(550, 830, 20):
        p.append(line(x, 172, x, 208, color="#94a3b8", sw=2.0))

    # Центральне з'єднання (стрілочний перевід)
    p.append(line(340, 180, 540, 180, color=LINE, sw=3.5))
    p.append(line(340, 200, 540, 200, color=LINE, sw=3.5))
    for x in range(350, 540, 20):
        p.append(line(x, 172, x, 208, color="#94a3b8", sw=2.0))

    # Тупикова маневрова колія (Стек операторів LIFO, веде вниз)
    p.append(line(430, 200, 430, 380, color=LINE, sw=3.5))
    p.append(line(450, 200, 450, 380, color=LINE, sw=3.5))
    p.append(line(420, 380, 460, 380, color=POS, sw=5.0)) # тупиковий упор
    for y in range(215, 375, 18):
        p.append(line(422, y, 458, y, color="#94a3b8", sw=2.0))

    # Підписи колій
    b1, _, _ = textbox(180, 130, "Вхідний потік (Інфікс)\n\"3 + 4 * 2\"", size=12, pad=6, fill=FILL_CARD, stroke=STROKE_CARD, bold=True)
    p.append(b1)
    p.append(arrow(260, 155, 310, 175, color=ACCENT_BLUE, sw=2.0))

    b2, _, _ = textbox(700, 130, "Вихідний потік (RPN)\n\"3 4 2 * +\"", size=12, pad=6, fill=FILL_CARD, stroke=STROKE_CARD, bold=True)
    p.append(b2)
    p.append(arrow(570, 175, 620, 155, color=FIELD, sw=2.0))

    b3, _, _ = textbox(440, 410, "Маневровий тупик (Стек операторів LIFO)", size=12, pad=6, fill="#fef2f2", stroke=POS, bold=True)
    p.append(b3)

    # Вагони-токени на коліях
    # На вході
    b_in1, _, _ = textbox(110, 190, "3", size=13, pad=7, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)
    b_in2, _, _ = textbox(160, 190, "+", size=13, pad=7, fill=FILL_OP, stroke=STROKE_OP, bold=True)
    b_in3, _, _ = textbox(210, 190, "4", size=13, pad=7, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)
    b_in4, _, _ = textbox(260, 190, "*", size=13, pad=7, fill=FILL_OP, stroke=STROKE_OP, bold=True)
    b_in5, _, _ = textbox(310, 190, "2", size=13, pad=7, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)
    p.extend([b_in1, b_in2, b_in3, b_in4, b_in5])

    # У стеку (тупику)
    b_st1, _, _ = textbox(440, 340, "+", size=14, pad=7, fill=FILL_OP, stroke=STROKE_OP, bold=True)
    b_st2, _, _ = textbox(440, 280, "*", size=14, pad=7, fill=FILL_OP, stroke=STROKE_OP, bold=True)
    p.extend([b_st1, b_st2])
    p.append(text(505, 340, "(дно стека)", size=10, color=MUTED, anchor="start"))
    p.append(text(505, 280, "(вершина)", size=10, color=MUTED, anchor="start"))

    # На виході
    b_out1, _, _ = textbox(630, 190, "3", size=13, pad=7, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)
    b_out2, _, _ = textbox(680, 190, "4", size=13, pad=7, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)
    b_out3, _, _ = textbox(730, 190, "2", size=13, pad=7, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)
    p.extend([b_out1, b_out2, b_out3])

    # Пояснювальні стрілки руху
    p.append(arrow(335, 175, 415, 260, color=STROKE_OP, sw=2.0))
    p.append(text(355, 230, "Оператор -> в стек", size=10, color=STROKE_OP, bold=True))

    p.append(arrow(465, 260, 545, 175, color=STROKE_OP, sw=2.0))
    p.append(text(535, 230, "Виштовхування -> у вихід", size=10, color=STROKE_OP, bold=True))

    p.append(arrow(340, 165, 540, 165, color=STROKE_NUM, sw=2.5))
    p.append(text(440, 150, "Числа прямують транзитом прямо у вихід", size=11, color=STROKE_NUM, bold=True))

    render(os.path.join(OUT, "shunting-railway-analogy.svg"), W, H, *p,
           title="Залізнична сортувальна станція Дейкстри")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 2 — Покрокове простеження стану стека та черги
# ─────────────────────────────────────────────────────────────────────────────
def fig_operator_stack_trace():
    W, H = 920, 480
    p = []

    p.append(text(460, 25, "Покроковий стан алгоритму для виразу: ( 3 + 4 ) * 2 ^ 3", size=15, color=INK, bold=True))

    # Стовпці таблиці
    headers = [
        (60, "Крок"),
        (130, "Токен"),
        (230, "Дія алгоритму"),
        (470, "Стек операторів (вершина праворуч)"),
        (750, "Вихідний потік (RPN)"),
    ]
    p.append(rect(20, 45, 880, 30, fill="#e2e8f0", stroke="#94a3b8", sw=1.0, rx=4))
    for x, h in headers:
        p.append(text(x, 65, h, size=11, color=INK, bold=True))

    steps = [
        ("1", "(", "Відкриваюча дужка -> на стек", "(", "", FILL),
        ("2", "3", "Число -> у вихід", "(", "3", FILL_CARD),
        ("3", "+", "Оператор '+' -> на стек", "(  +", "3", FILL),
        ("4", "4", "Число -> у вихід", "(  +", "3  4", FILL_CARD),
        ("5", ")", "Закриваюча дужка -> виштовхнути '+' до '('", "порожньо", "3  4  +", "#fef3c7"),
        ("6", "*", "Оператор '*' -> на стек", "*", "3  4  +", FILL),
        ("7", "2", "Число -> у вихід", "*", "3  4  +  2", FILL_CARD),
        ("8", "^", "Оператор '^' (пріор. 4 > 3) -> на стек", "*  ^", "3  4  +  2", FILL),
        ("9", "3", "Число -> у вихід", "*  ^", "3  4  +  2  3", FILL_CARD),
        ("10", "Кінець", "Виштовхнути всі залишки зі стека", "порожньо", "3  4  +  2  3  ^  *", "#dcfce7"),
    ]

    y = 80
    row_h = 36
    for s_num, tok, act, st, out, bg in steps:
        p.append(rect(20, y, 880, row_h, fill=bg, stroke="#e2e8f0", sw=1.0, rx=2))
        p.append(text(60, y + 22, s_num, size=11, color=INK, bold=True))

        # Бейдж токена
        col = STROKE_OP if tok in ["+", "*", "^"] else (STROKE_PAREN if tok in ["(", ")"] else (FIELD if tok == "Кінець" else STROKE_NUM))
        f_col = FILL_OP if tok in ["+", "*", "^"] else (FILL_PAREN if tok in ["(", ")"] else ("#e0f2fe" if tok not in ["Кінець"] else "#dcfce7"))
        b_tok, _, _ = textbox(130, y + 18, tok, size=11, pad=4, fill=f_col, stroke=col, bold=True)
        p.append(b_tok)

        p.append(text(230, y + 22, act, size=10.5, color=INK, anchor="middle"))

        # Стек
        st_box, _, _ = textbox(470, y + 18, st, size=11, pad=4, fill=FILL, stroke=LINE, min_w=120)
        p.append(st_box)

        # Вихід RPN
        out_box, _, _ = textbox(750, y + 18, out if out else "(порожньо)", size=11, pad=4, fill="#f8fafc", stroke=FIELD if s_num == "10" else "#94a3b8", min_w=200, bold=(s_num == "10"))
        p.append(out_box)

        y += row_h + 3

    render(os.path.join(OUT, "operator-stack-trace.svg"), W, H, *p,
           title="Покроковий слід алгоритму сортувальної станції")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 3 — Пріоритет та асоціативність операторів
# ─────────────────────────────────────────────────────────────────────────────
def fig_associativity_precedence():
    W, H = 880, 420
    p = []

    p.append(text(440, 28, "Вплив асоціативності на обробку операторів однакового пріоритету", size=15, color=INK, bold=True))

    # Ліва асоціативність
    p.append(rect(30, 55, 390, 345, fill=FILL_CARD, stroke=STROKE_CARD, sw=1.5, rx=8))
    p.append(text(225, 80, "Ліва асоціативність: a - b - c", size=13, color=ACCENT_BLUE, bold=True))
    p.append(text(225, 102, "Групування зліва направо: ( ( a - b ) - c )", size=11, color=MUTED))

    # Пояснення правила
    b_left_rule, _, _ = textbox(225, 140, "Умова виштовхування зі стека:\nprec(top) >= prec(incoming)\nОператор того ж пріоритету ВИШТОВХУЄТЬСЯ", size=10.5, pad=6, fill="#eff6ff", stroke=ACCENT_BLUE)
    p.append(b_left_rule)

    # Дерево для лівої асоціативності
    # Корінь '-' (другий)
    b_l1, _, _ = textbox(225, 210, "Op: '-' (2)", size=11, pad=5, fill=FILL_OP, stroke=STROKE_OP, bold=True)
    b_l2, _, _ = textbox(135, 280, "Op: '-' (1)", size=11, pad=5, fill=FILL_OP, stroke=STROKE_OP, bold=True)
    b_l3, _, _ = textbox(315, 280, "Var: c", size=11, pad=5, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)
    b_l4, _, _ = textbox(90, 350, "Var: a", size=11, pad=5, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)
    b_l5, _, _ = textbox(180, 350, "Var: b", size=11, pad=5, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)

    p.append(line(225, 225, 135, 265, color=LINE, sw=1.5))
    p.append(line(225, 225, 315, 265, color=LINE, sw=1.5))
    p.append(line(135, 295, 90, 335, color=LINE, sw=1.5))
    p.append(line(135, 295, 180, 335, color=LINE, sw=1.5))
    p.extend([b_l1, b_l2, b_l3, b_l4, b_l5])


    # Права асоціативність
    p.append(rect(460, 55, 390, 345, fill=FILL_CARD, stroke=STROKE_CARD, sw=1.5, rx=8))
    p.append(text(655, 80, "Права асоціативність: a ^ b ^ c", size=13, color=POS, bold=True))
    p.append(text(655, 102, "Групування справа наліво: ( a ^ ( b ^ c ) )", size=11, color=MUTED))

    # Пояснення правила
    b_right_rule, _, _ = textbox(655, 140, "Умова виштовхування зі стека:\nprec(top) > prec(incoming)\nОператор того ж пріоритету ЛИШАЄТЬСЯ на стеку", size=10.5, pad=6, fill="#fef2f2", stroke=POS)
    p.append(b_right_rule)

    # Дерево для правої асоціативності
    # Корінь '^' (перший)
    b_r1, _, _ = textbox(655, 210, "Op: '^' (1)", size=11, pad=5, fill=FILL_OP, stroke=STROKE_OP, bold=True)
    b_r2, _, _ = textbox(565, 280, "Var: a", size=11, pad=5, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)
    b_r3, _, _ = textbox(745, 280, "Op: '^' (2)", size=11, pad=5, fill=FILL_OP, stroke=STROKE_OP, bold=True)
    b_r4, _, _ = textbox(700, 350, "Var: b", size=11, pad=5, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)
    b_r5, _, _ = textbox(790, 350, "Var: c", size=11, pad=5, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)

    p.append(line(655, 225, 565, 265, color=LINE, sw=1.5))
    p.append(line(655, 225, 745, 265, color=LINE, sw=1.5))
    p.append(line(745, 295, 700, 335, color=LINE, sw=1.5))
    p.append(line(745, 295, 790, 335, color=LINE, sw=1.5))
    p.extend([b_r1, b_r2, b_r3, b_r4, b_r5])

    render(os.path.join(OUT, "associativity-precedence.svg"), W, H, *p,
           title="Асоціативність та пріоритети операторів")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 4 — Обчислення виразу в RPN на стеку операндів
# ─────────────────────────────────────────────────────────────────────────────
def fig_rpn_stack_evaluation():
    W, H = 880, 380
    p = []

    p.append(text(440, 25, "Стек-орієнтоване обчислення виразу RPN: \"5  3  4  *  +\"", size=15, color=INK, bold=True))

    stages = [
        ("Токени: 5, 3, 4\nКладемо числа", ["4", "3", "5"], "Стек росте", FILL_NUM, STROKE_NUM),
        ("Токен: '*'\nВиштовхуємо 4 і 3", ["12", "5"], "3 * 4 = 12", FILL_OP, STROKE_OP),
        ("Токен: '+'\nВиштовхуємо 12 і 5", ["17"], "5 + 12 = 17", FILL_OP, STROKE_OP),
        ("Кінець виразу\nФінальний результат", ["17"], "Результат = 17", "#dcfce7", FIELD),
    ]

    x_step = 210
    start_x = 110
    for idx, (title, stack_vals, desc, f_col, s_col) in enumerate(stages):
        cx = start_x + idx * x_step

        # Картка етапу
        p.append(rect(cx - 95, 50, 190, 310, fill=FILL_CARD, stroke=STROKE_CARD, sw=1.2, rx=6))
        b_t, _, _ = textbox(cx, 85, title, size=11, pad=4, fill=FILL, stroke="#94a3b8", bold=True)
        p.append(b_t)

        # Стакан стека
        p.append(line(cx - 45, 140, cx - 45, 270, color=LINE, sw=2.0))
        p.append(line(cx + 45, 140, cx + 45, 270, color=LINE, sw=2.0))
        p.append(line(cx - 45, 270, cx + 45, 270, color=LINE, sw=2.5))

        # Елементи у стакані (знизу догори)
        y_val = 245
        for v in reversed(stack_vals):
            b_v, _, _ = textbox(cx, y_val, v, size=13, pad=4, fill=f_col, stroke=s_col, min_w=70, bold=True)
            p.append(b_v)
            y_val -= 36

        # Опис дії внизу
        b_d, _, _ = textbox(cx, 320, desc, size=11.5, pad=5, fill="#f8fafc", stroke=s_col, bold=True)
        p.append(b_d)

        # Стрілка переходу
        if idx < len(stages) - 1:
            p.append(arrow(cx + 98, 190, cx + 112, 190, color=ACCENT_BLUE, sw=2.0))

    render(os.path.join(OUT, "rpn-stack-evaluation.svg"), W, H, *p,
           title="Обчислення постфіксного виразу на стеку")


# ─────────────────────────────────────────────────────────────────────────────
# Фіг. 5 — Пряма побудова дерева AST під час сортувальної станції
# ─────────────────────────────────────────────────────────────────────────────
def fig_expression_tree_ast():
    W, H = 940, 420
    p = []

    p.append(text(470, 25, "Пряма побудова дерева виразу (AST) під час Shunting-Yard", size=15, color=INK, bold=True))

    # Ліва частина: Стек вузлів AST
    p.append(rect(30, 50, 380, 350, fill=FILL_CARD, stroke=STROKE_CARD, sw=1.5, rx=8))
    p.append(text(220, 75, "Стек покажчиків на вузли (Node Stack)", size=13, color=ACCENT_BLUE, bold=True))
    p.append(text(220, 95, "Числа створюють листки, оператори зв'язують вузли", size=10.5, color=MUTED))

    # Схема стакану операндів
    p.append(line(120, 130, 120, 310, color=LINE, sw=2.0))
    p.append(line(320, 130, 320, 310, color=LINE, sw=2.0))
    p.append(line(120, 310, 320, 310, color=LINE, sw=3.0))

    # Вузли в стеку
    b_st_node1, _, _ = textbox(220, 275, "Node( 5 )", size=12, pad=6, fill=FILL_NUM, stroke=STROKE_NUM, min_w=160, bold=True)
    b_st_node2, _, _ = textbox(220, 215, "Node( * ) -> [ 3, 4 ]", size=12, pad=6, fill=FILL_OP, stroke=STROKE_OP, min_w=160, bold=True)
    p.extend([b_st_node1, b_st_node2])

    p.append(text(220, 345, "Коли оператор '+' виштовхується:", size=11, color=INK, bold=True))
    p.append(text(220, 365, "Right = pop(), Left = pop() -> новий Node(+)", size=10.5, color=MUTED))

    # Центральна стрілка перетворення
    p.append(arrow(415, 225, 465, 225, color=FIELD, sw=2.5))
    p.append(text(440, 210, "Згортання", size=11, color=FIELD, bold=True))

    # Права частина: Зібране дерево виразу
    p.append(rect(470, 50, 440, 350, fill=FILL_CARD, stroke=STROKE_CARD, sw=1.5, rx=8))
    p.append(text(690, 75, "Готове дерево виразу (AST)", size=13, color=FIELD, bold=True))
    p.append(text(690, 95, "Корінь на вершині стека вузлів", size=10.5, color=MUTED))

    # Вузли дерева
    b_root, _, _ = textbox(690, 140, "OpNode( + )", size=12, pad=6, fill=FILL_OP, stroke=STROKE_OP, bold=True)
    b_left, _, _ = textbox(570, 230, "NumNode( 5 )", size=11, pad=5, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)
    b_mul, _, _  = textbox(810, 230, "OpNode( * )", size=11, pad=5, fill=FILL_OP, stroke=STROKE_OP, bold=True)
    b_m1, _, _   = textbox(740, 320, "NumNode( 3 )", size=10.5, pad=4, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)
    b_m2, _, _   = textbox(860, 320, "NumNode( 4 )", size=10.5, pad=4, fill=FILL_NUM, stroke=STROKE_NUM, bold=True)

    # Гілки дерева
    p.append(line(690, 160, 570, 210, color=LINE, sw=1.8))
    p.append(line(690, 160, 810, 210, color=LINE, sw=1.8))
    p.append(line(810, 250, 740, 300, color=LINE, sw=1.8))
    p.append(line(810, 250, 860, 300, color=LINE, sw=1.8))

    p.extend([b_root, b_left, b_mul, b_m1, b_m2])

    render(os.path.join(OUT, "expression-tree-ast.svg"), W, H, *p,
           title="Побудова дерева виразу під час сортувальної станції")


if __name__ == "__main__":
    fig_shunting_railway_analogy()
    fig_operator_stack_trace()
    fig_associativity_precedence()
    fig_rpn_stack_evaluation()
    fig_expression_tree_ast()
    print("All shunting-yard figures generated successfully.")

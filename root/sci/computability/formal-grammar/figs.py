# -*- coding: utf-8 -*-
"""figs.py — генерація SVG-фігур для теми «Формальні граматики (CFG, BNF)».
svgkit імпортується зі scripts/ у корені репозиторію.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

# ── Палітра ──────────────────────────────────────────────────────────────────
NODE_NONTERM = "#2457d6"  # синій для нетерміналів
NODE_TERM    = "#27ae60"  # зелений для терміналів
ACCENT_RED   = "#c0392b"  # червоний для конфлікту/неоднозначності
BG_LIGHT_NT  = "#edf2fd"
BG_LIGHT_TR  = "#eafaf1"
BG_LIGHT_WRN = "#fdecea"


# ── Фігура 1: Дерево виводу арифметичного виразу x + y * z ───────────────────
def fig_parse_tree():
    W, H = 840, 520
    P = []

    # Заголовок і підзаголовок
    P.append(text(W / 2, 34, "Дерево виводу виразу x + y * z для однозначної граматики", size=16, color=INK, bold=True))
    P.append(text(W / 2, 58, "Граматика: E → E + T | T,  T → T * F | F,  F → id  (множення глибше в дереві → вищий пріоритет)", size=12, color=MUTED))

    # Координати вузлів дерева
    coords = {
        "root": (420, 105),
        "e1": (210, 185),
        "plus": (420, 185),
        "t1": (630, 185),
        "t_left": (210, 265),
        "t_mul_l": (530, 265),
        "star": (630, 265),
        "f_mul_r": (730, 265),
        "f_left": (210, 345),
        "f_mul_l": (530, 345),
        "leaf_x": (210, 425),
        "leaf_y": (530, 425),
        "leaf_z": (730, 425)
    }

    # Ребра дерева
    edges = [
        ("root", "e1"), ("root", "plus"), ("root", "t1"),
        ("e1", "t_left"), ("t_left", "f_left"), ("f_left", "leaf_x"),
        ("t1", "t_mul_l"), ("t1", "star"), ("t1", "f_mul_r"),
        ("t_mul_l", "f_mul_l"), ("f_mul_l", "leaf_y"),
        ("f_mul_r", "leaf_z")
    ]

    for p1, p2 in edges:
        x1, y1 = coords[p1]
        x2, y2 = coords[p2]
        P.append(line(x1, y1, x2, y2, color=LINE, sw=1.6))

    # Малювання нетермінальних вузлів (круги)
    nt_nodes = [
        ("root", "E"), ("e1", "E"), ("t1", "T"),
        ("t_left", "T"), ("f_left", "F"),
        ("t_mul_l", "T"), ("f_mul_l", "F"), ("f_mul_r", "F")
    ]

    for node_id, lbl in nt_nodes:
        cx, cy = coords[node_id]
        P.append(circle(cx, cy, 18, fill=BG_LIGHT_NT, stroke=NODE_NONTERM, sw=1.8))
        P.append(text(cx, cy + 5, lbl, size=14, color=NODE_NONTERM, bold=True))

    # Малювання термінальних вузлів (зелені)
    t_nodes = [
        ("plus", "+"), ("star", "*"),
        ("leaf_x", "x"), ("leaf_y", "y"), ("leaf_z", "z")
    ]

    for node_id, lbl in t_nodes:
        cx, cy = coords[node_id]
        P.append(rect(cx - 16, cy - 16, 32, 32, fill=BG_LIGHT_TR, stroke=NODE_TERM, sw=1.8, rx=6))
        P.append(text(cx, cy + 5, lbl, size=15, color=NODE_TERM, bold=True))

    # Нижня стрічка крони (yield)
    P.append(line(130, 480, 790, 480, color=MUTED, sw=1.2, dash="4,4"))
    P.append(text(W / 2, 502, "Крона дерева (результат зліва направо):  x  +  y  *  z", size=13, color=INK, bold=True))

    render("img/parse-tree-expression.svg", W, H, *P)


# ── Фігура 2: Проблема dangling else (дві інтерпретації) ──────────────────────
def fig_dangling_else():
    W, H = 940, 500
    P = []

    P.append(text(W / 2, 30, "Проблема неоднозначності: dangling else для вкладеного if-виразу", size=16, color=INK, bold=True))
    P.append(text(W / 2, 52, "Рядок:  if c1 then if c2 then s1 else s2  —  два принципово різні дерева виводу", size=12, color=MUTED))

    # Ліве дерево: else прив'язується до внутрішнього if (стандартна поведінка C/C++)
    P.append(text(240, 85, "Варіант А (прив'язка до ближчого if c2)", size=13, color=NODE_TERM, bold=True))
    P.append(fitbox(40, 100, 400, 350, "", fill="#f9fbfd", stroke=NODE_NONTERM, sw=1.2))

    coords_a = {
        "s0": (240, 130),
        "if1": (80, 190), "c1": (150, 190), "then1": (220, 190), "s_inner": (350, 190),
        "if2": (260, 270), "c2": (310, 270), "then2": (360, 270), "s1": (400, 270), "else2": (350, 350), "s2": (410, 350)
    }

    edges_a = [
        ("s0", "if1"), ("s0", "c1"), ("s0", "then1"), ("s0", "s_inner"),
        ("s_inner", "if2"), ("s_inner", "c2"), ("s_inner", "then2"), ("s_inner", "s1"),
        ("s_inner", "else2"), ("s_inner", "s2")
    ]

    for p1, p2 in edges_a:
        P.append(line(coords_a[p1][0], coords_a[p1][1], coords_a[p2][0], coords_a[p2][1], color=LINE, sw=1.4))

    # Нетермінали А
    for k, lbl in [("s0", "S"), ("s_inner", "S")]:
        cx, cy = coords_a[k]
        P.append(circle(cx, cy, 14, fill=BG_LIGHT_NT, stroke=NODE_NONTERM, sw=1.6))
        P.append(text(cx, cy + 4, lbl, size=12, color=NODE_NONTERM, bold=True))

    # Термінали А
    for k, lbl in [("if1", "if"), ("c1", "c1"), ("then1", "then"),
                   ("if2", "if"), ("c2", "c2"), ("then2", "then"), ("s1", "s1"),
                   ("else2", "else"), ("s2", "s2")]:
        cx, cy = coords_a[k]
        P.append(rect(cx - 15, cy - 12, 30, 24, fill=BG_LIGHT_TR, stroke=NODE_TERM, sw=1.4, rx=4))
        P.append(text(cx, cy + 4, lbl, size=11, color=NODE_TERM, bold=True))

    # Праве дерево: else прив'язується до зовнішнього if c1
    P.append(text(700, 85, "Варіант Б (прив'язка до дальшого if c1)", size=13, color=ACCENT_RED, bold=True))
    P.append(fitbox(500, 100, 400, 350, "", fill="#fdfbfb", stroke=ACCENT_RED, sw=1.2))

    coords_b = {
        "s0": (700, 130),
        "if1": (530, 190), "c1": (580, 190), "then1": (630, 190), "s_inner": (700, 200), "else1": (810, 190), "s2": (865, 190),
        "if2": (630, 280), "c2": (680, 280), "then2": (730, 280), "s1": (780, 280)
    }

    edges_b = [
        ("s0", "if1"), ("s0", "c1"), ("s0", "then1"), ("s0", "s_inner"), ("s0", "else1"), ("s0", "s2"),
        ("s_inner", "if2"), ("s_inner", "c2"), ("s_inner", "then2"), ("s_inner", "s1")
    ]

    for p1, p2 in edges_b:
        P.append(line(coords_b[p1][0], coords_b[p1][1], coords_b[p2][0], coords_b[p2][1], color=LINE, sw=1.4))

    # Нетермінали Б
    for k, lbl in [("s0", "S"), ("s_inner", "S")]:
        cx, cy = coords_b[k]
        P.append(circle(cx, cy, 14, fill=BG_LIGHT_NT, stroke=NODE_NONTERM, sw=1.6))
        P.append(text(cx, cy + 4, lbl, size=12, color=NODE_NONTERM, bold=True))

    # Термінали Б
    for k, lbl in [("if1", "if"), ("c1", "c1"), ("then1", "then"), ("else1", "else"), ("s2", "s2"),
                   ("if2", "if"), ("c2", "c2"), ("then2", "then"), ("s1", "s1")]:
        cx, cy = coords_b[k]
        P.append(rect(cx - 15, cy - 12, 30, 24, fill=BG_LIGHT_TR, stroke=NODE_TERM, sw=1.4, rx=4))
        P.append(text(cx, cy + 4, lbl, size=11, color=NODE_TERM, bold=True))

    P.append(text(W / 2, 475, "Граматика без розрізнення відкритих/закритих гілок допускає обидві побудови.", size=12, color=MUTED))

    render("img/dangling-else-ambiguity.svg", W, H, *P)


# ── Фігура 3: Конвеєр нормалізації до нормальної форми Чомскі (CNF) ────────────
def fig_cnf_pipeline():
    W, H = 960, 360
    P = []

    P.append(text(W / 2, 32, "П'ятиетапний конвеєр приведення КС-граматики до форми Чомскі (CNF)", size=16, color=INK, bold=True))
    P.append(text(W / 2, 54, "Цільова форма правил:  A → BC  або  A → a  (плюс S₀ → ε, якщо ε ∈ L(G))", size=12, color=MUTED))

    steps = [
        ("1. START", "Новий старт\nS₀ → S\n(S₀ не в RHS)", 110),
        ("2. NULL", "Вилучення\nε-правил\nA → ε\n(nullable)", 280),
        ("3. UNIT", "Вилучення\nланцюгових\nA → B\n(unit pairs)", 450),
        ("4. TERM", "Ізоляція\nтерміналів\nT_a → a\n(в довгих RHS)", 620),
        ("5. BIN", "Бінаризація\nправил > 2\nA → B₁C₁\n(каскади)", 790)
    ]

    for i, (title, desc, cx) in enumerate(steps):
        # Блок етапу
        tb, bw, bh = textbox(cx, 165, f"{title}\n\n{desc}", size=12, pad=10, fill=BG_LIGHT_NT, stroke=NODE_NONTERM, sw=1.6, min_w=140)
        P.append(tb)

        # Стрілка переходу до наступного етапу
        if i < len(steps) - 1:
            next_cx = steps[i + 1][2]
            P.append(arrow(cx + bw / 2 + 2, 165, next_cx - bw / 2 - 4, 165, color=LINE, sw=1.8))

    # Підсумок властивостей CNF внизу
    P.append(rect(60, 270, 840, 65, fill=BG_LIGHT_TR, stroke=NODE_TERM, sw=1.5, rx=6))
    P.append(text(W / 2, 295, "Гарантії нормальної форми Чомскі:", size=13, color=NODE_TERM, bold=True))
    P.append(text(W / 2, 318, "• Дерево виводу строго двійкове  • Довжина виведення слова |w| = n рівно 2n − 1 кроків  • Алгоритм CYK розпізнає за O(n³)", size=11.5, color=INK))

    render("img/cnf-pipeline.svg", W, H, *P)


# ── Фігура 4: Синтаксична діаграма (Railroad Diagram) для правила EBNF ─────────
def fig_railroad_ebnf():
    W, H = 880, 300
    P = []

    P.append(text(W / 2, 30, "Синтаксична діаграма (Railroad Diagram): правило EBNF для арифметичного виразу", size=16, color=INK, bold=True))
    P.append(text(W / 2, 52, "Правило:  Expr = Term , { ( \"+\" | \"-\" ) , Term } ;", size=12, color=MUTED))

    # Головна рейка (лінія зліва направо)
    P.append(line(60, 140, 150, 140, color=LINE, sw=2))

    # Вузол Term (обов'язковий перший)
    tb1, w1, h1 = textbox(210, 140, "Term", size=13, pad=12, fill=BG_LIGHT_NT, stroke=NODE_NONTERM, sw=1.6)
    P.append(tb1)

    # Лінія після Term
    P.append(line(210 + w1 / 2, 140, 310, 140, color=LINE, sw=2))

    # Прямий шлях до виходу (якщо повторень 0 разів)
    P.append(line(310, 140, 770, 140, color=LINE, sw=2))
    P.append(line(770, 140, 830, 140, color=LINE, sw=2))

    # Петля повторення знизу: розгалуження на { ("+" | "-") , Term }
    P.append(line(730, 140, 730, 220, color=LINE, sw=1.8))
    P.append(line(730, 220, 680, 220, color=LINE, sw=1.8))

    # Вузол Term у петлі
    tb2, w2, h2 = textbox(610, 220, "Term", size=13, pad=10, fill=BG_LIGHT_NT, stroke=NODE_NONTERM, sw=1.6)
    P.append(tb2)

    P.append(line(610 - w2 / 2, 220, 520, 220, color=LINE, sw=1.8))

    # Розгалуження на "+" або "-"
    P.append(line(520, 220, 480, 195, color=LINE, sw=1.6))
    P.append(line(520, 220, 480, 245, color=LINE, sw=1.6))

    tb_plus, _, _ = textbox(450, 195, " + ", size=12, pad=6, fill=BG_LIGHT_TR, stroke=NODE_TERM, sw=1.5, rx=12)
    P.append(tb_plus)
    tb_minus, _, _ = textbox(450, 245, " − ", size=12, pad=6, fill=BG_LIGHT_TR, stroke=NODE_TERM, sw=1.5, rx=12)
    P.append(tb_minus)

    P.append(line(420, 195, 380, 220, color=LINE, sw=1.6))
    P.append(line(420, 245, 380, 220, color=LINE, sw=1.6))

    # Повернення назад на вхід після першого Term
    P.append(line(380, 220, 310, 220, color=LINE, sw=1.8))
    P.append(line(310, 220, 310, 140, color=LINE, sw=1.8))

    # Стрілки напрямку руху по рейках
    P.append(arrow(100, 140, 130, 140, color=LINE, sw=2))
    P.append(arrow(785, 140, 815, 140, color=LINE, sw=2))
    P.append(arrow(680, 220, 660, 220, color=LINE, sw=1.8))
    P.append(arrow(345, 220, 325, 220, color=LINE, sw=1.8))

    # Позначки початку і кінця
    P.append(circle(55, 140, 6, fill=INK, stroke=INK, sw=1))
    P.append(circle(835, 140, 6, fill=INK, stroke=INK, sw=1))

    # Підписи
    P.append(text(70, 125, "Вхід", size=11, color=MUTED, bold=True))
    P.append(text(820, 125, "Вихід", size=11, color=MUTED, bold=True))
    P.append(text(W / 2, 280, "Квадратні блоки — нетермінали; заокруглені — термінали; розгалуження — альтернат; петля — { ... }", size=11.5, color=MUTED))

    render("img/ebnf-railroad.svg", W, H, *P)


if __name__ == "__main__":
    fig_parse_tree()
    fig_dangling_else()
    fig_cnf_pipeline()
    fig_railroad_ebnf()
    print("All figures generated successfully.")

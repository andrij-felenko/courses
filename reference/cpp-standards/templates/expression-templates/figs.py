# -*- coding: utf-8 -*-
"""Фігури до теми «Шаблони виразів: коли вираз стає деревом типів»."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG, exist_ok=True)

def fig_et_evaluation():
    W, H = 1000, 480
    out = []

    # Title / Header areas
    out.append(text(W / 2, 28, "Порівняння обчислення виразу: Vector result = A + B + C + D;", size=16, color=INK, bold=True))

    # Top Section: Naive Overloading
    out.append(rect(30, 50, W - 60, 190, fill="#fff5f5", stroke="#feb2b2", rx=8))
    out.append(text(50, 75, "1. Наївне перевантаження operator+ (жадібне обчислення)", size=14, color="#c53030", anchor="start", bold=True))

    # Nodes for naive
    bx1, w1, _ = textbox(110, 130, ["A + B"], size=13, fill="#ffffff", stroke="#fc8181")
    t1, wt1, _ = textbox(270, 130, ["Тимчасовий T1", "(Heap alloc 1)"], size=12, fill="#fed7d7", stroke="#e53e3e")
    t2, wt2, _ = textbox(490, 130, ["Тимчасовий T2", "(Heap alloc 2)"], size=12, fill="#fed7d7", stroke="#e53e3e")
    t3, wt3, _ = textbox(710, 130, ["Тимчасовий T3", "(Heap alloc 3)"], size=12, fill="#fed7d7", stroke="#e53e3e")
    res1, wr1, _ = textbox(910, 130, ["Result"], size=13, fill="#ffffff", stroke="#fc8181")

    out.extend([bx1, t1, t2, t3, res1])
    out.append(arrow(110 + w1/2 + 4, 130, 270 - wt1/2 - 4, 130, color="#e53e3e"))
    out.append(arrow(270 + wt1/2 + 4, 130, 490 - wt2/2 - 4, 130, color="#e53e3e"))
    out.append(text(380, 115, "+ C", size=12, color="#c53030", bold=True))
    out.append(arrow(490 + wt2/2 + 4, 130, 710 - wt3/2 - 4, 130, color="#e53e3e"))
    out.append(text(600, 115, "+ D", size=12, color="#c53030", bold=True))
    out.append(arrow(710 + wt3/2 + 4, 130, 910 - wr1/2 - 4, 130, color="#e53e3e"))

    out.append(text(W / 2, 210, "Результат: 3 тимчасові масиви в купі, 3 окремих цикли, 6 читань і 3 записи в RAM на елемент", size=12, color="#9b2c2c", bold=True))

    # Bottom Section: Expression Templates
    out.append(rect(30, 260, W - 60, 200, fill="#f0fff4", stroke="#9ae6b4", rx=8))
    out.append(text(50, 285, "2. Шаблони виразів (Expression Templates / ліниві)", size=14, color="#276749", anchor="start", bold=True))

    # AST Type node box
    ast_box, ast_w, _ = textbox(300, 360, [
        "Об'єкт AST дерева типів (0 байтів алокацій):",
        "VecAdd<VecAdd<VecAdd<Vector, Vector>, Vector>, Vector>",
        "Зберігає лише const& посилання на A, B, C, D"
    ], size=12, fill="#ffffff", stroke="#48bb78")
    out.append(ast_box)

    res2, wr2, _ = textbox(850, 360, ["Result Vector", "(1 виділення)"], size=13, fill="#c6f6d5", stroke="#2f855a")
    out.append(res2)

    out.append(arrow(300 + ast_w/2 + 8, 360, 850 - wr2/2 - 8, 360, color="#2f855a"))
    out.append(text((300 + ast_w/2 + 850 - wr2/2)/2, 340, "operator= (Один цикл)", size=12, color="#276749", bold=True))

    out.append(text(W / 2, 435, "Код циклу: for (i) result[i] = A[i] + B[i] + C[i] + D[i];  (0 буферів, 1 цикл, SIMD-векторизація)", size=12, color="#22543d", bold=True))

    render(os.path.join(IMG, 'et-evaluation.svg'), W, H, *out, title="Порівняння обчислення виразу: наївне проти шаблонів виразів")

if __name__ == '__main__':
    fig_et_evaluation()
    print("Generated figures in img/")

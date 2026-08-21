# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми Lisp (book/programming/languages/lisp)."""

import sys
import os

# 4 рівні вгору до кореня репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_cons_memory():
    """cons-memory.svg: будова cons-комірки та представлення списку (A (B C) D)."""
    W, H = 820, 360
    f = []

    # Заголовок зверху
    f.append(text(410, 25, "Представлення зв'язаних списків у пам'яті (cons-комірки)", size=16, bold=True))

    # Секція 1: Одиночна cons-комірка
    f.append(text(120, 65, "Анатомія комірки cons", size=13, bold=True, color=LINE))
    # Блок комірки (два поля CAR та CDR)
    f.append(rect(40, 80, 80, 50, fill="#eef2f7", stroke=LINE, sw=1.5, rx=4))
    f.append(rect(120, 80, 80, 50, fill="#eef2f7", stroke=LINE, sw=1.5, rx=4))
    f.append(text(80, 110, "CAR", size=13, bold=True, color=NEG))
    f.append(text(160, 110, "CDR", size=13, bold=True, color=POS))
    f.append(text(80, 150, "Значення / елемент", size=11, color=MUTED))
    f.append(text(160, 150, "Хвіст / наступна пара", size=11, color=MUTED))

    # Секція 2: Ланцюжок списку (A (B C) D)
    f.append(text(540, 65, "Список (A (B C) D) у вигляді зв'язаного графа cons-пар", size=13, bold=True, color=LINE))

    # Верхній ланцюжок: 3 комірки (для A, для (B C), для D)
    # Комірка 1: CAR -> 'A, CDR -> Комірка 2
    f.append(rect(300, 90, 50, 40, fill="#eef2f7", stroke=LINE, sw=1.5, rx=3))
    f.append(rect(350, 90, 50, 40, fill="#eef2f7", stroke=LINE, sw=1.5, rx=3))
    f.append(circle(325, 110, 4, fill=LINE, stroke=LINE))
    f.append(circle(375, 110, 4, fill=LINE, stroke=LINE))

    # Значення 'A під першою коміркою
    f.append(rect(305, 170, 40, 30, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(325, 190, "A", size=14, bold=True, color=FIELD))
    f.append(arrow(325, 114, 325, 166, color=LINE, sw=1.5))

    # Стрілка від CDR 1 до Комірки 2
    f.append(arrow(379, 110, 446, 110, color=LINE, sw=1.5))

    # Комірка 2: CAR -> підсписок (B C), CDR -> Комірка 3
    f.append(rect(450, 90, 50, 40, fill="#eef2f7", stroke=LINE, sw=1.5, rx=3))
    f.append(rect(500, 90, 50, 40, fill="#eef2f7", stroke=LINE, sw=1.5, rx=3))
    f.append(circle(475, 110, 4, fill=LINE, stroke=LINE))
    f.append(circle(525, 110, 4, fill=LINE, stroke=LINE))

    # Стрілка від CDR 2 до Комірки 3
    f.append(arrow(529, 110, 596, 110, color=LINE, sw=1.5))

    # Комірка 3: CAR -> 'D, CDR -> NIL
    f.append(rect(600, 90, 50, 40, fill="#eef2f7", stroke=LINE, sw=1.5, rx=3))
    f.append(rect(650, 90, 50, 40, fill="#eef2f7", stroke=LINE, sw=1.5, rx=3))
    f.append(circle(625, 110, 4, fill=LINE, stroke=LINE))
    f.append(line(650, 130, 700, 90, color=POS, sw=2))  # Діагональ для NIL
    f.append(text(730, 115, "NIL ( / )", size=12, bold=True, color=POS))

    # Значення 'D під третьою коміркою
    f.append(rect(605, 170, 40, 30, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(625, 190, "D", size=14, bold=True, color=FIELD))
    f.append(arrow(625, 114, 625, 166, color=LINE, sw=1.5))

    # Підсписок (B C): відгалуження вниз від Комірки 2
    f.append(arrow(475, 114, 475, 226, color=LINE, sw=1.5))

    # Комірка підсписку 1 (для B)
    f.append(rect(450, 230, 50, 40, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=3))
    f.append(rect(500, 230, 50, 40, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=3))
    f.append(circle(475, 250, 4, fill=LINE, stroke=LINE))
    f.append(circle(525, 250, 4, fill=LINE, stroke=LINE))

    # Значення 'B під коміркою підсписку 1
    f.append(rect(455, 300, 40, 30, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(475, 320, "B", size=14, bold=True, color=FIELD))
    f.append(arrow(475, 254, 475, 296, color=LINE, sw=1.5))

    # Стрілка від CDR підсписку 1 до підсписку 2
    f.append(arrow(529, 250, 576, 250, color=LINE, sw=1.5))

    # Комірка підсписку 2 (для C)
    f.append(rect(580, 230, 50, 40, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=3))
    f.append(rect(630, 230, 50, 40, fill="#fef9e7", stroke="#d4ac0d", sw=1.5, rx=3))
    f.append(circle(605, 250, 4, fill=LINE, stroke=LINE))
    f.append(line(630, 270, 680, 230, color=POS, sw=2))  # Діагональ для NIL
    f.append(text(710, 255, "NIL", size=12, bold=True, color=POS))

    # Значення 'C під коміркою підсписку 2
    f.append(rect(585, 300, 40, 30, fill="#e8f5e9", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(605, 320, "C", size=14, bold=True, color=FIELD))
    f.append(arrow(605, 254, 605, 296, color=LINE, sw=1.5))

    render(os.path.join(IMG, "cons-memory.svg"), W, H, *f)


def fig_homoiconicity_ast():
    """homoiconicity-ast.svg: тотожність текстового виразу, структури cons-пар та дерева AST."""
    W, H = 840, 380
    f = []

    f.append(text(420, 25, "Гомоіконічність: код як дерево списків та абстрактне синтаксичне дерево", size=16, bold=True))

    # Ліва колонка: Текстовий S-вираз
    f.append(rect(30, 60, 230, 290, fill="#fcfcfd", stroke=MUTED, sw=1, rx=6))
    f.append(text(145, 90, "1. Текстовий S-вираз", size=14, bold=True, color=LINE))
    f.append(rect(45, 120, 200, 60, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    f.append(text(145, 155, "(+ (* a 2) b)", size=16, bold=True, color=NEG))

    f.append(mtext(145, 220, [
        "Текст є прямим",
        "серіалізованим записом",
        "структури дерева.",
        "Парсер Reader перетворює",
        "дужки на зв'язки списку."
    ], size=12, color=MUTED, anchor="middle"))

    # Стрілка між 1 та 2
    f.append(arrow(265, 150, 305, 150, color=LINE, sw=2))
    f.append(text(285, 140, "Read", size=11, bold=True, color=FIELD))

    # Центральна колонка: Структура cons-пар у пам'яті
    f.append(rect(310, 60, 250, 290, fill="#fcfcfd", stroke=MUTED, sw=1, rx=6))
    f.append(text(435, 90, "2. Список cons-пар у купі", size=14, bold=True, color=LINE))

    # Вузол +
    f.append(rect(330, 120, 40, 26, fill="#e8f5e9", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(350, 138, "+", size=14, bold=True, color=FIELD))
    f.append(rect(370, 120, 40, 26, fill="#eef2f7", stroke=LINE, sw=1.2, rx=3))
    f.append(text(390, 138, "·", size=14, bold=True))

    # Відгалуження на підсписок (* a 2)
    f.append(arrow(390, 146, 390, 185, color=LINE, sw=1.2))

    f.append(rect(360, 190, 35, 24, fill="#fef9e7", stroke="#d4ac0d", sw=1.2, rx=3))
    f.append(text(377, 207, "*", size=13, bold=True, color="#b7950b"))
    f.append(rect(395, 190, 35, 24, fill="#fef9e7", stroke="#d4ac0d", sw=1.2, rx=3))
    f.append(text(412, 207, "·", size=13, bold=True))

    f.append(arrow(430, 202, 445, 202, color=LINE, sw=1.2))
    f.append(rect(450, 190, 30, 24, fill="#e8f5e9", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(465, 207, "a", size=13, bold=True, color=FIELD))

    f.append(arrow(480, 202, 495, 202, color=LINE, sw=1.2))
    f.append(rect(500, 190, 30, 24, fill="#e8f5e9", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(515, 207, "2", size=13, bold=True, color=FIELD))

    # Продовження головного списку до 'b
    f.append(arrow(410, 133, 445, 133, color=LINE, sw=1.2))
    f.append(rect(450, 120, 40, 26, fill="#e8f5e9", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(470, 138, "b", size=14, bold=True, color=FIELD))
    f.append(rect(490, 120, 35, 26, fill="#eef2f7", stroke=LINE, sw=1.2, rx=3))
    f.append(text(507, 138, "NIL", size=11, bold=True, color=POS))

    f.append(mtext(435, 280, [
        "Звичайні структури даних,",
        "доступні для car / cdr / map.",
        "Програма оперує кодом як списком."
    ], size=11, color=MUTED, anchor="middle"))

    # Стрілка між 2 та 3
    f.append(arrow(565, 150, 605, 150, color=LINE, sw=2))
    f.append(text(585, 140, "Тотожно", size=11, bold=True, color=POS))

    # Права колонка: Логічне дерево AST
    f.append(rect(610, 60, 200, 290, fill="#fcfcfd", stroke=MUTED, sw=1, rx=6))
    f.append(text(710, 90, "3. Логічне дерево AST", size=14, bold=True, color=LINE))

    # Вузол кореня (+)
    f.append(circle(710, 130, 16, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(710, 135, "+", size=16, bold=True, color=POS))

    # Гілки від кореня (+)
    f.append(line(698, 142, 665, 188, color=LINE, sw=1.5))
    f.append(line(722, 142, 755, 188, color=LINE, sw=1.5))

    # Ліве піддерево (*)
    f.append(circle(660, 200, 15, fill="#fef9e7", stroke="#d4ac0d", sw=1.5))
    f.append(text(660, 205, "*", size=15, bold=True, color="#b7950b"))

    # Листок праворуч (b)
    f.append(circle(760, 200, 15, fill="#e8f5e9", stroke=FIELD, sw=1.5))
    f.append(text(760, 205, "b", size=13, bold=True, color=FIELD))

    # Листки під (*) -> a, 2
    f.append(line(650, 212, 635, 258, color=LINE, sw=1.5))
    f.append(line(670, 212, 685, 258, color=LINE, sw=1.5))

    f.append(circle(630, 270, 14, fill="#e8f5e9", stroke=FIELD, sw=1.5))
    f.append(text(630, 275, "a", size=13, bold=True, color=FIELD))

    f.append(circle(690, 270, 14, fill="#e8f5e9", stroke=FIELD, sw=1.5))
    f.append(text(690, 275, "2", size=13, bold=True, color=FIELD))

    f.append(mtext(710, 318, [
        "Синтаксичне дерево виразу",
        "повністю збігається зі списком."
    ], size=11, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, "homoiconicity-ast.svg"), W, H, *f)


def fig_eval_apply_cycle():
    """eval-apply-cycle.svg: двотактний взаєморекурсивний цикл обчислення eval та apply."""
    W, H = 800, 370
    f = []

    f.append(text(400, 25, "Двотактна модель обчислення Lisp: взаємодія eval та apply", size=16, bold=True))

    # Вхідний вираз зліва
    f.append(rect(30, 140, 130, 70, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    f.append(text(95, 165, "Вхідний вираз", size=12, color=MUTED))
    f.append(text(95, 190, "(f x y)", size=15, bold=True, color=LINE))

    # Стрілка від входу до eval
    f.append(arrow(160, 175, 225, 175, color=LINE, sw=1.8))
    f.append(text(192, 163, "expr, env", size=11, bold=True, color=MUTED))

    # Блок EVAL
    f.append(rect(230, 90, 200, 180, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    f.append(text(330, 120, "eval(expr, env)", size=16, bold=True, color=NEG))
    f.append(line(245, 135, 415, 135, color=NEG, sw=1, dash="3,3"))

    f.append(mtext(330, 160, [
        "1. Атом → повернути значення",
        "2. Символ → шукати в env",
        "3. Спецформа (if, lambda, quote)",
        "   → обробити безпосередньо",
        "4. Виклик функції:",
        "   eval(f), eval(x), eval(y)..."
    ], size=11, color=INK, anchor="middle"))

    # Стрілка від EVAL до APPLY (верхня дуга)
    f.append(arrow(430, 140, 505, 140, color=FIELD, sw=2))
    f.append(text(468, 128, "func, args", size=12, bold=True, color=FIELD))

    # Блок APPLY
    f.append(rect(510, 90, 220, 180, fill="#e8f5e9", stroke=FIELD, sw=2, rx=8))
    f.append(text(620, 120, "apply(func, args)", size=16, bold=True, color=FIELD))
    f.append(line(525, 135, 715, 135, color=FIELD, sw=1, dash="3,3"))

    f.append(mtext(620, 160, [
        "1. Примітив (C/апаратний):",
        "   обчислити результат напряму",
        "2. Користувацька функція (лямбда):",
        "   створити новий фрейм env",
        "   зв'язати параметри з args,",
        "   підготувати тіло (body)"
    ], size=11, color=INK, anchor="middle"))

    # Зворотна стрілка від APPLY до EVAL (нижня дуга для обчислення тіла лямбди)
    f.append(line(620, 270, 620, 310, color=POS, sw=1.8))
    f.append(line(620, 310, 330, 310, color=POS, sw=1.8))
    f.append(arrow(330, 310, 330, 272, color=POS, sw=1.8))
    f.append(text(475, 332, "eval(body, new_env) — виконання тіла замикання", size=12, bold=True, color=POS))

    # Вихід результату вправо (для примітивів / завершення)
    f.append(arrow(730, 175, 775, 175, color=LINE, sw=1.8))
    f.append(text(755, 163, "Значення", size=11, bold=True, color=MUTED))

    render(os.path.join(IMG, "eval-apply-cycle.svg"), W, H, *f)


def fig_macro_expansion():
    """macro-expansion.svg: пайплайн макророзгортання (трансформація AST) проти текстових макросів C."""
    W, H = 840, 370
    f = []

    f.append(text(420, 25, "Механізм макросів: синтаксична трансформація AST у Lisp проти тексту в C", size=16, bold=True))

    # Верхня панель: C Preprocessor (текстовий рівень)
    f.append(rect(30, 55, 780, 130, fill="#fdfefe", stroke=MUTED, sw=1, rx=6))
    f.append(text(140, 78, "C Preprocessor: текстова заміна", size=13, bold=True, color=POS))

    f.append(rect(50, 95, 180, 70, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    f.append(text(140, 120, "Сирий текст коду", size=11, color=MUTED))
    f.append(text(140, 145, "#define SQR(x) x*x", size=12, bold=True, color=POS))

    f.append(arrow(230, 130, 285, 130, color=POS, sw=1.5))
    f.append(text(258, 120, "Підстановка", size=10, color=MUTED))

    f.append(rect(290, 95, 230, 70, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    f.append(text(405, 120, "Текстовий результат", size=11, color=MUTED))
    f.append(text(405, 145, "SQR(1 + 2)  →  1 + 2 * 1 + 2", size=12, bold=True, color=POS))

    f.append(arrow(520, 130, 575, 130, color=POS, sw=1.5))
    f.append(text(548, 120, "Парсинг", size=10, color=MUTED))

    f.append(rect(580, 95, 210, 70, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4))
    f.append(text(685, 120, "Помилкове обчислення", size=11, color=POS, bold=True))
    f.append(text(685, 145, "Результат: 5 замість 9", size=12, bold=True, color=LINE))

    # Нижня панель: Lisp Macroexpansion (структурний рівень)
    f.append(rect(30, 205, 780, 145, fill="#fdfefe", stroke=MUTED, sw=1, rx=6))
    f.append(text(160, 228, "Lisp Defmacro: трансформація синтаксичного дерева", size=13, bold=True, color=FIELD))

    f.append(rect(50, 245, 180, 85, fill="#e8f5e9", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(140, 270, "Вхідне AST (S-вираз)", size=11, color=MUTED))
    f.append(text(140, 295, "(sqr (+ 1 2))", size=13, bold=True, color=FIELD))
    f.append(text(140, 315, "список: (sqr (+ 1 2))", size=10, color=MUTED))

    f.append(arrow(230, 287, 285, 287, color=FIELD, sw=1.5))
    f.append(text(258, 275, "Macro-fn", size=10, bold=True, color=FIELD))

    f.append(rect(290, 245, 230, 85, fill="#e8f5e9", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(405, 268, "Трансформація кодом Lisp", size=11, color=MUTED))
    f.append(text(405, 290, "(let ((g (+ 1 2)))", size=12, bold=True, color=LINE))
    f.append(text(405, 312, "  (* g g))", size=12, bold=True, color=LINE))

    f.append(arrow(520, 287, 575, 287, color=FIELD, sw=1.5))
    f.append(text(548, 275, "Компіляція", size=10, color=MUTED))

    f.append(rect(580, 245, 210, 85, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    f.append(text(685, 270, "Коректне AST", size=11, color=NEG, bold=True))
    f.append(text(685, 295, "Один раз: g = 3", size=12, bold=True, color=LINE))
    f.append(text(685, 315, "Результат: 9 (безпечно)", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "macro-expansion.svg"), W, H, *f)


def main():
    fig_cons_memory()
    fig_homoiconicity_ast()
    fig_eval_apply_cycle()
    fig_macro_expansion()
    print("Усі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()

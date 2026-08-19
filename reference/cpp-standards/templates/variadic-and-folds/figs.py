# -*- coding: utf-8 -*-
"""Фігури до теми «Шаблони змінної арності й вирази згортки»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def fig_pack_expansion_mechanics():
    W, H = 1040, 480
    f = []

    # Заголовок
    f.append(textbox(520, 30, "Механіка розпакування пакетів: оголошення, патерн та інстанціювання",
                     size=15, bold=True, fill="#eef3f8")[0])

    # Ліва колонка: Оголошення пакетів
    f.append(rect(30, 65, 300, 355, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(180, 95, "Оголошення пакетів", size=14, bold=True))
    f.append(mtext(180, 125, ["Синтаксис еліпсиса (...) створює", "пакет типів або значень"], size=11, color=MUTED))

    f.append(textbox(180, 195, "template <typename... Types>\nvoid print_all(Types... args);",
                     size=11, fill="#f8fafc", stroke=LINE)[0])

    f.append(textbox(180, 290, "Types: пакет типів\n<int, double, string>\n\nargs: пакет аргументів\n(42, 3.14, \"text\")",
                     size=11, fill="#eaf0fd", stroke=NEG)[0])

    f.append(textbox(180, 385, "sizeof...(Types) == 3\n(константа часу компіляції)",
                     size=11, fill="#eef7ee", stroke=POS)[0])

    # Стрілка між лівою та центральною колонками
    f.append(arrow(335, 240, 375, 240))
    f.append(text(355, 225, "Патерн", size=10, bold=True, color=MUTED))

    # Центральна колонка: Правило розпакування патерну
    f.append(rect(380, 65, 300, 355, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(530, 95, "Патерн розпакування", size=14, bold=True))
    f.append(mtext(530, 125, ["Вираз зліва від еліпсиса", "тиражується для кожного елемента"], size=11, color=MUTED))

    f.append(textbox(530, 195, "Pattern(pack)... \n\nПриклад:\nstd::forward<Types>(args)...",
                     size=11, fill="#fff8e7", stroke=FIELD)[0])

    f.append(textbox(530, 295, "Синхронне розпакування:\nfunc(keys, values)...\n\nВимога: довжини пакетів\nмусять точно збігатися!",
                     size=11, fill="#fdf0ed", stroke=POS)[0])

    f.append(textbox(530, 385, "Контексти: виклики, списки,\nініціалізація, спадкування",
                     size=11, fill="#f4f6f8", stroke=LINE)[0])

    # Стрілка між центральною та правою колонками
    f.append(arrow(685, 240, 725, 240))
    f.append(text(705, 225, "Генерація", size=10, bold=True, color=MUTED))

    # Права колонка: Результат генерації компілятора
    f.append(rect(730, 65, 280, 355, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(870, 95, "Синтезований виклик", size=14, bold=True))
    f.append(mtext(870, 125, ["Кома-розділений список", "в абстрактному дереві (AST)"], size=11, color=MUTED))

    f.append(textbox(870, 205, "consume(\n  std::forward<int>(a1),\n  std::forward<double>(a2),\n  std::forward<string>(a3)\n);",
                     size=11, fill="#eef7ee", stroke=POS)[0])

    f.append(textbox(870, 340, "Повний інлайнінг:\nвідсутні масиви у пам'яті,\nнульовий оверхед виклику",
                     size=11, fill="#eaf0fd", stroke=NEG)[0])

    # Нижній підсумок
    f.append(textbox(520, 450, "Розпакування пакета — це синтаксична трансформація AST на етапі компіляції без рантайм-витрат",
                     size=12, bold=True, fill="#f4f4f6", stroke=MUTED)[0])

    render(os.path.join(OUT, 'pack-expansion-mechanics.svg'), W, H, *f)


def fig_fold_expression_forms():
    W, H = 1060, 500
    f = []

    # Заголовок
    f.append(textbox(530, 28, "Чотири граматичні форми виразів згортки (Fold Expressions, C++17)",
                     size=15, bold=True, fill="#eef3f8")[0])

    # 1. Unary Left
    f.append(rect(30, 60, 235, 385, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(147, 85, "Unary Left (... op E)", size=13, bold=True))
    f.append(mtext(147, 112, ["Ліва унарна згортка", "Асоціативність: вліво"], size=11, color=MUTED))
    f.append(textbox(147, 160, "(... + args)", size=12, bold=True, fill="#eaf0fd", stroke=NEG)[0])
    f.append(textbox(147, 240, "Розкриття виразу:\n(((a1 + a2) + a3) + a4)\n\nПорожній пакет:\n&& -> true, || -> false,\n,  -> void()\nінші op -> помилка!",
                     size=11, fill="#f8fafc", stroke=LINE)[0])
    f.append(textbox(147, 380, "Застосування:\nпотоки (std::cout << ...)\nта додавання чисел",
                     size=11, fill="#eef7ee", stroke=POS)[0])

    # 2. Unary Right
    f.append(rect(280, 60, 235, 385, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(397, 85, "Unary Right (E op ...)", size=13, bold=True))
    f.append(mtext(397, 112, ["Права унарна згортка", "Асоціативність: вправо"], size=11, color=MUTED))
    f.append(textbox(397, 160, "(args + ...)", size=12, bold=True, fill="#eaf0fd", stroke=NEG)[0])
    f.append(textbox(397, 240, "Розкриття виразу:\n(a1 + (a2 + (a3 + a4)))\n\nПорожній пакет:\n&& -> true, || -> false,\n,  -> void()\nінші op -> помилка!",
                     size=11, fill="#f8fafc", stroke=LINE)[0])
    f.append(textbox(397, 380, "Застосування:\nправоасоціативні op:\nприсвоєння (=), стек",
                     size=11, fill="#eef7ee", stroke=POS)[0])

    # 3. Binary Left
    f.append(rect(535, 60, 245, 385, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(657, 85, "Binary Left (I op ... op E)", size=13, bold=True))
    f.append(mtext(657, 112, ["Ліва бінарна згортка", "З явним ініціалізатором I"], size=11, color=MUTED))
    f.append(textbox(657, 160, "(init + ... + args)", size=12, bold=True, fill="#fff8e7", stroke=FIELD)[0])
    f.append(textbox(657, 240, "Розкриття виразу:\n((((init + a1) + a2) + a3) + a4)\n\nПорожній пакет:\nРезультат == init\n(дозволено для всіх op)",
                     size=11, fill="#f8fafc", stroke=LINE)[0])
    f.append(textbox(657, 380, "Застосування:\nдрук у потік із префіксом,\nпочаткове накопичення",
                     size=11, fill="#eef7ee", stroke=POS)[0])

    # 4. Binary Right
    f.append(rect(795, 60, 235, 385, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(912, 85, "Binary Right (E op ... op I)", size=13, bold=True))
    f.append(mtext(912, 112, ["Права бінарна згортка", "З кінцевим значенням I"], size=11, color=MUTED))
    f.append(textbox(912, 160, "(args + ... + init)", size=12, bold=True, fill="#fff8e7", stroke=FIELD)[0])
    f.append(textbox(912, 240, "Розкриття виразу:\n(a1 + (a2 + (a3 + (a4 + init))))\n\nПорожній пакет:\nРезультат == init\n(дозволено для всіх op)",
                     size=11, fill="#f8fafc", stroke=LINE)[0])
    f.append(textbox(912, 380, "Застосування:\nланцюжки трансформацій,\nтермінальні вузли списків",
                     size=11, fill="#eef7ee", stroke=POS)[0])

    # Підсумок
    f.append(textbox(530, 470, "Вираз згортки обов'язково обмежується круглими дужками; бінарна форма гарантує безпеку порожніх пакетів",
                     size=12, bold=True, fill="#f4f4f6", stroke=MUTED)[0])

    render(os.path.join(OUT, 'fold-expression-forms.svg'), W, H, *f)


def fig_recursive_vs_fold_ast():
    W, H = 1040, 480
    f = []

    # Заголовок
    f.append(textbox(520, 30, "Порівняння компіляції: C++11 рекурсивні шаблони проти C++17 Fold Expressions",
                     size=15, bold=True, fill="#eef3f8")[0])

    # Ліва панель: C++11 Рекурсія
    f.append(rect(30, 65, 465, 355, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(262, 95, "C++11: Рекурсивне інстанціювання", size=14, bold=True, color=POS))
    f.append(mtext(262, 125, ["Кожен аргумент породжує окрему інстанціацію шаблону,", "навантажуючи компілятор глибиною рекурсії O(N)"],
                   size=11, color=MUTED))

    f.append(textbox(262, 210, "sum(1, 2, 3, 4)\n  -> sum(1, Tail<2,3,4>...)\n    -> sum(2, Tail<3,4>...)\n      -> sum(3, Tail<4>...)\n        -> sum(4) [базовий випадок]",
                     size=11, fill="#fdf0ed", stroke=POS)[0])

    f.append(textbox(262, 335, "Проблеми підходу:\n* N окремих функцій у таблиці символів\n* Роздування бінарного коду без інлайнінгу\n* Повільна компіляція (витрати пам'яті AST)",
                     size=11, fill="#f8fafc", stroke=LINE)[0])

    # Права панель: C++17 Fold Expression
    f.append(rect(545, 65, 465, 355, fill=BG, stroke=MUTED, sw=1.2))
    f.append(text(777, 95, "C++17: Вираз згортки (Fold)", size=14, bold=True, color=FIELD))
    f.append(mtext(777, 125, ["Один єдиний шаблон інстанціюється миттєво;", "компілятор згортає операцію в єдиний вузол виразу O(1)"],
                   size=11, color=MUTED))

    f.append(textbox(777, 210, "template <typename... Args>\nauto sum(Args... args) {\n    return (args + ...);\n}\n// AST: (1 + (2 + (3 + 4)))",
                     size=11, fill="#eef7ee", stroke=FIELD)[0])

    f.append(textbox(777, 335, "Переваги підходу:\n* Рівно одна інстанціація функції в пам'яті\n* Нульовий оверхед на рекурсивні виклики\n* Миттєва трансляція та спрощена діагностика",
                     size=11, fill="#eaf0fd", stroke=NEG)[0])

    # Підсумок
    f.append(textbox(520, 450, "C++17 згортка замінює рекурсивну генерацію AST-дерев пласким двійковим виразом безпосередньо у вузлі кодогенерації",
                     size=12, bold=True, fill="#f4f4f6", stroke=MUTED)[0])

    render(os.path.join(OUT, 'recursive-vs-fold-ast.svg'), W, H, *f)


if __name__ == '__main__':
    fig_pack_expansion_mechanics()
    fig_fold_expression_forms()
    fig_recursive_vs_fold_ast()
    print("All figures generated successfully!")

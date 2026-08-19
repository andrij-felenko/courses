# -*- coding: utf-8 -*-
"""Фігури до теми «if constexpr: гілка, якої не існує»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_ast_pruning():
    """Механізм відсікання AST та інстанціювання в if constexpr."""
    W, H = 1040, 480
    out = []

    # Заголовок та фаза 1
    out.append(fitbox(20, 20, 290, 130,
                      "Фаза 1: Синтаксичний аналіз\n(Template Definition Parsing)\n\n• Перевірка базової граматики C++\n• Побудова неінстанційованого AST\n• Збереження залежних імен без перевірки",
                      size=12, fill="#f8fafc", stroke="#64748b"))

    out.append(arrow(320, 85, 370, 85))

    # Фаза 2: Інстанціювання
    out.append(fitbox(380, 20, 310, 130,
                      "Фаза 2: Інстанціювання для типу T\n(Template Instantiation)\n\n• Підстановка конкретного типу T\n• Обчислення умови if constexpr (bool)\n• Вибір активної гілки компілятором",
                      size=12, fill="#eff6ff", stroke="#3b82f6"))

    out.append(arrow(700, 55, 745, 55))
    out.append(arrow(700, 115, 745, 115))

    # Результат: Активна гілка
    out.append(fitbox(755, 20, 265, 60,
                      "Активна гілка (Active Branch)\n• Повне інстанціювання залежних типів\n• Генерація інструкцій машинного коду",
                      size=11, fill="#f0fdf4", stroke=FIELD))

    # Результат: Відкинута гілка
    out.append(fitbox(755, 90, 265, 60,
                      "Відкинута гілка (Discarded Statement)\n• Залежні вирази НЕ інстанціюються\n• Машинний код НЕ генерується взагалі",
                      size=11, fill="#fef2f2", stroke=POS))

    # Детальна схема внизу
    out.append(rect(20, 175, 1000, 280, fill="#fafafa", stroke="#cbd5e1"))

    out.append(fitbox(35, 190, 460, 110,
                      "Шаблон функції з умовним компілюванням:\n\ntemplate<typename T>\nauto process(T val) {\n  if constexpr (std::is_pointer_v<T>) return *val;\n  else return val;\n}",
                      size=12, fill="#ffffff", stroke="#94a3b8"))

    # Випадок 1: T = int
    out.append(fitbox(515, 190, 490, 115,
                      "Спеціалізація process<int>(int val):\n\n• Умова std::is_pointer_v<int> ⇒ false\n• return *val; ⇒ ВІДКИДАЄТЬСЯ (немає помилки розіменування int!)\n• return val; ⇒ активна (тип повернення виведено як int)",
                      size=11, fill="#eff6ff", stroke="#3b82f6"))

    # Випадок 2: T = int*
    out.append(fitbox(515, 320, 490, 115,
                      "Спеціалізація process<int*>(int* val):\n\n• Умова std::is_pointer_v<int*> ⇒ true\n• return *val; ⇒ активна (розпаковує вказівник, тип int)\n• return val; ⇒ ВІДКИДАЄТЬСЯ (вказівник не повертається)",
                      size=11, fill="#f0fdf4", stroke=FIELD))

    out.append(fitbox(35, 320, 460, 115,
                      "Ключовий інваріант стандарту C++17 [stmt.if]:\n\nВідкинута гілка у тілі шаблону не піддається\nінстанціюванню для заданих аргументів шаблону,\nзапобігаючи помилкам несумісності типів і методів.",
                      size=11, fill="#fffbeb", stroke="#d97706"))

    render(os.path.join(IMG, 'constexpr-if-ast-pruning.svg'), W, H, *out,
           title="Механізм відсікання синтаксичного дерева (AST Pruning) в if constexpr")


def fig_tag_sfinae_comparison():
    """Порівняння архітектурних підходів розгалуження: Tag Dispatch vs SFINAE vs if constexpr."""
    W = 1040
    M = 20
    cols = [220, 270, 270, 240]
    head = ["Характеристика", "Tag Dispatching (C++98/03)", "SFINAE / enable_if (C++11/14)", "if constexpr (C++17)"]
    rows = [
        ["Архітектурна модель",
         "Розподіл логіки на перевантажені\nдопоміжні функції через типи-теги",
         "Множинні шаблони з взаємовиключними\nумовами у заголовку чи параметрах",
         "Єдина узагальнена функція з лінійним\nпроцедурним кодом усередині тіла"],
        ["Кількість функцій",
         "1 диспетчер + N реалізацій\n(по одній на кожну категорію)",
         "N незалежних шаблонів функцій\nіз захаращеними сигнатурами",
         "1 єдина функція (без допоміжних\nструктур чи перевантажень)"],
        ["Діагностика помилок",
         "Помилка вибору перевантаження;\nсередній рівень шуму компілятора",
         "Величезні каскади помилок\nsubstitution failure на сотні рядків",
         "Точна локальна діагностика\nвсередині конкретної гілки коду"],
        ["Вплив на компіляцію",
         "Створення додаткових типів-тегів\nта роздуття таблиці перевантажень",
         "Значні витрати на перевірку SFINAE\nта генерацію складних манглованих імен",
         "Мінімальне навантаження: компілятор\nпросто відсікає неактивне піддерево AST"],
        ["Читабельність коду",
         "Низька: потік виконання розірвано\nміж кількома окремими функціями",
         "Вкрай низька: складна шаблонна магія\nприховує реальну логіку алгоритму",
         "Висока: природний синтаксис if/else,\nзрозумілий будь-якому розробнику"]
    ]
    HH, RH, GAP = 50, 74, 6
    H = 40 + HH + len(rows) * RH + 20
    out = []

    x = M
    for i, c in enumerate(cols):
        fill = "#e2e8f0" if i == 0 else ("#e0f2fe" if i == 3 else "#f1f5f9")
        out.append(fitbox(x, 40, c - GAP, HH - GAP, head[i], size=13, bold=True, fill=fill))
        x += c

    y = 40 + HH
    for ri, r in enumerate(rows):
        x = M
        for i, cell in enumerate(r):
            if i == 0:
                fill = "#f8fafc"
            elif i == 3:
                fill = "#f0fdf4"
            else:
                fill = "#ffffff"
            out.append(fitbox(x, y, cols[i] - GAP, RH - GAP, cell, size=11, bold=(i == 0), fill=fill))
            x += cols[i]
        y += RH

    render(os.path.join(IMG, 'tag-sfinae-vs-constexpr-if.svg'), W, H, *out,
           title="Порівняння підходів статичного розгалуження в C++")


def fig_dependent_false():
    """Механізм відкладеної діагностики static_assert через dependent_false."""
    W, H = 1000, 360
    out = []

    # Лівий блок: static_assert(false) - Помилка на фазі 1
    out.append(fitbox(30, 20, 440, 60,
                      "Проблема: static_assert(false) у відкинутій гілці\nПомилка компіляції виникає ЗАВЖДИ на Фазі 1",
                      size=13, bold=True, fill="#fef2f2", stroke=POS))

    out.append(fitbox(30, 95, 440, 110,
                      "template<typename T>\nvoid handle(T val) {\n  if constexpr (std::is_integral_v<T>) { ... }\n  else static_assert(false, \"Unsupported type!\");\n}",
                      size=12, fill="#ffffff", stroke="#94a3b8"))

    out.append(fitbox(30, 220, 440, 115,
                      "Чому це не працює:\n\n1. Вираз false НЕ залежить від параметра шаблону T.\n2. Згідно з [temp.res], компілятор зобов'язаний\n   перевірити незалежні вирази на Фазі 1 (парсинг).\n3. Збірка аварійно зупиняється ще до інстанціювання!",
                      size=11, fill="#fff1f2", stroke=POS))

    # Правий блок: dependent_false<T> - Відкладена перевірка на фазі 2
    out.append(fitbox(530, 20, 440, 60,
                      "Рішення: шаблон dependent_false<T>\nПеревірка відкладається до моменту вибору гілки на Фазі 2",
                      size=13, bold=True, fill="#f0fdf4", stroke=FIELD))

    out.append(fitbox(530, 95, 440, 110,
                      "template<typename> inline constexpr bool dependent_false = false;\n\ntemplate<typename T>\nvoid handle(T val) {\n  if constexpr (std::is_integral_v<T>) { ... }\n  else static_assert(dependent_false<T>, \"Unsupported type!\");\n}",
                      size=12, fill="#ffffff", stroke="#94a3b8"))

    out.append(fitbox(530, 220, 440, 115,
                      "Як це працює:\n\n1. dependent_false<T> синтаксично залежить від типу T.\n2. Компілятор відкладає обчислення на Фазу 2 (інстанціювання).\n3. Якщо гілка else відкинута, вираз НЕ інстанціюється.\n4. Помилка виникає ЛИШЕ якщо дійсно передано непідтримуваний T.",
                      size=11, fill="#f0fdf4", stroke=FIELD))

    render(os.path.join(IMG, 'dependent-false-mechanism.svg'), W, H, *out,
           title="Механізм відкладеної перевірки static_assert через dependent_false")


def fig_return_deduction():
    """Виведення типу повернення auto при умовному компілюванні if constexpr."""
    W, H = 980, 360
    out = []

    # Загальний заголовок і приклад коду
    out.append(fitbox(30, 20, 420, 150,
                      "Шаблон функції з виведенням auto:\n\ntemplate<typename T>\nauto get_representation(T val) {\n  if constexpr (std::is_integral_v<T>)\n    return val * 2;          // int\n  else if constexpr (std::is_floating_point_v<T>)\n    return val + 0.5;        // double\n  else\n    return std::string(val); // std::string\n}",
                      size=11, fill="#ffffff", stroke="#94a3b8"))

    out.append(fitbox(30, 185, 420, 150,
                      "Правило виведення типу повернення [dcl.spec.auto]:\n\nУ звичайній функції кожна інструкція return повинна\nвиводити в точності один і той самий тип даних.\n\nВ if constexpr інструкції return у відкинутих гілках\nПОВНІСТЮ ІГНОРУЮТЬСЯ під час виведення типу auto!",
                      size=11, fill="#eff6ff", stroke="#3b82f6"))

    # Справа: 3 сценарії інстанціювання
    out.append(fitbox(480, 20, 470, 95,
                      "Виклик get_representation(10) [T = int]:\n\n• Активна гілка 1 ⇒ повертає 20 (int)\n• Гілки 2 і 3 відкинуті й не впливають на результат\n⇒ Результуючий тип функції: int",
                      size=11, fill="#f0fdf4", stroke=FIELD))

    out.append(fitbox(480, 130, 470, 95,
                      "Виклик get_representation(3.14) [T = double]:\n\n• Активна гілка 2 ⇒ повертає 3.64 (double)\n• Гілки 1 і 3 відкинуті й не впливають на результат\n⇒ Результуючий тип функції: double",
                      size=11, fill="#f0fdf4", stroke=FIELD))

    out.append(fitbox(480, 240, 470, 95,
                      "Виклик get_representation(\"text\") [T = const char*]:\n\n• Активна гілка 3 ⇒ повертає об'єкт std::string\n• Гілки 1 і 2 відкинуті й не викликають множення тексту\n⇒ Результуючий тип функції: std::string",
                      size=11, fill="#f0fdf4", stroke=FIELD))

    render(os.path.join(IMG, 'return-type-deduction.svg'), W, H, *out,
           title="Виведення типу повернення auto при умовному компілюванні")


if __name__ == "__main__":
    fig_ast_pruning()
    fig_tag_sfinae_comparison()
    fig_dependent_false()
    fig_return_deduction()
    print("Всі фігури успішно згенеровано.")

# -*- coding: utf-8 -*-
"""Фігури до теми «Що приніс C++17» (reference/cpp-standards/releases/cpp17-features)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Палітра
LANG_FILL = "#eef6fc"
LANG_STROKE = "#1d70b8"
TMP_FILL = "#f3f0fc"
TMP_STROKE = "#6f42c1"
MEM_FILL = "#fdf2e9"
MEM_STROKE = "#d35400"
STL_FILL = "#eafaf1"
STL_STROKE = "#27ae60"
ERR_FILL = "#fdf0ed"
ERR_STROKE = "#d4351c"
BOX_FILL = "#f8f9fa"
BOX_STROKE = "#505a5f"

# ── 1. Карта ключових стовпів C++17 ───────────────────────────────────────────
def fig_cpp17_feature_map():
    W, H = 940, 520
    f = []

    f.append(text(W / 2, 32, "Архітектурні стовпи стандарту C++17 (ISO/IEC 14882:2017)", size=16, bold=True, color="#0b0c0c"))

    # Центральний вузол
    b_center, wc, hc = textbox(W / 2, 85, ["C++17", "Практичність, ергономіка", "та словникові типи"], size=13, fill="#ffffff", stroke=LINE, sw=2, min_w=200, bold=True)
    f.append(b_center)

    # 4 основні сектори
    # 1. Синтаксична ергономіка (ліворуч зверху)
    b1, w1, h1 = textbox(210, 200, [
        "Синтаксична ергономіка ядра",
        "• auto [a, b] = ... (Structured Bindings)",
        "• if / switch (init; condition)",
        "• inline-змінні для заголовочних файлів",
        "• Спрощені вкладені простори назв A::B::C"
    ], size=12, fill=LANG_FILL, stroke=LANG_STROKE, min_w=320)

    # 2. Метапрограмування й шаблони (праворуч зверху)
    b2, w2, h2 = textbox(730, 200, [
        "Шаблони та метапрограмування",
        "• if constexpr (усунення гілок без SFINAE)",
        "• Fold Expressions: (... + args)",
        "• CTAD: виведення аргументів класів",
        "• auto в нетипових параметрах шаблону"
    ], size=12, fill=TMP_FILL, stroke=TMP_STROKE, min_w=320)

    # 3. Модель пам'яті та об'єкти (ліворуч знизу)
    b3, w3, h3 = textbox(210, 390, [
        "Життєвий цикл і матеріалізація",
        "• Гарантований пропуск копіювання (RVO)",
        "• prvalue як інструкція ініціалізації",
        "• Повернення non-movable типів за значенням",
        "• Строгий порядок обчислення виразів"
    ], size=12, fill=MEM_FILL, stroke=MEM_STROKE, min_w=320)

    # 4. Словникові типи та підсистеми STL (праворуч знизу)
    b4, w4, h4 = textbox(730, 390, [
        "Стандартна бібліотека (STL)",
        "• std::optional, std::variant, std::any",
        "• std::string_view (безкоштовний зріз)",
        "• std::filesystem (кросплатформні файли)",
        "• <execution>: паралельні алгоритми STL"
    ], size=12, fill=STL_FILL, stroke=STL_STROKE, min_w=320)

    f += [b1, b2, b3, b4]

    # Зв'язувальні стрілки від центру
    f.append(arrow(W / 2 - 80, 110, 210 + 60, 200 - h1 / 2, color=LANG_STROKE))
    f.append(arrow(W / 2 + 80, 110, 730 - 60, 200 - h2 / 2, color=TMP_STROKE))
    f.append(arrow(W / 2 - 80, 115, 210 + 60, 390 - h3 / 2, color=MEM_STROKE))
    f.append(arrow(W / 2 + 80, 115, 730 - 60, 390 - h4 / 2, color=STL_STROKE))

    f.append(text(W / 2, 490, "Стандарт C++17 усунув щоденний шаблонний шум і дав уніфіковані типи для надійного системного коду", size=12, color=MUTED))

    render(os.path.join(IMG, "cpp17-feature-map.svg"), W, H, *f, title="Архітектурні стовпи стандарту C++17")


# ── 2. Гарантоване вилучення копіювання: C++11/14 vs C++17 ─────────────────────
def fig_copy_elision_prvalue():
    W, H = 920, 430
    f = []

    f.append(text(W / 2, 28, "Еволюція ініціалізації: Опціональне RVO (C++11/14) vs Матеріалізація prvalue (C++17)", size=15, bold=True, color="#0b0c0c"))

    # Ліва колонка: C++11/14
    f.append(text(230, 65, "C++11 / C++14: prvalue створює тимчасовий об'єкт", size=13, bold=True, color=ERR_STROKE))
    b11_1, w11_1, h11_1 = textbox(230, 120, ["Функція повертає значення", "Widget make() { return Widget(); }"], size=11, fill=BOX_FILL, stroke=BOX_STROKE, min_w=340)
    b11_2, w11_2, h11_2 = textbox(230, 205, ["Створення тимчасового об'єкта на стеку", "Обов'язкова наявність Widget(Widget&&)!"], size=11, fill=ERR_FILL, stroke=ERR_STROKE, min_w=340)
    b11_3, w11_3, h11_3 = textbox(230, 295, ["Ініціалізація цільової змінної", "Widget w = make(); // RVO є лише оптимізацією"], size=11, fill=BOX_FILL, stroke=BOX_STROKE, min_w=340)
    b11_res, _, _ = textbox(230, 375, ["✗ Non-movable типи повертати за значенням ЗАБОРОНЕНО"], size=11, fill=ERR_FILL, stroke=ERR_STROKE, min_w=340, bold=True)
    f += [b11_1, b11_2, b11_3, b11_res]
    f.append(arrow(230, 120 + h11_1 / 2, 230, 205 - h11_2 / 2, color=ERR_STROKE))
    f.append(arrow(230, 205 + h11_2 / 2, 230, 295 - h11_3 / 2, color=ERR_STROKE))
    f.append(arrow(230, 295 + h11_3 / 2, 230, 375 - 18, color=ERR_STROKE))

    # Розділювач
    f.append(line(460, 50, 460, 400, color="#d1d5db", sw=1.5, dash="4,4"))

    # Права колонка: C++17
    f.append(text(690, 65, "C++17: prvalue є рецептом ініціалізації (без копій)", size=13, bold=True, color=STL_STROKE))
    b17_1, w17_1, h17_1 = textbox(690, 120, ["Функція повертає prvalue вираз", "Widget make() { return Widget(); }"], size=11, fill=BOX_FILL, stroke=BOX_STROKE, min_w=340)
    b17_2, w17_2, h17_2 = textbox(690, 205, ["Пряме передавання адреси призначення", "Ніякого проміжного об'єкта не існує!"], size=11, fill=STL_FILL, stroke=STL_STROKE, min_w=340)
    b17_3, w17_3, h17_3 = textbox(690, 295, ["Конструювання прямо в пам'яті w", "Конструктор переміщення НЕ потрібен"], size=11, fill=STL_FILL, stroke=STL_STROKE, min_w=340)
    b17_res, _, _ = textbox(690, 375, ["✓ Гарантоване конструювання за місцем (Non-movable дозволені)"], size=11, fill=STL_FILL, stroke=STL_STROKE, min_w=340, bold=True)
    f += [b17_1, b17_2, b17_3, b17_res]
    f.append(arrow(690, 120 + h17_1 / 2, 690, 205 - h17_2 / 2, color=STL_STROKE))
    f.append(arrow(690, 205 + h17_2 / 2, 690, 295 - h17_3 / 2, color=STL_STROKE))
    f.append(arrow(690, 295 + h17_3 / 2, 690, 375 - 18, color=STL_STROKE))

    render(os.path.join(IMG, "copy-elision-prvalue.svg"), W, H, *f, title="Гарантоване вилучення копіювання в C++17")


# ── 3. Розміщення словникових типів у пам'яті ──────────────────────────────────
def fig_vocabulary_types_layout():
    W, H = 940, 480
    f = []

    f.append(text(W / 2, 28, "Розміщення словникових типів C++17 у пам'яті (Memory Layout)", size=15, bold=True, color="#0b0c0c"))

    # 1. std::optional<T>
    f.append(text(230, 68, "std::optional<T>", size=13, bold=True, color=LANG_STROKE))
    f.append(rect(60, 85, 340, 105, fill=LANG_FILL, stroke=LANG_STROKE, rx=6))
    f.append(rect(75, 105, 90, 65, fill="#ffffff", stroke=LANG_STROKE, rx=4))
    f.append(text(120, 135, "bool", size=12, bold=True, color=LANG_STROKE))
    f.append(text(120, 155, "engaged", size=10, color=MUTED))
    f.append(rect(170, 105, 50, 65, fill="#e5e7eb", stroke="#9ca3af", rx=4))
    f.append(text(195, 140, "pad", size=10, color=MUTED))
    f.append(rect(225, 105, 160, 65, fill="#ffffff", stroke=LANG_STROKE, rx=4))
    f.append(text(305, 135, "Зберігання T", size=12, bold=True, color=LANG_STROKE))
    f.append(text(305, 155, "aligned_storage[sizeof(T)]", size=10, color=MUTED))
    f.append(text(230, 205, "Стек: sizeof(T) + align padding (нуль динамічної пам'яті)", size=11, color=INK))

    # 2. std::variant<A, B, C>
    f.append(text(710, 68, "std::variant<A, B, C>", size=13, bold=True, color=TMP_STROKE))
    f.append(rect(540, 85, 340, 105, fill=TMP_FILL, stroke=TMP_STROKE, rx=6))
    f.append(rect(555, 105, 90, 65, fill="#ffffff", stroke=TMP_STROKE, rx=4))
    f.append(text(600, 135, "size_t", size=12, bold=True, color=TMP_STROKE))
    f.append(text(600, 155, "type_index", size=10, color=MUTED))
    f.append(rect(650, 105, 40, 65, fill="#e5e7eb", stroke="#9ca3af", rx=4))
    f.append(text(670, 140, "pad", size=10, color=MUTED))
    f.append(rect(695, 105, 170, 65, fill="#ffffff", stroke=TMP_STROKE, rx=4))
    f.append(text(780, 135, "union { A; B; C; }", size=12, bold=True, color=TMP_STROKE))
    f.append(text(780, 155, "max(sizeof(A, B, C))", size=10, color=MUTED))
    f.append(text(710, 205, "Стек: типобезпечний tagged union без виділення купи", size=11, color=INK))

    # 3. std::any (Small Object Optimization)
    f.append(text(230, 255, "std::any (SOO механізм)", size=13, bold=True, color=MEM_STROKE))
    f.append(rect(60, 275, 340, 120, fill=MEM_FILL, stroke=MEM_STROKE, rx=6))
    f.append(rect(75, 295, 100, 75, fill="#ffffff", stroke=MEM_STROKE, rx=4))
    f.append(text(125, 330, "type_info*", size=11, bold=True, color=MEM_STROKE))
    f.append(text(125, 350, "vtable / RTTI", size=10, color=MUTED))
    f.append(rect(180, 295, 205, 75, fill="#ffffff", stroke=MEM_STROKE, rx=4))
    f.append(text(282, 325, "Внутрішній буфер (≤ 24 B)", size=11, bold=True, color=MEM_STROKE))
    f.append(text(282, 345, "або вказівник на купу (heap ptr)", size=10, color=ERR_STROKE))
    f.append(text(230, 410, "Стирання типу: SOO для малих об'єктів, heap для великих", size=11, color=INK))

    # 4. std::string_view
    f.append(text(710, 255, "std::string_view", size=13, bold=True, color=STL_STROKE))
    f.append(rect(540, 275, 340, 120, fill=STL_FILL, stroke=STL_STROKE, rx=6))
    f.append(rect(560, 305, 140, 60, fill="#ffffff", stroke=STL_STROKE, rx=4))
    f.append(text(630, 332, "const char* data", size=12, bold=True, color=STL_STROKE))
    f.append(text(630, 350, "8 байтів (вказівник)", size=10, color=MUTED))
    f.append(rect(710, 305, 150, 60, fill="#ffffff", stroke=STL_STROKE, rx=4))
    f.append(text(785, 332, "size_t length", size=12, bold=True, color=STL_STROKE))
    f.append(text(785, 350, "8 байтів (розмір)", size=10, color=MUTED))
    f.append(text(710, 410, "16 байтів на стеку: нуль алокацій, O(1) зрізи рядків", size=11, color=INK))

    f.append(text(W / 2, 455, "Словникові типи C++17 мають строгу семантику значень і контрольовану ціну розміщення", size=12, color=MUTED))

    render(os.path.join(IMG, "vocabulary-types-layout.svg"), W, H, *f, title="Розміщення словникових типів C++17 у пам'яті")


# ── 4. Усунення неактивних гілок в if constexpr ────────────────────────────────
def fig_if_constexpr_branch_elimination():
    W, H = 920, 430
    f = []

    f.append(text(W / 2, 28, "Компіляція розгалуження: Звичайний if vs if constexpr", size=15, bold=True, color="#0b0c0c"))

    # Ліворуч: звичайний if
    f.append(text(230, 65, "Звичайний if (runtime-перевірка)", size=13, bold=True, color=ERR_STROKE))
    b_if1, _, _ = textbox(230, 120, ["Синтаксичний аналіз шаблону", "template <typename T> void process(T v)"], size=11, fill=BOX_FILL, stroke=BOX_STROKE, min_w=340)
    b_if2, _, _ = textbox(230, 205, ["Обидві гілки інстанціюються", "if (std::is_integral_v<T>) v.clear(); else v++;"], size=11, fill=ERR_FILL, stroke=ERR_STROKE, min_w=340)
    b_if3, _, _ = textbox(230, 295, ["Помилка компіляції для непідтримуваного T", "T = int: помилка 'int no member clear()'"], size=11, fill=ERR_FILL, stroke=ERR_STROKE, min_w=340)
    b_if_res, _, _ = textbox(230, 375, ["Потрібні складні SFINAE / std::enable_if перевантаження"], size=11, fill=BOX_FILL, stroke=BOX_STROKE, min_w=340)
    f += [b_if1, b_if2, b_if3, b_if_res]
    f.append(arrow(230, 140, 230, 185, color=ERR_STROKE))
    f.append(arrow(230, 225, 230, 275, color=ERR_STROKE))
    f.append(arrow(230, 315, 230, 355, color=ERR_STROKE))

    # Розділювач
    f.append(line(460, 50, 460, 400, color="#d1d5db", sw=1.5, dash="4,4"))

    # Праворуч: if constexpr
    f.append(text(690, 65, "if constexpr (compile-time вибір)", size=13, bold=True, color=STL_STROKE))
    b_cf1, _, _ = textbox(690, 120, ["Обчислення константного виразу", "if constexpr (std::is_integral_v<T>)"], size=11, fill=BOX_FILL, stroke=BOX_STROKE, min_w=340)
    b_cf2, _, _ = textbox(690, 205, ["Відкидання хибної гілки компілятором", "Хибна гілка НЕ інстанціюється для типу T!"], size=11, fill=STL_FILL, stroke=STL_STROKE, min_w=340)
    b_cf3, _, _ = textbox(690, 295, ["Чиста генерація AST лише для істинної гілки", "Жодних синтаксичних конфліктів у бінарнику"], size=11, fill=STL_FILL, stroke=STL_STROKE, min_w=340)
    b_cf_res, _, _ = textbox(690, 375, ["✓ Просте монолітне тіло функції без дублювання перевантажень"], size=11, fill=STL_FILL, stroke=STL_STROKE, min_w=340, bold=True)
    f += [b_cf1, b_cf2, b_cf3, b_cf_res]
    f.append(arrow(690, 140, 690, 185, color=STL_STROKE))
    f.append(arrow(690, 225, 690, 275, color=STL_STROKE))
    f.append(arrow(690, 315, 690, 355, color=STL_STROKE))

    render(os.path.join(IMG, "if-constexpr-branch-elimination.svg"), W, H, *f, title="Усунення неактивних гілок у if constexpr")


if __name__ == "__main__":
    fig_cpp17_feature_map()
    fig_copy_elision_prvalue()
    fig_vocabulary_types_layout()
    fig_if_constexpr_branch_elimination()
    print("All figures generated successfully.")

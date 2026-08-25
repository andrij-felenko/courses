# -*- coding: utf-8 -*-
"""Фігури до теми «std::type_traits»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_taxonomy():
    """Класифікація категорій і властивостей std::type_traits."""
    W = 1040
    M = 20
    head = ["Категорія трейтів", "Приклади метафункцій у <type_traits>", "Що саме перевіряє або змінює"]
    cols = [240, 420, 340]
    rows = [
        ["Первинні категорії\n(Primary Categories)",
         "is_void, is_integral, is_pointer,\nis_class, is_union, is_function",
         "14 взаємовиключних категорій,\nякі покривають абсолютно всі типи C++"],
        ["Складені категорії\n(Composite Categories)",
         "is_reference, is_arithmetic,\nis_object, is_compound, is_scalar",
         "Об'єднання первинних категорій\nдля зручних узагальнених перевірок"],
        ["Властивості та відносини\n(Properties & Relations)",
         "is_const, is_trivially_copyable,\nis_same<T, U>, is_base_of<Base, Derived>",
         "Перевірка кваліфікаторів, вимог до пам'яті\nта ієрархічних зв'язків між типами"],
        ["Модифікатори типів\n(Type Transformations)",
         "remove_const_t, remove_reference_t,\ndecay_t, add_lvalue_reference_t",
         "Трансформація типу: зняття const/ref,\nрозпад масивів і додавання посилань"]
    ]
    HH, RH, GAP = 54, 78, 6
    H = 50 + HH + len(rows) * RH + 24
    out = []

    x = M
    for i, c in enumerate(cols):
        out.append(fitbox(x, 50, c - GAP, HH - GAP, head[i], size=14, bold=True, fill="#e8edf3"))
        x += c

    y = 50 + HH
    for ri, r in enumerate(rows):
        x = M
        for i, cell in enumerate(r):
            fill = "#eef4ff" if i == 0 else "#f7f9fb"
            out.append(fitbox(x, y, cols[i] - GAP, RH - GAP, cell, size=13, bold=(i == 0), fill=fill))
            x += cols[i]
        y += RH

    render(os.path.join(IMG, 'traits-taxonomy.svg'), W, H, *out,
           title="Класифікація категорій і властивостей std::type_traits")


def fig_metafunction_pipeline():
    """Анатомія метафункції типу (Type Trait Meta-function)."""
    W, H = 960, 360
    out = []

    b1, w1, h1 = textbox(200, 110, ["Аргумент-тип T", "const std::string&"], size=15, pad=16, bold=True)
    out.append(b1)
    out.append(text(200, 110 - h1 / 2 - 16, "Вхідний тип у метафункцію", size=13, color=MUTED))

    b2, w2, h2 = textbox(480, 110,
                         ["template<class T>", "struct is_lvalue_reference", ": false_type {};",
                          "/* спеціалізація для T& */"],
                         size=14, pad=16, fill="#eef4ff", stroke=NEG)
    out.append(b2)
    out.append(text(480, 110 - h2 / 2 - 16, "Механізм часткової спеціалізації шаблону", size=13, color=MUTED))

    b3, w3, h3 = textbox(770, 110, ["Результат обчислення", "value = true", "type = true_type"], size=14, pad=16, fill="#eaf7ee", stroke=POS)
    out.append(b3)
    out.append(text(770, 110 - h3 / 2 - 16, "Результат під час компіляції", size=13, color=MUTED))

    out.append(arrow(200 + w1 / 2 + 10, 110, 480 - w2 / 2 - 10, 110))
    out.append(arrow(480 + w2 / 2 + 10, 110, 770 - w3 / 2 - 10, 110))

    y = 250
    b_v, _, _ = textbox(300, y, ["C++17 Variable Template Helper:", "is_lvalue_reference_v<T>", "⇒ constexpr bool"], size=13, pad=12, fill="#fff8e1", stroke="#b8860b")
    b_t, _, _ = textbox(660, y, ["C++14 Alias Template Helper:", "remove_reference_t<T>", "⇒ using type"], size=13, pad=12, fill="#fff8e1", stroke="#b8860b")
    out.append(b_v)
    out.append(b_t)

    out.append(text(W / 2, 330, "Метафункція перетворює типи або значення під час компіляції через спадкування від integral_constant", size=13, color=MUTED))

    render(os.path.join(IMG, 'meta-function-pipeline.svg'), W, H, *out,
           title="Анатомія метафункції типу (Type Trait Meta-function)")


def fig_evolution():
    """Еволюція розгалуження за трейтами в коді C++."""
    W = 1000
    M = 20
    cols = [160, 240, 310, 250]
    head = ["Ера стандарту", "Підхід розгалуження", "Конструкція в коді", "Ефективність і прочитання"]
    rows = [
        ["C++11 Tag", "Tag Dispatching", "overload(T val, std::true_type)\noverload(T val, std::false_type)", "Додаткові перевантаження,\nінтроспекція через типи-теги"],
        ["C++11 SFINAE", "std::enable_if_t", "template<typename T,\n  std::enable_if_t<is_copy_v<T>>* = nullptr>", "Складний синтаксис,\nважке читання помилок збірки"],
        ["C++17 Branch", "if constexpr", "if constexpr (std::is_trivially_copyable_v<T>) {\n  std::memcpy(...);\n}", "Один код усередині функції,\nневибрана гілка не компілюється"],
        ["C++20 Concept", "requires-clause", "template<typename T>\nrequires std::is_trivially_copyable_v<T>\nvoid process(T val)", "Найчистіші повідомлення помилок,\nдекларативне обмеження API"]
    ]
    HH, RH, GAP = 54, 84, 6
    H = 50 + HH + len(rows) * RH + 24
    out = []

    x = M
    for i, c in enumerate(cols):
        out.append(fitbox(x, 50, c - GAP, HH - GAP, head[i], size=14, bold=True, fill="#e8edf3"))
        x += c

    y = 50 + HH
    for ri, r in enumerate(rows):
        x = M
        for i, cell in enumerate(r):
            fill = "#eef4ff" if i == 0 else "#f7f9fb"
            out.append(fitbox(x, y, cols[i] - GAP, RH - GAP, cell, size=13, bold=(i == 0), fill=fill))
            x += cols[i]
        y += RH

    render(os.path.join(IMG, 'sfinae-vs-ifconstexpr-evolution.svg'), W, H, *out,
           title="Еволюція розгалуження за трейтами в коді C++")


def fig_decay_flow():
    """Етапи трансформації типів у std::decay."""
    W, H = 980, 350
    out = []

    b_in, w_in, _ = textbox(150, 110, ["Вхідний тип:", "const int[5]", "або const int&", "або void(int)"], size=13, pad=12, fill="#fdecea", stroke=POS)
    b_s1, w_s1, _ = textbox(380, 110, ["1. remove_reference", "const int[5]", "const int", "void(int)"], size=13, pad=12)
    b_s2, w_s2, _ = textbox(620, 110, ["2. Array / Func Decay", "const int*", "const int", "void(*)(int)"], size=13, pad=12)
    b_s3, w_s3, _ = textbox(850, 110, ["3. Stripping CV", "const int*", "int", "void(*)(int)"], size=13, pad=12, fill="#eaf7ee", stroke=POS)

    out.append(b_in)
    out.append(b_s1)
    out.append(b_s2)
    out.append(b_s3)

    out.append(arrow(150 + w_in / 2 + 6, 110, 380 - w_s1 / 2 - 6, 110))
    out.append(arrow(380 + w_s1 / 2 + 6, 110, 620 - w_s2 / 2 - 6, 110))
    out.append(arrow(620 + w_s2 / 2 + 6, 110, 850 - w_s3 / 2 - 6, 110))

    b_note, _, _ = textbox(W / 2, 260,
                           ["Правило std::decay імітує передачу за значенням у функцію:",
                            "масиви стають вказівниками, функції — вказівниками на функції,",
                            "а для звичайних типів видаляються посилання та зовнішні const/volatile"],
                           size=13, pad=14, fill="#eef4ff", stroke=NEG)
    out.append(b_note)

    render(os.path.join(IMG, 'decay-transformation-flow.svg'), W, H, *out,
           title="Етапи трансформації типів у std::decay")


fig_taxonomy()
fig_metafunction_pipeline()
fig_evolution()
fig_decay_flow()
print("ok")

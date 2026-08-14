# -*- coding: utf-8 -*-
"""Фігури до теми «Інвалідація ітераторів: механізми, правила та захист пам'яті» (reference/cpp-standards/library)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# ── 1. Реалокація std::vector та масова інвалідація ──────────────────────────
def fig_vector_reallocation():
    W, H = 920, 420
    f = []

    # Заголовок блоку 1: Старий буфер
    f.append(text(220, 40, "1. Буфер до push_back() (size = 4, capacity = 4)", size=13, bold=True, color=INK))
    
    # Осередки старого буфера
    old_data = ["elem 0", "elem 1", "elem 2", "elem 3"]
    for i, val in enumerate(old_data):
        x = 60 + i * 85
        f.append(rect(x, 60, 80, 50, fill="#f4f6f8", stroke=LINE))
        f.append(text(x + 40, 90, val, size=12, bold=True, color=INK))

    # Ітератор, що вказує на elem 1
    f.append(arrow(185, 160, 185, 115, color=POS, sw=2))
    f.append(text(185, 180, "it (вказує на elem 1)", size=12, bold=True, color=POS))
    f.append(text(185, 198, "Адреса в RAM: 0x1008", size=11, color=MUTED))

    # Заголовок блоку 2: Операція реалокації
    f.append(text(460, 220, "push_back(elem 4) викликає виділення нового буфера (capacity = 8)", size=13, bold=True, color=POS))
    f.append(arrow(460, 230, 460, 260, color=POS, sw=2))

    # Заголовок блоку 3: Новий буфер
    f.append(text(460, 280, "2. Новий буфер у купі (адреса 0x5000) після переміщення даних", size=13, bold=True, color=FIELD))

    new_data = ["elem 0", "elem 1", "elem 2", "elem 3", "elem 4", "порожньо", "порожньо", "порожньо"]
    for i, val in enumerate(new_data):
        x = 50 + i * 95
        fill_c = "#eaf7ee" if i <= 4 else "#ffffff"
        stroke_c = FIELD if i <= 4 else MUTED
        text_c = INK if i <= 4 else MUTED
        f.append(rect(x, 300, 90, 50, fill=fill_c, stroke=stroke_c))
        f.append(text(x + 45, 330, val, size=11, bold=True if i <= 4 else False, color=text_c))

    # Перекреслений старий ітератор (висячий вказівник)
    f.append(textbox(185, 385, "it стає висячим вказівником!\nСтарий буфер 0x1000 звільнено через delete[]", size=11, pad=8, fill="#fdecea", stroke=POS)[0])

    render(os.path.join(IMG, "vector-reallocation.svg"), W, H, *f,
           title="Динамічна реалокація std::vector та повна інвалідація всіх ітераторів")


# ── 2. Зсув елементів при видаленні/вставці у середовище std::vector ─────────
def fig_vector_shift_invalidation():
    W, H = 920, 380
    f = []

    f.append(text(460, 35, "Видалення елемента erase(it_B) з середини std::vector", size=14, bold=True, color=INK))

    # До видалення
    f.append(text(150, 80, "До видалення:", size=13, bold=True, color=INK))
    before_elems = ["A [0]", "B [1]", "C [2]", "D [3]", "E [4]"]
    for i, val in enumerate(before_elems):
        x = 50 + i * 110
        fill_c = "#fdecea" if i == 1 else FILL
        stroke_c = POS if i == 1 else LINE
        f.append(rect(x, 100, 100, 45, fill=fill_c, stroke=stroke_c))
        f.append(text(x + 50, 127, val, size=12, bold=True, color=INK))

    # Позначення ітератора на C
    f.append(arrow(325, 185, 325, 150, color=NEG, sw=2))
    f.append(text(325, 205, "it_C (вказував на [2])", size=11, bold=True, color=NEG))

    # Після видалення та зсуву
    f.append(text(150, 240, "Після erase(B) — лівий зсув елементів C, D, E:", size=13, bold=True, color=POS))
    after_elems = ["A [0]", "C [1]", "D [2]", "E [3]", "--- [4]"]
    for i, val in enumerate(after_elems):
        x = 50 + i * 110
        fill_c = "#eaf7ee" if i in [1, 2, 3] else FILL
        stroke_c = FIELD if i in [1, 2, 3] else LINE
        f.append(rect(x, 260, 100, 45, fill=fill_c, stroke=stroke_c))
        f.append(text(x + 50, 287, val, size=12, bold=True, color=INK))

    # Пояснення інвалідації it_C
    f.append(textbox(325, 340, "it_C збережає стару адресу ітерованої комірки,\nале тепер там лежить D замість C (зміщення індексу й даних)", size=11, pad=8, fill="#fdecea", stroke=POS)[0])

    render(os.path.join(IMG, "vector-shift-invalidation.svg"), W, H, *f,
           title="Зсув елементів у пам'яті при видаленні з середини вектора")


# ── 3. Архітектура std::deque ───────────────────────────────────────────────
def fig_deque_map_and_blocks():
    W, H = 920, 400
    f = []

    f.append(text(460, 35, "Архітектура std::deque: розрив між Map-ітераторами та сторінками даних", size=14, bold=True, color=INK))

    # Центральний масив покажчиків Map
    f.append(text(180, 80, "Центральний вектор Map (покажчики на блоки)", size=12, bold=True, color=INK))
    for i in range(5):
        x = 60 + i * 70
        fill_c = "#eaf7ee" if 1 <= i <= 3 else FILL
        f.append(rect(x, 100, 65, 40, fill=fill_c, stroke=LINE))
        f.append(text(x + 32, 125, f"Block {i}", size=11, color=INK))

    # Сторінки даних у купі
    f.append(text(650, 80, "Незалежні сторінки даних у RAM (фіксований розмір)", size=12, bold=True, color=FIELD))
    
    pages = [
        ("Block 1 Data", ["val 0", "val 1", "val 2"]),
        ("Block 2 Data", ["val 3", "val 4", "val 5"]),
        ("Block 3 Data", ["val 6", "val 7", "val 8"])
    ]

    for p_idx, (p_title, p_vals) in enumerate(pages):
        py = 110 + p_idx * 80
        f.append(rect(520, py, 340, 60, fill="#f4f6f8", stroke=FIELD, sw=1.5))
        f.append(text(580, py + 35, p_title, size=11, bold=True, color=FIELD))
        for v_idx, v_name in enumerate(p_vals):
            vx = 660 + v_idx * 65
            f.append(rect(vx, py + 12, 60, 36, fill="#ffffff", stroke=LINE))
            f.append(text(vx + 30, py + 34, v_name, size=10, color=INK))

    # Зв'язки від Map до сторінок
    f.append(arrow(162, 140, 520, 140, color=FIELD))
    f.append(arrow(232, 140, 520, 220, color=FIELD))
    f.append(arrow(302, 140, 520, 300, color=FIELD))

    # Вердикт нижче
    f.append(textbox(460, 365, "Вставка спереду/ззаду перевиділяє Map → ітератори deque (покажчики у Map) ІНВАЛІДУЮТЬСЯ,\nпроте сторінки даних не рухаються → покажчики T* та посилання T& залишаються 100% ДІЙСНИМИ!", size=11, pad=8, fill="#eaf7ee", stroke=FIELD)[0])

    render(os.path.join(IMG, "deque-map-and-blocks.svg"), W, H, *f,
           title="Архітектура std::deque: розрив між стійкістю покажчиків та інвалідацією ітератора")


# ── 4. Спектр стійкості ітераторів ──────────────────────────────────────────
def fig_invalidation_spectrum():
    W, H = 1040, 380
    f = []

    f.append(text(520, 35, "Класифікація контейнерів за гарантіями стабільності ітераторів", size=14, bold=True, color=INK))

    containers_info = [
        ("std::vector / string", "Слабка", "Реалокація нищить все", "Зсув інвалідує хвіст", "#fdecea", POS),
        ("std::deque", "Селективна", "Ітератори змінні", "Посилання T& дійсні 100%", "#fff8e7", "#d97706"),
        ("std::unordered_map", "Висока", "rehash() змінює ітератор", "Посилання T& незмінні", "#eef2ff", NEG),
        ("std::list / std::map", "Абсолютна", "Вставка без інвалідації", "Лише видалений вузол", "#eaf7ee", FIELD)
    ]

    for i, (name, tag, line1, line2, fill_c, stroke_c) in enumerate(containers_info):
        cx = 135 + i * 250
        content = f"{name}\n[{tag}]\n{line1}\n{line2}"
        b, w, h = textbox(cx, 160, content, size=11, pad=8, fill=fill_c, stroke=stroke_c, sw=1.8, rx=6, min_w=225)
        f.append(b)

    f.append(line(60, 290, 980, 290, color=MUTED, sw=2, dash="4,4"))
    f.append(text(140, 320, "← Вища швидкість кешу, менша стабільність адреси", size=11, color=MUTED))
    f.append(text(890, 320, "Нижча щільність RAM, вища стабільність адреси →", size=11, color=MUTED))

    render(os.path.join(IMG, "invalidation-spectrum.svg"), W, H, *f,
           title="Спектр стійкості ітераторів та посилань для різних сімейств контейнерів")


if __name__ == "__main__":
    fig_vector_reallocation()
    fig_vector_shift_invalidation()
    fig_deque_map_and_blocks()
    fig_invalidation_spectrum()
    print("Всі фігури для iterator-invalidation успішно згенеровано.")

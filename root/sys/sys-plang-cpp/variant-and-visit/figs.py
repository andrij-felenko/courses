# -*- coding: utf-8 -*-
"""Фігури до теми «std::variant та std::visit» (reference/cpp-standards/library/variant-and-visit)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Фігура 1: Растрове розпланування пам'яті std::variant ────────────────
def fig_variant_memory_layout():
    W, H = 920, 460
    f = []

    f.append(text(W / 2, 35, "Внутрішня структура пам'яті std::variant<int, std::string, double>", size=16, bold=True))

    # Секція А: Структура std::variant у пам'яті
    f.append(text(220, 80, "Суцільний блок пам'яті std::variant на стеку", size=13, bold=True, anchor="middle", color=INK))

    # Буфер пам'яті
    b_buf, w_buf, h_buf = textbox(220, 150, ["storage_type storage[max_size]", "sizeof = sizeof(std::string)", "alignas = alignof(std::string)"],
                                  size=12, pad=12, fill="#eef2ff", stroke=NEG, sw=1.8)
    f.append(b_buf)

    # Дискримінатор (індекс)
    b_idx, w_idx, h_idx = textbox(220, 250, ["size_t index_", "Значення: 0..N-1 або npos", "Визначає активний тип"],
                                  size=12, pad=12, fill="#fcf8e3", stroke=MUTED, sw=1.8)
    f.append(b_idx)

    # Вирівнювання (padding)
    b_pad, w_pad, h_pad = textbox(220, 340, ["Padding (вирівнювання)", "Забезпечує кордон вирівнювання", "типу для процесора"],
                                  size=12, pad=10, fill="#f4f6f8", stroke=LINE, sw=1.2)
    f.append(b_pad)

    # Загальний розмір
    f.append(rect(60, 395, 320, 35, fill="#eaf7ee", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(220, 417, "Загальний sizeof = max(sizeof(T_i)) + sizeof(index_) + padding", size=11.5, color=FIELD, bold=True))

    # Секція Б: Активна альтернатива та перекриття
    f.append(text(670, 80, "Варіанти розміщення альтернатив у буфері", size=13, bold=True, anchor="middle", color=INK))

    # Варіант 0: int
    b_alt0, w_alt0, _ = textbox(670, 130, ["index_ = 0  ->  int (4 bytes)", "Решта буфера не ініціалізована (char storage)"],
                                size=12, pad=10, fill="#eaf7ee", stroke=FIELD, sw=1.5)
    f.append(b_alt0)

    # Варіант 1: std::string
    b_alt1, w_alt1, _ = textbox(670, 220, ["index_ = 1  ->  std::string (32 bytes)", "Займає весь буфер, викликається конструктор/деструктор"],
                                size=12, pad=10, fill="#eef2ff", stroke=NEG, sw=1.5)
    f.append(b_alt1)

    # Варіант 2: double
    b_alt2, w_alt2, _ = textbox(670, 310, ["index_ = 2  ->  double (8 bytes)", "Вирівнювання по 8 байт"],
                                size=12, pad=10, fill="#fcf8e3", stroke=MUTED, sw=1.5)
    f.append(b_alt2)

    # Варіант npos: valueless
    b_alt3, w_alt3, _ = textbox(670, 390, ["index_ = variant_npos  ->  valueless_by_exception", "Буфер не містить жодного об'єкта"],
                                size=12, pad=10, fill="#fdecea", stroke=POS, sw=1.5)
    f.append(b_alt3)

    # Стрілки зв'язку
    f.append(arrow(340, 150, 480, 130, color=FIELD, sw=1.5))
    f.append(arrow(340, 190, 480, 220, color=NEG, sw=1.5))
    f.append(arrow(340, 250, 480, 310, color=MUTED, sw=1.5))
    f.append(arrow(340, 280, 480, 390, color=POS, sw=1.5))

    f.append(text(W / 2, 448, "Гарантія безпеки: std::variant автоматично відстежує активний тип та керує його життєвим циклом", size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "variant-memory-layout.svg"), W, H, *f,
           title="Структура пам'яті std::variant")


# ── 2. Фігура 2: Диспетчеризація std::visit ──────────────────────────────────
def fig_visit_dispatch_matrix():
    W, H = 920, 460
    f = []

    f.append(text(W / 2, 35, "Матриця диспетчеризації std::visit(visitor, v1, v2) для двох варіантів", size=16, bold=True))

    # Джерело: 2 варіанти
    b_v1, w_v1, _ = textbox(160, 110, ["std::variant v1", "Альтернативи: A1, A2", "v1.index() ∈ {0, 1}"],
                            size=12, pad=10, fill="#eef2ff", stroke=NEG, sw=1.5)
    b_v2, w_v2, _ = textbox(160, 230, ["std::variant v2", "Альтернативи: B1, B2, B3", "v2.index() ∈ {0, 1, 2}"],
                            size=12, pad=10, fill="#fcf8e3", stroke=MUTED, sw=1.5)
    f += [b_v1, b_v2]

    # Таблиця покажчиків на функції (2D Jump Table)
    f.append(text(620, 85, "Двовимірна таблиця переходів 2 x 3 (Jump Table)", size=13, bold=True, anchor="middle", color=INK))

    # Сітка матриці 2х3
    grid_items = [
        ("A1, B1", 450, 130, "#eaf7ee", FIELD),
        ("A1, B2", 620, 130, "#eaf7ee", FIELD),
        ("A1, B3", 790, 130, "#eaf7ee", FIELD),
        ("A2, B1", 450, 210, "#eaf7ee", FIELD),
        ("A2, B2", 620, 210, "#eaf7ee", FIELD),
        ("A2, B3", 790, 210, "#eaf7ee", FIELD),
    ]

    for label, x, y, bg, border in grid_items:
        tb, _, _ = textbox(x, y, [f"func_ptr[{label}]", "Call: visitor(A_i, B_j)"],
                           size=11, pad=8, fill=bg, stroke=border, sw=1.2)
        f.append(tb)

    # Опис O(1) індексації
    b_lookup, w_lookup, _ = textbox(620, 310, [
        "Обчислення індексу в таблиці: matrix[v1.index()][v2.index()]",
        "Прямий виклик покажчика на функцію за один крок O(1)",
        "Жодних віртуальних таблиць (vtable) чи динамічного виділення"
    ], size=12, pad=12, fill="#f4f6f8", stroke=LINE, sw=1.5)
    f.append(b_lookup)

    # Стрілка від варіантів до таблиці
    f.append(arrow(270, 110, 380, 130, color=NEG, sw=1.8))
    f.append(arrow(270, 230, 380, 210, color=MUTED, sw=1.8))

    f.append(text(W / 2, 448, "Генерація матриці комбінацій відбувається на етапі компіляції з опрацюванням усіх перегрузок visitor", size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "visit-dispatch-matrix.svg"), W, H, *f,
           title="Матриця диспетчеризації std::visit")


# ── 3. Фігура 3: Перехід у стан valueless_by_exception ───────────────────────
def fig_valueless_state_transition():
    W, H = 920, 440
    f = []

    f.append(text(W / 2, 35, "Механіка переходу std::variant у стан valueless_by_exception", size=16, bold=True))

    # Стан 1: Валідний початковий об'єкт
    b_st1, w_st1, _ = textbox(160, 160, [
        "Стан 1: Валідний",
        "index_ = 0 (Тип T1)",
        "T1 в буфері ініціалізовано"
    ], size=12, pad=12, fill="#eaf7ee", stroke=FIELD, sw=1.8)

    # Крок операції присвоєння v = T2(...)
    b_op, w_op, _ = textbox(460, 100, [
        "Операція v = T2(args...)",
        "1. Деструктор ~T1() знищує старий об'єкт",
        "2. Конструктор T2(args...) створює новий"
    ], size=11.5, pad=10, fill="#fcf8e3", stroke=MUTED, sw=1.5)

    # Помилка: Виняток під час створення T2
    b_err, w_err, _ = textbox(460, 240, [
        "ПОМИЛКА: Виняток!",
        "T2(args...) кидає виняток",
        "T1 вже знищено, T2 не створено"
    ], size=11.5, pad=10, fill="#fdecea", stroke=POS, sw=1.8)

    # Стан 2: Невалідний стан valueless
    b_st2, w_st2, _ = textbox(760, 160, [
        "Стан 2: Valueless",
        "index_ = variant_npos",
        "valueless_by_exception() == true"
    ], size=12, pad=12, fill="#fdecea", stroke=POS, sw=1.8)

    f += [b_st1, b_op, b_err, b_st2]

    # Переходи
    f.append(arrow(260, 140, 360, 100, color=FIELD, sw=1.5))
    f.append(arrow(560, 100, 660, 140, color=FIELD, sw=1.5))
    f.append(arrow(460, 145, 460, 195, color=POS, sw=1.8))
    f.append(arrow(560, 240, 660, 180, color=POS, sw=1.8))

    # Нижній опис відновлення
    b_rec, w_rec, _ = textbox(460, 350, [
        "Шляхи відновлення з valueless стану:",
        "• v.emplace<T>(args...) — створення нового об'єкта в буфері без огляду на минулий стан",
        "• v = T(...) — присвоєння валідного значення через переміщення/копіювання"
    ], size=12, pad=12, fill="#eef2ff", stroke=NEG, sw=1.5)
    f.append(b_rec)

    f.append(text(W / 2, 428, "Виклик std::get або std::visit у стані valueless_by_exception викидає std::bad_variant_access", size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "valueless-state-transition.svg"), W, H, *f,
           title="Перехід у стан valueless_by_exception")


if __name__ == "__main__":
    fig_variant_memory_layout()
    fig_visit_dispatch_matrix()
    fig_valueless_state_transition()
    print("Figures generated successfully.")

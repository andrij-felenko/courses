# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми 'abstract-class'."""

import sys
import os

# 4 рівні вгору до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_vtable_pure_virtual():
    """Фігура 1: Будова пам'яті та таблиці vtable для абстрактного та конкретного класів."""
    w, h = 880, 480
    frags = []

    # Заголовок фігури
    frags.append(text(w / 2, 28, "Таблиця vtable: заглушка __cxa_pure_virtual та заміщення в нащадку", size=16, bold=True))

    # --- Ліва частина: Абстрактний клас Shape ---
    frags.append(text(210, 68, "Абстрактний базовий клас Shape", size=14, bold=True, color=POS))
    
    # Стан об'єкта Shape під час конструювання
    b1 = fitbox(40, 95, 340, 75, "Об'єкт Shape у пам'яті (під час Shape())\n[ vptr = &vtable for Shape ]\n[ id: uint32_t, color: uint32_t ]", size=12, fill="#fdf2e9", stroke=POS)
    frags.append(b1)

    # vtable для Shape
    frags.append(text(210, 205, "vtable for Shape (у сегменті .rodata)", size=13, bold=True))
    vt_shape_slots = [
        ("Слот 0: RTTI typeinfo for Shape", "#eaeded", INK, False),
        ("Слот 1: virtual void draw() = 0  ->  &__cxa_pure_virtual", "#fadbd8", POS, True),
        ("Слот 2: virtual double area() = 0  ->  &__cxa_pure_virtual", "#fadbd8", POS, True),
        ("Слот 3: virtual ~Shape()  ->  &Shape::~Shape()", "#e8f8f5", INK, False),
    ]
    y_off = 225
    for title, fill_c, text_c, is_b in vt_shape_slots:
        frags.append(fitbox(40, y_off, 340, 36, title, size=11, fill=fill_c, color=text_c, bold=is_b))
        y_off += 42

    # Заглушка runtime
    frags.append(fitbox(40, 415, 340, 45, "Системна заглушка __cxa_pure_virtual()\nДрук помилки у stderr -> std::terminate() / abort()", size=11, fill="#f2d7d5", stroke=POS, color=POS, bold=True))

    # Стрілки ліворуч
    frags.append(arrow(210, 170, 210, 220, color=POS))
    frags.append(arrow(210, 375, 210, 410, color=POS))

    # --- Розділювач ---
    frags.append(line(440, 60, 440, 465, color=MUTED, sw=1.2, dash="4,4"))

    # --- Права частина: Конкретний клас Circle ---
    frags.append(text(650, 68, "Конкретний похідний клас Circle", size=14, bold=True, color=FIELD))

    # Об'єкт Circle у пам'яті
    b2 = fitbox(480, 95, 360, 75, "Повний об'єкт Circle у пам'яті\n[ vptr = &vtable for Circle ]\n[ id, color (від Shape) | radius: double ]", size=12, fill="#eafaf1", stroke=FIELD)
    frags.append(b2)

    # vtable для Circle
    frags.append(text(660, 205, "vtable for Circle (у сегменті .rodata)", size=13, bold=True))
    vt_circle_slots = [
        ("Слот 0: RTTI typeinfo for Circle", "#eaeded", INK, False),
        ("Слот 1: virtual void draw() override  ->  &Circle::draw()", "#d5f5e3", FIELD, True),
        ("Слот 2: virtual double area() override  ->  &Circle::area()", "#d5f5e3", FIELD, True),
        ("Слот 3: virtual ~Circle() override  ->  &Circle::~Circle()", "#d5f5e3", INK, False),
    ]
    y_off = 225
    for title, fill_c, text_c, is_b in vt_circle_slots:
        frags.append(fitbox(480, y_off, 360, 36, title, size=11, fill=fill_c, color=text_c, bold=is_b))
        y_off += 42

    # Код конкретних методів
    frags.append(fitbox(480, 415, 360, 45, "Виконуваний машинний код (.text)\nCircle::draw() { ... }  та  Circle::area() { return π*r²; }", size=11, fill="#e8f8f5", stroke=FIELD, color=FIELD, bold=True))

    # Стрілки праворуч
    frags.append(arrow(660, 170, 660, 220, color=FIELD))
    frags.append(arrow(660, 375, 660, 410, color=FIELD))

    render(os.path.join(OUT_DIR, "vtable-pure-virtual.svg"), w, h, *frags)


def fig_construction_vptr_transition():
    """Фігура 2: Покроковий рух vptr під час конструювання та деструкції об'єкта."""
    w, h = 920, 460
    frags = []

    frags.append(text(w / 2, 26, "Еволюція покажчика vptr під час життєвого циклу об'єкта", size=16, bold=True))

    steps = [
        ("1. Виділення пам'яті", "Сирий буфер пам'яті\nsizeof(Derived) байтів\n(vptr ще не ініціалізовано)", "#f4f6f8", LINE, INK),
        ("2. Конструктор Base()", "Виконується Base::Base()\nvptr -> vtable for Base\n[Виклик pure virtual -> КРАХ!]", "#fadbd8", POS, POS),
        ("3. Конструктор Derived()", "Виконується Derived::Derived()\nvptr переписується на\nvtable for Derived", "#eafaf1", FIELD, FIELD),
        ("4. Зрілий об'єкт", "Об'єкт повністю готовий\nvptr -> vtable for Derived\nВсі віртуальні виклики безпечні", "#d5f5e3", FIELD, INK),
        ("5. Деструктор Derived()", "Виконується ~Derived()\nОчищення ресурсів нащадка\nvptr ще vtable for Derived", "#eafaf1", FIELD, INK),
        ("6. Деструктор Base()", "Виконується ~Base()\nvptr відкочується до\nvtable for Base [Знову небезпека!]", "#fadbd8", POS, POS),
    ]

    col_w = 270
    row_h = 160
    
    # Верхній ряд: кроки 1, 2, 3 (конструювання)
    frags.append(text(460, 65, "--- Фаза конструювання (знизу вгору по ієрархії) ---", size=13, bold=True, color=LINE))
    for i in range(3):
        title, body, fill_c, strk_c, txt_c = steps[i]
        x = 30 + i * (col_w + 35)
        y = 85
        frags.append(rect(x, y, col_w, row_h, fill=fill_c, stroke=strk_c, sw=1.8, rx=6))
        frags.append(text(x + col_w / 2, y + 25, title, size=13, bold=True, color=txt_c))
        frags.append(mtext(x + col_w / 2, y + 65, body, size=11, color=INK, lh=1.35))
        if i < 2:
            frags.append(arrow(x + col_w + 4, y + row_h / 2, x + col_w + 31, y + row_h / 2, color=LINE, sw=2))

    # Нижній ряд: кроки 4, 5, 6 (робота й деструкція)
    frags.append(text(460, 275, "--- Фаза роботи та деструкції (згори вниз по ієрархії) ---", size=13, bold=True, color=LINE))
    for i in range(3):
        title, body, fill_c, strk_c, txt_c = steps[i + 3]
        x = 30 + i * (col_w + 35)
        y = 295
        frags.append(rect(x, y, col_w, row_h, fill=fill_c, stroke=strk_c, sw=1.8, rx=6))
        frags.append(text(x + col_w / 2, y + 25, title, size=13, bold=True, color=txt_c))
        frags.append(mtext(x + col_w / 2, y + 65, body, size=11, color=INK, lh=1.35))
        if i < 2:
            frags.append(arrow(x + col_w + 4, y + row_h / 2, x + col_w + 31, y + row_h / 2, color=LINE, sw=2))

    render(os.path.join(OUT_DIR, "construction-vptr-transition.svg"), w, h, *frags)


def fig_abstract_class_vs_interface():
    """Фігура 3: Порівняльна структура абстрактного класу проти чистого інтерфейсу."""
    w, h = 880, 440
    frags = []

    frags.append(text(w / 2, 28, "Абстрактний клас (Is-A) проти Чистого інтерфейсу (Can-Do)", size=16, bold=True))

    # Ліва картка: Абстрактний клас
    x1, y1, cw, ch = 40, 60, 380, 355
    frags.append(rect(x1, y1, cw, ch, fill="#fdfefe", stroke=NEG, sw=2, rx=8))
    frags.append(rect(x1, y1, cw, 42, fill="#ebf5fb", stroke=NEG, sw=2, rx=8))
    frags.append(text(x1 + cw / 2, y1 + 26, "Абстрактний клас (Is-A / Різновид)", size=14, bold=True, color=NEG))

    left_rows = [
        "1. Семантика: «є спеціалізацією спільного предка»",
        "2. Стан: містить поля даних, змінні екземпляра",
        "3. Реалізація: містить конкретні методи, каркасні алгоритми",
        "4. Патерн: основа для Template Method / NVI ідіоми",
        "5. Зв'язування: одинарне спадкування (ієрархічне дерево)",
        "6. Конструктор: керує ініціалізацією спільного стану",
        "7. Ціна змін: зміна предка зачіпає всіх нащадків",
    ]
    ly = y1 + 68
    for row in left_rows:
        frags.append(text(x1 + 18, ly, row, size=11, color=INK, anchor="start"))
        ly += 41

    # Права картка: Інтерфейс
    x2, y2 = 460, 60
    frags.append(rect(x2, y2, cw, ch, fill="#fdfefe", stroke=FIELD, sw=2, rx=8))
    frags.append(rect(x2, y2, cw, 42, fill="#eafaf1", stroke=FIELD, sw=2, rx=8))
    frags.append(text(x2 + cw / 2, y2 + 26, "Інтерфейс / Протокол (Can-Do / Роль)", size=14, bold=True, color=FIELD))

    right_rows = [
        "1. Семантика: «володіє здатністю, грає роль у системі»",
        "2. Стан: не має стану (жодних нестатичних полів)",
        "3. Реалізація: лише сигнатури (або чисті допоміжні default)",
        "4. Патерн: основа для Strategy / Observer / DI",
        "5. Зв'язування: множинна реалізація без конфліктів стану",
        "6. Конструктор: відсутній (немає стану для ініціалізації)",
        "7. Ціна змін: легке підключення до неспоріднених типів",
    ]
    ry = y2 + 68
    for row in right_rows:
        frags.append(text(x2 + 18, ry, row, size=11, color=INK, anchor="start"))
        ry += 41

    render(os.path.join(OUT_DIR, "abstract-class-vs-interface.svg"), w, h, *frags)


def fig_devirtualization_final():
    """Фігура 4: Оптимізація девіртуалізації за допомогою final / sealed."""
    w, h = 880, 420
    frags = []

    frags.append(text(w / 2, 28, "Девіртуалізація: як final перетворює непрямий виклик на прямий", size=16, bold=True))

    # Верхній блок: Звичайний поліморфний виклик (без final)
    frags.append(rect(40, 60, 800, 160, fill="#fcf3cf", stroke="#f39c12", sw=1.5, rx=6))
    frags.append(text(60, 85, "1. Звичайний віртуальний метод (відкрита ієрархія, без final)", size=13, bold=True, color="#b7950b", anchor="start"))
    
    frags.append(fitbox(60, 105, 350, 95, "Код виклику:\nShape* s = get_shape();\ns->draw();\n(Компілятор не знає конкретний підтип)", size=11, fill="#ffffff", stroke="#f39c12"))
    
    frags.append(arrow(425, 150, 465, 150, color=LINE, sw=1.8))
    
    frags.append(fitbox(480, 105, 340, 95, "Машинний код (непрямий стрибок):\n1. mov (%rdi), %rax     [читання vptr]\n2. mov 0x08(%rax), %rdx  [читання слоту vtable]\n3. call *%rdx           [непрямий стрибок, без inline]", size=11, fill="#fdebd0", stroke=POS, color=POS, bold=True))

    # Нижній блок: Виклик з final / закритою ієрархією
    frags.append(rect(40, 240, 800, 160, fill="#d4efdf", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(60, 265, "2. Метод або клас позначено final / sealed (закрита точка розширення)", size=13, bold=True, color=FIELD, anchor="start"))

    frags.append(fitbox(60, 285, 350, 95, "Код виклику:\nCircle* c = get_circle();\nc->draw();  // Circle або draw() є final\n(Компілятор точно знає тип наперед)", size=11, fill="#ffffff", stroke=FIELD))

    frags.append(arrow(425, 330, 465, 330, color=FIELD, sw=1.8))

    frags.append(fitbox(480, 285, 340, 95, "Оптимізований код (Девіртуалізація):\n1. call Circle::draw   [прямий виклик]\nАБО вбудовування тіла (inline):\n// Тіло методу підставлено прямо на місце!", size=11, fill="#e8f8f5", stroke=FIELD, color=FIELD, bold=True))

    render(os.path.join(OUT_DIR, "devirtualization-final.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_vtable_pure_virtual()
    fig_construction_vptr_transition()
    fig_abstract_class_vs_interface()
    fig_devirtualization_final()
    print("Всі фігури згенеровано успішно у ./img/")

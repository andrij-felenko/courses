# -*- coding: utf-8 -*-
"""Фігури до теми «Вартість інстанціації шаблонів у C++»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_instantiation_pipeline():
    W, H = 1020, 360
    out = []

    out.append(text(W / 2, 30, "Конвеєр неявної інстанціації шаблону в компіляторі", size=18, bold=True))

    steps = [
        ("1. Виклик / Використання", ["Точка інстанціації (POI)", "Розпізнавання залежних імен", "Пошук ADL для аргументів"], "#eef4ff", MUTED),
        ("2. Підстановка типів", ["Заміна параметрів шаблону", "Перевірка SFINAE / Concepts", "Перевірка обмежень і типів"], "#fcf8e3", "#d6a928"),
        ("3. Синтез вузлів AST", ["Генерація спеціалізації", "Перевірка внутрішніх виразів", "Перевірка метапрограмування"], "#e8f8f5", POS),
        ("4. Генерація коду", ["Побудова машинного коду", "Поміщення в COMDAT-секцію", "Формування .o об'єкта"], "#fdecea", NEG)
    ]

    x_start = 40
    box_w = 200
    gap = 45
    y_center = 180

    for i, (title_text, items, bg_fill, border_color) in enumerate(steps):
        x = x_start + i * (box_w + gap)
        b, w, h = textbox(x + box_w / 2, y_center, [title_text] + items, size=13, pad=12, fill=bg_fill, stroke=border_color)
        out.append(b)

        if i < len(steps) - 1:
            arrow_start_x = x + box_w
            arrow_end_x = x + box_w + gap
            out.append(arrow(arrow_start_x + 4, y_center, arrow_end_x - 4, y_center))

    out.append(text(W / 2, 325, "Кожен новий тип аргументу повторює весь конвеєр з етапу 1 до етапу 4", size=13, color=MUTED))

    render(os.path.join(IMG, 'instantiation-pipeline.svg'), W, H, *out,
           title="Етапи обробки шаблону компілятором від використання до машинного коду")


def fig_comdat_deduplication():
    W, H = 1000, 420
    out = []

    out.append(text(W / 2, 30, "Дублювання інстанціації та згортання COMDAT-секцій лінкером", size=18, bold=True))

    tus = ["main.cpp", "network.cpp", "graphics.cpp"]
    tu_x = [180, 500, 820]
    y_tu = 90

    for i, tu in enumerate(tus):
        b, _, _ = textbox(tu_x[i], y_tu, [f"Одиниця компіляції: {tu}", "#include <vector>", "std::vector<int> v;"], size=13, pad=10, fill="#eef4ff", stroke=MUTED)
        out.append(b)

        b_comp, _, _ = textbox(tu_x[i], y_tu + 100, [f"Компілятор ({tu})", "Повне розгортання AST", "Генерація код vector<int>"], size=12, pad=10, fill="#fcf8e3", stroke="#d6a928")
        out.append(b_comp)

        out.append(arrow(tu_x[i], y_tu + 35, tu_x[i], y_tu + 75))

        b_obj, _, _ = textbox(tu_x[i], y_tu + 190, [f"Об'єктний файл (.o)", "Секція COMDAT:", "vector<int>::push_back"], size=12, pad=10, fill="#fdecea", stroke=NEG)
        out.append(b_obj)

        out.append(arrow(tu_x[i], y_tu + 135, tu_x[i], y_tu + 165))

        out.append(arrow(tu_x[i], y_tu + 230, 500, 315))

    b_linker, _, _ = textbox(500, 355, ["Компонувальник (Linker / COMDAT Folding)", "Видалення 2 дублікатів vector<int>::push_back", "Залишається ЛИШЕ 1 копія в бінарному файлі"], size=13, pad=12, fill="#e8f8f5", stroke=POS)
    out.append(b_linker)

    render(os.path.join(IMG, 'comdat-deduplication.svg'), W, H, *out,
           title="Марна робота компілятора при дубльованій неявній інстанціації в багатьох файлах")


def fig_optimization_techniques():
    W, H = 1040, 380
    out = []

    out.append(text(W / 2, 30, "Порівняння архітектурних підходів до зниження вартості шаблонів", size=18, bold=True))

    approaches = [
        ("Наївний шаблон", ["Header-only реалізація", "Інстанціація в кожному .cpp", "Високий Code Bloat", "Повільна компіляція"], "#fdecea", NEG),
        ("Extern Template", ["Явна інстанціація в 1 .cpp", "Заборона неявної в інших", "Нульове дублювання", "Швидка компіляція"], "#eef4ff", MUTED),
        ("Pointer Folding", ["Узагальнена основа на void*", "Тонкі inline обгортки", "1 копія коду для всіх T*", "Мінімальний бінарник"], "#fcf8e3", "#d6a928"),
        ("C++20 Concepts", ["Перевірка обмежень до signature", "Швидкий відсів кандидатів", "Немає SFINAE-сміття", "Чисті помилки"], "#e8f8f5", POS)
    ]

    x_start = 30
    box_w = 215
    gap = 35
    y_center = 190

    for i, (title_text, items, bg_fill, border_color) in enumerate(approaches):
        x = x_start + i * (box_w + gap)
        b, w, h = textbox(x + box_w / 2, y_center, [title_text] + items, size=13, pad=14, fill=bg_fill, stroke=border_color)
        out.append(b)

    out.append(text(W / 2, 340, "Комбінація цих технічних рішень дає швидку збірку та компактний машинний код", size=13, color=MUTED))

    render(os.path.join(IMG, 'optimization-techniques.svg'), W, H, *out,
           title="Вплив architectural паттернів на час збірки та розмір виконуваного файлу")


if __name__ == '__main__':
    fig_instantiation_pipeline()
    fig_comdat_deduplication()
    fig_optimization_techniques()
    print("Всі фігури успішно згенеровано у теку img/")

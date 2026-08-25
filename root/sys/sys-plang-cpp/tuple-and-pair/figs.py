# -*- coding: utf-8 -*-
"""Фігури до теми «std::tuple та std::pair»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Макет пам'яті std::pair та std::tuple (вирівнювання, padding, EBO) ────────────
def fig_tuple_layout():
    W, H = 940, 460
    f = []

    f.append(text(470, 30, "Макет пам'яті std::pair та std::tuple у C++", size=16, color=INK, anchor="middle", bold=True))

    # Секція 1: std::pair<char, double>
    f.append(text(40, 65, "1. std::pair<char, double>: вирівнювання за межею 8 байтів (alignof = 8)", size=13, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(40, 85, 120, 50, "char first\n(1 байт)", size=11, fill="#fff7e6", stroke=POS))
    f.append(fitbox(160, 85, 240, 50, "Padding bytes\n(7 байтів набивки)", size=11, fill="#f4f6f8", stroke=MUTED))
    f.append(fitbox(400, 85, 480, 50, "double second\n(8 байтів)", size=11, fill="#e8f6ee", stroke=FIELD))
    f.append(text(40, 150, "Всього sizeof(std::pair<char, double>) = 16 байтів через вимогу alignof(double) = 8", size=11, color=MUTED, anchor="start"))

    # Розділювальна лінія 1
    f.append(line(40, 175, 900, 175, color=MUTED, sw=1, dash="4 4"))

    # Секція 2: Порядок полів у std::tuple та оптимізація упаковки
    f.append(text(40, 195, "2. Вплив порядку полів у std::tuple на підсумковий розмір", size=13, color=INK, anchor="start", bold=True))

    # Поганий порядок: tuple<char, double, char>
    f.append(text(40, 220, "Неоптимальний порядок: std::tuple<char, double, char>", size=12, color=NEG, anchor="start", bold=True))
    f.append(fitbox(40, 235, 70, 45, "char", size=11, fill="#fff7e6", stroke=POS))
    f.append(fitbox(110, 235, 150, 45, "pad (7B)", size=10, fill="#f4f6f8", stroke=MUTED))
    f.append(fitbox(260, 235, 200, 45, "double (8B)", size=11, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(460, 235, 70, 45, "char", size=11, fill="#fff7e6", stroke=POS))
    f.append(fitbox(530, 235, 150, 45, "pad (7B)", size=10, fill="#f4f6f8", stroke=MUTED))
    f.append(fitbox(690, 235, 190, 45, "Разом: 24 байти", size=12, fill="#fde8e8", stroke=NEG))

    # Оптимальний порядок: tuple<double, char, char>
    f.append(text(40, 300, "Оптимальний порядок: std::tuple<double, char, char>", size=12, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(40, 315, 200, 45, "double (8B)", size=11, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(240, 315, 70, 45, "char", size=11, fill="#fff7e6", stroke=POS))
    f.append(fitbox(310, 315, 70, 45, "char", size=11, fill="#fff7e6", stroke=POS))
    f.append(fitbox(380, 315, 150, 45, "pad (6B)", size=10, fill="#f4f6f8", stroke=MUTED))
    f.append(fitbox(690, 315, 190, 45, "Разом: 16 байтів", size=12, fill="#e8f6ee", stroke=FIELD))

    # Розділювальна лінія 2
    f.append(line(40, 375, 900, 375, color=MUTED, sw=1, dash="4 4"))

    # Секція 3: EBO (Empty Base Optimization)
    f.append(text(40, 395, "3. Оптимізація порожньої бази (EBO): std::tuple<int, EmptyTag> входить у 4 байти", size=13, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(40, 412, 430, 38, "int value (4 байти)", size=11, fill="#e8f6ee", stroke=FIELD))
    f.append(fitbox(480, 412, 430, 38, "EmptyTag (0 байтів завдяки EBO / [[no_unique_address]])", size=11, fill="#eef2f7", stroke=POS))

    render(os.path.join(OUT, 'tuple-layout.svg'), W, H, *f, title="Макет пам'яті std::pair та std::tuple")


# ── 2. Механіка розпакування кортежу через std::apply та index_sequence ──────────────
def fig_tuple_unpacking_flow():
    W, H = 940, 380
    f = []

    f.append(text(470, 30, "Розпакування std::tuple у виклик функції через std::apply", size=16, color=INK, anchor="middle", bold=True))

    # Кортеж на вході
    f.append(fitbox(40, 80, 220, 110, "std::tuple<T0, T1, T2>\nt = {arg0, arg1, arg2}", size=12, fill="#eef2f7", stroke=LINE))

    # Індексна послідовність
    f.append(arrow(260, 135, 315, 135, color=INK, sw=2))
    f.append(fitbox(320, 80, 240, 110, "std::index_sequence<0, 1, 2>\nГенерація індексів на етапі компіляції", size=12, fill="#fff7e6", stroke=POS))

    # Шаблонне розгортання пакету
    f.append(arrow(560, 135, 615, 135, color=INK, sw=2))
    f.append(fitbox(620, 80, 280, 110, "Розгортання пакета виразів:\nf(std::get<Is>(t)...)\n==> f(get<0>(t), get<1>(t), get<2>(t))", size=11, fill="#e8f6ee", stroke=FIELD))

    # Результат
    f.append(arrow(470, 190, 470, 245, color=INK, sw=2))
    f.append(fitbox(220, 250, 500, 75, "Виклик цільової функції чи лямбди: f(arg0, arg1, arg2)\nПовноцінне передавання категорій значень через std::forward", size=12, fill="#e8f6ee", stroke=FIELD))

    f.append(text(470, 355, "std::apply усуває ручне розгортання ітераторів та забезпечує нульові накладні витрати на етапі виконання", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, 'tuple-unpacking-flow.svg'), W, H, *f, title="Розпакування std::tuple через std::apply")


# ── 3. Протокол структурованих зв'язувань (C++17) ──────────────────────────────────
def fig_structured_bindings_mechanics():
    W, H = 940, 390
    f = []

    f.append(text(470, 30, "Протокол структурованих зв'язувань (Structured Bindings) у C++17", size=16, color=INK, anchor="middle", bold=True))

    # Вираз розкладання
    f.append(fitbox(40, 75, 860, 45, "Код розробника: auto [x, y, z] = get_data_tuple();", size=13, fill="#eef2f7", stroke=LINE))

    # Три кроки компіляції
    f.append(fitbox(40, 140, 260, 120, "Крок 1: Запит розміру\nstd::tuple_size<E>::value\nПеревіряється кількість елементів (повинна бути 3)", size=11, fill="#fff7e6", stroke=POS))
    f.append(arrow(300, 200, 335, 200, color=INK, sw=2))

    f.append(fitbox(340, 140, 260, 120, "Крок 2: Запит типів\nstd::tuple_element<i, E>::type\nВизначення типів x, y, z для кожного індексу i", size=11, fill="#fff7e6", stroke=POS))
    f.append(arrow(600, 200, 635, 200, color=INK, sw=2))

    f.append(fitbox(640, 140, 260, 120, "Крок 3: Извлечення даних\nget<i>(e)\nМетод e.get<i>() або вільна функція get<i>(e)", size=11, fill="#e8f6ee", stroke=FIELD))

    # Підсумкове зв'язування імен
    f.append(arrow(470, 260, 470, 290, color=INK, sw=2))
    f.append(fitbox(170, 295, 600, 50, "Імена x, y, z стають псевдонімами для елементів прихованого об'єкта e\nПривязка до rvalue/lvalue відповідно до авто-специфікатора (auto, const auto&, auto&&)", size=11, fill="#e8f6ee", stroke=FIELD))

    f.append(text(470, 365, "Будь-який користувацький тип може підтримувати розкладання, реалізувавши цю трійку метафункцій", size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, 'structured-bindings-mechanics.svg'), W, H, *f, title="Протокол структурованих зв'язувань")


if __name__ == '__main__':
    fig_tuple_layout()
    fig_tuple_unpacking_flow()
    fig_structured_bindings_mechanics()
    print("Згенеровано фігури у теці img/")

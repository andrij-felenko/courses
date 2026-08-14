# -*- coding: utf-8 -*-
"""Фігури до теми «std::string та std::string_view»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Порівняння макетів пам'яті: std::string проти std::string_view ──────
def fig_string_vs_stringview_layout():
    W, H = 940, 440
    f = []

    # Верхня панель: std::string
    f.append(text(50, 45, "std::string (Володіння пам'яттю на купі)", size=16, color=INK, anchor="start", bold=True))
    
    # Стек об'єкт std::string (24 байти)
    f.append(fitbox(50, 65, 260, 110, "std::string (на стеку)\nptr ────┐\nsize: 13  │\ncap: 31   │", size=13, fill="#eef2f7", stroke=LINE))
    
    # Стрілка з стеку в купу
    f.append(arrow(310, 95, 470, 95, color=NEG, sw=2))
    
    # Буфер у купі
    f.append(fitbox(475, 65, 415, 110, "Динамічний буфер у купі (Heap Allocation)\n['H','e','l','l','o',',',' ','W','o','r','l','d','!','\\0']", size=13, fill="#e8f6ee", stroke=FIELD))
    
    f.append(text(470, 195, "std::string володіє буфером: виділяє пам'ять через new[], стежить за capacity та гарантує '\\0'", size=11, color=MUTED))

    # Розділювальна лінія
    f.append(line(40, 215, 900, 215, color=MUTED, sw=1, dash="6 5"))

    # Нижня панель: std::string_view
    f.append(text(50, 245, "std::string_view (Безволодісний погляд на підрядок)", size=16, color=INK, anchor="start", bold=True))

    # Об'єкт string_view на стеку (16 байтів)
    f.append(fitbox(50, 265, 260, 110, "std::string_view (на стеку)\nptr ────────┐\nsize: 5     │\n(без cap)   │", size=13, fill="#fff7e6", stroke=POS))

    # Стрілка на існуючий масив/буфер
    f.append(arrow(310, 295, 545, 295, color=POS, sw=2))

    # Існуючі дані в пам'яті (літерал або чужий рядок)
    f.append(fitbox(475, 265, 415, 110, "Зовнішній буфер у пам'яті (без виділення пам'яті!)\n['H','e','l','l','o',',',' ','W','o','r','l','d','!','\\0']\n      ▲             ▲\n      └─ size = 5 ──┘", size=12, fill="#f4f6f8", stroke=LINE))

    f.append(text(470, 395, "std::string_view лише посилається на чужу пам'ять: sizeof=16 байтів (ptr + size), O(1) substr, без '\\0'", size=11, color=MUTED))

    render(os.path.join(OUT, 'string-vs-stringview-layout.svg'), W, H, *f,
           title="Макет пам'яті std::string та std::string_view")


# ── 2. Оптимізація малих рядків (SSO Layout) ──────────────────────────────
def fig_sso_layout():
    W, H = 940, 420
    f = []

    f.append(text(50, 40, "Оптимізація малих рядків (SSO — Small String Optimization)", size=16, color=INK, anchor="start", bold=True))

    # Режим 1: Малий рядок (SSO Active)
    f.append(text(50, 75, "Режим 1: Короткий рядок (довжина ≤ 15..23 символів)", size=14, color=FIELD, anchor="start", bold=True))
    f.append(fitbox(50, 95, 840, 100,
                    "Внутрішній union об'єкта std::string (на стеку, 24/32 байти):\n"
                    "[ Буфер на стеку: 'S' 'm' 'a' 'l' 'l' '\\0' . . . . . . . . . . . . . . . | size/tag ]\n"
                    "Пам'ять у купі НЕ ВИДІЛЯЄТЬСЯ. Дані розміщені безпосередньо всередині самого об'єкта.",
                    size=12, fill="#e8f6ee", stroke=FIELD))

    # Режим 2: Великий рядок (Heap Allocation Active)
    f.append(text(50, 230, "Режим 2: Довгий рядок (довжина > 15..23 символів)", size=14, color=NEG, anchor="start", bold=True))
    f.append(fitbox(50, 250, 360, 110,
                    "Об'єкт std::string на стеку:\n"
                    "ptr: 0x7fff5fbff010 ───┐\n"
                    "size: 1024              │\n"
                    "capacity: 2048          │", size=12, fill="#eef2f7", stroke=LINE))

    f.append(arrow(410, 305, 495, 305, color=NEG, sw=2))

    f.append(fitbox(500, 250, 390, 110,
                    "Динамічний буфер у купі (Heap Allocation):\n"
                    "['V','e','r','y',' ','l','o','n','g',' ','s','t','r','i','n','g','...','\\0']\n"
                    "Буфер виділено через malloc/new[]; при зростанні робиться realloc", size=12, fill="#f4f6f8", stroke=LINE))

    f.append(text(470, 390, "SSO усуває виклики new/delete для коротких рядків за рахунок більшого розміру sizeof(std::string)", size=11, color=MUTED))

    render(os.path.join(OUT, 'sso-layout.svg'), W, H, *f,
           title="Макет пам'яті при оптимізації малих рядків (SSO)")


# ── 3. Небезпека dangling string_view ─────────────────────────────────────
def fig_dangling_string_view():
    W, H = 940, 420
    f = []

    f.append(text(50, 40, "Пастка: Провалений вказівник (Dangling string_view)", size=16, color=POS, anchor="start", bold=True))

    # Крок 1: Створення тимчасового std::string
    f.append(text(50, 75, "1. Створення тимчасового std::string", size=13, color=INK, anchor="start", bold=True))
    f.append(fitbox(50, 95, 340, 80, "std::string_view sv = get_name();\n// get_name() повертає тимчасовий std::string", size=12, fill="#fff7e6", stroke=POS))

    f.append(arrow(390, 135, 455, 135, color=MUTED, sw=2))

    # Тимчасовий об'єкт та його буфер
    f.append(fitbox(460, 95, 430, 80, "Тимчасовий std::string (rvalue)\nВиділений буфер у купі: [\"Alexander\\0\"]\nsv.ptr показує на цей буфер", size=12, fill="#eef2f7", stroke=LINE))

    # Крок 2: Знищення тимчасового об'єкта
    f.append(line(40, 195, 900, 195, color=MUTED, sw=1, dash="6 5"))

    f.append(text(50, 220, "2. Кінцівка виразу (Full-expression end): Тимчасовий об'єкт знищується!", size=13, color=POS, anchor="start", bold=True))

    f.append(fitbox(50, 240, 340, 110, "std::string_view sv;\nsv.ptr ───┐ (недійсний!)\nsv.size = 9│", size=12, fill="#fdf2f2", stroke=POS))

    f.append(arrow(390, 295, 455, 295, color=POS, sw=2))

    f.append(fitbox(460, 240, 430, 110, "Звільнена пам'ять (Freed Heap Memory)\n[ Звільнено / Пошкоджено ] ✖\nВиклик sv.data() або друк викликає Undefined Behavior!", size=12, fill="#fdf2f2", stroke=POS))

    f.append(text(470, 385, "std::string_view НЕ продовжує час життя тимчасових об'єктів (на відміну від const std::string&)", size=11, color=POS, bold=True))

    render(os.path.join(OUT, 'dangling-string-view.svg'), W, H, *f,
           title="Небезпека виникнення dangling pointer при вживанні string_view з тимчасовими об'єктами")


# ── 4. Вартість викликів залежно від типу параметра ───────────────────────
def fig_param_conversion_cost():
    W, H = 940, 440
    f = []

    f.append(text(50, 40, "Порівняння вартості передачі аргументів у функцію", size=16, color=INK, anchor="start", bold=True))

    cols = [(240, "Аргумент: const char*"), (470, "Аргумент: std::string"), (700, "Аргумент: підрядок")]
    CW, RH = 210, 80

    f.append(fitbox(30, 60, 200, 40, "Параметр функції \\ Аргумент", size=10, fill="#eceff3", color=MUTED))
    for x, name in cols:
        f.append(fitbox(x, 60, CW, 40, name, size=11, fill="#eceff3", bold=True))

    rows = [
        (110, "const std::string&\n(посилання на володаря)",
         [("Обов'язкова алокація!\nСтворення temp string", "bad"), ("0 алокацій\nПередача за посиланням", "good"), ("Обов'язкова алокація!\nКопія підрядка у купу", "bad")]),
        (200, "std::string_view\n(безволодісний погляд)",
         [("0 алокацій\nОбчислення strlen O(N)", "good"), ("0 алокацій\nВказівник + розмір O(1)", "best"), ("0 алокацій\nЗміщення вказівника O(1)", "best")]),
        (290, "std::string\n(передача за значенням)",
         [("1 алокація\nСтворення нового рядка", "bad"), ("1 копія або move\nЯкщо std::move -> O(1)", "warn"), ("1 алокація\nНовий рядок у купі", "bad")]),
    ]

    style = {
        "best": dict(fill="#e8f6ee", stroke=FIELD, color=INK, bold=True),
        "good": dict(fill="#f4f6f8", stroke=LINE, color=INK, bold=False),
        "warn": dict(fill="#fff7e6", stroke=POS, color=INK, bold=False),
        "bad":  dict(fill="#fdf2f2", stroke=POS, color=POS, bold=True),
    }

    for y, label, cells in rows:
        f.append(fitbox(30, y, 200, RH, label, size=11, fill="#fbfcfd", bold=True))
        for (x, _), (txt, kind) in zip(cols, cells):
            f.append(fitbox(x, y, CW, RH, txt, size=10, **style[kind]))

    f.append(text(470, 395, "std::string_view усуває тимчасові алокації для будь-яких джерел текстових даних", size=11, color=MUTED))

    render(os.path.join(OUT, 'param-conversion-cost.svg'), W, H, *f,
           title="Порівняльна таблиця алокацій і продуктивності при передачі рядків")


if __name__ == "__main__":
    fig_string_vs_stringview_layout()
    fig_sso_layout()
    fig_dangling_string_view()
    fig_param_conversion_cost()
    print("Всі 4 SVG фігури успішно згенеровано у img/")

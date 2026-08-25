# -*- coding: utf-8 -*-
"""Фігури до теми «Оптимізація порожньої бази й [[no_unique_address]]»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── 1. Чому повний об'єкт не може мати розмір 0 ─────────────────────────────
def fig_non_zero_size():
    W, H = 960, 480
    parts = []

    parts.append(text(W / 2, 40, "Правило ненульового розміру: ідентичність і адресна арифметика",
                      size=16, bold=True, color=INK))

    # Секція А: Два окремі об'єкти
    parts.append(text(240, 80, "Два окремі об'єкти (Empty a, b;)", size=14, bold=True, color=MUTED))
    b1, w1, _ = textbox(150, 130, ["об'єкт a", "адреса 0x1000", "розмір: 1 байт"], size=13, fill="#eaf0fd", stroke=NEG)
    b2, w2, _ = textbox(330, 130, ["об'єкт b", "адреса 0x1001", "розмір: 1 байт"], size=13, fill="#eaf0fd", stroke=NEG)
    parts += [b1, b2]
    parts.append(mtext(240, 195, ["&a != &b — різні об'єкти", "мають гарантовано різні адреси"],
                       size=12, color=FIELD, bold=True))

    # Секція Б: Масив
    parts.append(text(720, 80, "Масив порожніх об'єктів (Empty arr[3];)", size=14, bold=True, color=MUTED))
    a0, _, _ = textbox(570, 130, ["arr[0]", "0x2000"], size=13, fill="#eafaf1", stroke=FIELD)
    a1, _, _ = textbox(720, 130, ["arr[1]", "0x2001"], size=13, fill="#eafaf1", stroke=FIELD)
    a2, _, _ = textbox(870, 130, ["arr[2]", "0x2002"], size=13, fill="#eafaf1", stroke=FIELD)
    parts += [a0, a1, a2]
    parts.append(mtext(720, 195, ["arr + 1 крокує на sizeof(Empty) байт вперед;", "якби розмір був 0, покажчик стояв би на місці"],
                       size=12, color=FIELD, bold=True))

    parts.append(line(40, 240, W - 40, 240, color=MUTED, sw=1, dash="6,6"))

    # Секція В: Наслідок для композиції
    parts.append(text(W / 2, 275, "Ціна композиції: вирівнювання роздуває 1 байт до розміру слова",
                      size=15, bold=True, color=POS))

    # Візуалізація пам'яті struct { int* ptr; Empty e; }
    x0, y0 = 100, 320
    # ptr: 8 байтів (0..7)
    parts.append(rect(x0, y0, 380, 55, fill="#eaf0fd", stroke=NEG, sw=1.5))
    parts.append(text(x0 + 190, y0 + 28, "int* ptr (8 байтів, зміщення 0..7)", size=13, color=NEG, bold=True))
    parts.append(text(x0 + 190, y0 + 46, "вирівнювання: 8 байтів", size=11, color=MUTED))

    # e: 1 байт (8)
    parts.append(rect(x0 + 380, y0, 90, 55, fill="#fdecea", stroke=POS, sw=1.5))
    parts.append(text(x0 + 425, y0 + 28, "Empty e", size=13, color=POS, bold=True))
    parts.append(text(x0 + 425, y0 + 46, "1 байт", size=11, color=POS))

    # padding: 7 байтів (9..15)
    parts.append(rect(x0 + 470, y0, 290, 55, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=0))
    parts.append(text(x0 + 615, y0 + 28, "порожнє заповнення (padding, 7 байтів)", size=13, color=MUTED))
    parts.append(text(x0 + 615, y0 + 46, "для вирівнювання загального розміру до кратного 8", size=11, color=MUTED))

    # Підсумкова стрілка розміру
    parts.append(line(x0, y0 + 75, x0 + 760, y0 + 75, color=INK, sw=1.2))
    parts.append(line(x0, y0 + 68, x0, y0 + 82, color=INK, sw=1.2))
    parts.append(line(x0 + 760, y0 + 68, x0 + 760, y0 + 82, color=INK, sw=1.2))
    parts.append(text(x0 + 380, y0 + 98, "Загальний sizeof(Holder) = 16 байтів замість корисних 8!",
                      size=14, bold=True, color=POS))

    render(os.path.join(IMG, 'non-zero-size.svg'), W, H, *parts,
           title="Чому об'єкт C++ має ненульовий розмір і як композиція подвоює пам'ять")


# ── 2. Empty Base Optimization (EBO) ────────────────────────────────────────
def fig_ebo_layout():
    W, H = 960, 430
    parts = []

    parts.append(line(480, 50, 480, 390, color=MUTED, sw=1, dash="5,5"))

    # Ліва колонка: Композиція
    parts.append(text(240, 45, "Композиція (без EBO)", size=16, bold=True, color=POS))
    parts.append(text(240, 75, "struct Holder { int* ptr; Deleter d; };", size=13, color=MUTED))

    yc = 120
    parts.append(rect(60, yc, 360, 50, fill="#eaf0fd", stroke=NEG, sw=1.5))
    parts.append(text(240, yc + 30, "int* ptr (8 байтів, зсув +0)", size=13, color=NEG, bold=True))

    parts.append(rect(60, yc + 60, 100, 50, fill="#fdecea", stroke=POS, sw=1.5))
    parts.append(text(110, yc + 90, "Deleter d (1 б)", size=12, color=POS, bold=True))

    parts.append(rect(170, yc + 60, 250, 50, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=0))
    parts.append(text(295, yc + 90, "padding (7 байтів)", size=12, color=MUTED))

    parts.append(fitbox(60, yc + 130, 360, 65,
                        ["sizeof(Holder) = 16 байтів",
                         "Накладні витрати: +100% до розміру покажчика"],
                        size=13, fill="#fdecea", stroke=POS, bold=True))

    # Права колонка: Спадкування (EBO)
    parts.append(text(720, 45, "Спадкування (EBO в дії)", size=16, bold=True, color=FIELD))
    parts.append(text(720, 75, "struct Holder : private Deleter { int* ptr; };", size=13, color=MUTED))

    ye = 120
    parts.append(rect(540, ye, 360, 60, fill="#eafaf1", stroke=FIELD, sw=2))
    parts.append(text(720, ye + 25, "Базовий підоб'єкт Deleter (зсув +0, розмір 0 байтів)", size=12, color=FIELD, bold=True))
    parts.append(text(720, ye + 45, "int* ptr (8 байтів, зсув +0)", size=13, color=NEG, bold=True))

    parts.append(fitbox(540, ye + 130, 360, 65,
                        ["sizeof(Holder) = 8 байтів",
                         "Нульові накладні витрати: стиснуто в 1 машинне слово"],
                        size=13, fill="#eafaf1", stroke=FIELD, bold=True))

    parts.append(mtext(W / 2, 395,
                       ["Базовий підоб'єкт ділить адресу 0x0 з першим полем;",
                        "правило sizeof >= 1 не застосовується до базових підоб'єктів"],
                       size=13, color=INK))

    render(os.path.join(IMG, 'ebo-layout.svg'), W, H, *parts,
           title="Порівняння розкладки пам'яті: композиція проти оптимізації порожньої бази")


# ── 3. C++20 [[no_unique_address]] ──────────────────────────────────────────
def fig_no_unique_address():
    W, H = 960, 420
    parts = []

    parts.append(text(W / 2, 40, "C++20 [[no_unique_address]]: чиста композиція без спадкування",
                      size=16, bold=True, color=INK))

    code_str = "struct ModernHolder { int* ptr; [[no_unique_address]] Deleter d; };"
    parts.append(text(W / 2, 75, code_str, size=14, color=MUTED))

    # Велика схема розкладки
    x, y, w, h = 180, 115, 600, 110
    parts.append(rect(x, y, w, h, fill="#eafaf1", stroke=FIELD, sw=2))

    # Спільний блок
    parts.append(text(x + w / 2, y + 35, "Адреса 0x1000 (зсув 0 байтів)", size=14, bold=True, color=FIELD))

    # Дві складові за однією адресою
    b_ptr, _, _ = textbox(x + 160, y + 75, ["int* ptr", "корисне поле (8 байтів)"], size=13, fill="#eaf0fd", stroke=NEG)
    b_del, _, _ = textbox(x + 440, y + 75, ["Deleter d", "[[no_unique_address]] (0 байтів)"], size=13, fill="#ffffff", stroke=FIELD)
    parts += [b_ptr, b_del]

    # Пояснення переваг
    grid_y = 255
    col_w = 270
    gap = 30
    c1_x = (W - 3 * col_w - 2 * gap) / 2

    box1 = fitbox(c1_x, grid_y, col_w, 95,
                  ["Композиція замість спадкування",
                   "Немає ризику зрізання типів (slicing)",
                   "і витоку внутрішнього інтерфейсу"],
                  size=12, fill=FILL, stroke=LINE)

    box2 = fitbox(c1_x + col_w + gap, grid_y, col_w, 95,
                  ["Працює з типами final",
                   "EBO не може спадкувати final-класи,",
                   "а атрибут члена підтримує їх вільно"],
                  size=12, fill=FILL, stroke=FIELD)

    box3 = fitbox(c1_x + 2 * (col_w + gap), grid_y, col_w, 95,
                  ["Краща підтримка шаблонів",
                   "Працює з lambdas, лямбда-делітерами",
                   "й stateless алокаторами прямо в полях"],
                  size=12, fill=FILL, stroke=LINE)

    parts += [box1, box2, box3]

    parts.append(text(W / 2, 385, "Підсумок: sizeof(ModernHolder) = 8 байтів (розмір 1 покажчика)",
                      size=14, bold=True, color=FIELD))

    render(os.path.join(IMG, 'no-unique-address.svg'), W, H, *parts,
           title="Розкладка пам'яті з атрибутом [[no_unique_address]]")


# ── 4. Пастка однакових типів ────────────────────────────────────────────────
def fig_same_type_trap():
    W, H = 960, 440
    parts = []

    parts.append(line(480, 50, 480, 400, color=MUTED, sw=1, dash="5,5"))

    # Ліва частина: Різні типи
    parts.append(text(240, 45, "Випадок А: РІЗНІ порожні типи", size=15, bold=True, color=FIELD))
    parts.append(text(240, 75, "[[no_unique_address]] EmptyA a;", size=13, color=MUTED))
    parts.append(text(240, 95, "[[no_unique_address]] EmptyB b; int x;", size=13, color=MUTED))

    # Схема А
    ya = 135
    parts.append(rect(60, ya, 360, 80, fill="#eafaf1", stroke=FIELD, sw=1.5))
    parts.append(text(240, ya + 28, "Зсув +0: EmptyA a (0 байтів) & EmptyB b (0 байтів)", size=12, color=FIELD, bold=True))
    parts.append(text(240, ya + 55, "Зсув +0: int x (4 байти)", size=13, color=NEG, bold=True))

    parts.append(fitbox(60, ya + 100, 360, 60,
                        ["&a == &b дозволено (різні типи!)",
                         "Загальний розмір = 4 байти"],
                        size=13, fill="#eafaf1", stroke=FIELD, bold=True))

    # Права частина: Однаковий тип
    parts.append(text(720, 45, "Випадок Б: ОДНАКОВИЙ порожній тип", size=15, bold=True, color=POS))
    parts.append(text(720, 75, "[[no_unique_address]] Empty a;", size=13, color=MUTED))
    parts.append(text(720, 95, "[[no_unique_address]] Empty b; int x;", size=13, color=MUTED))

    # Схема Б
    yb = 135
    parts.append(rect(540, yb, 100, 45, fill="#eafaf1", stroke=FIELD, sw=1.5))
    parts.append(text(590, yb + 26, "a (зсув 0)", size=12, color=FIELD, bold=True))

    parts.append(rect(650, yb, 100, 45, fill="#fdecea", stroke=POS, sw=1.5))
    parts.append(text(700, yb + 26, "b (зсув 1)", size=12, color=POS, bold=True))

    parts.append(rect(760, yb, 140, 45, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=0))
    parts.append(text(830, yb + 26, "padding (2 б)", size=12, color=MUTED))

    parts.append(rect(540, yb + 55, 360, 45, fill="#eaf0fd", stroke=NEG, sw=1.5))
    parts.append(text(720, yb + 82, "int x (4 байти, зсув +4 через вирівнювання)", size=12, color=NEG, bold=True))

    parts.append(fitbox(540, yb + 120, 360, 80,
                        ["Заборонено &a == &b для однакового типу!",
                         "b зміщується на +1 байт -> padding ->",
                         "Загальний розмір зростає до 8 байтів!"],
                        size=12, fill="#fdecea", stroke=POS, bold=True))

    parts.append(mtext(W / 2, 415,
                       ["Стандарт C++ забороняє двом підоб'єктам однакового типу мати однакову адресу;",
                        "тому оптимізатор змушений призначити другому члену унікальне ненульове зміщення"],
                       size=12, color=INK))

    render(os.path.join(IMG, 'same-type-trap.svg'), W, H, *parts,
           title="Крайовий випадок: колізія адрес при збігу типів двох порожніх членів")


if __name__ == '__main__':
    fig_non_zero_size()
    fig_ebo_layout()
    fig_no_unique_address()
    fig_same_type_trap()
    print("ok")

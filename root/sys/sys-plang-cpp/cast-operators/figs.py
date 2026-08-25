# -*- coding: utf-8 -*-
"""Фігури до теми «Оператори приведення: static_cast, reinterpret_cast, const_cast, dynamic_cast» (reference/cpp-standards/language/cast-operators)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

FREEZE_FILL = "#fdecea"
OPEN_FILL   = "#eaf7ee"
WARN_FILL   = "#fef9e7"
BLUE_FILL   = "#eaf0fd"
PURPLE_FILL = "#f3e8fd"


# ── 1. Карта чотирьох іменованих операторів приведення ────────────────────────
def fig_four_casts_quadrant():
    W, H = 920, 470
    f = []

    f.append(rect(10, 10, 900, 450, fill=BG, stroke=LINE, sw=1.5))
    f.append(text(460, 40, "Система чотирьох іменованих операторів приведення в C++", size=16, bold=True))
    f.append(text(460, 62, "Розподіл за часом перевірки та характером перетворення типів", size=13, color=MUTED))

    # Стовпчик 1: static_cast
    s_b, s_w, s_h = textbox(240, 160, [
        "static_cast<T>(v)",
        "Статична семантична конверсія",
        "• Числові перетворення (int ↔ double)",
        "• Upcast та unchecked downcast",
        "• Зворотні перетворення через void*",
        "• Виклик явних ctor / conversion ops",
        "Вартість у runtime: 0 (компіляторна)"
    ], size=13, pad=12, fill=OPEN_FILL, stroke=FIELD, sw=2, min_w=400)
    f.append(s_b)

    # Стовпчик 2: dynamic_cast
    d_b, d_w, d_h = textbox(680, 160, [
        "dynamic_cast<T>(v)",
        "Динамічна поліморфна перевірка",
        "• Безпечний downcast в ієрархії з vtable",
        "• Cross-cast між гілками спадкування",
        "• Вказівник: повертає nullptr при невдачі",
        "• Посилання: кидає std::bad_cast",
        "Вартість у runtime: обхід RTTI-дерева"
    ], size=13, pad=12, fill=PURPLE_FILL, stroke="#8e44ad", sw=2, min_w=400)
    f.append(d_b)

    # Стовпчик 3: const_cast
    c_b, c_w, c_h = textbox(240, 345, [
        "const_cast<T>(v)",
        "Модифікація кваліфікаторів типу",
        "• Зняття або додавання const / volatile",
        "• Безпечно: коли сам об'єкт не константний",
        "• Небезпечно: запис у справжній const → UB",
        "• Не змінює двійкове представлення",
        "Вартість у runtime: 0 (кваліфікатор)"
    ], size=13, pad=12, fill=WARN_FILL, stroke="#d35400", sw=2, min_w=400)
    f.append(c_b)

    # Стовпчик 4: reinterpret_cast
    r_b, r_w, r_h = textbox(680, 345, [
        "reinterpret_cast<T>(v)",
        "Побітове переосмислення адреси",
        "• Вказівник ↔ ціле число (uintptr_t)",
        "• Вказівник ↔ вказівник без спільних предків",
        "• Не зміщує байти при спадкуванні!",
        "• Доступ до значення через чужий тип → UB",
        "Вартість у runtime: 0 (Strict Aliasing ризик)"
    ], size=13, pad=12, fill=FREEZE_FILL, stroke=POS, sw=2, min_w=400)
    f.append(r_b)

    render(os.path.join(IMG, "four-casts-quadrant.svg"), W, H, *f,
           title="Система чотирьох іменованих операторів приведення в C++")


# ── 2. Каскад C-style cast ──────────────────────────────────────────────────
def fig_c_cast_sequence():
    W, H = 920, 520
    f = []

    f.append(rect(10, 10, 900, 500, fill=BG, stroke=LINE, sw=1.5))
    f.append(text(460, 38, "П'ятиступеневий алгоритм розгортання C-style cast (T)expr", size=16, bold=True))
    f.append(text(460, 60, "Компілятор вибирає перший варіант, що синтаксично підходить (ISO C++ [expr.cast])", size=13, color=MUTED))

    steps = [
        ("Спроба 1", "const_cast<T>(expr)", "Зміна const / volatile", OPEN_FILL, FIELD),
        ("Спроба 2", "static_cast<T>(expr)", "Семантичне приведення / upcast / downcast", OPEN_FILL, FIELD),
        ("Спроба 3", "static_cast + const_cast", "Семантична зміна + зняття кваліфікатора", WARN_FILL, "#d35400"),
        ("Спроба 4", "reinterpret_cast<T>(expr)", "Побітове переосмислення вказівника", FREEZE_FILL, POS),
        ("Спроба 5", "reinterpret_cast + const_cast", "Побітове переосмислення + зняття const", FREEZE_FILL, POS),
    ]

    for i, (num, code_txt, desc, fill_c, stroke_c) in enumerate(steps):
        y = 105 + i * 66
        b, w, h = textbox(300, y, [num + ": " + code_txt, desc], size=13, pad=8,
                          fill=fill_c, stroke=stroke_c, sw=1.5, min_w=450)
        f.append(b)

        if i < len(steps) - 1:
            f.append(arrow(300, y + 24, 300, y + 42, color=MUTED))
            f.append(text(340, y + 34, "не підійшло", size=11, color=MUTED, anchor="start"))

    # Блок небезпеки праворуч
    f.append(rect(580, 105, 310, 370, fill=FREEZE_FILL, stroke=POS, sw=2))
    f.append(text(735, 140, "Чому це небезпечно?", size=15, bold=True, color=POS))
    f.append(text(735, 170, "Тихий перехід у reinterpret_cast", size=13, bold=True))

    exp_lines = [
        "Нехай клас Base стане private-базою",
        "або втратить спадкування під час",
        "рефакторингу. Тоді static_cast",
        "дав би чітку помилку компіляції.",
        "",
        "Але C-style cast (Base*)pDerived",
        "мовчки провалиться до Спроби 4",
        "і згенерує reinterpret_cast!",
        "",
        "Вказівник не буде зміщено,",
        "а програма отримає приховане UB."
    ]
    f.append(mtext(735, 205, exp_lines, size=12, color=INK, lh=1.35))

    render(os.path.join(IMG, "c-cast-sequence.svg"), W, H, *f,
           title="П'ятиступеневий каскад C-style cast")


# ── 3. Зміщення вказівника при множинному спадкуванні ─────────────────────────
def fig_pointer_adjustment():
    W, H = 920, 440
    f = []

    f.append(rect(10, 10, 900, 420, fill=BG, stroke=LINE, sw=1.5))
    f.append(text(460, 36, "Множинне спадкування: зміщення адреси при приведенні типів", size=16, bold=True))
    f.append(text(460, 58, "Розкладка об'єкта Derived у пам'яті: struct Derived : BaseA, BaseB", size=13, color=MUTED))

    # Схема пам'яті Derived
    f.append(rect(60, 95, 800, 110, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(460, 115, "Об'єкт Derived у пам'яті (розмір 24 байти)", size=13, bold=True))

    # Підоб'єкт BaseA
    f.append(rect(80, 130, 240, 60, fill=BLUE_FILL, stroke=NEG, sw=1.5))
    f.append(text(200, 155, "Підоб'єкт BaseA (8 B)", size=13, bold=True))
    f.append(text(200, 175, "Зсув: +0 байтів [0x1000]", size=12, color=MUTED))

    # Підоб'єкт BaseB
    f.append(rect(330, 130, 240, 60, fill=WARN_FILL, stroke="#d35400", sw=1.5))
    f.append(text(450, 155, "Підоб'єкт BaseB (8 B)", size=13, bold=True))
    f.append(text(450, 175, "Зсув: +8 байтів [0x1008]", size=12, color=MUTED))

    # Поля Derived
    f.append(rect(580, 130, 260, 60, fill=OPEN_FILL, stroke=FIELD, sw=1.5))
    f.append(text(710, 155, "Власні поля Derived (8 B)", size=13, bold=True))
    f.append(text(710, 175, "Зсув: +16 байтів [0x1010]", size=12, color=MUTED))

    # Порівняння двох операторів при downcast від BaseB*
    f.append(text(460, 235, "Приведення вказівника BaseB* ptr = 0x1008 назад до Derived*:", size=14, bold=True))

    # static_cast
    s_b, s_w, s_h = textbox(250, 325, [
        "static_cast<Derived*>(ptr)",
        "• Знає розкладку класів на етапі компіляції",
        "• Автоматично віднімає зсув 8 байтів: 0x1008 − 8",
        "• Результат: 0x1000 (початок об'єкта Derived)",
        "✓ Коректний доступ до всіх полів та методів"
    ], size=12, pad=10, fill=OPEN_FILL, stroke=FIELD, sw=1.5, min_w=380)
    f.append(s_b)

    # reinterpret_cast
    r_b, r_w, r_h = textbox(670, 325, [
        "reinterpret_cast<Derived*>(ptr)",
        "• Не знає семантики класів, копіює «сирі» біти",
        "• Залишає адресу 0x1008 без жодного зсуву",
        "• Вважає початком Derived середину об'єкта!",
        "✗ Спроба читання полів Derived/BaseA призведе до сміття/UB"
    ], size=12, pad=10, fill=FREEZE_FILL, stroke=POS, sw=1.5, min_w=380)
    f.append(r_b)

    render(os.path.join(IMG, "pointer-adjustment.svg"), W, H, *f,
           title="Зміщення адреси при множинному спадкуванні")


# ── 4. Пастка Strict Aliasing ───────────────────────────────────────────────
def fig_strict_aliasing_trap():
    W, H = 920, 440
    f = []

    f.append(rect(10, 10, 900, 420, fill=BG, stroke=LINE, sw=1.5))
    f.append(text(460, 36, "Пастка Strict Aliasing при порушенні сумісності типів", size=16, bold=True))
    f.append(text(460, 58, "Оптимізатор компілятора (-O2/-O3) припускає, що вказівники різних типів не перетинаються", size=13, color=MUTED))

    # Лівий блок: Код і намір
    f.append(rect(40, 85, 380, 315, fill=FILL, stroke=LINE, sw=1.5))
    f.append(text(230, 115, "Код із порушенням Strict Aliasing", size=14, bold=True))

    code_lines = [
        "float f = 1.0f;",
        "int* pi = reinterpret_cast<int*>(&f);",
        "",
        "float step1 = f;     // Читання f",
        "*pi = 0x40000000;    // Запис через int*",
        "float step2 = f;     // Повторне читання f",
        "",
        "return step1 + step2;"
    ]
    f.append(mtext(60, 150, code_lines, size=13, color=INK, anchor="start", lh=1.35))

    # Правий блок: Оптимізація та збій
    f.append(rect(460, 85, 420, 315, fill=FREEZE_FILL, stroke=POS, sw=2))
    f.append(text(670, 115, "Що насправді робить оптимізатор", size=14, bold=True, color=POS))

    opt_lines = [
        "1. Компілятор бачить, що float* і int*",
        "   мають різні несумісні типи (ISO C++ §7.2.1).",
        "",
        "2. За правилом Strict Aliasing запис у *pi",
        "   НЕ МОЖЕ змінити значення змінної f.",
        "",
        "3. Оптимізатор вважає читання step2",
        "   надлишковим і використовує старе значення f,",
        "   збережене у FPU/SSE-регістрі xmm0!",
        "",
        "4. Результат: запис *pi ігнорується для f,",
        "   повертається 1.0f + 1.0f замість очікуваного 3.0f.",
        "   Поведінка є невизначеною (UB)."
    ]
    f.append(mtext(480, 150, opt_lines, size=12, color=INK, anchor="start", lh=1.3))

    render(os.path.join(IMG, "strict-aliasing-trap.svg"), W, H, *f,
           title="Пастка Strict Aliasing при переосмисленні типів")


# ── 5. Навігація dynamic_cast та RTTI ─────────────────────────────────────────
def fig_dynamic_cast_rtti():
    W, H = 920, 460
    f = []

    f.append(rect(10, 10, 900, 440, fill=BG, stroke=LINE, sw=1.5))
    f.append(text(460, 36, "Механізм dynamic_cast: динамічна навігація поліморфною ієрархією", size=16, bold=True))
    f.append(text(460, 58, "Перевірка фактичного типу об'єкта під час виконання через RTTI", size=13, color=MUTED))

    # Об'єкт у пам'яті з vptr
    f.append(rect(40, 95, 230, 160, fill=PURPLE_FILL, stroke="#8e44ad", sw=1.5))
    f.append(text(155, 125, "Об'єкт у пам'яті", size=14, bold=True))
    f.append(rect(55, 145, 200, 36, fill=BG, stroke="#8e44ad", sw=1.5))
    f.append(text(155, 168, "vptr (вказівник на vtable)", size=12, bold=True))
    f.append(rect(55, 190, 200, 50, fill=BG, stroke=LINE, sw=1))
    f.append(text(155, 212, "Поля об'єкта", size=12, color=MUTED))
    f.append(text(155, 228, "(Derived)", size=11, color=MUTED))

    # Стрілка від vptr до VTable
    f.append(arrow(255, 163, 335, 163, color="#8e44ad", sw=2))

    # VTable та RTTI
    f.append(rect(340, 95, 260, 200, fill=BLUE_FILL, stroke=NEG, sw=1.5))
    f.append(text(470, 120, "Таблиця vtable & RTTI", size=14, bold=True))

    f.append(rect(355, 135, 230, 42, fill=WARN_FILL, stroke="#d35400", sw=1.5))
    f.append(text(470, 153, "RTTI Complete Object Locator", size=12, bold=True))
    f.append(text(470, 169, "Зсуви та type_info для Derived", size=11, color=MUTED))

    f.append(rect(355, 185, 230, 32, fill=BG, stroke=LINE, sw=1))
    f.append(text(470, 205, "slot 0: &Derived::func1()", size=12))

    f.append(rect(355, 225, 230, 32, fill=BG, stroke=LINE, sw=1))
    f.append(text(470, 245, "slot 1: &Derived::func2()", size=12))

    # Стрілка від RTTI до розгалуження
    f.append(arrow(585, 156, 645, 156, color=MUTED, sw=1.8))
    f.append(arrow(645, 156, 645, 290, color=MUTED, sw=1.8))

    # Блок результатів dynamic_cast
    s_box, s_w, s_h = textbox(770, 160, [
        "Цільовий тип знайдено (Успіх)",
        "• Обчислює правильну базову адресу",
        "• Повертає Derived*",
        "✓ Швидкість залежить від глибини дерева"
    ], size=12, pad=10, fill=OPEN_FILL, stroke=FIELD, sw=1.5, min_w=240)
    f.append(s_box)

    f_box, f_w, f_h = textbox(770, 320, [
        "Невідповідний тип (Невдача)",
        "• Для вказівників (Target*):",
        "  повертає nullptr",
        "• Для посилань (Target&):",
        "  викидає виняток std::bad_cast"
    ], size=12, pad=10, fill=FREEZE_FILL, stroke=POS, sw=1.5, min_w=240)
    f.append(f_box)

    f.append(arrow(645, 156, 665, 156, color=FIELD, sw=1.8))
    f.append(arrow(645, 290, 665, 320, color=POS, sw=1.8))

    f.append(text(460, 420, "dynamic_cast вимагає поліморфного типу (хоча б одна віртуальна функція у базовому класі)",
                  size=13, color=MUTED))

    render(os.path.join(IMG, "dynamic-cast-rtti.svg"), W, H, *f,
           title="Механізм dynamic_cast та навігація RTTI")


if __name__ == "__main__":
    fig_four_casts_quadrant()
    fig_c_cast_sequence()
    fig_pointer_adjustment()
    fig_strict_aliasing_trap()
    fig_dynamic_cast_rtti()
    print("All figures generated successfully.")


# -*- coding: utf-8 -*-
import sys, os

# 4 levels up to scripts/ from reference/cpp-standards/releases/cpp20-features
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "Consolas, 'DejaVu Sans Mono', monospace"


def mono(x, y, s, size=12, color=INK, anchor="middle", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


def monobox(x, y, w, h, lines, size=12, fill=FILL, stroke=LINE, sw=1.5, color=INK,
            lh=1.4, dash=None, anchor="middle", bold=False):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=8)
    if dash:
        out = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" fill="%s" '
               'stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>'
               % (x, y, w, h, fill, stroke, sw, dash))
    n = len(lines)
    cy = y + h / 2 - (n - 1) * size * lh / 2 + size * 0.35
    px = x + w / 2 if anchor == "middle" else x + 16
    for i, ln in enumerate(lines):
        out += mono(px, cy + i * size * lh, ln, size=size, color=color, anchor=anchor, bold=bold)
    return out


# ── 1. Велика четвірка C++20 ───────────────────────────────────────────────
def fig_four_pillars():
    W, H = 1080, 500
    p = []

    # Тло картки
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke=LINE, sw=1.2, rx=10))
    p.append(text(W / 2, 40, "«Велика четвірка» фундаментальних технологій C++20", size=16, bold=True, color=INK))

    col_w = 240
    gap = 20
    start_x = 35
    top_y = 68
    box_h = 405

    # 1. Концепти
    bx1 = start_x
    p.append(rect(bx1, top_y, col_w, box_h, fill="#eef7ee", stroke=FIELD, sw=2, rx=8))
    p.append(text(bx1 + col_w / 2, top_y + 28, "1. Концепти", size=15, bold=True, color=FIELD))
    p.append(mono(bx1 + col_w / 2, top_y + 48, "concept / requires", size=11, bold=True, color=FIELD))
    p.append(line(bx1 + 15, top_y + 60, bx1 + col_w - 15, top_y + 60, color=FIELD, sw=1.2))

    p.append(text(bx1 + 15, top_y + 82, "Сутність:", size=11.5, bold=True, anchor="start", color=INK))
    p.append(text(bx1 + 15, top_y + 102, "Предикати перевірки типів", size=11, anchor="start", color=INK))
    p.append(text(bx1 + 15, top_y + 120, "на етапі компіляції.", size=11, anchor="start", color=INK))

    p.append(text(bx1 + 15, top_y + 148, "Що замінює:", size=11.5, bold=True, anchor="start", color=INK))
    p.append(text(bx1 + 15, top_y + 168, "Громіздкий SFINAE,", size=11, anchor="start", color=INK))
    p.append(mono(bx1 + 15, top_y + 186, "std::enable_if_t", size=10.5, anchor="start", color=MUTED))

    p.append(text(bx1 + 15, top_y + 214, "Ключові переваги:", size=11.5, bold=True, anchor="start", color=FIELD))
    p.append(text(bx1 + 15, top_y + 234, "• Чіткі помилки збірки", size=11, anchor="start", color=INK))
    p.append(text(bx1 + 15, top_y + 252, "• Перевантаження за", size=11, anchor="start", color=INK))
    p.append(text(bx1 + 25, top_y + 270, "ступенем обмеження", size=11, anchor="start", color=INK))
    p.append(text(bx1 + 15, top_y + 288, "• Скорочені шаблони", size=11, anchor="start", color=INK))

    p.append(monobox(bx1 + 12, top_y + 312, col_w - 24, 78,
                     ["template<std::integral T>", "void process(T val);"],
                     size=10.5, fill="#fff", stroke=FIELD, sw=1, anchor="start"))

    # 2. Модулі
    bx2 = start_x + (col_w + gap)
    p.append(rect(bx2, top_y, col_w, box_h, fill="#f0f4ff", stroke=NEG, sw=2, rx=8))
    p.append(text(bx2 + col_w / 2, top_y + 28, "2. Модулі", size=15, bold=True, color=NEG))
    p.append(mono(bx2 + col_w / 2, top_y + 48, "import / export", size=11, bold=True, color=NEG))
    p.append(line(bx2 + 15, top_y + 60, bx2 + col_w - 15, top_y + 60, color=NEG, sw=1.2))

    p.append(text(bx2 + 15, top_y + 82, "Сутність:", size=11.5, bold=True, anchor="start", color=INK))
    p.append(text(bx2 + 15, top_y + 102, "Компіляція інтерфейсів", size=11, anchor="start", color=INK))
    p.append(text(bx2 + 15, top_y + 120, "у бінарні блоки (BMI).", size=11, anchor="start", color=INK))

    p.append(text(bx2 + 15, top_y + 148, "Що замінює:", size=11.5, bold=True, anchor="start", color=INK))
    p.append(text(bx2 + 15, top_y + 168, "Текстову підстановку", size=11, anchor="start", color=INK))
    p.append(mono(bx2 + 15, top_y + 186, "#include та header guards", size=10.5, anchor="start", color=MUTED))

    p.append(text(bx2 + 15, top_y + 214, "Ключові переваги:", size=11.5, bold=True, anchor="start", color=NEG))
    p.append(text(bx2 + 15, top_y + 234, "• Ізоляція макросів", size=11, anchor="start", color=INK))
    p.append(text(bx2 + 15, top_y + 252, "• Прискорення компіляції", size=11, anchor="start", color=INK))
    p.append(text(bx2 + 15, top_y + 270, "• Чітке розмежування", size=11, anchor="start", color=INK))
    p.append(text(bx2 + 25, top_y + 288, "експорту й деталей", size=11, anchor="start", color=INK))

    p.append(monobox(bx2 + 12, top_y + 312, col_w - 24, 78,
                     ["export module math;", "export int add(int a, int b);"],
                     size=10.5, fill="#fff", stroke=NEG, sw=1, anchor="start"))

    # 3. Корутини
    bx3 = start_x + (col_w + gap) * 2
    p.append(rect(bx3, top_y, col_w, box_h, fill="#fdf2f2", stroke=POS, sw=2, rx=8))
    p.append(text(bx3 + col_w / 2, top_y + 28, "3. Корутини", size=15, bold=True, color=POS))
    p.append(mono(bx3 + col_w / 2, top_y + 48, "co_await / co_yield", size=11, bold=True, color=POS))
    p.append(line(bx3 + 15, top_y + 60, bx3 + col_w - 15, top_y + 60, color=POS, sw=1.2))

    p.append(text(bx3 + 15, top_y + 82, "Сутність:", size=11.5, bold=True, anchor="start", color=INK))
    p.append(text(bx3 + 15, top_y + 102, "Безстекові функції з можливістю", size=10.5, anchor="start", color=INK))
    p.append(text(bx3 + 15, top_y + 120, "призупинення й відновлення.", size=10.5, anchor="start", color=INK))

    p.append(text(bx3 + 15, top_y + 148, "Що замінює:", size=11.5, bold=True, anchor="start", color=INK))
    p.append(text(bx3 + 15, top_y + 168, "Пекло зворотних викликів,", size=11, anchor="start", color=INK))
    p.append(text(bx3 + 15, top_y + 186, "ручні машини станів", size=11, anchor="start", color=MUTED))

    p.append(text(bx3 + 15, top_y + 214, "Ключові переваги:", size=11.5, bold=True, anchor="start", color=POS))
    p.append(text(bx3 + 15, top_y + 234, "• Лінійний асинхронний код", size=11, anchor="start", color=INK))
    p.append(text(bx3 + 15, top_y + 252, "• Ліниві генератори", size=11, anchor="start", color=INK))
    p.append(text(bx3 + 15, top_y + 270, "• Мінімальний оверхед", size=11, anchor="start", color=INK))
    p.append(text(bx3 + 25, top_y + 288, "(HALO оптимізація)", size=11, anchor="start", color=INK))

    p.append(monobox(bx3 + 12, top_y + 312, col_w - 24, 78,
                     ["generator<int> seq() {", "  co_yield 42;", "}"],
                     size=10.5, fill="#fff", stroke=POS, sw=1, anchor="start"))

    # 4. Діапазони
    bx4 = start_x + (col_w + gap) * 3
    p.append(rect(bx4, top_y, col_w, box_h, fill="#fbf5fd", stroke="#8e44ad", sw=2, rx=8))
    p.append(text(bx4 + col_w / 2, top_y + 28, "4. Діапазони", size=15, bold=True, color="#8e44ad"))
    p.append(mono(bx4 + col_w / 2, top_y + 48, "std::ranges / views", size=11, bold=True, color="#8e44ad"))
    p.append(line(bx4 + 15, top_y + 60, bx4 + col_w - 15, top_y + 60, color="#8e44ad", sw=1.2))

    p.append(text(bx4 + 15, top_y + 82, "Сутність:", size=11.5, bold=True, anchor="start", color=INK))
    p.append(text(bx4 + 15, top_y + 102, "Концепція діапазону як", size=11, anchor="start", color=INK))
    p.append(text(bx4 + 15, top_y + 120, "цілісного об'єкта зі sentinel.", size=11, anchor="start", color=INK))

    p.append(text(bx4 + 15, top_y + 148, "Що замінює:", size=11.5, bold=True, anchor="start", color=INK))
    p.append(text(bx4 + 15, top_y + 168, "Пари ітераторів begin/end,", size=11, anchor="start", color=INK))
    p.append(text(bx4 + 15, top_y + 186, "жадібні проміжні копії", size=11, anchor="start", color=MUTED))

    p.append(text(bx4 + 15, top_y + 214, "Ключові переваги:", size=11.5, bold=True, anchor="start", color="#8e44ad"))
    p.append(text(bx4 + 15, top_y + 234, "• Ліниві адаптери через |", size=11, anchor="start", color=INK))
    p.append(text(bx4 + 15, top_y + 252, "• Проекції в алгоритмах", size=11, anchor="start", color=INK))
    p.append(text(bx4 + 15, top_y + 270, "• Безпека висячих ітераторів", size=11, anchor="start", color=INK))
    p.append(text(bx4 + 25, top_y + 288, "(std::ranges::dangling)", size=11, anchor="start", color=INK))

    p.append(monobox(bx4 + 12, top_y + 312, col_w - 24, 78,
                     ["auto v = data", "  | views::filter(even)", "  | views::take(5);"],
                     size=10.5, fill="#fff", stroke="#8e44ad", sw=1, anchor="start"))

    render(os.path.join(OUT, "cpp20-four-pillars.svg"), W, H, *p)


# ── 2. Модель корутин у C++20 ──────────────────────────────────────────────
def fig_coroutines_model():
    W, H = 1080, 520
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke=LINE, sw=1.2, rx=10))
    p.append(text(W / 2, 38, "Модель виконання корутин у C++20: взаємодія компонентів", size=16, bold=True, color=INK))

    # Лівий блок: Код функції-корутини
    bx1, by1, bw1, bh1 = 35, 70, 310, 420
    p.append(rect(bx1, by1, bw1, bh1, fill="#fff", stroke=LINE, sw=1.5, rx=8))
    p.append(text(bx1 + bw1 / 2, by1 + 25, "Корутина (Функція у коді)", size=14, bold=True, color=INK))
    p.append(line(bx1 + 15, by1 + 38, bx1 + bw1 - 15, by1 + 38, color=MUTED, sw=1))

    code_lines = [
        "Task<int> async_work() {",
        "  // 1. initial_suspend()",
        "  int a = fetch_local();",
        "  co_await remote_io();",
        "  // [точка призупинення 1]",
        "  int b = 100;",
        "  co_yield (a + b);",
        "  // [точка призупинення 2]",
        "  co_return 0;",
        "  // 2. final_suspend()",
        "}"
    ]
    p.append(monobox(bx1 + 12, by1 + 50, bw1 - 24, 250, code_lines, size=11, fill="#f4f6f8", stroke=LINE, sw=1, anchor="start"))

    p.append(text(bx1 + 15, by1 + 325, "Маркери перетворення на корутину:", size=11.5, bold=True, anchor="start", color=POS))
    p.append(text(bx1 + 15, by1 + 348, "• Наявність co_await, co_yield або co_return", size=10.5, anchor="start", color=INK))
    p.append(text(bx1 + 15, by1 + 368, "• Повертаний тип має trait promise_type", size=10.5, anchor="start", color=INK))
    p.append(text(bx1 + 15, by1 + 388, "• Тіло розбивається на скінченний автомат", size=10.5, anchor="start", color=INK))

    # Середній блок: Фрейм корутини (в купі або HALO)
    bx2, by2, bw2, bh2 = 380, 70, 340, 420
    p.append(rect(bx2, by2, bw2, bh2, fill="#fdf2f2", stroke=POS, sw=2, rx=8))
    p.append(text(bx2 + bw2 / 2, by2 + 25, "Фрейм корутини (Coroutine Frame)", size=14, bold=True, color=POS))
    p.append(line(bx2 + 15, by2 + 38, bx2 + bw2 - 15, by2 + 38, color=POS, sw=1))

    # Секції фрейму
    p.append(rect(bx2 + 15, by2 + 50, bw2 - 30, 65, fill="#fff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(bx2 + bw2 / 2, by2 + 72, "Об'єкт Promise (promise_type)", size=12, bold=True, color=FIELD))
    p.append(mono(bx2 + bw2 / 2, by2 + 95, "get_return_object(), unhandled_exception()", size=10, color=INK))

    p.append(rect(bx2 + 15, by2 + 125, bw2 - 30, 65, fill="#fff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(bx2 + bw2 / 2, by2 + 147, "Копії / переміщення аргументів", size=12, bold=True, color=NEG))
    p.append(mono(bx2 + bw2 / 2, by2 + 170, "Зберігають стан при виході зі стека", size=10.5, color=MUTED))

    p.append(rect(bx2 + 15, by2 + 200, bw2 - 30, 65, fill="#fff", stroke=POS, sw=1.2, rx=6))
    p.append(text(bx2 + bw2 / 2, by2 + 222, "Локальні змінні через точки паузи", size=12, bold=True, color=POS))
    p.append(mono(bx2 + bw2 / 2, by2 + 245, "int a, int b (збережені між resume)", size=10.5, color=INK))

    p.append(rect(bx2 + 15, by2 + 275, bw2 - 30, 65, fill="#fff", stroke="#8e44ad", sw=1.2, rx=6))
    p.append(text(bx2 + bw2 / 2, by2 + 297, "Індекс точки призупинення", size=12, bold=True, color="#8e44ad"))
    p.append(mono(bx2 + bw2 / 2, by2 + 320, "Число для switch(suspend_point)", size=10.5, color=INK))

    p.append(rect(bx2 + 15, by2 + 350, bw2 - 30, 52, fill="#fff", stroke=LINE, sw=1, rx=6))
    p.append(text(bx2 + bw2 / 2, by2 + 372, "HALO (Heap Allocation Elision)", size=11.5, bold=True, color=INK))
    p.append(text(bx2 + bw2 / 2, by2 + 390, "Оптимізація інлайнінгу: розміщення на стеку", size=10, color=MUTED))

    # Правий блок: Керування (coroutine_handle & Awaiter)
    bx3, by3, bw3, bh3 = 750, 70, 295, 420
    p.append(rect(bx3, by3, bw3, bh3, fill="#f0f4ff", stroke=NEG, sw=2, rx=8))
    p.append(text(bx3 + bw3 / 2, by2 + 25, "Зовнішній інтерфейс і чекач", size=14, bold=True, color=NEG))
    p.append(line(bx3 + 15, by3 + 38, bx3 + bw3 - 15, by3 + 38, color=NEG, sw=1))

    p.append(rect(bx3 + 15, by3 + 50, bw3 - 30, 95, fill="#fff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(bx3 + bw3 / 2, by3 + 70, "std::coroutine_handle<P>", size=12, bold=True, color=NEG))
    p.append(mono(bx3 + bw3 / 2, by3 + 90, "handle.resume()", size=11, bold=True, color=FIELD))
    p.append(mono(bx3 + bw3 / 2, by3 + 110, "handle.destroy()", size=11, bold=True, color=POS))
    p.append(mono(bx3 + bw3 / 2, by3 + 130, "handle.done()", size=11, color=INK))

    p.append(rect(bx3 + 15, by3 + 160, bw3 - 30, 160, fill="#fff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(bx3 + bw3 / 2, by3 + 182, "Протокол Awaiter (co_await)", size=12, bold=True, color=FIELD))
    p.append(line(bx3 + 30, by3 + 192, bx3 + bw3 - 30, by3 + 192, color=FIELD, sw=1))
    p.append(text(bx3 + 25, by3 + 212, "1. await_ready() -> bool", size=11, bold=True, anchor="start", color=INK))
    p.append(text(bx3 + 35, by3 + 228, "Чи є результат готовим негайно?", size=10, anchor="start", color=MUTED))
    p.append(text(bx3 + 25, by3 + 248, "2. await_suspend(handle)", size=11, bold=True, anchor="start", color=INK))
    p.append(text(bx3 + 35, by3 + 264, "Куди передати керування?", size=10, anchor="start", color=MUTED))
    p.append(text(bx3 + 25, by3 + 284, "3. await_resume() -> T", size=11, bold=True, anchor="start", color=INK))
    p.append(text(bx3 + 35, by3 + 300, "Отримати значення виразу", size=10, anchor="start", color=MUTED))

    p.append(text(bx3 + 15, by3 + 345, "Синхронізація:", size=11.5, bold=True, anchor="start", color=INK))
    p.append(text(bx3 + 15, by3 + 365, "Керування повертається викликачу", size=10.5, anchor="start", color=INK))
    p.append(text(bx3 + 15, by3 + 383, "у точці призупинення, а потім", size=10.5, anchor="start", color=INK))
    p.append(text(bx3 + 15, by3 + 401, "відновлюється через resume().", size=10.5, anchor="start", color=INK))

    # Стрілки
    p.append(arrow(345, 200, 380, 200, color=POS, sw=2))
    p.append(arrow(720, 100, 750, 100, color=NEG, sw=2))

    render(os.path.join(OUT, "cpp20-coroutines-model.svg"), W, H, *p)


# ── 3. Конвеєр обробки діапазонів ──────────────────────────────────────────
def fig_ranges_pipeline():
    W, H = 1080, 480
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke=LINE, sw=1.2, rx=10))
    p.append(text(W / 2, 38, "Лінива композиція діапазонів std::ranges: виконання за запитом", size=16, bold=True, color=INK))

    # Верхній блок: Код конвеєра
    p.append(rect(40, 65, 1000, 56, fill="#fff", stroke="#8e44ad", sw=1.8, rx=8))
    p.append(mono(540, 98, "auto pipeline = data | views::filter(is_even) | views::transform(square) | views::take(2);",
                  size=12.5, bold=True, color="#8e44ad"))

    # Блоки адаптерів
    step_y = 150
    bw = 210
    bh = 190
    gap = 40
    start_x = 45

    # Джерело: data
    bx0 = start_x
    p.append(rect(bx0, step_y, bw, bh, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=8))
    p.append(text(bx0 + bw / 2, step_y + 25, "Контейнер даних", size=13, bold=True, color=INK))
    p.append(mono(bx0 + bw / 2, step_y + 45, "std::vector<int>", size=11, color=MUTED))
    p.append(line(bx0 + 15, step_y + 58, bx0 + bw - 15, step_y + 58, color=MUTED, sw=1))
    p.append(mono(bx0 + bw / 2, step_y + 85, "[ 1,  2,  3,  4,  5 ]", size=11.5, bold=True, color=INK))
    p.append(text(bx0 + 15, step_y + 120, "Виділена пам'ять:", size=11, bold=True, anchor="start", color=INK))
    p.append(text(bx0 + 15, step_y + 140, "5 елементів у heap.", size=10.5, anchor="start", color=INK))
    p.append(text(bx0 + 15, step_y + 160, "Володіє даними.", size=10.5, italic=True, anchor="start", color=MUTED))

    # 1. views::filter
    bx1 = start_x + (bw + gap)
    p.append(rect(bx1, step_y, bw, bh, fill="#eef7ee", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(bx1 + bw / 2, step_y + 25, "views::filter", size=13, bold=True, color=FIELD))
    p.append(mono(bx1 + bw / 2, step_y + 45, "filter_view (O(1) mem)", size=11, color=FIELD))
    p.append(line(bx1 + 15, step_y + 58, bx1 + bw - 15, step_y + 58, color=FIELD, sw=1))
    p.append(mono(bx1 + bw / 2, step_y + 85, "x % 2 == 0", size=11.5, bold=True, color=FIELD))
    p.append(text(bx1 + 15, step_y + 120, "Лінивий предикат:", size=11, bold=True, anchor="start", color=INK))
    p.append(text(bx1 + 15, step_y + 140, "Пропускає 1, 3, 5.", size=10.5, anchor="start", color=INK))
    p.append(text(bx1 + 15, step_y + 160, "Пропускає далі: 2, 4.", size=10.5, anchor="start", color=FIELD))

    # 2. views::transform
    bx2 = start_x + (bw + gap) * 2
    p.append(rect(bx2, step_y, bw, bh, fill="#f0f4ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(bx2 + bw / 2, step_y + 25, "views::transform", size=13, bold=True, color=NEG))
    p.append(mono(bx2 + bw / 2, step_y + 45, "transform_view (O(1) mem)", size=11, color=NEG))
    p.append(line(bx2 + 15, step_y + 58, bx2 + bw - 15, step_y + 58, color=NEG, sw=1))
    p.append(mono(bx2 + bw / 2, step_y + 85, "x * x", size=11.5, bold=True, color=NEG))
    p.append(text(bx2 + 15, step_y + 120, "Трансформація:", size=11, bold=True, anchor="start", color=INK))
    p.append(text(bx2 + 15, step_y + 140, "2 -> 4", size=10.5, anchor="start", color=INK))
    p.append(text(bx2 + 15, step_y + 160, "4 -> 16", size=10.5, anchor="start", color=NEG))

    # 3. views::take
    bx3 = start_x + (bw + gap) * 3
    p.append(rect(bx3, step_y, bw, bh, fill="#fbf5fd", stroke="#8e44ad", sw=1.8, rx=8))
    p.append(text(bx3 + bw / 2, step_y + 25, "views::take(2)", size=13, bold=True, color="#8e44ad"))
    p.append(mono(bx3 + bw / 2, step_y + 45, "take_view (O(1) mem)", size=11, color="#8e44ad"))
    p.append(line(bx3 + 15, step_y + 58, bx3 + bw - 15, step_y + 58, color="#8e44ad", sw=1))
    p.append(mono(bx3 + bw / 2, step_y + 85, "limit = 2", size=11.5, bold=True, color="#8e44ad"))
    p.append(text(bx3 + 15, step_y + 120, "Зупинка за лічильником:", size=11, bold=True, anchor="start", color=INK))
    p.append(text(bx3 + 15, step_y + 140, "Обмежує кількість.", size=10.5, anchor="start", color=INK))
    p.append(text(bx3 + 15, step_y + 160, "Sentinel сигналізує кінець.", size=10.5, anchor="start", color="#8e44ad"))

    # Стрілки конвеєра
    p.append(arrow(bx0 + bw, step_y + bh / 2, bx1, step_y + bh / 2, color=FIELD, sw=2))
    p.append(arrow(bx1 + bw, step_y + bh / 2, bx2, step_y + bh / 2, color=NEG, sw=2))
    p.append(arrow(bx2 + bw, step_y + bh / 2, bx3, step_y + bh / 2, color="#8e44ad", sw=2))

    # Нижній блок: Результат у циклі
    p.append(rect(40, 360, 1000, 90, fill="#eef7ee", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(540, 385, "Споживання елементів у циклі: for (int x : pipeline)", size=13, bold=True, color=FIELD))
    p.append(mono(540, 410, "Крок 1: береться 1 (відкинуто), береться 2 -> підноситься до квадрату -> видає 4", size=11, color=INK))
    p.append(mono(540, 432, "Крок 2: береться 3 (відкинуто), береться 4 -> підноситься до квадрату -> видає 16 -> Sentinel завершує цикл", size=11, color=INK))

    render(os.path.join(OUT, "cpp20-ranges-pipeline.svg"), W, H, *p)


# ── 4. Тристороннє порівняння <=> ──────────────────────────────────────────
def fig_spaceship_operator():
    W, H = 1080, 500
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke=LINE, sw=1.2, rx=10))
    p.append(text(W / 2, 38, "Оператор <=> і синтез 6 операторів порівняння у C++20", size=16, bold=True, color=INK))

    # Лівий блок: Що пише програміст
    bx1, by1, bw1, bh1 = 40, 70, 380, 400
    p.append(rect(bx1, by1, bw1, bh1, fill="#eef7ee", stroke=FIELD, sw=2, rx=8))
    p.append(text(bx1 + bw1 / 2, by1 + 25, "Код користувача у C++20", size=14, bold=True, color=FIELD))
    p.append(line(bx1 + 15, by1 + 38, bx1 + bw1 - 15, by1 + 38, color=FIELD, sw=1))

    struct_code = [
        "struct Record {",
        "  int id;",
        "  std::string name;",
        "  double score;",
        "",
        "  // Єдиний рядок для всіх 6 операцій:",
        "  auto operator<=>(const Record&) const",
        "       = default;",
        "};"
    ]
    p.append(monobox(bx1 + 15, by1 + 50, bw1 - 30, 190, struct_code, size=11, fill="#fff", stroke=FIELD, sw=1, anchor="start"))

    p.append(text(bx1 + 15, by1 + 265, "Що виконує = default:", size=11.5, bold=True, anchor="start", color=FIELD))
    p.append(text(bx1 + 15, by1 + 288, "• Почленне лексикографічне порівняння", size=10.5, anchor="start", color=INK))
    p.append(text(bx1 + 15, by1 + 308, "• Автоматичне виведення категорії порядку:", size=10.5, anchor="start", color=INK))
    p.append(mono(bx1 + 25, by1 + 328, "double -> std::partial_ordering", size=10.5, color=POS, anchor="start"))
    p.append(text(bx1 + 15, by1 + 350, "• Автоматичний синтез оператора operator==", size=10.5, anchor="start", color=INK))
    p.append(text(bx1 + 15, by1 + 370, "  (для максимальної швидкодії O(1))", size=10, italic=True, anchor="start", color=MUTED))

    # Стрілка між блоками
    p.append(arrow(430, 260, 480, 260, color=FIELD, sw=2.5))
    p.append(rect(435, 230, 40, 22, fill="#fff", stroke=MUTED, sw=1, rx=4))
    p.append(text(455, 245, "синтез", size=9.5, bold=True, color=INK))

    # Правий блок: Що автоматично генерує компілятор
    bx2, by2, bw2, bh2 = 490, 70, 550, 400
    p.append(rect(bx2, by2, bw2, bh2, fill="#f0f4ff", stroke=NEG, sw=2, rx=8))
    p.append(text(bx2 + bw2 / 2, by2 + 25, "Набір переписаних кандидатів (Overload Resolution)", size=14, bold=True, color=NEG))
    p.append(line(bx2 + 15, by2 + 38, bx2 + bw2 - 15, by2 + 38, color=NEG, sw=1))

    # Список операцій
    ops = [
        ("a == b", "Синтезований a.operator==(b) або перевернутий b.operator==(a)", FIELD),
        ("a != b", "Переписаний вираз: !(a == b)", FIELD),
        ("a < b",  "Переписаний вираз: (a <=> b) < 0", POS),
        ("a <= b", "Переписаний вираз: (a <=> b) <= 0", POS),
        ("a > b",  "Переписаний вираз: (a <=> b) > 0  або  0 < (b <=> a)", "#8e44ad"),
        ("a >= b", "Переписаний вираз: (a <=> b) >= 0 або  0 <= (b <=> a)", "#8e44ad"),
    ]

    for i, (op_expr, op_desc, op_col) in enumerate(ops):
        oy = by2 + 50 + i * 55
        p.append(rect(bx2 + 15, oy, bw2 - 30, 48, fill="#fff", stroke=op_col, sw=1.2, rx=6))
        p.append(mono(bx2 + 30, oy + 28, op_expr, size=12.5, bold=True, color=op_col, anchor="start"))
        p.append(mono(bx2 + 120, oy + 28, "→  " + op_desc, size=10.5, color=INK, anchor="start"))

    p.append(text(bx2 + bw2 / 2, by2 + 388, "Підтримка гетерогенних порівнянь: (a == 5) автоматично працює для (5 == a)",
                  size=10.5, italic=True, color=MUTED))

    render(os.path.join(OUT, "cpp20-spaceship-operator.svg"), W, H, *p)


def main():
    fig_four_pillars()
    fig_coroutines_model()
    fig_ranges_pipeline()
    fig_spaceship_operator()
    print("ok")


if __name__ == "__main__":
    main()

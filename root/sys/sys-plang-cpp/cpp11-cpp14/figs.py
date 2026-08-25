# -*- coding: utf-8 -*-
"""Фігури до теми «C++11 і C++14: перелом»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_paradigm_shift():
    """Порівняння парадигм C++98 та Modern C++ (C++11/C++14)."""
    W, H = 960, 430
    out = []

    out.append(text(W / 2, 50, "Чотири стовпи фундаментального переосмислення мови", size=13, color=MUTED))

    col_w = 205
    gap = 25
    start_x = 35
    y_top = 75
    h_col = 330

    pillars = [
        {
            "num": "Стовп 1",
            "title": "Управління ресурсами",
            "stroke": POS,
            "c98_title": "C++98: Ручне копіювання",
            "c98_items": ["Глибоке копіювання буферів", "auto_ptr із небезпечним transfer", "Вихідні параметри (T* out)"],
            "c14_title": "C++11/14: Move & RAII",
            "c14_items": ["Семантика переміщення rvalue", "std::unique_ptr / shared_ptr", "std::make_unique, нуль витоків"]
        },
        {
            "num": "Стовп 2",
            "title": "Багатопотоковість",
            "stroke": NEG,
            "c98_title": "C++98: Поза стандартом",
            "c98_items": ["Немає моделі пам'яті в ISO", "Платформні pthread / Win32", "Невизначена поведінка перегонів"],
            "c14_title": "C++11/14: Нативна модель",
            "c14_items": ["Формальний memory model", "<thread>, <atomic>, <mutex>", "happens-before гарантії"]
        },
        {
            "num": "Стовп 3",
            "title": "Виразність і типи",
            "stroke": FIELD,
            "c98_title": "C++98: Громіздкий синтаксис",
            "c98_items": ["Явні типи ітераторів", "std::bind1st, функтори-класи", "Макрос NULL і слабкі enum"],
            "c14_title": "C++11/14: Автовиведення",
            "c14_items": ["auto, decltype, decltype(auto)", "Лямбда-вирази й generic auto", "nullptr, enum class, override"]
        },
        {
            "num": "Стовп 4",
            "title": "Час компіляції",
            "stroke": "#d97706",
            "c98_title": "C++98: Шаблонна магія",
            "c98_items": ["Рекурсивні інстанціації", "Макроси препроцесора", "Повільна збірка коду"],
            "c14_title": "C++11/14: constexpr метакод",
            "c14_items": ["constexpr функції та цикли", "Шаблони зі змінною кількістю", "Шаблонні змінні (C++14)"]
        }
    ]

    for i, p in enumerate(pillars):
        cx = start_x + i * (col_w + gap) + col_w / 2

        out.append(rect(cx - col_w / 2, y_top, col_w, h_col, fill="#ffffff", stroke=p["stroke"], sw=2, rx=8))
        out.append(text(cx, y_top + 22, p["num"], size=11, color=p["stroke"], bold=True))
        out.append(text(cx, y_top + 42, p["title"], size=13, bold=True))
        out.append(line(cx - col_w / 2 + 10, y_top + 54, cx + col_w / 2 - 10, y_top + 54, color=p["stroke"], sw=1))

        c98_y = y_top + 64
        out.append(rect(cx - col_w / 2 + 8, c98_y, col_w - 16, 115, fill="#fef2f2", stroke="#f87171", sw=1, rx=5))
        out.append(text(cx, c98_y + 18, p["c98_title"], size=10, color=POS, bold=True))
        for j, itm in enumerate(p["c98_items"]):
            out.append(text(cx, c98_y + 40 + j * 24, itm, size=9.5, color=INK))

        arr_y = c98_y + 125
        out.append(arrow(cx, arr_y, cx, arr_y + 15, color=LINE, sw=1.8))

        c14_y = arr_y + 20
        out.append(rect(cx - col_w / 2 + 8, c14_y, col_w - 16, 115, fill="#f0fdf4", stroke="#4ade80", sw=1, rx=5))
        out.append(text(cx, c14_y + 18, p["c14_title"], size=10, color=FIELD, bold=True))
        for j, itm in enumerate(p["c14_items"]):
            out.append(text(cx, c14_y + 40 + j * 24, itm, size=9.5, color=INK))

    render(os.path.join(IMG, 'paradigm-shift.svg'), W, H, *out,
           title="Парадигмальний перелом: від C++98 до Modern C++ (C++11/C++14)")


def fig_move_vs_copy():
    """Порівняння механіки копіювання lvalue та переміщення rvalue."""
    W, H = 900, 430
    out = []

    out.append(text(W / 2, 48, "Глибоке копіювання пам'яті проти миттєвої передачі володіння покажчиком", size=13, color=MUTED))

    y1 = 70
    out.append(rect(40, y1, 820, 155, fill="#fffaf0", stroke="#d97706", sw=1.5, rx=8))
    out.append(text(60, y1 + 25, "Копіювання lvalue: std::vector<int> b = a; (глибоке дублювання)", size=13, color="#b45309", anchor="start", bold=True))

    bb1, _, _ = textbox(160, y1 + 80, "Об'єкт A (lvalue)\nptr: 0x1000\nsize: 100'000\ncap: 100'000", size=10.5, pad=8, fill="#ffffff", stroke=LINE)
    out.append(bb1)

    bb2, _, _ = textbox(400, y1 + 80, "Буфер у купі (0x1000)\n[ 100'000 елементів ]\nРозмір: 400 КБ", size=10.5, pad=8, fill="#f3f4f6", stroke=LINE)
    out.append(bb2)
    out.append(arrow(225, y1 + 80, 315, y1 + 80, color=LINE, sw=1.5))

    bb3, _, _ = textbox(620, y1 + 80, "Об'єкт B (копія)\nptr: 0x5000 (новий!)\nsize: 100'000\ncap: 100'000", size=10.5, pad=8, fill="#ffffff", stroke=POS)
    out.append(bb3)

    bb4, _, _ = textbox(780, y1 + 80, "Новий буфер (0x5000)\nПобайтова копія (memcpy)\nВитрати: нова алокація", size=10, pad=6, fill="#fee2e2", stroke=POS)
    out.append(bb4)
    out.append(arrow(685, y1 + 80, 715, y1 + 80, color=POS, sw=1.5))
    out.append(text(510, y1 + 140, "Ціна: malloc(400KB) + memcpy 400KB пам'яті ядра/купи", size=11, color=POS, bold=True))

    y2 = 245
    out.append(rect(40, y2, 820, 165, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    out.append(text(60, y2 + 25, "Переміщення rvalue: std::vector<int> c = std::move(a); (крадіжка покажчика)", size=13, color=FIELD, anchor="start", bold=True))

    bb5, _, _ = textbox(160, y2 + 85, "Об'єкт A (moved-from)\nptr: nullptr\nsize: 0\ncap: 0", size=10.5, pad=8, fill="#f9fafb", stroke=MUTED)
    out.append(bb5)

    bb6, _, _ = textbox(450, y2 + 85, "Буфер у купі (0x1000)\n[ 100'000 елементів залишаються на місці ]\nНуль виділень пам'яті!", size=10.5, pad=8, fill="#dcfce7", stroke=FIELD)
    out.append(bb6)

    bb7, _, _ = textbox(740, y2 + 85, "Об'єкт C (новий власник)\nptr: 0x1000 (перехоплено!)\nsize: 100'000\ncap: 100'000", size=10.5, pad=8, fill="#ffffff", stroke=FIELD)
    out.append(bb7)

    out.append(arrow(665, y2 + 85, 575, y2 + 85, color=FIELD, sw=2))
    out.append(line(225, y2 + 85, 325, y2 + 85, color=MUTED, sw=1.2, dash="4,4"))
    out.append(text(W / 2, y2 + 148, "Ціна: 3 копіювання 64-бітних полів (24 байти у регістрах) — складність O(1)", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, 'move-vs-copy.svg'), W, H, *out,
           title="Семантика переміщення (C++11) проти глибокого копіювання (C++98)")


def fig_memory_model_sync():
    """Синхронізація потоків і відношення happens-before у моделі пам'яті C++11."""
    W, H = 920, 450
    out = []

    out.append(text(W / 2, 48, "Міжпотокова синхронізація через std::atomic і впорядкування пам'яті", size=13, color=MUTED))

    cx1 = 220
    out.append(rect(cx1 - 165, 75, 330, 260, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    out.append(text(cx1, 98, "Потік 1: Producer", size=13, color=NEG, bold=True))

    bb_p1, _, _ = textbox(cx1, 142, "1. Звичайний запис даних:\ndata = 42;\n(non-atomic payload)", size=10.5, pad=6, fill="#ffffff", stroke=LINE)
    out.append(bb_p1)

    out.append(arrow(cx1, 175, cx1, 205, color=NEG, sw=1.5))
    out.append(text(cx1 + 80, 190, "sequenced-before", size=9.5, color=MUTED, italic=True))

    bb_p2, _, _ = textbox(cx1, 245, "2. Атомарний реліз прапорця:\nready.store(true,\n  std::memory_order_release);", size=10, pad=6, fill="#dbeafe", stroke=NEG)
    out.append(bb_p2)

    cx2 = 700
    out.append(rect(cx2 - 165, 75, 330, 260, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    out.append(text(cx2, 98, "Потік 2: Consumer", size=13, color=FIELD, bold=True))

    bb_c1, _, _ = textbox(cx2, 142, "3. Атомарне захоплення:\nwhile (!ready.load(\n  std::memory_order_acquire));", size=10, pad=6, fill="#dcfce7", stroke=FIELD)
    out.append(bb_c1)

    out.append(arrow(cx2, 185, cx2, 215, color=FIELD, sw=1.5))
    out.append(text(cx2 + 80, 200, "sequenced-before", size=9.5, color=MUTED, italic=True))

    bb_c2, _, _ = textbox(cx2, 255, "4. Безпечне читання даних:\nassert(data == 42);\n(гарантовано без data race!)", size=10.5, pad=6, fill="#ffffff", stroke=FIELD)
    out.append(bb_c2)

    # Центральний блок синхронізації
    cx_mid = 460
    bb_sync, _, _ = textbox(cx_mid, 195, "synchronizes-with\nміжпотокова синхронізація\n(реліз-аквайр бар'єр)", size=10.5, pad=8, fill="#fff1f2", stroke=POS)
    out.append(bb_sync)

    out.append(arrow(cx1 + 165, 245, cx_mid - 85, 215, color=POS, sw=1.8))
    out.append(arrow(cx_mid + 85, 175, cx2 - 165, 142, color=POS, sw=1.8))

    # Нижній банер гарантії
    out.append(rect(60, 360, 800, 48, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    out.append(text(W / 2, 382, "Транзитивне відношення пам'яті: (1) happens-before (4)", size=12, color=INK, bold=True))
    out.append(text(W / 2, 400, "Компілятор і процесор не мають права переставити інструкції через бар'єри синхронізації", size=10.5, color=MUTED))

    render(os.path.join(IMG, 'memory-model-sync.svg'), W, H, *out,
           title="Модель пам'яті C++11: синхронізація між потоками через acquire-release")


def fig_constexpr_evolution():
    """Еволюція обчислень під час компіляції від C++98 до C++14."""
    W, H = 920, 410
    out = []

    out.append(text(W / 2, 48, "Від рекурсивної шаблонізації до імперативного коду часу компіляції", size=13, color=MUTED))

    col_w = 265
    gap = 25
    start_x = 35
    y_top = 75
    h_col = 310

    stages = [
        {
            "std": "C++98: Template Meta",
            "color": POS,
            "fill": "#fff5f5",
            "stroke": "#f87171",
            "code": "template<int N>\nstruct Fact {\n  enum { val = N * Fact<N-1>::val };\n};\ntemplate<> struct Fact<0> {\n  enum { val = 1 };\n};",
            "traits": ["Тільки рекурсивні структури", "enum hack або static const", "Переповнення лімітів компілятора", "Повільна інстанціація AST"]
        },
        {
            "std": "C++11: Чистий constexpr",
            "color": "#d97706",
            "fill": "#fffbeb",
            "stroke": "#f59e0b",
            "code": "constexpr int fact(int n) {\n  return (n <= 1)\n    ? 1\n    : n * fact(n - 1);\n}\n// Тільки один оператор return!",
            "traits": ["Перші constexpr функції", "Строго один оператор return", "Тільки тернарний оператор ?:", "Без локальних змінних і циклів"]
        },
        {
            "std": "C++14: Імперативний constexpr",
            "color": FIELD,
            "fill": "#f0fdf4",
            "stroke": "#4ade80",
            "code": "constexpr int fact(int n) {\n  int res = 1;\n  for (int i = 2; i <= n; ++i)\n    res *= i;\n  return res;\n}",
            "traits": ["Повноцінні цикли for / while", "Мутабельні локальні змінні", "Розгалуження if / switch", "Шаблонні змінні template var"]
        }
    ]

    for i, st in enumerate(stages):
        cx = start_x + i * (col_w + gap) + col_w / 2

        out.append(rect(cx - col_w / 2, y_top, col_w, h_col, fill=st["fill"], stroke=st["stroke"], sw=2, rx=8))
        out.append(text(cx, y_top + 24, st["std"], size=12, color=st["color"], bold=True))
        out.append(line(cx - col_w / 2 + 10, y_top + 36, cx + col_w / 2 - 10, y_top + 36, color=st["stroke"], sw=1))

        bb, _, _ = textbox(cx, y_top + 105, st["code"], size=9.5, pad=6, fill="#ffffff", stroke="#d1d5db")
        out.append(bb)

        ty = y_top + 190
        for tr in st["traits"]:
            out.append(text(cx, ty, "• " + tr, size=10, color=INK))
            ty += 24

    render(os.path.join(IMG, 'constexpr-evolution.svg'), W, H, *out,
           title="Еволюція метапрограмування: від C++98 до C++14 constexpr")


if __name__ == '__main__':
    fig_paradigm_shift()
    fig_move_vs_copy()
    fig_memory_model_sync()
    fig_constexpr_evolution()
    print("Всі 4 фігури успішно згенеровано.")

# -*- coding: utf-8 -*-
"""Фігури до теми «Що приніс C++23»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_cpp23_architecture_map():
    """Схема ключових напрямів стандарту C++23."""
    W, H = 1000, 470
    out = []

    out.append(text(W / 2, 50, "Чотири головні вектори інновацій: від виправлення ядра до нових абстракцій STL", size=13, color=MUTED))

    col_w = 215
    gap = 25
    start_x = 35
    y_top = 75
    h_col = 365

    pillars = [
        {
            "num": "Ядро мови",
            "title": "Language Core",
            "fill": "#eef4ff",
            "stroke": NEG,
            "items": [
                "Deducing this (this Self&&)",
                "Багатовимірний operator[]",
                "auto(x) та auto{x} prvalue",
                "if consteval та constexpr cmath",
                "Послаблення вимог constexpr"
            ],
            "desc": ["Усунення дублювання", "методів та розширення", "обчислень під час компіляції"]
        },
        {
            "num": "Словникові типи",
            "title": "Vocabulary Types",
            "fill": "#f0fdf4",
            "stroke": FIELD,
            "items": [
                "std::expected<T, E>",
                "Монадичні optional (and_then)",
                "std::move_only_function",
                "std::forward_like",
                "std::to_underlying"
            ],
            "desc": ["Функціональна обробка", "помилок без винятків", "та виразні пайплайни"]
        },
        {
            "num": "Дані та діапазони",
            "title": "Data & Ranges",
            "fill": "#fffbeb",
            "stroke": "#d97706",
            "items": [
                "std::mdspan багатовимірний вид",
                "std::flat_map / std::flat_set",
                "std::generator для корутин",
                "Нові адаптери std::ranges",
                "std::span / string_view оновлення"
            ],
            "desc": ["Кеш-локальні структури,", "неперервні тензорні види", "та ліниві генератори"]
        },
        {
            "num": "Введення/вивід та діагностика",
            "title": "I/O & Diagnostics",
            "fill": "#fdf2f8",
            "stroke": POS,
            "items": [
                "std::print та std::println",
                "Бібліотека <stacktrace>",
                "Зафіксовані типи <stdfloat>",
                "std::format форматування рядків",
                "std::unreachable оптимізація"
            ],
            "desc": ["Швидкий типобезпечний", "вивід і захоплення стека", "без сторонніх бібліотек"]
        }
    ]

    for i, p in enumerate(pillars):
        cx = start_x + i * (col_w + gap) + col_w / 2

        out.append(rect(cx - col_w / 2, y_top, col_w, h_col, fill=p["fill"], stroke=p["stroke"], sw=2, rx=8))

        out.append(text(cx, y_top + 24, p["num"], size=12, color=p["stroke"], bold=True))
        out.append(text(cx, y_top + 46, p["title"], size=13, bold=True))

        out.append(line(cx - col_w / 2 + 12, y_top + 60, cx + col_w / 2 - 12, y_top + 60, color=p["stroke"], sw=1))

        item_y = y_top + 84
        for item in p["items"]:
            bb, _, _ = textbox(cx, item_y, item, size=11, pad=5, fill="#ffffff", stroke="#d1d5db", sw=1, min_w=col_w - 20)
            out.append(bb)
            item_y += 44

        out.append(line(cx - col_w / 2 + 12, y_top + 308, cx + col_w / 2 - 12, y_top + 308, color="#d1d5db", sw=1))
        out.append(mtext(cx, y_top + 328, p["desc"], size=11, color=INK, lh=1.35, bold=False))

    render(os.path.join(IMG, 'cpp23-architecture-map.svg'), W, H, *out,
           title="Архітектурні стовпи стандарту C++23")


def fig_deducing_this_mechanism():
    """Схема механізму Deducing this проти класичного підходу C++20."""
    W, H = 960, 420
    out = []

    out.append(text(W / 2, 50, "Явний параметр об'єкта скорочує шаблони й замінює складне успадкування", size=13, color=MUTED))

    card_w = 420
    card_h = 325
    y_card = 75

    lx = 45
    cx_l = lx + card_w / 2
    out.append(rect(lx, y_card, card_w, card_h, fill="#fff5f5", stroke=POS, sw=2, rx=8))
    out.append(text(cx_l, y_card + 26, "C++20: Комбінаторний вибух і CRTP", size=14, color=POS, bold=True))
    out.append(line(lx + 15, y_card + 38, lx + card_w - 15, y_card + 38, color=POS, sw=1))

    c20_points = [
        "1. Чотири дубльовані методи доступу:\n   operator[]() &, const&, &&, const&&",
        "2. Успадкування CRTP: struct Derived : Base<Derived>\n   з небезпечним static_cast<Derived*>(this)",
        "3. Рекурсивні лямбди вимагають повільного\n   std::function або окремих допоміжних структур",
        "4. Неможливість ідеально прокинути cv-ref\n   кваліфікатори об'єкта в один шаблон"
    ]
    y_p = y_card + 64
    for pt in c20_points:
        bb, _, _ = textbox(cx_l, y_p, pt, size=11, pad=6, fill="#ffffff", stroke="#fca5a5", sw=1, min_w=card_w - 30)
        out.append(bb)
        y_p += 65

    rx_pos = 495
    cx_r = rx_pos + card_w / 2
    out.append(rect(rx_pos, y_card, card_w, card_h, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    out.append(text(cx_r, y_card + 26, "C++23: Явний параметр (Deducing this)", size=14, color=FIELD, bold=True))
    out.append(line(rx_pos + 15, y_card + 38, rx_pos + card_w - 15, y_card + 38, color=FIELD, sw=1))

    c23_points = [
        "1. Один шаблонний метод з дедукцією типу:\n   auto&& operator[](this Self&& self, size_t i)",
        "2. Чиста композиція без шаблонного успадкування:\n   метод базового класу сам бачить тип нащадка",
        "3. Природна рекурсія в лямбдах:\n   [](this auto self, int n) { return self(n-1); }",
        "4. std::forward_like<Self>(member) зберігає\n   константність та rvalue-семантику вихідного виразу"
    ]
    y_p = y_card + 64
    for pt in c23_points:
        bb, _, _ = textbox(cx_r, y_p, pt, size=11, pad=6, fill="#ffffff", stroke="#86efac", sw=1, min_w=card_w - 30)
        out.append(bb)
        y_p += 65

    render(os.path.join(IMG, 'deducing-this-mechanism.svg'), W, H, *out,
           title="Еволюція методів об'єкта: від чотирьох перевантажень до Deducing this")


def fig_monadic_pipeline():
    """Схема залізничної моделі (Railway-oriented) для std::expected та std::optional."""
    W, H = 960, 420
    out = []

    out.append(text(W / 2, 50, "Монадичний потік обробки значень: щаслива колія проти автоматичного відгалуження помилок", size=13, color=MUTED))

    y_val = 140
    y_err = 290

    out.append(line(70, y_val, 890, y_val, color=FIELD, sw=3))
    out.append(text(70, y_val - 25, "Колія значення (T)", size=13, color=FIELD, bold=True, anchor="start"))

    out.append(line(70, y_err, 890, y_err, color=POS, sw=3))
    out.append(text(70, y_err + 35, "Колія помилки (E)", size=13, color=POS, bold=True, anchor="start"))

    steps = [
        {"x": 160, "name": "Вхідний виклик", "type": "expected<T, E>"},
        {"x": 380, "name": "and_then(parse)", "type": "T1 -> expected<T2, E>"},
        {"x": 600, "name": "transform(validate)", "type": "T2 -> T3"},
        {"x": 820, "name": "or_else(fallback)", "type": "Обробка помилки"}
    ]

    for st in steps:
        sx = st["x"]

        out.append(circle(sx, y_val, 16, fill="#ffffff", stroke=FIELD, sw=2.5))
        out.append(textbox(sx, y_val - 50, st["name"], size=12, pad=5, fill="#f0fdf4", stroke=FIELD, bold=True)[0])
        out.append(text(sx, y_val + 30, st["type"], size=10, color=MUTED))

        out.append(circle(sx, y_err, 14, fill="#ffffff", stroke=POS, sw=2.5))

    out.append(arrow(160, y_val + 16, 160, y_err - 16, color=POS, sw=2))
    out.append(textbox(205, (y_val + y_err) / 2 - 15, "Якщо помилка:\nобхід and_then", size=10, pad=4, fill="#fff5f5", stroke=POS)[0])

    out.append(arrow(380, y_val + 16, 380, y_err - 16, color=POS, sw=2))
    out.append(arrow(600, y_val + 16, 600, y_err - 16, color=POS, sw=2))

    out.append(arrow(820, y_err - 16, 820, y_val + 16, color=FIELD, sw=2))
    out.append(textbox(860, (y_val + y_err) / 2 + 15, "or_else:\nповернення", size=10, pad=4, fill="#f0fdf4", stroke=FIELD)[0])

    render(os.path.join(IMG, 'monadic-pipeline.svg'), W, H, *out,
           title="Монадичний конвеєр std::expected та std::optional")


def fig_mdspan_layout():
    """Схема відображення багатовимірних індексів у неперервний буфер пам'яті через std::mdspan."""
    W, H = 960, 430
    out = []

    out.append(text(W / 2, 50, "Багатовимірний логічний вимір та його проекція на лінійний масив байтів", size=13, color=MUTED))

    mx_left = 60
    my_top = 95
    cell_w = 70
    cell_h = 45

    out.append(text(mx_left + 140, my_top - 12, "Логічна матриця mdspan: extents<3, 4>", size=13, bold=True))

    matrix_data = [
        ["(0,0)", "(0,1)", "(0,2)", "(0,3)"],
        ["(1,0)", "(1,1)", "(1,2)", "(1,3)"],
        ["(2,0)", "(2,1)", "(2,2)", "(2,3)"]
    ]

    for r in range(3):
        for c in range(4):
            x = mx_left + c * cell_w
            y = my_top + r * cell_h
            fill_c = "#e0f2fe" if r == 1 and c == 2 else "#ffffff"
            stroke_c = NEG if r == 1 and c == 2 else "#cbd5e1"
            sw_c = 2 if r == 1 and c == 2 else 1
            out.append(rect(x, y, cell_w, cell_h, fill=fill_c, stroke=stroke_c, sw=sw_c, rx=4))
            txt_color = NEG if r == 1 and c == 2 else INK
            out.append(text(x + cell_w / 2, y + cell_h / 2 + 4, matrix_data[r][c], size=11, color=txt_color, bold=(r == 1 and c == 2)))

    formula_box_x = 440
    formula_box_y = 120
    out.append(rect(formula_box_x, formula_box_y, 470, 95, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    out.append(text(formula_box_x + 235, formula_box_y + 24, "Формула відображення layout_right (C-порядок):", size=12, bold=True))
    out.append(text(formula_box_x + 235, formula_box_y + 50, "index = row * Stride_Row + col = 1 * 4 + 2 = 6", size=13, color=NEG, bold=True))
    out.append(text(formula_box_x + 235, formula_box_y + 76, "Елемент (1,2) потрапляє в 6-ту комірку фізичного буфера", size=11, color=MUTED))

    out.append(arrow(mx_left + 2 * cell_w + cell_w / 2, my_top + cell_h + cell_h / 2 + 15, formula_box_x + 235, formula_box_y - 8, color=NEG, sw=2))

    buf_x = 60
    buf_y = 300
    bcell_w = 68
    bcell_h = 50

    out.append(text(buf_x + 400, buf_y - 15, "Фізичний неперервний буфер у пам'яті (12 елементів T*):", size=13, bold=True))

    for idx in range(12):
        bx = buf_x + idx * bcell_w
        by = buf_y
        is_target = (idx == 6)
        fill_b = "#e0f2fe" if is_target else "#f1f5f9"
        stroke_b = NEG if is_target else "#94a3b8"
        sw_b = 2.5 if is_target else 1
        out.append(rect(bx, by, bcell_w, bcell_h, fill=fill_b, stroke=stroke_b, sw=sw_b, rx=4))
        out.append(text(bx + bcell_w / 2, by + 20, "idx[%d]" % idx, size=11, color=NEG if is_target else INK, bold=is_target))
        label_coord = "(%d,%d)" % (idx // 4, idx % 4)
        out.append(text(bx + bcell_w / 2, by + 38, label_coord, size=10, color=MUTED))

    out.append(arrow(formula_box_x + 235, formula_box_y + 95, buf_x + 6 * bcell_w + bcell_w / 2, buf_y - 5, color=NEG, sw=2.5))

    render(os.path.join(IMG, 'mdspan-layout.svg'), W, H, *out,
           title="Проекція багатовимірних координат у std::mdspan")


if __name__ == '__main__':
    fig_cpp23_architecture_map()
    fig_deducing_this_mechanism()
    fig_monadic_pipeline()
    fig_mdspan_layout()
    print("Figures generated successfully!")

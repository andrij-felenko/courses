# -*- coding: utf-8 -*-
"""Фігури до теми «Затуляння імен і using-оголошення» (reference/cpp-standards/language)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

FREEZE_FILL = "#fdecea"
OPEN_FILL = "#eaf7ee"
WARN_FILL = "#fff8e6"
MUTED_BG = "#f8f9fa"


# ── 1. Ієрархія пошуку імен і зупинка на першій області ─────────────────────
def fig_lookup_scope():
    W, H = 920, 430
    f = []

    # Заголовок / пояснення
    f.append(text(W / 2, 28, "Пошук імені (Name Lookup) зупиняється на першій же знайденій області", size=15, bold=True))

    # Сходинки областей видимості
    scopes = [
        ("1. Локальний блок (Local block)", "x, y, локальні змінні", False, 80),
        ("2. Похідний клас (Derived class)", "foo(double) — ім'я ЗНАЙДЕНО!", True, 150),
        ("3. Базовий клас (Base class)", "foo(int), foo(string_view) — ЗАТУЛЕНО", False, 220),
        ("4. Простір імен (Namespace)", "foo(char) — пошук сюди не дійде", False, 290),
        ("5. Глобальна область (Global scope)", "foo(float) — пошук сюди не дійде", False, 360),
    ]

    for title, desc, found, y in scopes:
        fill_col = WARN_FILL if found else (FREEZE_FILL if "ЗАТУЛЕНО" in desc else MUTED_BG)
        stroke_col = POS if found else (MUTED if "не дійде" in desc else LINE)
        sw = 2.0 if found else 1.2
        
        box, bw, bh = textbox(280, y, [title, desc], size=13, pad=10,
                              fill=fill_col, stroke=stroke_col, sw=sw, min_w=420)
        f.append(box)

    # Стрілка пошуку зліва знизу вгору
    f.append(arrow(40, 100, 40, 360, color=LINE, sw=2))
    f.append(text(40, 60, "Напрям", size=12, color=MUTED, bold=True))
    f.append(text(40, 75, "пошуку", size=12, color=MUTED, bold=True))

    # Панель праворуч: наслідок для розв'язання перевантажень
    res_box, rw, rh = textbox(720, 220, [
        "Множина кандидатів (Candidate Set):",
        "Лише { Derived::foo(double) }",
        "",
        "Виклик: d.foo(\"рядок\")",
        "✗ Помилка: неможливо перетворити",
        "  const char* на double.",
        "",
        "Base::foo(string_view) навіть",
        "не розглядалася компілятором!"
    ], size=12, pad=14, fill=FREEZE_FILL, stroke=POS, sw=2, min_w=280)
    f.append(res_box)

    # Стрілка від знайденої області до результату
    f.append(arrow(500, 150, 570, 170, color=POS, sw=2))

    render(os.path.join(IMG, "lookup-scope-hierarchy.svg"), W, H, *f,
           title="Пошук імені зупиняється на першій знайденій області")


# ── 2. Затуляння методів у похідному класі та відновлення через using ───────
def fig_base_derived():
    W, H = 940, 420
    f = []

    f.append(text(W / 2, 28, "Відновлення множини перевантажень через using Base::foo", size=15, bold=True))

    # Ліва колонка: без using (затуляння)
    f.append(text(240, 65, "Без using: Затуляння імен", size=14, color=POS, bold=True))
    
    b1, w1, h1 = textbox(240, 130, [
        "struct Base {",
        "    void foo(int);",
        "    void foo(string_view);",
        "};"
    ], size=12, pad=10, fill=MUTED_BG, stroke=LINE, min_w=300)
    
    d1, wd1, hd1 = textbox(240, 230, [
        "struct Derived : Base {",
        "    void foo(double); // затуляє Base::foo",
        "};"
    ], size=12, pad=10, fill=FREEZE_FILL, stroke=POS, sw=1.8, min_w=300)
    
    r1, wr1, hr1 = textbox(240, 340, [
        "d.foo(3.14);   // ✓ Derived::foo(double)",
        "d.foo(10);     // ⚠ Derived::foo(10.0) [int->double]",
        "d.foo(\"hi\");   // ✗ Помилка компіляції!"
    ], size=12, pad=10, fill=BG, stroke=MUTED, min_w=300)
    
    f += [b1, d1, r1]
    f.append(arrow(240, 170, 240, 195, color=POS, sw=1.5))
    f.append(arrow(240, 270, 240, 295, color=LINE, sw=1.5))

    # Розділювач
    f.append(line(470, 55, 470, 395, color=LINE, sw=1.2, dash="4,4"))

    # Права колонка: з using (об'єднання перевантажень)
    f.append(text(700, 65, "З using: Об'єднана множина кандидатів", size=14, color=FIELD, bold=True))
    
    b2, w2, h2 = textbox(700, 130, [
        "struct Base {",
        "    void foo(int);",
        "    void foo(string_view);",
        "};"
    ], size=12, pad=10, fill=MUTED_BG, stroke=LINE, min_w=320)
    
    d2, wd2, hd2 = textbox(700, 230, [
        "struct Derived : Base {",
        "    using Base::foo; // втягує всі перевантаження",
        "    void foo(double);",
        "};"
    ], size=12, pad=10, fill=OPEN_FILL, stroke=FIELD, sw=1.8, min_w=320)
    
    r2, wr2, hr2 = textbox(700, 340, [
        "d.foo(3.14);   // ✓ Derived::foo(double)",
        "d.foo(10);     // ✓ Base::foo(int) [точний збіг]",
        "d.foo(\"hi\");   // ✓ Base::foo(string_view)"
    ], size=12, pad=10, fill=BG, stroke=FIELD, min_w=320)
    
    f += [b2, d2, r2]
    f.append(arrow(700, 170, 700, 195, color=FIELD, sw=1.5))
    f.append(arrow(700, 270, 700, 295, color=FIELD, sw=1.5))

    render(os.path.join(IMG, "base-derived-hiding.svg"), W, H, *f,
           title="Затуляння методів базового класу та їх відновлення через using")


# ── 3. using-оголошення проти using-директиви ──────────────────────────────
def fig_decl_vs_directive():
    W, H = 940, 410
    f = []

    f.append(text(W / 2, 28, "using-оголошення (введення в область) vs using-директива (видимість у предку)", size=15, bold=True))

    # Ліворуч: using-оголошення
    f.append(text(240, 65, "using-оголошення: using A::f;", size=14, color=FIELD, bold=True))
    
    box_decl, w_d, h_d = textbox(240, 150, [
        "namespace A { void f(double); }",
        "void f(int); // глобальна функція",
        "",
        "void test() {",
        "    using A::f; // вносить f у поточну область test",
        "    f(1);       // викликає A::f(double)",
        "}"
    ], size=12, pad=12, fill=OPEN_FILL, stroke=FIELD, sw=1.8, min_w=320)
    
    res_decl, wr_d, hr_d = textbox(240, 295, [
        "Механізм:",
        "• f стає локальним символом у test().",
        "• Повністю ЗАТУЛЯЄ глобальну f(int).",
        "• Overload resolution обирає A::f(double)."
    ], size=12, pad=10, fill=MUTED_BG, stroke=LINE, min_w=320)
    
    f += [box_decl, res_decl]

    # Розділювач
    f.append(line(470, 55, 470, 385, color=LINE, sw=1.2, dash="4,4"))

    # Праворуч: using-директива
    f.append(text(700, 65, "using-директива: using namespace A;", size=14, color=POS, bold=True))
    
    box_dir, w_dir, h_dir = textbox(700, 150, [
        "namespace A { void f(double); }",
        "void f(int); // глобальна функція",
        "",
        "void test() {",
        "    using namespace A; // вільний доступ на рівні спільного предка",
        "    f(1); // ✗ Неоднозначність (ambiguity)!",
        "}"
    ], size=12, pad=12, fill=FREEZE_FILL, stroke=POS, sw=1.8, min_w=320)
    
    res_dir, wr_dir, hr_dir = textbox(700, 295, [
        "Механізм:",
        "• Символи A стають видимими в найближчому",
        "  спільному просторі-предку (тут: global).",
        "• Обидві f(int) та f(double) на одному рівні!",
        "• Виклик f(1) спричиняє помилку неоднозначності."
    ], size=12, pad=10, fill=MUTED_BG, stroke=LINE, min_w=320)
    
    f += [box_dir, res_dir]

    render(os.path.join(IMG, "declaration-vs-directive.svg"), W, H, *f,
           title="Різниця механізмів using-оголошення та using-директиви")


# ── 4. Зміна прав доступу за допомогою using ────────────────────────────────
def fig_access_control():
    W, H = 920, 390
    f = []

    f.append(text(W / 2, 28, "Переналаштування прав доступу в похідному класі через using", size=15, bold=True))

    # Базовий клас
    b_box, bw, bh = textbox(220, 170, [
        "class SocketBase {",
        "protected:",
        "    void set_timeout(int ms);",
        "    void raw_write(span<byte>);",
        "public:",
        "    void close();",
        "};"
    ], size=12, pad=12, fill=MUTED_BG, stroke=LINE, min_w=280)
    f.append(b_box)

    # Похідний клас
    d_box, dw, dh = textbox(670, 170, [
        "class TcpStream : private SocketBase {",
        "public:",
        "    // 1. Відкриваємо protected-метод назовні",
        "    using SocketBase::set_timeout;",
        "",
        "    // 2. Відкриваємо окремі public-методи з private бази",
        "    using SocketBase::close;",
        "",
        "    // raw_write лишається схованою в private",
        "};"
    ], size=12, pad=12, fill=OPEN_FILL, stroke=FIELD, sw=1.8, min_w=380)
    f.append(d_box)

    # Стрілки адаптації
    f.append(arrow(370, 140, 470, 140, color=FIELD, sw=1.8))
    f.append(text(420, 125, "робимо public", size=12, color=FIELD, bold=True))

    f.append(arrow(370, 200, 470, 200, color=FIELD, sw=1.8))
    f.append(text(420, 185, "зберігаємо public", size=12, color=FIELD, bold=True))

    f.append(text(W / 2, 340, "Права доступу визначаються секцією (public/protected/private), у якій стоїть using", size=13, color=MUTED))

    render(os.path.join(IMG, "access-control-reshape.svg"), W, H, *f,
           title="Зміна прав доступу до членів базового класу через using")


if __name__ == "__main__":
    fig_lookup_scope()
    fig_base_derived()
    fig_decl_vs_directive()
    fig_access_control()
    print("All figures generated successfully.")

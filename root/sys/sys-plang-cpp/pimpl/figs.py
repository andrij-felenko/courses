# -*- coding: utf-8 -*-
"""Фігури до теми «PIMPL: сховати реалізацію за вказівником»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

HEAD = "#eceff3"
OK   = "#e8f6ee"
WARN = "#fff7e6"
HOT  = "#fdecea"


# ── 1. Брандмауер компіляції: пряме включення проти PIMPL ───────────────────
def fig_compilation_firewall():
    W, H = 1000, 480
    f = []

    # Ліва частина: пряме включення
    f.append(text(250, 36, "Пряме оголошення полів у заголовку",
                  size=14, color=POS, bold=True))
    f.append(fitbox(60, 60, 380, 70,
                    "Widget.h (містить приватні поля й важкі заголовки)\n#include <vector>, #include <windows.h>, #include <openssl/ssl.h>",
                    size=11, fill=HOT, stroke=POS))

    f.append(arrow(150, 134, 110, 200, color=POS))
    f.append(arrow(250, 134, 250, 200, color=POS))
    f.append(arrow(350, 134, 390, 200, color=POS))

    f.append(fitbox(50, 205, 120, 50, "client_a.cpp\n(перезбірка)", size=11, fill=HOT))
    f.append(fitbox(190, 205, 120, 50, "client_b.cpp\n(перезбірка)", size=11, fill=HOT))
    f.append(fitbox(330, 205, 120, 50, "client_c.cpp\n(перезбірка)", size=11, fill=HOT))

    f.append(fitbox(50, 280, 400, 54,
                    "Зміна одного приватного поля в Widget.h змушує\nперекомпілювати всі одиниці трансляції проєкту",
                    size=11, fill=FILL, color=MUTED))

    # Розділювач
    f.append(line(490, 30, 490, 430, color=MUTED, sw=1, dash="6 5"))

    # Права частина: PIMPL брандмауер
    f.append(text(740, 36, "Брандмауер компіляції (PIMPL)",
                  size=14, color=FIELD, bold=True))
    f.append(fitbox(540, 60, 400, 70,
                    "Widget.h (публічний інтерфейс + struct Impl;)\nжодних важких залежностей, лише std::unique_ptr<Impl> pImpl_;",
                    size=11, fill=OK, stroke=FIELD))

    # Клієнти не перезбираються
    f.append(arrow(600, 134, 570, 200, color=MUTED))
    f.append(arrow(740, 134, 740, 200, color=MUTED))
    f.append(arrow(880, 134, 910, 200, color=MUTED))

    f.append(fitbox(520, 205, 120, 50, "client_a.cpp\n(без змін)", size=11, fill=FILL))
    f.append(fitbox(680, 205, 120, 50, "client_b.cpp\n(без змін)", size=11, fill=FILL))
    f.append(fitbox(840, 205, 120, 50, "client_c.cpp\n(без змін)", size=11, fill=FILL))

    # Стрілка на Widget.cpp
    f.append(fitbox(610, 285, 260, 64,
                    "Widget.cpp (повне struct Impl)\nвключає <vector>, <openssl/ssl.h>",
                    size=11, fill=OK, stroke=FIELD))
    f.append(arrow(740, 258, 740, 282, color=FIELD))

    f.append(fitbox(530, 370, 420, 54,
                    "Зміна полів Impl у Widget.cpp вимагає компіляції\nлише одного файла Widget.cpp. Клієнти лише лінкуються.",
                    size=11, fill=OK, color=INK))

    f.append(text(500, 460,
                  "PIMPL діє як захисна стіна: деталі реалізації ізольовані в одному .cpp",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'compilation-firewall.svg'), W, H, *f,
           title="Брандмауер компіляції: пряме включення проти PIMPL")


# ── 2. Розташування в пам'яті: Звичайний ↔ Класичний PIMPL ↔ Fast PIMPL ─────
def fig_memory_layout_pimpl():
    W, H = 1000, 500
    f = []

    # 1. Звичайний об'єкт
    f.append(fitbox(50, 40, 280, 36, "1. Пряме збереження полів", size=13, fill=HEAD, bold=True))
    f.append(fitbox(50, 90, 280, 40, "Стек / Пам'ять власника (Widget)", size=11, fill=FILL, color=MUTED))
    f.append(fitbox(50, 135, 280, 42, "int id_ (4 байта)", size=12, fill=BG))
    f.append(fitbox(50, 180, 280, 42, "std::string name_ (32 байта)", size=12, fill=BG))
    f.append(fitbox(50, 225, 280, 42, "SSL_CTX* ctx_ (8 байтів)", size=12, fill=BG))
    f.append(fitbox(50, 270, 280, 42, "std::vector<int> buf_ (24 байта)", size=12, fill=BG))
    f.append(fitbox(50, 325, 280, 60, "Разом: sizeof(Widget) = 72 байта\nЗміна поля змінює розмір об'єкта на стеку!", size=11, fill=HOT))

    # 2. Класичний PIMPL
    f.append(fitbox(360, 40, 280, 36, "2. Класичний PIMPL (std::unique_ptr)", size=13, fill=HEAD, bold=True))
    f.append(fitbox(360, 90, 280, 40, "Стек (Widget)", size=11, fill=FILL, color=MUTED))
    f.append(fitbox(360, 135, 280, 50, "std::unique_ptr<Impl> pImpl_\n(8 байтів адреси)", size=12, fill=OK, stroke=FIELD))
    f.append(arrow(500, 188, 500, 220, color=FIELD))
    f.append(fitbox(360, 225, 280, 130, "Динамічна купа (Купа/Heap)\nstruct Impl (72 байта):\n· int id_\n· std::string name_\n· SSL_CTX* ctx_\n· std::vector<int> buf_", size=11, fill=BG))
    f.append(fitbox(360, 370, 280, 60, "sizeof(Widget) = 8 байтів стабільно\nЦіна: heap-алокація + розіменування вказівника", size=11, fill=OK))

    # 3. Fast PIMPL (Inline буфер)
    f.append(fitbox(670, 40, 280, 36, "3. Fast PIMPL (Фіксований буфер)", size=13, fill=HEAD, bold=True))
    f.append(fitbox(670, 90, 280, 40, "Стек (Widget)", size=11, fill=FILL, color=MUTED))
    f.append(fitbox(670, 135, 280, 140, "alignas(8) std::byte storage_[96]\n\n[Усередині буфера через placement new]\nstruct Impl (72 байта)\n+ 24 байти запасу під майбутні поля", size=11, fill=WARN, stroke=LINE))
    f.append(fitbox(670, 290, 280, 70, "Купа не задіяна (0 алокацій)\nПрямий доступ за зсувом без додаткового стрибка", size=11, fill=OK))
    f.append(fitbox(670, 370, 280, 60, "sizeof(Widget) = 96 байтів фіксовано\nОбмеження: фіксована стеля розміру Impl", size=11, fill=WARN))

    f.append(text(500, 475,
                  "Класичний PIMPL обирає повну ізоляцію через купу; Fast PIMPL усуває алокацію ціною резерву на стеку",
                  size=11, color=MUTED))

    render(os.path.join(OUT, 'memory-layout-pimpl.svg'), W, H, *f,
           title="Розташування об'єкта в пам'яті: звичайний клас, PIMPL і Fast PIMPL")


# ── 3. Пастка неповного типу при руйнуванні unique_ptr ──────────────────────
def fig_incomplete_type_trap():
    W, H = 980, 460
    f = []

    # Заголовок зверху
    f.append(text(490, 32, "Чому деструктор класу з PIMPL не можна генерувати за замовчуванням у заголовку",
                  size=14, color=INK, bold=True))

    # Лівий блок: помилковий підхід
    f.append(fitbox(40, 60, 420, 36, "Помилка: деструктор у заголовку (або неявний)", size=12, fill=HOT, color=POS, bold=True))
    f.append(fitbox(40, 105, 420, 120,
                    "// Widget.h\nclass Widget {\n    struct Impl; // неповний тип (Incomplete Type)\n    std::unique_ptr<Impl> pImpl_;\npublic:\n    Widget();\n    ~Widget() = default; // помилка інстанціювання!\n};",
                    size=11, fill=BG, stroke=POS))

    f.append(arrow(250, 228, 250, 260, color=POS))

    f.append(fitbox(40, 265, 420, 140,
                    "// main.cpp (#include \"Widget.h\")\nvoid foo() { Widget w; } // на виході викликається ~Widget()\n\n~unique_ptr<Impl>() викликає std::default_delete<Impl>::operator()\nякий робить static_assert(sizeof(Impl) > 0) або delete (Impl*);\nКомпілятор бачить: sizeof(Impl) невідомий → ПОМИЛКА КОМПІЛЯЦІЇ!",
                    size=11, fill=HOT, color=POS))

    # Правий блок: коректний підхід
    f.append(fitbox(520, 60, 420, 36, "Правильно: деструктор визначений у .cpp файлі", size=12, fill=OK, color=FIELD, bold=True))
    f.append(fitbox(520, 105, 420, 120,
                    "// Widget.h\nclass Widget {\n    struct Impl;\n    std::unique_ptr<Impl> pImpl_;\npublic:\n    Widget();\n    ~Widget(); // лише оголошення!\n};",
                    size=11, fill=BG, stroke=FIELD))

    f.append(arrow(730, 228, 730, 260, color=FIELD))

    f.append(fitbox(520, 265, 420, 140,
                    "// Widget.cpp\n#include \"Widget.h\"\nstruct Widget::Impl {\n    // повне визначення структури: розмір відомий!\n};\nWidget::Widget() : pImpl_(std::make_unique<Impl>()) {}\nWidget::~Widget() = default; // тепер Impl повний, delete коректний!",
                    size=11, fill=OK, color=INK))

    f.append(text(490, 435,
                  "std::default_delete вимагає повного типу в точці інстанціювання деструктора",
                  size=12, color=MUTED))

    render(os.path.join(OUT, 'incomplete-type-trap.svg'), W, H, *f,
           title="Пастка неповного типу при руйнуванні unique_ptr")


if __name__ == '__main__':
    fig_compilation_firewall()
    fig_memory_layout_pimpl()
    fig_incomplete_type_trap()
    print("All figures generated successfully.")

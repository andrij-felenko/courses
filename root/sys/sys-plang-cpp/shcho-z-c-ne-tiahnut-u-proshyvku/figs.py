# -*- coding: utf-8 -*-
"""Фігури до теми «Що з C++ не тягнуть у прошивку: винятки, RTTI, купа, віртуальні виклики»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_exceptions_unwind_overhead():
    """Накладні витрати розгортання стеку: таблиці та пошук обробника проти повернення коду."""
    W, H = 1060, 420
    out = []

    # Ліва колонка — Механізм винятків (Table-driven Unwinding)
    lx = 270
    b_ex_title, _, _ = textbox(lx, 50, "Механізм винятків (Itanium / ARM EHABI)", size=15, pad=12, fill="#fdecea", stroke=POS, bold=True)
    out.append(b_ex_title)

    b_flash, _, _ = textbox(lx, 130, ["Таблиці Flash (.ARM.exidx / .ARM.extab):", "• Описи діапазонів адрес функцій", "• Інструкції відновлення регістрів", "• Вказівники на Landing Pads (+15-30% Flash)"],
                            size=12, pad=10, fill="#ffffff", stroke=LINE)
    b_throw, _, _ = textbox(lx, 230, ["Виклик throw Error{}:", "1. __cxa_allocate_exception (динамічна пам'ять)", "2. Personality Routine сканує таблиці розгортання", "3. Відновлення регістрів стек-фрейм за фреймом"],
                            size=12, pad=10, fill="#fff5f5", stroke=POS)
    b_cost, _, _ = textbox(lx, 340, ["Результат у прошивці:", "• Недетермінована затримка (500–5000 тактів)", "• Роздутий двійковий файл через таблиці"],
                           size=12, pad=10, fill="#fdecea", stroke=POS, bold=True)
    out.append(b_flash)
    out.append(b_throw)
    out.append(b_cost)
    out.append(arrow(lx, 175, lx, 195, color=POS))
    out.append(arrow(lx, 280, lx, 305, color=POS))

    # Розділювальна лінія
    out.append(line(530, 30, 530, 390, color=MUTED, dash="4,4"))

    # Права колонка — Детерміновані значення помилок (std::expected / коди)
    rx = 790
    b_exp_title, _, _ = textbox(rx, 50, "Значення результату (std::expected / статус)", size=15, pad=12, fill="#eaf7ee", stroke=FIELD, bold=True)
    out.append(b_exp_title)

    b_layout, _, _ = textbox(rx, 130, ["Розміщення в регістрах або на стеку:", "• Об'єднання union { T val; E err; } + bool flag", "• Без допоміжних таблиць метаданих у Flash", "• Нульові накладні витрати на рівні бінарника"],
                             size=12, pad=10, fill="#ffffff", stroke=LINE)
    b_return, _, _ = textbox(rx, 230, ["Повернення значення:", "1. Запис коду/значення в регістри R0-R1", "2. Пряма інструкція процесора BX LR", "3. Умовний перехід за прапорцем (CBZ / CBNZ)"],
                             size=12, pad=10, fill="#f4fbf6", stroke=FIELD)
    b_res_good, _, _ = textbox(rx, 340, ["Результат у прошивці:", "• Жорсткий детермінізм (1–3 такти процесора)", "• Компактний машинний код без схованих викликів"],
                               size=12, pad=10, fill="#eaf7ee", stroke=FIELD, bold=True)
    out.append(b_layout)
    out.append(b_return)
    out.append(b_res_good)
    out.append(arrow(rx, 175, rx, 195, color=FIELD))
    out.append(arrow(rx, 280, rx, 305, color=FIELD))

    render(os.path.join(IMG, 'exceptions-unwind-overhead.svg'), W, H, *out,
           title="Порівняння розгортання винятків та передачі помилок через значення")


def fig_vtable_vs_crtp_memory():
    """Порівняння структури об'єкта й викликів: vtable проти CRTP."""
    W, H = 1060, 390
    out = []

    # Ліва частина — Virtual Dispatch
    lx = 270
    b_v_title, _, _ = textbox(lx, 50, "Динамічний поліморфізм (vptr + vtable)", size=15, pad=12, fill="#fdecea", stroke=POS, bold=True)
    out.append(b_v_title)

    b_v_obj, _, _ = textbox(lx, 130, ["Об'єкт у SRAM (+4 або +8 байтів):", "[ vptr = &vtable | data_field ]"],
                            size=12, pad=10, fill="#ffffff", stroke=LINE)
    b_v_tbl, _, _ = textbox(lx, 215, ["Таблиця vtable у Flash (Flash .rodata):", "[ typeinfo* | &UartDriver::send ]"],
                            size=12, pad=10, fill="#ffffff", stroke=LINE)
    b_v_call, _, _ = textbox(lx, 310, ["Виклик uart->send(byte):", "• LDR R3, [R0] (завантаження vptr)", "• LDR R3, [R3, #4] (адреса методу)", "• BLX R3 (непрямий перехід, скидання конвеєра)"],
                             size=12, pad=10, fill="#fdecea", stroke=POS)
    out.append(b_v_obj)
    out.append(b_v_tbl)
    out.append(b_v_call)
    out.append(arrow(lx, 160, lx, 185, color=POS))
    out.append(arrow(lx, 250, lx, 275, color=POS))

    # Розділювальна лінія
    out.append(line(530, 30, 530, 365, color=MUTED, dash="4,4"))

    # Права частина — CRTP / Static Dispatch
    rx = 790
    b_c_title, _, _ = textbox(rx, 50, "Статичний поліморфізм (CRTP / Шаблони)", size=15, pad=12, fill="#eaf7ee", stroke=FIELD, bold=True)
    out.append(b_c_title)

    b_c_obj, _, _ = textbox(rx, 130, ["Об'єкт у SRAM (0 байтів оверхеду):", "[ data_field ] (жодного службового вказівника)"],
                            size=12, pad=10, fill="#ffffff", stroke=LINE)
    b_c_tbl, _, _ = textbox(rx, 215, ["Таблиця у Flash:", "ВІДСУТНЯ (компілятор знає точний тип)"],
                            size=12, pad=10, fill="#ffffff", stroke=LINE)
    b_c_call, _, _ = textbox(rx, 310, ["Виклик uart.send(byte):", "• Прямий виклик BL або повний інлайнінг (0 тактів)", "• Оптимізація регістрів та видалення мертвого коду", "• Повна передбачуваність часу виконання"],
                             size=12, pad=10, fill="#eaf7ee", stroke=FIELD)
    out.append(b_c_obj)
    out.append(b_c_tbl)
    out.append(b_c_call)
    out.append(arrow(rx, 160, rx, 185, color=FIELD))
    out.append(arrow(rx, 250, rx, 275, color=FIELD))

    render(os.path.join(IMG, 'vtable-vs-crtp-memory.svg'), W, H, *out,
           title="Розкладка в пам'яті та механізм виклику: vtable проти CRTP")


def fig_heap_fragmentation_baremetal():
    """Фрагментація динамічної купи в мікроконтролері проти статичного пулу."""
    W, H = 1060, 410
    out = []

    # Верхня частина — Фрагментація купи
    b_f_title, _, _ = textbox(530, 45, "Динамічна купа (malloc / new): прогресуюча фрагментація SRAM", size=15, pad=10, fill="#fdecea", stroke=POS, bold=True)
    out.append(b_f_title)

    # Карта пам'яті купи
    # Загальний блок SRAM: x=100 .. 960, w=860, y=85, h=45
    out.append(rect(100, 85, 860, 45, fill="#ffffff", stroke=LINE, sw=1.5))
    # Зайняті блоки (червоні) та вільні дірки (зелені/сірі)
    out.append(rect(105, 90, 160, 35, fill="#ffcccc", stroke=POS, sw=1))
    out.append(text(185, 112, "Зайнято: 256 Б", size=11, color=INK))

    out.append(rect(270, 90, 80, 35, fill="#e8f5e9", stroke=FIELD, sw=1))
    out.append(text(310, 112, "Дірка 96 Б", size=11, color=INK))

    out.append(rect(355, 90, 210, 35, fill="#ffcccc", stroke=POS, sw=1))
    out.append(text(460, 112, "Зайнято: 512 Б", size=11, color=INK))

    out.append(rect(570, 90, 110, 35, fill="#e8f5e9", stroke=FIELD, sw=1))
    out.append(text(625, 112, "Дірка 128 Б", size=11, color=INK))

    out.append(rect(685, 90, 180, 35, fill="#ffcccc", stroke=POS, sw=1))
    out.append(text(775, 112, "Зайнято: 384 Б", size=11, color=INK))

    out.append(rect(870, 90, 85, 35, fill="#e8f5e9", stroke=FIELD, sw=1))
    out.append(text(912, 112, "Дірка 64 Б", size=11, color=INK))

    b_fail, _, _ = textbox(530, 165, "Запит malloc(200 байтів) зазнає невдачі (NULL), хоча сумарно вільно 288 байтів (96 + 128 + 64)!",
                           size=12, pad=8, fill="#fdecea", stroke=POS, bold=True)
    out.append(b_fail)

    # Лінія розділення
    out.append(line(80, 205, 980, 205, color=MUTED, dash="4,4"))

    # Нижня частина — Фіксований статичний пул
    b_p_title, _, _ = textbox(530, 240, "Альтернатива: Статичний пул однакових блоків (Fixed-Size Pool Allocator)", size=15, pad=10, fill="#eaf7ee", stroke=FIELD, bold=True)
    out.append(b_p_title)

    out.append(rect(100, 280, 860, 45, fill="#ffffff", stroke=LINE, sw=1.5))
    # Рівномірні слоти по 135px
    for i, (status, label) in enumerate([("busy", "Слот 1 [Зайнято]"), ("free", "Слот 2 [Вільний]"), ("busy", "Слот 3 [Зайнято]"),
                                         ("free", "Слот 4 [Вільний]"), ("busy", "Слот 5 [Зайнято]"), ("free", "Слот 6 [Вільний]")]):
        bx = 105 + i * 142
        fill_c = "#ffcccc" if status == "busy" else "#eaf7ee"
        strk_c = POS if status == "busy" else FIELD
        out.append(rect(bx, 285, 138, 35, fill=fill_c, stroke=strk_c, sw=1))
        out.append(text(bx + 69, 307, label, size=11, color=INK))

    b_pool_desc, _, _ = textbox(530, 360, "Виділення та звільнення за O(1) тактів: нульова фрагментація, повний детермінізм, розміщення у .bss",
                                size=12, pad=8, fill="#eaf7ee", stroke=FIELD, bold=True)
    out.append(b_pool_desc)

    render(os.path.join(IMG, 'heap-fragmentation-baremetal.svg'), W, H, *out,
           title="Фрагментація динамічної купи проти статичного блокового пулу")


if __name__ == '__main__':
    fig_exceptions_unwind_overhead()
    fig_vtable_vs_crtp_memory()
    fig_heap_fragmentation_baremetal()
    print("ok")

# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. ffi-boundary: Межа FFI між керованим середовищем і C ABI ───────────────
def fig_ffi_boundary():
    W, H = 880, 430
    p = []

    # Тло та секції
    p.append(rect(20, 20, 250, 390, fill="#f0f4f9", stroke=NEG, sw=1.5, rx=8))
    p.append(rect(290, 20, 300, 390, fill="#fdfbf4", stroke=LINE, sw=1.5, rx=8))
    p.append(rect(610, 20, 250, 390, fill="#f9f0ee", stroke=POS, sw=1.5, rx=8))

    # Заголовки секцій
    p.append(text(145, 50, "Керований рантайм", size=15, bold=True, color=NEG))
    p.append(text(145, 68, "(Python, Java, Go, Node.js)", size=11, color=MUTED))

    p.append(text(440, 50, "Міст FFI / Маршалінг", size=15, bold=True, color=INK))
    p.append(text(440, 68, "(libffi, ctypes, cgo, JNI)", size=11, color=MUTED))

    p.append(text(735, 50, "Рідний C ABI / Залізо", size=15, bold=True, color=POS))
    p.append(text(735, 68, "(C, C++, Rust cdylib, SO/DLL)", size=11, color=MUTED))

    # Елементи лівої секції (Кероване середовище)
    b, _, _ = textbox(145, 115, ["Динамічні об'єкти / VM", "PyObject, Java Heap, Go GC"], size=12, pad=8, fill=BG, stroke=NEG, min_w=220)
    p.append(b)
    b, _, _ = textbox(145, 195, ["Збирач сміття (GC)", "Переміщує об'єкти в пам'яті"], size=12, pad=8, fill=BG, stroke=NEG, min_w=220)
    p.append(b)
    b, _, _ = textbox(145, 275, ["Керовані рядки й списки", "UTF-16, товсті зрізи, COW"], size=12, pad=8, fill=BG, stroke=NEG, min_w=220)
    p.append(b)
    b, _, _ = textbox(145, 355, ["Винятки мови (Exceptions)", "Розкрутка стека рантайму"], size=12, pad=8, fill=BG, stroke=NEG, min_w=220)
    p.append(b)

    # Елементи центральної секції (Шар перетворення)
    b, _, _ = textbox(440, 115, ["Маршалінг типів", "int/float → регістри ABI"], size=12, pad=8, fill=BG, stroke=LINE, min_w=260)
    p.append(b)
    b, _, _ = textbox(440, 195, ["Фіксація пам'яті (Pinning)", "Захист адреси від ходу GC"], size=12, pad=8, fill=BG, stroke=LINE, min_w=260)
    p.append(b)
    b, _, _ = textbox(440, 275, ["Конвертація буферів", "Копіювання або нуль-термінатор"], size=12, pad=8, fill=BG, stroke=LINE, min_w=260)
    p.append(b)
    b, _, _ = textbox(440, 355, ["Перехоплення помилок", "Переклад кодів / сигналів OS"], size=12, pad=8, fill=BG, stroke=LINE, min_w=260)
    p.append(b)

    # Елементи правої секції (Рідний код)
    b, _, _ = textbox(735, 115, ["Сирий C-виклик", "Регістри RDI..R9 / RCX..R9"], size=12, pad=8, fill=BG, stroke=POS, min_w=220)
    p.append(b)
    b, _, _ = textbox(735, 195, ["Статична сира адреса", "Фіксований покажчик (void*)"], size=12, pad=8, fill=BG, stroke=POS, min_w=220)
    p.append(b)
    b, _, _ = textbox(735, 275, ["C-структури / C-string", "ASCII/UTF-8 з \\0, набивка ABI"], size=12, pad=8, fill=BG, stroke=POS, min_w=220)
    p.append(b)
    b, _, _ = textbox(735, 355, ["Ручне керування пам'яттю", "malloc() / free(), errno"], size=12, pad=8, fill=BG, stroke=POS, min_w=220)
    p.append(b)

    # Стрілки взаємодії
    p.append(arrow(255, 115, 310, 115, color=NEG, sw=1.8))
    p.append(arrow(570, 115, 625, 115, color=POS, sw=1.8))

    p.append(arrow(255, 195, 310, 195, color=NEG, sw=1.8))
    p.append(arrow(570, 195, 625, 195, color=POS, sw=1.8))

    p.append(arrow(255, 275, 310, 275, color=NEG, sw=1.8))
    p.append(arrow(570, 275, 625, 275, color=POS, sw=1.8))

    p.append(arrow(255, 355, 310, 355, color=NEG, sw=1.8))
    p.append(arrow(570, 355, 625, 355, color=POS, sw=1.8))

    render(os.path.join(OUT, "ffi-boundary.svg"), W, H, *p)


# ── 2. calling-conventions-x64: System V AMD64 проти Microsoft x64 ────────────
def fig_calling_conventions_x64():
    W, H = 880, 450
    p = []

    # Заголовок блоку System V AMD64
    p.append(rect(20, 20, 840, 190, fill="#f4f7fc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(40, 48, "System V AMD64 ABI (Linux, macOS, FreeBSD)", size=14, bold=True, color=NEG, anchor="start"))
    p.append(text(40, 68, "6 цілочисельних регістрів для аргументів + XMM0..7 для чисел з плаваючою комою", size=11, color=MUTED, anchor="start"))

    # Блоки регістрів System V
    regs_sysv = [
        ("1-й", "RDI"), ("2-й", "RSI"), ("3-й", "RDX"),
        ("4-й", "RCX"), ("5-й", "R8"),  ("6-й", "R9"),
        ("7-й+", "Стек (16B)")
    ]
    x_start = 40
    for i, (arg_n, reg_name) in enumerate(regs_sysv):
        bx = x_start + i * 114
        fill_col = "#e3ecf9" if i < 6 else "#f9e8e5"
        stroke_col = NEG if i < 6 else POS
        p.append(rect(bx, 90, 106, 60, fill=fill_col, stroke=stroke_col, sw=1.3, rx=5))
        p.append(text(bx + 53, 112, arg_n, size=11, bold=False, color=MUTED))
        p.append(text(bx + 53, 134, reg_name, size=12, bold=True, color=INK))

    p.append(text(40, 178, "Результат: RAX (цілі / вказівники), RDX (друге 64-бітне слово), XMM0 (float/double)", size=11, color=INK, anchor="start"))
    p.append(text(40, 196, "Red Zone: 128 байтів нижче RSP захищено від переривань (лише користувацький простір)", size=11, color=MUTED, anchor="start"))

    # Заголовок блоку Microsoft x64
    p.append(rect(20, 230, 840, 200, fill="#fdf8f4", stroke=POS, sw=1.5, rx=8))
    p.append(text(40, 258, "Microsoft x64 ABI (Windows)", size=14, bold=True, color=POS, anchor="start"))
    p.append(text(40, 278, "4 регістри для аргументів + обов'язковий Shadow Space (32 байти на стеку)", size=11, color=MUTED, anchor="start"))

    # Блоки регістрів Win64
    regs_win = [
        ("1-й", "RCX / XMM0"), ("2-й", "RDX / XMM1"),
        ("3-й", "R8 / XMM2"),  ("4-й", "R9 / XMM3"),
        ("Тінь", "Shadow Space (32B)"),
        ("5-й+", "Стек")
    ]
    x_start_w = 40
    widths = [118, 118, 118, 118, 155, 110]
    cur_x = x_start_w
    for i, (arg_n, reg_name) in enumerate(regs_win):
        w_box = widths[i]
        fill_col = "#faece8" if i < 4 else ("#fff4d8" if i == 4 else "#f3f3f3")
        stroke_col = POS if i < 4 else (LINE if i == 4 else MUTED)
        p.append(rect(cur_x, 300, w_box, 60, fill=fill_col, stroke=stroke_col, sw=1.3, rx=5))
        p.append(text(cur_x + w_box / 2, 322, arg_n, size=11, bold=False, color=MUTED))
        p.append(text(cur_x + w_box / 2, 344, reg_name, size=11, bold=True, color=INK))
        cur_x += w_box + 12

    p.append(text(40, 388, "Shadow (Home) Space: викликач зобов'язаний виділити 32 байти на стеку навіть без аргументів!", size=11, bold=True, color=POS, anchor="start"))
    p.append(text(40, 408, "Результат: RAX (цілі/вказівники), XMM0 (float/double); вирівнювання стека строго 16 байтів", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "calling-conventions-x64.svg"), W, H, *p)


# ── 3. gc-pinning-hazard: Небезпека переміщення GC та Pinning ─────────────────
def fig_gc_pinning_hazard():
    W, H = 880, 400
    p = []

    # Ліва колонка: Без Pinning (Аварія)
    p.append(rect(20, 20, 410, 360, fill="#fdf2f0", stroke=POS, sw=1.5, rx=8))
    p.append(text(225, 48, "Без Pinning: Переміщення об'єкта GC", size=13, bold=True, color=POS))
    p.append(text(225, 68, "Компактифікатор дефрагментує купу під час C-виклику", size=10, color=MUTED))

    # Стан 1: C-код отримує покажчик
    p.append(rect(40, 95, 370, 70, fill=BG, stroke=LINE, sw=1.2, rx=5))
    p.append(text(55, 118, "1. C-код отримує сирий вказівник: ptr = 0x1000", size=11, bold=True, anchor="start", color=INK))
    p.append(rect(55, 130, 160, 24, fill="#e8f0fe", stroke=NEG, sw=1, rx=3))
    p.append(text(135, 146, "Об'єкт за адресою 0x1000", size=10, color=NEG))
    p.append(arrow(280, 142, 220, 142, color=POS, sw=1.5))
    p.append(text(330, 146, "C ptr: 0x1000", size=10, bold=True, color=POS))

    # Стан 2: GC переносить об'єкт
    p.append(rect(40, 185, 370, 75, fill=BG, stroke=POS, sw=1.4, rx=5))
    p.append(text(55, 208, "2. GC спрацьовує і переносить дані на 0x2000", size=11, bold=True, anchor="start", color=POS))
    p.append(rect(55, 222, 160, 24, fill="#fdecea", stroke=POS, sw=1, rx=3))
    p.append(text(135, 238, "Нова адреса: 0x2000", size=10, bold=True, color=POS))
    p.append(text(230, 238, "0x1000 тепер сміття!", size=10, italic=True, color=POS, anchor="start"))

    # Стан 3: C-код пише за старою адресою
    p.append(rect(40, 280, 370, 80, fill="#faece8", stroke=POS, sw=1.5, rx=5))
    p.append(text(55, 305, "3. Рідна функція виконує запис: *ptr = 42;", size=11, bold=True, anchor="start", color=POS))
    p.append(text(55, 326, "Запис у 0x1000 руйнує чужий об'єкт у купі", size=10, color=INK, anchor="start"))
    p.append(text(55, 345, "КРАХ: Непередбачуване пошкодження пам'яті (UB)", size=10, bold=True, color=POS, anchor="start"))


    # Права колонка: З Pinning (Безпечно)
    p.append(rect(450, 20, 410, 360, fill="#f0f7f2", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(655, 48, "З Pinning: Фіксація адреси в пам'яті", size=13, bold=True, color=FIELD))
    p.append(text(655, 68, "GC позначає блок як нерухомий до завершення FFI", size=10, color=MUTED))

    # Стан 1: Pinning активується
    p.append(rect(470, 95, 370, 70, fill=BG, stroke=LINE, sw=1.2, rx=5))
    p.append(text(485, 118, "1. Pinning: об'єкт позначається PINNED (0x1000)", size=11, bold=True, anchor="start", color=INK))
    p.append(rect(485, 130, 160, 24, fill="#e2f3e8", stroke=FIELD, sw=1, rx=3))
    p.append(text(565, 146, "PINNED [0x1000]", size=10, bold=True, color=FIELD))
    p.append(arrow(710, 142, 650, 142, color=FIELD, sw=1.5))
    p.append(text(760, 146, "C ptr: 0x1000", size=10, bold=True, color=FIELD))

    # Стан 2: GC обходить закріплений об'єкт
    p.append(rect(470, 185, 370, 75, fill=BG, stroke=FIELD, sw=1.4, rx=5))
    p.append(text(485, 208, "2. GC рухає інші об'єкти, але 0x1000 лишається", size=11, bold=True, anchor="start", color=FIELD))
    p.append(rect(485, 222, 160, 24, fill="#e2f3e8", stroke=FIELD, sw=1, rx=3))
    p.append(text(565, 238, "Адреса незмінна: 0x1000", size=10, color=FIELD))
    p.append(text(660, 238, "GC не переміщує об'єкт", size=10, italic=True, color=MUTED, anchor="start"))

    # Стан 3: Безпечний запис та Unpinning
    p.append(rect(470, 280, 370, 80, fill="#eaf6ee", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(485, 305, "3. C-код завершує роботу і повертає керування", size=11, bold=True, anchor="start", color=FIELD))
    p.append(text(485, 326, "Запис у 0x1000 безпечний. Рантайм викликає Unpin", size=10, color=INK, anchor="start"))
    p.append(text(485, 345, "ЦІЛІСНІСТЬ ЗБЕРЕЖЕНО: Дані валідні, GC продовжує роботу", size=10, bold=True, color=FIELD, anchor="start"))

    render(os.path.join(OUT, "gc-pinning-hazard.svg"), W, H, *p)


# ── 4. libffi-flow: Динамічна диспетчеризація через CIF ───────────────────────
def fig_libffi_flow():
    W, H = 880, 390
    p = []

    # Тло
    p.append(rect(20, 20, 840, 350, fill="#fcfdfe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(440, 48, "Конвеєр динамічного виклику через libffi", size=14, bold=True, color=INK))
    p.append(text(440, 68, "Як динамічний рантайм формує машинний виклик під будь-який C ABI без кодогенерації", size=11, color=MUTED))

    # 4 кроки конвеєра
    steps = [
        ("1. Опис сигнатури", ["ffi_type *args[]", "ffi_type *rtype"], 50, 110, 170),
        ("2. Побудова CIF", ["ffi_prep_cif()", "Розрахунок зсувів/ABI"], 250, 110, 170),
        ("3. Буфер аргументів", ["void *avalues[]", "Вказівники на пам'ять"], 450, 110, 180),
        ("4. Асемблерний міст", ["ffi_call(&cif, ...)", "Розкладка по регістрах"], 660, 110, 180)
    ]

    for title, lines, bx, by, bw in steps:
        p.append(rect(bx, by, bw, 90, fill="#f4f7fb", stroke=NEG, sw=1.3, rx=6))
        p.append(text(bx + bw / 2, by + 24, title, size=11, bold=True, color=NEG))
        for li, line_text in enumerate(lines):
            p.append(text(bx + bw / 2, by + 48 + li * 20, line_text, size=10, color=INK))

    # Стрілки між кроками
    p.append(arrow(220, 155, 245, 155, color=LINE, sw=1.8))
    p.append(arrow(420, 155, 445, 155, color=LINE, sw=1.8))
    p.append(arrow(630, 155, 655, 155, color=LINE, sw=1.8))

    # Блок виконання (Нижня частина)
    p.append(rect(50, 230, 790, 110, fill="#fdf8f4", stroke=POS, sw=1.4, rx=6))
    p.append(text(445, 255, "Низькорівневий трамплін ffi_call_SYSV / ffi_call_win64 (Assembly)", size=12, bold=True, color=POS))

    # 3 блоки всередині трампліна
    p.append(rect(70, 270, 230, 50, fill=BG, stroke=LINE, sw=1, rx=4))
    p.append(text(185, 290, "Завантаження регістрів", size=10, bold=True, color=INK))
    p.append(text(185, 308, "RDI/RSI/RDX... або RCX/RDX...", size=9, color=MUTED))

    p.append(rect(330, 270, 230, 50, fill=BG, stroke=LINE, sw=1, rx=4))
    p.append(text(445, 290, "Вирівнювання стека", size=10, bold=True, color=INK))
    p.append(text(445, 308, "16-byte align + Shadow Space", size=9, color=MUTED))

    p.append(rect(590, 270, 230, 50, fill=BG, stroke=LINE, sw=1, rx=4))
    p.append(text(705, 290, "Апаратний виклик CALL", size=10, bold=True, color=POS))
    p.append(text(705, 308, "Зчитування RAX/XMM0 у rvalue", size=9, color=MUTED))

    render(os.path.join(OUT, "libffi-flow.svg"), W, H, *p)


if __name__ == "__main__":
    fig_ffi_boundary()
    fig_calling_conventions_x64()
    fig_gc_pinning_hazard()
    fig_libffi_flow()
    print("All figures generated successfully.")

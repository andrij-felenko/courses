# -*- coding: utf-8 -*-
import sys, os
# 4 рівні вгору від root/eng/sf-devices/chytannia-dyzasemblera до scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори ролей
ARM   = "#1e8449"   # стандарт / ядро ARM (зелений)
ARMF  = "#d5f5e3"
BLUE  = "#1a5276"   # пам'ять / ELF / адреси (синій)
BLUEF = "#d6eaf8"
AMBER = "#b9770e"   # попередження / проміжні стани (амбра)
AMBERF= "#fdf3d6"
VIOLET= "#7d3c98"   # код C++ / структури (фіолетовий)
VIOLETF="#f0e6fa"
RED   = "#c0392b"   # стек / виклики / переривання (червоний)
REDF  = "#fadbd8"


# ── 1. pipeline-to-asm: конвеєр компіляції та DWARF-зіставлення ──────────────
def fig_pipeline_to_asm():
    W, H = 820, 360
    p = []

    # Заголовок фігури
    p.append(text(W / 2, 28, "Конвеєр перетворення коду C/C++ у машинний лістинг та DWARF-зіставлення", size=14, color=INK, bold=True))

    # Блоки процесу (зліва направо)
    stages = [
        ("Сирцевий код", "firmware.c / .cpp\nВисокорівневі вирази", VIOLETF, VIOLET, 40, 60, 150, 75),
        ("Компілятор", "GCC / Clang (-O2 -g3)\nAST -> GIMPLE / LLVM IR", AMBERF, AMBER, 230, 60, 160, 75),
        ("Асемблер", "arm-none-eabi-as\n.s -> .o (коди інструкцій)", ARMF, ARM, 430, 60, 160, 75),
        ("Компонувальник", "arm-none-eabi-ld\n.elf (адреси + DWARF)", BLUEF, BLUE, 630, 60, 150, 75)
    ]

    for title, desc, fill, stroke_col, x, y, w, h in stages:
        p.append(rect(x, y, w, h, fill=fill, stroke=stroke_col, sw=1.8, rx=6))
        p.append(text(x + w / 2, y + 24, title, size=12, color=stroke_col, bold=True))
        p.append(mtext(x + w / 2, y + 44, desc, size=10, color=INK, lh=1.25))

    # Стрілки між етапами
    p.append(arrow(190, 97, 230, 97, color=MUTED, sw=1.8))
    p.append(arrow(390, 97, 430, 97, color=MUTED, sw=1.8))
    p.append(arrow(590, 97, 630, 97, color=MUTED, sw=1.8))

    # Нижній блок: objdump та gdb
    p.append(rect(40, 175, 740, 145, fill="#f8f9fa", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(40 + 740 / 2, 198, "Інструменти інтроспекції та аналізу: зіставлення адрес і рядків", size=12, color=INK, bold=True))

    # Дві панелі всередині інтроспекції
    # Ліва панель: objdump -d -S
    p.append(rect(60, 215, 340, 90, fill=BLUEF, stroke=BLUE, sw=1.4, rx=4))
    p.append(text(230, 235, "objdump -d -S -C firmware.elf", size=11, color=BLUE, bold=True))
    p.append(mtext(230, 255, "Читає секцію .debug_line у ELF\nПеремішує рядки C з Thumb-2 кодом\nСтатичний лістинг усієї програми", size=9.5, color=INK, lh=1.25))

    # Права панель: GDB disassemble /m
    p.append(rect(420, 215, 340, 90, fill=ARMF, stroke=ARM, sw=1.4, rx=4))
    p.append(text(590, 235, "gdb: disassemble /m /r $pc", size=11, color=ARM, bold=True))
    p.append(mtext(590, 255, "Динамічний аналіз у точці зупину\nПоказує $pc, регістри, сирі байти\nДозволяє крокувати по інструкціях (stepi)", size=9.5, color=INK, lh=1.25))

    # Стрілка від ELF вниз до інструментів
    p.append(arrow(705, 135, 705, 175, color=BLUE, sw=1.8))

    render(os.path.join(OUT, "pipeline-to-asm.svg"), W, H, *p,
           title="Конвеєр компіляції та формування лістингу")


# ── 2. aapcs-stack-frame: конвенція AAPCS та розподіл регістрів ──────────────
def fig_aapcs_stack_frame():
    W, H = 820, 430
    p = []

    p.append(text(W / 2, 28, "Конвенція викликів AAPCS (ARM Cortex-M): регістри та кадр стека", size=14, color=INK, bold=True))

    # Ліва частина: регістровий файл ARM (16 регістрів)
    p.append(text(210, 60, "Регістровий файл ядра (R0 — R15)", size=12, color=INK, bold=True))

    # R0-R3: Аргументи та повернення (Caller-saved)
    p.append(rect(40, 75, 340, 65, fill=ARMF, stroke=ARM, sw=1.6, rx=4))
    p.append(text(210, 95, "R0 — R3 (Caller-saved / Scratch)", size=11, color=ARM, bold=True))
    p.append(mtext(210, 115, "Перші 4 аргументи функції; R0/R1 повертають результат\nВикликана функція може вільно перезаписувати", size=9.5, color=INK, lh=1.2))

    # R4-R11: Змінні функції (Callee-saved)
    p.append(rect(40, 148, 340, 85, fill=BLUEF, stroke=BLUE, sw=1.6, rx=4))
    p.append(text(210, 168, "R4 — R11 (Callee-saved / Preserved)", size=11, color=BLUE, bold=True))
    p.append(mtext(210, 188, "Локальні змінні та регістровий розподіл\nФункція ЗОБОВ'ЯЗАНА зберегти на стек (PUSH)\nі відновити перед поверненням (POP)", size=9.5, color=INK, lh=1.2))

    # R12-R15: Спеціальні регістри
    p.append(rect(40, 241, 340, 105, fill=AMBERF, stroke=AMBER, sw=1.6, rx=4))
    p.append(text(210, 261, "R12, R13(SP), R14(LR), R15(PC)", size=11, color=AMBER, bold=True))
    p.append(mtext(210, 281, "R12 (IP): внутрішній скретч виклику\nR13 (SP): вказівник активного стека (вирівнювання 8 байт)\nR14 (LR): адреса повернення (Link Register)\nR15 (PC): лічильник команд (Program Counter)", size=9.5, color=INK, lh=1.2))

    # Легенда збереження
    p.append(rect(40, 356, 160, 26, fill=ARMF, stroke=ARM, sw=1.2, rx=3))
    p.append(text(120, 373, "Caller-saved (R0-R3, R12)", size=9.5, color=ARM, bold=True))
    p.append(rect(220, 356, 160, 26, fill=BLUEF, stroke=BLUE, sw=1.2, rx=3))
    p.append(text(300, 373, "Callee-saved (R4-R11)", size=9.5, color=BLUE, bold=True))

    # Права частина: Кадр стека у пам'яті
    p.append(text(600, 60, "Кадр стека в RAM (SP росте вниз)", size=12, color=INK, bold=True))

    stack_x, stack_w = 440, 320
    stack_items = [
        ("Вищі адреси пам'яті (RAM)", "#ffffff", MUTED, 24),
        ("5-й, 6-й... аргументи (якщо параметрів > 4)", REDF, RED, 35),
        ("Збережений LR (R14) — адреса повернення", AMBERF, AMBER, 32),
        ("Збережені Callee-saved регістри (R4 — R11)", BLUEF, BLUE, 38),
        ("Локальні змінні / буфери на стеку", VIOLETF, VIOLET, 38),
        ("Padding для вирівнювання SP на 8 байт", "#eef0f2", MUTED, 28),
        ("Поточний SP (Top of Stack) -> Нижчі адреси", ARMF, ARM, 30),
    ]

    sy = 80
    for label, fill, col, h in stack_items:
        p.append(rect(stack_x, sy, stack_w, h, fill=fill, stroke=col, sw=1.5, rx=0))
        p.append(text(stack_x + stack_w / 2, sy + h / 2 + 4, label, size=10, color=col if col != MUTED else INK, bold=(col != "#ffffff" and col != MUTED)))
        sy += h

    # Стрілка росту стека
    p.append(arrow(780, 110, 780, 280, color=RED, sw=2.0))
    p.append(mtext(795, 195, "Стек\nросте\nвниз", size=9, color=RED, anchor="start", lh=1.2))

    # Підпис внизу
    p.append(text(W / 2, H - 16, "AAPCS гарантує збереження R4-R11 між викликами та 8-байтне вирівнювання SP на публічних межах", size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "aapcs-stack-frame.svg"), W, H, *p,
           title="Конвенція викликів AAPCS та кадр стека")


# ── 3. switch-jump-table: таблиця переходів TBB / TBH ────────────────────────
def fig_switch_jump_table():
    W, H = 820, 380
    p = []

    p.append(text(W / 2, 28, "Механізм таблиці переходів Thumb-2: від індексу до виконання гілки", size=14, color=INK, bold=True))

    # Крок 1: Вхідне значення та перевірка меж
    p.append(rect(40, 65, 210, 120, fill=VIOLETF, stroke=VIOLET, sw=1.6, rx=5))
    p.append(text(145, 88, "1. Перевірка діапазону", size=11.5, color=VIOLET, bold=True))
    p.append(mtext(145, 112, "CMP  R0, #4\nBHI  .L_default\n\nПеревіряє, чи індекс\nвкладається в межі [0..max]", size=10, color=INK, lh=1.25))

    # Стрілка до TBB
    p.append(arrow(250, 125, 290, 125, color=MUTED, sw=1.8))

    # Крок 2: Інструкція TBB
    p.append(rect(290, 65, 220, 120, fill=ARMF, stroke=ARM, sw=1.8, rx=5))
    p.append(text(400, 88, "2. Інструкція TBB [PC, Rm]", size=11.5, color=ARM, bold=True))
    p.append(mtext(400, 112, "TBB  [PC, R0]\n\nОбчислює адресу переходу:\nPC += 2 * Table[R0]\nВиконує атомарний стрибок", size=10, color=INK, lh=1.25))

    # Стрілка до таблиці зміщень
    p.append(arrow(510, 125, 550, 125, color=MUTED, sw=1.8))

    # Крок 3: Таблиця байтових зміщень у Flash (.rodata)
    p.append(rect(550, 65, 230, 120, fill=BLUEF, stroke=BLUE, sw=1.6, rx=5))
    p.append(text(665, 88, "3. Таблиця зміщень у Flash", size=11.5, color=BLUE, bold=True))
    p.append(mtext(665, 112, ".L_table:\n.byte (.L_case0 - .L_table)/2\n.byte (.L_case1 - .L_table)/2\n.byte (.L_case2 - .L_table)/2\n.byte (.L_case3 - .L_table)/2", size=9.5, color=INK, lh=1.2))

    # Нижня частина: Цільові блоки коду (case 0..3 + default)
    p.append(text(W / 2, 218, "Цільові мітки обробників гілок case у Flash-пам'яті", size=12, color=INK, bold=True))

    cases = [
        (".L_case0", "Обробник режиму 0\nSTR R1, [R2, #0]\nB   .L_exit", ARMF, ARM, 40, 235, 135, 85),
        (".L_case1", "Обробник режиму 1\nADD R1, R1, #1\nB   .L_exit", ARMF, ARM, 195, 235, 135, 85),
        (".L_case2", "Обробник режиму 2\nBL  process_tx\nB   .L_exit", ARMF, ARM, 350, 235, 135, 85),
        (".L_case3", "Обробник режиму 3\nMOV R0, #0\nB   .L_exit", ARMF, ARM, 505, 235, 135, 85),
        (".L_default", "Гілка default\nBL  panic_error\nB   .L_exit", REDF, RED, 660, 235, 120, 85),
    ]

    for title, desc, fill, stroke_col, x, y, w, h in cases:
        p.append(rect(x, y, w, h, fill=fill, stroke=stroke_col, sw=1.4, rx=4))
        p.append(text(x + w / 2, y + 20, title, size=11, color=stroke_col, bold=True))
        p.append(mtext(x + w / 2, y + 42, desc, size=9.5, color=INK, lh=1.2))

    # Пунктирні стрілки від таблиці вниз до блоків
    p.append(line(600, 185, 107, 235, color=ARM, sw=1.4, dash="3,3"))
    p.append(line(630, 185, 262, 235, color=ARM, sw=1.4, dash="3,3"))
    p.append(line(665, 185, 417, 235, color=ARM, sw=1.4, dash="3,3"))
    p.append(line(700, 185, 572, 235, color=ARM, sw=1.4, dash="3,3"))
    p.append(line(145, 185, 720, 235, color=RED, sw=1.4, dash="3,3"))

    p.append(text(W / 2, H - 16, "TBB забезпечує час переходу O(1) незалежно від кількості варіантів case у щільних діапазонах", size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "switch-jump-table.svg"), W, H, *p,
           title="Таблиця переходів switch-case (TBB) у Thumb-2")


# ── 4. vtable-lookup: виклик віртуального методу C++ ─────────────────────────
def fig_vtable_lookup():
    W, H = 820, 420
    p = []

    p.append(text(W / 2, 28, "Анатомія віртуального виклику C++ у Thumb-2: від покажчика this до BLX", size=14, color=INK, bold=True))

    # Ліва частина: Об'єкт у пам'яті (RAM)
    obj_x, obj_y, obj_w = 50, 70, 220
    p.append(rect(obj_x, obj_y, obj_w, 200, fill="#ffffff", stroke=VIOLET, sw=1.8, rx=6))
    p.append(rect(obj_x, obj_y, obj_w, 32, fill=VIOLETF, stroke=VIOLET, sw=1.8, rx=0))
    p.append(text(obj_x + obj_w / 2, obj_y + 20, "Об'єкт у RAM (R0 = this)", size=11.5, color=VIOLET, bold=True))

    p.append(rect(obj_x + 10, obj_y + 45, obj_w - 20, 40, fill=ARMF, stroke=ARM, sw=1.4, rx=3))
    p.append(text(obj_x + obj_w / 2, obj_y + 62, "vptr (зміщення +0)", size=10.5, color=ARM, bold=True))
    p.append(text(obj_x + obj_w / 2, obj_y + 77, "-> вказівник на таблицю vtable", size=9, color=MUTED))

    p.append(rect(obj_x + 10, obj_y + 95, obj_w - 20, 40, fill="#f4f6f8", stroke=MUTED, sw=1.2, rx=3))
    p.append(text(obj_x + obj_w / 2, obj_y + 112, "uint32_t pin_mask_ (+4)", size=10, color=INK))
    p.append(text(obj_x + obj_w / 2, obj_y + 127, "поле даних об'єкта", size=9, color=MUTED))

    p.append(rect(obj_x + 10, obj_y + 145, obj_w - 20, 40, fill="#f4f6f8", stroke=MUTED, sw=1.2, rx=3))
    p.append(text(obj_x + obj_w / 2, obj_y + 162, "uint32_t baudrate_ (+8)", size=10, color=INK))
    p.append(text(obj_x + obj_w / 2, obj_y + 177, "поле даних об'єкта", size=9, color=MUTED))

    # Середня частина: vtable у Flash (.rodata)
    vt_x, vt_y, vt_w = 320, 70, 230
    p.append(rect(vt_x, vt_y, vt_w, 200, fill="#ffffff", stroke=BLUE, sw=1.8, rx=6))
    p.append(rect(vt_x, vt_y, vt_w, 32, fill=BLUEF, stroke=BLUE, sw=1.8, rx=0))
    p.append(text(vt_x + vt_w / 2, vt_y + 20, "vtable класу у Flash (.rodata)", size=11.5, color=BLUE, bold=True))

    p.append(rect(vt_x + 10, vt_y + 45, vt_w - 20, 40, fill="#f4f6f8", stroke=MUTED, sw=1.2, rx=3))
    p.append(text(vt_x + vt_w / 2, vt_y + 62, "vtable[0]: ~Driver() (+0)", size=10, color=INK))
    p.append(text(vt_x + vt_w / 2, vt_y + 77, "вказівник на деструктор", size=9, color=MUTED))

    p.append(rect(vt_x + 10, vt_y + 95, vt_w - 20, 40, fill=ARMF, stroke=ARM, sw=1.6, rx=3))
    p.append(text(vt_x + vt_w / 2, vt_y + 112, "vtable[1]: write() (+4)", size=10.5, color=ARM, bold=True))
    p.append(text(vt_x + vt_w / 2, vt_y + 127, "вказівник на реалізацію методу", size=9, color=MUTED))

    p.append(rect(vt_x + 10, vt_y + 145, vt_w - 20, 40, fill="#f4f6f8", stroke=MUTED, sw=1.2, rx=3))
    p.append(text(vt_x + vt_w / 2, vt_y + 162, "vtable[2]: read() (+8)", size=10, color=INK))
    p.append(text(vt_x + vt_w / 2, vt_y + 177, "вказівник на реалізацію методу", size=9, color=MUTED))

    # Стрілка від vptr до vtable
    p.append(arrow(obj_x + obj_w - 10, obj_y + 65, vt_x + 10, vt_y + 65, color=ARM, sw=1.8))

    # Права частина: Тіло функції у Flash (.text)
    fn_x, fn_y, fn_w = 600, 70, 180
    p.append(rect(fn_x, fn_y, fn_w, 200, fill="#ffffff", stroke=ARM, sw=1.8, rx=6))
    p.append(rect(fn_x, fn_y, fn_w, 32, fill=ARMF, stroke=ARM, sw=1.8, rx=0))
    p.append(text(fn_x + fn_w / 2, fn_y + 20, "Код методу (.text)", size=11.5, color=ARM, bold=True))

    p.append(rect(fn_x + 10, fn_y + 75, fn_w - 20, 85, fill=ARMF, stroke=ARM, sw=1.4, rx=4))
    p.append(text(fn_x + fn_w / 2, fn_y + 98, "UartDriver::write()", size=10.5, color=ARM, bold=True))
    p.append(mtext(fn_x + fn_w / 2, fn_y + 118, "PUSH {r4, lr}\n...\nSTR  R1, [R2, #4]\nPOP  {r4, pc}", size=9.5, color=INK, lh=1.25))

    # Стрілка від vtable[1] до функції
    p.append(arrow(vt_x + vt_w - 10, vt_y + 115, fn_x + 10, fn_y + 115, color=ARM, sw=1.8))

    # Нижня панель: Послідовність інструкцій Thumb-2
    p.append(rect(50, 290, 730, 95, fill="#f8f9fa", stroke=MUTED, sw=1.5, rx=5))
    p.append(text(415, 310, "Послідовність виконання інструкцій Thumb-2 для виклику dev->write(byte)", size=11.5, color=INK, bold=True))

    steps = [
        ("1. Читання vptr", "LDR  R3, [R0, #0]", ARMF, ARM, 70, 325, 160, 48),
        ("2. Вибірка адреси", "LDR  R3, [R3, #4]", BLUEF, BLUE, 250, 325, 160, 48),
        ("3. Підготовка аргументу", "MOV  R1, #0x55", VIOLETF, VIOLET, 430, 325, 160, 48),
        ("4. Непрямий виклик", "BLX  R3  (R0=this)", REDF, RED, 610, 325, 150, 48)
    ]

    for title, asm, fill, stroke_col, x, y, w, h in steps:
        p.append(rect(x, y, w, h, fill=fill, stroke=stroke_col, sw=1.4, rx=3))
        p.append(text(x + w / 2, y + 18, title, size=9.5, color=stroke_col, bold=True))
        p.append(text(x + w / 2, y + 36, asm, size=10, color=INK, bold=True))

    p.append(text(W / 2, H - 14, "Виклик віртуального методу потребує 2 звернення до пам'яті (vptr та адреса методу) перед непрямим BLX", size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "vtable-lookup.svg"), W, H, *p,
           title="Анатомія виклику віртуального методу C++ у Thumb-2")


if __name__ == "__main__":
    fig_pipeline_to_asm()
    fig_aapcs_stack_frame()
    fig_switch_jump_table()
    fig_vtable_lookup()
    print("Всі 4 фігури успішно згенеровано у teці img/")

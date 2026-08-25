# -*- coding: utf-8 -*-
"""Фігури до теми «Map-файл: що з'їло флеш і RAM»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DIRTY = "#fdecea"     # червонуватий акцент (переповнення, помилка, важкий символ)
CLEAN = "#eaf7ef"     # зеленуватий акцент (оптимізація, вільне місце)
BLUE_BG = "#eef4ff"   # синій акцент (структури даних, розкладка)
YELLOW_BG = "#fffbe6" # жовтий акцент (проміжні стадії, увага)


def node(cx, cy, label, fill=FILL, stroke=LINE, bold=False, size=13, sw=1.5, min_w=0):
    frag, w, h = textbox(cx, cy, label, size=size, fill=fill, stroke=stroke,
                         bold=bold, sw=sw, min_w=min_w)
    return frag, (cx, cy, w, h)


def down_arr(a, b, color=LINE, sw=1.8):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return arrow(ax, ay + ah / 2 + 2, bx, by - bh / 2 - 4, color=color, sw=sw)


def right_arr(a, b, color=LINE, sw=1.8):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return arrow(ax + aw / 2 + 2, ay, bx - bw / 2 - 4, by, color=color, sw=sw)


# ── 1. Анатомія Map-файлу ──────────────────────────────────────────────────
def fig_map_anatomy():
    W, H = 1000, 560
    parts = []

    # Загальна рамка та заголовок
    parts.append(rect(30, 20, 940, 520, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(500, 48, "Структура Linker Map файлу (GNU ld) і напрям діагностики", size=16, bold=True, color=INK))

    # Секція 1: Archive members
    b1, g1 = node(250, 115, "1. Archive Members Included\nВтягнуті об'єкти зі статичних бібліотек (libc.a, libgcc.a)\nПоказує: який саме символ змусив лінкер підтягнути весь .o",
                  size=12, fill=YELLOW_BG, stroke=MUTED, min_w=400)

    # Секція 2: Memory Configuration
    b2, g2 = node(750, 115, "2. Memory Configuration\nМежі регіонів із Linker Script (FLASH, RAM, CCMRAM)\nПоказує: ORIGIN, LENGTH та апаратні атрибути (xr, rw)",
                  size=12, fill=BLUE_BG, stroke=NEG, min_w=400)

    # Секція 3: Discarded Input Sections
    b3, g3 = node(250, 260, "3. Discarded Input Sections\nСекції, викинуті через -Wl,--gc-sections\nПоказує: які функції та змінні визнано мертвим кодом",
                  size=12, fill=CLEAN, stroke=FIELD, min_w=400)

    # Секція 4: Linker Script and Memory Map (Центральний)
    b4, g4 = node(750, 260, "4. Linker Script & Memory Map\nПовна розкладка кожного символу за адресами VMA/LMA\nПоказує: точний розмір у hex/dec, падінг (*fill*) і внесок файлів",
                  size=12, fill=DIRTY, stroke=POS, bold=True, min_w=400)

    # Секція 5: Cross Reference Table
    b5, g5 = node(500, 420, "5. Cross Reference Table (--cref)\nТаблиця перехресних посилань між символами та об'єктними файлами\nПоказує: де символ визначено і звідки саме його викликають у проєкті",
                  size=12.5, fill=BLUE_BG, stroke=NEG, bold=True, min_w=700)

    # Стрілки взаємозв'язку розслідування
    parts += [b1, b2, b3, b4, b5]
    parts.append(down_arr(g1, g3, color=MUTED))
    parts.append(down_arr(g2, g4, color=NEG))
    
    # Зв'язок від карти пам'яті до таблиці посилань
    parts.append(arrow(750, g4[1] + g4[3] / 2 + 2, 650, g5[1] - g5[3] / 2 - 4, color=POS, sw=2.0))
    parts.append(text(760, 350, "Знайшли важкий символ", size=11, color=POS, bold=True, anchor="start"))

    # Зв'язок від таблиці посилань до аналізу бібліотек
    parts.append(arrow(350, g5[1] - g5[3] / 2 - 4, 250, g3[1] + g3[3] / 2 + 2, color=FIELD, sw=2.0))
    parts.append(text(240, 350, "Чому не викинуто?", size=11, color=FIELD, bold=True, anchor="end"))

    # Підсумок внизу
    parts.append(text(500, 510, "Алгоритм пошуку: Розмір у карті (4) → Хто викликав у cref (5) → Чи спрацював gc-sections (3)", size=12, color=INK, italic=True))

    render(os.path.join(IMG, "map-file-anatomy.svg"), W, H, *parts,
           title="Анатомія Map-файлу компонувальника GNU ld")


# ── 2. Розподіл секцій між Flash та RAM ────────────────────────────────────
def fig_memory_regions():
    W, H = 1040, 560
    parts = []

    # Заголовок
    parts.append(text(520, 32, "Розподіл секцій прошивки між енергонезалежною Flash та SRAM", size=16, bold=True, color=INK))

    # Ліва колонка: FLASH (ROM)
    parts.append(rect(40, 55, 430, 480, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(255, 82, "FLASH (Енергонезалежна ROM)", size=14.5, bold=True, color=NEG))
    parts.append(text(255, 100, "Зберігається при вимкненні живлення", size=11, color=MUTED))

    f1, _ = node(255, 150, ".text (Машинний код функцій, переривання, стартап)\nРозмір: десятки/сотні КБ. Лише читання (rx)", size=11, fill=BLUE_BG, stroke=NEG, min_w=380)
    f2, _ = node(255, 230, ".rodata (Незмінні константи, рядки, lookup-таблиці)\nРозмір: байти — десятки КБ. Лише читання (r)", size=11, fill=CLEAN, stroke=FIELD, min_w=380)
    f3, gf3 = node(255, 325, ".data LMA (Початкові значення змінних)\nЗберігається у Flash, копіюється в RAM при старті!\nПлатить подвійну ціну за розмір", size=11, fill=DIRTY, stroke=POS, bold=True, min_w=380)
    
    parts.append(rect(65, 400, 380, 115, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    parts.append(text(255, 425, "Переповнення: region 'FLASH' overflowed", size=12, bold=True, color=POS))
    parts.append(text(255, 450, "Сума (.text + .rodata + .data LMA) > Розмір Flash", size=11, color=INK))
    parts.append(text(255, 475, "Причина: важкий код бібліотек, RTTI,", size=10.5, color=MUTED))
    parts.append(text(255, 495, "відсутність const у великих таблицях", size=10.5, color=MUTED))

    # Права колонка: RAM (SRAM)
    parts.append(rect(570, 55, 430, 480, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(785, 82, "SRAM (Оперативна пам'ять RAM)", size=14.5, bold=True, color=FIELD))
    parts.append(text(785, 100, "Втрачається при вимкненні, швидкий доступ (rwx/rw)", size=11, color=MUTED))

    r1, gr1 = node(785, 150, ".data VMA (Робоча копія ініціалізованих змінних)\nАдреса виконання в RAM, модифікується під час роботи", size=11, fill=DIRTY, stroke=POS, bold=True, min_w=380)
    r2, _ = node(785, 230, ".bss (Неініціалізовані статичні/глобальні змінні)\nЗаповнюється нулями стартап-кодом. У Flash займає 0 байтів!", size=11, fill=BLUE_BG, stroke=NEG, min_w=380)
    r3, _ = node(785, 325, "Купа (Heap) та Стек (Stack)\nДинамічна пам'ять (malloc/new) росте вгору ↑\nСтек викликів локальних змінних росте вниз ↓", size=11, fill=YELLOW_BG, stroke=MUTED, min_w=380)

    parts.append(rect(595, 400, 380, 115, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    parts.append(text(785, 425, "Переповнення: region 'RAM' overflowed", size=12, bold=True, color=POS))
    parts.append(text(785, 450, "Сума (.data VMA + .bss + Стек + Купа) > Розмір RAM", size=11, color=INK))
    parts.append(text(785, 475, "Причина: великі нестатичні буфери,", size=10.5, color=MUTED))
    parts.append(text(785, 495, "переповнення стеку, забутий const", size=10.5, color=MUTED))

    # Стрілка між .data LMA та .data VMA (проводимо збоку, текст згори)
    parts += [f1, f2, f3, r1, r2, r3]
    parts.append(text(520, 215, "Копіювання", size=11, bold=True, color=POS))
    parts.append(text(520, 232, "Reset_Handler", size=10, color=MUTED))
    parts.append(arrow(gf3[0] + gf3[2] / 2 + 5, gf3[1] - 20, gr1[0] - gr1[2] / 2 - 5, gr1[1] + 20, color=POS, sw=2.2))

    render(os.path.join(IMG, "memory-regions-footprint.svg"), W, H, *parts,
           title="Розподіл секцій прошивки між Flash та SRAM")


# ── 3. Алгоритм розслідування за таблицею перехресних посилань ─────────────
def fig_investigation_flow():
    W, H = 1020, 520
    parts = []

    # Заголовок
    parts.append(text(510, 35, "Ланцюжок розслідування: від помилки лінкера до винного рядка", size=16, bold=True, color=INK))

    # Крок 1: Помилка
    s1, g1 = node(150, 140, "Крок 1: Симптом\nregion 'FLASH' overflowed\nby 24188 bytes",
                  size=12, fill=DIRTY, stroke=POS, bold=True, min_w=200)

    # Крок 2: Пошук важкого символу
    s2, g2 = node(400, 140, "Крок 2: Memory Map\nЗнаходимо найбільшу секцію:\n.text._dtoa_r (0x2140 байтів)\nу складі libc_nano.a",
                  size=12, fill=YELLOW_BG, stroke=MUTED, min_w=220)

    # Крок 3: Cross Reference Table
    s3, g3 = node(670, 140, "Крок 3: Розділ Cross Reference\nШукаємо символ _dtoa_r:\n_dtoa_r ← vfprintf_r ← vsprintf\n← sprintf (усі з libc_nano.a)",
                  size=12, fill=BLUE_BG, stroke=NEG, min_w=240)

    # Крок 4: Власний код
    s4, g4 = node(910, 140, "Крок 4: Точка входу\nПошук виклику sprintf:\ntelemetry.c:84\nвикликає sprintf(buf, \"%f\", v)",
                  size=12, fill=DIRTY, stroke=POS, bold=True, min_w=170)

    parts += [s1, s2, s3, s4]
    parts.append(right_arr(g1, g2, color=POS))
    parts.append(right_arr(g2, g3, color=MUTED))
    parts.append(right_arr(g3, g4, color=NEG))

    # Нижній блок: Варіанти вирішення проблеми
    parts.append(rect(60, 250, 900, 230, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(510, 275, "Крок 5: Інженерне усунення причини роздування", size=14, bold=True, color=FIELD))

    sol1, _ = node(230, 360, "Рішення А: nano.specs\nПідключити -specs=nano.specs\nта вимкнути float у printf\nЗаощаджує: ~18–25 КБ Flash",
                   size=11.5, fill=CLEAN, stroke=FIELD, min_w=240)

    sol2, _ = node(510, 360, "Рішення Б: Легкий форматер\nЗаміна sprintf на власну\nфункцію форматування (fixed-point)\nЗаощаджує: ~30 КБ Flash",
                   size=11.5, fill=CLEAN, stroke=FIELD, min_w=240)

    sol3, _ = node(790, 360, "Рішення В: C++ Прапорці\nВимкнути -fno-exceptions\nта -fno-rtti, прибрати зайвий vtable\nЗаощаджує: ~20–50 КБ Flash",
                   size=11.5, fill=CLEAN, stroke=FIELD, min_w=240)

    parts += [sol1, sol2, sol3]
    
    # Стрілка від Кроку 4 до блоку рішень
    parts.append(arrow(910, g4[1] + g4[3] / 2 + 2, 790, 290, color=FIELD, sw=2.0))
    parts.append(arrow(910, g4[1] + g4[3] / 2 + 2, 510, 290, color=FIELD, sw=2.0))
    parts.append(arrow(910, g4[1] + g4[3] / 2 + 2, 230, 290, color=FIELD, sw=2.0))

    render(os.path.join(IMG, "cref-investigation-flow.svg"), W, H, *parts,
           title="Алгоритм пошуку причини роздування пам'яті через Cross Reference Table")


def main():
    fig_map_anatomy()
    fig_memory_regions()
    fig_investigation_flow()
    print("Всі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Фігури теми «Вирівнювання й розміщувальний new»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


def fig_hardware_bus_alignment():
    """Апаратне читання через 32/64-бітну шину: вирівняний доступ за 1 такт проти невирівняного."""
    W, H = 940, 480
    f = []

    # Заголовки двох колонок
    f.append(fitbox(40, 30, 410, 40, "Вирівняний доступ: адреса 0x1000 (uint32_t)", size=13, bold=True,
                    fill="#eef7ee", stroke=FIELD, color=FIELD))
    f.append(fitbox(490, 30, 410, 40, "Невирівняний доступ: адреса 0x1002 (uint32_t)", size=13, bold=True,
                    fill="#fdecea", stroke=POS, color=POS))

    # Ліва колонка: вирівняний доступ
    # Смуга пам'яті (4 слова по 4 байти = 16 байтів)
    y_mem = 95
    f.append(fitbox(40, y_mem, 410, 26, "Фізичні слова пам'яті (ширина шини = 4 байти)", size=11, bold=True,
                    fill="#eef2f7", stroke=MUTED, color=MUTED))

    # 4 слова
    words_left = [
        ("Слово 0: 0x1000..0x1003", 40, "#d4edda", FIELD, "4 байти цілком у Слові 0"),
        ("Слово 1: 0x1004..0x1007", 145, "#f4f6f8", LINE, "вільно"),
        ("Слово 2: 0x1008..0x100B", 250, "#f4f6f8", LINE, "вільно"),
        ("Слово 3: 0x100C..0x100F", 355, "#f4f6f8", LINE, "вільно"),
    ]
    for label, x_box, bg_c, str_c, note in words_left:
        f.append(rect(x_box, 130, 95, 60, fill=bg_c, stroke=str_c, sw=1.5))
        f.append(fitbox(x_box + 3, 133, 89, 24, label, size=9, bold=True, fill=bg_c, stroke=bg_c, color=INK))
        f.append(fitbox(x_box + 3, 160, 89, 26, note, size=9, fill=bg_c, stroke=bg_c, color=MUTED))

    # Стрілка шини
    f.append(arrow(245, 205, 245, 255, color=FIELD, sw=2.5))
    f.append(fitbox(90, 260, 310, 32, "1 цикл читання шини даних", size=12, bold=True,
                    fill="#eef7ee", stroke=FIELD, color=FIELD))

    f.append(fitbox(40, 310, 410, 140,
                    "• Адреса 0x1000 кратна 4 (молодші біти 00)\n"
                    "• Процесор зчитує всі 4 байти за одну транзакцію\n"
                    "• Максимальна швидкість виконання\n"
                    "• Гарантована атомарність на апаратному рівні",
                    size=12, pad=10, fill=BG, stroke=FIELD))

    # Права колонка: невирівняний доступ
    f.append(fitbox(490, y_mem, 410, 26, "Фізичні слова пам'яті (ширина шини = 4 байти)", size=11, bold=True,
                    fill="#eef2f7", stroke=MUTED, color=MUTED))

    # 4 слова праворуч
    words_right = [
        ("Слово 0: 0x1000..0x1003", 490, "#fff3cd", "#d39e00", "Байти [0, 1] числа"),
        ("Слово 1: 0x1004..0x1007", 595, "#fff3cd", "#d39e00", "Байти [2, 3] числа"),
        ("Слово 2: 0x1008..0x100B", 700, "#f4f6f8", LINE, "вільно"),
        ("Слово 3: 0x100C..0x100F", 805, "#f4f6f8", LINE, "вільно"),
    ]
    for label, x_box, bg_c, str_c, note in words_right:
        f.append(rect(x_box, 130, 95, 60, fill=bg_c, stroke=str_c, sw=1.5))
        f.append(fitbox(x_box + 3, 133, 89, 24, label, size=9, bold=True, fill=bg_c, stroke=bg_c, color=INK))
        f.append(fitbox(x_box + 3, 160, 89, 26, note, size=9, fill=bg_c, stroke=bg_c, color=MUTED))

    # Стрілки для двох транзакцій
    f.append(arrow(537, 205, 537, 245, color=POS, sw=2))
    f.append(arrow(642, 205, 642, 245, color=POS, sw=2))
    f.append(fitbox(490, 255, 410, 38, "2 цикли шини + склеювання байтів (або апаратний Fault)", size=11, bold=True,
                    fill="#fdecea", stroke=POS, color=POS))

    f.append(fitbox(490, 310, 410, 140,
                    "• Адреса 0x1002 не кратна 4: число розірване між словами\n"
                    "• x86: дві транзакції пам'яті + бітовий зсув у конвеєрі\n"
                    "• ARM/RISC-V: падіння в UsageFault / SIGBUS\n"
                    "• Втрата атомарності доступу, пенальті продуктивності",
                    size=12, pad=10, fill=BG, stroke=POS))

    render(os.path.join(IMG, 'hardware-bus-alignment.svg'), W, H, *f,
           title="Апаратні вимоги вирівнювання шини пам'яті")


def fig_placement_new_storage():
    """Етапи розміщувального new: сирий буфер -> вирівнювання -> конструктор -> ручний деструктор."""
    W, H = 940, 520
    f = []

    steps = [
        ("1. Сирий буфер пам'яті", "alignas(T) std::byte buffer[sizeof(T)];\nБайти виділені на стеку, у статичній пам'яті чи купі. Об'єкта ще нема.", "#eef2f7", MUTED),
        ("2. Контроль вирівнювання", "std::align перевіряє адресу та зсуває вказівник на потрібне зміщення (padding offset).", "#eaf0fd", NEG),
        ("3. Розміщувальний new", "new (ptr) Type(args...);\nВиклик конструктора на підготовлених байтах. Початок часу життя об'єкта.", "#eef7ee", FIELD),
        ("4. Ручний виклик деструктора", "ptr->~Type();\nЗавершення часу життя об'єкта. Буфер лишається цілим і готовим до повторного вжитку.", "#fdecea", POS),
    ]

    y0, bh, dy = 35, 95, 120
    for i, (title_s, desc_s, bg_c, str_c) in enumerate(steps):
        y = y0 + i * dy
        f.append(fitbox(40, y, 260, bh, title_s, size=13, bold=True, fill=bg_c, stroke=str_c, color=str_c))
        f.append(fitbox(320, y, 580, bh, desc_s, size=12, pad=10, fill=BG, stroke=LINE))
        if i < len(steps) - 1:
            f.append(arrow(170, y + bh, 170, y + dy, color=INK, sw=2))

    render(os.path.join(IMG, 'placement-new-storage.svg'), W, H, *f,
           title="Життєвий цикл пам'яті та об'єкта при розміщувальному new")


def fig_cache_line_false_sharing():
    """False Sharing на межі кеш-лінії 64 байти та виправлення через alignas."""
    W, H = 940, 480
    f = []

    # Верхній блок: Проблема False Sharing
    f.append(fitbox(40, 25, 860, 36, "Проблема: дві змінні в одній 64-байтній кеш-лінії (False Sharing)", size=13, bold=True,
                    fill="#fdecea", stroke=POS, color=POS))

    # Спільна кеш-лінія
    f.append(rect(60, 75, 820, 75, fill="#fff3cd", stroke=POS, sw=1.8))
    f.append(fitbox(70, 85, 380, 55, "Ядро 0 змінює a:\nstruct Data { int a; int b; } data;\n(data.a на байті 0..3)", size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))
    f.append(fitbox(470, 85, 390, 55, "Ядро 1 змінює b:\n(data.b на байті 4..7)\nПостійне скидання лінії між кешами L1!", size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))

    f.append(fitbox(60, 160, 820, 45, "Протокол когерентності (MESI) передає всю 64-байтну лінію між ядрами при кожному записі. Продуктивність падає в десятки разів.", size=11, pad=6, fill=BG, stroke=LINE, color=INK))

    # Розділювальна лінія
    f.append(line(40, 225, 900, 225, color=MUTED, sw=1.2, dash="4,4"))

    # Нижній блок: Виправлення через alignas(64)
    f.append(fitbox(40, 245, 860, 36, "Розв'язання: розділення на окремі кеш-лінії через alignas(hardware_destructive_interference_size)", size=13, bold=True,
                    fill="#eef7ee", stroke=FIELD, color=FIELD))

    # Кеш-лінія 1
    f.append(rect(60, 295, 390, 85, fill="#eef7ee", stroke=FIELD, sw=1.6))
    f.append(fitbox(75, 305, 360, 65, "Кеш-лінія 0 (64 байти):\nalignas(64) int a;\nНалежить виключно Ядру 0", size=11, bold=True, fill=BG, stroke=FIELD, color=FIELD))

    # Кеш-лінія 2
    f.append(rect(490, 295, 390, 85, fill="#eef7ee", stroke=FIELD, sw=1.6))
    f.append(fitbox(505, 305, 360, 65, "Кеш-лінія 1 (64 байти):\nalignas(64) int b;\nНалежить виключно Ядру 1", size=11, bold=True, fill=BG, stroke=FIELD, color=FIELD))

    f.append(fitbox(60, 395, 820, 55, "Ядра модифікують свої змінні повністю незалежно у власних кешах L1 без взаємного блокування та інвалідації шини.", size=11, pad=6, fill=BG, stroke=FIELD, color=FIELD))

    render(os.path.join(IMG, 'cache-line-false-sharing.svg'), W, H, *f,
           title="Вирівнювання на розмір кеш-лінії та запобігання False Sharing")


if __name__ == '__main__':
    fig_hardware_bus_alignment()
    fig_placement_new_storage()
    fig_cache_line_false_sharing()
    print("All figures generated successfully.")

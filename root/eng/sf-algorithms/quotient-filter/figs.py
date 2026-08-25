# -*- coding: utf-8 -*-
"""Фігури до статті «Квошієнтний фільтр (Quotient Filter)».
Запуск із теки теми: python figs.py
Виводить SVG у ./img/. Усі тексти та розмітки сумісні з svgkit та svgcheck.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# ── 1. Анатомія слота та розщеплення хешу на частку й залишок ───────────────
def fig_anatomy():
    W, H = 940, 500
    parts = []

    parts.append(text(W / 2, 28, "Анатомія квошієнтного фільтра: розщеплення хешу та структура слота", size=16, bold=True))

    # Верхній блок: вхідний ключ x -> 64-бітний хеш -> q бітів частки + r бітів залишку
    tb_key, _, _ = textbox(130, 85, 'Ключ x\n"user_42"', size=13, pad=8, fill="#eaf0fd", stroke=NEG, bold=True)
    parts.append(tb_key)

    parts.append(arrow(205, 85, 275, 85, color=MUTED, sw=1.5))
    parts.append(text(240, 75, "hash(x)", size=11, color=MUTED, italic=True))

    # Хеш-значення p бітів
    parts.append(rect(280, 60, 380, 50, fill="#fafbfc", stroke=LINE, sw=1.2, rx=4))
    parts.append(text(470, 75, "Повний 64-бітний хеш h(x) (розмір p = q + r бітів)", size=11, color=MUTED))
    
    # Розщеплення на q і r
    parts.append(rect(290, 83, 170, 22, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
    parts.append(text(375, 98, "q бітів: частка (quotient)", size=11, color=POS, bold=True))

    parts.append(rect(470, 83, 180, 22, fill="#e8f8f0", stroke=FIELD, sw=1.2, rx=3))
    parts.append(text(560, 98, "r бітів: залишок (remainder)", size=11, color=FIELD, bold=True))

    # Стрілки вниз від q та r
    parts.append(arrow(375, 110, 375, 160, color=POS, sw=1.5))
    parts.append(arrow(560, 110, 560, 240, color=FIELD, sw=1.5))

    # Пояснення ролі q
    tb_q_role, _, _ = textbox(375, 185, "Канонічний індекс слота:\ncanonical_slot = f_q = h(x) >> r\n(адресація 2^q комірок у таблиці)", size=12, pad=7, fill="#fdecea", stroke=POS)
    parts.append(tb_q_role)

    # Нижній блок: Детальна будова одного слота (3 біти метаданих + r бітів залишку)
    parts.append(text(W / 2, 260, "Будова окремого слота таблиці (розмір: r + 3 біти)", size=14, bold=True))

    # Рамка слота
    sx, sy, sw, sh = 100, 290, 740, 100
    parts.append(rect(sx, sy, sw, sh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))

    # Три біти метаданих
    bw = 140
    # Біт 1: is_occupied
    parts.append(rect(sx + 15, sy + 15, bw, 70, fill="#fff2e8", stroke="#fa541c", sw=1.2, rx=4))
    parts.append(text(sx + 15 + bw / 2, sy + 38, "is_occupied", size=13, color="#fa541c", bold=True))
    parts.append(text(sx + 15 + bw / 2, sy + 58, "1 біт: чи є елементи", size=11, color=MUTED))
    parts.append(text(sx + 15 + bw / 2, sy + 74, "з канонічним f_q = i", size=11, color=MUTED))

    # Біт 2: is_continuation
    parts.append(rect(sx + 165, sy + 15, bw, 70, fill="#f9f0ff", stroke="#722ed1", sw=1.2, rx=4))
    parts.append(text(sx + 165 + bw / 2, sy + 38, "is_continuation", size=13, color="#722ed1", bold=True))
    parts.append(text(sx + 165 + bw / 2, sy + 58, "1 біт: чи продовжує", size=11, color=MUTED))
    parts.append(text(sx + 165 + bw / 2, sy + 74, "поточну серію (run)", size=11, color=MUTED))

    # Біт 3: is_shifted
    parts.append(rect(sx + 315, sy + 15, bw, 70, fill="#e6f7ff", stroke="#1890ff", sw=1.2, rx=4))
    parts.append(text(sx + 315 + bw / 2, sy + 38, "is_shifted", size=13, color="#1890ff", bold=True))
    parts.append(text(sx + 315 + bw / 2, sy + 58, "1 біт: чи зміщено", size=11, color=MUTED))
    parts.append(text(sx + 315 + bw / 2, sy + 74, "елемент від f_q", size=11, color=MUTED))

    # Поле залишку remainder
    rw = 235
    parts.append(rect(sx + 480, sy + 15, rw, 70, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=4))
    parts.append(text(sx + 480 + rw / 2, sy + 38, "remainder (залишок f_r)", size=13, color=FIELD, bold=True))
    parts.append(text(sx + 480 + rw / 2, sy + 58, "r бітів корисного навантаження", size=11, color=MUTED))
    parts.append(text(sx + 480 + rw / 2, sy + 74, "зберігає залишок хешу", size=11, color=MUTED))

    # Нижній висновок
    tb_bottom, _, _ = textbox(W / 2, 440, "Завдяки частці f_q адреса не зберігається явно: номер комірки відновлює старші біти хешу", size=12, pad=6, fill="#ffffff", stroke=MUTED)
    parts.append(tb_bottom)

    render(os.path.join(IMG, "quotient-filter-anatomy.svg"), W, H, *parts)


# ── 2. Організація набігів (Runs) та кластерів (Clusters) ───────────────────
def fig_runs_and_clusters():
    W, H = 940, 500
    parts = []

    parts.append(text(W / 2, 28, "Групування відбитків у набіги (Runs) та суцільні кластери (Clusters)", size=16, bold=True))

    # Таблиця слотів 0..7
    start_x = 70
    start_y = 110
    cell_w = 98
    cell_h = 130

    slots_data = [
        # idx, occ, cont, shift, rem, note
        (0, "0", "0", "0", "—", "Порожній"),
        (1, "1", "0", "0", "0x2A", "Початок серії f_q=1"),
        (2, "1", "1", "1", "0x5F", "Продовження f_q=1"),
        (3, "0", "0", "1", "0x12", "Початок серії f_q=2"),
        (4, "1", "0", "1", "0x8B", "Початок серії f_q=4"),
        (5, "0", "0", "0", "—", "Порожній"),
        (6, "1", "0", "0", "0x3C", "Початок серії f_q=6"),
        (7, "0", "0", "0", "—", "Порожній"),
    ]

    # Верхній маркер кластера 1..4
    parts.append(rect(start_x + cell_w * 1, start_y - 35, cell_w * 4, 25, fill="#fffbe6", stroke="#d48806", sw=1.2, rx=4))
    parts.append(text(start_x + cell_w * 3, start_y - 18, "Кластер (суцільний блок зайнятих слотів 1..4)", size=12, color="#d48806", bold=True))

    # Маркер кластера 6
    parts.append(rect(start_x + cell_w * 6, start_y - 35, cell_w * 1, 25, fill="#fffbe6", stroke="#d48806", sw=1.2, rx=4))
    parts.append(text(start_x + cell_w * 6.5, start_y - 18, "Кластер 6", size=12, color="#d48806", bold=True))

    for idx, occ, cont, shift, rem, note in slots_data:
        cx = start_x + idx * cell_w
        cy = start_y
        is_empty = (rem == "—")

        # Фон комірки
        bg = "#ffffff" if is_empty else "#f8fafc"
        border_col = MUTED if is_empty else LINE
        parts.append(rect(cx, cy, cell_w - 4, cell_h, fill=bg, stroke=border_col, sw=1.2, rx=4))

        # Заголовок індексу
        parts.append(rect(cx, cy, cell_w - 4, 24, fill="#eef2f7", stroke=border_col, sw=1.0, rx=3))
        parts.append(text(cx + (cell_w - 4) / 2, cy + 16, f"Слот [{idx}]", size=12, bold=True))

        # Біти: O, C, S
        col_o = "#fa541c" if occ == "1" else MUTED
        col_c = "#722ed1" if cont == "1" else MUTED
        col_s = "#1890ff" if shift == "1" else MUTED

        parts.append(text(cx + 16, cy + 44, f"O:{occ}", size=11, color=col_o, bold=(occ == "1")))
        parts.append(text(cx + 46, cy + 44, f"C:{cont}", size=11, color=col_c, bold=(cont == "1")))
        parts.append(text(cx + 76, cy + 44, f"S:{shift}", size=11, color=col_s, bold=(shift == "1")))

        # Залишок
        rem_bg = "#e8f8f0" if not is_empty else "#ffffff"
        rem_col = FIELD if not is_empty else MUTED
        parts.append(rect(cx + 8, cy + 58, cell_w - 20, 28, fill=rem_bg, stroke=rem_col, sw=1.0, rx=3))
        parts.append(text(cx + (cell_w - 4) / 2, cy + 76, rem, size=12, color=rem_col, bold=not is_empty))

        # Короткий підпис
        sub_size = fit_font(note, cell_w - 10, size=10, min_size=9)
        parts.append(text(cx + (cell_w - 4) / 2, cy + 105, note, size=sub_size, color=MUTED))

    # Нижній пояснювальний блок: розбір набігів
    by = start_y + cell_h + 30
    parts.append(rect(start_x, by, cell_w * 8 - 4, 150, fill="#fdfefe", stroke=MUTED, sw=1.0, rx=6))
    parts.append(text(start_x + (cell_w * 8) / 2, by + 24, "Як декодуються набіги (Runs) у кластері [1..4]:", size=13, bold=True))

    run1_desc = "• Набіг f_q = 1: починається у слоті [1] (C=0, S=0) і продовжується у слоті [2] (C=1, S=1). Містить 2 елементи: {0x2A, 0x5F}."
    run2_desc = "• Набіг f_q = 2: починається у слоті [3] (C=0, S=1), зміщений вправо. Містить 1 елемент: {0x12}. Оскільки O[2]=1, набіг існує."
    run3_desc = "• Слот [3] не має своїх канонічних елементів (O[3]=0), але зберігає зміщений елемент чужого набігу."
    run4_desc = "• Набіг f_q = 4: починається у слоті [4] (C=0, S=1), зміщений через заповненість попередніх слотів. Містить {0x8B}."

    parts.append(text(start_x + 20, by + 52, run1_desc, size=11, anchor="start"))
    parts.append(text(start_x + 20, by + 76, run2_desc, size=11, anchor="start"))
    parts.append(text(start_x + 20, by + 100, run3_desc, size=11, anchor="start"))
    parts.append(text(start_x + 20, by + 124, run4_desc, size=11, anchor="start"))

    render(os.path.join(IMG, "quotient-filter-run-cluster.svg"), W, H, *parts)


# ── 3. Зсув слотів при вставці (Robin Hood Displacement) ────────────────────
def fig_insertion_shift():
    W, H = 940, 520
    parts = []

    parts.append(text(W / 2, 28, "Вставка нового елемента: зсув набігів за правилом Робіна Гуда", size=16, bold=True))

    # Стан ДО вставки
    parts.append(text(120, 65, "Стан ДО вставки елемента e = (f_q=2, f_r=0x33):", size=13, bold=True))

    start_x = 70
    y_before = 85
    cw = 98
    ch = 90

    data_before = [
        (0, "0", "0", "0", "—"),
        (1, "1", "0", "0", "0x20"),
        (2, "1", "0", "0", "0x70"),
        (3, "0", "0", "0", "—"),
        (4, "0", "0", "0", "—"),
        (5, "0", "0", "0", "—"),
        (6, "0", "0", "0", "—"),
        (7, "0", "0", "0", "—"),
    ]

    for idx, occ, cont, shift, rem in data_before:
        cx = start_x + idx * cw
        is_empty = (rem == "—")
        parts.append(rect(cx, y_before, cw - 4, ch, fill="#ffffff" if is_empty else "#f8fafc", stroke=MUTED, sw=1.0, rx=3))
        parts.append(text(cx + (cw - 4) / 2, y_before + 18, f"[{idx}]", size=11, bold=True))
        parts.append(text(cx + (cw - 4) / 2, y_before + 40, f"O:{occ} C:{cont} S:{shift}", size=10, color=MUTED))
        parts.append(rect(cx + 8, y_before + 50, cw - 20, 26, fill="#e8f8f0" if not is_empty else "#ffffff", stroke=FIELD if not is_empty else MUTED, sw=1.0, rx=3))
        parts.append(text(cx + (cw - 4) / 2, y_before + 67, rem, size=11, color=FIELD if not is_empty else MUTED))

    # Пояснення кроку
    step_tb, _, _ = textbox(W / 2, 220, "Вставляємо e = (f_q=2, f_r=0x33). Канонічний слот [2] вже зайнятий залишком 0x70 (f_q=2).\nОскільки 0x33 < 0x70, новий залишок мусить стояти ПЕРЕД 0x70 для збереження порядку набігу.\nЕлемент 0x70 зсувається вправо у слот [3] і отримує прапорець is_shifted = 1, is_continuation = 1.", size=12, pad=8, fill="#fffbe6", stroke="#d48806")
    parts.append(step_tb)

    # Стрілка переходу
    parts.append(arrow(W / 2, 265, W / 2, 290, color=POS, sw=2.0))

    # Стан ПІСЛЯ вставки
    y_after = 310
    parts.append(text(120, y_after - 15, "Стан ПІСЛЯ вставки та прапорці оновлених комірок:", size=13, bold=True))

    data_after = [
        (0, "0", "0", "0", "—", False),
        (1, "1", "0", "0", "0x20", False),
        (2, "1", "0", "0", "0x33", True),   # Новий елемент
        (3, "0", "1", "1", "0x70", True),   # Зсунутий елемент
        (4, "0", "0", "0", "—", False),
        (5, "0", "0", "0", "—", False),
        (6, "0", "0", "0", "—", False),
        (7, "0", "0", "0", "—", False),
    ]

    for idx, occ, cont, shift, rem, is_changed in data_after:
        cx = start_x + idx * cw
        is_empty = (rem == "—")
        bg_col = "#fdecea" if is_changed else ("#ffffff" if is_empty else "#f8fafc")
        border_col = POS if is_changed else (MUTED if is_empty else LINE)
        parts.append(rect(cx, y_after, cw - 4, ch, fill=bg_col, stroke=border_col, sw=1.5 if is_changed else 1.0, rx=4))
        parts.append(text(cx + (cw - 4) / 2, y_after + 18, f"[{idx}]", size=11, bold=True))
        
        col_o = "#fa541c" if occ == "1" else MUTED
        col_c = "#722ed1" if cont == "1" else MUTED
        col_s = "#1890ff" if shift == "1" else MUTED
        parts.append(text(cx + 16, y_after + 40, f"O:{occ}", size=10, color=col_o, bold=(occ=="1")))
        parts.append(text(cx + 46, y_after + 40, f"C:{cont}", size=10, color=col_c, bold=(cont=="1")))
        parts.append(text(cx + 76, y_after + 40, f"S:{shift}", size=10, color=col_s, bold=(shift=="1")))

        rem_bg = "#e8f8f0" if not is_empty else "#ffffff"
        parts.append(rect(cx + 8, y_after + 50, cw - 20, 26, fill=rem_bg, stroke=FIELD if not is_empty else MUTED, sw=1.0, rx=3))
        parts.append(text(cx + (cw - 4) / 2, y_after + 67, rem, size=11, color=FIELD if not is_empty else MUTED, bold=is_changed))

    # Підписи під зміненими слотами
    parts.append(text(start_x + 2 * cw + (cw - 4) / 2, y_after + ch + 18, "Новий елемент (C=0, S=0)", size=10, color=POS, bold=True))
    parts.append(text(start_x + 3 * cw + (cw - 4) / 2, y_after + ch + 18, "Зсунутий (C=1, S=1)", size=10, color=POS, bold=True))

    # Підсумковий висновок
    tb_shift_summary, _, _ = textbox(W / 2, 485, "Каскадний зсув виконується виключно в межах одного суцільного кластера, не зачіпаючи решту таблиці", size=11, pad=6, fill="#ffffff", stroke=MUTED)
    parts.append(tb_shift_summary)

    render(os.path.join(IMG, "quotient-filter-insertion-shift.svg"), W, H, *parts)


# ── 4. Локальність доступу до пам'яті: Фільтр Блума проти Квошієнтного ───────
def fig_locality():
    W, H = 940, 520
    parts = []

    parts.append(text(W / 2, 28, "Локальність кешу та дискового I/O: Фільтр Блума проти Квошієнтного фільтра", size=16, bold=True))

    # Ліва колонка: Фільтр Блума (k розрізнених звернень)
    lx = 50
    ly = 65
    lw = 400
    lh = 390

    parts.append(rect(lx, ly, lw, lh, fill="#fdfdfe", stroke=MUTED, sw=1.0, rx=8))
    parts.append(text(lx + lw / 2, ly + 26, "Фільтр Блума (k = 4 хеш-функції)", size=14, color=POS, bold=True))

    tb_bloom_desc, _, _ = textbox(lx + lw / 2, ly + 72, "Запит ключа x вимагає k випадкових бітових проб.\nКожна проба потрапляє в окрему лінію кешу (L3 / RAM).\nДля SSD/NVMe: k випадкових зчитувань сторінок!", size=11, pad=6, fill="#fdecea", stroke=POS)
    parts.append(tb_bloom_desc)

    # Візуалізація 4 випадкових ліній
    for i, line_idx in enumerate([12, 148, 590, 891]):
        by = ly + 130 + i * 42
        parts.append(rect(lx + 20, by, lw - 40, 32, fill="#fff1f0", stroke=POS, sw=1.0, rx=3))
        parts.append(text(lx + 35, by + 20, f"Кеш-лінія #{line_idx}:", size=11, color=MUTED, anchor="start"))
        parts.append(text(lx + lw - 35, by + 20, f"h_{i+1}(x) → 1 біт (Cache Miss)", size=11, color=POS, bold=True, anchor="end"))

    tb_bloom_res, _, _ = textbox(lx + lw / 2, ly + 335, "Швидкість: обмежується затримкою пам'яті (Memory Latency)\nУтилізація кеш-лінії: лише 1 біт із 64 байтів (0.2%)", size=11, pad=6, fill="#fafbfc", stroke=MUTED)
    parts.append(tb_bloom_res)

    # Права колонка: Квошієнтний фільтр (суцільне лінійне зондування)
    rx = 490
    ry = 65
    rw = 400
    rh = 390

    parts.append(rect(rx, ry, rw, rh, fill="#fdfdfe", stroke=MUTED, sw=1.0, rx=8))
    parts.append(text(rx + rw / 2, ry + 26, "Квошієнтний фільтр (1 хеш-функція)", size=14, color=FIELD, bold=True))

    tb_qf_desc, _, _ = textbox(rx + rw / 2, ry + 72, "Запит ключа x обчислює 1 адресу слота f_q.\nПошук набігу сканує сусідні слоти лінійним зондуванням.\nУсі перевірки відбуваються в ОДНІЙ 64-байтовій кеш-лінії!", size=11, pad=6, fill="#e8f8f0", stroke=FIELD)
    parts.append(tb_qf_desc)

    # Візуалізація однієї кеш-лінії
    parts.append(rect(rx + 20, ry + 130, rw - 40, 140, fill="#f6ffed", stroke=FIELD, sw=1.5, rx=4))
    parts.append(text(rx + rw / 2, ry + 152, "Єдина 64-байтова кеш-лінія ЦП / 4КБ сторінка SSD", size=12, color=FIELD, bold=True))

    for s in range(4):
        slot_x = rx + 35 + s * 82
        slot_y = ry + 170
        parts.append(rect(slot_x, slot_y, 76, 50, fill="#ffffff", stroke=FIELD, sw=1.0, rx=3))
        parts.append(text(slot_x + 38, slot_y + 20, f"Слот [{s+2}]", size=10, bold=True))
        parts.append(text(slot_x + 38, slot_y + 38, "O C S rem", size=9, color=MUTED))

    # Стрілка лінійного скану під слотами
    parts.append(arrow(rx + 50, ry + 245, rx + rw - 50, ry + 245, color=POS, sw=1.8))
    parts.append(text(rx + rw / 2, ry + 238, "Лінійний скан у межах однієї кеш-лінії", size=10, color=POS, bold=True))

    tb_qf_res, _, _ = textbox(rx + rw / 2, ry + 335, "Швидкість: повна пропускна здатність кешу L1/L2 (Cache Hits)\nУтилізація: апаратний префетчер підвантажує сусідні слоти", size=11, pad=6, fill="#fafbfc", stroke=MUTED)
    parts.append(tb_qf_res)

    # Нижній загальний висновок
    tb_bottom_loc, _, _ = textbox(W / 2, 485, "Квошієнтний фільтр забезпечує на порядки вищу пропускну здатність на SSD та Flash-пам'яті завдяки послідовному доступу", size=11, pad=6, fill="#ffffff", stroke=MUTED)
    parts.append(tb_bottom_loc)

    render(os.path.join(IMG, "quotient-filter-vs-bloom-locality.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_anatomy()
    fig_runs_and_clusters()
    fig_insertion_shift()
    fig_locality()
    print("Усі 4 фігури успішно згенеровано у ./img/")

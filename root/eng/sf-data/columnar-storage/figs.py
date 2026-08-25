# -*- coding: utf-8 -*-
"""Фігури до статті «Стовпцеве зберігання» (Columnar Storage).
Запуск із теки теми: py -3 figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

GOOD = FIELD        # зелений — ефективне використання кешу / стовпцевий розклад
WEAK = POS          # червоний — баласт пам'яті / неефективне зчитування
HL_BLUE = "#eef4ff" # світло-синя заливка
ACCENT_BLUE = "#2457d6"
HL_GREEN = "#eafaf1"
HL_YELLOW = "#fef9e7"
HL_RED = "#fdf2f2"

# ── Фіг. 1: Рядковий (NSM) проти стовпцевого (DSM) розкладу ─────────────────
def fig_row_vs_column():
    W, H = 960, 480
    parts = [text(W / 2, 26, "Фізичне розміщення даних: рядковий (NSM) проти стовпцевого (DSM) розкладу", size=15, bold=True)]

    # Ліва панель: Рядковий розклад (NSM)
    parts.append(rect(20, 48, 445, 412, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(242, 74, "Рядковий розклад (NSM / OLTP)", size=14, bold=True, color=INK))
    parts.append(text(242, 94, "Кортежі зберігаються неперервно рядок за рядком", size=11, color=MUTED))

    # Візуалізація пам'яті рядкового розкладу
    rows_data = [
        ("Рядок 0", ["ID: 1", "Дата: 2026-08-01", "Сума: 450 грн", "Опис: Електроніка..."]),
        ("Рядок 1", ["ID: 2", "Дата: 2026-08-01", "Сума: 120 грн", "Опис: Книги та канц..."]),
        ("Рядок 2", ["ID: 3", "Дата: 2026-08-02", "Сума: 890 грн", "Опис: Одяг зимовий..."])
    ]
    
    y_off = 112
    for r_idx, (r_title, cols) in enumerate(rows_data):
        parts.append(rect(36, y_off, 413, 56, fill="#fbfcfd", stroke=MUTED, sw=1))
        parts.append(text(46, y_off + 16, r_title, size=10.5, bold=True, color=MUTED, anchor="start"))
        
        col_w = [45, 105, 95, 140]
        cx = 46
        for c_idx, c_text in enumerate(cols):
            is_target = (c_idx == 2) # Стовпець "Сума"
            bg_c = "#e8f5e9" if is_target else HL_RED
            st_c = GOOD if is_target else "#e0a0a0"
            parts.append(rect(cx, y_off + 24, col_w[c_idx], 24, fill=bg_c, stroke=st_c, sw=1.2, rx=3))
            parts.append(text(cx + col_w[c_idx]/2, y_off + 39, c_text, size=9.5, bold=is_target, color=GOOD if is_target else INK))
            cx += col_w[c_idx] + 5
        y_off += 66

    # Блок пояснення зчитування для NSM
    parts.append(rect(36, 316, 413, 62, fill=HL_RED, stroke=WEAK, sw=1.2))
    parts.append(text(242, 336, "Запит: SELECT SUM(Сума) FROM транзакції", size=11, bold=True, color=WEAK))
    parts.append(text(242, 354, "Зчитується 100% байтів усіх полів; ~80% даних у кеші — баласт", size=10, color=INK))
    parts.append(text(242, 368, "Пропускна здатність RAM витрачається на непотрібні поля", size=10, color=MUTED))

    parts.append(fitbox(36, 388, 413, 60,
                        "Властивість: миттєва вставка та вибірка цілого рядка за ключем.\nНедолік в аналітиці: шина пам'яті й L1/L2 кеш перевантажені\nполями, які не беруть участі в агрегації.",
                        size=10.5, fill=FILL, stroke="none", color=INK))

    # Права панель: Стовпцевий розклад (DSM)
    parts.append(rect(495, 48, 445, 412, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(717, 74, "Стовпцевий розклад (DSM / OLAP)", size=14, bold=True, color=INK))
    parts.append(text(717, 94, "Кожен стовпець зберігається як суцільний щільний масив", size=11, color=MUTED))

    # Візуалізація стовпців у DSM
    cols_dsm = [
        ("Стовпець «ID»", ["1", "2", "3", "..."], 85, FILL, LINE),
        ("Стовпець «Дата»", ["2026-08-01", "2026-08-01", "2026-08-02", "..."], 105, FILL, LINE),
        ("Стовпець «Сума»", ["450 грн", "120 грн", "890 грн", "..."], 105, HL_GREEN, GOOD),
        ("Стовпець «Опис»", ["Електр...", "Книги...", "Одяг...", "..."], 95, FILL, LINE)
    ]
    
    cx_dsm = 510
    for col_title, vals, cw, c_bg, c_st in cols_dsm:
        is_sum = (col_title == "Стовпець «Сума»")
        parts.append(rect(cx_dsm, 112, cw, 188, fill=c_bg if is_sum else "#fbfcfd", stroke=c_st, sw=1.8 if is_sum else 1))
        parts.append(fitbox(cx_dsm + 2, 116, cw - 4, 24, col_title, size=10, bold=True, fill="none", stroke="none", color=GOOD if is_sum else INK))
        
        y_val = 146
        for v in vals:
            parts.append(rect(cx_dsm + 6, y_val, cw - 12, 22, fill=HL_GREEN if is_sum else BG, stroke=GOOD if is_sum else MUTED, sw=1, rx=3))
            parts.append(text(cx_dsm + cw/2, y_val + 14, v, size=9.5, bold=is_sum, color=GOOD if is_sum else INK))
            y_val += 28
        cx_dsm += cw + 8

    # Блок пояснення зчитування для DSM
    parts.append(rect(511, 316, 413, 62, fill=HL_GREEN, stroke=GOOD, sw=1.2))
    parts.append(text(717, 336, "Запит: SELECT SUM(Сума) FROM транзакції", size=11, bold=True, color=GOOD))
    parts.append(text(717, 354, "Зчитується ВИКЛЮЧНО стовпець «Сума» (100% корисних байтів)", size=10, color=INK))
    parts.append(text(717, 368, "Лінійний доступ до пам'яті, ідеальна робота апаратного Prefetcher", size=10, color=MUTED))

    parts.append(fitbox(511, 388, 413, 60,
                        "Властивість: нульове читання зайвих стовпців, максимальний коефіцієнт\nстиснення завдяки однорідності типу даних, векторне виконання SIMD.\nКомпроміс: реконструкція повного кортежу вимагає склеювання стовпців.",
                        size=10.5, fill=FILL, stroke="none", color=INK))

    render(os.path.join(OUT, "row-vs-column-layout.svg"), W, H, *parts)
    print("Generated row-vs-column-layout.svg")


# ── Фіг. 2: Стовпцеві алгоритми стиснення та кодування ───────────────────────
def fig_columnar_encodings():
    W, H = 960, 480
    parts = [text(W / 2, 26, "Алгоритми кодування однорідних стовпців (Columnar Encodings)", size=15, bold=True)]

    # 4 блоки кодувань у сітці 2x2
    # 1. RLE (Run-Length Encoding)
    parts.append(rect(20, 50, 445, 195, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(242, 72, "1. Стиснення довжинами серій (RLE)", size=13, bold=True, color=ACCENT_BLUE))
    parts.append(text(242, 90, "Заміна довгих послідовностей однакових значень парами (значення, кількість)", size=10, color=MUTED))
    
    parts.append(text(46, 114, "Сирі дані:", size=10.5, bold=True, anchor="start"))
    raw_rle = ["UA", "UA", "UA", "UA", "PL", "PL", "DE", "DE", "DE", "DE", "DE"]
    rx = 116
    for val in raw_rle:
        parts.append(rect(rx, 102, 27, 20, fill=FILL, stroke=LINE, sw=1, rx=2))
        parts.append(text(rx + 13.5, 115, val, size=9.5))
        rx += 29

    parts.append(arrow(242, 130, 242, 148, color=ACCENT_BLUE, sw=1.5))

    parts.append(text(46, 168, "RLE-потік:", size=10.5, bold=True, anchor="start"))
    rle_res = [("UA", 4), ("PL", 2), ("DE", 5)]
    rx = 116
    for val, cnt in rle_res:
        parts.append(rect(rx, 155, 68, 26, fill=HL_BLUE, stroke=ACCENT_BLUE, sw=1.2, rx=3))
        parts.append(text(rx + 34, 171, "%s × %d" % (val, cnt), size=10, bold=True, color=ACCENT_BLUE))
        rx += 76
    parts.append(text(355, 171, "11 значень → 3 пари", size=10, color=FIELD, bold=True, anchor="start"))
    parts.append(text(242, 218, "Ідеально для відсортованих стовпців з низькою кардинальністю", size=10, color=MUTED))

    # 2. Bit-Packing / Frame of Reference (FoR)
    parts.append(rect(495, 50, 445, 195, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(717, 72, "2. Зсув від бази та бітове пакування (FoR / Bit-Packing)", size=13, bold=True, color=ACCENT_BLUE))
    parts.append(text(717, 90, "Віднімання мінімального значення й пакування чисел у мінімальну кількість бітів", size=10, color=MUTED))

    parts.append(text(512, 114, "32-бітні цілі:", size=10.5, bold=True, anchor="start"))
    for_raw = [1002, 1005, 1001, 1007, 1003, 1000]
    fx = 596
    for v in for_raw:
        parts.append(rect(fx, 102, 44, 20, fill=FILL, stroke=LINE, sw=1, rx=2))
        parts.append(text(fx + 22, 115, str(v), size=9.5))
        fx += 48

    parts.append(arrow(717, 130, 717, 148, color=ACCENT_BLUE, sw=1.5))

    parts.append(text(512, 168, "База = 1000:", size=10.5, bold=True, anchor="start"))
    for_deltas = [2, 5, 1, 7, 3, 0]
    fx = 596
    for v in for_deltas:
        parts.append(rect(fx, 156, 44, 24, fill=HL_GREEN, stroke=FIELD, sw=1.2, rx=2))
        parts.append(text(fx + 22, 171, "%d (3b)" % v, size=9.5, bold=True, color=FIELD))
        fx += 48
    parts.append(text(717, 218, "Діапазон [0..7] потребує лише 3 біти замість 32 бітів (економія 90.6%)", size=10, color=FIELD, bold=True))

    # 3. Dictionary Encoding (Словникове кодування)
    parts.append(rect(20, 260, 445, 205, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(242, 282, "3. Словникове кодування (Dictionary Encoding)", size=13, bold=True, color=ACCENT_BLUE))
    parts.append(text(242, 300, "Заміна довгих рядків компактними числовими індексами у словнику", size=10, color=MUTED))

    # Словник
    parts.append(rect(36, 320, 135, 95, fill=HL_YELLOW, stroke="#d4ac0d", sw=1.2))
    parts.append(text(103, 336, "Словник (Dictionary)", size=9.5, bold=True))
    parts.append(text(46, 356, "0 → \"Kyiv\"", size=9.5, anchor="start"))
    parts.append(text(46, 374, "1 → \"Lviv\"", size=9.5, anchor="start"))
    parts.append(text(46, 392, "2 → \"Odesa\"", size=9.5, anchor="start"))

    # Масив індексів
    parts.append(rect(190, 320, 260, 95, fill=HL_BLUE, stroke=ACCENT_BLUE, sw=1.2))
    parts.append(text(320, 336, "Масив індексів стовпця", size=9.5, bold=True, color=ACCENT_BLUE))
    parts.append(text(320, 356, "Рядок: [ 0, 1, 0, 2, 1, 0, 0, 2 ]", size=10, bold=True))
    parts.append(text(320, 376, "Замість 8 довгих текстових рядків —", size=9.5, color=MUTED))
    parts.append(text(320, 394, "8 компактних 2-бітних індексів", size=9.5, bold=True, color=FIELD))

    parts.append(text(242, 444, "Фільтрація WHERE місто = 'Kyiv' перетворюється на WHERE id = 0", size=10, color=INK))

    # 4. Delta Encoding (Дельта-кодування)
    parts.append(rect(495, 260, 445, 205, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(717, 282, "4. Дельта-кодування (Delta Encoding)", size=13, bold=True, color=ACCENT_BLUE))
    parts.append(text(717, 300, "Збереження різниці між сусідніми значеннями (часові ряди, ID)", size=10, color=MUTED))

    parts.append(text(512, 326, "Часові мітки:", size=10, bold=True, anchor="start"))
    ts_raw = [1700000000, 1700000004, 1700000010, 1700000015]
    tx = 604
    for v in ts_raw:
        parts.append(rect(tx, 316, 76, 20, fill=FILL, stroke=LINE, sw=1, rx=2))
        parts.append(text(tx + 38, 329, str(v), size=9.5))
        tx += 80

    parts.append(arrow(717, 344, 717, 360, color=ACCENT_BLUE, sw=1.5))

    parts.append(text(512, 382, "Дельти:", size=10, bold=True, anchor="start"))
    ts_deltas = [("Base", 1700000000), ("+4", 4), ("+6", 6), ("+5", 5)]
    tx = 604
    for lbl, _ in ts_deltas:
        parts.append(rect(tx, 372, 76, 24, fill=HL_GREEN, stroke=FIELD, sw=1.2, rx=2))
        parts.append(text(tx + 38, 387, lbl, size=9.5, bold=True, color=FIELD))
        tx += 80

    parts.append(text(717, 422, "Дельти мають малу величину й стискаються через RLE / Bit-Packing", size=10, color=MUTED))
    parts.append(text(717, 444, "Основа зберігання часових рядів (Gorilla / DoubleDelta)", size=10, bold=True, color=INK))

    render(os.path.join(OUT, "columnar-encodings.svg"), W, H, *parts)
    print("Generated columnar-encodings.svg")


# ── Фіг. 3: Векторизована фільтрація SIMD та пізня матеріалізація ────────────
def fig_vectorized_simd():
    W, H = 960, 480
    parts = [text(W / 2, 26, "Векторизована фільтрація SIMD та пізня матеріалізація (Late Materialization)", size=15, bold=True)]

    # Крок 1: Векторне завантаження стовпця
    parts.append(rect(20, 52, 280, 405, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(160, 76, "1. Векторне завантаження", size=12.5, bold=True, color=ACCENT_BLUE))
    parts.append(text(160, 94, "Стовпець «Вік» (32-бітні цілі)", size=10, color=MUTED))

    vals = [24, 45, 19, 62, 31, 58, 17, 40]
    vy = 115
    for i, v in enumerate(vals):
        parts.append(rect(45, vy, 230, 24, fill=FILL, stroke=LINE, sw=1, rx=2))
        parts.append(text(70, vy + 15, "Рядок %d:" % i, size=9.5, color=MUTED, anchor="start"))
        parts.append(text(220, vy + 15, str(v), size=10, bold=True, anchor="end"))
        vy += 28

    parts.append(fitbox(30, 355, 260, 90,
                        "Векторний блок (наприклад, 1024 або 4096 елементів) повністю поміщається в L1-кеш процесора.\nНуль віртуальних викликів next().",
                        size=9.5, fill=FILL, stroke="none", color=INK))

    # Стрілка між кроком 1 і 2
    parts.append(arrow(305, 230, 335, 230, color=ACCENT_BLUE, sw=2))

    # Крок 2: SIMD Порівняння
    parts.append(rect(340, 52, 290, 405, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(485, 76, "2. SIMD Порівняння (AVX-256)", size=12.5, bold=True, color=ACCENT_BLUE))
    parts.append(text(485, 94, "Предикат: WHERE Вік >= 30", size=10.5, bold=True, color=POS))

    # 256-бітний SIMD регістр
    parts.append(rect(352, 115, 266, 45, fill=HL_BLUE, stroke=ACCENT_BLUE, sw=1.5, rx=3))
    parts.append(text(485, 133, "_mm256_cmpgt_epi32(vec, 29)", size=9.5, bold=True, color=ACCENT_BLUE))
    parts.append(text(485, 149, "1 тактова операція CPU над 8 числами", size=9.5, color=MUTED))

    # Результат: Бітова маска (Selection Vector)
    parts.append(text(485, 185, "Бітова маска вибірки (Selection Mask):", size=10, bold=True))
    
    mask_res = [(24, 0, WEAK), (45, 1, FIELD), (19, 0, WEAK), (62, 1, FIELD),
                (31, 1, FIELD), (58, 1, FIELD), (17, 0, WEAK), (40, 1, FIELD)]
    
    my = 202
    for v, m, col in mask_res:
        bg_m = HL_GREEN if m == 1 else HL_RED
        parts.append(rect(370, my, 230, 22, fill=bg_m, stroke=col, sw=1.2, rx=2))
        parts.append(text(390, my + 14, "Вік %d" % v, size=9.5, color=INK, anchor="start"))
        parts.append(text(570, my + 14, "Маска: %d" % m, size=9.5, bold=True, color=col, anchor="end"))
        my += 26

    parts.append(fitbox(350, 412, 270, 36, "Розгалуження if відсутні → нуль branch mispredictions!", size=9.5, fill=HL_GREEN, stroke=FIELD, color=FIELD, bold=True))

    # Стрілка між кроком 2 і 3
    parts.append(arrow(635, 230, 665, 230, color=ACCENT_BLUE, sw=2))

    # Крок 3: Пізня матеріалізація
    parts.append(rect(670, 52, 270, 405, fill=BG, stroke=MUTED, sw=1.2))
    parts.append(text(805, 76, "3. Пізня матеріалізація", size=12.5, bold=True, color=FIELD))
    parts.append(text(805, 94, "Зчитування решти стовпців за маскою", size=10, color=MUTED))

    # Підсумкові рядки
    parts.append(text(805, 125, "Зчитуємо «Ім'я» та «Email»", size=10, bold=True))
    parts.append(text(805, 140, "лише для відфільтрованих індексів:", size=9.5, color=MUTED))

    p_rows = [
        (1, "Рядок 1: Олена (45 р.)"),
        (3, "Рядок 3: Тарас (62 р.)"),
        (4, "Рядок 4: Анна (31 р.)"),
        (5, "Рядок 5: Ігор (58 р.)"),
        (7, "Рядок 7: Марія (40 р.)")
    ]
    py = 160
    for r_idx, r_text in p_rows:
        parts.append(rect(685, py, 240, 26, fill=HL_GREEN, stroke=FIELD, sw=1.2, rx=3))
        parts.append(text(695, py + 16, r_text, size=9.5, bold=True, color=INK, anchor="start"))
        py += 32

    parts.append(fitbox(680, 345, 250, 100,
                        "Рядки 0, 2, 6 відкинуто на етапі бітової маски.\nТекстові поля «Ім'я» та «Email» для них навіть НЕ завантажувалися з пам'яті чи диска!",
                        size=9.5, fill=HL_YELLOW, stroke="#d4ac0d", color=INK))

    render(os.path.join(OUT, "vectorized-simd-filter.svg"), W, H, *parts)
    print("Generated vectorized-simd-filter.svg")


# ── Фіг. 4: Структура файлу Parquet та механізм Data Skipping ───────────────
def fig_parquet_layout():
    W, H = 960, 510
    parts = [text(W / 2, 26, "Анатомія файлу Apache Parquet та механізм Data Skipping (PAX-модель)", size=15, bold=True)]

    # Контейнер Parquet файлу
    parts.append(rect(20, 48, 920, 450, fill="#fafbfc", stroke=MUTED, sw=1.2))

    # Header
    parts.append(rect(35, 60, 890, 26, fill=FILL, stroke=LINE, sw=1.2, rx=3))
    parts.append(text(480, 76, "Magic Number: 'PAR1' (4 байти заголовка)", size=10.5, bold=True, color=INK))

    # Row Group 0
    parts.append(rect(35, 94, 890, 164, fill=BG, stroke=ACCENT_BLUE, sw=1.5, rx=4))
    parts.append(text(60, 112, "Row Group 0 (Група рядків, наприклад 512 MB або 1 000 000 рядків)", size=11, bold=True, color=ACCENT_BLUE, anchor="start"))

    # Стовпцеві чанки всередині Row Group 0
    chunks = [
        ("Column Chunk 0: «User_ID»", ["Page 0 (Dict)", "Page 1 (Data)", "Page 2 (Data)"], 275),
        ("Column Chunk 1: «Amount»", ["Data Page 0 (Plain)", "Data Page 1 (Plain)", "Data Page 2 (Plain)"], 285),
        ("Column Chunk 2: «Status»", ["Dict Page", "Data Page 0 (RLE)", "Data Page 1 (RLE)"], 285)
    ]
    cx = 50
    for ch_title, pages, ch_w in chunks:
        parts.append(rect(cx, 124, ch_w, 124, fill=HL_BLUE, stroke=ACCENT_BLUE, sw=1.2, rx=3))
        parts.append(text(cx + ch_w/2, 140, ch_title, size=10, bold=True, color=ACCENT_BLUE))
        
        # Сторінки всередині чанка
        py = 152
        for pg in pages:
            parts.append(rect(cx + 8, py, ch_w - 16, 22, fill=BG, stroke=MUTED, sw=1, rx=2))
            parts.append(text(cx + ch_w/2, py + 14, pg, size=9.5, color=INK))
            py += 26
        cx += ch_w + 16

    # Row Group 1 (Згорнута для схеми)
    parts.append(rect(35, 266, 890, 38, fill=FILL, stroke=MUTED, sw=1, rx=3))
    parts.append(text(480, 289, "Row Group 1 (наступні 1 000 000 рядків: Column Chunk 0, 1, 2...)", size=10.5, color=MUTED))

    # File Footer (Нижня частина Parquet файлу з метаданими)
    parts.append(rect(35, 312, 890, 146, fill=HL_YELLOW, stroke="#d4ac0d", sw=1.5, rx=4))
    parts.append(text(480, 330, "File Footer: FileMetaData (Thrift Metadata)", size=12, bold=True, color="#7d6608"))

    # Складові футера
    parts.append(rect(50, 344, 270, 102, fill=BG, stroke="#b7950b", sw=1, rx=3))
    parts.append(text(185, 362, "Схема таблиці (Schema)", size=10, bold=True))
    parts.append(text(60, 382, "• Стовпець 0: int64 user_id", size=9.5, anchor="start"))
    parts.append(text(60, 402, "• Стовпець 1: double amount", size=9.5, anchor="start"))
    parts.append(text(60, 422, "• Стовпець 2: byte_array status", size=9.5, anchor="start"))

    parts.append(rect(335, 344, 370, 102, fill=BG, stroke="#b7950b", sw=1, rx=3))
    parts.append(text(520, 362, "Статистика стовпців (Data Skipping)", size=10, bold=True, color=FIELD))
    parts.append(text(345, 382, "• Row Group 0 [amount]: min=10.50, max=450.00", size=9.5, color=FIELD, bold=True, anchor="start"))
    parts.append(text(345, 402, "• Row Group 1 [amount]: min=500.00, max=1200.00", size=9.5, color=MUTED, anchor="start"))
    parts.append(text(345, 424, "Запит WHERE amount > 490 повністю пропускає Row Group 0!", size=9.5, color=POS, bold=True, anchor="start"))

    parts.append(rect(720, 344, 190, 102, fill=BG, stroke="#b7950b", sw=1, rx=3))
    parts.append(text(815, 362, "Зсуви та розміри", size=10, bold=True))
    parts.append(text(730, 384, "• Офсети Row Groups", size=9.5, color=MUTED, anchor="start"))
    parts.append(text(730, 404, "• Footer Length (4B)", size=9.5, color=MUTED, anchor="start"))
    parts.append(text(730, 424, "• Magic 'PAR1' (4B)", size=9.5, bold=True, color=INK, anchor="start"))

    # Підсумкова стрілка
    parts.append(text(480, 478, "Читач Parquet спочатку зчитує кінець файлу (Footer), аналізує Min/Max статистики й завантажує лише потрібні байти Chunks", size=10, bold=True, color=INK))

    render(os.path.join(OUT, "parquet-file-layout.svg"), W, H, *parts)
    print("Generated parquet-file-layout.svg")


if __name__ == "__main__":
    fig_row_vs_column()
    fig_columnar_encodings()
    fig_vectorized_simd()
    fig_parquet_layout()
    print("All figures generated successfully.")

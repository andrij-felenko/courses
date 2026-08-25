# -*- coding: utf-8 -*-
"""Фігури до теми «Планувальник запитів та аналіз EXPLAIN»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Конвеєр обробки запиту: від SQL до виконання ───────────────────────
def fig_query_pipeline():
    W, H = 980, 480
    frags = []

    blocks = [
        ("SQL-запит", "Декларативний опис:\nщо саме вибрати,\nбез вказівки як"),
        ("Парсер та аналіз", "Синтаксичний аналіз,\nперевірка типів і назв,\nпобудова дерева AST"),
        ("Переписувач", "Розгортання в'ю,\nспрощення виразів,\nпроштовхування фільтрів"),
        ("Оптимізатор (CBO)", "Простір планів,\nоцінка селективності,\nрозрахунок вартості"),
        ("Рушій виконання", "Ітератор Volcano:\nвузли викликають next(),\nповертаючи кортежі"),
    ]

    bx_coords = [40, 230, 420, 610, 800]
    box_w = 140
    box_h = 170
    box_y = 110

    for i, (title, desc) in enumerate(blocks):
        x = bx_coords[i]
        is_opt = (i == 3)
        col_border = FIELD if is_opt else LINE
        col_fill = "#eef9f1" if is_opt else FILL
        sw = 2.5 if is_opt else 1.5

        frags.append(rect(x, box_y, box_w, box_h, rx=8, fill=col_fill, stroke=col_border, sw=sw))
        frags.append(text(x + box_w / 2, box_y + 30, title, size=13, bold=True, color=col_border))
        frags.append(line(x + 12, box_y + 44, x + box_w - 12, box_y + 44, color=MUTED, sw=1, dash="3 3"))
        frags.append(fitbox(x + 8, box_y + 55, box_w - 16, box_h - 65, desc, size=11, color=INK))

        if i < len(blocks) - 1:
            next_x = bx_coords[i + 1]
            frags.append(arrow(x + box_w + 4, box_y + box_h / 2, next_x - 4, box_y + box_h / 2, color=INK, sw=1.8))

    cat_x, cat_y, cat_w, cat_h = 590, 340, 180, 95
    frags.append(rect(cat_x, cat_y, cat_w, cat_h, rx=6, fill="#fdfaf3", stroke="#d97706", sw=1.5))
    frags.append(text(cat_x + cat_w / 2, cat_y + 24, "Системний каталог", size=12, bold=True, color="#d97706"))
    cat_desc = "Гістограми розподілу,\nсписки частих значень (MCV),\nкількість сторінок і кортежів"
    frags.append(fitbox(cat_x + 6, cat_y + 34, cat_w - 12, cat_h - 40, cat_desc, size=10, color=INK))

    frags.append(arrow(cat_x + cat_w / 2, cat_y - 4, bx_coords[3] + box_w / 2, box_y + box_h + 4, color="#d97706", sw=1.8))
    frags.append(text(cat_x + cat_w / 2 + 55, cat_y - 20, "статистика", size=11, color="#d97706", italic=True))

    top_labels = [
        (135, "текст"),
        (325, "AST"),
        (515, "логічний план"),
        (705, "фізичний план"),
    ]
    for lx, lt in top_labels:
        frags.append(text(lx, box_y - 14, lt, size=11, color=MUTED, italic=True))

    return render(os.path.join(OUT, 'query-pipeline.svg'), W, H, *frags,
                  title="Життєвий цикл запиту: від тексту SQL до виконання")


# ── 2. Чотири способи сканування таблиці ──────────────────────────────────
def fig_scan_types():
    W, H = 980, 560
    frags = []

    scans = [
        ("Seq Scan", "Послідовне читання",
         "Читає всі сторінки таблиці\nпідряд. Ефективно при вибірці\nпонад 15-20% рядків завдяки\nпослідовному I/O та випереджальному\nчитанню (read-ahead).",
         NEG),
        ("Index Scan", "Індексний пошук",
         "Спуск по B-дереву до листків,\nзвідки за покажчиками (TID)\nчитаються сторінки таблиці.\nШвидко для кількох рядків,\nале створює випадковий I/O.",
         FIELD),
        ("Index Only Scan", "Виключно за індексом",
         "Усі потрібні поля є в індексі.\nДані таблиці не читаються,\nякщо карта видимості (VM)\nпідтверджує актуальність\nсторінки для всіх транзакцій.",
         "#8e44ad"),
        ("Bitmap Scan", "Двоетапна вибірка",
         "Етап 1: BitmapIndexScan збирає\nномери сторінок у бітову мапу.\nЕтап 2: BitmapHeapScan сортує\nномери сторінок і читає таблицю\nвпорядковано без зайвих повернень.",
         "#d97706"),
    ]

    col_w = 215
    col_gap = 20
    start_x = 35
    top_y = 60
    box_h = 450

    for i, (title, subtitle, desc, col) in enumerate(scans):
        x = start_x + i * (col_w + col_gap)
        frags.append(rect(x, top_y, col_w, box_h, rx=8, fill=FILL, stroke=col, sw=2))

        # Шапка картки
        frags.append(rect(x, top_y, col_w, 65, rx=8, fill=col, stroke=col))
        frags.append(text(x + col_w / 2, top_y + 26, title, size=14, bold=True, color="#ffffff"))
        frags.append(text(x + col_w / 2, top_y + 48, subtitle, size=11, color="#ffffff"))

        # Схематичний рисунок механізму всередині картки
        diag_y = top_y + 80
        diag_h = 160
        frags.append(rect(x + 10, diag_y, col_w - 20, diag_h, rx=4, fill="#ffffff", stroke="#d1d5db", sw=1))

        if i == 0:  # Seq Scan
            for p in range(4):
                px = x + 25 + p * 42
                frags.append(rect(px, diag_y + 40, 36, 55, rx=3, fill="#e8f4fd", stroke=NEG, sw=1.2))
                frags.append(text(px + 18, diag_y + 72, f"P{p+1}", size=11, color=NEG, bold=True))
            frags.append(arrow(x + 20, diag_y + 115, x + col_w - 20, diag_y + 115, color=NEG, sw=2))
            frags.append(text(x + col_w / 2, diag_y + 138, "послідовний I/O", size=10, color=NEG, italic=True))

        elif i == 1:  # Index Scan
            frags.append(rect(x + 75, diag_y + 15, 45, 26, rx=2, fill="#eef9f1", stroke=FIELD, sw=1))
            frags.append(text(x + 97, diag_y + 32, "Корінь", size=9, color=FIELD))
            frags.append(rect(x + 30, diag_y + 55, 50, 24, rx=2, fill="#eef9f1", stroke=FIELD, sw=1))
            frags.append(text(x + 55, diag_y + 71, "Листок", size=9, color=FIELD))
            frags.append(line(x + 85, diag_y + 41, x + 65, diag_y + 55, color=FIELD, sw=1.2))

            frags.append(rect(x + 120, diag_y + 70, 60, 65, rx=3, fill="#fdfaf3", stroke=LINE, sw=1))
            frags.append(text(x + 150, diag_y + 88, "Таблиця", size=9, color=MUTED))
            frags.append(text(x + 150, diag_y + 112, "TID (3,8)", size=9, bold=True, color=POS))
            frags.append(arrow(x + 80, diag_y + 67, x + 118, diag_y + 105, color=POS, sw=1.5))
            frags.append(text(x + col_w / 2, diag_y + 150, "випадковий доступ до купи", size=10, color=POS, italic=True))

        elif i == 2:  # Index Only Scan
            frags.append(rect(x + 25, diag_y + 30, 70, 50, rx=3, fill="#f5eefb", stroke="#8e44ad", sw=1.2))
            frags.append(text(x + 60, diag_y + 52, "Листок", size=10, color="#8e44ad", bold=True))
            frags.append(text(x + 60, diag_y + 68, "Ключ + Поля", size=9, color="#8e44ad"))

            frags.append(rect(x + 115, diag_y + 30, 70, 50, rx=3, fill="#eafaf1", stroke=FIELD, sw=1.2))
            frags.append(text(x + 150, diag_y + 52, "Карта VM", size=10, color=FIELD, bold=True))
            frags.append(text(x + 150, diag_y + 68, "all-visible: 1", size=9, color=FIELD))

            frags.append(text(x + col_w / 2, diag_y + 115, "Читання з купи = 0", size=11, color="#8e44ad", bold=True))
            frags.append(text(x + col_w / 2, diag_y + 138, "дані зібрано з індексу", size=10, color=MUTED, italic=True))

        elif i == 3:  # Bitmap Scan
            frags.append(rect(x + 20, diag_y + 18, 155, 38, rx=3, fill="#fef5e7", stroke="#d97706", sw=1.2))
            frags.append(text(x + 97, diag_y + 34, "Bitmap у RAM", size=10, bold=True, color="#d97706"))
            frags.append(text(x + 97, diag_y + 49, "Page 2: [..] | Page 7: [..]", size=9, color=INK))

            frags.append(arrow(x + 97, diag_y + 58, x + 97, diag_y + 80, color="#d97706", sw=1.5))

            frags.append(rect(x + 25, diag_y + 85, 42, 40, rx=2, fill="#fdfaf3", stroke=LINE, sw=1))
            frags.append(text(x + 46, diag_y + 108, "P 2", size=10, bold=True, color=INK))

            frags.append(rect(x + 125, diag_y + 85, 42, 40, rx=2, fill="#fdfaf3", stroke=LINE, sw=1))
            frags.append(text(x + 146, diag_y + 108, "P 7", size=10, bold=True, color=INK))

            frags.append(text(x + col_w / 2, diag_y + 146, "сортований I/O по сторінках", size=10, color="#d97706", italic=True))

        frags.append(fitbox(x + 10, diag_y + diag_h + 15, col_w - 20, box_h - diag_h - 95, desc, size=11, color=INK))

    return render(os.path.join(OUT, 'scan-types.svg'), W, H, *frags,
                  title="Порівняння фізичних операторів доступу до даних")


# ── 3. Три фізичні алгоритми з'єднання ─────────────────────────────────────
def fig_join_strategies():
    W, H = 980, 520
    frags = []

    joins = [
        ("Nested Loop", "Вкладений цикл",
         "Для кожного кортежу зовнішньої\nтаблиці A виконується пошук\nу внутрішній таблиці B.\nІдеально, якщо A крихітна (1-100),\nа таблиця B має індекс за ключем.",
         NEG),
        ("Hash Join", "З'єднання хешуванням",
         "Фаза 1 (Build): будує хеш-таблицю\nпо меншій таблиці B у пам'яті.\nФаза 2 (Probe): сканує таблицю A\nі шукає збіги за хеш-ключем.\nШвидко для великих невпорядкованих даних.",
         FIELD),
        ("Merge Join", "З'єднання злиттям",
         "Обидва входи мають бути\nвідсортовані за ключем з'єднання.\nДва курсори сканують входи\nсинхронно за один прохід.\nМінімальна пам'ять, ідеально при індексах.",
         "#2457d6"),
    ]

    col_w = 290
    col_gap = 25
    start_x = 35
    top_y = 50
    box_h = 430

    for i, (title, subtitle, desc, col) in enumerate(joins):
        x = start_x + i * (col_w + col_gap)
        frags.append(rect(x, top_y, col_w, box_h, rx=8, fill=FILL, stroke=col, sw=2))

        frags.append(rect(x, top_y, col_w, 60, rx=8, fill=col, stroke=col))
        frags.append(text(x + col_w / 2, top_y + 25, title, size=15, bold=True, color="#ffffff"))
        frags.append(text(x + col_w / 2, top_y + 46, subtitle, size=11, color="#ffffff"))

        diag_y = top_y + 75
        diag_h = 165
        frags.append(rect(x + 10, diag_y, col_w - 20, diag_h, rx=4, fill="#ffffff", stroke="#d1d5db", sw=1))

        if i == 0:  # Nested Loop
            frags.append(rect(x + 20, diag_y + 35, 65, 95, rx=3, fill="#fdfaf3", stroke=LINE, sw=1))
            frags.append(text(x + 52, diag_y + 52, "A (Outer)", size=10, bold=True, color=INK))
            frags.append(text(x + 52, diag_y + 75, "ряд 1 →", size=9, color=POS, bold=True))
            frags.append(text(x + 52, diag_y + 95, "ряд 2 →", size=9, color=MUTED))
            frags.append(text(x + 52, diag_y + 115, "ряд N →", size=9, color=MUTED))

            frags.append(rect(x + 175, diag_y + 35, 80, 95, rx=3, fill="#eef9f1", stroke=FIELD, sw=1))
            frags.append(text(x + 215, diag_y + 52, "B (Inner)", size=10, bold=True, color=FIELD))
            frags.append(text(x + 215, diag_y + 75, "Index Scan", size=9, color=FIELD))
            frags.append(text(x + 215, diag_y + 95, "або SeqScan", size=9, color=MUTED))
            frags.append(text(x + 215, diag_y + 115, "на ітерацію", size=9, color=MUTED))

            frags.append(arrow(x + 88, diag_y + 72, x + 172, diag_y + 72, color=POS, sw=1.8))
            frags.append(text(x + 130, diag_y + 64, "probe", size=9, color=POS, italic=True))
            frags.append(text(x + col_w / 2, diag_y + 150, "N ітерацій пошуку по B", size=10, color=POS, bold=True))

        elif i == 1:  # Hash Join
            frags.append(rect(x + 20, diag_y + 20, 65, 45, rx=2, fill="#eef9f1", stroke=FIELD, sw=1))
            frags.append(text(x + 52, diag_y + 38, "Таблиця B", size=9, bold=True, color=FIELD))
            frags.append(text(x + 52, diag_y + 52, "(Build)", size=9, color=MUTED))

            frags.append(rect(x + 160, diag_y + 20, 95, 60, rx=3, fill="#fef5e7", stroke="#d97706", sw=1.2))
            frags.append(text(x + 207, diag_y + 38, "Хеш-таблиця", size=10, bold=True, color="#d97706"))
            frags.append(text(x + 207, diag_y + 54, "у пам'яті (RAM)", size=9, color=MUTED))
            frags.append(text(x + 207, diag_y + 68, "key → [кортежі]", size=9, color=INK))

            frags.append(arrow(x + 88, diag_y + 42, x + 156, diag_y + 42, color=FIELD, sw=1.5))
            frags.append(text(x + 122, diag_y + 35, "1. Build", size=9, color=FIELD, bold=True))

            frags.append(rect(x + 20, diag_y + 95, 65, 45, rx=2, fill="#fdfaf3", stroke=LINE, sw=1))
            frags.append(text(x + 52, diag_y + 113, "Таблиця A", size=9, bold=True, color=INK))
            frags.append(text(x + 52, diag_y + 127, "(Probe)", size=9, color=MUTED))

            frags.append(arrow(x + 88, diag_y + 117, x + 175, diag_y + 83, color=POS, sw=1.5))
            frags.append(text(x + 130, diag_y + 115, "2. Probe", size=9, color=POS, bold=True))
            frags.append(text(x + col_w / 2, diag_y + 152, "Одноразовий прохід по A і B", size=10, color=FIELD, bold=True))

        elif i == 2:  # Merge Join
            frags.append(rect(x + 25, diag_y + 25, 95, 95, rx=3, fill="#e8f4fd", stroke="#2457d6", sw=1))
            frags.append(text(x + 72, diag_y + 42, "Сортована A", size=9, bold=True, color="#2457d6"))
            frags.append(text(x + 72, diag_y + 62, "ID: 10 → [✓]", size=9, color=INK))
            frags.append(text(x + 72, diag_y + 82, "ID: 25   [ ]", size=9, color=MUTED))
            frags.append(text(x + 72, diag_y + 102, "ID: 40   [ ]", size=9, color=MUTED))

            frags.append(rect(x + 155, diag_y + 25, 95, 95, rx=3, fill="#e8f4fd", stroke="#2457d6", sw=1))
            frags.append(text(x + 202, diag_y + 42, "Сортована B", size=9, bold=True, color="#2457d6"))
            frags.append(text(x + 202, diag_y + 62, "ID: 10 → [✓]", size=9, color=INK))
            frags.append(text(x + 202, diag_y + 82, "ID: 18   [ ]", size=9, color=MUTED))
            frags.append(text(x + 202, diag_y + 102, "ID: 25   [ ]", size=9, color=MUTED))

            frags.append(line(x + 122, diag_y + 62, x + 152, diag_y + 62, color=FIELD, sw=2))
            frags.append(text(x + 137, diag_y + 55, "==", size=11, bold=True, color=FIELD))
            frags.append(text(x + col_w / 2, diag_y + 148, "Обидва курсори йдуть уперед", size=10, color="#2457d6", bold=True))

        frags.append(fitbox(x + 10, diag_y + diag_h + 15, col_w - 20, box_h - diag_h - 90, desc, size=11, color=INK))

    return render(os.path.join(OUT, 'join-strategies.svg'), W, H, *frags,
                  title="Порівняння алгоритмів з'єднання: Nested Loop, Hash Join та Merge Join")


# ── 4. Анатомія дерева плану EXPLAIN та потік даних ────────────────────────
def fig_explain_tree_flow():
    W, H = 980, 500
    frags = []

    rx, ry, rw, rh = 340, 50, 300, 90
    frags.append(rect(rx, ry, rw, rh, rx=6, fill="#eef9f1", stroke=FIELD, sw=2))
    frags.append(text(rx + rw / 2, ry + 24, "->  Hash Join  (parent)", size=13, bold=True, color=FIELD))
    frags.append(text(rx + rw / 2, ry + 45, "cost=184.20..942.50  rows=4300  width=72", size=10, color=INK))
    frags.append(text(rx + rw / 2, ry + 65, "actual time=0.82..14.30  rows=4120  loops=1", size=10, bold=True, color=POS))
    frags.append(text(rx + rw / 2, ry + 80, "Hash Cond: (orders.user_id = users.id)", size=9, color=MUTED))

    lx, ly, lw, lh = 80, 220, 320, 100
    frags.append(rect(lx, ly, lw, lh, rx=6, fill=FILL, stroke=LINE, sw=1.5))
    frags.append(text(lx + lw / 2, ly + 24, "->  Seq Scan on orders", size=12, bold=True, color=INK))
    frags.append(text(lx + lw / 2, ly + 45, "cost=0.00..540.00  rows=15000  width=40", size=10, color=INK))
    frags.append(text(lx + lw / 2, ly + 65, "actual time=0.04..6.80  rows=15000  loops=1", size=10, bold=True, color=POS))
    frags.append(text(lx + lw / 2, ly + 85, "Filter: (status = 'paid')", size=9, color=MUTED))

    hx, hy, hw, hh = 560, 200, 310, 80
    frags.append(rect(hx, hy, hw, hh, rx=6, fill="#fef5e7", stroke="#d97706", sw=1.5))
    frags.append(text(hx + hw / 2, hy + 24, "->  Hash", size=12, bold=True, color="#d97706"))
    frags.append(text(hx + hw / 2, hy + 45, "cost=160.00..160.00  rows=1200  width=32", size=10, color=INK))
    frags.append(text(hx + hw / 2, hy + 65, "actual time=0.74..0.74  rows=1180  loops=1", size=10, bold=True, color=POS))

    ix, iy, iw, ih = 560, 340, 310, 95
    frags.append(rect(ix, iy, iw, ih, rx=6, fill=FILL, stroke=LINE, sw=1.5))
    frags.append(text(ix + iw / 2, iy + 24, "->  Index Scan on users (idx_users_city)", size=11, bold=True, color=INK))
    frags.append(text(ix + iw / 2, iy + 45, "cost=0.28..160.00  rows=1200  width=32", size=10, color=INK))
    frags.append(text(ix + iw / 2, iy + 65, "actual time=0.03..0.52  rows=1180  loops=1", size=10, bold=True, color=POS))
    frags.append(text(ix + iw / 2, iy + 83, "Index Cond: (city = 'Kyiv')", size=9, color=MUTED))

    frags.append(line(rx + 80, ry + rh, lx + lw / 2, ly, color=LINE, sw=1.5))
    frags.append(line(rx + rw - 80, ry + rh, hx + hw / 2, hy, color=LINE, sw=1.5))
    frags.append(line(hx + hw / 2, hy + hh, ix + iw / 2, iy, color=LINE, sw=1.5))

    frags.append(arrow(lx + 30, ly - 40, lx + 30, ly - 5, color=NEG, sw=1.8))
    frags.append(text(lx - 20, ly - 20, "1. next()", size=10, bold=True, color=NEG))

    frags.append(arrow(hx + 30, hy - 35, hx + 30, hy - 5, color=NEG, sw=1.8))
    frags.append(text(hx - 20, hy - 20, "2. next()", size=10, bold=True, color=NEG))

    frags.append(arrow(lx + lw - 30, ly - 5, lx + lw - 30, ly - 45, color=FIELD, sw=1.8))
    frags.append(text(lx + lw + 25, ly - 22, "кортежі", size=10, bold=True, color=FIELD))

    frags.append(arrow(hx + hw - 30, hy - 5, hx + hw - 30, hy - 40, color=FIELD, sw=1.8))
    frags.append(text(hx + hw + 25, hy - 20, "кортежі", size=10, bold=True, color=FIELD))

    leg_x, leg_y, leg_w, leg_h = 50, 370, 360, 110
    frags.append(rect(leg_x, leg_y, leg_w, leg_h, rx=6, fill="#fdfaf3", stroke="#d97706", sw=1.2))
    frags.append(text(leg_x + 12, leg_y + 22, "Анатомія рядка EXPLAIN:", size=11, bold=True, color="#d97706", anchor="start"))
    frags.append(text(leg_x + 12, leg_y + 44, "cost=A..B : A = вартість першого рядка, B = повна вартість", size=10, color=INK, anchor="start"))
    frags.append(text(leg_x + 12, leg_y + 64, "rows=N : прогнозована оптимізатором кількість рядків", size=10, color=INK, anchor="start"))
    frags.append(text(leg_x + 12, leg_y + 84, "actual time=A..B : реальний час у мс (перший..останній рядок)", size=10, color=POS, anchor="start"))
    frags.append(text(leg_x + 12, leg_y + 101, "loops=L : кількість ітерацій (дійсний час = time * loops)", size=10, color=POS, anchor="start"))

    return render(os.path.join(OUT, 'explain-tree-flow.svg'), W, H, *frags,
                  title="Структура плану EXPLAIN та двобічний потік виконання Volcano")


def main():
    fig_query_pipeline()
    fig_scan_types()
    fig_join_strategies()
    fig_explain_tree_flow()
    print("Усі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()

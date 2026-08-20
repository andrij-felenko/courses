# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми chess-bitboard.
Всі фігури відповідають палітрі та правилам svgkit/svgcheck.
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def draw_bitboard_mapping():
    """Фігура 1: Відображення 64 клітинок шахівниці (a1..h8) на 64-бітний регістр."""
    w, h = 920, 440
    frags = []

    # Заголовок зверху
    frags.append(text(460, 28, "Ізоморфізм шахівниці 8×8 та 64-бітного машинного регістра uint64_t", size=16, bold=True))

    # Ліва частина: Шахова дошка 8x8
    board_x, board_y = 60, 60
    cell_s = 40

    files_lbl = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    ranks_lbl = ['8', '7', '6', '5', '4', '3', '2', '1']

    # Підписи стовпчиків (файлів) та рядків (рангів)
    for col in range(8):
        frags.append(text(board_x + col * cell_s + cell_s / 2, board_y - 8, files_lbl[col], size=13, bold=True, color=MUTED))
    for row in range(8):
        frags.append(text(board_x - 14, board_y + row * cell_s + cell_s / 2 + 5, ranks_lbl[row], size=13, bold=True, color=MUTED))

    # Клітинки дошки
    for row in range(8):
        for col in range(8):
            sq_idx = (7 - row) * 8 + col
            cx = board_x + col * cell_s
            cy = board_y + row * cell_s
            is_light = (row + col) % 2 == 0
            cell_fill = "#f0f2f5" if is_light else "#d0d7de"

            # Виділимо спеціальні поля (a1 = 0, h8 = 63, d4 = 27, e4 = 28)
            stroke_col = LINE
            sw = 1.0
            if sq_idx == 0:  # a1
                cell_fill = "#eaf0fd"
                stroke_col = NEG
                sw = 2.0
            elif sq_idx == 63:  # h8
                cell_fill = "#fdecea"
                stroke_col = POS
                sw = 2.0
            elif sq_idx in (27, 28):  # d4, e4
                cell_fill = "#e8f8f0"
                stroke_col = FIELD
                sw = 1.5

            frags.append(rect(cx, cy, cell_s, cell_s, fill=cell_fill, stroke=stroke_col, sw=sw, rx=2))
            frags.append(text(cx + cell_s / 2, cy + cell_s / 2 + 4, str(sq_idx), size=11, color=INK))

    # Підпис під дошкою
    frags.append(text(board_x + 4 * cell_s, board_y + 8 * cell_s + 24, "Координата (r, c)  →  Індекс біта = r · 8 + c", size=13, bold=True, color=LINE))

    # Права частина: 64-бітний регістр у пам'яті
    reg_x, reg_y = 450, 75
    reg_w, reg_h = 430, 48

    frags.append(textbox(reg_x + reg_w / 2, reg_y - 20, "64-бітний регістр загального призначення (uint64_t)", size=14, bold=True)[0])

    # Малюємо смужку регістра
    frags.append(rect(reg_x, reg_y, reg_w, reg_h, fill=FILL, stroke=LINE, sw=1.8, rx=6))

    # Секції регістра: біт 63 (MSB), ..., біт 28-27, ..., біт 0 (LSB)
    seg_w = 52
    # MSB (h8 - біт 63)
    frags.append(rect(reg_x + 4, reg_y + 4, seg_w, reg_h - 8, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    frags.append(text(reg_x + 4 + seg_w / 2, reg_y + 28, "біт 63", size=12, bold=True, color=POS))
    frags.append(text(reg_x + 4 + seg_w / 2, reg_y + reg_h + 16, "h8 (MSB)", size=11, color=POS, bold=True))

    # Біти 62..29 (крапки)
    frags.append(text(reg_x + 95, reg_y + 28, "• • •", size=14, color=MUTED))

    # Біти 28..27 (e4, d4)
    frags.append(rect(reg_x + 140, reg_y + 4, 75, reg_h - 8, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(reg_x + 177, reg_y + 28, "біти 28..27", size=11, bold=True, color=FIELD))
    frags.append(text(reg_x + 177, reg_y + reg_h + 16, "e4, d4", size=11, color=FIELD, bold=True))

    # Біти 26..1 (крапки)
    frags.append(text(reg_x + 270, reg_y + 28, "• • •", size=14, color=MUTED))

    # LSB (a1 - біт 0)
    frags.append(rect(reg_x + reg_w - seg_w - 4, reg_y + 4, seg_w, reg_h - 8, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(reg_x + reg_w - 4 - seg_w / 2, reg_y + 28, "біт 0", size=12, bold=True, color=NEG))
    frags.append(text(reg_x + reg_w - 4 - seg_w / 2, reg_y + reg_h + 16, "a1 (LSB)", size=11, color=NEG, bold=True))

    # Пояснювальні блоки в правій колонці
    info_y = 190
    tb1, _, _ = textbox(reg_x + reg_w / 2, info_y + 25,
                        "Встановлення поля sq:  mask |= (1ULL << sq)\n"
                        "Перевірка поля sq:    (mask >> sq) & 1ULL\n"
                        "Очищення поля sq:      mask &= ~(1ULL << sq)",
                        size=12, pad=10, fill="#ffffff", stroke=MUTED, rx=6)
    frags.append(tb1)

    tb2, _, _ = textbox(reg_x + reg_w / 2, info_y + 115,
                        "Повний стан 64 клітинок займає рівно 8 байтів!\n"
                        "Перетин множин (attack & pieces) виконується за 1 такт АЛП\n"
                        "без звернень до оперативної пам'яті та без циклів.",
                        size=12, pad=10, fill="#f8fafc", stroke=FIELD, rx=6)
    frags.append(tb2)

    # Стрілки зв'язку
    frags.append(arrow(board_x + 7.5 * cell_s, board_y + 0.5 * cell_s, reg_x + 28, reg_y + 4, color=POS, sw=1.5))
    frags.append(arrow(board_x + 0.5 * cell_s, board_y + 7.5 * cell_s, reg_x + reg_w - 28, reg_y + 4, color=NEG, sw=1.5))

    render(os.path.join(IMG_DIR, "bitboard-mapping.svg"), w, h, *frags)


def draw_sliding_ray_occlusion():
    """Фігура 2: Поширення променів атаки лінійної фігури (тура на d4) та зупинка на блокерах."""
    w, h = 920, 460
    frags = []

    frags.append(text(460, 26, "Генерація променів ковзної фігури (Тура на d4) та блокування перешкодами", size=16, bold=True))

    # Шахова дошка з променями
    board_x, board_y = 60, 60
    cell_s = 42

    files_lbl = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    ranks_lbl = ['8', '7', '6', '5', '4', '3', '2', '1']

    for col in range(8):
        frags.append(text(board_x + col * cell_s + cell_s / 2, board_y - 8, files_lbl[col], size=13, bold=True, color=MUTED))
    for row in range(8):
        frags.append(text(board_x - 14, board_y + row * cell_s + cell_s / 2 + 5, ranks_lbl[row], size=13, bold=True, color=MUTED))

    # Малюємо клітинки
    for row in range(8):
        for col in range(8):
            cx = board_x + col * cell_s
            cy = board_y + row * cell_s
            is_light = (row + col) % 2 == 0
            cell_fill = "#f7f9fa" if is_light else "#e4e8ec"
            stroke_col = LINE
            sw = 1.0
            label = ""
            lbl_color = INK
            lbl_size = 14
            bold = False

            # Тура на d4 (col=3, row=4)
            if row == 4 and col == 3:
                cell_fill = "#eaf0fd"
                stroke_col = NEG
                sw = 2.5
                label = "♜ R"
                lbl_color = NEG
                bold = True
            # Промінь на північ: d5, d6 (вільні), d7 (ворожий кінь - удар), d8 (закритий)
            elif col == 3 and row in (2, 3):  # d6, d5
                cell_fill = "#e8f8f0"
                stroke_col = FIELD
                label = "•"
                lbl_color = FIELD
                lbl_size = 20
            elif col == 3 and row == 1:  # d7 (ворог)
                cell_fill = "#fdecea"
                stroke_col = POS
                sw = 2.0
                label = "♞ N"
                lbl_color = POS
                bold = True
            elif col == 3 and row == 0:  # d8 (тінь за блокером)
                cell_fill = "#e2e2e2"
                label = "закрите"
                lbl_size = 9
                lbl_color = MUTED

            # Промінь на південь: d3 (вільне), d2 (свій пішак - блокада), d1 (закрите)
            elif col == 3 and row == 5:  # d3
                cell_fill = "#e8f8f0"
                stroke_col = FIELD
                label = "•"
                lbl_color = FIELD
                lbl_size = 20
            elif col == 3 and row == 6:  # d2 (свій пішак)
                cell_fill = "#fff3cd"
                stroke_col = "#d97706"
                sw = 2.0
                label = "♙ P"
                lbl_color = "#d97706"
                bold = True
            elif col == 3 and row == 7:  # d1 (тінь)
                cell_fill = "#e2e2e2"
                label = "закрите"
                lbl_size = 9
                lbl_color = MUTED

            # Промінь на схід: e4, f4 (вільні), g4 (ворожа тура - удар), h4 (закрите)
            elif row == 4 and col in (4, 5):  # e4, f4
                cell_fill = "#e8f8f0"
                stroke_col = FIELD
                label = "•"
                lbl_color = FIELD
                lbl_size = 20
            elif row == 4 and col == 6:  # g4 (ворог)
                cell_fill = "#fdecea"
                stroke_col = POS
                sw = 2.0
                label = "♜ r"
                lbl_color = POS
                bold = True
            elif row == 4 and col == 7:  # h4 (тінь)
                cell_fill = "#e2e2e2"
                label = "закрите"
                lbl_size = 9
                lbl_color = MUTED

            # Промінь на захід: a4, b4, c4 (вільні до краю)
            elif row == 4 and col in (0, 1, 2):
                cell_fill = "#e8f8f0"
                stroke_col = FIELD
                label = "•"
                lbl_color = FIELD
                lbl_size = 20

            frags.append(rect(cx, cy, cell_s, cell_s, fill=cell_fill, stroke=stroke_col, sw=sw, rx=3))
            if label:
                frags.append(text(cx + cell_s / 2, cy + cell_s / 2 + 5, label, size=lbl_size, color=lbl_color, bold=bold))

    # Права панель: Алгоритм та маски
    right_x = 440
    tb_algo, _, _ = textbox(right_x + 225, 95,
                            "Математика променів та блокування:\n"
                            "1. Маска зайнятості (Occupancy) містить усі фігури на дошці.\n"
                            "2. Промінь ковзної фігури поширюється вздовж напрямку (N, S, E, W)\n"
                            "   до першого встановленого біта-перешкоди (Blocker).\n"
                            "3. Перший блокер включається в маску атаки (можливе взяття).\n"
                            "4. Усі поля за блокером відсікаються (Ray Shadow).",
                            size=12, pad=10, fill=FILL, stroke=LINE, rx=6)
    frags.append(tb_algo)

    # Легенда кольорів
    leg_y = 210
    frags.append(rect(right_x + 10, leg_y, 22, 22, fill="#eaf0fd", stroke=NEG, sw=2, rx=3))
    frags.append(text(right_x + 40, leg_y + 16, "Ковзна фігура (джерело променів d4)", size=12, anchor="start", bold=True))

    frags.append(rect(right_x + 10, leg_y + 35, 22, 22, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(right_x + 40, leg_y + 51, "Доступні поля переміщення (вільні клітинки)", size=12, anchor="start"))

    frags.append(rect(right_x + 10, leg_y + 70, 22, 22, fill="#fdecea", stroke=POS, sw=2, rx=3))
    frags.append(text(right_x + 40, leg_y + 86, "Ворожа фігура-блокер (дозволене взяття)", size=12, anchor="start", bold=True))

    frags.append(rect(right_x + 10, leg_y + 105, 22, 22, fill="#fff3cd", stroke="#d97706", sw=2, rx=3))
    frags.append(text(right_x + 40, leg_y + 121, "Власна фігура (блокер ходу, захищене поле)", size=12, anchor="start"))

    frags.append(rect(right_x + 10, leg_y + 140, 22, 22, fill="#e2e2e2", stroke=MUTED, sw=1, rx=3))
    frags.append(text(right_x + 40, leg_y + 156, "Тінь за перешкодою (недосяжні поля)", size=12, anchor="start"))

    tb_final, _, _ = textbox(right_x + 225, leg_y + 205,
                             "Фінальна фільтрація:  LegalMoves = Attacks & ~FriendlyPieces",
                             size=13, pad=8, fill="#ffffff", stroke=FIELD, rx=6, bold=True, color=FIELD)
    frags.append(tb_final)

    render(os.path.join(IMG_DIR, "sliding-ray-occlusion.svg"), w, h, *frags)


def draw_magic_hashing_pipeline():
    """Фігура 3: Конвеєр хешування Magic Bitboards."""
    w, h = 980, 440
    frags = []

    frags.append(text(490, 26, "Конвеєр генерації атак через Magic Bitboards (Ідеальне хешування за O(1))", size=16, bold=True))

    # Схема конвеєра: 5 блоків у ланцюжку
    bx = 30
    by = 65
    bw = 150
    bh = 72

    # Блок 1: Вхідна зайнятість
    frags.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(bx + bw / 2, by + 28, "1. Повна зайнятість", size=12, bold=True))
    frags.append(text(bx + bw / 2, by + 48, "Occupancy (64 біти)", size=11, color=MUTED))

    # Оператор AND
    frags.append(arrow(bx + bw, by + bh / 2, bx + bw + 42, by + bh / 2, color=LINE, sw=1.5))
    frags.append(text(bx + bw + 21, by + bh / 2 - 12, "&", size=16, bold=True, color=NEG))

    # Блок 2: Маска променів
    bx2 = bx + bw + 42
    frags.append(rect(bx2, by, bw, bh, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(bx2 + bw / 2, by + 24, "2. Маска променів", size=12, bold=True, color=NEG))
    frags.append(text(bx2 + bw / 2, by + 42, "Relevant Mask (k біт)", size=11, color=NEG))
    frags.append(text(bx2 + bw / 2, by + 58, "Blockers = Occ & Mask", size=10, color=MUTED))

    # Оператор Множення
    frags.append(arrow(bx2 + bw, by + bh / 2, bx2 + bw + 42, by + bh / 2, color=LINE, sw=1.5))
    frags.append(text(bx2 + bw + 21, by + bh / 2 - 12, "×", size=18, bold=True, color=POS))

    # Блок 3: Magic Constant
    bx3 = bx2 + bw + 42
    frags.append(rect(bx3, by, bw, bh, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(bx3 + bw / 2, by + 24, "3. Магічне число", size=12, bold=True, color=POS))
    frags.append(text(bx3 + bw / 2, by + 42, "Magic 64-bit const", size=11, color=POS))
    frags.append(text(bx3 + bw / 2, by + 58, "Розносить біти в MSB", size=10, color=MUTED))

    # Оператор Зсуву
    frags.append(arrow(bx3 + bw, by + bh / 2, bx3 + bw + 42, by + bh / 2, color=LINE, sw=1.5))
    frags.append(text(bx3 + bw + 21, by + bh / 2 - 12, ">>", size=15, bold=True, color=FIELD))

    # Блок 4: Індекс
    bx4 = bx3 + bw + 42
    frags.append(rect(bx4, by, bw, bh, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(bx4 + bw / 2, by + 24, "4. Зсув (64 - b)", size=12, bold=True, color=FIELD))
    frags.append(text(bx4 + bw / 2, by + 42, "Індекс у таблиці", size=11, bold=True, color=FIELD))
    frags.append(text(bx4 + bw / 2, by + 58, "Діапазон 0 .. 2ᵇ - 1", size=10, color=MUTED))

    # Стрілка до виходу
    frags.append(arrow(bx4 + bw, by + bh / 2, bx4 + bw + 42, by + bh / 2, color=LINE, sw=1.5))

    # Блок 5: Атака
    bx5 = bx4 + bw + 42
    frags.append(rect(bx5, by, bw, bh, fill="#ffffff", stroke=LINE, sw=2, rx=6))
    frags.append(text(bx5 + bw / 2, by + 28, "5. Готова маска", size=12, bold=True))
    frags.append(text(bx5 + bw / 2, by + 48, "AttackTable[idx]", size=11, color=FIELD, bold=True))

    # Нижня частина: два чітко розведені інформаційні блоки
    mid_y = 175
    card_w = 440
    card_h = 230

    # Ліва картка: Математична суть
    frags.append(rect(30, mid_y, card_w, card_h, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(30 + card_w / 2, mid_y + 25, "Математична суть хешування:", size=13, bold=True, color=INK))
    frags.append(text(45, mid_y + 55, "• Для клітинки є k релевантних бітів-блокерів (k ≤ 12)", size=12, anchor="start"))
    frags.append(text(45, mid_y + 82, "• Кількість конфігурацій перешкод дорівнює 2ᵏ (64..4096)", size=12, anchor="start"))
    frags.append(text(45, mid_y + 110, "• 64-бітне множення розносить активні біти k у верхні b розрядів", size=12, anchor="start"))
    frags.append(text(45, mid_y + 138, "• Зсув >> (64 - b) виділяє b старших бітів як ідеальний хеш", size=12, anchor="start"))
    frags.append(text(45, mid_y + 165, "• Без колізій: кожна конфігурація перешкод має свій індекс!", size=12, anchor="start", bold=True, color=FIELD))
    frags.append(text(45, mid_y + 195, "Часова складність: O(1) за 3 операції АЛП (AND, MUL, SHR)", size=11, anchor="start", italic=True, color=MUTED))

    # Права картка: Апаратний PEXT
    frags.append(rect(510, mid_y, card_w, card_h, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(510 + card_w / 2, mid_y + 25, "Апаратний еквівалент: BMI2 PEXT (x86 Haswell+)", size=13, bold=True, color=NEG))
    frags.append(text(525, mid_y + 55, "Інструкція _pext_u64 витягує всі біти за маскою за 1 такт:", size=12, anchor="start"))
    frags.append(text(525, mid_y + 85, "uint64_t idx = _pext_u64(occ, mask);", size=12, anchor="start", bold=True, color=LINE))
    frags.append(text(525, mid_y + 110, "uint64_t att = attack_table[base_offset + idx];", size=12, anchor="start", bold=True, color=FIELD))
    frags.append(text(525, mid_y + 145, "• Усуває потребу пошуку магічних констант під час розробки", size=12, anchor="start"))
    frags.append(text(525, mid_y + 172, "• Розмір таблиці атак скорочується до мінімально можливого", size=12, anchor="start"))
    frags.append(text(525, mid_y + 198, "• Латентність виклику: рівно 1 машинний такт без зсувів!", size=11, anchor="start", bold=True, color=NEG))

    render(os.path.join(IMG_DIR, "magic-hashing-pipeline.svg"), w, h, *frags)


def draw_scheduler_priority_bitmap():
    """Фігура 4: O(1) бітова черга та диспетчер пріоритетів в операційній системі."""
    w, h = 920, 460
    frags = []

    frags.append(text(460, 26, "Архітектура O(1) планувальника ОС на основі пріоритетної бітової черги", size=16, bold=True))

    # Ліва колонка: 64-бітний бітмап активних пріоритетів
    map_x = 50
    map_y = 65
    map_w = 260
    map_h = 320

    frags.append(rect(map_x, map_y, map_w, map_h, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(map_x + map_w / 2, map_y + 24, "64-бітна бітова маска черг", size=13, bold=True))
    frags.append(text(map_x + map_w / 2, map_y + 42, "uint64_t active_prio_mask", size=11, color=MUTED))

    # Рядки пріоритетів (від 0 до 7 для наочності)
    prio_items = [
        ("Пріоритет 0 (Real-Time)", 1, POS, "Активна задача"),
        ("Пріоритет 1 (Audio Driver)", 0, MUTED, "Черга порожня"),
        ("Пріоритет 2 (Network RX)", 1, FIELD, "Активна задача"),
        ("Пріоритет 3 (Graphics Server)", 0, MUTED, "Черга порожня"),
        ("Пріоритет 4 (Database Worker)", 1, FIELD, "Активна задача"),
        ("Пріоритети 5..62", 0, MUTED, "Черги порожні"),
        ("Пріоритет 63 (Idle Loop)", 1, NEG, "Фоновий потік"),
    ]

    row_y = map_y + 60
    for idx, (name, bit_val, color, desc) in enumerate(prio_items):
        ry = row_y + idx * 35
        # Квадратик біта
        frags.append(rect(map_x + 15, ry, 26, 24, fill="#ffffff" if bit_val == 0 else ("#fdecea" if idx == 0 else "#e8f8f0"), stroke=color, sw=1.5, rx=3))
        frags.append(text(map_x + 28, ry + 16, str(bit_val), size=12, bold=True, color=color))

        # Назва
        frags.append(text(map_x + 50, ry + 16, name, size=11, anchor="start", color=INK if bit_val == 1 else MUTED, bold=(bit_val == 1)))

    # Центральний блок: Апаратний CTZ / TZCNT
    ctz_cx = 425
    ctz_cy = 185
    tb_ctz, ctz_w, ctz_h = textbox(ctz_cx, ctz_cy,
                                  "Апаратний CTZ\n"
                                  "__builtin_ctzll()\n"
                                  "1 машинний такт O(1)\n"
                                  "Індекс = 0 (MSB=0)",
                                  size=12, pad=10, fill="#fdecea", stroke=POS, sw=2, rx=6, bold=True, color=POS)
    frags.append(tb_ctz)

    # Стрілка від бітмапу до CTZ
    frags.append(arrow(map_x + map_w, map_y + 72, ctz_cx - ctz_w / 2, ctz_cy - 20, color=POS, sw=2))

    # Права колонка: Масив списків задач
    arr_x = 560
    arr_y = 65
    arr_w = 310
    arr_h = 320

    frags.append(rect(arr_x, arr_y, arr_w, arr_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(arr_x + arr_w / 2, arr_y + 24, "Масив голів черг задач Runqueue", size=13, bold=True))
    frags.append(text(arr_x + arr_w / 2, arr_y + 42, "struct TaskList runqueues[64]", size=11, color=MUTED))

    # Черги
    q_items = [
        (0, "Task #104 [Audio RT] -> Task #105", POS, True),
        (1, "NULL (список порожній)", MUTED, False),
        (2, "Task #88 [Network Worker]", FIELD, False),
        (3, "NULL (список порожній)", MUTED, False),
        (4, "Task #12 [DB Query]", FIELD, False),
        ("5..62", "NULL ...", MUTED, False),
        (63, "Task #0 [Kernel Idle]", NEG, False),
    ]

    for idx, (p_num, task_str, color, is_selected) in enumerate(q_items):
        ry = row_y + idx * 35
        fill_col = "#fdecea" if is_selected else ("#f8fafc" if color != MUTED else "#ffffff")
        stroke_col = color if is_selected else (LINE if color != MUTED else "#d0d7de")
        frags.append(rect(arr_x + 10, ry, arr_w - 20, 24, fill=fill_col, stroke=stroke_col, sw=1.5 if is_selected else 1.0, rx=4))
        frags.append(text(arr_x + 20, ry + 16, f"[{p_num}] {task_str}", size=11, anchor="start", color=color, bold=is_selected))

    # Стрілка від CTZ до вибраної черги [0]
    frags.append(arrow(ctz_cx + ctz_w / 2, ctz_cy - 20, arr_x + 10, row_y + 12, color=POS, sw=2))

    # Пояснення знизу
    tb_bottom, _, _ = textbox(460, 420,
                              "Диспетчеризація за 1 такт: вибір найвищого пріоритету не залежить від кількості потоків у системі!\n"
                              "Порожні черги (біт=0) миттєво пропускаються апаратним пріоритетним шифратором без перевірок if.",
                              size=12, pad=8, fill="#f8fafc", stroke=FIELD, rx=6)
    frags.append(tb_bottom)

    render(os.path.join(IMG_DIR, "scheduler-priority-bitmap.svg"), w, h, *frags)


if __name__ == "__main__":
    print("Генерація SVG-фігур для теми chess-bitboard...")
    draw_bitboard_mapping()
    draw_sliding_ray_occlusion()
    draw_magic_hashing_pipeline()
    draw_scheduler_priority_bitmap()
    print("Фігури успішно згенеровано у теці img/.")

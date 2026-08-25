# -*- coding: utf-8 -*-
import sys, os
# 4 levels up to reach scripts/ in repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Colors
FREE_FILL   = "#eef7ee"    # Light green for free blocks
FREE_STROKE = "#27ae60"    # Dark green stroke
ALLOC_FILL  = "#fdecea"    # Light red for allocated blocks
ALLOC_STROKE= "#c0392b"    # Dark red stroke
SPLIT_FILL  = "#eaf0fd"    # Light blue for split parent blocks
SPLIT_STROKE= "#2457d6"    # Dark blue stroke
BG_BAR      = "#f4f6f8"

# ── 1. buddy-tree-split: Рекурсивне розщеплення від 64K до 8K ──────────────
def fig_tree_split():
    W, H = 880, 480
    p = []
    
    # Title & Headers
    p.append(text(W / 2, 28, "Рекурсивний поділ блоку 64 КБ для запиту 7 КБ (порядок 3 = 8 КБ)", size=15, bold=True))
    
    # Level descriptions on the left
    levels = [
        ("Порядок 6 (64 КБ)", 75),
        ("Порядок 5 (32 КБ)", 165),
        ("Порядок 4 (16 КБ)", 255),
        ("Порядок 3 (8 КБ)",  355),
    ]
    for lbl, y in levels:
        p.append(text(85, y + 16, lbl, size=11, color=MUTED, anchor="start", bold=True))
        p.append(line(40, y + 36, 210, y + 36, color="#e2e8f0", sw=1))

    # Order 6: Root 64 KB (offset 0..64)
    # x ranges from 240 to 820 -> width 580
    x_root, w_root = 240, 580
    p.append(rect(x_root, 60, w_root, 36, fill=SPLIT_FILL, stroke=SPLIT_STROKE, sw=1.5, rx=4))
    p.append(text(x_root + w_root / 2, 82, "Блок 64 КБ [0x0000..0xFFFF] — розщеплюється", size=12, color=SPLIT_STROKE, bold=True))
    
    # Arrows from Order 6 to Order 5
    p.append(arrow(x_root + w_root / 4, 98, x_root + w_root / 4, 148, color=LINE, sw=1.5))
    p.append(arrow(x_root + 3 * w_root / 4, 98, x_root + 3 * w_root / 4, 148, color=LINE, sw=1.5))
    
    # Order 5: Left 32 KB (split), Right 32 KB (free -> free_list[5])
    w5 = (w_root - 16) / 2
    x5_0 = x_root
    x5_1 = x_root + w5 + 16
    
    p.append(rect(x5_0, 150, w5, 36, fill=SPLIT_FILL, stroke=SPLIT_STROKE, sw=1.5, rx=4))
    p.append(text(x5_0 + w5 / 2, 172, "Лівий 32 КБ [0x0000] (розщеплюється)", size=11, color=SPLIT_STROKE, bold=True))
    
    p.append(rect(x5_1, 150, w5, 36, fill=FREE_FILL, stroke=FREE_STROKE, sw=1.5, rx=4))
    p.append(text(x5_1 + w5 / 2, 168, "Правий близнюк 32 КБ [0x8000]", size=11, color=FREE_STROKE, bold=True))
    p.append(text(x5_1 + w5 / 2, 181, "→ вільний, у free_list[5]", size=10, color=MUTED))
    
    # Arrows from Order 5 to Order 4
    p.append(arrow(x5_0 + w5 / 4, 188, x5_0 + w5 / 4, 238, color=LINE, sw=1.5))
    p.append(arrow(x5_0 + 3 * w5 / 4, 188, x5_0 + 3 * w5 / 4, 238, color=LINE, sw=1.5))
    
    # Order 4: Left 16 KB (split), Right 16 KB (free -> free_list[4])
    w4 = (w5 - 12) / 2
    x4_0 = x5_0
    x4_1 = x5_0 + w4 + 12
    
    p.append(rect(x4_0, 240, w4, 36, fill=SPLIT_FILL, stroke=SPLIT_STROKE, sw=1.5, rx=4))
    p.append(text(x4_0 + w4 / 2, 262, "Лівий 16 КБ (розщепл.)", size=10.5, color=SPLIT_STROKE, bold=True))
    
    p.append(rect(x4_1, 240, w4, 36, fill=FREE_FILL, stroke=FREE_STROKE, sw=1.5, rx=4))
    p.append(text(x4_1 + w4 / 2, 258, "Правий 16 КБ [0x4000]", size=10.5, color=FREE_STROKE, bold=True))
    p.append(text(x4_1 + w4 / 2, 271, "→ free_list[4]", size=9.5, color=MUTED))
    
    # Arrows from Order 4 to Order 3
    p.append(arrow(x4_0 + w4 / 4, 278, x4_0 + w4 / 4, 338, color=LINE, sw=1.5))
    p.append(arrow(x4_0 + 3 * w4 / 4, 278, x4_0 + 3 * w4 / 4, 338, color=LINE, sw=1.5))
    
    # Order 3: Left 8 KB (allocated), Right 8 KB (free -> free_list[3])
    w3 = (w4 - 10) / 2
    x3_0 = x4_0
    x3_1 = x4_0 + w3 + 10
    
    p.append(rect(x3_0, 340, w3, 46, fill=ALLOC_FILL, stroke=ALLOC_STROKE, sw=2, rx=4))
    p.append(text(x3_0 + w3 / 2, 360, "8 КБ [0x0000]", size=11, color=ALLOC_STROKE, bold=True))
    p.append(text(x3_0 + w3 / 2, 376, "ВИДІЛЕНО (7 КБ)", size=9.5, color=ALLOC_STROKE))
    
    p.append(rect(x3_1, 340, w3, 46, fill=FREE_FILL, stroke=FREE_STROKE, sw=1.5, rx=4))
    p.append(text(x3_1 + w3 / 2, 360, "8 КБ [0x2000]", size=11, color=FREE_STROKE, bold=True))
    p.append(text(x3_1 + w3 / 2, 376, "→ free_list[3]", size=9.5, color=MUTED))
    
    # Bottom Summary Box
    p.append(rect(40, 412, 800, 52, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(55, 432, "Результат:", size=11, color=INK, anchor="start", bold=True))
    p.append(text(130, 432, "Користувач отримав блок 8 КБ за адресою 0x0000 (внутрішня фрагментація = 1 КБ).", size=11, color=INK, anchor="start"))
    p.append(text(55, 451, "Списки вільних:", size=11, color=INK, anchor="start", bold=True))
    p.append(text(160, 451, "free_list[3] поповнився блоком [0x2000]; free_list[4] — блоком [0x4000]; free_list[5] — блоком [0x8000].", size=11, color=MUTED, anchor="start"))
    
    render(os.path.join(OUT, "buddy-tree-split.svg"), W, H, *p)


# ── 2. buddy-bitwise-xor: Побітова арифметика XOR ───────────────────────────
def fig_bitwise_xor():
    W, H = 880, 420
    p = []
    
    p.append(text(W / 2, 28, "Побітове обчислення адреси близнюка: buddy_addr = addr ⊕ (1 ≪ k)", size=15, bold=True))
    
    # Block A: Left Buddy (0x2000, Order 3 -> Size 8 KB = 0x2000)
    # Box 1: Left Buddy Address
    bx1, by1, bw, bh = 50, 70, 360, 140
    p.append(rect(bx1, by1, bw, bh, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(bx1 + 20, by1 + 26, "Лівий близнюк (A): Порядок k = 3 (8 КБ)", size=12, color=INK, anchor="start", bold=True))
    p.append(text(bx1 + 20, by1 + 52, "Шістнадцяткова адреса:", size=11, color=MUTED, anchor="start"))
    p.append(text(bx1 + 180, by1 + 52, "0x2000 (8192)", size=11, color=INK, anchor="start", bold=True))
    p.append(text(bx1 + 20, by1 + 76, "Двійковий вигляд:", size=11, color=MUTED, anchor="start"))
    p.append(text(bx1 + 140, by1 + 76, "0010 0000 0000 0000", size=12, color=NEG, anchor="start", bold=True))
    p.append(text(bx1 + 20, by1 + 102, "Біт k = 13:", size=11, color=MUTED, anchor="start"))
    p.append(text(bx1 + 100, by1 + 102, "0 (ознака лівого близнюка)", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(bx1 + 20, by1 + 124, "Вирівнювання:", size=10, color=MUTED, anchor="start"))
    p.append(text(bx1 + 115, by1 + 124, "addr & (2³ − 1) == 0 (кратна 8192)", size=10, color=INK, anchor="start"))

    # Box 2: XOR Operation
    cx, cy = 440, 140
    p.append(circle(cx, cy, 22, fill="#eaf0fd", stroke=SPLIT_STROKE, sw=2))
    p.append(text(cx, cy + 6, "⊕", size=22, color=SPLIT_STROKE, bold=True))
    p.append(text(cx, cy + 36, "XOR 2¹³", size=10.5, color=MUTED))

    # Box 3: Right Buddy Address
    bx2, by2 = 470, 70
    p.append(rect(bx2, by2, bw, bh, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(bx2 + 20, by2 + 26, "Правий близнюк (B): Порядок k = 3 (8 КБ)", size=12, color=INK, anchor="start", bold=True))
    p.append(text(bx2 + 20, by2 + 52, "Шістнадцяткова адреса:", size=11, color=MUTED, anchor="start"))
    p.append(text(bx2 + 180, by2 + 52, "0x0000 (0)", size=11, color=INK, anchor="start", bold=True))
    p.append(text(bx2 + 20, by2 + 76, "Двійковий вигляд:", size=11, color=MUTED, anchor="start"))
    p.append(text(bx2 + 140, by2 + 76, "0000 0000 0000 0000", size=12, color=POS, anchor="start", bold=True))
    p.append(text(bx2 + 20, by2 + 102, "Біт k = 13:", size=11, color=MUTED, anchor="start"))
    p.append(text(bx2 + 100, by2 + 102, "1 ↔ 0 (перемикається XOR-ом)", size=11, color=SPLIT_STROKE, anchor="start", bold=True))
    p.append(text(bx2 + 20, by2 + 124, "Вирівнювання:", size=10, color=MUTED, anchor="start"))
    p.append(text(bx2 + 115, by2 + 124, "addr & (2³ − 1) == 0 (кратна 8192)", size=10, color=INK, anchor="start"))

    # Bottom Panel: Parent Block Masking
    p.append(rect(50, 235, 780, 160, fill="#f4f6f8", stroke="#94a3b8", sw=1.4, rx=6))
    p.append(text(75, 260, "Спільний батьківський блок при злитті (Порядок k + 1 = 4, 16 КБ):", size=12, color=INK, anchor="start", bold=True))
    
    p.append(text(75, 288, "Батьківська адреса:", size=11, color=MUTED, anchor="start"))
    p.append(text(215, 288, "parent = addr & ~(1 ≪ k) = min(A, B) = 0x0000", size=12, color=INK, anchor="start", bold=True))
    
    # Table of bit differences
    p.append(text(75, 318, "Маска порядку k = 3:", size=11, color=MUTED, anchor="start"))
    p.append(text(215, 318, "1 ≪ 13 = 0x2000 = 0010 0000 0000 0000", size=11, color=SPLIT_STROKE, anchor="start"))
    
    p.append(text(75, 342, "Інверсна маска ~(1 ≪ 13):", size=11, color=MUTED, anchor="start"))
    p.append(text(215, 342, "1101 1111 1111 1111 (обнуляє 13-й біт для обох близнюків)", size=11, color=FIELD, anchor="start"))
    
    p.append(text(75, 372, "Властивість інволюції:", size=11, color=MUTED, anchor="start", bold=True))
    p.append(text(230, 372, "(addr ⊕ 2ᵏ) ⊕ 2ᵏ = addr  (двічі застосований XOR повертає вихідну адресу)", size=11, color=INK, anchor="start"))
    
    render(os.path.join(OUT, "buddy-bitwise-xor.svg"), W, H, *p)


# ── 3. buddy-coalescing: Каскадне злиття близнюків ──────────────────────────
def fig_coalescing():
    W, H = 880, 460
    p = []
    
    p.append(text(W / 2, 28, "Каскадне злиття (Coalescing) блоку 8 КБ [0x0000] до 32 КБ [0x0000]", size=15, bold=True))
    
    # Step 1: Freeing 8 KB at 0x0000
    y_s1 = 65
    p.append(textbox(130, y_s1 + 22, "Крок 1: Звільнення 8 КБ\naddr = 0x0000, k = 3", size=11, pad=8, fill="#ffffff", stroke=ALLOC_STROKE, bold=True)[0])
    
    # Draw order 3 state
    p.append(rect(270, y_s1, 120, 44, fill=FREE_FILL, stroke=FREE_STROKE, sw=2, rx=4))
    p.append(text(330, y_s1 + 22, "0x0000 (8 КБ)", size=11, color=FREE_STROKE, bold=True))
    p.append(text(330, y_s1 + 36, "щойно звільнено", size=9, color=MUTED))
    
    p.append(text(410, y_s1 + 22, "⊕", size=16, color=MUTED, bold=True))
    
    p.append(rect(430, y_s1, 120, 44, fill=FREE_FILL, stroke=FREE_STROKE, sw=1.5, rx=4))
    p.append(text(490, y_s1 + 22, "0x2000 (8 КБ)", size=11, color=FREE_STROKE, bold=True))
    p.append(text(490, y_s1 + 36, "вільний у free_list[3]", size=9, color=MUTED))
    
    p.append(arrow(565, y_s1 + 22, 605, y_s1 + 22, color=FIELD, sw=2))
    p.append(text(620, y_s1 + 22, "Близнюк вільний! Видаляємо з free_list[3]", size=11, color=FIELD, anchor="start", bold=True))
    
    # Arrow to Step 2
    p.append(arrow(330, y_s1 + 48, 330, y_s1 + 88, color=LINE, sw=1.5))
    p.append(arrow(490, y_s1 + 48, 410, y_s1 + 88, color=LINE, sw=1.5))
    
    # Step 2: Merge into 16 KB at 0x0000
    y_s2 = 165
    p.append(textbox(130, y_s2 + 22, "Крок 2: Злиття в 16 КБ\naddr = 0x0000, k = 4", size=11, pad=8, fill="#ffffff", stroke=SPLIT_STROKE, bold=True)[0])
    
    p.append(rect(270, y_s2, 250, 44, fill=FREE_FILL, stroke=FREE_STROKE, sw=2, rx=4))
    p.append(text(395, y_s2 + 22, "Злитий блок 16 КБ [0x0000]", size=11, color=FREE_STROKE, bold=True))
    p.append(text(395, y_s2 + 36, "новий близнюк: 0x0000 ⊕ 16К = 0x4000", size=9.5, color=MUTED))
    
    p.append(text(535, y_s2 + 22, "⊕", size=16, color=MUTED, bold=True))
    
    p.append(rect(555, y_s2, 120, 44, fill=FREE_FILL, stroke=FREE_STROKE, sw=1.5, rx=4))
    p.append(text(615, y_s2 + 22, "0x4000 (16 КБ)", size=11, color=FREE_STROKE, bold=True))
    p.append(text(615, y_s2 + 36, "вільний у free_list[4]", size=9, color=MUTED))
    
    p.append(arrow(685, y_s2 + 22, 725, y_s2 + 22, color=FIELD, sw=2))
    p.append(text(740, y_s2 + 22, "Близнюк вільний!", size=11, color=FIELD, anchor="start", bold=True))
    
    # Arrow to Step 3
    p.append(arrow(395, y_s2 + 48, 395, y_s2 + 88, color=LINE, sw=1.5))
    p.append(arrow(615, y_s2 + 48, 510, y_s2 + 88, color=LINE, sw=1.5))
    
    # Step 3: Merge into 32 KB at 0x0000, next buddy 0x8000 is ALLOCATED
    y_s3 = 265
    p.append(textbox(130, y_s3 + 22, "Крок 3: Злиття в 32 КБ\naddr = 0x0000, k = 5", size=11, pad=8, fill="#ffffff", stroke=SPLIT_STROKE, bold=True)[0])
    
    p.append(rect(270, y_s3, 375, 44, fill=FREE_FILL, stroke=FREE_STROKE, sw=2, rx=4))
    p.append(text(457, y_s3 + 22, "Злитий блок 32 КБ [0x0000]", size=11, color=FREE_STROKE, bold=True))
    p.append(text(457, y_s3 + 36, "новий близнюк: 0x0000 ⊕ 32К = 0x8000", size=9.5, color=MUTED))
    
    p.append(text(660, y_s3 + 22, "⊕", size=16, color=MUTED, bold=True))
    
    p.append(rect(680, y_s3, 120, 44, fill=ALLOC_FILL, stroke=ALLOC_STROKE, sw=2, rx=4))
    p.append(text(740, y_s3 + 22, "0x8000 (32 КБ)", size=11, color=ALLOC_STROKE, bold=True))
    p.append(text(740, y_s3 + 36, "ЗАЙНЯТИЙ (Alloc)", size=9, color=ALLOC_STROKE))
    
    # Bottom stop result
    p.append(rect(50, 345, 780, 95, fill="#f8fafc", stroke="#94a3b8", sw=1.4, rx=6))
    p.append(text(75, 370, "Зупинка каскаду злиття:", size=12, color=POS, anchor="start", bold=True))
    p.append(text(250, 370, "Близнюк 0x8000 зайнятий → подальше злиття неможливе.", size=12, color=INK, anchor="start"))
    p.append(text(75, 395, "Фінальна дія:", size=11, color=INK, anchor="start", bold=True))
    p.append(text(175, 395, "Вставляємо отриманий блок 32 КБ [0x0000] у голову списку free_list[5].", size=11, color=FREE_STROKE, anchor="start", bold=True))
    p.append(text(75, 420, "Часова складність:", size=11, color=MUTED, anchor="start", bold=True))
    p.append(text(210, 420, "O(MAX_ORDER − k) кроків, кожен крок — вилучення з двозв'язного списку за O(1).", size=11, color=MUTED, anchor="start"))
    
    render(os.path.join(OUT, "buddy-coalescing.svg"), W, H, *p)


# ── 4. buddy-bitmap-tracking: Бітова карта та дескриптори ────────────────────
def fig_bitmap_tracking():
    W, H = 880, 450
    p = []
    
    p.append(text(W / 2, 28, "Відстеження стану близнюків: Однобітна оптимізація Кнута vs Дескриптори", size=15, bold=True))
    
    # Left Section: 1 bit per buddy pair (Knuth's method)
    bx1, by1, bw, bh = 40, 60, 385, 365
    p.append(rect(bx1, by1, bw, bh, fill="#f8fafc", stroke="#94a3b8", sw=1.4, rx=6))
    p.append(text(bx1 + bw / 2, by1 + 24, "Метод 1: 1 біт на пару близнюків (Кнут)", size=12, color=SPLIT_STROKE, bold=True))
    
    p.append(text(bx1 + 16, by1 + 54, "Принцип інвертування біта пари:", size=11, color=INK, anchor="start", bold=True))
    p.append(text(bx1 + 16, by1 + 74, "• Біт = 0: Обидва близнюки вільні АБО обидва зайняті", size=10.5, color=MUTED, anchor="start"))
    p.append(text(bx1 + 16, by1 + 92, "• Біт = 1: Рівно один близнюк вільний, другий зайнятий", size=10.5, color=MUTED, anchor="start"))
    
    # State transition boxes
    ty = by1 + 115
    p.append(rect(bx1 + 20, ty, 345, 65, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(bx1 + 30, ty + 20, "При виділенні будь-якого з пари:", size=10.5, color=POS, anchor="start", bold=True))
    p.append(text(bx1 + 30, ty + 38, "bitmap[pair_idx] ^= 1", size=11, color=LINE, anchor="start", bold=True))
    p.append(text(bx1 + 30, ty + 54, "Якщо новий стан 0 → обидва стали зайняті", size=9.5, color=MUTED, anchor="start"))
    
    ty2 = ty + 75
    p.append(rect(bx1 + 20, ty2, 345, 75, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(bx1 + 30, ty2 + 20, "При звільненні будь-якого з пари:", size=10.5, color=FREE_STROKE, anchor="start", bold=True))
    p.append(text(bx1 + 30, ty2 + 38, "bitmap[pair_idx] ^= 1", size=11, color=LINE, anchor="start", bold=True))
    p.append(text(bx1 + 30, ty2 + 54, "Якщо новий стан 0 → близнюк вільний (зливаємо!)", size=9.5, color=FREE_STROKE, anchor="start", bold=True))
    p.append(text(bx1 + 30, ty2 + 68, "Якщо новий стан 1 → близнюк зайнятий (стоп)", size=9.5, color=MUTED, anchor="start"))
    
    p.append(text(bx1 + 16, by1 + 345, "Витрата пам'яті: 2^(MAX_ORDER − k − 1) бітів на порядок", size=10, color=FIELD, anchor="start", bold=True))

    # Right Section: Explicit Node Descriptors (Linux struct page style)
    bx2 = 455
    p.append(rect(bx2, by1, bw, bh, fill="#f8fafc", stroke="#94a3b8", sw=1.4, rx=6))
    p.append(text(bx2 + bw / 2, by1 + 24, "Метод 2: Явні дескриптори блоків / сторінок", size=12, color=FIELD, bold=True))
    
    p.append(text(bx2 + 16, by1 + 54, "Масив дескрипторів (напр. struct page):", size=11, color=INK, anchor="start", bold=True))
    
    # Struct diagram
    sy = by1 + 75
    p.append(rect(bx2 + 20, sy, 345, 145, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(bx2 + 30, sy + 22, "struct block_descriptor {", size=11, color=INK, anchor="start", bold=True))
    p.append(text(bx2 + 45, sy + 44, "uint8_t  order;       // поточний порядок блоку", size=10, color=SPLIT_STROKE, anchor="start"))
    p.append(text(bx2 + 45, sy + 64, "uint8_t  is_free;     // 1 = у списку вільних, 0 = зайнятий", size=10, color=FREE_STROKE, anchor="start"))
    p.append(text(bx2 + 45, sy + 84, "node_t*  next;        // покажчик двозв'язного списку", size=10, color=MUTED, anchor="start"))
    p.append(text(bx2 + 45, sy + 104, "node_t*  prev;        // для швидкого видалення O(1)", size=10, color=MUTED, anchor="start"))
    p.append(text(bx2 + 30, sy + 128, "};", size=11, color=INK, anchor="start", bold=True))
    
    # Verification condition
    cy = sy + 160
    p.append(rect(bx2 + 20, cy, 345, 85, fill="#ffffff", stroke=FREE_STROKE, sw=1.2, rx=4))
    p.append(text(bx2 + 30, cy + 20, "Умова безпечного злиття близнюка B:", size=10.5, color=INK, anchor="start", bold=True))
    p.append(text(bx2 + 30, cy + 42, "1. desc[B].is_free == 1", size=10.5, color=FREE_STROKE, anchor="start", bold=True))
    p.append(text(bx2 + 30, cy + 60, "2. desc[B].order == current_order", size=10.5, color=SPLIT_STROKE, anchor="start", bold=True))
    p.append(text(bx2 + 30, cy + 76, "(захист від злиття з підблоком або надблоком)", size=9, color=MUTED, anchor="start"))
    
    p.append(text(bx2 + 16, by1 + 345, "Перевага: захист від пасток неоднозначності без колізій", size=10, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "buddy-bitmap-tracking.svg"), W, H, *p)


if __name__ == "__main__":
    fig_tree_split()
    fig_bitwise_xor()
    fig_coalescing()
    fig_bitmap_tracking()
    print("Figures generated successfully.")

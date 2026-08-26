# -*- coding: utf-8 -*-
"""Фігури до статті «Пам'ять без купи: пули, арени, бюджет».
1) heap-fragmentation-anatomy.svg — анатомія фрагментації купи та зіткнення зі стеком;
2) fixed-pool-intrusive-list.svg — блоковий пул з інваріантом зв'язного списку у вільних блоках;
3) linear-arena-lifecycle.svg — життєвий цикл лінійної арени та дворівневий scratchpad.
Запуск: python figs.py (вивід у ./img/)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Анатомія фрагментації купи та зіткнення зі стеком ─────────────
def fig_heap_fragmentation():
    W, H = 840, 480
    frags = []

    # Тло
    frags.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=4))

    # Заголовок секції А: Зовнішня фрагментація
    frags.append(text(20, 28, "1. Зовнішня фрагментація динамічної купи (Heap Fragmentation)", size=14, color=INK, anchor="start", bold=True))

    # Смуга пам'яті: 64 КБ SRAM
    bar_x, bar_y, bar_w, bar_h = 40, 50, 760, 48
    frags.append(rect(bar_x, bar_y, bar_w, bar_h, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=4))

    # Блоки всередині смуги (Зайняті та Вільні)
    blocks = [
        (40, 110, "#e2e8f0", INK, "Зайнято (Пакет A)\n128 Б", False),
        (150, 60, "#fee2e2", POS, "Вільна дірка\n48 Б", True),
        (210, 90, "#e2e8f0", INK, "Зайнято (Сесія)\n96 Б", False),
        (300, 70, "#fee2e2", POS, "Вільна дірка\n64 Б", True),
        (370, 140, "#e2e8f0", INK, "Зайнято (JSON-буфер)\n160 Б", False),
        (510, 80, "#fee2e2", POS, "Вільна дірка\n80 Б", True),
        (590, 210, "#e2e8f0", INK, "Зайнято (Сертифікат)\n240 Б", False),
    ]

    for bx, bw, bfill, bcol, blabel, is_hole in blocks:
        st_col = POS if is_hole else "#64748b"
        frags.append(rect(bx, bar_y, bw, bar_h, fill=bfill, stroke=st_col, sw=1.2, rx=2))
        lines = blabel.split("\n")
        frags.append(text(bx + bw / 2, bar_y + 18, lines[0], size=10, color=bcol, bold=True))
        frags.append(text(bx + bw / 2, bar_y + 34, lines[1], size=9, color=bcol))

    # Пояснення парадоксу фрагментації
    alert_box, _, _ = textbox(W / 2, 132,
                              "Сумарно вільно: 48 Б + 64 Б + 80 Б = 192 Байти  |  Запит malloc(120) повертає NULL!\n"
                              "Найбільший неперервний блок = 80 Б. Купа вичерпана за наявності вільної пам'яті.",
                              size=11, pad=8, fill="#fef2f2", stroke=POS, sw=1.2, color=POS, bold=True)
    frags.append(alert_box)

    # Розділювач
    frags.append(line(40, 175, 800, 175, color="#e2e8f0", sw=1.5, dash="4,4"))

    # Заголовок секції Б: Зіткнення Стека та Купи в SRAM
    frags.append(text(20, 202, "2. Відсутність апаратного захисту: ризик катастрофічного зіткнення (Stack-Heap Collision)", size=14, color=INK, anchor="start", bold=True))

    # Діаграма пам'яті SRAM мікроконтролера
    map_x, map_y, map_w, map_h = 60, 225, 720, 90
    frags.append(rect(map_x, map_y, map_w, map_h, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))

    # Секції SRAM
    s1_w = 140
    frags.append(rect(map_x, map_y, s1_w, map_h, fill="#e2e8f0", stroke="#475569", sw=1.2, rx=4))
    frags.append(text(map_x + s1_w / 2, map_y + 35, "Глобальні змінні", size=11, bold=True))
    frags.append(text(map_x + s1_w / 2, map_y + 55, "(.data + .bss)", size=10, color=MUTED))

    # Купа
    heap_w = 170
    frags.append(rect(map_x + s1_w, map_y, heap_w, map_h, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(map_x + s1_w + heap_w / 2, map_y + 32, "Динамічна купа (Heap)", size=11, color=POS, bold=True))
    frags.append(text(map_x + s1_w + heap_w / 2, map_y + 50, "Зростає праворуч →", size=10, color=POS))
    frags.append(line(map_x + s1_w + 30, map_y + 68, map_x + s1_w + heap_w - 30, map_y + 68, color=POS, sw=2))

    # Небезпечна зона зіткнення
    danger_x = map_x + s1_w + heap_w
    danger_w = 130
    frags.append(rect(danger_x, map_y, danger_w, map_h, fill="#fef2f2", stroke=POS, sw=2, rx=4))
    frags.append(text(danger_x + danger_w / 2, map_y + 35, "ЗОНА ЗІТКНЕННЯ", size=11, color=POS, bold=True))
    frags.append(text(danger_x + danger_w / 2, map_y + 55, "Непомітний оверлей", size=9, color=POS))
    frags.append(text(danger_x + danger_w / 2, map_y + 70, "HardFault / Смерть", size=9, color=POS, bold=True))

    # Стек
    stack_w = 160
    frags.append(rect(danger_x + danger_w, map_y, stack_w, map_h, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(danger_x + danger_w + stack_w / 2, map_y + 32, "Стек викликів (Stack)", size=11, color=NEG, bold=True))
    frags.append(text(danger_x + danger_w + stack_w / 2, map_y + 50, "← Зростає ліворуч", size=10, color=NEG))
    frags.append(line(danger_x + danger_w + stack_w - 30, map_y + 68, danger_x + danger_w + 30, map_y + 68, color=NEG, sw=2))

    # Вектори / стек переривань
    isr_w = 120
    frags.append(rect(danger_x + danger_w + stack_w, map_y, isr_w, map_h, fill="#e2e8f0", stroke="#475569", sw=1.2, rx=4))
    frags.append(text(danger_x + danger_w + stack_w + isr_w / 2, map_y + 35, "Стек переривань", size=11, bold=True))
    frags.append(text(danger_x + danger_w + stack_w + isr_w / 2, map_y + 55, "Main / MSP Stack", size=10, color=MUTED))

    # Нижній висновок
    bot_box, _, _ = textbox(W / 2, 410,
                            "MISRA C:2012 Rule 21.3 забороняє динамічну пам'ять (malloc/free/realloc/calloc).\n"
                            "Рішення: 100% статичний розподіл пулів фіксованих блоків та лінійних арен на етапі компіляції.",
                            size=11, pad=10, fill="#f0fdf4", stroke=FIELD, sw=1.5, color="#166534", bold=True)
    frags.append(bot_box)

    svg_content = '\n'.join(frags)
    with open(os.path.join(OUT, 'heap-fragmentation-anatomy.svg'), 'w', encoding='utf-8') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">\n{svg_content}\n</svg>')


# ── Фігура 2: Блоковий пул та Intrusive Free List ───────────────────────────
def fig_fixed_pool():
    W, H = 840, 460
    frags = []

    frags.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=4))

    # Заголовок
    frags.append(text(20, 28, "Архітектура блокового пула фіксованого розміру (Fixed-Size Block Pool)", size=14, color=INK, anchor="start", bold=True))

    # Статичний масив пам'яті
    frags.append(text(40, 60, "Статичний буфер у RAM: N однакових блоків розміром S байтів кожен", size=11, color=MUTED, anchor="start"))

    # Розміщення: Дескриптор пула ліворуч, далі 4 блоки
    # Блоки: 0: Вільний, 1: Зайнятий, 2: Вільний, 3: Вільний
    blk_y = 75
    blk_w, blk_h = 145, 80
    start_x = 185
    spacing = 16

    # Дескриптор пула ліворуч
    head_box, hw, hh = textbox(95, blk_y + blk_h / 2, "Дескриптор пула:\nfree_head", size=11, pad=10, fill="#eff6ff", stroke=NEG, sw=1.5, color=NEG, bold=True)
    frags.append(head_box)

    # Стрілка від free_head до Блоку 0
    frags.append(line(95 + hw / 2, blk_y + blk_h / 2, start_x, blk_y + blk_h / 2, color=NEG, sw=2))

    block_states = [
        ("Блок 0 [Вільний]", "next -> Блок 2", "#dbeafe", NEG, True),
        ("Блок 1 [Зайнятий]", "Корисні дані\n(App Data)", "#f1f5f9", INK, False),
        ("Блок 2 [Вільний]", "next -> Блок 3", "#dbeafe", NEG, True),
        ("Блок 3 [Вільний]", "next = NULL (Хвіст)", "#dbeafe", NEG, True),
    ]

    for i, (bhead, bbody, bfill, bcol, is_free) in enumerate(block_states):
        bx = start_x + i * (blk_w + spacing)
        st_col = NEG if is_free else "#64748b"
        frags.append(rect(bx, blk_y, blk_w, blk_h, fill=bfill, stroke=st_col, sw=1.5, rx=4))
        frags.append(text(bx + blk_w / 2, blk_y + 22, bhead, size=11, color=bcol, bold=True))

        lines = bbody.split("\n")
        if len(lines) == 1:
            frags.append(text(bx + blk_w / 2, blk_y + 48, lines[0], size=10, color=bcol))
        else:
            frags.append(text(bx + blk_w / 2, blk_y + 44, lines[0], size=10, color=bcol))
            frags.append(text(bx + blk_w / 2, blk_y + 60, lines[1], size=9, color=MUTED))

        # Адреса вгорі над блоком
        frags.append(text(bx + blk_w / 2, blk_y - 8, f"addr + {i}*S", size=9, color=MUTED))

    # Стрілка від Блоку 0 (x = start_x + blk_w/2) до Блоку 2 (x = start_x + 2*(blk_w+spacing) + blk_w/2)
    b0_cx = start_x + blk_w / 2
    b2_cx = start_x + 2 * (blk_w + spacing) + blk_w / 2
    b3_cx = start_x + 3 * (blk_w + spacing) + blk_w / 2

    # З'єднувальна дуга Блок 0 -> Блок 2 (знизу)
    frags.append(line(b0_cx, blk_y + blk_h, b0_cx, 195, color=NEG, sw=1.5))
    frags.append(line(b0_cx, 195, b2_cx - 20, 195, color=NEG, sw=1.5))
    frags.append(line(b2_cx - 20, 195, b2_cx - 20, blk_y + blk_h, color=NEG, sw=1.5))

    # З'єднувальна дуга Блок 2 -> Блок 3 (знизу)
    frags.append(line(b2_cx + 20, blk_y + blk_h, b2_cx + 20, 180, color=NEG, sw=1.5))
    frags.append(line(b2_cx + 20, 180, b3_cx, 180, color=NEG, sw=1.5))
    frags.append(line(b3_cx, 180, b3_cx, blk_y + blk_h, color=NEG, sw=1.5))

    # Блок опису операцій O(1)
    op_box_x, op_box_y = 40, 240
    frags.append(rect(op_box_x, op_box_y, 760, 160, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))

    frags.append(text(op_box_x + 20, op_box_y + 24, "Детерміновані операції без фрагментації:", size=12, color=INK, anchor="start", bold=True))

    # Виділення pool_alloc()
    frags.append(text(op_box_x + 30, op_box_y + 52, "• Виділення pool_alloc() — O(1) час виконання (3 процесорні інструкції):", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(op_box_x + 50, op_box_y + 72, "void* p = pool->head;   pool->head = *(void**)p;   return p;", size=11, color=NEG, anchor="start"))
    frags.append(text(op_box_x + 50, op_box_y + 88, "Блок виймається з голови зв'язного списку. Нульовий оверхед пам'яті для виділеного блоку!", size=10, color=MUTED, anchor="start"))

    # Звільнення pool_free()
    frags.append(text(op_box_x + 30, op_box_y + 116, "• Звільнення pool_free(p) — O(1) час виконання (2 процесорні інструкції):", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(op_box_x + 50, op_box_y + 136, "*(void**)p = pool->head;   pool->head = p;", size=11, color=FIELD, anchor="start"))
    frags.append(text(op_box_x + 50, op_box_y + 150, "Блок повертається у голову списку. Відсутність обходу сусідніх чанків і злиття (coalescing).", size=10, color=MUTED, anchor="start"))

    svg_content = '\n'.join(frags)
    with open(os.path.join(OUT, 'fixed-pool-intrusive-list.svg'), 'w', encoding='utf-8') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">\n{svg_content}\n</svg>')


# ── Фігура 3: Лінійна арена та Scratchpad ───────────────────────────────────
def fig_arena_lifecycle():
    W, H = 840, 460
    frags = []

    frags.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=4))

    # Заголовок
    frags.append(text(20, 28, "Лінійна арена пам'яті (Linear Arena) та двосторонній Scratchpad", size=14, color=INK, anchor="start", bold=True))

    # Секція 1: Одностороння лінійна арена (Bump Allocator)
    frags.append(text(30, 58, "1. Життєвий цикл обробки транзакції / кадру (Frame Allocator)", size=12, color=INK, anchor="start", bold=True))

    bar_x, bar_y, bar_w, bar_h = 40, 72, 760, 48
    frags.append(rect(bar_x, bar_y, bar_w, bar_h, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=4))

    # Зайняті частини арени
    a_blocks = [
        (40, 120, "#dcfce7", FIELD, "Об'єкт A (Парсер)\n120 Байтів"),
        (160, 16, "#f1f5f9", MUTED, "Pad\n8B"),
        (176, 180, "#dcfce7", FIELD, "Об'єкт B (Таблиця)\n180 Байтів"),
        (356, 12, "#f1f5f9", MUTED, "Pad\n4B"),
        (368, 110, "#dcfce7", FIELD, "Об'єкт C (Фільтр)\n110 Байтів"),
        (478, 322, "#ffffff", MUTED, "Невикористаний резерв арени\n(Free Capacity: 322 Байти)"),
    ]

    for bx, bw, bfill, bcol, blabel in a_blocks:
        frags.append(rect(bx, bar_y, bw, bar_h, fill=bfill, stroke="#cbd5e1", sw=1, rx=2))
        lines = blabel.split("\n")
        frags.append(text(bx + bw / 2, bar_y + 18, lines[0], size=10, color=bcol, bold=True))
        frags.append(text(bx + bw / 2, bar_y + 34, lines[1], size=9, color=bcol))

    # Вказівник offset (курсор)
    frags.append(line(478, bar_y + bar_h, 478, bar_y + bar_h + 22, color=POS, sw=2))
    frags.append(text(478, bar_y + bar_h + 35, "offset (курсор)", size=11, color=POS, bold=True))
    frags.append(text(478, bar_y + bar_h + 48, "Bump Allocation O(1)", size=9, color=POS))

    # Стрілка скидання арени arena_reset()
    frags.append(line(478, bar_y + bar_h + 60, 45, bar_y + bar_h + 60, color=NEG, sw=1.8))
    frags.append(text(260, bar_y + bar_h + 75, "arena_reset() повертає offset = 0 за одну команду O(1) наприкінці кадру", size=10, color=NEG, bold=True))

    # Розділювач
    frags.append(line(40, 215, 800, 215, color="#e2e8f0", sw=1.5, dash="4,4"))

    # Секція 2: Двонаправлена арена (Double-Ended Scratchpad)
    frags.append(text(30, 240, "2. Двостороння арена (Double-Ended Arena): стійкі дані + тимчасовий Scratchpad", size=12, color=INK, anchor="start", bold=True))

    dbar_y = 255
    frags.append(rect(bar_x, dbar_y, bar_w, bar_h, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=4))

    # Зліва ростуть довготривалі об'єкти (Нижня арена)
    frags.append(rect(bar_x, dbar_y, 220, bar_h, fill="#e0e7ff", stroke=NEG, sw=1.2, rx=2))
    frags.append(text(bar_x + 110, dbar_y + 20, "Стійкі дані кадру (Persistent)", size=10, color=NEG, bold=True))
    frags.append(text(bar_x + 110, dbar_y + 36, "Зростає зліва направо →", size=9, color=NEG))

    # Справа ростуть тимчасові буфери (Scratchpad)
    frags.append(rect(bar_x + bar_w - 200, dbar_y, 200, bar_h, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=2))
    frags.append(text(bar_x + bar_w - 100, dbar_y + 20, "Тимчасовий Scratchpad", size=10, color="#b45309", bold=True))
    frags.append(text(bar_x + bar_w - 100, dbar_y + 36, "← Зростає справа наліво", size=9, color="#b45309"))

    # Вільний зазор між ними
    frags.append(text(bar_x + 390, dbar_y + 28, "Спільний динамічний зазор", size=11, color=MUTED))

    # Вказівники
    frags.append(line(bar_x + 220, dbar_y + bar_h, bar_x + 220, dbar_y + bar_h + 18, color=NEG, sw=2))
    frags.append(text(bar_x + 220, dbar_y + bar_h + 30, "lower_offset", size=10, color=NEG, bold=True))

    frags.append(line(bar_x + bar_w - 200, dbar_y + bar_h, bar_x + bar_w - 200, dbar_y + bar_h + 18, color="#b45309", sw=2))
    frags.append(text(bar_x + bar_w - 200, dbar_y + bar_h + 30, "upper_offset", size=10, color="#b45309", bold=True))

    # Переваги підсумок
    summary_box, _, _ = textbox(W / 2, 395,
                                "Головний інваріант: Нуль індивідуальних викликів free() -> Нуль витоків пам'яті (Memory Leaks).\n"
                                "Повна локальність кешу даних L1, детермінований час O(1) і відсутність метаданих на кожен об'єкт.",
                                size=11, pad=10, fill="#f0fdf4", stroke=FIELD, sw=1.5, color="#166534", bold=True)
    frags.append(summary_box)

    svg_content = '\n'.join(frags)
    with open(os.path.join(OUT, 'linear-arena-lifecycle.svg'), 'w', encoding='utf-8') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">\n{svg_content}\n</svg>')


if __name__ == '__main__':
    fig_heap_fragmentation()
    fig_fixed_pool()
    fig_arena_lifecycle()
    print("Згенеровано 3 фігури в img/")

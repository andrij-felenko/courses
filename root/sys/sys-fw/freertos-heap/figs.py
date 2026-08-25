# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. heap-schemes-overview: Порівняння 5 схем FreeRTOS та ESP-IDF ──────────
def fig_schemes_overview():
    W, H = 860, 440
    p = []
    
    # Головна підкладка
    p.append(rect(20, 20, 820, 400, fill="#fdfefe", stroke=LINE, sw=1.5, rx=10))
    p.append(text(430, 48, "Архітектурні моделі розподілу динамічної пам'яті у FreeRTOS та ESP-IDF", size=14, bold=True, color=INK))
    
    cols = [
        (35, "heap_1", "Лінійний бамп", "Без free()", "O(1)", "#eafaf0", FIELD, "Детерміновано", FIELD),
        (168, "heap_2", "Best-Fit", "Без злиття", "O(N)", "#fdf6e3", "#b8860b", "O(N) пошук", "#b8860b"),
        (301, "heap_3", "Обгортка libc", "Пауза шедулера", "libc", "#fbf0f0", POS, "Залежить від libc", POS),
        (434, "heap_4", "First-Fit", "Злиття сусідів", "O(N)", "#eaf0fd", NEG, "O(N) пошук", "#b8860b"),
        (567, "heap_5", "Мультирегіон", "Злиття + банки", "O(N)", "#f3e8fd", "#7d3c98", "O(N) пошук", "#7d3c98"),
        (700, "ESP-IDF", "heap_caps/TLSF", "O(1) + теги пам'яті", "O(1)", "#e8f8f5", "#117a65", "Детерміновано", FIELD),
    ]
    
    card_w = 125
    for x, name, algo, feat, cplx, fill_col, border_col, det_label, det_col in cols:
        p.append(rect(x, 75, card_w, 325, fill=fill_col, stroke=border_col, sw=1.8, rx=8))
        p.append(text(x + card_w/2, 104, name, size=13, bold=True, color=border_col))
        
        # Розділювач
        p.append(line(x + 10, 118, x + card_w - 10, 118, color=border_col, sw=1.0, dash="3,3"))
        
        # Секція: Алгоритм
        p.append(text(x + card_w/2, 140, "Алгоритм:", size=10, color=MUTED, bold=True))
        p.append(rect(x + 8, 150, card_w - 16, 32, fill="#ffffff", stroke=border_col, sw=1.0, rx=4))
        p.append(text(x + card_w/2, 170, algo, size=10, bold=True, color=INK))
        
        # Секція: Звільнення
        p.append(text(x + card_w/2, 204, "Звільнення:", size=10, color=MUTED, bold=True))
        p.append(rect(x + 8, 214, card_w - 16, 32, fill="#ffffff", stroke=border_col, sw=1.0, rx=4))
        p.append(text(x + card_w/2, 234, feat, size=10, color=INK))
        
        # Секція: Складність
        p.append(text(x + card_w/2, 268, "Складність:", size=10, color=MUTED, bold=True))
        p.append(rect(x + 18, 278, card_w - 36, 30, fill="#ffffff", stroke=border_col, sw=1.2, rx=4))
        p.append(text(x + card_w/2, 298, cplx, size=11, bold=True, color=border_col))
        
        # Підсумок детермінізму
        p.append(text(x + card_w/2, 345, "Передбачуваність:", size=9, color=MUTED))
        p.append(text(x + card_w/2, 365, det_label, size=10, bold=True, color=det_col))

    render(os.path.join(OUT, "heap-schemes-overview.svg"), W, H, *p,
           title="Порівняння схем алокаторів FreeRTOS та ESP-IDF")


# ── 2. heap1-bump-pointer: Механіка лінійного алокатора heap_1 ───────────────
def fig_heap1_bump():
    W, H = 780, 250
    p = []
    
    bx, by, bw, bh = 50, 65, 680, 85
    p.append(rect(bx, by, bw, bh, fill="#f4f6f8", stroke=LINE, sw=2, rx=8))
    p.append(text(bx + bw/2, by - 16, "Статичний масив ucHeap[ configTOTAL_HEAP_SIZE ]", size=13, bold=True, color=INK))
    
    # Виділені блоки
    p.append(rect(bx, by, 140, bh, fill="#d5f5e3", stroke=FIELD, sw=1.5, rx=0))
    p.append(text(bx + 70, by + 36, "Задача 1 (TCB)", size=10, bold=True, color=FIELD))
    p.append(text(bx + 70, by + 54, "+ стек (640 Б)", size=9, color=FIELD))
    
    p.append(rect(bx + 140, by, 180, bh, fill="#d6eaf8", stroke=NEG, sw=1.5, rx=0))
    p.append(text(bx + 230, by + 36, "Черга повідомлень", size=10, bold=True, color=NEG))
    p.append(text(bx + 230, by + 54, "1024 байти", size=9, color=NEG))
    
    p.append(rect(bx + 320, by, 110, bh, fill="#e8daef", stroke="#7d3c98", sw=1.5, rx=0))
    p.append(text(bx + 375, by + 36, "М'ютекс", size=10, bold=True, color="#7d3c98"))
    p.append(text(bx + 375, by + 54, "128 байтів", size=9, color="#7d3c98"))
    
    # Вільний простір
    p.append(rect(bx + 430, by, 250, bh, fill="#ffffff", stroke=MUTED, sw=1.0, rx=0))
    p.append(text(bx + 555, by + 36, "Вільна пам'ять", size=11, bold=True, color=MUTED))
    p.append(text(bx + 555, by + 54, "(незайманий залишок пулу)", size=9, color=MUTED))
    
    # Вказівник xNextFreeByte
    p.append(arrow(bx + 430, by + bh + 42, bx + 430, by + bh + 4, color=POS, sw=2.2))
    p.append(text(bx + 430, by + bh + 58, "xNextFreeByte (бамп-покажчик зміщення)", size=11, bold=True, color=POS))
    p.append(text(bx + 430, by + bh + 74, "Рух лише вперед; виклик vPortFree() нічого не робить", size=10, italic=True, color=MUTED))

    render(os.path.join(OUT, "heap1-bump-pointer.svg"), W, H, *p,
           title="Лінійний алокатор heap_1: бамп-покажчик")


# ── 3. heap2-vs-heap4-fragmentation: Порівняння heap_2 та heap_4 ─────────────
def fig_heap2_vs_heap4():
    W, H = 820, 430
    p = []
    
    p.append(rect(20, 20, 780, 390, fill="#fdfefe", stroke=LINE, sw=1.5, rx=10))
    
    p.append(text(410, 45, "Виділено три блоки (A=200Б, B=300Б, C=200Б), після чого блоки A та B звільнено", size=12, bold=True, color=INK))
    
    # Секція heap_2 (без злиття)
    y2 = 75
    p.append(rect(40, y2, 740, 135, fill="#fdfcf7", stroke="#b8860b", sw=1.5, rx=6))
    p.append(text(60, y2 + 24, "heap_2 (Best-Fit, список за розміром, БЕЗ злиття сусідів):", size=11, bold=True, color="#b8860b", anchor="start"))
    
    p.append(rect(60, y2 + 38, 160, 50, fill="#ffffff", stroke="#b8860b", sw=1.5, rx=4))
    p.append(text(140, y2 + 68, "Вільний A (200 Б)", size=10, bold=True, color="#b8860b"))
    
    p.append(rect(230, y2 + 38, 220, 50, fill="#ffffff", stroke="#b8860b", sw=1.5, rx=4))
    p.append(text(340, y2 + 68, "Вільний B (300 Б)", size=10, bold=True, color="#b8860b"))
    
    p.append(rect(460, y2 + 38, 160, 50, fill="#d6eaf8", stroke=NEG, sw=1.5, rx=4))
    p.append(text(540, y2 + 68, "Зайнятий C (200 Б)", size=10, bold=True, color=NEG))
    
    p.append(rect(630, y2 + 38, 130, 50, fill="#f4f6f8", stroke=MUTED, sw=1.0, rx=4))
    p.append(text(695, y2 + 68, "Решта пулу...", size=10, color=MUTED))
    
    p.append(text(60, y2 + 112, "Запит на 400 Б → ВІДМОВА (NULL)! Сусідні блоки A і B ізольовані й не об'єднуються.", size=10, bold=True, color=POS, anchor="start"))
    
    # Секція heap_4 (зі злиттям)
    y4 = 230
    p.append(rect(40, y4, 740, 160, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(60, y4 + 24, "heap_4 (First-Fit, список за адресою, ЗЛИВАННЯ суміжних вільних блоків):", size=11, bold=True, color=FIELD, anchor="start"))
    
    p.append(rect(60, y4 + 38, 390, 50, fill="#d5f5e3", stroke=FIELD, sw=2.0, rx=4))
    p.append(text(255, y4 + 62, "Об'єднаний вільний блок (A + B = 500 Б)", size=11, bold=True, color=FIELD))
    p.append(text(255, y4 + 77, "Суміжні вільні ділянки зшиваються в єдиний монолітний простір", size=9, color=MUTED))
    
    p.append(rect(460, y4 + 38, 160, 50, fill="#d6eaf8", stroke=NEG, sw=1.5, rx=4))
    p.append(text(540, y4 + 68, "Зайнятий C (200 Б)", size=10, bold=True, color=NEG))
    
    p.append(rect(630, y4 + 38, 130, 50, fill="#f4f6f8", stroke=MUTED, sw=1.0, rx=4))
    p.append(text(695, y4 + 68, "Решта пулу...", size=10, color=MUTED))
    
    p.append(text(60, y4 + 114, "Запит на 400 Б → УСПІХ! Виділяється 400 Б, залишок 100 Б повертається у список.", size=10, bold=True, color=FIELD, anchor="start"))
    p.append(text(60, y4 + 135, "Зовнішня фрагментація активно нівелюється під час кожного виклику vPortFree()", size=9, italic=True, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "heap2-vs-heap4-fragmentation.svg"), W, H, *p,
           title="Фрагментація пам'яті: heap_2 проти злиття блоків у heap_4")


# ── 4. block-link-anatomy: Анатомія заголовка BlockLink_t та вирівнювання ────
def fig_block_link():
    W, H = 780, 320
    p = []
    
    p.append(rect(20, 20, 740, 280, fill="#fdfefe", stroke=LINE, sw=1.5, rx=10))
    p.append(text(390, 45, "Анатомія виділеного блока пам'яті та заголовка BlockLink_t (32-бітний MCU)", size=13, bold=True, color=INK))
    
    # Головний блок
    bx, by, bw, bh = 50, 75, 680, 90
    p.append(rect(bx, by, bw, bh, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=6))
    
    # Заголовок BlockLink_t (8 байтів: 2x 32-бітних слова)
    hw = 230
    p.append(rect(bx, by, hw, bh, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    p.append(text(bx + hw/2, by + 20, "Службовий заголовок BlockLink_t (8 Б)", size=10, bold=True, color=NEG))
    
    # Підполя заголовка
    p.append(rect(bx + 10, by + 32, 100, 48, fill="#ffffff", stroke=NEG, sw=1.0, rx=3))
    p.append(text(bx + 60, by + 50, "pxNextFreeBlock", size=9, bold=True, color=NEG))
    p.append(text(bx + 60, by + 68, "4 байти", size=9, color=MUTED))
    
    p.append(rect(bx + 120, by + 32, 100, 48, fill="#ffffff", stroke=NEG, sw=1.0, rx=3))
    p.append(text(bx + 170, by + 50, "xBlockSize | MSB", size=9, bold=True, color=NEG))
    p.append(text(bx + 170, by + 68, "4 байти (MSB=стан)", size=9, color=MUTED))
    
    # Корисне навантаження
    pw = 450
    p.append(rect(bx + hw, by, pw, bh, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(bx + hw + pw/2, by + 35, "Корисне навантаження (Payload) користувача", size=12, bold=True, color=FIELD))
    p.append(text(bx + hw + pw/2, by + 58, "Вирівняно на 8 байтів (portBYTE_ALIGNMENT)", size=10, color=MUTED))
    
    # Покажчики та виноски
    p.append(rect(50, 195, 310, 85, fill="#fef9e7", stroke="#b8860b", sw=1.2, rx=6))
    p.append(text(205, 215, "Біт стану xBlockAllocatedBit (старший біт MSB):", size=9, bold=True, color="#b8860b"))
    p.append(text(205, 235, "• Біт 31 = 1: Блок виділено (зайнято користувачем)", size=9, color=INK))
    p.append(text(205, 252, "• Біт 31 = 0: Блок вільний у списку xStart/xEnd", size=9, color=INK))
    p.append(text(205, 269, "Економить 4 байти на прапорець зайнятості!", size=9, italic=True, color=FIELD))
    
    # Виноска вказівника користувача праворуч
    p.append(rect(390, 195, 340, 85, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(560, 215, "Вказівник pv від pvPortMalloc():", size=10, bold=True, color=FIELD))
    p.append(text(560, 235, "pv = (void*)( (uint8_t*)pBlock + xHeapStructSize )", size=9, bold=True, color=INK))
    p.append(text(560, 254, "При vPortFree(pv) заголовок шукається зсувом назад:", size=9, color=MUTED))
    p.append(text(560, 270, "pBlock = (BlockLink_t*)( (uint8_t*)pv - xHeapStructSize )", size=9, color=MUTED))

    render(os.path.join(OUT, "block-link-anatomy.svg"), W, H, *p,
           title="Анатомія заголовка блока BlockLink_t у FreeRTOS")


# ── 5. heap5-multi-region: Мультирегіональний пул пам'яті heap_5 ──────────────
def fig_heap5_regions():
    W, H = 820, 320
    p = []
    
    p.append(rect(20, 20, 780, 280, fill="#fdfefe", stroke=LINE, sw=1.5, rx=10))
    p.append(text(410, 45, "Ініціалізація розрізнених банків пам'яті через vPortDefineHeapRegions() у heap_5", size=12, bold=True, color=INK))
    
    regions = [
        (40, "Регіон 0 (Внутрішня SRAM 1)", "0x20000000", "Розмір: 64 КБ", "#d5f5e3", FIELD),
        (280, "Регіон 1 (Внутрішня SRAM 2)", "0x20040000", "Розмір: 128 КБ", "#d6eaf8", NEG),
        (520, "Регіон 2 (Зовнішня SDRAM / PSRAM)", "0x60000000", "Розмір: 4 МБ", "#e8daef", "#7d3c98"),
    ]
    
    rw = 220
    for x, title, addr, sz, fill_col, border_col in regions:
        p.append(rect(x, 75, rw, 130, fill=fill_col, stroke=border_col, sw=1.8, rx=8))
        p.append(text(x + rw/2, 100, title, size=10, bold=True, color=border_col))
        
        p.append(rect(x + 30, 115, rw - 60, 28, fill="#ffffff", stroke=border_col, sw=1.0, rx=4))
        p.append(text(x + rw/2, 133, addr, size=10, bold=True, color=INK))
        
        p.append(text(x + rw/2, 165, sz, size=10, bold=True, color=INK))
        p.append(text(x + rw/2, 185, "Елемент HeapRegion_t", size=9, italic=True, color=MUTED))
        
    # Стрілки зв'язування регіонів у єдиний ланцюг
    p.append(arrow(262, 140, 278, 140, color=POS, sw=2.2))
    p.append(arrow(502, 140, 518, 140, color=POS, sw=2.2))
    
    # Нижній блок правил
    p.append(rect(40, 220, 740, 65, fill="#f4f6f8", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(410, 240, "Критичне правило впорядкування: Регіони в масиві МУСЯТЬ бути відсортовані за зростанням адрес!", size=10, bold=True, color=POS))
    p.append(text(410, 258, "Масив завершується нульовим термінатором: { NULL, 0 }. Усі регіони зшиваються в єдиний First-Fit список.", size=10, color=INK))
    p.append(text(410, 274, "Злиття блоків (coalescing) працює всередині кожного банку; між банками межі фізично ізольовані.", size=9, italic=True, color=MUTED))

    render(os.path.join(OUT, "heap5-multi-region.svg"), W, H, *p,
           title="Мультирегіональний розподіл пам'яті heap_5")


# ── 6. esp-idf-heap-caps-tlsf: Гетерогенна пам'ять ESP32 та TLSF ──────────────
def fig_esp_heap_caps():
    W, H = 840, 420
    p = []
    
    p.append(rect(20, 20, 800, 380, fill="#fdfefe", stroke=LINE, sw=1.5, rx=10))
    p.append(text(420, 45, "Гетерогенна пам'ять ESP32: селекція алокації через heap_caps_malloc() та TLSF", size=13, bold=True, color=INK))
    
    # Лівий блок: Запит із тегами можливостей
    p.append(rect(40, 75, 230, 290, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8))
    p.append(text(155, 102, "Запит програми", size=12, bold=True, color=NEG))
    
    p.append(text(155, 126, "heap_caps_malloc(sz, caps)", size=9, bold=True, color=INK))
    
    caps = [
        ("MALLOC_CAP_DMA", "Буфери SPI/I2S/Wi-Fi", POS),
        ("MALLOC_CAP_EXEC", "Код IRAM / хуки ISR", "#7d3c98"),
        ("MALLOC_CAP_SPIRAM", "Зовнішня PSRAM (MB)", FIELD),
        ("MALLOC_CAP_INTERNAL", "Швидка пам'ять SRAM", NEG),
        ("MALLOC_CAP_8BIT", "Звичайні дані (DRAM)", "#b8860b"),
    ]
    
    y = 148
    for c_name, c_desc, col in caps:
        p.append(rect(55, y, 200, 34, fill="#ffffff", stroke=col, sw=1.2, rx=4))
        p.append(text(155, y + 14, c_name, size=9, bold=True, color=col))
        p.append(text(155, y + 27, c_desc, size=9, color=MUTED))
        y += 42
        
    # Центральний диспетчер тегів
    p.append(rect(300, 135, 160, 170, fill="#fdf6e3", stroke="#b8860b", sw=2.0, rx=8))
    p.append(text(380, 165, "Каталог регіонів", size=11, bold=True, color="#b8860b"))
    p.append(text(380, 185, "та матриця", size=11, bold=True, color="#b8860b"))
    p.append(text(380, 205, "можливостей", size=11, bold=True, color="#b8860b"))
    p.append(text(380, 225, "(Capabilities)", size=11, bold=True, color="#b8860b"))
    p.append(text(380, 260, "Фільтрація за", size=9, italic=True, color=MUTED))
    p.append(text(380, 276, "бітовою маскою", size=9, italic=True, color=MUTED))
    
    p.append(arrow(272, 220, 298, 220, color=NEG, sw=2.2))
    
    # Правий блок: Фізичні пули пам'яті TLSF
    pools = [
        (490, 75, "Внутрішня IRAM (Код)", "TLSF Pool (EXEC)", "#e8daef", "#7d3c98"),
        (490, 150, "Внутрішня DRAM (SRAM / DMA)", "TLSF Pool (DMA, 8BIT, INT)", "#d5f5e3", FIELD),
        (490, 225, "Зовнішня PSRAM (SPI RAM)", "TLSF Pool (SPIRAM, 8BIT)", "#d6eaf8", NEG),
        (490, 300, "RTC Fast/Slow Memory", "TLSF Pool (RETENTION)", "#fef9e7", "#b8860b"),
    ]
    
    pw = 310
    for x, py_pos, p_title, p_sub, p_fill, p_col in pools:
        p.append(rect(x, py_pos, pw, 65, fill=p_fill, stroke=p_col, sw=1.5, rx=6))
        p.append(text(x + pw/2, py_pos + 22, p_title, size=11, bold=True, color=p_col))
        p.append(text(x + pw/2, py_pos + 42, p_sub, size=9, bold=True, color=INK))
        p.append(text(x + pw/2, py_pos + 56, "O(1) TLSF алокатор зі злиттям", size=9, italic=True, color=MUTED))
        p.append(arrow(462, 220, x - 2, py_pos + 32, color=p_col, sw=1.5))
        
    render(os.path.join(OUT, "esp-idf-heap-caps-tlsf.svg"), W, H, *p,
           title="Архітектура пам'яті ESP-IDF: heap_caps та TLSF")


if __name__ == "__main__":
    fig_schemes_overview()
    fig_heap1_bump()
    fig_heap2_vs_heap4()
    fig_block_link()
    fig_heap5_regions()
    fig_esp_heap_caps()
    print("Figures generated successfully.")

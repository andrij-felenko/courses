# -*- coding: utf-8 -*-
import sys, os

# Додаємо scripts до sys.path для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори
GOLD = "#b8860b"
PURPLE = "#8e44ad"
CYAN = "#00838f"

def fig_sbrk_collision():
    """Діаграма колізії купи та стека в SRAM при викликах _sbrk."""
    W, H = 840, 530
    p = []
    
    # Заголовок / фонова панель
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8))
    p.append(text(W / 2, 38, "Карта оперативної пам'яті SRAM: механізм росту купи та детекція колізії зі стеком", size=15, color=INK, bold=True))
    
    # Основний блок пам'яті SRAM
    ram_x = 50
    ram_y = 100
    ram_w = 740
    ram_h = 100
    
    # Секції пам'яті:
    # 1. Статична пам'ять (.data + .bss)
    w_static = 140
    p.append(rect(ram_x, ram_y, w_static, ram_h, fill="#e8edf5", stroke=NEG, sw=1.5, rx=0))
    p.append(text(ram_x + w_static / 2, ram_y + 35, ".data / .bss", size=13, color=NEG, bold=True))
    p.append(text(ram_x + w_static / 2, ram_y + 58, "Статичні дані", size=11, color=MUTED))
    p.append(text(ram_x + w_static / 2, ram_y + 78, "глобальні змінні", size=10, color=MUTED))
    
    # 2. Купа (Heap) - активна частина
    w_heap = 160
    heap_x = ram_x + w_static
    p.append(rect(heap_x, ram_y, w_heap, ram_h, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=0))
    p.append(text(heap_x + w_heap / 2, ram_y + 35, "Купа (Heap)", size=13, color=FIELD, bold=True))
    p.append(text(heap_x + w_heap / 2, ram_y + 58, "Виділені блоки", size=11, color=MUTED))
    p.append(text(heap_x + w_heap / 2, ram_y + 78, "malloc() / new", size=10, color=MUTED))
    
    # 3. Вільний простір (Free Margin)
    w_free = 170
    free_x = heap_x + w_heap
    p.append(rect(free_x, ram_y, w_free, ram_h, fill="#fffde7", stroke=GOLD, sw=1.5, rx=0))
    p.append(text(free_x + w_free / 2, ram_y + 35, "Вільна пам'ять", size=13, color=GOLD, bold=True))
    p.append(text(free_x + w_free / 2, ram_y + 58, "Запас росту купи", size=11, color=MUTED))
    p.append(text(free_x + w_free / 2, ram_y + 78, "до межі стека", size=10, color=MUTED))
    
    # 4. Захисний бар'єр (Safety Gap)
    w_gap = 60
    gap_x = free_x + w_free
    p.append(rect(gap_x, ram_y, w_gap, ram_h, fill="#fee2e2", stroke=POS, sw=1.5, rx=0))
    p.append(text(gap_x + w_gap / 2, ram_y + 45, "Бар'єр", size=11, color=POS, bold=True))
    p.append(text(gap_x + w_gap / 2, ram_y + 65, "GAP", size=10, color=POS, bold=True))
    
    # 5. Стек (Stack)
    w_stack = 210
    stack_x = gap_x + w_gap
    p.append(rect(stack_x, ram_y, w_stack, ram_h, fill="#fdecea", stroke=POS, sw=1.5, rx=0))
    p.append(text(stack_x + w_stack / 2, ram_y + 35, "Стек викликів", size=13, color=POS, bold=True))
    p.append(text(stack_x + w_stack / 2, ram_y + 58, "Локальні змінні, ISR", size=11, color=MUTED))
    p.append(text(stack_x + w_stack / 2, ram_y + 78, "Поточний SP ядра", size=10, color=MUTED))
    
    # Зовнішній контур
    p.append(rect(ram_x, ram_y, ram_w, ram_h, fill="none", stroke=INK, sw=2, rx=0))
    
    # Адресні мітки зверху
    p.append(line(ram_x, ram_y - 20, ram_x, ram_y, color=LINE, sw=1.2, dash="2,2"))
    p.append(text(ram_x, ram_y - 26, "0x20000000", size=10, color=INK, anchor="start"))
    
    p.append(line(heap_x, ram_y - 20, heap_x, ram_y, color=LINE, sw=1.2, dash="2,2"))
    p.append(text(heap_x, ram_y - 26, "_end / __heap_start__", size=10, color=FIELD, anchor="middle", bold=True))
    
    p.append(line(free_x, ram_y - 20, free_x, ram_y, color=LINE, sw=1.2, dash="2,2"))
    p.append(text(free_x, ram_y - 26, "Поточний break", size=10, color=GOLD, anchor="middle", bold=True))
    
    p.append(line(gap_x, ram_y - 20, gap_x, ram_y, color=LINE, sw=1.2, dash="2,2"))
    p.append(text(gap_x, ram_y - 26, "__StackLimit", size=10, color=POS, anchor="middle", bold=True))
    
    p.append(line(ram_x + ram_w, ram_y - 20, ram_x + ram_w, ram_y, color=LINE, sw=1.2, dash="2,2"))
    p.append(text(ram_x + ram_w, ram_y - 26, "_estack (Вершина RAM)", size=10, color=INK, anchor="end"))
    
    # Стрілки росту знизу пам'яті (у зоні ram_y + 100 до 250)
    y_arrows = ram_y + 122
    p.append(arrow(heap_x + 10, y_arrows, free_x + 60, y_arrows, color=FIELD, sw=2.2))
    p.append(text(heap_x + 100, y_arrows + 16, "Ріст купи через _sbrk (+incr) →", size=10, color=FIELD, bold=True, anchor="middle"))
    
    p.append(arrow(ram_x + ram_w - 10, y_arrows, stack_x - 10, y_arrows, color=POS, sw=2.2))
    p.append(text(stack_x + 90, y_arrows + 16, "← Ріст стека через push/виклики", size=10, color=POS, bold=True, anchor="middle"))
    
    # Нижній блок: 3 картки процесу _sbrk
    y_cards = 270
    h_card = 220
    w_c = 226
    gap_c = 25
    
    # Картка 1: Запит
    c1_x = 50
    p.append(rect(c1_x, y_cards, w_c, h_card, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(rect(c1_x, y_cards, w_c, 32, fill="#f1f5f9", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(c1_x + w_c / 2, y_cards + 21, "1. Запит пам'яті", size=12, color=INK, bold=True))
    p.append(mtext(c1_x + w_c / 2, y_cards + 52, 
        "1. malloc() потребує чанк\n"
        "2. Виклик _sbrk(incr)\n"
        "3. Отримання SP процесора:\n"
        "   __get_MSP() або __get_SP()\n"
        "4. Розрахунок нової межі:\n"
        "   next_brk = prev_brk + incr", size=11, color=INK, lh=1.4))
    
    # Стрілка 1->2
    p.append(arrow(c1_x + w_c + 4, y_cards + 105, c1_x + w_c + gap_c - 4, y_cards + 105, color=LINE, sw=1.8))
    
    # Картка 2: Перевірка
    c2_x = c1_x + w_c + gap_c
    p.append(rect(c2_x, y_cards, w_c, h_card, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(rect(c2_x, y_cards, w_c, 32, fill="#fef3c7", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(c2_x + w_c / 2, y_cards + 21, "2. Перевірка колізії", size=12, color=GOLD, bold=True))
    p.append(mtext(c2_x + w_c / 2, y_cards + 52,
        "Умова безпеки:\n"
        "next_brk + STACK_MARGIN\n"
        "    <= current_sp\n\n"
        "Якщо запас є (без колізії):\n"
        "heap_end = next_brk\n"
        "return prev_brk (Успіх)", size=11, color=INK, lh=1.4))
        
    # Стрілка 2->3
    p.append(arrow(c2_x + w_c + 4, y_cards + 105, c2_x + w_c + gap_c - 4, y_cards + 105, color=LINE, sw=1.8))
    
    # Картка 3: Захист від падіння
    c3_x = c2_x + w_c + gap_c
    p.append(rect(c3_x, y_cards, w_c, h_card, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(rect(c3_x, y_cards, w_c, 32, fill="#fee2e2", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(c3_x + w_c / 2, y_cards + 21, "3. Захист від аварії", size=12, color=POS, bold=True))
    p.append(mtext(c3_x + w_c / 2, y_cards + 52,
        "Колізія (next_brk > SP):\n"
        "1. Заборона росту break\n"
        "2. Встановлення коду помилки:\n"
        "   errno = ENOMEM\n"
        "3. return (void*)-1\n"
        "4. malloc() повертає NULL\n"
        "   Стек не пошкоджено!", size=11, color=INK, lh=1.4))
        
    svg_content = "\n".join(p)
    with open(os.path.join(OUT, "newlib-sbrk-heap-stack-collision.svg"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (W, H, W, H))
        f.write('<defs>\n')
        f.write('  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n')
        f.write('    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>\n' % LINE)
        f.write('  </marker>\n')
        f.write('</defs>\n')
        f.write(svg_content)
        f.write('\n</svg>')

def fig_nano_specs_optimization():
    """Діаграма порівняння та оптимізації Newlib проти Newlib-nano."""
    W, H = 840, 520
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8))
    p.append(text(W / 2, 38, "Архітектурне порівняння: стандартна Newlib проти Newlib-nano (--specs=nano.specs)", size=15, color=INK, bold=True))
    
    # Ліва колонка: Повна Newlib
    x_left = 40
    y_top = 70
    w_col = 360
    h_col = 420
    
    p.append(rect(x_left, y_top, w_col, h_col, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    p.append(rect(x_left, y_top, w_col, 40, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=6))
    p.append(text(x_left + w_col / 2, y_top + 25, "Стандартна Newlib (libc.a)", size=14, color=INK, bold=True))
    
    # Блоки всередині повної Newlib
    y_item = y_top + 55
    
    # 1. vfprintf & Float
    p.append(rect(x_left + 15, y_item, w_col - 30, 75, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    p.append(text(x_left + 25, y_item + 22, "Монолітний vfprintf / vfscanf", size=12, color=POS, bold=True, anchor="start"))
    p.append(mtext(x_left + 25, y_item + 42,
        "• Плаваюча кома (%f, %e) завжди влінкована\n"
        "• Алгоритми Dragon4 / Grisu + Bignum арифметика\n"
        "• Flash overhead: +35..50 КБ коду!", size=10, color=INK, lh=1.35, anchor="start"))
        
    y_item += 85
    # 2. struct _reent
    p.append(rect(x_left + 15, y_item, w_col - 30, 75, fill="#fef3c7", stroke=GOLD, sw=1.2, rx=4))
    p.append(text(x_left + 25, y_item + 22, "Повна структура struct _reent", size=12, color=GOLD, bold=True, anchor="start"))
    p.append(mtext(x_left + 25, y_item + 42,
        "• Повні файлові буфери FILE, масиви signal/locale\n"
        "• Розмір: ~1024..1200 байтів на КОЖЕН потік!\n"
        "• Катастрофічні витрати RAM у RTOS", size=10, color=INK, lh=1.35, anchor="start"))
        
    y_item += 85
    # 3. Dynamic Heap & File IO
    p.append(rect(x_left + 15, y_item, w_col - 30, 75, fill="#e8edf5", stroke=NEG, sw=1.2, rx=4))
    p.append(text(x_left + 25, y_item + 22, "Повнофункціональний стрімовий I/O", size=12, color=NEG, bold=True, anchor="start"))
    p.append(mtext(x_left + 25, y_item + 42,
        "• Динамічне виділення буферів при відкритті stdin/out\n"
        "• Тягне за собою важкий алокатор Doug Lea malloc\n"
        "• Багатовимірні таблиці перетворення локалей", size=10, color=INK, lh=1.35, anchor="start"))

    y_item += 85
    # 4. Підсумок витрат
    p.append(rect(x_left + 15, y_item, w_col - 30, 60, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=4))
    p.append(text(x_left + w_col / 2, y_item + 22, "Загальний відбиток (Footprint):", size=11, color=MUTED, bold=True))
    p.append(text(x_left + w_col / 2, y_item + 45, "Flash: 45–70 КБ  |  RAM: 1.5–3+ КБ", size=13, color=POS, bold=True))

    # Права колонка: Newlib-nano
    x_right = 440
    
    p.append(rect(x_right, y_top, w_col, h_col, fill="#ffffff", stroke=FIELD, sw=1.8, rx=6))
    p.append(rect(x_right, y_top, w_col, 40, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(x_right + w_col / 2, y_top + 25, "Newlib-nano (libc_nano.a)", size=14, color=FIELD, bold=True))

    y_item = y_top + 55
    
    # 1. Nano vfprintf & Pluggable Float
    p.append(rect(x_right + 15, y_item, w_col - 30, 75, fill="#ecfdf5", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(x_right + 25, y_item + 22, "Оптимізований _nano_vfprintf", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(mtext(x_right + 25, y_item + 42,
        "• За замовчуванням: лише цілочисельний друк (%d, %x, %s)\n"
        "• Float підключається опційно: -u _printf_float\n"
        "• Flash overhead: лише 2–5 КБ коду!", size=10, color=INK, lh=1.35, anchor="start"))
        
    y_item += 85
    # 2. struct _reent nano
    p.append(rect(x_right + 15, y_item, w_col - 30, 75, fill="#ecfdf5", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(x_right + 25, y_item + 22, "Компактна struct _reent (Tiny)", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(mtext(x_right + 25, y_item + 42,
        "• Мінімальні статичні покажчики, урізані структури\n"
        "• Розмір: лише ~80–120 байтів на потік!\n"
        "• Ідеально для FreeRTOS / Zephyr та малих SRAM", size=10, color=INK, lh=1.35, anchor="start"))

    y_item += 85
    # 3. Nano-malloc
    p.append(rect(x_right + 15, y_item, w_col - 30, 75, fill="#ecfdf5", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(x_right + 25, y_item + 22, "Легкий nano-malloc & небуферизований I/O", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(mtext(x_right + 25, y_item + 42,
        "• Спрощений однозв'язний список вільних блоків\n"
        "• Прямий вивід у заглушки без масивних проміжних черг\n"
        "• Мінімальне споживання RAM рантаймом", size=10, color=INK, lh=1.35, anchor="start"))

    y_item += 85
    # 4. Підсумок витрат nano
    p.append(rect(x_right + 15, y_item, w_col - 30, 60, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=4))
    p.append(text(x_right + w_col / 2, y_item + 22, "Загальний відбиток (Footprint):", size=11, color=MUTED, bold=True))
    p.append(text(x_right + w_col / 2, y_item + 45, "Flash: 6–15 КБ  |  RAM: 150–300 байтів", size=13, color=FIELD, bold=True))

    svg_content = "\n".join(p)
    with open(os.path.join(OUT, "newlib-nano-specs-optimization.svg"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n' % (W, H, W, H))
        f.write('<defs>\n')
        f.write('  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n')
        f.write('    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>\n' % LINE)
        f.write('  </marker>\n')
        f.write('</defs>\n')
        f.write(svg_content)
        f.write('\n</svg>')

if __name__ == "__main__":
    fig_sbrk_collision()
    fig_nano_specs_optimization()
    print("Figures generated successfully.")

# -*- coding: utf-8 -*-
"""Фігури до статті «Свої секції, буфер DMA, стек і купа під свій обсяг».
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Розкладка пам'яті: Flash (LMA) ↔ RAM домени (VMA) ───────────────────
def fig_memory_map():
    W, H = 880, 520
    f = []

    # Заголовок
    f.append(text(W / 2, 28, "Розкладка пам'яті мікроконтролера: LMA у Flash та VMA у доменах RAM",
                  size=16, bold=True))

    # Стовпчик Flash (LMA)
    fx, fy, fw, fh = 60, 70, 240, 420
    f.append(rect(fx, fy, fw, fh, fill="#fdfefe", stroke=LINE, sw=1.8, rx=8))
    f.append(rect(fx, fy, fw, 36, fill="#2c3e50", stroke=LINE, sw=1.8, rx=8))
    f.append(text(fx + fw / 2, fy + 22, "FLASH (LMA: 0x08000000)", size=13, color="#ffffff", bold=True))

    # Блоки всередині Flash
    f.append(fitbox(fx + 10, fy + 46, fw - 20, 48, ".isr_vector\nТаблиця векторів (SP, Reset)", fill="#eaeded", stroke=MUTED, size=11, bold=True))
    f.append(fitbox(fx + 10, fy + 100, fw - 20, 68, ".text\nМашинний код функцій", fill="#d4efdf", stroke="#27ae60", size=11, bold=True))
    f.append(fitbox(fx + 10, fy + 174, fw - 20, 48, ".rodata\nКонстанти, рядки, таблиці", fill="#e8f8f5", stroke=MUTED, size=11, bold=True))
    f.append(fitbox(fx + 10, fy + 228, fw - 20, 68, "Початкові значення .data\n(образ ініціалізації LMA)", fill="#fdebd0", stroke="#e67e22", size=11, bold=True))
    f.append(fitbox(fx + 10, fy + 302, fw - 20, 68, "Початкові значення .ram_code\n(швидкі функції для ITCM)", fill="#ebdef0", stroke="#8e44ad", size=11, bold=True))
    f.append(fitbox(fx + 10, fy + 376, fw - 20, 36, "Вільний Flash", fill="#f4f6f8", stroke=MUTED, size=10, italic=True))

    # Стовпчик RAM_D1 / DTCM (VMA)
    rx, ry, rw, rh = 360, 70, 230, 420
    f.append(rect(rx, ry, rw, rh, fill="#fdfefe", stroke=LINE, sw=1.8, rx=8))
    f.append(rect(rx, ry, rw, 36, fill="#1b4f72", stroke=LINE, sw=1.8, rx=8))
    f.append(text(rx + rw / 2, ry + 22, "DTCM / RAM_D1 (0x20000000)", size=12, color="#ffffff", bold=True))

    f.append(fitbox(rx + 10, ry + 46, rw - 20, 56, ".data (VMA)\nГлобальні ініціалізовані змінні", fill="#fdebd0", stroke="#e67e22", size=11, bold=True))
    f.append(fitbox(rx + 10, ry + 108, rw - 20, 56, ".bss (VMA)\nОбнулені змінні (NOLOAD)", fill="#ebf5fb", stroke="#2980b9", size=11, bold=True))
    f.append(fitbox(rx + 10, ry + 170, rw - 20, 64, "Купа (Heap: _Min_Heap_Size)\nРосте вгору (sbrk →)", fill="#fef9e7", stroke="#f39c12", size=11, bold=True))
    f.append(fitbox(rx + 10, ry + 240, rw - 20, 80, "Вільний простір пам'яті\n(Safety Gap / запас)", fill="#ffffff", stroke=MUTED, size=10, italic=True))
    f.append(fitbox(rx + 10, ry + 326, rw - 20, 64, "Стек (Stack: _Min_Stack_Size)\nРосте вниз (← SP)", fill="#fadbd8", stroke="#c0392b", size=11, bold=True))
    f.append(text(rx + rw / 2, ry + 404, "_estack = 0x20020000", size=10, bold=True, color="#c0392b"))

    # Стовпчик RAM_D2 (VMA DMA Domain)
    dx, dy, dw, dh = 630, 70, 200, 420
    f.append(rect(dx, dy, dw, dh, fill="#fdfefe", stroke=LINE, sw=1.8, rx=8))
    f.append(rect(dx, dy, dw, 36, fill="#4a235a", stroke=LINE, sw=1.8, rx=8))
    f.append(text(dx + dw / 2, dy + 22, "RAM_D2 (0x30000000)", size=12, color="#ffffff", bold=True))

    f.append(fitbox(dx + 10, dy + 46, dw - 20, 80, ".dma_buffer (VMA)\nБуфери Ethernet, SDMMC, SPI\n(ALIGN(32), Non-cacheable)", fill="#d5f5e3", stroke="#27ae60", size=10.5, bold=True))
    f.append(fitbox(dx + 10, dy + 132, dw - 20, 60, "DMA-дескриптори\nКільцеві списки передачі", fill="#e8f8f5", stroke="#16a085", size=10.5, bold=True))
    f.append(fitbox(dx + 10, dy + 198, dw - 20, 204, "Вільна пам'ять домену D2", fill="#f4f6f8", stroke=MUTED, size=10, italic=True))

    # Стрілки копіювання / ініціалізації
    f.append(arrow(fx + fw - 10, fy + 262, rx + 10, ry + 74, color="#e67e22", sw=2.0))
    f.append(text((fx + fw + rx) / 2, fy + 160, "Startup: копіювання\n_sidata → _sdata", size=10.5, bold=True, color="#d35400"))

    f.append(line(rx + rw / 2, ry + 234, rx + rw / 2, ry + 248, color="#f39c12", sw=1.8))
    f.append(arrow(rx + rw / 2, ry + 248, rx + rw / 2, ry + 258, color="#f39c12", sw=1.8))

    f.append(line(rx + rw / 2, ry + 326, rx + rw / 2, ry + 312, color="#c0392b", sw=1.8))
    f.append(arrow(rx + rw / 2, ry + 312, rx + rw / 2, ry + 302, color="#c0392b", sw=1.8))

    render(os.path.join(IMG, "linker-memory-map.svg"), W, H, *f)


# ── 2. Проблема D-Cache False Sharing та вирівнювання ALIGN(32) ─────────────
def fig_cache_coherency():
    W, H = 880, 480
    f = []

    f.append(text(W / 2, 28, "Когерентність D-Cache і DMA: проблема False Sharing на рядку кешу 32 байти",
                  size=15, bold=True))

    # ── Варіант А: Без вирівнювання (Аварія / False Sharing) ──
    ax, ay, aw, ah = 50, 60, 780, 180
    f.append(rect(ax, ay, aw, ah, fill="#fdf2e9", stroke="#e67e22", sw=1.6, rx=8))
    f.append(text(ax + 20, ay + 26, "Варіант А: Буфер не вирівняно на 32 байти (False Sharing)", size=13, bold=True, color="#b9770e", anchor="start"))

    # Рядок кешу 1 (32 байти)
    c1_x, c1_y, c1_w, c1_h = ax + 30, ay + 48, 340, 50
    f.append(rect(c1_x, c1_y, c1_w, c1_h, fill="#f9ebea", stroke="#c0392b", sw=1.5, rx=4))
    f.append(rect(c1_x + 10, c1_y + 8, 110, 34, fill="#f5b7b1", stroke="#922b21", sw=1.2, rx=3))
    f.append(text(c1_x + 65, c1_y + 29, "uint32_t flags", size=10, bold=True, color="#922b21"))
    f.append(rect(c1_x + 125, c1_y + 8, 205, 34, fill="#aed6f1", stroke="#2471a3", sw=1.2, rx=3))
    f.append(text(c1_x + 227, c1_y + 29, "dma_rx_buf[0..21]", size=10, bold=True, color="#1b4f72"))
    f.append(text(c1_x + c1_w / 2, c1_y + c1_h + 18, "Рядок кешу 0 (32 байти: адреса 0x20000000..0x2000001F)", size=9.5, color=MUTED))

    # Рядок кешу 2 (32 байти)
    c2_x, c2_y, c2_w, c2_h = ax + 390, ay + 48, 360, 50
    f.append(rect(c2_x, c2_y, c2_w, c2_h, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=4))
    f.append(rect(c2_x + 10, c2_y + 8, 220, 34, fill="#aed6f1", stroke="#2471a3", sw=1.2, rx=3))
    f.append(text(c2_x + 120, c2_y + 29, "dma_rx_buf[22..63]", size=10, bold=True, color="#1b4f72"))
    f.append(rect(c2_x + 235, c2_y + 8, 115, 34, fill="#f5b7b1", stroke="#922b21", sw=1.2, rx=3))
    f.append(text(c2_x + 292, c2_y + 29, "sys_counter", size=10, bold=True, color="#922b21"))
    f.append(text(c2_x + c2_w / 2, c2_y + c2_h + 18, "Рядок кешу 1 (32 байти: адреса 0x20000020..0x2000003F)", size=9.5, color=MUTED))

    f.append(text(ax + aw / 2, ay + 148, "Inval D-Cache після DMA RX знищує зміни у flags; Clean D-Cache затирає нові дані dma_rx_buf!",
                  size=11, bold=True, color="#c0392b"))

    # ── Варіант Б: Ізоляція через ALIGN(32) ──
    bx, by, bw, bh = 50, 260, 780, 190
    f.append(rect(bx, by, bw, bh, fill="#eafaf1", stroke="#27ae60", sw=1.6, rx=8))
    f.append(text(bx + 20, by + 26, "Варіант Б: Буфер вирівняно на ALIGN(32) та кратно 32 байтам (Безпечно)", size=13, bold=True, color="#196f3d", anchor="start"))

    # Рядок кешу 1 (змінні CPU)
    k1_x, k1_y, k1_w, k1_h = bx + 30, by + 48, 220, 50
    f.append(rect(k1_x, k1_y, k1_w, k1_h, fill="#f9ebea", stroke="#c0392b", sw=1.5, rx=4))
    f.append(rect(k1_x + 10, k1_y + 8, 200, 34, fill="#f5b7b1", stroke="#922b21", sw=1.2, rx=3))
    f.append(text(k1_x + 110, k1_y + 29, "Звичайні змінні CPU", size=10, bold=True, color="#922b21"))
    f.append(text(k1_x + k1_w / 2, k1_y + k1_h + 18, "Кеш-рядок 0 (CPU-only)", size=9.5, color=MUTED))

    # Рядки кешу для DMA (вирівняні)
    k2_x, k2_y, k2_w, k2_h = bx + 270, by + 48, 480, 50
    f.append(rect(k2_x, k2_y, k2_w, k2_h, fill="#d4efdf", stroke="#27ae60", sw=1.8, rx=4))
    f.append(rect(k2_x + 10, k2_y + 8, 460, 34, fill="#abebc6", stroke="#1e8449", sw=1.4, rx=3))
    f.append(text(k2_x + 240, k2_y + 29, "dma_rx_buf[64] — строго ізольований у цілих рядках кешу (2 × 32B)", size=10.5, bold=True, color="#145a32"))
    f.append(text(k2_x + k2_w / 2, k2_y + k2_h + 18, "Кеш-рядки 1 та 2 (Тільки DMA: Invalidate та Clean повністю безпечні)", size=9.5, color="#1e8449", bold=True))

    f.append(text(bx + bw / 2, by + 150, "Повна ізоляція: операції кешу над DMA-буфером не зачіпають жодних сусідніх змінних CPU.",
                  size=11, bold=True, color="#1e8449"))

    render(os.path.join(IMG, "dma-cache-alignment.svg"), W, H, *f)


# ── 3. Стек і купа: динаміка росту та запобігання зіткненню ──────────────────
def fig_stack_heap_collision():
    W, H = 840, 520
    f = []

    f.append(text(W / 2, 28, "Організація оперативної пам'яті: зустрічний рух купи та стека й захист _sbrk()",
                  size=15, bold=True))

    # Рамка всієї RAM
    rx, ry, rw, rh = 120, 60, 600, 420
    f.append(rect(rx, ry, rw, rh, fill="#fdfefe", stroke=LINE, sw=2, rx=8))

    # Секції від низу (0x20000000) до верху
    # Нижня частина: .data та .bss
    f.append(fitbox(rx + 15, ry + 15, rw - 30, 46, ".data + .bss (статична пам'ять, межа _ebss / end = 0x20004000)", fill="#e8f8f5", stroke="#16a085", size=11, bold=True))

    # Купа (Heap)
    f.append(fitbox(rx + 15, ry + 70, rw - 30, 75, "Купа (Heap: malloc / new)\nПоточний покажчик: heap_end\nРосте вгору при викликах _sbrk(incr)", fill="#fef9e7", stroke="#f39c12", size=11.5, bold=True))

    # Стрілка росту купи вгору
    f.append(arrow(rx + 80, ry + 150, rx + 80, ry + 195, color="#d35400", sw=2.2))
    f.append(text(rx + 150, ry + 175, "Ріст купи (↑ _sbrk)", size=11, bold=True, color="#d35400", anchor="start"))

    # Вільна зона (Safety Gap)
    f.append(rect(rx + 15, ry + 155, rw - 30, 150, fill="#fbfcfc", stroke="#bdc3c7", sw=1.5, rx=4))
    f.append(text(rx + rw / 2, ry + 215, "Вільна динамічна пам'ять (Unallocated Gap)", size=12, color=MUTED, bold=True))
    f.append(text(rx + rw / 2, ry + 240, "Якщо heap_end + incr перевищить ліміт стека → _sbrk повертає ENOMEM", size=10.5, color="#c0392b", bold=True))

    # Стрілка росту стека вниз
    f.append(arrow(rx + rw - 80, ry + 360, rx + rw - 80, ry + 315, color="#922b21", sw=2.2))
    f.append(text(rx + rw - 150, ry + 340, "Ріст стека (↓ виклики, ISR)", size=11, bold=True, color="#922b21", anchor="end"))

    # Стек (Stack)
    f.append(fitbox(rx + 15, ry + 315, rw - 30, 85, "Стек (Stack: локальні змінні, кадри функцій, переривання)\nПоточний покажчик: SP (MSP / PSP)\nГарантований резерв: _Min_Stack_Size", fill="#fadbd8", stroke="#c0392b", size=11.5, bold=True))

    # Вершина стека
    f.append(line(rx, ry + 400, rx + rw, ry + 400, color="#78281f", sw=2.5))
    f.append(text(rx + rw / 2, ry + 412, "Вершина пам'яті: _estack = ORIGIN(RAM) + LENGTH(RAM) (0x20020000)", size=11, bold=True, color="#78281f"))

    # Маркери адрес ліворуч
    f.append(text(rx - 10, ry + 38, "0x20000000", size=10, color=MUTED, anchor="end"))
    f.append(text(rx - 10, ry + 70, "_ebss / end", size=10, color="#16a085", bold=True, anchor="end"))
    f.append(text(rx - 10, ry + 150, "heap_end", size=10, color="#d35400", bold=True, anchor="end"))
    f.append(text(rx - 10, ry + 315, "SP (поточний)", size=10, color="#922b21", bold=True, anchor="end"))
    f.append(text(rx - 10, ry + 405, "_estack", size=10, color="#78281f", bold=True, anchor="end"))

    render(os.path.join(IMG, "stack-heap-layout.svg"), W, H, *f)


if __name__ == "__main__":
    fig_memory_map()
    fig_cache_coherency()
    fig_stack_heap_collision()
    print("All figures generated successfully.")

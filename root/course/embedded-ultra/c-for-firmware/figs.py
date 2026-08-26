# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. memory-layout: Flash та SRAM секції мікроконтролера ──────────────────
def fig_memory_layout():
    W, H = 960, 520
    p = []

    # Заголовок фігури
    p.append(text(W / 2, 34, "Розподіл пам'яті мікроконтролера: Flash (енергонезалежна) та SRAM (оперативна)", size=16, color=INK, bold=True))

    # Ліва колонка: Flash
    fx, fy, fw, fh = 80, 70, 360, 410
    p.append(rect(fx, fy, fw, fh, fill="#f8fafc", stroke=FIELD, sw=2, rx=8))
    p.append(text(fx + fw / 2, fy + 26, "FLASH ROM (0x08000000)", size=14, color=FIELD, bold=True))
    p.append(text(fx + fw / 2, fy + 44, "Енергонезалежна пам'ять програм і сталих даних", size=11, color=MUTED))

    # Секції Flash
    flash_blocks = [
        (".vector_table", "Вектори скидання та переривань (MSP, Reset, HardFault, ISR)", "#eaf2ec", FIELD, 50),
        (".text", "Машинний код функцій та інструкцій процесора", "#eef6ef", FIELD, 120),
        (".rodata", "Константи, рядкові літерали, статичні таблиці", "#eaf2ec", FIELD, 60),
        (".data (образ)", "Початкові значення ініціалізованих змінних", "#fef3c7", "#d97706", 60),
    ]

    cur_y = fy + 58
    for name, desc, bg_col, border_col, bh in flash_blocks:
        p.append(rect(fx + 16, cur_y, fw - 32, bh, fill=bg_col, stroke=border_col, sw=1.5, rx=6))
        p.append(text(fx + 30, cur_y + 22, name, size=13, color=border_col, bold=True, anchor="start"))
        p.append(text(fx + 30, cur_y + 40, desc, size=10.5, color=INK, anchor="start"))
        cur_y += bh + 8

    # Права колонка: SRAM
    sx, sy, sw, sh = 520, 70, 360, 410
    p.append(rect(sx, sy, sw, sh, fill="#f8fafc", stroke=NEG, sw=2, rx=8))
    p.append(text(sx + sw / 2, sy + 26, "SRAM (0x20000000)", size=14, color=NEG, bold=True))
    p.append(text(sx + sw / 2, sy + 44, "Швидка оперативна пам'ять змінного стану", size=11, color=MUTED))

    # Секції SRAM
    sram_blocks = [
        (".data (активна)", "Глобальні змінні з початковим значенням (копія з Flash)", "#fef3c7", "#d97706", 52),
        (".bss (обнулена)", "Неініціалізовані глобальні та статичні змінні (zeroed)", "#e0f2fe", "#0284c7", 52),
        ("Heap (Купа)", "Динамічна пам'ять (malloc/free) — табу у критичних прошивках", "#fef2f2", POS, 54),
        ("Вільний простір", "Зазор безпеки між купою та стеком (запобігає накладанню)", "#ffffff", "#94a3b8", 48),
        ("Stack (Стек)", "Кадри функцій, локальні змінні, регістри ISR (росте вниз)", "#ede9fe", "#7c3aed", 70),
    ]

    cur_y = sy + 58
    for name, desc, bg_col, border_col, bh in sram_blocks:
        p.append(rect(sx + 16, cur_y, sw - 32, bh, fill=bg_col, stroke=border_col, sw=1.5, rx=6))
        p.append(text(sx + 30, cur_y + 20, name, size=12.5, color=border_col, bold=True, anchor="start"))
        p.append(text(sx + 30, cur_y + 36, desc, size=10, color=INK, anchor="start"))
        cur_y += bh + 6

    # Стрілки росту й копіювання
    # 1. Копіювання .data з Flash у SRAM під час запуску
    p.append(arrow(fx + fw - 16, fy + 338, sx + 16, sy + 84, color="#d97706", sw=2))
    p.append(text((fx + fw + sx) / 2, sy + 185, "startup копіює .data", size=10.5, color="#d97706", bold=True))

    # 2. Напрямки росту купи і стека
    p.append(arrow(sx + sw - 36, sy + 195, sx + sw - 36, sy + 235, color=POS, sw=1.8))
    p.append(text(sx + sw - 42, sy + 215, "↑ ріст", size=9.5, color=POS, anchor="end"))

    p.append(arrow(sx + sw - 36, sy + 380, sx + sw - 36, sy + 340, color="#7c3aed", sw=1.8))
    p.append(text(sx + sw - 42, sy + 360, "↓ ріст", size=9.5, color="#7c3aed", anchor="end"))

    render(os.path.join(OUT, "memory-layout.svg"), W, H, *p,
           title="Розподіл пам'яті прошивки між Flash та SRAM")


# ── 2. volatile-compiler-loop: Поведінка компілятора з volatile і без ─────────
def fig_volatile_loop():
    W, H = 960, 440
    p = []

    p.append(text(W / 2, 32, "Компіляція циклу опитування апаратного регістра: без volatile проти volatile", size=15, color=INK, bold=True))

    # Ліва половина: БЕЗ volatile (баг)
    lx, ly, lw, lh = 50, 60, 410, 350
    p.append(rect(lx, ly, lw, lh, fill="#fef2f2", stroke=POS, sw=2, rx=8))
    p.append(text(lx + lw / 2, ly + 28, "БЕЗ volatile — Фатальна оптимізація", size=14, color=POS, bold=True))

    # Код C
    p.append(rect(lx + 20, ly + 46, lw - 40, 60, fill="#ffffff", stroke="#fca5a5", sw=1.2, rx=4))
    p.append(text(lx + 32, ly + 68, "// C-код опитування апаратного прапорця", size=10, color=MUTED, anchor="start"))
    p.append(text(lx + 32, ly + 90, "while (!(UART_SR & RXNE_FLAG));", size=12, color=INK, bold=True, anchor="start"))

    # Логіка оптимізатора
    p.append(rect(lx + 20, ly + 118, lw - 40, 78, fill="#fff5f5", stroke=POS, sw=1, rx=4))
    p.append(text(lx + 32, ly + 138, "Оптимізатор GCC -O2 міркує:", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(lx + 32, ly + 158, "1. Змінна UART_SR не змінюється всередині циклу.", size=10, color=INK, anchor="start"))
    p.append(text(lx + 32, ly + 176, "2. Читаю регістр один раз у R0 ДО початку циклу.", size=10, color=INK, anchor="start"))

    # Асемблерний результат
    p.append(rect(lx + 20, ly + 208, lw - 40, 120, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=4))
    p.append(text(lx + 32, ly + 230, "LDR   R0, [R1]      ; прочитав UART_SR один раз", size=11, color="#38bdf8", anchor="start"))
    p.append(text(lx + 32, ly + 252, "TST   R0, #0x20     ; перевірив прапорець", size=11, color="#38bdf8", anchor="start"))
    p.append(text(lx + 32, ly + 274, "loop:               ; зациклення на старій копії", size=11, color="#f87171", bold=True, anchor="start"))
    p.append(text(lx + 32, ly + 296, "BEQ   loop          ; зависання назавжди!", size=11, color="#f87171", bold=True, anchor="start"))

    # Права половина: З volatile (коректно)
    rx, ry, rw, rh = 500, 60, 410, 350
    p.append(rect(rx, ry, rw, rh, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    p.append(text(rx + rw / 2, ry + 28, "З volatile — Коректне апаратне опитування", size=14, color=FIELD, bold=True))

    # Код C
    p.append(rect(rx + 20, ry + 46, rw - 40, 60, fill="#ffffff", stroke="#86efac", sw=1.2, rx=4))
    p.append(text(rx + 32, ry + 68, "// C-код із коректним модифікатором", size=10, color=MUTED, anchor="start"))
    p.append(text(rx + 32, ry + 90, "while (!(*(volatile uint32_t *)SR & RXNE));", size=12, color=INK, bold=True, anchor="start"))

    # Логіка оптимізатора
    p.append(rect(rx + 20, ry + 118, rw - 40, 78, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    p.append(text(rx + 32, ry + 138, "Оптимізатор GCC -O2 виконує контракт:", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(rx + 32, ry + 158, "1. volatile забороняє кешувати пам'ять у регістрі.", size=10, color=INK, anchor="start"))
    p.append(text(rx + 32, ry + 176, "2. Кожна ітерація генерує реальну інструкцію LDR.", size=10, color=INK, anchor="start"))

    # Асемблерний результат
    p.append(rect(rx + 20, ry + 208, rw - 40, 120, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=4))
    p.append(text(rx + 32, ry + 230, "loop:               ; початок ітерації", size=11, color="#4ade80", bold=True, anchor="start"))
    p.append(text(rx + 32, ry + 252, "LDR   R0, [R1]      ; щоразу читає шину заліза!", size=11, color="#4ade80", bold=True, anchor="start"))
    p.append(text(rx + 32, ry + 274, "TST   R0, #0x20     ; перевіряє свіжий біт", size=11, color="#38bdf8", anchor="start"))
    p.append(text(rx + 32, ry + 296, "BEQ   loop          ; виходить, щойно байт прибув", size=11, color="#38bdf8", anchor="start"))

    render(os.path.join(OUT, "volatile-compiler-loop.svg"), W, H, *p,
           title="Генерація асемблера для опитування регістрів з volatile та без")


# ── 3. ring-buffer-telemetry: Статичний кільцевий буфер телеметрії ─────────────
def fig_ring_buffer():
    W, H = 960, 450
    p = []

    p.append(text(W / 2, 32, "Статичний lock-free кільцевий буфер телеметрії: схема Single-Producer Single-Consumer", size=15, color=INK, bold=True))

    # Комірки буфера (8 комірок, capacity=8, mask=7)
    cx, cy, r = 360, 240, 130
    import math

    p.append(circle(cx, cy, r + 45, fill="#f8fafc", stroke="#cbd5e1", sw=1.5))
    p.append(circle(cx, cy, r - 45, fill="#ffffff", stroke="#cbd5e1", sw=1.5))

    n_cells = 8
    cell_names = ["0xAA", "0x12", "0x04", "0xFF", "[вільно]", "[вільно]", "[вільно]", "[вільно]"]
    cell_cols = ["#e0f2fe", "#e0f2fe", "#e0f2fe", "#e0f2fe", "#ffffff", "#ffffff", "#ffffff", "#ffffff"]
    cell_borders = ["#0284c7", "#0284c7", "#0284c7", "#0284c7", "#cbd5e1", "#cbd5e1", "#cbd5e1", "#cbd5e1"]

    for i in range(n_cells):
        angle = (i * 2 * math.pi / n_cells) - (math.pi / 2)
        px = cx + r * math.cos(angle)
        py = cy + r * math.sin(angle)

        p.append(circle(px, py, 30, fill=cell_cols[i], stroke=cell_borders[i], sw=1.8))
        p.append(text(px, py - 6, "[%d]" % i, size=9.5, color=MUTED, bold=True))
        p.append(text(px, py + 12, cell_names[i], size=11, color=INK, bold=True))

    # Стрілка head (запис з ISR)
    # head зараз на комірці 4
    h_angle = (4 * 2 * math.pi / n_cells) - (math.pi / 2)
    hx = cx + (r + 75) * math.cos(h_angle)
    hy = cy + (r + 75) * math.sin(h_angle)
    htx = cx + (r + 34) * math.cos(h_angle)
    hty = cy + (r + 34) * math.sin(h_angle)
    p.append(arrow(hx, hy, htx, hty, color=POS, sw=2.4))
    p.append(rect(hx - 80, hy - 14, 75, 28, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(hx - 42, hy + 4, "head = 4 (ISR)", size=10, color=POS, bold=True))

    # Стрілка tail (читання з main)
    # tail зараз на комірці 0
    t_angle = (0 * 2 * math.pi / n_cells) - (math.pi / 2)
    tx = cx + (r + 75) * math.cos(t_angle)
    ty = cy + (r + 75) * math.sin(t_angle)
    ttx = cx + (r + 34) * math.cos(t_angle)
    tty = cy + (r + 34) * math.sin(t_angle)
    p.append(arrow(tx, ty, ttx, tty, color=FIELD, sw=2.4))
    p.append(rect(tx - 45, ty - 34, 90, 26, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(tx, ty - 17, "tail = 0 (main)", size=10, color=FIELD, bold=True))

    # Текстовий блок пояснення праворуч
    bx, by, bw, bh = 600, 75, 320, 335
    p.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(bx + bw / 2, by + 26, "Ключові інваріанти структури", size=13, color=INK, bold=True))

    notes = [
        ("1. Розмір = 2^N (степінь двійки)", "Інкремент без ділення: idx = (idx + 1) & MASK, де MASK = CAPACITY - 1.", FIELD),
        ("2. Виробник (ISR UART):", "Збільшує лише head. Не блокується і не виділяє пам'ять.", POS),
        ("3. Споживач (super-loop):", "Збільшує лише tail. Вичитує кадри та рахує CRC.", FIELD),
        ("4. Стан «Порожній»:", "head == tail (немає нових байтів).", MUTED),
        ("5. Стан «Повний»:", "((head + 1) & MASK) == tail. Резервується одна комірка.", "#d97706"),
    ]

    ny = by + 48
    for h_txt, b_txt, col in notes:
        p.append(text(bx + 16, ny, h_txt, size=11, color=col, bold=True, anchor="start"))
        p.append(mtext(bx + 16, ny + 16, b_txt, size=10, color=INK, anchor="start", lh=1.25))
        ny += 54

    render(os.path.join(OUT, "ring-buffer-telemetry.svg"), W, H, *p,
           title="Статичний кільцевий буфер для зв'язку ISR та основного циклу")


if __name__ == "__main__":
    fig_memory_layout()
    fig_volatile_loop()
    fig_ring_buffer()
    print("OK: figures ->", OUT)

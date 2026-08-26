# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Figure 1: Трансформації оптимізатора (-O0 проти -O2/-O3) ───────────────────
def fig_optimizer_transformations():
    W, H = 940, 420
    p = []

    # Заголовок блоків
    p.append(rect(20, 20, 435, 380, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(rect(485, 20, 435, 380, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))

    # Ліва колонка: Debug (-O0)
    p.append(rect(35, 35, 405, 42, fill="#e2e8f0", stroke=NEG, sw=1.5, rx=6))
    p.append(text(237, 61, "Збірка Debug (-O0): буквальна трансляція", size=13, color=NEG, bold=True))

    debug_items = [
        ("Стек для кожної змінної", "Кожна локальна змінна живе в SRAM; LDR/STR на кожну операцію"),
        ("Повне збереження викликів", "Жодного inlining: кожна функція генерує чесний BL/BLX та пролог"),
        ("Буквальне виконання циклів", "Порожні цикли затримки for (i=0; i<N; i++) крутяться в залізі"),
        ("Строгий порядок пам'яті", "Інструкції йдуть у порядку C-коду; таймінги довгі й повільні"),
        ("Побічний ефект: маскування багів", "Повільний CPU встигає за периферією, RAM занулена зневаджувачем")
    ]

    for i, (title, desc) in enumerate(debug_items):
        yy = 95 + i * 58
        p.append(rect(35, yy, 405, 50, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=5))
        p.append(text(50, yy + 20, title, size=12, color=INK, anchor="start", bold=True))
        p.append(text(50, yy + 38, desc, size=10, color=MUTED, anchor="start"))

    # Права колонка: Release (-O2 / -O3)
    p.append(rect(500, 35, 405, 42, fill="#e2e8f0", stroke=POS, sw=1.5, rx=6))
    p.append(text(702, 61, "Збірка Release (-O2 / -O3): оптимізований конвеєр", size=13, color=POS, bold=True))

    release_items = [
        ("Регістровий розподіл", "Змінні кешуються в R0–R12; RAM не опитується без volatile"),
        ("Агресивний Inlining", "Тіла функцій вбудовуються, межі викликів та кадри стека стираються"),
        ("Викидання мертвого коду (DCE)", "Порожні затримки без side-effects видаляються на 100% (0 нс)"),
        ("Перевпорядкування операцій", "Компілятор переставляє LDR/STR для уникнення конвеєрних пауз"),
        ("Наслідок: оголення дефектів", "Швидкість x10 ламає гонки таймінгів; сміття стека замінює нулі")
    ]

    for i, (title, desc) in enumerate(release_items):
        yy = 95 + i * 58
        p.append(rect(500, yy, 405, 50, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=5))
        p.append(text(515, yy + 20, title, size=12, color=INK, anchor="start", bold=True))
        p.append(text(515, yy + 38, desc, size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "optimizer-transformations.svg"), W, H, *p)


# ── Figure 2: Кешування змінної в регістрі без volatile ────────────────────────
def fig_volatile_register_caching():
    W, H = 940, 440
    p = []

    # Верхній блок: БЕЗ volatile (Пастка)
    p.append(rect(20, 20, 900, 190, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(40, 48, "1. Без volatile: оптимізатор виносить читання за межі циклу", size=13, color=POS, anchor="start", bold=True))

    # CPU & Register
    p.append(rect(50, 70, 240, 120, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(170, 95, "Ядро процесора (CPU)", size=12, color=INK, bold=True))
    p.append(rect(70, 115, 200, 55, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    p.append(text(170, 135, "Регістр R0 = 0", size=12, color=POS, bold=True))
    p.append(text(170, 155, "(закешовано навічно)", size=10, color=MUTED))

    # Loop path in CPU
    p.append(rect(340, 70, 260, 120, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(470, 95, "Асемблерний цикл (-O2)", size=12, color=INK, bold=True))
    p.append(text(470, 120, "LDR  R0, [R1]   ; раз ДО циклу", size=11, color=MUTED))
    p.append(text(470, 140, "loop: CMP  R0, #0", size=11, color=POS, bold=True))
    p.append(text(470, 160, "      BEQ  loop      ; вічний цикл!", size=11, color=POS, bold=True))

    # Bus & Peripheral
    p.append(rect(650, 70, 240, 120, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(770, 95, "Шина AHB / Регістр UART_SR", size=12, color=INK, bold=True))
    p.append(rect(670, 115, 200, 55, fill="#ecfdf5", stroke=FIELD, sw=1, rx=4))
    p.append(text(770, 135, "Апаратний бік: TXE = 1", size=12, color=FIELD, bold=True))
    p.append(text(770, 155, "(CPU сюди більше не дивиться)", size=10, color=MUTED))

    p.append(arrow(310, 142, 335, 142, color=POS, sw=1.8))
    p.append(line(605, 142, 645, 142, color="#94a3b8", sw=1.5, dash="4,4"))
    p.append(text(625, 132, "✖", size=16, color=POS))

    # Нижній блок: З volatile (Правильно)
    p.append(rect(20, 230, 900, 190, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(40, 258, "2. З volatile: кожна ітерація виконує чесний LDR із фізичної шини", size=13, color=FIELD, anchor="start", bold=True))

    # CPU & Register
    p.append(rect(50, 280, 240, 120, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(170, 305, "Ядро процесора (CPU)", size=12, color=INK, bold=True))
    p.append(rect(70, 325, 200, 55, fill="#dcfce7", stroke=FIELD, sw=1, rx=4))
    p.append(text(170, 345, "Регістр R0 оновлюється", size=12, color=FIELD, bold=True))
    p.append(text(170, 365, "LDR на кожному кроці", size=10, color=MUTED))

    # Loop path in CPU
    p.append(rect(340, 280, 260, 120, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(470, 305, "Асемблерний цикл (-O2)", size=12, color=INK, bold=True))
    p.append(text(470, 330, "loop: LDR  R0, [R1]   ; ЧИТАННЯ!", size=11, color=FIELD, bold=True))
    p.append(text(470, 350, "      CMP  R0, #0", size=11, color=INK))
    p.append(text(470, 370, "      BEQ  loop      ; вихід коли TXE=1", size=11, color=INK))

    # Bus & Peripheral
    p.append(rect(650, 280, 240, 120, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(770, 305, "Шина AHB / Регістр UART_SR", size=12, color=INK, bold=True))
    p.append(rect(670, 325, 200, 55, fill="#dcfce7", stroke=FIELD, sw=1, rx=4))
    p.append(text(770, 345, "Апаратний бік: TXE = 1", size=12, color=FIELD, bold=True))
    p.append(text(770, 365, "Прапорець успішно прочитано", size=10, color=MUTED))

    p.append(arrow(310, 350, 335, 350, color=FIELD, sw=1.8))
    p.append(arrow(645, 350, 605, 350, color=FIELD, sw=1.8))
    p.append(text(625, 340, "✓", size=16, color=FIELD))

    render(os.path.join(OUT, "volatile-register-caching.svg"), W, H, *p)


# ── Figure 3: Гонка таймінгів DMA та процесора ─────────────────────────────────
def fig_dma_cpu_race():
    W, H = 940, 380
    p = []

    # Верхня шкала: Debug (-O0)
    p.append(rect(20, 20, 900, 160, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(40, 45, "Debug (-O0): повільний процесор маскує відсутність синхронізації", size=13, color=NEG, anchor="start", bold=True))

    # DMA timeline
    p.append(text(40, 80, "DMA пересилання:", size=11, color=INK, anchor="start", bold=True))
    p.append(rect(180, 65, 320, 26, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    p.append(text(340, 82, "Копіювання 64 байтів у SRAM (120 мкс)", size=10, color=NEG, bold=True))

    # CPU timeline
    p.append(text(40, 125, "CPU обробка коду:", size=11, color=INK, anchor="start", bold=True))
    p.append(rect(180, 110, 360, 26, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    p.append(text(360, 127, "Повільний пролог, стек, розрахунки (-O0: 150 мкс)", size=10, color=MUTED))
    p.append(rect(550, 110, 240, 26, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(670, 127, "Читання буфера (УСПІХ, дані готові)", size=10, color=FIELD, bold=True))

    p.append(line(505, 60, 505, 145, color=FIELD, sw=1.5, dash="3,3"))
    p.append(text(505, 158, "DMA завершився РАНІШЕ читання", size=10, color=FIELD))

    # Нижня шкала: Release (-O2)
    p.append(rect(20, 200, 900, 160, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(40, 225, "Release (-O2): швидкий процесор обганяє DMA і читає сміття (Race Condition)", size=13, color=POS, anchor="start", bold=True))

    # DMA timeline
    p.append(text(40, 260, "DMA пересилання:", size=11, color=INK, anchor="start", bold=True))
    p.append(rect(180, 245, 320, 26, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    p.append(text(340, 262, "Копіювання 64 байтів у SRAM (120 мкс)", size=10, color=NEG, bold=True))

    # CPU timeline
    p.append(text(40, 305, "CPU обробка коду:", size=11, color=INK, anchor="start", bold=True))
    p.append(rect(180, 290, 60, 26, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    p.append(text(210, 307, "-O2 (15 мкс)", size=9, color=MUTED))
    p.append(rect(250, 290, 240, 26, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(370, 307, "Читання буфера (АВАРІЯ: байти 8..63 ще не готові!)", size=10, color=POS, bold=True))

    p.append(line(245, 240, 245, 325, color=POS, sw=1.5, dash="3,3"))
    p.append(text(245, 340, "CPU читає напівпорожній буфер", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "dma-cpu-race.svg"), W, H, *p)


# ── Figure 4: Буфер запису шини та бар'єр пам'яті (DSB) ────────────────────────
def fig_write_buffer_barrier():
    W, H = 940, 400
    p = []

    # Верхній сценарій: БЕЗ DSB
    p.append(rect(20, 20, 900, 170, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(40, 45, "Без бар'єра пам'яті: скидання прапорця застряє в буфері запису", size=13, color=POS, anchor="start", bold=True))

    # Блоки верхнього сценарію
    p.append(rect(40, 65, 170, 70, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=5))
    p.append(text(125, 90, "1. CPU (ISR)", size=11, color=INK, bold=True))
    p.append(text(125, 115, "EXTI->PR = 1;", size=10, color=MUTED))

    p.append(arrow(215, 100, 255, 100, color=POS, sw=1.5))

    p.append(rect(260, 65, 200, 70, fill="#fee2e2", stroke=POS, sw=1.2, rx=5))
    p.append(text(360, 90, "2. Write Buffer (AHB)", size=11, color=POS, bold=True))
    p.append(text(360, 115, "Запис ще в черзі!", size=10, color=POS))

    p.append(arrow(465, 100, 505, 100, color="#94a3b8", sw=1.5))

    p.append(rect(510, 65, 180, 70, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=5))
    p.append(text(600, 90, "3. Периферія EXTI", size=11, color=INK, bold=True))
    p.append(text(600, 115, "PR все ще = 1", size=10, color=POS, bold=True))

    p.append(arrow(695, 100, 735, 100, color=POS, sw=1.5))

    p.append(rect(740, 65, 160, 70, fill="#fee2e2", stroke=POS, sw=1.2, rx=5))
    p.append(text(820, 90, "4. NVIC Контролер", size=11, color=POS, bold=True))
    p.append(text(820, 115, "Повторний ISR шторм!", size=10, color=POS, bold=True))

    p.append(text(470, 160, "CPU повертається з ISR (BX LR), доки периферія не скинула сигнал переривання", size=11, color=POS))

    # Нижній сценарій: З DSB / Dummy Read
    p.append(rect(20, 210, 900, 170, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(40, 235, "З бар'єром __DSB(): процесор очікує завершення транзакції на шині", size=13, color=FIELD, anchor="start", bold=True))

    # Блоки нижнього сценарію
    p.append(rect(40, 255, 170, 70, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=5))
    p.append(text(125, 280, "1. CPU (ISR)", size=11, color=INK, bold=True))
    p.append(text(125, 305, "EXTI->PR = 1; __DSB();", size=10, color=MUTED))

    p.append(arrow(215, 290, 255, 290, color=FIELD, sw=1.5))

    p.append(rect(260, 255, 200, 70, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(360, 280, "2. Write Buffer скинуто", size=11, color=FIELD, bold=True))
    p.append(text(360, 305, "Транзакція завершена", size=10, color=FIELD))

    p.append(arrow(465, 290, 505, 290, color=FIELD, sw=1.5))

    p.append(rect(510, 255, 180, 70, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=5))
    p.append(text(600, 280, "3. Периферія EXTI", size=11, color=INK, bold=True))
    p.append(text(600, 305, "PR очищено в 0", size=10, color=FIELD, bold=True))

    p.append(arrow(695, 290, 735, 290, color=FIELD, sw=1.5))

    p.append(rect(740, 255, 160, 70, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(820, 280, "4. NVIC Контролер", size=11, color=FIELD, bold=True))
    p.append(text(820, 305, "Чистий вихід з ISR", size=10, color=FIELD, bold=True))

    p.append(text(470, 350, "CPU безпечно повертається в основну програму; лінія переривання деактивована", size=11, color=FIELD))

    render(os.path.join(OUT, "write-buffer-barrier.svg"), W, H, *p)


def main():
    fig_optimizer_transformations()
    fig_volatile_register_caching()
    fig_dma_cpu_race()
    fig_write_buffer_barrier()
    print("All figures generated successfully.")

if __name__ == "__main__":
    main()

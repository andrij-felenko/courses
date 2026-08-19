# -*- coding: utf-8 -*-
"""Фігури до статті «Емуляція систем команд: інтерпретація та JIT». Вивід — ./img/*.svg."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

GREEN_FILL = "#eafaf1"
RED_FILL   = "#fdecea"
BLUE_FILL  = "#eaf0fd"
AMBER_FILL = "#fff7e6"
AMBER_STK  = "#c98a00"


# ── Фігура 1: Інтерпретація проти JIT-компіляції ──────────────────────────────
def fig_interpreter_vs_jit():
    W, H = 940, 520
    p = []
    # Заголовки колонок
    p.append(text(235, 45, "Інтерпретація (Fetch-Decode-Execute)", size=15, bold=True))
    p.append(text(705, 45, "Динамічна бінарна трансляція (JIT)", size=15, bold=True))
    # Розділювач
    p.append(line(470, 30, 470, 490, color=MUTED, sw=1.2, dash="5,5"))

    # ── Ліва колонка: Інтерпретатор ──
    p.append(fitbox(85, 75, 300, 46, "1. Вибірка: читання байтів за PC", size=13))
    p.append(arrow(235, 121, 235, 147, color=INK, sw=1.8))

    p.append(fitbox(85, 147, 300, 46, "2. Декодування: виділення опкоду", size=13))
    p.append(arrow(235, 193, 235, 219, color=INK, sw=1.8))

    p.append(fitbox(85, 219, 300, 56, "3. Диспетчер: switch / непрямий стрибок\n(промахи блоку передбачення BTB!)",
                    size=12.5, fill=RED_FILL, stroke=POS, bold=True))
    p.append(arrow(235, 275, 235, 301, color=INK, sw=1.8))

    p.append(fitbox(85, 301, 300, 46, "4. Виконання: функція-обробник команди", size=13))
    p.append(arrow(235, 347, 235, 373, color=INK, sw=1.8))

    p.append(fitbox(85, 373, 300, 46, "5. Оновлення стану: PC = PC + len", size=13))

    # Зворотна стрілка циклу
    p.append(line(85, 396, 45, 396, color=POS, sw=1.8))
    p.append(line(45, 396, 45, 98, color=POS, sw=1.8))
    p.append(arrow(45, 98, 85, 98, color=POS, sw=1.8))
    p.append(text(38, 247, "цикл", size=11, color=POS, anchor="end", bold=True))

    p.append(fitbox(60, 442, 350, 46, "Накладні витрати: 15–50 інструкцій хоста\nна кожну 1 гостьову команду",
                    size=12, fill=FILL, stroke=MUTED))

    # ── Права колонка: JIT / DBT ──
    p.append(fitbox(555, 75, 300, 50, "Гостьовий базовий блок (Basic Block)\n[послідовність до найближчого стрибка]",
                    size=12.5, fill=BLUE_FILL, stroke=NEG))
    p.append(arrow(705, 125, 705, 153, color=INK, sw=1.8))

    p.append(fitbox(555, 153, 300, 54, "JIT-компілятор: трансляція блоку\n[IR → оптимізація → нативний код хоста]",
                    size=12.5, fill=AMBER_FILL, stroke=AMBER_STK, bold=True))
    p.append(arrow(705, 207, 705, 235, color=INK, sw=1.8))

    p.append(fitbox(555, 235, 300, 54, "Кеш трансляцій (Code Cache)\n[збереження скомпільованого коду TB]",
                    size=12.5, fill=GREEN_FILL, stroke=FIELD, bold=True))
    p.append(arrow(705, 289, 705, 317, color=INK, sw=1.8))

    p.append(fitbox(555, 317, 300, 60, "Пряме виконання на залізі хоста\nбез заходу в диспетчер\n(нативна швидкість конвеєра)",
                    size=12.5, fill=GREEN_FILL, stroke=FIELD))

    # Швидкий цикл усередині кешу
    p.append(line(855, 347, 895, 347, color=FIELD, sw=1.8))
    p.append(line(895, 347, 895, 262, color=FIELD, sw=1.8))
    p.append(arrow(895, 262, 855, 262, color=FIELD, sw=1.8))
    p.append(text(902, 305, "зшивання", size=11, color=FIELD, anchor="start", bold=True))

    p.append(fitbox(530, 442, 350, 46, "Накладні витрати: 1.2–2.5 інструкцій хоста\nна 1 гостьову команду в гарячому коді",
                    size=12, fill=FILL, stroke=MUTED))

    render(os.path.join(IMG, "interpreter-vs-jit.svg"), W, H, *p,
           title="Інтерпретація проти динамічної бінарної трансляції")


# ── Фігура 2: Зшивання базових блоків (Block Chaining) ────────────────────────
def fig_block_chaining():
    W, H = 940, 480
    p = []
    p.append(text(470, 35, "Зшивання базових блоків (Block Chaining / Direct Linking)", size=15, bold=True))

    # Контейнер кешу коду
    p.append(rect(40, 60, 860, 390, fill="#fafbfc", stroke=LINE, sw=1.5))
    p.append(text(60, 85, "КЕШ ТРАНСЛЯЦІЙ (Code Cache)", size=12.5, color=MUTED, bold=True, anchor="start"))

    # Блок TB1
    p.append(rect(80, 115, 220, 180, fill=BLUE_FILL, stroke=NEG, sw=1.6))
    p.append(text(190, 140, "Блок TB1 (гостьовий)", size=13, bold=True, color=NEG))
    p.append(text(190, 165, "нативні інструкції хоста", size=11.5, color=INK))
    p.append(text(190, 185, "обчислення результатів", size=11.5, color=INK))
    p.append(text(190, 205, "перевірка умови переходу", size=11.5, color=INK))
    # Хвіст TB1
    p.append(fitbox(95, 230, 190, 48, "Хвіст: jmp [патч-зона]\nTB2 (taken) / TB3 (else)",
                    size=11.5, fill=AMBER_FILL, stroke=AMBER_STK, bold=True))

    # Блок TB2
    p.append(rect(400, 100, 210, 110, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
    p.append(text(505, 125, "Блок TB2 (гілка Taken)", size=13, bold=True, color=FIELD))
    p.append(text(505, 150, "нативні коди цілі переходу", size=11.5, color=INK))
    p.append(text(505, 175, "jmp наступний TB...", size=11.5, color=MUTED))

    # Блок TB3
    p.append(rect(400, 240, 210, 110, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
    p.append(text(505, 265, "Блок TB3 (гілка Fallthrough)", size=13, bold=True, color=FIELD))
    p.append(text(505, 290, "нативні коди продовження", size=11.5, color=INK))
    p.append(text(505, 315, "jmp наступний TB...", size=11.5, color=MUTED))

    # Диспетчер емулятора
    p.append(rect(690, 160, 180, 130, fill=RED_FILL, stroke=POS, sw=1.6))
    p.append(text(780, 190, "Диспетчер", size=14, bold=True, color=POS))
    p.append(text(780, 212, "пошук у хеш-таблиці", size=11.5, color=INK))
    p.append(text(780, 232, "guest_pc → host_ptr", size=11.5, color=INK))
    p.append(text(780, 255, "JIT-компіляція блоку", size=11, color=MUTED))

    # Зв'язки: незашитий стан (через диспетчер)
    p.append(arrow(285, 245, 690, 215, color=POS, sw=1.5))
    p.append(text(485, 222, "1. До зшивання: вихід у диспетчер через трамплін", size=11, color=POS))

    # Зв'язки: зшитий стан (прямий нативний jmp)
    p.append(arrow(285, 235, 400, 155, color=FIELD, sw=2.2))
    p.append(text(310, 180, "Прямий jmp TB2", size=12, color=FIELD, bold=True))

    p.append(arrow(285, 265, 400, 295, color=FIELD, sw=2.2))
    p.append(text(310, 310, "Прямий jmp TB3", size=12, color=FIELD, bold=True))

    # Пояснення внизу
    p.append(fitbox(70, 385, 800, 50,
                    "Емулятор замінює інструкцію виклику диспетчера на прямий нативний стрибок jmp у пам'яті.\n"
                    "Програма переходить між блоками на рівні заліза без виконання жодної інструкції емулятора.",
                    size=12, fill=BG, stroke=MUTED))

    render(os.path.join(IMG, "block-chaining.svg"), W, H, *p,
           title="Зшивання базових блоків у кеші трансляцій")


# ── Фігура 3: Програмний SoftTLB — швидкий і повільний шляхи ─────────────────
def fig_softtlb():
    W, H = 940, 500
    p = []
    p.append(text(470, 35, "Програмний SoftTLB: швидкий шлях проти повільного", size=15, bold=True))

    # Вхід: Гостьова віртуальна адреса
    p.append(fitbox(340, 60, 260, 46, "Гостьова віртуальна адреса (GVA)\n[номер сторінки + зміщення]",
                    size=12.5, fill=BLUE_FILL, stroke=NEG, bold=True))
    p.append(arrow(470, 106, 470, 140, color=INK, sw=1.8))

    # Індексація таблиці
    p.append(fitbox(320, 140, 300, 44, "Індекс SoftTLB = (GVA >> 12) & MASK", size=13))
    p.append(arrow(470, 184, 470, 215, color=INK, sw=1.8))

    # Блок перевірки тегу
    p.append(fitbox(280, 215, 380, 50, "Порівняння тегу в записі SoftTLB:\ntlb[index].tag_vaddr == (GVA & PAGE_MASK) ?",
                    size=12.5, fill=AMBER_FILL, stroke=AMBER_STK, bold=True))

    # Гілка Швидкого шляху (Fast Path) - ліворуч
    p.append(arrow(280, 240, 160, 240, color=FIELD, sw=2.2))
    p.append(arrow(160, 240, 160, 285, color=FIELD, sw=2.2))
    p.append(text(215, 230, "ТАК (Влучання)", size=12, color=FIELD, bold=True))

    p.append(rect(40, 285, 240, 150, fill=GREEN_FILL, stroke=FIELD, sw=1.8))
    p.append(text(160, 310, "ШВИДКИЙ ШЛЯХ (Fast Path)", size=13, bold=True, color=FIELD))
    p.append(text(160, 335, "HVA = GVA + tlb[index].addend", size=12, color=INK, bold=True))
    p.append(text(160, 360, "Прямий доступ: *hva", size=12, color=INK))
    p.append(text(160, 385, "3–5 інструкцій JIT-коду", size=12, color=MUTED))
    p.append(text(160, 410, "Час: ~1–3 такти процесора", size=11.5, color=FIELD, bold=True))

    # Гілка Повільного шляху (Slow Path) - праворуч
    p.append(arrow(660, 240, 780, 240, color=POS, sw=2.2))
    p.append(arrow(780, 240, 780, 285, color=POS, sw=2.2))
    p.append(text(725, 230, "НІ (Промах / Захист)", size=12, color=POS, bold=True))

    p.append(rect(640, 285, 260, 175, fill=RED_FILL, stroke=POS, sw=1.8))
    p.append(text(770, 310, "ПОВІЛЬНИЙ ШЛЯХ (Slow Path)", size=13, bold=True, color=POS))
    p.append(text(770, 332, "Виклик C-хелпера емулятора:", size=11.5, color=INK))
    p.append(text(770, 352, "• Прохід таблиць сторінок MMU", size=11.5, color=INK))
    p.append(text(770, 372, "• Доступ до MMIO-пристроїв", size=11.5, color=INK))
    p.append(text(770, 392, "• Генерація Page Fault / SMC", size=11.5, color=INK))
    p.append(text(770, 415, "• Оновлення запису SoftTLB", size=11.5, color=FIELD, bold=True))
    p.append(text(770, 440, "Час: ~50–300 тактів", size=11.5, color=POS, bold=True))

    render(os.path.join(IMG, "softtlb-path.svg"), W, H, *p,
           title="Трансляція адрес через програмний SoftTLB")


# ── Фігура 4: Ліниве обчислення прапорців стану ────────────────────────────────
def fig_lazy_flags():
    W, H = 920, 460
    p = []
    p.append(text(460, 35, "Ліниве обчислення прапорців стану (Lazy Flags Evaluation)", size=15, bold=True))

    # Ліва частина: Арифметична команда (ADD)
    p.append(rect(50, 70, 260, 240, fill=BLUE_FILL, stroke=NEG, sw=1.6))
    p.append(text(180, 95, "Гостьова команда ADD R1, R2", size=13, bold=True, color=NEG))
    p.append(text(180, 120, "Традиційний підхід:", size=11.5, color=MUTED))
    p.append(text(180, 140, "Обчислення всіх 6 прапорців:", size=11.5, color=POS, bold=True))
    p.append(text(180, 160, "ZF, SF, CF, OF, PF, AF", size=12, color=POS))
    p.append(text(180, 185, "Витрати: 8–12 інструкцій хоста", size=11.5, color=POS))
    p.append(line(70, 200, 290, 200, color=MUTED, sw=1, dash="3,3"))
    p.append(text(180, 220, "Лінивий підхід (Lazy):", size=12, color=FIELD, bold=True))
    p.append(text(180, 245, "Зберегти лише 4 значення", size=12, color=INK))
    p.append(text(180, 270, "в структуру CPUState", size=12, color=INK))
    p.append(text(180, 292, "Витрати: 1–2 інструкції хоста", size=11.5, color=FIELD, bold=True))

    # Центр: Структура CPUState
    p.append(arrow(310, 190, 370, 190, color=INK, sw=2))
    p.append(rect(370, 70, 210, 240, fill=AMBER_FILL, stroke=AMBER_STK, sw=1.8))
    p.append(text(475, 95, "Структура CPUState", size=13.5, bold=True, color=AMBER_STK))
    p.append(text(475, 125, "cc_op  = CC_OP_ADD", size=12, color=INK, bold=True))
    p.append(text(475, 155, "cc_src1 = 0x00000040", size=12, color=INK))
    p.append(text(475, 185, "cc_src2 = 0x00000020", size=12, color=INK))
    p.append(text(475, 215, "cc_dst  = 0x00000060", size=12, color=INK, bold=True))
    p.append(text(475, 250, "Прапорці EFLAGS", size=11.5, color=MUTED))
    p.append(text(475, 270, "НЕ обчислюються!", size=12, color=FIELD, bold=True))
    p.append(text(475, 290, "[відкладено]", size=11.5, color=MUTED))

    # Права частина: Запит прапорця умовним переходом (JE)
    p.append(arrow(580, 190, 640, 190, color=INK, sw=2))
    p.append(rect(640, 70, 230, 240, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
    p.append(text(755, 95, "Умовний перехід JE target", size=13, bold=True, color=FIELD))
    p.append(text(755, 125, "Команда читає лише ZF", size=12, color=INK))
    p.append(text(755, 155, "Обчислення на вимогу:", size=12, color=FIELD, bold=True))
    p.append(fitbox(655, 175, 200, 44, "ZF = (cc_dst == 0)", size=12.5, fill=BG, stroke=FIELD, bold=True))
    p.append(text(755, 240, "Решта 5 прапорців", size=12, color=MUTED))
    p.append(text(755, 260, "(CF, OF, SF, PF, AF)", size=12, color=MUTED))
    p.append(text(755, 285, "так і не обчислюються!", size=12, color=FIELD, bold=True))

    # Нижній банер
    p.append(fitbox(70, 340, 780, 56,
                    "Економія: 85–90% усіх виставлених прапорців ніколи не читаються наступним кодом.\n"
                    "Ліниве обчислення усуває непотрібну роботу й прискорює JIT-код на 30–40%.",
                    size=12, fill=FILL, stroke=MUTED))

    render(os.path.join(IMG, "lazy-flags.svg"), W, H, *p,
           title="Ліниве обчислення прапорців стану процесора")


if __name__ == "__main__":
    fig_interpreter_vs_jit()
    fig_block_chaining()
    fig_softtlb()
    fig_lazy_flags()
    print("Всі фігури згенеровано успішно.")

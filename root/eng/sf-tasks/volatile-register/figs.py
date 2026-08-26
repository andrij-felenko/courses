# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff1"


def fig_compiler_optimizations():
    W, H = 1160, 560
    p = []

    # Лівий блок: Без volatile
    p.append(rect(30, 50, 530, 480, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(295, 80, "Опитування без volatile (Оптимізація LICM)", size=15, bold=True, color=POS))
    p.append(text(295, 102, "Компілятор вважає змінну незмінною в однопотоковому коді", size=12, color=MUTED))

    # C код
    p.append(fitbox(55, 125, 480, 55, "C: while (!(*STATUS_PTR & READY_BIT)) {\n       /* очікування готовності периферії */\n   }", size=12, fill=FILL, stroke=LINE))

    # Дія компілятора
    p.append(fitbox(55, 195, 480, 50, "Оптимізатор (GCC/Clang -O2):\nВиносить читання пам'яті за межі циклу (Loop Invariant)", size=12, fill=RED_FILL, stroke=POS))

    # Згенерований асемблер
    p.append(fitbox(55, 260, 480, 110, "ARM Cortex-M Асемблер:\n  LDR  R0, [R1]      ; Одноразове читання адреси в регістр R0\n  TST  R0, #1        ; Перевірка біта готовності\n.L_loop:\n  BEQ  .L_loop       ; ЗАВИСАННЯ: перевірка R0 без повторного читання!", size=12, fill=RED_FILL, stroke=POS, bold=True))

    # Наслідок у системі
    p.append(fitbox(55, 385, 480, 125, "Апаратний наслідок:\n- Процесор крутиться у нескінченному циклі в регістрах CPU\n- Жодної транзакції на системній шині APB/AHB не відбувається\n- Навіть якщо залізо виставило READY_BIT = 1, CPU цього не побачить", size=12, fill=WARM_FILL, stroke=POS))

    # Правий блок: З volatile
    p.append(rect(600, 50, 530, 480, fill=BG, stroke=MUTED, sw=1.2, rx=10))
    p.append(text(865, 80, "Опитування через volatile uint32_t*", size=15, bold=True, color=FIELD))
    p.append(text(865, 102, "Кожне звернення є обов'язковим сайд-ефектом (Side Effect)", size=12, color=MUTED))

    # C код
    p.append(fitbox(625, 125, 480, 55, "C: while (!(*(volatile uint32_t*)STATUS_PTR & READY_BIT)) {\n       /* очікування готовності периферії */\n   }", size=12, fill=FILL, stroke=LINE))

    # Дія компілятора
    p.append(fitbox(625, 195, 480, 50, "Оптимізатор (GCC/Clang -O2):\nЗаборонено кешувати значення або викидати читання з циклу", size=12, fill=GREEN_FILL, stroke=FIELD))

    # Згенерований асемблер
    p.append(fitbox(625, 260, 480, 110, "ARM Cortex-M Асемблер:\n.L_loop:\n  LDR  R0, [R1]      ; Читання з адреси пам'яті на КОЖНІЙ ітерації!\n  TST  R0, #1        ; Перевірка біта готовності\n  BEQ  .L_loop       ; Перехід на початок циклу з новим LDR", size=12, fill=GREEN_FILL, stroke=FIELD, bold=True))

    # Наслідок у системі
    p.append(fitbox(625, 385, 480, 125, "Апаратний наслідок:\n- На кожній ітерації генерується реальний шинний цикл зчитування\n- Процесор негайно бачить оновлення апаратного статусу залізом\n- Цикл коректно завершується після підняття прапорця", size=12, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'compiler-optimizations-vs-hardware.svg'), W, H, *p,
           title="Оптимізація циклу опитування компілятором: без volatile проти volatile")


def fig_volatile_vs_barriers():
    W, H = 1160, 640
    p = []

    # 1. Рівень компілятора
    p.append(rect(40, 50, 1080, 140, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(fitbox(60, 65, 220, 110, "1. Рівень компілятора\n\nСтатичний аналіз та\nгенерація інструкцій", size=13, fill=BLUE_FILL, stroke=NEG, bold=True))
    p.append(fitbox(300, 65, 390, 110, "Семантика volatile:\n- Забороняє кешування у регістрах CPU\n- Забороняє видалення записів (DSE)\n- Фіксує порядок volatile-доступів в asm\n- НЕ впорядковує звичайні змінні!", size=12, fill=FILL, stroke=LINE))
    p.append(fitbox(710, 65, 390, 110, "Компіляторний бар'єр asm(\"\" ::: \"memory\"):\n- Забороняє компілятору переносити\n  БУДЬ-ЯКІ читання/записи крізь межу\n- Скидає змінні з регістрів у RAM\n- НЕ генерує жодних інструкцій CPU!", size=12, fill=WARM_FILL, stroke=MUTED))

    # Пояснення переходу між рівнями
    p.append(text(580, 212, "Згенерований потік машинних інструкцій (Асемблер)", size=12, color=MUTED, italic=True))
    p.append(arrow(350, 209, 400, 209, color=NEG, sw=1.5))
    p.append(arrow(810, 209, 760, 209, color=NEG, sw=1.5))

    # 2. Рівень процесора та шини
    p.append(rect(40, 230, 1080, 135, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(fitbox(60, 245, 220, 105, "2. Рівень процесора і шини\n\nДинамічне виконання та\nапаратна буферизація", size=13, fill=RED_FILL, stroke=POS, bold=True))
    p.append(fitbox(300, 245, 800, 105, "Апаратна мікроархітектура (Out-of-Order, Store Buffers, Write Buffers, Interconnect):\n- Конвеєр CPU може виконувати шинні запити поза порядком (Out-of-Order)\n- Буфери запису (Store Buffer) затримують потрапляння даних у пам'ять або периферію\n- Інструкції volatile в асемблері НЕ захищають від апаратного перевпорядкування шини!", size=12, fill=RED_FILL, stroke=POS))

    # Пояснення переходу між рівнями
    p.append(text(580, 390, "Керування мікроархітектурою через спеціальні інструкції бар'єрів", size=12, color=FIELD, italic=True))
    p.append(arrow(310, 387, 360, 387, color=FIELD, sw=1.5))
    p.append(arrow(850, 387, 800, 387, color=FIELD, sw=1.5))

    # 3. Апаратні бар'єри пам'яті
    p.append(rect(40, 410, 1080, 200, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(fitbox(60, 425, 220, 170, "3. Апаратні бар'єри (ARM)\n\nКерування конвеєром,\nбуферами запису та\nшинними транзакціями", size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))

    p.append(fitbox(300, 425, 260, 170, "DMB (Data Memory Barrier):\n\nГарантує строгий порядок доступу\nдо пам'яті: усі попередні\nзвернення завершуються перед\nнаступними для пам'яті та DMA.", size=12, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(575, 425, 260, 170, "DSB (Data Synchronization Barrier):\n\nЗупиняє виконання коду CPU\nдо повного завершення всіх\nшинних операцій (скидання буферів\nзапису до MMIO та RAM).", size=12, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(850, 425, 250, 170, "ISB (Instruction Sync Barrier):\n\nСкидає конвеєр інструкцій CPU,\nзмушуючи вибирати код заново\nпісля зміни таблиць векторів\nабо налаштувань MPU.", size=12, fill=GREEN_FILL, stroke=FIELD))

    render(os.path.join(IMG, 'volatile-vs-barriers.svg'), W, H, *p,
           title="Розподіл обов'язків між volatile, компіляторними бар'єрами та апаратними бар'єрами")


def fig_mmio_struct_layout():
    W, H = 1160, 530
    p = []

    # Ліва колонка: Адресна карта пам'яті
    p.append(rect(40, 50, 520, 450, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(300, 78, "Апаратна пам'ять периферійного модуля (MMIO)", size=15, bold=True, color=FIELD))

    # Елементи пам'яті з адресами
    p.append(fitbox(60, 100, 480, 50, "Базова адреса + 0x00: Control Register 1 (CR1)\n32-бітний регістр конфігурації (RW)", size=12, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(60, 160, 480, 50, "Базова адреса + 0x04: Control Register 2 (CR2)\n32-бітний регістр налаштування швидкості (RW)", size=12, fill=GREEN_FILL, stroke=FIELD))
    p.append(fitbox(60, 220, 480, 50, "Базова адреса + 0x08: Status Register (SR)\n32-бітний регістр стану заліза (Тільки читання / RO)", size=12, fill=WARM_FILL, stroke=MUTED))
    p.append(fitbox(60, 280, 480, 50, "Базова адреса + 0x0C .. +0x10: RESERVED\nНездійснені апаратні адреси (Зміщення 8 байтів)", size=12, fill=GREY_FILL, stroke=MUTED))
    p.append(fitbox(60, 340, 480, 50, "Базова адреса + 0x14: Data Register (DR)\n32-бітний регістр передачі/прийому даних (RW)", size=12, fill=BLUE_FILL, stroke=NEG))

    p.append(text(300, 425, "Кожен регістр займає строго 4 байти (32-бітна сітка APB/AHB)", size=12, color=MUTED, italic=True))
    p.append(text(300, 450, "Доступ через байтові операції (LDRB) може викликати Bus Fault!", size=12, color=POS, bold=True))

    # Права колонка: Оголошення C / C++ структури
    p.append(rect(600, 50, 520, 450, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    p.append(text(860, 78, "Оголошення C/C++ структури та накладання вказівника", size=15, bold=True, color=POS))

    code_text = (
        "typedef struct {\n"
        "    volatile uint32_t CR1;        /* +0x00: RW */\n"
        "    volatile uint32_t CR2;        /* +0x04: RW */\n"
        "    const volatile uint32_t SR;   /* +0x08: RO */\n"
        "    uint32_t RESERVED[2];         /* +0x0C..+0x10 */\n"
        "    volatile uint32_t DR;         /* +0x14: RW */\n"
        "} USART_TypeDef;\n\n"
        "#define USART1 ((USART_TypeDef*)0x40013800UL)"
    )
    p.append(fitbox(620, 100, 480, 210, code_text, size=12, fill=FILL, stroke=LINE))

    p.append(fitbox(620, 325, 480, 145, "Правила безпечного проектування:\n1. volatile uint32_t гарантує 32-бітний LDR/STR без кешу\n2. const volatile захищає регістри тільки-для-читання на рівні типів\n3. Масиви RESERVED зберігають апаратні зміщення без packing\n4. Без __attribute__((packed)), щоб компілятор не дробив слова", size=12, fill=WARM_FILL, stroke=MUTED))

    render(os.path.join(IMG, 'mmio-struct-memory-layout.svg'), W, H, *p,
           title="Організація пам'яті MMIO-структури та відображення регістрів периферії")


if __name__ == '__main__':
    fig_compiler_optimizations()
    fig_volatile_vs_barriers()
    fig_mmio_struct_layout()
    print("SVGs successfully generated!")

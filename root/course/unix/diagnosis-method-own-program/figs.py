# -*- coding: utf-8 -*-
"""Генератор векторних ілюстрацій для теми «Метод діагностики власної програми».

Фігури:
1. crash-triage-pipeline.svg — П'ятиетапний інженерний конвеєр локалізації крашів і дефектів пам'яті.
2. signal-trapping-and-core-generation.svg — Архітектурний шлях від апаратного винятку CPU до запису ELF Core Dump.
3. asan-shadow-memory-redzones.svg — Будова тіньової пам'яті та механіка отруєння червоних зон AddressSanitizer.
"""

import os
import sys

# Підключаємо спільний модуль svgkit (4 рівні вгору до scripts/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"


def fig_crash_pipeline():
    W, H = 1000, 480
    frags = []

    # Заголовок
    frags.append(fitbox(200, 15, 600, 36, "Інженерний конвеєр діагностики падінь (Crash Triage Workflow)",
                        size=15, fill=PALE, stroke=INK, sw=1.8, color=INK, bold=True))
    frags.append(text(W / 2, 68, "Послідовний перехід від перехоплення сигналу до точної локалізації дефекту в коді",
                      size=12, color=MUTED, italic=True))

    stages = [
        ("1. Сигнал ядра",
         "Перехоплення збою:\n• SIGSEGV (0x0 / VMA)\n• SIGBUS (mmap/align)\n• SIGABRT (assert/heap)\n• SIGFPE (div by zero)",
         WARM, POS),
        ("2. Core Dump",
         "Фіксація пам'яті:\n• ulimit -c unlimited\n• /proc/.../core_pattern\n• systemd-coredump\n• coredumpctl list/info",
         COOL, NEG),
        ("3. Розбір у GDB",
         "Посмертний аналіз:\n• bt full (стек і кадри)\n• info registers ($rip, $rsp)\n• x/16gx (пам'ять стека)\n• DWARF addr2line",
         PALE, LINE),
        ("4. Санітайзери",
         "Інструментація збірки:\n• -fsanitize=address\n• -fsanitize=undefined\n• Тіньова пам'ять (ASan)\n• Лов use-after-free/OOB",
         GREENF, FIELD),
        ("5. Емуляція",
         "Динамічний аудит:\n• Valgrind Memcheck\n• Пошук неініціалізованих\n• Аналіз закритих бінарників\n• Точний звіт витоків",
         "#fef9e7", "#d4ac0d")
    ]

    box_w = 172
    box_h = 240
    gap = 20
    start_x = 30
    start_y = 95

    for i, (title, desc, fill_c, stroke_c) in enumerate(stages):
        cur_x = start_x + i * (box_w + gap)
        frags.append(fitbox(cur_x, start_y, box_w, box_h, f"{title}\n\n{desc}",
                            size=12, pad=10, fill=fill_c, stroke=stroke_c, sw=1.8))
        if i < len(stages) - 1:
            frags.append(arrow(cur_x + box_w, start_y + box_h / 2,
                               cur_x + box_w + gap, start_y + box_h / 2,
                               color=LINE, sw=1.8))

    # Нижня підсумкова смуга
    bottom_y = start_y + box_h + 30
    frags.append(fitbox(start_x, bottom_y, W - 2 * start_x, 70,
                        "Виробниче середовище (Production):  Core Dumps + systemd-coredump + GDB (нульовий оверхед до краху)\n"
                        "Розробка та тестування (CI / Debug):  ASan + UBSan (швидкі тести) або Valgrind (чорні скриньки)",
                        size=12, fill=PALE, stroke=LINE, sw=1.5, bold=True))

    render(os.path.join(OUT, "crash-triage-pipeline.svg"), W, H, *frags)


def fig_signal_trapping():
    W, H = 1000, 460
    frags = []

    frags.append(fitbox(200, 15, 600, 36, "Шлях аварійного сигналу: від апаратного винятку до ELF Core Dump",
                        size=15, fill=PALE, stroke=INK, sw=1.8, color=INK, bold=True))
    frags.append(text(W / 2, 68, "Механізм взаємодії апаратного забезпечення MMU/CPU, ядра Linux та простору користувача",
                      size=12, color=MUTED, italic=True))

    layers = [
        ("Апаратний шар (CPU / MMU)",
         "• Page Fault (#PF, CR2 = адреса)\n• Division by Zero (#DE)\n• General Protection (#GP)\n• Alignment Check (#AC)",
         WARM, POS, 40, 100, 260, 220),
        ("Простір ядра (Linux Kernel)",
         "• Обробник винятків (do_page_fault)\n• Перевірка дерева VMA процесу\n• Генерація сигналу (force_sig_info)\n• do_coredump() вивантажує стан",
         COOL, NEG, 370, 100, 260, 220),
        ("Служби простору користувача",
         "• /proc/sys/kernel/core_pattern\n• Служба systemd-coredump\n• Збереження стисненого ELF Core\n• База аварій coredumpctl",
         GREENF, FIELD, 700, 100, 260, 220)
    ]

    for title, desc, fill_c, stroke_c, lx, ly, lw, lh in layers:
        frags.append(fitbox(lx, ly, lw, lh, f"{title}\n\n{desc}",
                            size=12, pad=10, fill=fill_c, stroke=stroke_c, sw=1.8))

    # З'єднувальні стрілки між шарами
    frags.append(arrow(300, 180, 370, 180, color=LINE, sw=2))
    frags.append(text(335, 170, "IDT Trap", size=10, color=MUTED, bold=True))

    frags.append(arrow(300, 240, 370, 240, color=LINE, sw=2))
    frags.append(text(335, 230, "SIGSEGV", size=10, color=POS, bold=True))

    frags.append(arrow(630, 210, 700, 210, color=LINE, sw=2))
    frags.append(text(665, 200, "Pipe Core", size=10, color=NEG, bold=True))

    # Нижній блок-результат
    frags.append(fitbox(40, 350, 920, 65,
                        "Результат аварії: процес завершується з кодом (128 + Signal), ядро генерує повний знімок\n"
                        "віртуальної пам'яті (ELF Core), доступний для аналізу в GDB без повторного відтворення збою.",
                        size=12, fill=PALE, stroke=LINE, sw=1.4))

    render(os.path.join(OUT, "signal-trapping-and-core-generation.svg"), W, H, *frags)


def fig_asan_shadow():
    W, H = 1000, 480
    frags = []

    frags.append(fitbox(200, 15, 600, 36, "Архітектура AddressSanitizer: тіньова пам'ять і червоні зони",
                        size=15, fill=PALE, stroke=INK, sw=1.8, color=INK, bold=True))
    frags.append(text(W / 2, 68, "Пряме відображення 8 байтів пам'яті застосунку в 1 байт Shadow Memory: (Addr >> 3) + Offset",
                      size=12, color=MUTED, italic=True))

    # Верхній блок: Пам'ять застосунку
    frags.append(fitbox(50, 100, 900, 110,
                        "Пам'ять застосунку (Application Virtual Memory):\n"
                        "[ Redzone: 16 байтів (0xFA) ] [ Буфер: malloc(24) - 24 байти адресні ] [ Redzone: 16 байтів (0xFA) ]\n"
                        "Помилка Out-of-Bounds: запис за індексом 25 потрапляє в отруєну червону зону (Heap Redzone).",
                        size=12, fill=WARM, stroke=POS, sw=1.6))

    # Стрілка відображення
    frags.append(arrow(500, 210, 500, 255, color=LINE, sw=2))
    frags.append(fitbox(350, 222, 300, 24, "Тіньове стиснення 8:1:  Shadow = (Addr >> 3) + Offset",
                        size=10, fill=PALE, stroke=LINE, sw=1.2, bold=True))

    # Середній блок: Тіньова пам'ять
    frags.append(fitbox(50, 260, 900, 100,
                        "Тіньова пам'ять (Shadow Memory):\n"
                        "[ 0xFA 0xFA ] (отруєно)  │  [ 0x00 0x00 0x00 ] (8+8+8 = 24 байти валідні)  │  [ 0xFA 0xFA ] (отруєно)\n"
                        "Байт 0x00 = усі 8 байтів вільні  •  0x01..0x07 = перші k байтів  •  0xFD = Heap UAF  •  0xF2 = Stack RZ",
                        size=12, fill=COOL, stroke=NEG, sw=1.6))

    # Нижній блок: Інструментована перевірка
    frags.append(fitbox(50, 380, 900, 65,
                        "Швидка компіляторна перевірка перед кожним доступом до пам'яті:\n"
                        "char *shadow = (addr >> 3) + 0x7fff8000;  if (*shadow && *shadow <= (addr & 7)) __asan_report_error();",
                        size=12, fill=GREENF, stroke=FIELD, sw=1.6, bold=True))

    render(os.path.join(OUT, "asan-shadow-memory-redzones.svg"), W, H, *frags)


def main():
    fig_crash_pipeline()
    fig_signal_trapping()
    fig_asan_shadow()
    print("Всі фігури успішно згенеровано в:", OUT)


if __name__ == "__main__":
    main()

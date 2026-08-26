# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми 'cpp-static-init-order'."""

import sys
import os

# 4 рівні вгору до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_init_phases_timeline():
    """Фігура 1: Послідовність фаз ініціалізації та руйнування статичних об'єктів у C++."""
    w, h = 920, 520
    frags = []

    frags.append(text(w / 2, 28, "Фази ініціалізації та руйнування глобальних і статичних об'єктів", size=16, bold=True))

    # --- Блок 1: Статична ініціалізація ---
    frags.append(text(220, 68, "1. СТАТИЧНА ІНІЦІАЛІЗАЦІЯ (компіляція та завантаження)", size=13, bold=True, color=POS))
    
    b_zero = fitbox(30, 85, 380, 75, "Zero Initialization (нульова фаза)\nЗавантажувач обнуляє сегмент .bss\nУсі глобальні байти заповнюються нулями (0x00)", size=11, fill="#fdf2e9", stroke=POS)
    frags.append(b_zero)

    b_const = fitbox(30, 175, 380, 75, "Constant Initialization (константна фаза)\nКомпілятор обчислює constexpr / constinit вирази\nЗначення напряму записуються в секцію .data / .rodata", size=11, fill="#fdf2e9", stroke=POS)
    frags.append(b_const)

    frags.append(arrow(220, 160, 220, 175, color=POS))

    # --- Блок 2: Динамічна ініціалізація ---
    frags.append(text(220, 275, "2. ДИНАМІЧНА ІНІЦІАЛІЗАЦІЯ (до входу в main)", size=13, bold=True, color="#d35400"))
    
    b_dyn = fitbox(30, 290, 380, 95, "Dynamic Initialization (виклики конструкторів)\nCRT обходить список показників .init_array / .ctors\nПорядок всередині одного .cpp: строго зверху вниз\nПорядок між різними .cpp: НЕ ВИЗНАЧЕНИЙ (ризик SIOF!)", size=11, fill="#fef9e7", stroke="#d35400")
    frags.append(b_dyn)

    frags.append(arrow(220, 250, 220, 265, color="#d35400"))

    # --- Центральний перехід: main() ---
    frags.append(rect(430, 235, 80, 50, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(470, 256, "Виконання", size=11, bold=True, color=FIELD))
    frags.append(text(470, 272, "main()", size=12, bold=True, color=FIELD))

    frags.append(arrow(410, 335, 430, 280, color=FIELD))
    frags.append(arrow(510, 280, 530, 335, color=NEG))

    # --- Блок 3: Завершення та руйнування ---
    frags.append(text(710, 275, "3. ДИНАМІЧНЕ РУЙНУВАННЯ (після виходу з main)", size=13, bold=True, color=NEG))
    
    b_destr = fitbox(520, 290, 380, 95, "Static Destruction (виклики деструкторів)\nВиконання обробників стека atexit / __cxa_atexit\nПорядок: строго LIFO (зворотний до завершення конструювання)\nЯкщо порядок конструювання був хибним -> ризик SDOF!", size=11, fill="#ebf5fb", stroke=NEG)
    frags.append(b_destr)

    # Пояснення внизу
    b_summary = fitbox(30, 420, 860, 75, "Критичне правило стандарту C++:\nСтатична ініціалізація завжди передує будь-якій динамічній ініціалізації.\nКонструктори глобальних змінних не мають визначеного порядку між одиницями трансляції.", size=11, fill="#f4f6f8", stroke=LINE)
    frags.append(b_summary)

    out_file = os.path.join(OUT_DIR, "init-phases-timeline.svg")
    render(out_file, w, h, *frags)
    print(f"Згенеровано: {out_file}")


def fig_siof_tu_collision():
    """Фігура 2: Зіткнення двох одиниць трансляції через невизначений порядок лінкера."""
    w, h = 920, 520
    frags = []

    frags.append(text(w / 2, 28, "Анатомія Static Initialization Order Fiasco (SIOF)", size=16, bold=True))

    # Ліва колонка: logger.cpp
    frags.append(text(220, 68, "Одиниця трансляції A (logger.cpp)", size=14, bold=True, color=FIELD))
    b_tu_a = fitbox(30, 85, 380, 110, "class Logger { ... };\n\n// Глобальний об'єкт журналу\nLogger g_logger(\"app.log\");\n\n[Ініціалізатор додається до .init_array]", size=11, fill="#eafaf1", stroke=FIELD)
    frags.append(b_tu_a)

    # Права колонка: network.cpp
    frags.append(text(700, 68, "Одиниця трансляції B (network.cpp)", size=14, bold=True, color=POS))
    b_tu_b = fitbox(510, 85, 380, 110, "class NetworkClient {\n  NetworkClient() {\n    g_logger.log(\"Init net...\"); // ВИКЛИК A!\n  }\n};\nNetworkClient g_net;\n[Ініціалізатор додається до .init_array]", size=11, fill="#fdf2e9", stroke=POS)
    frags.append(b_tu_b)

    # Центральна секція: Лінкер та бінарний файл
    frags.append(fitbox(150, 220, 620, 50, "Лінкування: порядок у секції .init_array залежить від прапорців, порядку файлів та тулчейну", size=12, fill="#f8f9f9", stroke=LINE, bold=True))

    frags.append(arrow(220, 195, 320, 220, color=FIELD))
    frags.append(arrow(700, 195, 600, 220, color=POS))

    # Сценарій краху
    frags.append(text(w / 2, 295, "Сценарій катастрофи під час запуску програми (до main)", size=14, bold=True, color=POS))

    b_step1 = fitbox(30, 315, 410, 85, "Крок 1: CRT першим викликає ініціалізатор B\nКонструктор NetworkClient() починає роботу.\nВін намагається використати g_logger.", size=11, fill="#fadbd8", stroke=POS)
    frags.append(b_step1)

    b_step2 = fitbox(480, 315, 410, 85, "Крок 2: Пам'ять g_logger ще не ініціалізована!\nВнутрішні вказівники та буфери є нулями (0x00) або сміттям.\nВиклик методу log() спричиняє Segmentation Fault або UB.", size=11, fill="#fadbd8", stroke=POS)
    frags.append(b_step2)

    frags.append(arrow(440, 357, 480, 357, color=POS, sw=2.5))

    # Підсумок розв'язання
    b_fix = fitbox(30, 425, 860, 75, "Причина аварії: порядок виклику конструкторів між різними .cpp не гарантується.\nРозв'язок: ідіома Meyer's Singleton (ініціалізація за першим викликом) або C++20 constinit.", size=11, fill="#f4f6f8", stroke=LINE)
    frags.append(b_fix)

    out_file = os.path.join(OUT_DIR, "siof-tu-collision.svg")
    render(out_file, w, h, *frags)
    print(f"Згенеровано: {out_file}")


def fig_schwarz_counter_lifecycle():
    """Фігура 3: Робота лічильника Шварца (Nifty Counter) для гарантії безпеки глобальних ресурсів."""
    w, h = 920, 520
    frags = []

    frags.append(text(w / 2, 28, "Ідіома Nifty Counter (Schwarz Counter) у заголовковому файлі", size=16, bold=True))

    # Верхній блок: Заголовковий файл
    b_hdr = fitbox(160, 55, 600, 75, "Заголовковий файл (наприклад, <iostream> або logger.hpp)\nstatic struct StreamInitializer { StreamInitializer(); ~StreamInitializer(); } s_init;\nКожен .cpp файл, що робить #include, отримує власну статичну копію s_init", size=11, fill="#e8f8f5", stroke=FIELD)
    frags.append(b_hdr)

    # Три одиниці трансляції
    b_tu1 = fitbox(30, 155, 260, 65, "Одиниця трансляції 1\n#include <iostream>\n-> static s_init (TU1)", size=11, fill="#f4f6f8", stroke=LINE)
    b_tu2 = fitbox(330, 155, 260, 65, "Одиниця трансляції 2\n#include <iostream>\n-> static s_init (TU2)", size=11, fill="#f4f6f8", stroke=LINE)
    b_tu3 = fitbox(630, 155, 260, 65, "Одиниця трансляції 3\n#include <iostream>\n-> static s_init (TU3)", size=11, fill="#f4f6f8", stroke=LINE)

    frags.append(b_tu1)
    frags.append(b_tu2)
    frags.append(b_tu3)

    frags.append(arrow(300, 130, 160, 155, color=FIELD))
    frags.append(arrow(460, 130, 460, 155, color=FIELD))
    frags.append(arrow(620, 130, 760, 155, color=FIELD))

    # Логіка лічильника під час запуску
    b_startup = fitbox(30, 245, 410, 145, "Стадія запуску (конструктори s_init):\n1. Перший TU: ++g_count (стає 1)\n   -> Виклик placement new для cout/logger\n2. Другий TU: ++g_count (стає 2)\n   -> Об'єкт уже готовий, пропуск\n3. Третій TU: ++g_count (стає 3)\n   -> Об'єкт уже готовий, пропуск", size=11, fill="#eafaf1", stroke=FIELD)
    frags.append(b_startup)

    # Логіка лічильника під час завершення
    b_teardown = fitbox(480, 245, 410, 145, "Стадія завершення (деструктори s_init):\n1. Третій TU: --g_count (стає 2)\n   -> Ресурс залишається активним\n2. Другий TU: --g_count (стає 1)\n   -> Ресурс залишається активним\n3. Перший TU: --g_count (стає 0)\n   -> Явний виклик деструктора ресурсу", size=11, fill="#ebf5fb", stroke=NEG)
    frags.append(b_teardown)

    # Підсумок
    b_result = fitbox(30, 415, 860, 85, "Гарантія безпеки:\nОскільки s_init оголошено у заголовку, його конструктор виконується ДО будь-яких глобальних змінних у цьому .cpp файлі.\nРесурс знищується лише тоді, коли останній .cpp файл завершить роботу.", size=11, fill="#fef9e7", stroke="#d35400")
    frags.append(b_result)

    out_file = os.path.join(OUT_DIR, "schwarz-counter-lifecycle.svg")
    render(out_file, w, h, *frags)
    print(f"Згенеровано: {out_file}")


if __name__ == "__main__":
    fig_init_phases_timeline()
    fig_siof_tu_collision()
    fig_schwarz_counter_lifecycle()

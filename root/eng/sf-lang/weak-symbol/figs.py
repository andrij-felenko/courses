# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми 'weak-symbol'."""

import os
import sys

# 4 рівні вгору до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_linker_symbol_resolution_precedence():
    """Фігура 1: Матриця пріоритетів лінкера при вирішенні конфліктів символів (Strong vs Weak)."""
    w, h = 920, 530
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Матриця пріоритетів розв'язання символів у лінкері (ELF Symbol Resolution)", size=16, bold=True))

    # Ліва колонка: Визначення символів (Definitions)
    frags.append(rect(30, 60, 415, 445, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(rect(30, 60, 415, 38, fill="#eaeded", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(237, 84, "Комбінація визначень (Definitions)", size=14, bold=True, color=INK))

    def_cases = [
        ("1. Сильний + Сильний (Strong + Strong)", "Два звичайні глобальні символи (STB_GLOBAL)\nз однаковим ім'ям у різних .o файлах", "#fadbd8", POS, "ПОМИЛКА: multiple definition", POS),
        ("2. Сильний + Слабкий (Strong + Weak)", "Один звичайний символ (STB_GLOBAL)\nта один або кілька слабких (STB_WEAK)", "#d5f5e3", FIELD, "УСПІХ: Обирається Сильний", FIELD),
        ("3. Слабкий + Слабкий (Weak + Weak)", "Кілька слабких символів (STB_WEAK)\nі жодного сильного визначення", "#fef9e7", "#b7950b", "УСПІХ: Обирається перший слабкий", "#b7950b"),
    ]

    y_cur = 110
    for title, desc, bg_color, border_color, result_text, res_color in def_cases:
        frags.append(rect(45, y_cur, 385, 114, fill="#ffffff", stroke=border_color, sw=1.5, rx=6))
        frags.append(text(60, y_cur + 22, title, size=12, bold=True, color=border_color, anchor="start"))
        frags.append(mtext(60, y_cur + 48, desc, size=11, color=INK, anchor="start", lh=1.3))
        frags.append(rect(55, y_cur + 76, 365, 28, fill=bg_color, stroke=border_color, sw=1, rx=4))
        frags.append(text(237, y_cur + 94, result_text, size=11, bold=True, color=res_color))
        y_cur += 128

    # Права колонка: Посилання на символи (References)
    frags.append(rect(475, 60, 415, 445, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(rect(475, 60, 415, 38, fill="#eaeded", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(682, 84, "Слабкі та сильні посилання (References)", size=14, bold=True, color=INK))

    ref_cases = [
        ("4. Сильне посилання без визначення", "Виклик extern void func(void);\nВизначення func відсутнє в усіх .o та .a", "#fadbd8", POS, "ПОМИЛКА: undefined reference", POS),
        ("5. Слабке посилання без визначення", "Оголошення extern __attribute__((weak))\nВизначення відсутнє в таблиці символів", "#ebf5fb", NEG, "УСПІХ: Адреса символу = 0 (NULL)", NEG),
        ("6. Слабке посилання + Визначення", "Оголошення extern __attribute__((weak))\nВизначення присутнє в одному з .o файлів", "#d5f5e3", FIELD, "УСПІХ: Адреса символу = &func", FIELD),
    ]

    y_cur = 110
    for title, desc, bg_color, border_color, result_text, res_color in ref_cases:
        frags.append(rect(490, y_cur, 385, 114, fill="#ffffff", stroke=border_color, sw=1.5, rx=6))
        frags.append(text(505, y_cur + 22, title, size=12, bold=True, color=border_color, anchor="start"))
        frags.append(mtext(505, y_cur + 48, desc, size=11, color=INK, anchor="start", lh=1.3))
        frags.append(rect(500, y_cur + 76, 365, 28, fill=bg_color, stroke=border_color, sw=1, rx=4))
        frags.append(text(682, y_cur + 94, result_text, size=11, bold=True, color=res_color))
        y_cur += 128

    render(os.path.join(OUT_DIR, "linker-symbol-resolution-precedence.svg"), w, h, *frags)


def fig_weak_isr_override_pattern():
    """Фігура 2: Архітектурний шаблон перевизначення обробників переривань через слабкі псевдоніми."""
    w, h = 940, 520
    frags = []

    frags.append(text(w / 2, 26, "Перевизначення обробників переривань: від сирцевих модулів до таблиці векторів", size=16, bold=True))

    # --- Колонка 1: Вхідні модулі (Ліворуч, x: 30..290) ---
    frags.append(rect(30, 60, 260, 440, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(rect(30, 60, 260, 36, fill="#eaeded", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(160, 83, "1. Вхідні модулі коду", size=13, bold=True))

    # Верхній блок: startup.c (Слабкі аліаси)
    frags.append(rect(42, 105, 236, 180, fill="#fef9e7", stroke="#b7950b", sw=1.5, rx=6))
    frags.append(text(160, 125, "startup.c (Слабкі символи)", size=11, bold=True, color="#7d6608"))
    st_text = (
        "void Default_Handler(void) {\n"
        "    while (1) {} // Зависання\n"
        "}\n"
        "// Слабкі псевдоніми (weak, alias):\n"
        "• SysTick_Handler (weak)\n"
        "• USART1_IRQHandler (weak)\n"
        "• TIM2_IRQHandler (weak)"
    )
    frags.append(fitbox(50, 135, 220, 140, st_text, size=10.5, fill="#ffffff", stroke="#d4ac0d", color=INK))

    # Нижній блок: main.c / uart.c (Сильні визначення)
    frags.append(rect(42, 300, 236, 185, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(160, 320, "main.c / uart.c (Сильні)", size=11, bold=True, color=FIELD))
    user_text = (
        "// main.c (Сильний символ)\n"
        "void SysTick_Handler(void) {\n"
        "    g_ticks++;\n"
        "}\n"
        "// uart.c (Сильний символ)\n"
        "void USART1_IRQHandler(void) {\n"
        "    rx_byte(USART1->RDR);\n"
        "}\n"
        "// TIM2 НЕ перевизначено!"
    )
    frags.append(fitbox(50, 330, 220, 145, user_text, size=10.5, fill="#ffffff", stroke=FIELD, color=INK))

    # --- Колонка 2: Робота лінкера (По центру, x: 330..600) ---
    frags.append(rect(330, 60, 270, 440, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(rect(330, 60, 270, 36, fill="#eaeded", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(465, 83, "2. Розв'язання імен лінкером", size=13, bold=True))

    res_slots = [
        ("SysTick_Handler", "Є СИЛЬНЕ у main.c\n-> Обирається main.c\nСлабке з startup відкинуто", "#d5f5e3", FIELD),
        ("USART1_IRQHandler", "Є СИЛЬНЕ у uart.c\n-> Обирається uart.c\nСлабке з startup відкинуто", "#d5f5e3", FIELD),
        ("TIM2_IRQHandler", "Сильного НЕМАЄ\n-> Береться слабке\nВеде на Default_Handler", "#fadbd8", POS),
    ]

    ry = 115
    for s_name, s_desc, s_bg, s_col in res_slots:
        frags.append(rect(342, ry, 246, 110, fill="#ffffff", stroke=s_col, sw=1.5, rx=6))
        frags.append(text(465, ry + 22, s_name, size=11.5, bold=True, color=s_col))
        frags.append(mtext(465, ry + 52, s_desc, size=10.5, color=INK, lh=1.3))
        ry += 125

    # --- Колонка 3: Таблиця векторів у Flash (Праворуч, x: 640..910) ---
    frags.append(rect(640, 60, 270, 440, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(rect(640, 60, 270, 36, fill="#eaeded", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(775, 83, "3. Flash ROM (.isr_vector)", size=13, bold=True))

    vec_rows = [
        ("0x08000000: Initial SP", "0x20010000 (RAM Top)", "#eaeded", INK),
        ("0x08000004: Reset_Handler", "0x08000100 (&Reset)", "#eaeded", INK),
        ("0x0800003C: SysTick_Handler", "0x08000450 (&main.c)", "#d5f5e3", FIELD),
        ("0x08000058: USART1_IRQHandler", "0x08000620 (&uart.c)", "#d5f5e3", FIELD),
        ("0x08000060: TIM2_IRQHandler", "0x08000120 (&Default)", "#fadbd8", POS),
        ("0x08000120: Default_Handler", "b 0x08000120 (Trap loop)", "#fcedec", POS),
    ]

    vy = 108
    for v_title, v_val, v_bg, v_col in vec_rows:
        frags.append(rect(652, vy, 246, 54, fill=v_bg, stroke=v_col, sw=1.2, rx=5))
        frags.append(text(775, vy + 20, v_title, size=11, bold=True, color=v_col))
        frags.append(text(775, vy + 40, v_val, size=10.5, color=INK))
        vy += 62

    # --- Стрілки між колонками (без перетинання тексту) ---
    # З Колонки 1 в Колонку 2
    frags.append(arrow(292, 195, 328, 170, color=LINE, sw=1.5))
    frags.append(arrow(292, 390, 328, 295, color=FIELD, sw=1.8))
    frags.append(arrow(292, 230, 328, 420, color=POS, sw=1.5))

    # З Колонки 2 в Колонку 3
    frags.append(arrow(602, 170, 638, 258, color=FIELD, sw=1.8))
    frags.append(arrow(602, 295, 638, 320, color=FIELD, sw=1.8))
    frags.append(arrow(602, 420, 638, 382, color=POS, sw=1.8))

    render(os.path.join(OUT_DIR, "weak-isr-override-pattern.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_linker_symbol_resolution_precedence()
    fig_weak_isr_override_pattern()
    print("Всі фігури згенеровано успішно у ./img/")

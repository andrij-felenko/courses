# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми Software DSM та механізм Twin-and-Diff."""

import os
import sys

# Підключаємо svgkit з scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle,
    textbox, fitbox, INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG, FONT
)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_false_sharing():
    """Ілюстрація конфлікту гранулярності: сторінка 4096 байтів проти змінних 8 байтів."""
    w, h = 820, 360
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Конфлікт гранулярності в розподіленій пам'яті", size=16, bold=True))

    # Спільна віртуальна сторінка 4096 байтів
    frags.append(rect(60, 60, 700, 70, fill="#f8fafc", stroke=LINE, sw=1.8, rx=6))
    frags.append(text(410, 82, "Віртуальна сторінка пам'яті (4096 байтів / 4 КБ)", size=13, bold=True, color=INK))

    # Змінна A
    frags.append(rect(90, 95, 140, 26, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(160, 112, "Змінна A (8 байтів)", size=11, bold=True, color=POS))

    # Змінна B
    frags.append(rect(590, 95, 140, 26, fill="#dbeafe", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(660, 112, "Змінна B (8 байтів)", size=11, bold=True, color=NEG))

    # Решта байтів сторінки
    frags.append(text(410, 112, "Незаймані байти сторінки (4080 байтів)", size=11, color=MUTED, italic=True))

    # Ліва колонка: Протокол Single-Writer
    frags.append(rect(60, 160, 335, 175, fill="#fff1f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(227, 185, "Протокол одного записувача (Single-Writer)", size=12, bold=True, color=POS))
    frags.append(line(75, 195, 380, 195, color=POS, sw=1.0, dash="3,3"))
    frags.append(mtext(227, 218, [
        "• Вузол 1 змінює A → відбирає виключні права",
        "• Сторінка на Вузлі 2 знеправлюється (PROT_NONE)",
        "• Вузол 2 змінює B → вимагає сторінку назад",
        "• Наслідок: пінг-понг усієї 4 КБ сторінки",
        "• Мережа перевантажена передачею 4096 Б"
    ], size=11, color=INK, lh=1.4))

    # Права колонка: Протокол Twin-and-Diff
    frags.append(rect(425, 160, 335, 175, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(592, 185, "Протокол Twin-and-Diff (Multiple-Writer)", size=12, bold=True, color=FIELD))
    frags.append(line(440, 195, 745, 195, color=FIELD, sw=1.0, dash="3,3"))
    frags.append(mtext(592, 218, [
        "• Вузли 1 і 2 пишуть одночасно у власні копії",
        "• Перший запис створює тіньовий двійник (Twin)",
        "• Під час синхронізації рахується різниця (Diff)",
        "• Мережею передаються лише байти змін (16 Б)",
        "• Дві зміни безконфліктно зливаються"
    ], size=11, color=INK, lh=1.4))

    # Стрілки від змінних до блоків
    frags.append(arrow(160, 125, 160, 155, color=POS, sw=1.5))
    frags.append(arrow(660, 125, 660, 155, color=FIELD, sw=1.5))

    render(os.path.join(IMG_DIR, 'false-sharing-granularity.svg'), w, h, *frags)


def fig_twin_diff_lifecycle():
    """Життєвий цикл сторінки та створення двійника (Twin) і різниці (Diff)."""
    w, h = 860, 480
    frags = []

    frags.append(text(w / 2, 26, "Чотири фази життєвого циклу сторінки в протоколі Twin-and-Diff", size=16, bold=True))

    # Фаза 1: Стан PROT_READ
    frags.append(rect(40, 60, 175, 110, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(127, 82, "1. Чистий стан", size=12, bold=True))
    frags.append(rect(55, 95, 145, 30, fill="#e2e8f0", stroke=MUTED, sw=1.0, rx=4))
    frags.append(text(127, 114, "Сторінка: PROT_READ", size=11, bold=True, color=INK))
    frags.append(text(127, 150, "Читання локальне (1 нс)", size=10, color=MUTED))

    # Стрілка 1 -> 2: Write Store
    frags.append(arrow(215, 115, 255, 115, color=POS, sw=1.8))
    frags.append(text(235, 102, "Store", size=10, bold=True, color=POS))

    # Фаза 2: Сторінкове виключення і створення Twin
    frags.append(rect(260, 60, 245, 190, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(382, 82, "2. Перехоплення запису", size=12, bold=True, color="#92400e"))
    frags.append(mtext(382, 106, [
        "MMU генерує Page Fault",
        "Обробник SIGSEGV:"
    ], size=10, color=INK, lh=1.3))

    # Twin і робоча сторінка
    frags.append(rect(275, 135, 105, 45, fill="#fde68a", stroke="#b45309", sw=1.2, rx=4))
    frags.append(text(327, 152, "Тіньовий Twin", size=10, bold=True))
    frags.append(text(327, 168, "memcpy(twin, p)", size=9, color=MUTED))

    frags.append(rect(390, 135, 105, 45, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(442, 152, "Робоча сторінка", size=10, bold=True, color=NEG))
    frags.append(text(442, 168, "PROT_READ|WRITE", size=9, color=NEG))

    frags.append(text(382, 202, "mprotect() розблоковує запис", size=10, bold=True, color=INK))
    frags.append(text(382, 220, "Команда повторюється процесором", size=9, color=MUTED))

    # Стрілка 2 -> 3
    frags.append(arrow(505, 115, 545, 115, color=FIELD, sw=1.8))
    frags.append(text(525, 102, "Виконання", size=10, bold=True, color=FIELD))

    # Фаза 3: Прямі модифікації в DRAM
    frags.append(rect(550, 60, 270, 130, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(685, 82, "3. Нативне виконання епохи", size=12, bold=True, color=FIELD))
    frags.append(mtext(685, 108, [
        "Потоки вільно виконують тисячі",
        "операцій читання та запису в DRAM",
        "з нульовими програмними накладними",
        "витратами на інструкцію (0 % оверхед)."
    ], size=10, color=INK, lh=1.3))

    # Стрілка 3 -> 4 (вниз і вліво)
    frags.append(arrow(685, 195, 685, 270, color=LINE, sw=1.8))
    frags.append(text(730, 235, "Точка синхронізації\n(Release / Barrier)", size=10, bold=True, color=INK))

    # Фаза 4: Генерація Diff і завершення епохи
    frags.append(rect(80, 280, 700, 180, fill="#f8fafc", stroke=LINE, sw=1.8, rx=6))
    frags.append(text(430, 305, "4. Обчислення компактного Diff і скидання прав", size=13, bold=True, color=INK))

    # Порівняння слів
    frags.append(rect(110, 325, 180, 50, fill="#fde68a", stroke="#b45309", sw=1.2, rx=4))
    frags.append(text(200, 345, "Twin (стан до змін)", size=11, bold=True))
    frags.append(text(200, 362, "[ 0x00, 0x00, 0x12, 0x34 ... ]", size=9, color=MUTED))

    frags.append(text(305, 352, "VS", size=12, bold=True, color=POS))

    frags.append(rect(325, 325, 180, 50, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(415, 345, "Робоча сторінка (після)", size=11, bold=True, color=NEG))
    frags.append(text(415, 362, "[ 0x00, 0x00, 0x99, 0x34 ... ]", size=9, color=NEG))

    frags.append(arrow(510, 350, 550, 350, color=FIELD, sw=1.8))

    # Журнал Diff
    frags.append(rect(555, 325, 200, 50, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(655, 345, "Diff-запис: [Зсув=2, Байт=0x99]", size=10, bold=True, color=FIELD))
    frags.append(text(655, 362, "Розмір: 6 байтів замість 4096", size=9, color=MUTED))

    # Нижній статус у фазі 4
    frags.append(text(430, 400, "1. Звільнення пам'яті Twin → 2. mprotect(p, PROT_READ) → 3. Передача Diff у мережу", size=11, bold=True, color=INK))
    frags.append(text(430, 425, "Сторінка повертається у Фазу 1 для захисту від майбутніх записів нової епохи.", size=10, color=MUTED, italic=True))

    render(os.path.join(IMG_DIR, 'twin-diff-lifecycle.svg'), w, h, *frags)


def fig_multi_writer_merge():
    """Безконфліктне злиття паралельних Diff-пакетів від незалежних вузлів."""
    w, h = 840, 420
    frags = []

    frags.append(text(w / 2, 26, "Безконфліктне злиття змін (Multi-Writer Reconciliation)", size=16, bold=True))

    # Базова сторінка на початку епохи
    frags.append(rect(310, 55, 220, 60, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(420, 75, "Базова спільна сторінка P₀", size=12, bold=True))
    frags.append(text(420, 95, "Байт [0..7] = 0x00 | Байт [100..107] = 0x00", size=10, color=MUTED))

    # Стрілки розгалуження до Вузла 1 та Вузла 2
    frags.append(arrow(360, 115, 200, 165, color=POS, sw=1.6))
    frags.append(arrow(480, 115, 640, 165, color=NEG, sw=1.6))

    # Вузол 1 (ліворуч)
    frags.append(rect(60, 170, 280, 105, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(200, 190, "Вузол 1: Запис у Байти [0..7]", size=11, bold=True, color=POS))
    frags.append(text(200, 210, "Зміна: Байт [0..7] := 0xAA", size=10, color=INK))
    frags.append(rect(80, 225, 240, 35, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(200, 246, "Diff₁: {Зсув: 0, Довжина: 8, Дані: 0xAA}", size=10, bold=True, color=POS))

    # Вузол 2 (праворуч)
    frags.append(rect(500, 170, 280, 105, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(640, 190, "Вузол 2: Запис у Байти [100..107]", size=11, bold=True, color=NEG))
    frags.append(text(640, 210, "Зміна: Байт [100..107] := 0xBB", size=10, color=INK))
    frags.append(rect(520, 225, 240, 35, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(640, 246, "Diff₂: {Зсув: 100, Довжина: 8, Дані: 0xBB}", size=10, bold=True, color=NEG))

    # Стрілки злиття до Вузла 3
    frags.append(arrow(200, 280, 350, 325, color=POS, sw=1.6))
    frags.append(arrow(640, 280, 490, 325, color=NEG, sw=1.6))

    # Вузол 3 (Одержувач / Бар'єр злиття)
    frags.append(rect(180, 325, 480, 85, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(420, 345, "Вузол 3: Накладання різниць (Diff Merging)", size=12, bold=True, color=FIELD))
    frags.append(text(420, 368, "apply_diff(P₀, Diff₁) → Байт [0..7] = 0xAA (збережено)", size=10, color=INK))
    frags.append(text(420, 388, "apply_diff(P₀, Diff₂) → Байт [100..107] = 0xBB (збережено)", size=10, color=INK))

    render(os.path.join(IMG_DIR, 'multi-writer-merge.svg'), w, h, *frags)


def fig_lazy_diff_accumulation():
    """Ланцюжки різниць та інтервальні векторні позначки в Lazy Release Consistency."""
    w, h = 840, 380
    frags = []

    frags.append(text(w / 2, 26, "Інтервальні часові мітки та накопичення Diff у Lazy RC (TreadMarks)", size=16, bold=True))

    # Вузол A
    frags.append(rect(50, 60, 220, 180, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(160, 82, "Вузол A (Власник замка L)", size=12, bold=True))
    frags.append(rect(65, 98, 190, 35, fill="#fee2e2", stroke=POS, sw=1.0, rx=4))
    frags.append(text(160, 118, "Інтервал 1: Запис у P₁ → Diff_A1", size=10, color=POS, bold=True))
    frags.append(rect(65, 140, 190, 35, fill="#fee2e2", stroke=POS, sw=1.0, rx=4))
    frags.append(text(160, 160, "Інтервал 2: Запис у P₂ → Diff_A2", size=10, color=POS, bold=True))
    frags.append(rect(65, 182, 190, 45, fill="#f1f5f9", stroke=MUTED, sw=1.0, rx=4))
    frags.append(text(160, 198, "Векторний час: [2, 0, 0]", size=10, bold=True))
    frags.append(text(160, 215, "Виклик: lock_release(L)", size=10, color=POS, bold=True))

    # Стрілка передачі замка до Вузла B
    frags.append(arrow(275, 205, 560, 205, color=LINE, sw=2.0))
    frags.append(text(420, 190, "Мережне повідомлення: Захоплення замка L", size=11, bold=True, color=INK))
    frags.append(text(420, 222, "Передається лише векторний годинник [2, 0, 0] (без самих даних сторінок!)", size=10, color=MUTED))

    # Вузол B
    frags.append(rect(570, 60, 220, 180, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(680, 82, "Вузол B (Отримувач замка L)", size=12, bold=True))
    frags.append(rect(585, 98, 190, 45, fill="#dbeafe", stroke=NEG, sw=1.0, rx=4))
    frags.append(text(680, 115, "Локальний час: [0, 1, 0]", size=10, bold=True))
    frags.append(text(680, 132, "Виклик: lock_acquire(L)", size=10, color=NEG, bold=True))
    frags.append(rect(585, 150, 190, 75, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=4))
    frags.append(text(680, 168, "Знеправлення сторінок:", size=10, bold=True, color="#92400e"))
    frags.append(text(680, 185, "P₁ → PROT_NONE", size=9, color=INK))
    frags.append(text(680, 200, "P₂ → PROT_NONE", size=9, color=INK))
    frags.append(text(680, 215, "(Diff запитуються лише при Fault)", size=9, color=MUTED, italic=True))

    # Нижня частина: Відкладений запит Diff при зверненні
    frags.append(rect(50, 260, 740, 100, fill="#f0fdf4", stroke=FIELD, sw=1.6, rx=6))
    frags.append(text(420, 282, "Ліниве підтягування різниці (Lazy Diff Fetch on Demand)", size=12, bold=True, color=FIELD))
    frags.append(mtext(420, 308, [
        "1. Вузол B звертається до P₁ → спрацьовує Read Fault на сторінці PROT_NONE.",
        "2. Вузол B виявляє за вектором брак інтервалу 1 від Вузла A → надсилає запит лише на Diff_A1.",
        "3. Вузол A надсилає компактний Diff_A1 → Вузол B накладає його й відновлює PROT_READ.",
        "4. Якщо Вузол B ніколи не звертається до P₂, сторінка P₂ взагалі не передається мережею!"
    ], size=10, color=INK, lh=1.35))

    render(os.path.join(IMG_DIR, 'lazy-diff-accumulation.svg'), w, h, *frags)


if __name__ == '__main__':
    fig_false_sharing()
    fig_twin_diff_lifecycle()
    fig_multi_writer_merge()
    fig_lazy_diff_accumulation()
    print("Figures generated successfully.")

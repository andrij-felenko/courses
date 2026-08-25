# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми bytes-characters-and-line-endings.
Запуск: python figs.py
Вивід у ./img/*.svg
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_kernel_opaque_bytes():
    """Фігура 1: Межа між ядром (неінтерпретовані байти) і простором користувача (локаль, символи)."""
    w, h = 880, 480
    frags = []

    # Заголовок / розділення просторів
    frags.append(rect(20, 20, 410, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(225, 52, "Простір користувача (User Space)", size=16, color=INK, bold=True))
    frags.append(text(225, 74, "Інтерпретація: LC_CTYPE, libc, термінал", size=12, color=MUTED))

    frags.append(rect(450, 20, 410, 440, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(655, 52, "Ядро Linux / Unix (Kernel Space)", size=16, color=INK, bold=True))
    frags.append(text(655, 74, "Неінтерпретований потік байтів (Opaque Bytes)", size=12, color=MUTED))

    # Секція користувача
    frags.append(rect(40, 100, 370, 75, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(225, 125, "Прикладна програма / Текстовий редактор", size=13, color=INK, bold=True))
    frags.append(text(225, 148, "Рядок: \"Звіт.txt\" (4 символи Unicode)", size=13, color=NEG, bold=True))
    frags.append(text(225, 165, "Символи: U+0417, U+0432, U+0456, U+0442 ...", size=11, color=MUTED))

    frags.append(arrow(225, 175, 225, 205, color=LINE, sw=1.5))

    frags.append(rect(40, 205, 370, 85, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(225, 228, "Бібліотека C (glibc / musl) & LC_CTYPE", size=13, color=INK, bold=True))
    frags.append(text(225, 250, "Кодування UTF-8: перетворення у байти", size=12, color=INK))
    frags.append(text(225, 272, "Результат: 12 байтів (D0 97 D0 B2 D1 96 D1 82 2E 74 78 74)", size=11, color=POS, bold=True))

    frags.append(arrow(225, 290, 225, 320, color=LINE, sw=1.5))

    frags.append(rect(40, 320, 370, 120, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(225, 342, "Термінал / Емулятор (pty / rendering)", size=13, color=INK, bold=True))
    frags.append(text(225, 364, "Декодує потік UTF-8, шукає гліфи у шрифті", size=11, color=INK))
    frags.append(text(225, 385, "Обчислює ширину колонок (wcwidth)", size=11, color=INK))
    frags.append(text(225, 406, "Розпізнає керуючі коди: \\n (LF), \\r (CR), ESC[...m", size=11, color=MUTED))
    frags.append(text(225, 427, "Виводить растрові символи на екранну сітку", size=11, color=FIELD, bold=True))

    # Стрілка між просторами (системний виклик)
    frags.append(arrow(410, 245, 450, 245, color=POS, sw=2))
    frags.append(text(430, 235, "open()", size=11, color=POS, bold=True))

    # Секція ядра
    frags.append(rect(470, 100, 370, 140, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(655, 125, "Системні виклики та VFS", size=13, color=INK, bold=True))
    frags.append(text(655, 148, "Отримує char* — масив невідомих байтів", size=12, color=INK))
    frags.append(rect(485, 160, 340, 40, fill="#fef2f2", stroke=POS, sw=1, rx=4))
    frags.append(text(655, 178, "Ядро знає лише 2 особливі байти:", size=11, color=POS, bold=True))
    frags.append(text(655, 194, "0x00 (NUL) — кінець рядка; 0x2F (/) — роздільник шляху", size=11, color=POS))
    frags.append(text(655, 226, "Решта 254 байтів (0x01..0xFF) — сліпий вантаж", size=11, color=MUTED))

    frags.append(arrow(655, 240, 655, 275, color=LINE, sw=1.5))

    frags.append(rect(470, 275, 370, 85, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(655, 300, "Файлові системи (ext4, XFS, Btrfs)", size=13, color=INK, bold=True))
    frags.append(text(655, 323, "Зберігає імена у каталогах як сирі октети", size=12, color=INK))
    frags.append(text(655, 345, "Вміст файлу — лінійний масив байтів без схеми", size=11, color=MUTED))

    frags.append(arrow(655, 360, 655, 395, color=LINE, sw=1.5))

    frags.append(rect(470, 395, 370, 45, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(655, 422, "Дисковий драйвер / Блоковий рівень (NVMe, SSD)", size=12, color=MUTED))

    render(os.path.join(IMG_DIR, "kernel-opaque-bytes.svg"), w, h, *frags)


def fig_utf8_byte_layout():
    """Фігура 2: Бітова структура UTF-8, маркери довжини та байти продовження."""
    w, h = 940, 430
    frags = []

    frags.append(text(470, 30, "Структура кодування UTF-8: самосинхронізація та діапазони", size=15, color=INK, bold=True))

    rows = [
        ("1 байт (ASCII)", "U+0000 .. U+007F", [("0", "#27ae60", 36), ("x x x x x x x", "#e2e8f0", 94)], "7 бітів даних"),
        ("2 байти", "U+0080 .. U+07FF", [("1 1 0", "#2457d6", 48), ("x x x x x", "#e2e8f0", 76), ("1 0", "#c0392b", 38), ("x x x x x x", "#e2e8f0", 86)], "11 бітів даних"),
        ("3 байти", "U+0800 .. U+FFFF", [("1 1 1 0", "#2457d6", 58), ("x x x x", "#e2e8f0", 68), ("1 0", "#c0392b", 38), ("x x x x x x", "#e2e8f0", 86), ("1 0", "#c0392b", 38), ("x x x x x x", "#e2e8f0", 86)], "16 бітів даних"),
        ("4 байти", "U+10000 .. U+10FFFF", [("1 1 1 1 0", "#2457d6", 64), ("x x x", "#e2e8f0", 56), ("1 0", "#c0392b", 36), ("x x x x x x", "#e2e8f0", 82), ("1 0", "#c0392b", 36), ("x x x x x x", "#e2e8f0", 82), ("1 0", "#c0392b", 36), ("x x x x x x", "#e2e8f0", 82)], "21 біт даних"),
    ]

    y = 65
    for title, codepoint_range, blocks, total_bits in rows:
        frags.append(rect(20, y, 900, 68, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
        frags.append(text(90, y + 26, title, size=13, color=INK, bold=True))
        frags.append(text(90, y + 48, codepoint_range, size=11, color=MUTED))

        bx = 175
        for bit_str, fill_col, bw in blocks:
            stroke_col = POS if fill_col == "#c0392b" else (NEG if fill_col == "#2457d6" else (FIELD if fill_col == "#27ae60" else LINE))
            txt_col = "#ffffff" if fill_col in ["#c0392b", "#2457d6", "#27ae60"] else INK
            frags.append(rect(bx, y + 14, bw, 40, fill=fill_col, stroke=stroke_col, sw=1, rx=4))
            frags.append(text(bx + bw / 2, y + 38, bit_str, size=11, color=txt_col, bold=True))
            bx += bw + 5

        frags.append(rect(785, y + 18, 120, 32, fill="#f8fafc", stroke=LINE, sw=1, rx=4))
        frags.append(text(845, y + 39, total_bits, size=11, color=INK, bold=True))
        y += 78

    # Легенда універсальних властивостей
    frags.append(rect(20, 360, 900, 52, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(circle(50, 386, 6, fill="#27ae60", stroke="#27ae60"))
    frags.append(text(150, 390, "0xxxxxxx — 7-бітний ASCII", size=11, color=INK))

    frags.append(circle(270, 386, 6, fill="#2457d6", stroke="#2457d6"))
    frags.append(text(410, 390, "11...0 — стартовий байт задає довжину", size=11, color=INK))

    frags.append(circle(570, 386, 6, fill="#c0392b", stroke="#c0392b"))
    frags.append(text(735, 390, "10xxxxxx — байти-продовження (самосинхронізація)", size=11, color=INK))

    render(os.path.join(IMG_DIR, "utf8-byte-layout.svg"), w, h, *frags)


def fig_line_ending_mechanics():
    """Фігура 3: Механіка CR vs LF (телетайп) та пастка shebang в ядрі Linux."""
    w, h = 880, 440
    frags = []

    # Ліва половина: Фізична модель телетайпа
    frags.append(rect(20, 20, 410, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(225, 48, "Механіка телетайпа (Teletype Model 33)", size=14, color=INK, bold=True))

    # CR блок
    frags.append(rect(40, 75, 370, 95, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    frags.append(text(225, 98, "CR (Carriage Return) — \\r (0x0D, 13)", size=13, color=POS, bold=True))
    frags.append(text(225, 120, "Повертає друкуючу каретку в крайню ліву позицію", size=11, color=INK))
    frags.append(text(225, 138, "Курсор стає в стовпець 0 без переходу на новий рядок", size=11, color=MUTED))
    frags.append(text(225, 156, "У терміналі: наступний текст перетирає старий!", size=11, color=POS))

    # LF блок
    frags.append(rect(40, 185, 370, 85, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(225, 208, "LF (Line Feed) — \\n (0x0A, 10)", size=13, color=NEG, bold=True))
    frags.append(text(225, 230, "Прокручує паперовий валик на один рядок вниз", size=11, color=INK))
    frags.append(text(225, 250, "Позиція каретки по горизонталі не змінюється", size=11, color=MUTED))

    # Підсумок систем
    frags.append(rect(40, 285, 370, 120, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(225, 310, "Розподіл системних стандартів:", size=12, color=INK, bold=True))
    frags.append(text(225, 335, "Unix / Linux: тільки LF (\\n) — економія 1 байта", size=12, color=FIELD, bold=True))
    frags.append(text(225, 357, "CP/M, MS-DOS, Windows: пара CRLF (\\r\\n)", size=12, color=POS, bold=True))
    frags.append(text(225, 382, "Драйвер TTY (ONLCR): видає \\r\\n на екран при виводі \\n", size=11, color=MUTED))

    # Права половина: Пастка shebang у ядрі Linux
    frags.append(rect(450, 20, 410, 400, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(655, 48, "Пастка Shebang (#!/bin/sh\\r\\n)", size=14, color=POS, bold=True))

    frags.append(rect(470, 75, 370, 80, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(655, 98, "Скрипт створено у Windows (CRLF):", size=12, color=INK, bold=True))
    frags.append(text(655, 120, "# ! / b i n / s h \\r \\n", size=13, color=POS, bold=True))
    frags.append(text(655, 140, "Байти: 23 21 2F 62 69 6E 2F 73 68 0D 0A", size=11, color=MUTED))

    frags.append(arrow(655, 155, 655, 185, color=POS, sw=1.5))

    frags.append(rect(470, 185, 370, 100, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    frags.append(text(655, 208, "Парсер ядра (fs/binfmt_script.c)", size=12, color=INK, bold=True))
    frags.append(text(655, 230, "Шукає кінець рядка до байта \\n (0x0A)", size=11, color=INK))
    frags.append(text(655, 250, "Символ \\r стає частиною імені файлу!", size=11, color=POS, bold=True))
    frags.append(text(655, 270, "Шлях інтерпретатора: \"/bin/sh\\r\" (9 байтів)", size=12, color=POS, bold=True))

    frags.append(arrow(655, 285, 655, 315, color=POS, sw=1.5))

    frags.append(rect(470, 315, 370, 90, fill="#fee2e2", stroke=POS, sw=1.2, rx=6))
    frags.append(text(655, 338, "Результат системного виклику execve():", size=12, color=POS, bold=True))
    frags.append(text(655, 360, "Файл \"/bin/sh\\r\" на диску не існує!", size=11, color=INK))
    frags.append(text(655, 385, "Помилка: ENOENT (No such file or directory)", size=12, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "line-ending-mechanics.svg"), w, h, *frags)


def fig_nul_separated_pipeline():
    """Фігура 4: Безпека конвеєрів — розбиття за \\n проти NUL-байта (0x00)."""
    w, h = 880, 420
    frags = []

    frags.append(text(440, 30, "Безпека конвеєрів: \\n (LF) проти NUL (0x00) як роздільника", size=15, color=INK, bold=True))

    # Верхній сценарій: Вразливий конвеєр (поділ за \\n або пробілом)
    frags.append(rect(30, 55, 820, 160, fill="#fff1f2", stroke="#fecdd3", sw=1.5, rx=8))
    frags.append(text(140, 80, "Небезпечний конвеєр (за замовчуванням):", size=13, color=POS, bold=True))
    frags.append(text(460, 80, "find . -name \"*.log\" | xargs rm", size=13, color=INK, bold=True))

    frags.append(rect(50, 100, 240, 60, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(170, 122, "Файл на файловій системі:", size=11, color=MUTED))
    frags.append(text(170, 144, "\"my report 2026.log\"", size=12, color=INK, bold=True))

    frags.append(arrow(290, 130, 350, 130, color=POS, sw=1.5))
    frags.append(text(320, 120, "потік", size=10, color=MUTED))

    frags.append(rect(350, 100, 210, 60, fill="#ffffff", stroke=POS, sw=1, rx=4))
    frags.append(text(455, 122, "xargs розбиває за пробілами:", size=11, color=POS, bold=True))
    frags.append(text(455, 144, "3 окремі аргументи", size=12, color=POS, bold=True))

    frags.append(arrow(560, 130, 620, 130, color=POS, sw=1.5))

    frags.append(rect(620, 100, 210, 60, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    frags.append(text(725, 122, "rm шукає три файли:", size=11, color=POS, bold=True))
    frags.append(text(725, 144, "\"my\", \"report\", \"2026.log\"", size=11, color=POS))

    frags.append(text(440, 195, "Катастрофа: випадкове видалення не тих файлів або помилки No such file", size=11, color=POS, bold=True))

    # Нижній сценарій: Безпечний NUL-конвеєр
    frags.append(rect(30, 230, 820, 165, fill="#f0fdf4", stroke="#bbf7d0", sw=1.5, rx=8))
    frags.append(text(130, 255, "Безпечний конвеєр (NUL-поділ):", size=13, color=FIELD, bold=True))
    frags.append(text(460, 255, "find . -name \"*.log\" -print0 | xargs -0 rm", size=13, color=INK, bold=True))

    frags.append(rect(50, 275, 240, 60, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    frags.append(text(170, 297, "Файл із пробілами чи \\n:", size=11, color=MUTED))
    frags.append(text(170, 319, "\"my report 2026.log\\0\"", size=12, color=FIELD, bold=True))

    frags.append(arrow(290, 305, 350, 305, color=FIELD, sw=1.5))
    frags.append(text(320, 295, "\\0 потік", size=10, color=FIELD))

    frags.append(rect(350, 275, 210, 60, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    frags.append(text(455, 297, "xargs -0 ділить ТІЛЬКИ по \\0:", size=11, color=FIELD, bold=True))
    frags.append(text(455, 319, "Пробіли та \\n зберігаються", size=11, color=INK))

    frags.append(arrow(560, 305, 620, 305, color=FIELD, sw=1.5))

    frags.append(rect(620, 275, 210, 60, fill="#dcfce7", stroke=FIELD, sw=1, rx=4))
    frags.append(text(725, 297, "rm отримує точний шлях:", size=11, color=FIELD, bold=True))
    frags.append(text(725, 319, "argv[1] = \"my report 2026.log\"", size=11, color=FIELD, bold=True))

    frags.append(text(440, 375, "NUL (0x00) — єдиний байт, заборонений в іменах файлів Unix, гарантує цілісність", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "nul-separated-pipeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_kernel_opaque_bytes()
    fig_utf8_byte_layout()
    fig_line_ending_mechanics()
    fig_nul_separated_pipeline()
    print("All figures generated successfully.")

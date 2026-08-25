# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми 'Текст як універсальний інтерфейс'."""

import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_record_and_field_separators():
    """Фігура 1: Анатомія рядкового потоку (Record Separators та Field Delimiters)."""
    w, h = 900, 480
    frags = []

    # Заголовок / шапка схеми
    frags.append(rect(20, 20, 860, 440, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Секція 1: Потік записів з роздільником \n (LF)
    frags.append(text(40, 52, "1. Поділ на записи: Record Separator (LF / 0x0A або NUL / 0x00)", size=14, bold=True, color="#1e293b", anchor="start"))
    
    # Запис 1
    frags.append(rect(40, 70, 360, 50, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(text(220, 100, "Запис 1: root:x:0:0:root:/root:/bin/bash", size=13, color="#1e3a8a", bold=True))
    
    # Роздільник запису 1 (\n)
    frags.append(rect(405, 70, 45, 50, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(427.5, 95, "\\n", size=13, color="#92400e", bold=True))
    frags.append(text(427.5, 110, "0x0A", size=9, color="#b45309"))

    # Запис 2
    frags.append(rect(455, 70, 360, 50, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(text(635, 100, "Запис 2: daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin", size=12, color="#1e3a8a", bold=True))

    # Роздільник запису 2 (\n)
    frags.append(rect(820, 70, 45, 50, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(842.5, 95, "\\n", size=13, color="#92400e", bold=True))
    frags.append(text(842.5, 110, "0x0A", size=9, color="#b45309"))

    # Стрілка вниз до розбору полів
    frags.append(arrow(220, 125, 220, 165, color="#3b82f6", sw=2))
    frags.append(text(230, 150, "Декомпозиція запису на поля", size=11, color="#2563eb", anchor="start", italic=True))

    # Секція 2: Поділ запису на поля (Field Delimiters)
    frags.append(text(40, 185, "2. Внутрішня структура запису: Field Delimiters (розділювачі полів ':')", size=14, bold=True, color="#1e293b", anchor="start"))

    # Колонки / поля запису root
    fields = [
        ("root", "1. Username", 70),
        ("x", "2. Passwd", 65),
        ("0", "3. UID", 55),
        ("0", "4. GID", 55),
        ("root", "5. GECOS", 75),
        ("/root", "6. Home Dir", 100),
        ("/bin/bash", "7. Shell", 110)
    ]

    curr_x = 40
    for i, (val, label, width) in enumerate(fields):
        # Блок поля
        frags.append(rect(curr_x, 205, width, 55, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=4))
        frags.append(text(curr_x + width / 2, 230, val, size=13, color="#14532d", bold=True))
        frags.append(text(curr_x + width / 2, 250, label, size=9, color="#15803d"))
        curr_x += width

        # Розділювач полів ':' між блоками
        if i < len(fields) - 1:
            frags.append(rect(curr_x + 3, 215, 22, 35, fill="#fef2f2", stroke="#dc2626", sw=1.2, rx=3))
            frags.append(text(curr_x + 14, 237, ":", size=14, color="#991b1b", bold=True))
            curr_x += 28

    # Секція 3: Порівняння конвенцій роздільників
    frags.append(text(40, 295, "3. Основні конвенції роздільників у середовищі Unix / Linux", size=14, bold=True, color="#1e293b", anchor="start"))

    conventions = [
        ("Двокрапка ':'", "/etc/passwd, PATH", "Фіксований текстовий реєстр; заборона двокрапки в даних"),
        ("Табуляція '\\t'", "cut, TSV, paste", "Однозначний машинний роздільник; зберігає пробіли у значеннях"),
        ("Пробіли (whitespace)", "ps, ls, df, fstab", "Табличний вигляд для людини; об'єднання послідовних пробілів"),
        ("Нульовий байт '\\0'", "find -print0 | xargs -0", "Абсолютна безпека; NUL неможливий у шляхах POSIX")
    ]

    box_w = 195
    for i, (name, files, desc) in enumerate(conventions):
        bx = 40 + i * 215
        frags.append(rect(bx, 315, box_w, 130, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
        frags.append(text(bx + box_w / 2, 337, name, size=12, bold=True, color="#0f172a"))
        frags.append(rect(bx + 15, 348, box_w - 30, 20, fill="#e2e8f0", stroke="#94a3b8", sw=0.8, rx=3))
        frags.append(text(bx + box_w / 2, 362, files, size=10, color="#334155"))
        
        # Дворядковий опис
        lines = [desc[:28], desc[28:56]] if len(desc) > 28 else [desc]
        for line_idx, line_str in enumerate(lines):
            frags.append(text(bx + box_w / 2, 388 + line_idx * 16, line_str.strip(), size=9, color="#64748b"))

    render(os.path.join(OUT_DIR, "record-and-field-separators.svg"), w, h, *frags)


def fig_pipeline_paradigms_comparison():
    """Фігура 2: Порівняння парадигм міжпроцесного зв'язку (Unix Text vs PowerShell Objects vs JSON Lines)."""
    w, h = 920, 480
    frags = []

    frags.append(rect(20, 20, 880, 440, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))

    # Стовпець 1: Unix Text Pipeline
    col1_x = 40
    col_w = 265
    frags.append(rect(col1_x, 40, col_w, 400, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(rect(col1_x, 40, col_w, 40, fill="#334155", stroke="#1e293b", sw=1.5, rx=6))
    frags.append(text(col1_x + col_w / 2, 65, "Unix: Сирий потік тексту", size=13, bold=True, color="#ffffff"))

    # Вміст 1
    frags.append(rect(col1_x + 15, 95, col_w - 30, 60, fill="#eff6ff", stroke="#3b82f6", sw=1, rx=4))
    frags.append(text(col1_x + col_w / 2, 118, "ps aux | grep nginx", size=11, bold=True, color="#1e40af"))
    frags.append(text(col1_x + col_w / 2, 138, "Байтовий потік (stream of bytes)", size=10, color="#3b82f6"))

    frags.append(arrow(col1_x + col_w / 2, 160, col1_x + col_w / 2, 185, color="#64748b", sw=1.5))

    frags.append(rect(col1_x + 15, 190, col_w - 30, 95, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(col1_x + col_w / 2, 210, "Парсинг тексту фільтрами", size=11, bold=True, color="#0f172a"))
    frags.append(text(col1_x + 25, 230, "• awk '{print $2}'", size=10, color="#334155", anchor="start"))
    frags.append(text(col1_x + 25, 250, "• Немає метаданих про типи", size=10, color="#dc2626", anchor="start"))
    frags.append(text(col1_x + 25, 270, "• Проблема пробілів та локалей", size=10, color="#dc2626", anchor="start"))

    frags.append(rect(col1_x + 15, 300, col_w - 30, 125, fill="#f0fdf4", stroke="#86efac", sw=1, rx=4))
    frags.append(text(col1_x + col_w / 2, 322, "Переваги та сумісність", size=11, bold=True, color="#166534"))
    frags.append(text(col1_x + 25, 342, "+ Будь-яка мова (C, Python, Go)", size=10, color="#15803d", anchor="start"))
    frags.append(text(col1_x + 25, 362, "+ Читабельність людиною (cat, less)", size=10, color="#15803d", anchor="start"))
    frags.append(text(col1_x + 25, 382, "+ Десятиліття стабільності API", size=10, color="#15803d", anchor="start"))
    frags.append(text(col1_x + 25, 402, "+ O(1) споживання пам'яті", size=10, color="#15803d", anchor="start"))

    # Стовпець 2: PowerShell Object Pipeline
    col2_x = 328
    frags.append(rect(col2_x, 40, col_w, 400, fill="#f8fafc", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(rect(col2_x, 40, col_w, 40, fill="#0369a1", stroke="#075985", sw=1.5, rx=6))
    frags.append(text(col2_x + col_w / 2, 65, "PowerShell: Об'єктний конвеєр", size=13, bold=True, color="#ffffff"))

    # Вміст 2
    frags.append(rect(col2_x + 15, 95, col_w - 30, 60, fill="#f0f9ff", stroke="#0ea5e9", sw=1, rx=4))
    frags.append(text(col2_x + col_w / 2, 118, "Get-Process | Where CPU -gt 10", size=11, bold=True, color="#0369a1"))
    frags.append(text(col2_x + col_w / 2, 138, "Живі об'єкти .NET (PSObject)", size=10, color="#0284c7"))

    frags.append(arrow(col2_x + col_w / 2, 160, col2_x + col_w / 2, 185, color="#0284c7", sw=1.5))

    frags.append(rect(col2_x + 15, 190, col_w - 30, 95, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(col2_x + col_w / 2, 210, "Типізовані властивості", size=11, bold=True, color="#0f172a"))
    frags.append(text(col2_x + 25, 230, "• $proc.Id, $proc.WorkingSet64", size=10, color="#334155", anchor="start"))
    frags.append(text(col2_x + 25, 250, "• Жодного парсингу рядків", size=10, color="#16a34a", anchor="start"))
    frags.append(text(col2_x + 25, 270, "• Безпека типів (int, DateTime)", size=10, color="#16a34a", anchor="start"))

    frags.append(rect(col2_x + 15, 300, col_w - 30, 125, fill="#fff1f2", stroke="#fecdd3", sw=1, rx=4))
    frags.append(text(col2_x + col_w / 2, 322, "Накладні витрати та межі", size=11, bold=True, color="#9f1239"))
    frags.append(text(col2_x + 25, 342, "− Потребує важкого .NET CLR", size=10, color="#be123c", anchor="start"))
    frags.append(text(col2_x + 25, 362, "− Важко передати в C/Rust утиліти", size=10, color="#be123c", anchor="start"))
    frags.append(text(col2_x + 25, 382, "− Серіалізація при міжхостовому зв'язку", size=10, color="#be123c", anchor="start"))
    frags.append(text(col2_x + 25, 402, "− Високі витрати пам'яті на об'єкт", size=10, color="#be123c", anchor="start"))

    # Стовпець 3: Structured JSON / ndjson Pipeline
    col3_x = 615
    frags.append(rect(col3_x, 40, col_w, 400, fill="#f8fafc", stroke="#7c3aed", sw=1.5, rx=6))
    frags.append(rect(col3_x, 40, col_w, 40, fill="#6d28d9", stroke="#5b21b6", sw=1.5, rx=6))
    frags.append(text(col3_x + col_w / 2, 65, "JSON Lines: Структурований потік", size=13, bold=True, color="#ffffff"))

    # Вміст 3
    frags.append(rect(col3_x + 15, 95, col_w - 30, 60, fill="#faf5ff", stroke="#a855f7", sw=1, rx=4))
    frags.append(text(col3_x + col_w / 2, 118, "docker events --format '{{json .}}'", size=10, bold=True, color="#6b21a8"))
    frags.append(text(col3_x + col_w / 2, 138, "Рядки валідного JSON (ndjson)", size=10, color="#7e22ce"))

    frags.append(arrow(col3_x + col_w / 2, 160, col3_x + col_w / 2, 185, color="#7c3aed", sw=1.5))

    frags.append(rect(col3_x + 15, 190, col_w - 30, 95, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(col3_x + col_w / 2, 210, "Обробка селекторами (jq, jc)", size=11, bold=True, color="#0f172a"))
    frags.append(text(col3_x + 25, 230, "• jq -r '.Action == \"start\"'", size=10, color="#334155", anchor="start"))
    frags.append(text(col3_x + 25, 250, "• Складні вкладені структури", size=10, color="#16a34a", anchor="start"))
    frags.append(text(col3_x + 25, 270, "• Базові типи (bool, number, null)", size=10, color="#16a34a", anchor="start"))

    frags.append(rect(col3_x + 15, 300, col_w - 30, 125, fill="#fefce8", stroke="#fde047", sw=1, rx=4))
    frags.append(text(col3_x + col_w / 2, 322, "Сучасний компроміс", size=11, bold=True, color="#854d0e"))
    frags.append(text(col3_x + 25, 342, "+ Універсальний для всіх мов", size=10, color="#713f12", anchor="start"))
    frags.append(text(col3_x + 25, 362, "+ Зберігає потоковість (line by line)", size=10, color="#713f12", anchor="start"))
    frags.append(text(col3_x + 25, 382, "− Витрати CPU на JSON-парсинг", size=10, color="#a16207", anchor="start"))
    frags.append(text(col3_x + 25, 402, "− Текстова надмірність ключів", size=10, color="#a16207", anchor="start"))

    render(os.path.join(OUT_DIR, "pipeline-paradigms-comparison.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_record_and_field_separators()
    fig_pipeline_paradigms_comparison()
    print("SVG figures generated successfully.")

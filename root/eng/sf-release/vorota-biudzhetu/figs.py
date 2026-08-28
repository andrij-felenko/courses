# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Ворота бюджету: флеш, RAM, стек, час завантаження»."""

import os
import sys

# Підключаємо svgkit з кореневої папки scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, textbox, fitbox, rect, line, arrow, circle, text, mtext,
    INK, MUTED, LINE, FILL, BG, POS, NEG, FIELD
)

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_embedded_memory_anatomy():
    """Фігура 1: Анатомія апаратних ресурсів Flash та SRAM з межами бюджетів."""
    w, h = 880, 520
    frags = []

    # Заголовок секції Flash (ROM)
    frags.append(rect(40, 50, 360, 440, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(220, 80, "Flash / ROM (Енергонезалежна пам'ять)", size=15, bold=True))
    frags.append(text(220, 100, "Фізичний обсяг: 512 КБ", size=12, color=MUTED))

    # Блоки всередині Flash
    # Вектори переривань
    frags.append(rect(60, 120, 320, 45, fill="#e0e7ff", stroke="#4f46e5", sw=1.2, rx=4))
    frags.append(text(220, 140, "Vector Table (Таблиця векторів ISR)", size=12, bold=True, color="#312e81"))
    frags.append(text(220, 155, "0x08000000 | 1 КБ", size=11, color=MUTED))

    # Секція .text
    frags.append(rect(60, 175, 320, 120, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=4))
    frags.append(text(220, 215, "Секція .text (Виконуваний машинний код)", size=13, bold=True, color="#1e3a8a"))
    frags.append(text(220, 235, "Функції програми, RTOS, драйвери периферії", size=11, color=INK))
    frags.append(text(220, 255, "Розмір: 210 КБ", size=11, color="#1e40af", bold=True))

    # Секція .rodata
    frags.append(rect(60, 305, 320, 75, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=4))
    frags.append(text(220, 335, "Секція .rodata (Константи та таблиці)", size=12, bold=True, color="#075985"))
    frags.append(text(220, 355, "Строкові літерали, lookup-таблиці, vtables | 45 КБ", size=11, color=INK))

    # Вільний запас / OTA Partition
    frags.append(rect(60, 390, 320, 85, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    frags.append(text(220, 420, "Запас Flash для OTA / Слот B", size=12, bold=True, color="#92400e"))
    frags.append(text(220, 440, "Вільний резерв: 256 КБ (Поріг CI: max 240 КБ / слот)", size=11, color="#b45309"))

    # Лінія жорсткого порогу Flash
    frags.append(line(45, 385, 395, 385, color=POS, sw=2, dash="5,3"))
    frags.append(text(220, 380, "Жорсткий ліміт розділу OTA: 256 КБ", size=10, bold=True, color=POS))

    # Заголовок секції RAM (SRAM)
    frags.append(rect(480, 50, 360, 440, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(660, 80, "SRAM (Оперативна пам'ять)", size=15, bold=True))
    frags.append(text(660, 100, "Фізичний обсяг: 128 КБ", size=12, color=MUTED))

    # Блоки всередині RAM
    # Секція .data
    frags.append(rect(500, 120, 320, 55, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=4))
    frags.append(text(660, 142, "Секція .data (Ініціалізовані глобальні змінні)", size=12, bold=True, color="#991b1b"))
    frags.append(text(660, 160, "Копіюються з Flash при старті | 12 КБ", size=11, color=MUTED))

    # Секція .bss
    frags.append(rect(500, 185, 320, 65, fill="#ffedd5", stroke="#f97316", sw=1.2, rx=4))
    frags.append(text(660, 210, "Секція .bss (Нульові глобальні/статичні змінні)", size=12, bold=True, color="#9a3412"))
    frags.append(text(660, 230, "Буфери, черги RTOS, дескриптори | 28 КБ", size=11, color=MUTED))

    # Динамічна область: Купа та Стек
    frags.append(rect(500, 260, 320, 160, fill="#ecfdf5", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(660, 285, "Динамічна пам'ять (Купа та Стеки задач)", size=13, bold=True, color="#065f46"))
    frags.append(text(660, 310, "Купа (Heap) зростає вгору ──>", size=11, color="#047857"))
    frags.append(text(660, 335, "<── Стек (Stack) зростає вниз", size=11, color="#047857"))
    frags.append(text(660, 365, "Доступний резерв динаміки: 88 КБ", size=11, bold=True, color="#065f46"))
    frags.append(text(660, 395, "Розрахований Max Stack: 24 КБ | Запас: 64 КБ", size=11, color=MUTED))

    # MPU Guard / Redzone
    frags.append(rect(500, 430, 320, 45, fill="#f3f4f6", stroke="#6b7280", sw=1.2, rx=4))
    frags.append(text(660, 452, "MPU Guard Region / Запобіжна зона", size=12, bold=True, color="#374151"))
    frags.append(text(660, 468, "Апаратний захист від переповнення стека", size=10, color=MUTED))

    # Лінія розділу статичної та динамічної RAM
    frags.append(line(485, 255, 835, 255, color=POS, sw=2, dash="5,3"))
    frags.append(text(660, 250, "Поріг статичної RAM (.data + .bss ≤ 40 КБ)", size=10, bold=True, color=POS))

    render(os.path.join(IMG_DIR, "embedded-memory-anatomy.svg"), w, h, *frags)


def fig_ci_budget_gate_flow():
    """Фігура 2: Конвеєр перевірки бюджетів у CI/CD з блокуванням злиття PR."""
    w, h = 920, 420
    frags = []

    # Крок 1: Запит на злиття
    b1, w1, h1 = textbox(110, 160, "Pull Request\n(Зміни коду)", size=13, bold=True, fill="#f1f5f9", stroke="#64748b", pad=12)
    frags.append(b1)

    frags.append(arrow(170, 160, 220, 160, color=LINE, sw=1.8))

    # Крок 2: Збірка з аналізом
    b2, w2, h2 = textbox(310, 160, "Компіляція та компонування\narm-none-eabi-gcc\n-fstack-usage -Wl,-Map", size=12, bold=True, fill="#e0e7ff", stroke="#4338ca", pad=10)
    frags.append(b2)

    frags.append(arrow(400, 160, 450, 160, color=LINE, sw=1.8))

    # Крок 3: Артефакти
    b3, w3, h3 = textbox(530, 160, "Артефакти збірки:\n• firmware.map\n• *.su (розмір стек-фреймів)\n• firmware.elf (секції)", size=11, bold=True, fill="#fef3c7", stroke="#d97706", pad=10)
    frags.append(b3)

    frags.append(arrow(610, 160, 660, 160, color=LINE, sw=1.8))

    # Крок 4: Валідатор воріт
    b4, w4, h4 = textbox(770, 160, "Ворота бюджету (Gates)\nПеревірка лімітів:\nFlash, RAM, Стек, Boot", size=12, bold=True, fill="#f8fafc", stroke=LINE, pad=12)
    frags.append(b4)

    # Розгалуження: Успіх vs Провал
    frags.append(arrow(770, 100, 770, 60, color=FIELD, sw=2.0))
    b_ok, wok, hok = textbox(770, 40, "✓ Бюджет дотримано: PR схвалено до злиття", size=12, bold=True, fill="#dcfce7", stroke=FIELD, pad=8, color="#166534")
    frags.append(b_ok)

    frags.append(arrow(770, 220, 770, 280, color=POS, sw=2.0))
    b_fail, wfail, hfail = textbox(770, 320, "✗ Перевищення бюджету!\nБлокування злиття PR\n+ Markdown звіт із дельтою", size=12, bold=True, fill="#fee2e2", stroke=POS, pad=10, color="#991b1b")
    frags.append(b_fail)

    # Нижній пояснювальний блок
    frags.append(rect(60, 370, 800, 35, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(460, 392, "Порівняння дельти PR з базовою гілкою (main): Flash Δ ≤ +1 КБ, RAM Δ ≤ +128 Б, Стек WCEP ≤ ліміт", size=11, color=MUTED, bold=True))

    render(os.path.join(IMG_DIR, "ci-budget-gate-flow.svg"), w, h, *frags)


def fig_static_stack_callgraph():
    """Фігура 3: Дерево викликів (Call Graph) та обчислення найгіршого шляху стека (WCEP)."""
    w, h = 900, 460
    frags = []

    # Корінь: Точка входу задачі
    b_root, _, _ = textbox(130, 220, "Task_Telemetry()\nСтек фрейму: 48 Б", size=12, bold=True, fill="#e0e7ff", stroke="#4f46e5", pad=10)
    frags.append(b_root)

    # Рівень 1
    b_n1, _, _ = textbox(360, 120, "Read_Sensors()\nСтек фрейму: 32 Б", size=11, bold=True, fill="#f1f5f9", stroke=LINE, pad=8)
    b_n2, _, _ = textbox(360, 320, "Format_Payload()\nСтек фрейму: 128 Б", size=11, bold=True, fill="#fef2f2", stroke=POS, pad=8)
    frags.append(b_n1)
    frags.append(b_n2)

    # Рівень 2 (гілка Read_Sensors)
    b_l1, _, _ = textbox(620, 70, "SPI_Transfer()\nСтек фрейму: 24 Б", size=11, bold=True, fill="#f1f5f9", stroke=LINE, pad=8)
    b_l2, _, _ = textbox(620, 160, "Scale_Values()\nСтек фрейму: 16 Б", size=11, bold=True, fill="#f1f5f9", stroke=LINE, pad=8)
    frags.append(b_l1)
    frags.append(b_l2)

    # Рівень 2 (гілка Format_Payload)
    b_l3, _, _ = textbox(620, 270, "Serialize_JSON()\nСтек фрейму: 256 Б", size=11, bold=True, fill="#fee2e2", stroke=POS, pad=8)
    b_l4, _, _ = textbox(620, 370, "Calc_CRC32()\nСтек фрейму: 16 Б", size=11, bold=True, fill="#f1f5f9", stroke=LINE, pad=8)
    frags.append(b_l3)
    frags.append(b_l4)

    # Стрілки з'єднань
    frags.append(arrow(200, 205, 290, 135, color=LINE, sw=1.5))
    frags.append(arrow(200, 235, 280, 310, color=POS, sw=2.2))  # Критичний шлях

    frags.append(arrow(430, 110, 545, 80, color=LINE, sw=1.5))
    frags.append(arrow(430, 130, 550, 155, color=LINE, sw=1.5))

    frags.append(arrow(440, 310, 540, 280, color=POS, sw=2.2))  # Критичний шлях
    frags.append(arrow(440, 330, 555, 365, color=LINE, sw=1.5))

    # Підсумкові блоки праворуч
    frags.append(rect(740, 50, 130, 150, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(805, 80, "Шлях 1 (SPI):", size=11, bold=True))
    frags.append(text(805, 105, "48 + 32 + 24", size=11, color=MUTED))
    frags.append(text(805, 125, "= 104 Байти", size=12, bold=True, color=FIELD))
    frags.append(text(805, 155, "Шлях 2 (Scale):", size=11, bold=True))
    frags.append(text(805, 175, "= 96 Байтів", size=11, color=MUTED))

    frags.append(rect(740, 240, 130, 180, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(805, 270, "Критичний шлях:", size=11, bold=True, color=POS))
    frags.append(text(805, 295, "48 + 128 + 256", size=11, color=MUTED))
    frags.append(text(805, 320, "= 432 Байти", size=13, bold=True, color=POS))
    frags.append(text(805, 355, "Ліміт задачі: 512 Б", size=10, color=MUTED))
    frags.append(text(805, 375, "Запас: 80 Б (15%)", size=11, bold=True, color="#b45309"))
    frags.append(text(805, 398, "Стан: У межах норми", size=10, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "static-stack-callgraph.svg"), w, h, *frags)


def fig_boot_time_milestones():
    """Фігура 4: Часовий бюджет фаз завантаження та контрольні мітки (Milestones)."""
    w, h = 900, 380
    frags = []

    # Часова вісь
    frags.append(line(80, 180, 820, 180, color=LINE, sw=2))
    frags.append(arrow(800, 180, 830, 180, color=LINE, sw=2))
    frags.append(text(830, 205, "Час (мс)", size=12, bold=True))

    # Мітка 0: Скидання (0 мс)
    frags.append(circle(100, 180, 6, fill=POS, stroke=LINE, sw=1.5))
    frags.append(line(100, 130, 100, 180, color=LINE, sw=1, dash="3,3"))
    frags.append(text(100, 120, "T0: 0 мс", size=11, bold=True))
    frags.append(text(100, 210, "Reset Handler", size=11, bold=True))
    frags.append(text(100, 225, "Старт ядра", size=10, color=MUTED))

    # Мітка 1: Тактування та пам'ять (2.5 мс)
    frags.append(circle(230, 180, 6, fill="#3b82f6", stroke=LINE, sw=1.5))
    frags.append(line(230, 100, 230, 180, color=LINE, sw=1, dash="3,3"))
    frags.append(text(230, 90, "T1: 2.5 мс", size=11, bold=True))
    frags.append(text(230, 210, "SystemInit", size=11, bold=True))
    frags.append(text(230, 225, "PLL + копіювання", size=10, color=MUTED))
    frags.append(text(230, 240, ".data та .bss", size=10, color=MUTED))

    # Мітка 2: Статичні конструктори C++ (6.0 мс)
    frags.append(circle(390, 180, 6, fill="#8b5cf6", stroke=LINE, sw=1.5))
    frags.append(line(390, 120, 390, 180, color=LINE, sw=1, dash="3,3"))
    frags.append(text(390, 110, "T2: 6.0 мс", size=11, bold=True))
    frags.append(text(390, 210, "C++ Static Init", size=11, bold=True))
    frags.append(text(390, 225, "__libc_init_array", size=10, color=MUTED))

    # Мітка 3: Ініціалізація шин і драйверів (18.0 мс)
    frags.append(circle(550, 180, 6, fill="#f59e0b", stroke=LINE, sw=1.5))
    frags.append(line(550, 90, 550, 180, color=LINE, sw=1, dash="3,3"))
    frags.append(text(550, 80, "T3: 18.0 мс", size=11, bold=True))
    frags.append(text(550, 210, "Драйвери шин", size=11, bold=True))
    frags.append(text(550, 225, "CAN / SPI / Сенсори", size=10, color=MUTED))

    # Мітка 4: Старт RTOS та готовність до зв'язку (32.0 мс)
    frags.append(circle(690, 180, 7, fill=FIELD, stroke=LINE, sw=2))
    frags.append(line(690, 70, 690, 180, color=FIELD, sw=1.5, dash="3,3"))
    frags.append(text(690, 60, "T4: 32.0 мс", size=12, bold=True, color="#15803d"))
    frags.append(text(690, 210, "First Task Ready", size=12, bold=True, color="#15803d"))
    frags.append(text(690, 228, "Перший фрейм CAN", size=10, color=MUTED))

    # Червона лінія дедлайну безпеки (50 мс)
    frags.append(line(780, 40, 780, 280, color=POS, sw=2.5, dash="6,4"))
    frags.append(text(780, 30, "Дедлайн готовності вузла: 50.0 мс", size=11, bold=True, color=POS))
    frags.append(text(780, 305, "Жорсткий ліміт ISO 26262 / CAN bus readiness", size=10, color=POS, bold=True))

    # Запас часу
    frags.append(rect(690, 140, 90, 25, fill="#dcfce7", stroke=FIELD, sw=1, rx=3))
    frags.append(text(735, 157, "Запас: 18 мс", size=10, bold=True, color="#166534"))

    # Пояснювальний блок знизу
    frags.append(rect(80, 335, 740, 35, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(450, 357, "CI/CD Gate перевіряє тривалість фаз у QEMU/HIL; регресія будь-якого етапу > 10% блокує злиття", size=11, color=MUTED, bold=True))

    render(os.path.join(IMG_DIR, "boot-time-milestones.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_embedded_memory_anatomy()
    fig_ci_budget_gate_flow()
    fig_static_stack_callgraph()
    fig_boot_time_milestones()
    print("Всі 4 фігури успішно згенеровано.")

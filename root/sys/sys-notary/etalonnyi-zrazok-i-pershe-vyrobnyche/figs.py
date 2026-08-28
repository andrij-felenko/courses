# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми «Еталонний зразок і перше виробниче»."""
import sys, os

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору від теки теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_golden_sample_lifecycle():
    """Фігура 1: Життєвий цикл еталонного зразка (Golden Sample)."""
    w, h = 980, 520
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Життєвий цикл та регламент збереження еталонного зразка (Golden Sample)", size=16, bold=True))

    # 5 послідовних етапів у верхньому ряду
    step_w = 172
    step_h = 170
    gap = 18
    start_x = 24
    y1 = 65

    steps = [
        ("1. Заморожування бази",
         "• Ревізія схемотехніки\n• Хеш специфікації BOM\n• Геометрія Gerber / ODB++\n• Координати CPL (X, Y, θ)\n• SHA-256 прошивки й OTP",
         "#edf4fc", "#2457d6"),
        ("2. Кваліфікація FAI",
         "• AS9102 Form 1, 2, 3\n• 100% замір геометрії\n• 3D Рентген (BGA/QFN)\n• Мікрошліфи зрізів плат\n• Перевірка класу IPC-610",
         "#f0fdf4", "#22c55e"),
        ("3. Зняття сигнатур",
         "• Еталонні форми сигналів\n• Пульсації шин живлення\n• Фазовий джитер тактування\n• ВЧ спектр і потужність\n• Профіль струмів споживання",
         "#fefce8", "#ca8a04"),
        ("4. Азотне сховище",
         "• Шафа з сухим азотом (N2)\n• Вологість RH < 5%, 21°C\n• Пакет MBB + картка HIC\n• Пломби захисту від змін\n• Дублікати (OEM + EMS)",
         "#faf5ff", "#9333ea"),
        ("5. Аудит та калібрування",
         "• Валідація тестерів FCT/ICT\n• Тест перед кожною зміною\n• Контроль дрейфу сенсорів\n• Планова річна переповірка\n• Журнал вилучення зразка",
         "#f8fafc", "#475569")
    ]

    for i, (stitle, sdesc, sfill, sstroke) in enumerate(steps):
        bx = start_x + i * (step_w + gap)
        frags.append(rect(bx, y1, step_w, step_h, fill=sfill, stroke=sstroke, sw=2, rx=8))
        frags.append(text(bx + step_w / 2, y1 + 24, stitle, size=12, color=sstroke, bold=True))
        frags.append(line(bx + 10, y1 + 34, bx + step_w - 10, y1 + 34, color=sstroke, sw=1, dash="3,2"))
        
        # Опис кроку
        lines = sdesc.split("\n")
        for li, line_txt in enumerate(lines):
            frags.append(text(bx + 10, y1 + 55 + li * 20, line_txt, size=10, color=INK, anchor="start"))

        # Стрілка між кроками
        if i < len(steps) - 1:
            ax = bx + step_w + 3
            ay = y1 + step_h / 2
            frags.append(arrow(ax, ay, ax + gap - 6, ay, color=LINE, sw=1.5))

    # Нижній блок: Замкнений контур ECO та лімітні зразки
    y2 = 265
    frags.append(rect(24, y2, 455, 230, fill="#fff1f2", stroke="#e11d48", sw=2, rx=8))
    frags.append(text(251, y2 + 28, "Петля інженерних змін (ECO / ECN)", size=13, color="#e11d48", bold=True))
    frags.append(line(40, y2 + 40, 460, y2 + 40, color="#e11d48", sw=1, dash="4,3"))

    eco_txt = [
        "1. Зміна ревізії: будь-яка заміна компонентів у BOM,",
        "   зміна топології PCB чи оновлення bootloader/прошивки.",
        "2. Інвалідація: поточний Golden Sample втрачає статус",
        "   еталона для нової партії продукції.",
        "3. Delta-FAI: виконання цільової перевірки змінених вузлів",
        "   та виготовлення нового комплекту Golden Sample.",
        "4. Архівування: старий зразок маркується як «Застарілий»",
        "   і зберігається 10 років для сервісних рекламацій."
    ]
    for li, line_txt in enumerate(eco_txt):
        frags.append(text(40, y2 + 65 + li * 20, line_txt, size=10, color=INK, anchor="start"))

    frags.append(rect(501, y2, 455, 230, fill="#f0fdfa", stroke="#0d9488", sw=2, rx=8))
    frags.append(text(728, y2 + 28, "Лімітні зразки (Limit Samples / Boundary Boards)", size=13, color="#0d9488", bold=True))
    frags.append(line(517, y2 + 40, 940, y2 + 40, color="#0d9488", sw=1, dash="4,3"))

    lim_txt = [
        "1. Призначення: на відміну від ідеального Golden Sample,",
        "   лімітні зразки задають граничні межі допуску (Go / No-Go).",
        "2. Візуальні дефекти: мінімально допустиме змочування",
        "   припою, допустимий кут перекосу компонентів 0402.",
        "3. Електричні межі: плати з граничним зміщенням частоти",
        "   кварца (±20 ppm) та мінімальним порогом напруги живлення.",
        "4. Налаштування AOI/AXOI: навчання оптичних алгоритмів",
        "   для відсіювання хибних спрацьовувань (False Positive)."
    ]
    for li, line_txt in enumerate(lim_txt):
        frags.append(text(517, y2 + 65 + li * 20, line_txt, size=10, color=INK, anchor="start"))

    render(os.path.join(IMG_DIR, "golden-sample-lifecycle.svg"), w, h, *frags)


def fig_fai_inspection_pipeline():
    """Фігура 2: Конвеєр First Article Inspection (AS9102 / IPC-A-610)."""
    w, h = 980, 520
    frags = []

    frags.append(text(w / 2, 28, "Конвеєр перевірки та кваліфікації першої партії (FAI AS9102 / IPC-A-610)", size=16, bold=True))

    col_w = 172
    col_h = 430
    gap = 18
    start_x = 24
    y1 = 60

    stages = [
        ("Етап 1: SMT Паста",
         "3D SPI Контроль",
         [
             "• Трафарет: товщина",
             "  100–120 мкм (лазер)",
             "• Паста: SAC305 Type 4",
             "• 3D SPI лазерний сканер:",
             "  Об'єм: 100% ± 20%",
             "  Висота шару: ±15 мкм",
             "  Зсув відбитка < 10%",
             "• Запобігання мікро-",
             "  перемичкам і пустотам",
             "• Відбраковка до пайки"
         ],
         "#eff6ff", "#3b82f6"),

        ("Етап 2: Pick & Place",
         "Монтаж і Оплавлення",
         [
             "• Точність PnP: ±25 мкм",
             "• Зусилля притискання",
             "  (без витіснення пасти)",
             "• Термопрофіль печі:",
             "  - Зона Soak: 150-190°C",
             "  - Час TAL (>217°C):",
             "    45–75 секунд",
             "  - Пік: 235–245°C",
             "  - Охолодження < 3°C/c",
             "• Запис профілю KIC"
         ],
         "#fdf4ff", "#c026d3"),

        ("Етап 3: AOI + AXOI",
         "Оптика і Рентген",
         [
             "• 3D AOI (Оптика):",
             "  - Зсув компонентів",
             "  - Полярність діодів/IC",
             "  - Меніск припою пайки",
             "• 3D AXOI (Рентген):",
             "  - Пустоти BGA < 15%",
             "  - QFN thermal pad > 70%",
             "  - Мостики під чіпами",
             "• Відповідність IPC-610",
             "  Class 2 / Class 3"
         ],
         "#fefce8", "#ca8a04"),

        ("Етап 4: ICT & FCT",
         "Тестування схем",
         [
             "• ICT (Bed of Nails):",
             "  - КЗ та обриви ліній",
             "  - Номінали R, C, L",
             "• JTAG Boundary Scan:",
             "  - BGA трасування шин",
             "• FCT (Функціонал):",
             "  - Запис bootloader/FW",
             "  - Прошивка ключів OTP",
             "  - Замір струмів і шин",
             "  - Калібрування ВЧ RF"
         ],
         "#f0fdf4", "#16a34a"),

        ("Етап 5: AS9102 Акт",
         "Статистичний звіт",
         [
             "• Звіт AS9102:",
             "  - Form 1: Part Number",
             "  - Form 2: Сировина/BOM",
             "  - Form 3: Заміри ТТХ",
             "• Статистика стабільності:",
             "  - Індекс Cp ≥ 1.67",
             "  - Індекс Cpk ≥ 1.33",
             "• Дозвіл на серію:",
             "  Підпис QC, OEM та EMS"
         ],
         "#fff7ed", "#ea580c")
    ]

    for i, (sheader, ssub, items_list, sfill, sstroke) in enumerate(stages):
        bx = start_x + i * (col_w + gap)
        frags.append(rect(bx, y1, col_w, col_h, fill=sfill, stroke=sstroke, sw=2, rx=8))
        frags.append(text(bx + col_w / 2, y1 + 22, sheader, size=12, color=sstroke, bold=True))
        frags.append(text(bx + col_w / 2, y1 + 40, ssub, size=10, color=MUTED, bold=False))
        frags.append(line(bx + 10, y1 + 49, bx + col_w - 10, y1 + 49, color=sstroke, sw=1, dash="3,2"))

        for li, it_text in enumerate(items_list):
            frags.append(text(bx + 10, y1 + 72 + li * 20, it_text, size=10, color=INK, anchor="start"))

        if i < len(stages) - 1:
            ax = bx + col_w + 3
            ay = y1 + col_h / 2
            frags.append(arrow(ax, ay, ax + gap - 6, ay, color=LINE, sw=1.5))

    render(os.path.join(IMG_DIR, "fai-inspection-pipeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_golden_sample_lifecycle()
    fig_fai_inspection_pipeline()
    print("All figures successfully generated in img/")

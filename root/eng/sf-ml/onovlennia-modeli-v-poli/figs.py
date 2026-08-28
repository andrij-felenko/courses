# -*- coding: utf-8 -*-
"""Фігури для статті про оновлення ML-моделей у полі (sf-ml).
Запуск: python figs.py
Виводить SVG у ./img/. Імпортує спільний svgkit зі scripts/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b8860b"


def fig_dual_model_flash_layout():
    W, H = 940, 500
    frags = []

    # Загальна рамка Flash
    frags.append(rect(40, 60, 520, 400, fill=BG, stroke=LINE, sw=2.0, rx=8))
    frags.append(text(300, 84, "Адресний простір NOR Flash (2048 КБ)", size=14, bold=True))

    # Секції Flash
    sections = [
        (96, 40, "0x0800_0000", "Завантажувач (Bootloader) · 64 КБ", "#f0f4fb", NEG, "Старт системи, перевірка векторів"),
        (142, 70, "0x0801_0000", "Прошивка застосунку та TFLM · 768 КБ", "#f0f4fb", NEG, "FreeRTOS, драйвери, рушій інференсу, OTA-стек"),
        (218, 38, "0x080D_0000", "Метадані та NV-конфіг · 32 КБ", "#fdf6e3", AMBER, "Покажчик активного слота, Trial-лічильник, CRC32"),
        (262, 80, "0x080D_8000", "Слот моделі А (АКТИВНИЙ) · 512 КБ", "#e8f6ee", FIELD, "Заголовок (Ed25519 + SHA256) + FlatBuffer int8 ваг"),
        (348, 80, "0x0815_8000", "Слот моделі B (СТАДІЙНИЙ / OTA) · 512 КБ", "#f4f6f8", INK, "Цільовий буфер запису чанків і тіньового тесту"),
        (434, 20, "0x081D_8000", "Журнал телеметрії · 160 КБ", "#f9f9f9", MUTED, "Лог розбіжностей"),
    ]

    for y, h, addr, title, bg, col, desc in sections:
        frags.append(rect(50, y, 500, h, fill=bg, stroke=col, sw=1.5, rx=4))
        frags.append(text(60, y + 16, addr, size=11, color=MUTED, anchor="start"))
        frags.append(text(200, y + 16, title, size=12, color=col, bold=True, anchor="start"))
        if h >= 38:
            frags.append(text(60, y + 32, desc, size=11, color=INK, anchor="start"))

    # Праві пояснювальні блоки
    callouts = [
        (100, 320, 80, "Основна прошивка", "Рушій інференсу TFLM скомпільований у код.\nПрацює безперервно навіть під час OTA.", NEG, "#f0f4fb"),
        (210, 320, 72, "Атомарний покажчик", "Один сектор пам'яті зберігає активний слот.\nПеремикання відбувається зміною 1 байта.", AMBER, "#fdf6e3"),
        (310, 320, 78, "Ізоляція пам'яті (Dual-Slot)", "OTA-клієнт стирає та пише Банк B.\nБанк A залишається недоторканим при збоях.", FIELD, "#e8f6ee"),
        (414, 320, 56, "Тіньовий запуск (Shadow Mode)", "Нова вага валідується на живому потоці сенсорів.", INK, "#f4f6f8"),
    ]

    for y, w, h, title, body, col, bg in callouts:
        frags.append(rect(580, y, w, h, fill=bg, stroke=col, sw=1.5, rx=6))
        frags.append(text(592, y + 20, title, size=13, color=col, bold=True, anchor="start"))
        frags.append(fitbox(592, y + 26, w - 24, h - 30, body, size=11, fill="none", stroke="none"))
        # Стрілка зв'язку
        frags.append(arrow(580, y + h / 2, 554, y + h / 2, color=col, sw=1.4))

    render(os.path.join(IMG, 'dual-model-flash-layout.svg'), W, H, *frags,
           title="Розкладка Flash-пам'яті для незалежного Dual-Bank оновлення моделей")


def fig_model_validation_fsm():
    W, H = 960, 560
    frags = []

    # Блоки станів
    # 1. Головний робочий стан
    frags.append(rect(40, 70, 220, 76, fill="#e8f6ee", stroke=FIELD, sw=2.0, rx=6))
    frags.append(text(150, 94, "1. ЗВИЧАЙНИЙ ІНФЕРЕНС", size=13, color=FIELD, bold=True))
    frags.append(text(150, 114, "Банк A керує моторами", size=11, color=INK))
    frags.append(text(150, 130, "Watchdog активний", size=10, color=MUTED))

    # 2. Завантаження
    frags.append(rect(370, 70, 220, 76, fill="#f0f4fb", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(480, 94, "2. ПРИЙОМ ЧАНКІВ (OTA)", size=13, color=NEG, bold=True))
    frags.append(text(480, 114, "Запис у стадійний Банк B", size=11, color=INK))
    frags.append(text(480, 130, "Бітова маска секторів", size=10, color=MUTED))

    # 3. Верифікація підпису
    frags.append(rect(700, 70, 220, 76, fill="#fdf6e3", stroke=AMBER, sw=1.8, rx=6))
    frags.append(text(810, 94, "3. КРИПТО-ВЕРИФІКАЦІЯ", size=13, color=AMBER, bold=True))
    frags.append(text(810, 114, "SHA-256 + Ed25519 підпис", size=11, color=INK))
    frags.append(text(810, 130, "Перевірка цілісності", size=10, color=MUTED))

    # 4. Валідація метаданих
    frags.append(rect(700, 220, 220, 76, fill="#fdf6e3", stroke=AMBER, sw=1.8, rx=6))
    frags.append(text(810, 244, "4. ВАЛІДАЦІЯ СХЕМИ", size=13, color=AMBER, bold=True))
    frags.append(text(810, 264, "OpResolver + тензори", size=11, color=INK))
    frags.append(text(810, 280, "Арена <= розмір SRAM", size=10, color=MUTED))

    # 5. Атомарний своп
    frags.append(rect(370, 220, 220, 76, fill="#f4f6f8", stroke=LINE, sw=1.8, rx=6))
    frags.append(text(480, 244, "5. АТОМАРНИЙ СВОП", size=13, color=INK, bold=True))
    frags.append(text(480, 264, "active_slot = BANK_B", size=11, color=INK))
    frags.append(text(480, 280, "Стан: TRIAL, boot_cnt = 0", size=10, color=MUTED))

    # 6. Тіньовий режим (Shadow Mode)
    frags.append(rect(370, 370, 220, 80, fill="#f0f4fb", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(480, 394, "6. ТІНЬОВИЙ ЗАПУСК", size=13, color=NEG, bold=True))
    frags.append(text(480, 414, "Паралельний інференс B", size=11, color=INK))
    frags.append(text(480, 430, "Порівняння з базою A", size=10, color=MUTED))

    # 7. Підтверджений успіх
    frags.append(rect(40, 370, 220, 80, fill="#e8f6ee", stroke=FIELD, sw=2.0, rx=6))
    frags.append(text(150, 394, "7. ПІДТВЕРДЖЕННЯ", size=13, color=FIELD, bold=True))
    frags.append(text(150, 414, "Дельта < порогу безпеки", size=11, color=INK))
    frags.append(text(150, 430, "Стан: CONFIRMED в NV", size=10, color=MUTED))

    # 8. Аварійний відкат (Rollback)
    frags.append(rect(700, 370, 220, 80, fill="#fdecea", stroke=POS, sw=2.0, rx=6))
    frags.append(text(810, 394, "8. АВАРІЙНИЙ ВІДКАТ", size=13, color=POS, bold=True))
    frags.append(text(810, 414, "active_slot = BANK_A", size=11, color=INK))
    frags.append(text(810, 430, "Стирання B + лог помилки", size=10, color=MUTED))

    # Стрілки переходів
    # 1 -> 2
    frags.append(arrow(260, 108, 366, 108, color=LINE))
    frags.append(text(313, 98, "OTA-запит", size=10, color=MUTED))

    # 2 -> 3
    frags.append(arrow(590, 108, 696, 108, color=LINE))
    frags.append(text(645, 98, "100% чанків", size=10, color=MUTED))

    # 3 -> 4
    frags.append(arrow(810, 146, 810, 216, color=AMBER))
    frags.append(text(816, 185, "Підпис OK", size=10, color=AMBER, anchor="start"))

    # 4 -> 5
    frags.append(arrow(700, 258, 594, 258, color=LINE))
    frags.append(text(647, 248, "Сумісно", size=10, color=MUTED))

    # 5 -> 6
    frags.append(arrow(480, 296, 480, 366, color=LINE))
    frags.append(text(486, 335, "Reboot / Trial", size=10, color=MUTED, anchor="start"))

    # 6 -> 7
    frags.append(arrow(370, 410, 264, 410, color=FIELD))
    frags.append(text(317, 400, "Валідно", size=10, color=FIELD))

    # 6 -> 8
    frags.append(arrow(590, 410, 696, 410, color=POS))
    frags.append(text(645, 400, "Розбіжність", size=10, color=POS))

    # 8 -> 1 (довга стрілка відкату вгору)
    frags.append(arrow(810, 450, 810, 480))
    frags.append(line(810, 480, 150, 480, color=POS, sw=1.5, dash="6 3"))
    frags.append(arrow(150, 480, 150, 150, color=POS))
    frags.append(text(480, 496, "Безпечний відкат на стабільний Банк A без втручання оператора", size=11, color=POS, bold=True))

    # Помилки верифікації 3 -> 8 та 4 -> 8
    frags.append(arrow(920, 108, 936, 108, color=POS))
    frags.append(line(936, 108, 936, 410, color=POS, sw=1.2, dash="4 4"))
    frags.append(arrow(936, 410, 924, 410, color=POS))
    frags.append(text(942, 260, "Невдалий підпис / несумісність", size=10, color=POS, anchor="start"))

    render(os.path.join(IMG, 'model-validation-fsm.svg'), W, H, *frags,
           title="Кінцевий автомат верифікації, безпечного тіньового тестування та відкату")


if __name__ == '__main__':
    fig_dual_model_flash_layout()
    fig_model_validation_fsm()
    print("OK: 2 фігури згенеровано у ./img/")

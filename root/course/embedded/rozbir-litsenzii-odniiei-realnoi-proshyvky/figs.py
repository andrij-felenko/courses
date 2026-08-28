# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальна палітра
GREEN_BG = "#eaf5ea"
GREEN_BD = "#27ae60"
GREEN_TX = "#196f3d"

BLUE_BG  = "#edf2fa"
BLUE_BD  = "#2457d6"
BLUE_TX  = "#1a3ea1"

AMBER_BG = "#fef9e7"
AMBER_BD = "#d4ac0d"
AMBER_TX = "#7d6608"

RED_BG   = "#fdedec"
RED_BD   = "#c0392b"
RED_TX   = "#78281f"

PURPLE_BG = "#f5eef8"
PURPLE_BD = "#8e44ad"
PURPLE_TX = "#512e5f"

GRAY_BG  = "#f4f6f7"
GRAY_BD  = "#7f8c8d"
GRAY_TX  = "#34495e"


# ── 1. firmware-stack-licenses: 7 шарів прошивки та їхні ліцензії ─────────────
def fig_firmware_stack():
    W, H = 840, 520
    p = []

    # Заголовок зверху
    p.append(text(W / 2, 28, "Анатомія прошивки польотного контролера: 7 шарів і ліцензійні режими", size=15, color=INK, bold=True))

    layers = [
        ("Шар 6: Застосунок", "Місія дрона, бізнес-логіка, протокол телеметрії", "Власна комерційна (All Rights Reserved)", RED_BG, RED_BD, RED_TX),
        ("Шар 5: Керування й DSP", "Власний алгоритм FOC двигунів + CMSIS-DSP + Madgwick AHRS", "Власна закрита / Apache-2.0 / MIT", PURPLE_BG, PURPLE_BD, PURPLE_TX),
        ("Шар 4: Мережа й сервіси", "Стек lwIP + криптографія mbedTLS + ФС FatFS + TinyUSB", "BSD-3-Clause / Apache-2.0 / ChaN / MIT", GREEN_BG, GREEN_BD, GREEN_TX),
        ("Шар 3: ОСРЧ (Kernel)", "FreeRTOS Kernel (планувальник задач, семафори, черги)", "MIT License (Amazon FreeRTOS)", GREEN_BG, GREEN_BD, GREEN_TX),
        ("Шар 2: HAL та драйвери", "ARM CMSIS Core + STM32Cube HAL периферії (UART/SPI/DMA)", "Apache-2.0 / BSD-3-Clause (ST SLA0048)", GREEN_BG, GREEN_BD, GREEN_TX),
        ("Шар 1: Закритий блоб", "Бінарний радіомодуль Wi-Fi/BLE (libphy.a, libcoexist.a)", "Пропрієтарна EULA чипмейкера (без коду)", AMBER_BG, AMBER_BD, AMBER_TX),
        ("Шар 0: Кремнієвий ROM", "Масковий апаратний завантажувач чипа (незмінний у Flash)", "Апаратна власність виробника кремнію", GRAY_BG, GRAY_BD, GRAY_TX),
    ]

    y_start = 58
    row_h = 58
    gap = 7
    box_w = 800
    box_x = (W - box_w) / 2

    for i, (lname, ldesc, llic, bg, bd, tx) in enumerate(layers):
        cy = y_start + i * (row_h + gap)
        # Рамка шару
        p.append(rect(box_x, cy, box_w, row_h, fill=bg, stroke=bd, sw=1.5, rx=5))

        # Назва шару ліворуч
        p.append(text(box_x + 16, cy + 24, lname, size=13, color=tx, anchor="start", bold=True))
        p.append(text(box_x + 16, cy + 44, ldesc, size=11, color=INK, anchor="start"))

        # Ліцензійна мітка праворуч
        tag_w = 290
        tag_x = box_x + box_w - tag_w - 12
        p.append(rect(tag_x, cy + 12, tag_w, 34, fill="#ffffff", stroke=bd, sw=1.2, rx=4))
        p.append(text(tag_x + tag_w / 2, cy + 34, llic, size=10.5, color=tx, anchor="middle", bold=True))

    p.append(text(W / 2, H - 10, "Усі шари збираються лінкером в один монолітний бінарник: ліцензійні вимоги діють одночасно", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "firmware-stack-licenses.svg"), W, H, *p)


# ── 2. static-linking-contagion: статичне лінкування та копілефт ──────────────
def fig_static_linking():
    W, H = 840, 460
    p = []

    p.append(text(W / 2, 26, "Статичне лінкування в MCU: каскадний ефект копілефту та блоб-пастка", size=15, color=INK, bold=True))

    # Ліва колонка: вхідні об'єктні файли
    p.append(text(140, 58, "Вхідні файли (.o / .a)", size=13, color=INK, bold=True))

    p.append(rect(30, 78, 220, 52, fill=RED_BG, stroke=RED_BD, sw=1.5, rx=5))
    p.append(text(140, 99, "main.o, control_foc.o", size=11.5, color=RED_TX, bold=True))
    p.append(text(140, 118, "Власний закритий код (IP)", size=10, color=INK))

    p.append(rect(30, 140, 220, 52, fill=GREEN_BG, stroke=GREEN_BD, sw=1.5, rx=5))
    p.append(text(140, 161, "freertos.a, lwip.a", size=11.5, color=GREEN_TX, bold=True))
    p.append(text(140, 180, "Пермісивний код (MIT / BSD)", size=10, color=INK))

    p.append(rect(30, 202, 220, 52, fill=AMBER_BG, stroke=AMBER_BD, sw=1.5, rx=5))
    p.append(text(140, 223, "libphy_wifi.a (блоб)", size=11.5, color=AMBER_TX, bold=True))
    p.append(text(140, 242, "EULA: заборона декомпіляції", size=10, color=INK))

    p.append(rect(30, 264, 220, 52, fill="#f9ebea", stroke="#e74c3c", sw=2, rx=5))
    p.append(text(140, 285, "gpl_algorithm.o", size=11.5, color=RED_TX, bold=True))
    p.append(text(140, 304, "Копілефт: ліцензія GPLv3", size=10, color=RED_TX, bold=True))

    # Стрілки до лінкера
    for y_in in [104, 166, 228, 290]:
        p.append(arrow(255, y_in, 315, 195, color=LINE, sw=1.5))

    # Центральний блок: Лінкер arm-none-eabi-ld
    p.append(rect(320, 130, 170, 130, fill=BLUE_BG, stroke=BLUE_BD, sw=2, rx=6))
    p.append(text(405, 165, "arm-none-eabi-ld", size=13, color=BLUE_TX, bold=True))
    p.append(text(405, 188, "Об'єднання символів", size=10.5, color=INK))
    p.append(text(405, 206, "в єдиний простір", size=10.5, color=INK))
    p.append(text(405, 224, "Flash: .text, .data", size=10.5, color=INK))
    p.append(text(405, 242, "Єдиний похідний твір", size=10, color=BLUE_TX, bold=True))

    # Стрілка праворуч
    p.append(arrow(495, 195, 545, 195, color=LINE, sw=2))

    # Права колонка: результат та юридичний глухий кут
    p.append(text(685, 58, "Юридичні наслідки лінкування", size=13, color=INK, bold=True))

    p.append(rect(550, 78, 265, 105, fill="#fdebd0", stroke="#d35400", sw=1.5, rx=5))
    p.append(text(682, 102, "1. Каскадна вимога GPLv3", size=12, color="#7e3200", bold=True))
    p.append(text(682, 124, "Весь монолітний образ firmware.elf", size=10.5, color=INK))
    p.append(text(682, 142, "стає похідним твором: вимога", size=10.5, color=INK))
    p.append(text(682, 160, "відкрити весь FOC/бізнес-код", size=10.5, color=RED_TX, bold=True))

    p.append(rect(550, 195, 265, 125, fill=RED_BG, stroke=RED_BD, sw=2, rx=5))
    p.append(text(682, 220, "2. Парадокс мертвого зашморгу", size=12, color=RED_TX, bold=True))
    p.append(text(682, 242, "GPLv3 §10 забороняє будь-які", size=10.5, color=INK))
    p.append(text(682, 260, "додаткові обмеження.", size=10.5, color=INK))
    p.append(text(682, 278, "EULA блоба забороняє публікацію.", size=10.5, color=INK))
    p.append(text(682, 300, "ВИПУСК ОБРАЗУ НЕЗАКОННИЙ", size=11, color=RED_TX, bold=True))

    # Нижній висновок
    p.append(rect(30, 360, 785, 62, fill="#f8f9fa", stroke=GRAY_BD, sw=1.5, rx=5))
    p.append(text(W / 2, 385, "Висновок для комерційної прошивки: жоден GPL-модуль не може бути статично злінкований", size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 406, "із закритими бінарними блобами або пропрієтарним кодом в одному адресному просторі Flash.", size=11, color=MUTED))

    render(os.path.join(OUT, "static-linking-contagion.svg"), W, H, *p)


# ── 3. lgpl-static-dilemma: пастка LGPL у мікроконтролерах ───────────────────
def fig_lgpl_dilemma():
    W, H = 840, 480
    p = []

    p.append(text(W / 2, 26, "Пастка LGPL: ПК із динамічним завантаженням проти монолітного MCU", size=15, color=INK, bold=True))

    # Верхня половина: ПК / Linux із динамічним лінкуванням
    p.append(rect(30, 55, 780, 165, fill=GREEN_BG, stroke=GREEN_BD, sw=1.5, rx=6))
    p.append(text(50, 80, "ПК / Linux із віртуальною пам'яттю (MMU) — Динамічне лінкування (.so / .dll)", size=12.5, color=GREEN_TX, anchor="start", bold=True))

    p.append(rect(50, 98, 200, 50, fill="#ffffff", stroke=RED_BD, sw=1.2, rx=4))
    p.append(text(150, 120, "closed_app (двійковий)", size=11, color=RED_TX, bold=True))
    p.append(text(150, 137, "Закритий код користувача", size=9.5, color=MUTED))

    p.append(arrow(255, 123, 315, 123, color=LINE, sw=1.5))
    p.append(text(285, 114, "dlopen()", size=9.5, color=MUTED))

    p.append(rect(320, 98, 200, 50, fill="#ffffff", stroke=BLUE_BD, sw=1.2, rx=4))
    p.append(text(420, 120, "libdsp.so (LGPLv3)", size=11, color=BLUE_TX, bold=True))
    p.append(text(420, 137, "Динамічна бібліотека", size=9.5, color=MUTED))

    p.append(rect(540, 98, 250, 105, fill="#ffffff", stroke=GREEN_BD, sw=1.2, rx=4))
    p.append(text(665, 118, "Відповідність ліцензії:", size=10.5, color=GREEN_TX, bold=True))
    p.append(text(665, 136, "Користувач може замінити", size=10, color=INK))
    p.append(text(665, 153, "файл libdsp.so на власний.", size=10, color=INK))
    p.append(text(665, 171, "Закритий код лишається закритим.", size=10, color=GREEN_TX, bold=True))
    p.append(text(665, 189, "Вимогу LGPL §4(d) виконано.", size=9.5, color=MUTED))

    p.append(text(50, 175, "Операційна система розділяє адреси: бібліотека підвантажується під час запуску окремо.", size=10.5, color=INK, anchor="start"))
    p.append(text(50, 195, "Перекомпіляція застосунку не потрібна, вихідники власного коду закриті.", size=10, color=MUTED, anchor="start"))

    # Нижня половина: Мікроконтролер (MCU) зі статичним лінкуванням
    p.append(rect(30, 235, 780, 205, fill=RED_BG, stroke=RED_BD, sw=1.5, rx=6))
    p.append(text(50, 260, "Мікроконтролер без MMU (ARM Cortex-M) — Статичне монолітне лінкування", size=12.5, color=RED_TX, anchor="start", bold=True))

    # Варіант А: Віддати .o файли
    p.append(rect(50, 278, 350, 145, fill="#ffffff", stroke=AMBER_BD, sw=1.2, rx=4))
    p.append(text(225, 300, "Варіант А: Роздача .o об'єктних файлів", size=11, color=AMBER_TX, bold=True))
    p.append(text(225, 320, "Виробник зобов'язаний надати покупцю:", size=10, color=INK))
    p.append(text(225, 338, "• Усі пропрієтарні main.o, foc.o", size=10, color=RED_TX))
    p.append(text(225, 356, "• Скрипт лінкера link.ld + Makefile", size=10, color=INK))
    p.append(text(225, 374, "• Інструкцію з перезбирання образу", size=10, color=INK))
    p.append(text(225, 396, "Розкриває імена символів, структури й логіку!", size=9.5, color=RED_TX, bold=True))

    # Варіант Б: Заміна на пермісивну бібліотеку
    p.append(rect(430, 278, 360, 145, fill="#ffffff", stroke=GREEN_BD, sw=1.2, rx=4))
    p.append(text(610, 300, "Варіант Б: Інженерне рішення (Чистий стек)", size=11, color=GREEN_TX, bold=True))
    p.append(text(610, 320, "Повна відмова від LGPL у статичному образі:", size=10, color=INK))
    p.append(text(610, 338, "• Заміна на Apache-2.0 / MIT / BSD", size=10, color=GREEN_TX, bold=True))
    p.append(text(610, 356, "• Використання CMSIS-DSP або mbedTLS", size=10, color=INK))
    p.append(text(610, 374, "• Або комерційна ліцензія від автора", size=10, color=INK))
    p.append(text(610, 396, "Нульовий ризик витоку коду чи вимог перелінку!", size=9.5, color=GREEN_TX, bold=True))

    p.append(text(W / 2, H - 10, "У прошивках мікроконтролерів LGPL практично еквівалентний зобов'язанням розкриття двійкових модулів", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "lgpl-static-dilemma.svg"), W, H, *p)


# ── 4. compliance-flow-pipeline: автоматизований конвеєр аудиту SBOM ─────────
def fig_compliance_pipeline():
    W, H = 840, 380
    p = []

    p.append(text(W / 2, 26, "Автоматизований конвеєр ліцензійного аудиту та генерації SBOM у CI/CD", size=15, color=INK, bold=True))

    steps = [
        ("1. Джерела", "Вихідний код,\nпідмодулі Git,\nSPDX-теги", BLUE_BG, BLUE_BD, BLUE_TX),
        ("2. Збірка", "Компіляція й\nлінкування\nfirmware.elf", GRAY_BG, GRAY_BD, GRAY_TX),
        ("3. Аудит мапи", "Аналіз .map файлу\nта arm-none-eabi-nm:\nхто увійшов у Flash", AMBER_BG, AMBER_BD, AMBER_TX),
        ("4. Шлюз правил", "Перевірка матриці:\nблокування GPLv3\nі нечистих ліцензій", RED_BG, RED_BD, RED_TX),
        ("5. Артефакти", "Генерація SBOM\n(CycloneDX JSON)\nта NOTICE.txt", GREEN_BG, GREEN_BD, GREEN_TX),
    ]

    bw = 140
    bh = 135
    start_x = 25
    gap = 22
    by = 65

    for i, (stitle, sdesc, bg, bd, tx) in enumerate(steps):
        bx = start_x + i * (bw + gap)
        p.append(rect(bx, by, bw, bh, fill=bg, stroke=bd, sw=1.8, rx=6))
        p.append(text(bx + bw / 2, by + 26, stitle, size=12, color=tx, bold=True))

        lines = sdesc.split("\n")
        for line_i, ln in enumerate(lines):
            p.append(text(bx + bw / 2, by + 56 + line_i * 18, ln, size=10, color=INK))

        # Стрілка до наступного блоку
        if i < len(steps) - 1:
            p.append(arrow(bx + bw + 2, by + bh / 2, bx + bw + gap - 2, by + bh / 2, color=LINE, sw=2))

    # Блок пояснення вихідних артефактів знизу
    p.append(rect(25, 225, 790, 115, fill="#fcfcfc", stroke=GREEN_BD, sw=1.5, rx=6))
    p.append(text(45, 248, "Обов'язкові артефакти юридично чистого релізу прошивки:", size=12, color=GREEN_TX, anchor="start", bold=True))

    p.append(text(45, 274, "• sbom-firmware.cdx.json / spdx.json — машинночитний паспорт компонентів (хеші, ліцензії, версії, CPE/PURL).", size=10.5, color=INK, anchor="start"))
    p.append(text(45, 296, "• THIRD_PARTY_NOTICES.txt — повний зведений текст ліцензій (MIT, BSD, Apache-2.0) для інструкції або веб-сервера.", size=10.5, color=INK, anchor="start"))
    p.append(text(45, 318, "• flash_license_table.bin — вбудована таблиця атрибуції у службовій секції Flash для виводу через CLI-консоль.", size=10.5, color=INK, anchor="start"))

    p.append(text(W / 2, H - 10, "Конвеєр автоматично ламає збірку в CI, якщо розробник підключив несумісну копілефтну бібліотеку", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "compliance-flow-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_firmware_stack()
    fig_static_linking()
    fig_lgpl_dilemma()
    fig_compliance_pipeline()
    print("All 4 figures generated successfully in ./img/")

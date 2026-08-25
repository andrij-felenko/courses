# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми Flash Encryption (ESP-IDF)."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_attack_vector_spi():
    """Фігура 1: Фізична незахищеність шини SPI та вектори атак."""
    w, h = 840, 420
    frags = []

    # Заголовок / тло
    frags.append(rect(10, 10, 820, 400, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(420, 34, "Вектори фізичних атак на зовнішню Flash-пам'ять без шифрування", size=15, bold=True))

    # Лівий блок: SoC ESP32
    frags.append(rect(25, 60, 215, 330, fill="#f0f4f8", stroke="#2457d6", sw=2, rx=6))
    frags.append(text(132, 86, "Мікроконтролер (SoC)", size=13, color="#2457d6", bold=True))
    frags.append(text(132, 104, "Захищений кристал", size=11, color=MUTED))

    b_cpu, _, _ = textbox(132, 148, "Процесорні ядра\n(Xtensa / RISC-V)", size=11.5, pad=8, fill="#ffffff", stroke="#2457d6", min_w=175)
    frags.append(b_cpu)

    b_sram, _, _ = textbox(132, 216, "Внутрішня пам'ять\n(SRAM + Mask ROM)", size=11.5, pad=8, fill="#ffffff", stroke="#2457d6", min_w=175)
    frags.append(b_sram)

    b_ctrl, _, _ = textbox(132, 290, "SPI Flash\nКонтролер", size=11.5, pad=8, fill="#ffffff", stroke="#2457d6", min_w=175)
    frags.append(b_ctrl)

    # Правий блок: Зовнішній SPI Flash
    frags.append(rect(600, 60, 215, 330, fill="#fdf2e9", stroke="#d35400", sw=2, rx=6))
    frags.append(text(707, 86, "Зовнішня Flash-пам'ять", size=13, color="#d35400", bold=True))
    frags.append(text(707, 104, "Корпус SOIC-8 / WSON-8", size=11, color=MUTED))

    b_chip, _, _ = textbox(707, 165, "Масив NOR Flash\n(Сектори 4 КБ / 64 КБ)", size=11.5, pad=8, fill="#ffffff", stroke="#d35400", min_w=175)
    frags.append(b_chip)

    b_cont, _, _ = textbox(707, 275, "Відкритий вміст:\n• Завантажувач\n• Код прошивки\n• Ключі доступу / Wi-Fi", size=11, pad=8, fill="#ffffff", stroke="#d35400", min_w=175)
    frags.append(b_cont)

    # Центральні лінії шини SPI
    frags.append(rect(265, 180, 310, 145, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=4))
    frags.append(text(420, 198, "Доріжки друкованої плати (PCB)", size=11, color=MUTED, bold=True))

    lines_info = [
        ("CLK (Тактовий сигнал)", 216),
        ("CS (Вибір мікросхеми)", 238),
        ("MOSI / IO0 (Дані вхід)", 260),
        ("MISO / IO1 (Дані вихід)", 282),
        ("WP, HOLD / IO2, IO3", 304)
    ]
    for name, y_pos in lines_info:
        frags.append(line(240, y_pos, 600, y_pos, color="#64748b", sw=1.5))
        frags.append(text(420, y_pos - 3, name, size=9.5, color="#334155"))

    # Атака 1: Логічний аналізатор зверху
    frags.append(rect(295, 60, 250, 85, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(420, 80, "Атака 1: Пасивне перехоплення", size=12, color=POS, bold=True))
    frags.append(text(420, 98, "Логічний аналізатор / осцилограф", size=11, color=INK))
    frags.append(text(420, 116, "Сніфінг шини під час старту чипа", size=10, color=MUTED))
    frags.append(arrow(420, 145, 420, 180, color=POS, sw=2))

    # Атака 2: Випаювання чіпа знизу
    frags.append(rect(295, 345, 250, 50, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(420, 363, "Атака 2: Випаювання мікросхеми", size=12, color=POS, bold=True))
    frags.append(text(420, 381, "Прямий дамп у програматорі CH341A", size=10, color=MUTED))
    frags.append(arrow(707, 390, 545, 375, color=POS, sw=1.5))

    render(os.path.join(IMG_DIR, "attack-vector-spi.svg"), w, h, *frags)


def fig_bus_encryption_arch():
    """Фігура 2: Апаратна архітектура прозорого шифрування шини SPI."""
    w, h = 890, 410
    frags = []

    # Загальний фон
    frags.append(rect(10, 10, 870, 390, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(445, 32, "Апаратний конвеєр прозорого дешифрування Flash (AES-XTS)", size=15, bold=True))

    # Кордон кремнію SoC
    frags.append(rect(25, 50, 620, 335, fill="#f8fafc", stroke="#3b82f6", sw=1.8, rx=6))
    frags.append(text(130, 72, "Внутрішній простір SoC ESP32", size=12, color="#1d4ed8", bold=True))

    # 1. CPU Core
    b_cpu, _, _ = textbox(95, 145, "Процесорне ядро\n(CPU Core)\nАдреса MMU:\n0x42000000", size=10.5, pad=8, fill="#ffffff", stroke="#1d4ed8", min_w=125)
    frags.append(b_cpu)

    # 2. MMU & Cache
    b_mmu, _, _ = textbox(235, 145, "MMU та кеш\n(Instruction / Data)\nТрансляція адрес\nі кеш-лінії", size=10.5, pad=8, fill="#ffffff", stroke="#1d4ed8", min_w=125)
    frags.append(b_mmu)

    # 3. AES-XTS Cryptographic Engine
    b_aes, _, _ = textbox(395, 145, "Апаратний рушій\nAES-XTS\nМиттєве розшифрування\nблоків по 32 байти", size=10.5, pad=8, fill="#ecfdf5", stroke=FIELD, min_w=150)
    frags.append(b_aes)

    # 4. eFuse Key Block (внизу)
    frags.append(rect(315, 255, 160, 95, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(395, 275, "eFuse Матриця", size=12, color=POS, bold=True))
    frags.append(text(395, 295, "Ключ шифрування", size=11, color=INK))
    frags.append(text(395, 312, "256-біт (AES-XTS)", size=10, color=MUTED))
    frags.append(text(395, 332, "Захист: RD_DIS = 1", size=10, color=POS, bold=True))

    # Стрілка від eFuse до AES engine
    frags.append(arrow(395, 255, 395, 195, color=POS, sw=2))
    frags.append(text(405, 225, "Лінія ключа", size=9, color=POS, anchor="start"))

    # 5. SPI Controller
    b_spic, _, _ = textbox(555, 145, "SPI Flash\nКонтролер\nФізичні транзакції\nпо шині SPI", size=10.5, pad=8, fill="#ffffff", stroke="#1d4ed8", min_w=125)
    frags.append(b_spic)

    # Зовнішній Flash (праворуч)
    frags.append(rect(675, 50, 190, 335, fill="#fefce8", stroke="#ca8a04", sw=1.8, rx=6))
    frags.append(text(770, 72, "Зовнішня SPI Flash", size=12, color="#854d0e", bold=True))

    b_ext, _, _ = textbox(770, 145, "Фізична Flash\nШифротекст (Ciphertext)\nЗашифровані сектори\nі таблиця розділів", size=10.5, pad=8, fill="#ffffff", stroke="#ca8a04", min_w=160)
    frags.append(b_ext)

    # Стрілки конвеєра даних
    # Flash -> SPI Controller
    frags.append(arrow(680, 135, 620, 135, color="#d97706", sw=2))
    frags.append(text(650, 120, "SPI Bus", size=10, color="#d97706"))
    frags.append(text(650, 150, "Шифротекст", size=9, color=MUTED))

    # SPI Controller -> AES Engine
    frags.append(arrow(490, 135, 475, 135, color=LINE, sw=1.5))

    # AES Engine -> MMU/Cache
    frags.append(arrow(318, 135, 300, 135, color=FIELD, sw=2))
    frags.append(text(310, 120, "Текст", size=9, color=FIELD))

    # MMU -> CPU
    frags.append(arrow(170, 135, 160, 135, color="#1d4ed8", sw=2))

    # Пояснювальний блок знизу
    frags.append(rect(40, 270, 240, 80, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(160, 292, "Властивості шифратора:", size=11, bold=True))
    frags.append(text(160, 312, "• Прозорість: 0% навантаження ЦПУ", size=10, color=INK))
    frags.append(text(160, 330, "• XIP: пряме виконання з кешу", size=10, color=INK))

    render(os.path.join(IMG_DIR, "bus-encryption-arch.svg"), w, h, *frags)


def fig_aes_xts_tweak():
    """Фігура 3: Робота модифікатора адреси (Tweak) в режимі AES-XTS."""
    w, h = 820, 360
    frags = []

    frags.append(rect(10, 10, 800, 340, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(410, 32, "Механізм модифікатора адреси (Tweak) у режимі AES-XTS", size=15, bold=True))

    # Блок 1 (Зсув 0x10000)
    frags.append(rect(30, 55, 360, 275, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(210, 78, "Блок 1 (Фізична адреса 0x010000)", size=12, color="#1e293b", bold=True))

    b_p1, _, _ = textbox(210, 115, "Відкритий текст P₁ (32 байти)\n[0xFF, 0xFF, 0xFF, ... 0xFF]", size=11, pad=6, fill="#f1f5f9", stroke="#64748b", min_w=300)
    frags.append(b_p1)

    b_tw1, _, _ = textbox(210, 185, "Обчислення твіка:\nT₁ = AES_K2 (0x010000)", size=11, pad=6, fill="#fef3c7", stroke="#d97706", min_w=240)
    frags.append(b_tw1)

    b_c1, _, _ = textbox(210, 275, "Шифротекст C₁ (у Flash):\n0x8F 3A D1 90 BC ... 4E", size=11, pad=8, fill="#fee2e2", stroke=POS, min_w=300)
    frags.append(b_c1)

    frags.append(arrow(210, 138, 210, 162, color=LINE, sw=1.5))
    frags.append(arrow(210, 212, 210, 245, color=POS, sw=1.8))
    frags.append(text(210, 235, "P₁ ⊕ T₁ → AES_K1 → ⊕ T₁", size=10, color=MUTED))

    # Блок 2 (Зсув 0x020000)
    frags.append(rect(430, 55, 360, 275, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(610, 78, "Блок 2 (Фізична адреса 0x020000)", size=12, color="#1e293b", bold=True))

    b_p2, _, _ = textbox(610, 115, "Той самий відкритий текст P₂ = P₁\n[0xFF, 0xFF, 0xFF, ... 0xFF]", size=11, pad=6, fill="#f1f5f9", stroke="#64748b", min_w=300)
    frags.append(b_p2)

    b_tw2, _, _ = textbox(610, 185, "Обчислення твіка:\nT₂ = AES_K2 (0x020000)  [T₂ ≠ T₁]", size=11, pad=6, fill="#fef3c7", stroke="#d97706", min_w=240)
    frags.append(b_tw2)

    b_c2, _, _ = textbox(610, 275, "Геть інший шифротекст C₂:\n0x1B 9C 04 F7 82 ... D3  (C₂ ≠ C₁)", size=11, pad=8, fill="#fee2e2", stroke=POS, min_w=300)
    frags.append(b_c2)

    frags.append(arrow(610, 138, 610, 162, color=LINE, sw=1.5))
    frags.append(arrow(610, 212, 610, 245, color=POS, sw=1.8))
    frags.append(text(610, 235, "P₂ ⊕ T₂ → AES_K1 → ⊕ T₂", size=10, color=MUTED))

    render(os.path.join(IMG_DIR, "aes-xts-tweak.svg"), w, h, *frags)


def fig_first_boot_flow():
    """Фігура 4: Життєвий цикл автоматичного шифрування під час першого старту."""
    w, h = 840, 390
    frags = []

    frags.append(rect(10, 10, 820, 370, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(420, 32, "Етапи первинного шифрування Flash під час першого завантаження", size=15, bold=True))

    steps = [
        ("1. Прошивання через UART", "ПК записує відкритий\nзавантажувач, таблицю\nрозділів та додаток у Flash.", 100, 110, "#f8fafc", "#64748b"),
        ("2. Старт ROM Bootloader", "ROM бачить прапорець\nактивації у меню конфігурації\nта передає хід завантажувачу.", 260, 110, "#eff6ff", "#3b82f6"),
        ("3. Генерація ключа eFuse", "Апаратний RNG генерує\n256-біт ключ. Запис у eFuse\nі блокування зчитування RD_DIS.", 420, 110, "#fef2f2", POS),
        ("4. Шифрування за місцем", "Завантажувач читає сектори,\nшифрує через AES-XTS і пише\nназад у Flash (in-place).", 580, 110, "#fefce8", "#ca8a04"),
        ("5. Фіксація лічильника", "Пропалювання FLASH_CRYPT_CNT.\nМ'яке перезавантаження чипа.\nНадалі шина завжди шифрована.", 740, 110, "#ecfdf5", FIELD),
    ]

    for title, desc, cx, cy, fill_c, stroke_c in steps:
        b_st, _, _ = textbox(cx, cy + 30, desc, size=10.5, pad=6, fill=fill_c, stroke=stroke_c, min_w=140)
        frags.append(b_st)
        frags.append(text(cx, cy - 22, title, size=11, color=stroke_c, bold=True))

    # Стрілки між етапами
    frags.append(arrow(170, 140, 190, 140, color=LINE, sw=1.5))
    frags.append(arrow(330, 140, 350, 140, color=LINE, sw=1.5))
    frags.append(arrow(490, 140, 510, 140, color=LINE, sw=1.5))
    frags.append(arrow(650, 140, 670, 140, color=LINE, sw=1.5))

    # Нижня плашка з режимами
    frags.append(rect(40, 235, 760, 120, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(420, 258, "Порівняння режимів Flash Encryption в ESP-IDF", size=13, bold=True))

    # Режим Development
    frags.append(rect(55, 275, 350, 65, fill="#eff6ff", stroke="#3b82f6", sw=1, rx=4))
    frags.append(text(230, 295, "Development Mode (Розробка)", size=11, color="#1d4ed8", bold=True))
    frags.append(text(230, 313, "• Дозволяє повторне перепрошивання через UART", size=10, color=INK))
    frags.append(text(230, 328, "• FLASH_CRYPT_CNT можна перемикати (до вичерпання бітів)", size=9.5, color=MUTED))

    # Режим Release
    frags.append(rect(435, 275, 350, 65, fill="#fef2f2", stroke=POS, sw=1, rx=4))
    frags.append(text(610, 295, "Release Mode (Серійне виробництво)", size=11, color=POS, bold=True))
    frags.append(text(610, 313, "• Незворотне блокування: FLASH_CRYPT_CNT = max", size=10, color=INK))
    frags.append(text(610, 328, "• UART ROM Download і JTAG назавжди відключені", size=9.5, color=POS))

    render(os.path.join(IMG_DIR, "first-boot-flow.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_attack_vector_spi()
    fig_bus_encryption_arch()
    fig_aes_xts_tweak()
    fig_first_boot_flow()
    print("Всі фігури згенеровано успішно.")

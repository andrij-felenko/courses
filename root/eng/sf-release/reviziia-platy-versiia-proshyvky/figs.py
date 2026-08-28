# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Мультибінарний підхід проти уніфікованого Single Binary ─────────────
def fig_single_binary_vs_multi_binary():
    W, H = 1000, 520
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Заголовок
    p.append(text(W / 2, 34, "Стратегії випуску: мультибінарна фрагментація проти Single Binary Multi-Hardware", size=15, color=INK, bold=True))
    
    # Ліва колонка: Мультибінарний підхід
    left_w = 450
    p.append(rect(30, 60, left_w, 430, fill="#fff5f5", stroke="#e03131", sw=1.4, rx=6))
    p.append(text(30 + left_w / 2, 86, "МУЛЬТИБІНАРНИЙ ПІДХІД (Multi-Binary)", size=13, color="#c92a2a", bold=True))
    p.append(text(30 + left_w / 2, 105, "Окремий артефакт під кожну ревізію плати", size=11, color=MUTED))
    
    # Блоки лівої колонки
    p.append(rect(50, 125, 410, 48, fill="#ffffff", stroke="#ffc9c9", sw=1.2, rx=4))
    p.append(text(255, 145, "Єдина кодова база з умовним препроцесором", size=11.5, color=INK, bold=True))
    p.append(text(255, 162, "#ifdef BOARD_REV_A / #elif BOARD_REV_B / #elif BOARD_REV_C", size=10, color="#862e9c"))
    
    p.append(arrow(255, 175, 255, 200, color=LINE, sw=1.6))
    
    p.append(rect(50, 202, 410, 50, fill="#ffffff", stroke="#ffc9c9", sw=1.2, rx=4))
    p.append(text(255, 222, "Роздільна збірка в CI: N паралельних бінарників", size=11.5, color=INK, bold=True))
    p.append(text(255, 240, "fw_revA_v2.4.bin   •   fw_revB_v2.4.bin   •   fw_revC_v2.4.bin", size=10.5, color="#c92a2a"))
    
    p.append(arrow(255, 254, 255, 278, color=LINE, sw=1.6))
    
    p.append(rect(50, 280, 410, 95, fill="#ffe3e3", stroke="#ffa8a8", sw=1.2, rx=4))
    p.append(text(255, 300, "Критичні ризики та експлуатаційні витрати:", size=11.5, color="#c92a2a", bold=True))
    p.append(mtext(255, 322, [
        "• Ризик прошити несумісний бінарник на заводі або під час OTA",
        "• Комбінаторний вибух матриці тестування (N прошивок × M плат)",
        "• Необхідність складного бекенду обліку ревізій кожного пристрою",
        "• Блокування оновлення при помилці в базі серійних номерів"
    ], size=10, color=INK, lh=1.35))
    
    p.append(rect(50, 390, 410, 85, fill="#ffffff", stroke="#e03131", sw=1.2, rx=4))
    p.append(text(255, 412, "Наслідок: Окрипічування (Bricking)", size=12, color="#c92a2a", bold=True))
    p.append(mtext(255, 434, [
        "Несумісна конфігурація GPIO Chip Select підвішує шину SPI;",
        "невідповідний драйвер сенсора впадає у нескінченний Bootloop."
    ], size=10.5, color=INK, lh=1.35))
    
    # Права колонка: Single Binary Multi-Hardware
    right_x = 520
    right_w = 450
    p.append(rect(right_x, 60, right_w, 430, fill="#f3faf7", stroke="#2b8a3e", sw=1.4, rx=6))
    p.append(text(right_x + right_w / 2, 86, "SINGLE BINARY MULTI-HARDWARE", size=13, color="#2b8a3e", bold=True))
    p.append(text(right_x + right_w / 2, 105, "Один універсальний бінарний образ для всього парку", size=11, color=MUTED))
    
    # Блоки правої колонки
    p.append(rect(right_x + 20, 125, 410, 48, fill="#ffffff", stroke="#b2f2bb", sw=1.2, rx=4))
    p.append(text(right_x + 225, 145, "Єдина кодова база з таблицями дескрипторів", size=11.5, color=INK, bold=True))
    p.append(text(right_x + 225, 162, "Абстрактні інтерфейси VTable + таблиця сумісності ревізій", size=10, color="#1864ab"))
    
    p.append(arrow(right_x + 225, 175, right_x + 225, 200, color=LINE, sw=1.6))
    
    p.append(rect(right_x + 20, 202, 410, 50, fill="#ffffff", stroke="#b2f2bb", sw=1.2, rx=4))
    p.append(text(right_x + 225, 222, "Єдиний артефакт збірки в CI конвеєрі", size=11.5, color=INK, bold=True))
    p.append(text(right_x + 225, 240, "firmware_v2.4_universal.bin (Один криптографічний підпис)", size=10.5, color="#2b8a3e", bold=True))
    
    p.append(arrow(right_x + 225, 254, right_x + 225, 278, color=LINE, sw=1.6))
    
    p.append(rect(right_x + 20, 280, 410, 95, fill="#d3f9d8", stroke="#8ce99a", sw=1.2, rx=4))
    p.append(text(right_x + 225, 300, "Динамічна адаптація на етапі запуску (Phase 0):", size=11.5, color="#2b8a3e", bold=True))
    p.append(mtext(right_x + 225, 322, [
        "• Апаратне зчитування Board ID (ADC / Strapping / EEPROM)",
        "• Автоматичне підтягування правильної карти пінів (Pinmux)",
        "• Підключення відповідного драйвера IMU / Flash без перепрошивки",
        "• Безпечний відкат до захищеного стану при невідомій ревізії"
    ], size=10, color=INK, lh=1.35))
    
    p.append(rect(right_x + 20, 390, 410, 85, fill="#ffffff", stroke="#2b8a3e", sw=1.2, rx=4))
    p.append(text(right_x + 225, 412, "Результат: 100% безпека релізу та OTA", size=12, color="#2b8a3e", bold=True))
    p.append(mtext(right_x + 225, 434, [
        "Один файл оновлення поширюється на всі плати Rev A, B, C;",
        "виключено людський фактор на конвеєрі та збої розсинхронізації."
    ], size=10.5, color=INK, lh=1.35))
    
    render(os.path.join(OUT, "single-binary-vs-multi-binary.svg"), W, H, *p)

# ── Фіг. 2: Апаратні топології детектування ревізії плати ─────────────────────
def fig_board_revision_detection_mechanisms():
    W, H = 1000, 540
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 34, "Апаратні механізми автодетектування ревізії друкованої плати", size=15, color=INK, bold=True))
    
    # 4 квадранти
    qw, qh = 460, 225
    
    # 1. Резистивний дільник на ADC (верхній лівий)
    x1, y1 = 30, 60
    p.append(rect(x1, y1, qw, qh, fill="#f8fafc", stroke="#3b82f6", sw=1.4, rx=6))
    p.append(text(x1 + qw / 2, y1 + 24, "1. Резистивний дільник на вході ADC", size=13, color="#1d4ed8", bold=True))
    p.append(mtext(x1 + qw / 2, y1 + 50, [
        "• 1 аналоговий пін кодує 4–8 ревізій через стабільні рівні напруги",
        "• Прецизійні резистори 1% (ряд E96) + фільтруючий керамічний конденсатор",
        "• Програмне вікно компаратора з гістерезисом та захистом від шуму Vref"
    ], size=10.5, color=INK, lh=1.35))
    
    # Схема мініатюрна
    p.append(rect(x1 + 20, y1 + 105, qw - 40, 105, fill="#ffffff", stroke="#93c5fd", sw=1, rx=4))
    p.append(text(x1 + qw / 2, y1 + 125, "VDD (3.3V) ──[ R_top ]──●──[ R_bot ]── GND", size=11, color="#1e293b", bold=True))
    p.append(text(x1 + qw / 2, y1 + 145, "                      │", size=11, color="#1e293b"))
    p.append(text(x1 + qw / 2, y1 + 160, "                      └──[ 100nF ]── ADC_IN (STM32/ESP32)", size=10.5, color="#1d4ed8"))
    p.append(text(x1 + qw / 2, y1 + 185, "Rev A: 0.0V (0x000)  •  Rev B: 1.65V (0x800)  •  Rev C: 3.3V (0xFFF)", size=10, color=MUTED))
    
    # 2. Strapping GPIO піни (верхній правий)
    x2, y2 = 510, 60
    p.append(rect(x2, y2, qw, qh, fill="#f8fafc", stroke="#8b5cf6", sw=1.4, rx=6))
    p.append(text(x2 + qw / 2, y1 + 24, "2. Цифрові піни конфігурації (Strapping GPIO)", size=13, color="#6d28d9", bold=True))
    p.append(mtext(x2 + qw / 2, y1 + 50, [
        "• 2–3 цифрових піни з підтяжками Pull-Up (1) або Pull-Down (0)",
        "• Зчитування бінарного коду в перші мікросекунди після Reset",
        "• Переведення пінів у High-Z або мультиплексування для виключення витоку"
    ], size=10.5, color=INK, lh=1.35))
    
    # Схема мініатюрна
    p.append(rect(x2 + 20, y1 + 105, qw - 40, 105, fill="#ffffff", stroke="#c4b5fd", sw=1, rx=4))
    p.append(text(x2 + qw / 2, y1 + 128, "[ GPIO_0 ] ── 10k до VDD (Bit 0 = 1)", size=11, color="#1e293b"))
    p.append(text(x2 + qw / 2, y1 + 150, "[ GPIO_1 ] ── 10k до GND (Bit 1 = 0)", size=11, color="#1e293b"))
    p.append(text(x2 + qw / 2, y1 + 172, "[ GPIO_2 ] ── 10k до VDD (Bit 2 = 1)", size=11, color="#1e293b"))
    p.append(text(x2 + qw / 2, y1 + 195, "Бінарний код: [1, 0, 1] = 0x05 ──> Ревізія Rev E", size=10.5, color="#6d28d9", bold=True))
    
    # 3. I2C/SPI Board ID EEPROM / OTP (нижній лівий)
    x3, y3 = 30, 295
    p.append(rect(x3, y3, qw, qh, fill="#f8fafc", stroke="#059669", sw=1.4, rx=6))
    p.append(text(x3 + qw / 2, y3 + 24, "3. Dedicated Board ID EEPROM / OTP пам'ять", size=13, color="#047857", bold=True))
    p.append(mtext(x3 + qw / 2, y3 + 50, [
        "• Окрема мікросхема 24C02 або блок One-Time Programmable (OTP) у MCU",
        "• Прошивається на стенді ATE під час вихідного заводського контролю",
        "• Зберігає структуру TLV: PCB Rev, BOM Variant, серійний номер, MAC-адресу"
    ], size=10.5, color=INK, lh=1.35))
    
    # Схема мініатюрна
    p.append(rect(x3 + 20, y3 + 105, qw - 40, 105, fill="#ffffff", stroke="#6ee7b7", sw=1, rx=4))
    p.append(text(x3 + qw / 2, y3 + 125, "Структура TLV (Type-Length-Value) у пам'яті:", size=11, color="#047857", bold=True))
    p.append(text(x3 + qw / 2, y3 + 148, "[ Tag 0x01: Magic 0xAA55 ] [ Tag 0x02: HW Rev = 0x02 (Rev B) ]", size=10.5, color="#1e293b"))
    p.append(text(x3 + qw / 2, y3 + 168, "[ Tag 0x03: BOM = 0x01 (No GPS) ] [ Tag 0x04: Calib Offsets... ]", size=10.5, color="#1e293b"))
    p.append(text(x3 + qw / 2, y3 + 190, "[ CRC-16 / SHA-256 Signature ] ──> Захист від пошкодження", size=10, color=MUTED))
    
    # 4. Device Tree Overlays (нижній правий)
    x4, y4 = 510, 295
    p.append(rect(x4, y4, qw, qh, fill="#f8fafc", stroke="#d97706", sw=1.4, rx=6))
    p.append(text(x4 + qw / 2, y4 + 24, "4. Device Tree Overlays (Linux / U-Boot)", size=13, color="#b45309", bold=True))
    p.append(mtext(x4 + qw / 2, y4 + 50, [
        "• Стандарт для Embedded Linux систем (Raspberry Pi CM4, i.MX8, STM32MP1)",
        "• Базовий образ ядра Linux однаковий для всіх ревізій",
        "• Завантажувач U-Boot читає Board ID і динамічно накладає dtbo-оверлей"
    ], size=10.5, color=INK, lh=1.35))
    
    # Схема мініатюрна
    p.append(rect(x4 + 20, y4 + 105, qw - 40, 105, fill="#ffffff", stroke="#fde68a", sw=1, rx=4))
    p.append(text(x4 + qw / 2, y4 + 125, "U-Boot зчитує Board ID: 0x03 ──> Вибирає оверлей:", size=11, color="#b45309", bold=True))
    p.append(text(x4 + qw / 2, y4 + 148, "base-board.dtb + board-revC-sensors.dtbo", size=10.5, color="#1e293b"))
    p.append(text(x4 + qw / 2, y4 + 168, "Патчинг дерева пристроїв у RAM перед запуском zImage", size=10.5, color="#1e293b"))
    p.append(text(x4 + qw / 2, y4 + 190, "Ядро бачить суворо релевантний список I2C/SPI шин та IRQ ліній", size=10, color=MUTED))
    
    render(os.path.join(OUT, "board-revision-detection-mechanisms.svg"), W, H, *p)

# ── Фіг. 3: Послідовність ранньої ініціалізації ────────────────────────────────
def fig_early_boot_initialization_sequence():
    W, H = 1000, 480
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 34, "Послідовність завантаження та динамічної конфігурації (Boot Flow)", size=15, color=INK, bold=True))
    
    # 5 послідовних фаз
    steps = [
        ("Phase 0: Reset Vector", "Вектор скидання, копіювання\n.data в SRAM, обнулення .bss,\nстарт внутрішнього RC-генератора", "#eff6ff", "#2563eb"),
        ("Phase 1: Board Sniffing", "Зчитування ADC дільника або\nStrapping пінів примітивним\nнеблокуючим драйвером", "#fdf4ff", "#c026d3"),
        ("Phase 2: Table Lookup", "Пошук ревізії у статичній\nтаблиці board_desc_table[].\nВерифікація підтримуваності", "#fffbeb", "#d97706"),
        ("Phase 3: Pinmux & Power", "Реконфігурація GPIO матриці,\nувімкнення стабілізаторів живлення\nдля сенсорів цієї ревізії", "#ecfdf5", "#059669"),
        ("Phase 4: Driver Binding", "Прив'язка драйверів (VTable),\nініціалізація BMI160/270, Flash,\nстарт бізнес-логіки", "#f8fafc", "#475569")
    ]
    
    step_w = 170
    step_h = 140
    gap = 22
    start_x = 28
    y_pos = 90
    
    for i, (title, desc, fill_c, stroke_c) in enumerate(steps):
        x = start_x + i * (step_w + gap)
        p.append(rect(x, y_pos, step_w, step_h, fill=fill_c, stroke=stroke_c, sw=1.6, rx=6))
        p.append(text(x + step_w / 2, y_pos + 24, title, size=11, color=stroke_c, bold=True))
        p.append(mtext(x + step_w / 2, y_pos + 52, desc.split("\n"), size=9.5, color=INK, lh=1.35))
        
        if i < len(steps) - 1:
            p.append(arrow(x + step_w + 3, y_pos + step_h / 2, x + step_w + gap - 3, y_pos + step_h / 2, color=LINE, sw=1.8))
            
    # Нижня частина: Гарантії безпеки та обробка крайових випадків
    p.append(rect(28, 260, W - 56, 185, fill="#fafafa", stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(W / 2, 285, "Захисні механізми на етапі запуску (Fail-Safe Guards)", size=13, color=INK, bold=True))
    
    guard_w = 290
    guard_h = 120
    
    # Guard 1
    g1_x = 48
    p.append(rect(g1_x, 305, guard_w, guard_h, fill="#ffffff", stroke="#ef4444", sw=1.2, rx=4))
    p.append(text(g1_x + guard_w / 2, 325, "1. Невідомий Board ID", size=11.5, color="#b91c1c", bold=True))
    p.append(mtext(g1_x + guard_w / 2, 348, [
        "Якщо ADC повернув значення поза",
        "дозволеними вікнами або ревізія",
        "новіша за підтримувану прошивкою:",
        "──> Перехід у Safe Recovery Mode"
    ], size=10, color=INK, lh=1.35))
    
    # Guard 2
    g2_x = 354
    p.append(rect(g2_x, 305, guard_w, guard_h, fill="#ffffff", stroke="#f59e0b", sw=1.2, rx=4))
    p.append(text(g2_x + guard_w / 2, 325, "2. Затримка стабілізації VDD", size=11.5, color="#b45309", bold=True))
    p.append(mtext(g2_x + guard_w / 2, 348, [
        "ADC не опитується до завершення",
        "наростання напруги живлення Vref.",
        "Апаратний Power-On-Reset + delay",
        "──> Виключає випадковий збій ID"
    ], size=10, color=INK, lh=1.35))
    
    # Guard 3
    g3_x = 660
    p.append(rect(g3_x, 305, guard_w, guard_h, fill="#ffffff", stroke="#10b981", sw=1.2, rx=4))
    p.append(text(g3_x + guard_w / 2, 325, "3. Zero-Allocation VTable", size=11.5, color="#047857", bold=True))
    p.append(mtext(g3_x + guard_w / 2, 348, [
        "Усі таблиці драйверів розміщені",
        "у Flash (секція .rodata). Жодного",
        "динамічного malloc() у runtime.",
        "──> Детерміністичний час старту"
    ], size=10, color=INK, lh=1.35))
    
    render(os.path.join(OUT, "early-boot-initialization-sequence.svg"), W, H, *p)

# ── Фіг. 4: Архітектура поліморфних драйверів та таблиць операцій ──────────────
def fig_polymorphic_driver_architecture():
    W, H = 1000, 520
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(W / 2, 34, "Архітектура поліморфного зв'язування драйверів (Driver VTable & Ops Pattern)", size=15, color=INK, bold=True))
    
    # Рівень 1: Бізнес-логіка (зверху)
    p.append(rect(250, 60, 500, 50, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=6))
    p.append(text(500, 82, "Рівень застосунку (Application Logic / Control Loop)", size=12.5, color="#1d4ed8", bold=True))
    p.append(text(500, 99, "imu_read_accel(&data);   flash_erase_sector(addr);", size=10.5, color=INK))
    
    p.append(arrow(500, 115, 500, 145, color=LINE, sw=1.8))
    
    # Рівень 2: Диспетчер апаратних абстракцій
    p.append(rect(200, 148, 600, 65, fill="#fdf4ff", stroke="#c026d3", sw=1.5, rx=6))
    p.append(text(500, 170, "Диспетчер ревізій та шар абстракцій (HAL / Board Manager)", size=12.5, color="#c026d3", bold=True))
    p.append(text(500, 192, "Структура board_ctx містить активні вказівники: imu_ops_t *imu, flash_ops_t *flash", size=10.5, color=INK))
    
    # Розгалуження стрілок від диспетчера вниз до таблиць
    p.append(arrow(350, 218, 250, 258, color=LINE, sw=1.6))
    p.append(arrow(650, 218, 750, 258, color=LINE, sw=1.6))
    
    p.append(text(270, 235, "Ревізія Rev A", size=10, color=MUTED))
    p.append(text(730, 235, "Ревізія Rev B / Rev C", size=10, color=MUTED))
    
    # Ліва гілка: Драйвери для Rev A
    p.append(rect(40, 262, 430, 225, fill="#f8fafc", stroke="#94a3b8", sw=1.4, rx=6))
    p.append(text(255, 286, "Конфігурація Rev A (2023)", size=12, color="#334155", bold=True))
    
    p.append(rect(60, 305, 390, 75, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(255, 325, "Драйвер IMU: Bosch BMI160", size=11, color="#1e293b", bold=True))
    p.append(mtext(255, 345, [
        "• I2C адреса: 0x68 (провідний пін SDO=GND)",
        "• SPI Chip Select: GPIOA_Pin_4",
        "• Таблиця ops: bmi160_init, bmi160_read, bmi160_sleep"
    ], size=9.5, color=INK, lh=1.3))
    
    p.append(rect(60, 395, 390, 75, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(255, 415, "Драйвер Flash: Winbond W25Q128", size=11, color="#1e293b", bold=True))
    p.append(mtext(255, 435, [
        "• JEDEC ID: 0xEF4018 (Quad-SPI Dummy Cycles = 6)",
        "• Розмір сектора: 4 КБ, розмір блоку: 64 КБ",
        "• Таблиця ops: w25q_init, w25q_read, w25q_write"
    ], size=9.5, color=INK, lh=1.3))
    
    # Права гілка: Драйвери для Rev B / C
    p.append(rect(530, 262, 430, 225, fill="#f0fdf4", stroke="#86efac", sw=1.4, rx=6))
    p.append(text(745, 286, "Конфігурація Rev B / Rev C (2024–2025)", size=12, color="#166534", bold=True))
    
    p.append(rect(550, 305, 390, 75, fill="#ffffff", stroke="#bbf7d0", sw=1.2, rx=4))
    p.append(text(745, 325, "Драйвер IMU: Bosch BMI270", size=11, color="#166534", bold=True))
    p.append(mtext(745, 345, [
        "• I2C адреса: 0x69 (SDO=VDD) / SPI CS: GPIOC_Pin_13",
        "• Завантаження фірмового мікрокоду ініціалізації в ASIC",
        "• Таблиця ops: bmi270_init, bmi270_read, bmi270_sleep"
    ], size=9.5, color=INK, lh=1.3))
    
    p.append(rect(550, 395, 390, 75, fill="#ffffff", stroke="#bbf7d0", sw=1.2, rx=4))
    p.append(text(745, 415, "Драйвер Flash: Macronix MX25L128", size=11, color="#166534", bold=True))
    p.append(mtext(745, 435, [
        "• JEDEC ID: 0xC22018 (Quad-SPI Dummy Cycles = 8)",
        "• Змінені таймінги підтяжки та регістри конфігурації QPI",
        "• Таблиця ops: mx25l_init, mx25l_read, mx25l_write"
    ], size=9.5, color=INK, lh=1.3))
    
    render(os.path.join(OUT, "polymorphic-driver-architecture.svg"), W, H, *p)

if __name__ == "__main__":
    fig_single_binary_vs_multi_binary()
    fig_board_revision_detection_mechanisms()
    fig_early_boot_initialization_sequence()
    fig_polymorphic_driver_architecture()
    print("All figures generated successfully.")

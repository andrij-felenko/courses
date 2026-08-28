# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Архітектура апаратного стенда інжекції збоїв живлення ─────────────
def fig_power_cut_hardware_harness():
    W, H = 1040, 590
    p = []

    # Загальне тло
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Архітектура автоматизованого стенда інжекції збоїв живлення (Power-Cut)", size=16, color="#0f172a", bold=True))
    p.append(text(W / 2, 58, "Високошвидкісний комутатор, активний розряд шини та цифровий бар'єр проти фантомного живлення", size=11, color="#64748b"))

    # Блок 1: Хост тестування (Runner / CI Host)
    hx, hy, hw, hh = 30, 85, 230, 475
    p.append(rect(hx, hy, hw, hh, fill="#f8fafc", stroke="#6366f1", sw=1.5, rx=6))
    p.append(text(hx + hw / 2, hy + 26, "Хост тестування (CI / Runner)", size=13, color="#4338ca", bold=True))
    p.append(text(hx + hw / 2, hy + 44, "Python / Orchestrator", size=9.5, color="#64748b"))

    p.append(rect(hx + 15, hy + 60, hw - 30, 115, fill="#ffffff", stroke="#818cf8", sw=1.1, rx=4))
    p.append(text(hx + hw / 2, hy + 80, "Генератор сценаріїв", size=11, color="#3730a3", bold=True))
    p.append(text(hx + hw / 2, hy + 100, "• Псевдовипадковий зсув", size=9.5, color="#334155"))
    p.append(text(hx + hw / 2, hy + 120, "• Просторове сканування", size=9.5, color="#334155"))
    p.append(text(hx + hw / 2, hy + 140, "• Розрахунок фази запису", size=9.5, color="#334155"))
    p.append(text(hx + hw / 2, hy + 158, "• Крок: 1 мкс .. 100 мс", size=9, color="#64748b"))

    p.append(rect(hx + 15, hy + 190, hw - 30, 130, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(hx + hw / 2, hy + 210, "Оракул цілісності", size=11, color="#475569", bold=True))
    p.append(text(hx + hw / 2, hy + 230, "• Валідація CRC розділів", size=9.5, color="#334155"))
    p.append(text(hx + hw / 2, hy + 250, "• Аудит стану LittleFS/UBIFS", size=9.5, color="#334155"))
    p.append(text(hx + hw / 2, hy + 270, "• Детекція Bootloop / Brick", size=9.5, color="#dc2626"))
    p.append(text(hx + hw / 2, hy + 290, "• Перевірка відкату (Rollback)", size=9.5, color="#15803d"))
    p.append(text(hx + hw / 2, hy + 308, "• Логування часових міток", size=9, color="#64748b"))

    p.append(rect(hx + 15, hy + 335, hw - 30, 115, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(hx + hw / 2, hy + 355, "Інтерфейси зв'язку", size=11, color="#475569", bold=True))
    p.append(text(hx + hw / 2, hy + 375, "USB / VCP (Команди)", size=9.5, color="#4338ca"))
    p.append(text(hx + hw / 2, hy + 395, "UART (Логи цілі)", size=9.5, color="#059669"))
    p.append(text(hx + hw / 2, hy + 415, "SWD / JTAG (Прошивка)", size=9.5, color="#64748b"))
    p.append(text(hx + hw / 2, hy + 435, "TCP/IP (CI Агент)", size=9, color="#64748b"))

    # Блок 2: Контролер стенда (Harness Controller)
    cx, cy, cw, ch = 290, 85, 380, 475
    p.append(rect(cx, cy, cw, ch, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=6))
    p.append(text(cx + cw / 2, cy + 26, "Апаратний стенд переривання живлення", size=13.5, color="#1d4ed8", bold=True))
    p.append(text(cx + cw / 2, cy + 44, "Мікроконтролерний модуль + Швидкісні ключі MOSFET", size=9.5, color="#64748b"))

    # Підблок MCU
    p.append(rect(cx + 15, cy + 60, cw - 30, 120, fill="#ffffff", stroke="#3b82f6", sw=1.2, rx=4))
    p.append(text(cx + cw / 2, cy + 80, "Мікроконтролер керування (STM32 / RP2040)", size=11, color="#1e40af", bold=True))
    p.append(text(cx + cw / 2, cy + 100, "• Апаратний таймер мікросекундних пауз (TIM2, 32-bit, 1 мкс)", size=9.5, color="#334155"))
    p.append(text(cx + cw / 2, cy + 120, "• Вхід зовнішнього тригера з DUT (GPIO EXTI / Capture)", size=9.5, color="#0284c7"))
    p.append(text(cx + cw / 2, cy + 140, "• Формувач комплементарних сигналів комутації", size=9.5, color="#334155"))
    p.append(text(cx + cw / 2, cy + 160, "• Лічильник циклів і моніторинг струму споживання", size=9.5, color="#64748b"))

    # Підблок силової частини
    p.append(rect(cx + 15, cy + 195, cw - 30, 130, fill="#fef2f2", stroke="#ef4444", sw=1.2, rx=4))
    p.append(text(cx + cw / 2, cy + 215, "Силовий каскад швидкісного знеструмлення", size=11, color="#991b1b", bold=True))
    p.append(text(cx + cw / 2, cy + 235, "P-MOSFET верхнього плеча (High-Side): R_ds < 15 мОм, t_off < 200 нс", size=9.5, color="#334155"))
    p.append(text(cx + cw / 2, cy + 255, "Активний розряд (Active Crowbar N-MOSFET + 2.2 Ом на землю)", size=9.5, color="#b91c1c"))
    p.append(text(cx + cw / 2, cy + 275, "Швидкість спаду шини: dV/dt > 10 В/мкс (злив заряду ємностей DUT)", size=9.5, color="#334155"))
    p.append(text(cx + cw / 2, cy + 295, "Захист від наскрізного струму (Dead-Time Generator: 50 нс)", size=9.5, color="#64748b"))

    # Підблок ізоляції
    p.append(rect(cx + 15, cy + 340, cw - 30, 120, fill="#f0fdf4", stroke="#16a34a", sw=1.2, rx=4))
    p.append(text(cx + cw / 2, cy + 360, "Бар'єр захисту від паразитного живлення", size=11, color="#15803d", bold=True))
    p.append(text(cx + cw / 2, cy + 380, "Цифрові ізолятори (ISO7741 / ADuM140) на UART, SWD, GPIO", size=9.5, color="#334155"))
    p.append(text(cx + cw / 2, cy + 400, "Блокування струму витоку крізь ESD-діоди мікроконтролера", size=9.5, color="#166534"))
    p.append(text(cx + cw / 2, cy + 420, "Відключення підтяжок (Pull-up) під час фази знеструмлення", size=9.5, color="#334155"))
    p.append(text(cx + cw / 2, cy + 440, "Гальванічна розв'язка вимірювальних кіл", size=9.5, color="#64748b"))

    # Блок 3: Цільовий пристрій (DUT)
    dx, dy, dw, dh = 700, 85, 310, 475
    p.append(rect(dx, dy, dw, dh, fill="#fffbeb", stroke="#d97706", sw=1.6, rx=6))
    p.append(text(dx + dw / 2, dy + 26, "Цільовий пристрій (DUT)", size=13.5, color="#b45309", bold=True))
    p.append(text(dx + dw / 2, dy + 44, "MCU + Flash + Периферія", size=9.5, color="#64748b"))

    p.append(rect(dx + 15, dy + 60, dw - 30, 115, fill="#ffffff", stroke="#f59e0b", sw=1.1, rx=4))
    p.append(text(dx + dw / 2, dy + 80, "Flash-пам'ять під навантаженням", size=11, color="#92400e", bold=True))
    p.append(text(dx + dw / 2, dy + 100, "• SPI NOR (W25Q128) / NAND", size=9.5, color="#334155"))
    p.append(text(dx + dw / 2, dy + 120, "• Стирання блоку (400 мс)", size=9.5, color="#dc2626"))
    p.append(text(dx + dw / 2, dy + 140, "• Запис сторінки (300 мкс)", size=9.5, color="#334155"))
    p.append(text(dx + dw / 2, dy + 158, "• Зона ризику: Torn Write", size=9, color="#b45309"))

    p.append(rect(dx + 15, dy + 190, dw - 30, 130, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(dx + dw / 2, dy + 210, "Критичні підсистеми", size=11, color="#475569", bold=True))
    p.append(text(dx + dw / 2, dy + 230, "• Завантажувач (Bootloader A/B)", size=9.5, color="#334155"))
    p.append(text(dx + dw / 2, dy + 250, "• Файлова система LittleFS", size=9.5, color="#334155"))
    p.append(text(dx + dw / 2, dy + 270, "• Енергонезалежні налаштування NVS", size=9.5, color="#334155"))
    p.append(text(dx + dw / 2, dy + 290, "• Таблиця розділів Flash", size=9.5, color="#64748b"))
    p.append(text(dx + dw / 2, dy + 308, "• Регістри статусу Write-In-Progress", size=9, color="#64748b"))

    p.append(rect(dx + 15, dy + 335, dw - 30, 115, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(dx + dw / 2, dy + 355, "Сигнали та контури", size=11, color="#475569", bold=True))
    p.append(text(dx + dw / 2, dy + 375, "V_DD (Керована шина живлення)", size=9.5, color="#dc2626"))
    p.append(text(dx + dw / 2, dy + 395, "GPIO Trigger (Синхронізація)", size=9.5, color="#0284c7"))
    p.append(text(dx + dw / 2, dy + 415, "UART Console (Телеметрія)", size=9.5, color="#059669"))
    p.append(text(dx + dw / 2, dy + 435, "BOR (Brown-out Reset поріг)", size=9.5, color="#64748b"))

    # З'єднувальні стрілки між блоками
    p.append(arrow(hx + hw, hy + 115, cx, cy + 115, color="#6366f1", sw=1.8))
    p.append(arrow(hx + hw, hy + 395, cx, cy + 395, color="#16a34a", sw=1.8))
    p.append(arrow(cx + cw, cy + 260, dx, dy + 375, color="#dc2626", sw=2.0))
    p.append(arrow(dx, dy + 395, cx + cw, cy + 120, color="#0284c7", sw=1.8))
    p.append(arrow(dx, dy + 415, cx + cw, cy + 415, color="#059669", sw=1.8))

    render(os.path.join(OUT, "power-cut-hardware-harness.svg"), W, H, *p)

# ── Фіг. 2: Фізика збою Flash-пам'яті та вікно метастабільності ────────────────
def fig_flash_state_transitions_and_corruption():
    W, H = 1040, 540
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Фізика збою Flash-пам'яті: часові масштаби операцій та вікно метастабільності", size=16, color="#0f172a", bold=True))
    p.append(text(W / 2, 58, "Колапс зарядового насоса, розрив транзакції стирання та утворення нестабільних бітів", size=11, color="#64748b"))

    # Панель 1: Часові масштаби операцій NOR/NAND Flash
    p.append(rect(30, 85, 980, 130, fill="#f8fafc", stroke="#94a3b8", sw=1.3, rx=6))
    p.append(text(520, 108, "Ієрархія тривалості операцій кремнієвого накопичувача (NOR / NAND Flash)", size=12.5, color="#1e293b", bold=True))

    # Смуга читання
    p.append(rect(50, 125, 160, 45, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=4))
    p.append(text(130, 144, "Читання байта/слова", size=10.5, color="#0369a1", bold=True))
    p.append(text(130, 160, "20 – 50 нс (Безпечно)", size=9.5, color="#0c4a6e"))

    # Смуга запису сторінки
    p.append(rect(230, 125, 240, 45, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(350, 144, "Програмування сторінки (Page)", size=10.5, color="#b45309", bold=True))
    p.append(text(350, 160, "100 – 400 мкс (Вікно Torn Write)", size=9.5, color="#78350f"))

    # Смуга стирання сектору
    p.append(rect(490, 125, 500, 45, fill="#fee2e2", stroke="#ef4444", sw=1.3, rx=4))
    p.append(text(740, 144, "Стирання сектора / блоку (Sector Erase, 4 КБ – 64 КБ)", size=10.5, color="#b91c1c", bold=True))
    p.append(text(740, 160, "20 – 400 мс: Критична зона високовольтного тунелювання заряду (12-18 В)", size=9.5, color="#991b1b"))

    p.append(text(520, 198, "Асиметрія: стирання триває у 1000 разів довше за запис — 95% обривів живлення вражають саме його", size=10, color="#475569", bold=True))

    # Панель 2: Графік спаду напруги V_DD та поведінка зарядового насоса
    gx, gy, gw, gh = 30, 235, 470, 280
    p.append(rect(gx, gy, gw, gh, fill="#fafaf9", stroke="#78716c", sw=1.3, rx=6))
    p.append(text(gx + gw / 2, gy + 24, "Динаміка напруги живлення та колапс Flash", size=12.5, color="#292524", bold=True))

    # Осі
    p.append(line(gx + 45, gy + 230, gx + gw - 25, gy + 230, color="#44403c", sw=1.5))
    p.append(line(gx + 45, gy + 45, gx + 45, gy + 230, color="#44403c", sw=1.5))
    p.append(text(gx + gw - 25, gy + 246, "Час (t)", size=10, color="#44403c", anchor="end"))
    p.append(text(gx + 40, gy + 55, "V_DD (В)", size=10, color="#44403c", anchor="end"))

    # Порогові лінії
    p.append(line(gx + 45, gy + 80, gx + gw - 25, gy + 80, color="#16a34a", sw=1.0, dash="4,4"))
    p.append(text(gx + 40, gy + 84, "3.3 В (Номінал)", size=9, color="#15803d", anchor="end"))

    p.append(line(gx + 45, gy + 130, gx + gw - 25, gy + 130, color="#d97706", sw=1.0, dash="4,4"))
    p.append(text(gx + 40, gy + 134, "2.7 В (BOR Поріг)", size=9, color="#b45309", anchor="end"))

    p.append(line(gx + 45, gy + 180, gx + gw - 25, gy + 180, color="#dc2626", sw=1.0, dash="4,4"))
    p.append(text(gx + 40, gy + 184, "2.0 В (Колапс V_PP)", size=9, color="#b91c1c", anchor="end"))

    # Крива знеструмлення
    p.append(line(gx + 45, gy + 80, gx + 150, gy + 80, color="#2563eb", sw=2.2))
    p.append(line(gx + 150, gy + 80, gx + 230, gy + 180, color="#ea580c", sw=2.2))
    p.append(line(gx + 230, gy + 180, gx + 270, gy + 230, color="#dc2626", sw=2.2))
    p.append(line(gx + 270, gy + 230, gx + gw - 25, gy + 230, color="#dc2626", sw=2.2))

    p.append(text(gx + 150, gy + 70, "Команда 0x20 (Erase)", size=9, color="#1d4ed8", bold=True))
    p.append(text(gx + 210, gy + 150, "Brownout фаза", size=9, color="#ea580c", bold=True))
    p.append(text(gx + 320, gy + 215, "0 В (Повне знеструмлення)", size=9, color="#dc2626"))

    # Панель 3: Стан комірок Flash пам'яті (Floating Gate)
    mx, my, mw, mh = 520, 235, 490, 280
    p.append(rect(mx, my, mw, mh, fill="#f8fafc", stroke="#64748b", sw=1.3, rx=6))
    p.append(text(mx + mw / 2, my + 24, "Трансформація стану напівпровідникової комірки", size=12.5, color="#0f172a", bold=True))

    # Стан 1: Стерто
    p.append(rect(mx + 20, my + 50, mw - 40, 60, fill="#f0fdf4", stroke="#16a34a", sw=1.2, rx=4))
    p.append(text(mx + 30, my + 72, "Стертий сектор (0xFF)", size=11, color="#15803d", bold=True, anchor="start"))
    p.append(text(mx + 30, my + 92, "Усі електрони видалені з плаваючого затвора. Порогова напруга V_th низька.", size=9.5, color="#334155", anchor="start"))

    # Стан 2: Метастабільність / Torn
    p.append(rect(mx + 20, my + 120, mw - 40, 75, fill="#fee2e2", stroke="#ef4444", sw=1.3, rx=4))
    p.append(text(mx + 30, my + 142, "Метастабільний стан (Torn Write / Half-Erased)", size=11, color="#b91c1c", bold=True, anchor="start"))
    p.append(text(mx + 30, my + 162, "Зарядовий насос згас на середині тунелювання. V_th знаходиться рівно", size=9.5, color="#7f1d1d", anchor="start"))
    p.append(text(mx + 30, my + 178, "на межі компаратора читання. Байт читається як 0 або 1 залежно від температури.", size=9.5, color="#7f1d1d", anchor="start"))

    # Стан 3: Записано
    p.append(rect(mx + 20, my + 205, mw - 40, 60, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=4))
    p.append(text(mx + 30, my + 227, "Коректно записані дані (0x00..0xFE)", size=11, color="#1d4ed8", bold=True, anchor="start"))
    p.append(text(mx + 30, my + 247, "Фіксований інжектований заряд, валідний CRC32 сторінки.", size=9.5, color="#334155", anchor="start"))

    render(os.path.join(OUT, "flash-state-transitions-and-corruption.svg"), W, H, *p)

# ── Фіг. 3: Атомарне перемикання A/B слотів під час обриву живлення ───────────
def fig_ab_partition_powercut_resilience():
    W, H = 1040, 550
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Атомарне перемикання A/B-слотів під час обриву живлення", size=16, color="#0f172a", bold=True))
    p.append(text(W / 2, 58, "Двобанкова схема прошивки, маркери стану завантажувача та безпечний відкат (Rollback)", size=11, color="#64748b"))

    # Блок Завантажувача (Bootloader & Meta)
    bx, by, bw, bh = 30, 85, 270, 440
    p.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke="#475569", sw=1.5, rx=6))
    p.append(text(bx + bw / 2, by + 26, "Завантажувальний сектор (MCUboot)", size=12.5, color="#1e293b", bold=True))
    p.append(text(bx + bw / 2, by + 44, "ROM / Первинний Bootloader (Фіксований)", size=9.5, color="#64748b"))

    p.append(rect(bx + 15, by + 65, bw - 30, 170, fill="#ffffff", stroke="#64748b", sw=1.1, rx=4))
    p.append(text(bx + bw / 2, by + 86, "Таблиця стану OTA (Metadata)", size=11, color="#0f172a", bold=True))
    p.append(text(bx + bw / 2, by + 106, "• Active Slot: SLOT_A (v1.0)", size=9.5, color="#059669", bold=True))
    p.append(text(bx + bw / 2, by + 126, "• Target Slot: SLOT_B (v2.0)", size=9.5, color="#d97706"))
    p.append(text(bx + bw / 2, by + 146, "• State: UPDATING (0x01)", size=9.5, color="#dc2626"))
    p.append(text(bx + bw / 2, by + 166, "• CRC32 Expected: 0x8F3C21A4", size=9.5, color="#334155"))
    p.append(text(bx + bw / 2, by + 186, "• Boot Attempts Left: 3", size=9.5, color="#334155"))
    p.append(text(bx + bw / 2, by + 206, "• Magic Header: 0x544F4F42", size=9.5, color="#64748b"))

    p.append(rect(bx + 15, by + 255, bw - 30, 155, fill="#fef2f2", stroke="#ef4444", sw=1.1, rx=4))
    p.append(text(bx + bw / 2, by + 276, "Логіка верифікації при рестарті", size=11, color="#991b1b", bold=True))
    p.append(text(bx + bw / 2, by + 296, "1. Читання маркерів OTA метаданих", size=9.5, color="#334155"))
    p.append(text(bx + bw / 2, by + 316, "2. Перевірка цілісності слота B", size=9.5, color="#334155"))
    p.append(text(bx + bw / 2, by + 336, "3. CRC32 пошкоджено? (Обрив)", size=9.5, color="#b91c1c", bold=True))
    p.append(text(bx + bw / 2, by + 356, "4. Анулювання спроби запису", size=9.5, color="#334155"))
    p.append(text(bx + bw / 2, by + 376, "5. Атомарний запуск слота A", size=9.5, color="#15803d", bold=True))
    p.append(text(bx + bw / 2, by + 396, "Пристрій залишається працездатним", size=9, color="#15803d"))

    # Блок Слот А (Активний)
    ax, ay, aw, ah = 330, 85, 320, 440
    p.append(rect(ax, ay, aw, ah, fill="#f0fdf4", stroke="#16a34a", sw=1.6, rx=6))
    p.append(text(ax + aw / 2, ay + 26, "Слот A: Поточна стабільна версія (v1.0)", size=13, color="#15803d", bold=True))
    p.append(text(ax + aw / 2, ay + 44, "Flash адреса: 0x08020000 – 0x080A0000 (512 КБ)", size=9.5, color="#64748b"))

    p.append(rect(ax + 15, ay + 65, aw - 30, 110, fill="#ffffff", stroke="#22c55e", sw=1.2, rx=4))
    p.append(text(ax + aw / 2, ay + 86, "Заголовок образу (Image Header)", size=11, color="#166534", bold=True))
    p.append(text(ax + aw / 2, ay + 106, "• Версія: v1.0.4-release", size=9.5, color="#334155"))
    p.append(text(ax + aw / 2, ay + 126, "• Підпис ECDSA-256: Валідний", size=9.5, color="#15803d"))
    p.append(text(ax + aw / 2, ay + 146, "• CRC32: 0xA1B2C3D4 (Збігається)", size=9.5, color="#15803d"))
    p.append(text(ax + aw / 2, ay + 164, "• Прапорець: CONFIRMED", size=9.5, color="#166534", bold=True))

    p.append(rect(ax + 15, ay + 190, aw - 30, 220, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(ax + aw / 2, ay + 212, "Тіло прошивки (Vector Table + Code)", size=11, color="#334155", bold=True))
    p.append(text(ax + aw / 2, ay + 234, "Вектори переривань ARM Cortex-M", size=9.5, color="#475569"))
    p.append(text(ax + aw / 2, ay + 254, "Ядро операційної системи (FreeRTOS)", size=9.5, color="#475569"))
    p.append(text(ax + aw / 2, ay + 274, "Драйвери зв'язку та периметра безпеки", size=9.5, color="#475569"))
    p.append(text(ax + aw / 2, ay + 294, "Стек протоколів та бізнес-логіка", size=9.5, color="#475569"))
    p.append(text(ax + aw / 2, ay + 320, "Недоторканний банк під час оновлення!", size=10, color="#15803d", bold=True))
    p.append(text(ax + aw / 2, ay + 340, "Жоден біт слота A не змінюється, доки", size=9.5, color="#64748b"))
    p.append(text(ax + aw / 2, ay + 360, "новий образ не пройде повний POST тест.", size=9.5, color="#64748b"))
    p.append(text(ax + aw / 2, ay + 390, "Стан: СТАБІЛЬНИЙ / РОБОЧИЙ", size=10.5, color="#15803d", bold=True))

    # Блок Слот B (Оновлюється / Збійний)
    sx, sy, sw, sh = 680, 85, 330, 440
    p.append(rect(sx, sy, sw, sh, fill="#fff1f2", stroke="#e11d48", sw=1.6, rx=6))
    p.append(text(sx + sw / 2, sy + 26, "Слот B: Цільовий банк (v2.0) [ОБРИВ]", size=13, color="#be123c", bold=True))
    p.append(text(sx + sw / 2, sy + 44, "Flash адреса: 0x080A0000 – 0x08120000 (512 КБ)", size=9.5, color="#64748b"))

    p.append(rect(sx + 15, sy + 65, sw - 30, 110, fill="#ffffff", stroke="#f43f5e", sw=1.2, rx=4))
    p.append(text(sx + sw / 2, sy + 86, "Заголовок нового образу (v2.0.0)", size=11, color="#9f1239", bold=True))
    p.append(text(sx + sw / 2, sy + 106, "• Записано блоків: 64 з 128", size=9.5, color="#e11d48"))
    p.append(text(sx + sw / 2, sy + 126, "• Стан: Сектор 0x080E0000 недотертий", size=9.5, color="#e11d48", bold=True))
    p.append(text(sx + sw / 2, sy + 146, "• Обчислений CRC32: 0x00000000 (Помилка)", size=9.5, color="#dc2626"))
    p.append(text(sx + sw / 2, sy + 164, "• Прапорець: CORRUPTED_IMAGE", size=9.5, color="#9f1239", bold=True))

    p.append(rect(sx + 15, sy + 190, sw - 30, 220, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    p.append(text(sx + sw / 2, sy + 212, "Анатомія розриву (Power-Cut Impact)", size=11, color="#334155", bold=True))
    p.append(text(sx + sw / 2, sy + 234, "Блок 0–63: Валідний бінарний код v2.0", size=9.5, color="#059669"))
    p.append(text(sx + sw / 2, sy + 254, "Блок 64: Обрив напруги на 320 мкс стирання", size=9.5, color="#dc2626", bold=True))
    p.append(text(sx + sw / 2, sy + 274, "Блок 65–127: Залишки старої версії / 0xFF", size=9.5, color="#64748b"))
    p.append(text(sx + sw / 2, sy + 300, "Наслідок без A/B слотів:", size=10, color="#b91c1c", bold=True))
    p.append(text(sx + sw / 2, sy + 320, "Пристрій перетворюється на «цеглину».", size=9.5, color="#dc2626"))
    p.append(text(sx + sw / 2, sy + 340, "Наслідок з A/B схемою:", size=10, color="#15803d", bold=True))
    p.append(text(sx + sw / 2, sy + 360, "Bootloader ігнорує слот B і стартує слот A.", size=9.5, color="#15803d"))
    p.append(text(sx + sw / 2, sy + 390, "Стан: ВІДХИЛЕНО / ВІДКОЧЕНО", size=10.5, color="#be123c", bold=True))

    # Стрілки
    p.append(arrow(bx + bw, by + 130, ax, ay + 130, color="#16a34a", sw=1.8))
    p.append(arrow(bx + bw, by + 160, sx, sy + 160, color="#e11d48", sw=1.8))

    render(os.path.join(OUT, "ab-partition-powercut-resilience.svg"), W, H, *p)

# ── Фіг. 4: Скінченний автомат циклу інжекції збоїв у тестовому конвеєрі ───────
def fig_power_cut_test_cycle_fsm():
    W, H = 1040, 560
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(W / 2, 38, "Скінченний автомат циклу інжекції збоїв у тестовому конвеєрі", size=16, color="#0f172a", bold=True))
    p.append(text(W / 2, 58, "Послідовність синхронізації, генерації мікросекундного знеструмлення та валідації оракулом", size=11, color="#64748b"))

    # Стан 1: IDLE / ARMED
    s1_x, s1_y, s1_w, s1_h = 30, 100, 210, 160
    p.append(rect(s1_x, s1_y, s1_w, s1_h, fill="#f8fafc", stroke="#6366f1", sw=1.5, rx=6))
    p.append(text(s1_x + s1_w / 2, s1_y + 26, "1. ГОТОВНІСТЬ (IDLE)", size=12, color="#4338ca", bold=True))
    p.append(text(s1_x + s1_w / 2, s1_y + 50, "• V_DD увімкнено (3.3 В)", size=9.5, color="#334155"))
    p.append(text(s1_x + s1_w / 2, s1_y + 70, "• Цільовий пристрій працює", size=9.5, color="#334155"))
    p.append(text(s1_x + s1_w / 2, s1_y + 90, "• Очікування тригера запису", size=9.5, color="#6366f1", bold=True))
    p.append(text(s1_x + s1_w / 2, s1_y + 110, "• Розрахунок зміщення t_delay", size=9.5, color="#64748b"))
    p.append(text(s1_x + s1_w / 2, s1_y + 130, "t_delay ∈ [0 .. 400 000] мкс", size=9, color="#4338ca"))

    # Стан 2: TRIGGER_ARMED
    s2_x, s2_y, s2_w, s2_h = 285, 100, 220, 160
    p.append(rect(s2_x, s2_y, s2_w, s2_h, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=6))
    p.append(text(s2_x + s2_w / 2, s2_y + 26, "2. ТРИГЕР ТА ВІДЛІК", size=12, color="#1d4ed8", bold=True))
    p.append(text(s2_x + s2_w / 2, s2_y + 50, "• DUT подає GPIO HIGH імпульс", size=9.5, color="#0284c7", bold=True))
    p.append(text(s2_x + s2_w / 2, s2_y + 70, "• Запуск таймера TIM2", size=9.5, color="#334155"))
    p.append(text(s2_x + s2_w / 2, s2_y + 90, "• Точний апаратний відлік", size=9.5, color="#334155"))
    p.append(text(s2_x + s2_w / 2, s2_y + 110, "• Ціль пише у Flash пам'ять", size=9.5, color="#ea580c"))
    p.append(text(s2_x + s2_w / 2, s2_y + 130, "Δt похибка < 100 нс", size=9, color="#1d4ed8"))

    # Стан 3: POWER_CUT & DISCHARGE
    s3_x, s3_y, s3_w, s3_h = 550, 100, 220, 160
    p.append(rect(s3_x, s3_y, s3_w, s3_h, fill="#fef2f2", stroke="#ef4444", sw=1.6, rx=6))
    p.append(text(s3_x + s3_w / 2, s3_y + 26, "3. ЗНЕСТРУМЛЕННЯ (CUT)", size=12, color="#b91c1c", bold=True))
    p.append(text(s3_x + s3_w / 2, s3_y + 50, "• Розмикання P-MOSFET", size=9.5, color="#dc2626", bold=True))
    p.append(text(s3_x + s3_w / 2, s3_y + 70, "• Вмикання Active Crowbar", size=9.5, color="#b91c1c"))
    p.append(text(s3_x + s3_w / 2, s3_y + 90, "• Розряд шини за 800 нс", size=9.5, color="#334155"))
    p.append(text(s3_x + s3_w / 2, s3_y + 110, "• Ізоляція ліній UART/SWD", size=9.5, color="#334155"))
    p.append(text(s3_x + s3_w / 2, s3_y + 130, "Пауза знеструмлення: 50 мс", size=9, color="#b91c1c"))

    # Стан 4: POWER_RESTORE
    s4_x, s4_y, s4_w, s4_h = 810, 100, 200, 160
    p.append(rect(s4_x, s4_y, s4_w, s4_h, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(s4_x + s4_w / 2, s4_y + 26, "4. ВІДНОВЛЕННЯ", size=12, color="#b45309", bold=True))
    p.append(text(s4_x + s4_w / 2, s4_y + 50, "• Вимкнення Crowbar", size=9.5, color="#334155"))
    p.append(text(s4_x + s4_w / 2, s4_y + 70, "• Замикання P-MOSFET", size=9.5, color="#15803d"))
    p.append(text(s4_x + s4_w / 2, s4_y + 90, "• Подача 3.3 В на DUT", size=9.5, color="#334155"))
    p.append(text(s4_x + s4_w / 2, s4_y + 110, "• Старт Bootloader", size=9.5, color="#d97706", bold=True))
    p.append(text(s4_x + s4_w / 2, s4_y + 130, "Таймаут завантаження: 2 с", size=9, color="#b45309"))

    # Стан 5: HEALTH_AUDIT & ORACLE VERDICT (Нижній поверх)
    hx, hy, hw, hh = 150, 330, 740, 190
    p.append(rect(hx, hy, hw, hh, fill="#f8fafc", stroke="#059669", sw=1.6, rx=6))
    p.append(text(hx + hw / 2, hy + 26, "5. АУДИТ ЗДОРОВ'Я ТА ВЕРДИКТ ОРАКУЛА (HEALTH AUDIT)", size=13.5, color="#065f46", bold=True))

    # Три виходи вердикту
    p.append(rect(hx + 20, hy + 50, 215, 120, fill="#f0fdf4", stroke="#16a34a", sw=1.2, rx=4))
    p.append(text(hx + 127, hy + 72, "ВЕРДИКТ: УСПІХ (OK)", size=11, color="#15803d", bold=True))
    p.append(text(hx + 127, hy + 92, "• Відкат або відновлення FS", size=9.5, color="#334155"))
    p.append(text(hx + 127, hy + 110, "• Валідний CRC32 пам'яті", size=9.5, color="#166534"))
    p.append(text(hx + 127, hy + 128, "• Пристрій вийшов на зв'язок", size=9.5, color="#334155"))
    p.append(text(hx + 127, hy + 148, "→ Наступна ітерація зсуву", size=9.5, color="#15803d", bold=True))

    p.append(rect(hx + 260, hy + 50, 215, 120, fill="#fff1f2", stroke="#e11d48", sw=1.2, rx=4))
    p.append(text(hx + 367, hy + 72, "ВЕРДИКТ: ЦЕГЛИНА (BRICK)", size=11, color="#9f1239", bold=True))
    p.append(text(hx + 367, hy + 92, "• Bootloader завис / HardFault", size=9.5, color="#be123c"))
    p.append(text(hx + 367, hy + 110, "• Відсутній вивід у консоль", size=9.5, color="#334155"))
    p.append(text(hx + 367, hy + 128, "• Пошкодження таблиці A/B", size=9.5, color="#334155"))
    p.append(text(hx + 367, hy + 148, "→ СТОП ТЕСТ, ДЕФЕКТ CI!", size=9.5, color="#9f1239", bold=True))

    p.append(rect(hx + 500, hy + 50, 220, 120, fill="#fef2f2", stroke="#ef4444", sw=1.2, rx=4))
    p.append(text(hx + 610, hy + 72, "ВЕРДИКТ: SILENT DATA LOSS", size=11, color="#b91c1c", bold=True))
    p.append(text(hx + 610, hy + 92, "• Пристрій завантажився", size=9.5, color="#334155"))
    p.append(text(hx + 610, hy + 110, "• Але конфігурацію пошкоджено", size=9.5, color="#b91c1c"))
    p.append(text(hx + 610, hy + 128, "• Метастабільні байти Flash", size=9.5, color="#334155"))
    p.append(text(hx + 610, hy + 148, "→ СТОП ТЕСТ, КРИТИЧНО!", size=9.5, color="#b91c1c", bold=True))

    # З'єднувальні стрілки верхнього ланцюга
    p.append(arrow(s1_x + s1_w, s1_y + 80, s2_x, s2_y + 80, color="#6366f1", sw=1.8))
    p.append(arrow(s2_x + s2_w, s2_y + 80, s3_x, s3_y + 80, color="#2563eb", sw=1.8))
    p.append(arrow(s3_x + s3_w, s3_y + 80, s4_x, s4_y + 80, color="#ef4444", sw=1.8))

    # Стрілка переходу від відновлення до аудиту
    p.append(arrow(s4_x + s4_w / 2, s4_y + s4_h, hx + hw - 100, hy, color="#d97706", sw=1.8))

    # Зворотна стрілка успіху на новий цикл
    p.append(arrow(hx + 20, hy + 100, s1_x + s1_w / 2, s1_y + s1_h, color="#16a34a", sw=1.8))

    render(os.path.join(OUT, "power-cut-test-cycle-fsm.svg"), W, H, *p)

if __name__ == "__main__":
    fig_power_cut_hardware_harness()
    fig_flash_state_transitions_and_corruption()
    fig_ab_partition_powercut_resilience()
    fig_power_cut_test_cycle_fsm()
    print("Усі 4 фігури згенеровано успішно.")

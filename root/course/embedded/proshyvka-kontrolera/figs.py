# -*- coding: utf-8 -*-
"""Фігури до статті «Прошивка контролера: сімейства, версії, завантажувач, відкат».
Курс: embedded, розділ: polotnyi-kontroler.
Чистий Python, без зовнішніх бібліотек; генерація SVG через svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Порівняння архітектур польотних стеків (Betaflight vs ArduPilot vs PX4)
# ─────────────────────────────────────────────────────────────────────────────
def fig_flight_stacks():
    W, H = 1000, 520
    frags = []
    frags.append(text(W / 2, 36, "Архітектурні моделі польотного програмного забезпечення", size=15, bold=True))

    col_w = 290
    gap = 35
    x_starts = [45, 45 + col_w + gap, 45 + (col_w + gap) * 2]

    # Колонка 1: Betaflight (Bare-Metal Super-Loop)
    x1 = x_starts[0]
    frags.append(rect(x1, 60, col_w, 420, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    b, _, _ = textbox(x1 + col_w / 2, 85, "Betaflight (Bare-Metal)", size=13, bold=True, stroke=POS, fill="#fdecea", min_w=260)
    frags.append(b)
    frags.append(text(x1 + col_w / 2, 112, "Детермінований суперцикл реального часу", size=10, color=MUTED, italic=True))

    b1, _, _ = textbox(x1 + col_w / 2, 150, "IMU SPI DMA (8 kHz / 4 kHz)", size=11, bold=True, stroke=LINE, fill=FILL, min_w=250)
    frags.append(b1)
    frags.append(arrow(x1 + col_w / 2, 168, x1 + col_w / 2, 192))

    b2, _, _ = textbox(x1 + col_w / 2, 215, "PID Fast-Loop (синхронно з гіро)\nДжитер < 5 мкс, нульовий оверхед", size=10.5, stroke=POS, fill="#fff5f5", min_w=250)
    frags.append(b2)
    frags.append(arrow(x1 + col_w / 2, 238, x1 + col_w / 2, 262))

    b3, _, _ = textbox(x1 + col_w / 2, 285, "DShot DMA (таймерні імпульси)", size=11, bold=True, stroke=LINE, fill=FILL, min_w=250)
    frags.append(b3)
    frags.append(arrow(x1 + col_w / 2, 303, x1 + col_w / 2, 327))

    b4, _, _ = textbox(x1 + col_w / 2, 365, "Фоновий Task Scheduler:\n• OSD / VTX телеметрія (50 Гц)\n• RX RC-протокол (150-500 Гц)\n• Чорна скринька Flash (1-2 кГц)", size=10, stroke=LINE, fill=FILL, min_w=250)
    frags.append(b4)

    frags.append(text(x1 + col_w / 2, 455, "Пріоритет: реакція пілота та акробатика", size=10, color=POS, bold=True))

    # Колонка 2: ArduPilot (ChibiOS RTOS)
    x2 = x_starts[1]
    frags.append(rect(x2, 60, col_w, 420, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    b, _, _ = textbox(x2 + col_w / 2, 85, "ArduPilot (ChibiOS RTOS)", size=13, bold=True, stroke=FIELD, fill="#eafaf0", min_w=260)
    frags.append(b)
    frags.append(text(x2 + col_w / 2, 112, "Шар AP_HAL + витісняльні потоки RTOS", size=10, color=MUTED, italic=True))

    b1, _, _ = textbox(x2 + col_w / 2, 150, "AP_HAL (апаратна абстракція)", size=11, bold=True, stroke=LINE, fill=FILL, min_w=250)
    frags.append(b1)
    frags.append(arrow(x2 + col_w / 2, 168, x2 + col_w / 2, 192))

    b2, _, _ = textbox(x2 + col_w / 2, 215, "Fast-Loop (400-1000 Гц, RTOS High)\nRate / Attitude PID регулятори", size=10.5, stroke=FIELD, fill="#f4fbf7", min_w=250)
    frags.append(b2)

    # Паралельні потоки RTOS
    frags.append(rect(x2 + 15, 255, col_w - 30, 150, fill="#f8fafc", stroke=LINE, sw=1, rx=6))
    frags.append(text(x2 + col_w / 2, 272, "Витісняльні потоки ChibiOS:", size=10.5, bold=True, color=INK))
    frags.append(text(x2 + col_w / 2, 296, "• Потік EKF3 (навігація 100 Гц)", size=10, color=INK))
    frags.append(text(x2 + col_w / 2, 320, "• Потік SD Card DataFlash логів", size=10, color=INK))
    frags.append(text(x2 + col_w / 2, 344, "• Потік MAVLink телеметрії (50 Гц)", size=10, color=INK))
    frags.append(text(x2 + col_w / 2, 368, "• Потік драйверів I2C / CAN шин", size=10, color=INK))
    frags.append(text(x2 + col_w / 2, 392, "Синхронізація: семафори та м'ютекси", size=9.5, color=MUTED, italic=True))

    frags.append(text(x2 + col_w / 2, 455, "Пріоритет: автономність, EKF і місії", size=10, color=FIELD, bold=True))

    # Колонка 3: PX4 Autopilot (NuttX POSIX)
    x3 = x_starts[2]
    frags.append(rect(x3, 60, col_w, 420, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    b, _, _ = textbox(x3 + col_w / 2, 85, "PX4 Autopilot (NuttX POSIX)", size=13, bold=True, stroke=NEG, fill="#edf2fc", min_w=260)
    frags.append(b)
    frags.append(text(x3 + col_w / 2, 112, "Мікроядро + асинхронна шина uORB", size=10, color=MUTED, italic=True))

    b1, _, _ = textbox(x3 + col_w / 2, 150, "Модуль «sensors» (SPI/I2C опитування)", size=10.5, stroke=LINE, fill=FILL, min_w=250)
    frags.append(b1)
    frags.append(arrow(x3 + col_w / 2, 168, x3 + col_w / 2, 192))

    b2, _, _ = textbox(x3 + col_w / 2, 220, "Шина uORB (Pub/Sub IPC в ОЗП)\nsensor_combined, vehicle_attitude", size=10.5, bold=True, stroke=NEG, fill="#f0f5ff", min_w=250)
    frags.append(b2)
    frags.append(arrow(x3 + col_w / 2, 248, x3 + col_w / 2, 272))

    # Модулі-підписники
    frags.append(rect(x3 + 15, 275, col_w - 30, 130, fill="#f8fafc", stroke=LINE, sw=1, rx=6))
    frags.append(text(x3 + col_w / 2, 292, "Ізольовані процеси NuttX:", size=10.5, bold=True, color=INK))
    frags.append(text(x3 + col_w / 2, 316, "• ekf2 (підписка на IMU/GNSS/Mag)", size=10, color=INK))
    frags.append(text(x3 + col_w / 2, 340, "• mc_rate_control (PID регулятор)", size=10, color=INK))
    frags.append(text(x3 + col_w / 2, 364, "• navigator / commander (місія)", size=10, color=INK))
    frags.append(text(x3 + col_w / 2, 388, "• mavlink daemon (зв'язок з GCS)", size=10, color=INK))

    frags.append(text(x3 + col_w / 2, 455, "Пріоритет: модульність, POSIX та IPC", size=10, color=NEG, bold=True))

    render(os.path.join(IMG, 'flight-stacks-architecture.svg'), W, H, *frags,
           title="Порівняння архітектур польотних стеків")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Анатомія Flash-пам'яті польотного контролера (Memory Layout)
# ─────────────────────────────────────────────────────────────────────────────
def fig_flash_layout():
    W, H = 960, 480
    frags = []
    frags.append(text(W / 2, 32, "Карта Flash-пам'яті польотного контролера (STM32 Cortex-M)", size=15, bold=True))

    # Стовпчик адрес (зліва)
    ax = 120
    # Блоки пам'яті (центр)
    bx = 320
    bw = 360

    # Блоки зверху вниз
    y0 = 65

    # 1. Вторинний завантажувач (Bootloader)
    frags.append(text(ax, y0 + 30, "0x0800 0000", size=11, bold=True, color=INK, anchor="end"))
    b1 = rect(bx, y0, bw, 60, fill="#fdecea", stroke=POS, sw=1.8, rx=6)
    frags.append(b1)
    frags.append(text(bx + bw / 2, y0 + 26, "Stage 2 Bootloader (16-32 КБ)", size=12, bold=True, color=POS))
    frags.append(text(bx + bw / 2, y0 + 46, "USB DFU протокол, перевірка хешу, відкат", size=10, color=MUTED))

    # 2. Таблиця векторів переривань додатку
    y1 = y0 + 75
    frags.append(text(ax, y1 + 25, "0x0800 8000 / 0x0801 0000", size=11, bold=True, color=INK, anchor="end"))
    b2 = rect(bx, y1, bw, 50, fill="#edf2fc", stroke=NEG, sw=1.8, rx=6)
    frags.append(b2)
    frags.append(text(bx + bw / 2, y1 + 22, "Векторна таблиця додатка (VTOR)", size=12, bold=True, color=NEG))
    frags.append(text(bx + bw / 2, y1 + 40, "Initial MSP + Reset_Handler + таблиця IRQ", size=10, color=MUTED))

    # 3. Основна прошивка (Application Partition)
    y2 = y1 + 65
    frags.append(text(ax, y2 + 50, "0x0801 0400", size=11, bold=True, color=INK, anchor="end"))
    b3 = rect(bx, y2, bw, 110, fill="#eafaf0", stroke=FIELD, sw=1.8, rx=6)
    frags.append(b3)
    frags.append(text(bx + bw / 2, y2 + 35, "Основний розділ прошивки (Application)", size=13, bold=True, color=FIELD))
    frags.append(text(bx + bw / 2, y2 + 60, "Секції коду .text, констант .rodata та ініціалізаторів .data", size=10.5, color=INK))
    frags.append(text(bx + bw / 2, y2 + 82, "Betaflight / ArduPilot / PX4 виконуваний бінарник (512 КБ – 1.8 МБ)", size=10, color=MUTED))

    # 4. Сектор параметрів / EEPROM Emulation
    y3 = y2 + 125
    frags.append(text(ax, y3 + 30, "Останній сектор (кінцева адреса)", size=11, bold=True, color=INK, anchor="end"))
    b4 = rect(bx, y3, bw, 65, fill="#fff8e7", stroke="#d48806", sw=1.8, rx=6)
    frags.append(b4)
    frags.append(text(bx + bw / 2, y3 + 26, "Сховище параметрів (EEPROM Emulation / LittleFS)", size=12, bold=True, color="#b37400"))
    frags.append(text(bx + bw / 2, y3 + 48, "Два сектори (Page A / Page B) для зносостійкості та атомарності", size=10, color=MUTED))

    # Окремий блок: Системна ROM (System Memory) праворуч
    sx = 730
    sy = 65
    frags.append(rect(sx, sy, 190, 180, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(sx + 95, sy + 25, "System ROM (ST)", size=12, bold=True, color=INK))
    frags.append(text(sx + 95, sy + 45, "0x1FFF 0000", size=10.5, bold=True, color=MUTED))
    frags.append(text(sx + 95, sy + 75, "Фабричний DFU", size=11, bold=True, color=POS))
    frags.append(text(sx + 95, sy + 95, "Зашитий на заводі", size=10, color=INK))
    frags.append(text(sx + 95, sy + 115, "Неможливо стерти", size=10, color=POS, bold=True))
    frags.append(text(sx + 95, sy + 140, "Активація: Boot0 = 1", size=10, color=MUTED, italic=True))
    frags.append(text(sx + 95, sy + 160, "або збій Stage 2", size=9.5, color=MUTED, italic=True))

    # Підписи та зв'язки
    frags.append(arrow(sx, sy + 80, bx + bw, y0 + 30, color=POS))
    frags.append(text(bx + bw + 20, y0 + 15, "Резервний шлях", size=9.5, color=POS))

    frags.append(text(W / 2, H - 18, "Розподіл Flash захищає системний завантажувач від перезапису й ізолює параметри від коду прошивки.", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, 'flash-memory-layout.svg'), W, H, *frags,
           title="Анатомія Flash пам'яті польотного контролера")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Алгоритм безпечного стрибка між завантажувачем і застосунком
# ─────────────────────────────────────────────────────────────────────────────
def fig_boot_jump():
    W, H = 960, 500
    frags = []
    frags.append(text(W / 2, 34, "Послідовність безпечного стрибка (Bootloader → Application)", size=15, bold=True))

    steps = [
        ("1. Вимкнення переривань", "__disable_irq();\nБлокування асинхронних подій під час переходу", POS),
        ("2. Зупинка таймерів і периферії", "SysTick->CTRL = 0; RCC деініціалізація\nСкидання тактування всіх шин (AHB/APB)", LINE),
        ("3. Очищення кешів та MPU (Cortex-M7)", "SCB_DisableDCache(); SCB_DisableICache();\nЗапобігання колізіям узгодженості пам'яті", LINE),
        ("4. Очищення черги NVIC", "NVIC->ICER[i] = 0xFFFFFFFF;\nNVIC->ICPR[i] = 0xFFFFFFFF; (скидання прапорців)", LINE),
        ("5. Валідація стека додатка", "MSP = *(uint32_t*)APP_ADDR;\nПеревірка: чи лежить MSP у межах діапазону RAM", FIELD),
        ("6. Релокація векторної таблиці", "SCB->VTOR = APP_ADDR;\nПеренаправлення обробників переривань на прошивку", NEG),
        ("7. Встановлення MSP і стрибок", "__set_MSP(MSP);\nJump to ((void(*)(void))*(APP_ADDR + 4))();", FIELD)
    ]

    sy = 65
    step_h = 52
    step_w = 560
    cx = W / 2

    for i, (title_, desc_, col) in enumerate(steps):
        y = sy + i * (step_h + 10)
        frags.append(rect(cx - step_w / 2, y, step_w, step_h, fill="#ffffff", stroke=col, sw=1.8, rx=6))

        # Номер і назва
        frags.append(text(cx - step_w / 2 + 15, y + 22, title_, size=11.5, bold=True, color=col, anchor="start"))
        # Опис
        desc_lines = desc_.split("\n")
        frags.append(text(cx - step_w / 2 + 15, y + 40, desc_lines[0], size=10, color=INK, anchor="start"))
        if len(desc_lines) > 1:
            frags.append(text(cx + step_w / 2 - 15, y + 40, desc_lines[1], size=9.5, color=MUTED, anchor="end"))

        if i < len(steps) - 1:
            frags.append(arrow(cx, y + step_h, cx, y + step_h + 10, color=LINE))

    # Бічна виноска про фатальну помилку
    fx = 830
    fy = sy + 4 * (step_h + 10)
    frags.append(rect(fx - 70, fy - 20, 140, 95, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(fx, fy, "Помилка валідації?", size=10.5, bold=True, color=POS))
    frags.append(text(fx, fy + 20, "MSP некоректний", size=9.5, color=INK))
    frags.append(text(fx, fy + 38, "→ Вхід у аварійний", size=9.5, color=POS, bold=True))
    frags.append(text(fx, fy + 56, "DFU завантажувач", size=9.5, color=POS))
    frags.append(line(cx + step_w / 2, fy + 25, fx - 70, fy + 25, color=POS, sw=1.4, dash="4 3"))

    render(os.path.join(IMG, 'boot-jump-flowchart.svg'), W, H, *frags,
           title="Алгоритм безпечного переходу завантажувача")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Дерево відновлення та захист від невдалої прошивки (Recovery Matrix)
# ─────────────────────────────────────────────────────────────────────────────
def fig_dfu_recovery():
    W, H = 960, 480
    frags = []
    frags.append(text(W / 2, 34, "Матриця завантаження, відновлення та відкату (Rollback)", size=15, bold=True))

    # 1. Подія увімкнення живлення
    b_pwr, _, _ = textbox(W / 2, 80, "Подача живлення / Reset (NRST)", size=13, bold=True, stroke=LINE, fill=FILL, min_w=280)
    frags.append(b_pwr)

    # Дві головні гілки: Апаратна та Програмна
    frags.append(arrow(W / 2 - 80, 102, 220, 140))
    frags.append(arrow(W / 2 + 80, 102, 740, 140))

    # Ліва гілка: Апаратний вхід (Boot0)
    b_boot0, _, _ = textbox(220, 165, "Апаратна перевірка:\nКнопка Boot0 натиснута (Boot0 = VDD)?", size=11, bold=True, stroke=POS, fill="#fdecea", min_w=300)
    frags.append(b_boot0)

    frags.append(arrow(220, 195, 220, 240))
    b_dfu_rom, _, _ = textbox(220, 275, "Фабричний ROM DFU Завантажувач\n(0x1FFF0000 — USB DFU / UART1)\nГарантований захист від перетворення на «цеглину»", size=10.5, stroke=POS, fill="#fff5f5", min_w=320)
    frags.append(b_dfu_rom)

    # Права гілка: Програмна перевірка
    b_soft, _, _ = textbox(740, 165, "Програмна перевірка:\nПрапорець у RTC Backup / 1200 baud USB touch?", size=11, bold=True, stroke=NEG, fill="#edf2fc", min_w=320)
    frags.append(b_soft)

    # Відгалуження від програмної
    frags.append(arrow(620, 195, 480, 240))
    frags.append(arrow(820, 195, 820, 240))

    # Прапорець встановлено -> Stage 2 Bootloader
    b_stage2, _, _ = textbox(480, 275, "Stage 2 DFU Bootloader\n(Очікування прошивки по USB/MAVLink)", size=10.5, stroke=NEG, fill="#f0f5ff", min_w=260)
    frags.append(b_stage2)

    # Прапорця немає -> Перевірка цілісності прошивки
    b_check, _, _ = textbox(820, 275, "Перевірка цілісності слота:\nВалідація CRC32/SHA256 та лічильника збоїв", size=10.5, bold=True, stroke=FIELD, fill="#eafaf0", min_w=280)
    frags.append(b_check)

    # Результат перевірки цілісності
    frags.append(arrow(820, 308, 820, 360))
    b_app, _, _ = textbox(820, 395, "Запуск основної прошивки (App)\nЯкщо збій запуску > 3 разів → A/B Rollback\nна попередній робочий банк Flash", size=10.5, stroke=FIELD, fill="#f4fbf7", min_w=280)
    frags.append(b_app)

    # Лінія аварійного повернення зі збою перевірки цілісності
    frags.append(arrow(680, 285, 610, 285, color=POS))
    frags.append(text(645, 270, "Пошкоджено", size=9.5, color=POS, bold=True))

    frags.append(text(W / 2, H - 18, "Багаторівнева система захисту унеможливлює незворотну втрату працездатності контролера.", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, 'dfu-recovery-matrix.svg'), W, H, *frags,
           title="Матриця завантаження та відновлення польотного контролера")


if __name__ == '__main__':
    fig_flight_stacks()
    fig_flash_layout()
    fig_boot_jump()
    fig_dfu_recovery()
    print("All figures generated successfully.")

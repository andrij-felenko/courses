# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. driver-layers: Трирівнева архітектура драйвера чипа ──
def fig_driver_layers():
    W, H = 920, 520
    p = []

    # Заголовок та фонові блоки трьох рівнів
    p.append(rect(20, 20, 880, 480, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(text(460, 45, "Архітектурні рівні чистого драйвера периферійного чипа", size=15, color=INK, bold=True))

    # Рівень 3: Прикладний API (SI units)
    p.append(rect(50, 70, 820, 110, fill="#eef6ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(80, 95, "Рівень 3: Прикладний API предметної області (SI Units)", size=13.5, color=NEG, bold=True, anchor="start"))
    p.append(text(80, 118, "• Приймає дескриптор пристрою (struct Device_t*) та повертає фізичні величини (м/с², Па, °C, Люкс)", size=11.5, color=INK, anchor="start"))
    p.append(text(80, 138, "• Застосовує коефіцієнти калібрування, температурну компенсацію та захист від артефактів вибірки", size=11.5, color=MUTED, anchor="start"))
    p.append(text(80, 158, "• Функції: sensor_init(), sensor_read_accel_si(&dev, &accel_m_s2), sensor_set_range(&dev, RANGE_4G)", size=11, color=LINE, anchor="start", bold=True))

    # Стрілки між Рівнем 3 і Рівнем 2
    p.append(arrow(460, 180, 460, 215, color=NEG, sw=2))
    p.append(text(480, 200, "Логічні команди та налаштування", size=10.5, color=MUTED, anchor="start"))

    # Рівень 2: Регістрова карта та стан чипа (Shadow State & Protocol)
    p.append(rect(50, 220, 820, 120, fill="#f0faf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(80, 245, "Рівень 2: Регістрова логіка та тіньовий стан (Register Map & State)", size=13.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(80, 268, "• Адреси регістрів, маски бітів (MASK / SHIFT), перевірка WHO_AM_I та бітів готовності (DRDY)", size=11.5, color=INK, anchor="start"))
    p.append(text(80, 288, "• Безпечний Read-Modify-Write (RMW), підтримка Shadow-регістрів для write-only та BDU-пакетного читання", size=11.5, color=MUTED, anchor="start"))
    p.append(text(80, 308, "• Перетворення сирих кодів (LSB, sign-extension, endianness) у внутрішні нормалізовані числа", size=11, color=LINE, anchor="start"))

    # Стрілки між Рівнем 2 і Рівнем 1
    p.append(arrow(460, 340, 460, 375, color=FIELD, sw=2))
    p.append(text(480, 360, "Сирі байти: (reg_addr, buffer, len)", size=10.5, color=MUTED, anchor="start"))

    # Рівень 1: Транспортна абстракція шини (Platform Bus Abstraction)
    p.append(rect(50, 380, 820, 100, fill="#fff8f0", stroke=POS, sw=1.8, rx=8))
    p.append(text(80, 405, "Рівень 1: Апаратна абстракція шини (Bus Transport Interface)", size=13.5, color=POS, bold=True, anchor="start"))
    p.append(text(80, 428, "• Вказівники на функції зворотного виклику: bus_read(ctx, reg, buf, len), bus_write(ctx, reg, buf, len), delay_ms()", size=11.5, color=INK, anchor="start"))
    p.append(text(80, 448, "• Повна ізоляція від платформи: жодних прямих викликів HAL_I2C, esp_err, Linux ioctl чи регістрів МК", size=11.5, color=MUTED, anchor="start"))
    p.append(text(80, 468, "• Драйвер компілюється на STM32, ESP32, AVR або в Unit-тестах на ПК без модифікації вихідного коду", size=11, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "driver-layers.svg"), W, H, *p)

# ── 2. rmw-pitfall-and-shadow: Небезпеки RMW та тіньові регістри ──
def fig_rmw_pitfall_and_shadow():
    W, H = 920, 480
    p = []

    p.append(rect(20, 20, 880, 440, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(text(460, 45, "Пастки прямого Read-Modify-Write (RMW) проти безпечного керування", size=15, color=INK, bold=True))

    # Ліва колонка: Проблеми наївного RMW
    p.append(rect(45, 75, 400, 365, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    p.append(text(245, 100, "Наївний прямий RMW (Помилка)", size=13, color=POS, bold=True))
    
    # 3 пастки
    p.append(rect(60, 120, 370, 85, fill="#ffffff", stroke=POS, sw=1, rx=5))
    p.append(text(75, 140, "1. Регістри зі скиданням по читанню (COR)", size=11.5, color=POS, bold=True, anchor="start"))
    p.append(text(75, 160, "Зчитування STATUS_REG заради 1 біта", size=11, color=INK, anchor="start"))
    p.append(text(75, 180, "безповоротно очищає прапорці переривань!", size=11, color=MUTED, anchor="start"))

    p.append(rect(60, 220, 370, 85, fill="#ffffff", stroke=POS, sw=1, rx=5))
    p.append(text(75, 240, "2. Регістри лише для запису (Write-Only)", size=11.5, color=POS, bold=True, anchor="start"))
    p.append(text(75, 260, "Читання повертає 0x00 або 0xFF.", size=11, color=INK, anchor="start"))
    p.append(text(75, 280, "RMW перезаписує сусідні біти сміттям!", size=11, color=MUTED, anchor="start"))

    p.append(rect(60, 320, 370, 100, fill="#ffffff", stroke=POS, sw=1, rx=5))
    p.append(text(75, 340, "3. Зарезервовані біти (Reserved Bits)", size=11.5, color=POS, bold=True, anchor="start"))
    p.append(text(75, 360, "Помилкове перезаписування бітів заводського", size=11, color=INK, anchor="start"))
    p.append(text(75, 380, "підстроювання або бітів Must-Be-Zero (MBZ)", size=11, color=MUTED, anchor="start"))
    p.append(text(75, 400, "призводить до декалібрування чи зависання.", size=11, color=MUTED, anchor="start"))

    # Права колонка: Архітектурне вирішення
    p.append(rect(475, 75, 400, 365, fill="#f0faf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(675, 100, "Безпечні патерни оновлення", size=13, color=FIELD, bold=True))

    p.append(rect(490, 120, 370, 85, fill="#ffffff", stroke=FIELD, sw=1, rx=5))
    p.append(text(505, 140, "1. Тіньовий стан у пам'яті ОЗП (Shadow State)", size=11.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(505, 160, "Зберігання копії регістрів у struct Device_t.", size=11, color=INK, anchor="start"))
    p.append(text(505, 180, "Запис: dev->shadow = (shadow & ~M) | V;", size=11, color=LINE, anchor="start", bold=True))

    p.append(rect(490, 220, 370, 85, fill="#ffffff", stroke=FIELD, sw=1, rx=5))
    p.append(text(505, 240, "2. Явні бітові маски та зсуви (Mask & Shift)", size=11.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(505, 260, "Ізоляція полів без зачіпання інших бітів:", size=11, color=INK, anchor="start"))
    p.append(text(505, 280, "#define REG_CTRL_ODR_MASK  (0x0F << 4)", size=11, color=LINE, anchor="start", bold=True))

    p.append(rect(490, 320, 370, 100, fill="#ffffff", stroke=FIELD, sw=1, rx=5))
    p.append(text(505, 340, "3. Атомарне блокування (BDU)", size=11.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(505, 360, "Активація Block Data Update для захисту", size=11, color=INK, anchor="start"))
    p.append(text(505, 380, "від розриву даних між читаннями MSB і LSB", size=11, color=MUTED, anchor="start"))
    p.append(text(505, 400, "під час внутрішнього оновлення АЦП.", size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "rmw-pitfall-and-shadow.svg"), W, H, *p)

# ── 3. device-descriptor-lifecycle: Життєвий цикл дескриптора пристрою ──
def fig_device_descriptor_lifecycle():
    W, H = 920, 420
    p = []

    p.append(rect(20, 20, 880, 380, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(text(460, 45, "Структура дескриптора пристрою та послідовність ініціалізації", size=15, color=INK, bold=True))

    # Схема структури дескриптора зліва
    p.append(rect(40, 75, 320, 305, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(200, 100, "struct chip_device_t", size=13, color=NEG, bold=True))
    p.append(line(40, 115, 360, 115, color=NEG, sw=1))

    fields = [
        ("bus_io", "const chip_bus_ops_t*", "Вказівники read/write"),
        ("user_ctx", "void*", "Хендл шини МК (I2C/SPI)"),
        ("dev_addr", "uint8_t", "7-біт I2C адреса / CS пін"),
        ("range", "chip_range_t", "Поточний діапазон (±2g..16g)"),
        ("scale_factor", "float", "Чутливість у SI одиницях"),
        ("shadow_ctrl", "uint8_t[4]", "Тіньові копії регістрів"),
        ("calib", "chip_calib_t", "Зсуви та коефіцієнти"),
        ("is_initialized", "bool", "Прапорець валідності стану")
    ]
    y = 135
    for name, ftype, desc in fields:
        p.append(text(50, y, name, size=11, color=INK, bold=True, anchor="start"))
        p.append(text(160, y, ftype, size=10.5, color=MUTED, anchor="start"))
        y += 20
        p.append(text(65, y, desc, size=9.5, color=MUTED, italic=True, anchor="start"))
        y += 15

    # Етапи життєвого циклу справа
    steps = [
        ("1. Ін'єкція залежностей", "Запис вказівників на шинні функції та хендл платформи у структуру.", NEG),
        ("2. Верифікація зв'язку", "Зчитування регістру WHO_AM_I / CHIP_ID та звірка з еталоном.", POS),
        ("3. Програмний Soft-Reset", "Подача біта перезавантаження та очікування очищення прапорця.", FIELD),
        ("4. Калібрування та конфіг", "Вичитування коефіцієнтів з NVM/OTP, налаштування ODR, BDU та діапазону.", LINE)
    ]

    x_step = 400
    y_step = 80
    for title, desc, col in steps:
        p.append(rect(x_step, y_step, 480, 60, fill="#ffffff", stroke=col, sw=1.5, rx=6))
        p.append(circle(x_step + 25, y_step + 30, 14, fill=col, stroke="#ffffff", sw=1.5))
        p.append(text(x_step + 25, y_step + 34, title[0], size=11, color="#ffffff", bold=True))
        p.append(text(x_step + 50, y_step + 22, title, size=12, color=col, bold=True, anchor="start"))
        p.append(text(x_step + 50, y_step + 45, desc, size=10.5, color=MUTED, anchor="start"))
        
        if y_step < 260:
            # Стрілка вниз
            p.append(arrow(x_step + 240, y_step + 60, x_step + 240, y_step + 75, color=MUTED, sw=1.5))
            
        y_step += 75

    render(os.path.join(OUT, "device-descriptor-lifecycle.svg"), W, H, *p)

# ── 4. error-handling-and-retries: Обробка помилок та механізм Retries ──
def fig_error_handling_and_retries():
    W, H = 920, 440
    p = []

    p.append(rect(20, 20, 880, 400, fill="#ffffff", stroke=MUTED, sw=1.2, rx=10))
    p.append(text(460, 45, "Стійка модель обробки транзакцій, тайм-аутів та повторних спроб", size=15, color=INK, bold=True))

    # Блок 1: Початок транзакції
    p.append(rect(50, 80, 220, 70, fill="#f8fafc", stroke=NEG, sw=1.5, rx=6))
    p.append(text(160, 110, "Запит читання / запису", size=12, color=NEG, bold=True))
    p.append(text(160, 130, "dev->bus_io->read()", size=10.5, color=MUTED))

    # Стрілка праворуч до Перевірки ACK/NACK
    p.append(arrow(270, 115, 335, 115, color=LINE, sw=1.5))

    # Блок 2: Перевірка результату шини
    p.append(rect(340, 85, 180, 60, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(430, 110, "Шина повернула", size=11, color=INK, bold=True))
    p.append(text(430, 128, "STATUS_OK?", size=11, color=INK, bold=True))

    # Гілка ТАК (Вниз) -> Перевірка даних/CRC
    p.append(arrow(430, 145, 430, 225, color=FIELD, sw=2))
    p.append(text(445, 185, "ТАК", size=11, color=FIELD, bold=True, anchor="start"))

    # Блок Успіх
    p.append(rect(320, 230, 220, 70, fill="#f0faf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(430, 260, "Валідація даних / DRDY", size=12, color=FIELD, bold=True))
    p.append(text(430, 280, "Конвертація в одиниці SI", size=10.5, color=MUTED))

    p.append(arrow(430, 300, 430, 345, color=FIELD, sw=1.5))

    p.append(rect(340, 350, 180, 45, fill="#27ae60", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(430, 377, "CHIP_STATUS_OK", size=12, color="#ffffff", bold=True))

    # Гілка НІ (Праворуч) -> Лічильник Retries
    p.append(arrow(520, 115, 615, 115, color=POS, sw=2))
    p.append(text(555, 105, "НІ (NACK/Збій)", size=10.5, color=POS, bold=True))

    p.append(rect(620, 85, 160, 60, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    p.append(text(700, 110, "retries < MAX?", size=11, color=POS, bold=True))
    p.append(text(700, 128, "(напр. 3 спроби)", size=9.5, color=MUTED))

    # Гілка Retries є -> Затримка і петля назад
    p.append(line(700, 85, 700, 55, color=POS, sw=1.5))
    p.append(line(700, 55, 160, 55, color=POS, sw=1.5))
    p.append(arrow(160, 55, 160, 75, color=POS, sw=1.5))
    p.append(text(430, 68, "retries++, delay_ms(backoff) — Повторити транзакцію", size=10.5, color=POS, bold=True))

    # Гілка Retries вичерпано -> Відновлення шини та Помилка
    p.append(arrow(700, 145, 700, 225, color=POS, sw=2))
    p.append(text(710, 185, "Вичерпано", size=10.5, color=POS, bold=True, anchor="start"))

    p.append(rect(600, 230, 200, 70, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    p.append(text(700, 255, "Спроба відновлення шини", size=11.5, color=POS, bold=True))
    p.append(text(700, 275, "9 тактів SCL / SPI re-init", size=10.5, color=MUTED))

    p.append(arrow(700, 300, 700, 345, color=POS, sw=1.5))

    p.append(rect(610, 350, 180, 45, fill="#c0392b", stroke=POS, sw=1.5, rx=6))
    p.append(text(700, 377, "CHIP_ERR_COMM_FAIL", size=12, color="#ffffff", bold=True))

    render(os.path.join(OUT, "error-handling-and-retries.svg"), W, H, *p)

if __name__ == "__main__":
    fig_driver_layers()
    fig_rmw_pitfall_and_shadow()
    fig_device_descriptor_lifecycle()
    fig_error_handling_and_retries()
    print("All figures generated successfully.")

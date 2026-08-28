# -*- coding: utf-8 -*-
"""Фігури для статті mezha-plata-zastosunok.
Згенеровані через svgkit зі scripts/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_bsp_boundary_architecture():
    """Архітектурна межа між застосунком, контрактом BSP та апаратною платою."""
    W, H = 840, 500
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 28, "Архітектурна межа «Застосунок ↔ BSP ↔ Апаратна плата»", size=16, color=INK, bold=True))

    # Рівень 1: Бізнес-логіка застосунку
    p.append(rect(60, 55, 720, 95, fill="#e8f4fd", stroke="#1d6fa5", sw=1.8, rx=8))
    p.append(text(420, 80, "Рівень застосунку (Application Domain / Pure Logic)", size=14, color="#1d6fa5", bold=True))
    p.append(text(420, 102, "Кінцеві автомати (FSM), математичні алгоритми, протоколи, керування телеметрією", size=11, color=INK))
    p.append(text(420, 124, "Нічого не знає про піни, порти, регістри, адреси I2C та полярність транзисторів", size=11, color="#0f4c81", bold=True))

    # Стрілка вниз: Застосунок викликає лише контракт
    p.append(arrow(420, 150, 420, 185, color="#1d6fa5", sw=2.0))
    p.append(text(435, 172, "Виклики через абстрактний контракт", size=10, color="#1d6fa5", anchor="start", bold=True))

    # Рівень 2: Контракт інтерфейсу BSP (Межа ізоляції)
    p.append(rect(60, 190, 720, 100, fill="#fef3c7", stroke="#b45309", sw=2.0, rx=8))
    p.append(text(420, 215, "Контракт інтерфейсу BSP (Board Support Package API)", size=14, color="#b45309", bold=True))
    
    # Блоки функцій контракту
    apis = [
        ("board_init()", 80, 235),
        ("board_led_set()", 225, 235),
        ("board_power_sensors()", 390, 235),
        ("board_get_battery_mv()", 575, 235),
    ]
    for fn, ax, ay in apis:
        p.append(rect(ax, ay, 150, 32, fill="#ffffff", stroke="#b45309", sw=1.2, rx=4))
        p.append(text(ax + 75, ay + 20, fn, size=11, color="#78350f", bold=True))

    p.append(text(420, 280, "Канонічні фізичні величини (мВ, °C), логічні стани, перевірка інваріантів", size=10, color="#92400e"))

    # Стрілка вниз: BSP транслює виклики в апаратні маніпуляції
    p.append(arrow(420, 290, 420, 325, color=POS, sw=2.0))
    p.append(text(435, 312, "Трансляція в низькорівневі виклики вендорного HAL", size=10, color=POS, anchor="start", bold=True))

    # Рівень 3: Конкретна апаратна реалізація плати
    p.append(rect(60, 330, 720, 145, fill="#f1f5f9", stroke="#475569", sw=1.8, rx=8))
    p.append(text(420, 355, "Конкретна друкована плата та кремній мікроконтролера", size=14, color="#334155", bold=True))

    hw_blocks = [
        ("GPIO / Піни", "PB12 (LED), PA4 (CS)\nПолярність Active-Low", 80, 375, "#fee2e2", POS),
        ("Шини I2C / SPI", "I2C1 (0x68 Gyro, 0x76 BME)\nSPI2 (DMA Rx/Tx буфери)", 260, 375, "#e0e7ff", "#4338ca"),
        ("Керування живленням", "P-MOSFET ключ (PE3)\nЧас стабілізації 15 мс", 440, 375, "#dcfce7", FIELD),
        ("Аналогові кола", "АЦП1 Канал 5, дільник\nR1=100кОм, R2=200кОм", 620, 375, "#fef9c3", "#a16207"),
    ]

    for htitle, hdesc, hx, hy, hfill, hstroke in hw_blocks:
        p.append(rect(hx, hy, 160, 85, fill=hfill, stroke=hstroke, sw=1.2, rx=5))
        p.append(text(hx + 80, hy + 20, htitle, size=11, color=hstroke, bold=True))
        lines = hdesc.split("\n")
        p.append(text(hx + 80, hy + 45, lines[0], size=10, color=INK))
        p.append(text(hx + 80, hy + 65, lines[1], size=10, color=INK))

    render(os.path.join(OUT, "bsp-boundary-architecture.svg"), W, H, *p)


def fig_hardware_leakage_vs_bsp_contract():
    """Порівняння витоку апаратних деталей та чистого контракту BSP."""
    W, H = 840, 470
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 26, "Витік апаратних деталей проти абстрактного контракту BSP", size=16, color=INK, bold=True))

    # Ліва колонка: Антипатерн — витік заліза
    p.append(rect(30, 45, 375, 405, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(217, 72, "Антипатерн: Прямий витік заліза в логіку", size=13, color=POS, bold=True))

    bad_items = [
        ("Застосунок знає номер піна:", "HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, GPIO_PIN_RESET);", 95),
        ("Застосунок знає адресу шини I2C:", "i2c_master_write_to_device(I2C_NUM_0, 0x68, reg, 2);", 175),
        ("Застосунок рахує резистори дільника:", "v_bat = (adc_raw * 3300 / 4095) * (100 + 47) / 47;", 255),
        ("Застосунок керує ключем живлення:", "HAL_GPIO_WritePin(GPIOE, GPIO_PIN_3, 0); // PMOS on\nHAL_Delay(15); // Очікування ємностей", 335),
    ]

    for label, code_sample, iy in bad_items:
        p.append(text(45, iy + 14, label, size=11, color=POS, anchor="start", bold=True))
        p.append(rect(45, iy + 22, 345, 46, fill="#ffffff", stroke="#fca5a5", sw=1.0, rx=4))
        clines = code_sample.split("\n")
        if len(clines) == 1:
            p.append(text(55, iy + 50, clines[0], size=10, color="#7f1d1d", anchor="start"))
        else:
            p.append(text(55, iy + 40, clines[0], size=10, color="#7f1d1d", anchor="start"))
            p.append(text(55, iy + 58, clines[1], size=10, color="#7f1d1d", anchor="start"))

    p.append(text(217, 435, "Зміна трасування чи ревізії плати руйнує весь проєкт", size=10, color=POS, bold=True))

    # Права колонка: Ідіоматичний BSP контракт
    p.append(rect(435, 45, 375, 405, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(622, 72, "Ідіоматичний підхід: Контракт межі BSP", size=13, color=FIELD, bold=True))

    good_items = [
        ("Семантичний намір керування індикатором:", "board_status_led_set(BOARD_LED_ID_SYSTEM, BOARD_LED_WARN);", 95),
        ("Отримання фізичних одиниць без адреси:", "board_read_inertial_data(&imu_accel_raw, &imu_gyro_dps);", 175),
        ("Готова напруга живлення в мілівольтах:", "uint16_t bat_mv = 0;\nboard_get_battery_voltage_mv(&bat_mv);", 255),
        ("Безпечне ввімкнення домену з таймінгом:", "board_power_sensors(true); // BSP контролює PMOS і delay", 335),
    ]

    for label, code_sample, iy in good_items:
        p.append(text(450, iy + 14, label, size=11, color=FIELD, anchor="start", bold=True))
        p.append(rect(450, iy + 22, 345, 46, fill="#ffffff", stroke="#86efac", sw=1.0, rx=4))
        clines = code_sample.split("\n")
        if len(clines) == 1:
            p.append(text(460, iy + 50, clines[0], size=10, color="#14532d", anchor="start"))
        else:
            p.append(text(460, iy + 40, clines[0], size=10, color="#14532d", anchor="start"))
            p.append(text(460, iy + 58, clines[1], size=10, color="#14532d", anchor="start"))

    p.append(text(622, 435, "Бізнес-логіка стабільна, 100% переносима та готова до тестів", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "hardware-leakage-vs-bsp-contract.svg"), W, H, *p)


def fig_dependency_injection_host_vs_target():
    """Dependency Injection: одна бізнес-логіка компілюється для заліза та для хост-тестів."""
    W, H = 840, 500
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 28, "Впровадження залежностей (DI): Цільовий чип проти Хост-тестів", size=16, color=INK, bold=True))

    # Центральний модуль: Ядро застосунку
    p.append(rect(230, 55, 380, 85, fill="#e8f4fd", stroke="#1d6fa5", sw=2.0, rx=8))
    p.append(text(420, 80, "Ядро застосунку (Application Logic)", size=14, color="#1d6fa5", bold=True))
    p.append(text(420, 102, "app_state_machine.c / telemetry_manager.cpp", size=11, color=INK))
    p.append(text(420, 122, "Залежить ТІЛЬКИ від bsp_interface.h (чисті віртуальні методи / покажчики)", size=10, color="#0f4c81"))

    # Розгалуження стрілок
    p.append(arrow(340, 140, 190, 190, color="#3b82f6", sw=2.0))
    p.append(text(230, 160, "Цільова збірка", size=11, color="#1d4ed8", bold=True))

    p.append(arrow(500, 140, 650, 190, color=FIELD, sw=2.0))
    p.append(text(605, 160, "Хостова збірка (CI/CD)", size=11, color=FIELD, bold=True))

    # Ліва гілка: Цільове залізо
    p.append(rect(40, 195, 360, 275, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    p.append(text(220, 220, "Цільова прошивка (Target Build)", size=13, color="#1e293b", bold=True))

    p.append(rect(60, 235, 320, 65, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=5))
    p.append(text(220, 255, "Реалізація BSP: bsp_target_stm32.c", size=11, color="#1d4ed8", bold=True))
    p.append(text(220, 275, "Пряма взаємодія з STM32 HAL / LL драйверами", size=10, color=INK))
    p.append(text(220, 290, "Таймери, DMA, апаратні регістри NVIC", size=10, color=MUTED))

    p.append(arrow(220, 300, 220, 330, color="#3b82f6", sw=1.5))

    p.append(rect(60, 330, 320, 65, fill="#fee2e2", stroke=POS, sw=1.2, rx=5))
    p.append(text(220, 350, "Кремній мікроконтролера та плата", size=11, color=POS, bold=True))
    p.append(text(220, 370, "STM32F401 / ESP32-S3 + Сенсори на друкованій платі", size=10, color=INK))
    p.append(text(220, 385, "Прошивка через SWD / JTAG програматор", size=10, color=MUTED))

    p.append(rect(60, 410, 320, 45, fill="#f1f5f9", stroke="none", rx=4))
    p.append(text(220, 428, "Виконується на реальному залізі", size=10, color="#334155", bold=True))
    p.append(text(220, 444, "Тестування вимагає стендів, приладів та осцилографа", size=10, color=MUTED))

    # Права гілка: Хостові юніт-тести
    p.append(rect(440, 195, 360, 275, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(620, 220, "Хостовий запуск (Unit Tests / PC Native)", size=13, color=FIELD, bold=True))

    p.append(rect(460, 235, 320, 65, fill="#ecfdf5", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(620, 255, "Мок-реалізація BSP: bsp_mock_host.cpp", size=11, color="#047857", bold=True))
    p.append(text(620, 275, "Імітація сенсорів, інжекція помилок I2C та збоїв живлення", size=10, color=INK))
    p.append(text(620, 290, "Запис викликаних методів у тестові буфери", size=10, color=MUTED))

    p.append(arrow(620, 300, 620, 330, color=FIELD, sw=1.5))

    p.append(rect(460, 330, 320, 65, fill="#e0e7ff", stroke="#4338ca", sw=1.2, rx=5))
    p.append(text(620, 350, "Фреймворк тестування (GoogleTest / Unity)", size=11, color="#4338ca", bold=True))
    p.append(text(620, 370, "Перевірка переходу станів FSM за 0.002 секунди", size=10, color=INK))
    p.append(text(620, 385, "TEST(BatteryAlert, ShutdownWhenVoltageBelow3200mV)", size=10, color="#3730a3"))

    p.append(rect(460, 410, 320, 45, fill="#ecfdf5", stroke="none", rx=4))
    p.append(text(620, 428, "100% тестів проходять на x86-64 / ARM64 хості", size=10, color=FIELD, bold=True))
    p.append(text(620, 444, "Миттєвий запуск у GitHub Actions / GitLab CI пайплайнах", size=10, color=MUTED))

    render(os.path.join(OUT, "dependency-injection-host-vs-target.svg"), W, H, *p)


def fig_bsp_lifecycle_sequence():
    """Життєвий цикл та послідовність викликів BSP при старті, роботі та переході в сон."""
    W, H = 840, 520
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 26, "Послідовність життєвого циклу плати під керуванням BSP", size=16, color=INK, bold=True))

    steps = [
        ("1. Reset / Early Init", "board_early_init()", "Налаштування тактування (PLL, HSE 24MHz), вимкнення невикористаної периферії", 55, "#fee2e2", POS),
        ("2. Конфігурація платформи", "board_init()", "Ініціалізація GPIO за замовчуванням, шин I2C/SPI, перевірка ліній живлення", 130, "#fef3c7", "#b45309"),
        ("3. Подача живлення на периферію", "board_power_sensors(true)", "Увімкнення P-MOSFET ключа, затримка 15 мс для заряду фільтрувальних конденсаторів", 205, "#dcfce7", FIELD),
        ("4. Робочий цикл застосунку", "board_get_battery_mv() / board_led_set()", "Регулярний огляд сенсорів, передача телеметрії, індикація робочого стану", 280, "#e8f4fd", "#1d6fa5"),
        ("5. Підготовка до глибокого сну", "board_power_sensors(false)", "Вимкнення живлення давачів, переведення ліній I2C (SCL/SDA) в Hi-Z для усунення витоків", 355, "#f3e8fd", "#7e22ce"),
        ("6. Вхід у режим мікрострумів", "board_enter_low_power()", "Зупинка швидкісних генераторів, перехід MCU в Stop/DeepSleep, струм < 15 мкА", 430, "#f1f5f9", "#475569"),
    ]

    for title, fn, desc, sy, sfill, sstroke in steps:
        p.append(rect(60, sy, 720, 62, fill=sfill, stroke=sstroke, sw=1.5, rx=6))
        p.append(text(80, sy + 24, title, size=12, color=sstroke, anchor="start", bold=True))
        p.append(rect(340, sy + 8, 250, 24, fill="#ffffff", stroke=sstroke, sw=1.0, rx=3))
        p.append(text(465, sy + 24, fn, size=10, color=sstroke, bold=True))
        p.append(text(80, sy + 48, desc, size=10, color=INK, anchor="start"))

        if sy < 430:
            p.append(arrow(420, sy + 62, 420, sy + 75, color=sstroke, sw=1.5))

    render(os.path.join(OUT, "bsp-lifecycle-sequence.svg"), W, H, *p)


if __name__ == "__main__":
    fig_bsp_boundary_architecture()
    fig_hardware_leakage_vs_bsp_contract()
    fig_dependency_injection_host_vs_target()
    fig_bsp_lifecycle_sequence()
    print("Всі 4 фігури успішно згенеровано у", OUT)

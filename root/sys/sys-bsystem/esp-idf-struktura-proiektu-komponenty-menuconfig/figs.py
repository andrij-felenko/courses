# -*- coding: utf-8 -*-
"""Фігури до теми «ESP-IDF: структура проєкту, компоненти, menuconfig»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DIRTY = "#fdecea"     # червонуватий / застереження / приватне
CLEAN = "#eaf7ef"     # зеленуватий / публічне / успіх
PANEL = "#f8fafc"
ACCENT = "#eaf0fd"    # блакитний / системний


# ── 1. Двоетапна архітектура збірки ESP-IDF ─────────────────────────────────
def fig_build_architecture():
    W, H = 1040, 480
    p = []

    p.append(text(520, 30, "Архітектура системи збірки ESP-IDF: від вихідних файлів до бінарного образу",
                  size=16, bold=True))

    # Ліва колонка: Вхідні артефакти
    p.append(rect(30, 60, 270, 390, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(165, 85, "1. Вхідні конфігурації та код", size=13.5, bold=True, color=INK))

    inputs = [
        ("Кореневий CMakeLists.txt\n(точка входу, include project.cmake)", 135),
        ("Компоненти (main/, components/)\n(CMakeLists.txt, коди C/C++, Kconfig)", 205),
        ("Схеми Kconfig / sdkconfig.defaults\n(декларативні дерева опцій)", 280),
        ("Таблиця розділів (partitions.csv)\n(розмітка адрес Flash-пам'яті)", 355),
    ]
    for desc, cy in inputs:
        p.append(fitbox(45, cy - 25, 240, 50, desc, size=11, fill=BG, stroke=MUTED))

    # Стрілки від входів до ядра збірки
    p.append(arrow(300, 135, 360, 135, color=LINE, sw=1.6))
    p.append(arrow(300, 205, 360, 205, color=LINE, sw=1.6))
    p.append(arrow(300, 280, 360, 280, color=LINE, sw=1.6))
    p.append(arrow(300, 355, 360, 355, color=LINE, sw=1.6))

    # Центральна колонка: Диспетчер та рушії кодогенерації
    p.append(rect(360, 60, 340, 390, fill=ACCENT, stroke=NEG, sw=1.8))
    p.append(text(530, 85, "2. Диспетчер idf.py та розширення CMake", size=13.5, bold=True, color=NEG))

    engines = [
        ("confgen.py (Kconfig parser)\nГенерація sdkconfig.h та sdkconfig.cmake", 135, FIELD),
        ("Фаза раннього розширення CMake\nПошук компонентів, виявлення залежностей", 205, NEG),
        ("Реєстрація таргетів (__idf_*)\nСтворення бібліотек, експорт заголовків", 280, NEG),
        ("Ninja / GCC Toolchain / gen_esp32part\nКрос-компіляція об'єктів та бінарників", 355, POS),
    ]
    for desc, cy, stroke_c in engines:
        p.append(fitbox(375, cy - 25, 310, 50, desc, size=11.5, fill=BG, stroke=stroke_c))

    # Стрілки від ядра до вихідних артефактів
    p.append(arrow(700, 135, 760, 135, color=LINE, sw=1.6))
    p.append(arrow(700, 205, 760, 205, color=LINE, sw=1.6))
    p.append(arrow(700, 280, 760, 280, color=LINE, sw=1.6))
    p.append(arrow(700, 355, 760, 355, color=LINE, sw=1.6))

    # Права колонка: Цільові артефакти прошивки
    p.append(rect(760, 60, 250, 390, fill=PANEL, stroke=FIELD, sw=1.8))
    p.append(text(885, 85, "3. Фінальні образи прошивки", size=13.5, bold=True, color=FIELD))

    outputs = [
        ("sdkconfig.h\n(макроси CONFIG_* для C/C++)", 135),
        ("bootloader.bin (зміщення 0x1000/0x0)\nЗавантажувач 2-го рівня", 205),
        ("partition-table.bin (0x8000)\nБінарна таблиця розділів", 280),
        ("app.bin (зміщення 0x10000)\nОбраз застосунку з заголовком", 355),
    ]
    for desc, cy in outputs:
        p.append(fitbox(775, cy - 25, 220, 50, desc, size=11, fill=CLEAN, stroke=FIELD))

    render(os.path.join(IMG, "esp-idf-build-architecture.svg"), W, H, *p,
           title="Архітектура системи збірки ESP-IDF")


# ── 2. Модель залежностей компонентів: REQUIRES vs PRIV_REQUIRES ──────────────
def fig_component_dependencies():
    W, H = 1000, 440
    p = []

    p.append(text(500, 30, "Поширення залежностей між компонентами: публічні та приватні інтерфейси",
                  size=15.5, bold=True))

    # Компонент A (Споживач верхнього рівня)
    p.append(rect(40, 70, 260, 330, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(170, 95, "Компонент: main", size=14, bold=True, color=INK))
    p.append(fitbox(55, 120, 230, 60, "Головний код застосунку\nmain.c / main.cpp\n#include \"sensor.h\"", size=12, fill=BG))
    p.append(fitbox(55, 210, 230, 80, "main/CMakeLists.txt:\nidf_component_register(\n  SRCS \"main.c\"\n  PRIV_REQUIRES sensor_hub\n)", size=11, fill=CLEAN, stroke=FIELD))
    p.append(fitbox(55, 315, 230, 65, "Бачить: sensor.h (публічний)\nНЕ бачить: i2c_bus.h (приватний)", size=11, fill=PANEL, stroke=MUTED))

    # Стрілка залежності main -> sensor_hub
    p.append(arrow(300, 250, 370, 250, color=FIELD, sw=2))
    p.append(text(335, 235, "REQUIRES", size=11, bold=True, color=FIELD))

    # Компонент B (Проміжний модуль sensor_hub)
    p.append(rect(370, 70, 280, 330, fill=CLEAN, stroke=FIELD, sw=1.8))
    p.append(text(510, 95, "Компонент: sensor_hub", size=14, bold=True, color=FIELD))
    p.append(fitbox(385, 120, 250, 80, "Публічний інтерфейс:\ninclude/sensor.h\n(експортується усім споживачам)", size=11.5, fill=BG, stroke=FIELD))
    p.append(fitbox(385, 210, 250, 100, "sensor_hub/CMakeLists.txt:\nidf_component_register(\n  SRCS \"sensor.c\"\n  INCLUDE_DIRS \"include\"\n  PRIV_REQUIRES i2c_driver\n)", size=10.5, fill=BG, stroke=LINE))
    p.append(fitbox(385, 325, 250, 55, "Реалізація sensor.c викликає\nприватний драйвер i2c_driver", size=11, fill=PANEL, stroke=MUTED))

    # Стрілка залежності sensor_hub -> i2c_driver
    p.append(arrow(650, 250, 710, 250, color=POS, sw=2))
    p.append(text(680, 235, "PRIV_REQ", size=10.5, bold=True, color=POS))

    # Компонент C (Низькорівневий драйвер i2c_driver)
    p.append(rect(710, 70, 250, 330, fill=DIRTY, stroke=POS, sw=1.6))
    p.append(text(835, 95, "Компонент: i2c_driver", size=14, bold=True, color=POS))
    p.append(fitbox(725, 120, 220, 80, "Публічний для sensor_hub:\ninclude/i2c_bus.h\n(робота з регістрами I2C)", size=11.5, fill=BG, stroke=POS))
    p.append(fitbox(725, 210, 220, 85, "i2c_driver/CMakeLists.txt:\nidf_component_register(\n  SRCS \"i2c_bus.c\"\n  INCLUDE_DIRS \"include\"\n  REQUIRES driver\n)", size=10.5, fill=BG, stroke=LINE))
    p.append(fitbox(725, 315, 220, 65, "Ізольований від main:\nзміна i2c_driver не викликає\nперекомпіляції main.c", size=11, fill=BG, stroke=FIELD))

    render(os.path.join(IMG, "component-dependency-flow.svg"), W, H, *p,
           title="Поширення залежностей між компонентами")


# ── 3. Конвеєр генерації конфігурації Kconfig ───────────────────────────────
def fig_kconfig_pipeline():
    W, H = 1020, 420
    p = []

    p.append(text(510, 30, "Конвеєр конфігурації Kconfig: від дерева меню до кодогенерації",
                  size=15.5, bold=True))

    # Крок 1: Джерела правил
    p.append(rect(30, 70, 220, 310, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(140, 95, "1. Джерела правил", size=13.5, bold=True))
    p.append(fitbox(45, 120, 190, 60, "Kconfig.projbuild\n(пункти головного меню)", size=11.5, fill=BG))
    p.append(fitbox(45, 195, 190, 60, "компоненти/Kconfig\n(меню Component config)", size=11.5, fill=BG))
    p.append(fitbox(45, 270, 190, 80, "sdkconfig.defaults\n(базові версіоновані\nналаштування проєкту)", size=11, fill=CLEAN, stroke=FIELD))

    p.append(arrow(250, 225, 290, 225, color=LINE, sw=1.8))

    # Крок 2: Інтерактивне або CI/CD редагування
    p.append(rect(290, 70, 200, 310, fill=ACCENT, stroke=NEG, sw=1.8))
    p.append(text(390, 95, "2. Конфігурація", size=13.5, bold=True, color=NEG))
    p.append(fitbox(305, 130, 170, 90, "idf.py menuconfig\n(інтерактивний TUI)\nАБО\nCI/CD злиття дефолтів", size=11.5, fill=BG, stroke=NEG))
    p.append(arrow(390, 220, 390, 255, color=NEG, sw=1.6))
    p.append(fitbox(305, 260, 170, 95, "Файл sdkconfig\nТекстовий ключ-значення:\nCONFIG_WIFI_SSID=\"IoT\"\nCONFIG_PORT=8080", size=11, fill=DIRTY, stroke=POS))

    p.append(arrow(490, 225, 530, 225, color=LINE, sw=1.8))

    # Крок 3: Утиліта confgen.py
    p.append(rect(530, 70, 190, 310, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(625, 95, "3. confgen.py", size=13.5, bold=True))
    p.append(fitbox(545, 145, 160, 160, "Парсер Kconfiglib:\n- перевірка типів\n- резолюція depends on\n- обчислення default\n- генерація залежностей", size=11.5, fill=BG, stroke=LINE))

    p.append(arrow(720, 225, 760, 225, color=LINE, sw=1.8))

    # Крок 4: Згенеровані вихідні файли
    p.append(rect(760, 70, 230, 310, fill=PANEL, stroke=FIELD, sw=1.8))
    p.append(text(875, 95, "4. Згенеровані артефакти", size=13.5, bold=True, color=FIELD))
    p.append(fitbox(775, 125, 200, 100, "build/config/sdkconfig.h\n#define CONFIG_PORT 8080\n#define CONFIG_WIFI_SSID \\\n  \"IoT\"\n(використовується в C/C++)", size=10.5, fill=CLEAN, stroke=FIELD))
    p.append(fitbox(775, 245, 200, 105, "build/config/sdkconfig.cmake\nset(CONFIG_PORT 8080)\nset(CONFIG_WIFI_ENABLED 1)\n(використовується в CMake\nдля умовних файлів)", size=10.5, fill=CLEAN, stroke=FIELD))

    render(os.path.join(IMG, "kconfig-generation-pipeline.svg"), W, H, *p,
           title="Конвеєр конфігурації Kconfig")


# ── 4. Розкладка SPI Flash-пам'яті та таблиця розділів ───────────────────────
def fig_flash_layout():
    W, H = 1040, 460
    p = []

    p.append(text(520, 30, "Фізична розкладка SPI Flash у ESP32 та послідовність завантаження",
                  size=15.5, bold=True))

    y_top = 70
    h_bar = 90

    blocks = [
        ("0x0000", "0x1000", 30, 90, "ROM / Header", "Вектори скидання", PANEL, MUTED),
        ("0x1000", "0x8000", 125, 135, "2nd Bootloader", "bootloader.bin (~28 КБ)", DIRTY, POS),
        ("0x8000", "0x9000", 265, 110, "Partition Table", "partitions.bin (4 КБ)", ACCENT, NEG),
        ("0x9000", "0xD000", 380, 100, "NVS (Data)", "Енергонезалежна (16 КБ)", PANEL, MUTED),
        ("0xD000", "0xF000", 485, 90, "otadata", "Вибір OTA (8 КБ)", PANEL, MUTED),
        ("0x10000", "0x110000", 580, 200, "Factory / OTA_0 (App)", "Головна прошивка app.bin (1 МБ)", CLEAN, FIELD),
        ("0x110000", "0x210000", 785, 220, "OTA_1 (App)", "Резервний розділ OTA (1 МБ)", BG, MUTED),
    ]

    for start_addr, end_addr, bx, bw, title_b, sub_b, fill_c, stroke_c in blocks:
        p.append(rect(bx, y_top, bw, h_bar, fill=fill_c, stroke=stroke_c, sw=1.8))
        p.append(text(bx + bw/2, y_top + 30, title_b, size=11.5, bold=True, color=INK))
        p.append(text(bx + bw/2, y_top + 55, sub_b, size=10, color=MUTED))
        p.append(text(bx + 5, y_top + h_bar + 16, start_addr, size=9.5, color=LINE, anchor="start"))

    p.append(text(1005, y_top + h_bar + 16, "0x400000 (4 МБ)", size=9.5, color=LINE, anchor="end"))

    # Нижня частина: Хронологічний ланцюг завантаження
    p.append(rect(20, 210, 1000, 220, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(520, 235, "Хронологічний ланцюг виконання коду при старті мікроконтролера", size=13.5, bold=True))

    steps = [
        ("1. ROM Bootloader", "Зашитий у кремній.\nПеревіряє strapping-піни,\nініціалізує базовий SPI,\nзчитує 0x1000 у IRAM", 145, PANEL, LINE),
        ("2. 2nd Stage Bootloader", "Виконується з IRAM.\nЧитає таблицю 0x8000,\nзчитує otadata (0xD000),\nперевіряє хеш SHA256 образу", 395, DIRTY, POS),
        ("3. Ініціалізація MMU Flash", "Налаштовує кеш-сторінки MMU\nдля виконання інструкцій (XIP)\nбезпосередньо з NOR Flash", 645, ACCENT, NEG),
        ("4. Application (app_main)", "Запуск FreeRTOS планувальника,\nініціалізація периферії,\nвиклик користувацького коду", 895, CLEAN, FIELD),
    ]

    for title_s, desc_s, cx, fill_s, stroke_s in steps:
        p.append(rect(cx - 110, 255, 220, 155, fill=fill_s, stroke=stroke_s, sw=1.6))
        p.append(text(cx, 280, title_s, size=12.5, bold=True, color=stroke_s))
        p.append(mtext(cx, 310, desc_s, size=11, color=INK, lh=1.35))

    # Стрілки між кроками
    p.append(arrow(257, 332, 283, 332, color=LINE, sw=1.8))
    p.append(arrow(507, 332, 533, 332, color=LINE, sw=1.8))
    p.append(arrow(757, 332, 783, 332, color=LINE, sw=1.8))

    render(os.path.join(IMG, "flash-memory-layout.svg"), W, H, *p,
           title="Фізична розкладка SPI Flash та послідовність завантаження")


if __name__ == "__main__":
    fig_build_architecture()
    fig_component_dependencies()
    fig_kconfig_pipeline()
    fig_flash_layout()

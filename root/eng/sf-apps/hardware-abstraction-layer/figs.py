# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Архітектура шарів: Додаток, Драйвери, HAL, BSP, LL, Залізо ────────────
def fig_embedded_hal_layering_architecture():
    W, H = 1000, 680
    frags = []

    # Заголовок
    frags.append(text(W / 2, 34, "Багатошарова архітектура вбудованої системи: межі переносимості",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 58, "Розподіл обов'язків між додатком, драйверами компонентів, HAL, BSP та регістрами",
                      size=12, color=MUTED))

    # Ліва колонка: Рівні переносимості (маркери)
    left_margin = 60
    layer_w = 880

    # Зона 1: Додаток
    y_app = 85
    h_app = 75
    frags.append(rect(left_margin, y_app, layer_w, h_app, fill="#eef7f2", stroke=FIELD, sw=2, rx=8))
    frags.append(text(left_margin + 20, y_app + 26, "Прикладний рівень (Application / Business Logic)",
                      size=14, bold=True, color=FIELD, anchor="start"))
    frags.append(text(left_margin + 20, y_app + 50,
                      "Керування станами системи · Обробка бізнес-правил · Телеметрія · 100% переносимий код",
                      size=12, color=INK, anchor="start"))

    # Зона 2: Драйвери зовнішніх компонентів (Middleware / Device Drivers)
    y_dev = 175
    h_dev = 80
    frags.append(rect(left_margin, y_dev, layer_w, h_dev, fill="#f0f5ff", stroke=NEG, sw=2, rx=8))
    frags.append(text(left_margin + 20, y_dev + 26, "Драйвери зовнішніх компонентів (Device / Sensor Drivers)",
                      size=14, bold=True, color=NEG, anchor="start"))
    frags.append(text(left_margin + 20, y_dev + 50,
                      "Протоколи чипів: BME280 (I2C/SPI), W25Q Flash (SPI), дисплеї SSD1306 · Спираються ЛИШЕ на HAL",
                      size=12, color=INK, anchor="start"))

    # Зона 3: Шар абстракції апаратного забезпечення (HAL - Hardware Abstraction Layer)
    y_hal = 270
    h_hal = 95
    frags.append(rect(left_margin, y_hal, layer_w, h_hal, fill="#fff8e8", stroke=POS, sw=2.5, rx=8))
    frags.append(text(left_margin + 20, y_hal + 26, "Шар абстрагування апаратного забезпечення (HAL Contracts / Interfaces)",
                      size=14, bold=True, color=POS, anchor="start"))
    frags.append(text(left_margin + 20, y_hal + 50,
                      "Єдині інтерфейси периферійних шин: GpioPin, I2cMaster, SpiMaster, UartPort, HardwareTimer",
                      size=12, bold=True, color=INK, anchor="start"))
    frags.append(text(left_margin + 20, y_hal + 72,
                      "Не містить прив'язки до регістрів конкретного чипа; контракт перемикання та обміну байтами",
                      size=11.5, color=MUTED, anchor="start"))

    # Зона 4: BSP (Board Support Package)
    y_bsp = 380
    h_bsp = 85
    frags.append(rect(left_margin, y_bsp, layer_w, h_bsp, fill="#faf5ff", stroke="#7c3aed", sw=2, rx=8))
    frags.append(text(left_margin + 20, y_bsp + 26, "Пакет підтримки плати (BSP - Board Support Package)",
                      size=14, bold=True, color="#7c3aed", anchor="start"))
    frags.append(text(left_margin + 20, y_bsp + 50,
                      "Конфігурація плати: тактування (Clock Tree), мапування пінів (Pinmux), живлення периферії",
                      size=12, color=INK, anchor="start"))
    frags.append(text(left_margin + 20, y_bsp + 70,
                      "Поєднує конкретний MCU з розводкою друкованої плати: board_init(), led_on(), power_up()",
                      size=11.5, color=MUTED, anchor="start"))

    # Зона 5: LL / Вендорні драйвери периферії (Low-Layer / CMSIS / SDK)
    y_ll = 480
    h_ll = 85
    frags.append(rect(left_margin, y_ll, layer_w, h_ll, fill="#fdf2f2", stroke="#be123c", sw=2, rx=8))
    frags.append(text(left_margin + 20, y_ll + 26, "Низькорівневий шар / Регістри вендора (LL Drivers / CMSIS / ESP-IDF LL)",
                      size=14, bold=True, color="#be123c", anchor="start"))
    frags.append(text(left_margin + 20, y_ll + 50,
                      "STM32 LL / pico-sdk hardware_* / ESP-IDF hal / NXP fsl_*: прямий запис у регістри та бітмаски",
                      size=12, color=INK, anchor="start"))
    frags.append(text(left_margin + 20, y_ll + 70,
                      "0% переносимості між виробниками; максимальна швидкість доступу до кремнію",
                      size=11.5, color=MUTED, anchor="start"))

    # Зона 6: Фізичне залізо (Silicon & PCB)
    y_hw = 580
    h_hw = 75
    frags.append(rect(left_margin, y_hw, layer_w, h_hw, fill="#f3f4f6", stroke="#374151", sw=2, rx=8))
    frags.append(text(left_margin + 20, y_hw + 26, "Фізичний кремній та схемотехніка (Hardware Silicon & External ICs)",
                      size=14, bold=True, color="#374151", anchor="start"))
    frags.append(text(left_margin + 20, y_hw + 50,
                      "Периферійні блоки MCU (GPIO, I2C, SPI контролери, DMA, NVIC) + Зовнішні датчики на шинах PCB",
                      size=12, color=INK, anchor="start"))

    # З'єднувальні стрілки праворуч
    arrow_x = left_margin + layer_w - 40
    frags.append(arrow(arrow_x, y_app + h_app, arrow_x, y_dev, color=LINE, sw=2))
    frags.append(arrow(arrow_x, y_dev + h_dev, arrow_x, y_hal, color=LINE, sw=2))
    frags.append(arrow(arrow_x, y_hal + h_hal, arrow_x, y_bsp, color=LINE, sw=2))
    frags.append(arrow(arrow_x, y_bsp + h_bsp, arrow_x, y_ll, color=LINE, sw=2))
    frags.append(arrow(arrow_x, y_ll + h_ll, arrow_x, y_hw, color=LINE, sw=2))

    out_path = os.path.join(IMG, 'embedded-hal-layering-architecture.svg')
    render(out_path, W, H, *frags)
    print(f"Generated: {out_path}")


# ── 2. Порівняння C vtable та C++20 концептів/шаблонів ────────────────────────
def fig_zero_cost_cxx_hal_vs_c_vtable():
    W, H = 1040, 580
    frags = []

    # Заголовок
    frags.append(text(W / 2, 34, "Динамічний диспетчер (C Vtable) проти нульової вартості (C++20 Concepts)",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 58, "Порівняння витрат пам'яті RAM, Flash та тактів процесора при виклику методу HAL",
                      size=12, color=MUTED))

    half_w = 440
    left_x = 50
    right_x = 550
    top_y = 85
    box_h = 460

    # ── Ліва колонка: Динамічний поліморфізм у C (Таблиця покажчиків) ─────────
    frags.append(rect(left_x, top_y, half_w, box_h, fill="#fffaf5", stroke=POS, sw=2, rx=8))
    frags.append(text(left_x + half_w / 2, top_y + 30, "Динамічний C HAL (Таблиця покажчиків)",
                      size=15, bold=True, color=POS))
    frags.append(text(left_x + half_w / 2, top_y + 52, "struct hal_gpio_ops + покажчик на контекст",
                      size=12, color=MUTED))

    # Схема RAM та виклику
    y_c1 = top_y + 75
    frags.append(rect(left_x + 20, y_c1, half_w - 40, 90, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
    frags.append(text(left_x + 35, y_c1 + 22, "1. Структура в RAM (Екземпляр девайса):", size=12, bold=True, anchor="start"))
    frags.append(text(left_x + 45, y_c1 + 45, "const struct hal_gpio_ops *ops;  // 4/8 байтів у RAM", size=11, color="#b91c1c", anchor="start"))
    frags.append(text(left_x + 45, y_c1 + 68, "void *ctx;                          // 4/8 байтів у RAM", size=11, color="#b91c1c", anchor="start"))

    y_c2 = y_c1 + 105
    frags.append(rect(left_x + 20, y_c2, half_w - 40, 105, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
    frags.append(text(left_x + 35, y_c2 + 22, "2. Механізм виклику під час виконання:", size=12, bold=True, anchor="start"))
    frags.append(text(left_x + 45, y_c2 + 45, "pin->ops->set_high(pin->ctx);", size=11.5, bold=True, color=INK, anchor="start"))
    frags.append(text(left_x + 45, y_c2 + 68, "• Зчитування покажчика vtable з RAM", size=11, color=MUTED, anchor="start"))
    frags.append(text(left_x + 45, y_c2 + 90, "• Непрямий перехід BLX R3 (зрив конвеєра CPU)", size=11, color=MUTED, anchor="start"))

    y_c3 = y_c2 + 120
    frags.append(rect(left_x + 20, y_c3, half_w - 40, 135, fill="#fee2e2", stroke=POS, sw=1.5, rx=5))
    frags.append(text(left_x + 35, y_c3 + 24, "Накладні витрати (Ціна абстракції):", size=12, bold=True, color=POS, anchor="start"))
    frags.append(text(left_x + 45, y_c3 + 48, "✖ RAM: 8-16 байтів на кожен пін / шину", size=11.5, color=INK, anchor="start"))
    frags.append(text(left_x + 45, y_c3 + 70, "✖ Flash: Vtables + прологи/епілоги (PUSH/POP)", size=11.5, color=INK, anchor="start"))
    frags.append(text(left_x + 45, y_c3 + 92, "✖ Час: 15-35 тактів на виклик (немає inlining)", size=11.5, color=INK, anchor="start"))
    frags.append(text(left_x + 45, y_c3 + 114, "✖ Оптимізатор не бачить констант адрес/масок", size=11.5, color=INK, anchor="start"))

    # ── Права колонка: Статичний поліморфізм у C++20 (Zero-Cost) ──────────────
    frags.append(rect(right_x, top_y, half_w, box_h, fill="#f4fbf7", stroke=FIELD, sw=2, rx=8))
    frags.append(text(right_x + half_w / 2, top_y + 30, "Статичний C++20 HAL (Zero-Cost)",
                      size=15, bold=True, color=FIELD))
    frags.append(text(right_x + half_w / 2, top_y + 52, "concept GpioPin + template / inline",
                      size=12, color=MUTED))

    # Схема RAM та виклику
    y_cpp1 = top_y + 75
    frags.append(rect(right_x + 20, y_cpp1, half_w - 40, 90, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
    frags.append(text(right_x + 35, y_cpp1 + 22, "1. Структура в RAM (Екземпляр девайса):", size=12, bold=True, anchor="start"))
    frags.append(text(right_x + 45, y_cpp1 + 45, "struct GpioPin<PortA, 5> {};  // Порожня структура", size=11, color=FIELD, anchor="start"))
    frags.append(text(right_x + 45, y_cpp1 + 68, "Розмір екземпляра в пам'яті: 0 байтів у RAM!", size=11, bold=True, color=FIELD, anchor="start"))

    y_cpp2 = y_cpp1 + 105
    frags.append(rect(right_x + 20, y_cpp2, half_w - 40, 105, fill="#ffffff", stroke=LINE, sw=1.2, rx=5))
    frags.append(text(right_x + 35, y_cpp2 + 22, "2. Механізм виклику під час компіляції:", size=12, bold=True, anchor="start"))
    frags.append(text(right_x + 45, y_cpp2 + 45, "pin.set_high();  // Повне вбудовування (inline)", size=11.5, bold=True, color=INK, anchor="start"))
    frags.append(text(right_x + 45, y_cpp2 + 68, "• Адреса регістра та бітова маска відомі наперед", size=11, color=MUTED, anchor="start"))
    frags.append(text(right_x + 45, y_cpp2 + 90, "• Компілятор генерує пряму інструкцію STR", size=11, color=MUTED, anchor="start"))

    y_cpp3 = y_cpp2 + 120
    frags.append(rect(right_x + 20, y_cpp3, half_w - 40, 135, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(right_x + 35, y_cpp3 + 24, "Накладні витрати (Нульова вартість):", size=12, bold=True, color=FIELD, anchor="start"))
    frags.append(text(right_x + 45, y_cpp3 + 48, "✔ RAM: Рівно 0 байтів (без динамічних таблиць)", size=11.5, color=INK, anchor="start"))
    frags.append(text(right_x + 45, y_cpp3 + 70, "✔ Flash: Жодних vtables і стек-фреймів виклику", size=11.5, color=INK, anchor="start"))
    frags.append(text(right_x + 45, y_cpp3 + 92, "✔ Час: 1 такт CPU (прямий запис у BSRR регістр)", size=11.5, color=INK, anchor="start"))
    frags.append(text(right_x + 45, y_cpp3 + 114, "✔ Dead Code Elimination видаляє весь зайвий код", size=11.5, color=INK, anchor="start"))

    out_path = os.path.join(IMG, 'zero-cost-cxx-hal-vs-c-vtable.svg')
    render(out_path, W, H, *frags)
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    fig_embedded_hal_layering_architecture()
    fig_zero_cost_cxx_hal_vs_c_vtable()

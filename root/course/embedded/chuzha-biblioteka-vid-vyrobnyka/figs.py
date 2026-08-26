# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. vendor-sdk-anatomy: Анатомія вендорського SDK ─────────────────────────
def fig_vendor_sdk_anatomy():
    W, H = 840, 480
    p = []

    # 1. Застосунок
    b_app, _, _ = textbox(
        420, 60,
        "Застосунок / Системна логіка\n(Зчитування температури, тиску, орієнтації)",
        size=13, bold=True, color=INK, fill="#e8f4fd", stroke=NEG, sw=1.8, pad=12
    )
    p.append(b_app)

    # Стрілка від програми до ядра SDK
    p.append(arrow(420, 88, 420, 130, color=INK, sw=1.8))
    p.append(text(430, 110, "sensor_get_data(&dev, ...)", size=11, color=MUTED, anchor="start", italic=True))

    # 2. Апаратно-незалежне ядро драйвера (Vendor SDK Core)
    p.append(rect(110, 136, 620, 160, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(text(420, 160, "Апаратно-незалежне ядро драйвера (Vendor SDK Core)", size=14, color=INK, bold=True))

    # Ліва внутрішня панель ядра
    p.append(rect(130, 180, 270, 96, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(mtext(265, 202, [
        "Математика і компенсація:",
        "• Калібрувальні формули",
        "• Розбір сирих бітів і регістрів",
        "• Завантаження мікрокоду"
    ], size=11, color=INK, anchor="middle"))

    # Права внутрішня панель ядра
    p.append(rect(440, 180, 270, 96, fill="#f0f4ff", stroke=NEG, sw=1.4, rx=6))
    p.append(mtext(575, 198, [
        "Дескриптор пристрою (struct dev):",
        "• void* intf_ptr (контекст шини)",
        "• read_fptr (вказівник читання)",
        "• write_fptr (вказівник запису)",
        "• delay_us (вказівник затримки)"
    ], size=10.5, color=NEG, anchor="middle"))

    # Стрілки від ядра до колбеків униз
    p.append(arrow(420, 296, 420, 346, color=INK, sw=1.8))
    p.append(text(430, 324, "Виклики через вказівники (dev->read / dev->delay)", size=11, color=POS, anchor="start", bold=True))

    # 3. Апаратні реалізації платформи (User Platform Layer)
    p.append(rect(110, 350, 620, 96, fill="#f1f5f9", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(420, 372, "Апаратний рівень платформи (Platform Hardware Layer)", size=13, color=FIELD, bold=True))

    p.append(rect(130, 386, 270, 50, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(mtext(265, 407, [
        "Драйвер шини МК (I2C / SPI)",
        "(HAL_I2C_Mem_Read / spi_write)"
    ], size=11, color=INK, anchor="middle"))

    p.append(rect(440, 386, 270, 50, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(mtext(575, 407, [
        "Служба часу (Timer / RTOS)",
        "(vTaskDelay / k_msleep / DWT)"
    ], size=11, color=INK, anchor="middle"))

    render(os.path.join(OUT, "vendor-sdk-anatomy.svg"), W, H, *p,
           title="Анатомія вендорського SDK: відокремлення ядра від апаратної платформи")


# ── 2. vendor-pitfalls-matrix: Приховані загрози вендорського коду ───────────
def fig_vendor_pitfalls():
    W, H = 840, 460
    p = []

    cols = [225, 615]
    rows = [140, 330]

    pitfalls = [
        (cols[0], rows[0], "Динамічна пам'ять (malloc / free)",
         ["• Непередбачуваний час виділення",
          "• Ризик фрагментації heap у тривалому часі",
          "• Збій у mission-critical / MISRA-C системах",
          "→ Лікування: статичні дескриптори"], POS, "#fdf2f2"),

        (cols[1], rows[0], "Блокуючий busy-wait у затримках",
         ["• delay_ms(100) палить мільйони тактів CPU",
          "• Голодування інших потоків у RTOS",
          "• Зрив жорстких часових дедлайнів",
          "→ Лікування: неблокуючий сон або переривання"], POS, "#fdf2f2"),

        (cols[0], rows[1], "Глобальний стан і static буфери",
         ["• Змінні static всередині функцій драйвера",
          "• Повна втрата реентрантності (reentrancy)",
          "• Неможливо підключити два однакових чипи",
          "→ Лікування: контекстний вказівник intf_ptr"], POS, "#fdf2f2"),

        (cols[1], rows[1], "Витрати стеку та відсутність меж",
         ["• Локальні буфери на 512–2048 байтів на стеку",
          "• Миттєвий Stack Overflow у потоці RTOS",
          "• Відсутність перевірок на NULL та межі",
          "→ Лікування: адаптер-валідатор і зовнішні буфери"], POS, "#fdf2f2"),
    ]

    for cx, cy, title, lines, col, fill in pitfalls:
        p.append(rect(cx - 180, cy - 80, 360, 160, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(cx, cy - 54, title, size=13, color=col, bold=True))
        p.append(line(cx - 165, cy - 42, cx + 165, cy - 42, color=col, sw=1.0, dash="3,3"))

        ty = cy - 24
        for ln in lines:
            bold_flag = ln.startswith("→")
            text_color = FIELD if bold_flag else INK
            p.append(text(cx - 160, ty, ln, size=10.5, color=text_color, anchor="start", bold=bold_flag))
            ty += 19

    render(os.path.join(OUT, "vendor-pitfalls-matrix.svg"), W, H, *p,
           title="Чотири головні підводні камені вендорського коду у вбудованих системах")


# ── 3. adapter-isolation-layer: Архітектура ізолюючого Адаптера ───────────────
def fig_adapter_isolation():
    W, H = 840, 430
    p = []

    # 1. Системний інтерфейс (ліворуч)
    p.append(rect(40, 70, 210, 320, fill="#e8f4fd", stroke=NEG, sw=1.8, rx=8))
    p.append(text(145, 100, "Системний шар", size=14, color=NEG, bold=True))
    p.append(text(145, 120, "(Чистий C++ / C API)", size=11, color=MUTED))
    p.append(line(55, 134, 235, 134, color=NEG, sw=1.0, dash="2,2"))

    p.append(mtext(145, 175, [
        "class ISensor {",
        "  virtual Result<Reading>",
        "    read() = 0;",
        "};",
        "",
        "Бізнес-логіка проєкту",
        "НЕ знає про структури",
        "Bosch, ST чи TI!"
    ], size=11, color=INK, anchor="middle"))

    # 2. Адаптер (посередині)
    p.append(rect(290, 70, 260, 320, fill="#f0fdf4", stroke=FIELD, sw=2.0, rx=8))
    p.append(text(420, 100, "Клас-Адаптер (Adapter)", size=15, color=FIELD, bold=True))
    p.append(text(420, 120, "Ізоляція та трансляція викликів", size=11, color=MUTED))
    p.append(line(305, 134, 535, 134, color=FIELD, sw=1.0, dash="2,2"))

    p.append(mtext(420, 168, [
        "• Зберігає struct bme280_dev",
        "• Володіє захистом шини (Mutex)",
        "• Статичні колбеки c_read / c_write",
        "• Передає this у dev.intf_ptr",
        "• Транслює помилки BME_* у Result",
        "• Неблокуючий сон у dev.delay_us",
        "• Автоматичне вимкнення в RAII"
    ], size=10.5, color=INK, anchor="middle", lh=1.4))

    # 3. Стороння бібліотека (праворуч)
    p.append(rect(590, 70, 210, 320, fill="#fff7ed", stroke=POS, sw=1.8, rx=8))
    p.append(text(695, 100, "Вендорський SDK", size=14, color=POS, bold=True))
    p.append(text(695, 120, "(Чужий C-код)", size=11, color=MUTED))
    p.append(line(605, 134, 785, 134, color=POS, sw=1.0, dash="2,2"))

    p.append(mtext(695, 175, [
        "bme280.c / bme280.h",
        "",
        "• Читання регістрів",
        "• Розрахунок формул",
        "• Специфічні структури",
        "• Коди BME280_E_*",
        "",
        "Компілюється ізольовано"
    ], size=11, color=INK, anchor="middle"))

    # Стрілки взаємодії між шарами
    p.append(arrow(250, 200, 290, 200, color=NEG, sw=1.8))
    p.append(text(270, 190, "read()", size=10, color=NEG, anchor="middle", bold=True))

    p.append(arrow(550, 200, 590, 200, color=FIELD, sw=1.8))
    p.append(text(570, 190, "API call", size=10, color=FIELD, anchor="middle", bold=True))

    # Зворотний колбек
    p.append(arrow(590, 250, 550, 250, color=POS, sw=1.8))
    p.append(text(570, 268, "callback", size=10, color=POS, anchor="middle", bold=True))

    render(os.path.join(OUT, "adapter-isolation-layer.svg"), W, H, *p,
           title="Патерн Адаптер: повна ізоляція стороннього драйвера від архітектури прошивки")


# ── 4. rtos-concurrency-model: Потокобезпечність і неблокуючі затримки ───────
def fig_rtos_concurrency():
    W, H = 840, 470
    p = []

    # Задачі RTOS
    b_t1, _, _ = textbox(180, 70, "Задача А (Telemetry)\nПріоритет: Нормальний", size=12, bold=True, color=INK, fill="#e8f4fd", stroke=NEG, sw=1.5, pad=10)
    b_t2, _, _ = textbox(660, 70, "Задача Б (Control Loop)\nПріоритет: Високий", size=12, bold=True, color=INK, fill="#e8f4fd", stroke=NEG, sw=1.5, pad=10)
    p.append(b_t1)
    p.append(b_t2)

    # Шар синхронізації та м'ютексів
    p.append(rect(100, 130, 640, 80, fill="#fdf4ff", stroke="#9333ea", sw=1.8, rx=8))
    p.append(text(420, 154, "Шар синхронізації (Дворівневе блокування)", size=13, color="#9333ea", bold=True))

    b_dev_mtx, _, _ = textbox(270, 184, "Device Mutex (Захист стану чипа)", size=10.5, color=INK, fill="#ffffff", stroke="#9333ea", sw=1.2, pad=6)
    b_bus_mtx, _, _ = textbox(570, 184, "Bus Mutex (Захист шини I2C/SPI)", size=10.5, color=INK, fill="#ffffff", stroke="#9333ea", sw=1.2, pad=6)
    p.append(b_dev_mtx)
    p.append(b_bus_mtx)

    # Стрілки від задач до м'ютексів
    p.append(arrow(180, 102, 240, 130, color=NEG, sw=1.6))
    p.append(arrow(660, 102, 600, 130, color=NEG, sw=1.6))

    # Обробка затримки delay_us
    p.append(rect(100, 240, 640, 100, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(420, 264, "Трансляція вендорської затримки (dev->delay_us)", size=13, color=FIELD, bold=True))

    b_delay1, _, _ = textbox(
        270, 304,
        "Затримка < 100 мкс:\nАпаратний таймер / DWT spin-wait\n(без оверхеду перемикання контексту)",
        size=10.5, color=INK, fill="#ffffff", stroke=FIELD, sw=1.2, pad=6
    )
    b_delay2, _, _ = textbox(
        570, 304,
        "Затримка ≥ 1 мс:\nvTaskDelay() / k_msleep()\n(віддача процесора іншим задачам)",
        size=10.5, color=INK, fill="#ffffff", stroke=FIELD, sw=1.2, pad=6
    )
    p.append(b_delay1)
    p.append(b_delay2)

    # Апаратний рівень
    p.append(arrow(420, 340, 420, 375, color=INK, sw=1.8))
    b_hw, _, _ = textbox(420, 405, "Фізична шина I2C / SPI та апаратні виводи сенсора", size=12, bold=True, color=INK, fill="#f1f5f9", stroke=LINE, sw=1.6, pad=10)
    p.append(b_hw)

    render(os.path.join(OUT, "rtos-concurrency-model.svg"), W, H, *p,
           title="Модель багатопотокової безпеки: м'ютекси та неблокуючі затримки в RTOS")


if __name__ == "__main__":
    fig_vendor_sdk_anatomy()
    fig_vendor_pitfalls()
    fig_adapter_isolation()
    fig_rtos_concurrency()
    print("Figures generated successfully.")

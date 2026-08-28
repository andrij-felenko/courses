# -*- coding: utf-8 -*-
import sys, os
# 4 рівні вгору від root/eng/sf-devices/driver-pattern до scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори ролей
GREEN  = "#1e8449"   # апаратний рівень / успіх / безпечні операції
GREENF = "#d5f5e3"
BLUE   = "#1a5276"   # публічний API / дескриптор / типи даних
BLUEF  = "#d6eaf8"
AMBER  = "#b9770e"   # конфігурація / стан / проміжний буфер
AMBERF = "#fdf3d6"
VIOLET = "#7d3c98"   # приватна реалізація / внутрішній стан
VIOLETF= "#f0e6fa"
RED    = "#c0392b"   # переривання / асинхронний потік / ISR
REDF   = "#fadbd8"


# ── 1. driver-handle-pattern-structure: структура та ізоляція дескриптора ─────
def fig_driver_handle_pattern_structure():
    W, H = 840, 500
    p = []

    # Заголовок фігури
    p.append(text(W / 2, 28, "Інкапсуляція стану драйвера через шаблон дескриптора (Handle Pattern)", size=13.5, color=INK, bold=True))

    # Ліва колонка: Публічний шар застосунку (Public API)
    x1, y1, w1 = 30, 54, 235
    h_col = 395
    p.append(rect(x1, y1, w1, h_col, fill="#ffffff", stroke=BLUE, sw=1.8, rx=6))
    p.append(rect(x1, y1, w1, 32, fill=BLUEF, stroke=BLUE, sw=1.8, rx=0))
    p.append(text(x1 + w1 / 2, y1 + 21, "Публічний API (i2c_driver.h)", size=11, color=BLUE, bold=True))

    # Публічний тип дескриптора (Opaque Pointer)
    p.append(rect(x1 + 10, y1 + 45, w1 - 20, 62, fill=BLUEF, stroke=BLUE, sw=1.2, rx=4))
    p.append(text(x1 + w1 / 2, y1 + 66, "Непрозорий дескриптор (Handle)", size=10, color=BLUE, bold=True))
    p.append(text(x1 + w1 / 2, y1 + 88, "typedef struct i2c_dev* i2c_h;", size=9.5, color=INK))

    # Структура конфігурації (ROM / Stack)
    p.append(rect(x1 + 10, y1 + 120, w1 - 20, 95, fill=AMBERF, stroke=AMBER, sw=1.2, rx=4))
    p.append(text(x1 + w1 / 2, y1 + 140, "Конфігурація (i2c_config_t)", size=10, color=AMBER, bold=True))
    p.append(mtext(x1 + w1 / 2, y1 + 160, "uint32_t clock_speed_hz\nuint8_t sda_pin, scl_pin\nuint16_t timeout_ms", size=9.5, color=INK, lh=1.3))

    # Публічні функції
    p.append(rect(x1 + 10, y1 + 230, w1 - 20, 130, fill="#f8f9fa", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(x1 + w1 / 2, y1 + 250, "Операції з дескриптором", size=10, color=INK, bold=True))
    p.append(mtext(x1 + w1 / 2, y1 + 272, "i2c_init(h, &cfg)\ni2c_write_sync(h, ...)\ni2c_read_async(h, ..., cb)\ni2c_get_stats(h, &st)", size=9.5, color=BLUE, lh=1.35))

    p.append(text(x1 + w1 / 2, y1 + 380, "Застосунок бачить лише API та покажчик", size=9.5, color=MUTED, italic=True))

    # Середня колонка: Приватна структура екземпляра в RAM (Private Driver Struct)
    x2, y2, w2 = 290, 54, 265
    p.append(rect(x2, y2, w2, h_col, fill="#ffffff", stroke=VIOLET, sw=1.8, rx=6))
    p.append(rect(x2, y2, w2, 32, fill=VIOLETF, stroke=VIOLET, sw=1.8, rx=0))
    p.append(text(x2 + w2 / 2, y2 + 21, "Приватна структура (RAM Instance)", size=11, color=VIOLET, bold=True))

    # Поля структури
    fields = [
        ("Базова адреса периферії", "I2C_TypeDef* regs  (0x40005400)", GREENF, GREEN),
        ("Машина станів (State)", "volatile i2c_state_t state (BUSY/IDLE)", AMBERF, AMBER),
        ("Контекст буферів DMA/IRQ", "uint8_t* tx_buf; size_t tx_len\nuint8_t* rx_buf; size_t rx_idx", VIOLETF, VIOLET),
        ("Асинхронний зворотний виклик", "i2c_callback_t on_complete\nvoid* user_data (closure context)", REDF, RED),
        ("Діагностика та статистика", "uint32_t bus_errors, timeouts", "#f4f6f8", MUTED),
    ]

    fy = y2 + 45
    for title, desc, fcol, scol in fields:
        fh = 56 if "\n" in desc else 48
        p.append(rect(x2 + 8, fy, w2 - 16, fh, fill=fcol, stroke=scol, sw=1.2, rx=3))
        p.append(text(x2 + 14, fy + 18, title, size=10, color=scol, bold=True, anchor="start"))
        if "\n" in desc:
            p.append(mtext(x2 + 14, fy + 35, desc, size=9.5, color=INK, anchor="start", lh=1.25))
        else:
            p.append(text(x2 + 14, fy + 36, desc, size=9.5, color=INK, anchor="start"))
        fy += fh + 8

    # Права колонка: Апаратний блок периферії (MMIO Registers)
    x3, y3, w3 = 580, 54, 230
    p.append(rect(x3, y3, w3, h_col, fill="#ffffff", stroke=GREEN, sw=1.8, rx=6))
    p.append(rect(x3, y3, w3, 32, fill=GREENF, stroke=GREEN, sw=1.8, rx=0))
    p.append(text(x3 + w3 / 2, y3 + 21, "Апаратний контролер (MMIO)", size=11, color=GREEN, bold=True))

    regs = [
        ("I2C1->CR1", "Керування тактуванням, PE, START, STOP"),
        ("I2C1->CR2", "Частота шини, переривання ITBUFEN"),
        ("I2C1->DR", "Регістр даних (Tx/Rx буфер FIFO)"),
        ("I2C1->SR1", "Статус: SB, ADDR, BTF, TXE, RXNE"),
        ("I2C1->SR2", "Статус: BUSY, MSL, DUALF"),
        ("DMA1_Ch6", "Контролер прямого доступу пам'яті"),
    ]

    ry = y3 + 45
    for rname, rdesc in regs:
        p.append(rect(x3 + 8, ry, w3 - 16, 48, fill=GREENF, stroke=GREEN, sw=1.1, rx=3))
        p.append(text(x3 + 14, ry + 18, rname, size=10, color=GREEN, bold=True, anchor="start"))
        p.append(text(x3 + 14, ry + 36, rdesc, size=9, color=INK, anchor="start"))
        ry += 56

    # Стрілки між колонками
    p.append(arrow(x1 + w1, y1 + 76, x2, y2 + 76, color=BLUE, sw=1.8))
    p.append(arrow(x2 + w2, y2 + 69, x3, y3 + 69, color=GREEN, sw=1.8))

    # Нижній пояснювальний рядок
    p.append(text(W / 2, H - 14, "Кожен фізичний порт має власний дескриптор у RAM, що унеможливлює стан гонитви та глобальні змінні", size=10.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "driver-handle-pattern-structure.svg"), W, H, *p,
           title="Інкапсуляція стану драйвера через дескриптор")


# ── 2. asynchronous-driver-callback-flow: життєвий цикл асинхронної транзакції ─
def fig_asynchronous_driver_callback_flow():
    W, H = 860, 520
    p = []

    # Заголовок фігури
    p.append(text(W / 2, 26, "Життєвий цикл неблокуючої транзакції: виклик, переривання та зворотний виклик", size=13.5, color=INK, bold=True))

    # 4 вертикальні лінії життя
    cols = [
        ("Застосунок (Task)", 120, BLUE, BLUEF),
        ("Драйвер (API)", 330, VIOLET, VIOLETF),
        ("Контролер / DMA", 540, GREEN, GREENF),
        ("Обробник IRQ / Callback", 740, RED, REDF),
    ]

    for title, cx, col, fill in cols:
        p.append(rect(cx - 85, 48, 170, 32, fill=fill, stroke=col, sw=1.6, rx=4))
        p.append(text(cx, 69, title, size=10.5, color=col, bold=True))
        p.append(line(cx, 80, cx, 465, color=MUTED, sw=1.2, dash="4,4"))

    # Часові кроки (стрілки та повідомлення)
    # Крок 1: Запит на транзакцію
    p.append(arrow(120, 110, 330, 110, color=BLUE, sw=1.6))
    p.append(text(225, 102, "1. transfer_async(&req, cb, ctx)", size=9.5, color=BLUE, bold=True))

    # Крок 2: Перевірка стану та налаштування апаратного блоку
    p.append(rect(315, 120, 30, 50, fill=VIOLETF, stroke=VIOLET, sw=1.4, rx=2))
    p.append(text(355, 138, "state: IDLE -> BUSY", size=9.5, color=VIOLET, anchor="start"))
    p.append(text(355, 156, "зберегти cb та ctx", size=9.5, color=MUTED, anchor="start"))

    p.append(arrow(330, 175, 540, 175, color=GREEN, sw=1.6))
    p.append(text(435, 167, "2. Запуск DMA / IRQ (CR1/CR2)", size=9.5, color=GREEN, bold=True))

    # Крок 3: Миттєве повернення керування у задачу
    p.append(arrow(330, 205, 120, 205, color=BLUE, sw=1.6))
    p.append(text(225, 197, "3. return DRIVER_OK (1.2 мкс)", size=9.5, color=BLUE))

    # Задача продовжує роботу (прямокутник поруч із лінією)
    p.append(rect(105, 215, 30, 95, fill=BLUEF, stroke=BLUE, sw=1.4, rx=2))
    p.append(rect(145, 230, 140, 55, fill="#f0f7fc", stroke=BLUE, sw=1.0, rx=4))
    p.append(mtext(215, 252, "Задача виконує\nіншу логіку або спить\nв очікуванні події RTOS", size=9, color=BLUE, anchor="middle", lh=1.2))

    # Апаратний блок передає байти
    p.append(rect(525, 185, 30, 125, fill=GREENF, stroke=GREEN, sw=1.4, rx=2))
    p.append(rect(565, 220, 145, 55, fill="#f0faf4", stroke=GREEN, sw=1.0, rx=4))
    p.append(mtext(637, 242, "Апаратна передача байтів\nпо фізичній шині\nбез задіяння CPU", size=9, color=GREEN, anchor="middle", lh=1.2))

    # Крок 4: Завершення передачі та апаратне переривання
    p.append(arrow(540, 315, 740, 315, color=RED, sw=1.8))
    p.append(text(640, 307, "4. Апаратне IRQ (Transfer Complete)", size=9.5, color=RED, bold=True))

    # Крок 5: Обробник переривання (ISR)
    p.append(rect(725, 320, 30, 85, fill=REDF, stroke=RED, sw=1.4, rx=2))
    p.append(arrow(740, 350, 330, 350, color=VIOLET, sw=1.4))
    p.append(text(535, 342, "5. Очищення прапорців, state -> IDLE", size=9.5, color=VIOLET))

    # Крок 6: Зворотний виклик користувача
    p.append(arrow(740, 390, 120, 390, color=RED, sw=1.6))
    p.append(text(430, 382, "6. Виклик cb(STATUS_OK, bytes, ctx) / надсилання події в чергу", size=9.5, color=RED, bold=True))

    # Завершення
    p.append(rect(105, 395, 30, 50, fill=BLUEF, stroke=BLUE, sw=1.4, rx=2))
    p.append(rect(145, 400, 140, 42, fill="#f0f7fc", stroke=BLUE, sw=1.0, rx=4))
    p.append(mtext(215, 418, "Обробка результату\nу фоновій задачі", size=9, color=BLUE, anchor="middle", lh=1.2))

    p.append(text(W / 2, H - 15, "Контекст ISR повинен бути мінімальним: зміна стану та сигналізація, без важких обчислень чи блокувань", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "asynchronous-driver-callback-flow.svg"), W, H, *p,
           title="Життєвий цикл асинхронної транзакції драйвера")


if __name__ == "__main__":
    fig_driver_handle_pattern_structure()
    fig_asynchronous_driver_callback_flow()
    print("Фігури успішно згенеровано у теці img/")

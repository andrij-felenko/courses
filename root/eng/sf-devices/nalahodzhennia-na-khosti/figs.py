# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_cycle_comparison():
    """Порівняння циклу зворотного зв'язку: чип (хвилини, HardFault) vs хост (мілісекунди, ASan/UBSan)."""
    W, H = 760, 430
    frags = []

    # Заголовок зверху
    frags.append(text(W / 2, 28, "Порівняння циклу розробки: на чипі проти на хості", size=16, color=INK, bold=True))

    # Ліва колонка — Target (МК)
    col_w = 340
    lx = 30
    frags.append(rect(lx, 50, col_w, 360, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    frags.append(text(lx + col_w / 2, 75, "Налагодження на чипі (Target)", size=14, color=POS, bold=True))
    frags.append(line(lx + 15, 88, lx + col_w - 15, 88, color="#fecaca", sw=1))

    t_steps = [
        ("1. Cross-компіляція (arm-none-eabi)", "Генерація .elf / .bin через важкий тулчейн"),
        ("2. Прошивка через SWD / JTAG", "Запис у Flash: 10–30 с (швидкість 50–100 КБ/с)"),
        ("3. Виконання на голій пам'яті", "Немає MMU: тихе затирання пам'яті суміжних структур"),
        ("4. Аварія без контексту", "Німий HardFault або зависання через тисячі тактів"),
        ("5. Пошук проблеми наосліп", "Лише 2–4 апаратні watchpoints, повільний printf"),
    ]

    for i, (title, desc) in enumerate(t_steps):
        sy = 102 + i * 54
        frags.append(rect(lx + 12, sy, col_w - 24, 46, fill=BG, stroke="#fca5a5", sw=1, rx=4))
        frags.append(text(lx + 20, sy + 18, title, size=11, color=INK, anchor="start", bold=True))
        frags.append(text(lx + 20, sy + 35, desc, size=10, color=MUTED, anchor="start"))
        if i < len(t_steps) - 1:
            frags.append(arrow(lx + col_w / 2, sy + 46, lx + col_w / 2, sy + 54, color=POS))

    frags.append(rect(lx + 12, 375, col_w - 24, 26, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    frags.append(text(lx + col_w / 2, 392, "Тривалість ітерації: 30–120 секунд на тест", size=11, color=POS, bold=True))

    # Права колонка — Host (комп'ютер)
    rx = 390
    frags.append(rect(rx, 50, col_w, 360, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(rx + col_w / 2, 75, "Налагодження на хості (Host-Based)", size=14, color=FIELD, bold=True))
    frags.append(line(rx + 15, 88, rx + col_w - 15, 88, color="#bbf7d0", sw=1))

    h_steps = [
        ("1. Нативна компіляція (Clang / GCC)", "Збірка під x86-64 / ARM64 з прапорцями санітайзерів"),
        ("2. Запуск у пам'яті хоста (RAM)", "Виконання стартує за 1–5 мілісекунд без прошивки"),
        ("3. Повний захист пам'яті (MMU + ASan)", "Тіньова пам'ять ловить вихід за межі на 1 байт"),
        ("4. Миттєва локалізація", "UBSan та ASan зупиняють процес на точному рядку коду"),
        ("5. Інтерактивний GDB + Valgrind", "Необмежені breakpoints, зворотний слід, аналіз пам'яті"),
    ]

    for i, (title, desc) in enumerate(h_steps):
        sy = 102 + i * 54
        frags.append(rect(rx + 12, sy, col_w - 24, 46, fill=BG, stroke="#86efac", sw=1, rx=4))
        frags.append(text(rx + 20, sy + 18, title, size=11, color=INK, anchor="start", bold=True))
        frags.append(text(rx + 20, sy + 35, desc, size=10, color=MUTED, anchor="start"))
        if i < len(h_steps) - 1:
            frags.append(arrow(rx + col_w / 2, sy + 46, rx + col_w / 2, sy + 54, color=FIELD))

    frags.append(rect(rx + 12, 375, col_w - 24, 26, fill="#dcfce7", stroke=FIELD, sw=1, rx=4))
    frags.append(text(rx + col_w / 2, 392, "Тривалість ітерації: 0.1–0.5 секунди на 100 тестів", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, 'host-vs-target-cycle.svg'), W, H, *frags,
           title="Порівняння циклів налагодження на фізичному чипі та на хості")


def fig_hal_mock_arch():
    """Архітектура ізоляції коду через межу HAL та взаємозамінні бекенди."""
    W, H = 760, 420
    frags = []

    frags.append(text(W / 2, 26, "Архітектура ізоляції: межа HAL та підміна бекендів", size=16, color=INK, bold=True))

    # Верхній шар: Бізнес-логіка та алгоритми
    bx, by, bw, bh = 60, 50, 640, 70
    frags.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(bx + bw / 2, by + 24, "Апаратно-незалежний шар (Бізнес-логіка та протоколи)", size=13, color=INK, bold=True))
    frags.append(text(bx + bw / 2, by + 46, "Парсери телеметрії · Обчислення контрольних сум · Кінцеві автомати (FSM) · Фільтри замірів", size=11, color=MUTED))

    # Межа HAL (Інтерфейс)
    ix, iy, iw, ih = 100, 155, 560, 50
    frags.append(rect(ix, iy, iw, ih, fill="#eff6ff", stroke=NEG, sw=2, rx=6))
    frags.append(text(ix + iw / 2, iy + 22, "Межа абстракції заліза (Hardware Abstraction Layer Interface)", size=13, color=NEG, bold=True))
    frags.append(text(ix + iw / 2, iy + 39, "hal_i2c_transfer() · hal_spi_exchange() · hal_gpio_write() · hal_get_tick_ms()", size=11, color=INK))

    # Стрілка зверху вниз до HAL
    frags.append(arrow(W / 2, by + bh, W / 2, iy, color=NEG, sw=1.8))

    # Два нижні блоки
    # Лівий — Target Backend
    tx, ty, tw, th = 60, 245, 300, 150
    frags.append(rect(tx, ty, tw, th, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    frags.append(text(tx + tw / 2, ty + 24, "Target Backend (Прошивка МК)", size=13, color=POS, bold=True))
    frags.append(line(tx + 12, ty + 36, tx + tw - 12, ty + 36, color="#fecaca", sw=1))
    frags.append(text(tx + 16, ty + 58, "• Прямий запис у MMIO регістри периферії", size=11, color=INK, anchor="start"))
    frags.append(text(tx + 16, ty + 78, "• Апаратні переривання (NVIC / INTC)", size=11, color=INK, anchor="start"))
    frags.append(text(tx + 16, ty + 98, "• DMA контролери та тактове дерево", size=11, color=INK, anchor="start"))
    frags.append(text(tx + 16, ty + 124, "Призначення: Робота на фізичній платі", size=11, color=POS, anchor="start", bold=True))

    # Правий — Host Mock Backend
    mx, my, mw, mh = 400, 245, 300, 150
    frags.append(rect(mx, my, mw, mh, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(mx + mw / 2, my + 24, "Host Mock Backend (Тестовий стенд)", size=13, color=FIELD, bold=True))
    frags.append(line(mx + 12, my + 36, mx + mw - 12, my + 36, color="#bbf7d0", sw=1))
    frags.append(text(mx + 16, my + 58, "• Віртуальні масиви регістрів датчиків у RAM", size=11, color=INK, anchor="start"))
    frags.append(text(mx + 16, my + 78, "• Ін'єкція збоїв: NACK, бітові спотворення", size=11, color=INK, anchor="start"))
    frags.append(text(mx + 16, my + 98, "• Симуляція переповнення та тайм-аутів", size=11, color=INK, anchor="start"))
    frags.append(text(mx + 16, my + 124, "Призначення: ASan, UBSan, Valgrind, CI/CD", size=11, color=FIELD, anchor="start", bold=True))

    # Стрілки від HAL до бекендів
    frags.append(arrow(ix + 120, iy + ih, tx + tw / 2, ty, color=POS, sw=1.5))
    frags.append(arrow(ix + iw - 120, iy + ih, mx + mw / 2, my, color=FIELD, sw=1.5))

    render(os.path.join(IMG, 'hal-mock-architecture.svg'), W, H, *frags,
           title="Архітектура ізоляції бізнес-логіки від апаратних регістрів через межу HAL")


def fig_asan_shadow_memory():
    """Схема роботи тіньової пам'яті AddressSanitizer (Shadow Memory і Redzones)."""
    W, H = 760, 440
    frags = []

    frags.append(text(W / 2, 26, "Механізм AddressSanitizer: проектування пам'яті та Redzones", size=16, color=INK, bold=True))

    # Блок застосунку (Application Memory)
    ax, ay, aw, ah = 50, 52, 660, 150
    frags.append(rect(ax, ay, aw, ah, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(ax + 16, ay + 20, "Пам'ять застосунку (Application Memory: 8 байтів на чанк)", size=12, color=INK, anchor="start", bold=True))

    # 8 чанків по 8 байтів
    cell_w = 75
    y_cells = ay + 36
    chunks = [
        ("Redzone", "#fee2e2", POS, "Отруєно [0xFA]"),
        ("Redzone", "#fee2e2", POS, "Отруєно [0xFA]"),
        ("buf[0..7]", "#dcfce7", FIELD, "Валідно [0x00]"),
        ("buf[8..15]", "#dcfce7", FIELD, "Валідно [0x00]"),
        ("buf[16..19]", "#fef9c3", "#ca8a04", "Частково [0x04]"),
        ("Redzone", "#fee2e2", POS, "Отруєно [0xFA]"),
        ("Redzone", "#fee2e2", POS, "Отруєно [0xFA]"),
        ("Сусідня змінна", "#e0e7ff", NEG, "Валідно [0x00]"),
    ]

    for i, (name, fill_c, stroke_c, _) in enumerate(chunks):
        cx = ax + 30 + i * cell_w
        frags.append(rect(cx, y_cells, cell_w - 6, 48, fill=fill_c, stroke=stroke_c, sw=1.5, rx=3))
        frags.append(text(cx + (cell_w - 6) / 2, y_cells + 22, name, size=10, color=stroke_c, bold=True))
        frags.append(text(cx + (cell_w - 6) / 2, y_cells + 38, "8 байтів", size=9, color=MUTED))

    # Напис про невалідний доступ під чанками в межах блоку застосунку
    frags.append(rect(ax + 180, ay + 96, 430, 42, fill="#fef2f2", stroke=POS, sw=1, rx=4))
    frags.append(text(ax + 195, ay + 114, "Спроба запису buf[20]: потрапляння в Redzone [0xFA]", size=11, color=POS, anchor="start", bold=True))
    frags.append(text(ax + 195, ay + 130, "→ Інструментований код миттєво генерує SIGABRT і стек викликів", size=10, color=MUTED, anchor="start"))

    # Формула посередині між блоками
    mid_box_y = ay + ah + 14
    frags.append(line(W / 2, ay + ah, W / 2, mid_box_y, color=NEG, sw=1.5, dash="3,3"))
    frags.append(rect(W / 2 - 180, mid_box_y, 360, 24, fill="#eff6ff", stroke=NEG, sw=1, rx=4))
    frags.append(text(W / 2, mid_box_y + 16, "Shadow_Address = (App_Address >> 3) + Offset", size=11, color=NEG, bold=True))
    frags.append(arrow(W / 2, mid_box_y + 24, W / 2, mid_box_y + 44, color=NEG, sw=1.5))

    # Блок тіньової пам'яті (Shadow Memory)
    sx, sy, sw, sh = 50, 280, 660, 135
    frags.append(rect(sx, sy, sw, sh, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(sx + 16, sy + 22, "Тіньова пам'ять (Shadow Memory: 1 байт на кожні 8 байтів застосунку)", size=12, color=INK, anchor="start", bold=True))

    sy_cells = sy + 40
    for i, (_, fill_c, stroke_c, val_str) in enumerate(chunks):
        cx = sx + 30 + i * cell_w
        frags.append(rect(cx, sy_cells, cell_w - 6, 46, fill=fill_c, stroke=stroke_c, sw=1.5, rx=3))
        frags.append(text(cx + (cell_w - 6) / 2, sy_cells + 20, val_str.split(" ")[1], size=11, color=stroke_c, bold=True))
        frags.append(text(cx + (cell_w - 6) / 2, sy_cells + 36, val_str.split(" ")[0], size=9, color=MUTED))

    render(os.path.join(IMG, 'asan-shadow-memory.svg'), W, H, *frags,
           title="Структура Shadow Memory та виявлення переповнення буфера через Redzone")


def fig_ci_pipeline():
    """Конвеєр автоматизованого тестування в CI/CD з санітайзерами та аналізом покриття."""
    W, H = 760, 390
    frags = []

    frags.append(text(W / 2, 26, "Конвеєр автоматизації тестування вбудованого коду (CI/CD Pipeline)", size=16, color=INK, bold=True))

    stages = [
        ("1. Збірка з ASan / UBSan", "clang -fsanitize=address,undefined", "#eff6ff", NEG),
        ("2. Запуск Unit-тестів", "Миттєве виявлення помилок пам'яті та UB", "#f0fdf4", FIELD),
        ("3. Valgrind Memcheck", "Пошук неініціалізованих змінних у RAM", "#fef9c3", "#ca8a04"),
        ("4. Звіт покриття Gcov / Lcov", "Перевірка 100% покриття критичних гілок", "#faf5ff", "#9333ea"),
        ("5. Релізний шлюз (Gate)", "Блокування злиття при дефектах пам'яті", "#f8fafc", INK),
    ]

    sw = 120
    sh = 130
    gap = 24
    start_x = (W - (len(stages) * sw + (len(stages) - 1) * gap)) / 2
    sy = 60

    for i, (title, sub, fill_c, stroke_c) in enumerate(stages):
        x = start_x + i * (sw + gap)
        frags.append(rect(x, sy, sw, sh, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        frags.append(circle(x + sw / 2, sy + 26, 14, fill=BG, stroke=stroke_c, sw=2))
        frags.append(text(x + sw / 2, sy + 31, str(i + 1), size=12, color=stroke_c, bold=True))

        lines_t = title.split(" ", 1)
        frags.append(text(x + sw / 2, sy + 58, lines_t[1] if len(lines_t) > 1 else lines_t[0], size=11, color=INK, bold=True))

        # Опис у кілька рядків
        words = sub.split(" ")
        w1 = " ".join(words[:len(words)//2])
        w2 = " ".join(words[len(words)//2:])
        frags.append(text(x + sw / 2, sy + 82, w1, size=9, color=MUTED))
        frags.append(text(x + sw / 2, sy + 96, w2, size=9, color=MUTED))

        if i < len(stages) - 1:
            ax1 = x + sw + 2
            ax2 = x + sw + gap - 2
            frags.append(arrow(ax1, sy + sh / 2, ax2, sy + sh / 2, color=MUTED, sw=1.5))

    # Нижній блок: Чому це можливо
    frags.append(rect(start_x, 220, W - 2 * start_x, 140, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(W / 2, 245, "Ключові переваги для автономного CI/CD конвеєра", size=13, color=INK, bold=True))

    benefits = [
        ("Повна незалежність від заліза", "Тести виконуються на стандартних x86-64 / ARM64 раннерах у хмарі без фізичних плат"),
        ("Паралелізація та масштабування", "Сотні тестових наборів запускаються паралельно у Docker-контейнерах за лічені секунди"),
        ("100% повторюваність збоїв", "Детерміновані віртуальні моки усувають плаваючі апаратні збої та шуми живлення"),
    ]

    for i, (h, d) in enumerate(benefits):
        by = 270 + i * 26
        frags.append(circle(start_x + 20, by + 4, 4, fill=FIELD, stroke=FIELD, sw=1))
        frags.append(text(start_x + 32, by + 8, h + ":", size=11, color=INK, anchor="start", bold=True))
        frags.append(text(start_x + 245, by + 8, d, size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'ci-coverage-pipeline.svg'), W, H, *frags,
           title="Автоматизований конвеєр перевірки вбудованого коду в CI/CD")


def main():
    fig_cycle_comparison()
    fig_hal_mock_arch()
    fig_asan_shadow_memory()
    fig_ci_pipeline()
    print("Всі 4 фігури успішно згенеровано.")


if __name__ == '__main__':
    main()

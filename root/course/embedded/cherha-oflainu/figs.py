# -*- coding: utf-8 -*-
"""Генерація фігур для теми 'Черга офлайну: збережи-й-перешли'."""
import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_store_and_forward_arch():
    """Архітектура підсистеми Store-and-Forward: шлях даних в онлайні та офлайні."""
    w, h = 860, 420
    frags = []

    # Заголовок секцій
    frags.append(text(200, 30, "Джерела та селекція", size=15, bold=True, color=LINE))
    frags.append(text(510, 30, "Буферизація та носії", size=15, bold=True, color=LINE))
    frags.append(text(750, 30, "Мережевий вихід", size=15, bold=True, color=LINE))

    frags.append(line(350, 20, 350, 400, color="#d0d7de", sw=1.5, dash="4,4"))
    frags.append(line(670, 20, 670, 400, color="#d0d7de", sw=1.5, dash="4,4"))

    # Блоки джерел
    frags.append(fitbox(30, 60, 140, 50, "Давачі (IMU, GPS)\n50 Гц потік", size=12, fill="#f8fafc"))
    frags.append(fitbox(30, 130, 140, 50, "Статус системи\n1 Гц телеметрія", size=12, fill="#f8fafc"))
    frags.append(fitbox(30, 200, 140, 50, "Критичні тривоги\nАварії та події", size=12, fill="#fef2f2", stroke=POS))

    # Селектор / класифікатор
    frags.append(fitbox(200, 95, 125, 130, "Класифікатор\nі фільтр\nпріоритетів", size=13, bold=True, fill="#f1f5f9"))

    frags.append(arrow(170, 85, 200, 120))
    frags.append(arrow(170, 155, 200, 160))
    frags.append(arrow(170, 225, 200, 195))

    # Сховища
    frags.append(fitbox(380, 70, 130, 65, "Оперативна пам'ять\nRAM буфер\n(Експрес-шлях)", size=12, fill="#ecfdf5", stroke=FIELD))
    frags.append(fitbox(380, 190, 140, 85, "Енергонезалежне\nсховище Flash/FRAM\n(Кільцева черга\nофлайну)", size=12, fill="#fffbeb", stroke="#d97706"))

    # Стрілки від фільтра до сховищ
    frags.append(arrow(325, 130, 380, 100, color=FIELD, sw=2))
    frags.append(text(350, 105, "Онлайн", size=11, color=FIELD, bold=True))

    frags.append(arrow(325, 190, 380, 220, color="#d97706", sw=2))
    frags.append(text(348, 235, "Офлайн", size=11, color="#d97706", bold=True))

    # Двоколійний диспетчер вивантаження
    frags.append(fitbox(545, 120, 105, 140, "Диспетчер\nвивантаження\n(Two-Track\nDrain)", size=12, bold=True, fill="#eff6ff", stroke=NEG))

    frags.append(arrow(510, 102, 545, 150, color=FIELD, sw=2))
    frags.append(arrow(520, 232, 545, 210, color="#d97706", sw=2))

    # Вихід у канал
    frags.append(fitbox(695, 95, 140, 60, "Пріоритетний потік\n(Свіжий стан)", size=12, bold=True, fill="#ecfdf5", stroke=FIELD))
    frags.append(fitbox(695, 205, 140, 60, "Фонова докачка\n(Історія з Flash)", size=12, bold=True, fill="#f8fafc", stroke=MUTED))

    frags.append(arrow(650, 155, 695, 125, color=FIELD, sw=2))
    frags.append(arrow(650, 220, 695, 235, color=LINE, sw=1.8))

    # Нижня плашка зі статусом каналу
    frags.append(fitbox(150, 340, 560, 50, "Стан каналу: ОФЛАЙН → накопичуємо у Flash | ОНЛАЙН → свіже негайно + історія у фоні", size=12, bold=True, fill="#f8fafc", stroke=LINE))

    render(os.path.join(IMG_DIR, "store-and-forward-arch.svg"), w, h, *frags)


def fig_ring_buffer_flash_sectors():
    """Організація кільцевої черги на секторах Flash-пам'яті: голови, хвости та стирання."""
    w, h = 860, 360
    frags = []

    # 6 секторів у кільці
    sectors = [
        ("Сектор 0\n(Вивантажено)", "#f1f5f9", LINE, "Вільний / очікує стирання"),
        ("Сектор 1\n(Хвіст / Tail)", "#dbeafe", NEG, "Найстаріші дані (читання)"),
        ("Сектор 2\n(Заповнено)", "#fef3c7", "#d97706", "Невідправлена історія"),
        ("Сектор 3\n(Заповнено)", "#fef3c7", "#d97706", "Невідправлена історія"),
        ("Сектор 4\n(Голова / Head)", "#dcfce7", FIELD, "Активний запис кадрів"),
        ("Сектор 5\n(Стерто 0xFF)", "#ffffff", "#94a3b8", "Підготовлений сектор"),
    ]

    sec_w = 125
    sec_h = 130
    start_x = 40
    start_y = 70

    for i, (name, fill_c, stroke_c, sub) in enumerate(sectors):
        x = start_x + i * 132
        frags.append(fitbox(x, start_y, sec_w, sec_h, name, size=13, bold=True, fill=fill_c, stroke=stroke_c, sw=2))
        frags.append(fitbox(x, start_y + sec_h + 12, sec_w, 45, sub, size=11, fill="#fafafa", stroke="#e2e8f0"))

    # Покажчики Head і Tail
    # Tail вказує на Сектор 1
    frags.append(arrow(238, 25, 238, 65, color=NEG, sw=2.5))
    frags.append(text(238, 18, "Tail (Звідси читаємо)", size=12, bold=True, color=NEG))

    # Head вказує на Сектор 4
    frags.append(arrow(634, 25, 634, 65, color=FIELD, sw=2.5))
    frags.append(text(634, 18, "Head (Сюди пишемо)", size=12, bold=True, color=FIELD))

    # Пояснення напрямку руху
    frags.append(arrow(180, 275, 680, 275, color=LINE, sw=2))
    frags.append(text(430, 298, "Напрямок просування черги (Append-Only) → від старого до нового", size=12, bold=True, color=LINE))

    # Попереджувальний сектор
    frags.append(text(765, 275, "Erase Ahead:", size=11, bold=True, color=POS))
    frags.append(text(765, 292, "Сектор 5 заздалегідь", size=10, color=MUTED))
    frags.append(text(765, 307, "стертий у 0xFF", size=10, color=MUTED))

    render(os.path.join(IMG_DIR, "ring-buffer-flash-sectors.svg"), w, h, *frags)


def fig_eviction_strategies():
    """Порівняння політик витіснення: сліпий FIFO проти пріоритетного проріджування."""
    w, h = 860, 350
    frags = []

    # Ліва колонка: Сліпий FIFO
    frags.append(fitbox(40, 30, 370, 45, "Сліпе витіснення (Flat FIFO)", size=14, bold=True, fill="#fee2e2", stroke=POS))
    
    frags.append(fitbox(50, 90, 350, 40, "12:00:01 — Аварія двигуна (Event)", size=12, fill="#fef2f2", stroke=POS))
    frags.append(fitbox(50, 135, 350, 35, "12:00:02 — Телеметрія 50 Гц (IMU)", size=11, fill="#f1f5f9"))
    frags.append(fitbox(50, 175, 350, 35, "12:00:03 — Телеметрія 50 Гц (IMU)", size=11, fill="#f1f5f9"))
    frags.append(fitbox(50, 215, 350, 35, "13:45:10 — Телеметрія 50 Гц (IMU)", size=11, fill="#f1f5f9"))

    # Хрестик на найстарішому критичному записі
    frags.append(arrow(20, 110, 48, 110, color=POS, sw=2))
    frags.append(text(225, 275, "Переповнення: стирається сектор з аварією,\nщоб зберегти одноманітний шум!", size=12, bold=True, color=POS))

    # Розділювач
    frags.append(line(430, 20, 430, 330, color="#d0d7de", sw=1.5, dash="4,4"))

    # Права колонка: Багаторівневе сховище
    frags.append(fitbox(450, 30, 370, 45, "Багаторівнева пріоритизація", size=14, bold=True, fill="#ecfdf5", stroke=FIELD))

    frags.append(fitbox(460, 90, 350, 60, "Кільце A: Журнал подій і тривог (Non-evictable)\n• Аварія двигуна • Знеструмлення • Помилки\nНіколи не витісняється телеметрією!", size=11, bold=True, fill="#fef2f2", stroke=POS))

    frags.append(fitbox(460, 160, 350, 50, "Кільце B: Періодичний статус (1 Гц)\n• Батарея • GPS координати • Температура\nПовільне витіснення за чергою", size=11, fill="#fefce8", stroke="#ca8a04"))

    frags.append(fitbox(460, 220, 350, 50, "Кільце C: Високочастотна телеметрія (50 Гц)\n• Сирі кути • Вібрація • Давачі\nПроріджування 50 Гц → 5 Гц або повний скид", size=11, fill="#f1f5f9", stroke=MUTED))

    frags.append(text(635, 295, "Результат: критичні події збережено на 100%,\nа менш важливий потік проріджено", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "eviction-strategies.svg"), w, h, *frags)


def fig_drain_order_comparison():
    """Порівняння порядку вивантаження: чистий FIFO проти двоколійного Two-Track."""
    w, h = 860, 370
    frags = []

    # Верхній блок: Чистий FIFO
    frags.append(fitbox(30, 25, 800, 40, "Стратегія 1: Чистий FIFO (вивантаження від старого до нового)", size=13, bold=True, fill="#fef2f2", stroke=POS))
    
    frags.append(fitbox(50, 75, 210, 50, "Зв'язок повернувся!\nКанал зайнятий...", size=11, fill="#f8fafc"))
    frags.append(fitbox(280, 75, 260, 50, "Вивантаження 50 МБ історії\n(запис 3-годинної давнини)", size=11, fill="#fee2e2", stroke=POS))
    frags.append(fitbox(560, 75, 250, 50, "Поточний стан апарата:\nЗАБЛОКОВАНО в черзі!", size=11, bold=True, fill="#fee2e2", stroke=POS))

    frags.append(arrow(260, 100, 280, 100))
    frags.append(arrow(540, 100, 560, 100))
    frags.append(text(430, 145, "Недолік: оператор не бачить, де дрон летить ЗАРАЗ, поки не прокачається вся історія!", size=12, color=POS, bold=True))

    # Нижній блок: Двоколійний Two-Track
    frags.append(fitbox(30, 180, 800, 40, "Стратегія 2: Двоколійне вивантаження (Two-Track Flush)", size=13, bold=True, fill="#ecfdf5", stroke=FIELD))

    frags.append(fitbox(50, 230, 220, 80, "Колія 1 (Realtime Fast-Path)\n• Свіжа телеметрія\n• Координати тут-і-зараз\n• Пріоритет: 80% смуги", size=11, bold=True, fill="#ecfdf5", stroke=FIELD))

    frags.append(fitbox(300, 230, 220, 80, "Колія 2 (Background Backfill)\n• Історія з Flash (FIFO)\n• Пакетне квитування ACK\n• Пріоритет: 20% смуги", size=11, bold=True, fill="#eff6ff", stroke=NEG))

    frags.append(fitbox(550, 230, 260, 80, "Сервер / Наземна станція\n• Миттєвий контроль апарата\n• Поступове заповнення\nісторичного графіка без затримок", size=11, fill="#fafafa", stroke=LINE))

    frags.append(arrow(270, 270, 300, 270, color=FIELD, sw=2))
    frags.append(arrow(520, 270, 550, 270, color=NEG, sw=2))
    frags.append(text(430, 335, "Результат: нульова затримка для свіжого керування + гарантована доставка історії", size=12, color=FIELD, bold=True))

    render(os.path.join(IMG_DIR, "drain-order-comparison.svg"), w, h, *frags)


def fig_power_loss_metadata():
    """Формат кадру з CRC32 та відновлення покажчиків після раптового знеструмлення."""
    w, h = 860, 360
    frags = []

    frags.append(text(430, 25, "Анатомія кадру в черзі Flash та відновлення після Power-Cut", size=15, bold=True, color=LINE))

    # Складові частини кадру
    fields = [
        ("Magic (2B)\n0xAA55", "#f1f5f9", 85),
        ("SeqNum (4B)\n0x00018A4F", "#e0e7ff", 115),
        ("Timestamp (8B)\nUnix Epoch ms", "#ede9fe", 130),
        ("Len & Typ (3B)\nLen=64, Typ=2", "#fce7f3", 115),
        ("Payload (N байтів)\nКорисне навантаження", "#fef3c7", 195),
        ("CRC-32 (4B)\nКонтрольна сума", "#dcfce7", 130),
    ]

    cur_x = 45
    box_y = 60
    box_h = 60
    for name, fill_c, bw in fields:
        frags.append(fitbox(cur_x, box_y, bw, box_h, name, size=11, bold=True, fill=fill_c, stroke=LINE))
        cur_x += bw + 8

    # Сценарій раптового знеструмлення під час запису
    frags.append(fitbox(45, 150, 770, 80, "Сценарій знеструмлення (Brownout під час запису другого кадру):\nКадр №1: [Magic ✓] [Seq=101 ✓] [Payload ✓] [CRC32 ✓] → Запис валідний, підтверджено\nКадр №2: [Magic ✓] [Seq=102] [Payload ... ЗНЕСТРУМЛЕННЯ! ... 0xFF 0xFF 0xFF] → CRC32 НЕ зійшовся!", size=12, fill="#fef2f2", stroke=POS))

    # Алгоритм відновлення при старті
    frags.append(fitbox(45, 250, 770, 85, "Алгоритм відновлення при завантаженні (Boot Recovery Scan):\n1. Читаємо активний сектор від початку, крок за кроком перевіряючи Magic та CRC-32 кожного кадру.\n2. Знайшовши перший битий CRC або чисті 0xFF — фіксуємо Head рівно на кінці останнього валідного Кадру №1.\n3. Жодного пошкодженого сміття не потрапляє в мережевий стек!", size=12, fill="#ecfdf5", stroke=FIELD))

    render(os.path.join(IMG_DIR, "power-loss-metadata.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_store_and_forward_arch()
    fig_ring_buffer_flash_sectors()
    fig_eviction_strategies()
    fig_drain_order_comparison()
    fig_power_loss_metadata()
    print("Усі фігури згенеровано успішно.")

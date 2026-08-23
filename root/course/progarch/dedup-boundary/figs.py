# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"

def fig_edge_vs_logic_split():
    """Порівняння двох підходів до дедуплікації:
    1. На межі (Edge Gateway + Redis cache) — дешево, швидко, але тимчасово.
    2. У глибині логіки (Domain Logic + Database ACID) — суворо, точно, але дорого."""
    W, H = 1040, 420
    f = []

    # Джерело: Клієнт / Повтори запитів
    f.append(fitbox(40, 160, 160, 90, "Клієнт / Retries\n\nДубльовані\nPOST / orders", size=13, bold=True, fill=NEUT, stroke=INK))

    # Розгалуження на два підходи
    f.append(arrow(200, 180, 260, 110, color=MUTED, sw=2))
    f.append(arrow(200, 230, 260, 300, color=MUTED, sw=2))

    # Верхній підхід: На межі (Edge Gateway)
    f.append(fitbox(260, 50, 240, 120, "1. Дедуп на межі (Edge Gateway)\n\n• Швидкий lookup у Redis\n• Відсікає 99% шторму дублів\n• Тимчасове вікно TTL", size=12, fill=AMBER_T, stroke=AMBER))
    f.append(arrow(500, 110, 560, 110, color=AMBER))
    f.append(fitbox(560, 80, 180, 60, "Відповідь з кешу (200 OK)\nбез виклику бекенду", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    # Нижній підхід: У логіці (Domain / DB)
    f.append(fitbox(260, 240, 240, 130, "2. Дедуп у логіці (Domain / DB)\n\n• Unique constraint в OLTP DB\n• Атомарність з бізнес-станом\n• Надійність при збоях воркера", size=12, fill=BLUE_T, stroke=NEG))
    f.append(arrow(500, 305, 560, 305, color=NEG))
    f.append(fitbox(560, 275, 180, 60, "ACID-транзакція у DB\nгарантована точність", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    # Порівняльна висновок-панель праворуч
    f.append(fitbox(780, 130, 220, 150, "Резюме архітектора\n\nМежа = Економія IOPS\nЛогіка = Точність ACID\n\nІдеально: Гібрид!", size=13, bold=True, fill=BG, stroke=INK))

    render(os.path.join(OUT, 'edge-vs-logic-split.svg'), W, H, *f,
           title="Порівняння дедуплікації на межі та всередині бізнес-логіки")

def fig_race_condition_at_edge():
    """Гонка дублів на межі: два паралельних запити на два різні Edge-вузли.
    Обидва роблять Read у Redis одночасно і проходять далі."""
    W, H = 1000, 380
    f = []

    f.append(fitbox(40, 140, 150, 80, "Клієнт (Retry)\n\nДубль 1 i Дубль 2\nодночасно!", size=13, bold=True, fill=RED_T, stroke=POS))

    # Два паралельні Edge вузли
    f.append(arrow(190, 160, 260, 100))
    f.append(arrow(190, 200, 260, 260))

    f.append(fitbox(260, 60, 200, 80, "Gateway Node A\n\n1. Read(Key) -> Not found\n2. Write(Key, In-Progress)", size=12, fill=NEUT))
    f.append(fitbox(260, 220, 200, 80, "Gateway Node B\n\n1. Read(Key) -> Not found!\n2. Write(Key, In-Progress)", size=12, fill=NEUT))

    # Спільний кеш / Redis
    f.append(fitbox(520, 140, 160, 90, "Кеш / Redis\n\nАсинхронна реплікація\nабо latency-вікно", size=12, fill=AMBER_T, stroke=AMBER))
    f.append(line(460, 100, 520, 160, color=MUTED, dash="4 3"))
    f.append(line(460, 260, 520, 200, color=MUTED, dash="4 3"))

    # Прорив обидвох запитів до Сервісу
    f.append(arrow(460, 100, 720, 100, color=POS, sw=2))
    f.append(arrow(460, 260, 720, 260, color=POS, sw=2))

    f.append(fitbox(720, 130, 240, 100, "Доменний Сервіс\n\nОтримав ДВА дублі!\nМежа не врятувала від race", size=13, bold=True, fill=RED_T, stroke=POS))

    render(os.path.join(OUT, 'race-condition-at-edge.svg'), W, H, *f,
           title="Гонка дублів при відсутності суворої розподіленої атомарності на межі")

def fig_premature_ack_hazard():
    """Раннє підтвердження на межі: Gateway зберігає ключ дедуплікації до завершення обробки.
    Якщо воркер падає, повторний запит клієнта блокується межею як дубль, а дані втрачено."""
    W, H = 1000, 360
    f = []

    f.append(fitbox(40, 130, 160, 80, "1. Клієнт\n\nНадсилає запит\nKey: TX-100", size=13, fill=NEUT))
    f.append(arrow(200, 170, 260, 170))

    f.append(fitbox(260, 120, 210, 100, "2. Edge Gateway\n\n• Зберігає Key в Redis\n• Передає воркеру", size=12, fill=AMBER_T, stroke=AMBER))
    f.append(arrow(470, 170, 530, 170))

    f.append(fitbox(530, 120, 200, 100, "3. Воркер / DB\n\nАварійний збій! (OOM / Crash)\nТранзакція відкотилася!", size=12, bold=True, fill=RED_T, stroke=POS))

    # Повтор запиту від клієнта
    f.append(fitbox(40, 250, 160, 80, "4. Повтор запиту\nчерез Retry\nKey: TX-100", size=12, fill=AMBER_T, stroke=AMBER))
    f.append(arrow(200, 290, 260, 290))

    f.append(fitbox(260, 250, 470, 80, "5. Блокування на межі: «Вже оброблено! (200 OK / 409)»\n\nХазард: Дані в DB НЕ записано, але межа вважає запит виконаним!", size=12, bold=True, fill=RED_T, stroke=POS))

    render(os.path.join(OUT, 'premature-ack-hazard.svg'), W, H, *f,
           title="Небезпека раннього підтвердження дедуплікації на межі при збоях воркера")

def fig_layered_dedup_architecture():
    """Гібридна двошарова дедуплікація:
    Шар 1 (Edge): Фільтр Блума / Redis TTL — грубий фільтр від штормів.
    Шар 2 (Logic): Unique Index у DB / Outbox — суворий ACID заслон."""
    W, H = 1020, 380
    f = []

    f.append(fitbox(40, 140, 150, 90, "Вхідний потік\nзапитів\n\n(Основні + Retries)", size=13, bold=True, fill=NEUT))

    f.append(arrow(190, 185, 250, 185))

    # Шар 1: Межа
    f.append(fitbox(250, 90, 240, 190, "Шар 1: Edge Filter (Redis/Bloom)\n\n• Coarse Deduplication\n• Перевірка TTL ключа\n• Відсікає 99% дублів\n• Захист від thundering herd", size=12, fill=AMBER_T, stroke=AMBER))

    # Відсічний потік 1
    f.append(arrow(370, 280, 370, 330, color=POS))
    f.append(fitbox(300, 330, 140, 40, "99% дублів відсічено", size=11, fill=RED_T))

    f.append(arrow(490, 185, 560, 185))

    # Шар 2: Доменний ACID
    f.append(fitbox(560, 90, 240, 190, "Шар 2: Domain ACID Gate (DB)\n\n• Fine Deduplication\n• UNIQUE constraint у DB\n• Transactional Outbox\n• 100% гарантія цілісності", size=12, fill=GREEN_T, stroke=FIELD))

    # Вихід
    f.append(arrow(800, 185, 860, 185, color=FIELD, sw=2))
    f.append(fitbox(860, 140, 130, 90, "Гарантовано\nєдине\nвиконання!", size=13, bold=True, fill=GREEN_T, stroke=FIELD))

    render(os.path.join(OUT, 'layered-dedup-architecture.svg'), W, H, *f,
           title="Дворівнева архітектура дедуплікації: грубий Edge-фільтр та суворий Domain ACID Gate")

if __name__ == '__main__':
    fig_edge_vs_logic_split()
    fig_race_condition_at_edge()
    fig_premature_ack_hazard()
    fig_layered_dedup_architecture()
    print("Figures generated successfully.")

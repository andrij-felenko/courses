# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

RED_T   = "#fdecea"
GREEN_T = "#f2faf5"
BLUE_T  = "#eaf0fd"
GREY_T  = "#f4f6f8"
WARN_T  = "#fef9e7"


# ── 1. Айсберг API: задокументований контракт проти спостережуваної поведінки ──
def fig_implicit_vs_explicit_contract():
    W, H = 1180, 620
    frags = []
    frags.append(text(W / 2, 36, "Айсберг API: задокументований контракт проти спостережуваної поведінки",
                      size=17, bold=True))

    # Водна лінія
    wl_y = 190
    frags.append(line(50, wl_y, W - 50, wl_y, color=NEG, sw=2.2, dash="6,6"))
    frags.append(text(W - 60, wl_y - 12, "Межа специфікації (водна лінія)", size=12, color=NEG, anchor="end", italic=True))

    # Верхівка айсберга (над водою)
    frags.append(fitbox(200, 65, 780, 100,
                         "ЯВНИЙ ДОКУМЕНТОВАНИЙ КОНТРАКТ (Верхівка)\n"
                         "• Типи аргументів і повертаних значень  • Коди помилок (HTTP 404, errno 2)\n"
                         "• Формальні схеми даних (Protobuf, JSON Schema)  • Семантичні гарантії SemVer",
                         size=13, bold=True, fill=GREEN_T, stroke=FIELD, sw=2.0))

    # Підводна частина айсберга (спостережувана реальність)
    frags.append(fitbox(100, 220, 980, 240,
                         "СПОСТЕРЕЖУВАНА ПОВЕДІНКА РЕАЛІЗАЦІЇ (Підводна частина)\n"
                         "За законом Гайрама, клієнти неминуче прив'язуються до цих недекларованих властивостей:",
                         size=13, bold=True, fill=RED_T, stroke=POS, sw=2.0))

    # Блоки спостережуваних деталей
    details = [
        (120, 280, 290, 75, "Порядок ітерації колекцій", "Хеш-таблиці без гарантії порядку,\nпослідовність полів у JSON"),
        (445, 280, 290, 75, "Тексти та форматування помилок", "Парсинг рядків 'file not found'\nзамість числових кодів"),
        (770, 280, 290, 75, "Часові характеристики (Latency)", "Очікування відповіді за 5 мс,\nпорядок фонових операцій"),
        (120, 370, 290, 75, "Мікроструктура протоколів", "Регістр заголовків HTTP,\nрозмір буферів, TLS-розширення"),
        (445, 370, 290, 75, "Внутрішній стек і стан", "Глибина стека, порядок викликів,\nпобічні ефекти алокатора"),
        (770, 370, 290, 75, "Терпимість до сміття (Postel)", "Прийняття некоректних полів,\nякі тепер не можна відкинути"),
    ]

    for x, y, w, h, head, body in details:
        frags.append(fitbox(x, y, w, h, f"{head}\n{body}", size=11.5, fill=BG, stroke=LINE, sw=1.2))

    # Підсумок у рамці
    frags.append(fitbox(100, 485, 980, 105,
                         "Парадокс сумісності:\n"
                         "Автор вважає публічним інтерфейсом лише верхівку над лінією.\n"
                         "Клієнтський код на практиці виконується проти всього айсберга.\n"
                         "Будь-яка зміна в підводній частині ламає клієнта так само, як і зміна публічного підпису.",
                         size=12.5, bold=True, fill=WARN_T, stroke=LINE, sw=1.6))

    render(os.path.join(IMG, 'implicit-vs-explicit-contract.svg'), W, H, *frags)


# ── 2. Петля закостеніння платформи: від неявної залежності до заморозки ───────
def fig_hyrums_law_ecosystem_ossification():
    W, H = 1200, 520
    frags = []
    frags.append(text(W / 2, 34, "Петля закостеніння платформи (Platform Ossification Loop)",
                      size=17, bold=True))

    boxes = [
        (60,  90, 230, 110, "1. Випуск API\nта оптимізація", "Платформа випускає API\nз детермінованою,\nале незадокументованою\nдеталлю реалізації", FIELD, GREEN_T),
        (350, 90, 230, 110, "2. Неявне\nзв'язування клієнтів", "Клієнти виявляють деталь\n(порядок ключів, latency)\nі зав'язують на неї\nсвої тести та логіку", LINE, GREY_T),
        (640, 90, 230, 110, "3. Рефакторинг\nабо виправлення", "Автор змінює деталь\n(новий хеш-алгоритм,\nшвидший пул потоків)\nу межах SemVer PATCH", LINE, GREY_T),
        (930, 90, 230, 110, "4. Аварія\nта регресія клієнтів", "Клієнтські сервіси\nпадають у продакшені.\nЗвинувачують автора\nу порушенні сумісності", POS, RED_T),
    ]

    for x, y, w, h, title, desc, col, tint in boxes:
        frags.append(fitbox(x, y, w, h, f"{title}\n\n{desc}", size=12, bold=True, fill=tint, stroke=col, sw=1.8))

    # Стрілки між верхніми кроками
    frags.append(arrow(290, 145, 345, 145, color=LINE, sw=2.0))
    frags.append(arrow(580, 145, 635, 145, color=LINE, sw=2.0))
    frags.append(arrow(870, 145, 925, 145, color=LINE, sw=2.0))

    # Зворотний рух унизу: Закостеніння
    frags.append(fitbox(200, 280, 800, 100,
                         "5. Закостеніння системи (Ossification)\n"
                         "Автор змушений скасувати оптимізацію, заморозити старий баг або додати шар емуляції.\n"
                         "Незадокументована поведінка назавжди стає частиною незмінного стандарту.",
                         size=13, bold=True, fill=RED_T, stroke=POS, sw=2.2))

    # Стрілка вниз від 4 до 5
    frags.append(arrow(1045, 200, 1045, 330, color=POS, sw=2.0))
    frags.append(arrow(1045, 330, 1005, 330, color=POS, sw=2.0))

    # Стрілка назад від 5 до 1 (параліч оновлень)
    frags.append(arrow(200, 330, 175, 330, color=POS, sw=2.0))
    frags.append(arrow(175, 330, 175, 205, color=POS, sw=2.0))
    frags.append(text(120, 260, "Параліч\nрозвитку", size=12, color=POS, bold=True, anchor="middle"))

    # Блок висновку
    frags.append(fitbox(150, 415, 900, 75,
                         "Наслідок закостеніння: чим популярніша бібліотека чи протокол (TCP, TLS, Win32),\n"
                         "тим вища ціна будь-якої внутрішньої зміни. Система втрачає здатність до еволюції.",
                         size=12.5, bold=True, fill=WARN_T, stroke=LINE, sw=1.5))

    render(os.path.join(IMG, 'hyrums-law-ecosystem-ossification.svg'), W, H, *frags)


# ── 3. Захисна рандомізація: як штучний шум рятує від закостеніння ─────────────
def fig_defensive_randomization_barrier():
    W, H = 1180, 560
    frags = []
    frags.append(text(W / 2, 34, "Захисна рандомізація: штучний шум проти неявного зв'язування",
                      size=17, bold=True))

    col_w = 510
    # Ліва колонка: Детермінована реалізація (Пастка)
    frags.append(fitbox(50, 75, col_w, 45, "ДЕТЕРМІНОВАНА РЕАЛІЗАЦІЯ (Хибна стабільність)",
                         size=13, bold=True, fill=RED_T, stroke=POS, sw=2.0))

    left_steps = [
        (50, 135, col_w, 65, "Порядок ключів у хеш-таблиці завжди однаковий\n(наприклад, залежить лише від порядку вставки)."),
        (50, 215, col_w, 65, "Клієнт пише тест: assert response == ['alpha', 'beta'].\nТест проходить у 100% випадків на CI."),
        (50, 295, col_w, 65, "Автор оновлює хеш-функцію заради швидкості.\nПорядок змінився на ['beta', 'alpha']."),
        (50, 375, col_w, 80, "КАТАСТРОФА В ПРОДАКШЕНІ:\nТести клієнта впали, білд заблоковано,\nавтора звинувачують у ламкому релізі."),
    ]
    for x, y, w, h, t in left_steps:
        frags.append(fitbox(x, y, w, h, t, size=11.5, fill=BG, stroke=POS, sw=1.3))

    # Стрілки ліворуч
    frags.append(arrow(50 + col_w / 2, 200, 50 + col_w / 2, 213, color=POS, sw=1.6))
    frags.append(arrow(50 + col_w / 2, 280, 50 + col_w / 2, 293, color=POS, sw=1.6))
    frags.append(arrow(50 + col_w / 2, 360, 50 + col_w / 2, 373, color=POS, sw=1.6))

    # Права колонка: Рандомізована реалізація (Стійкість)
    frags.append(fitbox(620, 75, col_w, 45, "ЗАХИСНА РАНДОМІЗАЦІЯ (Активна ентропія)",
                         size=13, bold=True, fill=GREEN_T, stroke=FIELD, sw=2.0))

    right_steps = [
        (620, 135, col_w, 65, "Порядок ітерації навмисно тасується щоразу\n(випадковий сід хешування, рандомний старт у Go map)."),
        (620, 215, col_w, 65, "Наївний тест клієнта падає на 2-му запуску локально.\nКлієнт бачить: порядок недетермінований!"),
        (620, 295, col_w, 65, "Клієнт пише стійкий код:\nвикликає sort() або перевіряє невпорядковану множину."),
        (620, 375, col_w, 80, "БЕЗПЕЧНА ЕВОЛЮЦІЯ:\nАвтор оновлює хеш-функцію, архітектуру та кеші.\nЖоден клієнт не зламався, бо контракт дотримано."),
    ]
    for x, y, w, h, t in right_steps:
        frags.append(fitbox(x, y, w, h, t, size=11.5, fill=BG, stroke=FIELD, sw=1.3))

    # Стрілки праворуч
    frags.append(arrow(620 + col_w / 2, 200, 620 + col_w / 2, 213, color=FIELD, sw=1.6))
    frags.append(arrow(620 + col_w / 2, 280, 620 + col_w / 2, 293, color=FIELD, sw=1.6))
    frags.append(arrow(620 + col_w / 2, 360, 620 + col_w / 2, 373, color=FIELD, sw=1.6))

    # Підсумковий висновок
    frags.append(fitbox(120, 475, 940, 65,
                         "Правило проєктування стійких систем:\n"
                         "Якщо поведінка не гарантована специфікацією, зробіть її активно нестабільною.\n"
                         "Штучний шум примушує клієнтів поважати межі контракту з першого дня.",
                         size=12.5, bold=True, fill=BLUE_T, stroke=NEG, sw=1.8))

    render(os.path.join(IMG, 'defensive-randomization-barrier.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_implicit_vs_explicit_contract()
    fig_hyrums_law_ecosystem_ossification()
    fig_defensive_randomization_barrier()
    print("All figures generated successfully.")

# -*- coding: utf-8 -*-
"""Фігури теми «Матеріалізовані в'ю як похідні дані (Materialized Views)». Вивід — ./img/*.svg"""
import sys, os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від теки теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── 1. virtual-vs-materialized-view.svg ─────────────────────────────────────────
# Порівняння виконання запиту через звичайне (віртуальне) та матеріалізоване представлення
def fig_virtual_vs_materialized():
    W, H = 960, 480
    f = []

    f.append(text(240, 50, "Віртуальне представлення (Virtual View)", size=16, bold=True, color=NEG))
    f.append(text(720, 50, "Матеріалізоване представлення (Materialized View)", size=16, bold=True, color=FIELD))

    # Ліва частина: Віртуальне в'ю (виконання на льоту)
    b1, w1, h1 = textbox(240, 110, "Клієнтський SQL-запит\nSELECT * FROM user_summary", size=13, fill="#eaf0fd", stroke=NEG, sw=1.8, pad=10)
    f.append(b1)

    f.append(arrow(240, 140, 240, 180, color=NEG, sw=1.8))
    f.append(text(250, 165, "Розгортання AST / макрос", size=11, color=MUTED, anchor="start"))

    b2, w2, h2 = textbox(240, 230, "Оптимізатор та план виконання\nHash Join (orders ⋈ items)\nФільтрація + GROUP BY", size=12, fill="#fdecea", stroke=NEG, sw=1.8, pad=12)
    f.append(b2)

    f.append(arrow(240, 280, 240, 330, color=NEG, sw=1.8))
    f.append(text(250, 310, "Повне сканування дисків", size=11, color=MUTED, anchor="start"))

    b3, w3, h3 = textbox(240, 380, "Базові таблиці на диску\norders (40M) + items (180M)\nЧас: 8.5 c | I/O: 14 ГБ", size=12, fill="#f4f6f8", stroke=LINE, sw=1.5, pad=12)
    f.append(b3)

    # Розділювач
    f.append(line(480, 40, 480, 440, color=MUTED, sw=1.2, dash="6,5"))

    # Права частина: Матеріалізоване в'ю (пряме читання готового стану)
    b4, w4, h4 = textbox(720, 110, "Клієнтський SQL-запит\nSELECT * FROM mv_user_summary", size=13, fill="#eaf0fd", stroke=FIELD, sw=1.8, pad=10)
    f.append(b4)

    f.append(arrow(720, 140, 720, 230, color=FIELD, sw=2.0))
    f.append(text(730, 185, "Прямий доступ без Join і GroupBy", size=11, color=FIELD, anchor="start", bold=True))

    b5, w5, h5 = textbox(720, 290, "Фізична таблиця на диску (MV)\nПопередньо обчислені агрегати\nIndex Scan / Seq Scan\nЧас: 1.2 мс | I/O: 16 КБ", size=12, fill="#d4edda", stroke=FIELD, sw=2.0, pad=14)
    f.append(b5)

    f.append(line(720, 350, 720, 390, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(720, 410, "Оновлюється окремо (Refresh / IVM)", size=11, color=MUTED, anchor="middle", italic=True))

    render(out("virtual-vs-materialized-view.svg"), W, H, *f,
           title="Віртуальне представлення проти матеріалізованого: динамічне обчислення vs збережений стан")


# ── 2. view-refresh-strategies.svg ─────────────────────────────────────────────
# Три основні моделі оновлення: Повне (Full), Інкрементне (IVM), Потокове (Streaming)
def fig_refresh_strategies():
    W, H = 960, 460
    f = []

    # Колонка 1: Повне оновлення (Full Refresh)
    f.append(text(160, 55, "Повне оновлення (Full Refresh)", size=14, bold=True, color=NEG))
    b1 = fitbox(40, 80, 240, 100, "Базові дані змінюються\n(INSERT / UPDATE / DELETE)\nЗміни накопичуються в базі", size=12, fill="#ffffff", stroke=LINE)
    f.append(b1)
    f.append(arrow(160, 180, 160, 230, color=NEG, sw=1.8))
    f.append(text(160, 205, "TRUNCATE + Повний рекомп'ют", size=10, color=NEG, anchor="middle", bold=True))
    b2 = fitbox(40, 230, 240, 120, "Перерахунок усього запиту\n• Тривале блокування або temp-таблиця\n• Високе навантаження на I/O\n• Періодичний запуск (cron)", size=11, fill="#fdecea", stroke=NEG)
    f.append(b2)
    b3 = fitbox(40, 370, 240, 60, "Затримка: висока (хвилини/години)\nЦіна запису: 0 на транзакцію", size=11, fill="#f4f6f8", stroke=MUTED)
    f.append(b3)

    # Колонка 2: Інкрементне оновлення (IVM)
    f.append(text(480, 55, "Інкрементне оновлення (IVM)", size=14, bold=True, color=FIELD))
    b4 = fitbox(360, 80, 240, 100, "Транзакція мутації генерує дельту\nΔR = (вставлені / видалені рядки)\nФіксація змін у WAL / тригерах", size=12, fill="#ffffff", stroke=LINE)
    f.append(b4)
    f.append(arrow(480, 180, 480, 230, color=FIELD, sw=1.8))
    f.append(text(480, 205, "Диференційні правила ΔV", size=10, color=FIELD, anchor="middle", bold=True))
    b5 = fitbox(360, 230, 240, 120, "Точкове оновлення агрегатів\n• Обробка лише рядків ΔR\n• Лічильники кратності (__count)\n• Синхронно або майже в реальному часі", size=11, fill="#d4edda", stroke=FIELD)
    f.append(b5)
    b6 = fitbox(360, 370, 240, 60, "Затримка: мілісекунди\nЦіна запису: додатковий I/O транзакції", size=11, fill="#f4f6f8", stroke=MUTED)
    f.append(b6)

    # Колонка 3: Неперервне потокове (Streaming)
    f.append(text(800, 55, "Потокове злиття (ClickHouse / Flink)", size=14, bold=True, color="#2457d6"))
    b7 = fitbox(680, 80, 240, 100, "Потік подій / чанків даних\nВставка блоками (Batch Insert)\nCDC / Kafka потік", size=12, fill="#ffffff", stroke=LINE)
    f.append(b7)
    f.append(arrow(800, 180, 800, 230, color="#2457d6", sw=1.8))
    f.append(text(800, 205, "Проміжні стани агрегатів", size=10, color="#2457d6", anchor="middle", bold=True))
    b8 = fitbox(680, 230, 240, 120, "Фонове злиття LSM-дерев\n• SummingMergeTree / Aggregating\n• Неблокувальне фонове згортання\n• Остаточна узгодженість", size=11, fill="#eaf0fd", stroke="#2457d6")
    f.append(b8)
    b9 = fitbox(680, 370, 240, 60, "Затримка: субсекундна\nЦіна запису: мінімальна (асинхронна)", size=11, fill="#f4f6f8", stroke=MUTED)
    f.append(b9)

    render(out("view-refresh-strategies.svg"), W, H, *f,
           title="Стратегії оновлення матеріалізованих даних: компроміс свіжості та обчислювальних витрат")


# ── 3. ivm-delta-propagation.svg ───────────────────────────────────────────────
# Конвеєр поширення дельт: Мутація -> Екстракція дельти -> Диференційні оператори -> Оновлення MV
def fig_ivm_delta_propagation():
    W, H = 960, 480
    f = []

    # Крок 1: Базова мутація
    b1, w1, h1 = textbox(140, 120, "Базова таблиця R\nINSERT INTO orders\nVALUES (101, 45.00)", size=12, fill="#ffffff", stroke=LINE, sw=1.5, pad=10)
    f.append(b1)

    f.append(arrow(240, 120, 330, 120, color=FIELD, sw=1.8))
    f.append(text(285, 105, "Мутація", size=11, color=MUTED, anchor="middle"))

    # Крок 2: Дельта-потік
    b2, w2, h2 = textbox(440, 120, "Дельта-потік ΔR\n+ {id: 101, amount: 45.00}\nЗнак: INSERT (+), DELETE (-)", size=12, fill="#eaf0fd", stroke=NEG, sw=1.8, pad=12)
    f.append(b2)

    f.append(arrow(440, 175, 440, 240, color=FIELD, sw=1.8))
    f.append(text(450, 210, "Диференційне обчислення", size=11, color=FIELD, anchor="start", bold=True))

    # Крок 3: Диференційні оператори
    b3 = fitbox(160, 250, 560, 120, "Алгебраїчні дельта-правила:\n• Фільтрація: Δ(σ_p(R)) = σ_p(ΔR)\n• З'єднання: Δ(R ⋈ S) = (ΔR ⋈ S_new) ∪ (R_old ⋈ ΔS)\n• Агрегація: SUM_new = SUM_old + Δamount, COUNT_new = COUNT_old + 1", size=12, fill="#fdecea", stroke=NEG, sw=1.5)
    f.append(b3)

    f.append(arrow(440, 370, 440, 410, color=FIELD, sw=1.8))

    # Крок 4: Фіксація в матеріалізованому стані
    b4, w4, h4 = textbox(440, 435, "Оновлений стан матеріалізованого в'ю (MV)\nКлюч знайдено: UPDATE row SET sum += 45.00, count += 1\nКлюч відсутній: INSERT INTO mv VALUES (key, 45.00, 1)", size=12, fill="#d4edda", stroke=FIELD, sw=2.0, pad=10)
    f.append(b4)

    # Боковий блок: лічильник кратності
    b5 = fitbox(760, 180, 170, 190, "Важливість __count:\n\nПри видаленні кортежу\nлічильник зменшується.\n\nКоли __count = 0,\nрядок видаляється з MV.\n\nЗапобігає фантомним\nнульовим групам!", size=10, fill="#f4f6f8", stroke=MUTED)
    f.append(b5)
    f.append(line(720, 310, 760, 310, color=MUTED, sw=1.2, dash="4,4"))

    render(out("ivm-delta-propagation.svg"), W, H, *f,
           title="Конвеєр інкрементного поширення змін (IVM Delta Pipeline)")


# ── 4. query-rewrite-mechanism.svg ─────────────────────────────────────────────
# Як оптимізатор переписує запит клієнта з базових таблиць на матеріалізоване в'ю
def fig_query_rewrite():
    W, H = 960, 460
    f = []

    # Клієнтський запит
    b1, w1, h1 = textbox(480, 60, "Вхідний SQL-запит клієнта до базових таблиць:\nSELECT category, SUM(total) FROM orders JOIN items ON ... WHERE date >= '2026-01-01' GROUP BY category", size=12, fill="#eaf0fd", stroke=LINE, sw=1.5, pad=12)
    f.append(b1)

    f.append(arrow(480, 105, 480, 160, color=LINE, sw=1.8))
    f.append(text(490, 135, "Аналіз оптимізатора (Query Optimizer)", size=11, color=MUTED, anchor="start"))

    # Блок перевірки відповідності (Matching / Subsumption)
    b2 = fitbox(200, 165, 560, 110, "Перевірка покриття представленням (View Containment & Matching):\n1. Чи містить MV потрібні таблиці та з'єднання (orders ⋈ items)? → Так\n2. Чи є необхідні стовпці (category, total) у схемі MV? → Так\n3. Чи покриває предикат MV фільтр запиту (date >= '2026-01-01')? → Так (або потрібен компенсаційний фільтр)", size=11, fill="#fdecea", stroke=NEG, sw=1.5)
    f.append(b2)

    # Дві гілки
    f.append(arrow(340, 275, 240, 330, color=NEG, sw=1.8))
    f.append(text(250, 295, "Збіг відсутній", size=11, color=NEG, anchor="end"))

    b3 = fitbox(80, 330, 320, 100, "Стандартний план (Base Plan)\n• Сканування orders (40M)\n• Сканування items (180M)\n• Hash Join + Group By на льоту\nВартість: Cost = 854 200", size=11, fill="#ffffff", stroke=NEG)
    f.append(b3)

    f.append(arrow(620, 275, 720, 330, color=FIELD, sw=2.0))
    f.append(text(710, 295, "Збіг знайдено! (Rewrite)", size=11, color=FIELD, anchor="start", bold=True))

    b4 = fitbox(560, 330, 340, 100, "Переписаний план (Rewritten Plan)\n• Запит замінюється на: SELECT * FROM mv_sales_by_cat\n• Точковий індексний скан\n• Нуль з'єднань на льоту\nВартість: Cost = 12.4 (прискорення ×68 000)", size=11, fill="#d4edda", stroke=FIELD, sw=2.0)
    f.append(b4)

    render(out("query-rewrite-mechanism.svg"), W, H, *f,
           title="Механізм автоматичного переписування запитів (Query Rewrite & View Matching)")


if __name__ == "__main__":
    fig_virtual_vs_materialized()
    fig_refresh_strategies()
    fig_ivm_delta_propagation()
    fig_query_rewrite()
    print("Усі 4 фігури успішно згенеровано у ./img/")

# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1: Пошукова підсистема як вторинна проєкція ───────────────────────
def fig_search_as_second_truth():
    W, H = 880, 390
    frags = []
    frags.append(text(W / 2, 28, "Пошукова підсистема як вторинна похідна проєкція", size=16, bold=True))
    frags.append(text(W / 2, 50, "первинна база гарантує транзакційний стан, а пошуковий індекс оптимізує читання",
                      size=12, color=MUTED, italic=True))

    # Клієнтські запити ліворуч (запис) і праворуч (пошук)
    b_write, _, _ = textbox(110, 110, ["Запис / Мутація", "POST /products", "PUT /orders/42"],
                            size=11, fill=BG, stroke=POS, sw=1.6, color=POS, bold=True)
    frags.append(b_write)

    b_read, _, _ = textbox(770, 110, ["Пошук / Фасети", "GET /search?q=sony", "sort=relevance"],
                           size=11, fill=BG, stroke=NEG, sw=1.6, color=NEG, bold=True)
    frags.append(b_read)

    # Первинна база (System of Record)
    frags.append(rect(40, 180, 240, 170, fill="#fdfefe", stroke=INK, sw=1.8))
    frags.append(text(160, 204, "Первинна база (OLTP)", size=13, bold=True))
    frags.append(text(160, 222, "PostgreSQL / MySQL", size=11, color=MUTED))
    frags.append(line(50, 232, 270, 232, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(fitbox(52, 240, 216, 28, "• ACID і суворі обмеження", size=10, fill=FILL, stroke=MUTED, sw=1.1))
    frags.append(fitbox(52, 274, 216, 28, "• Журнал WAL і точкові B-Tree", size=10, fill=FILL, stroke=MUTED, sw=1.1))
    frags.append(fitbox(52, 308, 216, 28, "• Єдине джерело правди", size=10, fill="#eafaf1", stroke=FIELD, sw=1.2, color=FIELD, bold=True))

    # Стрілка від запису до БД
    frags.append(arrow(110, 142, 110, 176, color=POS, sw=1.8))

    # Конвеєр синхронізації (посередині)
    frags.append(rect(320, 180, 240, 170, fill="#f9f9fb", stroke=FIELD, sw=1.8))
    frags.append(text(440, 204, "Конвеєр синхронізації", size=13, bold=True, color=FIELD))
    frags.append(text(440, 222, "Transactional Outbox / CDC", size=11, color=MUTED))
    frags.append(line(330, 232, 550, 232, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(fitbox(332, 240, 216, 28, "• Атомарний запис події в БД", size=10, fill=FILL, stroke=MUTED, sw=1.1))
    frags.append(fitbox(332, 274, 216, 28, "• Черга: Kafka / RabbitMQ", size=10, fill=FILL, stroke=MUTED, sw=1.1))
    frags.append(fitbox(332, 308, 216, 28, "• Монотонні версії (OCC)", size=10, fill=FILL, stroke=MUTED, sw=1.1))

    # Стрілка БД -> Конвеєр
    frags.append(arrow(280, 265, 316, 265, color=FIELD, sw=1.8))
    frags.append(text(300, 255, "події", size=9, color=FIELD, bold=True))

    # Пошуковий рушій (праворуч)
    frags.append(rect(600, 180, 240, 170, fill="#fdfefe", stroke=NEG, sw=1.8))
    frags.append(text(720, 204, "Пошуковий рушій", size=13, bold=True, color=NEG))
    frags.append(text(720, 222, "OpenSearch / Elasticsearch", size=11, color=MUTED))
    frags.append(line(610, 232, 830, 232, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(fitbox(612, 240, 216, 28, "• Інвертований індекс і BM25", size=10, fill=FILL, stroke=MUTED, sw=1.1))
    frags.append(fitbox(612, 274, 216, 28, "• Стовпчикові Doc Values", size=10, fill=FILL, stroke=MUTED, sw=1.1))
    frags.append(fitbox(612, 308, 216, 28, "• Похідна денормалізована проєкція", size=9, fill="#eaf0fd", stroke=NEG, sw=1.2, color=NEG, bold=True))

    # Стрілка Конвеєр -> Пошуковий рушій
    frags.append(arrow(560, 265, 596, 265, color=FIELD, sw=1.8))
    frags.append(text(580, 255, "індекс", size=9, color=FIELD, bold=True))

    # Стрілка Клієнт читання -> Пошуковий рушій
    frags.append(arrow(770, 142, 770, 176, color=NEG, sw=1.8))

    render(os.path.join(IMG, "search-as-second-truth.svg"), W, H, *frags)


# ── Фігура 2: Аварії наївного подвійного запису ──────────────────────────────
def fig_dual_write_race():
    W, H = 880, 440
    frags = []
    frags.append(text(W / 2, 28, "Аварії наївного подвійного запису: часткова відмова й перестановка", size=16, bold=True))
    frags.append(text(W / 2, 50, "прямий подвійний запис у коді бекенда веде до перманентної неузгодженості",
                      size=12, color=MUTED, italic=True))

    # Панель 1: Часткова відмова
    frags.append(rect(40, 75, 385, 345, fill=BG, stroke=POS, sw=1.8))
    frags.append(text(232, 102, "1. Часткова відмова або відкат", size=13, bold=True, color=POS))

    frags.append(fitbox(56, 122, 353, 40, "① db.Save(item)  →  COMMIT у базі успішний", size=11, fill=FILL, stroke=MUTED, sw=1.2))
    frags.append(fitbox(56, 170, 353, 40, "② search.Index(item)  →  таймаут / крах мережі", size=11, fill="#fdecea", stroke=POS, sw=1.5, color=POS, bold=True))
    frags.append(fitbox(56, 218, 353, 40, "③ Клієнт отримав HTTP 500 або помилку", size=11, fill=FILL, stroke=MUTED, sw=1.2))

    frags.append(fitbox(56, 275, 353, 62, "У первинній базі: запис збережено ✓\nУ пошуковому індексі: старі дані або порожнеча ✗",
                        size=11, fill="#fff5f5", stroke=POS, sw=1.6, color=POS, bold=True))
    frags.append(fitbox(56, 352, 353, 52, "Наслідок: перманентний розсинхрон даних,\nпошук не знаходить існуючий товар",
                        size=10, fill=FILL, stroke=MUTED, sw=1.1, italic=True))

    # Панель 2: Перегони та перестановка порядку (Out-of-order)
    frags.append(rect(455, 75, 385, 345, fill=BG, stroke=POS, sw=1.8))
    frags.append(text(647, 102, "2. Перестановка порядку (Out-of-Order)", size=13, bold=True, color=POS))

    frags.append(fitbox(471, 122, 353, 40, "t1: Потік A: update(Чернетка) → затримка мережі", size=11, fill=FILL, stroke=MUTED, sw=1.2))
    frags.append(fitbox(471, 170, 353, 40, "t2: Потік B: update(Опубліковано) → Search.Index()", size=11, fill=FILL, stroke=MUTED, sw=1.2))
    frags.append(fitbox(471, 218, 353, 40, "t3: Потік A нарешті добіг: Search.Index(Чернетка)", size=11, fill="#fdecea", stroke=POS, sw=1.5, color=POS, bold=True))

    frags.append(fitbox(471, 275, 353, 62, "У первинній базі: Опубліковано (останній стан)\nУ пошуковому індексі: Чернетка (перезапис старим)",
                        size=11, fill="#fff5f5", stroke=POS, sw=1.6, color=POS, bold=True))
    frags.append(fitbox(471, 352, 353, 52, "Наслідок: опублікований товар сховано з каталогу,\nхоча в базі він активний",
                        size=10, fill=FILL, stroke=MUTED, sw=1.1, italic=True))

    render(os.path.join(IMG, "dual-write-race.svg"), W, H, *frags)


# ── Фігура 3: Анатомія пошукового вузла ──────────────────────────────────────
def fig_inverted_index_anatomy():
    W, H = 880, 440
    frags = []
    frags.append(text(W / 2, 26, "Анатомія пошукового вузла: аналізатори, індекс та doc values", size=16, bold=True))
    frags.append(text(W / 2, 46, "текст розкладається на терми для відповідності, а скаляри — у стовпці для фасетів",
                      size=12, color=MUTED, italic=True))

    # Вхідний документ
    frags.append(fitbox(60, 68, 760, 36, "Вхідний документ doc#12:  {\"title\": \"Sony бездротові навушники\", \"price\": 4500, \"category\": \"audio\"}",
                        size=11, fill="#f0f4f8", stroke=INK, sw=1.5, bold=True))

    # Конвеєр текстового аналізу (ліворуч зверху)
    frags.append(rect(60, 120, 760, 72, fill=BG, stroke=FIELD, sw=1.6))
    frags.append(text(440, 138, "Конвеєр текстового аналізу (Text Analyzer Pipeline)", size=12, bold=True, color=FIELD))

    # 3 кроки аналізатора
    frags.append(fitbox(80, 150, 200, 32, "1. Фільтр символів\n(HTML, лапки)", size=10, fill=FILL, stroke=MUTED, sw=1.1))
    frags.append(arrow(285, 166, 325, 166, color=FIELD, sw=1.5))
    frags.append(fitbox(330, 150, 200, 32, "2. Токенізатор\n(розбиття за пробілами)", size=10, fill=FILL, stroke=MUTED, sw=1.1))
    frags.append(arrow(535, 166, 575, 166, color=FIELD, sw=1.5))
    frags.append(fitbox(580, 150, 220, 32, "3. Фільтри токенів\n(lowercase, стемінг: навушник)", size=10, fill=FILL, stroke=MUTED, sw=1.1))

    # Стрілка від конвеєра до структур збереження
    frags.append(arrow(260, 196, 260, 222, color=INK, sw=1.6))
    frags.append(arrow(620, 196, 620, 222, color=INK, sw=1.6))

    # Ліва колонка: Інвертований індекс (Posting Lists)
    frags.append(rect(60, 226, 365, 195, fill=BG, stroke=NEG, sw=1.8))
    frags.append(text(242, 248, "Інвертований індекс (Inverted Index)", size=12, bold=True, color=NEG))
    frags.append(text(242, 265, "для повнотекстового пошуку та BM25", size=10, color=MUTED))
    frags.append(line(75, 273, 410, 273, color=MUTED, sw=1.0, dash="3,3"))

    frags.append(fitbox(75, 281, 335, 30, "«bezdrotov»  →  [doc#12, doc#45]", size=10, fill=FILL, stroke=MUTED, sw=1.1))
    frags.append(fitbox(75, 317, 335, 30, "«navushnyk»  →  [doc#12, doc#88, doc#104]", size=10, fill=FILL, stroke=MUTED, sw=1.1))
    frags.append(fitbox(75, 353, 335, 30, "«sony»       →  [doc#12, doc#19, doc#301]", size=10, fill=FILL, stroke=MUTED, sw=1.1))
    frags.append(text(242, 404, "Швидкий перетин множин і розрахунок TF-IDF/BM25", size=9, color=NEG, italic=True))

    # Права колонка: Стовпчикові Doc Values
    frags.append(rect(455, 226, 365, 195, fill=BG, stroke=FIELD, sw=1.8))
    frags.append(text(637, 248, "Стовпчикові значення (Doc Values)", size=12, bold=True, color=FIELD))
    frags.append(text(637, 265, "для фільтрації, сортування та фасетів", size=10, color=MUTED))
    frags.append(line(470, 273, 805, 273, color=MUTED, sw=1.0, dash="3,3"))

    frags.append(fitbox(470, 281, 335, 30, "price:      [doc#12: 4500, doc#45: 3200]", size=10, fill=FILL, stroke=MUTED, sw=1.1))
    frags.append(fitbox(470, 317, 335, 30, "category:   [doc#12: audio, doc#45: audio]", size=10, fill=FILL, stroke=MUTED, sw=1.1))
    frags.append(fitbox(470, 353, 335, 30, "in_stock:   [doc#12: true, doc#45: false]", size=10, fill=FILL, stroke=MUTED, sw=1.1))
    frags.append(text(637, 404, "Стовпчиковий доступ без розпакування всього JSON", size=9, color=FIELD, italic=True))

    render(os.path.join(IMG, "inverted-index-anatomy.svg"), W, H, *frags)


# ── Фігура 4: Жива переіндексація через псевдоніми індексів ─────────────────
def fig_zero_downtime_reindex():
    W, H = 880, 420
    frags = []
    frags.append(text(W / 2, 26, "Жива переіндексація без простою через псевдоніми (Aliases)", size=16, bold=True))
    frags.append(text(W / 2, 46, "клієнт завжди звертається до псевдоніма, поки новий індекс наповнюється у фоні",
                      size=12, color=MUTED, italic=True))

    # Схема 4 кроків
    steps = [
        (40, "1. Створення v2", ["Створення products_v2", "з новою схемою й", "новими аналізаторами"], MUTED, FILL),
        (245, "2. Бекфіл з БД", ["Вивантаження історії", "з первинної БД батчами", "в products_v2"], FIELD, "#eafaf1"),
        (450, "3. Доганяння CDC", ["Вичитування черги змін,", "що накопичилися за час", "бекфілу (лаг → 0)"], FIELD, "#eafaf1"),
        (655, "4. Атомарний світч", ["POST /_aliases", "remove: products_v1", "add: products_v2"], POS, "#fdecea"),
    ]

    for sx, title, lines_s, col, bg_col in steps:
        frags.append(rect(sx, 75, 185, 140, fill=bg_col, stroke=col, sw=1.7))
        frags.append(text(sx + 92, 100, title, size=12, bold=True, color=col))
        frags.append(line(sx + 15, 110, sx + 170, 110, color=col, sw=1.0, dash="2,2"))
        ly = 130
        for ln in lines_s:
            frags.append(text(sx + 92, ly, ln, size=10, color=INK))
            ly += 18

    frags.append(arrow(228, 145, 242, 145, color=FIELD, sw=1.8))
    frags.append(arrow(433, 145, 447, 145, color=FIELD, sw=1.8))
    frags.append(arrow(638, 145, 652, 145, color=FIELD, sw=1.8))

    # Нижня частина: стан псевдоніма До та Після
    frags.append(rect(40, 240, 385, 155, fill=BG, stroke=MUTED, sw=1.6))
    frags.append(text(232, 265, "До перемикання (Фаза 1–3)", size=12, bold=True, color=MUTED))
    frags.append(fitbox(60, 280, 345, 34, "Псевдонім: products_live  →  products_v1", size=11, fill="#f0f4f8", stroke=INK, sw=1.3, bold=True))
    frags.append(fitbox(60, 324, 345, 52, "• Пошуковий трафік обслуговує v1\n• У v2 у фоні йде наповнення та доганяння черги", size=10, fill=FILL, stroke=MUTED, sw=1.1))

    frags.append(rect(455, 240, 385, 155, fill=BG, stroke=FIELD, sw=1.8))
    frags.append(text(647, 265, "Після перемикання (Фаза 4–5)", size=12, bold=True, color=FIELD))
    frags.append(fitbox(475, 280, 345, 34, "Псевдонім: products_live  →  products_v2", size=11, fill="#eafaf1", stroke=FIELD, sw=1.5, color=FIELD, bold=True))
    frags.append(fitbox(475, 324, 345, 52, "• Пошуковий трафік миттєво переходить на v2\n• Старий v1 переводиться в read-only і видаляється", size=10, fill=FILL, stroke=MUTED, sw=1.1))

    render(os.path.join(IMG, "zero-downtime-reindex.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_search_as_second_truth()
    fig_dual_write_race()
    fig_inverted_index_anatomy()
    fig_zero_downtime_reindex()
    print("All figures generated successfully.")

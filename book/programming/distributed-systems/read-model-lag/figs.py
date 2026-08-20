# -*- coding: utf-8 -*-
"""Фігури до теми «Лаг read-model як контракт»."""
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"    # застарілий стан / аномалія / лаг
COOL = "#eaf0fd"    # нейтральні блоки / сервіси
GOOD = "#e8f6ee"    # актуальний стан / свіжі дані
WARN_BG = "#fff9db" # очікування / перевірка умови
PANEL = "#f8f9fa"   # фонова панель


# ── 1. Конвеєр CQRS та виникнення вікна лагу ────────────────────────────────
def fig_read_model_cqrs_pipeline():
    W, H = 1080, 560
    f = []

    # Заголовок
    f.append(text(W / 2, 30, "Конвеєр проєкцій у CQRS та утворення часового вікна лагу", size=16, bold=True))

    # Панель 1: Command Side (Запис)
    f.append(rect(30, 60, 310, 460, fill=COOL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(185, 86, "КОМАНДНИЙ КОНТУР (WRITE SIDE)", size=13, color=NEG, bold=True))

    f.append(fitbox(50, 110, 270, 64, "Клієнтський запит на запис\nPOST /orders (створення замовлення)", size=12, bold=True, fill=BG))
    f.append(arrow(185, 174, 185, 204, color=LINE, sw=1.8))

    f.append(fitbox(50, 204, 270, 76, "Командний обробник (Command API)\nВалідація бізнес-правил\nГенерація події OrderCreated", size=11, fill=BG))
    f.append(arrow(185, 280, 185, 310, color=LINE, sw=1.8))

    f.append(fitbox(50, 310, 270, 90, "Транзакційне сховище (Write DB)\nТаблиця агрегатів (State)\nТаблиця Outbox (Події)\nФіксація TX: v_write = 1042", size=11, bold=True, fill=GOOD, stroke=FIELD))
    f.append(arrow(185, 400, 185, 434, color=LINE, sw=1.8))

    f.append(fitbox(50, 434, 270, 64, "Відповідь клієнту: 200 OK\nВерсійний токен: v = 1042", size=12, bold=True, fill=BG))

    # Стрілка передачі до брокера
    f.append(arrow(320, 355, 380, 355, color=POS, sw=2.2))
    f.append(text(350, 345, "CDC / Poller", size=10, color=POS, bold=True))

    # Панель 2: Асинхронна магістраль (Event Broker)
    f.append(rect(380, 60, 310, 460, fill=WARN_BG, stroke=LINE, sw=1.2, rx=8))
    f.append(text(535, 86, "ПОТОКОВА МАГІСТРАЛЬ (KAFKA)", size=13, color=INK, bold=True))

    f.append(fitbox(400, 120, 270, 70, "Журнал подій (Partition Log)\nЧерга незмінних записів\nOffset 1040 | 1041 | 1042", size=11, bold=True, fill=BG))

    # Блок затримок
    f.append(rect(400, 210, 270, 170, fill="#ffffff", stroke="#d97706", sw=1.5, rx=6))
    f.append(text(535, 232, "Складові фізичного лагу (Δt):", size=11, color="#d97706", bold=True))
    f.append(text(415, 258, "1. Буферизація та пакування (linger.ms)", size=10, color=INK, anchor="start"))
    f.append(text(415, 282, "2. Мережева затримка до споживача", size=10, color=INK, anchor="start"))
    f.append(text(415, 306, "3. Пакетне вичитування (batch fetch)", size=10, color=INK, anchor="start"))
    f.append(text(415, 330, "4. Десеріалізація та трансформація", size=10, color=INK, anchor="start"))
    f.append(text(415, 354, "5. Оновлення B-дерев / пошукових індексів", size=10, color=INK, anchor="start"))

    f.append(arrow(535, 380, 535, 410, color=LINE, sw=1.8))
    f.append(fitbox(400, 410, 270, 88, "Поточний стан проєктора:\nОброблено до offset = 1040\nЛаг зміщення: Δv = 2 події\nЧасовий лаг: Δt = 340 мс", size=11, bold=True, fill=WARM, stroke=POS))

    # Стрілка передачі до Read Side
    f.append(arrow(670, 454, 730, 454, color=FIELD, sw=2.2))
    f.append(text(700, 442, "Apply", size=11, color=FIELD, bold=True))

    # Панель 3: Query Side (Read Model)
    f.append(rect(730, 60, 320, 460, fill=COOL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(890, 86, "КОНТУР ЧИТАННЯ (READ MODEL)", size=13, color=NEG, bold=True))

    f.append(fitbox(750, 110, 280, 76, "Матеріалізоване представлення\nPostgreSQL View / Elasticsearch\nПоточна версія: v_read = 1040\n(СТАН ЗАСТАРІЛИЙ НА 340 мс)", size=11, bold=True, fill=WARM, stroke=POS))
    f.append(arrow(890, 230, 890, 186, color=LINE, sw=1.8))

    f.append(fitbox(750, 230, 280, 70, "Шлюз читання (Query API)\nGET /orders/ORD-5542\nОтримання запиту від клієнта", size=11, fill=BG))

    # Аномалія
    f.append(rect(750, 320, 280, 178, fill=WARM, stroke=POS, sw=1.5, rx=6))
    f.append(text(890, 344, "Аномалії без контракту:", size=11, color=POS, bold=True))
    f.append(text(762, 370, "• 404 Not Found (замовлення «зникло»)", size=10, color=INK, anchor="start"))
    f.append(text(762, 396, "• Читання старого балансу рахунку", size=10, color=INK, anchor="start"))
    f.append(text(762, 422, "• Повторний клік і дублювання оплати", size=10, color=INK, anchor="start"))
    f.append(text(762, 448, "• Порушення монотонності читань", size=10, color=INK, anchor="start"))
    f.append(text(762, 474, "• Стрибки часу назад при F5", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "read-model-cqrs-pipeline.svg"), W, H, *f)


# ── 2. Виконання контракту причинної узгодженості (Read-Your-Writes) ─────────
def fig_lag_contract_causal_token():
    W, H = 1040, 580
    f = []

    f.append(text(W / 2, 30, "Виконання контракту Read-Your-Own-Writes через версійний токен", size=16, bold=True))

    # Стовпці акторів
    actors = [
        (100, "Клієнт (UI/App)"),
        (370, "Command API"),
        (640, "Query Gateway"),
        (910, "Read Projector")
    ]

    # Вертикальні лінії життя
    for x, name in actors:
        f.append(textbox(x, 70, name, size=12, bold=True, fill=COOL, pad=10)[0])
        f.append(line(x, 96, x, 540, color=LINE, sw=1.2, dash="4,4"))

    # Подія 1: Запис
    y1 = 130
    f.append(arrow(100, y1, 370, y1, color=LINE, sw=1.8))
    f.append(text(235, y1 - 10, "1. POST /order/create", size=11, bold=True))

    y2 = 170
    f.append(fitbox(270, y2 - 16, 200, 32, "Фіксація в DB: v = 1042", size=10, fill=GOOD, stroke=FIELD))

    y3 = 210
    f.append(arrow(370, y3, 100, y3, color=FIELD, sw=1.8))
    f.append(text(235, y3 - 10, "2. 200 OK + Token: v=1042", size=11, color=FIELD, bold=True))

    # Подія 2: Асинхронний запис у чергу
    f.append(line(370, 180, 890, 238, color=MUTED, sw=1.5, dash="5,3"))
    f.append(arrow(890, 238, 910, 242, color=MUTED, sw=1.5))
    f.append(text(640, 200, "Подія в Kafka (offset=1042)", size=10, color=MUTED))

    # Подія 3: Негайне читання від клієнта
    y4 = 270
    f.append(arrow(100, y4, 640, y4, color=POS, sw=1.8))
    f.append(text(370, y4 - 10, "3. GET /order (X-Required-Version: 1042)", size=11, color=POS, bold=True))

    # Подія 4: Перевірка ватерлінії
    y5 = 320
    f.append(fitbox(520, y5 - 22, 240, 44, "Перевірка водяного знака:\nwatermark (1040) < v_req (1042)", size=10, fill=WARM, stroke=POS))

    # Подія 5: Очікування на Condition Variable
    y6 = 380
    f.append(fitbox(520, y6 - 18, 240, 36, "Блокування / Await (бюджет 50 мс)", size=10, bold=True, fill=WARN_BG, stroke="#d97706"))

    # Подія 6: Проєктор доганяє чергу
    y7 = 420
    f.append(fitbox(800, y7 - 20, 220, 40, "Застосування події 1042\nОновлення watermark = 1042", size=10, fill=GOOD, stroke=FIELD))
    f.append(arrow(910, 440, 640, 460, color=FIELD, sw=1.8))
    f.append(text(775, 445, "signal(watermark_reached)", size=10, color=FIELD, bold=True))

    # Подія 7: Пробудження та повернення відповіді
    y8 = 490
    f.append(arrow(640, y8, 100, y8, color=FIELD, sw=2.0))
    f.append(text(370, y8 - 10, "4. 200 OK + Свіжі дані (X-Lag-Ms: 14ms)", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "lag-contract-causal-token.svg"), W, H, *f)


# ── 3. Вимірювання лагу: Offset vs Синтетичний Heartbeat ────────────────────
def fig_watermark_heartbeat_lag():
    W, H = 1060, 520
    f = []

    f.append(text(W / 2, 30, "Вимірювання лагу: хибність зміщення (offset) проти маркерного пульсу", size=16, bold=True))

    # Блок 1: Оманливе зміщення (Offset Lag)
    f.append(rect(30, 60, 480, 430, fill=PANEL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(270, 88, "СИТУАЦІЯ А: Оманливість метрики Offset Lag", size=12, color=POS, bold=True))

    f.append(fitbox(50, 110, 440, 80, "Сценарій 1: Потік телеметрії (10 000 подій/с)\nProducer Offset: 5 000 000 | Consumer Offset: 4 990 000\nМетрика: Offset Lag = 10 000 повідомлень\nРЕАЛЬНІСТЬ: Дані відстають лише на 10-20 мілісекунд (НОРМА)", size=11, fill=BG))

    f.append(fitbox(50, 205, 440, 84, "Сценарій 2: Неактивний орендар / Нічний час (0.01 подій/с)\nProducer Offset: 500 | Consumer Offset: 499\nМетрика: Offset Lag = 1 повідомлення\nРЕАЛЬНІСТЬ: Подія зависла 4 години тому через збій (КРИЗА)", size=11, fill=WARM, stroke=POS))

    f.append(rect(50, 305, 440, 165, fill=BG, stroke=POS, sw=1.2, rx=6))
    f.append(text(270, 330, "Чому метрика offset lag не є контрактом:", size=11, color=POS, bold=True))
    f.append(text(65, 358, "1. Зміщення не має фізичної розмірності часу (секунд)", size=10, color=INK, anchor="start"))
    f.append(text(65, 384, "2. Залежить від миттєвої інтенсивності бізнес-трафіку", size=10, color=INK, anchor="start"))
    f.append(text(65, 410, "3. Не дає змоги перевірити SLA користувача (напр. ≤ 500 мс)", size=10, color=INK, anchor="start"))
    f.append(text(65, 436, "4. Приховує зависання на поодиноких рідкісних подіях", size=10, color=INK, anchor="start"))

    # Блок 2: Синтетичний пульс (Heartbeat Watermark)
    f.append(rect(550, 60, 480, 430, fill=PANEL, stroke=LINE, sw=1.2, rx=8))
    f.append(text(790, 88, "СИТУАЦІЯ Б: Синтетичний пульс (Heartbeat / Watermark)", size=12, color=FIELD, bold=True))

    f.append(fitbox(570, 110, 440, 70, "Генератор пульсу (Heartbeat Injector)\nКожні 100 мс інжектує службову подію в Outbox:\nHeartbeatEvent { timestamp: t_mono_now }", size=11, fill=GOOD, stroke=FIELD))

    f.append(arrow(790, 180, 790, 210, color=FIELD, sw=1.8))

    f.append(fitbox(570, 210, 440, 70, "Проходження крізь чергу Kafka\nСлужбовий пульс рухається в тому ж порядку,\nщо й бізнес-транзакції у відповідній партиції", size=11, fill=BG))

    f.append(arrow(790, 280, 790, 310, color=FIELD, sw=1.8))

    f.append(fitbox(570, 310, 440, 80, "Обчислення лагу на Проєкторі:\nПри читанні пульсу H(t_sent):\nФізичний лаг = t_mono_local - t_sent\nМетрика завжди актуальна, навіть без бізнес-записів!", size=11, bold=True, fill=GOOD, stroke=FIELD))

    f.append(rect(570, 405, 440, 65, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    f.append(text(790, 428, "Гарантія для SLA-контракту:", size=11, color=FIELD, bold=True))
    f.append(text(790, 452, "Лаг вимірюється в мілісекундах незалежно від навантаження", size=10, color=INK))

    render(os.path.join(OUT, "watermark-heartbeat-lag.svg"), W, H, *f)


if __name__ == "__main__":
    fig_read_model_cqrs_pipeline()
    fig_lag_contract_causal_token()
    fig_watermark_heartbeat_lag()
    print("Усі 3 фігури успішно згенеровано у папку img/")

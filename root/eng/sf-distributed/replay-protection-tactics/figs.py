# -*- coding: utf-8 -*-
"""Фігури до теми «Захист від переграних повідомлень як тактика»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / збій / перегравання / атака
COOL = "#eaf0fd"   # протокол / інформація / заголовки
GOOD = "#e8f6ee"   # успіх / валідація / захист
ACCENT = "#fff8e1" # проміжний стан / перевірка


# ── 1. Таксономія перегравання: випадкове vs зловмисне ───────────────────────
def fig_replay_vector_taxonomy():
    W, H = 1200, 680
    f = []

    f.append(fitbox(40, 20, 1120, 46,
                    "ТАКСОНОМІЯ ПЕРЕГРАВАННЯ: випадкові системні дублі проти зловмисних атак повторення",
                    size=14, bold=True, fill=COOL))

    col_w = 540.0
    y_top = 80.0

    # Ліва колонка: Випадкове системне перегравання
    f.append(fitbox(45, y_top, col_w, 42,
                    "ВИПАДКОВЕ ПЕРЕГРАВАННЯ (Infrastructure & Network Flaws)",
                    size=12.5, bold=True, fill=ACCENT, stroke=LINE, sw=1.8))

    f.append(fitbox(45, y_top + 50, col_w, 95,
                    "ДЖЕРЕЛА:\n"
                    "• Мережеві таймаути клієнта (RPC / HTTP) та агресивні повторні спроби (Retries).\n"
                    "• Семантика at-least-once у чергах повідомлень (RabbitMQ, Kafka) при падінні воркера.\n"
                    "• Ребалансування споживачів та повторна вичитка з останнього збереженого зсуву.\n"
                    "• Збій мережевого обладнання або дублювання пакетів на рівні маршрутизації.",
                    size=11, fill="#ffffff", stroke=LINE, sw=1.2))

    f.append(fitbox(45, y_top + 155, col_w, 85,
                    "ХАРАКТЕРИСТИКА ЗАГРОЗИ:\n"
                    "• Повідомлення повністю легітимне та підписане дійсним клієнтом.\n"
                    "• Тіло та заголовки ідентичні оригіналу; надходить без злого умислу.\n"
                    "• Небезпека: подвійне списання балансу, повторний запис у БД, вичерпання ресурсів.",
                    size=11, fill="#ffffff", stroke=LINE, sw=1.2))

    f.append(fitbox(45, y_top + 250, col_w, 95,
                    "ГОЛОВНІ ТАКТИКИ ЗАХИСТУ:\n"
                    "1. Ключі ідемпотентності (Idempotency-Key) у заголовках запиту.\n"
                    "2. Транзакційна таблиця вхідних повідомлень (Inbox Pattern) у БД.\n"
                    "3. Монотонні перевірки станів (Optimistic Locking / FSM Guards).\n"
                    "4. Ковзне вікно дедуплікації на брокері або шлюзі.",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    # Права колонка: Зловмисне перегравання
    f.append(fitbox(615, y_top, col_w, 42,
                    "ЗЛОВМИСНЕ ПЕРЕГРАВАННЯ (Adversarial Replay Attack)",
                    size=12.5, bold=True, fill=WARM, stroke=POS, sw=1.8))

    f.append(fitbox(615, y_top + 50, col_w, 95,
                    "ДЖЕРЕЛА:\n"
                    "• Перехоплення підписаного криптографічного пакета в незахищеному каналі (MitM).\n"
                    "• Повторне надсилання автентифікаційного токена, квитка Kerberos або підпису.\n"
                    "• Повторне виконання авторизованої команди переказу коштів або відкриття замка.\n"
                    "• Затримка передачі пакета зловмисником та надсилання після зміни контексту.",
                    size=11, fill="#ffffff", stroke=POS, sw=1.2))

    f.append(fitbox(615, y_top + 155, col_w, 85,
                    "ХАРАКТЕРИСТИКА ЗАГРОЗИ:\n"
                    "• Криптографічний підпис (HMAC/RSA) валідний, бо створений жертвою.\n"
                    "• Зловмиснику не потрібно знати секретний ключ — достатньо переслати сирий байткод.\n"
                    "• Небезпека: несанкціонований доступ, розкрадання активів, обхід контролю доступу.",
                    size=11, fill="#ffffff", stroke=POS, sw=1.2))

    f.append(fitbox(615, y_top + 250, col_w, 95,
                    "ГОЛОВНІ ТАКТИКИ ЗАХИСТУ:\n"
                    "1. Одноразові випадкові числа (Cryptographic Nonce) + челендж сервера.\n"
                    "2. Часові мітки (Timestamp) + жорстке часове вікно валідності.\n"
                    "3. Ковзні бітмапи порядкових номерів (IPsec / QUIC Anti-Replay).\n"
                    "4. Одноразові токени з прив'язкою до каналу (Channel Binding).",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    # Нижній блок: спільний висновок для архітектора
    f.append(fitbox(45, 450, 1110, 80,
                    "КЛЮЧОВИЙ ВИСНОВОК АРХІТЕКТОРА:\n"
                    "Криптографічний підпис захищає цілісність та автентичність даних, але БЕЗСИЛИЙ проти перегравання.\n"
                    "Захист від повторення вимагає внесення в протокол динамічного фактора: або монотонного стану (State),\n"
                    "або обмеженого часу (Time), або непередбачуваної ентропії (Nonce).",
                    size=12, bold=True, fill=COOL, stroke=NEG, sw=1.5))

    f.append(fitbox(45, 545, 1110, 110,
                    "ШАРИ ОБОРОНИ В РОЗПОДІЛЕНІЙ СИСТЕМІ:\n"
                    "[Транспорт/Мережа: Nonce + Bitmap] → [API Шлюз: Timestamp + Idempotency Cache] → [Брокер: Fencing Tokens] → [База Даних: Inbox + FSM]",
                    size=12.5, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    render(os.path.join(OUT, 'replay-vector-taxonomy.svg'), W, H, *f)


# ── 2. Механіка ковзного бітмапа (Sliding Bitmap Window) ─────────────────────
def fig_sliding_bitmap_window_logic():
    W, H = 1200, 700
    f = []

    f.append(fitbox(40, 20, 1120, 46,
                    "МЕХАНІКА КОВЗНОГО БІТМАПА: Перевірка порядкових номерів у вікні W за O(1)",
                    size=14, bold=True, fill=COOL))

    # Схема вікна
    f.append(fitbox(50, 80, 1100, 36,
                    "СТРУКТУРА СТАНУ ФІЛЬТРА: Максимальний номер Seq_max = 100, Розмір вікна W = 64 біти",
                    size=12, bold=True, fill=FILL))

    # Шкала номерів
    f.append(arrow(60, 160, 1140, 160, color=LINE, sw=2))
    f.append(text(1150, 164, "Seq No", size=12, bold=True, anchor="start"))

    # Зона 1: Застарілі (s <= Seq_max - W) -> s <= 36
    f.append(rect(80, 135, 300, 50, fill="#f5f5f5", stroke="#cccccc", sw=1.5))
    f.append(text(230, 165, "ЗОНА 1: Застарілі (s <= 36) [REJECT]", size=11.5, bold=True, color=MUTED))

    # Зона 2: Вікно W = 64 (37 .. 100)
    f.append(rect(390, 130, 470, 60, fill=GOOD, stroke=FIELD, sw=2.5))
    f.append(text(625, 165, "ЗОНА 2: Активне вікно W=64 біти (Seq ∈ [37 .. 100])", size=12.5, bold=True, color=FIELD))

    # Зона 3: Майбутні (s > 100)
    f.append(rect(870, 135, 250, 50, fill=COOL, stroke=NEG, sw=1.5))
    f.append(text(995, 165, "ЗОНА 3: Нові (s > 100) [ADVANCE]", size=11.5, bold=True, color=NEG))

    # Маркери
    f.append(line(390, 120, 390, 205, color=POS, sw=2, dash="4,4"))
    f.append(text(390, 220, "Seq_max - W (36)", size=11, color=POS, bold=True))

    f.append(line(860, 120, 860, 205, color=FIELD, sw=2.5))
    f.append(text(860, 220, "Seq_max = 100", size=11, color=FIELD, bold=True))

    # 3 Сценарії обробки вхідного пакета
    y_card = 250.0
    cw = 350.0

    # Картка 1: s <= Seq_max - W
    f.append(fitbox(50, y_card, cw, 42,
                    "ВИПАДОК 1: s <= Seq_max - W (s = 30)",
                    size=12, bold=True, fill=WARM, stroke=POS, sw=1.8))
    f.append(fitbox(50, y_card + 48, cw, 175,
                    "УМОВА: Номер випав за ліву межу вікна.\n\n"
                    "ПЕРЕВІРКА:\n"
                    "• Пакет занадто старий.\n"
                    "• Інформація про нього вже витіснена.\n\n"
                    "ДІЯ:\n"
                    "→ Негайне відхилення (DROP).\n"
                    "→ Бітмап НЕ змінюється.\n"
                    "→ Лічильник drop_stale++.",
                    size=11, fill="#ffffff", stroke=POS, sw=1.2))

    # Картка 2: s усередині вікна
    f.append(fitbox(425, y_card, cw, 42,
                    "ВИПАДОК 2: Seq_max - W < s <= Seq_max (s = 85)",
                    size=12, bold=True, fill=ACCENT, stroke=LINE, sw=1.8))
    f.append(fitbox(425, y_card + 48, cw, 175,
                    "УМОВА: Номер усередині активного вікна.\n\n"
                    "БІТОВА ПЕРЕВІРКА:\n"
                    "• diff = Seq_max - s = 100 - 85 = 15.\n"
                    "• bit = (bitmap >> diff) & 1ULL.\n\n"
                    "ДІЯ:\n"
                    "→ Якщо bit == 1: ДУБЛІКАТ (DROP).\n"
                    "→ Якщо bit == 0: ПРИЙНЯТИ.\n"
                    "→ bitmap |= (1ULL << diff).",
                    size=11, fill="#ffffff", stroke=LINE, sw=1.2))

    # Картка 3: s > Seq_max
    f.append(fitbox(800, y_card, cw, 42,
                    "ВИПАДОК 3: s > Seq_max (s = 105)",
                    size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.8))
    f.append(fitbox(800, y_card + 48, cw, 175,
                    "УМОВА: Новий максимальний номер.\n\n"
                    "ЗСУВ ВІКНА:\n"
                    "• shift = s - Seq_max = 105 - 100 = 5.\n"
                    "• bitmap = (bitmap << shift) | 1ULL.\n"
                    "• Seq_max = s = 105.\n\n"
                    "ДІЯ:\n"
                    "→ Пакет приймається (ACCEPT).\n"
                    "→ Старі 5 бітів зліва витісняються.",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.2))

    # Футер з оцінкою ефективності
    f.append(fitbox(50, 495, 1100, 175,
                    "ПЕРЕВАГИ СТРУКТУРИ КОВЗНОГО БІТМАПА (IPsec RFC 4303 / RFC 6479, QUIC):\n"
                    "1. Пам'ять O(1): Фіксований розмір стану (лише 8 байтів для W=64 або 128 байтів для W=1024).\n"
                    "2. Швидкість O(1): Перевірка та встановлення прапорця за 2–3 такти процесора (бітові зсуви <<, >> та маски &).\n"
                    "3. Стійкість до перевпорядкування (Out-of-Order): Пакети, затримані мережею на відстань < W, успішно приймаються.\n"
                    "4. Без блокувань (Lock-Free): У багатопотоковому середовищі реалізується через atomic compare-and-swap (CAS).",
                    size=11.5, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    render(os.path.join(OUT, 'sliding-bitmap-window-logic.svg'), W, H, *f)


# ── 3. Токени огорожі та зомбі-перегравання (Fencing Tokens) ────────────────
def fig_fencing_token_zombie_replay():
    W, H = 1200, 700
    f = []

    f.append(fitbox(40, 20, 1120, 46,
                    "ТОКЕНИ ОГОРОЖІ (FENCING TOKENS): Захист від запізнілого перегравання команд зомбі-лідером",
                    size=14, bold=True, fill=COOL))

    # Схема 4-х учасників: Клієнт 1 (старий), Брокер замків, Клієнт 2 (новий), Сховище
    y_top = 80.0
    cw = 240.0

    f.append(fitbox(45, y_top, cw, 45, "КЛІЄНТ 1 (Лідер А)\n[Зомбі через GC pause]", size=12, bold=True, fill=WARM, stroke=POS, sw=1.8))
    f.append(fitbox(335, y_top, cw, 45, "СЕРВЕР БЛОКУВАНЬ\n(Zookeeper / Raft / etcd)", size=12, bold=True, fill=COOL, stroke=NEG, sw=1.8))
    f.append(fitbox(625, y_top, cw, 45, "КЛІЄНТ 2 (Лідер Б)\n[Новий легітимний лідер]", size=12, bold=True, fill=GOOD, stroke=FIELD, sw=1.8))
    f.append(fitbox(915, y_top, cw, 45, "СПІЛЬНЕ СХОВИЩЕ (БД)\n[Огорожа: max_token = 34]", size=12, bold=True, fill=FILL, stroke=LINE, sw=1.8))

    # Вертикальні лінії життя
    f.append(line(165, 130, 165, 520, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(455, 130, 455, 520, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(745, 130, 745, 520, color=LINE, sw=1.5, dash="4,4"))
    f.append(line(1035, 130, 1035, 520, color=LINE, sw=1.5, dash="4,4"))

    # Крок 1: Клієнт 1 бере лок
    f.append(arrow(165, 150, 455, 150, color=NEG, sw=1.8))
    f.append(text(310, 142, "1. AcquireLock()", size=11, bold=True))

    f.append(arrow(455, 175, 165, 175, color=FIELD, sw=1.8))
    f.append(text(310, 167, "2. Granted (Fencing Token = 33)", size=11, color=FIELD, bold=True))

    # Крок 2: Пауза збирача сміття у Клієнта 1
    f.append(rect(145, 195, 40, 130, fill=WARM, stroke=POS, sw=2))
    f.append(text(165, 260, "GC PAUSE", size=10, bold=True, color=POS))
    f.append(text(250, 245, "Клієнт 1 завис на 15 секунд;\nОренда блокування спливає!", size=10.5, color=POS))

    # Крок 3: Сервер відкликає лок через таймаут і віддає Клієнту 2
    f.append(arrow(745, 285, 455, 285, color=NEG, sw=1.8))
    f.append(text(600, 277, "3. AcquireLock()", size=11, bold=True))

    f.append(arrow(455, 310, 745, 310, color=FIELD, sw=1.8))
    f.append(text(600, 302, "4. Granted (Fencing Token = 34)", size=11, color=FIELD, bold=True))

    # Крок 4: Клієнт 2 пише у сховище з токеном 34
    f.append(arrow(745, 345, 1035, 345, color=FIELD, sw=2))
    f.append(text(890, 337, "5. Write(data, token=34)", size=11, color=FIELD, bold=True))

    f.append(fitbox(935, 360, 200, 45, "Сховище: 34 > 0\nЗапис OK! max_token = 34", size=10.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    # Крок 5: Клієнт 1 прокидається і надсилає запізнілий запит (Replay of Stale Command)
    f.append(arrow(165, 435, 1035, 435, color=POS, sw=2))
    f.append(text(600, 427, "6. Запізнілий запис Клієнта 1: Write(stale_data, token=33) [ЗОМБІ-ПЕРЕГРАВАННЯ]", size=11, color=POS, bold=True))

    # Крок 6: Сховище відхиляє старий токен
    f.append(fitbox(935, 450, 200, 50, "Сховище: 33 < 34!\nВІДХИЛЕНО: Fencing Error!", size=10.5, bold=True, fill=WARM, stroke=POS, sw=1.8))

    f.append(arrow(1035, 510, 165, 510, color=POS, sw=1.8))
    f.append(text(600, 502, "7. Error 409 Conflict: Stale Fencing Token", size=11, color=POS, bold=True))

    # Футер з правилом
    f.append(fitbox(45, 545, 1110, 130,
                    "ЧОМУ РОЗПОДІЛЕНИЙ ЗАМОК БЕЗ ТОКЕНА ОГОРОЖІ Є ІЛЮЗІЄЮ БЕЗПЕКИ:\n"
                    "Жоден клієнт не може знати, чи володіє він замком у момент здійснення запису в базу даних (GC-паузи, свопінг, мережеві затримки).\n"
                    "Тому кінцеве сховище ЗОБОВ'ЯЗАНЕ саме виступати бар'єром огорожі, приймаючи тільки монотонно зростаючі номери епох (Epochs / Fencing Tokens).\n"
                    "Будь-який запит із токеном token <= max_seen_token відкидається як запізніле перегравання.",
                    size=11.5, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    render(os.path.join(OUT, 'fencing-token-zombie-replay.svg'), W, H, *f)


# ── 4. Багаторівнева матриця тактик захисту ─────────────────────────────────
def fig_replay_tactics_defense_matrix():
    W, H = 1200, 700
    f = []

    f.append(fitbox(40, 20, 1120, 46,
                    "БАГАТОРІВНЕВА СИСТЕМА ТАКТИК ЗАХИСТУ ВІД ПЕРЕГРАВАННЯ В АРХІТЕКТУРІ",
                    size=14, bold=True, fill=COOL))

    layers = [
        ("РІВЕНЬ 1: МЕРЕЖА ТА ТРАНСПОРТ (Wire & Transport)",
         "Ковзні бітмапи (Sliding Bitmaps, IPsec / QUIC), криптографічні Nonce, монотонні лічильники пакетів",
         "Відсікання мережевого шторму дублікатів та MitM-атак на рівні ядра / sidecar за лічені наносекунди (O(1) пам'ять).",
         GOOD, FIELD),
        ("РІВЕНЬ 2: ПРИКОРДОННИЙ ШЛЮЗ (API Gateway / Ingress)",
         "Часові мітки (Timestamps) + TTL-вікно (напр. ±300 с) + розподілений кеш Nonce (Redis / Memory)",
         "Захист публічних HTTP/gRPC API. Відсікає 99.9% застарілих та повторних запитів до передачі у внутрішню мережу.",
         COOL, NEG),
        ("РІВЕНЬ 3: ШЛЮЗ ЗАСТОСУНКУ (Idempotency Key Interceptor)",
         "Заголовки Idempotency-Key (UUIDv7) + збереження результату первинної відповіді в кеші / БД",
         "Гарантія того, що клієнт при retry отримає точний збережений результат першого виклику без повторного виконання бізнес-логіки.",
         ACCENT, LINE),
        ("РІВЕНЬ 4: РОЗПОДІЛЕНА КООРДИНАЦІЯ (Distributed Coordination)",
         "Токени огорожі (Fencing Tokens), монотонні номери епох (Epoch Numbers, Raft / Paxos)",
         "Захист від зомбі-лідерів після спліт-брейну або тривалих пауз процесу під час запису в спільні ресурси.",
         WARM, POS),
        ("РІВЕНЬ 5: ДОМЕННЕ ЯДРО ТА БАЗА ДАНИХ (Domain Core & Storage)",
         "Transactional Inbox Table, оптимістичне блокування (OCC / version), монотонні FSM-автомати",
         "Остаточний рубеж оборони: перевірка версії агрегату (WHERE version = expected) унеможливлює повторну мутацію стану.",
         GOOD, FIELD),
    ]

    y_pos = 80.0
    for title, tech, purpose, fill_c, stroke_c in layers:
        f.append(fitbox(45, y_pos, 1110, 32, title, size=12.5, bold=True, fill=fill_c, stroke=stroke_c, sw=1.8))
        f.append(fitbox(45, y_pos + 34, 450, 68, "ІНСТРУМЕНТИ:\n" + tech, size=11, bold=True, fill="#ffffff", stroke=stroke_c, sw=1.2))
        f.append(fitbox(500, y_pos + 34, 655, 68, "ПРИЗНАЧЕННЯ ТА ЕФЕКТ:\n" + purpose, size=11, fill="#ffffff", stroke=stroke_c, sw=1.2))
        y_pos += 114.0

    # Футер
    f.append(fitbox(45, 655, 1110, 32,
                    "ПРАВИЛО ГЛИБОКОГО ЗАХИСТУ: Жоден окремий рівень не дає 100% гарантії. Стійкість виникає лише з комбінації тактик.",
                    size=12, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    render(os.path.join(OUT, 'replay-tactics-defense-matrix.svg'), W, H, *f)


if __name__ == '__main__':
    fig_replay_vector_taxonomy()
    fig_sliding_bitmap_window_logic()
    fig_fencing_token_zombie_replay()
    fig_replay_tactics_defense_matrix()
    print("All figures generated successfully.")

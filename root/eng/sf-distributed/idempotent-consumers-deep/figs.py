# -*- coding: utf-8 -*-
"""Фігури до теми «Ідемпотентні консюмери ГЛИБОКО»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / збій / отруйна петля / витік
COOL = "#eaf0fd"   # стан / брокер / інформаційне поле
GOOD = "#e8f6ee"   # успіх / чисте рішення / дедуп / захист
ACCENT = "#fff8e1" # проміжний стан / сайд-ефект

# ── 1. Анатомія вікна дедуплікації (Sliding Dedup Window) ───────────────────
def fig_dedup_sliding_window_retention():
    W, H = 1200, 680
    f = []

    f.append(fitbox(40, 20, 1120, 46,
                    "АНАТОМІЯ ВІКНА ДЕДУПЛІКАЦІЇ: межі зберігання ключів, очищення TTL та загроза пізніх дублів",
                    size=14, bold=True, fill=COOL))

    # Верхній блок: Часова шкала та вікно зберігання
    f.append(fitbox(50, 80, 1100, 36,
                    "ЧАСОВА ШКАЛА ЖИТТЄВОГО ЦИКЛУ ПОВІДОМЛЕНЬ І ВІКНА ДЕДУПЛІКАЦІЇ (Tw)",
                    size=12, bold=True, fill=FILL))

    # Смуга часу
    f.append(arrow(80, 150, 1120, 150, color=LINE, sw=2))
    f.append(text(1130, 154, "Час (t)", size=12, bold=True, anchor="start"))

    # Зони на шкалі
    # Зона 1: Очищена історія (t < t_now - Tw)
    f.append(rect(80, 130, 260, 40, fill="#f0f0f0", stroke="#cccccc", sw=1))
    f.append(text(210, 155, "Очищена історія (TTL сплив)", size=11, color=MUTED))

    # Зона 2: Активне вікно дедуплікації Tw (t_now - Tw <= t <= t_now)
    f.append(rect(340, 125, 520, 50, fill=GOOD, stroke=FIELD, sw=2))
    f.append(text(600, 155, "АКТИВНЕ ВІКНО ДЕДУПЛІКАЦІЇ (Tw = T_broker + T_lag + T_jitter)", size=12, bold=True, color=FIELD))

    # Зона 3: Майбутні повідомлення
    f.append(rect(860, 130, 240, 40, fill=COOL, stroke=NEG, sw=1))
    f.append(text(980, 155, "Поточний час (t_now) / Нові події", size=11, color=NEG))

    # Поділки
    f.append(line(340, 120, 340, 180, color=POS, sw=2, dash="4,4"))
    f.append(text(340, 195, "Межа витіснення (t_now - Tw)", size=11, color=POS))

    f.append(line(860, 120, 860, 180, color=FIELD, sw=2))
    f.append(text(860, 195, "Поточний момент t_now", size=11, bold=True, color=FIELD))

    # Нижній блок: Порівняння сценаріїв прибуття дублікатів
    y_sc = 230.0
    hw = 530.0

    # Ліва картка: Дублікат усередині вікна (Успішна дедуплікація)
    f.append(fitbox(50, y_sc, hw, 50,
                    "СЦЕНАРІЙ 1: Дублікат прибуває ВСЕРЕДИНІ вікна (t ∈ Tw)",
                    size=12.5, bold=True, fill=GOOD, stroke=FIELD, sw=2))

    f.append(fitbox(50, y_sc + 60, hw, 140,
                    "1. Повідомлення ID=8492 вперше оброблено в момент t_0.\n"
                    "2. Ключ 'msg:8492' збережено в inbox-таблиці з TTL = 7 діб.\n"
                    "3. Мережевий таймаут брокера пересилає дублікат через 12 секунд.\n"
                    "4. Споживач перевіряє inbox: ключ знайдено!\n"
                    "5. ДІЯ: Мутація пропускається, відправляється швидкий ACK.\n"
                    "Результат: Стан системи цілісний, бізнес-ефект однократний.",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.4))

    f.append(fitbox(50, y_sc + 210, hw, 65,
                    "ВИСНОВОК: Поки дублікат вкладається у вікно Tw, дедуплікація\n"
                    "працює детерміновано без додаткових обмежень.",
                    size=11.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    # Права картка: Пізній дублікат поза вікном (Аварія / Пробиття дедуплікації)
    f.append(fitbox(620, y_sc, hw, 50,
                    "СЦЕНАРІЙ 2: Пізній дублікат ПОЗА вікном (t < t_now - Tw)",
                    size=12.5, bold=True, fill=WARM, stroke=POS, sw=2))

    f.append(fitbox(620, y_sc + 60, hw, 140,
                    "1. Повідомлення ID=1020 оброблено 10 днів тому (TTL=7 діб сплив).\n"
                    "2. Фоновий процес вичистив ключ 'msg:1020' для економії пам'яті.\n"
                    "3. Інженер повторно програє збійну чергу (Dead Letter Queue replay).\n"
                    "4. Споживач перевіряє inbox: запис ВІДСУТНІЙ (хибно-нове!).\n"
                    "5. ДІЯ: Споживач виконує списання вдруге!\n"
                    "Результат: Подвійне списання коштів, фінансова розбіжність.",
                    size=11, fill="#ffffff", stroke=POS, sw=1.4))

    f.append(fitbox(620, y_sc + 210, hw, 65,
                    "ЗАХИСТ ВІД ПІЗНІХ ДУБЛІВ: Монотонні контрольні точки (версії/епохи)\n"
                    "або детерміноване узгодження з журналом подій джерела.",
                    size=11.5, bold=True, fill=WARM, stroke=POS, sw=1.5))

    # Футер з інженерним правилом
    f.append(fitbox(50, 575, 1100, 75,
                    "ЗОЛОТЕ ПРАВИЛО ВІКНА ДЕДУПЛІКАЦІЇ:\n"
                    "Тривалість вікна Tw мусить перевищувати максимальний час утримання повідомлень у брокері (Broker Retention)\n"
                    "+ максимальний допустимий лаг відновлення споживача + розбіжність мережевих годинників.",
                    size=12, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    render(os.path.join(OUT, 'dedup-sliding-window-retention.svg'), W, H, *f)


# ── 2. Розділення чистого рішення й зовнішніх сайд-ефектів ───────────────────
def fig_pure_decision_vs_side_effect_pipeline():
    W, H = 1200, 700
    f = []

    f.append(fitbox(40, 20, 1120, 46,
                    "ТРИФАЗНИЙ КОНВЕЄР: Розділення чистого транзакційного рішення та зовнішніх сайд-ефектів",
                    size=14, bold=True, fill=COOL))

    # Три фази конвеєра
    col_w = 350.0
    y_top = 85.0

    # ФАЗА 1: Чисте локальне рішення
    f.append(fitbox(50, y_top, col_w, 60,
                    "ФАЗА 1: ЧИСТЕ РІШЕННЯ\nЛокальна ACID-транзакція",
                    size=13, bold=True, fill=GOOD, stroke=FIELD, sw=2))

    f.append(fitbox(50, y_top + 70, col_w, 240,
                    "1. Отримано подію: OrderCharged {id: 42, sum: 500}\n\n"
                    "2. BEGIN TRANSACTION (PostgreSQL):\n"
                    "   - INSERT INTO inbox (msg_id, status)\n"
                    "     VALUES ('msg-42', 'PENDING_CALL')\n"
                    "     ON CONFLICT DO NOTHING;\n"
                    "   - Розрахунок детермінованого токена:\n"
                    "     idemp_key = hash(msg_id, 'stripe_charge')\n"
                    "   - Запис наміру в outbox / intent-лог;\n"
                    "3. COMMIT;\n\n"
                    "Результат: Намір зафіксовано в БД.",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.4))

    f.append(fitbox(50, y_top + 320, col_w, 90,
                    "ТОЧКА ЗБОЮ 1 (Крах до виклику API):\n"
                    "База пам'ятає стан PENDING_CALL.\n"
                    "При повторі споживач бачить намір\n"
                    "і безпечно переходить до Фази 2.",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    # Стрілка між Фазою 1 і Фазою 2
    f.append(arrow(405, y_top + 190, 420, y_top + 190, color=LINE, sw=2.5))

    # ФАЗА 2: Зовнішній мережевий сайд-ефект
    f.append(fitbox(425, y_top, col_w, 60,
                    "ФАЗА 2: САЙД-ЕФЕКТ\nМережевий виклик стороннього API",
                    size=13, bold=True, fill=ACCENT, stroke="#d4ac0d", sw=2))

    f.append(fitbox(425, y_top + 70, col_w, 240,
                    "1. Формування HTTP POST до Stripe / SMS-шлюзу:\n"
                    "   Headers: Idempotency-Key = idemp_key\n"
                    "   Body: {amount: 500, currency: 'UAH'}\n\n"
                    "2. Виконання мережевого запиту:\n"
                    "   - Зовнішній сервіс отримує запит.\n"
                    "   - Якщо запит повторний (за idemp_key),\n"
                    "     сервіс повертає кешований результат,\n"
                    "     НЕ списуючи кошти вдруге!\n\n"
                    "3. Отримано відповідь: charge_id = 'ch_9912'.",
                    size=11, fill="#ffffff", stroke="#d4ac0d", sw=1.4))

    f.append(fitbox(425, y_top + 320, col_w, 90,
                    "ТОЧКА ЗБОЮ 2 (Крах під час/після виклику):\n"
                    "Списання відбулося, але ACK брокеру не пішов.\n"
                    "Новий воркер викличе Stripe з ТИМ САМИМ\n"
                    "idemp_key → Stripe НЕ зніме гроші вдруге!",
                    size=11, bold=True, fill=ACCENT, stroke="#d4ac0d", sw=1.2))

    # Стрілка між Фазою 2 і Фазою 3
    f.append(arrow(780, y_top + 190, 795, y_top + 190, color=LINE, sw=2.5))

    # ФАЗА 3: Фіналізація та коміт зсуву
    f.append(fitbox(800, y_top, col_w, 60,
                    "ФАЗА 3: ФІНАЛІЗАЦІЯ\nЗакріплення стану та ACK брокеру",
                    size=13, bold=True, fill=GOOD, stroke=FIELD, sw=2))

    f.append(fitbox(800, y_top + 70, col_w, 240,
                    "1. BEGIN TRANSACTION (PostgreSQL):\n"
                    "   - UPDATE inbox SET status = 'COMPLETED',\n"
                    "     external_ref = 'ch_9912'\n"
                    "     WHERE msg_id = 'msg-42';\n"
                    "   - UPDATE orders SET status = 'PAID'\n"
                    "     WHERE id = 42;\n"
                    "2. COMMIT;\n\n"
                    "3. Підтвердження повідомлення в брокері:\n"
                    "   - consumer.commit_offset('msg-42')\n"
                    "   - Брокер просуває вказівник зчитування.",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.4))

    f.append(fitbox(800, y_top + 320, col_w, 90,
                    "ТОЧКА ЗБОЮ 3 (Крах до commit offset):\n"
                    "Брокер пересилає подію знову. Споживач\n"
                    "бачить status='COMPLETED' у базі даних,\n"
                    "пропускає кроки 1-2 і шле ACK брокеру.",
                    size=11, bold=True, fill=GOOD, stroke=FIELD, sw=1.2))

    # Нижній банер: Порівняння з наївною схемою
    f.append(fitbox(50, 520, 1100, 70,
                    "ФУНДАМЕНТАЛЬНЕ ПРАВИЛО ЗОВНІШНІХ ЕФЕКТІВ:\n"
                    "Неможливо включити сторонній HTTP/gRPC сервіс у локальну транзакцію бази даних.\n"
                    "Єдиний надійний спосіб — генерація детермінованого токена ідемпотентності на Фазі 1 та передача його зовнішньому API на Фазі 2.",
                    size=12, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    render(os.path.join(OUT, 'pure-decision-vs-side-effect-pipeline.svg'), W, H, *f)


# ── 3. Отруйна петля (Poison Loop) та механіка її розриву ────────────────────
def fig_poison_loop_break_mechanics():
    W, H = 1200, 680
    f = []

    f.append(fitbox(40, 20, 1120, 46,
                    "АНАТОМІЯ ОТРУЙНОЇ ПЕТЛІ (POISON LOOP) ТА 4-РІВНЕВИЙ МЕХАНІЗМ РОЗРИВУ",
                    size=14, bold=True, fill=WARM, stroke=POS, sw=2))

    # Ліва половина: Схема утворення отруйної петлі
    hw = 530.0
    y0 = 85.0

    f.append(fitbox(50, y0, hw, 50,
                    "НЕБЕЗПЕКА: ЯК УТВОРЮЄТЬСЯ ОТРУЙНА ПЕТЛЯ",
                    size=13, bold=True, fill=WARM, stroke=POS, sw=2))

    f.append(fitbox(50, y0 + 60, hw, 260,
                    "┌─────────────────────────────────────────────────────────────┐\n"
                    "│ 1. Брокер видає 'отруйне' повідомлення msg-99 (битий JSON /  │\n"
                    "│    несумісна бізнес-логіка / збій стороннього сервісу).     │\n"
                    "│                                                             │\n"
                    "│ 2. Споживач бере повідомлення в обробку:                   │\n"
                    "│    - Або падає з фатальною помилкою (Panic/OOM/SIGSEGV)     │\n"
                    "│    - Або виконує неідемпотентний сайд-ефект і падає до ACK! │\n"
                    "│                                                             │\n"
                    "│ 3. Брокер НЕ отримує ACK протягом Visibility Timeout.       │\n"
                    "│                                                             │\n"
                    "│ 4. Брокер повертає msg-99 на початок черги.                 │\n"
                    "│                                                             │\n"
                    "│ 5. Споживач знову читає msg-99 і ЗНОВУ ПАДАЄ!               │\n"
                    "└─────────────────────────────────────────────────────────────┘\n"
                    "НАСЛІДКИ: 100% завантаження CPU, блокування всієї партиції,\n"
                    "каскадне падіння пулу воркерів та подвоєння побічних ефектів.",
                    size=11, fill="#ffffff", stroke=POS, sw=1.4))

    f.append(fitbox(50, y0 + 330, hw, 90,
                    "ПАСТКА БЕЗЗАХИСНОГО RETRY:\n"
                    "Необмежені повторні спроби (infinite retries) за наявності\n"
                    "детермінованої помилки перетворюють споживача на генератор збоїв,\n"
                    "паралізуючи обробку всіх наступних валідних повідомлень.",
                    size=11.5, bold=True, fill=WARM, stroke=POS, sw=1.5))

    # Права половина: 4-рівневий контур захисту
    f.append(fitbox(620, y0, hw, 50,
                    "РІШЕННЯ: 4-РІВНЕВИЙ РОЗРИВ ОТРУЙНОЇ ПЕТЛІ",
                    size=13, bold=True, fill=GOOD, stroke=FIELD, sw=2))

    f.append(fitbox(620, y0 + 60, hw, 70,
                    "РІВЕНЬ 1: Лічильник спроб (Delivery Attempts / Redelivery Count)\n"
                    "Брокер або заголовок повідомлення фіксує лічильник N.\n"
                    "Якщо N > MaxRetries (наприклад, 3-5), повідомлення маркується як отруйне.",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.3))

    f.append(fitbox(620, y0 + 135, hw, 70,
                    "РІВЕНЬ 2: Транзакційна ліза обробки (Processing Lease)\n"
                    "Фіксація взяття повідомлення в базі даних із таймаутом оренди.\n"
                    "Якщо воркер зависає, ліза захищає від одночасного подвійного виконання.",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.3))

    f.append(fitbox(620, y0 + 210, hw, 70,
                    "РІВЕНЬ 3: Ізоляція в Dead Letter Queue (DLQ) з компенсацією\n"
                    "Отруйне повідомлення вилучається з основного потоку й записується в DLQ;\n"
                    "зсув (offset) у брокері підтверджується, звільняючи чергу.",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.3))

    f.append(fitbox(620, y0 + 285, hw, 70,
                    "РІВЕНЬ 4: Аварійний розривач ланцюга (Circuit Breaker)\n"
                    "Якщо частка збійних повідомлень перевищує 15% за 1 хвилину,\n"
                    "консюмер призупиняє вичитку (pause), щоб не спалити зовнішнє API.",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.3))

    f.append(fitbox(620, y0 + 360, hw, 60,
                    "РЕЗУЛЬТАТ: Черга продовжує рух, збійні події безпечно ізолюються,\n"
                    "а споживач ніколи не потрапляє в нескінченний цикл рестартів.",
                    size=11.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    # Нижній підсумок
    f.append(fitbox(50, 550, 1100, 75,
                    "ІНЖЕНЕРНИЙ ЗАКОН ОТРУЙНИХ ПОВІДОМЛЕНЬ:\n"
                    "Будь-який ідемпотентний консюмер зобов'язаний мати жорсткий ліміт спроб і детермінований маршрут у DLQ.\n"
                    "Ніколи не дозволяйте непідтвердженому збою блокувати просування зсуву в черзі безстроково.",
                    size=12, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    render(os.path.join(OUT, 'poison-loop-break-mechanics.svg'), W, H, *f)


# ── 4. Дедуплікація при ребалансуванні та зміні топології ─────────────────────
def fig_repartition_rebalance_fencing():
    W, H = 1200, 680
    f = []

    f.append(fitbox(40, 20, 1120, 46,
                    "ДЕДУПЛІКАЦІЯ ПРИ РЕБАЛАНСУВАННІ: Захист від розщеплення мозку через епохи та Fencing Tokens",
                    size=14, bold=True, fill=COOL))

    hw = 530.0
    y0 = 85.0

    # Ліва колонка: Проблема зомбі-споживача під час ребалансу
    f.append(fitbox(50, y0, hw, 50,
                    "ПРОБЛЕМА: ЗОМБІ-СПОЖИВАЧ ПРИ РЕБАЛАНСУВАННІ",
                    size=12.5, bold=True, fill=WARM, stroke=POS, sw=2))

    f.append(fitbox(50, y0 + 60, hw, 380,
                    "1. Воркер А обробляє партицію P0 (Епоха покоління Gen=1).\n\n"
                    "2. Воркер А потрапляє в тривалу GC-паузу (Stop-the-World на 35 с).\n\n"
                    "3. Координатор групи фіксує таймаут серцебиття (heartbeat timeout)\n"
                    "   і запускає РЕБАЛАНСУВАННЯ групи (Rebalance).\n\n"
                    "4. Партицію P0 призначено новому Воркеру Б (Нова епоха Gen=2).\n\n"
                    "5. Воркер Б вичитує повідомлення offset=100, успішно змінює БД,\n"
                    "   оновлює стан і комітить offset=101.\n\n"
                    "6. Воркер А «прокидається» після паузи! Він НЕ знає, що втратив\n"
                    "   партицію, і намагається записати застарілі результати offset=100\n"
                    "   у базу даних поверх нових змін Воркера Б!\n\n"
                    "ХАЗАРД: Розщеплення мозку (Split-Brain) та затирання стану.",
                    size=11, fill="#ffffff", stroke=POS, sw=1.4))

    f.append(fitbox(50, y0 + 450, hw, 60,
                    "БЕЗ ЗАХИСТУ ЕПОХ: Два воркери вважають себе власниками\n"
                    "однієї партиції й виконують конкуруючі мутації.",
                    size=11.5, bold=True, fill=WARM, stroke=POS, sw=1.5))

    # Права колонка: Рішення з епохами та Fencing Tokens
    f.append(fitbox(620, y0, hw, 50,
                    "РІШЕННЯ: ЗАХИСТ ЧЕРЕЗ FENCING TOKENS ТА ЕПОХИ",
                    size=12.5, bold=True, fill=GOOD, stroke=FIELD, sw=2))

    f.append(fitbox(620, y0 + 60, hw, 380,
                    "1. Кожне призначення партиції супроводжується монотонним\n"
                    "   токеном огорожі: Fencing Token (Generation Epoch E).\n\n"
                    "2. База даних фіксує максимальну побачену епоху для кожної\n"
                    "   партиції в таблиці блокувань / метаданих:\n"
                    "   partition_leases (partition_id PRIMARY KEY, epoch BIGINT).\n\n"
                    "3. Коли Воркер Б (Gen=2) починає роботу, він оновлює:\n"
                    "   UPDATE partition_leases SET epoch = 2 WHERE partition_id = 0;\n\n"
                    "4. Коли «зомбі» Воркер А (Gen=1) прокидається й намагається зробити:\n"
                    "   UPDATE balances SET amount = ... WHERE epoch >= 1\n"
                    "   БАЗА ВІДКИДАЄ ЗАПИС, бо в таблиці вже записано epoch=2!\n\n"
                    "5. Транзакція Воркера А скасовується, зомбі-запис блокується.",
                    size=11, fill="#ffffff", stroke=FIELD, sw=1.4))

    f.append(fitbox(620, y0 + 450, hw, 60,
                    "РЕЗУЛЬТАТ: Монотонні токени огорожі гарантують, що лише актуальний\n"
                    "активний воркер поточної генерації може змінювати стан системи.",
                    size=11.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))

    # Нижній банер
    f.append(fitbox(50, 580, 1100, 65,
                    "ІНЖЕНЕРНИЙ ВИСНОВОК:\n"
                    "Дедуплікація в розподіленому кластері невіддільна від захисту від зомбі-процесів.\n"
                    "Поєднання Inbox-таблиці з перевіркою монотонної епохи (Fencing Token) усуває ризик подвійного запису при ребалансах.",
                    size=12, bold=True, fill=FILL, stroke=LINE, sw=1.5))

    render(os.path.join(OUT, 'repartition-rebalance-fencing.svg'), W, H, *f)


def main():
    fig_dedup_sliding_window_retention()
    fig_pure_decision_vs_side_effect_pipeline()
    fig_poison_loop_break_mechanics()
    fig_repartition_rebalance_fencing()
    print("All figures generated successfully.")

if __name__ == '__main__':
    main()

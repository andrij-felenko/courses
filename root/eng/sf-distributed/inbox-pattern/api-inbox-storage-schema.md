# 📋 Специфікація схеми таблиці та контрактів Transactional Inbox

Схема таблиці вхідної скриньки (Transactional Inbox) є контрактом збереження стану між асинхронним транспортом повідомлень та реляційним сховищем споживача. Її головне інженерне завдання — забезпечити фізичну неподільність перевірки унікальності повідомлення, фіксації його поточного стану в скінченному автоматі та мутації прикладних бізнес-таблиць.

Нижче наведено формальну специфікацію DDL, контрактів полів, рівнів ізоляції транзакцій, правил переходів станів, класифікації помилок, метрик телеметрії та стратегій індексування для промислової експлуатації в різних системах керування базами даних.

## DDL-визначення таблиці вхідної скриньки

Для коректної роботи в умовах багатопотокової конкурентності та розподілених воркерів таблиця вхідної скриньки повинна підтримувати суворі обмеження первинного ключа, перевірку допустимих статусів та механізм блокування через часові лізи (leases).

:::tabs
```sql
-- PostgreSQL DDL (Рекомендована промислова конфігурація)
CREATE TABLE inbox_messages (
    message_id       VARCHAR(128) NOT NULL,
    consumer_group   VARCHAR(64)  NOT NULL DEFAULT 'default',
    event_type       VARCHAR(128) NOT NULL,
    payload          JSONB        NOT NULL,
    status           VARCHAR(32)  NOT NULL DEFAULT 'RECEIVED',
    retry_count      INTEGER      NOT NULL DEFAULT 0,
    max_retries      INTEGER      NOT NULL DEFAULT 5,
    last_error       TEXT,
    locked_until     TIMESTAMPTZ,
    locked_by        VARCHAR(64),
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    processed_at     TIMESTAMPTZ,
    PRIMARY KEY (message_id, consumer_group),
    CONSTRAINT chk_inbox_status CHECK (status IN ('RECEIVED', 'PROCESSING', 'PROCESSED', 'FAILED'))
);

-- Частковий індекс для конкурентної вибірки активних завдань воркерами
CREATE INDEX idx_inbox_active_polling 
ON inbox_messages (consumer_group, created_at) 
WHERE status IN ('RECEIVED', 'PROCESSING');

-- Частковий індекс для фонового процесу очищення (TTL Pruning)
CREATE INDEX idx_inbox_processed_cleanup 
ON inbox_messages (processed_at) 
WHERE status = 'PROCESSED';
```
```sql
-- MySQL 8.0+ DDL (з підтримкою InnoDB та JSON)
CREATE TABLE inbox_messages (
    message_id       VARCHAR(128) NOT NULL,
    consumer_group   VARCHAR(64)  NOT NULL DEFAULT 'default',
    event_type       VARCHAR(128) NOT NULL,
    payload          JSON         NOT NULL,
    status           VARCHAR(32)  NOT NULL DEFAULT 'RECEIVED',
    retry_count      INT          NOT NULL DEFAULT 0,
    max_retries      INT          NOT NULL DEFAULT 5,
    last_error       TEXT,
    locked_until     DATETIME(6)  NULL,
    locked_by        VARCHAR(64)  NULL,
    created_at       DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    processed_at     DATETIME(6)  NULL,
    PRIMARY KEY (message_id, consumer_group),
    INDEX idx_inbox_polling (consumer_group, status, locked_until, created_at),
    INDEX idx_inbox_cleanup (processed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
```
```sql
-- SQLite DDL (для вбудованих застосунків та крайових вузлів)
CREATE TABLE inbox_messages (
    message_id       TEXT NOT NULL,
    consumer_group   TEXT NOT NULL DEFAULT 'default',
    event_type       TEXT NOT NULL,
    payload          TEXT NOT NULL,
    status           TEXT NOT NULL CHECK(status IN ('RECEIVED', 'PROCESSING', 'PROCESSED', 'FAILED')),
    retry_count      INTEGER NOT NULL DEFAULT 0,
    max_retries      INTEGER NOT NULL DEFAULT 5,
    last_error       TEXT,
    locked_until     INTEGER, -- Час у мілісекундах Epoch Unix
    locked_by        TEXT,
    created_at       INTEGER NOT NULL,
    processed_at     INTEGER,
    PRIMARY KEY (message_id, consumer_group)
);

CREATE INDEX idx_inbox_polling ON inbox_messages (consumer_group, status, locked_until);
CREATE INDEX idx_inbox_cleanup ON inbox_messages (processed_at);
```
:::

## Детальний опис полів та інваріантів

Кожне поле таблиці виконує чітку функцію в системі розподіленого контролю виконання:

1. **`message_id` (`VARCHAR(128)`):** Глобальний ідентифікатор події. Формується на стороні відправника (наприклад, формат UUIDv4 або монотонний UUIDv7). Складає складений первинний ключ разом із `consumer_group`. Головний інваріант: у межах однієї групи споживачів повторна вставка того самого `message_id` повинна завершуватися помилкою порушення унікальності або ігноруватися через конструкцію `ON CONFLICT DO NOTHING`.
2. **`consumer_group` (`VARCHAR(64)`):** Ідентифікатор логічного контексту або підсистеми споживача. Дозволяє кільком незалежним бізнес-обробникам (наприклад, сервісу аналітики та сервісу білінгу) використовувати спільну таблицю або спільний екземпляр бази даних без взаємного блокування чи колізій ідентифікаторів.
3. **`event_type` (`VARCHAR(128)`):** Канонічне ім'я доменної події (наприклад, `billing.invoice_settled.v2`). Використовується диспетчером споживача для динамічної маршрутизації до відповідного обробника (Handler) без потреби розпаковувати повний JSON-документ.
4. **`payload` (`JSONB / JSON / TEXT`):** Повне тіло вхідного повідомлення у форматі серіалізації (JSON, Avro чи Protobuf у шістнадцятковому або рядковому вигляді). Зберігання сирого тіла є критичним для асинхронного двоетапного режиму (Staged Inbox), де вичитування з черги відокремлене від бізнес-обробки.
5. **`status` (`VARCHAR(32)`):** Поточний стан повідомлення в скінченному автоматі життєвого циклу. Допустимі значення строго обмежені перевіркою `CHECK`: `RECEIVED`, `PROCESSING`, `PROCESSED`, `FAILED`.
6. **`retry_count` (`INTEGER`):** Лічильник невдалих спроб виконання бізнес-транзакції. Інкрементується на одиницю при кожному аварійному завершенні або перехопленні винятку під час роботи доменного коду.
7. **`max_retries` (`INTEGER`):** Конфігураційний ліміт спроб (за замовчуванням 5). Коли `retry_count >= max_retries`, статус повідомлення автоматично переводиться у `FAILED`, що запобігає нескінченному блокуванню черги отруйними повідомленнями (Poison Messages).
8. **`last_error` (`TEXT`):** Текстовий опис останнього винятку, код помилки та зріз стека викликів (stack trace). Забезпечує діагностику інцидентів без потреби шукати первинні логи у розподілених сховищах телеметрії.
9. **`locked_until` (`TIMESTAMPTZ / INTEGER`):** Часова мітка завершення дії ексклюзивного права на обробку (Lease). Якщо поточний час перевищує `locked_until`, повідомлення вважається покинутим (наприклад, через аварійну зупинку процесу воркера) і може бути повторно захоплене іншим екземпляром.
10. **`locked_by` (`VARCHAR(64)`):** Унікальне системне ім'я вузла або ідентифікатор потоку (наприклад, назва пода в Kubernetes `orders-consumer-84f9b-zk29a`), який зараз володіє лізою.
11. **`created_at` (`TIMESTAMPTZ`):** Час надходження повідомлення в базу даних споживача. Використовується для контролю порядку обробки (FIFO) та вимірювання затримки доставки (Delivery Lag).
12. **`processed_at` (`TIMESTAMPTZ`):** Точний момент успішної фіксації бізнес-транзакції. Слугує опорною точкою для розрахунку строку давності запису при фоновому очищенні (TTL Retention).

## Специфікація скінченного автомата переходів станів

Життєвий цикл повідомлення у вхідній скриньці підпорядковується суворим інваріантам скінченного автомата:

| Початковий стан | Подія / Умова | Кінцевий стан | Зміни в полях таблиці | Опис транзакційного ефекту |
| :--- | :--- | :--- | :--- | :--- |
| *Не існує* | Отримання з черги (Асинхронний режим) | `RECEIVED` | `created_at = NOW()`, `status = 'RECEIVED'` | Повідомлення збережено в буфері. Брокеру повертається підтвердження (ACK). |
| *Не існує* | Отримання з черги (Синхронний режим) | `PROCESSED` | `processed_at = NOW()`, `status = 'PROCESSED'` | Атомарно виконуються бізнес-зміни й запис в `inbox`. Брокеру повертається ACK. |
| `RECEIVED` | Захоплення воркером | `PROCESSING` | `locked_until = NOW() + INTERVAL '30s'`, `locked_by = worker_id` | Воркер отримує ексклюзивне право на обробку завдяки `FOR UPDATE SKIP LOCKED`. |
| `PROCESSING` | Успішне виконання бізнес-коду | `PROCESSED` | `status = 'PROCESSED'`, `processed_at = NOW()`, `locked_until = NULL` | Бізнес-транзакція зафіксована (`COMMIT`). Завдання знято з обробки. |
| `PROCESSING` | Тимчасовий збій (`retry < max`) | `RECEIVED` | `status = 'RECEIVED'`, `retry_count++`, `last_error = err`, `locked_until = NULL` | Транзакція відкотилася. Повідомлення повернуто в чергу з експоненційним запізненням. |
| `PROCESSING` | Фатальний збій (`retry >= max`) | `FAILED` | `status = 'FAILED'`, `retry_count++`, `last_error = err`, `locked_until = NULL` | Повідомлення ізольовано від основного потоку. Спрацьовує сповіщення або відправка в DLQ. |
| `PROCESSING` | Аварія воркера (спливання лізи) | `PROCESSING` | `locked_until < NOW()` | Новий воркер виявляє прострочену лізу й оновлює `locked_until` на себе. |
| `PROCESSED` | Спливання строку збереження | *Видалено* | Рядок вилучається (`DELETE` / `DROP PARTITION`) | Фоновий процес TTL звільняє дисковий простір після завершення безпечного вікна. |

## Класифікація помилок та тактики повторів

При виникненні виняткових ситуацій під час виконання обробника споживач зобов'язаний розрізняти тип збою для вибору коректної тактики:

1. **Тимчасові помилки (Transient Failures):**
   - Блокування рядків у базі даних (Deadlock `40P01` або Lock Not Available `55P03`).
   - Короткочасні мережеві розриви або таймаути внутрішніх системних викликів.
   - *Тактика:* Транзакція відкочується, статус залишається `RECEIVED`, лічильник `retry_count` збільшується, а наступна спроба планується з експоненційним відступом (Exponential Backoff з додаванням випадкового тремтіння — jitter).
2. **Термінальні доменні помилки (Terminal Failures):**
   - Порушення схеми корисного навантаження (Invalid JSON, відсутність обов'язкових полів).
   - Невиправні порушення бізнес-правил (спроба списання з неіснуючого рахунку).
   - *Тактика:* Повторення не має сенсу, оскільки дані є некоректними. Повідомлення негайно переводиться в статус `FAILED`, фіксується в таблиці та передається до оператора або спеціалізованої черги мертвих листів (Dead Letter Queue).
3. **Аварійне переривання процесу (Process Termination / Crash):**
   - Аварійне завершення процесу споживача операційною системою (SIGKILL / OOM).
   - *Тактика:* Транзакція бази даних автоматично закривається та відкочується СУБД. Ліза `locked_until` стає неактивною після завершення часового вікна, після чого повідомлення автоматично підхоплюється сусіднім екземпляром воркера.

## Рівні ізоляції транзакцій та поведінка блокувань

Для гарантування відсутності станів гонитви запити взаємодії з таблицею `inbox_messages` повинні виконуватися з дотриманням відповідних рівнів транзакційної ізоляції:

- **Read Committed (Стандарт для PostgreSQL та MySQL):** Достатній для більшості операцій за умови використання атомарних конструкцій `INSERT ... ON CONFLICT` або блокування вибірки `SELECT ... FOR UPDATE SKIP LOCKED`. Кожен рядок блокується ексклюзивним замком на рівні рядка (Row-Level Exclusive Lock) до моменту коміту транзакції.
- **Repeatable Read / Serializable:** Використовується, коли логіка обробника вимагає повної узгодженості читання кількох пов'язаних таблиць. У разі виникнення помилок серіалізації (Serialization Failure у PostgreSQL) обробник зобов'язаний автоматично повторити транзакцію з початкової точки.

## Стандартні операційні SQL-запити

### 1. Синхронна атомарна дедуплікація (Inline режим)

```sql
-- Виконується в межах єдиної транзакції разом із бізнес-змінами
INSERT INTO inbox_messages (
    message_id, 
    consumer_group, 
    event_type, 
    payload, 
    status, 
    processed_at
) VALUES (
    :message_id, 
    :consumer_group, 
    :event_type, 
    :payload, 
    'PROCESSED', 
    NOW()
) ON CONFLICT (message_id, consumer_group) DO NOTHING;

-- Перевірка кількості вставлених рядків:
-- Якщо rows_affected == 0 -> дублікат! Відкочуємо транзакцію і негайно шлемо ACK брокеру.
-- Якщо rows_affected == 1 -> нове повідомлення. Продовжуємо виконання доменного коду.
```

### 2. Конкурентна вибірка завдань пулом воркерів (Staged режим)

```sql
WITH candidate_batch AS (
    SELECT message_id, consumer_group
    FROM inbox_messages
    WHERE consumer_group = :consumer_group
      AND (
          status = 'RECEIVED'
          OR (status = 'PROCESSING' AND locked_until < NOW())
      )
    ORDER BY created_at ASC
    LIMIT :batch_size
    FOR UPDATE SKIP LOCKED
)
UPDATE inbox_messages m
SET status = 'PROCESSING',
    locked_until = NOW() + (:lease_seconds || ' seconds')::INTERVAL,
    locked_by = :worker_instance_id
FROM candidate_batch c
WHERE m.message_id = c.message_id
  AND m.consumer_group = c.consumer_group
RETURNING m.message_id, m.event_type, m.payload, m.retry_count;
```

### 3. Фіксація помилки з експоненційним запізненням

```sql
UPDATE inbox_messages
SET retry_count = retry_count + 1,
    last_error = :error_message,
    status = CASE 
        WHEN retry_count + 1 >= max_retries THEN 'FAILED' 
        ELSE 'RECEIVED' 
    END,
    -- Якщо статус лишається RECEIVED, відсуваємо час наступної обробки (Backoff)
    locked_until = CASE 
        WHEN retry_count + 1 < max_retries THEN NOW() + (POWER(2, retry_count) || ' seconds')::INTERVAL
        ELSE NULL 
    END,
    locked_by = NULL
WHERE message_id = :message_id
  AND consumer_group = :consumer_group;
```

### 4. Пакетне фонове очищення застарілих записів (TTL Pruning)

```sql
DELETE FROM inbox_messages
WHERE (message_id, consumer_group) IN (
    SELECT message_id, consumer_group
    FROM inbox_messages
    WHERE status = 'PROCESSED'
      AND processed_at < NOW() - (:retention_days || ' days')::INTERVAL
    ORDER BY processed_at ASC
    LIMIT :delete_batch_size
);
```

## Метрики спостережливості та телеметрія

Надійна експлуатація патерну вимагає експорту таких ключових метрик у систему моніторингу (Prometheus / OpenTelemetry):

- `inbox_messages_received_total{consumer_group, event_type}` — загальна кількість отриманих повідомлень.
- `inbox_duplicates_dropped_total{consumer_group, event_type}` — кількість відхилених дублікатів.
- `inbox_messages_processed_total{consumer_group, event_type}` — кількість успішно завершених бізнес-транзакцій.
- `inbox_messages_failed_total{consumer_group, event_type}` — кількість повідомлень, що досягли статусу `FAILED`.
- `inbox_processing_duration_seconds{consumer_group, event_type}` — гістограма часу виконання бізнес-обробки.
- `inbox_lease_expirations_total{consumer_group}` — кількість випадків перехоплення прострочених ліз через падіння воркерів.
- `inbox_backlog_size{consumer_group, status}` — поточна кількість записів у станах `RECEIVED` та `PROCESSING`.

Ця специфікація забезпечує повний контракт зберігання, необхідний для побудови надійного ідемпотентного споживача подій у будь-якій корпоративній реляційній базі даних.

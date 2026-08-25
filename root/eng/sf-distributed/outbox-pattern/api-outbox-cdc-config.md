# 📋 Контракт таблиці Outbox та конфігурація CDC-конектора Debezium

Цей довідник містить повну специфікацію реляційної схеми вихідної скриньки (*Transactional Outbox Table*), конфігурацію конектора розподіленого вилучення змін *Debezium PostgreSQL Connector* та налаштування модуля маршрутизації подій *Outbox Event Router (SMT)* для публікації доменних подій в кластер Apache Kafka.

## Схема реляційної таблиці Outbox (PostgreSQL DDL)

Таблиця вихідної скриньки оптимізована для двох режимів експлуатації: високої інтенсивності вставок транзакцій застосунку та швидкого декодування журналом WAL із мінімальним дисковим роздуванням (*table bloat*).

```sql
CREATE TABLE public.outbox (
    id             UUID                     NOT NULL,
    aggregate_type VARCHAR(128)             NOT NULL,
    aggregate_id   VARCHAR(128)             NOT NULL,
    type           VARCHAR(256)             NOT NULL,
    payload        JSONB                    NOT NULL,
    headers        JSONB                    DEFAULT '{}'::jsonb NOT NULL,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL,
    
    CONSTRAINT pk_outbox PRIMARY KEY (id)
)
WITH (
    autovacuum_vacuum_scale_factor = 0.01,
    autovacuum_vacuum_threshold = 100,
    autovacuum_vacuum_cost_limit = 2000,
    fillfactor = 90
);

-- Індекс для режиму періодичного опитування (Polling Publisher).
-- Якщо ретрансляція здійснюється виключно через CDC (Debezium), індекс не потрібен.
CREATE INDEX idx_outbox_polling ON public.outbox (created_at ASC)
    INCLUDE (aggregate_id, aggregate_type, type);
```

### Фізична організація дискових сторінок та налаштування зберігання

У високонавантажених системах таблиця `outbox` зазнає безперервного потоку операцій запису. При використанні схеми з періодичним очищенням або модифікацією статусів звичайні дефолтні налаштування PostgreSQL призводять до деградації продуктивності.

Параметр `fillfactor = 90` резервує 10% простору на кожній 8-кілобайтній дисковій сторінці таблиці. Це дозволяє рушію PostgreSQL виконувати оптимізацію *HOT (Heap-Only Tuples)*: якщо запис оновлюється або позначається як видалений у межах тієї самої сторінки, покажчики в індексах не переписуються, що суттєво знижує навантаження на дискову підсистему.

Агресивні параметри `autovacuum_vacuum_scale_factor = 0.01` та `autovacuum_vacuum_threshold = 100` змушують фоновий демон очищення запускатися вже після того, як у таблиці накопичиться 100 мертвих рядків або мутує 1% обсягу даних. Це запобігає неконтрольованому зростанню розміру файлу таблиці на диску.

### Призначення та семантика полів таблиці

Кожне поле таблиці виконує чітко визначену архітектурну функцію в конвеєрі передачі подій:

* **`id` (UUID):** Первинний ключ події. Генерується на боці застосунку перед початком транзакції. Рекомендується використовувати часово-впорядковані ідентифікатори UUIDv7 замість суто випадкових UUIDv4. Це запобігає фрагментації B-Tree індексу первинного ключа, оскільки нові записи завжди додаються в кінець дерева. Отримувачі подій використовують цей ідентифікатор у своїх таблицях `inbox` для наскрізної дедуплікації.
* **`aggregate_type` (VARCHAR):** Логічний домен або назва агрегату предметної області (наприклад, `orders`, `payments`, `users`). Модуль SMT використовує це значення для динамічної маршрутизації повідомлення у відповідний топік брокера.
* **`aggregate_id` (VARCHAR):** Унікальний ідентифікатор конкретного екземпляра сутності (наприклад, номер замовлення `ord-4812`). Це поле стає ключем повідомлення в Apache Kafka (*Message Key*). Завдяки детермінованому хешуванню ключа всі події, що стосуються одного замовлення, гарантовано потрапляють в одну й ту саму партицію топіка, що забезпечує збереження суворого хронологічного порядку їх обробки.
* **`type` (VARCHAR):** Специфічний тип доменної події (наприклад, `OrderCreated`, `PaymentCaptured`, `OrderCancelled`). Значення трансформується у заголовок повідомлення Kafka, дозволяючи консюмерам фільтрувати події без повного розбору тіла корисного навантаження.
* **`payload` (JSONB):** Структуроване бізнес-тіло повідомлення. Використання двійкового формату JSONB у PostgreSQL забезпечує валідацію коректності JSON на етапі вставки та дозволяє застосунку записувати довільні вкладені структури.
* **`headers` (JSONB):** Додаткові службові атрибути, які передаються безпосередньо в протокольні заголовки брокера (*Kafka Record Headers*). Тут розміщуються контекст розподіленого трасування OpenTelemetry (`traceparent`, `tracestate`), версія схеми даних та ідентифікатор користувача, який ініціював дію.
* **`created_at` (TIMESTAMPTZ):** Фізичний момент фіксації запису. Функція `clock_timestamp()` повертає реальний поточний час у момент виконання операції, на відміну від `NOW()`, яка повертає час старту поточної транзакції.

## Конфігурація Debezium PostgreSQL Connector

Нижче наведено робочий маніфест конфігурації конектора для платформи Kafka Connect у форматі JSON. Конектор підключається до реплікаційного слота PostgreSQL, читає журнал WAL через плагін `pgoutput` та трансформує вставки в топіки Kafka за допомогою `EventRouter`.

```json
{
  "name": "debezium-outbox-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "tasks.max": "1",
    "plugin.name": "pgoutput",
    
    "database.hostname": "postgres-primary.internal",
    "database.port": "5432",
    "database.user": "cdc_debezium_user",
    "database.password": "${file:/secrets/db.properties:cdc_password}",
    "database.dbname": "shop_db",
    "database.server.name": "shop_prod",
    
    "table.include.list": "public.outbox",
    "slot.name": "debezium_outbox_slot",
    "slot.drop.on.stop": "false",
    "publication.name": "dbz_outbox_publication",
    "publication.autocreate.mode": "filtered",
    
    "tombstones.on.delete": "false",
    "decimal.handling.mode": "double",
    "heartbeat.interval.ms": "5000",
    "heartbeat.action.query": "UPDATE public.outbox_heartbeat SET last_heartbeat = NOW() WHERE id = 1;",
    
    "transforms": "outbox",
    "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
    
    "transforms.outbox.table.fields.additional.placement": "type:header:eventType,headers:header",
    "transforms.outbox.table.field.event.id": "id",
    "transforms.outbox.table.field.event.key": "aggregate_id",
    "transforms.outbox.table.field.event.timestamp": "created_at",
    "transforms.outbox.table.field.event.payload": "payload",
    
    "transforms.outbox.route.by.field": "aggregate_type",
    "transforms.outbox.route.topic.replacement": "shop.events.${routedByValue}",
    
    "transforms.outbox.tracing.span.context.field": "headers",
    "transforms.outbox.tracing.operation.name": "outbox-forward"
  }
}
```

### Покроковий розбір параметрів конфігурації конектора

1. **`connector.class` та `tasks.max`:** Визначає Java-клас конектора. Значення `tasks.max` для реплікації PostgreSQL завжди дорівнює `1`, оскільки один реплікаційний слот PostgreSQL може безпечно читатися лише одним послідовним потоком процесу.
2. **`plugin.name: pgoutput`:** Вказує використання стандартного плагіна логічного декодування, вбудованого в ядро PostgreSQL починаючи з версії 10. Це усуває необхідність компіляції та встановлення сторонніх C-бібліотек (таких як застарілий `decoderbufs`).
3. **`table.include.list: public.outbox`:** Суворо обмежує область моніторингу виключно таблицею вихідної скриньки. Зміни в інших таблицях бази даних Debezium повністю ігнорує, що знижує витрати пам'яті та процесорного часу.
4. **`slot.name` та `slot.drop.on.stop`:** Задає ім'я реплікаційного слота. Параметр `slot.drop.on.stop = false` є критично важливим для надійності: при плановій зупинці або перезапуску Kafka Connect слот зберігається в базі даних, накопичуючи позицію LSN. Після перезапуску Debezium продовжує вичитувати події точно з місця зупинки без втрати жодної транзакції.
5. **`heartbeat.interval.ms` та `heartbeat.action.query`:** Запобігають небезпечному накопиченню незафіксованих WAL-файлів на диску при низькій інтенсивності подій у таблиці `outbox`. Конектор періодично виконує легковажне оновлення таблиці пульсу, змушуючи базу даних просувати позицію підтвердженого LSN вперед.

## Довідник параметрів Outbox Event Router (SMT)

Модуль `EventRouter` перехоплює стандартну внутрішню подію зміни рядка Debezium (*Change Event Envelope*) і перетворює її на чистий запис Kafka без надлишкових метаданих бази даних.

| Параметр | Тип | Дефолтне значення | Опис дії |
| :--- | :--- | :--- | :--- |
| `table.field.event.id` | Рядок | `id` | Поле, значення якого копіюється в заголовок `id` Kafka-повідомлення або використовується для ідентифікації. |
| `table.field.event.key` | Рядок | `aggregate_id` | Поле, що стає ключем (*Message Key*) запису в Kafka. Усі події з однаковим ключем потрапляють в одну партицію. |
| `table.field.event.payload` | Рядок | `payload` | Поле таблиці, вміст якого стає корисним навантаженням (*Payload / Value*) повідомлення Kafka. |
| `table.field.event.timestamp` | Рядок | порожньо | Поле, що встановлює часову мітку (*Kafka Record Timestamp*). |
| `route.by.field` | Рядок | `aggregate_type` | Поле, значення якого підставляється в змінну `${routedByValue}` для динамічного визначення цільового топіка. |
| `route.topic.replacement` | Рядок | `outbox.event.${routedByValue}` | Шаблон імені топіка Kafka. Наприклад, рядок з `aggregate_type = 'orders'` буде надіслано в топік `shop.events.orders`. |
| `table.fields.additional.placement` | Список | порожньо | Правила переносу колонок у заголовки Kafka. Формат: `<поле>:<тип_розміщення>:<ім'я_заголовка>`. |
| `route.tombstone.on.empty.payload` | Булеве | `false` | Чи надсилати tombstone-повідомлення при порожньому payload для сповіщення про видалення сутності. |

## Формат вихідного повідомлення Kafka (CloudEvents Contract)

Після проходження конвеєра Debezium SMT запис у топіку Kafka `shop.events.orders` набуває стандартизованого вигляду, повністю сумісного зі специфікацією CloudEvents 1.0:

```
[Kafka Record Metadata]
Topic:     shop.events.orders
Partition: 3 (визначено як murmur2_hash("order-98421") % TotalPartitions)
Key:       "order-98421"
Timestamp: 1724151600123

[Kafka Headers]
id:           "f47ac10b-58cc-4372-a567-0e02b2c3d479"
eventType:    "OrderPaid"
traceparent:  "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
contentType:  "application/json"

[Kafka Value (JSON Payload)]
{
  "orderId": "order-98421",
  "userId": 8412,
  "amount": 120000.00,
  "currency": "UAH",
  "items": [
    { "sku": "SRV-XEON-64G", "quantity": 1, "price": 120000.00 }
  ],
  "paidAt": "2026-08-20T12:00:00.123Z"
}
```

## Налаштування прав доступу та безпеки в PostgreSQL

Для безпечної роботи реплікаційного слота обліковий запис Debezium повинен володіти суворо обмеженими правами:

```sql
-- 1. Створення службового користувача з правами реплікації
CREATE USER cdc_debezium_user WITH REPLICATION ENCRYPTED PASSWORD 'strong_password';

-- 2. Надання прав на читання схеми та таблиці outbox
GRANT USAGE ON SCHEMA public TO cdc_debezium_user;
GRANT SELECT ON TABLE public.outbox TO cdc_debezium_user;

-- 3. Створення таблиці для механізму пульсу (heartbeat)
CREATE TABLE public.outbox_heartbeat (
    id             INT PRIMARY KEY,
    last_heartbeat TIMESTAMPTZ NOT NULL
);
INSERT INTO public.outbox_heartbeat (id, last_heartbeat) VALUES (1, NOW());
GRANT SELECT, UPDATE ON TABLE public.outbox_heartbeat TO cdc_debezium_user;

-- 4. Створення вибіркової публікації тільки для таблиці outbox
CREATE PUBLICATION dbz_outbox_publication FOR TABLE public.outbox, public.outbox_heartbeat;
```

## Діагностика та моніторинг реплікаційного слота

У промисловій експлуатації критично важливо відстежувати відставання реплікаційного слота (*Replication Lag*). Якщо Debezium зупиниться або втратить зв'язок із брокером Kafka, PostgreSQL не зможе видаляти застарілі WAL-файли з диска, що може призвести до повного вичерпання дискового простору сервера бази даних.

Запит для перевірки стану слота та обсягу накопиченого журналу:

```sql
SELECT 
    slot_name,
    active,
    active_pid,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained_wal_bytes,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)) AS pending_cdc_lag
FROM pg_replication_slots
WHERE slot_name = 'debezium_outbox_slot';
```

Показник `pending_cdc_lag` відображає точний обсяг даних у байтах, які ще не були оброблені конектором Debezium та відправлені в Apache Kafka.

> 🔧 **Навіщо це.** Встановлюйте алерти в системі Prometheus на метрику `retained_wal_bytes > 10 GB`. Це завчасно попередить чергового інженера про зупинку конектора до того, як база даних аварійно заблокує всі операції запису через переповнення файлової системи.

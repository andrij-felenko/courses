# 📋 Інтерфейс та конфігурація матеріалізованих представлень у PostgreSQL та ClickHouse

Матеріалізовані представлення в реляційних та аналітичних рушіях суттєво відрізняються синтаксисом, моделлю виконання, внутрішньою архітектурою, механізмами оновлення та поведінкою блокувань. Нижче наведено детальний технічний довідник контрактів, параметрів конфігурації, системних каталогів та діагностичних команд для PostgreSQL, ClickHouse, Oracle Database та Microsoft SQL Server.

---

### PostgreSQL: Командний інтерфейс, блокування та системні каталоги

У PostgreSQL матеріалізоване представлення є самостійним типом відношення (`relkind = 'm'`), яке фізично зберігається на диску у власному файлі сторінок (`relfilenode`), володіє власною статистикою планувальника та дозволяє створювати вторинні індекси.

#### 1. Створення представлення та параметри збереження

```sql
CREATE MATERIALIZED VIEW [ IF NOT EXISTS ] view_name
    [ (column_name [, ...] ) ]
    [ USING method ]
    [ WITH ( storage_parameter [= value] [, ... ] ) ]
    [ TABLESPACE tablespace_name ]
    AS query
    [ WITH [ NO ] DATA ];
```

Параметри команди:
* **`WITH DATA` (типова поведінка)**: запит `query` виконується безпосередньо під час створення представлення. Результат записується на диск у новий файл `relfilenode`, після чого представлення стає доступним для читання.
* **`WITH NO DATA`**: у системному каталозі реєструються лише метадані. Фізичний файл на диску створюється порожнім, а прапорець `relispopulated` встановлюється у значення `false`. Будь-яка спроба виконати `SELECT` до першого оновлення повертає помилку `ERROR: materialized view "..." has not been populated`. Цей режим є обов'язковим у скриптах міграцій, коли базові таблиці ще не заповнені або оновлення планується виконати у фоновому потоці.
* **`USING method`**: вказує рушій табличного доступу (Table Access Method, за замовчуванням `heap`).
* **`WITH (autovacuum_enabled = true, fillfactor = 80)`**: дозволяє налаштовувати коефіцієнт заповнення сторінок `fillfactor` та параметри фонового очищення від мертвих кортежів `autovacuum`.

#### 2. Команди оновлення (Refresh) та поведінка блокувань

```sql
REFRESH MATERIALIZED VIEW [ CONCURRENTLY ] view_name
    [ WITH [ NO ] DATA ];
```

##### Стандартне оновлення (`REFRESH MATERIALIZED VIEW`)
* **Рівень блокування**: накладає блокування `AccessExclusiveLock` на матеріалізоване представлення.
* **Вплив на конкурентність**: повністю блокує всі паралельні читання `SELECT`, інші оновлення `REFRESH` та операції вакуумування.
* **Механізм виконання**: створює новий фізичний файл `relfilenode`, повністю виконує запит `query`, скидає результат на диск, підміняє покажчик у системному каталозі `pg_class` та видаляє старий файл. Це найшвидший за часом спосіб повного оновлення, оскільки він не генерує мертвих кортежів і не потребує транзакційного журналу різниць.

##### Конкурентне оновлення (`REFRESH MATERIALIZED VIEW CONCURRENTLY`)
* **Рівень блокування**: накладає блокування `ExclusiveLock`. Дозволяє паралельним процесам безперешкодно читати старий стан представлення через оператори `SELECT`, але блокує інші операції модифікації схеми та паралельні `REFRESH`.
* **Обов'язкова вимога**: представлення зобов'язане мати щонайменше один **унікальний індекс** (`UNIQUE INDEX`), побудований без умови `WHERE` (часткові унікальні індекси не підтримуються).
* **Внутрішній алгоритм**:
  1. Створюється тимчасова таблиця, у яку повністю записується результат виконання вихідного запиту.
  2. Рушій виконує внутрішнє диференційне з'єднання старої версії представлення та тимчасової таблиці:
     ```sql
     -- Псевдокод внутрішнього порівняння PostgreSQL:
     SELECT diff.* FROM (
         SELECT 'INSERT' AS op, t.* FROM temp_table t
         LEFT JOIN matview m ON m.unique_key = t.unique_key
         WHERE m.unique_key IS NULL
         UNION ALL
         SELECT 'DELETE' AS op, m.* FROM matview m
         LEFT JOIN temp_table t ON t.unique_key = m.unique_key
         WHERE t.unique_key IS NULL
         UNION ALL
         SELECT 'UPDATE' AS op, t.* FROM temp_table t
         JOIN matview m ON m.unique_key = t.unique_key
         WHERE t.* IS DISTINCT FROM m.*
     ) diff;
     ```
  3. Усі знайдені різниці застосовуються як атомарний пакет операцій `INSERT`, `UPDATE` та `DELETE` безпосередньо до основного відношення в межах поточної транзакції.
* **Накладні витрати**: конкурентне оновлення вимагає до 2.5 разів більше дискового простору та в 2–4 рази більше часу, ніж стандартний `REFRESH`, а також генерує великий обсяг записів у журналі WAL.

#### 3. Моніторинг та системний каталог `pg_matviews`

Для перевірки стану та діагностики розміру матеріалізованих представлень використовується системне представлення `pg_matviews` разом із функціями вимірювання розміру:

```sql
SELECT
    schemaname,
    matviewname,
    matviewowner,
    ispopulated,
    pg_size_pretty(pg_total_relation_size(schemaname || '.' || matviewname)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname || '.' || matviewname)) AS data_size,
    pg_size_pretty(pg_indexes_size(schemaname || '.' || matviewname)) AS index_size
FROM pg_matviews;
```

---

### ClickHouse: Потоковий тригерний конвеєр перетворення

У стовпчиковій СУБД ClickHouse матеріалізоване представлення функціонує не як періодичний статичний знімок, а як **потоковий тригер на рівні блоків вставки**. Коли клієнт або черга повідомлень виконує `INSERT` у вихідну таблицю, рушій перехоплює вставлений блок даних у пам'яті, застосовує до нього вираз `SELECT` і відправляє агрегований результат у цільову таблицю.

#### 1. Синтаксис явного зв'язування з цільовою таблицею (`TO`)

Найбільш надійним архітектурним патерном у ClickHouse є явне створення цільової фізичної таблиці з рушієм сімейства `MergeTree` та окреме підключення матеріалізованого представлення через конструкцію `TO`:

```sql
-- 1. Цільова фізична таблиця для збереження агрегованих сум
CREATE TABLE analytics.daily_sales_dest (
    event_date Date,
    category_id UInt32,
    total_amount SimpleAggregateFunction(sum, Float64),
    order_count SimpleAggregateFunction(sum, UInt64)
) ENGINE = SummingMergeTree()
PRIMARY KEY (event_date, category_id)
ORDER BY (event_date, category_id);

-- 2. Матеріалізоване представлення-конвеєр
CREATE MATERIALIZED VIEW analytics.mv_daily_sales
TO analytics.daily_sales_dest
AS SELECT
    toDate(created_at) AS event_date,
    category_id,
    sum(amount) AS total_amount,
    count() AS order_count
FROM raw_data.orders
GROUP BY event_date, category_id;
```

#### 2. Рушій `AggregatingMergeTree` та функції проміжних бінарних станів

Для складних агрегатів, які не можна звести до простих сум (підрахунок унікальних значень, перцентилі, квантилі), ClickHouse використовує рушій `AggregatingMergeTree`. Стовпці такої таблиці зберігають бінарні серіалізовані стани агрегатних функцій (суфікс `*State`):

```sql
-- Таблиця агрегації перцентилів та унікальних користувачів
CREATE TABLE analytics.user_metrics_dest (
    event_date Date,
    device_type LowCardinality(String),
    unique_users AggregateFunction(uniq, UInt64),
    latency_p95 AggregateFunction(quantile(0.95), Float32),
    latency_p99 AggregateFunction(quantile(0.99), Float32)
) ENGINE = AggregatingMergeTree()
PRIMARY KEY (event_date, device_type)
ORDER BY (event_date, device_type);

-- Матеріалізоване в'ю накопичення станів
CREATE MATERIALIZED VIEW analytics.mv_user_metrics
TO analytics.user_metrics_dest
AS SELECT
    toDate(timestamp) AS event_date,
    device_type,
    uniqState(user_id) AS unique_users,
    quantileState(0.95)(latency_ms) AS latency_p95,
    quantileState(0.99)(latency_ms) AS latency_p99
FROM raw_data.access_logs
GROUP BY event_date, device_type;
```

#### 3. Читання агрегованих станів (суфікс `*Merge`)

Під час виконання аналітичних запитів над `AggregatingMergeTree` бінарні стани окремих LSM-партів зливаються за допомогою відповідних функцій із суфіксом `*Merge`:

```sql
SELECT
    event_date,
    device_type,
    uniqMerge(unique_users) AS active_users,
    quantileMerge(0.95)(latency_p95) AS p95,
    quantileMerge(0.99)(latency_p99) AS p99
FROM analytics.user_metrics_dest
WHERE event_date >= today() - INTERVAL 7 DAY
GROUP BY event_date, device_type
ORDER BY event_date, device_type;
```

#### 4. Особливості та підводні камені ClickHouse

* **Відсутність ретроспективного заповнення (Backfill)**: Створення матеріалізованого представлення `CREATE MATERIALIZED VIEW` у ClickHouse обробляє виключно **майбутні вставки**. Дані, які вже перебували в таблиці `orders` до моменту створення в'ю, не потрапляють у цільову таблицю. Для їхнього перенесення потрібен ручний запит:
  ```sql
  INSERT INTO analytics.daily_sales_dest
  SELECT toDate(created_at), category_id, sum(amount), count()
  FROM raw_data.orders
  GROUP BY toDate(created_at), category_id;
  ```
* **Незворотність помилок у в'ю**: Якщо під час виконання `INSERT` у вихідну таблицю вираз матеріалізованого представлення завершується аварійно (наприклад, через переповнення пам'яті `Memory limit exceeded`), **вся транзакція вставки у вихідну таблицю відхиляється**.

---

### Oracle Database: Журнали змін та швидке інкрементне оновлення

У СУБД Oracle реалізовано одну з найбільш зрілих моделей інкрементного оновлення `FAST REFRESH`. Для її функціонування над базовими таблицями створюються спеціальні системні журнали змін (Materialized View Logs):

```sql
-- 1. Створення журналу змін над базовою таблицею
CREATE MATERIALIZED VIEW LOG ON sales_orders
WITH ROWID, PRIMARY KEY (order_id, category_id),
SEQUENCE (amount, quantity)
INCLUDING NEW VALUES;

-- 2. Створення матеріалізованого представлення з підтримкою FAST REFRESH
CREATE MATERIALIZED VIEW mv_sales_summary
BUILD IMMEDIATE
REFRESH FAST ON COMMIT
ENABLE QUERY REWRITE
AS SELECT
    category_id,
    COUNT(*) AS total_orders,
    SUM(amount) AS total_revenue
FROM sales_orders
GROUP BY category_id;
```

Внутрішня системна таблиця журналу `MLOG$_SALES_ORDERS` зберігає ідентифікатор рядка `ROWID`, мітку часу транзакції `SNAPTIME$$`, тип DML-операції `DMLTYPE$$` (`I` для вставки, `U` для оновлення, `D` для видалення) та старі й нові значення агрегатних стовпців. Під час фіксації транзакції рушій зчитує лише нові рядки з `MLOG$_` і застосовує диференційні зміни безпосередньо до `mv_sales_summary`.

---

### Microsoft SQL Server: Індексовані представлення (Indexed Views)

У SQL Server матеріалізація досягається через накладання унікального кластеризованого індексу на стандартне представлення:

```sql
-- Створення представлення з жорсткою прив'язкою до схеми
CREATE VIEW dbo.vw_category_sales
WITH SCHEMABINDING
AS
SELECT
    category_id,
    COUNT_BIG(*) AS total_items,
    SUM(ISNULL(amount, 0)) AS total_revenue
FROM dbo.order_items
GROUP BY category_id;
GO

-- Фізична матеріалізація через кластеризований індекс
CREATE UNIQUE CLUSTERED INDEX idx_vw_category_sales
ON dbo.vw_category_sales (category_id);
```

Вимоги та обмеження SQL Server:
1. **`WITH SCHEMABINDING`**: забороняє будь-яку зміну структури базових таблиць (видалення або зміну типів стовпців), поки існує індексоване представлення.
2. **Обов'язковість `COUNT_BIG(*)`**: для коректного відстеження видалень у групах агрегації `GROUP BY` представлення зобов'язане містити `COUNT_BIG(*)` (64-бітний лічильник кратності).
3. **Підказка `WITH (NOEXPAND)`**: у редакції SQL Server Standard Edition оптимізатор автоматично розгортає представлення в AST-макрос, ігноруючи матеріалізований індекс, якщо клієнтський запит явно не вказує підказку `FROM dbo.vw_category_sales WITH (NOEXPAND)`. Лише редакція Enterprise Edition виконує прозоре автоматичне переписування запитів.

---

### Підсумковий порівняльний довідник

| Характеристика | PostgreSQL | ClickHouse | Oracle Database | MS SQL Server |
| :--- | :--- | :--- | :--- | :--- |
| **Термін у діалекті** | Materialized View | Materialized View | Materialized View | Indexed View |
| **Базовий механізм оновлення** | Повне оновлення (`REFRESH`) | Тригерна обробка вхідного блоку `INSERT` | `COMPLETE`, `FAST` (інкрементне) або `FORCE` | Синхронне транзакційне (`ON COMMIT`) |
| **Журнал фіксації дельт** | Немає (або зовнішній CDC через WAL) | Не потрібен (пакетне виконання над блоком) | Журнал змін `Materialized View Log` (`MLOG$_`) | Системний журнал транзакцій бази (`LDF`) |
| **Вимоги до схеми** | Довільний SQL-запит | Тільки прямий `SELECT` з агрегацією | Заборонено недетерміновані вирази | Обов'язкове `WITH SCHEMABINDING`, без `OUTER JOIN` |
| **Автоматичне переписування** | Немає в ядрі (вимагає прямого звернення) | Відсутнє | Працює через параметр `QUERY_REWRITE_ENABLED` | Працює автоматично в Enterprise Edition (або підказка `NOEXPAND`) |
| **Поведінка читачів при оновленні** | `ExclusiveLock` при `CONCURRENTLY` (читання вільне) | Неблокувальне читання (LSM-знімки) | Читання узгодженої версії через MVCC | Неблокувальне читання (під Snapshot Isolation) |

# 📋 Довідник безпечних DDL операцій та чекліст Zero-Downtime

Зміна схеми у високонавантажених базах даних під активним користувацьким трафіком вимагає суворого дотримання інженерних протоколів безпеки. Наївне виконання команд на зразок `ALTER TABLE ... ADD COLUMN ... DEFAULT ...` у старих версіях або додавання індексів без спеціальних прапорців може повністю заблокувати роботу виробничого кластера.

Цей довідник містить повну класифікацію безпечних та небезпечних DDL-операцій у PostgreSQL та MySQL, системні параметри тайм-аутів для захисту від блокувальних каскадів, а також покроковий чекліст для CI/CD конвеєрів.

---

### Класифікація DDL операцій у PostgreSQL (версії 11+)

У сучасних версіях PostgreSQL поведінка DDL суттєво оптимізована, проте багато операцій досі вимагають ексклюзивного блокування `AccessExclusiveLock`.

#### Таблиця операцій та рівнів блокування

| DDL Операція | Рівень блокування | Блокує читання? | Блокує запис? | Переписує всю таблицю? | Безпечна для Production? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ADD COLUMN col_name type` (NULL) | `AccessExclusiveLock` | Так (на частку мс) | Так (на частку мс) | Ні (лише метадані) | **Безпечно** (якщо встановлено `lock_timeout`) |
| `ADD COLUMN col type DEFAULT val` (PG 11+) | `AccessExclusiveLock` | Так (на частку мс) | Так (на частку мс) | Ні (зберігається в каталозі) | **Безпечно** (для константних значень) |
| `ADD COLUMN col type DEFAULT volatile_func()` | `AccessExclusiveLock` | Так (на весь час) | Так (на весь час) | Так (обчислює для кожного рядка) | **НЕБЕЗПЕЧНО!** Викликає тривалий Downtime. |
| `CREATE INDEX name ON tbl(col)` | `ShareLock` | Ні | Так (блокує всі `INSERT/UPDATE/DELETE`) | Ні | **НЕБЕЗПЕЧНО!** Блокує будь-яку модифікацію даних. |
| `CREATE INDEX CONCURRENTLY` | `ShareUpdateExclusive` | Ні | Ні | Ні | **БЕЗПЕЧНО.** Вимагає двох проходів, не блокує запис. |
| `DROP INDEX CONCURRENTLY` | `ShareUpdateExclusive` | Ні | Ні | Ні | **БЕЗПЕЧНО.** |
| `ALTER TABLE ... VALIDATE CONSTRAINT` | `ShareUpdateExclusive` | Ні | Ні | Ні | **БЕЗПЕЧНО.** Перевіряє обмеження без блокування запису. |
| `ALTER TABLE ... ADD CONSTRAINT NOT NULL` | `AccessExclusiveLock` | Так (на весь час) | Так (на весь час) | Так (сканує всю таблицю) | **НЕБЕЗПЕЧНО!** Вимагає попереднього додавання `CHECK (col IS NOT NULL) NOT VALID`. |
| `ALTER COLUMN TYPE (varchar(50) -> varchar(100))` | `AccessExclusiveLock` | Так (на частку мс) | Так (на частку мс) | Ні (лише оновлення метаданих) | **Безпечно** |
| `ALTER COLUMN TYPE (int -> bigint)` | `AccessExclusiveLock` | Так (на весь час) | Так (на весь час) | Так (повне копіювання таблиці) | **НЕБЕЗПЕЧНО!** Вимагає патерну Expand/Contract. |

---

### Детальний аналіз інженерних пасток при додаванні зовнішніх ключів (Foreign Keys)

Додавання зовнішнього ключа через стандартну конструкцію `ALTER TABLE orders ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id);` захоплює `AccessExclusiveLock` одночасно на **двох таблицях**: як на дочірній таблиці `orders`, так і на батьківській `users`.

Якщо таблиця `users` має високу частоту оновлень, система миттєво зазнає взаємного блокування (Deadlock) або каскадної зупинки обробки запитів.

#### Безпечний протокол додавання зовнішнього ключа:

```sql
-- 1. Додавання зовнішнього ключа без перевірки існуючих даних (миттєве блокування)
ALTER TABLE orders ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) NOT VALID;

-- 2. Валідація зовнішнього ключа у фоновому режимі (ShareRowExclusiveLock, читання та запис дозволені!)
ALTER TABLE orders VALIDATE CONSTRAINT fk_user;
```

Під час фази валідації PostgreSQL послідовно перевіряє всі рядки, не блокуючи паралельні операції модифікації в таблицях `users` та `orders`.

---

### Безпечне приєднання секцій (ATTACH PARTITION) у секціонованих таблицях

При роботі з великими секціонованими таблицями (Declarative Partitioning) пряме виконання команди `ALTER TABLE logs ATTACH PARTITION logs_2026_08 FOR VALUES FROM ('2026-08-01') TO ('2026-08-31');` вимагає повного сканування нової секції для перевірки того, що всі її рядки потрапляють у вказаний діапазон дат.

Під час цього сканування вся батьківська таблиця `logs` блокується монопольним замком `AccessExclusiveLock`, що повністю зупиняє вставку нових логів.

#### Безпечний патерн приєднання нової секції:

```sql
-- 1. Створення окремої таблиці секції
CREATE TABLE logs_2026_08 (LIKE logs INCLUDING ALL);

-- 2. Додавання перевірочного обмеження CHECK, що повністю покриває діапазон
ALTER TABLE logs_2026_08 ADD CONSTRAINT check_partition_bounds 
    CHECK (log_date >= '2026-08-01' AND log_date < '2026-09-01');

-- 3. Приєднання секції (миттєво, оскільки CHECK-обмеження гарантує валідність діапазону)
ALTER TABLE logs ATTACH PARTITION logs_2026_08 
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

-- 4. Видалення надлишкового обмеження CHECK після успішного приєднання
ALTER TABLE logs_2026_08 DROP CONSTRAINT check_partition_bounds;
```

---

### Обов'язкові налаштування сесії перед виконанням DDL

Щоб запобігти зависанню міграції у черзі блокувань та вичерпанню пулу з'єднань, кожна транзакція міграції повинна починатися з налаштування захисних тайм-аутів:

```sql
-- 1. Обмеження часу очікування отримання блокування (1-2 секунди)
SET lock_timeout = '2s';

-- 2. Обмеження загального часу виконання DDL запиту
SET statement_timeout = '30s';

-- 3. Для неблокуючих індексів (CONCURRENTLY) відключаємо стандартний транзакційний блок
-- Поза транзакцією:
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

Якщо протягом 2 секунд інша тривала транзакція утримує блокування на таблиці, команда негайно впаде з контрольованою помилкою, не накопичуючи чергу заблокованих запитів користувачів. Мігратор може спробувати повторити операцію пізніше за алгоритмом експоненційного відступу (Exponential Backoff).

---

### Патерн безпечного додавання NOT NULL обмеження в PostgreSQL

Пряме виконання команди `ALTER TABLE users ALTER COLUMN email SET NOT NULL;` призводить до повного сканування всієї таблиці під блокуванням `AccessExclusiveLock`. На таблиці з 50 мільйонами рядків це спричинить простий тривалістю в кілька хвилин.

#### Безпечний чотирикроковий рецепт Zero-Downtime

```sql
-- Крок 1: Додавання перевірочного обмеження без валідації (миттєве оновлення метаданих)
ALTER TABLE users ADD CONSTRAINT check_email_not_null CHECK (email IS NOT NULL) NOT VALID;

-- Крок 2: Валідація накопичених даних у фоновому режимі (ShareUpdateExclusiveLock, запис відкритий!)
ALTER TABLE users VALIDATE CONSTRAINT check_email_not_null;

-- Крок 3: Встановлення справжнього NOT NULL (миттєво, бо перевірку вже підтверджено обмеженням)
ALTER TABLE users ALTER COLUMN email SET NOT NULL;

-- Крок 4: Видалення тепер уже надлишкового обмеження CHECK
ALTER TABLE users DROP CONSTRAINT check_email_not_null;
```

---

### Класифікація DDL операцій у MySQL InnoDB (Online DDL)

Починаючи з MySQL 5.6+, рушій InnoDB підтримує механізм Online DDL із синтаксисом `ALGORITHM` та `LOCK`:

```sql
ALTER TABLE orders ADD INDEX idx_created_at (created_at),
    ALGORITHM=INPLACE,
    LOCK=NONE;
```

#### Матриця режимів Online DDL у MySQL

* `ALGORITHM=INPLACE, LOCK=NONE`: Операція виконується на місці без блокування паралельних читань та записів.
* `ALGORITHM=INPLACE, LOCK=SHARED`: Дозволяє паралельне читання, але блокує всі `INSERT/UPDATE/DELETE`.
* `ALGORITHM=COPY, LOCK=EXCLUSIVE`: Створює повну копію таблиці, блокуючи будь-який доступ (використовувати суворо заборонено у production).
* `ALGORITHM=INSTANT` (MySQL 8.0+): Миттєве оновлення метаданих без перезапису сторінок таблиці (додавання колонок у кінець таблиці, перейменування).

---

### Діагностичні SQL-запити для моніторингу черги блокувань

Для швидкого виявлення заблокованих запитів під час міграцій використовуються системні каталоги:

```sql
-- Пошук транзакцій, які очікують блокування, та процесів, що їх утримують (PostgreSQL)
SELECT 
    blocked_locks.pid     AS blocked_pid,
    blocked_activity.usename  AS blocked_user,
    blocking_locks.pid    AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query    AS blocked_statement,
    blocking_activity.query   AS blocking_statement
FROM  pg_catalog.pg_locks         blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks         blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

---

### Робота з перейменуванням таблиць та синонімами (Views / Aliases)

Коли необхідно перейменувати активну таблицю без зупинки коду старої версії додатку, використовується техніка створення перегляду-обгортки:

```sql
-- 1. Перейменування оригінальної таблиці
ALTER TABLE legacy_users RENAME TO users;

-- 2. Миттєве створення оновлюваного перегляду зі старим іменем (Updatable View)
CREATE VIEW legacy_users AS SELECT * FROM users;
```

Завдяки механізму автоматично оновлюваних переглядів (Automatically Updatable Views) у PostgreSQL та MySQL, старий код додатку може безперешкодно виконувати команди `INSERT`, `UPDATE` та `DELETE` над переглядом `legacy_users` без жодних модифікацій вихідного коду сервісу.

---

### Контроль розміру дискового простору та фрагментації (Bloat)

При масштабних перебудовах таблиць або додаванні важких індексів необхідно враховувати коефіцієнт подвоєння дискового простору. Такі операції, як `CREATE INDEX CONCURRENTLY` або робота `pg_repack`, вимагають наявності щонайменше 100% вільного дискового простору від поточного розміру таблиці для розміщення тимчасових структур та журналів змін до моменту завершення синхронізації.

---

### Контрольний чекліст аудиту міграцій для CI/CD

Перед злиттям гілки з міграцією в основний репозиторій автоматичний лінтер (наприклад, Squawk або pg-audit) повинен підтвердити виконання таких обов'язкових правил:

1. **Відсутність `ALTER TABLE` над живими полями без `lock_timeout`**: Будь-який скрипт повинен містити префікс встановлення безпечного тайм-ауту сесії.
2. **Індекси створюються виключно з прапорцем `CONCURRENTLY`**: Заборонено пряме виконання `CREATE INDEX`.
3. **Зміна типів колонок виконується за схемою Expand/Contract**: Заборонено пряме приведення типів (`ALTER TYPE`), що викликає повний перезапис сторінок таблиці.
4. **Видалення колонок виконується у два релізи**: Спочатку колонка перестає читатися й писатися новим кодом додатку, і лише в наступному релізі виконується DDL `DROP COLUMN`.
5. **Розмір батчів при масивному бекфілі обмежений**: Заборонено оновлювати мільйони рядків єдиною командою `UPDATE`. Оновлення повинно виконуватися чанками по 1000–5000 рядків із паузами для запобігання росту журналу WAL та відставання реплікації.
6. **Заборона виконання `CREATE INDEX CONCURRENTLY` всередині транзакційного блоку**: Усі мігратори повинні запускати паралельні індекси поза контекстом `BEGIN ... COMMIT`.
7. **Перевірка блокування зовнішніх ключів**: Будь-який `FOREIGN KEY` додається виключно з прапорцем `NOT VALID` із наступною асинхронною валідацією.
8. **Безпечне приєднання секцій**: Будь-яка нова секція створюється окремо з явним обмеженням `CHECK` до виклику команди `ATTACH PARTITION`.
9. **Заборона додавання колонок із функціональними дефолтами**: Додавання колонок із `DEFAULT now()` або випадковими функціями заборонено, оскільки це вимагає повного перезапису кожного рядка таблиці.
10. **Обов'язковий моніторинг вільного дискового простору**: Наявність мінімум подвійного запасу сховища перед запуском операцій онлайн-дефрагментації або побудови глобальних індексів.

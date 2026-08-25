# 📋 Реляційна схема та контракт API гросбуха

Ця довідкова специфікація визначає промислову реляційну схему даних на рівні СУБД PostgreSQL та контракт прикладного інтерфейсу (REST/JSON API) для сервісу гросбуха подвійного запису. Архітектура спроектована з розрахунком на високонавантажені фінансові системи, де будь-яка втрата цілісності, гонка потоків чи несанкціонована зміна даних тягне прямі фінансові та юридичні збитки.

## Принципи проектування схеми даних

Реляційна модель гросбуха спирається на розділення сутностей на три концептуальні рівні:
1. **План рахунків (*Chart of Accounts*)**: довідник рахунків, що класифікує активи, зобов'язання, власний капітал, доходи та витрати.
2. **Заголовки транзакцій (*Transaction Headers*)**: фіксація бізнес-події, зовнішнього ідентифікатора та ключа ідемпотентності.
3. **Журнал проводок (*Postings Log*)**: атомарні, незмінні рядки руху коштів між окремими рахунками.

### Чому обрано цілочисельний тип `BIGINT`

Усі фінансові суми в таблиці `postings` зберігаються у вигляді 64-бітного знакового цілого числа `BIGINT`. Сума виражається в мінімальних неподільних одиницях валюти (копійках, центах, сатоші або десятитисячних частках базової валюти — бейсіс-поінтах). Такий вибір усуває будь-які накопичувальні похибки двійкового округлення, притаманні стандартам чисел із плаваючою комою (IEEE 754), і водночас працює швидше та займає менше дискового простору, ніж рядковий або довільний десятковий тип `NUMERIC`. 64-бітне ціле число дозволяє зберігати суми до `9 223 372 036 854 775 807` одиниць (понад 92 квадрильйони гривень у копійках), що повністю виключає ризик арифметичного переповнення в осяжному майбутньому.

## Схема реляційної бази даних (DDL)

```sql
-- 1. Перелік класів рахунків згідно з фундаментальною бухгалтерською моделлю
CREATE TYPE account_type AS ENUM (
    'ASSET',      -- Активи (кошти в банку, каса, дебіторська заборгованість)
    'LIABILITY',  -- Зобов'язання (кошти клієнтів, борги перед постачальниками)
    'EQUITY',     -- Власний капітал (статутний фонд, нерозподілений прибуток)
    'REVENUE',    -- Доходи (комісії, плата за послуги, виручка)
    'EXPENSE'     -- Витрати (оренда, комісії еквайрингу, серверна інфраструктура)
);

-- 2. Таблиця рахунків (Chart of Accounts)
CREATE TABLE accounts (
    id            BIGSERIAL PRIMARY KEY,
    code          VARCHAR(64) NOT NULL UNIQUE,
    name          VARCHAR(255) NOT NULL,
    type          account_type NOT NULL,
    currency      CHAR(3) NOT NULL DEFAULT 'UAH',
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Заголовки транзакцій (Transaction Headers)
CREATE TABLE transactions (
    id              BIGSERIAL PRIMARY KEY,
    idempotency_key VARCHAR(128) NOT NULL UNIQUE,
    description     TEXT NOT NULL,
    posted_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Незмінний журнал проводок (Postings Log)
CREATE TABLE postings (
    id             BIGSERIAL PRIMARY KEY,
    transaction_id BIGINT NOT NULL REFERENCES transactions(id) ON DELETE RESTRICT,
    account_id     BIGINT NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    amount         BIGINT NOT NULL, -- Додатне значення: дебет/зарахування, від'ємне: кредит/списання
    sequence_num   BIGSERIAL NOT NULL UNIQUE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_posting_amount_non_zero CHECK (amount <> 0)
);

-- Індекси для оптимізації читання та звірок
CREATE INDEX idx_postings_account_seq ON postings(account_id, sequence_num);
CREATE INDEX idx_postings_tx_id ON postings(transaction_id);

-- 5. Тригер захисту незмінності журналу (Immutability Enforcement)
CREATE OR REPLACE FUNCTION prevent_posting_mutation()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Порушення аудиту: незмінний журнал проводок (postings) заборонено модифікувати або видаляти. Виправлення дозволено лише через сторнування.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_protect_postings
BEFORE UPDATE OR DELETE ON postings
FOR EACH ROW EXECUTE FUNCTION prevent_posting_mutation();

-- 6. Відкладений перевірочний тригер інваріанта нульової суми транзакції
CREATE OR REPLACE FUNCTION check_transaction_zero_sum()
RETURNS TRIGGER AS $$
DECLARE
    v_sum BIGINT;
    v_count INT;
BEGIN
    SELECT COALESCE(SUM(amount), 0), COUNT(*)
    INTO v_sum, v_count
    FROM postings
    WHERE transaction_id = NEW.transaction_id;

    IF v_count < 2 THEN
        RAISE EXCEPTION 'Транзакція #% недійсні: проведення повинно містити щонайменше дві проводки (знайдено %)',
            NEW.transaction_id, v_count;
    END IF;

    IF v_sum <> 0 THEN
        RAISE EXCEPTION 'Порушення балансу: сума проводок транзакції #% становить % замість очікуваного 0',
            NEW.transaction_id, v_sum;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE CONSTRAINT TRIGGER trg_enforce_zero_sum
AFTER INSERT ON postings
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION check_transaction_zero_sum();

-- 7. Таблиця періодичних матеріалізованих знімків залишків (Balance Snapshots)
CREATE TABLE balance_snapshots (
    account_id     BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    sequence_num   BIGINT NOT NULL,
    balance        BIGINT NOT NULL,
    snapshot_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (account_id, sequence_num)
);
```

## Механізм роботи відкладеного тригера цілісності

Звичайне табличне обмеження `CHECK` у реляційних СУБД працює на рівні окремого рядка і не здатне перевірити агреговану умову над кількома рядками. Оскільки фінансова транзакція записується в таблицю `postings` кількома послідовними операціями `INSERT` (по одному рядку для кожної проводки), проміжний стан після вставки першого рядка завжди має ненульову суму.

Для розв'язання цієї проблеми в схемі застосовано **відкладений обмежений тригер (*Constraint Trigger*)** з параметром `DEFERRABLE INITIALLY DEFERRED`. Він дозволяє додатку вставляти всі необхідні проводки всередині однієї транзакції бази даних без виклику виключень на кожному окремому рядку. Перевірка функції `check_transaction_zero_sum()` автоматично спрацьовує в момент виклику команди `COMMIT`. Якщо на момент фіксації сума проводок `SUM(amount)` не дорівнює нулю, вся транзакція СУБД негайно відкочується (`ROLLBACK`), гарантуючи абсолютну атомарність інваріанта.

## Індексна стратегія та оптимізація запитів

Схема використовує два спеціалізовані B-Tree індекси для оптимізації типових фінансових запитів:
1. **Складений індекс `idx_postings_account_seq (account_id, sequence_num)`**:
   Цей індекс є ключовим для обчислення залишків за патерном `Snapshot + Delta`. Коли додаток запитує баланс за формулою `WHERE account_id = 42 AND sequence_num > 1000000`, планувальник запитів PostgreSQL використовує пряме індексне сканування діапазону (*Index Range Scan*), уникаючи повного перегляду таблиці проводок. Крім того, цей індекс підтримує швидку генерацію виписок із сортуванням за монотонним порядковим номером.
2. **Індекс зовнішнього ключа `idx_postings_tx_id (transaction_id)`**:
   Забезпечує миттєве вилучення всіх проводок конкретної транзакції при аудиті, сторнуванні або перевірці нульової суми у відкладеному тригері. Без цього індексу перевірка зовнішнього ключа при вставці вимагала б послідовного сканування таблиці.

## Контроль конкурентності та захист від овердрафтів

Для більшості операцій у гросбусі достатньо рівня ізоляції транзакцій `READ COMMITTED`, оскільки записи в таблицю `postings` лише додаються. Проте коли бізнес-правило вимагає запобігання від'ємному балансу (захист від несанкціонованого овердрафту на клієнтських рахунках), просте читання та перевірка балансу перед вставкою проводок створює ризик гонки потоків (*Race Condition*).

Для абсолютного захисту від овердрафту застосовується техніка песимістичного блокування рахунку перед записом транзакції:
```sql
-- Блокування рядка рахунку для серіалізації паралельних списань
SELECT id FROM accounts WHERE code = 'CUSTOMER_WALLET_104' FOR UPDATE;
```
Цей виклик гарантує, що лише один обробник одночасно обчислює доступний залишок і записує списання, унеможливлюючи подвійну витрату коштів.

## Контракт прикладного HTTP/JSON API

### 1. Створення фінансової транзакції (Проведення)

Ендпоінт приймає запит на фіксацію господарської операції, що складається з набору проводок.

- **HTTP-метод**: `POST /v1/ledger/transactions`
- **Заголовки**:
  - `Idempotency-Key`: рядок UUID v4 (обов'язковий для захисту від подвійних списань при збоях мережі).
  - `Content-Type`: `application/json`

**Тіло запиту (Request Body):**
```json
{
  "description": "Оплата замовлення №94812 та утримання еквайрингової комісії",
  "postings": [
    {
      "account_code": "CUSTOMER_WALLET_USD_104",
      "amount": -10000
    },
    {
      "account_code": "MERCHANT_SETTLEMENT_USD_550",
      "amount": 9750
    },
    {
      "account_code": "ACQUIRING_FEE_REVENUE_USD",
      "amount": 250
    }
  ]
}
```

**Семантика полів:**
- `account_code` — унікальний текстовий ідентифікатор рахунку в плані рахунків.
- `amount` — знакова сума в мінімальних одиницях валюти (`-10000` відповідає списуванню 100.00 USD, `+9750` — зарахуванню 97.50 USD торговцю, `+250` — зарахуванню 2.50 USD комісії).

**Успішна відповідь (`201 Created` при першому виклику або `200 OK` при ідемпотентному повторі):**
```json
{
  "transaction_id": 904128,
  "idempotency_key": "7b6f3c1a-2894-4d6a-912a-89a1c90df102",
  "posted_at": "2026-08-20T16:40:12.381Z",
  "status": "POSTED",
  "postings_count": 3
}
```

**Матриця помилок валідації:**
- `400 Bad Request` — Сума проводок не дорівнює 0, передано менше двох проводок або сума будь-якої проводки дорівнює 0.
- `404 Not Found` — Один із переданих `account_code` відсутній у базі або деактивований.
- `409 Conflict` — Ключ ідемпотентності вже був використаний для транзакції з іншим корисним навантаженням.

---

### 2. Запит балансу рахунку на поточний момент або за номером послідовності

Ендпоінт повертає поточний розрахований баланс рахунку або історичний баланс на конкретну точку журналу.

- **HTTP-метод**: `GET /v1/ledger/accounts/{code}/balance`
- **Параметри запиту (Query Parameters)**:
  - `at_sequence`: ціле число (опціонально, повертає стан на момент конкретного порядкового номера `sequence_num`).

**Відповідь (`200 OK`):**
```json
{
  "account_code": "MERCHANT_SETTLEMENT_USD_550",
  "currency": "USD",
  "type": "LIABILITY",
  "calculated_balance": 4859000,
  "formatted_balance": "48590.00 USD",
  "at_sequence": 1284900,
  "snapshot_used_sequence": 1284000,
  "delta_postings_evaluated": 14
}
```

---

### 3. Отримання фінансової виписки рахунку (Statement API)

Ендпоінт повертає хронологічний реєстр проводок із розрахунком поточного залишку після кожної операції.

- **HTTP-метод**: `GET /v1/ledger/accounts/{code}/statement`
- **Параметри запиту (Query Parameters)**:
  - `limit`: кількість записів на сторінку (за замовчуванням 50, максимум 200).
  - `cursor`: порядковий номер `sequence_num` для пагінації за курсором (*Keyset Pagination*).
  - `from_date`: початкова часова мітка ISO-8601.
  - `to_date`: кінцева часова мітка ISO-8601.

**Відповідь (`200 OK`):**
```json
{
  "account_code": "CUSTOMER_WALLET_USD_104",
  "currency": "USD",
  "opening_balance": 25000,
  "closing_balance": 15000,
  "total_debits": 0,
  "total_credits": 10000,
  "postings": [
    {
      "sequence_num": 1284890,
      "transaction_id": 904128,
      "posted_at": "2026-08-20T16:40:12.381Z",
      "description": "Оплата замовлення №94812",
      "amount": -10000,
      "running_balance": 15000
    }
  ],
  "next_cursor": 1284890,
  "has_more": false
}
```

---

### 4. Сторнування транзакції (Compensating Reversal)

Створює компенсуючу транзакцію з протилежними сумами для повного скасування наслідків попередньої помилкової транзакції.

- **HTTP-метод**: `POST /v1/ledger/transactions/{id}/reversal`
- **Заголовки**:
  - `Idempotency-Key`: рядок UUID v4

**Тіло запиту:**
```json
{
  "reason": "Помилкове подвійне списання за зверненням користувача №ticket-4029"
}
```

**Відповідь (`201 Created`):**
```json
{
  "reversal_transaction_id": 904130,
  "original_transaction_id": 904128,
  "status": "REVERSED",
  "posted_at": "2026-08-20T16:42:00.119Z"
}
```

# ⚙️ Реалізація Transactional Outbox та ідемпотентного споживача

<preknowlist>
- [Transactional Outbox](root:progarch/dh-handover-saga) — гарантія атомарної публікації подій разом із мутацією БД.
- [Ідемпотентність](root:com-protocol/api-idempotency) — збереження інваріантів при повторній обробці однакових повідомлень.
</preknowlist>

Під час проєктування високонавантажених розподілених баз даних та фінансових платформ найнебезпечнішою точкою архітектурної відмови є **подвійний запис (Dual-Write Hazard)**. У монолітних системах минулого розробники звикли спиратися на транзакційний потенціал єдиної бази даних: у межах одного блоку `BEGIN ... COMMIT` можна було оновити кілька таблиць і бути впевненим, що дані зміняться атомарно. Проте у розподіленій архітектурі, де доменні контексти відокремлені, а зв'язок між ними здійснюється через брокери повідомлень (Apache Kafka, RabbitMQ, NATS), ця гарантія повністю зникає.

Типова помилка недосвідченого інженера полягає у спробі виконати послідовний подвійний запис у коді застосунку:

```
1. BEGIN TRANSACTION у базі даних
2. UPDATE wallet_accounts SET balance = balance - 100 WHERE id = 'acc-123'
3. COMMIT TRANSACTION у базі даних
4. kafka_producer.send("FundsTransferred", payload)  <-- ТАЙМАУТ АБО ПАДІННЯ ПРОЦЕСУ ТУТ!
```

Якщо сервіс зазнає аварійного завершення (OOM-killer, падіння живильного кабелю сервера, перезапуск контейнера Kubernetes) між кроком 3 і кроком 4, у базі даних кошти будуть незворотно списані, але брокер повідомлень та решта мікросервісів системи (сервіс замовлень, сповіщень, аналітики) ніколи не дізнаються про цю операцію. Спроба поміняти місцями кроки (спочатку відправити в Kafka, а потім зробити `COMMIT`) створює ще гірший сценарій: брокер отримає подію, сервіс замовлень почне відвантаження товару, а транзакція у базі даних впаде через помилку інваріанту `InsufficientFunds`.

Ця вставка містить вичерпний практичний розбір двох фундаментальних патернів, які надійно усувають проблему подвійного запису та гарантують математичну консистентність між ACID-базою даних та асинхронним брокером: **Transactional Outbox** (атомарне збереження на боці видавця) та **Ідемпотентний споживач з дедуплікацією** (на боці отримувача).

---

## 1. Топологія баз даних та схема атомарної транзакції

Фундаментальна ідея патерну **Transactional Outbox** полягає у відмові від прямої відправки повідомлень у мережевий сокет брокера під час бізнес-транзакції. Замість цього подія записується безпосередньо у базу даних — у спеціально створену службову таблицю `outbox_events`, **у тій самій SQL-транзакції**, що й мутація бізнес-стану гаманця чи замовлення.

Оскільки реляційна база даних гарантує суворі властивості ACID (Atomicity, Consistency, Isolation, Durability), запис події в таблицю Outbox відбудеться тоді й лише тоді, коли буде успішно зафіксовано зміни балансу. Якщо транзакція відкотиться (`ROLLBACK`), подія Outbox зникне разом із невдалими змінами балансу.

Після успішної фіксації транзакції окремий фоновий процес — **Outbox Relayer** — вичитає невідправлені події з таблиці `outbox_events`, відправить їх у Kafka і позначає як оброблені (`processed_at = NOW()`).

```sql
-- Схема таблиці балансів гаманців
CREATE TABLE wallet_accounts (
    account_id VARCHAR(64) PRIMARY KEY,
    balance_cents BIGINT NOT NULL CHECK (balance_cents >= 0),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Схема службової таблиці Transactional Outbox
CREATE TABLE outbox_events (
    event_id VARCHAR(64) PRIMARY KEY,
    aggregate_type VARCHAR(64) NOT NULL,
    aggregate_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- Схема таблиці дедуплікації оброблених повідомлень на боці споживача
CREATE TABLE processed_messages (
    message_id VARCHAR(64) PRIMARY KEY,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Порівняння механізмів вичитання Outbox: Polling vs Change Data Capture (CDC)

Для передачі подій із таблиці `outbox_events` у брокер повідомлень застосовують одну з двох технологічних стратегій:

1. **Запит із певною періодичністю (Periodic Polling Relayer):** Фоновий потік застосунку раз на 100–500 мс виконує SQL-запит `SELECT * FROM outbox_events WHERE processed_at IS NULL ORDER BY created_at ASC LIMIT 100 FOR UPDATE SKIP LOCKED`. Використання конструкції `FOR UPDATE SKIP LOCKED` є критичним: воно дає змогу паралельним потокам релея обробляти різні блоки рядків, не блокуючи один одного.
2. **Захоплення змін даних (Change Data Capture, CDC):** Спеціалізований інструмент (наприклад, Debezium або PGLogical) підключається безпосередньо до журналу попереднього запису СУБД (Write-Ahead Log, WAL). Зміни в таблиці `outbox_events` зчитуються на рівні бінарного логу баз даних і транслюються у Kafka з нульовим додатковим навантаженням на SQL-рушій.

---

## 2. Реалізація атомарного збереження (Transactional Outbox)

Нижче наведено ідіоматичну реалізацію проведення фінансової операції переказу та атомарного створення події Outbox у єдиному ACID-блоці.

:::tabs
```cpp
// C++20: Idiomatic RAII Transaction & Outbox Repository
#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <chrono>

enum class TxError {
    DatabaseConnectionFailed,
    InsufficientFunds,
    OutboxWriteFailed,
    TransactionAborted
};

struct OutboxEvent {
    std::string event_id;
    std::string aggregate_type;
    std::string aggregate_id;
    std::string event_type;
    std::string payload_json;
};

// Мок-адаптер бази даних з підтримкою RAII-транзакцій
class DbConnection {
public:
    void begin_transaction() {
        std::cout << "[DB] BEGIN TRANSACTION;\n";
        in_tx_ = true;
    }
    
    void commit() {
        if (in_tx_) {
            std::cout << "[DB] COMMIT;\n";
            in_tx_ = false;
        }
    }
    
    void rollback() {
        if (in_tx_) {
            std::cout << "[DB] ROLLBACK;\n";
            in_tx_ = false;
        }
    }
    
    bool is_in_transaction() const { return in_tx_; }
    
    bool execute_sql(std::string_view query) {
        std::cout << "[DB EXEC] " << query << "\n";
        return true;
    }

private:
    bool in_tx_{false};
};

// RAII обгортка для безпечного управління транзакцією
class ScopedTransaction {
public:
    explicit ScopedTransaction(DbConnection& db) : db_(db) {
        db_.begin_transaction();
    }
    
    ~ScopedTransaction() {
        if (!committed_ && db_.is_in_transaction()) {
            db_.rollback();
        }
    }
    
    void commit() {
        db_.commit();
        committed_ = true;
    }

    ScopedTransaction(const ScopedTransaction&) = delete;
    ScopedTransaction& operator=(const ScopedTransaction&) = delete;

private:
    DbConnection& db_;
    bool committed_{false};
};

class WalletRepository {
public:
    explicit WalletRepository(DbConnection& db) : db_(db) {}

    std::expected<void, TxError> transfer_and_publish_outbox(
        std::string_view sender_id,
        std::string_view receiver_id,
        int64_t amount_cents,
        const OutboxEvent& event
    ) {
        ScopedTransaction tx(db_);

        // 1. Перевірка інваріанту та оновлення балансу відправника
        std::string update_sender = "UPDATE wallet_accounts SET balance_cents = balance_cents - " +
            std::to_string(amount_cents) + " WHERE account_id = '" + std::string(sender_id) + "'";
        if (!db_.execute_sql(update_sender)) {
            return std::unexpected(TxError::InsufficientFunds);
        }

        // 2. Поповнення балансу отримувача
        std::string update_receiver = "UPDATE wallet_accounts SET balance_cents = balance_cents + " +
            std::to_string(amount_cents) + " WHERE account_id = '" + std::string(receiver_id) + "'";
        if (!db_.execute_sql(update_receiver)) {
            return std::unexpected(TxError::TransactionAborted);
        }

        // 3. Запис події у таблицю outbox_events у цій же транзакції
        std::string insert_outbox = "INSERT INTO outbox_events (event_id, aggregate_type, aggregate_id, event_type, payload_json) VALUES ('" +
            event.event_id + "', '" + event.aggregate_type + "', '" + event.aggregate_id + "', '" +
            event.event_type + "', '" + event.payload_json + "')";
        if (!db_.execute_sql(insert_outbox)) {
            return std::unexpected(TxError::OutboxWriteFailed);
        }

        tx.commit();
        return {};
    }

private:
    DbConnection& db_;
};
```
```c
/* C: Low-level Manual Transaction Handling & Outbox Pattern */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    char event_id[64];
    char aggregate_type[64];
    char aggregate_id[64];
    char event_type[64];
    char payload_json[512];
} outbox_event_t;

typedef struct {
    bool in_transaction;
} db_conn_t;

static bool db_execute(db_conn_t *conn, const char *sql) {
    printf("[C DB EXEC] %s\n", sql);
    return true;
}

int wallet_transfer_with_outbox(
    db_conn_t *conn,
    const char *sender_id,
    const char *receiver_id,
    long long amount_cents,
    const outbox_event_t *event
) {
    if (!conn) return -1;

    /* BEGIN TX */
    conn->in_transaction = true;
    printf("[C DB] BEGIN TRANSACTION;\n");

    /* 1. Deduct balance */
    char sql_buffer[1024];
    snprintf(sql_buffer, sizeof(sql_buffer),
             "UPDATE wallet_accounts SET balance_cents = balance_cents - %lld WHERE account_id = '%s'",
             amount_cents, sender_id);
    if (!db_execute(conn, sql_buffer)) {
        goto rollback;
    }

    /* 2. Credit balance */
    snprintf(sql_buffer, sizeof(sql_buffer),
             "UPDATE wallet_accounts SET balance_cents = balance_cents + %lld WHERE account_id = '%s'",
             amount_cents, receiver_id);
    if (!db_execute(conn, sql_buffer)) {
        goto rollback;
    }

    /* 3. Insert Outbox Event */
    snprintf(sql_buffer, sizeof(sql_buffer),
             "INSERT INTO outbox_events (event_id, aggregate_type, aggregate_id, event_type, payload_json) "
             "VALUES ('%s', '%s', '%s', '%s', '%s')",
             event->event_id, event->aggregate_type, event->aggregate_id,
             event->event_type, event->payload_json);
    if (!db_execute(conn, sql_buffer)) {
        goto rollback;
    }

    /* COMMIT */
    printf("[C DB] COMMIT;\n");
    conn->in_transaction = false;
    return 0;

rollback:
    printf("[C DB] ROLLBACK;\n");
    conn->in_transaction = false;
    return -1;
}
```
```go
// Go: Idiomatic Transactional Outbox Handler
package main

import (
	"context"
	"database/sql"
	"fmt"
)

type OutboxEvent struct {
	EventID       string
	AggregateType string
	AggregateID   string
	EventType     string
	PayloadJSON   string
}

func TransferWithOutbox(ctx context.Context, db *sql.DB, senderID, receiverID string, amountCents int64, event OutboxEvent) error {
	tx, err := db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelSerializable})
	if err != nil {
		return fmt.Errorf("failed to begin tx: %w", err)
	}
	defer tx.Rollback()

	// 1. Списання коштів
	_, err = tx.ExecContext(ctx, "UPDATE wallet_accounts SET balance_cents = balance_cents - $1 WHERE account_id = $2", amountCents, senderID)
	if err != nil {
		return fmt.Errorf("sender debit failed: %w", err)
	}

	// 2. Поповнення коштів
	_, err = tx.ExecContext(ctx, "UPDATE wallet_accounts SET balance_cents = balance_cents + $1 WHERE account_id = $2", receiverID)
	if err != nil {
		return fmt.Errorf("receiver credit failed: %w", err)
	}

	// 3. Запис у outbox_events
	outboxSQL := `INSERT INTO outbox_events (event_id, aggregate_type, aggregate_id, event_type, payload_json) VALUES ($1, $2, $3, $4, $5)`
	_, err = tx.ExecContext(ctx, outboxSQL, event.EventID, event.AggregateType, event.AggregateID, event.EventType, event.PayloadJSON)
	if err != nil {
		return fmt.Errorf("outbox insert failed: %w", err)
	}

	return tx.Commit()
}
```
:::

---

## 3. Гарантії обробки та ідемпотентний споживач (Idempotent Consumer)

Незважаючи на те, що патерн Transactional Outbox вирішує проблему на боці видавця, він не може гарантувати підхід «строго один раз» (Exactly-Once Delivery) на рівні мережі. У розподілених системах брокери повідомлень класу Apache Kafka забезпечують рівень доставки **At-Least-Once** («принаймні один раз»).

Це означає, що за певних умов (мережевий розрив під час відправки підтвердження ACK, перезапуск споживача, перебалансування партицій) той самий пакет подій може бути доставлений споживачу двічі або більше разів. Якщо споживач сліпо повторить фінансову операцію — кошти будуть списані повторно.

Для захисту від повторної обробки дубльованих повідомлень сервіс-споживач застосовує патерн **Ідемпотентного споживача (Idempotent Consumer)** на основі таблиці дедуплікації.

### Алгоритм атомарної дедуплікації повідомлень:

1. Споживач вичитує повідомлення з Kafka і витягує унікальний ідентифікатор `message_id` (або `event_id`).
2. Відкривається локальна SQL-транзакція.
3. Виконується атомарна спроба вставити ідентифікатор у таблицю оброблених повідомлень:
   ```sql
   INSERT INTO processed_messages (message_id) 
   VALUES ('msg-uuid-9901-abcd') 
   ON CONFLICT (message_id) DO NOTHING;
   ```
4. Споживач перевіряє кількість змінених рядків (`rows_affected`). 
   * Якщо `rows_affected == 0` — це означає, що повідомлення з таким ідентифікатором **вже було успішно оброблено раніше**. Транзакція негайно фіксується або відкочується без виконання бізнес-логіки, а offset у Kafka підтверджується.
   * Якщо `rows_affected == 1` — повідомлення обробляється вперше. Виконується мутація бізнес-стану, і транзакція комітиться.

### Стратегія очищення та ліміти таблиці дедуплікації

Таблиця `processed_messages` з часом розростається до мільйонів рядків, що може знизити швидкість вставки за рахунок зростання B-Tree індексу. Для підтримки високої швидкодії застосовують наступні інженерні тактики:

* **Партиціонування за часом (Time-based Partitioning):** Таблиця ділиться на денні або тижневі партиції. Застарілі партиції (старші за 30 днів) миттєво скидаються через `DROP TABLE`, що значно швидше за стандартний `DELETE`.
* **Використання Redis з TTL:** Для високошвидкісних сценаріїв перевірка ключа ідемпотентності виконується в Redis за допомогою комбінованої команди `SET key value NX EX 259200` (де TTL становить 3 дні). Проте в критично важливих фінансових модулях первинна перевірка все одно дублюється в SQL-таблиці для збереження ACID-надійності.
* **Обробка винятків та Dead-Letter Queue (DLQ):** Якщо бізнес-логіка обробки повідомлення завершується кричущою помилкою (неправильний JSON-формат, пошкоджені дані), транзакція з вставкою `message_id` відкочується, а повідомлення перенаправляється в чергу мертвих листів (DLQ) для ручного розбору інженерами.

Використання комбінації Transactional Outbox на боці видавця та ідемпотентної дедуплікації на боці споживача перетворює асинхронну мережу з гарантією At-Least-Once на фактичний семантичний еквівалент **Exactly-Once Processing**, забезпечуючи 100% надійність міжсервісного обміну.

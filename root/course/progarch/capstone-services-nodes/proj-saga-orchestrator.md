# ⚙️ Реалізація Saga-оркестратора та Transactional Outbox

Ця вставка містить вихідний код, інфраструктурні схеми та практичні алгоритми реалізації оркестратора розподілених транзакцій (Saga Orchestrator) і паттерна Transactional Outbox для високонавантаженої платформи еквайрингу PayFlow. Представлений підхід забезпечує гарантії консистентності фінансових операцій без використання блокуючих двофазних комітів (2PC).

---

## 1. Архітектура Saga проти двофазного коміту (2PC)

У розподілених системах забезпечення цілісності даних при виконанні кроків, що охоплюють кілька незалежних баз даних, класично розв'язувалося протоколом двофазного коміту (Two-Phase Commit, 2PC). Однак у високонавантаженій платформі еквайрингу з обсягом 10 000 RPS застосування 2PC створює неприпустимі архітектурні ризики.

### Чому 2PC не масштабується у високопродуктивних мережах:
1. **Синхронне блокування ресурсів (Blocking Protocol):** Під час першої фази (Prepare) координатор блокує рядки в усіх базах даних учасників. Якщо один із вузлів уповільнюється або втрачає мережевий зв'язок, уся система заблокована в очікуванні рішення фази Commit.
2. **Вразливість до точок відмови (Single Point of Failure):** Падіння координатора між фазами Prepare та Commit залишає бази даних учасників у невизначеному заблокованому стані.
3. **Висока латентність (Network RTT):** 2PC вимагає мінімум двох послідовних мережевих обмінів (network round-trips) між координатором та учасниками, що збільшує p99 латентність на 10–50 мс.

Паттерн **Saga** вирішує цю проблему за допомогою серії послідовних локальних ACID-транзакцій. Кожен крок Саги виконує зміни у власній базі даних і публікує тригер для наступного кроку. Якщо один із кроків завершується помилкою, Saga Orchestrator виконує зворотний ланцюг **компенсаційних транзакцій (Compensating Transactions)** для відновлення бізнес-інваріанту.

---

## 2. Схема автомата станів Saga (Charge Saga State Machine)

При обробці транзакції списання коштів сплата проходить крізь суворо визначений автомат станів (State Machine). Оркестратор централізовано управляє переходами між станами та у разі виникнення помилок виконує компенсаційні дії.

```
 [START] ──► PENDING ──► RECORDING_LEDGER ──► COMMITTING_OUTBOX ──► SUCCEEDED
               │                 │                    │
               ▼                 ▼                    ▼
           REJECTED ◄──── COMPENSATING ◄─────────── FAILED
```

### Деталізація фаз виконання Saga:
1. **PENDING:** Початкова перевірка запиту, валідація JWT-токена та атомарне встановлення ключа ідемпотентності у Redis через команду `SET key value NX PX 30000`. Якщо ключ вже існує, запит відхиляється або повертає збережену відповідь.
2. **RECORDING_LEDGER:** Синхронний gRPC-виклик до `Ledger Node` для запису подвійного запису. Якщо `Ledger Node` відповідає `STATUS_COMMITTED`, Saga переходить до наступної фази. Якщо повертається `STATUS_REJECTED_INSUFFICIENT_FUNDS`, Saga переходить у стан `REJECTED`.
3. **COMMITTING_OUTBOX:** Відкриття локальної ACID-транзакції у PostgreSQL: оновлення статусу платежу на `SUCCEEDED` та атомарна вставка події в таблицю `outbox_events`.
4. **COMPENSATING (Компенсаційний маневр):** Якщо `Ledger Node` повертає непередбачену помилку або мережевий таймаут перевищує 500 мс, оркестратор здійснює компенсаційний gRPC-виклик `CancelHold` для зняття резервування та маркує Saga як `FAILED`.

---

## 3. Схема таблиць PostgreSQL для Transactional Outbox

Для атомарного запису фінансового стану та подій у межах однієї бази даних використовується наступна DDL-структура:

```sql
-- Таблиця станів платежів
CREATE TABLE charges (
    id VARCHAR(64) PRIMARY KEY,
    merchant_id VARCHAR(64) NOT NULL,
    idempotency_key VARCHAR(128) NOT NULL,
    amount_cents BIGINT NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status VARCHAR(32) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uk_merchant_idempotency UNIQUE (merchant_id, idempotency_key)
);

-- Таблиця Transactional Outbox
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Індекс для швидкої вибірки необроблених подій релей-процесором
CREATE INDEX idx_outbox_unprocessed ON outbox_events (created_at) WHERE processed = FALSE;
```

### Фізичні механізми вибірки та MVCC у PostgreSQL
Використання часткового індексу `WHERE processed = FALSE` гарантує, що розмір індексу залишається крихітним (лише невідправлені події), навіть коли загальна таблиця `outbox_events` містить мільйони історичних записів. Завдяки механізму мультиверсійного контролю конкурентності (MVCC) вставка нових рядків `INSERT INTO outbox_events` не блокує параллельне читання вибірки `SELECT ... FOR UPDATE SKIP LOCKED`процесом-релеєм.

---

## 4. Практична реалізація Saga Worker та Outbox Processor

Нижче наведено вихідний код реалізації оркестратора саги та обробника таблиці Outbox мовами Go та C++.

:::tabs
```go
package saga

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"time"
)

type SagaStatus string

const (
	StatusPending     SagaStatus = "PENDING"
	StatusSucceeded   SagaStatus = "SUCCEEDED"
	StatusFailed      SagaStatus = "FAILED"
	StatusCompensated SagaStatus = "COMPENSATED"
)

// ChargeSagaState описує поточний стан транзакції саги
type ChargeSagaState struct {
	ChargeID       string     `json:"charge_id"`
	MerchantID     string     `json:"merchant_id"`
	IdempotencyKey string     `json:"idempotency_key"`
	AmountCents    int64      `json:"amount_cents"`
	Currency       string     `json:"currency"`
	Status         SagaStatus `json:"status"`
}

type OutboxEvent struct {
	ID        string    `json:"id"`
	EventType string    `json:"event_type"`
	Payload   []byte    `json:"payload"`
	CreatedAt time.Time `json:"created_at"`
}

type PaymentSagaOrchestrator struct {
	db *sql.DB
}

func NewOrchestrator(db *sql.DB) *PaymentSagaOrchestrator {
	return &PaymentSagaOrchestrator{db: db}
}

// CommitSagaWithOutbox виконує атомарну локальну ACID транзакцію
func (o *PaymentSagaOrchestrator) CommitSagaWithOutbox(ctx context.Context, saga *ChargeSagaState) error {
	// Встановлюємо таймаут транзакції на рівні контексту (2 секунди)
	ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
	defer cancel()

	tx, err := o.db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelReadCommitted})
	if err != nil {
		return fmt.Errorf("failed to begin database transaction: %w", err)
	}
	// Захисний механізм: у разі паніки або помилки робимо Rollback
	defer tx.Rollback()

	// 1. Збереження або оновлення стану платежу (Upsert)
	sagaQuery := `
		INSERT INTO charges (id, merchant_id, idempotency_key, amount_cents, currency, status, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, NOW())
		ON CONFLICT (merchant_id, idempotency_key) 
		DO UPDATE SET status = EXCLUDED.status, updated_at = NOW()
	`
	_, err = tx.ExecContext(ctx, sagaQuery, saga.ChargeID, saga.MerchantID, saga.IdempotencyKey, saga.AmountCents, saga.Currency, saga.Status)
	if err != nil {
		return fmt.Errorf("failed to record charge state: %w", err)
	}

	// 2. Серіалізація об'єкта саги у JSON для Outbox
	eventPayload, err := json.Marshal(saga)
	if err != nil {
		return fmt.Errorf("failed to marshal outbox event payload: %w", err)
	}

	// 3. Запис події у таблицю outbox_events у межах ТІЄЇ Ж транзакції
	outboxQuery := `
		INSERT INTO outbox_events (id, event_type, payload, created_at, processed)
		VALUES (gen_random_uuid(), $1, $2, NOW(), false)
	`
	eventType := "charge.succeeded"
	if saga.Status == StatusFailed {
		eventType = "charge.failed"
	}

	_, err = tx.ExecContext(ctx, outboxQuery, eventType, eventPayload)
	if err != nil {
		return fmt.Errorf("failed to insert outbox event record: %w", err)
	}

	// 4. Успішна фіксація транзакції
	if err := tx.Commit(); err != nil {
		return fmt.Errorf("failed to commit saga transaction: %w", err)
	}

	return nil
}

// ProcessOutboxBatch зчитує невідправлені події з підтримкою паралельного блокування FOR UPDATE SKIP LOCKED
func (o *PaymentSagaOrchestrator) ProcessOutboxBatch(ctx context.Context, batchSize int) ([]OutboxEvent, error) {
	tx, err := o.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, err
	}
	defer tx.Rollback()

	// FOR UPDATE SKIP LOCKED дозволяє декільком воркерам читати таблицю outbox без взаємного блокування
	query := `
		SELECT id, event_type, payload, created_at
		FROM outbox_events
		WHERE processed = FALSE
		ORDER BY created_at ASC
		LIMIT $1
		FOR UPDATE SKIP LOCKED
	`
	rows, err := tx.QueryContext(ctx, query, batchSize)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var events []OutboxEvent
	var eventIDs []string

	for rows.Next() {
		var evt OutboxEvent
		if err := rows.Scan(&evt.ID, &evt.EventType, &evt.Payload, &evt.CreatedAt); err != nil {
			return nil, err
		}
		events = append(events, evt)
		eventIDs = append(eventIDs, evt.ID)
	}

	// Позначаємо вичитані події як оброблені
	if len(eventIDs) > 0 {
		updateQuery := `UPDATE outbox_events SET processed = TRUE, processed_at = NOW() WHERE id = ANY($1)`
		if _, err := tx.ExecContext(ctx, updateQuery, eventIDs); err != nil {
			return nil, err
		}
	}

	if err := tx.Commit(); err != nil {
		return nil, err
	}

	log.Printf("[OUTBOX] Successfully fetched and marked %d events", len(events))
	return events, nil
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <chrono>
#include <expected>
#include <stdexcept>

namespace payflow::saga {

enum class SagaStatus {
    Pending,
    Succeeded,
    Failed,
    Compensated
};

struct ChargeSagaState {
    std::string charge_id;
    std::string merchant_id;
    std::string idempotency_key;
    int64_t amount_cents;
    std::string currency;
    SagaStatus status;
};

struct OutboxRecord {
    std::string event_id;
    std::string event_type;
    std::string payload_json;
    std::chrono::system_clock::time_point created_at;
};

// RAII обгортка бази даних для гарантії атомарного завершення транзакції
class DbTransaction {
public:
    explicit DbTransaction() : committed_(false) {
        std::cout << "[DB] BEGIN LOCAL ACID TRANSACTION\n";
    }
    
    ~DbTransaction() {
        if (!committed_) {
            std::cout << "[DB] ROLLBACK TRANSACTION (RAII Safe Guard)\n";
        }
    }

    void execute(const std::string& query) {
        std::cout << "[DB EXEC] " << query << "\n";
    }

    void commit() {
        std::cout << "[DB] COMMIT TRANSACTION SUCCESSFUL\n";
        committed_ = true;
    }

    // Заборона копіювання транзакційного об'єкта
    DbTransaction(const DbTransaction&) = delete;
    DbTransaction& operator=(const DbTransaction&) = delete;

private:
    bool committed_;
};

class PaymentSagaOrchestrator {
public:
    // Повертає std::expected (C++23) для явною обробки помилок без винятків
    std::expected<void, std::string> commit_saga_with_outbox(const ChargeSagaState& saga) {
        try {
            DbTransaction tx;

            // 1. Запис стану саги
            std::string status_str = (saga.status == SagaStatus::Succeeded) ? "SUCCEEDED" : "FAILED";
            std::string charge_sql = "INSERT INTO charges (id, merchant_id, idempotency_key, amount_cents, status) "
                                     "VALUES ('" + saga.charge_id + "', '" + saga.merchant_id + "', '" + 
                                     saga.idempotency_key + "', " + std::to_string(saga.amount_cents) + ", '" + status_str + "')";
            tx.execute(charge_sql);

            // 2. Атомарний запис у таблицю outbox
            std::string event_type = (saga.status == SagaStatus::Succeeded) ? "charge.succeeded" : "charge.failed";
            std::string outbox_sql = "INSERT INTO outbox_events (event_type, payload) VALUES ('" + 
                                     event_type + "', '{\"charge_id\":\"" + saga.charge_id + "\"}')";
            tx.execute(outbox_sql);

            // 3. Фіксація змін
            tx.commit();
            return {};
        } catch (const std::exception& e) {
            return std::unexpected(std::string("Database ACID failure: ") + e.what());
        }
    }
};

} // namespace payflow::saga
```
:::

---

## 5. Детальний аналіз реалізації та обробки помилок

### 1. Механізм RAII у C++ реалізації
У C++ коді використано паттерн RAII (Resource Acquisition Is Initialization — від латинського *initium* — початок) через клас `DbTransaction`. Якщо під час виконання SQL-запитів виникає виняток (наприклад, втрачено з'єднання з PostgreSQL або виник deadlock), деструктор `~DbTransaction()` автоматично викликає `ROLLBACK`, якщо транзакцію не було явно зафіксовано через `commit()`. Це гарантує відсутність завислих транзакцій у базі даних навіть при катастрофічних збоях у пам'яті.

### 2. Конкурентна вибірка через `FOR UPDATE SKIP LOCKED`
У Go реалізації метод `ProcessOutboxBatch` використовує конструкцію `FOR UPDATE SKIP LOCKED`. Це критично важливо при розгортанні кластера з 20 воркерів Outbox Processor. Без `SKIP LOCKED` кожен воркер намагався б заблокувати перші 100 рядків таблиці `outbox_events`, що викликало б масові блокування та зниження пропускної здатності. З `SKIP LOCKED` кожен воркер миттєво пропускає вже заблоковані іншими воркерами рядки та обробляє власну порцію.

### 3. Захист від отруйних повідомлень (Poison Messages) та DLQ
Якщо сервер торговця повертає помилку або не відповідає на Webhook, подія повертається в чергу з экспоненційним запізненням. Якщо подія не може бути доставлена після 10 спроб (протягом 24 годин), вона переміщується в Dead Letter Queue (DLQ) — окрему таблицю або топік `payflow.webhooks.dlq`. Це запобігає блокуванню асинхронної черги та дозволяє інженерам підтримки проаналізувати причину відмови.

### 4. Вікно дедуплікації споживачів (Deduplication Window)
Оскільки гарантія доставки At-Least-Once допускає повторну відправку подій при мережевих збоях, кожен споживач у `Webhook Worker Pool` перевіряє унікальний ключ `event_id` у Redis із TTL 24 години:

```go
func (w *WebhookWorker) ProcessEvent(ctx context.Context, evt OutboxEvent) error {
	key := fmt.Sprintf("dedup:event:%s", evt.ID)
	ok, err := w.redisClient.SetNX(ctx, key, "1", 24*time.Hour).Result()
	if err != nil {
		return fmt.Errorf("redis dedup check failed: %w", err)
	}
	if !ok {
		log.Printf("[DEDUP] Skipping duplicate event %s", evt.ID)
		return nil // Дублікат пропущено
	}

	return w.sendWebhookHTTP(ctx, evt)
}
```

### 5. Метрики та спостережність (Observability & Metrics)
Для моніторингу роботи Saga Orchestrator у систему вбудовано наступні метрики Prometheus:
* `payflow_saga_execution_duration_seconds` (histogram): Час виконання повної Saga за перцентилями p50, p95, p99.
* `payflow_outbox_unprocessed_events_count` (gauge): Кількість накопичених невідправлених подій у таблиці `outbox_events` (сигнал про лаг процесора).
* `payflow_webhook_retry_attempts_total` (counter): Лічильник повторних спроб доставки вебхуків у розрізі методів та кодів помилок.

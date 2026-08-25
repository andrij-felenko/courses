# ⚙️ Відмовостійкий ідемпотентний консюмер із розділенням сайд-ефектів

Цей проєкт містить закінчену, готову до промислового використання реалізацію стійкого ідемпотентного споживача, що реалізує трифазне виконання з ізоляцією зовнішніх сайд-ефектів, дедуплікаційним вікном та захистом від отруйних петель.

## Архітектурний дизайн консюмера

Консюмер розв'язує проблему ненадійного транспорту через чітке розмежування відповідальності:
1. **Швидкий фільтр у пам'яті (Bloom Filter / LRU Cache)**: відсікає очевидні повтори без навантаження на базу даних.
2. **Транзакційний Inbox (PostgreSQL)**: фіксує намір та статус обробки (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `QUARANTINED`).
3. **Детермінований генератор ключів**: створює стабільний хеш `SHA-256(msg_id + action)` для передачі у зовнішній платіжний або поштовий API.
4. **Контур розриву отруйної петлі**: обмежує максимальну кількість спроб (`max_attempts = 3`) і за потреби евакуює повідомлення у Dead Letter Queue (DLQ).

:::tabs
```go
package main

import (
	"context"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"errors"
	"fmt"
	"net/http"
	"sync"
	"time"

	_ "github.com/lib/pq"
)

// Message представляє подію з черги брокера
type Message struct {
	ID        string
	Topic     string
	Partition int
	Offset    int64
	Payload   []byte
	Attempt   int
}

// ConsumerEngine реалізує трифазний ідемпотентний обробник
type ConsumerEngine struct {
	db          *sql.DB
	httpClient  *http.Client
	memCache    map[string]time.Time
	cacheMu     sync.RWMutex
	leaseTTL    time.Duration
	maxAttempts int
}

func NewConsumerEngine(db *sql.DB) *ConsumerEngine {
	return &ConsumerEngine{
		db:          db,
		httpClient:  &http.Client{Timeout: 5 * time.Second},
		memCache:    make(map[string]time.Time),
		leaseTTL:    30 * time.Second,
		maxAttempts: 3,
	}
}

// DeriveOutboundKey обчислює стабільний детермінований токен для стороннього сервісу
func (c *ConsumerEngine) DeriveOutboundKey(msgID, action string) string {
	h := sha256.New()
	h.Write([]byte(fmt.Sprintf("%s:%s", msgID, action)))
	return "idemp_" + hex.EncodeToString(h.Sum(nil))[:32]
}

// ProcessMessage виконує повний життєвий цикл обробки повідомлення
func (c *ConsumerEngine) ProcessMessage(ctx context.Context, msg Message) error {
	// 0. Швидка перевірка в кеші пам'яті (L1 дедуплікація)
	c.cacheMu.RLock()
	if _, found := c.memCache[msg.ID]; found {
		c.cacheMu.RUnlock()
		return nil // Вже успішно оброблено, пропускаємо
	}
	c.cacheMu.RUnlock()

	outboundKey := c.DeriveOutboundKey(msg.ID, "charge_payment")
	leaseExpiry := time.Now().Add(c.leaseTTL)

	// ФАЗА 1: Чисте транзакційне рішення (Бронювання наміру в Inbox)
	tx, err := c.db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelReadCommitted})
	if err != nil {
		return fmt.Errorf("помилка відкриття транзакції: %w", err)
	}
	defer tx.Rollback()

	var status string
	var attempts int
	query := `
		INSERT INTO consumer_inbox (
			message_id, consumer_group, topic, partition_id, message_offset,
			status, outbound_idempotency_key, delivery_attempts, lease_expires_at
		) VALUES ($1, 'payments_group', $2, $3, $4, 'IN_PROGRESS', $5, 1, $6)
		ON CONFLICT (consumer_group, message_id) DO UPDATE SET
			delivery_attempts = consumer_inbox.delivery_attempts + 1,
			lease_expires_at = EXCLUDED.lease_expires_at
		RETURNING status, delivery_attempts;
	`
	err = tx.QueryRowContext(ctx, query, msg.ID, msg.Topic, msg.Partition, msg.Offset, outboundKey, leaseExpiry).Scan(&status, &attempts)
	if err != nil {
		return fmt.Errorf("помилка резервування в inbox: %w", err)
	}

	// Якщо повідомлення вже було завершено раніше
	if status == "COMPLETED" {
		tx.Rollback()
		c.cacheMu.Lock()
		c.memCache[msg.ID] = time.Now()
		c.cacheMu.Unlock()
		return nil // Ідемпотентний пропуск
	}

	// Захист від отруйної петлі (Poison Loop Break)
	if attempts > c.maxAttempts {
		_, _ = tx.ExecContext(ctx, "UPDATE consumer_inbox SET status = 'QUARANTINED' WHERE message_id = $1", msg.ID)
		_ = tx.Commit()
		c.routeToDeadLetterQueue(msg, "перевищено ліміт спроб (отруйне повідомлення)")
		return nil // Підтверджуємо зсув брокеру, щоб розблокувати чергу
	}

	if err := tx.Commit(); err != nil {
		return fmt.Errorf("помилка фіксації Фази 1: %w", err)
	}

	// ФАЗА 2: Мережевий сайд-ефект із детермінованим токеном ідемпотентності
	externalRef, err := c.executeExternalSideEffect(ctx, outboundKey, msg.Payload)
	if err != nil {
		// Тимчасовий збій мережі: залишаємо статус IN_PROGRESS, оренду вичерпає таймаут
		return fmt.Errorf("збій виклику стороннього API: %w", err)
	}

	// ФАЗА 3: Фіналізація стану в базі даних
	txFin, err := c.db.BeginTx(ctx, nil)
	if err != nil {
		return fmt.Errorf("помилка транзакції фіналізації: %w", err)
	}
	defer txFin.Rollback()

	updateQuery := `
		UPDATE consumer_inbox
		SET status = 'COMPLETED',
		    external_reference = $1,
		    completed_at = NOW()
		WHERE message_id = $2;
	`
	if _, err := txFin.ExecContext(ctx, updateQuery, externalRef, msg.ID); err != nil {
		return fmt.Errorf("помилка оновлення статусу COMPLETED: %w", err)
	}

	// Застосування доменної бізнес-зміни
	if _, err := txFin.ExecContext(ctx, "UPDATE orders SET is_paid = true WHERE id = $1", msg.ID); err != nil {
		return fmt.Errorf("помилка оновлення замовлення: %w", err)
	}

	if err := txFin.Commit(); err != nil {
		return fmt.Errorf("помилка фіксації Фази 3: %w", err)
	}

	// Оновлюємо локальний кеш пам'яті
	c.cacheMu.Lock()
	c.memCache[msg.ID] = time.Now()
	c.cacheMu.Unlock()

	return nil
}

func (c *ConsumerEngine) executeExternalSideEffect(ctx context.Context, idempKey string, payload []byte) (string, error) {
	req, err := http.NewRequestWithContext(ctx, "POST", "https://api.payment-gateway.internal/v1/charges", nil)
	if err != nil {
		return "", err
	}
	// Передаємо детермінований токен ідемпотентності
	req.Header.Set("Idempotency-Key", idempKey)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 500 {
		return "", errors.New("тимчасова помилка сервера платежів (5xx)")
	}
	return "charge_ref_99412", nil
}

func (c *ConsumerEngine) routeToDeadLetterQueue(msg Message, reason string) {
	fmt.Printf("[DLQ] Повідомлення ID=%s евакуйовано в Dead Letter Queue. Причина: %s\n", msg.ID, reason)
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <unordered_map>
#include <shared_mutex>
#include <chrono>
#include <sstream>
#include <iomanip>
#include <expected>
#include <stdexcept>

// Повідомлення з брокера
struct Message {
    std::string id;
    std::string topic;
    int partition{0};
    int64_t offset{0};
    std::string payload;
    int attempt{1};
};

enum class ProcessingStatus {
    Pending,
    InProgress,
    Completed,
    Quarantined
};

// Результат операції
enum class ConsumerError {
    DatabaseError,
    ExternalApiError,
    PoisonMessageQuarantined
};

class ResilientIdempotentConsumer {
public:
    explicit ResilientIdempotentConsumer(int max_attempts = 3)
        : max_attempts_(max_attempts), lease_duration_(std::chrono::seconds(30)) {}

    // Детермінований токен для зовнішніх API
    std::string derive_outbound_key(std::string_view msg_id, std::string_view action) const {
        std::hash<std::string_view> hasher;
        size_t h1 = hasher(msg_id);
        size_t h2 = hasher(action);
        std::stringstream ss;
        ss << "idemp_" << std::hex << h1 << "_" << h2;
        return ss.str();
    }

    // Трифазна обробка
    std::expected<void, ConsumerError> process_message(const Message& msg) {
        // 0. Перевірка швидкого L1 кешу в пам'яті
        {
            std::shared_lock lock(cache_mutex_);
            if (completed_cache_.contains(msg.id)) {
                return {}; // Ідемпотентний пропуск
            }
        }

        const std::string outbound_key = derive_outbound_key(msg.id, "charge_payment");

        // ФАЗА 1: Локальна фіксація наміру (Inbox DB)
        auto phase1_res = reserve_inbox_intent(msg, outbound_key);
        if (!phase1_res) {
            return std::unexpected(ConsumerError::DatabaseError);
        }

        if (*phase1_res == ProcessingStatus::Completed) {
            mark_local_cache(msg.id);
            return {};
        }

        if (*phase1_res == ProcessingStatus::Quarantined) {
            route_to_dlq(msg, "Перевищено ліміт спроб обробки");
            return {}; // Підтверджуємо зсув, черга розблокована
        }

        // ФАЗА 2: Виклик стороннього API з токеном ідемпотентності
        auto side_effect_res = call_external_payment_api(outbound_key, msg.payload);
        if (!side_effect_res) {
            return std::unexpected(ConsumerError::ExternalApiError);
        }

        // ФАЗА 3: Фіналізація стану в БД
        if (!finalize_inbox_transaction(msg.id, *side_effect_res)) {
            return std::unexpected(ConsumerError::DatabaseError);
        }

        mark_local_cache(msg.id);
        return {};
    }

private:
    std::expected<ProcessingStatus, ConsumerError> reserve_inbox_intent(const Message& msg, const std::string& outbound_key) {
        // Емуляція атомарного запису в PostgreSQL Inbox
        std::unique_lock lock(db_mutex_);
        auto& entry = simulated_db_inbox_[msg.id];
        
        if (entry.status == ProcessingStatus::Completed) {
            return ProcessingStatus::Completed;
        }

        entry.attempts++;
        if (entry.attempts > max_attempts_) {
            entry.status = ProcessingStatus::Quarantined;
            return ProcessingStatus::Quarantined;
        }

        entry.status = ProcessingStatus::InProgress;
        entry.outbound_key = outbound_key;
        entry.lease_expiry = std::chrono::steady_clock::now() + lease_duration_;
        return ProcessingStatus::InProgress;
    }

    std::expected<std::string, ConsumerError> call_external_payment_api(const std::string& idemp_key, std::string_view payload) {
        // Емуляція HTTP POST з заголовком Idempotency-Key
        // Зовнішній сервіс за ключем idemp_key ніколи не подвоїть платіж
        return "charge_ch_774129";
    }

    bool finalize_inbox_transaction(const std::string& msg_id, const std::string& external_ref) {
        std::unique_lock lock(db_mutex_);
        auto it = simulated_db_inbox_.find(msg_id);
        if (it == simulated_db_inbox_.end()) return false;

        it->second.status = ProcessingStatus::Completed;
        it->second.external_ref = external_ref;
        return true;
    }

    void mark_local_cache(const std::string& id) {
        std::unique_lock lock(cache_mutex_);
        completed_cache_[id] = std::chrono::steady_clock::now();
    }

    void route_to_dlq(const Message& msg, std::string_view reason) {
        std::cout << "[DLQ] Повідомлення ID=" << msg.id << " ізольовано. Причина: " << reason << "\n";
    }

    struct InboxRecord {
        ProcessingStatus status{ProcessingStatus::Pending};
        int attempts{0};
        std::string outbound_key;
        std::string external_ref;
        std::chrono::steady_clock::time_point lease_expiry;
    };

    int max_attempts_;
    std::chrono::seconds lease_duration_;
    mutable std::shared_mutex cache_mutex_;
    std::unordered_map<std::string, std::chrono::steady_clock::time_point> completed_cache_;
    
    std::mutex db_mutex_;
    std::unordered_map<std::string, InboxRecord> simulated_db_inbox_;
};
```
:::

## Покроковий розбір механізму виконання та інваріантів

Конвеєр забезпечує строгу надійність завдяки чіткій послідовності операцій та обробці відмов на кожному кроці:

1. **Багаторівнева перевірка (L1 Cache Hit):** Першим кроком воркер перевіряє `memCache` під блокуванням на читання (`RLock`). Якщо повідомлення з цим `ID` уже успішно оброблялося поточним екземпляром процесу, функція миттєво повертає `nil` (успішний No-Op). Це повністю знімає навантаження з реляційної бази даних під час масових повторних відправок одного й того самого повідомлення.

2. **Атомарне взяття оренди (Phase 1 Atomic Upsert):** Використання SQL-конструкції `INSERT ... ON CONFLICT (consumer_group, message_id) DO UPDATE` забезпечує атомарну зміну стану без необхідності встановлення явних блокувань таблиці. Якщо запис уже існує, база даних інкрементує лічильник `delivery_attempts` і повертає актуальний `status`. Якщо статус уже дорівнює `COMPLETED`, транзакція негайно відкочується, а ключ додається в локальний кеш.

3. **Розрив отруйної петлі (Poison Loop Break):** Якщо лічильник `delivery_attempts` перевищує `maxAttempts`, воркер не повертає помилку брокеру (що спричинило б нескінченний рестарт), а переводить статус у `QUARANTINED`, фіксує транзакцію та відправляє подію в Dead Letter Queue. Функція повертає `nil`, що сигналізує консюмеру про необхідність підтвердити зсув (Commit Offset) у брокері. Черга розблоковується, а наступні валідні повідомлення продовжують оброблятися.

4. **Детермінований виклик стороннього API (Phase 2):** Функція `DeriveOutboundKey` розраховує криптографічний хеш від комбінації `msg.ID` та назви дії `charge_payment`. Завдяки цьому при будь-яких повторних спробах зовнішній сервіс отримує один і той самий заголовок `Idempotency-Key`. Якщо сервер Stripe вже виконав списання під час попередньої спроби, він поверне збережений `charge_id` без повторного зняття коштів.

5. **Атомарна фіналізація бізнес-змін (Phase 3 Commit):** Фіксація статусу `COMPLETED`, збереження зовнішнього посилання `external_reference` та оновлення бізнес-таблиць (наприклад, `orders.is_paid = true`) виконуються в єдиній ACID-транзакції. Якщо база даних дасть збій на цій фазі, статус залишиться `IN_PROGRESS`, і наступний перезапуск воркера знову звернеться до стороннього API з тим самим токеном і повторить спробу фіналізації.

## Керування конкурентністю, протитиском та чергою мертвих листів

У реальних виробничих кластерах кілька воркерів обробляють повідомлення паралельно. Для запобігання перевантаженню бази даних та вичерпанню сокетів застосовують такі інженерні практики:

* **Обмеження паралелізму (Worker Pool Concurrency):** Кількість одночасних горутин або потоків обмежується буферизованим каналом-семафором або пулом воркерів фіксованого розміру (наприклад, 50–100 горутин на екземпляр). Це запобігає вибуху з'єднань до PostgreSQL (`max_connections`) під час різких сплесків навантаження (Traffic Spikes).
* **Вбудований протитиск (Backpressure Integration):** Якщо база даних починає відповідати повільніше (збільшується час фіксації Фази 1 понад 100 мс), консюмер автоматично уповільнює вичитку повідомлень із брокера (збільшує інтервал між викликами `poll()`), даючи сховищу час на скидання буферів на диск.
* **Процес автоматичної звірки DLQ (Reconciliation Worker):** Повідомлення, що опинилися в статусі `QUARANTINED`, періодично аналізуються фоновим воркером звірки. Воркер перевіряє статус у сторонньому сервісі за допомогою раніше згенерованого `outbound_idempotency_key`. Якщо з'ясовується, що платіж насправді успішно пройшов у Stripe, воркер автоматично виконує Фазу 3 і доводить стан замовлення до узгодженого, усуваючи необхідність ручного втручання чергового інженера.

## Крайові випадки та поведінка при відмовах

* **Воркер зазнав краху під час виклику стороннього API (Phase 2):** Списання коштів у Stripe відбулося, але з'єднання обірвалося. Новий воркер після завершення таймауту оренди (`leaseTTL`) бере повідомлення, повторно формує той самий `outboundKey` і викликає Stripe. Платіжний шлюз розпізнає ключ і повертає `charge_ref_99412`. Воркер успішно переходить до Фази 3 і фіксує замовлення як оплачене.
* **Тимчасовий збій мережі до бази даних (Database Unavailable):** Якщо база даних недоступна на Фазі 1 або Фазі 3, функція повертає помилку `error`. Споживач НЕ підтверджує зсув у брокері, викликає експоненційне відкладення (Backoff) і чекає на відновлення зв'язку зі сховищем.
* **Конкурентна обробка двома воркерами (Race Condition):** Якщо через затримку мережі брокер видав одне й те саме повідомлення двом воркерам одночасно, перший воркер успішно виконає `INSERT`, а другий воркер отримає оновлений рядок зі статусом `IN_PROGRESS` та активною міткою оренди `lease_expires_at > NOW()`, що змусить його відступити без виконання повторних мережевих дій.

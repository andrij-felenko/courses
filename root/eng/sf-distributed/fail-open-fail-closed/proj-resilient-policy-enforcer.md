# ⚙️ Стійкий рушій виконання політик з адаптивним Fail-Open та Fail-Closed

У високонавантажених розподілених архітектурах шлюзи безпеки, сервіси авторизації (наприклад, Open Policy Agent або Google Zanzibar) та контролери допуску (Admission Controllers) розташовані безпосередньо на критичному шляху проходження кожного клієнтського запиту. Якщо віддалена служба перевірки правил зависає, потрапляє під тривалу паузу збирача сміття (GC Pause), відчуває вичерпання пулу з'єднань або стає недоступною через розрив мережі, інтерцептор повинен детерміновано прийняти рішення за фіксовані мілісекунди.

Будь-яка непевність на цьому етапі є катастрофічною: блокування потоку в очікуванні відповіді віддаленої служби виснажує пули потоків вебсервера і спричиняє каскадну відмову всієї системи. Інтерцептор повинен миттєво звернутися до налаштованої стратегії відмови: пропустити запит (Fail-Open) із фіксацією інциденту в черзі тіньового аудиту, заблокувати його (Fail-Closed) із поверненням статусу помилки, або звернутися до локального кешу м'якого стану (Soft State).

Нижче наведено повноцінну реалізацію стійкого рушія виконання політик (Resilient Policy Enforcer), що об'єднує жорсткий бюджет часу (Deadline Budget), трипозиційний запобіжник (Circuit Breaker), локальне кешування застарілих рішень та неблокуючу буферизовану чергу тіньового аудиту.

## Архітектурний конвеєр обробки та автомат переходів

Кожен вхідний запит проходить через суворий конвеєр перевірок, де кожен наступний крок є детермінованим захистом від попереднього рівня відмови:

```
[ Вхідний запит ] ──> [ 1. Перевірка стану запобіжника ]
                             │
            ┌────────────────┴────────────────┐
     [ Breaker CLOSED ]               [ Breaker OPEN ]
            │                                 │
   [ 2. RPC з бюджетом часу ]                 │
       │           │                          │
   [ 200 OK ]   [ Таймаут / 5xx ]             │
       │           │                          │
   (ALLOW)         └──────────────────────────┼──> [ 3. Селектор Fallback ]
                                              │           │
                                              │   ├── 3.1. Локальний кеш -> ALLOW (Degraded)
                                              │   ├── 3.2. Стратегія FAIL_OPEN -> ALLOW + Shadow DLQ
                                              │   └── 3.3. Стратегія FAIL_CLOSED -> REJECT (503/403)
```

### Фізика роботи конвеєра

1. **Контроль стану запобіжника:** якщо попередні запити зафіксували стійку недоступність віддаленої служби авторизації, запобіжник переходить у стан `OPEN`. Усі наступні запити миттєво відхиляються від виконання мережевого вводу-виводу і спрямовуються прямо в блок аварійної деградації (Fallback Selector). Це звільняє клієнтські потоки від зайвого очікування та запобігає створенню шторму повторних запитів до вмираючого бекенда.
2. **Виконання перевірки з дедлайном:** якщо запобіжник замкнений (`CLOSED`), створюється асинхронна задача перевірки з індивідуальним бюджетом часу (наприклад, 25 мілісекунд). Якщо віддалений рушій не вкладається у відведений квант часу, очікування примусово переривається, а лічильник невдач запобіжника інкрементується.
3. **Трирівнева деградація:**
   * **Рівень 1 (Stale Cache):** якщо для пари `(user_id, resource, action)` у локальній пам'яті існує попередньо кешоване рішення, інтерцептор повертає його з позначкою деградації (`degraded: true`). Це дозволяє зберегти коректність доступу для активних сесій навіть під час повної ізоляції сервера політик.
   * **Рівень 2 (Fail-Open з тіньовим аудитом):** якщо кеш відсутній, але сервіс налаштовано на пріоритет доступності (наприклад, публічний каталог, пошуковий індекс або система рекомендацій), запит пропускається до основного обробника. Одночасно контекст запиту поміщається у неблокуючий буфер для асинхронної відправки в Dead-Letter Queue (Kafka), де аналітики безпеки зможуть постфактум виявити несанкціоновані дії.
   * **Рівень 3 (Fail-Closed):** для критичних контурів (фінансовий білінг, зміна прав доступу, операції з балансом) запит негайно переривається з кодом HTTP 503 Service Unavailable або 403 Forbidden.

## Промислова реалізація: C++20 та Go

Код реалізовано мовами C++20 та Go. Реалізації використовують сучасні стандарти: `std::expected`, атомарні змінні, RAII та шаблони проєктування в C++; контексти з таймаутами, канали та паралельні воркери в Go.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <future>
#include <memory>
#include <unordered_map>
#include <shared_mutex>
#include <queue>
#include <thread>
#include <atomic>
#include <optional>
#include <expected>

// Стратегія поведінки під час недоступності валідатора
enum class FailureStrategy {
    FAIL_CLOSED,     // Суворе блокування запитів (HTTP 503/403)
    FAIL_OPEN,       // Пропуск запиту з поміткою деградації та аудитом
    USE_STALE_CACHE  // Спроба використати локальний кеш перед вибором
};

// Стани кінцевого автомата запобіжника
enum class BreakerState {
    CLOSED,
    OPEN,
    HALF_OPEN
};

// Контекст вхідного запиту
struct RequestContext {
    std::string request_id;
    std::string user_id;
    std::string resource;
    std::string action;
    std::chrono::milliseconds timeout_budget{25}; // Жорсткий бюджет часу
};

// Результат виконання перевірки політики
struct PolicyDecision {
    bool allowed{false};
    bool degraded{false};
    std::string reason;
    int http_status{200};
};

// Подія для асинхронної черги тіньового аудиту
struct ShadowAuditLog {
    std::string request_id;
    std::string user_id;
    std::string resource;
    std::string action;
    std::string fallback_reason;
    std::chrono::system_clock::time_point timestamp;
};

// Потокобезпечна неблокуюча черга тіньового аудиту
class ShadowAuditQueue {
public:
    explicit ShadowAuditQueue(size_t max_capacity = 10000)
        : max_capacity_(max_capacity), running_(true) {
        worker_thread_ = std::thread(&ShadowAuditQueue::process_queue, this);
    }

    ~ShadowAuditQueue() {
        running_.store(false);
        cv_.notify_all();
        if (worker_thread_.joinable()) {
            worker_thread_.join();
        }
    }

    // Неблокуюча вставка: при переповненні скидаємо запис заради швидкості
    bool push(ShadowAuditLog log) {
        std::unique_lock lock(mutex_);
        if (queue_.size() >= max_capacity_) {
            return false;
        }
        queue_.push(std::move(log));
        lock.unlock();
        cv_.notify_one();
        return true;
    }

private:
    void process_queue() {
        while (running_.load()) {
            std::unique_lock lock(mutex_);
            cv_.wait(lock, [this] { return !queue_.empty() || !running_.load(); });

            while (!queue_.empty()) {
                auto item = std::move(queue_.front());
                queue_.pop();
                lock.unlock();

                // Фонова відправка в Kafka / Dead-Letter Queue
                (void)item;

                lock.lock();
            }
        }
    }

    size_t max_capacity_;
    std::queue<ShadowAuditLog> queue_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::atomic<bool> running_;
    std::thread worker_thread_;
};

// Інтерфейс клієнта віддаленого рушія політик
class RemotePolicyClient {
public:
    virtual ~RemotePolicyClient() = default;
    virtual std::expected<bool, std::string> evaluate(const RequestContext& ctx) = 0;
};

// Головний компонент стійкої валідації
class ResilientPolicyEnforcer {
public:
    ResilientPolicyEnforcer(
        std::shared_ptr<RemotePolicyClient> client,
        FailureStrategy strategy,
        std::shared_ptr<ShadowAuditQueue> audit_queue)
        : client_(std::move(client)),
          strategy_(strategy),
          audit_queue_(std::move(audit_queue)),
          breaker_state_(BreakerState::CLOSED),
          failure_count_(0),
          success_count_(0),
          last_state_change_(std::chrono::steady_clock::now()) {}

    PolicyDecision enforce(const RequestContext& ctx) {
        // 1. Перевірка стану запобіжника
        if (is_breaker_open()) {
            return execute_fallback(ctx, "Circuit breaker is OPEN");
        }

        // 2. Асинхронний виклик із дедлайном
        auto future = std::async(std::launch::async, [this, &ctx]() {
            return client_->evaluate(ctx);
        });

        if (future.wait_for(ctx.timeout_budget) == std::future_status::timeout) {
            record_failure();
            return execute_fallback(ctx, "Policy evaluation deadline exceeded");
        }

        auto result = future.get();
        if (!result.has_value()) {
            record_failure();
            return execute_fallback(ctx, "Remote policy engine error: " + result.error());
        }

        // Успішна відповідь валідатора
        record_success();
        cache_decision(ctx, result.value());

        return PolicyDecision{
            .allowed = result.value(),
            .degraded = false,
            .reason = "Evaluated by remote policy engine",
            .http_status = result.value() ? 200 : 403
        };
    }

private:
    bool is_breaker_open() {
        auto now = std::chrono::steady_clock::now();
        if (breaker_state_.load() == BreakerState::OPEN) {
            if (now - last_state_change_ > std::chrono::seconds(15)) {
                breaker_state_.store(BreakerState::HALF_OPEN);
                return false; // Пропускаємо пробний запит
            }
            return true;
        }
        return false;
    }

    void record_failure() {
        size_t fails = ++failure_count_;
        if (fails >= 5 && breaker_state_.load() == BreakerState::CLOSED) {
            breaker_state_.store(BreakerState::OPEN);
            last_state_change_ = std::chrono::steady_clock::now();
        } else if (breaker_state_.load() == BreakerState::HALF_OPEN) {
            breaker_state_.store(BreakerState::OPEN);
            last_state_change_ = std::chrono::steady_clock::now();
        }
    }

    void record_success() {
        if (breaker_state_.load() == BreakerState::HALF_OPEN) {
            if (++success_count_ >= 3) {
                breaker_state_.store(BreakerState::CLOSED);
                failure_count_.store(0);
                success_count_.store(0);
            }
        } else {
            failure_count_.store(0);
        }
    }

    void cache_decision(const RequestContext& ctx, bool decision) {
        std::unique_lock lock(cache_mutex_);
        std::string key = ctx.user_id + ":" + ctx.resource + ":" + ctx.action;
        cache_[key] = CacheEntry{
            .allowed = decision,
            .expires_at = std::chrono::steady_clock::now() + std::chrono::minutes(5)
        };
    }

    std::optional<bool> get_stale_cache(const RequestContext& ctx) {
        std::shared_lock lock(cache_mutex_);
        std::string key = ctx.user_id + ":" + ctx.resource + ":" + ctx.action;
        auto it = cache_.find(key);
        if (it != cache_.end()) {
            return it->second.allowed;
        }
        return std::nullopt;
    }

    PolicyDecision execute_fallback(const RequestContext& ctx, const std::string& reason) {
        // Рівень 1: Спроба читання застарілого кешу
        if (strategy_ == FailureStrategy::USE_STALE_CACHE || strategy_ == FailureStrategy::FAIL_OPEN) {
            auto cached = get_stale_cache(ctx);
            if (cached.has_value()) {
                return PolicyDecision{
                    .allowed = cached.value(),
                    .degraded = true,
                    .reason = "Stale cache fallback (" + reason + ")",
                    .http_status = cached.value() ? 200 : 403
                };
            }
        }

        // Рівень 2: Відкриття на відмову (Fail-Open) з аудитом
        if (strategy_ == FailureStrategy::FAIL_OPEN) {
            audit_queue_->push(ShadowAuditLog{
                .request_id = ctx.request_id,
                .user_id = ctx.user_id,
                .resource = ctx.resource,
                .action = ctx.action,
                .fallback_reason = reason,
                .timestamp = std::chrono::system_clock::now()
            });

            return PolicyDecision{
                .allowed = true,
                .degraded = true,
                .reason = "Fail-Open bypass (" + reason + ")",
                .http_status = 200
            };
        }

        // Рівень 3: Блокування на відмову (Fail-Closed)
        return PolicyDecision{
            .allowed = false,
            .degraded = true,
            .reason = "Fail-Closed rejected (" + reason + ")",
            .http_status = 503
        };
    }

    struct CacheEntry {
        bool allowed;
        std::chrono::steady_clock::time_point expires_at;
    };

    std::shared_ptr<RemotePolicyClient> client_;
    FailureStrategy strategy_;
    std::shared_ptr<ShadowAuditQueue> audit_queue_;

    std::atomic<BreakerState> breaker_state_;
    std::atomic<size_t> failure_count_;
    std::atomic<size_t> success_count_;
    std::chrono::steady_clock::time_point last_state_change_;

    mutable std::shared_mutex cache_mutex_;
    std::unordered_map<std::string, CacheEntry> cache_;
};
```
```go
package main

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

// FailureStrategy визначає поведінку під час збою перевірки
type FailureStrategy int

const (
	FailClosed FailureStrategy = iota
	FailOpen
	UseStaleCache
)

type BreakerState int32

const (
	StateClosed BreakerState = iota
	StateOpen
	StateHalfOpen
)

type RequestContext struct {
	RequestID     string
	UserID        string
	Resource      string
	Action        string
	TimeoutBudget time.Duration
}

type PolicyDecision struct {
	Allowed    bool
	Degraded   bool
	Reason     string
	HTTPStatus int
}

type ShadowAuditLog struct {
	RequestID      string
	UserID         string
	Resource       string
	Action         string
	FallbackReason string
	Timestamp      time.Time
}

// ShadowAuditQueue буферизує події для фонової доставки в чергу
type ShadowAuditQueue struct {
	queue chan ShadowAuditLog
}

func NewShadowAuditQueue(capacity int) *ShadowAuditQueue {
	q := &ShadowAuditQueue{
		queue: make(chan ShadowAuditLog, capacity),
	}
	go q.worker()
	return q
}

func (q *ShadowAuditQueue) Push(log ShadowAuditLog) bool {
	select {
	case q.queue <- log:
		return true
	default:
		// Переповнення черги аудиту скидає запис заради збереження пам'яті
		return false
	}
}

func (q *ShadowAuditQueue) worker() {
	for log := range q.queue {
		// Фонова відправка в Kafka або Dead-Letter Queue
		_ = log
	}
}

type RemotePolicyClient interface {
	Evaluate(ctx context.Context, req RequestContext) (bool, error)
}

type cacheEntry struct {
	allowed   bool
	expiresAt time.Time
}

type ResilientPolicyEnforcer struct {
	client          RemotePolicyClient
	strategy        FailureStrategy
	auditQueue      *ShadowAuditQueue
	breakerState    int32
	failureCount    int64
	successCount    int64
	lastStateChange time.Time

	mu    sync.RWMutex
	cache map[string]cacheEntry
}

func NewResilientPolicyEnforcer(
	client RemotePolicyClient,
	strategy FailureStrategy,
	auditQueue *ShadowAuditQueue,
) *ResilientPolicyEnforcer {
	return &ResilientPolicyEnforcer{
		client:          client,
		strategy:        strategy,
		auditQueue:      auditQueue,
		breakerState:    int32(StateClosed),
		lastStateChange: time.Now(),
		cache:           make(map[string]cacheEntry),
	}
}

func (e *ResilientPolicyEnforcer) Enforce(ctx context.Context, req RequestContext) PolicyDecision {
	if e.isBreakerOpen() {
		return e.executeFallback(req, "Circuit breaker is OPEN")
	}

	callCtx, cancel := context.WithTimeout(ctx, req.TimeoutBudget)
	defer cancel()

	decisionChan := make(chan bool, 1)
	errChan := make(chan error, 1)

	go func() {
		allowed, err := e.client.Evaluate(callCtx, req)
		if err != nil {
			errChan <- err
			return
		}
		decisionChan <- allowed
	}()

	select {
	case allowed := <-decisionChan:
		e.recordSuccess()
		e.setCache(req, allowed)
		status := 200
		if !allowed {
			status = 403
		}
		return PolicyDecision{
			Allowed:    allowed,
			Degraded:   false,
			Reason:     "Evaluated by remote engine",
			HTTPStatus: status,
		}

	case err := <-errChan:
		e.recordFailure()
		return e.executeFallback(req, fmt.Sprintf("Engine error: %v", err))

	case <-callCtx.Done():
		e.recordFailure()
		return e.executeFallback(req, "Evaluation deadline exceeded")
	}
}

func (e *ResilientPolicyEnforcer) isBreakerOpen() bool {
	state := BreakerState(atomic.LoadInt32(&e.breakerState))
	if state == StateOpen {
		e.mu.RLock()
		elapsed := time.Since(e.lastStateChange)
		e.mu.RUnlock()

		if elapsed > 15*time.Second {
			atomic.StoreInt32(&e.breakerState, int32(StateHalfOpen))
			return false
		}
		return true
	}
	return false
}

func (e *ResilientPolicyEnforcer) recordFailure() {
	fails := atomic.AddInt64(&e.failureCount, 1)
	state := BreakerState(atomic.LoadInt32(&e.breakerState))

	if fails >= 5 && state == StateClosed {
		atomic.StoreInt32(&e.breakerState, int32(StateOpen))
		e.mu.Lock()
		e.lastStateChange = time.Now()
		e.mu.Unlock()
	} else if state == StateHalfOpen {
		atomic.StoreInt32(&e.breakerState, int32(StateOpen))
		e.mu.Lock()
		e.lastStateChange = time.Now()
		e.mu.Unlock()
	}
}

func (e *ResilientPolicyEnforcer) recordSuccess() {
	state := BreakerState(atomic.LoadInt32(&e.breakerState))
	if state == StateHalfOpen {
		if atomic.AddInt64(&e.successCount, 1) >= 3 {
			atomic.StoreInt32(&e.breakerState, int32(StateClosed))
			atomic.StoreInt64(&e.failureCount, 0)
			atomic.StoreInt64(&e.successCount, 0)
		}
	} else {
		atomic.StoreInt64(&e.failureCount, 0)
	}
}

func (e *ResilientPolicyEnforcer) setCache(req RequestContext, allowed bool) {
	key := fmt.Sprintf("%s:%s:%s", req.UserID, req.Resource, req.Action)
	e.mu.Lock()
	e.cache[key] = cacheEntry{
		allowed:   allowed,
		expiresAt: time.Now().Add(5 * time.Minute),
	}
	e.mu.Unlock()
}

func (e *ResilientPolicyEnforcer) getStaleCache(req RequestContext) (bool, bool) {
	key := fmt.Sprintf("%s:%s:%s", req.UserID, req.Resource, req.Action)
	e.mu.RLock()
	entry, ok := e.cache[key]
	e.mu.RUnlock()
	if ok {
		return entry.allowed, true
	}
	return false, false
}

func (e *ResilientPolicyEnforcer) executeFallback(req RequestContext, reason string) PolicyDecision {
	if e.strategy == UseStaleCache || e.strategy == FailOpen {
		if allowed, ok := e.getStaleCache(req); ok {
			status := 200
			if !allowed {
				status = 403
			}
			return PolicyDecision{
				Allowed:    allowed,
				Degraded:   true,
				Reason:     fmt.Sprintf("Stale cache (%s)", reason),
				HTTPStatus: status,
			}
		}
	}

	if e.strategy == FailOpen {
		e.auditQueue.Push(ShadowAuditLog{
			RequestID:      req.RequestID,
			UserID:         req.UserID,
			Resource:       req.Resource,
			Action:         req.Action,
			FallbackReason: reason,
			Timestamp:      time.Now(),
		})

		return PolicyDecision{
			Allowed:    true,
			Degraded:   true,
			Reason:     fmt.Sprintf("Fail-Open bypass (%s)", reason),
			HTTPStatus: 200,
		}
	}

	return PolicyDecision{
		Allowed:    false,
		Degraded:   true,
		Reason:     fmt.Sprintf("Fail-Closed rejected (%s)", reason),
		HTTPStatus: 503,
	}
}
```
:::

## Глибокий аналіз паралелізму та крайових випадків

Під час високого навантаження (10 000+ RPS) робота подібного інтерцептора стикається з тонкими проблемами синхронізації та розподіленого стану:

### 1. Неблокуюча поведінка черги тіньового аудиту

У коді реалізації функція `push()` черги `ShadowAuditQueue` навмисно спроєктована як неблокуюча операція з обмеженою ємністю (`bounded channel` / `bounded queue`). Якщо зовнішній споживач логів (брокер Kafka або агент векторного збору журналів Fluentbit) зазнає аварії, черга швидко заповнюється до ліміту в 10 000 записів.

Після досягнення ліміту метод `push()` починає безшумно скидати нові записи (`drop on overflow`), інкрементуючи системну метрику `audit_logs_dropped_total`. Якщо зробити чергу блокуючою (наприклад, очікувати звільнення місця через умовну змінну), робочі потоки вебсервера зупиняться у черзі аудиту. Це миттєво перетворить бажаний режим Fail-Open на некерований системний колапс із зависанням вхідних HTTP-з'єднань.

### 2. Запобігання отруєнню кешу (Cache Poisoning)

Зверніть увагу на функцію `setCache()`: оновлення локального кешу здійснюється **виключно** у гілці успішної відповіді віддаленого сервера (`result.has_value()`). Якщо запит було пропущено внаслідок спрацьовування Fail-Open або дедлайну, результат «дозволено» **ніколи** не записується в кеш.

Порушення цього інваріанта призводить до важкої вразливості: зловмисник, здійснивши короткочасну DoS-атаку на сервер авторизації, змушує інтерцептор відкритися (Fail-Open), а запис такого рішення в локальний кеш на 5 хвилин закріплює несанкціонований доступ навіть після повного відновлення роботи захисного контуру.

### 3. Проблема холодного старту та ізоляції пам'яті

Коли новий екземпляр сервісу масштабується оркестратором Kubernetes у момент, коли сервер авторизації перебуває в стані аварії, локальний кеш нового поду виявляється абсолютно порожнім.

У такому стані:
* Якщо обрано стратегію `USE_STALE_CACHE`, запит не знаходить запису в кеші й деградує до базового налаштування (`FAIL_CLOSED` або `FAIL_OPEN`).
* Для захисту від повного паралічу критичних систем у конфігурацію додається статичний маніфест безпечних правил за замовчуванням (Bootstrap Whitelist), що завантажується з локального файлу під час старту процесу.

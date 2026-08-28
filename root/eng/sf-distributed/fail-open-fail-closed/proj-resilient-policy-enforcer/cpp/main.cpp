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

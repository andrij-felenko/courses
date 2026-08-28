#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <optional>
#include <expected>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <random>
#include <algorithm>
#include <format>

using namespace std::chrono_literals;

enum class OpStatus : uint8_t {
    Pending = 0,
    Running,
    Succeeded,
    Failed,
    Cancelled
};

struct OperationRecord {
    std::string id;
    std::string owner_id;
    std::string idempotency_key;
    uint32_t payload_hash{0};
    OpStatus status{OpStatus::Pending};
    float progress{0.0f};
    std::string stage{"queued"};
    uint32_t attempt{0};
    uint64_t lease_token{0};
    std::chrono::system_clock::time_point lease_until;
    bool cancel_requested{false};
    std::string result_url;
    std::chrono::system_clock::time_point created_at;
    std::chrono::system_clock::time_point updated_at;
};

enum class EngineError {
    ConflictMutatedPayload,
    CapacityExceeded,
    LeaseLost,
    InvalidTransition,
    NotFound
};

class OperationStorageEngine {
public:
    OperationStorageEngine() = default;

    std::expected<OperationRecord, EngineError> submit(
        std::string_view id,
        std::string_view owner,
        std::string_view idem_key,
        uint32_t hash) 
    {
        std::unique_lock lock(mutex_);
        const auto now = std::chrono::system_clock::now();

        // 1. Дедуплікація за ключем ідемпотентності
        if (!idem_key.empty()) {
            for (const auto& [_, rec] : table_) {
                if (rec.owner_id == owner && rec.idempotency_key == idem_key) {
                    if (rec.payload_hash != hash) {
                        return std::unexpected(EngineError::ConflictMutatedPayload);
                    }
                    return rec; // Повертаємо існуючу операцію без повторного створення
                }
            }
        }

        // 2. Створення нового запису
        OperationRecord new_rec{
            .id = std::string(id),
            .owner_id = std::string(owner),
            .idempotency_key = std::string(idem_key),
            .payload_hash = hash,
            .status = OpStatus::Pending,
            .progress = 0.0f,
            .stage = "queued",
            .attempt = 0,
            .lease_token = 0,
            .lease_until = now,
            .cancel_requested = false,
            .result_url = "",
            .created_at = now,
            .updated_at = now
        };

        table_[new_rec.id] = new_rec;
        cv_task_.notify_one();
        return new_rec;
    }

    std::expected<OperationRecord, EngineError> claim_task(uint64_t worker_token, std::chrono::seconds lease_duration) {
        std::unique_lock lock(mutex_);
        
        while (!shutdown_) {
            const auto now = std::chrono::system_clock::now();
            for (auto& [_, rec] : table_) {
                const bool is_pending = (rec.status == OpStatus::Pending);
                const bool is_expired = (rec.status == OpStatus::Running && rec.lease_until < now);

                if (is_pending || is_expired) {
                    rec.status = OpStatus::Running;
                    ++rec.attempt;
                    rec.lease_token = worker_token;
                    rec.lease_until = now + lease_duration;
                    rec.stage = "processing";
                    rec.updated_at = now;
                    return rec;
                }
            }
            cv_task_.wait(lock);
        }
        return std::unexpected(EngineError::NotFound);
    }

    std::expected<bool, EngineError> heartbeat(
        std::string_view op_id,
        uint64_t worker_token,
        float progress,
        std::string_view stage,
        std::chrono::seconds lease_ext) 
    {
        std::unique_lock lock(mutex_);
        auto it = table_.find(std::string(op_id));
        if (it == table_.end()) return std::unexpected(EngineError::NotFound);

        auto& rec = it->second;
        const auto now = std::chrono::system_clock::now();

        if (rec.status != OpStatus::Running || rec.lease_token != worker_token || rec.lease_until < now) {
            return std::unexpected(EngineError::LeaseLost);
        }

        rec.lease_until = now + lease_ext;
        rec.progress = std::clamp(progress, 0.0f, 1.0f);
        rec.stage = stage;
        rec.updated_at = now;
        return rec.cancel_requested;
    }

    std::expected<void, EngineError> commit_success(
        std::string_view op_id,
        uint64_t worker_token,
        std::string_view result_url) 
    {
        std::unique_lock lock(mutex_);
        auto it = table_.find(std::string(op_id));
        if (it == table_.end()) return std::unexpected(EngineError::NotFound);

        auto& rec = it->second;
        const auto now = std::chrono::system_clock::now();

        if (rec.status != OpStatus::Running || rec.lease_token != worker_token || rec.lease_until < now) {
            return std::unexpected(EngineError::LeaseLost);
        }

        rec.status = OpStatus::Succeeded;
        rec.progress = 1.0f;
        rec.stage = "completed";
        rec.result_url = result_url;
        rec.updated_at = now;
        return {};
    }

    [[nodiscard]] std::optional<OperationRecord> get_status(std::string_view op_id) const {
        std::unique_lock lock(mutex_);
        auto it = table_.find(std::string(op_id));
        if (it != table_.end()) return it->second;
        return std::nullopt;
    }

    void shutdown() {
        std::unique_lock lock(mutex_);
        shutdown_ = true;
        cv_task_.notify_all();
    }

private:
    mutable std::mutex mutex_;
    std::condition_variable cv_task_;
    std::unordered_map<std::string, OperationRecord> table_;
    bool shutdown_{false};
};

/* Клієнт автоматичного опитування з джитером */
class AsyncOperationClient {
public:
    explicit AsyncOperationClient(OperationStorageEngine& engine) : engine_(engine), rng_(std::random_device{}()) {}

    std::expected<std::string, std::string> poll_until_complete(std::string_view op_id, std::chrono::seconds timeout) {
        const auto deadline = std::chrono::system_clock::now() + timeout;
        uint32_t attempt = 0;

        while (std::chrono::system_clock::now() < deadline) {
            auto status_opt = engine_.get_status(op_id);
            if (!status_opt) return std::unexpected("Операцію не знайдено на сервері");

            const auto& rec = *status_opt;
            if (rec.status == OpStatus::Succeeded) {
                return rec.result_url;
            }
            if (rec.status == OpStatus::Failed) {
                return std::unexpected("Операція завершилася помилкою виконання");
            }
            if (rec.status == OpStatus::Cancelled) {
                return std::unexpected("Операцію було скасовано користувачем");
            }

            // Розрахунок паузи з повним джитером (Full Jitter)
            const uint32_t max_backoff = std::min(1u << std::min(attempt++, 6u), 16u);
            std::uniform_int_distribution<uint32_t> dist(1, max_backoff);
            const auto sleep_dur = std::chrono::seconds(dist(rng_));

            std::this_thread::sleep_for(sleep_dur);
        }

        return std::unexpected("Перевищено граничний дедлайн очікування операції");
    }

private:
    OperationStorageEngine& engine_;
    std::mt19937 rng_;
};

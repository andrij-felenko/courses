#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <mutex>
#include <shared_mutex>
#include <condition_variable>
#include <chrono>
#include <optional>
#include <expected>
#include <thread>
#include <vector>

namespace cqrs {

using Version = uint64_t;
using EntityId = std::string;

// Структура представлення сутності для читання
struct OrderView {
    EntityId order_id;
    std::string customer_id;
    std::string status;
    int64_t total_cents{0};
    Version version{0};
};

// Перелік можливих помилок виконання запиту
enum class GatewayError {
    Timeout,
    NotFound,
    PrimaryUnavailable,
    InternalError
};

// Реєстр ватерліній та синхронізація очікування версій
class WatermarkRegistry {
public:
    void update_watermark(const EntityId& id, Version new_version) {
        std::unique_lock lock(mutex_);
        auto& current = watermarks_[id];
        if (new_version > current) {
            current = new_version;
            // Пробуджуємо всі потоки, що чекають оновлення цієї або меншої версії
            cv_.notify_all();
        }
    }

    [[nodiscard]] Version get_watermark(const EntityId& id) const {
        std::shared_lock lock(mutex_);
        auto it = watermarks_.find(id);
        return (it != watermarks_.end()) ? it->second : 0;
    }

    [[nodiscard]] bool wait_for_version(
        const EntityId& id,
        Version required_version,
        std::chrono::milliseconds timeout
    ) {
        std::unique_lock lock(mutex_);
        return cv_.wait_for(lock, timeout, [&] {
            auto it = watermarks_.find(id);
            return (it != watermarks_.end()) && (it->second >= required_version);
        });
    }

private:
    mutable std::shared_mutex mutex_;
    std::condition_variable_any cv_;
    std::unordered_map<EntityId, Version> watermarks_;
};

// Сховище моделі читання (Read Model Store)
class ReadModelStore {
public:
    void upsert(OrderView view) {
        std::unique_lock lock(mutex_);
        store_[view.order_id] = std::move(view);
    }

    [[nodiscard]] std::optional<OrderView> find(const EntityId& id) const {
        std::shared_lock lock(mutex_);
        auto it = store_.find(id);
        if (it != store_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

private:
    mutable std::shared_mutex mutex_;
    std::unordered_map<EntityId, OrderView> store_;
};

// Первинне транзакційне сховище (Write Model Primary Database)
class PrimaryWriteStore {
public:
    void save(OrderView order) {
        std::unique_lock lock(mutex_);
        primary_db_[order.order_id] = std::move(order);
    }

    [[nodiscard]] std::optional<OrderView> fetch_direct(const EntityId& id) const {
        std::shared_lock lock(mutex_);
        auto it = primary_db_.find(id);
        if (it != primary_db_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

private:
    mutable std::shared_mutex mutex_;
    std::unordered_map<EntityId, OrderView> primary_db_;
};

// Шлюз запитів на читання з контролем контракту причинності
class CausalQueryGateway {
public:
    CausalQueryGateway(
        std::shared_ptr<WatermarkRegistry> registry,
        std::shared_ptr<ReadModelStore> read_store,
        std::shared_ptr<PrimaryWriteStore> write_store
    ) : registry_(std::move(registry)),
        read_store_(std::move(read_store)),
        write_store_(std::move(write_store)) {}

    [[nodiscard]] std::expected<OrderView, GatewayError> get_order(
        const EntityId& id,
        std::optional<Version> required_version,
        std::chrono::milliseconds wait_budget = std::chrono::milliseconds(50)
    ) {
        if (required_version.has_value()) {
            const Version req_v = *required_version;
            const Version current_v = registry_->get_watermark(id);

            if (current_v < req_v) {
                // Входимо в кероване очікування наздоганяння проєкції
                const bool caught_up = registry_->wait_for_version(id, req_v, wait_budget);
                if (!caught_up) {
                    // Бюджет часу вичерпано: перемикаємося на первинну базу (Primary Fallback)
                    auto direct_res = write_store_->fetch_direct(id);
                    if (direct_res.has_value()) {
                        return *direct_res;
                    }
                    return std::unexpected(GatewayError::Timeout);
                }
            }
        }

        // Швидкий шлях: читання з денормалізованого представлення
        auto view = read_store_->find(id);
        if (view.has_value()) {
            return *view;
        }

        // Аварійний шлях: якщо сутність щойно створена і відсутня в моделі читання
        auto fallback = write_store_->fetch_direct(id);
        if (fallback.has_value()) {
            return *fallback;
        }

        return std::unexpected(GatewayError::NotFound);
    }

private:
    std::shared_ptr<WatermarkRegistry> registry_;
    std::shared_ptr<ReadModelStore> read_store_;
    std::shared_ptr<PrimaryWriteStore> write_store_;
};

} // namespace cqrs

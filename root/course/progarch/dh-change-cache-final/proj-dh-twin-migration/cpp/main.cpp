// C++20: Idiomatic Zero-Downtime Twin Migrator & Coalesced Cache Invalidator
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <mutex>
#include <future>
#include <chrono>
#include <expected>
#include <optional>
#include <atomic>
#include <random>

struct DeviceTwinState {
    std::string home_id;
    std::string device_id;
    std::string state_json;
    uint64_t version{0};
    uint64_t observed_at_ms{0};
    uint64_t updated_at_ms{0};
};

enum class MigrationPhase {
    Phase0_Baseline,
    Phase1_DualWrite,
    Phase2_ReadPrimaryV_Backfill,
    Phase3_Contract
};

enum class TwinError {
    NotFound,
    Timeout,
    StorageFailure,
    VersionConflict
};

// Абстрактний шов твіна (Branch by Abstraction)
class IDeviceTwinStorage {
public:
    virtual ~IDeviceTwinStorage() = default;
    virtual std::expected<DeviceTwinState, TwinError> get_state(std::string_view home_id) = 0;
    virtual std::expected<void, TwinError> save_state(const DeviceTwinState& state) = 0;
};

// Сплав Singleflight (Request Coalescing) та версійного кешування
class SingleflightCache {
private:
    struct CacheEntry {
        DeviceTwinState state;
        uint64_t expires_at_ms;
    };

    std::unordered_map<std::string, CacheEntry> cache_;
    std::unordered_map<std::string, std::shared_future<std::expected<DeviceTwinState, TwinError>>> in_flight_;
    mutable std::mutex mutex_;

public:
    std::expected<DeviceTwinState, TwinError> get_or_fetch(
        std::string_view home_id,
        uint64_t now_ms,
        auto fetch_fn) 
    {
        std::unique_lock lock(mutex_);
        std::string key(home_id);

        // 1. Перевірка наявності в кеші (із урахуванням Soft TTL)
        if (auto it = cache_.find(key); it != cache_.end()) {
            if (it->second.expires_at_ms > now_ms) {
                return it->second.state;
            }
        }

        // 2. Якщо запит вже обробляється іншим потоком — чекаємо того самого майбутнього результату
        if (auto it = in_flight_.find(key); it != in_flight_.end()) {
            auto fut = it->second;
            lock.unlock(); // Знімаємо замок на час очікування майбутнього результату
            return fut.get();
        }

        // 3. Створення нового in-flight запиту для першого потоку
        std::promise<std::expected<DeviceTwinState, TwinError>> promise;
        std::shared_future<std::expected<DeviceTwinState, TwinError>> fut = promise.get_future().share();
        in_flight_[key] = fut;
        lock.unlock(); // Виконуємо запит до БД поза глобальним замком

        auto result = fetch_fn(home_id);

        lock.lock();
        if (result.has_value()) {
            // Soft TTL (5000ms) + Jitter (±500ms) для відсікання синхронного знецінення
            static std::mt19937 gen(1337);
            std::uniform_int_distribution<uint64_t> dist(0, 1000);
            uint64_t jitter = dist(gen);
            cache_[key] = CacheEntry{result.value(), now_ms + 5000 + jitter};
        }
        in_flight_.erase(key);
        promise.set_value(result);
        return result;
    }

    void invalidate_if_newer(std::string_view home_id, uint64_t new_version) {
        std::lock_guard lock(mutex_);
        std::string key(home_id);
        if (auto it = cache_.find(key); it != cache_.end()) {
            if (new_version >= it->second.state.version) {
                cache_.erase(it);
            }
        }
    }
};

// Головний фасадер міграції твінів Digital Homes
class TwinMigrationFacade {
private:
    std::shared_ptr<IDeviceTwinStorage> storage_b_;
    std::shared_ptr<IDeviceTwinStorage> storage_c_;
    std::atomic<MigrationPhase> phase_{MigrationPhase::Phase0_Baseline};
    SingleflightCache cache_;
    std::atomic<uint64_t> mismatch_count_{0};

public:
    TwinMigrationFacade(std::shared_ptr<IDeviceTwinStorage> b, std::shared_ptr<IDeviceTwinStorage> c)
        : storage_b_(std::move(b)), storage_c_(std::move(c)) {}

    void set_phase(MigrationPhase phase) noexcept {
        phase_.store(phase, std::memory_order_release);
    }

    std::expected<DeviceTwinState, TwinError> get_device_twin(std::string_view home_id, uint64_t now_ms) {
        auto current_phase = phase_.load(std::memory_order_acquire);

        auto fetch_from_db = [&](std::string_view hid) -> std::expected<DeviceTwinState, TwinError> {
            if (current_phase == MigrationPhase::Phase0_Baseline || current_phase == MigrationPhase::Phase1_DualWrite) {
                return storage_b_->get_state(hid);
            }
            
            // Phase 2 або 3: Основне джерело — Твін В із Fallback на Б
            auto res_c = storage_c_->get_state(hid);
            if (res_c.has_value() || current_phase == MigrationPhase::Phase3_Contract) {
                return res_c;
            }
            
            // Fallback на Б під час Phase 2 при виникненні помилок у В
            return storage_b_->get_state(hid);
        };

        return cache_.get_or_fetch(home_id, now_ms, fetch_from_db);
    }

    std::expected<void, TwinError> save_device_twin(const DeviceTwinState& state) {
        auto current_phase = phase_.load(std::memory_order_acquire);

        if (current_phase == MigrationPhase::Phase0_Baseline) {
            return storage_b_->save_state(state);
        }

        if (current_phase == MigrationPhase::Phase1_DualWrite) {
            auto res_b = storage_b_->save_state(state);
            if (res_b.has_value()) {
                // Асинхронний/Transactional Outbox запис у В
                auto res_c = storage_c_->save_state(state);
                if (!res_c.has_value()) {
                    mismatch_count_.fetch_add(1, std::memory_order_relaxed);
                }
            }
            return res_b;
        }

        if (current_phase == MigrationPhase::Phase2_ReadPrimaryV_Backfill || current_phase == MigrationPhase::Phase3_Contract) {
            auto res_c = storage_c_->save_state(state);
            if (res_c.has_value()) {
                cache_.invalidate_if_newer(state.home_id, state.version);
            }
            return res_c;
        }

        return std::unexpected(TwinError::StorageFailure);
    }

    uint64_t get_mismatch_count() const noexcept {
        return mismatch_count_.load(std::memory_order_relaxed);
    }
};

// C++20: Фаза-орієнтований фасадер твінів та Singleflight кеш
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <unordered_map>
#include <mutex>
#include <future>
#include <expected>
#include <atomic>

struct DeviceTwinDTO {
    std::string home_id;
    std::string state_json;
    uint64_t version_seq{0};
    uint64_t observed_at_ms{0};
    uint64_t updated_at_ms{0};
};

enum class MigrationPhase {
    Phase0_Baseline,
    Phase1_DualWrite,
    Phase2_ReadPrimaryV_Backfill,
    Phase3_Contract
};

enum class StorageError { NotFound, Timeout, DbError };

// Абстрактний шов твіна (Branch by Abstraction)
class ITwinStorage {
public:
    virtual ~ITwinStorage() = default;
    virtual std::expected<DeviceTwinDTO, StorageError> read_twin(std::string_view home_id) = 0;
    virtual std::expected<void, StorageError> write_twin(const DeviceTwinDTO& dto) = 0;
};

// Захищений кеш із Singleflight (Request Coalescing)
class CoalescedCache {
private:
    struct CacheValue {
        DeviceTwinDTO dto;
        uint64_t expires_at_ms;
    };
    std::unordered_map<std::string, CacheValue> store_;
    std::unordered_map<std::string, std::shared_future<std::expected<DeviceTwinDTO, StorageError>>> in_flight_;
    std::mutex lock_;

public:
    std::expected<DeviceTwinDTO, StorageError> fetch_coalesced(
        std::string_view home_id,
        uint64_t now_ms,
        auto db_fetcher) 
    {
        std::unique_lock<std::mutex> guard(lock_);
        std::string key(home_id);

        // 1. Читання з кешу
        if (auto it = store_.find(key); it != store_.end()) {
            if (it->second.expires_at_ms > now_ms) {
                return it->second.dto;
            }
        }

        // 2. Якщо запит уже летить — чекаємо на спільне майбутнє
        if (auto it = in_flight_.find(key); it != in_flight_.end()) {
            auto shared_fut = it->second;
            guard.unlock();
            return shared_fut.get();
        }

        // 3. Перший потік створює запит
        std::promise<std::expected<DeviceTwinDTO, StorageError>> promise;
        auto shared_fut = promise.get_future().share();
        in_flight_[key] = shared_fut;
        guard.unlock();

        auto db_res = db_fetcher(home_id);

        guard.lock();
        if (db_res.has_value()) {
            uint64_t jitter = rand() % 500;
            store_[key] = CacheValue{ db_res.value(), now_ms + 4000 + jitter };
        }
        in_flight_.erase(key);
        promise.set_value(db_res);
        return db_res;
    }

    void invalidate_versioned(std::string_view home_id, uint64_t version) {
        std::lock_guard<std::mutex> guard(lock_);
        std::string key(home_id);
        if (auto it = store_.find(key); it != store_.end()) {
            if (version >= it->second.dto.version_seq) {
                store_.erase(it);
            }
        }
    }
};

// Фасадер міграції твінів
class MigrationTwinFacade {
private:
    std::shared_ptr<ITwinStorage> legacy_b_;
    std::shared_ptr<ITwinStorage> cqrs_v_;
    CoalescedCache cache_;
    std::atomic<MigrationPhase> current_phase_{MigrationPhase::Phase0_Baseline};

public:
    MigrationTwinFacade(std::shared_ptr<ITwinStorage> b, std::shared_ptr<ITwinStorage> v)
        : legacy_b_(std::move(b)), cqrs_v_(std::move(v)) {}

    void set_phase(MigrationPhase phase) noexcept {
        current_phase_.store(phase, std::memory_order_release);
    }

    std::expected<DeviceTwinDTO, StorageError> get_twin(std::string_view home_id, uint64_t now_ms) {
        auto phase = current_phase_.load(std::memory_order_acquire);

        auto fetch_db = [&](std::string_view hid) -> std::expected<DeviceTwinDTO, StorageError> {
            if (phase == MigrationPhase::Phase0_Baseline || phase == MigrationPhase::Phase1_DualWrite) {
                return legacy_b_->read_twin(hid);
            }
            // Phase 2 & 3: Читаємо з CQRS V, з fallback на Legacy B у Phase 2
            auto res_v = cqrs_v_->read_twin(hid);
            if (res_v.has_value() || phase == MigrationPhase::Phase3_Contract) {
                return res_v;
            }
            return legacy_b_->read_twin(hid); // Fallback
        };

        return cache_.fetch_coalesced(home_id, now_ms, fetch_db);
    }
};

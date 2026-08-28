#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <chrono>
#include <thread>
#include <random>
#include <stdexcept>
#include <algorithm>

// Контракт запису даних
struct OrderRecord {
    std::uint64_t id;
    double amount;
    std::string status;
    bool has_v2_discount;
};

// Стан контрольної точки
struct Checkpoint {
    std::string job_id;
    std::uint64_t last_processed_id{0};
    std::uint64_t total_processed{0};
    std::uint64_t total_failed{0};
};

// Інтерфейс сховища контрольних точок (RAII abstraction)
class ICheckpointStore {
public:
    virtual ~ICheckpointStore() = default;
    virtual Checkpoint load_checkpoint(const std::string& job_id) = 0;
    virtual void save_checkpoint(const Checkpoint& cp) = 0;
};

// Симуляція сховища контрольних точок у пам'яті
class InMemoryCheckpointStore : public ICheckpointStore {
private:
    Checkpoint current_cp_;
public:
    explicit InMemoryCheckpointStore(std::string job_id) {
        current_cp_.job_id = std::move(job_id);
    }

    Checkpoint load_checkpoint(const std::string& job_id) override {
        return current_cp_;
    }

    void save_checkpoint(const Checkpoint& cp) override {
        current_cp_ = cp;
        std::cout << "[CHECKPOINT] Saved progress: last_id=" << cp.last_processed_id 
                  << ", total=" << cp.total_processed << std::endl;
    }
};

// Адаптивний регулятор затримки (Adaptive Throttler)
class AdaptiveThrottler {
private:
    std::chrono::milliseconds current_delay_{10};
    const std::chrono::milliseconds min_delay_{5};
    const std::chrono::milliseconds max_delay_{1000};
    const double max_allowed_p99_ms_{30.0};

public:
    std::chrono::milliseconds calculate_delay(double current_db_p99_ms) {
        if (current_db_p99_ms > max_allowed_p99_ms_) {
            // Експоненційне збільшення затримки при високому навантаженні
            current_delay_ = std::min(max_delay_, current_delay_ * 2);
            std::cout << "[THROTTLE] High DB Latency (" << current_db_p99_ms 
                      << "ms). Increased delay to " << current_delay_.count() << "ms\n";
        } else {
            // Поступове зменшення затримки
            current_delay_ = std::max(min_delay_, std::chrono::milliseconds(
                static_cast<long long>(current_delay_.count() * 0.9)));
        }
        return current_delay_;
    }
};

// Основний рушій бекфілу
class BackfillEngine {
private:
    std::string job_id_;
    std::shared_ptr<ICheckpointStore> checkpoint_store_;
    AdaptiveThrottler throttler_;
    std::size_t batch_size_{1000};

    // Симуляція обчислення знижки v2
    double compute_v2_discount(const OrderRecord& order) {
        if (order.amount < 0) {
            throw std::invalid_argument("Poison pill: negative order amount");
        }
        return order.amount * 0.15;
    }

    // Симуляція вибірки за Keyset курсором: WHERE id > last_id ORDER BY id ASC LIMIT batch_size
    std::vector<OrderRecord> fetch_batch_from_db(std::uint64_t last_id, std::size_t limit) {
        std::vector<OrderRecord> batch;
        for (std::size_t i = 1; i <= limit; ++i) {
            std::uint64_t next_id = last_id + i;
            if (next_id > 10000) break; // Межа історії
            batch.push_back({next_id, 100.0 + (next_id % 50), "COMPLETED", false});
        }
        return batch;
    }

    // Симуляція оновлення записів із захистом WHERE v2 IS NULL
    std::size_t update_batch_in_db(const std::vector<OrderRecord>& batch, std::vector<std::uint64_t>& dlq) {
        std::size_t updated_count = 0;
        for (const auto& record : batch) {
            try {
                double discount = compute_v2_discount(record);
                // Імітація атомарного UPDATE orders SET discount_v2 = :val WHERE id = :id AND discount_v2 IS NULL
                updated_count++;
            } catch (const std::exception& ex) {
                dlq.push_back(record.id);
                std::cerr << "[DLQ] Record " << record.id << " failed: " << ex.what() << std::endl;
            }
        }
        return updated_count;
    }

public:
    BackfillEngine(std::string job_id, std::shared_ptr<ICheckpointStore> cp_store)
        : job_id_(std::move(job_id)), checkpoint_store_(std::move(cp_store)) {}

    void execute() {
        Checkpoint cp = checkpoint_store_->load_checkpoint(job_id_);
        std::cout << "[ENGINE] Starting backfill from last_id=" << cp.last_processed_id << std::endl;

        while (true) {
            auto batch = fetch_batch_from_db(cp.last_processed_id, batch_size_);
            if (batch.empty()) {
                std::cout << "[ENGINE] Backfill completed successfully!\n";
                break;
            }

            std::vector<std::uint64_t> dlq;
            std::size_t successful_updates = update_batch_in_db(batch, dlq);

            cp.last_processed_id = batch.back().id;
            cp.total_processed += successful_updates;
            cp.total_failed += dlq.size();

            // Сохранение контрольной точки
            checkpoint_store_->save_checkpoint(cp);

            // Опитування метрик та адаптивна затримка
            double simulated_p99_latency_ms = 15.0 + (cp.total_processed % 30);
            auto sleep_delay = throttler_.calculate_delay(simulated_p99_latency_ms);
            std::this_thread::sleep_for(sleep_delay);
        }
    }
};

int main() {
    auto store = std::make_shared<InMemoryCheckpointStore>("job_discount_v2");
    BackfillEngine engine("job_discount_v2", store);
    engine.execute();
    return 0;
}

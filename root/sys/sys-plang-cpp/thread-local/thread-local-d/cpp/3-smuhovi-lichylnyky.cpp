#include <atomic>
#include <vector>
#include <numeric>

class ThreadSafeMetric {
    struct ThreadCounter {
        std::atomic<uint64_t> value{0};
        alignas(64) char padding[56]; // Захист від False Sharing між сусідніми структурами
    };

    static inline std::vector<ThreadCounter*> registry_;
    static inline std::mutex registry_mtx_;

    static ThreadCounter& get_local_counter() {
        thread_local ThreadCounter local_counter;
        thread_local struct Registration {
            Registration(ThreadCounter* counter) {
                std::lock_guard<std::mutex> lock(registry_mtx_);
                registry_.push_back(counter);
            }
        } reg(&local_counter);
        return local_counter;
    }

public:
    void increment() {
        // Локальний інкремент без конкуренції: запис виключно у власний L1-кеш
        get_local_counter().value.fetch_add(1, std::memory_order_relaxed);
    }

    uint64_t read_total() const {
        std::lock_guard<std::mutex> lock(registry_mtx_);
        uint64_t total = 0;
        for (const auto* counter : registry_) {
            total += counter->value.load(std::memory_order_relaxed);
        }
        return total;
    }
};

#include <atomic>
#include <vector>
#include <cstdint>

// AtomicLong аналог для суворого лімітування
class StrictRateLimiter {
private:
    std::atomic<std::int64_t> current_tokens;

public:
    explicit StrictRateLimiter(std::int64_t capacity) : current_tokens(capacity) {}

    bool try_acquire() {
        std::int64_t current = current_tokens.load(std::memory_order_relaxed);
        while (current > 0) {
            if (current_tokens.compare_exchange_weak(current, current - 1,
                                                    std::memory_order_acquire,
                                                    std::memory_order_relaxed)) {
                return true;
            }
        }
        return false;
    }
};

// Простий шардований акумулятор для швидкого запису метрик
class StripedMetricCounter {
private:
    struct alignas(64) Cell {
        std::atomic<std::int64_t> count{0};
    };
    std::vector<Cell> cells;
    const size_t mask;

public:
    explicit StripedMetricCounter(size_t num_cells = 16)
        : cells(num_cells), mask(num_cells - 1) {}

    void increment(size_t thread_id) {
        cells[thread_id & mask].count.fetch_add(1, std::memory_order_relaxed);
    }

    std::int64_t get_snapshot() const {
        std::int64_t total = 0;
        for (const auto& cell : cells) {
            total += cell.count.load(std::memory_order_relaxed);
        }
        return total;
    }
};

#include <atomic>
#include <vector>
#include <cstdint>
#include <thread>

class StripedAccumulator {
private:
    struct alignas(64) Cell {
        std::atomic<std::int64_t> value{0};
    };

    std::vector<Cell> cells;
    std::atomic<std::int64_t> base{0};
    const size_t mask;

public:
    explicit StripedAccumulator(size_t num_cells = 16) 
        : cells(num_cells), mask(num_cells - 1) {}

    void add(std::int64_t val, size_t thread_probe) {
        size_t idx = thread_probe & mask;
        cells[idx].value.fetch_add(val, std::memory_order_relaxed);
    }

    std::int64_t sum() const {
        std::int64_t total = base.load(std::memory_order_relaxed);
        for (const auto& cell : cells) {
            total += cell.value.load(std::memory_order_relaxed);
        }
        return total;
    }
};

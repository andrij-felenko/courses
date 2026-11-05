#include <atomic>
#include <vector>
#include <thread>
#include <cstdint>

// Вирівнювання структури за розміром cache line (64 байти) для запобігання false sharing
struct alignas(64) PaddedCell {
    std::atomic<int64_t> value{0};
};

class StripedLongAdder {
private:
    std::atomic<int64_t> base{0};
    std::vector<PaddedCell> cells;
    size_t mask;

public:
    explicit StripedLongAdder(size_t num_cells = 8) : cells(num_cells), mask(num_cells - 1) {}

    void add(int64_t x) {
        int64_t b = base.load(std::memory_order_relaxed);
        // Спроба прискореного оновлення base за відсутності конкуренції
        if (base.compare_exchange_weak(b, b + x, std::memory_order_relaxed)) {
            return;
        }

        // Обчислення локального хешу потоку для вибору комірки
        size_t hash = std::hash<std::thread::id>{}(std::this_thread::get_id());
        size_t idx = hash & mask;

        // Інкремент атомарної комірки
        cells[idx].value.fetch_add(x, std::memory_order_relaxed);
    }

    int64_t sum() const {
        int64_t result = base.load(std::memory_order_relaxed);
        for (const auto& cell : cells) {
            result += cell.value.load(std::memory_order_relaxed);
        }
        return result;
    }
};

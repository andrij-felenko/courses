#include <atomic>
#include <cstdint>
#include <cstddef>
#include <array>

template <size_t MaxCells = 8>
class LongAdderCounter {
private:
    struct alignas(64) Cell {
        std::atomic<uint64_t> value{0};
        uint8_t padding[64 - sizeof(std::atomic<uint64_t>)]{};
    };

    std::atomic<uint64_t> base_{0};
    std::array<Cell, MaxCells> cells_{};
    size_t active_cells_{MaxCells};

public:
    explicit LongAdderCounter(size_t active_cells = MaxCells)
        : active_cells_(active_cells > MaxCells ? MaxCells : active_cells) {}

    void add(uint64_t val, size_t thread_id) noexcept {
        uint64_t b = base_.load(std::memory_order_relaxed);
        if (base_.compare_exchange_weak(b, b + val, std::memory_order_relaxed)) {
            return;
        }

        size_t index = thread_id % active_cells_;
        uint64_t c = cells_[index].value.load(std::memory_order_relaxed);
        while (!cells_[index].value.compare_exchange_weak(c, c + val, std::memory_order_relaxed)) {
            // Оновлення комірки при локальній конкуренції
        }
    }

    void increment(size_t thread_id) noexcept {
        add(1, thread_id);
    }

    [[nodiscard]] uint64_t sum() const noexcept {
        uint64_t total = base_.load(std::memory_order_relaxed);
        for (size_t i = 0; i < active_cells_; ++i) {
            total += cells_[i].value.load(std::memory_order_relaxed);
        }
        return total;
    }
};

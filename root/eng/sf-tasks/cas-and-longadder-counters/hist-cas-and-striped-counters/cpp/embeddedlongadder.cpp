#include <atomic>
#include <cstdint>
#include <array>

template <size_t StripesCount = 4>
class EmbeddedLongAdder {
private:
    static_assert((StripesCount & (StripesCount - 1)) == 0, "StripesCount must be a power of 2");

    struct alignas(64) Cell {
        std::atomic<int64_t> value{0};
    };

    std::array<Cell, StripesCount> cells;
    std::atomic<int64_t> base{0};

    inline size_t get_stripe_index() const noexcept {
        // Отримання ідентифікатора апаратного ядра або потоку RTOS
        uint32_t id = get_current_core_id(); 
        return static_cast<size_t>(id & (StripesCount - 1));
    }

public:
    void add(int64_t x) noexcept {
        size_t idx = get_stripe_index();
        // Використання relaxed memory order для максимальної швидкості
        cells[idx].value.fetch_add(x, std::memory_order_relaxed);
    }

    void increment() noexcept {
        add(1);
    }

    int64_t sum() const noexcept {
        int64_t total = base.load(std::memory_order_relaxed);
        for (const auto& cell : cells) {
            total += cell.value.load(std::memory_order_relaxed);
        }
        return total;
    }
};

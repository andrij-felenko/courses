#include <cstdint>
#include <atomic>
#include <vector>
#include <memory>
#include <new>

// Реалізація високоефективного шардованого лічильника LongAdder мовою C++
class LongAdder {
private:
    static constexpr std::size_t HardwareCacheLineSize = 64;

    // Спеціалізована комірка з гарантованим вирівнюванням на розмір кєш-лінії
    struct alignas(HardwareCacheLineSize) Cell {
        std::atomic<std::int64_t> value{0};

        explicit Cell(std::int64_t val) noexcept : value(val) {}
    };

    alignas(HardwareCacheLineSize) std::atomic<std::int64_t> base_{0};
    alignas(HardwareCacheLineSize) std::atomic<std::uint32_t> cells_busy_{0};
    std::atomic<Cell*> cells_{nullptr};
    std::atomic<std::size_t> cells_capacity_{0};

public:
    LongAdder() noexcept = default;

    ~LongAdder() {
        Cell* cells = cells_.load(std::memory_order_relaxed);
        if (cells != nullptr) {
            delete[] cells;
        }
    }

    LongAdder(const LongAdder&) = delete;
    LongAdder& operator=(const LongAdder&) = delete;

    // Додавання значення х із застосуванням шардингу комірок
    void add(std::int64_t x, std::uint32_t thread_probe) noexcept {
        Cell* cells = cells_.load(std::memory_order_relaxed);

        // Швидкий шлях без колізій над базовим значенням
        if (cells == nullptr) {
            std::int64_t b = base_.load(std::memory_order_relaxed);
            if (base_.compare_exchange_weak(b, b + x, std::memory_order_relaxed)) {
                return;
            }
        }

        // Шардинг: спроба оновлення локальної комірки потоку
        std::size_t cap = cells_capacity_.load(std::memory_order_relaxed);
        if (cells != nullptr && cap > 0) {
            std::size_t idx = thread_probe & (cap - 1);
            Cell& cell = cells[idx];
            std::int64_t v = cell.value.load(std::memory_order_relaxed);
            if (cell.value.compare_exchange_weak(v, v + x, std::memory_order_relaxed)) {
                return;
            }
        }

        // Атомарне оновлення бази при колізіях
        std::int64_t b = base_.load(std::memory_order_relaxed);
        while (!base_.compare_exchange_weak(b, b + x, std::memory_order_release)) {
            // Безблокуюча спроба
        }
    }

    void increment(std::uint32_t thread_probe) noexcept {
        add(1, thread_probe);
    }

    // Отримання підсумкового сумарного значення
    [[nodiscard]] std::int64_t sum() const noexcept {
        std::int64_t total = base_.load(std::memory_order_acquire);
        Cell* cells = cells_.load(std::memory_order_acquire);
        std::size_t cap = cells_capacity_.load(std::memory_order_relaxed);

        if (cells != nullptr) {
            for (std::size_t i = 0; i < cap; ++i) {
                total += cells[i].value.load(std::memory_order_relaxed);
            }
        }
        return total;
    }
};

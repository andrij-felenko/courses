#include <atomic>
#include <array>
#include <cstddef>
#include <new>
#include <optional>

template <typename T, std::size_t Capacity = 1024>
class SpscRingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of 2");
    static constexpr std::size_t Mask = Capacity - 1;
    static constexpr std::size_t CacheLineSize = 64;

public:
    SpscRingBuffer() : head_(0), tail_(0) {}

    // Заборона копіювання для збереження цілісності індексів
    SpscRingBuffer(const SpscRingBuffer&) = delete;
    SpscRingBuffer& operator=(const SpscRingBuffer&) = delete;

    bool push(T item) {
        const std::size_t current_head = head_.load(std::memory_order_relaxed);
        const std::size_t current_tail = tail_.load(std::memory_order_acquire);

        if (current_head - current_tail >= Capacity) {
            return false; // Буфер переповнений
        }

        buffer_[current_head & Mask] = std::move(item);

        // memory_order_release гарантує, що запис у buffer_ зафіксується в пам'яті
        // раніше, ніж споживач побачить оновлений індекс head_
        head_.store(current_head + 1, std::memory_order_release);
        return true;
    }

    std::optional<T> pop() {
        const std::size_t current_tail = tail_.load(std::memory_order_relaxed);
        const std::size_t current_head = head_.load(std::memory_order_acquire);

        if (current_tail == current_head) {
            return std::nullopt; // Буфер порожній
        }

        T item = std::move(buffer_[current_tail & Mask]);

        // memory_order_release повідомляє виробнику про звільнення комірки
        tail_.store(current_tail + 1, std::memory_order_release);
        return item;
    }

private:
    // Масив елементів
    std::array<T, Capacity> buffer_{};

    // Рознесення змінних на окремі кеш-лінії для запобігання False Sharing
    alignas(CacheLineSize) std::atomic<std::size_t> head_;
    alignas(CacheLineSize) std::atomic<std::size_t> tail_;
};

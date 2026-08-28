#include <cstdint>
#include <cstddef>
#include <array>
#include <atomic>
#include <optional>
#include <span>

// Шаблонний безблокувальний SPSC FIFO для сучасного C++20
template <typename T, std::size_t Capacity>
class SpscQueue {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two!");
    static_assert(Capacity >= 2, "Capacity must be at least 2");

public:
    constexpr SpscQueue() noexcept : head_{0}, tail_{0} {}

    // Заборона копіювання та переміщення
    SpscQueue(const SpscQueue&) = delete;
    SpscQueue& operator=(const SpscQueue&) = delete;

    // Виробник: викликається тільки з контексту Producer (наприклад, ISR)
    [[nodiscard]] bool push(const T& item) noexcept {
        const std::size_t current_head = head_.load(std::memory_order_relaxed);
        const std::size_t current_tail = tail_.load(std::memory_order_acquire);

        if ((current_head - current_tail) >= Capacity) {
            return false; // Буфер переповнено
        }

        buffer_[current_head & Mask] = item;
        // Публікація нового елемента з Release semantics
        head_.store(current_head + 1, std::memory_order_release);
        return true;
    }

    // Споживач: викликається тільки з контексту Consumer
    [[nodiscard]] std::optional<T> pop() noexcept {
        const std::size_t current_tail = tail_.load(std::memory_order_relaxed);
        const std::size_t current_head = head_.load(std::memory_order_acquire);

        if (current_head == current_tail) {
            return std::nullopt; // Буфер порожній
        }

        T item = buffer_[current_tail & Mask];
        // Звільнення слота з Release semantics
        tail_.store(current_tail + 1, std::memory_order_release);
        return item;
    }

    [[nodiscard]] bool empty() const noexcept {
        return head_.load(std::memory_order_relaxed) == tail_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] std::size_t size() const noexcept {
        const std::size_t h = head_.load(std::memory_order_relaxed);
        const std::size_t t = tail_.load(std::memory_order_relaxed);
        return (h >= t) ? (h - t) : 0;
    }

private:
    static constexpr std::size_t Mask = Capacity - 1;
    
    // Масив для збереження корисного навантаження
    std::array<T, Capacity> buffer_{};
    
    // Атомарні індекси
    alignas(4) std::atomic<std::size_t> head_;
    alignas(4) std::atomic<std::size_t> tail_;
};

#include <cstdint>
#include <cstddef>
#include <array>
#include <atomic>
#include <optional>
#include <span>
#include <concepts>

template <typename T, size_t Capacity>
requires ((Capacity & (Capacity - 1)) == 0 && Capacity > 1)
class SpscRingBuffer {
public:
    constexpr SpscRingBuffer() : head_(0), tail_(0) {}

    /* Викликається з ISR: запис елемента без блокування */
    bool push_from_isr(const T& item) noexcept {
        const size_t current_head = head_.load(std::memory_order_relaxed);
        const size_t current_tail = tail_.load(std::memory_order_acquire);
        const size_t next_head = (current_head + 1) & kMask;

        if (next_head == current_tail) {
            return false; // Буфер переповнено (Overrun)
        }

        buffer_[current_head] = item;

        // Release-бар'єр: гарантує, що запис buffer_[current_head] завершено
        // до оновлення head_, щоб читач не побачив сміття
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    /* Викликається з основного потоку: читання елемента */
    std::optional<T> pop_from_main() noexcept {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        // Acquire-бар'єр: гарантує актуальність даних у буфері, записаних в ISR
        const size_t current_head = head_.load(std::memory_order_acquire);

        if (current_tail == current_head) {
            return std::nullopt; // Буфер порожній
        }

        T item = buffer_[current_tail];
        tail_.store((current_tail + 1) & kMask, std::memory_order_release);
        return item;
    }

    [[nodiscard]] size_t size() const noexcept {
        const size_t head = head_.load(std::memory_order_relaxed);
        const size_t tail = tail_.load(std::memory_order_relaxed);
        return (head - tail) & kMask;
    }

    [[nodiscard]] bool empty() const noexcept {
        return head_.load(std::memory_order_relaxed) == tail_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] static constexpr size_t capacity() noexcept {
        return Capacity - 1; // 1 слот зарезервовано під умову заповненості
    }

private:
    static constexpr size_t kMask = Capacity - 1;
    
    // Вирівнювання за кеш-лінією для запобігання False Sharing на багатоядерних МК (ESP32/RP2040)
    alignas(64) std::array<T, Capacity> buffer_{};
    alignas(64) std::atomic<size_t> head_{0};
    alignas(64) std::atomic<size_t> tail_{0};
};

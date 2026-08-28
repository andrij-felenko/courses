#include <cstdint>
#include <cstddef>
#include <array>
#include <optional>
#include <atomic>
#include <span>
#include <concepts>

template <std::size_t Capacity>
    requires ((Capacity > 0) && ((Capacity & (Capacity - 1)) == 0))
class LockFreeIsrRingBuffer {
public:
    constexpr LockFreeIsrRingBuffer() noexcept = default;

    /* Заборона копіювання для збереження атомарності */
    LockFreeIsrRingBuffer(const LockFreeIsrRingBuffer&) = delete;
    LockFreeIsrRingBuffer& operator=(const LockFreeIsrRingBuffer&) = delete;

    /* Викликається з обробника переривань (ISR) */
    [[nodiscard]] bool put_from_isr(std::uint8_t byte) noexcept {
        const std::size_t current_head = head_.load(std::memory_order_relaxed);
        const std::size_t next_head = (current_head + 1U) & Mask;

        if (next_head == tail_.load(std::memory_order_acquire)) {
            return false; /* Переповнення буфера */
        }

        storage_[current_head] = byte;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    /* Викликається з фонового потоку */
    [[nodiscard]] std::optional<std::uint8_t> get() noexcept {
        const std::size_t current_tail = tail_.load(std::memory_order_relaxed);

        if (current_tail == head_.load(std::memory_order_acquire)) {
            return std::nullopt; /* Буфер порожній */
        }

        const std::uint8_t byte = storage_[current_tail];
        tail_.store((current_tail + 1U) & Mask, std::memory_order_release);
        return byte;
    }

    [[nodiscard]] bool empty() const noexcept {
        return head_.load(std::memory_order_relaxed) == tail_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] static constexpr std::size_t capacity() noexcept {
        return Capacity;
    }

private:
    static constexpr std::size_t Mask = Capacity - 1U;
    std::array<std::uint8_t, Capacity> storage_{};
    std::atomic<std::size_t> head_{0U};
    std::atomic<std::size_t> tail_{0U};
};

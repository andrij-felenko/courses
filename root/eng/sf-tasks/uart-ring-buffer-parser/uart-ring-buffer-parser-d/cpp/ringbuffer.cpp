#include <cstdint>
#include <cstddef>
#include <array>
#include <atomic>
#include <optional>

template <typename T, std::size_t N>
class RingBuffer {
    static_assert((N & (N - 1)) == 0, "Capacity N must be a power of two!");
public:
    constexpr RingBuffer() : head_(0), tail_(0) {}

    bool push(T item) noexcept {
        const std::size_t current_head = head_.load(std::memory_order_relaxed);
        const std::size_t next_head = (current_head + 1U) & Mask;
        if (next_head == tail_.load(std::memory_order_acquire)) {
            return false; // Буфер переповнений
        }
        buffer_[current_head] = item;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    std::optional<T> pop() noexcept {
        const std::size_t current_tail = tail_.load(std::memory_order_relaxed);
        if (current_tail == head_.load(std::memory_order_acquire)) {
            return std::nullopt; // Буфер порожній
        }
        T item = buffer_[current_tail];
        tail_.store((current_tail + 1U) & Mask, std::memory_order_release);
        return item;
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return (head_.load(std::memory_order_relaxed) - tail_.load(std::memory_order_relaxed)) & Mask;
    }

private:
    static constexpr std::size_t Mask = N - 1U;
    std::array<T, N> buffer_{};
    std::atomic<std::size_t> head_{0};
    std::atomic<std::size_t> tail_{0};
};

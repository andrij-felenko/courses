#include <cstdint>
#include <cstddef>
#include <array>
#include <atomic>

template <typename T, std::size_t Size>
class UartRingBuffer {
    static_assert((Size & (Size - 1)) == 0, "Розмір буфера повинен бути степенем двійки!");

public:
    UartRingBuffer() : head_(0), tail_(0) {}

    [[nodiscard]] bool is_empty() const noexcept {
        return head_.load(std::memory_order_relaxed) == tail_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] bool is_full() const noexcept {
        const std::size_t next_head = (head_.load(std::memory_order_relaxed) + 1) & mask_;
        return next_head == tail_.load(std::memory_order_acquire);
    }

    bool put(T item) noexcept {
        const std::size_t current_head = head_.load(std::memory_order_relaxed);
        const std::size_t next_head = (current_head + 1) & mask_;
        if (next_head == tail_.load(std::memory_order_acquire)) {
            return false; // Буфер заповнений
        }
        buffer_[current_head] = item;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    bool get(T& item) noexcept {
        const std::size_t current_tail = tail_.load(std::memory_order_relaxed);
        if (current_tail == head_.load(std::memory_order_acquire)) {
            return false; // Буфер порожній
        }
        item = buffer_[current_tail];
        tail_.store((current_tail + 1) & mask_, std::memory_order_release);
        return true;
    }

    [[nodiscard]] std::size_t count() const noexcept {
        return (head_.load(std::memory_order_relaxed) - tail_.load(std::memory_order_relaxed)) & mask_;
    }

private:
    std::array<T, Size> buffer_{};
    static constexpr std::size_t mask_ = Size - 1;
    std::atomic<std::size_t> head_{0};
    std::atomic<std::size_t> tail_{0};
};

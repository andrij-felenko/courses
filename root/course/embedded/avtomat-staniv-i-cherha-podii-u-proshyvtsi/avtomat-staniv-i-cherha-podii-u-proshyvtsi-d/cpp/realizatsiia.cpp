#include <cstdint>
#include <array>
#include <optional>
#include <atomic>

template <typename EventType, size_t Capacity = 16>
class EventQueue {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of 2");

public:
    constexpr EventQueue() : head_(0), tail_(0) {}

    // Виклик з ISR
    bool push(const EventType& event) noexcept {
        const size_t current_head = head_.load(std::memory_order_relaxed);
        const size_t next_head = (current_head + 1) & (Capacity - 1);

        if (next_head == tail_.load(std::memory_order_acquire)) {
            return false; // Черга переповнена
        }

        buffer_[current_head] = event;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    // Виклик з головного циклу
    std::optional<EventType> pop() noexcept {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);

        if (current_tail == head_.load(std::memory_order_acquire)) {
            return std::nullopt; // Черга порожня
        }

        EventType event = buffer_[current_tail];
        tail_.store((current_tail + 1) & (Capacity - 1), std::memory_order_release);
        return event;
    }

    [[nodiscard]] bool empty() const noexcept {
        return head_.load(std::memory_order_relaxed) == tail_.load(std::memory_order_relaxed);
    }

private:
    std::array<EventType, Capacity> buffer_{};
    std::atomic<size_t> head_{0};
    std::atomic<size_t> tail_{0};
};

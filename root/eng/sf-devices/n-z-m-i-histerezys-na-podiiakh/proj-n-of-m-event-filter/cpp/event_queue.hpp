/**
 * @file event_queue.hpp
 * @brief C++20 потокобезпечна черга міток часу
 */

#pragma once

#include <cstdint>
#include <array>
#include <atomic>
#include <optional>

namespace embedded::queue {

template <std::size_t Capacity = 64>
    requires ((Capacity & (Capacity - 1)) == 0 && Capacity >= 2)
class SpscEventQueue final {
public:
    struct Event {
        uint32_t timestamp_us{0};
        uint8_t  channel_id{0};
        bool     edge_level{false};
    };

    bool Push(uint8_t ch, bool level, uint32_t ts) noexcept {
        const auto head = head_.load(std::memory_order_relaxed);
        const auto next_head = (head + 1) & Mask;

        if (next_head == tail_.load(std::memory_order_acquire)) {
            return false; // Черга заповнена
        }

        buffer_[head] = Event{ts, ch, level};
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    [[nodiscard]] std::optional<Event> Pop() noexcept {
        const auto tail = tail_.load(std::memory_order_relaxed);
        if (tail == head_.load(std::memory_order_acquire)) {
            return std::nullopt; // Порожньо
        }

        Event ev = buffer_[tail];
        tail_.store((tail + 1) & Mask, std::memory_order_release);
        return ev;
    }

private:
    static constexpr std::size_t Mask = Capacity - 1;
    std::array<Event, Capacity> buffer_{};
    std::atomic<std::size_t> head_{0};
    std::atomic<std::size_t> tail_{0};
};

} // namespace embedded::queue

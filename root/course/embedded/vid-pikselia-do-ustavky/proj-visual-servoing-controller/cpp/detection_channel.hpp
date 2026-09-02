#pragma once

#include <atomic>
#include <array>
#include <cstddef>
#include <optional>

namespace servo {

/* Канал детекцій між потоком зору і контуром керування: один виробник,
 * один споживач, без замків. Контур реального часу не має права заснути
 * на м'ютексі, який захопив потік інференсу.
 *
 * Черга свідомо коротка: детекція, що пролежала півсекунди, вже не потрібна,
 * а глибока черга лише ховала б відставання споживача. */
template <typename T, std::size_t Capacity = 16>
    requires ((Capacity & (Capacity - 1)) == 0)
class SpscChannel {
public:
    /* Викликає ЛИШЕ потік зору. */
    bool push(const T& value) noexcept {
        const auto tail = tail_.load(std::memory_order_relaxed);
        if (tail - head_.load(std::memory_order_acquire) >= Capacity) {
            dropped_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }
        slots_[tail & kMask] = value;
        tail_.store(tail + 1, std::memory_order_release);   /* слот видно раніше за tail */
        return true;
    }

    /* Викликає ЛИШЕ контур керування. */
    [[nodiscard]] std::optional<T> pop() noexcept {
        const auto head = head_.load(std::memory_order_relaxed);
        if (head == tail_.load(std::memory_order_acquire)) {
            return std::nullopt;
        }
        T value = slots_[head & kMask];
        head_.store(head + 1, std::memory_order_release);
        return value;
    }

    [[nodiscard]] unsigned dropped() const noexcept {
        return dropped_.load(std::memory_order_relaxed);
    }

private:
    static constexpr std::size_t kMask = Capacity - 1;

    std::array<T, Capacity> slots_{};
    std::atomic<std::size_t> head_{0};
    std::atomic<std::size_t> tail_{0};
    std::atomic<unsigned> dropped_{0};
};

}  // namespace servo

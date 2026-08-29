#pragma once

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace linkmux {

// Кільце «один пише — один читає»: продюсер це переривання приймача,
// консюмер — задача арбітра. Індекси ростуть без обгортання, у слот
// перетворюються маскою, тому «повне» і «порожнє» розрізняються самі собою.
template <typename T, std::size_t Capacity>
class SpscRing {
    static_assert(Capacity >= 2 && (Capacity & (Capacity - 1)) == 0,
                  "місткість мусить бути степенем двійки");

public:
    // Контекст переривання: head рухає лише цей бік
    bool push(const T& item) noexcept {
        const auto head = head_.load(std::memory_order_relaxed);
        const auto tail = tail_.load(std::memory_order_acquire);
        if (head - tail >= Capacity) {
            ++overruns_;   // задача не встигла: кадр гине тут, а не псує чергу
            return false;
        }
        slots_[head & kMask] = item;
        // release: вміст слота мусить стати видимим раніше за новий head
        head_.store(head + 1, std::memory_order_release);
        return true;
    }

    // Контекст задачі: порожньо — це не помилка, тому optional, а не код
    [[nodiscard]] std::optional<T> pop() noexcept {
        const auto tail = tail_.load(std::memory_order_relaxed);
        const auto head = head_.load(std::memory_order_acquire);
        if (head == tail) {
            return std::nullopt;
        }
        T item = slots_[tail & kMask];
        tail_.store(tail + 1, std::memory_order_release);
        return item;
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return head_.load(std::memory_order_relaxed) - tail_.load(std::memory_order_relaxed);
    }
    [[nodiscard]] std::uint32_t overruns() const noexcept { return overruns_; }

private:
    static constexpr std::size_t kMask = Capacity - 1;

    std::array<T, Capacity>  slots_{};
    std::atomic<std::size_t> head_{0};
    std::atomic<std::size_t> tail_{0};
    std::uint32_t            overruns_{0};
};

}  // namespace linkmux

#include <atomic>
#include <array>
#include <cstddef>
#include <optional>

template <typename T, std::size_t Capacity = 1024>
class SpscQueue {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of 2");
    static constexpr std::size_t Mask = Capacity - 1;

public:
    bool push(T item) {
        const std::size_t h = head_.load(std::memory_order_relaxed);
        const std::size_t t = tail_.load(std::memory_order_acquire);

        if (h - t >= Capacity) return false;

        buffer_[h & Mask] = std::move(item);
        head_.store(h + 1, std::memory_order_release);
        return true;
    }

    std::optional<T> pop() {
        const std::size_t t = tail_.load(std::memory_order_relaxed);
        const std::size_t h = head_.load(std::memory_order_acquire);

        if (t == h) return std::nullopt;

        T item = std::move(buffer_[t & Mask]);
        tail_.store(t + 1, std::memory_order_release);
        return item;
    }

private:
    std::array<T, Capacity> buffer_{};
    alignas(64) std::atomic<std::size_t> head_{0};
    alignas(64) std::atomic<std::size_t> tail_{0};
};

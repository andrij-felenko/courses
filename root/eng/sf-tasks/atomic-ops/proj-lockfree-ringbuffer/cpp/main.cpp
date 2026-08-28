#include <atomic>
#include <cstddef>
#include <new>
#include <optional>
#include <utility>
#include <vector>

template <typename T, std::size_t Capacity>
class LockFreeRingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two");

public:
    LockFreeRingBuffer() : head_(0), tail_(0) {
        buffer_.resize(Capacity);
    }

    template <typename... Args>
    bool push(Args&&... args) {
        const std::size_t head = head_.load(std::memory_order_relaxed);
        const std::size_t tail = tail_.load(std::memory_order_acquire);

        if ((head - tail) >= Capacity) {
            return false; // Буфер переповнений
        }

        buffer_[head & (Capacity - 1)] = T(std::forward<Args>(args)...);
        head_.store(head + 1, std::memory_order_release);
        return true;
    }

    std::optional<T> pop() {
        const std::size_t tail = tail_.load(std::memory_order_relaxed);
        const std::size_t head = head_.load(std::memory_order_acquire);

        if (tail == head) {
            return std::nullopt; // Буфер порожній
        }

        T item = std::move(buffer_[tail & (Capacity - 1)]);
        tail_.store(tail + 1, std::memory_order_release);
        return item;
    }

private:
    std::vector<T> buffer_;
    
    // Запобігаємо False Sharing між Producer та Consumer
    alignas(64) std::atomic<std::size_t> head_;
    alignas(64) std::atomic<std::size_t> tail_;
};

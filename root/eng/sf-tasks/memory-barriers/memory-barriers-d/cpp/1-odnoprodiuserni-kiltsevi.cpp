// SPSC кільцевий буфер мовою C++17 (std::atomic, std::optional)
#include <atomic>
#include <vector>
#include <optional>

template <typename T, size_t Size>
class SPSCQueue {
private:
    std::vector<T> buffer_ = std::vector<T>(Size);
    alignas(64) std::atomic<size_t> head_{0};
    alignas(64) std::atomic<size_t> tail_{0};

public:
    bool enqueue(T val) {
        size_t head = head_.load(std::memory_order_relaxed);
        size_t tail = tail_.load(std::memory_order_acquire);

        if ((head - tail) >= Size)
            return false;

        buffer_[head % Size] = std::move(val);
        head_.store(head + 1, std::memory_order_release);
        return true;
    }

    std::optional<T> dequeue() {
        size_t tail = tail_.load(std::memory_order_relaxed);
        size_t head = head_.load(std::memory_order_acquire);

        if (tail == head)
            return std::nullopt;

        T val = std::move(buffer_[tail % Size]);
        tail_.store(tail + 1, std::memory_order_release);
        return val;
    }
};

template <typename T, size_t Size>
requires ((Size & (Size - 1)) == 0)
class SpscQueue {
public:
    bool push(const T& sample) noexcept {
        const size_t currentHead = head_.load(std::memory_order_relaxed);
        const size_t nextHead = (currentHead + 1) & (Size - 1);
        if (nextHead == tail_.load(std::memory_order_acquire)) {
            return false;
        }
        buffer_[currentHead] = sample;
        head_.store(nextHead, std::memory_order_release);
        return true;
    }

    std::optional<T> pop() noexcept {
        const size_t currentTail = tail_.load(std::memory_order_relaxed);
        if (currentTail == head_.load(std::memory_order_acquire)) {
            return std::nullopt;
        }
        T item = buffer_[currentTail];
        tail_.store((currentTail + 1) & (Size - 1), std::memory_order_release);
        return item;
    }
private:
    std::array<T, Size> buffer_{};
    std::atomic<size_t> head_{0};
    std::atomic<size_t> tail_{0};
};

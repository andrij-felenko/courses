#include <cstdint>
#include <array>
#include <optional>

template <typename T, size_t Capacity>
class LockFreeEventQueue {
public:
    constexpr LockFreeEventQueue() = default;

    bool post(const T& item) noexcept {
        // На мікроконтролері огортається в збереження регістру PRIMASK
        if (count_ >= Capacity) {
            overflow_drops_++;
            return false;
        }
        buffer_[head_] = item;
        head_ = (head_ + 1) % Capacity;
        count_++;
        return true;
    }

    std::optional<T> pop() noexcept {
        if (count_ == 0) {
            return std::nullopt;
        }
        T item = buffer_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        count_--;
        return item;
    }

    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] bool empty() const noexcept { return count_ == 0; }
    [[nodiscard]] uint32_t drops() const noexcept { return overflow_drops_; }

private:
    std::array<T, Capacity> buffer_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
    volatile size_t count_{0};
    uint32_t overflow_drops_{0};
};

#include <cstdint>
#include <array>
#include <optional>

template <typename EventType, size_t Capacity>
class StaticEventQueue {
public:
    StaticEventQueue() : head_{0}, tail_{0}, count_{0}, max_usage_{0} {}

    bool push(const EventType& e) {
        CriticalSectionGuard guard;
        if (count_ >= Capacity) {
            return false;
        }

        ring_[head_] = e;
        head_ = (head_ + 1) % Capacity;
        ++count_;

        if (count_ > max_usage_) {
            max_usage_ = count_;
        }
        return true;
    }

    std::optional<EventType> pop() {
        CriticalSectionGuard guard;
        if (count_ == 0) {
            return std::nullopt;
        }

        EventType e = ring_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        --count_;
        return e;
    }

    [[nodiscard]] size_t max_usage() const {
        CriticalSectionGuard guard;
        return max_usage_;
    }

private:
    struct CriticalSectionGuard {
        uint32_t primask_;
        CriticalSectionGuard() {
            __asm__ volatile (
                "mrs %0, primask\n"
                "cpsid i\n"
                : "=r" (primask_) :: "memory"
            );
        }
        ~CriticalSectionGuard() {
            __asm__ volatile (
                "msr primask, %0\n"
                ::: "memory"
            );
        }
    };

    std::array<EventType, Capacity> ring_{};
    size_t head_{0};
    size_t tail_{0};
    size_t count_{0};
    size_t max_usage_{0};
};

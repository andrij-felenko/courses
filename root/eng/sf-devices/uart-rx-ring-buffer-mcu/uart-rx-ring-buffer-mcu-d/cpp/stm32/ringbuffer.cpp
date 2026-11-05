#include <cstdint>
#include <cstddef>

template <size_t Capacity>
class RingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of 2");

public:
    enum class Status { Ok, Empty, Full };

    RingBuffer() : head_(0), tail_(0) {}

    Status PushFromIsr(uint8_t data) {
        size_t next_head = (head_ + 1) & mask_;
        if (next_head == tail_) {
            return Status::Full;
        }
        buffer_[head_] = data;
        head_ = next_head;
        return Status::Ok;
    }

    Status Pop(uint8_t &data) {
        if (head_ == tail_) {
            return Status::Empty;
        }
        data = buffer_[tail_];
        tail_ = (tail_ + 1) & mask_;
        return Status::Ok;
    }

    size_t Available() const {
        return (head_ - tail_) & mask_;
    }

private:
    uint8_t buffer_[Capacity];
    static constexpr size_t mask_ = Capacity - 1;
    volatile size_t head_;
    volatile size_t tail_;
};

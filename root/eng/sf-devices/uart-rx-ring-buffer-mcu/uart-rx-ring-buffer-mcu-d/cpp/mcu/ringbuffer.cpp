#include <cstdint>
#include <cstddef>

template <typename T, std::size_t Size>
class RingBuffer {
    static_assert((Size & (Size - 1)) == 0, "Розмір буфера мусить бути степенем двійки!");
private:
    uint8_t buffer_[Size];
    volatile std::size_t head_{0};
    volatile std::size_t tail_{0};
    static constexpr std::size_t Mask = Size - 1;

public:
    constexpr RingBuffer() = default;

    bool push(T data) noexcept {
        std::size_t next_head = (head_ + 1) & Mask;
        if (next_head == tail_) {
            return false; /* Переповнення буфера */
        }
        buffer_[head_] = data;
        head_ = next_head;
        return true;
    }

    bool pop(T& data) noexcept {
        if (head_ == tail_) {
            return false; /* Порожній буфер */
        }
        data = buffer_[tail_];
        tail_ = (tail_ + 1) & Mask;
        return true;
    }

    [[nodiscard]] std::size_t available() const noexcept {
        return (head_ - tail_) & Mask;
    }
};

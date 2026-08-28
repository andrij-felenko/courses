// Інкапсульований нуль-копіювальний кільцевий буфер (C++)
#include <cstdint>
#include <cstddef>
#include <array>
#include <optional>

template <size_t Capacity = 256>
class RingBuffer {
public:
    constexpr RingBuffer() noexcept = default;

    [[nodiscard]] bool push(uint8_t byte) noexcept {
        const size_t next = (head_ + 1) % Capacity;
        if (next == tail_) {
            return false; // Переповнення буфера
        }
        storage_[head_] = byte;
        head_ = next;
        return true;
    }

    [[nodiscard]] std::optional<uint8_t> pop() noexcept {
        if (head_ == tail_) {
            return std::nullopt; // Буфер порожній
        }
        const uint8_t byte = storage_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        return byte;
    }

    [[nodiscard]] size_t available() const noexcept {
        return (head_ >= tail_) ? (head_ - tail_) : (Capacity - tail_ + head_);
    }

private:
    std::array<uint8_t, Capacity> storage_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
};

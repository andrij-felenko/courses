#include <cstdint>
#include <cstddef>
#include <atomic>
#include <array>

template <size_t Size = 256>
class UartRingBuffer {
    static_assert((Size & (Size - 1)) == 0, "Розмір буфера має бути степенем двійки");

public:
    UartRingBuffer() : head_(0), tail_(0) {}

    bool put(uint8_t data) {
        const size_t current_head = head_.load(std::memory_order_relaxed);
        const size_t next_head = (current_head + 1) & (Size - 1);

        // Перевірка на переповнення з семантикою Acquire для читання tail
        if (next_head == tail_.load(std::memory_order_acquire)) {
            return false;
        }

        buffer_[current_head] = data;
        // Публікація нового head із семантикою Release
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    bool get(uint8_t &data) {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        // Читання head із семантикою Acquire
        const size_t current_head = head_.load(std::memory_order_acquire);

        if (current_tail == current_head) {
            return false;
        }

        data = buffer_[current_tail];
        // Оновлення tail із семантикою Release
        tail_.store((current_tail + 1) & (Size - 1), std::memory_order_release);
        return true;
    }

private:
    std::array<uint8_t, Size> buffer_;
    std::atomic<size_t> head_;
    std::atomic<size_t> tail_;
};

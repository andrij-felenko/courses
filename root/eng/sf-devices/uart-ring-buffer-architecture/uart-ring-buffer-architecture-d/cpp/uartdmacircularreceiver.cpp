#include <cstdint>
#include <cstddef>
#include <algorithm>

template <std::size_t BufferSize>
class UartDmaCircularReceiver {
    static_assert((BufferSize & (BufferSize - 1)) == 0, "Розмір буфера повинен бути степенем двійки");

public:
    UartDmaCircularReceiver() : old_head_(0), tail_(0) {}

    // Обробка події Idle Line з передачею поточного лічильника DMA NDTR
    void handle_idle_event(std::size_t dma_ndtr) {
        const std::size_t current_head = BufferSize - dma_ndtr;
        if (current_head != old_head_) {
            old_head_ = current_head;
            // Повідомити обробник про оновлення вказівника
        }
    }

    std::size_t read(uint8_t* dest, std::size_t max_len) {
        std::size_t count = 0;
        while ((tail_ != old_head_) && (count < max_len)) {
            dest[count] = buffer_[tail_];
            tail_ = (tail_ + 1) & Mask;
            count++;
        }
        return count;
    }

    uint8_t* get_raw_buffer() { return buffer_; }
    constexpr std::size_t get_size() const { return BufferSize; }

private:
    static constexpr std::size_t Mask = BufferSize - 1;
    alignas(32) uint8_t buffer_[BufferSize]; // Вирівнювання для сумісності з кешем/MPU
    volatile std::size_t old_head_;
    std::size_t tail_;
};

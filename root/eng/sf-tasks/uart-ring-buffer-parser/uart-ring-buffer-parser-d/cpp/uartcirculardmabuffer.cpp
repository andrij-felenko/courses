#include <cstdint>
#include <atomic>
#include <array>

template <std::size_t N>
class UartCircularDmaBuffer {
    static_assert((N & (N - 1)) == 0, "Buffer size must be a power of two!");
public:
    constexpr UartCircularDmaBuffer() : head_(0), tail_(0) {}

    /* Оновлення позиції head за даними апаратного лічильника DMA */
    void update_head_from_dma(std::size_t dma_ndtr) noexcept {
        std::size_t dma_head = (N - dma_ndtr) & Mask;
        head_.store(dma_head, std::memory_order_release);
    }

    /* Отримання чергового байта споживачем */
    bool pop(uint8_t& byte) noexcept {
        const std::size_t current_tail = tail_.load(std::memory_order_relaxed);
        if (current_tail == head_.load(std::memory_order_acquire)) {
            return false; // Порожній буфер
        }
        byte = buffer_[current_tail];
        tail_.store((current_tail + 1U) & Mask, std::memory_order_release);
        return true;
    }

    uint8_t* raw_buffer() noexcept { return buffer_.data(); }

private:
    static constexpr std::size_t Mask = N - 1U;
    alignas(32) std::array<uint8_t, N> buffer_{}; // Вирівнювання для D-Cache
    std::atomic<std::size_t> head_{0};
    std::atomic<std::size_t> tail_{0};
};

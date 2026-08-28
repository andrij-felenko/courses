#include <cstdint>
#include <cstddef>
#include <array>
#include <atomic>
#include <span>
#include <optional>

template <size_t CapacityPowerOfTwo>
class LockFreeRingBuffer {
    static_assert((CapacityPowerOfTwo & (CapacityPowerOfTwo - 1)) == 0, "Capacity must be a power of two");
    static constexpr size_t Mask = CapacityPowerOfTwo - 1;

private:
    alignas(4) std::array<uint8_t, CapacityPowerOfTwo> storage_{};
    alignas(4) std::atomic<size_t> head_{0};
    alignas(4) std::atomic<size_t> tail_{0};

public:
    constexpr LockFreeRingBuffer() noexcept = default;

    [[nodiscard]] bool push_from_isr(uint8_t byte) noexcept {
        const size_t current_head = head_.load(std::memory_order_relaxed);
        const size_t current_tail = tail_.load(std::memory_order_acquire);

        if ((current_head - current_tail) >= CapacityPowerOfTwo) {
            return false; // Overflow
        }

        storage_[current_head & Mask] = byte;
        head_.store(current_head + 1, std::memory_order_release);
        return true;
    }

    [[nodiscard]] std::optional<uint8_t> pop() noexcept {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        const size_t current_head = head_.load(std::memory_order_acquire);

        if (current_head == current_tail) {
            return std::nullopt; // Empty
        }

        const uint8_t byte = storage_[current_tail & Mask];
        tail_.store(current_tail + 1, std::memory_order_release);
        return byte;
    }

    [[nodiscard]] size_t size() const noexcept {
        const size_t current_head = head_.load(std::memory_order_relaxed);
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        return (current_head >= current_tail) ? (current_head - current_tail) : 0;
    }

    [[nodiscard]] bool empty() const noexcept {
        return size() == 0;
    }
};

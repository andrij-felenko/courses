#include <cstdint>
#include <cstddef>
#include <array>
#include <atomic>

template <size_t SizePowerOfTwo>
class FastLockFreeFifo {
    static constexpr size_t Mask = SizePowerOfTwo - 1;

private:
    std::array<uint8_t, SizePowerOfTwo> buffer_{};
    alignas(4) std::atomic<size_t> head_{0};
    alignas(4) std::atomic<size_t> tail_{0};

public:
    constexpr FastLockFreeFifo() noexcept = default;

    [[nodiscard]] bool put(uint8_t byte) noexcept {
        const size_t h = head_.load(std::memory_order_relaxed);
        const size_t t = tail_.load(std::memory_order_acquire);
        if ((h - t) >= SizePowerOfTwo) return false;
        buffer_[h & Mask] = byte;
        head_.store(h + 1, std::memory_order_release);
        return true;
    }
};

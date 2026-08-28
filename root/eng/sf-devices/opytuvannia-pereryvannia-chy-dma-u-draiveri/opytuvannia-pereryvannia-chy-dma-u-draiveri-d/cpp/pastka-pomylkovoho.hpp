#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <cstring>

extern "C" {
    void SCB_CleanDCache_by_Addr(uint32_t *addr, int32_t dsize);
    void SCB_InvalidateDCache_by_Addr(uint32_t *addr, int32_t dsize);
}

namespace DriverUtils {
    constexpr size_t CacheLineSize = 32;

    template <size_t N>
    constexpr size_t align_to_cache_line() noexcept {
        return (N + CacheLineSize - 1) & ~(CacheLineSize - 1);
    }
}

template <size_t PayloadSize>
class CacheCoherentDmaBuffer {
    static constexpr size_t AlignedCapacity = DriverUtils::align_to_cache_line<PayloadSize>();

private:
    alignas(32) std::array<uint8_t, AlignedCapacity> storage_{};

public:
    constexpr CacheCoherentDmaBuffer() noexcept = default;

    [[nodiscard]] uint8_t* data() noexcept { return storage_.data(); }
    [[nodiscard]] const uint8_t* data() const noexcept { return storage_.data(); }
    [[nodiscard]] constexpr size_t capacity() const noexcept { return AlignedCapacity; }

    void flush_for_tx() noexcept {
        auto* addr = reinterpret_cast<uint32_t*>(storage_.data());
        SCB_CleanDCache_by_Addr(addr, static_cast<int32_t>(AlignedCapacity));
        asm volatile ("dsb" ::: "memory");
    }

    void invalidate_for_rx() noexcept {
        auto* addr = reinterpret_cast<uint32_t*>(storage_.data());
        SCB_InvalidateDCache_by_Addr(addr, static_cast<int32_t>(AlignedCapacity));
        asm volatile ("dsb" ::: "memory");
    }
};

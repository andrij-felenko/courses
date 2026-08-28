#include <cstdint>
#include <cstddef>
#include <span>

void speculative_leak(size_t untrusted_index,
                      std::span<const uint8_t> array1,
                      std::span<const uint8_t> array2) noexcept {
    if (untrusted_index < array1.size()) {
        const uint8_t secret = array1[untrusted_index];
        [[maybe_unused]] volatile uint8_t dummy = array2[secret * 64];
    }
}

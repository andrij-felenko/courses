#include <cstdint>
#include <cstddef>
#include <span>
#include <atomic>

namespace crypto::memory {

/* Безпечне стирання чутливих даних із пам'яті */
void secure_cleanse(std::span<uint8_t> buffer) noexcept {
    volatile uint8_t *p = buffer.data();
    for (size_t i = 0; i < buffer.size(); ++i) {
        p[i] = 0;
    }
    #if defined(__GNUC__) || defined(__clang__)
    asm volatile ("" : : "r" (buffer.data()) : "memory");
    #endif
}

} // namespace crypto::memory

#include <span>
#include <cstdint>
#include <atomic>

template <typename T, size_t N>
void secure_memzero(std::span<T, N> buffer) noexcept {
    auto* ptr = static_cast<volatile uint8_t*>(static_cast<void*>(buffer.data()));
    size_t bytes = buffer.size_bytes();
    while (bytes--) {
        *ptr++ = 0;
    }
    std::atomic_signal_fence(std::memory_order_seq_cst);
}

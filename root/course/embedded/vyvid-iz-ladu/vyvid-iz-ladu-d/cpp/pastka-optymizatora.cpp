/* Безпечне затирання пам'яті в C++ через std::span та бар'єр компілятора */
template <typename T, size_t Extent>
void secure_memzero(std::span<T, Extent> buffer) noexcept {
    volatile auto* p = reinterpret_cast<volatile uint8_t*>(buffer.data());
    size_t bytes = buffer.size_bytes();
    while (bytes--) {
        *p++ = 0x00;
    }
    __asm__ __volatile__("" : : "r"(buffer.data()) : "memory");
}

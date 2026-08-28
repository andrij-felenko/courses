// Запис 48-бітного числа в буфер (little-endian)
constexpr void packUint48(std::span<uint8_t, 6> buf, uint64_t val) noexcept {
    for (size_t i = 0; i < 6; ++i) {
        buf[i] = static_cast<uint8_t>((val >> (i * 8)) & 0xFF);
    }
}

// Читання 48-бітного числа з буфера (little-endian)
[[nodiscard]] constexpr uint64_t unpackUint48(std::span<const uint8_t, 6> buf) noexcept {
    uint64_t res = 0;
    for (size_t i = 0; i < 6; ++i) {
        res |= (static_cast<uint64_t>(buf[i]) << (i * 8));
    }
    return res;
}

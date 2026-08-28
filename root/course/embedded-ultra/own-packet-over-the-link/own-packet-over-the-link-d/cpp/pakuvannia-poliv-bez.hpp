/* Безпечна серіалізація мовою C++ через std::span */
inline void packUint16Le(std::span<std::uint8_t> buf, std::uint16_t val) noexcept {
    buf[0] = static_cast<std::uint8_t>(val & 0xFF);
    buf[1] = static_cast<std::uint8_t>((val >> 8) & 0xFF);
}

inline void packUint32Le(std::span<std::uint8_t> buf, std::uint32_t val) noexcept {
    buf[0] = static_cast<std::uint8_t>(val & 0xFF);
    buf[1] = static_cast<std::uint8_t>((val >> 8) & 0xFF);
    buf[2] = static_cast<std::uint8_t>((val >> 16) & 0xFF);
    buf[3] = static_cast<std::uint8_t>((val >> 24) & 0xFF);
}

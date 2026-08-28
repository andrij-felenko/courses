// Ідіоматичний потоковий декодер UTF-8 на C++20
#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>

struct Utf8DecodeResult {
    char32_t code_point{0xFFFD};
    size_t   bytes_consumed{1};
};

[[nodiscard]] constexpr Utf8DecodeResult utf8_decode_next(std::span<const uint8_t> bytes) noexcept {
    if (bytes.empty()) return {0xFFFD, 0};
    
    uint8_t b0 = bytes[0];
    if (b0 < 0x80) {
        return {static_cast<char32_t>(b0), 1};
    }
    
    char32_t cp = 0;
    size_t needed = 0;
    
    if ((b0 & 0xE0) == 0xC0) {
        cp = b0 & 0x1F;
        needed = 1;
        if (cp < 0x02) return {0xFFFD, 1}; // Overlong
    } else if ((b0 & 0xF0) == 0xE0) {
        cp = b0 & 0x0F;
        needed = 2;
    } else if ((b0 & 0xF8) == 0xF0) {
        cp = b0 & 0x07;
        needed = 3;
        if (cp > 0x04) return {0xFFFD, 1}; // Out of range (> U+10FFFF)
    } else {
        return {0xFFFD, 1}; // Invalid lead byte
    }
    
    if (bytes.size() < 1 + needed) {
        return {0xFFFD, bytes.size()}; // Truncated
    }
    
    for (size_t i = 1; i <= needed; ++i) {
        uint8_t bi = bytes[i];
        if ((bi & 0xC0) != 0x80) {
            return {0xFFFD, i}; // Invalid continuation byte
        }
        cp = (cp << 6) | (bi & 0x3F);
    }
    
    if ((cp >= 0xD800 && cp <= 0xDFFF) || (needed == 2 && cp < 0x0800) || (needed == 3 && cp < 0x10000)) {
        return {0xFFFD, 1 + needed};
    }
    
    return {cp, 1 + needed};
}

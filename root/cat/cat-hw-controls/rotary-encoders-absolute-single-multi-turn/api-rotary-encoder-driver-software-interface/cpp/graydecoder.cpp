#include <cstdint>

class GrayDecoder {
public:
    // Оптимізоване 32-бітне перетворення коду Ґрея
    static constexpr uint32_t toBinary(uint32_t gray) noexcept {
        gray ^= (gray >> 1);
        gray ^= (gray >> 2);
        gray ^= (gray >> 4);
        gray ^= (gray >> 8);
        gray ^= (gray >> 16);
        return gray;
    }

    // Універсальний маскований метод для заданої бітової ширини
    static constexpr uint32_t toBinary(uint32_t gray, uint8_t bitWidth) noexcept {
        uint32_t binary = gray;
        for (uint32_t shift = 1; shift < bitWidth; shift <<= 1) {
            binary ^= (binary >> shift);
        }
        return binary & ((1ULL << bitWidth) - 1);
    }
};

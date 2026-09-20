#include <cstdint>

class DipFieldExtractor {
public:
    static constexpr std::uint8_t makeMask(std::uint8_t width, std::uint8_t shift) {
        return static_cast<std::uint8_t>(((1U << width) - 1U) << shift);
    }

    static std::uint8_t extractField(std::uint8_t norm_byte, std::uint8_t width, std::uint8_t shift) {
        std::uint8_t mask = makeMask(width, shift);
        return static_cast<std::uint8_t>((norm_byte & mask) >> shift);
    }

    static bool extractFlag(std::uint8_t norm_byte, std::uint8_t bit_index) {
        return (norm_byte & (1U << bit_index)) != 0;
    }
};

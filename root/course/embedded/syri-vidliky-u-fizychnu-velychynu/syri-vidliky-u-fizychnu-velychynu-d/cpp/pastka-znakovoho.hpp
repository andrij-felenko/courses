#include <cstdint>
#include <array>
#include <span>

namespace sensor {

struct Vector3i16 {
    int16_t x{0};
    int16_t y{0};
    int16_t z{0};
};

class RawFrameParser {
public:
    // Розбір кадру з лівим вирівнюванням (Left-aligned)
    [[nodiscard]] static constexpr Vector3i16 parse_left_aligned(std::span<const uint8_t, 6> buf) noexcept {
        auto assemble = [](uint8_t lsb, uint8_t msb) constexpr -> int16_t {
            const auto raw = static_cast<int16_t>(static_cast<uint16_t>(lsb) | 
                                                 (static_cast<uint16_t>(msb) << 8));
            return static_cast<int16_t>(raw >> 4);
        };

        return Vector3i16{
            .x = assemble(buf[0], buf[1]),
            .y = assemble(buf[2], buf[3]),
            .z = assemble(buf[4], buf[5])
        };
    }

    // Розбір кадру з правим вирівнюванням (Right-aligned) та знаковим розширенням
    [[nodiscard]] static constexpr Vector3i16 parse_right_aligned(std::span<const uint8_t, 6> buf) noexcept {
        auto sign_extend_12 = [](uint8_t lsb, uint8_t msb) constexpr -> int16_t {
            const auto u16 = static_cast<uint16_t>(lsb | (static_cast<uint16_t>(msb) << 8));
            return static_cast<int16_t>(static_cast<int16_t>(u16 << 4) >> 4);
        };

        return Vector3i16{
            .x = sign_extend_12(buf[0], buf[1]),
            .y = sign_extend_12(buf[2], buf[3]),
            .z = sign_extend_12(buf[4], buf[5])
        };
    }
};

} // namespace sensor

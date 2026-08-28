#include <cstdint>
#include <cstddef>
#include <span>
#include <array>

namespace sd {

// Обчислення CRC7 у стилі сучасного C++20 через std::span
constexpr uint8_t calculate_crc7(std::span<const uint8_t> data) noexcept {
    uint8_t crc = 0;
    for (const uint8_t byte : data) {
        uint8_t current = byte;
        for (int bit = 0; bit < 8; ++bit) {
            crc <<= 1;
            if ((current ^ crc) & 0x80) {
                crc ^= 0x09;
            }
            current <<= 1;
        }
    }
    return static_cast<uint8_t>(crc & 0x7F);
}

// Одночасний розрахунок 4 незалежних CRC16 для ліній DAT0..DAT3 над 512-байтним блоком
class BlockCrc16Calculator {
public:
    using CrcArray = std::array<uint16_t, 4>;

    static constexpr CrcArray calculate(std::span<const uint8_t, 512> block) noexcept {
        CrcArray crcs = {0, 0, 0, 0};
        for (const uint8_t byte : block) {
            // Старший нібл (лінії DAT3..DAT0)
            process_nibble(crcs, static_cast<uint8_t>(byte >> 4));
            // Молодший нібл (лінії DAT3..DAT0)
            process_nibble(crcs, static_cast<uint8_t>(byte & 0x0F));
        }
        return crcs;
    }

private:
    static constexpr void process_nibble(CrcArray& crcs, uint8_t nibble) noexcept {
        for (size_t lane = 0; lane < 4; ++lane) {
            const uint16_t bit = (nibble >> lane) & 0x01;
            const uint16_t inv = bit ^ ((crcs[lane] >> 15) & 1);
            crcs[lane] <<= 1;
            if (inv) {
                crcs[lane] ^= 0x1021;
            }
        }
    }
};

} // namespace sd

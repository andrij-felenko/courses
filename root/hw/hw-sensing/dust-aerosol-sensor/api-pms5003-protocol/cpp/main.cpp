#include <cstdint>
#include <span>

class Pms5003Verifier {
public:
    static constexpr size_t FrameSize = 32;

    static constexpr bool verify(std::span<const uint8_t, FrameSize> buffer) noexcept {
        if (buffer[0] != 0x42 || buffer[1] != 0x4D) {
            return false;
        }

        const auto frameLen = static_cast<uint16_t>((buffer[2] << 8) | buffer[3]);
        if (frameLen != 28) {
            return false;
        }

        uint16_t calcSum = 0;
        for (size_t i = 0; i < 30; ++i) {
            calcSum += buffer[i];
        }

        const auto rxSum = static_cast<uint16_t>((buffer[30] << 8) | buffer[31]);
        return (calcSum == rxSum);
    }
};

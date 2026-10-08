#include <cstdint>

class AngleEncoderDecoder {
public:
    static constexpr float DEGREES_PER_LSB = 360.0f / 16384.0f;

    struct DecodedAngle {
        float angle_degrees;
        bool error_flag;
        bool parity_valid;
    };

    static DecodedAngle decode_spi_frame(uint16_t frame) {
        // Обчислення парності побітовим XOR
        uint16_t temp = frame ^ (frame >> 8);
        temp ^= (temp >> 4);
        temp ^= (temp >> 2);
        temp ^= (temp >> 1);
        bool parity_ok = ((temp & 1) == 0);

        bool ef = (frame & 0x4000) != 0;
        uint16_t raw_angle = frame & 0x3FFF;

        return DecodedAngle{
            .angle_degrees = static_cast<float>(raw_angle) * DEGREES_PER_LSB,
            .error_flag = ef,
            .parity_valid = parity_ok
        };
    }
};

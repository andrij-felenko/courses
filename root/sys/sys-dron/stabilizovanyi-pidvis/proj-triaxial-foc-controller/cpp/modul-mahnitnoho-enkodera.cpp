#include <cstdint>
#include <bit>
#include <expected>
#include <numbers>

namespace gimbal {

enum class EncoderError {
    ParityMismatch,
    SensorFault,
    SpiTimeout
};

class As5048aParser {
public:
    static constexpr uint16_t CMD_READ_ANGLE = 0x3FFF;
    static constexpr uint16_t PARITY_BIT     = 0x8000;
    static constexpr uint16_t ERROR_FLAG     = 0x4000;
    static constexpr uint16_t DATA_MASK      = 0x3FFF;

    static std::expected<float, EncoderError> parse_response(uint16_t raw_response) noexcept {
        const uint16_t payload = raw_response & ~PARITY_BIT;
        const bool is_odd = (std::popcount(payload) % 2) != 0;
        const bool frame_parity_bit = (raw_response & PARITY_BIT) != 0;

        if (is_odd != frame_parity_bit) {
            return std::unexpected(EncoderError::ParityMismatch);
        }

        if ((raw_response & ERROR_FLAG) != 0) {
            return std::unexpected(EncoderError::SensorFault);
        }

        const uint16_t raw_ticks = raw_response & DATA_MASK;
        const float angle_rad = (static_cast<float>(raw_ticks) / 16384.0f) * (2.0f * std::numbers::pi_v<float>);
        return angle_rad;
    }
};

} // namespace gimbal

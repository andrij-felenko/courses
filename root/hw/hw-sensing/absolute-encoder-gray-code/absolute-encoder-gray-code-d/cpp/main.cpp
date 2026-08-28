#include <cstdint>
#include <cmath>
#include <numbers>
#include <expected>
#include <concepts>

namespace sensing {

enum class EncoderError : uint8_t {
    CrcMismatch,
    HardwareFault,
    WarningDegradation,
    CommunicationTimeout
};

struct Angle {
    double radians{0.0};
    double degrees{0.0};
    int32_t full_turns{0};

    [[nodiscard]] constexpr double total_radians() const noexcept {
        return radians + static_cast<double>(full_turns) * 2.0 * std::numbers::pi;
    }
};

template <uint8_t SingleTurnBits, uint8_t MultiTurnBits = 0, bool IsGrayCoded = true>
class AbsoluteEncoderDecoder {
public:
    static constexpr uint8_t kSingleTurnBits = SingleTurnBits;
    static constexpr uint8_t kMultiTurnBits = MultiTurnBits;
    static constexpr uint8_t kTotalPosBits = SingleTurnBits + MultiTurnBits;
    static constexpr uint8_t kPayloadBits = kTotalPosBits + 2; // + Error + Warning
    static constexpr double kStepsPerTurn = static_cast<double>(1ULL << SingleTurnBits);

    [[nodiscard]] static constexpr uint32_t gray_to_binary(uint32_t gray) noexcept {
        gray ^= (gray >> 1);
        gray ^= (gray >> 2);
        gray ^= (gray >> 4);
        gray ^= (gray >> 8);
        gray ^= (gray >> 16);
        return gray;
    }

    [[nodiscard]] static constexpr uint8_t calculate_crc6(uint64_t data, uint8_t bit_count) noexcept {
        uint8_t crc = 0x00;
        for (int8_t i = static_cast<int8_t>(bit_count - 1); i >= 0; --i) {
            uint8_t bit = static_cast<uint8_t>((data >> i) & 1ULL);
            uint8_t do_invert = static_cast<uint8_t>(((crc >> 5) & 1U) ^ bit);
            crc <<= 1;
            if (do_invert) {
                crc ^= 0x03; // Поліном BiSS-C: x^6 + x^1 + 1
            }
        }
        return static_cast<uint8_t>((~crc) & 0x3FU);
    }

    [[nodiscard]] static std::expected<Angle, EncoderError> decode_biss_frame(uint64_t raw_frame) noexcept {
        const uint8_t received_crc = static_cast<uint8_t>(raw_frame & 0x3FU);
        const uint64_t payload = (raw_frame >> 6) & ((1ULL << kPayloadBits) - 1ULL);

        if (calculate_crc6(payload, kPayloadBits) != received_crc) {
            return std::unexpected(EncoderError::CrcMismatch);
        }

        const bool error_active = ((payload >> 1) & 1ULL) == 0;
        if (error_active) {
            return std::unexpected(EncoderError::HardwareFault);
        }

        const uint64_t raw_pos = payload >> 2;
        constexpr uint64_t st_mask = (1ULL << SingleTurnBits) - 1ULL;
        constexpr uint64_t mt_mask = (1ULL << MultiTurnBits) - 1ULL;

        uint32_t st_raw = static_cast<uint32_t>(raw_pos & st_mask);
        uint32_t mt_raw = static_cast<uint32_t>((raw_pos >> SingleTurnBits) & mt_mask);

        if constexpr (IsGrayCoded) {
            st_raw = gray_to_binary(st_raw);
            mt_raw = gray_to_binary(mt_raw);
        }

        Angle result{};
        result.degrees = (static_cast<double>(st_raw) / kStepsPerTurn) * 360.0;
        result.radians = (static_cast<double>(st_raw) / kStepsPerTurn) * (2.0 * std::numbers::pi);
        result.full_turns = static_cast<int32_t>(mt_raw);

        return result;
    }
};

} // namespace sensing

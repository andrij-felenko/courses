#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>

namespace embedded::rf {

inline constexpr uint32_t CalibrationMagic = 0x52464341; // "RFCA"
inline constexpr size_t ChannelCount = 14;

enum class CalibrationError : uint8_t {
    InvalidMagic,
    ChecksumMismatch,
    ValueOutOfRange,
    HardwareFault
};

struct alignas(4) CalibrationData {
    uint32_t magic{CalibrationMagic};
    uint8_t xtal_cap_trim{0};                          // 0..63 tuning steps
    std::array<int8_t, ChannelCount> power_offset_dbm{}; // Per-channel offset
    uint16_t crc16{0};

    [[nodiscard]] constexpr uint16_t compute_crc() const noexcept {
        uint16_t crc = 0xFFFF;
        const auto payload = std::as_bytes(std::span{this, 1}).first(sizeof(CalibrationData) - sizeof(uint16_t));
        for (auto byte : payload) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021 : (crc << 1);
            }
        }
        return crc;
    }
};

class RfTransceiverController {
public:
    static std::expected<void, CalibrationError> apply_calibration(const CalibrationData& calib) noexcept {
        if (calib.magic != CalibrationMagic) {
            return std::unexpected(CalibrationError::InvalidMagic);
        }

        if (calib.compute_crc() != calib.crc16) {
            return std::unexpected(CalibrationError::ChecksumMismatch);
        }

        if (calib.xtal_cap_trim > 63) {
            return std::unexpected(CalibrationError::ValueOutOfRange);
        }

        // Пряме оновлення апаратного регістру PLL через RAII-подібний доступ
        auto* xtal_reg = reinterpret_cast<volatile uint32_t*>(0x40024040);
        *xtal_reg = (*xtal_reg & ~0x3FU) | (calib.xtal_cap_trim & 0x3FU);

        // Оновлення пам'яті таблиці потужності каналів
        auto* power_lut = reinterpret_cast<volatile int8_t*>(0x40024100);
        for (size_t ch = 0; ch < ChannelCount; ++ch) {
            const int8_t offset = calib.power_offset_dbm[ch];
            if (offset < -12 || offset > 12) {
                return std::unexpected(CalibrationError::ValueOutOfRange);
            }
            power_lut[ch] = offset;
        }

        return {};
    }
};

} // namespace embedded::rf

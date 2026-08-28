#include <cstdint>
#include <expected>

namespace mcu::adc {

enum class ConversionError : uint8_t {
    InvalidRawCode,
    CorruptedCalibrationData
};

class PrecisionAdcConverter {
public:
    static constexpr uint16_t kFactoryVrefMv       = 3000;
    static constexpr uintptr_t kVrefintCalRegister = 0x1FFF75AA;
    static constexpr uint32_t kAdcMaxCounts        = 4095;

    [[nodiscard]] static std::expected<uint32_t, ConversionError>
    calculate_vdda_millivolts(uint16_t raw_vref_code) noexcept {
        if (raw_vref_code == 0) {
            return std::unexpected(ConversionError::InvalidRawCode);
        }

        const auto* cal_word = reinterpret_cast<const uint16_t*>(kVrefintCalRegister);
        const uint32_t vref_cal = *cal_word;

        if (vref_cal == 0 || vref_cal == 0xFFFF) {
            return std::unexpected(ConversionError::CorruptedCalibrationData);
        }

        return (static_cast<uint32_t>(kFactoryVrefMv) * vref_cal) / raw_vref_code;
    }

    [[nodiscard]] static std::expected<uint32_t, ConversionError>
    calculate_channel_millivolts(uint16_t raw_channel_code, uint16_t raw_vref_code) noexcept {
        auto vdda_result = calculate_vdda_millivolts(raw_vref_code);
        if (!vdda_result.has_value()) {
            return std::unexpected(vdda_result.error());
        }

        return (*vdda_result * static_cast<uint32_t>(raw_channel_code)) / kAdcMaxCounts;
    }
};

} // namespace mcu::adc

#include <cstdint>
#include <optional>
#include <span>
#include <expected>

namespace dvt {

enum class TestMode : uint8_t {
    SleepDeep = 0,
    ClockMco  = 1,
    AdcVerify = 2,
    BusStress = 3
};

enum class AdcError : uint8_t {
    DivisionByZero,
    CalibrationCorrupted,
    HardwareTimeout
};

struct AdcMetric {
    uint32_t raw_vref_adc{0};
    uint32_t calculated_vdda_mv{0};
    int32_t  error_vs_nominal_mv{0};

    [[nodiscard]] constexpr bool is_within_tolerance(int32_t tolerance_mv) const noexcept {
        int32_t diff = error_vs_nominal_mv >= 0 ? error_vs_nominal_mv : -error_vs_nominal_mv;
        return diff <= tolerance_mv;
    }
};

class AdcVerifier {
public:
    static constexpr uint16_t kFactoryVrefCalMv = 3000;
    static constexpr uintptr_t kVrefCalAddress  = 0x1FFF75AA;

    [[nodiscard]] static std::expected<AdcMetric, AdcError>
    calculate_vdda(uint16_t adc_raw_vref) noexcept {
        if (adc_raw_vref == 0) {
            return std::unexpected(AdcError::DivisionByZero);
        }

        const auto* cal_ptr = reinterpret_cast<const uint16_t*>(kVrefCalAddress);
        const uint32_t vref_cal = *cal_ptr;
        if (vref_cal == 0 || vref_cal == 0xFFFF) {
            return std::unexpected(AdcError::CalibrationCorrupted);
        }

        AdcMetric metric{};
        metric.raw_vref_adc = adc_raw_vref;
        metric.calculated_vdda_mv = (static_cast<uint32_t>(kFactoryVrefCalMv) * vref_cal) / adc_raw_vref;
        metric.error_vs_nominal_mv = static_cast<int32_t>(metric.calculated_vdda_mv) - 3300;

        return metric;
    }
};

class ClockOutputManager {
public:
    enum class Prescaler : uint8_t { Div1 = 0, Div2 = 1, Div4 = 2, Div8 = 3, Div16 = 4 };

    static void configure_mco(bool enable, Prescaler div) noexcept {
        // Конфігурація регістрів тактування RCC_CFGR_MCOSEL
        (void)enable;
        (void)div;
    }
};

} // namespace dvt

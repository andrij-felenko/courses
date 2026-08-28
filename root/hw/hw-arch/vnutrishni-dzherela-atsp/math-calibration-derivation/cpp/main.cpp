#include <cstdint>
#include <tuple>

namespace McuAdc::Math {

struct CalculationResult {
    uint32_t vdda_mv{0};
    int32_t  temperature_deci_celsius{0};
    uint32_t channel_mv{0};
};

[[nodiscard]] constexpr CalculationResult calculate_fixed_point(
    uint16_t vrefint_cal,
    uint16_t ts_cal1,
    uint16_t ts_cal2,
    uint16_t raw_vrefint,
    uint16_t raw_ts,
    uint16_t raw_channel) noexcept {
    
    if (raw_vrefint == 0) {
        return {};
    }

    CalculationResult res;

    // 1. VDDA в мВ з симетричним округленням
    const uint32_t vdda_mv = (static_cast<uint32_t>(3000) * vrefint_cal + (raw_vrefint / 2U)) / raw_vrefint;
    res.vdda_mv = vdda_mv;

    // 2. Нормалізація термодатчика
    const uint32_t ts_norm = (static_cast<uint32_t>(raw_ts) * vrefint_cal + (raw_vrefint / 2U)) / raw_vrefint;

    // 3. Температура в 0.1 °C
    const int32_t delta_cal = static_cast<int32_t>(ts_cal2) - static_cast<int32_t>(ts_cal1);
    if (delta_cal > 0) {
        res.temperature_deci_celsius = ((static_cast<int32_t>(ts_norm - ts_cal1) * 1000 + (delta_cal / 2)) / delta_cal) + 300;
    }

    // 4. Зовнішній канал
    res.channel_mv = (vdda_mv * static_cast<uint32_t>(raw_channel) + 2047U) / 4095U;

    return res;
}

} // namespace McuAdc::Math

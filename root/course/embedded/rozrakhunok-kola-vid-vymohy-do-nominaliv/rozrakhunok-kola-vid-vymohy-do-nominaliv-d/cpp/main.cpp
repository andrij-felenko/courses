#include <cstdint>
#include <algorithm>

namespace embedded::hw {

/* Ідіоматична C++ структура конфігурації з типобезпечними параметрами за замовчуванням */
struct AdcDividerChannel {
    uint32_t r1_ohms{100'000};
    uint32_t r2_ohms{200'000};
    uint16_t vref_mv{3300};
    uint16_t adc_max_code{4095};
    int16_t  cal_offset_mv{0};
    uint32_t cal_gain_ppm{1'000'000};  // 1.000000 у системі PPM
};

class BatteryVoltageSensor {
public:
    explicit constexpr BatteryVoltageSensor(AdcDividerChannel config) noexcept
        : config_{config} {}

    [[nodiscard]] constexpr uint32_t convertRawToMv(uint16_t raw_code) const noexcept {
        if (config_.adc_max_code == 0 || config_.r2_ohms == 0) {
            return 0;
        }

        // 1. Напруга на піні АЦП
        const auto v_pin = (static_cast<uint64_t>(raw_code) * config_.vref_mv) / config_.adc_max_code;

        // 2. Відновлення вхідної напруги через дільник Тевеніна
        const auto r_total = static_cast<uint64_t>(config_.r1_ohms) + config_.r2_ohms;
        const auto v_bat_raw = (v_pin * r_total) / config_.r2_ohms;

        // 3. Калібрувальна корекція
        auto v_calibrated = static_cast<int64_t>(v_bat_raw) + config_.cal_offset_mv;
        if (config_.cal_gain_ppm != 1'000'000 && config_.cal_gain_ppm != 0) {
            v_calibrated = (v_calibrated * static_cast<int64_t>(config_.cal_gain_ppm)) / 1'000'000;
        }

        return static_cast<uint32_t>(std::max<int64_t>(0, v_calibrated));
    }

private:
    AdcDividerChannel config_;
};

} // namespace embedded::hw

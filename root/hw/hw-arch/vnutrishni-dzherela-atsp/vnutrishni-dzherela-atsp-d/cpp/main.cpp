#include <cstdint>
#include <optional>
#include <span>

namespace Hardware {

struct PowerMetrics {
    uint32_t vdda_millivolts{0};
    int32_t  temperature_deci_celsius{0}; // Одиниці: 0.1 °C
    uint32_t vbat_millivolts{0};
};

class InternalAdcMonitor {
public:
    struct CalibrationData {
        uint16_t vrefint_cal{1650};
        uint16_t ts_cal1{1035};
        uint16_t ts_cal2{1380};
        uint16_t vref_mv{3000};
        int16_t  t_cal1_c{30};
        int16_t  t_cal2_c{130};
        uint8_t  vbat_divider{3};
    };

    InternalAdcMonitor() noexcept {
        load_factory_calibration();
    }

    [[nodiscard]] std::optional<PowerMetrics> calculate(uint16_t raw_vrefint,
                                                        uint16_t raw_temp,
                                                        uint16_t raw_vbat) const noexcept {
        if (raw_vrefint == 0) {
            return std::nullopt;
        }

        PowerMetrics metrics;

        // 1. Відновлення точного VDDA
        const uint32_t vdda = (static_cast<uint32_t>(cal_.vref_mv) * cal_.vrefint_cal +
                               (raw_vrefint / 2U)) / raw_vrefint;
        metrics.vdda_millivolts = vdda;

        // 2. Нормалізація коду термодатчика до напруги калібрування
        const uint32_t ts_norm = (static_cast<uint32_t>(raw_temp) * cal_.vrefint_cal +
                                  (raw_vrefint / 2U)) / raw_vrefint;

        // 3. Лінійна інтерполяція температури
        const int32_t delta_cal = static_cast<int32_t>(cal_.ts_cal2) - static_cast<int32_t>(cal_.ts_cal1);
        if (delta_cal > 0) {
            const int32_t delta_t = (cal_.t_cal2_c - cal_.t_cal1_c) * 10;
            metrics.temperature_deci_celsius = ((static_cast<int32_t>(ts_norm - cal_.ts_cal1) * delta_t) / delta_cal) +
                                               (cal_.t_cal1_c * 10);
        }

        // 4. Напруга на виводі VBAT
        const uint32_t vbat_channel = (vdda * static_cast<uint32_t>(raw_vbat) + 2047U) / 4095U;
        metrics.vbat_millivolts = vbat_channel * cal_.vbat_divider;

        return metrics;
    }

private:
    void load_factory_calibration() noexcept {
        constexpr uintptr_t addr_vref = 0x1FFF75AAUL;
        constexpr uintptr_t addr_ts1  = 0x1FFF75A8UL;
        constexpr uintptr_t addr_ts2  = 0x1FFF75CAUL;

        cal_.vrefint_cal = *reinterpret_cast<const volatile uint16_t*>(addr_vref);
        cal_.ts_cal1     = *reinterpret_cast<const volatile uint16_t*>(addr_ts1);
        cal_.ts_cal2     = *reinterpret_cast<const volatile uint16_t*>(addr_ts2);

        // Fallback при відсутності коректних заводських записів
        if (cal_.vrefint_cal < 1000 || cal_.vrefint_cal > 2500 || cal_.ts_cal2 <= cal_.ts_cal1) {
            cal_.vrefint_cal = 1650;
            cal_.ts_cal1     = 1035;
            cal_.ts_cal2     = 1380;
        }
    }

    CalibrationData cal_{};
};

} // namespace Hardware

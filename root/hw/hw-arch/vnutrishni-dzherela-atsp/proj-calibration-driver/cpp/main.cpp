#include <cstdint>
#include <span>
#include <array>
#include <algorithm>
#include <optional>

namespace McuAdc {

/**
 * @brief Структура фізичних результатів з типізованими одиницями
 */
struct InternalMetrics {
    uint32_t millivolts_vdda{0};
    int32_t  millidegrees_temperature{0}; // 1/1000 °C
    uint32_t millivolts_vbat{0};
};

/**
 * @brief Драйвер калібрування внутрішніх джерел АЦП на C++20
 */
class CalibrationDriver {
public:
    struct CalibrationRom {
        uint16_t vrefint_cal{0};
        uint16_t ts_cal1{0};
        uint16_t ts_cal2{0};
        uint16_t cal_vref_mv{3000};
        int16_t  ts_cal1_c{30};
        int16_t  ts_cal2_c{130};
        uint8_t  vbat_multiplier{3};
    };

    explicit CalibrationDriver(std::optional<CalibrationRom> custom_rom = std::nullopt) noexcept {
        if (custom_rom.has_value()) {
            rom_ = *custom_rom;
        } else {
            read_hardware_rom();
        }
    }

    /**
     * @brief Розрахунок метрик за сирими відліками
     */
    [[nodiscard]] std::optional<InternalMetrics> calculate(
        uint16_t raw_vrefint,
        uint16_t raw_temperature,
        uint16_t raw_vbat) const noexcept {
        
        if (raw_vrefint == 0 || rom_.vrefint_cal == 0) {
            return std::nullopt;
        }

        InternalMetrics result;

        // 1. Точна напруга VDDA в мВ (цілочисельне ділення з математичним округленням)
        const uint32_t vdda_mv = (static_cast<uint32_t>(rom_.cal_vref_mv) * rom_.vrefint_cal + 
                                  (raw_vrefint / 2U)) / raw_vrefint;
        result.millivolts_vdda = vdda_mv;

        // 2. Нормалізація відліку термодатчика до напруги 3000 мВ
        const uint32_t ts_norm = (static_cast<uint32_t>(raw_temperature) * rom_.vrefint_cal + 
                                  (raw_vrefint / 2U)) / raw_vrefint;

        // 3. Інтерполяція температури в міліградусах (0.001 °C)
        const int32_t delta_cal = static_cast<int32_t>(rom_.ts_cal2) - static_cast<int32_t>(rom_.ts_cal1);
        if (delta_cal > 0) {
            const int32_t delta_temp_mc = (rom_.ts_cal2_c - rom_.ts_cal1_c) * 1000;
            const int32_t temp_mc = (static_cast<int32_t>(ts_norm - rom_.ts_cal1) * delta_temp_mc + (delta_cal / 2)) / delta_cal +
                                    (rom_.ts_cal1_c * 1000);
            result.millidegrees_temperature = temp_mc;
        }

        // 4. Напруга батареї
        const uint32_t vbat_pin_mv = (vdda_mv * static_cast<uint32_t>(raw_vbat) + 2047U) / 4095U;
        result.millivolts_vbat = vbat_pin_mv * rom_.vbat_multiplier;

        return result;
    }

    /**
     * @brief Медіанний фільтр для масиву відліків
     */
    template <size_t N>
    [[nodiscard]] static uint16_t filter_median(std::array<uint16_t, N> samples) noexcept {
        static_assert(N % 2 == 1, "Кількість відліків має бути непарною");
        std::nth_element(samples.begin(), samples.begin() + N / 2, samples.end());
        return samples[N / 2];
    }

private:
    void read_hardware_rom() noexcept {
        constexpr uintptr_t addr_vrefint = 0x1FFF75AAUL;
        constexpr uintptr_t addr_ts_cal1 = 0x1FFF75A8UL;
        constexpr uintptr_t addr_ts_cal2 = 0x1FFF75CAUL;

        rom_.vrefint_cal     = *reinterpret_cast<const volatile uint16_t*>(addr_vrefint);
        rom_.ts_cal1         = *reinterpret_cast<const volatile uint16_t*>(addr_ts_cal1);
        rom_.ts_cal2         = *reinterpret_cast<const volatile uint16_t*>(addr_ts_cal2);
        rom_.cal_vref_mv     = 3000;
        rom_.ts_cal1_c       = 30;
        rom_.ts_cal2_c       = 130;
        rom_.vbat_multiplier = 3;

        // Fallback при некоректному ROM
        if (rom_.vrefint_cal < 1000 || rom_.vrefint_cal > 2500 || rom_.ts_cal2 <= rom_.ts_cal1) {
            rom_.vrefint_cal = 1650;
            rom_.ts_cal1     = 1035;
            rom_.ts_cal2     = 1380;
        }
    }

    CalibrationRom rom_{};
};

} // namespace McuAdc

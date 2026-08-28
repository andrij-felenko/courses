#include <cstdint>
#include <span>
#include <optional>

namespace McuAdc {

/**
 * @brief Структура заводського калібрування з типізованими параметрами
 */
struct FactoryCalibration {
    uint16_t vrefint_cal{1650};
    uint16_t ts_cal1{1035};
    uint16_t ts_cal2{1380};
    uint16_t cal_vref_mv{3000};
    int16_t  ts_cal1_temp_c{30};
    int16_t  ts_cal2_temp_c{130};
    uint8_t  vbat_multiplier{3};

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return (vrefint_cal > 1000 && vrefint_cal < 2500) &&
               (ts_cal1 > 500 && ts_cal1 < 3000) &&
               (ts_cal2 > ts_cal1 && ts_cal2 < 4095);
    }
};

/**
 * @brief Безпечне читання заводських констант для сімейства STM32G4
 */
[[nodiscard]] inline FactoryCalibration read_hardware_calibration() noexcept {
    constexpr uintptr_t addr_vrefint = 0x1FFF75AAUL;
    constexpr uintptr_t addr_ts_cal1 = 0x1FFF75A8UL;
    constexpr uintptr_t addr_ts_cal2 = 0x1FFF75CAUL;

    FactoryCalibration cal;
    cal.vrefint_cal     = *reinterpret_cast<const volatile uint16_t*>(addr_vrefint);
    cal.ts_cal1         = *reinterpret_cast<const volatile uint16_t*>(addr_ts_cal1);
    cal.ts_cal2         = *reinterpret_cast<const volatile uint16_t*>(addr_ts_cal2);
    cal.cal_vref_mv     = 3000;
    cal.ts_cal1_temp_c  = 30;
    cal.ts_cal2_temp_c  = 130;
    cal.vbat_multiplier = 3;

    if (!cal.is_valid()) {
        // Fallback константи при пошкодженій системній пам'яті
        cal.vrefint_cal = 1650;
        cal.ts_cal1     = 1035;
        cal.ts_cal2     = 1380;
    }

    return cal;
}

} // namespace McuAdc

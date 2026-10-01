#ifndef OPTICAL_POWER_METER_HPP
#define OPTICAL_POWER_METER_HPP

#include <vector>
#include <cstdint>
#include <cstddef>
#include <optional>

namespace opm {

/**
 * @brief Точка калібрувальної таблиці спектральної чутливості фотодіода.
 */
struct CalibPoint {
    std::uint16_t wavelength_nm; /**< Довжина хвилі у нанометрах */
    float sensitivity_a_w;       /**< Спектральна чутливість R(λ) у А/Вт */
};

/**
 * @brief Апаратні параметри вимірювального тракту OPM.
 */
struct HardwareConfig {
    float tia_gain_ohm{100000.0f};      /**< Опір зворотного зв'язку TIA Rf (Ом) */
    float adc_vref_v{3.3f};             /**< Опорна напруга АЦП (В) */
    std::uint32_t adc_max_count{4095};  /**< Максимальний відлік АЦП (наприклад, 12-біт = 4095) */
    float lidt_max_power_w{0.100f};     /**< Поріг оптичного руйнування LIDT (Вт) */
};

/**
 * @brief Результат вимірювання оптичної потужності.
 */
struct MeasurementResult {
    float power_w{0.0f};          /**< Потужність у Ватах */
    float power_dbm{-120.0f};     /**< Потужність у dBm */
    bool lidt_exceeded{false};    /**< Прапорець перевищення порогу LIDT */
};

/**
 * @brief Клас ООП-драйвера оптичного ватметра.
 */
class OpticalPowerMeter {
public:
    explicit OpticalPowerMeter(HardwareConfig config, std::vector<CalibPoint> calib_table);

    /**
     * @brief Процедура автоматичного калібрування темнового струму (zeroing).
     * @param dark_adc_samples Вектор відліків АЦП при закритому фотодетекторі.
     */
    bool calibrateDarkOffset(const std::vector<std::uint16_t>& dark_adc_samples);

    /**
     * @brief Встановлення робочої довжини хвилі випромінювання.
     * @return true якщо довжина хвилі присутня у діапазоні таблиці, інакше false.
     */
    bool setWavelength(std::uint16_t wavelength_nm);

    /**
     * @brief Обробка сирого відліку АЦП і перетворення у фізичні значення потужності.
     */
    [[nodiscard]] std::optional<MeasurementResult> processAdcSample(std::uint16_t raw_adc_sample);

    [[nodiscard]] std::uint16_t currentWavelength() const noexcept { return current_wavelength_nm_; }
    [[nodiscard]] float currentSensitivity() const noexcept { return current_sensitivity_a_w_; }
    [[nodiscard]] float darkOffsetVoltage() const noexcept { return dark_offset_v_; }

    /**
     * @brief Статичний метод конверсії Ватів у dBm.
     */
    static float wattsToDbm(float power_w) noexcept;

private:
    float interpolateSensitivity(std::uint16_t wavelength_nm) const;

    HardwareConfig config_;
    std::vector<CalibPoint> calib_table_;
    float dark_offset_v_{0.0f};
    std::uint16_t current_wavelength_nm_{0};
    float current_sensitivity_a_w_{0.0f};
    std::vector<std::uint16_t> filter_buffer_;
    std::size_t filter_index_{0};
};

} // namespace opm

#endif // OPTICAL_POWER_METER_HPP

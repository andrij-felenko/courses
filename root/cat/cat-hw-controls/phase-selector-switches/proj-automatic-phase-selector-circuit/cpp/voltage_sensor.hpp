#ifndef VOLTAGE_SENSOR_HPP
#define VOLTAGE_SENSOR_HPP

#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <optional>

namespace hw_controls {

/**
 * @brief Ідентифікатори фазних каналів трифазної мережі
 */
enum class PhaseId : uint8_t {
    L1 = 0,
    L2 = 1,
    L3 = 2,
    None = 0xFF
};

/**
 * @brief Кількість фаз у системі
 */
inline constexpr std::size_t PHASE_COUNT = 3;

/**
 * @brief Параметри калібрування каналу АЦП для вимірювання напруги
 */
struct AdcConfig {
    float v_ref = 3.3f;             ///< Опорна напруга АЦП у вольтах (В)
    uint32_t adc_resolution = 4095; ///< Максимальне дискретне значення (12-бітний АЦП)
    float divider_ratio = 100.0f;   ///< Коефіцієнт зменшення дільника/трансформатора напруги
    uint16_t zero_offset = 2048;    ///< Офсет «віртуальної землі» для змінної напруги
};

/**
 * @brief Клас для дискретизації та обчислення True RMS напруги по трьох фазах
 */
class VoltageSensor {
public:
    explicit VoltageSensor(const AdcConfig& config = {})
        : config_(config) {
        rms_voltages_.fill(0.0f);
    }

    /**
     * @brief Обчислення діючого значення (True RMS) для конкретної фази за буфером відліків
     * @param phase Ідентифікатор фази (L1, L2 або L3)
     * @param adc_samples Буфер сирих вибірок АЦП
     */
    void process_samples(PhaseId phase, std::span<const uint16_t> adc_samples) {
        if (phase == PhaseId::None || static_cast<std::size_t>(phase) >= PHASE_COUNT) {
            return;
        }

        if (adc_samples.empty() || config_.adc_resolution == 0) {
            rms_voltages_[static_cast<std::size_t>(phase)] = 0.0f;
            return;
        }

        const float volts_per_lsb = config_.v_ref / static_cast<float>(config_.adc_resolution);
        double sum_squares = 0.0;

        for (const uint16_t raw_sample : adc_samples) {
            const int32_t centered = static_cast<int32_t>(raw_sample) - static_cast<int32_t>(config_.zero_offset);
            const float inst_voltage_sensor = static_cast<float>(centered) * volts_per_lsb;
            const float inst_voltage_mains = inst_voltage_sensor * config_.divider_ratio;
            sum_squares += static_cast<double>(inst_voltage_mains * inst_voltage_mains);
        }

        const float mean_square = static_cast<float>(sum_squares / static_cast<double>(adc_samples.size()));
        rms_voltages_[static_cast<std::size_t>(phase)] = std::sqrt(mean_square);
    }

    /**
     * @brief Отримання обчисленого значення True RMS для фази
     */
    [[nodiscard]] float get_rms(PhaseId phase) const {
        if (phase == PhaseId::None || static_cast<std::size_t>(phase) >= PHASE_COUNT) {
            return 0.0f;
        }
        return rms_voltages_[static_cast<std::size_t>(phase)];
    }

    /**
     * @brief Отримання всіх обчислених RMS напруг
     */
    [[nodiscard]] std::array<float, PHASE_COUNT> get_all_rms() const {
        return rms_voltages_;
    }

    /**
     * @brief Оновлення конфігурації АЦП
     */
    void set_config(const AdcConfig& config) {
        config_ = config;
    }

    /**
     * @brief Перевірка, чи не перевищує напруга максимально допустиме значення сенсора
     */
    [[nodiscard]] bool is_sensor_saturated(PhaseId phase, uint16_t raw_sample) const {
        (void)phase;
        return (raw_sample >= config_.adc_resolution) || (raw_sample == 0);
    }

private:
    AdcConfig config_;
    std::array<float, PHASE_COUNT> rms_voltages_{};
};

} // namespace hw_controls

#endif // VOLTAGE_SENSOR_HPP

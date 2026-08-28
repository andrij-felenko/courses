#include <cstdint>
#include <cmath>
#include <span>
#include <algorithm>
#include <expected>

namespace mox {

/* Розрахунок CRC-8 (поліном 0x31) з безпечним використанням std::span */
[[nodiscard]] constexpr uint8_t calculate_crc8(std::span<const uint8_t> data) noexcept {
    constexpr uint8_t polynomial = 0x31;
    uint8_t crc = 0xFF;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x80) ? static_cast<uint8_t>((crc << 1) ^ polynomial)
                               : static_cast<uint8_t>(crc << 1);
        }
    }
    return crc;
}

/* Модель вихідних метрик газового сенсора */
struct SensorMetrics {
    float compensated_resistance_kohm;
    float baseline_resistance_kohm;
    int16_t voc_index;     // 0..500, типовий фон = 100
    uint16_t eco2_ppm;     // 400..60000 ppm eCO2
};

enum class EngineError {
    SensorNotReady,
    InvalidSensorReading,
    HumidityOutOfRange
};

class GasProcessingEngine {
public:
    explicit constexpr GasProcessingEngine(float initial_baseline_kohm = 100.0f) noexcept
        : baseline_{std::max(1.0f, initial_baseline_kohm)} {}

    /* Обчислення абсолютної вологості за формулою Магнуса (г/м^3) */
    [[nodiscard]] static float absolute_humidity(float temp_c, float rh_percent) noexcept {
        const float clamped_rh = std::clamp(rh_percent, 0.0f, 100.0f);
        const float p_sat = 6.112f * std::exp((17.62f * temp_c) / (243.12f + temp_c));
        const float p_vapor = p_sat * (clamped_rh / 100.0f);
        return 216.7f * (p_vapor / (273.15f + temp_c));
    }

    /* Оновлення конвеєра вимірювання */
    [[nodiscard]] std::expected<SensorMetrics, EngineError> process_sample(
        float raw_resistance_kohm,
        float temp_c,
        float rh_percent) noexcept
    {
        if (raw_resistance_kohm <= 0.001f) {
            return std::unexpected(EngineError::InvalidSensorReading);
        }

        ++sample_count_;
        if (sample_count_ > warmup_threshold_) {
            is_warmed_up_ = true;
        }

        // 1. Вологісна компенсація
        const float ah = absolute_humidity(temp_c, rh_percent);
        const float delta_h = ah - reference_humidity_;
        const float comp_factor = std::exp(k_humidity_ * delta_h);
        const float comp_resistance = raw_resistance_kohm * comp_factor;

        // 2. Адаптація базової лінії
        if (is_warmed_up_) {
            if (comp_resistance > baseline_) {
                baseline_ += alpha_up_ * (comp_resistance - baseline_);
            } else {
                baseline_ += alpha_down_ * (comp_resistance - baseline_);
            }
        } else {
            baseline_ = comp_resistance;
        }

        // 3. Формування логарифмічного VOC Index
        const float ratio = std::log(baseline_ / comp_resistance);
        const float raw_voc = 100.0f + voc_gain_ * ratio;
        const auto clamped_voc = static_cast<int16_t>(std::clamp(raw_voc, 0.0f, 500.0f) + 0.5f);

        // 4. Оцінка eCO2
        uint16_t eco2 = 400;
        if (ratio > 0.0f) {
            const float calculated_eco2 = 400.0f + 1200.0f * std::pow(ratio, 1.45f);
            eco2 = static_cast<uint16_t>(std::clamp(calculated_eco2, 400.0f, 60000.0f));
        }

        return SensorMetrics{
            .compensated_resistance_kohm = comp_resistance,
            .baseline_resistance_kohm = baseline_,
            .voc_index = clamped_voc,
            .eco2_ppm = eco2
        };
    }

    [[nodiscard]] float get_baseline() const noexcept { return baseline_; }
    void restore_baseline(float saved_baseline_kohm) noexcept {
        if (saved_baseline_kohm > 1.0f) {
            baseline_ = saved_baseline_kohm;
            is_warmed_up_ = true;
        }
    }

private:
    float baseline_{100.0f};
    static constexpr float alpha_up_{0.001f};       // Швидкий ріст до чистого фону
    static constexpr float alpha_down_{0.00002f};   // Повільний спад
    static constexpr float k_humidity_{0.035f};     // Коефіцієнт впливу вологи
    static constexpr float reference_humidity_{10.0f};
    static constexpr float voc_gain_{250.0f};
    static constexpr uint32_t warmup_threshold_{60};
    uint32_t sample_count_{0};
    bool is_warmed_up_{false};
};

} // namespace mox

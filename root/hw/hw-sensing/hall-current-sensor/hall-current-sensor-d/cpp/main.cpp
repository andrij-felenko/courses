#include <cstdint>
#include <concepts>
#include <span>
#include <algorithm>
#include <numeric>
#include <expected>

/**
 * @brief Перелік можливих помилок калібрування струмового сенсора.
 */
enum class SensorError {
    EmptySampleBuffer,
    HardwareClipping,
    OffsetOutOfBounds
};

/**
 * @brief Драйвер сенсора струму на ефекті Холла із захистом типів та фільтрацією.
 */
class HallCurrentSensor {
public:
    struct Config {
        uint32_t adc_max_ticks{4095};          // Роздільність АЦП (12 біт)
        float    vref_volts{3.3f};             // Опорна напруга АЦП
        float    sensitivity_mv_per_a{100.0f}; // Чутливість (мВ/А)
        float    filter_alpha{0.1f};           // Коефіцієнт EMA фільтра
    };

    explicit constexpr HallCurrentSensor(const Config& config) noexcept
        : config_(config),
          zero_offset_volts_(config.vref_volts * 0.5f),
          filtered_current_a_(0.0f),
          is_calibrated_(false) {}

    /**
     * @brief Калібрування зміщення нуля струму на основі вибірки відліків АЦП у спокої.
     */
    [[nodiscard]] std::expected<void, SensorError> calibrate_zero(std::span<const uint16_t> samples) noexcept {
        if (samples.empty()) {
            return std::unexpected(SensorError::EmptySampleBuffer);
        }

        const auto sum = std::accumulate(samples.begin(), samples.end(), uint64_t{0});
        const float avg_ticks = static_cast<float>(sum) / static_cast<float>(samples.size());
        const float calculated_offset = (avg_ticks / static_cast<float>(config_.adc_max_ticks)) * config_.vref_volts;

        // Перевірка правдоподібності нуля (зміщення має бути в межах 30%..70% від Vref)
        if (calculated_offset < config_.vref_volts * 0.3f || calculated_offset > config_.vref_volts * 0.7f) {
            return std::unexpected(SensorError::OffsetOutOfBounds);
        }

        zero_offset_volts_ = calculated_offset;
        filtered_current_a_ = 0.0f;
        is_calibrated_ = true;
        return {};
    }

    /**
     * @brief Оновлення вимірювання за новим кодом АЦП.
     * @return Поточний миттєвий струм в амперах.
     */
    float update(uint16_t raw_adc_ticks) noexcept {
        const float v_measured = (static_cast<float>(raw_adc_ticks) / static_cast<float>(config_.adc_max_ticks)) * config_.vref_volts;
        const float delta_v_mv = (v_measured - zero_offset_volts_) * 1000.0f;
        const float raw_current_a = delta_v_mv / config_.sensitivity_mv_per_a;

        filtered_current_a_ = (config_.filter_alpha * raw_current_a) +
                              ((1.0f - config_.filter_alpha) * filtered_current_a_);

        return raw_current_a;
    }

    [[nodiscard]] constexpr float filtered_current() const noexcept { return filtered_current_a_; }
    [[nodiscard]] constexpr float zero_offset() const noexcept { return zero_offset_volts_; }
    [[nodiscard]] constexpr bool is_calibrated() const noexcept { return is_calibrated_; }

private:
    Config config_;
    float  zero_offset_volts_;
    float  filtered_current_a_;
    bool   is_calibrated_;
};

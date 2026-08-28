#include <cstdint>
#include <cmath>
#include <span>
#include <optional>
#include <algorithm>
#include <array>

namespace embedded::sensing {

enum class SensorType : uint8_t {
    Ultrasonic,
    OpticalToF,
    MmWaveRadar
};

struct RawMeasurement {
    SensorType type;
    uint32_t raw_value;      // УЗ: час у мкс; ToF/Радар: дистанція в мм
    uint16_t signal_quality; // Оцінка сигналу (SNR або MCPS)
    uint16_t ambient_noise;  // Рівень фонового IR засвічення
    bool is_valid_hw;
};

struct EnvironmentState {
    float temperature_celsius{20.0f};
    bool bright_sunlight{false};
};

struct FusionOutput {
    uint16_t safe_distance_mm{0};
    uint8_t confident_sources{0};
    bool emergency_stop_required{false};
};

class RangeSensorFusion {
public:
    static constexpr uint16_t kInvalidRange = 0xFFFF;
    static constexpr uint16_t kEmergencyThresholdMm = 150;

    [[nodiscard]] static constexpr float CalculateSoundSpeed(float temp_c) noexcept {
        return (331.3f + 0.606f * temp_c) * 0.001f; // мм/мкс
    }

    [[nodiscard]] FusionOutput Evaluate(
        std::span<const RawMeasurement> measurements,
        const EnvironmentState& env
    ) const noexcept {
        struct FilteredPoint {
            uint16_t distance_mm;
            float confidence;
        };

        std::array<FilteredPoint, 8> valid_points{};
        size_t valid_count = 0;

        for (const auto& item : measurements) {
            if (!item.is_valid_hw || valid_count >= valid_points.size()) {
                continue;
            }

            auto processed = ValidateAndScale(item, env);
            if (processed.has_value()) {
                valid_points[valid_count++] = *processed;
            }
        }

        if (valid_count == 0) {
            // Повна втрата даних від сенсорів — безпечна зупинка
            return FusionOutput{
                .safe_distance_mm = 0,
                .confident_sources = 0,
                .emergency_stop_required = true
            };
        }

        // Консервативний пошук найближчої достовірної перешкоди
        uint16_t min_distance = kInvalidRange;
        for (size_t i = 0; i < valid_count; ++i) {
            if (valid_points[i].confidence >= 0.30f) {
                min_distance = std::min(min_distance, valid_points[i].distance_mm);
            }
        }

        // Якщо всі точки мали низьку довіру, беремо мінімум серед усіх наявних
        if (min_distance == kInvalidRange) {
            for (size_t i = 0; i < valid_count; ++i) {
                min_distance = std::min(min_distance, valid_points[i].distance_mm);
            }
        }

        return FusionOutput{
            .safe_distance_mm = min_distance,
            .confident_sources = static_cast<uint8_t>(valid_count),
            .emergency_stop_required = (min_distance <= kEmergencyThresholdMm)
        };
    }

private:
    struct FilteredPointInternal {
        uint16_t distance_mm;
        float confidence;
    };

    [[nodiscard]] std::optional<FilteredPointInternal> ValidateAndScale(
        const RawMeasurement& m,
        const EnvironmentState& env
    ) const noexcept {
        switch (m.type) {
            case SensorType::Ultrasonic: {
                if (m.raw_value >= 180 && m.raw_value <= 24000) {
                    const float v_sound = CalculateSoundSpeed(env.temperature_celsius);
                    const auto dist = static_cast<uint16_t>((m.raw_value * v_sound) * 0.5f);
                    return FilteredPointInternal{dist, 0.70f};
                }
                break;
            }

            case SensorType::OpticalToF: {
                const auto dist = static_cast<uint16_t>(m.raw_value);
                if (dist >= 20 && dist <= 4000) {
                    float conf = 0.90f;
                    if (env.bright_sunlight || m.ambient_noise > 1500) {
                        conf = (m.signal_quality > 500) ? 0.35f : 0.10f;
                    }
                    return FilteredPointInternal{dist, conf};
                }
                break;
            }

            case SensorType::MmWaveRadar: {
                const auto dist = static_cast<uint16_t>(m.raw_value);
                if (dist >= 100 && dist <= 15000) {
                    return FilteredPointInternal{dist, 0.85f};
                }
                break;
            }
        }
        return std::nullopt;
    }
};

} // namespace embedded::sensing

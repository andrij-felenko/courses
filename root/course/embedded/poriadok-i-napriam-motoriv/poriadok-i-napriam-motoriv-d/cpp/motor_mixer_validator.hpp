/* ============================================================================
 * motor_mixer_validator.hpp — Ідіоматичний валідатор мікшера на C++20
 * ============================================================================ */
#pragma once
#include <array>
#include <span>
#include <expected>
#include <cmath>
#include <cstdint>

enum class SpinDirection : int8_t {
    Ccw =  1, // Проти годинникової стрілки
    Cw  = -1  // За годинниковою стрілкою
};

enum class ValidationError : uint8_t {
    RollSignMismatch,
    PitchSignMismatch,
    YawSignMismatch,
    ThrustUnbalanced,
    YawTorqueImbalance
};

struct MotorGeometry {
    float x_offset{0.0f}; // Поздовжнє плече (вперед: +X, метри)
    float y_offset{0.0f}; // Поперечне плече (праворуч: +Y, метри)
    SpinDirection spin{SpinDirection::Ccw};
};

struct MotorMixEntry {
    float roll{0.0f};
    float pitch{0.0f};
    float yaw{0.0f};
    float throttle{1.0f};
};

template <size_t MotorCount>
class FrameMixerValidator {
public:
    using ConfigArray   = std::array<MotorGeometry, MotorCount>;
    using MixerArray    = std::array<MotorMixEntry, MotorCount>;
    using ValidationRes = std::expected<void, ValidationError>;

    constexpr FrameMixerValidator(const ConfigArray& geom, const MixerArray& mix)
        : geometry_(geom), mixer_(mix) {}

    [[nodiscard]] constexpr ValidationRes validate() const noexcept {
        float total_yaw_bias   = 0.0f;
        float total_roll_sum   = 0.0f;
        float total_pitch_sum  = 0.0f;

        for (size_t i = 0; i < MotorCount; ++i) {
            const auto& [x, y, spin] = geometry_[i];
            const auto& [r, p, y_mix, thr] = mixer_[i];

            // 1. Валідація знаку осі Roll
            if (std::abs(y) > 0.001f) {
                const float expected_roll = (y > 0.0f) ? -1.0f : 1.0f;
                if ((r * expected_roll) < 0.0f) {
                    return std::unexpected(ValidationError::RollSignMismatch);
                }
            }

            // 2. Валідація знаку осі Pitch
            if (std::abs(x) > 0.001f) {
                const float expected_pitch = (x > 0.0f) ? -1.0f : 1.0f;
                if ((p * expected_pitch) < 0.0f) {
                    return std::unexpected(ValidationError::PitchSignMismatch);
                }
            }

            // 3. Валідація знаку реактивного моменту Yaw
            const float expected_yaw = (spin == SpinDirection::Ccw) ? 1.0f : -1.0f;
            if ((y_mix * expected_yaw) < 0.0f) {
                return std::unexpected(ValidationError::YawSignMismatch);
            }

            total_yaw_bias  += static_cast<float>(spin);
            total_roll_sum  += r;
            total_pitch_sum += p;
        }

        // Перевірка нульового балансу моментів перерозподілу
        if (std::abs(total_roll_sum) > 0.001f || std::abs(total_pitch_sum) > 0.001f) {
            return std::unexpected(ValidationError::ThrustUnbalanced);
        }

        // Перевірка паритету CW / CCW моторів для усунення дрейфу по Yaw
        if (std::abs(total_yaw_bias) > 0.001f) {
            return std::unexpected(ValidationError::YawTorqueImbalance);
        }

        return {};
    }

private:
    ConfigArray geometry_;
    MixerArray mixer_;
};

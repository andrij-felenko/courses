#include <cstdint>
#include <algorithm>
#include <array>
#include <span>

enum class Direction : int8_t {
    Negative = -1,
    Hold     = 0,
    Positive = 1
};

enum class EngagementState : int8_t {
    EngagedNegative = -1,
    CrossingGap     = 0,
    EngagedPositive = 1
};

struct BacklashSettings {
    int32_t backlash_steps{0};      // Повний люфт у кроках
    int32_t max_speed_hz{2000};     // Максимальна швидкість вибірки (крок/с)
    int32_t acceleration_hz2{10000};// Прискорення вибірки (крок/с^2)
    int32_t deadband_threshold{2};  // Поріг чутливості до зміни напрямку
};

struct CompensationResult {
    int32_t steps_to_issue;
    bool is_in_backlash_gap;
};

template <size_t AxisCount = 3>
class MultiAxisBacklashCompensator {
public:
    constexpr MultiAxisBacklashCompensator() = default;

    void configure_axis(size_t axis_idx, const BacklashSettings& settings) {
        if (axis_idx < AxisCount) {
            settings_[axis_idx] = settings;
            state_[axis_idx] = EngagementState::EngagedPositive;
            last_direction_[axis_idx] = Direction::Positive;
            gap_progress_[axis_idx] = 0;
            current_speed_[axis_idx] = 0.0f;
            sub_step_accumulator_[axis_idx] = 0.0f;
        }
    }

    void reset_to_homed_state(size_t axis_idx, Direction home_approach_dir) {
        if (axis_idx >= AxisCount) return;
        
        state_[axis_idx] = (home_approach_dir == Direction::Positive) 
                           ? EngagementState::EngagedPositive 
                           : EngagementState::EngagedNegative;
        last_direction_[axis_idx] = home_approach_dir;
        gap_progress_[axis_idx] = 0;
        current_speed_[axis_idx] = 0.0f;
        sub_step_accumulator_[axis_idx] = 0.0f;
    }

    [[nodiscard]] CompensationResult process_axis_quantum(
        size_t axis_idx, 
        Direction commanded_dir, 
        float dt_seconds) noexcept 
    {
        if (axis_idx >= AxisCount) {
            return {0, false};
        }

        const auto& cfg = settings_[axis_idx];
        if (cfg.backlash_steps <= 0) {
            return {1, false}; // Люфт нульовий — передаємо плановий крок
        }

        // Детекція реверсу
        if (commanded_dir != Direction::Hold && commanded_dir != last_direction_[axis_idx]) {
            if (state_[axis_idx] != EngagementState::CrossingGap) {
                state_[axis_idx] = EngagementState::CrossingGap;
                gap_progress_[axis_idx] = 0;
                current_speed_[axis_idx] = 0.0f;
            }
            last_direction_[axis_idx] = commanded_dir;
        }

        if (state_[axis_idx] == EngagementState::CrossingGap) {
            // Профіль розгону з обмеженням прискорення
            current_speed_[axis_idx] += static_cast<float>(cfg.acceleration_hz2) * dt_seconds;
            current_speed_[axis_idx] = std::min(current_speed_[axis_idx], static_cast<float>(cfg.max_speed_hz));

            float delta_steps_real = current_speed_[axis_idx] * dt_seconds + sub_step_accumulator_[axis_idx];
            auto steps_to_emit = static_cast<int32_t>(delta_steps_real);
            sub_step_accumulator_[axis_idx] = delta_steps_real - static_cast<float>(steps_to_emit);

            int32_t remaining = cfg.backlash_steps - gap_progress_[axis_idx];
            if (steps_to_emit >= remaining) {
                steps_to_emit = remaining;
                gap_progress_[axis_idx] += steps_to_emit;
                state_[axis_idx] = (last_direction_[axis_idx] == Direction::Positive)
                                   ? EngagementState::EngagedPositive
                                   : EngagementState::EngagedNegative;
                current_speed_[axis_idx] = 0.0f;
                sub_step_accumulator_[axis_idx] = 0.0f;
                return {steps_to_emit, false};
            }

            gap_progress_[axis_idx] += steps_to_emit;
            return {steps_to_emit, true};
        }

        return {1, false};
    }

    [[nodiscard]] EngagementState get_axis_state(size_t axis_idx) const noexcept {
        return (axis_idx < AxisCount) ? state_[axis_idx] : EngagementState::CrossingGap;
    }

private:
    std::array<BacklashSettings, AxisCount> settings_{};
    std::array<EngagementState, AxisCount> state_{};
    std::array<Direction, AxisCount> last_direction_{};
    std::array<int32_t, AxisCount> gap_progress_{};
    std::array<float, AxisCount> current_speed_{};
    std::array<float, AxisCount> sub_step_accumulator_{};
};

#include <cstdint>
#include <array>
#include <algorithm>
#include <cmath>
#include <span>
#include <expected>

namespace embedded::bench {

constexpr size_t kLidarRaysCount = 64;
constexpr size_t kHiddenNeurons = 16;
constexpr float kMaxAllowedSpeedMmS = 2000.0f;
constexpr float kEmergencyBrakeDecel = 4000.0f;
constexpr float kSafeDistanceMinMm = 300.0f;
constexpr float kConfHystHigh = 0.80f;
constexpr float kConfHystLow = 0.65f;
constexpr uint32_t kMinDwellCycles = 20;
constexpr uint32_t kWcetDeadlineCycles = 360000;

struct SensorFrame {
    std::array<float, 4> distance_sonar_mm{};
    std::array<int8_t, kLidarRaysCount> lidar_depth_int8{};
    float battery_voltage_v{12.0f};
    float motor_temp_c{45.0f};
};

struct MlInferenceOutput {
    float target_speed_mm_s{0.0f};
    float confidence{0.0f};
    bool  deadline_met{false};
};

enum class ArbiterMode : uint8_t {
    RuleSafeDefault,
    MlOptimalPath,
    RuleRateLimited,
    RuleEmergency
};

struct StepOutput {
    float command_speed_mm_s{0.0f};
    ArbiterMode active_mode{ArbiterMode::RuleSafeDefault};
    uint32_t execution_cycles{0};
};

class HybridArbiterBenchmark {
public:
    constexpr HybridArbiterBenchmark() noexcept = default;

    [[nodiscard]] StepOutput execute_cycle(
        const SensorFrame& sensors,
        const MlInferenceOutput& ml_output,
        float dt_sec
    ) noexcept {
        const uint32_t start_tick = get_cycles();
        ++mode_dwell_counter_;

        const float safe_limit = compute_safe_speed(sensors, last_output_speed_, dt_sec);

        // 1. Апаратний захист від перегріву та просідання напруги
        if (sensors.motor_temp_c > 85.0f || sensors.battery_voltage_v < 10.5f) {
            current_mode_ = ArbiterMode::RuleEmergency;
            ++safety_interventions_;
            last_output_speed_ = 0.0f;
            return {
                .command_speed_mm_s = 0.0f,
                .active_mode = ArbiterMode::RuleEmergency,
                .execution_cycles = get_cycles() - start_tick
            };
        }

        // 2. Гістерезисна фільтрація впевненості моделі
        bool ml_trusted = false;
        if (current_mode_ == ArbiterMode::MlOptimalPath) {
            ml_trusted = ml_output.deadline_met && (ml_output.confidence >= kConfHystLow);
        } else if (mode_dwell_counter_ >= kMinDwellCycles) {
            ml_trusted = ml_output.deadline_met && (ml_output.confidence >= kConfHystHigh);
        }

        // 3. Селекція виходу з контролем інваріантів безпеки
        if (ml_trusted) {
            const float ml_speed = ml_output.target_speed_mm_s;
            if (ml_speed <= safe_limit) {
                current_mode_ = ArbiterMode::MlOptimalPath;
                last_output_speed_ = ml_speed;
                return {
                    .command_speed_mm_s = ml_speed,
                    .active_mode = ArbiterMode::MlOptimalPath,
                    .execution_cycles = get_cycles() - start_tick
                };
            }

            // Бар'єр обмежує вихід до безпечної межі
            current_mode_ = ArbiterMode::RuleRateLimited;
            ++safety_interventions_;
            last_output_speed_ = safe_limit;
            return {
                .command_speed_mm_s = safe_limit,
                .active_mode = ArbiterMode::RuleRateLimited,
                .execution_cycles = get_cycles() - start_tick
            };
        }

        // 4. Резервний вихід за замовчуванням
        if (current_mode_ == ArbiterMode::MlOptimalPath) {
            mode_dwell_counter_ = 0;
            if (!ml_output.deadline_met) {
                ++ml_overtime_events_;
            }
        }
        current_mode_ = ArbiterMode::RuleSafeDefault;
        last_output_speed_ = safe_limit;
        return {
            .command_speed_mm_s = safe_limit,
            .active_mode = ArbiterMode::RuleSafeDefault,
            .execution_cycles = get_cycles() - start_tick
        };
    }

    [[nodiscard]] constexpr uint32_t safety_interventions() const noexcept {
        return safety_interventions_;
    }

    [[nodiscard]] constexpr uint32_t overtime_events() const noexcept {
        return ml_overtime_events_;
    }

private:
    [[nodiscard]] static float compute_safe_speed(
        const SensorFrame& sensors,
        float current_speed,
        float dt_sec
    ) noexcept {
        const auto min_it = std::min_element(sensors.distance_sonar_mm.begin(), sensors.distance_sonar_mm.end());
        const float min_dist = (min_it != sensors.distance_sonar_mm.end()) ? *min_it : 0.0f;

        if (min_dist <= kSafeDistanceMinMm) {
            const float decel_step = kEmergencyBrakeDecel * dt_sec;
            if (current_speed > decel_step) return current_speed - decel_step;
            if (current_speed < -decel_step) return current_speed + decel_step;
            return 0.0f;
        }

        const float allowed_speed = (min_dist - kSafeDistanceMinMm) * 2.5f;
        return std::min(allowed_speed, kMaxAllowedSpeedMmS);
    }

    [[nodiscard]] static uint32_t get_cycles() noexcept {
        #if defined(__arm__) || defined(__thumb__)
        volatile uint32_t* DWT_CYCCNT = reinterpret_cast<volatile uint32_t*>(0xE0001004);
        return *DWT_CYCCNT;
        #else
        static uint32_t mock_ticks{0};
        return mock_ticks += 42;
        #endif
    }

    float last_output_speed_{0.0f};
    ArbiterMode current_mode_{ArbiterMode::RuleSafeDefault};
    uint32_t mode_dwell_counter_{0};
    uint32_t safety_interventions_{0};
    uint32_t ml_overtime_events_{0};
};

} // namespace embedded::bench

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <numeric>

enum class TestState : uint8_t {
    Idle,
    Evacuating,
    Settling,
    Measuring,
    Passed,
    FailedLeak,
    FailedTimeout
};

struct TestConfig {
    float target_vacuum_kpa{30.0f};
    float max_leak_rate_kpa_min{0.10f};
    uint32_t settling_time_ms{15000};
    uint32_t measure_time_ms{45000};
};

struct ActuatorControl {
    bool pump_enable{false};
    bool valve_enable{false};
};

class VacuumDecayTester {
public:
    static constexpr size_t kMaxSamples = 128;

    explicit constexpr VacuumDecayTester(const TestConfig& config) noexcept
        : config_(config) {}

    void start(float ambient_pressure_kpa, uint32_t now_ms) noexcept {
        start_pressure_kpa_ = ambient_pressure_kpa;
        current_pressure_kpa_ = ambient_pressure_kpa;
        state_ = TestState::Evacuating;
        state_start_ms_ = now_ms;
        sample_count_ = 0;
        last_sample_ms_ = now_ms;
        calculated_leak_rate_ = 0.0f;
    }

    ActuatorControl update(float p_kpa, uint32_t now_ms) noexcept {
        current_pressure_kpa_ = p_kpa;
        const uint32_t elapsed = now_ms - state_start_ms_;
        ActuatorControl ctrl{};

        switch (state_) {
            case TestState::Evacuating:
                ctrl.pump_enable = true;
                ctrl.valve_enable = true;
                if ((start_pressure_kpa_ - p_kpa) >= config_.target_vacuum_kpa) {
                    state_ = TestState::Settling;
                    state_start_ms_ = now_ms;
                    ctrl.pump_enable = false;
                } else if (elapsed > 30000) {
                    state_ = TestState::FailedTimeout;
                    ctrl.pump_enable = false;
                    ctrl.valve_enable = false;
                }
                break;

            case TestState::Settling:
                ctrl.pump_enable = false;
                ctrl.valve_enable = true;
                if (elapsed >= config_.settling_time_ms) {
                    state_ = TestState::Measuring;
                    state_start_ms_ = now_ms;
                    sample_count_ = 0;
                    last_sample_ms_ = now_ms;
                }
                break;

            case TestState::Measuring:
                ctrl.pump_enable = false;
                ctrl.valve_enable = true;
                if (now_ms - last_sample_ms_ >= 500 && sample_count_ < kMaxSamples) {
                    time_samples_[sample_count_] = static_cast<float>(elapsed) / 1000.0f;
                    pressure_samples_[sample_count_] = p_kpa;
                    ++sample_count_;
                    last_sample_ms_ = now_ms;
                }

                if (elapsed >= config_.measure_time_ms) {
                    float slope_sec = compute_ols_slope(
                        std::span(time_samples_.data(), sample_count_),
                        std::span(pressure_samples_.data(), sample_count_)
                    );
                    calculated_leak_rate_ = slope_sec * 60.0f;

                    state_ = (calculated_leak_rate_ <= config_.max_leak_rate_kpa_min)
                             ? TestState::Passed
                             : TestState::FailedLeak;
                    ctrl.valve_enable = false;
                }
                break;

            default:
                ctrl.pump_enable = false;
                ctrl.valve_enable = false;
                break;
        }
        return ctrl;
    }

    [[nodiscard]] TestState state() const noexcept { return state_; }
    [[nodiscard]] float leak_rate_kpa_min() const noexcept { return calculated_leak_rate_; }

private:
    static float compute_ols_slope(std::span<const float> x, std::span<const float> y) noexcept {
        if (x.size() < 2 || x.size() != y.size()) return 0.0f;
        const auto n = static_cast<float>(x.size());
        float sum_x = 0.0f, sum_y = 0.0f, sum_xy = 0.0f, sum_xx = 0.0f;
        for (size_t i = 0; i < x.size(); ++i) {
            sum_x += x[i];
            sum_y += y[i];
            sum_xy += x[i] * y[i];
            sum_xx += x[i] * x[i];
        }
        const float denom = n * sum_xx - sum_x * sum_x;
        if (denom == 0.0f) return 0.0f;
        return (n * sum_xy - sum_x * sum_y) / denom;
    }

    TestConfig config_{};
    TestState state_{TestState::Idle};
    uint32_t state_start_ms_{0};
    uint32_t last_sample_ms_{0};
    float start_pressure_kpa_{101.3f};
    float current_pressure_kpa_{101.3f};
    float calculated_leak_rate_{0.0f};

    std::array<float, kMaxSamples> time_samples_{};
    std::array<float, kMaxSamples> pressure_samples_{};
    size_t sample_count_{0};
};

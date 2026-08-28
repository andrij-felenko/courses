#include <cstdint>
#include <algorithm>

namespace power_control {

class FocDeadTimeCompensator {
public:
    struct Config {
        uint32_t compensation_ticks{15}; // Тактів корекції
        float current_threshold_a{0.2f}; // Поріг струму для лінійного переходу, А
    };

    explicit FocDeadTimeCompensator(const Config& cfg) noexcept : config_(cfg) {}

    struct PwmDutyOutput {
        uint32_t ccr_a;
        uint32_t ccr_b;
        uint32_t ccr_c;
    };

    PwmDutyOutput compensate(uint32_t raw_ccr_a, uint32_t raw_ccr_b, uint32_t raw_ccr_c,
                            float i_a, float i_b, float i_c) const noexcept {
        const auto calc_delta = [this](float current) noexcept -> int32_t {
            const float norm = std::clamp(current / config_.current_threshold_a, -1.0f, 1.0f);
            return static_cast<int32_t>(norm * static_cast<float>(config_.compensation_ticks));
        };

        return PwmDutyOutput{
            static_cast<uint32_t>(static_cast<int32_t>(raw_ccr_a) + calc_delta(i_a)),
            static_cast<uint32_t>(static_cast<int32_t>(raw_ccr_b) + calc_delta(i_b)),
            static_cast<uint32_t>(static_cast<int32_t>(raw_ccr_c) + calc_delta(i_c))
        };
    }

private:
    Config config_;
};

} // namespace power_control

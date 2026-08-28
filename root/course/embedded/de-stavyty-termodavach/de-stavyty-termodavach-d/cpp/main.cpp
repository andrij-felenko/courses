// Обчислення одного кроку компенсатора самонагріву в ООП-стилі
#include <cmath>

class ThermalStepFilter {
public:
    constexpr ThermalStepFilter(float r_th1, float tau1, float r_th2, float tau2) noexcept
        : r_th1_(r_th1), tau1_(tau1), r_th2_(r_th2), tau2_(tau2) {}

    [[nodiscard]] float process(float raw_temp, float heat_power, float dt) noexcept {
        const float a1 = std::exp(-dt / tau1_);
        const float a2 = std::exp(-dt / tau2_);

        state1_ = (a1 * state1_) + ((1.0f - a1) * (r_th1_ * heat_power));
        state2_ = (a2 * state2_) + ((1.0f - a2) * (r_th2_ * heat_power));

        const float delta_self = state1_ + state2_;
        return raw_temp - delta_self;
    }

    void reset() noexcept {
        state1_ = 0.0f;
        state2_ = 0.0f;
    }

private:
    float r_th1_{12.0f};
    float tau1_{8.0f};
    float r_th2_{45.0f};
    float tau2_{120.0f};
    float state1_{0.0f};
    float state2_{0.0f};
};

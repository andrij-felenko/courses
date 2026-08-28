#include <cmath>
#include <numbers>

[[nodiscard]] constexpr float wrap_pi_fmod(float angle) noexcept {
    constexpr float kTwoPi = 2.0f * std::numbers::pi_v<float>;
    float a = std::fmod(angle + std::numbers::pi_v<float>, kTwoPi);
    if (a < 0.0f) {
        a += kTwoPi;
    }
    return a - std::numbers::pi_v<float>;
}

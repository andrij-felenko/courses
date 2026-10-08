#include <cmath>
#include <numbers>

struct ResolverResult {
    float angle_rad{0.0f};
    bool fault{false};
};

ResolverResult process_resolver_signals(float u_sin, float u_cos, float ref_amplitude, float tolerance) noexcept {
    const float magnitude_sq = u_sin * u_sin + u_cos * u_cos;
    const float expected_sq = ref_amplitude * ref_amplitude;
    
    if (std::abs(magnitude_sq - expected_sq) > tolerance) {
        return {.angle_rad = 0.0f, .fault = true};
    }
    
    float angle = std::atan2(u_sin, u_cos);
    if (angle < 0.0f) {
        angle += 2.0f * std::numbers::pi_v<float>;
    }
    return {.angle_rad = angle, .fault = false};
}

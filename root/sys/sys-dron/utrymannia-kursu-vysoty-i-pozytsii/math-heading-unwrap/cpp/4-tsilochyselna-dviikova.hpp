#include <cstdint>
#include <numbers>

[[nodiscard]] constexpr float calc_heading_error_bam(float target_rad, float meas_rad) noexcept {
    constexpr float kRadToBam = 32768.0f / std::numbers::pi_v<float>;
    constexpr float kBamToRad = std::numbers::pi_v<float> / 32768.0f;

    const auto target_bam = static_cast<uint16_t>(target_rad * kRadToBam);
    const auto meas_bam   = static_cast<uint16_t>(meas_rad * kRadToBam);

    const auto diff_bam = static_cast<int16_t>(target_bam - meas_bam);
    return static_cast<float>(diff_bam) * kBamToRad;
}

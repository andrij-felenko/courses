#include <array>
#include <vector>
#include <span>
#include <optional>
#include <algorithm>
#include <cstddef>

namespace photometry {

constexpr double KM_PHOTOPIC = 683.002; // лм/Вт
constexpr double CIE_V_MIN_NM = 380.0;
constexpr double CIE_V_MAX_NM = 780.0;
constexpr double CIE_V_STEP_NM = 5.0;

// Таблиця CIE 1924 V(λ) з кроком 5 нм
constexpr std::array<double, 81> CIE_V_LAMBDA = {
    0.000039, 0.000064, 0.000120, 0.000217, 0.000396,
    0.000640, 0.001210, 0.002180, 0.004000, 0.007300,
    0.011600, 0.016840, 0.023000, 0.029800, 0.038000,
    0.048000, 0.060000, 0.073900, 0.090980, 0.112600,
    0.139020, 0.169300, 0.208020, 0.258600, 0.323000,
    0.407300, 0.503000, 0.608200, 0.710000, 0.793200,
    0.862000, 0.914850, 0.954000, 0.980300, 0.994950,
    1.000000, 0.995000, 0.978600, 0.952000, 0.915400,
    0.870000, 0.816300, 0.757000, 0.694900, 0.631000,
    0.566800, 0.503000, 0.441200, 0.381000, 0.321000,
    0.265000, 0.217000, 0.175000, 0.138200, 0.107000,
    0.081600, 0.061000, 0.044580, 0.032000, 0.023200,
    0.017000, 0.011920, 0.008210, 0.005723, 0.004102,
    0.002929, 0.002091, 0.001484, 0.001047, 0.000740,
    0.000520, 0.000361, 0.000249, 0.000172, 0.000120,
    0.000085, 0.000059, 0.000041, 0.000029, 0.000020,
    0.000015
};

struct SpectralSample {
    double wavelength_nm{0.0};
    double spectral_power{0.0};
};

struct PhotometricResult {
    double radiant_flux_w{0.0};     // Радіометрична потужність (Вт)
    double luminous_flux_lm{0.0};   // Світловий потік (лм) або освітленість (лк)
    double luminous_efficacy{0.0};  // Світлова віддача (лм/Вт)
};

[[nodiscard]] constexpr double interpolate_v_lambda(double wavelength_nm) noexcept {
    if (wavelength_nm < CIE_V_MIN_NM || wavelength_nm > CIE_V_MAX_NM) {
        return 0.0;
    }
    const double pos = (wavelength_nm - CIE_V_MIN_NM) / CIE_V_STEP_NM;
    const auto idx = static_cast<std::size_t>(pos);
    if (idx >= CIE_V_LAMBDA.size() - 1) {
        return CIE_V_LAMBDA.back();
    }
    const double frac = pos - static_cast<double>(idx);
    return CIE_V_LAMBDA[idx] * (1.0 - frac) + CIE_V_LAMBDA[idx + 1] * frac;
}

[[nodiscard]] std::optional<PhotometricResult> calculate(std::span<const SpectralSample> samples) noexcept {
    if (samples.size() < 2) {
        return std::nullopt;
    }

    double total_radiant_flux = 0.0;
    double total_weighted_integral = 0.0;

    for (std::size_t i = 0; i < samples.size() - 1; ++i) {
        const double w1 = samples[i].wavelength_nm;
        const double w2 = samples[i + 1].wavelength_nm;
        const double dw = w2 - w1;

        if (dw <= 0.0) {
            return std::nullopt; // Довжини хвиль мусять строго зростати
        }

        const double p1 = samples[i].spectral_power;
        const double p2 = samples[i + 1].spectral_power;

        total_radiant_flux += 0.5 * (p1 + p2) * dw;

        const double v1 = interpolate_v_lambda(w1);
        const double v2 = interpolate_v_lambda(w2);
        total_weighted_integral += 0.5 * (p1 * v1 + p2 * v2) * dw;
    }

    const double luminous_flux = KM_PHOTOPIC * total_weighted_integral;
    const double efficacy = (total_radiant_flux > 1e-12)
        ? (luminous_flux / total_radiant_flux)
        : 0.0;

    return PhotometricResult{
        .radiant_flux_w = total_radiant_flux,
        .luminous_flux_lm = luminous_flux,
        .luminous_efficacy = efficacy
    };
}

} // namespace photometry

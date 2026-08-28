#include <cmath>
#include <numeric>
#include <algorithm>

namespace fdt {

double LinearResponseCalculator::callen_welton_factor(double omega_rad_s) const noexcept {
    const double abs_omega = std::abs(omega_rad_s);
    if (abs_omega < 1e-12) {
        // Границя низьких частот: coth(x) ≈ 1/x
        return (2.0 * env_.k_B * env_.temperature_kelvin) / (env_.hbar * 1e-12);
    }
    const double x = (env_.hbar * abs_omega) / (2.0 * env_.k_B * env_.temperature_kelvin);
    if (x < 1e-4) {
        // Класична границя Тейлора: coth(x) ≈ 1/x + x/3
        return (1.0 / x) + (x / 3.0);
    }
    return 1.0 / std::tanh(x);
}

std::expected<double, FdtError>
LinearResponseCalculator::theoretical_psd(double omega_rad_s, double im_chi) const noexcept {
    if (env_.temperature_kelvin <= 0.0) {
        return std::unexpected(FdtError::TemperatureOutOfRange);
    }
    const double factor = callen_welton_factor(omega_rad_s);
    return env_.hbar * factor * im_chi;
}

std::expected<std::vector<double>, FdtError>
KramersKronigTransform::reconstruct_real_part(std::span<const double> omegas,
                                              std::span<const double> im_chi) {
    if (omegas.size() != im_chi.size() || omegas.empty()) {
        return std::unexpected(FdtError::InvalidDataSize);
    }

    const size_t N = omegas.size();
    std::vector<double> re_chi(N, 0.0);

    // Чисельне інтегрування методом трапецій із вилученням сингулярності (Principal Value)
    for (size_t i = 0; i < N; ++i) {
        double w_i = omegas[i];
        double sum = 0.0;

        for (size_t j = 0; j < N - 1; ++j) {
            if (i == j || i == j + 1) continue; // Пропускаємо точку сингулярності за Коші

            double x0 = omegas[j];
            double x1 = omegas[j + 1];
            double y0 = (x0 * im_chi[j]) / (x0 * x0 - w_i * w_i);
            double y1 = (x1 * im_chi[j + 1]) / (x1 * x1 - w_i * w_i);

            sum += 0.5 * (y0 + y1) * (x1 - x0);
        }
        re_chi[i] = (2.0 / M_PI) * sum;
    }

    return re_chi;
}

} // namespace fdt

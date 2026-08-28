// C++20: RAII-обробник діелектричного спектрометра з квадратурним DSP-ядром
#include <cmath>
#include <complex>
#include <optional>
#include <span>
#include <vector>
#include <numbers>

struct DielectricSpectrumPoint {
    double frequency_hz{0.0};
    double eps_real{1.0};
    double eps_imag{0.0};
    double loss_tangent{0.0};
};

class DigitalPermittivityAnalyzer {
public:
    constexpr DigitalPermittivityAnalyzer(double c0_farads, double cp_farads) noexcept
        : c0_{c0_farads}, cp_{cp_farads} {}

    // Квадратурне детектування імпедансу за вибірками напруги та струму
    [[nodiscard]] std::optional<DielectricSpectrumPoint> process_quadrature(
        double frequency_hz,
        std::span<const float> voltage_samples,
        std::span<const float> current_samples) const {

        if (voltage_samples.size() != current_samples.size() || voltage_samples.empty()) {
            return std::nullopt;
        }

        const size_t n = voltage_samples.size();
        double v_real = 0.0, v_imag = 0.0;
        double i_real = 0.0, i_imag = 0.0;

        for (size_t k = 0; k < n; ++k) {
            const double phase = 2.0 * std::numbers::pi * static_cast<double>(k) / static_cast<double>(n);
            const double cos_p = std::cos(phase);
            const double sin_p = std::sin(phase);

            v_real += voltage_samples[k] * cos_p;
            v_imag += voltage_samples[k] * sin_p;
            i_real += current_samples[k] * cos_p;
            i_imag += current_samples[k] * sin_p;
        }

        const std::complex<double> v_complex{v_real * 2.0 / n, v_imag * 2.0 / n};
        const std::complex<double> i_complex{i_real * 2.0 / n, i_imag * 2.0 / n};

        if (std::abs(v_complex) < 1e-9) {
            return std::nullopt;
        }

        // Комплексна провідність Y = I / V
        const std::complex<double> admittance = i_complex / v_complex;
        const double omega = 2.0 * std::numbers::pi * frequency_hz;

        const double cap_total = admittance.imag() / omega;
        const double conductance = admittance.real();

        DielectricSpectrumPoint pt;
        pt.frequency_hz = frequency_hz;
        pt.eps_real = (cap_total - cp_) / c0_;
        pt.eps_imag = conductance / (omega * c0_);
        pt.loss_tangent = (pt.eps_real > 1e-6) ? (pt.eps_imag / pt.eps_real) : 0.0;

        return pt;
    }

private:
    double c0_;
    double cp_;
};

#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <span>

class SkinEffectAnalytical {
public:
    using Complex = std::complex<double>;

    explicit SkinEffectAnalytical(double conductivity_sm = 5.8e7, double relative_mu = 1.0)
        : sigma_(conductivity_sm), mu_r_(relative_mu) {}

    [[nodiscard]] double skinDepth(double frequencyHz) const noexcept {
        constexpr double mu0 = 4.0 * std::numbers::pi * 1e-7;
        const double omega = 2.0 * std::numbers::pi * frequencyHz;
        return std::sqrt(2.0 / (omega * (mu0 * mu_r_) * sigma_));
    }

    [[nodiscard]] double acToDcRatio(double wireRadiusM, double frequencyHz) const {
        const double delta = skinDepth(frequencyHz);
        const double x = wireRadiusM / delta;

        if (x < 0.1) {
            return 1.0 + (1.0 / 48.0) * std::pow(x, 4.0);
        }
        if (x > 15.0) {
            return 0.5 * x + 0.25 + 0.094 / x;
        }

        const Complex k{(1.0 / delta), (1.0 / delta)};
        const Complex ka = k * wireRadiusM;

        const Complex i0 = besselI0(ka);
        const Complex i1 = besselI1(ka);

        const Complex ratio = (ka / 2.0) * (i0 / i1);
        return ratio.real();
    }

private:
    double sigma_;
    double mu_r_;

    static Complex besselI0(Complex z) noexcept {
        Complex sum{1.0, 0.0};
        Complex term{1.0, 0.0};
        const Complex z_sq_4 = (z * z) / 4.0;

        for (int k = 1; k <= 60; ++k) {
            term = term * z_sq_4 / static_cast<double>(k * k);
            sum += term;
            if (std::abs(term) < 1e-12 * std::abs(sum)) break;
        }
        return sum;
    }

    static Complex besselI1(Complex z) noexcept {
        Complex sum = z / 2.0;
        Complex term = z / 2.0;
        const Complex z_sq_4 = (z * z) / 4.0;

        for (int k = 1; k <= 60; ++k) {
            term = term * z_sq_4 / static_cast<double>(k * (k + 1));
            sum += term;
            if (std::abs(term) < 1e-12 * std::abs(sum)) break;
        }
        return sum;
    }
};

class SkinEffectFDMSolver {
public:
    using Complex = std::complex<double>;

    SkinEffectFDMSolver(double thicknessM, std::size_t nodes = 200)
        : thickness_(thicknessM), nodes_(nodes), dx_(thicknessM / static_cast<double>(nodes - 1)) {}

    [[nodiscard]] std::vector<Complex> solveField(double frequencyHz, std::span<const double> sigmaProfile, double muR = 1.0) const {
        constexpr double mu0 = 4.0 * std::numbers::pi * 1e-7;
        const double omega = 2.0 * std::numbers::pi * frequencyHz;
        const std::size_t n = nodes_;

        std::vector<Complex> a(n, 0.0), b(n, 0.0), c(n, 0.0), rhs(n, 0.0);

        b[0] = 1.0; rhs[0] = 1.0;
        b[n - 1] = 1.0; rhs[n - 1] = 1.0;

        for (std::size_t i = 1; i < n - 1; ++i) {
            const double sigma_i = sigmaProfile[i];
            a[i] = 1.0;
            c[i] = 1.0;
            b[i] = Complex(-2.0, - omega * (mu0 * muR) * sigma_i * (dx_ * dx_));
            rhs[i] = 0.0;
        }

        std::vector<Complex> c_prime(n, 0.0), d_prime(n, 0.0);
        c_prime[0] = c[0] / b[0];
        d_prime[0] = rhs[0] / b[0];

        for (std::size_t i = 1; i < n; ++i) {
            Complex temp = b[i] - a[i] * c_prime[i - 1];
            c_prime[i] = c[i] / temp;
            d_prime[i] = (rhs[i] - a[i] * d_prime[i - 1]) / temp;
        }

        std::vector<Complex> e_field(n, 0.0);
        e_field[n - 1] = d_prime[n - 1];
        for (std::size_t i = n - 2; i < n; --i) {
            e_field[i] = d_prime[i] - c_prime[i] * e_field[i + 1];
        }

        return e_field;
    }

private:
    double thickness_;
    std::size_t nodes_;
    double dx_;
};

int main() {
    constexpr double wireRadius = 0.001; // 1 мм
    SkinEffectAnalytical calc(5.8e7, 1.0); // Мідь

    const std::vector<double> freqs = {50.0, 1e3, 10e3, 100e3, 1e6, 10e6};

    std::cout << std::left << std::setw(15) << "Частота (Гц)"
              << std::setw(18) << "Скін-шар (мкм)"
              << std::setw(15) << "R_AC / R_DC" << "\n";
    std::cout << std::string(48, '-') << "\n";

    for (double f : freqs) {
        double delta = calc.skinDepth(f);
        double ratio = calc.acToDcRatio(wireRadius, f);

        std::cout << std::left << std::setw(15) << f
                  << std::setw(18) << (delta * 1e6)
                  << std::setw(15) << ratio << "\n";
    }

    return 0;
}

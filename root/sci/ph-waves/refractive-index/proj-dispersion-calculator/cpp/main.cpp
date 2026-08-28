#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <string_view>
#include <iomanip>
#include <span >
#include <expected>
#include <stdexcept>

namespace optics {

constexpr double SPEED_OF_LIGHT_M_S = 299792458.0;

enum class DispersionError {
    OutOfSpectralRange,
    NearResonancePole,
    InvalidWavelength
};

struct SellmeierCoefficients {
    std::string_view name;
    std::array<double, 3> B;
    std::array<double, 3> C; // квадрат резонансних довжин у мкм²
    double min_lambda_um;
    double max_lambda_um;
};

class DispersionEngine {
public:
    explicit constexpr DispersionEngine(SellmeierCoefficients mat) noexcept 
        : mat_(mat) {}

    [[nodiscard]] std::expected<double, DispersionError> 
    refractiveIndex(double lambda_um) const noexcept {
        if (lambda_um < mat_.min_lambda_um || lambda_um > mat_.max_lambda_um) {
            return std::unexpected(DispersionError::OutOfSpectralRange);
        }
        const double lam2 = lambda_um * lambda_um;
        double n2 = 1.0;
        for (std::size_t i = 0; i < mat_.B.size(); ++i) {
            const double denom = lam2 - mat_.C[i];
            if (std::abs(denom) < 1e-12) {
                return std::unexpected(DispersionError::NearResonancePole);
            }
            n2 += (mat_.B[i] * lam2) / denom;
        }
        return std::sqrt(n2);
    }

    [[nodiscard]] std::expected<double, DispersionError> 
    groupIndex(double lambda_um, double step_um = 1e-4) const noexcept {
        auto n_res = refractiveIndex(lambda_um);
        auto n_plus = refractiveIndex(lambda_um + step_um);
        auto n_minus = refractiveIndex(lambda_um - step_um);

        if (!n_res || !n_plus || !n_minus) {
            return std::unexpected(DispersionError::NearResonancePole);
        }

        const double dn_dlam = (*n_plus - *n_minus) / (2.0 * step_um);
        return *n_res - lambda_um * dn_dlam;
    }

    [[nodiscard]] std::expected<double, DispersionError> 
    chromaticDispersion(double lambda_um, double step_um = 5e-4) const noexcept {
        auto n_center = refractiveIndex(lambda_um);
        auto n_plus = refractiveIndex(lambda_um + step_um);
        auto n_minus = refractiveIndex(lambda_um - step_um);

        if (!n_center || !n_plus || !n_minus) {
            return std::unexpected(DispersionError::NearResonancePole);
        }

        const double d2n_dlam2 = (*n_plus - 2.0 * (*n_center) + *n_minus) / (step_um * step_um);
        const double c_um_ps = SPEED_OF_LIGHT_M_S * 1e-6; // мкм / пс
        
        const double D_raw = - (lambda_um / c_um_ps) * d2n_dlam2;
        return D_raw * 1000.0; // пс / (нм · км)
    }

    [[nodiscard]] std::string_view name() const noexcept { return mat_.name; }

private:
    SellmeierCoefficients mat_;
};

void analyzeMaterial(const DispersionEngine& engine, std::span<const double> wavelengths) {
    std::cout << "\n=== Аналіз спектральної дисперсії: " << engine.name() << " ===\n"
              << std::fixed << std::setprecision(5)
              << "λ (мкм)  |   n(λ)   |   n_g(λ)  |  D [пс/(нм·км)] |   v_g (10^8 м/с)\n"
              << "---------+----------+-----------+-----------------+------------------\n";

    for (const double lam : wavelengths) {
        auto n = engine.refractiveIndex(lam);
        auto ng = engine.groupIndex(lam);
        auto D = engine.chromaticDispersion(lam);

        if (n && ng && D) {
            const double vg = SPEED_OF_LIGHT_M_S / (*ng) / 1e8;
            std::cout << std::setw(8) << std::setprecision(4) << lam << " | "
                      << std::setw(8) << std::setprecision(5) << *n << " | "
                      << std::setw(9) << std::setprecision(5) << *ng << " | "
                      << std::setw(15) << std::setprecision(3) << *D << " | "
                      << std::setw(16) << std::setprecision(4) << vg << "\n";
        } else {
            std::cout << std::setw(8) << lam << " | ERROR: Out of spectral validity range\n";
        }
    }
}

} // namespace optics

int main() {
    using namespace optics;

    constexpr SellmeierCoefficients nbk7{
        "Schott N-BK7",
        { 1.03961212, 0.231792344, 1.01046945 },
        { 0.00600069867, 0.0200179144, 103.560653 },
        0.300, 2.500
    };

    constexpr SellmeierCoefficients fused_silica{
        "Fused Silica (SiO2)",
        { 0.696166300, 0.407942600, 0.897479400 },
        { 0.00467914826, 0.0135120631, 97.9340025 },
        0.210, 3.700
    };

    const DispersionEngine engine_bk7(nbk7);
    const DispersionEngine engine_silica(fused_silica);

    const std::array<double, 5> wavelengths{ 0.400, 0.5893, 0.850, 1.310, 1.550 };

    analyzeMaterial(engine_bk7, wavelengths);
    analyzeMaterial(engine_silica, wavelengths);

    return 0;
}

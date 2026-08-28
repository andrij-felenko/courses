#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <algorithm>
#include <string_view>

enum class CrystalLattice {
    SimpleCubic,
    BodyCenteredCubic,
    FaceCenteredCubic,
    Diamond
};

struct DiffractionReflection {
    int h{0};
    int k{0};
    int l{0};
    double interplanar_d_nm{0.0};
    double bragg_theta_deg{0.0};
    double two_theta_deg{0.0};
    double relative_intensity{0.0};
};

class DiffractionEngine {
public:
    [[nodiscard]] static constexpr double calculate_structure_factor_sq(
        CrystalLattice lattice, int h, int k, int l) noexcept {
        const int sum = h + k + l;
        const bool even_h = (h % 2 == 0);
        const bool even_k = (k % 2 == 0);
        const bool even_l = (l % 2 == 0);
        const bool same_parity = (even_h == even_k) && (even_k == even_l);

        switch (lattice) {
            case CrystalLattice::SimpleCubic:
                return 1.0;

            case CrystalLattice::BodyCenteredCubic:
                return (sum % 2 == 0) ? 4.0 : 0.0;

            case CrystalLattice::FaceCenteredCubic:
                return same_parity ? 16.0 : 0.0;

            case CrystalLattice::Diamond:
                if (!same_parity) return 0.0;
                if (!even_h) return 32.0; // Усі індекси непарні
                return (sum % 4 == 0) ? 64.0 : 0.0; // Парні індекси, сума 4n
        }
        return 0.0;
    }

    [[nodiscard]] static std::vector<DiffractionReflection> compute_spectrum(
        CrystalLattice lattice,
        double lattice_parameter_a_nm,
        double wavelength_lambda_nm,
        int max_hkl_index = 4) {

        std::vector<DiffractionReflection> reflections;

        for (int h = 0; h <= max_hkl_index; ++h) {
            for (int k = 0; k <= max_hkl_index; ++k) {
                for (int l = 0; l <= max_hkl_index; ++l) {
                    if (h == 0 && k == 0 && l == 0) continue;

                    const double intensity = calculate_structure_factor_sq(lattice, h, k, l);
                    if (intensity <= 0.001) continue;

                    const double hkl_sum_sq = static_cast<double>(h * h + k * k + l * l);
                    const double d = lattice_parameter_a_nm / std::sqrt(hkl_sum_sq);
                    const double sin_theta = wavelength_lambda_nm / (2.0 * d);

                    if (sin_theta <= 1.0) {
                        const double theta_rad = std::asin(sin_theta);
                        const double theta_deg = theta_rad * (180.0 / std::numbers::pi);

                        reflections.push_back(DiffractionReflection{
                            .h = h,
                            .k = k,
                            .l = l,
                            .interplanar_d_nm = d,
                            .bragg_theta_deg = theta_deg,
                            .two_theta_deg = 2.0 * theta_deg,
                            .relative_intensity = intensity
                        });
                    }
                }
            }
        }

        std::ranges::sort(reflections, [](const auto& lhs, const auto& rhs) noexcept {
            return lhs.two_theta_deg < rhs.two_theta_deg;
        });

        return reflections;
    }
};

void display_diffraction_table(std::string_view title,
                               const std::vector<DiffractionReflection>& reflections) {
    std::cout << "=========================================================================\n";
    std::cout << "  СИМУЛЯЦІЙНИЙ СПЕКТР: " << title << "\n";
    std::cout << "=========================================================================\n";
    std::cout << std::right
              << std::setw(10) << "(h k l)" << " | "
              << std::setw(10) << "d (нм)" << " | "
              << std::setw(12) << "theta (deg)" << " | "
              << std::setw(14) << "2*theta (deg)" << " | "
              << std::setw(14) << "Інтенсивність" << "\n";
    std::cout << "-------------------------------------------------------------------------\n";

    for (const auto& ref : reflections) {
        std::cout << "  (" << ref.h << " " << ref.k << " " << ref.l << ")   | "
                  << std::fixed << std::setprecision(4)
                  << std::setw(9) << ref.interplanar_d_nm << " | "
                  << std::setprecision(2)
                  << std::setw(11) << ref.bragg_theta_deg << " | "
                  << std::setw(13) << ref.two_theta_deg << " | "
                  << std::setprecision(1)
                  << std::setw(13) << ref.relative_intensity << "\n";
    }
    std::cout << "-------------------------------------------------------------------------\n";
    std::cout << " Кількість дозволених дифракційних максимуми: " << reflections.size() << "\n\n";
}

int main() {
    constexpr double lambda_cu_ka1 = 0.15406; // Мідне випромінювання Cu K-alpha1 (нм)

    const auto silicon_spectrum = DiffractionEngine::compute_spectrum(
        CrystalLattice::Diamond, 0.5431, lambda_cu_ka1, 4);
    display_diffraction_table("Кремній Si (Алмазна ґратка, a = 0.5431 нм)", silicon_spectrum);

    const auto copper_spectrum = DiffractionEngine::compute_spectrum(
        CrystalLattice::FaceCenteredCubic, 0.3615, lambda_cu_ka1, 3);
    display_diffraction_table("Мідь Cu (Гранецентрована FCC, a = 0.3615 нм)", copper_spectrum);

    return 0;
}

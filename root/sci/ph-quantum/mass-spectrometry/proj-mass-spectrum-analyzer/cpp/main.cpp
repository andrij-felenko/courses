#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <expected>
#include <iomanip>
#include <span>

namespace nuclear_physics {

// Фундаментальні фізичні константи
constexpr double AMU_TO_MEV = 931.494'102'42;
constexpr double MASS_PROTON = 1.007'276'466'621;
constexpr double MASS_NEUTRON = 1.008'664'915'95;
constexpr double MASS_ELECTRON = 0.000'548'579'909;

struct TofPoint {
    double freq_hz{0.0};
    double tof_us{0.0};
    double tof_err_us{1.0};
};

struct ResonanceResult {
    double nu_c_hz{0.0};
    double nu_c_err_hz{0.0};
    double t_base_us{0.0};
    double depth_us{0.0};
    double fwhm_hz{0.0};
    double chi2_red{0.0};
};

struct NuclearProperties {
    double atomic_mass_amu{0.0};
    double mass_uncert_amu{0.0};
    double binding_energy_mev{0.0};
    double binding_energy_err_mev{0.0};
    double specific_binding_energy_mev{0.0};
};

enum class AnalysisError {
    InsufficentData,
    InvalidUncertainty,
    FitFailed
};

// Клас обробки мас-спектрометричних резонансів
class MassSpectrumAnalyzer {
public:
    static std::expected<ResonanceResult, AnalysisError> AnalyzeTofSpectrum(std::span<const TofPoint> points) {
        if (points.size() < 5) {
            return std::unexpected(AnalysisError::InsufficentData);
        }

        double min_tof = points[0].tof_us;
        double max_tof = points[0].tof_us;
        double freq_at_min = points[0].freq_hz;

        for (const auto& pt : points) {
            if (pt.tof_us < min_tof) {
                min_tof = pt.tof_us;
                freq_at_min = pt.freq_hz;
            }
            if (pt.tof_us > max_tof) {
                max_tof = pt.tof_us;
            }
        }

        double best_nu_c = freq_at_min;
        double best_sigma = 25.0;
        double min_chi2 = 1e18;
        double best_depth = max_tof - min_tof;

        // Пошук оптимальної циклотронної частоти nu_c
        for (double f_offset = -60.0; f_offset <= 60.0; f_offset += 0.25) {
            double trial_freq = freq_at_min + f_offset;
            for (double trial_sigma = 10.0; trial_sigma <= 60.0; trial_sigma += 1.0) {
                double chi2 = 0.0;
                for (const auto& pt : points) {
                    double df = pt.freq_hz - trial_freq;
                    double calc_t = max_tof - best_depth * std::exp(-(df * df) / (2.0 * trial_sigma * trial_sigma));
                    double err = (pt.tof_err_us > 0.0) ? pt.tof_err_us : 1.0;
                    double diff = (pt.tof_us - calc_t) / err;
                    chi2 += diff * diff;
                }
                if (chi2 < min_chi2) {
                    min_chi2 = chi2;
                    best_nu_c = trial_freq;
                    best_sigma = trial_sigma;
                }
            }
        }

        ResonanceResult res{};
        res.nu_c_hz = best_nu_c;
        res.nu_c_err_hz = best_sigma / std::sqrt(static_cast<double>(points.size()));
        res.t_base_us = max_tof;
        res.depth_us = best_depth;
        res.fwhm_hz = 2.35482 * best_sigma;
        res.chi2_red = min_chi2 / static_cast<double>(points.size() - 4);

        return res;
    }

    static NuclearProperties CalculateMassAndEnergy(
        double nu_x, double nu_x_err,
        double nu_ref, double nu_ref_err,
        double m_ref_amu, int Z, int A)
    {
        double R = nu_ref / nu_x;
        double R_err = R * std::sqrt(std::pow(nu_ref_err / nu_ref, 2) + std::pow(nu_x_err / nu_x, 2));

        double m_atom = R * (m_ref_amu - MASS_ELECTRON) + MASS_ELECTRON;
        double m_err = R_err * (m_ref_amu - MASS_ELECTRON);
        double m_nuc = m_atom - Z * MASS_ELECTRON;

        int N = A - Z;
        double m_free = Z * MASS_PROTON + N * MASS_NEUTRON;
        double eb = (m_free - m_nuc) * AMU_TO_MEV;
        double eb_err = m_err * AMU_TO_MEV;

        return NuclearProperties{
            .atomic_mass_amu = m_atom,
            .mass_uncert_amu = m_err,
            .binding_energy_mev = eb,
            .binding_energy_err_mev = eb_err,
            .specific_binding_energy_mev = eb / static_cast<double>(A)
        };
    }
};

} // namespace nuclear_physics

int main() {
    using namespace nuclear_physics;
    std::cout << std::fixed << std::setprecision(8);
    std::cout << "=== C++20 Обробка мас-спектрометричних резонансів ===\n\n";

    const std::vector<TofPoint> spectrum = {
        {1264720.0, 148.5, 1.2},
        {1264750.0, 145.2, 1.1},
        {1264780.0, 122.1, 1.3},
        {1264800.0, 95.4,  1.0},
        {1264820.0, 71.2,  0.9},
        {1264840.0, 98.1,  1.1},
        {1264860.0, 125.6, 1.2},
        {1264890.0, 147.0, 1.0},
        {1264920.0, 149.1, 1.3}
    };

    auto fit_result = MassSpectrumAnalyzer::AnalyzeTofSpectrum(spectrum);
    if (!fit_result) {
        std::cerr << "Помилка аналізу мас-спектра!\n";
        return 1;
    }

    const auto& res = fit_result.value();
    std::cout << "Визначена циклотронна частота nu_c : " << res.nu_c_hz << " +/- " << res.nu_c_err_hz << " Гц\n";
    std::cout << "Ширина лінії FWHM                 : " << res.fwhm_hz << " Гц\n";
    std::cout << "Приведений Хі-квадрат χ²_red      : " << std::setprecision(3) << res.chi2_red << "\n\n";

    // Обчислення масових параметрів ізотопу 85Rb
    auto props = MassSpectrumAnalyzer::CalculateMassAndEnergy(
        res.nu_c_hz, res.nu_c_err_hz,
        8961420.0, 0.05,
        84.9117897, 37, 85
    );

    std::cout << std::setprecision(8);
    std::cout << "--- Результати мас-спектрометричного розрахунку 85Rb ---\n";
    std::cout << "Атомна маса M(85Rb)                : " << props.atomic_mass_amu << " +/- " << props.mass_uncert_amu << " а.о.м.\n";
    std::cout << "Повна енергія зв'язку ядра E_b    : " << std::setprecision(3) << props.binding_energy_mev << " +/- " << props.binding_energy_err_mev << " МеВ\n";
    std::cout << "Питома енергія зв'язку E_b / A    : " << std::setprecision(4) << props.specific_binding_energy_mev << " МеВ/нуклон\n";

    return 0;
}

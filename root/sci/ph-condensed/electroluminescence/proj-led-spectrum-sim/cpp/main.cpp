#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>

struct LedParameters {
    double bandgap_ev = 1.42;        // E_g для GaAs (еВ)
    double temp_k = 300.0;           // Температура переходу (К)
    double active_layer_nm = 10.0;   // Товщина активної зони (нм)
    double coeff_A = 1.0e7;          // SRH коефіцієнт (1/с)
    double coeff_B = 1.0e-10;        // Випромінювальний B (см³/с)
    double coeff_C = 1.0e-30;        // Оже C (см⁶/с)
};

struct SpectrumPoint {
    double energy_ev;
    double wavelength_nm;
    double intensity;
};

struct EfficiencyPoint {
    double current_density_a_cm2;
    double carrier_density_cm3;
    double internal_efficiency_pct;
};

class LedSimulator {
public:
    explicit LedSimulator(LedParameters params) : params_(std::move(params)) {}

    // Обчислення спектра випромінювання
    std::vector<SpectrumPoint> calculateSpectrum(double min_ev, double max_ev, int points) const {
        std::vector<SpectrumPoint> spectrum;
        spectrum.reserve(points);

        const double kb_ev = 8.617333262145e-5; // стала Больцмана в еВ/К
        const double hc_ev_nm = 1239.84193;     // h*c в еВ*нм
        const double kt = kb_ev * params_.temp_k;

        double step = (max_ev - min_ev) / (points - 1);
        double max_intensity = 0.0;

        for (int i = 0; i < points; ++i) {
            double energy = min_ev + i * step;
            double intensity = 0.0;

            if (energy >= params_.bandgap_ev) {
                double delta_e = energy - params_.bandgap_ev;
                intensity = energy * energy * std::sqrt(delta_e) * std::exp(-delta_e / kt);
            }

            double wavelength = (energy > 0.0) ? (hc_ev_nm / energy) : 0.0;
            spectrum.push_back({energy, wavelength, intensity});
            max_intensity = std::max(max_intensity, intensity);
        }

        // Нормалізація інтенсивності до 1.0
        if (max_intensity > 0.0) {
            for (auto& pt : spectrum) {
                pt.intensity /= max_intensity;
            }
        }

        return spectrum;
    }

    // Обчислення характеристики квантового виходу η_int(J)
    std::vector<EfficiencyPoint> calculateEfficiencyCurve(double min_log_n, double max_log_n, int points) const {
        std::vector<EfficiencyPoint> curve;
        curve.reserve(points);

        const double q_elem = 1.602176634e-19; // Кл
        double active_layer_cm = params_.active_layer_nm * 1.0e-7;

        double step = (max_log_n - min_log_n) / (points - 1);

        for (int i = 0; i < points; ++i) {
            double log_n = min_log_n + i * step;
            double n = std::pow(10.0, log_n); // см⁻³

            double r_srh = params_.coeff_A * n;
            double r_rad = params_.coeff_B * n * n;
            double r_auger = params_.coeff_C * n * n * n;

            double r_total = r_srh + r_rad + r_auger;

            // Густина струму J = q * d * R_total (А/см²)
            double j_a_cm2 = q_elem * active_layer_cm * r_total;
            double eta_int = (r_total > 0.0) ? (r_rad / r_total * 100.0) : 0.0;

            curve.push_back({j_a_cm2, n, eta_int});
        }

        return curve;
    }

private:
    LedParameters params_;
};

int main() {
    LedParameters params;
    params.bandgap_ev = 1.42;       // GaAs
    params.temp_k = 300.0;
    params.active_layer_nm = 10.0;  // Квантова яма 10 нм

    LedSimulator sim(params);

    // 1. Розрахунок спектра
    auto spectrum = sim.calculateSpectrum(1.35, 1.60, 50);

    std::cout << "=== Спектр випромінювання світлодіода GaAs (300 K) ===\n";
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Енергія (еВ) | Довжина хвилі (нм) | Однор. інтенсивність\n";
    std::cout << "-----------------------------------------------------\n";

    for (size_t i = 0; i < spectrum.size(); i += 5) {
        std::cout << "   " << spectrum[i].energy_ev << "      |       "
                  << spectrum[i].wavelength_nm << "       |        "
                  << spectrum[i].intensity << "\n";
    }

    // 2. Розрахунок квантового виходу
    auto eff_curve = sim.calculateEfficiencyCurve(15.0, 19.0, 20);

    std::cout << "\n=== Внутрішній квантовий вихід та Оже-згасання ===\n";
    std::cout << "J (А/см²)    | n (см⁻³)      | η_int (%)\n";
    std::cout << "----------------------------------------\n";

    for (const auto& pt : eff_curve) {
        std::cout << std::scientific << std::setprecision(2)
                  << pt.current_density_a_cm2 << "   |  "
                  << pt.carrier_density_cm3 << "  |  "
                  << std::fixed << std::setprecision(1)
                  << pt.internal_efficiency_pct << "%\n";
    }

    return 0;
}

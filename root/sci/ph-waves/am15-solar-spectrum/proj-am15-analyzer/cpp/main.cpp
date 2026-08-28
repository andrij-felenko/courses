#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <iomanip>
#include <numeric>
#include <span>

// Фізичні константи у системі SI
constexpr double H_PLANCK = 6.62607015e-34;    // Стала Планка [Дж·с]
constexpr double C_LIGHT  = 2.99792458e8;       // Швидкість світла у вакуумі [м/с]
constexpr double Q_ELEM   = 1.602176634e-19;     // Елементарний електричний заряд [Кл]

struct BandResult {
    std::string name;
    double power_w_m2;
    double percentage;
};

struct SemiconductorSpec {
    std::string name;
    double bandgap_ev;
};

inline double photon_energy_joules(double wavelength_nm) noexcept {
    const double wavelength_m = wavelength_nm * 1e-9;
    return (H_PLANCK * C_LIGHT) / wavelength_m;
}

struct SpectrumAnalysis {
    double total_power_w_m2;
    double total_photon_flux;
    std::vector<BandResult> bands;
};

SpectrumAnalysis analyze_am15_spectrum(std::span<const double> wavelengths,
                                       std::span<const double> irradiance_g) {
    double total_power = 0.0;
    double uv_power = 0.0;
    double vis_power = 0.0;
    double nir_power = 0.0;
    double ir_power = 0.0;
    double total_photon_flux = 0.0;

    const size_t n_points = wavelengths.size();
    for (size_t i = 0; i < n_points - 1; ++i) {
        const double w1 = wavelengths[i];
        const double w2 = wavelengths[i + 1];
        const double e1 = irradiance_g[i];
        const double e2 = irradiance_g[i + 1];

        const double dw = w2 - w1;
        const double e_avg = 0.5 * (e1 + e2);
        const double p_step = e_avg * dw;
        total_power += p_step;

        const double w_mid = 0.5 * (w1 + w2);
        const double e_phot = photon_energy_joules(w_mid);
        total_photon_flux += p_step / e_phot;

        if (w_mid < 400.0) {
            uv_power += p_step;
        } else if (w_mid < 700.0) {
            vis_power += p_step;
        } else if (w_mid < 1100.0) {
            nir_power += p_step;
        } else {
            ir_power += p_step;
        }
    }

    std::vector<BandResult> bands = {
        {"УФ (280–400 нм)", uv_power, (uv_power / total_power) * 100.0},
        {"Видимий (400–700 нм)", vis_power, (vis_power / total_power) * 100.0},
        {"Ближній ІЧ (700–1100 нм)", nir_power, (nir_power / total_power) * 100.0},
        {"Далекий ІЧ (>1100 нм)", ir_power, (ir_power / total_power) * 100.0}
    };

    return SpectrumAnalysis{total_power, total_photon_flux, std::move(bands)};
}

double calculate_jsc(std::span<const double> wavelengths,
                      std::span<const double> irradiance_g,
                      double bandgap_ev) {
    const double lambda_cut_nm = 1239.841984 / bandgap_ev;
    double photons_absorbed = 0.0;

    for (size_t i = 0; i < wavelengths.size() - 1; ++i) {
        const double w1 = wavelengths[i];
        const double w2 = wavelengths[i + 1];
        if (w1 >= lambda_cut_nm) {
            break;
        }

        double dw = w2 - w1;
        const double e_avg = 0.5 * (irradiance_g[i] + irradiance_g[i + 1]);
        double w_mid = 0.5 * (w1 + w2);

        if (w2 > lambda_cut_nm) {
            dw = lambda_cut_nm - w1;
            w_mid = 0.5 * (w1 + lambda_cut_nm);
        }

        const double e_phot = photon_energy_joules(w_mid);
        photons_absorbed += (e_avg * dw) / e_phot;
    }

    const double j_sc_a_m2 = Q_ELEM * photons_absorbed;
    return j_sc_a_m2 / 10.0; // Конвертація з А/м² у мА/см²
}

int main() {
    std::vector<double> wavelengths;
    std::vector<double> irradiance;

    double w = 280.0;
    while (w <= 4000.0) {
        wavelengths.push_back(w);
        double val = 0.0;
        if (w >= 290.0) {
            val = 1.57 * std::exp(-std::pow((w - 500.0) / 380.0, 2.0));
            if (w >= 755.0 && w <= 770.0) val *= 0.35;
            if (w >= 920.0 && w <= 970.0) val *= 0.25;
            if (w >= 1110.0 && w <= 1160.0) val *= 0.30;
            if (w >= 1340.0 && w <= 1450.0) val *= 0.08;
            if (w >= 1800.0 && w <= 1950.0) val *= 0.05;
        }
        irradiance.push_back(val);
        const double step = (w < 1000.0) ? 1.0 : ((w < 2000.0) ? 5.0 : 20.0);
        w += step;
    }

    const auto initial_analysis = analyze_am15_spectrum(wavelengths, irradiance);
    const double scale = 1000.0 / initial_analysis.total_power_w_m2;
    for (auto& val : irradiance) {
        val *= scale;
    }

    const auto analysis = analyze_am15_spectrum(wavelengths, irradiance);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Загальна потужність AM1.5G: " << analysis.total_power_w_m2 << " Вт/м²\n";
    std::cout << "Загальний фотонний потік: " << std::scientific << std::setprecision(3) 
              << analysis.total_photon_flux << " фотонів/(м²·с)\n\n";

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "Розподіл потужності за діапазонами:\n";
    for (const auto& b : analysis.bands) {
        std::cout << "  • " << b.name << ": " << b.power_w_m2 << " Вт/м² (" << b.percentage << "%)\n";
    }

    const std::vector<SemiconductorSpec> semiconductors = {
        {"Кремній (Si)", 1.12},
        {"Арсенід галію (GaAs)", 1.42},
        {"Телурид кадмію (CdTe)", 1.50}
    };

    std::cout << "\nГраничний фотострум короткого замикання J_sc (при EQE = 100%):\n";
    for (const auto& semi : semiconductors) {
        const double jsc = calculate_jsc(wavelengths, irradiance, semi.bandgap_ev);
        std::cout << "  • " << semi.name << " (Eg = " << semi.bandgap_ev << " еВ): J_sc = " << jsc << " мА/см²\n";
    }

    return 0;
}

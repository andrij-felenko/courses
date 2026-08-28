#include <iostream>
#include <cmath>
#include <numbers>
#include <optional>
#include <string>

namespace rf {

struct PllConfig {
    double out_freq_hz{2.4e9};       // Вихідна частота
    double pfd_freq_hz{25.0e6};      // Опорна частота PFD
    double charge_pump_amp{0.0025};  // Струм CP
    double vco_gain_hz_v{30.0e6};    // Крутизна VCO
    double target_bw_hz{100.0e3};    // Смуга петлі
    double target_pm_deg{50.0};      // Запас по фазі
    double pfd_fom_db{-230.0};       // FOM шуму детектора
    double vco_noise_1mhz{-120.0};   // Шум VCO на 1 МГц
};

struct PllSimulationResult {
    double n_divider;
    double c1_farad;
    double r1_ohm;
    double c2_farad;
    double natural_freq_rad_s;
    double damping_factor;
    double phase_margin_deg;
    double lock_time_us;
    double inband_phase_noise_dbc;
    double total_phase_noise_100k_dbc;
};

class SynthesizerPlanner {
public:
    static std::optional<PllSimulationResult> compute(const PllConfig& cfg) noexcept {
        if (cfg.pfd_freq_hz <= 0.0 || cfg.out_freq_hz <= 0.0 || cfg.target_bw_hz <= 0.0) {
            return std::nullopt;
        }

        PllSimulationResult res{};
        res.n_divider = cfg.out_freq_hz / cfg.pfd_freq_hz;

        const double wc = 2.0 * std::numbers::pi * cfg.target_bw_hz;
        const double k_vco_rad = 2.0 * std::numbers::pi * cfg.vco_gain_hz_v;
        const double pm_rad = cfg.target_pm_deg * (std::numbers::pi / 180.0);

        // Обчислення C1 та R1
        res.c1_farad = (cfg.charge_pump_amp * k_vco_rad * std::cos(pm_rad)) /
                        (2.0 * std::numbers::pi * res.n_divider * wc * wc);

        res.damping_factor = 0.707;
        res.r1_ohm = (2.0 * res.damping_factor) / (wc * res.c1_farad);
        res.c2_farad = res.c1_farad / 10.0;

        res.natural_freq_rad_s = std::sqrt((cfg.charge_pump_amp * k_vco_rad) /
                                           (2.0 * std::numbers::pi * res.n_divider * res.c1_farad));

        // Запас по фазі
        const double c_eq = (res.c1_farad * res.c2_farad) / (res.c1_farad + res.c2_farad);
        const double phi_1 = std::atan(wc * res.r1_ohm * res.c1_farad);
        const double phi_2 = std::atan(wc * res.r1_ohm * c_eq);
        res.phase_margin_deg = (phi_1 - phi_2) * (180.0 / std::numbers::pi);

        // Час встановлення
        constexpr double step_freq_hz = 50.0e6;
        constexpr double tol_freq_hz = 1000.0;
        res.lock_time_us = (-std::log(tol_freq_hz / step_freq_hz) /
                           (res.damping_factor * res.natural_freq_rad_s)) * 1.0e6;

        // Шуми
        res.inband_phase_noise_dbc = cfg.pfd_fom_db +
                                     10.0 * std::log10(cfg.pfd_freq_hz) +
                                     20.0 * std::log10(res.n_divider);

        const double vco_100k = cfg.vco_noise_1mhz + 20.0 * std::log10(1.0e6 / 100.0e3);
        const double p_inband = std::pow(10.0, res.inband_phase_noise_dbc / 10.0);
        const double p_vco = std::pow(10.0, vco_100k / 10.0);
        res.total_phase_noise_100k_dbc = 10.0 * std::log10(p_inband + p_vco);

        return res;
    }
};

} // namespace rf

int main() {
    rf::PllConfig config{
        .out_freq_hz = 2.4e9,
        .pfd_freq_hz = 25.0e6,
        .charge_pump_amp = 0.0025,
        .vco_gain_hz_v = 30.0e6,
        .target_bw_hz = 100.0e3,
        .target_pm_deg = 50.0,
        .pfd_fom_db = -230.0,
        .vco_noise_1mhz = -120.0
    };

    if (auto res = rf::SynthesizerPlanner::compute(config)) {
        std::cout << "=== Результати розрахунку ФАПЧ 2.4 ГГц (C++) ===\n";
        std::cout << "Коефіцієнт N: " << res->n_divider << "\n";
        std::cout << "Петльовий фільтр: C1 = " << res->c1_farad * 1e9 << " нФ, "
                  << "R1 = " << res->r1_ohm << " Ом, "
                  << "C2 = " << res->c2_farad * 1e12 << " пФ\n";
        std::cout << "Частота петлі (omega_n): " << res->natural_freq_rad_s / 1000.0 << " крад/с\n";
        std::cout << "Запас по фазі (PM): " << res->phase_margin_deg << " deg\n";
        std::cout << "Час захоплення (t_lock): " << res->lock_time_us << " мкс\n";
        std::cout << "Внутрішньосмуговий шум: " << res->inband_phase_noise_dbc << " дБн/Гц\n";
        std::cout << "Шум на відбудові 100 кГц: " << res->total_phase_noise_100k_dbc << " дБн/Гц\n";
    }
    return 0;
}

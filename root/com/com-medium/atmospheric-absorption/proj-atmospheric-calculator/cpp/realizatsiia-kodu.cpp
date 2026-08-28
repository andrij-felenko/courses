#include <iostream>
#include <cmath>
#include <vector>
#include <string_view>
#include <numbers>
#include <iomanip>

namespace rf_propagation {

/* Спосіб поляризації електромагнітної хвилі */
enum class Polarization {
    Horizontal,
    Vertical,
    Circular
};

/* Налаштування радіолінії */
struct LinkConfig {
    double frequency_ghz{28.0};
    double distance_km{5.0};
    double elevation_deg{0.0};
    double rain_rate_mm_h{50.0};
    double humidity_g_m3{7.5};
    Polarization polarization{Polarization::Horizontal};
};

/* Результати детального аналізу згасання */
struct AttenuationReport {
    double gamma_o2_db_km{0.0};
    double gamma_h2o_db_km{0.0};
    double gamma_gas_db_km{0.0};
    double gamma_rain_db_km{0.0};
    double path_gas_atten_db{0.0};
    double path_rain_atten_db{0.0};
    double total_attenuation_db{0.0};
};

class AtmosphericCalculator {
public:
    constexpr AtmosphericCalculator() noexcept = default;

    /* Обчислення питомого поглинання газами за модельними виразами ITU-R P.676 */
    [[nodiscard]] std::pair<double, double> compute_gas_specific_attenuation(
        double f_ghz, double humidity) const noexcept 
    {
        const double f2 = f_ghz * f_ghz;
        
        // Поглинання киснем O2
        const double term_o1 = 7.27 / (f2 + 0.351);
        const double term_o2 = 7.5 / ((f_ghz - 57.0) * (f_ghz - 57.0) + 2.44);
        const double gamma_o2 = (term_o1 + term_o2) * f2 * 1e-3;

        // Поглинання водяною парою H2O
        const double term_w1 = 0.05 + 0.002 * humidity;
        const double term_w2 = 3.6 / ((f_ghz - 22.235) * (f_ghz - 22.235) + 8.5);
        const double term_w3 = 10.6 / ((f_ghz - 183.31) * (f_ghz - 183.31) + 9.0);
        const double gamma_h2o = (term_w1 + term_w2 + term_w3) * f2 * humidity * 1e-4;

        return {gamma_o2, gamma_h2o};
    }

    /* Обчислення коефіцієнтів дощового згасання k та alpha за ITU-R P.838 */
    [[nodiscard]] std::pair<double, double> compute_rain_coefficients(
        double f_ghz, Polarization pol, double elevation_deg) const noexcept 
    {
        double k_h{0.0}, k_v{0.0}, a_h{0.0}, a_v{0.0};

        if (f_ghz <= 10.0) {
            k_h = 0.01217; k_v = 0.01129; a_h = 1.2571; a_v = 1.2156;
        } else if (f_ghz <= 20.0) {
            k_h = 0.0751;  k_v = 0.0691;  a_h = 1.0993; a_v = 1.0654;
        } else if (f_ghz <= 30.0) {
            k_h = 0.2403;  k_v = 0.2291;  a_h = 0.9485; a_v = 0.9129;
        } else if (f_ghz <= 60.0) {
            k_h = 0.8606;  k_v = 0.8474;  a_h = 0.7656; a_v = 0.7589;
        } else {
            k_h = 1.3200;  k_v = 1.3100;  a_h = 0.6900; a_v = 0.6850;
        }

        const double theta_rad = elevation_deg * std::numbers::pi / 180.0;
        const double cos2_theta = std::cos(theta_rad) * std::cos(theta_rad);

        double tau_deg = 0.0;
        if (pol == Polarization::Vertical) tau_deg = 90.0;
        else if (pol == Polarization::Circular) tau_deg = 45.0;

        const double tau_rad = tau_deg * std::numbers::pi / 180.0;
        const double cos_2tau = std::cos(2.0 * tau_rad);

        const double k = (k_h + k_v + (k_h - k_v) * cos2_theta * cos_2tau) / 2.0;
        const double alpha = (k_h * a_h + k_v * a_v + (k_h * a_h - k_v * a_v) * cos2_theta * cos_2tau) / (2.0 * k);

        return {k, alpha};
    }

    /* Повний розрахунок згасання для заданої конфігурації траси */
    [[nodiscard]] AttenuationReport evaluate(const LinkConfig& cfg) const {
        AttenuationReport report;

        const auto [g_o2, g_h2o] = compute_gas_specific_attenuation(cfg.frequency_ghz, cfg.humidity_g_m3);
        report.gamma_o2_db_km = g_o2;
        report.gamma_h2o_db_km = g_h2o;
        report.gamma_gas_db_km = g_o2 + g_h2o;

        const auto [k, alpha] = compute_rain_coefficients(cfg.frequency_ghz, cfg.polarization, cfg.elevation_deg);
        report.gamma_rain_db_km = k * std::pow(cfg.rain_rate_mm_h, alpha);

        // Корегування довжини траси через обмеженість розміру дощового осередку
        const double r_factor = (cfg.distance_km > 1.0) ? (1.0 / (1.0 + 0.045 * cfg.distance_km)) : 1.0;
        const double eff_rain_dist = cfg.distance_km * r_factor;

        report.path_gas_atten_db = report.gamma_gas_db_km * cfg.distance_km;
        report.path_rain_atten_db = report.gamma_rain_db_km * eff_rain_dist;
        report.total_attenuation_db = report.path_gas_atten_db + report.path_rain_atten_db;

        return report;
    }
};

} // namespace rf_propagation

int main() {
    using namespace rf_propagation;

    AtmosphericCalculator calc;
    LinkConfig config{
        .frequency_ghz = 28.0,
        .distance_km = 5.0,
        .elevation_deg = 0.0,
        .rain_rate_mm_h = 50.0,
        .humidity_g_m3 = 7.5,
        .polarization = Polarization::Horizontal
    };

    const auto report = calc.evaluate(config);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Обчислення згасання (Мова C++20 / Modern API) ===\n";
    std::cout << "Частота: " << config.frequency_ghz << " ГГц | Відстань: " << config.distance_km << " км\n";
    std::cout << "Питоме згасання O2:    " << report.gamma_o2_db_km << " дБ/км\n";
    std::cout << "Питоме згасання H2O:   " << report.gamma_h2o_db_km << " дБ/км\n";
    std::cout << "Сумарне газове:        " << report.gamma_gas_db_km << " дБ/км (Траса: " << report.path_gas_atten_db << " дБ)\n";
    std::cout << "Питоме дощове згасання: " << report.gamma_rain_db_km << " дБ/км (Траса: " << report.path_rain_atten_db << " дБ)\n";
    std::cout << "Загальні втрати траси:  " << report.total_attenuation_db << " дБ\n";

    return 0;
}

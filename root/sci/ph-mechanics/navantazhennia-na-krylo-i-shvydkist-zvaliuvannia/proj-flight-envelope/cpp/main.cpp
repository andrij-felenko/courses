#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <numbers>
#include <optional>
#include <stdexcept>

namespace aero {

constexpr double g_accel = 9.80665;
constexpr double isa_t0 = 288.15;
constexpr double isa_p0 = 101325.0;
constexpr double isa_lapse_rate = 0.0065;
constexpr double isa_r_air = 287.058;

struct AtmosphereState {
    double altitude_m{0.0};
    double temperature_k{isa_t0};
    double pressure_pa{isa_p0};
    double density_kg_m3{1.225};
};

struct AircraftSpecs {
    double mass_kg;          // злітна маса, кг
    double wing_area_m2;     // площа крила, м²
    double mac_m;            // середня аеродинамічна хорда, м
    double cl_max_pos;       // C_L,max
    double cl_max_neg;       // C_L,min (за модулем)
    double dcl_dalpha_rad;   // dC_L/dα (рад⁻¹)
    double n_max_pos;        // +n_max
    double n_max_neg;        // -n_max
    double v_ne_ms;          // V_NE, м/с
};

struct FlightEnvelopeSummary {
    double wing_loading_n_m2;
    double wing_loading_kg_m2;
    double v_stall_0_ms;
    double v_stall_alt_ms;
    double v_maneuver_va_ms;
    double v_maneuver_va_neg_ms;
};

struct BankTurnResult {
    double bank_deg;
    double load_factor_g;
    double stall_speed_ms;
    double turn_radius_m;
    double turn_rate_deg_s;
};

struct GustResult {
    double gust_speed_ms;
    double flight_speed_ms;
    double mass_ratio_mu_g;
    double gust_alleviation_kg;
    double delta_n_g;
    double total_n_g;
};

class FlightDynamicsCalculator {
public:
    explicit FlightDynamicsCalculator(AircraftSpecs specs)
        : specs_(std::move(specs)) {
        if (specs_.mass_kg <= 0.0 || specs_.wing_area_m2 <= 0.0 || specs_.cl_max_pos <= 0.0) {
            throw std::invalid_argument("Некоректні геометричні або масові параметри ЛА");
        }
    }

    [[nodiscard]] static AtmosphereState get_isa_atmosphere(double altitude_m) noexcept {
        AtmosphereState atmo;
        atmo.altitude_m = std::clamp(altitude_m, 0.0, 11000.0);
        atmo.temperature_k = isa_t0 - isa_lapse_rate * atmo.altitude_m;
        const double exponent = g_accel / (isa_r_air * isa_lapse_rate);
        atmo.pressure_pa = isa_p0 * std::pow(atmo.temperature_k / isa_t0, exponent);
        atmo.density_kg_m3 = atmo.pressure_pa / (isa_r_air * atmo.temperature_k);
        return atmo;
    }

    [[nodiscard]] FlightEnvelopeSummary compute_envelope(double altitude_m) const noexcept {
        const double weight_n = specs_.mass_kg * g_accel;
        const double ws_n = weight_n / specs_.wing_area_m2;
        const double ws_kg = specs_.mass_kg / specs_.wing_area_m2;

        const auto atmo_sea = get_isa_atmosphere(0.0);
        const auto atmo_alt = get_isa_atmosphere(altitude_m);

        const double vs0 = std::sqrt(2.0 * ws_n / (atmo_sea.density_kg_m3 * specs_.cl_max_pos));
        const double vs_alt = std::sqrt(2.0 * ws_n / (atmo_alt.density_kg_m3 * specs_.cl_max_pos));
        const double va = vs0 * std::sqrt(specs_.n_max_pos);

        const double vs_neg = std::sqrt(2.0 * ws_n / (atmo_sea.density_kg_m3 * specs_.cl_max_neg));
        const double va_neg = vs_neg * std::sqrt(std::abs(specs_.n_max_neg));

        return {
            .wing_loading_n_m2 = ws_n,
            .wing_loading_kg_m2 = ws_kg,
            .v_stall_0_ms = vs0,
            .v_stall_alt_ms = vs_alt,
            .v_maneuver_va_ms = va,
            .v_maneuver_va_neg_ms = va_neg
        };
    }

    [[nodiscard]] std::optional<BankTurnResult> compute_bank_turn(
        double altitude_m, double bank_deg, double true_airspeed_ms) const noexcept {
        if (bank_deg < 0.0 || bank_deg >= 85.0 || true_airspeed_ms <= 0.0) {
            return std::nullopt;
        }

        const auto atmo = get_isa_atmosphere(altitude_m);
        const double ws_n = (specs_.mass_kg * g_accel) / specs_.wing_area_m2;
        const double bank_rad = bank_deg * std::numbers::pi / 180.0;
        const double cos_phi = std::cos(bank_rad);
        const double nz = 1.0 / cos_phi;

        const double v_stall_turn = std::sqrt(2.0 * ws_n * nz / (atmo.density_kg_m3 * specs_.cl_max_pos));

        double radius = 1e9;
        double omega_deg_s = 0.0;
        if (bank_deg >= 0.1) {
            const double tan_phi = std::tan(bank_rad);
            radius = (true_airspeed_ms * true_airspeed_ms) / (g_accel * tan_phi);
            omega_deg_s = (g_accel * tan_phi / true_airspeed_ms) * (180.0 / std::numbers::pi);
        }

        return BankTurnResult{
            .bank_deg = bank_deg,
            .load_factor_g = nz,
            .stall_speed_ms = v_stall_turn,
            .turn_radius_m = radius,
            .turn_rate_deg_s = omega_deg_s
        };
    }

    [[nodiscard]] GustResult compute_gust(double altitude_m, double airspeed_ms, double gust_ms) const noexcept {
        const auto atmo = get_isa_atmosphere(altitude_m);
        const double ws_kg = specs_.mass_kg / specs_.wing_area_m2;
        const double ws_n = ws_kg * g_accel;

        const double mu_g = (2.0 * ws_kg) / (atmo.density_kg_m3 * specs_.mac_m * specs_.dcl_dalpha_rad);
        const double k_g = (0.88 * mu_g) / (5.3 + mu_g);
        const double delta_n = (k_g * atmo.density_kg_m3 * airspeed_ms * specs_.dcl_dalpha_rad * gust_ms) / (2.0 * ws_n);

        return {
            .gust_speed_ms = gust_ms,
            .flight_speed_ms = airspeed_ms,
            .mass_ratio_mu_g = mu_g,
            .gust_alleviation_kg = k_g,
            .delta_n_g = delta_n,
            .total_n_g = 1.0 + delta_n
        };
    }

private:
    AircraftSpecs specs_;
};

} // namespace aero

int main() {
    using namespace aero;

    const AircraftSpecs uav{
        .mass_kg = 18.5,
        .wing_area_m2 = 0.85,
        .mac_m = 0.35,
        .cl_max_pos = 1.45,
        .cl_max_neg = 0.85,
        .dcl_dalpha_rad = 5.2,
        .n_max_pos = 4.5,
        .n_max_neg = -2.0,
        .v_ne_ms = 48.0
    };

    const FlightDynamicsCalculator calc(uav);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== РОЗРАХУНОК ПОЛЬОТНОГО КОНВЕРТА БПЛА (C++20) ===\n";
    const auto env = calc.compute_envelope(1500.0);
    std::cout << "Питоме навантаження W/S: " << env.wing_loading_n_m2 << " Н/м² ("
              << env.wing_loading_kg_m2 << " кг/м²)\n";
    std::cout << "Швидкість звалювання 1g (H=0 м):   " << env.v_stall_0_ms << " м/с ("
              << env.v_stall_0_ms * 3.6 << " км/год)\n";
    std::cout << "Швидкість звалювання 1g (H=1500 м): " << env.v_stall_alt_ms << " м/с ("
              << env.v_stall_alt_ms * 3.6 << " км/год)\n";
    std::cout << "Швидкість маневрування V_A:         " << env.v_maneuver_va_ms << " м/с ("
              << env.v_maneuver_va_ms * 3.6 << " км/год)\n\n";

    std::cout << "=== ЗМІНА ШВИДКОСТІ ЗВАЛЮВАННЯ ТА ПЕРЕВАНТАЖЕННЯ У ВІРАЖІ (v = 28 м/с) ===\n";
    std::cout << "  Крен φ  |  Перевантаження n_z  |  v_зв (м/с)  |  Радіус R (м)  |  Омега (град/с)\n";
    std::cout << "----------+----------------------+--------------+----------------+----------------\n";

    const std::vector<double> bank_angles{0.0, 15.0, 30.0, 45.0, 60.0, 70.0, 75.0};
    for (const double bank : bank_angles) {
        if (const auto pt = calc.compute_bank_turn(500.0, bank, 28.0); pt.has_value()) {
            std::cout << "   " << std::setw(2) << static_cast<int>(pt->bank_deg) << "°    |       "
                      << std::setw(4) << pt->load_factor_g << " g        |    "
                      << std::setw(5) << pt->stall_speed_ms << "     |     "
                      << std::setw(6) << pt->turn_radius_m << "     |     "
                      << std::setw(5) << pt->turn_rate_deg_s << "\n";
        }
    }

    std::cout << "\n=== ОЦІНКА ВЕРТИКАЛЬНОГО ПОРИВУ ВІТРУ (H=500 м, v=30 м/с, w=7 м/с) ===\n";
    const auto gust = calc.compute_gust(500.0, 30.0, 7.0);
    std::cout << "Коефіцієнт маси μ_g:         " << gust.mass_ratio_mu_g << "\n";
    std::cout << "Коефіцієнт послаблення K_g:  " << std::setprecision(3) << gust.gust_alleviation_kg << "\n";
    std::cout << "Приріст перевантаження Δn:   +" << std::setprecision(2) << gust.delta_n_g << " g\n";
    std::cout << "Сумарне перевантаження n:    " << gust.total_n_g << " g (допустиме n_max = "
              << uav.n_max_pos << " g)\n";

    return 0;
}

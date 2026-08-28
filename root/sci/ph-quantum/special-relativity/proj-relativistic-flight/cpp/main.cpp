#include <iostream>
#include <cmath>
#include <expected>
#include <format>
#include <numbers>

namespace relativity {

/* Фізичні константи C++23 */
constexpr double c_speed = 299792458.0;
constexpr double sec_per_year = 365.25 * 86400.0;
constexpr double g_accel = 9.80665;

/* Результати симуляції кінематики */
struct FlightState {
    double proper_time_years;
    double earth_time_years;
    double distance_light_years;
    double velocity_c;
    double gamma;
};

/* Чотири-імпульс релятивістської частинки */
struct FourMomentum {
    double energy_gev{0.0};
    double px_gev{0.0};
    double py_gev{0.0};
    double pz_gev{0.0};

    [[nodiscard]] constexpr double invariant_mass() const noexcept {
        const double p2 = px_gev * px_gev + py_gev * py_gev + pz_gev * pz_gev;
        const double m2 = energy_gev * energy_gev - p2;
        return m2 >= 0.0 ? std::sqrt(m2) : 0.0;
    }
};

/* Перелік помилок перетворення */
enum class BoostError {
    SuperluminalSpeed,
    InvalidMomentum
};

class RelativisticSimulator {
public:
    /* Розрахунок міжзоряного перельоту зі сталим прискоренням */
    [[nodiscard]] static FlightState simulate_flight(
        double proper_years, double accel_m_s2 = g_accel) noexcept 
    {
        const double tau_sec = proper_years * sec_per_year;
        const double alpha = (accel_m_s2 * tau_sec) / c_speed;

        const double sinh_a = std::sinh(alpha);
        const double cosh_a = std::cosh(alpha);
        const double tanh_a = std::tanh(alpha);

        const double t_sec = (c_speed / accel_m_s2) * sinh_a;
        
        /* Використання sinh^2 для запобігання втраті точності при малих значеннях alpha */
        const double sinh_half = std::sinh(alpha / 2.0);
        const double x_meters = ((2.0 * c_speed * c_speed) / accel_m_s2) * (sinh_half * sinh_half);

        return FlightState{
            .proper_time_years = proper_years,
            .earth_time_years = t_sec / sec_per_year,
            .distance_light_years = x_meters / (c_speed * sec_per_year),
            .velocity_c = tanh_a,
            .gamma = cosh_a
        };
    }

    /* Лоренцівський буст 4-імпульсу з обробкою помилок через std::expected */
    [[nodiscard]] static std::expected<FourMomentum, BoostError> boost(
        const FourMomentum& p, double v_c) noexcept 
    {
        if (std::abs(v_c) >= 1.0) {
            return std::unexpected(BoostError::SuperluminalSpeed);
        }

        const double gamma = 1.0 / std::sqrt(1.0 - v_c * v_c);
        return FourMomentum{
            .energy_gev = gamma * (p.energy_gev - v_c * p.px_gev),
            .px_gev     = gamma * (p.px_gev - v_c * p.energy_gev),
            .py_gev     = p.py_gev,
            .pz_gev     = p.pz_gev
        };
    }
};

} // namespace relativity

int main() {
    using namespace relativity;

    constexpr double tau_years = 5.0;
    const auto flight = RelativisticSimulator::simulate_flight(tau_years);

    std::cout << std::format("=========================================================\n");
    std::cout << std::format("  СИМУЛЯЦІЯ РЕЛЯТИВІСТСЬКОГО РУХУ ТА БУСТУ (C++23)\n");
    std::cout << std::format("=========================================================\n\n");

    std::cout << std::format("--- РЕЗУЛЬТАТИ ПЕРЕЛЬОТУ (Прискорення a = 1g) ---\n");
    std::cout << std::format(" Власний час (tau) : {:.2f} років\n", flight.proper_time_years);
    std::cout << std::format(" Час на Землі (t)   : {:.2f} років\n", flight.earth_time_years);
    std::cout << std::format(" Відстань (x)       : {:.2f} св. років\n", flight.distance_light_years);
    std::cout << std::format(" Швидкість (v/c)     : {:.8f}\n", flight.velocity_c);
    std::cout << std::format(" Фактор Лоренца (γ)  : {:.2f}\n\n", flight.gamma);

    constexpr FourMomentum proton{ .energy_gev = 0.938272 };
    const auto boosted = RelativisticSimulator::boost(proton, flight.velocity_c);

    if (boosted) {
        std::cout << std::format("--- БУСТ ЧОТИРИ-ІМПУЛЬСУ ПРОТОНА ---\n");
        std::cout << std::format(" Початкова маса : {:.6f} ГеВ/c²\n", proton.invariant_mass());
        std::cout << std::format(" Енергія у S'   : {:.4f} ГеВ\n", boosted->energy_gev);
        std::cout << std::format(" Імпульс px'    : {:.4f} ГеВ/c\n", boosted->px_gev);
        std::cout << std::format(" Кінцева маса   : {:.6f} ГеВ/c² (інваріант збережено)\n", 
                                 boosted->invariant_mass());
    } else {
        std::cerr << "Помилка при виконанні бусту Лоренца!\n";
    }

    return 0;
}

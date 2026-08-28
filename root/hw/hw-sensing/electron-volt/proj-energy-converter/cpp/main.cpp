#include <iostream>
#include <cmath>
#include <expected>
#include <iomanip>
#include <string_view>

namespace physics {

// Фізичні константи в системі SI та еВ
constexpr double c_speed = 299792458.0;
constexpr double e_charge = 1.602176634e-19;
constexpr double kb_joule = 1.380649e-23;
constexpr double hc_ev_nm = 1239.84198;

constexpr double mass_electron_ev = 510998.95;
constexpr double mass_proton_ev   = 938272088.16;
constexpr double mass_alpha_ev    = 3727379400.0;

struct ParticleKinematics {
    double total_kin_ev{0.0};
    double gamma{1.0};
    double beta{0.0};
    double velocity_m_s{0.0};
    double momentum_ev_c{0.0};
    double de_broglie_nm{0.0};
    double temp_kelvin{0.0};
};

enum class KinematicError {
    NegativeEnergy,
    InvalidRestMass,
    InvalidCharge
};

[[nodiscard]] constexpr std::string_view error_to_string(KinematicError err) noexcept {
    switch (err) {
        case KinematicError::NegativeEnergy: return "Кінетична енергія не може бути від'ємною.";
        case KinematicError::InvalidRestMass: return "Маса спокою має бути строго додатною.";
        case KinematicError::InvalidCharge: return "Заряд має бути додатним цілим числом.";
    }
    return "Невідома помилка.";
}

class KinematicsCalculator {
public:
    [[nodiscard]] static std::expected<ParticleKinematics, KinematicError>
    compute(double energy_ev, double rest_mass_ev, int charge_z = 1) noexcept {
        if (energy_ev < 0.0) {
            return std::unexpected(KinematicError::NegativeEnergy);
        }
        if (rest_mass_ev <= 0.0) {
            return std::unexpected(KinematicError::InvalidRestMass);
        }
        if (charge_z <= 0) {
            return std::unexpected(KinematicError::InvalidCharge);
        }

        ParticleKinematics res;
        res.total_kin_ev = energy_ev * static_cast<double>(charge_z);
        const double eps = res.total_kin_ev / rest_mass_ev;
        res.gamma = 1.0 + eps;

        // Чисельно стабільне обчислення безрозмірної швидкості
        if (eps < 1e-5) {
            res.beta = std::sqrt(2.0 * eps) * (1.0 - 0.375 * eps + 0.3125 * eps * eps);
        } else {
            res.beta = std::sqrt(1.0 - 1.0 / (res.gamma * res.gamma));
        }

        res.velocity_m_s = res.beta * c_speed;
        res.momentum_ev_c = std::sqrt(res.total_kin_ev * (res.total_kin_ev + 2.0 * rest_mass_ev));
        res.de_broglie_nm = (res.momentum_ev_c > 0.0) ? (hc_ev_nm / res.momentum_ev_c) : 0.0;

        const double energy_joules = res.total_kin_ev * e_charge;
        res.temp_kelvin = energy_joules / kb_joule;

        return res;
    }
};

} // namespace physics

int main() {
    std::cout << "=== Обчислювальний модуль (C++23 implementation) ===\n";

    auto res = physics::KinematicsCalculator::compute(7000000000000.0, physics::mass_proton_ev); // 7 ТеВ протон в LHC
    if (res) {
        std::cout << std::fixed << std::setprecision(6);
        std::cout << "7 ТеВ протон (LHC):\n";
        std::cout << "  Фактор Лоренца γ: " << res->gamma << "\n";
        std::cout << "  Швидкість v/c: " << res->beta << "\n";
        std::cout << "  Швидкість v: " << res->velocity_m_s << " м/с\n";
        std::cout << "  Імпульс p*c: " << res->momentum_ev_c / 1.0e9 << " ГеВ\n";
    } else {
        std::cerr << "Помилка розрахунку: " << physics::error_to_string(res.error()) << "\n";
    }

    return 0;
}

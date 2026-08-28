#include <iostream>
#include <array>
#include <cmath>
#include <optional>
#include <numbers>
#include <iomanip>

namespace isa {

// Фізичні константи ISA
constexpr double g0         = 9.80665;
constexpr double r_spec     = 287.05287;
constexpr double r_earth    = 6356766.0;
constexpr double gamma_air  = 1.40;
constexpr double beta_s     = 1.458e-6;
constexpr double sutherland = 110.4;

constexpr double t0         = 288.15;
constexpr double p0         = 101325.0;
constexpr double rho0       = 1.2250;
constexpr double max_h      = 84852.0;

struct State {
    double h_geopotential{0.0};
    double z_geometric{0.0};
    double temperature{0.0};
    double temp_celsius{0.0};
    double pressure{0.0};
    double density{0.0};
    double sound_speed{0.0};
    double dynamic_visc{0.0};
    double kinematic_visc{0.0};
};

struct Layer {
    double h_base;
    double t_base;
    double lapse;
    double p_base;
};

// Фіксована таблиця 7 шарів атмосфери ISA
constexpr std::array<Layer, 7> layers = {{
    {     0.0, 288.15, -0.00650, 101325.0  },
    { 11000.0, 216.65,  0.00000,  22632.1  },
    { 20000.0, 216.65,  0.00100,   5474.89 },
    { 32000.0, 228.65,  0.00280,    868.019},
    { 47000.0, 270.65,  0.00000,    110.906},
    { 51000.0, 270.65, -0.00280,     66.9389},
    { 71000.0, 214.65, -0.00200,      3.95642}
}};

// Перетворення висот
[[nodiscard]] constexpr double z_to_h(double z_m) noexcept {
    return (r_earth * z_m) / (r_earth + z_m);
}

[[nodiscard]] constexpr double h_to_z(double h_m) noexcept {
    if (h_m >= r_earth) return r_earth * 100.0;
    return (r_earth * h_m) / (r_earth - h_m);
}

// Розрахунок стану атмосфери за геопотенціальною висотою
[[nodiscard]] std::optional<State> evaluate_h(double h_m) noexcept {
    if (h_m < 0.0 || h_m > max_h) {
        return std::nullopt;
    }

    std::size_t idx = 0;
    for (std::size_t i = 0; i < layers.size() - 1; ++i) {
        if (h_m >= layers[i + 1].h_base) {
            idx = i + 1;
        } else {
            break;
        }
    }

    const auto& layer = layers[idx];
    const double dh = h_m - layer.h_base;
    const double t = layer.t_base + layer.lapse * dh;
    double p = 0.0;

    if (std::abs(layer.lapse) < 1e-10) {
        p = layer.p_base * std::exp(- (g0 * dh) / (r_spec * layer.t_base));
    } else {
        const double n_p = - g0 / (r_spec * layer.lapse);
        p = layer.p_base * std::pow(t / layer.t_base, n_p);
    }

    const double rho = p / (r_spec * t);
    const double a = std::sqrt(gamma_air * r_spec * t);
    const double mu = (beta_s * std::pow(t, 1.5)) / (t + sutherland);
    const double nu = mu / rho;

    return State{
        .h_geopotential = h_m,
        .z_geometric    = h_to_z(h_m),
        .temperature    = t,
        .temp_celsius   = t - 273.15,
        .pressure       = p,
        .density        = rho,
        .sound_speed    = a,
        .dynamic_visc   = mu,
        .kinematic_visc = nu
    };
}

// Барометрична висота у тропосфері
[[nodiscard]] constexpr double pressure_altitude(double pressure_pa) noexcept {
    if (pressure_pa <= 0.0) return 0.0;
    constexpr double n_p_inv = 1.0 / 5.25588;
    return (t0 / 0.0065) * (1.0 - std::pow(pressure_pa / p0, n_p_inv));
}

// Перетворення CAS у TAS
[[nodiscard]] double cas_to_tas(double cas_ms, double density_kg_m3) noexcept {
    if (density_kg_m3 <= 0.0) return cas_ms;
    return cas_ms * std::sqrt(rho0 / density_kg_m3);
}

} // namespace isa

int main() {
    constexpr double test_h = 10000.0; // 10 км
    const auto result = isa::evaluate_h(test_h);

    if (result.has_value()) {
        const auto& s = result.value();
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "--- ISA C++20 стан на h = " << s.h_geopotential << " м ---\n";
        std::cout << "Геометрична висота Z: " << s.z_geometric << " м\n";
        std::cout << "Температура: " << s.temperature << " K (" << s.temp_celsius << " °C)\n";
        std::cout << "Тиск: " << s.pressure << " Па (" << (s.pressure / 100.0) << " гПа)\n";
        std::cout << "Густина: " << s.density << " кг/м³\n";
        std::cout << "Швидкість звуку: " << s.sound_speed << " м/с\n";

        constexpr double cas = 150.0;
        const double tas = isa::cas_to_tas(cas, s.density);
        std::cout << "CAS = " << cas << " м/с -> TAS = " << tas << " м/с\n";
    }
    return 0;
}

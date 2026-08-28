// isa.hpp — Modern C++20 API для Міжнародної стандартної атмосфери ISA
#ifndef ISA_LIBRARY_HPP
#define ISA_LIBRARY_HPP

#include <array>
#include <cmath>
#include <optional>
#include <string_view>
#include <concepts>

namespace isa {

// ── Фундаментальні фізичні константи (constexpr) ─────────────────────────
constexpr double g0            = 9.80665;
constexpr double r_spec        = 287.05287;
constexpr double r_earth       = 6356766.0;
constexpr double gamma_air     = 1.40;
constexpr double sutherland_s  = 110.4;
constexpr double sutherland_b  = 1.458e-6;

constexpr double p0            = 101325.0;
constexpr double t0            = 288.15;
constexpr double rho0          = 1.2250;
constexpr double max_h_meters  = 84852.0;

// ── Повний термодинамічний стан атмосфери ────────────────────────────────
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

    [[nodiscard]] constexpr double pressure_hpa() const noexcept {
        return pressure / 100.0;
    }
};

// ── C++20 Клас обчислювача атмосфери ISA ─────────────────────────────────
class AtmosphereCalculator {
public:
    AtmosphereCalculator() = delete; // Статичний модуль без стану

    [[nodiscard]] static constexpr double z_to_h(double z_m) noexcept {
        return (r_earth * z_m) / (r_earth + z_m);
    }

    [[nodiscard]] static constexpr double h_to_z(double h_m) noexcept {
        if (h_m >= r_earth) return r_earth * 100.0;
        return (r_earth * h_m) / (r_earth - h_m);
    }

    // Розрахунок стану за висотою (повертає std::optional замість винятків)
    [[nodiscard]] static std::optional<State> evaluate(double h_geopotential_m) noexcept;

    // Обернені навігаційні обчислювачі
    [[nodiscard]] static std::optional<double> pressure_altitude(double pressure_pa) noexcept;
    [[nodiscard]] static std::optional<double> density_altitude(double pressure_pa, double temp_k) noexcept;

    // Аеродинамічні перетворення швидкостей
    [[nodiscard]] static constexpr double cas_to_tas(double cas_ms, double density_kg_m3) noexcept {
        if (density_kg_m3 <= 0.0) return cas_ms;
        return cas_ms * std::sqrt(rho0 / density_kg_m3);
    }

    [[nodiscard]] static constexpr double tas_to_mach(double tas_ms, double sound_speed_ms) noexcept {
        if (sound_speed_ms <= 0.0) return 0.0;
        return tas_ms / sound_speed_ms;
    }
};

} // namespace isa

#endif // ISA_LIBRARY_HPP

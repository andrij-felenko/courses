// ============================================================================
// Симулятор траєкторій частинок у токамаку (C++20, RAII, std::span, constexpr)
// ============================================================================
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <string_view>
#include <iomanip>

namespace tokamak {

constexpr double kChargeE = 1.602176634e-19;
constexpr double kAmu     = 1.6605390666e-27;

struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};

    constexpr Vec3 operator+(const Vec3& o) const noexcept { return {x + o.x, y + o.y, z + o.z}; }
    constexpr Vec3 operator-(const Vec3& o) const noexcept { return {x - o.x, y - o.y, z - o.z}; }
    constexpr Vec3 operator*(double s)      const noexcept { return {x * s, y * s, z * s}; }

    [[nodiscard]] constexpr double dot(const Vec3& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }

    [[nodiscard]] constexpr Vec3 cross(const Vec3& o) const noexcept {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }

    [[nodiscard]] double norm() const noexcept { return std::sqrt(dot(*this)); }
};

struct TokamakGeometry {
    double R0{1.65};      // Великий радіус (м)
    double a0{0.50};      // Малий радіус (м)
    double B_tor0{2.50};  // Тороїдальне поле (Тл)
    double B_pol0{0.25};  // Полоїдальне поле (Тл)
};

struct Particle {
    double mass{2.0 * kAmu};
    double charge{kChargeE};
    Vec3 pos{};
    Vec3 vel{};
};

class OrbitSimulator {
public:
    explicit OrbitSimulator(TokamakGeometry geom) : geom_(geom) {}

    [[nodiscard]] Vec3 getField(const Vec3& pos) const noexcept {
        const double R = std::sqrt(pos.x * pos.x + pos.y * pos.y);
        if (R < 1e-6) return {};

        const double cos_phi = pos.x / R;
        const double sin_phi = pos.y / R;
        const double z = pos.z;
        const double r_local = std::sqrt((R - geom_.R0) * (R - geom_.R0) + z * z);

        const double B_phi = geom_.B_tor0 * (geom_.R0 / R);
        const double B_x_tor = -B_phi * sin_phi;
        const double B_y_tor =  B_phi * cos_phi;

        const double B_pol_mag = geom_.B_pol0 * (r_local / geom_.a0) * (geom_.R0 / R);
        const double B_R_pol = (r_local > 1e-6) ? -B_pol_mag * (z / r_local) : 0.0;
        const double B_z_pol = (r_local > 1e-6) ?  B_pol_mag * ((R - geom_.R0) / r_local) : 0.0;

        return {
            B_x_tor + B_R_pol * cos_phi,
            B_y_tor + B_R_pol * sin_phi,
            B_z_pol
        };
    }

    void stepBoris(Particle& p, double dt) const noexcept {
        const Vec3 B = getField(p.pos);
        const double q_m = p.charge / p.mass;

        const Vec3 t = B * (q_m * 0.5 * dt);
        const double t_sq = t.dot(t);
        const Vec3 s = t * (2.0 / (1.0 + t_sq));

        const Vec3 v_prime = p.vel + p.vel.cross(t);
        const Vec3 v_plus  = p.vel + v_prime.cross(s);

        p.vel = v_plus;
        p.pos = p.pos + p.vel * dt;
    }

    struct SimulationResult {
        double R_min;
        double R_max;
        double banana_width;
        std::string_view orbit_type;
    };

    [[nodiscard]] SimulationResult run(Particle p, double dt, size_t steps) const {
        double R_min = 1e9, R_max = -1e9;

        for (size_t i = 0; i < steps; ++i) {
            stepBoris(p, dt);
            const double R = std::sqrt(p.pos.x * p.pos.x + p.pos.y * p.pos.y);
            R_min = std::min(R_min, R);
            R_max = std::max(R_max, R);
        }

        const double width = R_max - R_min;
        std::string_view type = (width > 0.05) ? "Заперта (бананна)" : "Пролітна";

        return {R_min, R_max, width, type};
    }

private:
    TokamakGeometry geom_;
};

} // namespace tokamak

int main() {
    using namespace tokamak;

    TokamakGeometry geom{.R0 = 1.65, .a0 = 0.50, .B_tor0 = 2.50, .B_pol0 = 0.25};
    OrbitSimulator sim(geom);

    const double energy_eV = 3000.0;
    Particle deuteron{
        .mass = 2.0 * kAmu,
        .charge = kChargeE,
        .pos = {geom.R0 + 0.20, 0.0, 0.0}
    };

    const double v_tot = std::sqrt(2.0 * energy_eV * kChargeE / deuteron.mass);
    constexpr double pitch_deg = 70.0;
    constexpr double pitch_rad = pitch_deg * std::numbers::pi / 180.0;

    deuteron.vel = {0.0, v_tot * std::cos(pitch_rad), v_tot * std::sin(pitch_rad)};

    constexpr double dt = 1.0e-9;
    constexpr size_t steps = 100000;

    std::cout << "=== Симулятор руху іона в токамаку (C++20) ===\n";
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Початковий радіус R = " << deuteron.pos.x << " м, E = " << (energy_eV / 1000.0) << " кеВ\n";

    const auto res = sim.run(deuteron, dt, steps);

    std::cout << std::setprecision(4);
    std::cout << "Результат симуляції (" << steps << " кроків):\n";
    std::cout << "  R_min = " << res.R_min << " м, R_max = " << res.R_max << " м\n";
    std::cout << "  Ширина бананної орбіти Δr_b = " << (res.banana_width * 100.0) << " см\n";
    std::cout << "  Тип орбіти: " << res.orbit_type << "\n";

    return 0;
}

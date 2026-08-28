#include <iostream>
#include <array>
#include <cmath>
#include <numbers>

namespace physics {

constexpr double MU_0 = 1.25663706212e-6; // [Гн/м]

struct Vector3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr double dot(const Vector3& other) const noexcept {
        return x * other.x + y * other.y + z * other.z;
    }

    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(dot(*this));
    }

    [[nodiscard]] constexpr Vector3 operator+(const Vector3& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }

    [[nodiscard]] constexpr Vector3 operator-(const Vector3& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }

    [[nodiscard]] constexpr Vector3 operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }
};

class DipoleFieldModel {
public:
    [[nodiscard]] static Vector3 calculate_field(const Vector3& dipole_mu, const Vector3& pos_r) noexcept {
        const double r_len = pos_r.norm();
        if (r_len < 1e-12) {
            return {};
        }

        const Vector3 r_hat = pos_r * (1.0 / r_len);
        const double mu_dot_rhat = dipole_mu.dot(r_hat);
        const double factor = MU_0 / (4.0 * std::numbers::pi * std::pow(r_len, 3));

        return (r_hat * (3.0 * mu_dot_rhat) - dipole_mu) * factor;
    }
};

struct ParticleState {
    double z_pos{0.0};
    double z_vel{0.0};
};

class SternGerlachSimulator {
public:
    explicit SternGerlachSimulator(double mass_kg, double gradient_t_m) noexcept
        : mass_(mass_kg), gradient_(gradient_t_m) {}

    [[nodiscard]] ParticleState step(ParticleState current, double mu_z, double dt_sec) const noexcept {
        const double force_z = mu_z * gradient_;
        const double accel_z = force_z / mass_;

        ParticleState next;
        next.z_vel = current.z_vel + accel_z * dt_sec;
        next.z_pos = current.z_pos + next.z_vel * dt_sec;
        return next;
    }

private:
    double mass_;
    double gradient_;
};

} // namespace physics

int main() {
    using namespace physics;

    // 1. Поле диполя
    const Vector3 mu{0.0, 0.0, 9.274e-24}; // 1 магнетон Бора [А·м²]
    const Vector3 r{0.05, 0.0, 0.05};       // [м]

    const Vector3 B = DipoleFieldModel::calculate_field(mu, r);
    std::cout << "Поле диполя на r=(0.05, 0, 0.05) м:
"
              << "  Bx = " << B.x << " Тл
"
              << "  By = " << B.y << " Тл
"
              << "  Bz = " << B.z << " Тл

";

    // 2. Симуляція Штерна — Герлаха
    constexpr double mass_Ag = 1.79e-25;  // [кг]
    constexpr double mu_Ag_z = 9.274e-24; // [А·м²]
    constexpr double dBz_dz  = 1000.0;    // [Тл/м]
    constexpr double dt      = 1e-6;      // [с]

    const SternGerlachSimulator sim(mass_Ag, dBz_dz);
    ParticleState state_up{};
    ParticleState state_down{};

    for (int step = 0; step < 100; ++step) {
        state_up   = sim.step(state_up,   +mu_Ag_z, dt);
        state_down = sim.step(state_down, -mu_Ag_z, dt);
    }

    std::cout << "Відхилення атома срібла через 100 мкс:
"
              << "  Спін вгору (+mu_z):  z = " << state_up.z_pos * 1000.0 << " мм, vz = " << state_up.z_vel << " м/с
"
              << "  Спін вниз  (-mu_z):  z = " << state_down.z_pos * 1000.0 << " мм, vz = " << state_down.z_vel << " м/с
";

    return 0;
}

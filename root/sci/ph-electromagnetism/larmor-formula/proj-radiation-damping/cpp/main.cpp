#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <array>
#include <numbers>

namespace electrodynamics {

/* Фізичні константи в системі SI */
inline constexpr double C_LIGHT = 2.99792458e8;     // швидкість світла, м/с
inline constexpr double EPS0    = 8.8541878128e-12; // електрична стала, Ф/м
inline constexpr double Q_ELEM  = -1.602176634e-19; // заряд електрона, Кл
inline constexpr double M_ELEM  = 9.1093837015e-31; // маса електрона, кг
inline constexpr double EV_JOULE = 1.602176634e-19; // 1 еВ у Джоулях

struct Vector3D {
    double x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] constexpr Vector3D operator+(const Vector3D& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vector3D operator*(double s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] double norm_sq() const noexcept {
        return x * x + y * y + z * z;
    }
    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(norm_sq());
    }
};

struct ParticleState {
    Vector3D pos{};
    Vector3D vel{};
};

class SynchrotronSimulator {
public:
    explicit SynchrotronSimulator(double b_field, double initial_vel) noexcept
        : b_field_(b_field) {
        state_.vel = {initial_vel, 0.0, 0.0};
        initial_kin_energy_ = 0.5 * M_ELEM * initial_vel * initial_vel;
    }

    struct StepLog {
        double time_ps;
        double radius_um;
        double speed_ratio;
        double power_nw;
        double energy_rad_ev;
    };

    StepLog step(double dt) noexcept {
        const auto deriv = compute_derivatives(state_);
        const double p_inst = compute_larmor_power(deriv.vel);
        total_radiated_energy_ += p_inst * dt;

        state_ = rk4_step(state_, dt);
        current_time_ += dt;

        const double v_mag = state_.vel.norm();
        const double r_cyc = (M_ELEM * v_mag) / (std::abs(Q_ELEM) * b_field_) * 1.0e6;

        return {
            current_time_ * 1.0e12,
            r_cyc,
            v_mag / C_LIGHT,
            p_inst * 1.0e9,
            total_radiated_energy_ / EV_JOULE
        };
    }

    [[nodiscard]] double initial_kinetic_energy() const noexcept { return initial_kin_energy_; }
    [[nodiscard]] double current_kinetic_energy() const noexcept {
        return 0.5 * M_ELEM * state_.vel.norm_sq();
    }
    [[nodiscard]] double total_radiated_energy() const noexcept { return total_radiated_energy_; }

private:
    double b_field_;
    ParticleState state_{};
    double current_time_{0.0};
    double initial_kin_energy_{0.0};
    double total_radiated_energy_{0.0};

    [[nodiscard]] ParticleState compute_derivatives(const ParticleState& s) const noexcept {
        // Сила Лоренца F_lor = q * (v x B) для B = (0, 0, B0)
        const Vector3D f_lor{
            Q_ELEM * s.vel.y * b_field_,
            -Q_ELEM * s.vel.x * b_field_,
            0.0
        };

        // Демпфування Ландау-Ліфшиця: F_rad = -gamma_damp * v_perp
        const double gamma_damp = (std::pow(Q_ELEM, 4) * b_field_ * b_field_) /
                                  (6.0 * std::numbers::pi * EPS0 * M_ELEM * M_ELEM * std::pow(C_LIGHT, 3));

        const Vector3D f_rad{
            -gamma_damp * s.vel.x,
            -gamma_damp * s.vel.y,
            0.0
        };

        return {
            s.vel,
            (f_lor + f_rad) * (1.0 / M_ELEM)
        };
    }

    [[nodiscard]] static double compute_larmor_power(const Vector3D& accel) noexcept {
        return (Q_ELEM * Q_ELEM * accel.norm_sq()) /
               (6.0 * std::numbers::pi * EPS0 * std::pow(C_LIGHT, 3));
    }

    [[nodiscard]] ParticleState rk4_step(const ParticleState& s, double dt) const noexcept {
        const auto k1 = compute_derivatives(s);

        const ParticleState s2{
            s.pos + k1.pos * (0.5 * dt),
            s.vel + k1.vel * (0.5 * dt)
        };
        const auto k2 = compute_derivatives(s2);

        const ParticleState s3{
            s.pos + k2.pos * (0.5 * dt),
            s.vel + k2.vel * (0.5 * dt)
        };
        const auto k3 = compute_derivatives(s3);

        const ParticleState s4{
            s.pos + k3.pos * dt,
            s.vel + k3.vel * dt
        };
        const auto k4 = compute_derivatives(s4);

        return {
            s.pos + (k1.pos + k2.pos * 2.0 + k3.pos * 2.0 + k4.pos) * (dt / 6.0),
            s.vel + (k1.vel + k2.vel * 2.0 + k3.vel * 2.0 + k4.vel) * (dt / 6.0)
        };
    }
};

} // namespace electrodynamics

int main() {
    using namespace electrodynamics;

    constexpr double B_FIELD = 5.0;            // 5 Тесла
    constexpr double V_INIT  = 0.2 * C_LIGHT;  // 0.2 c
    constexpr double DT      = 1.0e-13;        // 0.1 пс
    constexpr int N_STEPS    = 10000;

    SynchrotronSimulator sim(B_FIELD, V_INIT);

    std::cout << std::left
              << std::setw(6)  << "Крок"
              << std::setw(12) << "Час (пс)"
              << std::setw(16) << "R_орбіти (мкм)"
              << std::setw(10) << "V/c"
              << std::setw(18) << "Потужність (нВт)"
              << "E_рад (еВ)\n";
    std::cout << std::string(72, '-') << "\n";

    for (int step = 0; step <= N_STEPS; ++step) {
        const auto log = sim.step(DT);

        if (step % 2000 == 0) {
            std::cout << std::left
                      << std::setw(6)  << step
                      << std::fixed << std::setprecision(2)
                      << std::setw(12) << log.time_ps
                      << std::setprecision(4)
                      << std::setw(16) << log.radius_um
                      << std::setprecision(3)
                      << std::setw(10) << log.speed_ratio
                      << std::scientific << std::setprecision(4)
                      << std::setw(18) << log.power_nw
                      << std::fixed << std::setprecision(4)
                      << log.energy_rad_ev << "\n";
        }
    }

    const double delta_ekin = sim.initial_kinetic_energy() - sim.current_kinetic_energy();

    std::cout << "\nБаланс збереження енергії:\n"
              << "  Втрата кінетичної енергії: " << delta_ekin << " Дж ("
              << (delta_ekin / EV_JOULE) << " еВ)\n"
              << "  Інтеграл випромінювання:   " << sim.total_radiated_energy() << " Дж ("
              << (sim.total_radiated_energy() / EV_JOULE) << " еВ)\n";

    return 0;
}

#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <string_view>
#include <expected>
#include <system_error>

constexpr double C_SPEED = 2.99792458e8;
constexpr double ELECTRON_MASS_KG = 9.1093837015e-31;
constexpr double ELECTRON_CHARGE_C = 1.602176634e-19;
constexpr double MEV_TO_JOULE = 1.602176634e-13;
constexpr double MEV_REST_MASS = 0.51099895;

struct Point2D {
    double x{0.0};
    double y{0.0};
};

struct ParticleState {
    Point2D pos{};
    double vx{0.0};
    double vy{0.0};
    double charge_sign{-1.0};
};

class TrackSimulator {
public:
    explicit TrackSimulator(double magnetic_field) : b_field_{magnetic_field} {}

    [[nodiscard]] std::vector<Point2D> run(ParticleState state, double dt, std::size_t steps) const {
        std::vector<Point2D> path;
        path.reserve(steps);

        for (std::size_t i = 0; i < steps; ++i) {
            path.push_back(state.pos);

            const double v_sq = state.vx * state.vx + state.vy * state.vy;
            double beta_sq = v_sq / (C_SPEED * C_SPEED);
            if (beta_sq >= 1.0) beta_sq = 0.999999;
            const double gamma = 1.0 / std::sqrt(1.0 - beta_sq);

            const double fx = state.charge_sign * ELECTRON_CHARGE_C * state.vy * b_field_;
            const double fy = -state.charge_sign * ELECTRON_CHARGE_C * state.vx * b_field_;

            const double ax = fx / (gamma * ELECTRON_MASS_KG);
            const double ay = fy / (gamma * ELECTRON_MASS_KG);

            state.vx += ax * dt;
            state.vy += ay * dt;

            state.pos.x += state.vx * dt;
            state.pos.y += state.vy * dt;
        }
        return path;
    }

private:
    double b_field_;
};

struct KinematicsResult {
    double kinetic_energy_mev;
    double gamma;
    double radius_m;
};

std::expected<KinematicsResult, std::string_view> calculate_pair_kinematics(double photon_energy_mev, double b_field) {
    if (photon_energy_mev < 2.0 * MEV_REST_MASS) {
        return std::unexpected("Енергія фотона замала для народження пари");
    }

    const double e_kin_total = photon_energy_mev - 2.0 * MEV_REST_MASS;
    const double e_kin_each = e_kin_total / 2.0;

    const double e_total_j = (e_kin_each + MEV_REST_MASS) * MEV_TO_JOULE;
    const double gamma = e_total_j / (ELECTRON_MASS_KG * C_SPEED * C_SPEED);
    const double beta = std::sqrt(1.0 - 1.0 / (gamma * gamma));
    const double v0 = beta * C_SPEED;

    const double p_joule_s = gamma * ELECTRON_MASS_KG * v0;
    const double radius = p_joule_s / (ELECTRON_CHARGE_C * b_field);

    return KinematicsResult{e_kin_each, gamma, radius};
}

int main() {
    constexpr double photon_energy = 5.0;
    constexpr double b_field = 0.5;

    auto result = calculate_pair_kinematics(photon_energy, b_field);
    if (!result) {
        std::cerr << "Помилка: " << result.error() << '\n';
        return 1;
    }

    std::cout << "Кінетична енергія частинки: " << result->kinetic_energy_mev << " МеВ\n";
    std::cout << "Лоренц-фактор γ: " << result->gamma << '\n';
    std::cout << "Радіус кривизни R: " << result->radius_m << " м\n";

    TrackSimulator sim{b_field};
    const double v0 = std::sqrt(1.0 - 1.0 / (result->gamma * result->gamma)) * C_SPEED;

    ParticleState electron{{0.0, 0.0}, 0.0, v0, -1.0};
    ParticleState positron{{0.0, 0.0}, 0.0, v0, +1.0};

    auto e_track = sim.run(electron, 1e-11, 1000);
    auto p_track = sim.run(positron, 1e-11, 1000);

    std::cout << "Успішно обчислено " << e_track.size() << " точок траєкторії.\n";
    return 0;
}

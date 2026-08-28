#include <iostream>
#include <vector>
#include <cmath>
#include <tuple>
#include <iomanip>

struct PlasmaParameters {
    double major_radius{1.65};  // R_0 (м)
    double minor_radius{0.50};  // a (м)
    double B_toroidal{2.50};    // B_0 (Тл)
    double B_poloidal{0.30};    // B_pol_0 на краю (Тл)
    double particle_mass{3.34e-27}; // Іон дейтерію (кг)
    double particle_charge{1.602e-19};
};

struct GuidingCenterState {
    double R;
    double Z;
    double v_parallel;
    double v_perp;
};

class GuidingCenterSimulator {
public:
    explicit GuidingCenterSimulator(PlasmaParameters params)
        : params_(std::move(params)) {}

    [[nodiscard]] std::pair<double, double> compute_velocity(double R, double Z, double v_par, double v_per) const {
        const double r = std::hypot(R - params_.major_radius, Z);
        const double r_safe = (r < 1e-6) ? 1e-6 : r;

        const double B_phi = params_.B_toroidal * params_.major_radius / R;
        const double B_pol = params_.B_poloidal * (r_safe / params_.minor_radius);
        const double B_total = std::hypot(B_phi, B_pol);

        const double mu = (params_.particle_mass * v_per * v_per) / (2.0 * B_total);
        const double v_drift_Z = (params_.particle_mass * v_par * v_par + mu * B_total) /
                                 (params_.particle_charge * params_.B_toroidal * params_.major_radius);

        const double v_rot_R = -v_par * (B_pol / B_total) * (Z / r_safe);
        const double v_rot_Z =  v_par * (B_pol / B_total) * ((R - params_.major_radius) / r_safe);

        return {v_rot_R, v_rot_Z + v_drift_Z};
    }

    void step_rk4(GuidingCenterState& state, double dt) const {
        auto [dR1, dZ1] = compute_velocity(state.R, state.Z, state.v_parallel, state.v_perp);
        auto [dR2, dZ2] = compute_velocity(state.R + 0.5*dt*dR1, state.Z + 0.5*dt*dZ1, state.v_parallel, state.v_perp);
        auto [dR3, dZ3] = compute_velocity(state.R + 0.5*dt*dR2, state.Z + 0.5*dt*dZ2, state.v_parallel, state.v_perp);
        auto [dR4, dZ4] = compute_velocity(state.R + dt*dR3, state.Z + dt*dZ3, state.v_parallel, state.v_perp);

        state.R += (dt / 6.0) * (dR1 + 2.0*dR2 + 2.0*dR3 + dR4);
        state.Z += (dt / 6.0) * (dZ1 + 2.0*dZ2 + 2.0*dZ3 + dZ4);
    }

private:
    PlasmaParameters params_;
};

int main() {
    PlasmaParameters params;
    GuidingCenterSimulator sim(params);
    GuidingCenterState state{.R = 1.85, .Z = 0.0, .v_parallel = 5.0e5, .v_perp = 7.0e5};

    constexpr double dt = 1.0e-8;
    constexpr int steps = 10000;

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Крок\tR (м)\t\tZ (м)\n";
    for (int i = 0; i <= steps; ++i) {
        if (i % 1000 == 0) {
            std::cout << i << "\t" << state.R << "\t" << state.Z << "\n";
        }
        sim.step_rk4(state, dt);
    }
    return 0;
}

// Simulation of Schmid factor and dislocation strain hardening in modern C++20
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <numeric>
#include <algorithm>
#include <iomanip>

namespace plasticity {

struct Vector3D {
    double x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] constexpr double dot(const Vector3D& other) const noexcept {
        return x * other.x + y * other.y + z * other.z;
    }

    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(dot(*this));
    }

    [[nodiscard]] Vector3D normalized() const {
        double n = norm();
        if (n < 1e-9) throw std::invalid_argument("Cannot normalize zero vector");
        return {x / n, y / n, z / n};
    }
};

struct SlipSystem {
    Vector3D plane_normal;
    Vector3D slip_direction;
};

struct Material {
    double shear_modulus_GPa{48.0};
    double burgers_vector_nm{0.256};
    double tau_0_MPa{1.5};
    double taylor_alpha{0.3};
    double k1_accumulation{4.5e8};
    double k2_annihilation{12.0};
    double initial_dislocation_density{1.0e11};
};

class CrystalPlasticitySimulator {
public:
    static constexpr std::array<SlipSystem, 12> fcc_slip_systems{{
        /* (111) plane */
        {{ 1.0,  1.0,  1.0}, { 0.0,  1.0, -1.0}},
        {{ 1.0,  1.0,  1.0}, { 1.0,  0.0, -1.0}},
        {{ 1.0,  1.0,  1.0}, { 1.0, -1.0,  0.0}},
        /* (-111) plane */
        {{-1.0,  1.0,  1.0}, { 0.0,  1.0, -1.0}},
        {{-1.0,  1.0,  1.0}, { 1.0,  0.0,  1.0}},
        {{-1.0,  1.0,  1.0}, { 1.0,  1.0,  0.0}},
        /* (1-11) plane */
        {{ 1.0, -1.0,  1.0}, { 0.0,  1.0,  1.0}},
        {{ 1.0, -1.0,  1.0}, { 1.0,  0.0, -1.0}},
        {{ 1.0, -1.0,  1.0}, { 1.0,  1.0,  0.0}},
        /* (11-1) plane */
        {{ 1.0,  1.0, -1.0}, { 0.0,  1.0,  1.0}},
        {{ 1.0,  1.0, -1.0}, { 1.0,  0.0,  1.0}},
        {{ 1.0,  1.0, -1.0}, { 1.0, -1.0,  0.0}}
    }};

    struct SchmidResult {
        double max_schmid_factor;
        std::size_t active_system_index;
    };

    [[nodiscard]] static SchmidResult compute_schmid_factor(const Vector3D& tensile_axis) {
        const Vector3D n_dir = tensile_axis.normalized();
        double max_m = 0.0;
        std::size_t best_idx = 0;

        for (std::size_t i = 0; i < fcc_slip_systems.size(); ++i) {
            const auto& sys = fcc_slip_systems[i];
            double cos_phi = std::abs(n_dir.dot(sys.plane_normal)) / sys.plane_normal.norm();
            double cos_lambda = std::abs(n_dir.dot(sys.slip_direction)) / sys.slip_direction.norm();
            double m = cos_phi * cos_lambda;

            if (m > max_m) {
                max_m = m;
                best_idx = i;
            }
        }
        return {max_m, best_idx};
    }

    struct SimulationPoint {
        double plastic_strain;
        double dislocation_density;
        double yield_stress_MPa;
    };

    [[nodiscard]] static std::vector<SimulationPoint> run_simulation(
        const Material& mat, 
        const Vector3D& tensile_axis, 
        double max_strain, 
        std::size_t steps) 
    {
        const auto [m_max, active_idx] = compute_schmid_factor(tensile_axis);
        std::vector<SimulationPoint> results;
        results.reserve(steps + 1);

        double rho = mat.initial_dislocation_density;
        const double d_eps = max_strain / static_cast<double>(steps);
        const double G_Pa = mat.shear_modulus_GPa * 1e9;
        const double b_m = mat.burgers_vector_nm * 1e-9;

        for (std::size_t i = 0; i <= steps; ++i) {
            double eps_p = static_cast<double>(i) * d_eps;
            double tau_Pa = (mat.tau_0_MPa * 1e6) + mat.taylor_alpha * G_Pa * b_m * std::sqrt(rho);
            double sigma_MPa = (tau_Pa / 1e6) / m_max;

            results.push_back({eps_p, rho, sigma_MPa});

            // Kocks-Mecking evolution equation
            double drho_deps = mat.k1_accumulation * std::sqrt(rho) - mat.k2_annihilation * rho;
            rho += drho_deps * d_eps;
        }

        return results;
    }
};

} // namespace plasticity

int main() {
    using namespace plasticity;

    Material copper;
    Vector3D tension_axis{1.0, 2.0, 3.0};

    auto [m_max, sys_idx] = CrystalPlasticitySimulator::compute_schmid_factor(tension_axis);
    std::cout << "C++20 Sim: Tension axis [1, 2, 3]\n";
    std::cout << "Max Schmid factor m_max = " << std::fixed << std::setprecision(4) 
              << m_max << " (System #" << sys_idx + 1 << ")\n";

    auto curve = CrystalPlasticitySimulator::run_simulation(copper, tension_axis, 0.20, 100);

    std::cout << "--------------------------------------------------\n";
    std::cout << "Деформація ε_p | Щільність ρ (м^-2) | Напруження σ (МПа)\n";
    std::cout << "--------------------------------------------------\n";

    for (std::size_t i = 0; i < curve.size(); i += curve.size() / 5) {
        const auto& pt = curve[i];
        std::cout << std::setw(14) << std::setprecision(3) << pt.plastic_strain << " | "
                  << std::scientific << std::setw(17) << std::setprecision(3) << pt.dislocation_density << " | "
                  << std::fixed << std::setw(19) << std::setprecision(2) << pt.yield_stress_MPa << "\n";
    }

    return 0;
}

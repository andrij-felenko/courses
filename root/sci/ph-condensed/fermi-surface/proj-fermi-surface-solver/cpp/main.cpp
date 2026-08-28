#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <numeric>
#include <span >

struct LatticeParams {
    double t_hopping_ev{1.0};  // Інтеграл перескоку в еВ
    double a_lattice_m{3.0e-10}; // Період ґратки в метрах
};

struct Point2D {
    double x{0.0};
    double y{0.0};
};

class FermiSurfaceSolver {
public:
    static constexpr double hbar = 1.054571817e-34;
    static constexpr double ev_to_joule = 1.602176634e-19;
    static constexpr double m_e = 9.1093837015e-31;

    explicit FermiSurfaceSolver(LatticeParams params) : params_(params) {}

    [[nodiscard]] double dispersion(double kx, double ky) const noexcept {
        const double t_joule = params_.t_hopping_ev * ev_to_joule;
        return -2.0 * t_joule * (std::cos(kx * params_.a_lattice_m) + 
                                 std::cos(ky * params_.a_lattice_m));
    }

    [[nodiscard]] double compute_orbit_area(double ef_joule, size_t grid_size) const {
        const double k_max = std::numbers::pi / params_.a_lattice_m;
        const double step = (2.0 * k_max) / static_cast<double>(grid_size - 1);

        std::vector<Point2D> contour;
        contour.reserve(grid_size * 4);

        for (size_t i = 0; i < grid_size - 1; ++i) {
            const double kx = -k_max + static_cast<double>(i) * step;
            for (size_t j = 0; j < grid_size - 1; ++j) {
                const double ky = -k_max + static_cast<double>(j) * step;

                const double e00 = dispersion(kx, ky);
                const double e10 = dispersion(kx + step, ky);
                const double e01 = dispersion(kx, ky + step);

                if ((e00 - ef_joule) * (e10 - ef_joule) <= 0.0 && std::abs(e10 - e00) > 1e-30) {
                    const double frac = (ef_joule - e00) / (e10 - e00);
                    contour.push_back({kx + frac * step, ky});
                }
                if ((e00 - ef_joule) * (e01 - ef_joule) <= 0.0 && std::abs(e01 - e00) > 1e-30) {
                    const double frac = (ef_joule - e00) / (e01 - e00);
                    contour.push_back({kx, ky + frac * step});
                }
            }
        }
        return polygon_area(contour);
    }

    [[nodiscard]] double compute_cyclotron_mass(double ef_ev, size_t grid_size) const {
        const double ef_joule = ef_ev * ev_to_joule;
        const double delta_e = 0.005 * ev_to_joule; // 5 меВ

        const double area_plus = compute_orbit_area(ef_joule + delta_e, grid_size);
        const double area_minus = compute_orbit_area(ef_joule - delta_e, grid_size);

        const double dA_dE = (area_plus - area_minus) / (2.0 * delta_e);
        return (hbar * hbar / (2.0 * std::numbers::pi)) * dA_dE;
    }

private:
    LatticeParams params_;

    [[nodiscard]] static double polygon_area(std::span<const Point2D> pts) noexcept {
        if (pts.size() < 3) return 0.0;
        double area = 0.0;
        for (size_t i = 0; i < pts.size(); ++i) {
            const size_t next = (i + 1) % pts.size();
            area += pts[i].x * pts[next].y - pts[next].x * pts[i].y;
        }
        return 0.5 * std::abs(area);
    }
};

int main() {
    LatticeParams params{.t_hopping_ev = 1.0, .a_lattice_m = 3.0e-10};
    FermiSurfaceSolver solver(params);

    constexpr size_t grid_size = 500;
    constexpr double ef_ev = -1.5;

    const double mass = solver.compute_cyclotron_mass(ef_ev, grid_size);

    std::cout << "Енергія Фермі E_F: " << ef_ev << " еВ\n";
    std::cout << "Циклотронна маса m_c*: " << mass << " кг ("
              << (mass / FermiSurfaceSolver::m_e) << " m_e)\n";

    return 0;
}

// dielectric_solver.cpp — Об'єктно-орієнтований C++20 розв'язувач полів D, E, P
#include <iostream>
#include <vector>
#include <memory>
#include <cmath>
#include <iomanip>
#include <span>
#include <stdexcept>

class DielectricPoissonSolver2D {
public:
    static constexpr double EPS0 = 8.854187817e-12;

    struct FieldPoint {
        double phi;
        double Ex, Ey;
        double Dx, Dy;
        double Px, Py;
    };

    DielectricPoissonSolver2D(size_t nx, size_t ny, double domain_size)
        : nx_(nx), ny_(ny), h_(domain_size / static_cast<double>(nx - 1)),
          phi_(nx * ny, 0.0), eps_r_(nx * ny, 1.0),
          rho_free_(nx * ny, 0.0), is_boundary_(nx * ny, false),
          Ex_(nx * ny, 0.0), Ey_(nx * ny, 0.0),
          Dx_(nx * ny, 0.0), Dy_(nx * ny, 0.0),
          Px_(nx * ny, 0.0), Py_(nx * ny, 0.0) {}

    void setup_microstrip_geometry(double substrate_eps_r, double strip_voltage) {
        for (size_t i = 0; i < nx_; ++i) {
            for (size_t j = 0; j < ny_ / 2; ++j) {
                eps_r_[index(i, j)] = substrate_eps_r;
            }
        }

        // Заземлені грані
        for (size_t i = 0; i < nx_; ++i) {
            set_boundary(i, 0, 0.0);
            set_boundary(i, ny_ - 1, 0.0);
        }

        // Смужковий провідник на межі розділу
        size_t j_strip = ny_ / 2;
        for (size_t i = nx_ / 4; i <= 3 * nx_ / 4; ++i) {
            set_boundary(i, j_strip, strip_voltage);
        }
    }

    double iterate_sor(double omega) {
        double max_diff = 0.0;
        double h2 = h_ * h_;

        for (size_t i = 1; i < nx_ - 1; ++i) {
            for (size_t j = 1; j < ny_ - 1; ++j) {
                size_t id = index(i, j);
                if (is_boundary_[id]) continue;

                double eps_e = 0.5 * (eps_r_[id] + eps_r_[index(i + 1, j)]);
                double eps_w = 0.5 * (eps_r_[id] + eps_r_[index(i - 1, j)]);
                double eps_n = 0.5 * (eps_r_[id] + eps_r_[index(i, j + 1)]);
                double eps_s = 0.5 * (eps_r_[id] + eps_r_[index(i, j - 1)]);

                double num = eps_e * phi_[index(i + 1, j)] +
                             eps_w * phi_[index(i - 1, j)] +
                             eps_n * phi_[index(i, j + 1)] +
                             eps_s * phi_[index(i, j - 1)] +
                             (h2 * rho_free_[id] / EPS0);
                double den = eps_e + eps_w + eps_n + eps_s;
                double phi_target = num / den;

                double diff = std::abs(phi_target - phi_[id]);
                if (diff > max_diff) max_diff = diff;

                phi_[id] += omega * (phi_target - phi_[id]);
            }
        }
        return max_diff;
    }

    void compute_fields() {
        double h2 = 2.0 * h_;
        for (size_t i = 1; i < nx_ - 1; ++i) {
            for (size_t j = 1; j < ny_ - 1; ++j) {
                size_t id = index(i, j);
                double ex = -(phi_[index(i + 1, j)] - phi_[index(i - 1, j)]) / h2;
                double ey = -(phi_[index(i, j + 1)] - phi_[index(i, j - 1)]) / h2;

                Ex_[id] = ex;
                Ey_[id] = ey;

                double eps = eps_r_[id];
                Dx_[id] = EPS0 * eps * ex;
                Dy_[id] = EPS0 * eps * ey;

                Px_[id] = Dx_[id] - EPS0 * ex;
                Py_[id] = Dy_[id] - EPS0 * ey;
            }
        }
    }

    [[nodiscard]] FieldPoint get_point(size_t i, size_t j) const {
        size_t id = index(i, j);
        return FieldPoint{
            .phi = phi_[id],
            .Ex = Ex_[id], .Ey = Ey_[id],
            .Dx = Dx_[id], .Dy = Dy_[id],
            .Px = Px_[id], .Py = Py_[id]
        };
    }

private:
    void set_boundary(size_t i, size_t j, double val) {
        size_t id = index(i, j);
        phi_[id] = val;
        is_boundary_[id] = true;
    }

    [[nodiscard]] size_t index(size_t i, size_t j) const noexcept {
        return i * ny_ + j;
    }

    size_t nx_, ny_;
    double h_;
    std::vector<double> phi_, eps_r_, rho_free_;
    std::vector<bool> is_boundary_;
    std::vector<double> Ex_, Ey_, Dx_, Dy_, Px_, Py_;
};

int main() {
    constexpr size_t N = 100;
    auto solver = std::make_unique<DielectricPoissonSolver2D>(N, N, 0.1);

    solver->setup_microstrip_geometry(4.4, 100.0);

    constexpr double omega = 1.90;
    size_t iter = 0;
    for (; iter < 5000; ++iter) {
        if (solver->iterate_sor(omega) < 1e-6) break;
    }

    solver->compute_fields();

    auto pt_sub = solver->get_point(N / 2, N / 4);
    auto pt_air = solver->get_point(N / 2, 3 * N / 4);

    std::cout << std::scientific << std::setprecision(3);
    std::cout << "[C++20 Solver] Збіжність за " << iter << " ітерацій.\n";
    std::cout << "Підкладка (eps=4.4): Ey = " << pt_sub.Ey << " В/м, Dy = " << pt_sub.Dy << " Кл/м²\n";
    std::cout << "Повітря    (eps=1.0): Ey = " << pt_air.Ey << " В/м, Dy = " << pt_air.Dy << " Кл/м²\n";

    return 0;
}

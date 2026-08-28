// dielectric_solver.cpp — Ідіоматичний C++20 розв'язувач полів D та E з RAII
#include <iostream>
#include <vector>
#include <memory>
#include <cmath>
#include <iomanip>
#include <span>

class DielectricFieldSolver2D {
public:
    static constexpr double EPS0 = 8.854187817e-12;

    DielectricFieldSolver2D(size_t nx, size_t ny)
        : nx_(nx), ny_(ny), h_(1.0 / static_cast<double>(nx - 1)),
          phi_(nx * ny, 0.0), eps_r_(nx * ny, 1.0),
          rho_free_(nx * ny, 0.0), Ex_(nx * ny, 0.0), Ey_(nx * ny, 0.0),
          Dx_(nx * ny, 0.0), Dy_(nx * ny, 0.0) {}

    void setup_layered_capacitor(double voltage, double eps_relative_top) {
        for (size_t i = 0; i < nx_; ++i) {
            for (size_t j = 0; j < ny_; ++j) {
                size_t idx = index(i, j);
                eps_r_[idx] = (j < ny_ / 2) ? 1.0 : eps_relative_top;
            }
        }
        for (size_t i = 0; i < nx_; ++i) {
            phi_[index(i, 0)] = 0.0;
            phi_[index(i, ny_ - 1)] = voltage;
        }
    }

    void solve_sor(size_t max_iterations, double omega) {
        for (size_t iter = 0; iter < max_iterations; ++iter) {
            for (size_t i = 1; i < nx_ - 1; ++i) {
                for (size_t j = 1; j < ny_ - 1; ++j) {
                    size_t idx = index(i, j);
                    double eps_e = 0.5 * (eps_r_[idx] + eps_r_[index(i + 1, j)]);
                    double eps_w = 0.5 * (eps_r_[idx] + eps_r_[index(i - 1, j)]);
                    double eps_n = 0.5 * (eps_r_[idx] + eps_r_[index(i, j + 1)]);
                    double eps_s = 0.5 * (eps_r_[idx] + eps_r_[index(i, j - 1)]);

                    double num = eps_e * phi_[index(i + 1, j)] + eps_w * phi_[index(i - 1, j)] +
                                 eps_n * phi_[index(i, j + 1)] + eps_s * phi_[index(i, j - 1)] +
                                 (h_ * h_ * rho_free_[idx] / EPS0);
                    double den = eps_e + eps_w + eps_n + eps_s;
                    double phi_new = num / den;

                    phi_[idx] += omega * (phi_new - phi_[idx]);
                }
            }
        }
    }

    void compute_vector_fields() {
        for (size_t i = 1; i < nx_ - 1; ++i) {
            for (size_t j = 1; j < ny_ - 1; ++j) {
                size_t idx = index(i, j);
                Ex_[idx] = -(phi_[index(i + 1, j)] - phi_[index(i - 1, j)]) / (2.0 * h_);
                Ey_[idx] = -(phi_[index(i, j + 1)] - phi_[index(i, j - 1)]) / (2.0 * h_);

                Dx_[idx] = EPS0 * eps_r_[idx] * Ex_[idx];
                Dy_[idx] = EPS0 * eps_r_[idx] * Ey_[idx];
            }
        }
    }

    struct FieldPoint {
        double Ey;
        double Dy;
    };

    FieldPoint get_point(size_t i, size_t j) const {
        size_t idx = index(i, j);
        return { Ey_[idx], Dy_[idx] };
    }

private:
    [[nodiscard]] size_t index(size_t i, size_t j) const noexcept {
        return i * ny_ + j;
    }

    size_t nx_, ny_;
    double h_;
    std::vector<double> phi_, eps_r_, rho_free_;
    std::vector<double> Ex_, Ey_, Dx_, Dy_;
};

int main() {
    constexpr size_t N = 80;
    auto solver = std::make_unique<DielectricFieldSolver2D>(N, N);

    solver->setup_layered_capacitor(100.0, 5.0);
    solver->solve_sor(2000, 1.85);
    solver->compute_vector_fields();

    auto pt_air = solver->get_point(N / 2, N / 4);
    auto pt_cer = solver->get_point(N / 2, 3 * N / 4);

    std::cout << std::scientific << std::setprecision(3);
    std::cout << "[C++20 Solver] Результати на лінії симетрії:\n";
    std::cout << "Повітря:  Ey = " << pt_air.Ey << " В/м, Dy = " << pt_air.Dy << " Кл/м²\n";
    std::cout << "Кераміка: Ey = " << pt_cer.Ey << " В/м, Dy = " << pt_cer.Dy << " Кл/м²\n";

    return 0;
}

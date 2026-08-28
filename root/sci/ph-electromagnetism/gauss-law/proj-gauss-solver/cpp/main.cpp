#include <iostream>
#include <vector>
#include <cmath>
#include <memory>
#include <expected>
#include <system_error>
#include <iomanip>

constexpr double EPSILON_0 = 8.854187817e-12; // Електрична стала (Ф/м)

enum class SolverError {
    InvalidDimensions,
    MemoryAllocationFailed,
    ConvergenceFailed
};

class ElectrostaticSolver3D {
private:
    int nx_, ny_, nz_;
    double h_;
    std::vector<double> v_;
    std::vector<double> rho_;
    std::vector<double> ex_;
    std::vector<double> ey_;
    std::vector<double> ez_;
    std::vector<bool> fixed_;

    [[nodiscard]] inline size_t idx(int i, int j, int k) const noexcept {
        return static_cast<size_t>(i) * (ny_ * nz_) + j * nz_ + k;
    }

public:
    ElectrostaticSolver3D(int nx, int ny, int nz, double h)
        : nx_(nx), ny_(ny), nz_(nz), h_(h),
          v_(nx * ny * nz, 0.0),
          rho_(nx * ny * nz, 0.0),
          ex_(nx * ny * nz, 0.0),
          ey_(nx * ny * nz, 0.0),
          ez_(nx * ny * nz, 0.0),
          fixed_(nx * ny * nz, false) {}

    void addCharge(int i, int j, int k, double coulombs) {
        if (i >= 0 && i < nx_ && j >= 0 && j < ny_ && k >= 0 && k < nz_) {
            double cell_vol = h_ * h_ * h_;
            rho_[idx(i, j, k)] += coulombs / cell_vol;
        }
    }

    void setBoundaryDirichlet(int i, int j, int k, double potential_volts) {
        size_t id = idx(i, j, k);
        v_[id] = potential_volts;
        fixed_[id] = true;
    }

    [[nodiscard]] std::expected<int, SolverError> solvePoisson(double tol = 1e-5, int max_iter = 2000, double omega = 1.5) {
        if (nx_ < 3 || ny_ < 3 || nz_ < 3) {
            return std::unexpected(SolverError::InvalidDimensions);
        }

        const double h2 = h_ * h_;
        const double inv_eps = 1.0 / EPSILON_0;

        for (int iter = 0; iter < max_iter; ++iter) {
            double max_diff = 0.0;

            for (int i = 1; i < nx_ - 1; ++i) {
                for (int j = 1; j < ny_ - 1; ++j) {
                    for (int k = 1; k < nz_ - 1; ++k) {
                        size_t curr = idx(i, j, k);
                        if (fixed_[curr]) continue;

                        double v_old = v_[curr];
                        double sum_nbrs = v_[idx(i + 1, j, k)] + v_[idx(i - 1, j, k)] +
                                          v_[idx(i, j + 1, k)] + v_[idx(i, j - 1, k)] +
                                          v_[idx(i, j, k + 1)] + v_[idx(i, j, k - 1)];

                        double v_gs = (sum_nbrs + h2 * rho_[curr] * inv_eps) / 6.0;
                        double v_new = (1.0 - omega) * v_old + omega * v_gs;

                        v_[curr] = v_new;
                        max_diff = std::max(max_diff, std::abs(v_new - v_old));
                    }
                }
            }

            if (max_diff < tol) {
                return iter + 1;
            }
        }
        return std::unexpected(SolverError::ConvergenceFailed);
    }

    void computeElectricField() {
        const double inv_2h = 1.0 / (2.0 * h_);
        for (int i = 1; i < nx_ - 1; ++i) {
            for (int j = 1; j < ny_ - 1; ++j) {
                for (int k = 1; k < nz_ - 1; ++k) {
                    size_t id = idx(i, j, k);
                    ex_[id] = -(v_[idx(i + 1, j, k)] - v_[idx(i - 1, j, k)]) * inv_2h;
                    ey_[id] = -(v_[idx(i, j + 1, k)] - v_[idx(i, j - 1, k)]) * inv_2h;
                    ez_[id] = -(v_[idx(i, j, k + 1)] - v_[idx(i, j, k - 1)]) * inv_2h;
                }
            }
        }
    }

    struct GaussResult {
        double flux;
        double q_enclosed;
        double expected_flux;
        double relative_error_percent;
    };

    [[nodiscard]] GaussResult verifyGaussLaw(int i1, int i2, int j1, int j2, int k1, int k2) const {
        double flux = 0.0;
        double area_elem = h_ * h_;
        double q_sum = 0.0;

        for (int i = i1; i <= i2; ++i) {
            for (int j = j1; j <= j2; ++j) {
                for (int k = k1; k <= k2; ++k) {
                    q_sum += rho_[idx(i, j, k)] * (h_ * h_ * h_);
                }
            }
        }

        for (int j = j1; j <= j2; ++j) {
            for (int k = k1; k <= k2; ++k) {
                flux += -ex_[idx(i1, j, k)] * area_elem;
                flux +=  ex_[idx(i2, j, k)] * area_elem;
            }
        }

        for (int i = i1; i <= i2; ++i) {
            for (int k = k1; k <= k2; ++k) {
                flux += -ey_[idx(i, j1, k)] * area_elem;
                flux +=  ey_[idx(i, j2, k)] * area_elem;
            }
        }

        for (int i = i1; i <= i2; ++i) {
            for (int j = j1; j <= j2; ++j) {
                flux += -ez_[idx(i, j, k1)] * area_elem;
                flux +=  ez_[idx(i, j, k2)] * area_elem;
            }
        }

        double expected = q_sum / EPSILON_0;
        double err = std::abs(flux - expected) / expected * 100.0;
        return {flux, q_sum, expected, err};
    }
};

int main() {
    constexpr int N = 41;
    constexpr double H = 0.05;
    ElectrostaticSolver3D solver(N, N, N, H);

    const int center = N / 2;
    solver.addCharge(center, center, center, 1.0e-9); // 1 нКл

    // Встановлення нульових граничних умов Діріхле
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            solver.setBoundaryDirichlet(i, j, 0, 0.0);
            solver.setBoundaryDirichlet(i, j, N - 1, 0.0);
            solver.setBoundaryDirichlet(i, 0, j, 0.0);
            solver.setBoundaryDirichlet(i, N - 1, j, 0.0);
            solver.setBoundaryDirichlet(0, i, j, 0.0);
            solver.setBoundaryDirichlet(N - 1, i, j, 0.0);
        }
    }

    std::cout << "Розв'язання рівняння Пуассона (C++ SOR)... ";
    auto result = solver.solvePoisson(1.0e-5, 2000, 1.6);
    if (result) {
        std::cout << "Збіжність досягнута за " << *result << " ітерацій.\n";
    } else {
        std::cerr << "Помилка розв'язання Пуассона!\n";
        return 1;
    }

    solver.computeElectricField();

    constexpr int margin = 5;
    auto gauss = solver.verifyGaussLaw(center - margin, center + margin,
                                       center - margin, center + margin,
                                       center - margin, center + margin);

    std::cout << std::scientific << std::setprecision(4);
    std::cout << "\n=== РЕЗУЛЬТАТИ ЧИСЕЛЬНОЇ ПЕРЕВІРКИ ЗАКОНУ ГАУССА (C++) ===\n";
    std::cout << "Внутрішній заряд Q_enclosed : " << gauss.q_enclosed << " Кл\n";
    std::cout << "Обчислений потік ∮ E · dA   : " << gauss.flux << " В·м\n";
    std::cout << "Теоретичний потік Q / eps0  : " << gauss.expected_flux << " В·м\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Відносна похибка сітки     : " << gauss.relative_error_percent << "%\n";

    return 0;
}

#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

class PotentialSolver {
public:
    PotentialSolver(size_t nx, size_t ny, double dx)
        : nx_(nx), ny_(ny), dx_(dx),
          phi_(nx, std::vector<double>(ny, 0.0)),
          Az_(nx, std::vector<double>(ny, 0.0)),
          Ax_(nx, std::vector<double>(ny, 0.0)),
          Ay_(nx, std::vector<double>(ny, 0.0)),
          Ex_(nx, std::vector<double>(ny, 0.0)),
          Ey_(nx, std::vector<double>(ny, 0.0)),
          Bx_(nx, std::vector<double>(ny, 0.0)),
          By_(nx, std::vector<double>(ny, 0.0)) {}

    void set_sources(size_t cx, size_t cy, double charge, double current) {
        rho_ = std::vector<std::vector<double>>(nx_, std::vector<double>(ny_, 0.0));
        Jz_  = std::vector<std::vector<double>>(nx_, std::vector<double>(ny_, 0.0));
        rho_[cx][cy] = charge;
        Jz_[cx][cy]  = current;
    }

    void solve(size_t max_iter = 2000, double tol = 1e-6) {
        solve_grid(phi_, rho_, max_iter, tol);
        solve_grid(Az_, Jz_, max_iter, tol);
        update_fields();
    }

    void apply_gauge_transformation(double scale) {
        for (size_t i = 1; i < nx_ - 1; ++i) {
            for (size_t j = 1; j < ny_ - 1; ++j) {
                double y = (static_cast<double>(j) - ny_ / 2.0) * dx_;
                double x = (static_cast<double>(i) - nx_ / 2.0) * dx_;
                Ax_[i][j] += scale * y;
                Ay_[i][j] += scale * x;
            }
        }
        update_fields();
    }

    struct FieldPoint {
        double Ex, Ey, Bx, By;
    };

    FieldPoint get_point(size_t i, size_t j) const {
        return {Ex_[i][j], Ey_[i][j], Bx_[i][j], By_[i][j]};
    }

private:
    void solve_grid(std::vector<std::vector<double>>& field,
                    const std::vector<std::vector<double>>& rhs,
                    size_t max_iter, double tol) {
        double dx2 = dx_ * dx_;
        std::vector<std::vector<double>> next = field;

        for (size_t iter = 0; iter < max_iter; ++iter) {
            double max_diff = 0.0;
            for (size_t i = 1; i < nx_ - 1; ++i) {
                for (size_t j = 1; j < ny_ - 1; ++j) {
                    next[i][j] = 0.25 * (field[i+1][j] + field[i-1][j] +
                                        field[i][j+1] + field[i][j-1] +
                                        dx2 * rhs[i][j]);
                    double diff = std::abs(next[i][j] - field[i][j]);
                    if (diff > max_diff) max_diff = diff;
                }
            }
            field = next;
            if (max_diff < tol) break;
        }
    }

    void update_fields() {
        for (size_t i = 1; i < nx_ - 1; ++i) {
            for (size_t j = 1; j < ny_ - 1; ++j) {
                Ex_[i][j] = -(phi_[i+1][j] - phi_[i-1][j]) / (2.0 * dx_);
                Ey_[i][j] = -(phi_[i][j+1] - phi_[i][j-1]) / (2.0 * dx_);

                Bx_[i][j] = (Az_[i][j+1] - Az_[i][j-1]) / (2.0 * dx_);
                By_[i][j] = -(Az_[i+1][j] - Az_[i-1][j]) / (2.0 * dx_);
            }
        }
    }

    size_t nx_, ny_;
    double dx_;
    std::vector<std::vector<double>> phi_, Az_, Ax_, Ay_;
    std::vector<std::vector<double>> Ex_, Ey_, Bx_, By_;
    std::vector<std::vector<double>> rho_, Jz_;
};

int main() {
    const size_t N = 64;
    const double dx = 0.1;
    PotentialSolver solver(N, N, dx);

    solver.set_sources(N / 2, N / 2, 10.0, 5.0);
    solver.solve();

    auto before = solver.get_point(N / 2 + 5, N / 2 + 5);

    solver.apply_gauge_transformation(2.5);
    auto after = solver.get_point(N / 2 + 5, N / 2 + 5);

    std::cout << std::scientific << std::setprecision(6);
    std::cout << "E_x до: " << before.Ex << ", після: " << after.Ex
              << " (diff: " << std::abs(before.Ex - after.Ex) << ")\n";
    std::cout << "B_x до: " << before.Bx << ", після: " << after.Bx
              << " (diff: " << std::abs(before.Bx - after.Bx) << ")\n";

    return 0;
}

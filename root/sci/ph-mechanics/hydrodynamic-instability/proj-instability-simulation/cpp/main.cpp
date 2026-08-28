#include <iostream>
#include <vector>
#include <cmath>
#include <memory>
#include <algorithm>

class KelvinHelmholtzSolverCpp {
private:
    int nx_, ny_;
    double lx_, ly_, dx_, dy_;
    double nu_, dt_;
    
    std::vector<double> w_;   // Вихровість
    std::vector<double> psi_; // Функція струменю
    std::vector<double> u_;   // Подовжня швидкість
    std::vector<double> v_;   // Поперечна швидкість

    [[nodiscard]] inline size_t idx(int i, int j) const noexcept {
        return static_cast<size_t>(j * nx_ + i);
    }

public:
    KelvinHelmholtzSolverCpp(int nx, int ny, double lx, double ly, double nu, double dt)
        : nx_(nx), ny_(ny), lx_(lx), ly_(ly), dx_(lx / nx), dy_(ly / ny), nu_(nu), dt_(dt),
          w_(nx * ny, 0.0), psi_(nx * ny, 0.0), u_(nx * ny, 0.0), v_(nx * ny, 0.0) {}

    void initShearLayer(double u0 = 1.0, double delta = 0.05, double eps = 0.05) {
        for (int j = 0; j < ny_; ++j) {
            double y = -ly_ / 2.0 + j * dy_;
            for (int i = 0; i < nx_; ++i) {
                double x = i * dx_;
                u_[idx(i, j)] = u0 * std::tanh(y / delta);
                v_[idx(i, j)] = eps * u0 * std::sin(2.0 * M_PI * x / lx_) * std::exp(-(y / delta) * (y / delta));
            }
        }

        for (int j = 1; j < ny_ - 1; ++j) {
            for (int i = 1; i < nx_ - 1; ++i) {
                double du_dy = (u_[idx(i, j + 1)] - u_[idx(i, j - 1)]) / (2.0 * dy_);
                double dv_dx = (v_[idx(i + 1, j)] - v_[idx(i - 1, j)]) / (2.0 * dx_);
                w_[idx(i, j)] = dv_dx - du_dy;
            }
        }
    }

    void solvePoissonJacobi(int maxIter = 100) {
        double dx2 = dx_ * dx_;
        double dy2 = dy_ * dy_;
        double factor = 0.5 * (dx2 * dy2) / (dx2 + dy2);

        for (int iter = 0; iter < maxIter; ++iter) {
            for (int j = 1; j < ny_ - 1; ++j) {
                for (int i = 1; i < nx_ - 1; ++i) {
                    psi_[idx(i, j)] = factor * (
                        (psi_[idx(i + 1, j)] + psi_[idx(i - 1, j)]) / dx2 +
                        (psi_[idx(i, j + 1)] + psi_[idx(i, j - 1)]) / dy2 +
                        w_[idx(i, j)]
                    );
                }
            }
        }

        for (int j = 1; j < ny_ - 1; ++j) {
            for (int i = 1; i < nx_ - 1; ++i) {
                u_[idx(i, j)] =  (psi_[idx(i, j + 1)] - psi_[idx(i, j - 1)]) / (2.0 * dy_);
                v_[idx(i, j)] = -(psi_[idx(i + 1, j)] - psi_[idx(i - 1, j)]) / (2.0 * dx_);
            }
        }
    }

    void step() {
        solvePoissonJacobi();

        double dx2 = dx_ * dx_;
        double dy2 = dy_ * dy_;

        std::vector<double> w_next = w_;
        for (int j = 1; j < ny_ - 1; ++j) {
            for (int i = 1; i < nx_ - 1; ++i) {
                size_t id = idx(i, j);
                double dw_dx = (w_[idx(i + 1, j)] - w_[idx(i - 1, j)]) / (2.0 * dx_);
                double dw_dy = (w_[idx(i, j + 1)] - w_[idx(i, j - 1)]) / (2.0 * dy_);
                double d2w_dx2 = (w_[idx(i + 1, j)] - 2.0 * w_[id] + w_[idx(i - 1, j)]) / dx2;
                double d2w_dy2 = (w_[idx(i, j + 1)] - 2.0 * w_[id] + w_[idx(i, j - 1)]) / dy2;

                double conv = u_[id] * dw_dx + v_[id] * dw_dy;
                double diff = nu_ * (d2w_dx2 + d2w_dy2);

                w_next[id] += dt_ * (-conv + diff);
            }
        }
        w_ = std::move(w_next);
    }

    [[nodiscard]] double getMaxVorticity() const noexcept {
        double max_w = 0.0;
        for (double val : w_) {
            max_w = std::abs(val) > max_w ? std::abs(val) : max_w;
        }
        return max_w;
    }
};

int main() {
    auto solver = std::make_unique<KelvinHelmholtzSolverCpp>(64, 64, 1.0, 1.0, 1e-4, 1e-3);
    solver->initShearLayer();
    for (int t = 0; t < 50; ++t) {
        solver->step();
    }
    std::cout << "C++ KH simulation finished. Max vorticity: " << solver->getMaxVorticity() << std::endl;
    return 0;
}

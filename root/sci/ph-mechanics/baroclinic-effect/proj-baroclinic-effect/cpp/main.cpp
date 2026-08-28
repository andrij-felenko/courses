#include <vector>
#include <span>
#include <stdexcept>
#include <cmath>

// Структура результату бароклінної діагностики у C++20
struct BaroclinicResult {
    std::vector<double> tau_z;
    std::vector<double> du_g_dz;
    std::vector<double> dv_g_dz;
};

class BaroclinicDiagnosticSolver {
public:
    BaroclinicDiagnosticSolver(size_t nx, size_t ny, size_t nz,
                               double dx, double dy, double f = 1e-4, double g = 9.81)
        : nx_(nx), ny_(ny), nz_(nz), dx_(dx), dy_(dy), f_(f), g_(g)
    {
        if (nx < 3 || ny < 3 || nz < 1) {
            throw std::invalid_argument("Розмір сітки повинен бути не менше 3x3x1");
        }
    }

    BaroclinicResult compute(std::span<const double> p,
                             std::span<const double> rho,
                             std::span<const double> T) const
    {
        const size_t total_size = nx_ * ny_ * nz_;
        if (p.size() != total_size || rho.size() != total_size || T.size() != total_size) {
            throw std::invalid_argument("Нерозмірні вхідні буфери сітки");
        }

        BaroclinicResult res{
            .tau_z   = std::vector<double>(total_size, 0.0),
            .du_g_dz = std::vector<double>(total_size, 0.0),
            .dv_g_dz = std::vector<double>(total_size, 0.0)
        };

        for (size_t k = 0; k < nz_; ++k) {
            for (size_t j = 1; j < ny_ - 1; ++j) {
                for (size_t i = 1; i < nx_ - 1; ++i) {
                    const size_t idx = k * (ny_ * nx_) + j * nx_ + i;

                    const double dp_dx = (p[idx + 1] - p[idx - 1]) / (2.0 * dx_);
                    const double dp_dy = (p[idx + nx_] - p[idx - nx_]) / (2.0 * dy_);

                    const double drho_dx = (rho[idx + 1] - rho[idx - 1]) / (2.0 * dx_);
                    const double drho_dy = (rho[idx + nx_] - rho[idx - nx_]) / (2.0 * dy_);

                    const double dT_dx = (T[idx + 1] - T[idx - 1]) / (2.0 * dx_);
                    const double dT_dy = (T[idx + nx_] - T[idx - nx_]) / (2.0 * dy_);

                    const double r = rho[idx];
                    res.tau_z[idx] = (drho_dx * dp_dy - drho_dy * dp_dx) / (r * r);

                    const double temp = T[idx];
                    res.du_g_dz[idx] = - (g_ / (f_ * temp)) * dT_dy;
                    res.dv_g_dz[idx] =   (g_ / (f_ * temp)) * dT_dx;
                }
            }
        }

        return res;
    }

private:
    size_t nx_, ny_, nz_;
    double dx_, dy_;
    double f_;
    double g_;
};

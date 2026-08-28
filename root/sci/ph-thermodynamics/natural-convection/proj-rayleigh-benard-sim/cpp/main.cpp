#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <iomanip>

class RayleighBenardSolver {
public:
    RayleighBenardSolver(std::size_t nx, std::size_t ny, double rayleigh, double prandtl)
        : m_nx(nx), m_ny(ny), m_ra(rayleigh), m_pr(prandtl),
          m_dx(2.0 / static_cast<double>(nx - 1)),
          m_dy(1.0 / static_cast<double>(ny - 1)),
          m_dt(0.0001),
          m_theta(ny, std::vector<double>(nx, 0.0)),
          m_omega(ny, std::vector<double>(nx, 0.0)),
          m_psi(ny, std::vector<double>(nx, 0.0)),
          m_u(ny, std::vector<double>(nx, 0.0)),
          m_v(ny, std::vector<double>(nx, 0.0))
    {
        initializeFields();
    }

    void step() {
        updateVelocities();
        advanceFields();
        solvePoissonPsi();
    }

    [[nodiscard]] double getCenterTemperature() const noexcept {
        return m_theta[m_ny / 2][m_nx / 2];
    }

    [[nodiscard]] double getMaxStreamFunction() const noexcept {
        double max_val = 0.0;
        for (const auto& row : m_psi) {
            for (double val : row) {
                max_val = std::max(max_val, std::abs(val));
            }
        }
        return max_val;
    }

private:
    void initializeFields() {
        for (std::size_t y = 0; y < m_ny; ++y) {
            for (std::size_t x = 0; x < m_nx; ++x) {
                double ly = static_cast<double>(y) * m_dy;
                double lx = static_cast<double>(x) * m_dx;
                /* Початкове лінійне поле з синусоїдальним збуренням */
                m_theta[y][x] = (1.0 - ly) + 0.05 * std::sin(std::numbers::pi * lx) * std::sin(std::numbers::pi * ly);
            }
        }
    }

    void updateVelocities() {
        for (std::size_t y = 1; y < m_ny - 1; ++y) {
            for (std::size_t x = 1; x < m_nx - 1; ++x) {
                m_u[y][x] = (m_psi[y + 1][x] - m_psi[y - 1][x]) / (2.0 * m_dy);
                m_v[y][x] = -(m_psi[y][x + 1] - m_psi[y][x - 1]) / (2.0 * m_dx);
            }
        }
    }

    void advanceFields() {
        std::vector<std::vector<double>> dtheta(m_ny, std::vector<double>(m_nx, 0.0));
        std::vector<std::vector<double>> domega(m_ny, std::vector<double>(m_nx, 0.0));

        double dx2 = m_dx * m_dx;
        double dy2 = m_dy * m_dy;

        for (std::size_t y = 1; y < m_ny - 1; ++y) {
            for (std::size_t x = 1; x < m_nx - 1; ++x) {
                double dth_dx = (m_theta[y][x + 1] - m_theta[y][x - 1]) / (2.0 * m_dx);
                double dth_dy = (m_theta[y + 1][x] - m_theta[y - 1][x]) / (2.0 * m_dy);
                double dom_dx = (m_omega[y][x + 1] - m_omega[y][x - 1]) / (2.0 * m_dx);
                double dom_dy = (m_omega[y + 1][x] - m_omega[y - 1][x]) / (2.0 * m_dy);

                double lap_th = (m_theta[y][x + 1] - 2.0 * m_theta[y][x] + m_theta[y][x - 1]) / dx2 +
                                (m_theta[y + 1][x] - 2.0 * m_theta[y][x] + m_theta[y - 1][x]) / dy2;
                double lap_om = (m_omega[y][x + 1] - 2.0 * m_omega[y][x] + m_omega[y][x - 1]) / dx2 +
                                (m_omega[y + 1][x] - 2.0 * m_omega[y][x] + m_omega[y - 1][x]) / dy2;

                dtheta[y][x] = -(m_u[y][x] * dth_dx + m_v[y][x] * dth_dy) + lap_th;
                domega[y][x] = -(m_u[y][x] * dom_dx + m_v[y][x] * dom_dy) +
                               m_pr * lap_om + m_ra * m_pr * dth_dx;
            }
        }

        for (std::size_t y = 1; y < m_ny - 1; ++y) {
            for (std::size_t x = 1; x < m_nx - 1; ++x) {
                m_theta[y][x] += m_dt * dtheta[y][x];
                m_omega[y][x] += m_dt * domega[y][x];
            }
        }

        /* Граничні умови Тома для завихреності на твердих стінках */
        for (std::size_t x = 0; x < m_nx; ++x) {
            m_omega[0][x] = -2.0 * m_psi[1][x] / dy2;
            m_omega[m_ny - 1][x] = -2.0 * m_psi[m_ny - 2][x] / dy2;
        }
    }

    void solvePoissonPsi() {
        double dx2 = m_dx * m_dx;
        double dy2 = m_dy * m_dy;
        double factor = 0.5 * dx2 * dy2 / (dx2 + dy2);
        constexpr double sor_relax = 1.75;

        for (int iter = 0; iter < 100; ++iter) {
            double max_err = 0.0;
            for (std::size_t y = 1; y < m_ny - 1; ++y) {
                for (std::size_t x = 1; x < m_nx - 1; ++x) {
                    double psi_new = factor * ((m_psi[y][x + 1] + m_psi[y][x - 1]) / dx2 +
                                              (m_psi[y + 1][x] + m_psi[y - 1][x]) / dy2 +
                                              m_omega[y][x]);
                    double diff = psi_new - m_psi[y][x];
                    m_psi[y][x] += sor_relax * diff;
                    max_err = std::max(max_err, std::abs(diff));
                }
            }
            if (max_err < 1e-5) break;
        }
    }

    std::size_t m_nx;
    std::size_t m_ny;
    double m_ra;
    double m_pr;
    double m_dx;
    double m_dy;
    double m_dt;
    std::vector<std::vector<double>> m_theta;
    std::vector<std::vector<double>> m_omega;
    std::vector<std::vector<double>> m_psi;
    std::vector<std::vector<double>> m_u;
    std::vector<std::vector<double>> m_v;
};

int main() {
    RayleighBenardSolver solver(64, 32, 3000.0, 0.71);

    std::cout << "Симуляція конвекції Рейле-Бенара на C++ (Ra = 3000.0)...\n";
    for (int step = 0; step < 1000; ++step) {
        solver.step();
        if (step % 200 == 0) {
            std::cout << "Крок " << std::setw(4) << step
                      << ": T_center = " << std::fixed << std::setprecision(4) << solver.getCenterTemperature()
                      << ", Psi_max = " << std::setprecision(5) << solver.getMaxStreamFunction() << '\n';
        }
    }
    std::cout << "Симуляція успішно завершена.\n";
    return 0;
}

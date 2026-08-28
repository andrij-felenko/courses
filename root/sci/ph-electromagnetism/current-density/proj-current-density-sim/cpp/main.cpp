#include <iostream>
#include <vector>
#include <cmath>
#include <memory>
#include <iomanip>

constexpr std::size_t NX = 64;
constexpr std::size_t NY = 32;
constexpr std::size_t MAX_ITER = 5000;
constexpr double TOL = 1e-5;
constexpr double SIGMA = 5.8e7; // См/м

struct Vector2D {
    double x{0.0};
    double y{0.0};
    [[nodiscard]] double magnitude() const noexcept {
        return std::hypot(x, y);
    }
};

class CurrentDensitySolver {
public:
    CurrentDensitySolver(std::size_t nx, std::size_t ny, double grid_step)
        : m_nx(nx), m_ny(ny), m_h(grid_step),
          m_v(ny, std::vector<double>(nx, 0.0)),
          m_j(ny, std::vector<Vector2D>(nx)),
          m_mask(ny, std::vector<bool>(nx, true)) 
    {
        init_geometry();
    }

    void solve() {
        for (std::size_t iter = 0; iter < MAX_ITER; ++iter) {
            double max_diff = 0.0;
            for (std::size_t j = 1; j < m_ny - 1; ++j) {
                for (std::size_t i = 1; i < m_nx - 1; ++i) {
                    if (!m_mask[j][i]) continue;

                    double old_v = m_v[j][i];
                    double sum = 0.0;
                    int count = 0;

                    if (m_mask[j][i + 1]) { sum += m_v[j][i + 1]; count++; }
                    if (m_mask[j][i - 1]) { sum += m_v[j][i - 1]; count++; }
                    if (m_mask[j + 1][i]) { sum += m_v[j + 1][i]; count++; }
                    if (m_mask[j - 1][i]) { sum += m_v[j - 1][i]; count++; }

                    if (count > 0) {
                        m_v[j][i] = sum / count;
                        max_diff = std::max(max_diff, std::abs(m_v[j][i] - old_v));
                    }
                }
            }
            if (max_diff < TOL) break;
        }

        compute_field();
    }

    [[nodiscard]] Vector2D current_density(std::size_t i, std::size_t j) const {
        return m_j.at(j).at(i);
    }

private:
    void init_geometry() {
        for (std::size_t j = 0; j < m_ny; ++j) {
            for (std::size_t i = 0; i < m_nx; ++i) {
                if (i >= 24 && i <= 40) {
                    if (j < 10 || j > 21) {
                        m_mask[j][i] = false; // Звуження
                    }
                }
            }
        }

        // Граничні умови
        for (std::size_t j = 0; j < m_ny; ++j) {
            if (m_mask[j][0]) m_v[j][0] = 10.0;
            if (m_mask[j][m_nx - 1]) m_v[j][m_nx - 1] = 0.0;
        }
    }

    void compute_field() {
        for (std::size_t j = 1; j < m_ny - 1; ++j) {
            for (std::size_t i = 1; i < m_nx - 1; ++i) {
                if (!m_mask[j][i]) continue;

                double dv_dx = (m_v[j][i + 1] - m_v[j][i - 1]) / (2.0 * m_h);
                double dv_dy = (m_v[j + 1][i] - m_v[j - 1][i]) / (2.0 * m_h);

                m_j[j][i] = {-SIGMA * dv_dx, -SIGMA * dv_dy};
            }
        }
    }

    std::size_t m_nx, m_ny;
    double m_h;
    std::vector<std::vector<double>> m_v;
    std::vector<std::vector<Vector2D>> m_j;
    std::vector<std::vector<bool>> m_mask;
};

int main() {
    CurrentDensitySolver solver(NX, NY, 0.001); // h = 1 мм
    solver.solve();

    auto j_center = solver.current_density(32, 16);
    std::cout << std::scientific << std::setprecision(3);
    std::cout << "C++ Солвер успішно виконано.\n";
    std::cout << "Модуль щільності струму J у звуженні: " << j_center.magnitude() << " А/м²\n";

    return 0;
}

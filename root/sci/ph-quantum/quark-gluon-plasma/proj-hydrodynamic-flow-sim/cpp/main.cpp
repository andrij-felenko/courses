#include <iostream>
#include <vector>
#include <cmath>
#include <memory>
#include <iomanip>
#include <algorithm>

constexpr int NX = 41;
constexpr int NY = 41;
constexpr int STEPS = 120;
constexpr double DX = 0.2;
constexpr double DY = 0.2;
constexpr double DT = 0.05;
constexpr double CS2 = 1.0 / 3.0;

struct GridCell {
    double energy{0.0};
    double vx{0.0};
    double vy{0.0};
};

class QGPHydroSimulation {
public:
    QGPHydroSimulation(double rx, double ry, double e0)
        : m_grid(NX, std::vector<GridCell>(NY)) {
        initGlauberEllipse(rx, ry, e0);
    }

    void step() {
        auto next_grid = m_grid;

        for (int i = 1; i < NX - 1; ++i) {
            for (int j = 1; j < NY - 1; ++j) {
                const double de_dx = (m_grid[i + 1][j].energy - m_grid[i - 1][j].energy) / (2.0 * DX);
                const double de_dy = (m_grid[i][j + 1].energy - m_grid[i][j - 1].energy) / (2.0 * DY);

                const double e_curr = m_grid[i][j].energy + 1e-6;
                const double p_curr = CS2 * e_curr;
                const double dp_dx = CS2 * de_dx;
                const double dp_dy = CS2 * de_dy;

                const double ax = -dp_dx / (e_curr + p_curr);
                const double ay = -dp_dy / (e_curr + p_curr);

                next_grid[i][j].vx = m_grid[i][j].vx + ax * DT;
                next_grid[i][j].vy = m_grid[i][j].vy + ay * DT;

                const double div_ev = (m_grid[i + 1][j].energy * m_grid[i + 1][j].vx - m_grid[i - 1][j].energy * m_grid[i - 1][j].vx) / (2.0 * DX) +
                                      (m_grid[i][j + 1].energy * m_grid[i][j + 1].vy - m_grid[i][j - 1].energy * m_grid[i][j - 1].vy) / (2.0 * DY);

                next_grid[i][j].energy = std::max(0.0, m_grid[i][j].energy - div_ev * DT);
            }
        }
        m_grid = std::move(next_grid);
    }

    [[nodiscard]] double calculateV2() const {
        double sum_num = 0.0;
        double sum_den = 0.0;

        for (int i = 0; i < NX; ++i) {
            for (int j = 0; j < NY; ++j) {
                const auto& cell = m_grid[i][j];
                const double px = cell.energy * cell.vx;
                const double py = cell.energy * cell.vy;
                const double p2 = px * px + py * py;

                if (p2 > 1e-8) {
                    sum_num += (px * px - py * py);
                    sum_den += (px * px + py * py);
                }
            }
        }
        return (sum_den > 0.0) ? (sum_num / sum_den) : 0.0;
    }

private:
    void initGlauberEllipse(double rx, double ry, double e0) {
        const int cx = NX / 2;
        const int cy = NY / 2;

        for (int i = 0; i < NX; ++i) {
            for (int j = 0; j < NY; ++j) {
                const double x = (i - cx) * DX;
                const double y = (j - cy) * DY;
                const double r2_ell = (x * x) / (rx * rx) + (y * y) / (ry * ry);

                if (r2_ell <= 1.0) {
                    m_grid[i][j].energy = e0 * (1.0 - r2_ell);
                }
            }
        }
    }

    std::vector<std::vector<GridCell>> m_grid;
};

int main() {
    QGPHydroSimulation sim(2.0, 3.5, 10.0);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Крок 0: початковий v2 = " << sim.calculateV2() << "\n";

    for (int step = 1; step <= STEPS; ++step) {
        sim.step();
        if (step % 30 == 0) {
            std::cout << "Крок " << step << ": v2 = " << sim.calculateV2() << "\n";
        }
    }

    return 0;
}

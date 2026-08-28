/* surface_leakage_sim.cpp - 2D FDM Laplace solver for PCB surface leakage (C++20) */
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <iomanip>
#include <span>

namespace pcb::sim {

constexpr int GridWidth = 80;
constexpr int GridHeight = 80;
constexpr double CellSizeMm = 0.1;
constexpr double SheetResistanceOhm = 1.0e10; /* 10 ГОм/квадрат */
constexpr int MaxIterations = 10000;
constexpr double ConvergenceTolerance = 1.0e-6;
constexpr double OmegaSor = 1.75;

enum class NodeType : uint8_t {
    Dielectric,
    PowerRail,
    HighZ,
    GuardRing,
    Ground
};

struct SimulationResult {
    int iterations{0};
    double leakageCurrentAmps{0.0};
};

class PcbSurfaceSolver {
public:
    explicit PcbSurfaceSolver(bool enableGuard) {
        initializeMesh(enableGuard);
    }

    [[nodiscard]] SimulationResult solve() {
        int iter = 0;
        double maxDiff = 0.0;

        do {
            maxDiff = 0.0;
            for (int y = 1; y < GridHeight - 1; ++y) {
                for (int x = 1; x < GridWidth - 1; ++x) {
                    if (nodeType_[y][x] != NodeType::Dielectric) {
                        continue;
                    }

                    const double vOld = potential_[y][x];
                    const double vRelaxed = 0.25 * (potential_[y + 1][x] + potential_[y - 1][x] +
                                                    potential_[y][x + 1] + potential_[y - 1][x]);
                    const double vNew = vOld + OmegaSor * (vRelaxed - vOld);

                    potential_[y][x] = vNew;
                    maxDiff = std::max(maxDiff, std::abs(vNew - vOld));
                }
            }
            ++iter;
        } while (maxDiff > ConvergenceTolerance && iter < MaxIterations);

        return {
            .iterations = iter,
            .leakageCurrentAmps = computeNodeLeakageCurrent()
        };
    }

private:
    std::array<std::array<double, GridWidth>, GridHeight> potential_{};
    std::array<std::array<NodeType, GridWidth>, GridHeight> nodeType_{};

    void initializeMesh(bool enableGuard) {
        for (int y = 0; y < GridHeight; ++y) {
            for (int x = 0; x < GridWidth; ++x) {
                potential_[y][x] = 0.0;
                nodeType_[y][x] = NodeType::Dielectric;

                if (x == 0 || x == GridWidth - 1 || y == 0 || y == GridHeight - 1) {
                    nodeType_[y][x] = NodeType::Ground;
                    potential_[y][x] = 0.0;
                } else if (x >= 10 && x <= 14 && y >= 15 && y <= 65) {
                    nodeType_[y][x] = NodeType::PowerRail;
                    potential_[y][x] = 15.0;
                } else if (x >= 45 && x <= 51 && y >= 37 && y <= 43) {
                    nodeType_[y][x] = NodeType::HighZ;
                    potential_[y][x] = 0.0;
                } else if (enableGuard) {
                    const bool inOuter = (x >= 37 && x <= 59 && y >= 29 && y <= 51);
                    const bool inInner = (x >= 40 && x <= 56 && y >= 32 && y <= 48);
                    if (inOuter && !inInner) {
                        nodeType_[y][x] = NodeType::GuardRing;
                        potential_[y][x] = 0.0;
                    }
                }
            }
        }
    }

    [[nodiscard]] double computeNodeLeakageCurrent() const {
        double totalFlux = 0.0;
        constexpr double sigmaSurface = 1.0 / SheetResistanceOhm;
        constexpr std::array<std::pair<int, int>, 4> directions{{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}};

        for (int y = 1; y < GridHeight - 1; ++y) {
            for (int x = 1; x < GridWidth - 1; ++x) {
                if (nodeType_[y][x] != NodeType::HighZ) {
                    continue;
                }

                for (const auto& [dx, dy] : directions) {
                    const int nx = x + dx;
                    const int ny = y + dy;
                    if (nodeType_[ny][nx] == NodeType::Dielectric) {
                        totalFlux += (potential_[ny][nx] - potential_[y][x]);
                    }
                }
            }
        }

        return sigmaSurface * totalFlux;
    }
};

} // namespace pcb::sim

int main() {
    using namespace pcb::sim;

    std::cout << "=== СИМУЛЯТОР ПОВЕРХНЕВОГО ВИТОКУ НА ДРУКОВАНІЙ ПЛАТІ (C++20) ===\n";
    std::cout << "Поверхневий опір: " << std::scientific << std::setprecision(1)
              << SheetResistanceOhm << " Ом/кв\n\n";

    PcbSurfaceSolver unshieldedSolver(false);
    const auto unshieldedResult = unshieldedSolver.solve();

    PcbSurfaceSolver guardedSolver(true);
    const auto guardedResult = guardedSolver.solve();

    std::cout << "--- РЕЗУЛЬТАТИ МОДЕЛЮВАННЯ ---\n";
    std::cout << "1. Без Guard Ring:\n"
              << "   - Ітерацій: " << unshieldedResult.iterations << "\n"
              << "   - Струм витоку: " << std::fixed << std::setprecision(2)
              << unshieldedResult.leakageCurrentAmps * 1.0e12 << " пА\n\n";

    std::cout << "2. З Guard Ring (V_guard = 0.0 В):\n"
              << "   - Ітерацій: " << guardedResult.iterations << "\n"
              << "   - Струм витоку: " << std::fixed << std::setprecision(2)
              << guardedResult.leakageCurrentAmps * 1.0e15 << " фА\n\n";

    const double ratio = (guardedResult.leakageCurrentAmps > 1.0e-25)
        ? (unshieldedResult.leakageCurrentAmps / guardedResult.leakageCurrentAmps)
        : 1.0e12;
    std::cout << "Придушення струму витоку: " << std::scientific << std::setprecision(1)
              << ratio << " разів\n";

    return 0;
}

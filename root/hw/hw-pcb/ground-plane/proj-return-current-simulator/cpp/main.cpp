#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <memory>
#include <iomanip>
#include <span>
#include <algorithm>
#include <stdexcept>
#include <format>

namespace pcb::em::fdm {

constexpr double Mu0 = 4.0 * std::numbers::pi * 1e-7;
constexpr double CopperSigma = 5.8e7;

struct GridDimensions {
    int nx{80};
    int ny{40};
    double gridStepM{0.00025};
    double dielectricHeightM{0.00012};
};

struct Point2D {
    int x{0};
    int y{0};
};

struct RectDefect {
    int xStart{0};
    int yStart{0};
    int width{0};
    int length{0};
};

class GroundPlaneSimulator {
public:
    explicit GroundPlaneSimulator(const GridDimensions& dims)
        : dims_{dims},
          potential_(static_cast<size_t>(dims.nx) * dims.ny, 0.0),
          jx_(static_cast<size_t>(dims.nx) * dims.ny, 0.0),
          jy_(static_cast<size_t>(dims.nx) * dims.ny, 0.0),
          jMag_(static_cast<size_t>(dims.nx) * dims.ny, 0.0),
          mask_(static_cast<size_t>(dims.nx) * dims.ny, 1) {}

    void addSlotDefect(const RectDefect& slot) noexcept {
        for (int y = slot.yStart; y < slot.yStart + slot.length && y < dims_.ny; ++y) {
            for (int x = slot.xStart; x < slot.xStart + slot.width && x < dims_.nx; ++x) {
                const auto idx = linearIndex(x, y);
                mask_[idx] = 0;
                potential_[idx] = 0.0;
            }
        }
    }

    void addStitchingBridge(const RectDefect& bridge) noexcept {
        for (int y = bridge.yStart; y < bridge.yStart + bridge.length && y < dims_.ny; ++y) {
            for (int x = bridge.xStart; x < bridge.xStart + bridge.width && x < dims_.nx; ++x) {
                const auto idx = linearIndex(x, y);
                mask_[idx] = 1;
            }
        }
    }

    [[nodiscard]] int solveSor(Point2D portIn, Point2D portOut, double tolerance = 1e-6, int maxIter = 5000) {
        const double rhoJ = 0.5 * (std::cos(std::numbers::pi / dims_.nx) + std::cos(std::numbers::pi / dims_.ny));
        const double omega = 2.0 / (1.0 + std::sqrt(1.0 - rhoJ * rhoJ));

        const auto inIdx = linearIndex(portIn.x, portIn.y);
        const auto outIdx = linearIndex(portOut.x, portOut.y);

        for (int iter = 0; iter < maxIter; ++iter) {
            double maxDiff = 0.0;

            for (int y = 0; y < dims_.ny; ++y) {
                for (int x = 0; x < dims_.nx; ++x) {
                    const auto idx = linearIndex(x, y);

                    if (idx == inIdx) {
                        potential_[idx] = 1.0;
                        continue;
                    }
                    if (idx == outIdx) {
                        potential_[idx] = 0.0;
                        continue;
                    }
                    if (mask_[idx] == 0) {
                        continue;
                    }

                    double sum = 0.0;
                    int count = 0;

                    if (x > 0 && mask_[idx - 1]) { sum += potential_[idx - 1]; count++; }
                    if (x < dims_.nx - 1 && mask_[idx + 1]) { sum += potential_[idx + 1]; count++; }
                    if (y > 0 && mask_[idx - dims_.nx]) { sum += potential_[idx - dims_.nx]; count++; }
                    if (y < dims_.ny - 1 && mask_[idx + dims_.nx]) { sum += potential_[idx + dims_.nx]; count++; }

                    if (count > 0) {
                        const double vNew = sum / static_cast<double>(count);
                        const double vSor = (1.0 - omega) * potential_[idx] + omega * vNew;
                        const double diff = std::abs(vSor - potential_[idx]);
                        if (diff > maxDiff) maxDiff = diff;
                        potential_[idx] = vSor;
                    }
                }
            }

            if (maxDiff < tolerance) {
                return iter + 1;
            }
        }
        return maxIter;
    }

    void computeCurrents() noexcept {
        const double inv2h = 1.0 / (2.0 * dims_.gridStepM);

        for (int y = 0; y < dims_.ny; ++y) {
            for (int x = 0; x < dims_.nx; ++x) {
                const auto idx = linearIndex(x, y);
                if (mask_[idx] == 0) {
                    jx_[idx] = jy_[idx] = jMag_[idx] = 0.0;
                    continue;
                }

                double dvDx = 0.0;
                double dvDy = 0.0;

                if (x > 0 && x < dims_.nx - 1 && mask_[idx - 1] && mask_[idx + 1]) {
                    dvDx = (potential_[idx + 1] - potential_[idx - 1]) * inv2h;
                } else if (x < dims_.nx - 1 && mask_[idx + 1]) {
                    dvDx = (potential_[idx + 1] - potential_[idx]) / dims_.gridStepM;
                } else if (x > 0 && mask_[idx - 1]) {
                    dvDx = (potential_[idx] - potential_[idx - 1]) / dims_.gridStepM;
                }

                if (y > 0 && y < dims_.ny - 1 && mask_[idx - dims_.nx] && mask_[idx + dims_.nx]) {
                    dvDy = (potential_[idx + dims_.nx] - potential_[idx - dims_.nx]) * inv2h;
                } else if (y < dims_.ny - 1 && mask_[idx + dims_.nx]) {
                    dvDy = (potential_[idx + dims_.nx] - potential_[idx]) / dims_.gridStepM;
                } else if (y > 0 && mask_[idx - dims_.nx]) {
                    dvDy = (potential_[idx] - potential_[idx - dims_.nx]) / dims_.gridStepM;
                }

                jx_[idx] = -CopperSigma * dvDx;
                jy_[idx] = -CopperSigma * dvDy;
                jMag_[idx] = std::hypot(jx_[idx], jy_[idx]);
            }
        }
    }

    [[nodiscard]] double extractLoopInductance(double testCurrentA = 1.0) const noexcept {
        double energySum = 0.0;
        for (size_t i = 0; i < mask_.size(); ++i) {
            if (mask_[i]) {
                energySum += jMag_[i] * jMag_[i];
            }
        }

        const double cellArea = dims_.gridStepM * dims_.gridStepM;
        const double totalEnergy = 0.5 * Mu0 * dims_.dielectricHeightM * cellArea * energySum;
        return (2.0 * totalEnergy) / (testCurrentA * testCurrentA);
    }

    [[nodiscard]] double peakCurrentDensity() const noexcept {
        return *std::max_element(jMag_.begin(), jMag_.end());
    }

private:
    [[nodiscard]] inline size_t linearIndex(int x, int y) const noexcept {
        return static_cast<size_t>(y) * dims_.nx + static_cast<size_t>(x);
    }

    GridDimensions dims_;
    std::vector<double> potential_;
    std::vector<double> jx_;
    std::vector<double> jy_;
    std::vector<double> jMag_;
    std::vector<uint8_t> mask_;
};

} // namespace pcb::em::fdm

int main() {
    using namespace pcb::em::fdm;

    constexpr GridDimensions dims{
        .nx = 80,
        .ny = 40,
        .gridStepM = 0.00025,
        .dielectricHeightM = 0.00012
    };

    std::cout << "===================================================================\n";
    std::cout << "     ЧИСЕЛЬНИЙ 2D FDM СИМУЛЯТОР ЗВОРОТНОГО СТРУМУ В GND (C++20)    \n";
    std::cout << "===================================================================\n\n";

    constexpr Point2D portIn{.x = 5, .y = 20};
    constexpr Point2D portOut{.x = 75, .y = 20};

    GroundPlaneSimulator simSolid(dims);
    const int iterSolid = simSolid.solveSor(portIn, portOut);
    simSolid.computeCurrents();
    const double lSolid = simSolid.extractLoopInductance(1.0);

    std::cout << "ТЕСТ 1: Нерозривний опорний шар землі (Solid GND Plane)\n";
    std::cout << "  Ітерацій SOR:                 " << iterSolid << "\n";
    std::cout << "  Петльова індуктивність L_loop: " << (lSolid * 1e9) << " нГн\n";
    std::cout << "  Пікова густина струму J_max:   " << (simSolid.peakCurrentDensity() * 1e-3) << " кА/м²\n\n";

    GroundPlaneSimulator simSlotted(dims);
    simSlotted.addSlotDefect(RectDefect{.xStart = 40, .yStart = 8, .width = 3, .length = 24});
    const int iterSlotted = simSlotted.solveSor(portIn, portOut);
    simSlotted.computeCurrents();
    const double lSlotted = simSlotted.extractLoopInductance(1.0);

    std::cout << "ТЕСТ 2: Перетин поперечного розрізу землі (Transverse Slot)\n";
    std::cout << "  Розмір розрізу:               0.75 x 6.00 мм\n";
    std::cout << "  Ітерацій SOR:                 " << iterSlotted << "\n";
    std::cout << "  Петльова індуктивність L_loop: " << (lSlotted * 1e9) << " нГн\n";
    std::cout << "  Сплеск індуктивності ΔL_slot:  +" << ((lSlotted - lSolid) * 1e9) << " нГн\n\n";

    GroundPlaneSimulator simStitched(dims);
    simStitched.addSlotDefect(RectDefect{.xStart = 40, .yStart = 8, .width = 3, .length = 24});
    simStitched.addStitchingBridge(RectDefect{.xStart = 40, .yStart = 19, .width = 3, .length = 3});
    const int iterStitched = simStitched.solveSor(portIn, portOut);
    simStitched.computeCurrents();
    const double lStitched = simStitched.extractLoopInductance(1.0);

    std::cout << "ТЕСТ 3: Розріз зі зшивальним містком землі (Stitching Bridge)\n";
    std::cout << "  Розмір містка:                0.75 x 0.75 мм\n";
    std::cout << "  Ітерацій SOR:                 " << iterStitched << "\n";
    std::cout << "  Петльова індуктивність L_loop: " << (lStitched * 1e9) << " нГн\n";
    std::cout << "  Відновлення індуктивності:     " << ((lSlotted - lStitched) / (lSlotted - lSolid) * 100.0) << "%\n\n";

    return 0;
}

#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <random>
#include <span>
#include <iomanip>
#include <algorithm>

namespace flash_model {

constexpr std::size_t CellCount = 50'000;
constexpr std::size_t StateCount = 8; /* TLC */
constexpr double InitialSigma = 0.075;

constexpr std::array<double, StateCount> VCenters = {
    1.25, 1.85, 2.45, 3.05, 3.65, 4.25, 4.85, 5.45
};

constexpr std::array<std::uint8_t, StateCount> GrayTable = {
    0x07, 0x06, 0x04, 0x05, 0x01, 0x00, 0x02, 0x03
};

class FlashDegradationSimulator {
public:
    explicit FlashDegradationSimulator(std::uint32_t seed = 12345) : rng_(seed) {}

    struct Metrics {
        std::size_t totalBits;
        std::size_t hardErrors;
        double rawBitErrorRate;
        double strongLlrFraction;
        double strongLlrAccuracy;
    };

    [[nodiscard]] Metrics evaluate(std::size_t peCycles, double retentionDays, double softDelta = 0.035) {
        std::uniform_int_distribution<int> stateDist(0, StateCount - 1);
        std::normal_distribution<double> normDist(0.0, 1.0);

        const double wearSigma = InitialSigma * (1.0 + 0.00025 * std::sqrt(static_cast<double>(peCycles)));
        const double vBoundary = (VCenters[3] + VCenters[4]) * 0.5;

        std::size_t hardErrors = 0;
        std::size_t strongCount = 0;
        std::size_t strongCorrect = 0;

        for (std::size_t i = 0; i < CellCount; ++i) {
            int state = stateDist(rng_);
            std::uint8_t writtenBits = GrayTable[state];

            double drift = (state > 0) ? (-0.0004 * state * std::log(1.0 + retentionDays * 24.0)) : 0.0;
            double vth = VCenters[state] + drift + normDist(rng_) * wearSigma;

            int readState = senseHard(vth);
            std::uint8_t readBits = GrayTable[readState];

            for (int b = 0; b < 3; ++b) {
                if (((bits_written_val(writtenBits, b)) != (bits_written_val(readBits, b)))) {
                    ++hardErrors;
                }
            }

            double llr = computeSoftLlr(vth, vBoundary, softDelta);
            if (std::abs(llr) > 4.5) {
                ++strongCount;
                bool isZero = (state >= 4);
                if ((llr > 0.0) == isZero) {
                    ++strongCorrect;
                }
            }
        }

        std::size_t totalBits = CellCount * 3;
        double rber = static_cast<double>(hardErrors) / static_cast<double>(totalBits);
        double strongFraction = static_cast<double>(strongCount) / static_cast<double>(CellCount) * 100.0;
        double strongAccuracy = (strongCount > 0)
            ? (static_cast<double>(strongCorrect) / static_cast<double>(strongCount) * 100.0)
            : 100.0;

        return { totalBits, hardErrors, rber, strongFraction, strongAccuracy };
    }

private:
    [[nodiscard]] static std::uint8_t bits_written_val(std::uint8_t val, int bit) noexcept {
        return (val >> bit) & 1;
    }

    [[nodiscard]] static int senseHard(double vth) noexcept {
        for (std::size_t i = 0; i < StateCount - 1; ++i) {
            double vRef = (VCenters[i] + VCenters[i + 1]) * 0.5;
            if (vth < vRef) return static_cast<int>(i);
        }
        return static_cast<int>(StateCount - 1);
    }

    [[nodiscard]] static double computeSoftLlr(double vth, double vRefMid, double deltaStep) noexcept {
        double deltaV = vth - vRefMid;
        double bin = std::floor(deltaV / deltaStep);
        bin = std::clamp(bin, -3.0, 2.0);
        return -bin * 2.4;
    }
};

} // namespace flash_model

int main() {
    flash_model::FlashDegradationSimulator sim(12345);

    const std::size_t peCycles = 2500;
    const double retentionDays = 90.0;

    std::cout << "=== Симулятор деградації комірок TLC Flash (C++20) ===\n"
              << "Кількість комірок: " << flash_model::CellCount
              << ", Циклів P/E: " << peCycles
              << ", Термін зберігання: " << retentionDays << " діб\n\n";

    auto metrics = sim.evaluate(peCycles, retentionDays);

    std::cout << "Помилок жорсткого читання: " << metrics.hardErrors << " з " << metrics.totalBits << " бітів\n"
              << "Вхідний рівень помилок (RBER): " << std::scientific << std::setprecision(4)
              << metrics.rawBitErrorRate << " (" << std::fixed << std::setprecision(3)
              << metrics.rawBitErrorRate * 100.0 << "%)\n"
              << "Частка високодостовірних LLR: " << std::setprecision(2) << metrics.strongLlrFraction << "%\n"
              << "Точність бітів з високим LLR: " << std::setprecision(4) << metrics.strongLlrAccuracy << "%\n";

    return 0;
}

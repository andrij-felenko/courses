#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <random>
#include <numbers>
#include <span>
#include <iomanip>

namespace flash_sim {

constexpr std::size_t CellCount = 100'000;
constexpr std::size_t StateCount = 8; // TLC: 8 станів напруги (3 біти)
constexpr double BaseSigma = 0.08;

constexpr std::array<double, StateCount> StateCenters = {
    1.20, 1.80, 2.40, 3.00, 3.60, 4.20, 4.80, 5.40
};

constexpr std::array<std::uint8_t, StateCount> GrayMap = {
    0x07, 0x06, 0x04, 0x05, 0x01, 0x00, 0x02, 0x03
};

class CellArraySimulator {
public:
    explicit CellArraySimulator(std::uint32_t seed = 42) : rng_(seed) {}

    struct SimulationResult {
        std::size_t totalBits;
        std::size_t hardErrors;
        double rawBitErrorRate;
        double highConfidenceAccuracy;
    };

    SimulationResult run(std::size_t peCycles, double retentionHours, double softStrobeDelta = 0.035) {
        std::uniform_int_distribution<int> stateDist(0, StateCount - 1);
        std::normal_distribution<double> normDist(0.0, 1.0);

        std::size_t totalBits = CellCount * 3;
        std::size_t hardErrors = 0;
        std::size_t highConfidenceTotal = 0;
        std::size_t highConfidenceCorrect = 0;

        const double wearFactor = 1.0 + 0.0003 * std::sqrt(static_cast<double>(peCycles));
        const double sigma = BaseSigma * wearFactor;

        for (std::size_t i = 0; i < CellCount; ++i) {
            int state = stateDist(rng_);
            std::uint8_t writtenBits = GrayMap[state];

            double drift = (state > 0) ? (-0.0005 * state * std::log(1.0 + retentionHours)) : 0.0;
            double vth = StateCenters[state] + drift + normDist(rng_) * sigma;

            int readState = senseHard(vth);
            std::uint8_t readBits = GrayMap[readState];

            for (int b = 0; b < 3; ++b) {
                if (((writtenBits >> b) & 1) != ((readBits >> b) & 1)) {
                    ++hardErrors;
                }
            }

            // М'яка оцінка LLR біля центрального розділового порогу
            double vRefMid = (StateCenters[3] + StateCenters[4]) * 0.5;
            double llr = computeLlr(vth, vRefMid, softStrobeDelta);

            if (std::abs(llr) > 5.0) {
                ++highConfidenceTotal;
                bool expectedZero = (state >= 4);
                bool predictedZero = (llr > 0.0);
                if (expectedZero == predictedZero) {
                    ++highConfidenceCorrect;
                }
            }
        }

        double rber = static_cast<double>(hardErrors) / static_cast<double>(totalBits);
        double accuracy = (highConfidenceTotal > 0) 
            ? (100.0 * static_cast<double>(highConfidenceCorrect) / static_cast<double>(highConfidenceTotal)) 
            : 100.0;

        return { totalBits, hardErrors, rber, accuracy };
    }

private:
    std::mt19937 rng_;

    [[nodiscard]] static int senseHard(double vth) noexcept {
        for (std::size_t i = 0; i < StateCount - 1; ++i) {
            double vRef = (StateCenters[i] + StateCenters[i + 1]) * 0.5;
            if (vth < vRef) {
                return static_cast<int>(i);
            }
        }
        return static_cast<int>(StateCount - 1);
    }

    [[nodiscard]] static double computeLlr(double vth, double vRefCenter, double deltaStep) noexcept {
        double diff = vth - vRefCenter;
        double binIndex = std::floor(diff / deltaStep);
        binIndex = std::clamp(binIndex, -4.0, 3.0);
        return -binIndex * 2.1;
    }
};

} // namespace flash_sim

int main() {
    flash_sim::CellArraySimulator sim(42);

    const std::size_t peCycles = 1500;
    const double retentionHours = 720.0; // 30 діб зберігання

    std::cout << "=== Симулятор зчитування Flash-комірок TLC (C++20) ===\n"
              << "Кількість досліджуваних комірок: " << flash_sim::CellCount << "\n"
              << "Циклів зносу (P/E): " << peCycles << ", Час утримання: " << retentionHours << " год\n\n";

    auto result = sim.run(peCycles, retentionHours);

    std::cout << "--- Результати моделювання ---\n"
              << "Помилок твердого читання: " << result.hardErrors << " з " << result.totalBits << " бітів\n"
              << "Вхідний рівень помилок (RBER): " << std::scientific << std::setprecision(5) 
              << result.rawBitErrorRate << " (" << std::fixed << std::setprecision(3) 
              << result.rawBitErrorRate * 100.0 << "%)\n"
              << "Достовірність високопріоритетних бінів LLR (|LLR| > 5.0): " 
              << std::setprecision(4) << result.highConfidenceAccuracy << "%\n";

    return 0;
}

#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>
#include <stdexcept>
#include <span>

class GenerationSimulator {
public:
    GenerationSimulator(size_t samples, double freq, double quant_step)
        : step_(quant_step)
    {
        orig_.reserve(samples);
        for (size_t i = 0; i < samples; ++i) {
            double t = static_cast<double>(i) / static_cast<double>(samples);
            orig_.push_back(std::sin(2.0 * std::numbers::pi * freq * t));
        }
        aligned_ = orig_;
        misaligned_ = orig_;
    }

    struct StepResult {
        int generation;
        double snr_aligned;
        double snr_misaligned;
    };

    StepResult step(double phase_shift) {
        ++current_gen_;

        // 1. Вирівняне квантування (на атракторі)
        for (auto &val : aligned_) {
            val = std::round(val / step_) * step_;
        }

        // 2. Квантування зі зсувом сітки
        for (auto &val : misaligned_) {
            double mod = val * (1.0 + phase_shift);
            mod = std::round(mod / step_) * step_;
            val = mod / (1.0 + phase_shift);
        }

        return {
            current_gen_,
            calculate_snr(orig_, aligned_),
            calculate_snr(orig_, misaligned_)
        };
    }

private:
    static double calculate_snr(std::span<const double> orig, std::span<const double> curr) {
        double p_sig = 0.0;
        double p_noise = 0.0;
        for (size_t i = 0; i < orig.size(); ++i) {
            p_sig += orig[i] * orig[i];
            double diff = curr[i] - orig[i];
            p_noise += diff * diff;
        }
        if (p_noise < 1e-15) return 999.0;
        return 10.0 * std::log10(p_sig / p_noise);
    }

    double step_;
    int current_gen_{0};
    std::vector<double> orig_;
    std::vector<double> aligned_;
    std::vector<double> misaligned_;
};

int main() {
    constexpr size_t SAMPLES = 4000;
    constexpr double FREQ = 5.0;
    constexpr double QUANT_STEP = 0.05;
    constexpr double DRIFT_EPS = 0.002;
    constexpr int TOTAL_GENERATIONS = 10;

    GenerationSimulator sim(SAMPLES, FREQ, QUANT_STEP);

    std::cout << "Покоління | SNR Aligned (дБ) | SNR Misaligned (дБ)\n";
    std::cout << "----------+-------------------+--------------------\n";

    for (int i = 0; i < TOTAL_GENERATIONS; ++i) {
        auto res = sim.step(DRIFT_EPS);
        std::cout << "   " << std::setw(2) << res.generation << "     |     "
                  << std::setw(7) << std::fixed << std::setprecision(2) << res.snr_aligned
                  << "       |      "
                  << std::setw(7) << std::fixed << std::setprecision(2) << res.snr_misaligned
                  << "\n";
    }

    return 0;
}

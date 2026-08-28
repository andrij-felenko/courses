#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <optional>
#include <string_view>

namespace rf {

enum class Injection { HighSide, LowSide };

struct FrequencyPlanConfig {
    double rf_frequency_hz;
    double if1_frequency_hz;
    double if2_frequency_hz;
    Injection lo1_injection{Injection::HighSide};
    Injection lo2_injection{Injection::HighSide};
    double roofing_bandwidth_hz{15000.0};
};

struct SpurProduct {
    int m_lo;
    int n_rf;
    int order;
    double frequency_hz;
    double offset_from_if1_hz;
};

struct FrequencyPlanResult {
    double lo1_hz;
    double img1_hz;
    double lo2_hz;
    double img2_hz;
    bool is_spectrum_inverted;
    std::vector<SpurProduct> detected_spurs;
};

class FrequencyPlanner {
public:
    explicit FrequencyPlanner(FrequencyPlanConfig config) : config_(config) {}

    [[nodiscard]] FrequencyPlanResult compute() const {
        FrequencyPlanResult result{};

        // Calculate 1st Conversion
        if (config_.lo1_injection == Injection::HighSide) {
            result.lo1_hz  = config_.rf_frequency_hz + config_.if1_frequency_hz;
            result.img1_hz = config_.rf_frequency_hz + 2.0 * config_.if1_frequency_hz;
        } else {
            result.lo1_hz  = config_.rf_frequency_hz - config_.if1_frequency_hz;
            result.img1_hz = config_.rf_frequency_hz - 2.0 * config_.if1_frequency_hz;
        }

        // Calculate 2nd Conversion
        if (config_.lo2_injection == Injection::HighSide) {
            result.lo2_hz  = config_.if1_frequency_hz + config_.if2_frequency_hz;
            result.img2_hz = config_.if1_frequency_hz + 2.0 * config_.if2_frequency_hz;
        } else {
            result.lo2_hz  = config_.if1_frequency_hz - config_.if2_frequency_hz;
            result.img2_hz = config_.if1_frequency_hz - 2.0 * config_.if2_frequency_hz;
        }

        // Evaluate spectrum inversion status
        const bool inv1 = (config_.lo1_injection == Injection::HighSide);
        const bool inv2 = (config_.lo2_injection == Injection::HighSide);
        result.is_spectrum_inverted = (inv1 != inv2);

        // Find spurious mixing products
        result.detected_spurs = find_spurs(result.lo1_hz);

        return result;
    }

private:
    [[nodiscard]] std::vector<SpurProduct> find_spurs(double lo1_hz) const {
        std::vector<SpurProduct> spurs;
        const double half_bw = config_.roofing_bandwidth_hz / 2.0;

        for (int m = 1; m <= 5; ++m) {
            for (int n = 1; n <= 5; ++n) {
                if (m == 1 && n == 1) continue; // Skip fundamental conversion

                double spur_freq = std::abs(static_cast<double>(m) * lo1_hz - 
                                            static_cast<double>(n) * config_.rf_frequency_hz);
                double offset = std::abs(spur_freq - config_.if1_frequency_hz);

                if (offset <= half_bw) {
                    spurs.push_back({m, n, m + n, spur_freq, offset});
                }
            }
        }
        return spurs;
    }

    FrequencyPlanConfig config_;
};

} // namespace rf

int main() {
    rf::FrequencyPlanConfig config{
        .rf_frequency_hz    = 14'050'000.0, // 14.050 MHz
        .if1_frequency_hz   = 45'000'000.0, // 45.000 MHz
        .if2_frequency_hz   =    455'000.0, // 455 kHz
        .lo1_injection      = rf::Injection::HighSide,
        .lo2_injection      = rf::Injection::HighSide,
        .roofing_bandwidth_hz =  15'000.0
    };

    rf::FrequencyPlanner planner(config);
    const auto res = planner.compute();

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== C++20 Калькулятор подвійного перетворення ===\n";
    std::cout << "Вхідна RF      : " << config.rf_frequency_hz / 1e6 << " МГц\n";
    std::cout << "Перша ПЧ (IF1) : " << config.if1_frequency_hz / 1e6 << " МГц\n";
    std::cout << "Друга ПЧ (IF2) : " << config.if2_frequency_hz / 1e3 << " кГц\n";
    std::cout << "--------------------------------------------------\n";
    std::cout << "Гетеродин 1 LO1: " << res.lo1_hz / 1e6 << " МГц\n";
    std::cout << "Дзеркальний 1  : " << res.img1_hz / 1e6 << " МГц\n";
    std::cout << "Гетеродин 2 LO2: " << res.lo2_hz / 1e6 << " МГц\n";
    std::cout << "Дзеркальний 2  : " << res.img2_hz / 1e6 << " МГц\n";
    std::cout << "Спектр         : " 
              << (res.is_spectrum_inverted ? "Інвертований" : "Прямий (Норма)") << "\n";
    std::cout << "--------------------------------------------------\n";

    if (res.detected_spurs.empty()) {
        std::cout << "Завад K <= 10 у смузі руфінг-фільтра не виявлено.\n";
    } else {
        std::cout << "Знайдено завади у смузі руфінгу:\n";
        for (const auto& spur : res.detected_spurs) {
            std::cout << " - Порядок K=" << spur.order 
                      << " (" << spur.m_lo << "*LO1 - " << spur.n_rf << "*RF): "
                      << spur.frequency_hz / 1e6 << " МГц, відхилення: "
                      << spur.offset_from_if1_hz / 1e3 << " кГц\n";
        }
    }

    return 0;
}

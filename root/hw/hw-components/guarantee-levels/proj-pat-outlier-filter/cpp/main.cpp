#include <iostream>
#include <vector>
#include <numeric>
#include <cmath>
#include <algorithm>
#include <span>
#include <string_view>
#include <expected>
#include <format>

// Статуси класифікації кристала
enum class DieStatus {
    Pass,              // Повністю придатний кристал
    OutlierReject,     // Статистичний викид за PAT (прихований дефект)
    HardReject         // Грубий брак (вихід за межі специфікації даташита)
};

// Параметри специфікації даташита
struct PatSpecification {
    double lsl;                // Нижня межа даташита
    double usl;                // Верхня межа даташита
    double sigma_multiplier{3.0}; // Множник сигми для динамічного коридору
};

// Розраховані адаптивні межі PAT
struct PatLimits {
    double mean;
    double std_dev;
    double dynamic_lsl;
    double dynamic_usl;
};

// Можливі помилки розрахунку
enum class PatError {
    InsufficientData,
    InvalidSpecification
};

class PartAverageTester {
public:
    explicit PartAverageTester(PatSpecification spec) : spec_(spec) {}

    // Обчислення адаптивних меж на основі зрізу вимірювань
    [[nodiscard]] std::expected<PatLimits, PatError> compute_limits(std::span<const double> data) const {
        if (data.size() < 2) {
            return std::unexpected(PatError::InsufficientData);
        }
        if (spec_.lsl >= spec_.usl || spec_.sigma_multiplier <= 0.0) {
            return std::unexpected(PatError::InvalidSpecification);
        }

        const double count = static_cast<double>(data.size());
        const double sum = std::accumulate(data.begin(), data.end(), 0.0);
        const double mean = sum / count;

        double sum_sq_diff = 0.0;
        for (const double val : data) {
            const double diff = val - mean;
            sum_sq_diff += diff * diff;
        }
        const double std_dev = std::sqrt(sum_sq_diff / (count - 1.0));

        const double raw_lsl = mean - (spec_.sigma_multiplier * std_dev);
        const double raw_usl = mean + (spec_.sigma_multiplier * std_dev);

        return PatLimits{
            .mean = mean,
            .std_dev = std_dev,
            .dynamic_lsl = std::max(spec_.lsl, raw_lsl),
            .dynamic_usl = std::min(spec_.usl, raw_usl)
        };
    }

    // Класифікація виміряного значення
    [[nodiscard]] DieStatus classify(double value, const PatLimits& limits) const noexcept {
        if (value < spec_.lsl || value > spec_.usl) {
            return DieStatus::HardReject;
        }
        if (value < limits.dynamic_lsl || value > limits.dynamic_usl) {
            return DieStatus::OutlierReject;
        }
        return DieStatus::Pass;
    }

    [[nodiscard]] static std::string_view status_to_string(DieStatus status) noexcept {
        switch (status) {
            case DieStatus::Pass:
                return "ПРИДАТНИЙ (PASS)";
            case DieStatus::OutlierReject:
                return "БРАК PAT (OUTLIER - прихований дефект!)";
            case DieStatus::HardReject:
                return "БРАК ДАТАШИТА (HARD REJECT)";
        }
        return "НЕВІДОМО";
    }

private:
    PatSpecification spec_;
};

int main() {
    const PatSpecification spec{
        .lsl = 80.0,
        .usl = 120.0,
        .sigma_multiplier = 3.0
    };

    const std::vector<double> wafer_measurements{
        99.2, 100.5, 98.8, 101.1, 99.7, 100.2,
        98.9, 100.8, 99.4, 114.0, 100.1, 125.5
    };

    const PartAverageTester tester(spec);
    const auto limits_result = tester.compute_limits(wafer_measurements);

    if (!limits_result) {
        std::cerr << "Помилка розрахунку параметрів PAT\n";
        return 1;
    }

    const auto& limits = *limits_result;
    std::cout << "=== Статистика вибірки пластини (AEC-Q001 PAT C++23) ===\n";
    std::cout << std::format("Середнє (Mean):       {:.3f} мкА\n", limits.mean);
    std::cout << std::format("Стандартне відхилення: {:.3f} мкА\n", limits.std_dev);
    std::cout << std::format("Межі даташита:        [{:.1f} ... {:.1f}] мкА\n", spec.lsl, spec.usl);
    std::cout << std::format("Динамічні межі PAT:   [{:.3f} ... {:.3f}] мкА\n\n", limits.dynamic_lsl, limits.dynamic_usl);

    std::cout << "Результати класифікації кристалів:\n";
    for (size_t i = 0; i < wafer_measurements.size(); ++i) {
        const double val = wafer_measurements[i];
        const DieStatus status = tester.classify(val, limits);
        std::cout << std::format("  Чіп #{:02d}: {:6.2f} мкА -> {}\n",
                                 i + 1, val, PartAverageTester::status_to_string(status));
    }

    return 0;
}

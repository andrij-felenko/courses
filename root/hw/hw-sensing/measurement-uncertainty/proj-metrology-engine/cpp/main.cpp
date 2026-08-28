#include <iostream>
#include <vector>
#include <string_view>
#include <cmath>
#include <numbers>
#include <span>
#include <numeric>
#include <optional>
#include <iomanip>

namespace metrology {

enum class Distribution {
    Rectangular, // u = a / sqrt(3)
    Triangular,  // u = a / sqrt(6)
    NormalK2,    // u = U / 2.0
    NormalK3,    // u = U / 3.0
    UShaped      // u = a / sqrt(2)
};

struct UncertaintyItem {
    std::string_view name;
    double std_uncertainty;
    double sensitivity{1.0};
    double degrees_of_freedom{std::numeric_limits<double>::infinity()};

    [[nodiscard]] constexpr double contribution() const noexcept {
        return sensitivity * std_uncertainty;
    }
};

struct MetrologyReport {
    double value;
    double u_combined;
    double expanded_u;
    double eff_dof;
    double coverage_factor;
};

// Чисельно стабільний акумулятор Велфорда для розрахунку типу A
class WelfordAccumulator {
public:
    void update(double x) noexcept {
        ++count_;
        double delta = x - mean_;
        mean_ += delta / static_cast<double>(count_);
        double delta2 = x - mean_;
        m2_ += delta * delta2;
    }

    void update(std::span<const double> samples) noexcept {
        for (double s : samples) {
            update(s);
        }
    }

    [[nodiscard]] std::size_t count() const noexcept { return count_; }
    [[nodiscard]] double mean() const noexcept { return mean_; }

    [[nodiscard]] std::optional<double> sample_variance() const noexcept {
        if (count_ < 2) return std::nullopt;
        return m2_ / static_cast<double>(count_ - 1);
    }

    [[nodiscard]] std::optional<double> standard_error_of_mean() const noexcept {
        auto var = sample_variance();
        if (!var) return std::nullopt;
        return std::sqrt(*var / static_cast<double>(count_));
    }

private:
    std::size_t count_{0};
    double mean_{0.0};
    double m2_{0.0};
};

// Оцінка стандартної невизначеності за Типом B
[[nodiscard]] constexpr double eval_type_b(double half_width, Distribution dist) noexcept {
    switch (dist) {
        case Distribution::Rectangular:
            return half_width / std::numbers::sqrt3;
        case Distribution::Triangular:
            return half_width / 2.449489742783178; // sqrt(6)
        case Distribution::NormalK2:
            return half_width / 2.0;
        case Distribution::NormalK3:
            return half_width / 3.0;
        case Distribution::UShaped:
            return half_width / std::numbers::sqrt2;
    }
    return half_width / std::numbers::sqrt3;
}

// Розрахунок невизначеності квантування АЦП
[[nodiscard]] constexpr double eval_adc_quantization(double v_ref, uint8_t bits) noexcept {
    double lsb = v_ref / static_cast<double>(1ULL << bits);
    return lsb / 3.4641016151377544; // sqrt(12)
}

// Калькулятор бюджету невизначеності
class UncertaintyBudget {
public:
    void add_item(UncertaintyItem item) {
        items_.push_back(item);
    }

    [[nodiscard]] std::optional<MetrologyReport> evaluate(double meas_val, double k = 2.0) const {
        if (items_.empty()) return std::nullopt;

        double sum_sq = 0.0;
        double ws_denom = 0.0;

        for (const auto& item : items_) {
            double c_u = item.contribution();
            double cont_sq = c_u * c_u;
            sum_sq += cont_sq;

            if (std::isfinite(item.degrees_of_freedom) && item.degrees_of_freedom > 0.0) {
                double cont_quad = cont_sq * cont_sq;
                ws_denom += cont_quad / item.degrees_of_freedom;
            }
        }

        double u_c = std::sqrt(sum_sq);
        double eff_dof = (ws_denom > 1e-15) ? (sum_sq * sum_sq) / ws_denom : std::numeric_limits<double>::infinity();

        return MetrologyReport{
            .value = meas_val,
            .u_combined = u_c,
            .expanded_u = k * u_c,
            .eff_dof = eff_dof,
            .coverage_factor = k
        };
    }

    [[nodiscard]] const std::vector<UncertaintyItem>& items() const noexcept {
        return items_;
    }

private:
    std::vector<UncertaintyItem> items_;
};

} // namespace metrology

int main() {
    using namespace metrology;

    WelfordAccumulator sampler;
    const std::vector<double> samples = {
        10.042, 10.038, 10.045, 10.040, 10.048, 10.037, 10.041, 10.044,
        10.039, 10.046, 10.040, 10.043, 10.036, 10.047, 10.041, 10.042
    };
    sampler.update(samples);

    auto u_a = sampler.standard_error_of_mean().value_or(0.0);
    double mean_pressure = sampler.mean();

    UncertaintyBudget budget;
    budget.add_item({"Випадковий шум вибірки", u_a, 1.0, static_cast<double>(samples.size() - 1)});
    budget.add_item({"Шум квантування АЦП", eval_adc_quantization(20.0, 16), 1.0});
    budget.add_item({"Калібрування давача", eval_type_b(0.05, Distribution::Rectangular), 1.0});
    budget.add_item({"Температурний дрейф", eval_type_b(0.02, Distribution::Triangular), 1.0});

    if (auto rep = budget.evaluate(mean_pressure, 2.0)) {
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "=== Метрологічний звіт вимірювання тиску (C++) ===\n";
        std::cout << "Оцінка значення (середнє): " << rep->value << " бар\n";
        std::cout << "Статистична невизначеність u_A: " << std::setprecision(5) << u_a << " бар\n";
        std::cout << "Сумарна невизначеність u_c:     " << rep->u_combined << " бар\n";
        std::cout << "Розширена невизначеність U(k=2): " << rep->expanded_u << " бар (P = 95.45%)\n";
        std::cout << "Ефективні ступені вільності nu:  " << std::setprecision(1) << rep->eff_dof << "\n";
        std::cout << "Результат для запису: P = (" << std::setprecision(4) << rep->value
                  << " +/- " << rep->expanded_u << ") бар, k=2\n";
    }

    return 0;
}

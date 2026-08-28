#include <iostream>
#include <span>
#include <vector>
#include <cmath>
#include <numbers>
#include <optional>
#include <iomanip>

namespace metrology {

// Чисельно стабільний акумулятор для однопрохідної статистики
class RunningStats {
public:
    void push(double x) noexcept {
        ++count_;
        const double delta = x - mean_;
        mean_ += delta / static_cast<double>(count_);
        const double delta2 = x - mean_;
        m2_ += delta * delta2;
    }

    void push(std::span<const double> data) noexcept {
        for (double v : data) {
            push(v);
        }
    }

    [[nodiscard]] std::size_t count() const noexcept { return count_; }
    [[nodiscard]] double mean() const noexcept { return mean_; }

    [[nodiscard]] std::optional<double> standard_uncertainty_a() const noexcept {
        if (count_ < 2) return std::nullopt;
        const double variance = m2_ / static_cast<double>(count_ - 1);
        return std::sqrt(variance / static_cast<double>(count_));
    }

private:
    std::size_t count_{0};
    double mean_{0.0};
    double m2_{0.0};
};

// Функція оцінювання типу B для рівномірного розподілу
[[nodiscard]] constexpr double type_b_rectangular(double half_width) noexcept {
    return half_width / std::numbers::sqrt3;
}

// Комбінування стандартних невизначеностей у розширену U
[[nodiscard]] inline double combine_expanded(double u_a, double u_b, double k = 2.0) noexcept {
    const double u_c = std::hypot(u_a, u_b);
    return k * u_c;
}

} // namespace metrology

int main() {
    using namespace metrology;

    RunningStats stats;
    const std::vector<double> samples = {1.254, 1.253, 1.255, 1.254, 1.254, 1.253, 1.255, 1.254};
    stats.push(samples);

    if (auto u_a = stats.standard_uncertainty_a()) {
        const double u_b = type_b_rectangular(0.001); // Паспортний допуск +/- 1 мВ
        const double u_exp = combine_expanded(*u_a, u_b, 2.0);

        std::cout << std::fixed << std::setprecision(4);
        std::cout << "Напруга: " << stats.mean() << " V, "
                  << "Розширена невизначеність U(k=2): +/- " << u_exp << " V\n";
    }

    return 0;
}

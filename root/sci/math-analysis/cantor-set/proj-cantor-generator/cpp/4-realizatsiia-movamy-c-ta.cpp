#include <iostream>
#include <vector>
#include <cmath>
#include <span>
#include <optional>
#include <iomanip>

namespace math::fractals {

struct Interval {
    double start{0.0};
    double end{1.0};

    [[nodiscard]] constexpr double length() const noexcept {
        return end - start;
    }
};

class CantorGenerator {
public:
    [[nodiscard]] static std::vector<Interval> generate_level(std::size_t level) {
        std::vector<Interval> current;
        current.reserve(1ULL << level);
        current.push_back({0.0, 1.0});

        for (std::size_t lvl = 0; lvl < level; ++lvl) {
            std::vector<Interval> next;
            next.reserve(current.size() * 2);

            for (const auto& [a, b] : current) {
                const double third = (b - a) / 3.0;
                next.push_back({a, a + third});
                next.push_back({b - third, b});
            }
            current = std::move(next);
        }
        return current;
    }

    [[nodiscard]] static bool contains_point(double x, std::size_t max_depth = 30) noexcept {
        if (x < 0.0 || x > 1.0) return false;

        double curr = x;
        for (std::size_t i = 0; i < max_depth; ++i) {
            curr *= 3.0;
            const auto digit = static_cast<int>(std::floor(curr));
            if (digit == 1) {
                return false;
            }
            if (digit == 2) {
                curr -= 2.0;
            }
        }
        return true;
    }

    [[nodiscard]] static double estimate_box_counting_dimension(std::size_t level) {
        const auto intervals = generate_level(level);
        const double epsilon = std::pow(3.0, -static_cast<double>(level));
        const double num_boxes = static_cast<double>(intervals.size());
        return std::log(num_boxes) / std::log(1.0 / epsilon);
    }
};

} // namespace math::fractals

int main() {
    using namespace math::fractals;

    constexpr std::size_t depth = 5;
    std::cout << "=== C++20 Модуль обчислення множини Кантора ===\n";

    const auto intervals = CantorGenerator::generate_level(depth);
    std::cout << "Рівень " << depth << ": " << intervals.size() << " інтервалів.\n";
    std::cout << "Перші 4 інтервали:\n";
    for (const auto& inv : std::span(intervals).subspan(0, std::min<std::size_t>(4, intervals.size()))) {
        std::cout << "  [" << std::fixed << std::setprecision(6) << inv.start << ", " << inv.end << "]\n";
    }

    const std::vector<double> test_points{0.0, 0.25, 1.0 / 3.0, 0.5, 0.75, 1.0};
    std::cout << "\nПеревірка належності точок (глибина 25):\n";
    for (double pt : test_points) {
        const bool inside = CantorGenerator::contains_point(pt, 25);
        std::cout << "  x = " << std::setw(8) << pt << " -> " << (inside ? "C (Належить)" : "U (Вилучено)") << "\n";
    }

    std::cout << "\nФрактальна вимірність Box-Counting:\n";
    for (std::size_t k = 1; k <= 8; ++k) {
        const double dim = CantorGenerator::estimate_box_counting_dimension(k);
        std::cout << "  k = " << k << " | dim = " << std::setprecision(8) << dim << "\n";
    }

    return 0;
}

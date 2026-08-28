#include <iostream>
#include <vector>
#include <optional>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <algorithm>

// Структура для збереження результатів пошуку
struct HallCandidate {
    std::uint64_t x{0};
    std::uint64_t y{0};
    std::int64_t diff{0};
    double ratio{0.0};
};

// Клас-шукач пар з дотриманням принципів RAII та чистоти функцій
class HallSearcher {
public:
    explicit HallSearcher(double threshold) noexcept : threshold_(threshold) {}

    [[nodiscard]] std::optional<HallCandidate> inspect(std::uint64_t x) const noexcept {
        const double x_dbl = static_cast<double>(x);
        const double sqrt_x = std::sqrt(x_dbl);
        const double y_ideal = x_dbl * sqrt_x;
        const auto y_base = static_cast<std::uint64_t>(std::floor(y_ideal));

        std::optional<HallCandidate> best;
        double min_ratio = 1e18;

        for (std::uint64_t dy = 0; dy <= 1; ++dy) {
            const std::uint64_t y = y_base + dy;
            if (y == 0) continue;

            const unsigned __int128 x128 = x;
            const unsigned __int128 y128 = y;
            const unsigned __int128 x_cube = x128 * x128 * x128;
            const unsigned __int128 y_sq = y128 * y128;

            if (y_sq == x_cube) continue; // Ігноруємо тривіальні розв'язки

            const bool is_negative = (y_sq < x_cube);
            const unsigned __int128 abs_diff_128 = is_negative ? (x_cube - y_sq) : (y_sq - x_cube);
            const double abs_diff = static_cast<double>(abs_diff_128);
            const double ratio = abs_diff / sqrt_x;

            if (ratio < threshold_ && ratio < min_ratio) {
                min_ratio = ratio;
                const auto signed_diff = is_negative 
                    ? -static_cast<std::int64_t>(abs_diff_128)
                    : static_cast<std::int64_t>(abs_diff_128);

                best = HallCandidate{x, y, signed_diff, ratio};
            }
        }
        return best;
    }

    [[nodiscard]] std::vector<HallCandidate> search_range(std::uint64_t start_x, std::uint64_t end_x) const {
        std::vector<HallCandidate> results;
        results.reserve(100); // Попереднє виділення пам'яті для уникнення реалокацій
        
        for (std::uint64_t x = start_x; x <= end_x; ++x) {
            if (auto cand = inspect(x)) {
                results.push_back(*cand);
            }
        }
        return results;
    }

private:
    double threshold_;
};

int main() {
    constexpr std::uint64_t max_x = 10'000'000;
    constexpr double threshold = 0.5;

    std::cout << "Запуск обчислювального пошуку пар Холла (x <= " << max_x 
              << ", ratio < " << threshold << ")\n";

    const HallSearcher searcher(threshold);
    const auto candidates = searcher.search_range(2, max_x);

    std::cout << std::setprecision(6) << std::fixed;
    for (std::size_t i = 0; i < candidates.size(); ++i) {
        const auto& c = candidates[i];
        std::cout << "Пара #" << (i + 1) 
                  << ": x = " << c.x 
                  << ", y = " << c.y 
                  << ", diff = " << c.diff 
                  << ", ratio = " << c.ratio << "\n";
    }

    std::cout << "Усього знайдено рекордно близьких пар: " << candidates.size() << "\n";
    return 0;
}

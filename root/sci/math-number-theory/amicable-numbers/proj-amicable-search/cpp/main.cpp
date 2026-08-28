#include <iostream>
#include <vector>
#include <cstdint>
#include <utility>
#include <format>

// Клас для обчислення та збереження результатів решета
class AmicableSieve {
public:
    explicit AmicableSieve(std::size_t limit)
        : limit_(limit), sum_divisors_(limit + 1, 0) {
        build_sieve();
    }

    // Отримання списку знайдених пар
    [[nodiscard]] std::vector<std::pair<std::size_t, std::size_t>> find_pairs() const {
        std::vector<std::pair<std::size_t, std::size_t>> pairs;

        for (std::size_t a = 2; a <= limit_; ++a) {
            const std::size_t b = sum_divisors_[a];

            // Сувора фільтрація канонічних пар (a < b)
            if (a < b && b <= limit_ && sum_divisors_[b] == a) {
                pairs.emplace_back(a, b);
            }
        }
        return pairs;
    }

private:
    // Внутрішній метод побудови адитивного решета O(N log N)
    void build_sieve() {
        for (std::size_t d = 1; d <= limit_ / 2; ++d) {
            for (std::size_t m = 2 * d; m <= limit_; m += d) {
                sum_divisors_[m] += d;
            }
        }
    }

    std::size_t limit_;
    std::vector<std::size_t> sum_divisors_;
};

int main() {
    constexpr std::size_t limit = 100'000;
    AmicableSieve sieve(limit);
    const auto pairs = sieve.find_pairs();

    std::cout << "--- Знайдені дружні пари у діапазоні до " << limit << " ---\n";
    for (std::size_t idx = 0; const auto& [a, b] : pairs) {
        std::cout << std::format("{:4}: ({}, {})\n", ++idx, a, b);
    }
    std::cout << "Усього знайдено пар: " << pairs.size() << '\n';

    return 0;
}

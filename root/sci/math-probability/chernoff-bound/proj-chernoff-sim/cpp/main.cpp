#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <iomanip>
#include <algorithm>

struct ConcentrationBounds {
    double markov{1.0};
    double chebyshev{1.0};
    double chernoff_approx{1.0};
    double chernoff_exact{1.0};
    double empirical{0.0};
};

class ChernoffSimulator {
public:
    ChernoffSimulator(int n, double p) : n_(n), p_(p), rd_(), gen_(rd_()) {}

    ConcentrationBounds evaluate(double delta, std::size_t trials) {
        ConcentrationBounds b;
        const double mu = n_ * p_;
        const double variance = n_ * p_ * (1.0 - p_);
        const double threshold = (1.0 + delta) * mu;

        // 1. Межа Маркова
        b.markov = std::min(1.0, mu / threshold);

        // 2. Межа Чебишова
        const double dev = threshold - mu;
        b.chebyshev = std::min(1.0, variance / (dev * dev));

        // 3. Межа Чернова (квадратична аппроксимація)
        b.chernoff_approx = std::min(1.0, std::exp(-mu * delta * delta / 3.0));

        // 4. Межа Чернова (точна форма через логарифмічний простір)
        const double log_exact = mu * (delta - (1.0 + delta) * std::log(1.0 + delta));
        b.chernoff_exact = std::min(1.0, std::exp(log_exact));

        // 5. Емпіричне розбиття через якісний генератор Mersenne Twister
        std::bernoulli_distribution dist(p_);
        std::size_t violations = 0;

        for (std::size_t t = 0; t < trials; ++t) {
            int sum = 0;
            for (int i = 0; i < n_; ++i) {
                if (dist(gen_)) {
                    sum++;
                }
            }
            if (sum >= threshold) {
                violations++;
            }
        }
        b.empirical = static_cast<double>(violations) / static_cast<double>(trials);

        return b;
    }

private:
    int n_;
    double p_;
    std::random_device rd_;
    std::mt19937 gen_;
};

int main() {
    constexpr int n = 300;
    constexpr double p = 0.3;
    constexpr double delta = 0.4;
    constexpr std::size_t trials = 200000;

    std::cout << "=== Симуляція нерівності Чернова (C++17) ===\n";
    std::cout << "Параметри: n = " << n << ", p = " << p 
              << ", delta = " << delta << ", trials = " << trials << "\n";
    std::cout << "Очікуване значення mu = " << n * p << "\n";
    std::cout << "Поріг відхилення T = " << (1.0 + delta) * n * p << "\n\n";

    ChernoffSimulator sim(n, p);
    auto bounds = sim.evaluate(delta, trials);

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Емпірична ймовірність Pr[X >= T] : " << bounds.empirical << "\n";
    std::cout << "----------------------------------------\n";
    std::cout << "Межа Маркова                     : " << bounds.markov << "\n";
    std::cout << "Межа Чебишова                    : " << bounds.chebyshev << "\n";
    std::cout << "Межа Чернова (квадратична)       : " << bounds.chernoff_approx << "\n";
    std::cout << "Межа Чернова (точна MGF)         : " << bounds.chernoff_exact << "\n";

    return 0;
}

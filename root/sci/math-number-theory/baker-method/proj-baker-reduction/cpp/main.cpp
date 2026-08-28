#include <iostream>
#include <cmath>
#include <vector>
#include <cstdint>
#include <algorithm>
#include <iomanip>

struct ReductionResult {
    uint64_t final_bound;
    std::size_t steps;
};

// Клас редуктора Бейкера-Давенпорта для двох логарифмів
class BakerDavenportReducer {
public:
    static ReductionResult reduce(double theta, double beta, double K, double c, uint64_t start_M) {
        uint64_t current_M = start_M;
        std::size_t steps = 0;

        while (true) {
            steps++;
            double target_q = 6.0 * static_cast<double>(current_M);

            double x = theta;
            double p_n2 = 1.0, p_n1 = std::floor(x);
            double q_n2 = 0.0, q_n1 = 1.0;

            while (q_n1 <= target_q) {
                double rem = x - std::floor(x);
                if (std::abs(rem) < 1e-15) break;
                x = 1.0 / rem;
                double an = std::floor(x);

                double pn = an * p_n1 + p_n2;
                double qn = an * q_n1 + q_n2;

                p_n2 = p_n1; p_n1 = pn;
                q_n2 = q_n1; q_n1 = qn;
            }

            double q_found = q_n1;
            double p_found = p_n1;

            double q_beta = q_found * beta;
            double dist_to_int = std::abs(q_beta - std::round(q_beta));
            double delta_theta = std::abs(q_found * theta - p_found);

            double epsilon = dist_to_int - static_cast<double>(current_M) * delta_theta;

            if (epsilon <= 0.0) {
                current_M *= 2;
                continue;
            }

            uint64_t b_new = static_cast<uint64_t>(std::floor(std::log(q_found * K / epsilon) / c));

            std::cout << "Крок " << steps << ": q = " << q_found 
                      << ", eps = " << std::scientific << epsilon 
                      << " -> B_new = " << b_new << "\n";

            if (b_new >= current_M) {
                return {current_M, steps};
            }

            current_M = b_new;
            if (current_M <= 50) {
                return {current_M, steps};
            }
        }
    }
};

int main() {
    double theta = std::log(2.0) / std::log(3.0);
    double beta = std::log(5.0) / std::log(3.0);
    double K = 100.0;
    double c = 0.8;
    uint64_t initial_M = 1000000000000000000ULL; // 10^18

    std::cout << "Початкова межа: " << initial_M << "\n";
    auto result = BakerDavenportReducer::reduce(theta, beta, K, c, initial_M);

    std::cout << "\nРедукована межа B <= " << result.final_bound << "\n";
    std::cout << "Усього кроків: " << result.steps << "\n";

    return 0;
}

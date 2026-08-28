#include <iostream>
#include <cstdint>
#include <vector>
#include <unordered_set>

class AliquotTracer {
public:
    static std::uint64_t sum_proper(std::uint64_t n) {
        if (n <= 1) return 0;
        std::uint64_t current_sigma = 1;
        std::uint64_t temp = n;

        for (std::uint64_t d = 2; d * d <= temp; ++d) {
            if (temp % d == 0) {
                std::uint64_t term_sum = 1;
                std::uint64_t p_power = 1;
                while (temp % d == 0) {
                    p_power *= d;
                    term_sum += p_power;
                    temp /= d;
                }
                current_sigma *= term_sum;
            }
        }
        if (temp > 1) current_sigma *= (1 + temp);
        return current_sigma - n;
    }

    static void trace(std::uint64_t start, std::size_t max_steps = 100) {
        std::uint64_t curr = start;
        std::unordered_set<std::uint64_t> visited;

        std::cout << "Sequence for " << start << ": " << curr;

        for (std::size_t step = 0; step < max_steps; ++step) {
            visited.insert(curr);
            curr = sum_proper(curr);
            std::cout << " -> " << curr;

            if (curr == 0) {
                std::cout << " [Terminated]\n";
                return;
            }
            if (visited.contains(curr)) {
                std::cout << " [Cycle Detected]\n";
                return;
            }
        }
        std::cout << " [Reached Max Steps]\n";
    }
};

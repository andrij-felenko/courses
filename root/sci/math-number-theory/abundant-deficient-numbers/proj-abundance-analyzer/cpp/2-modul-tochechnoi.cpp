#include <iostream>
#include <vector>
#include <cstdint>
#include <optional>
#include <stdexcept>

enum class NumberClass {
    Deficient,
    Perfect,
    Abundant
};

struct AbundanceResult {
    std::uint64_t number{0};
    std::uint64_t sigma{0};
    std::uint64_t sum_proper{0};
    double index{0.0};
    NumberClass classification{NumberClass::Deficient};
};

class AbundanceAnalyzer {
public:
    [[nodiscard]] static AbundanceResult analyze(std::uint64_t n) {
        if (n == 0) {
            throw std::invalid_argument("Zero has undefined abundance.");
        }

        if (n == 1) {
            return AbundanceResult{
                .number = 1,
                .sigma = 1,
                .sum_proper = 0,
                .index = 1.0,
                .classification = NumberClass::Deficient
            };
        }

        std::uint64_t temp = n;
        std::uint64_t current_sigma = 1;

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

        if (temp > 1) {
            current_sigma *= (1 + temp);
        }

        const std::uint64_t proper = current_sigma - n;
        const double idx = static_cast<double>(current_sigma) / static_cast<double>(n);

        NumberClass cls = NumberClass::Deficient;
        if (proper == n) {
            cls = NumberClass::Perfect;
        } else if (proper > n) {
            cls = NumberClass::Abundant;
        }

        return AbundanceResult{
            .number = n,
            .sigma = current_sigma,
            .sum_proper = proper,
            .index = idx,
            .classification = cls
        };
    }
};

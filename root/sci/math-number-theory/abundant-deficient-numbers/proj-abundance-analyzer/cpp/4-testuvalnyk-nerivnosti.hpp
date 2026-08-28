#include <cmath>
#include <cstdint>
#include <iostream>
#include <numbers>

class RobinTester {
public:
    static constexpr double EXP_GAMMA = 1.7810724179901979852;

    [[nodiscard]] static bool check(std::uint64_t n, std::uint64_t sigma_n) noexcept {
        if (n <= 5040) return true;

        const double index = static_cast<double>(sigma_n) / static_cast<double>(n);
        const double bound = EXP_GAMMA * std::log(std::log(static_cast<double>(n)));

        return index < bound;
    }
};

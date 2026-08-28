#include <vector>
#include <cstdint>
#include <algorithm>
#include <iostream>

class WeirdNumberDetector {
public:
    [[nodiscard]] static bool is_semiperfect_bitwise(std::uint64_t n, const std::vector<std::uint64_t>& divisors) {
        std::size_t words = (n / 64) + 1;
        std::vector<std::uint64_t> dp(words, 0);
        dp[0] = 1ULL;

        for (std::uint64_t d : divisors) {
            std::size_t word_shift = d / 64;
            std::uint64_t bit_shift = d % 64;

            for (std::size_t w = words; w-- > word_shift; ) {
                std::size_t src = w - word_shift;
                std::uint64_t shifted = dp[src] << bit_shift;
                if (bit_shift > 0 && src > 0) {
                    shifted |= (dp[src - 1] >> (64 - bit_shift));
                }
                dp[w] |= shifted;
            }

            if ((dp[n / 64] & (1ULL << (n % 64))) != 0) {
                return true;
            }
        }

        return (dp[n / 64] & (1ULL << (n % 64))) != 0;
    }

    [[nodiscard]] static bool is_weird(std::uint64_t n) {
        if (n <= 1) return false;

        std::vector<std::uint64_t> divisors;
        std::uint64_t sum_proper = 0;

        for (std::uint64_t d = 1; d * d <= n; ++d) {
            if (n % d == 0) {
                divisors.push_back(d);
                sum_proper += d;

                std::uint64_t paired = n / d;
                if (paired != d && paired != n) {
                    divisors.push_back(paired);
                    sum_proper += paired;
                }
            }
        }

        if (sum_proper <= n) {
            return false;
        }

        std::sort(divisors.begin(), divisors.end());

        return !is_semiperfect_bitwise(n, divisors);
    }
};

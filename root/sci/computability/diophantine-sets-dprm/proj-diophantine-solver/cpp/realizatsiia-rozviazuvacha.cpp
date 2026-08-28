#include <iostream>
#include <vector>
#include <optional>
#include <cmath>
#include <string>
#include <algorithm>

using uint128_t = unsigned __int128;

struct PellPair {
    uint128_t x{0};
    uint128_t y{0};

    [[nodiscard]] std::string to_string_x() const {
        return format_u128(x);
    }
    [[nodiscard]] std::string to_string_y() const {
        return format_u128(y);
    }

private:
    static std::string format_u128(uint128_t val) {
        if (val == 0) return "0";
        std::string s;
        while (val > 0) {
            s.push_back(static_cast<char>('0' + (val % 10)));
            val /= 10;
        }
        std::reverse(s.begin(), s.end());
        return s;
    }
};

class PellSolver {
public:
    static std::optional<PellPair> find_fundamental(uint64_t d) noexcept {
        const auto a0 = static_cast<uint64_t>(std::sqrt(d));
        if (a0 * a0 == d) {
            return std::nullopt; // Повний квадрат не має розв'язків
        }

        uint64_t m = 0;
        uint64_t d_denom = 1;
        uint64_t a = a0;

        uint128_t p_prev2 = 0, p_prev1 = 1, p_curr = a0;
        uint128_t q_prev2 = 1, q_prev1 = 0, q_curr = 1;

        while (true) {
            if (p_curr * p_curr - static_cast<uint128_t>(d) * q_curr * q_curr == 1) {
                return PellPair{p_curr, q_curr};
            }

            m = d_denom * a - m;
            d_denom = (d - m * m) / d_denom;
            a = (a0 + m) / d_denom;

            p_prev2 = p_prev1;
            p_prev1 = p_curr;
            p_curr = static_cast<uint128_t>(a) * p_prev1 + p_prev2;

            q_prev2 = q_prev1;
            q_prev1 = q_curr;
            q_curr = static_cast<uint128_t>(a) * q_prev1 + q_prev2;
        }
    }

    static PellPair next_power(const PellPair& fund, const PellPair& prev, uint64_t d) noexcept {
        return PellPair{
            fund.x * prev.x + static_cast<uint128_t>(d) * fund.y * prev.y,
            fund.y * prev.x + fund.x * prev.y
        };
    }
};

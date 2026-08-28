#include <iostream>
#include <numeric>
#include <optional>
#include <utility>
#include <cstdint>

// Швидке модульне піднесення до степеня
constexpr uint64_t mod_pow(uint64_t base, uint64_t exp, uint64_t mod) noexcept {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            result = static_cast<uint64_t>(static_cast<unsigned __int128>(result) * base % mod);
        }
        base = static_cast<uint64_t>(static_cast<unsigned __int128>(base) * base % mod);
        exp >>= 1;
    }
    return result;
}

// Класичне декодування періоду через неперервні дроби та факторизація
std::optional<std::pair<uint64_t, uint64_t>> factorize_from_phase(
    uint64_t N, uint64_t a, uint64_t y, uint64_t Q) noexcept {
    
    if (y == 0) return std::nullopt;

    uint64_t num = y;
    uint64_t den = Q;

    uint64_t p_prev2 = 0, p_prev1 = 1;
    uint64_t q_prev2 = 1, q_prev1 = 0;

    while (den != 0) {
        const uint64_t a_k = num / den;
        const uint64_t rem = num % den;

        const uint64_t p_curr = a_k * p_prev1 + p_prev2;
        const uint64_t q_curr = a_k * q_prev1 + q_prev2;

        p_prev2 = p_prev1; p_prev1 = p_curr;
        q_prev2 = q_prev1; q_prev1 = q_curr;

        num = den;
        den = rem;

        if (q_curr >= N) break;

        // Перевіряємо q_curr як порядок елемента r
        if (mod_pow(a, q_curr, N) == 1) {
            if (q_curr % 2 == 0) {
                const uint64_t half_pow = mod_pow(a, q_curr / 2, N);
                if (half_pow != N - 1 && half_pow != 1) {
                    const uint64_t factor1 = std::gcd(half_pow - 1, N);
                    const uint64_t factor2 = std::gcd(half_pow + 1, N);

                    if (factor1 > 1 && factor1 < N) {
                        return std::make_pair(factor1, N / factor1);
                    }
                    if (factor2 > 1 && factor2 < N) {
                        return std::make_pair(factor2, N / factor2);
                    }
                }
            }
        }
    }
    return std::nullopt;
}

int main() {
    constexpr uint64_t N = 15;
    constexpr uint64_t a = 7;
    constexpr uint64_t y = 192;
    constexpr uint64_t Q = 256;

    if (const auto factors = factorize_from_phase(N, a, y, Q)) {
        const auto [p, q] = *factors;
        std::cout << "Успіх: " << N << " = " << p << " * " << q << '\n';
    } else {
        std::cout << "Не вдалося знайти дільники з фази.\n";
    }
    return 0;
}

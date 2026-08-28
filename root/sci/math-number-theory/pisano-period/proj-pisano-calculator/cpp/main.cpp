#include <iostream>
#include <vector>
#include <numeric>
#include <array>
#include <cstdint>

/* Таблиця матриць 2x2 для ідіоматичного C++20 з компресією методів */
class Matrix2x2 {
public:
    std::array<std::array<std::uint64_t, 2>, 2> m{{{0, 0}, {0, 0}}};

    static constexpr Matrix2x2 identity() noexcept {
        return Matrix2x2{{{{1, 0}, {0, 1}}}};
    }

    static constexpr Matrix2x2 fibonacci_base() noexcept {
        return Matrix2x2{{{{1, 1}, {1, 0}}}};
    }

    [[nodiscard]] Matrix2x2 multiply(const Matrix2x2& other, std::uint64_t mod) const noexcept {
        Matrix2x2 res;
        for (std::size_t i = 0; i < 2; ++i) {
            for (std::size_t j = 0; j < 2; ++j) {
                std::uint64_t sum = 0;
                for (std::size_t k = 0; k < 2; ++k) {
#if defined(__SIZEOF_INT128__)
                    auto prod = static_cast<std::uint64_t>(
                        (static_cast<unsigned __int128>(m[i][k]) * other.m[k][j]) % mod
                    );
#else
                    std::uint64_t prod = (m[i][k] % mod) * (other.m[k][j] % mod) % mod;
#endif
                    sum = (sum + prod) % mod;
                }
                res.m[i][j] = sum;
            }
        }
        return res;
    }
};

/* Бінарне піднесення до степеня з RAII та константними методами */
[[nodiscard]] Matrix2x2 matrix_power(Matrix2x2 base, std::uint64_t exp, std::uint64_t mod) noexcept {
    Matrix2x2 result = Matrix2x2::identity();
    while (exp > 0) {
        if (exp & 1) {
            result = result.multiply(base, mod);
        }
        base = base.multiply(base, mod);
        exp >>= 1;
    }
    return result;
}

/* Обчислення F_n mod m */
[[nodiscard]] std::uint64_t fibonacci_mod(std::uint64_t n, std::uint64_t mod) noexcept {
    if (n == 0 || mod == 1) return 0;
    const auto Q = Matrix2x2::fibonacci_base();
    const auto R = matrix_power(Q, n - 1, mod);
    return R.m[0][0];
}

/* Знаходження періоду Пізано π(m) через лінійне зациклення */
[[nodiscard]] std::uint64_t pisano_period(std::uint64_t m) noexcept {
    if (m <= 1) return 1;

    std::uint64_t prev = 0;
    std::uint64_t curr = 1;

    const std::uint64_t max_steps = m * 6;
    for (std::uint64_t i = 0; i < max_steps; ++i) {
        std::uint64_t next = (prev + curr) % m;
        prev = curr;
        curr = next;

        if (prev == 0 && curr == 1) {
            return i + 1;
        }
    }
    return 0;
}

int main() {
    constexpr std::uint64_t mod = 1000;
    const std::uint64_t period = pisano_period(mod);

    std::cout << "Pisano period pi(" << mod << ") = " << period << "\n";

    constexpr std::uint64_t n = 1'000'000'000'000'000'000ULL; // 10^18
    const std::uint64_t n_reduced = n % period;
    const std::uint64_t fn = fibonacci_mod(n_reduced, mod);

    std::cout << "F(10^18) mod " << mod << " = " << fn << "\n";
    return 0;
}

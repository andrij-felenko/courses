#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <expected>
#include <numeric>
#include <span>

namespace math::number_theory {

using Complex = std::complex<double>;

class JacobiSumCalculator {
public:
    enum class Error {
        InvalidModulus,
        NotPrime,
        DegreeDoesNotDivideOrder
    };

    explicit JacobiSumCalculator(uint64_t prime_modulus)
        : p_(prime_modulus), g_(find_primitive_root(prime_modulus)) {
        build_log_table();
    }

    [[nodiscard]] Complex compute_jacobi_sum(uint64_t a, uint64_t b) const {
        Complex sum{0.0, 0.0};
        for (uint64_t t = 0; t < p_; ++t) {
            uint64_t t2 = (p_ + 1 - (t % p_)) % p_;
            sum += eval_character(t, a) * eval_character(t2, b);
        }
        return sum;
    }

    [[nodiscard]] std::expected<uint64_t, Error> count_fermat_points(uint64_t n) const {
        uint64_t phi = p_ - 1;
        if (phi % n != 0) {
            return std::unexpected(Error::DegreeDoesNotDivideOrder);
        }

        uint64_t step = phi / n;
        Complex total_sum{0.0, 0.0};

        for (uint64_t i = 1; i < n; ++i) {
            for (uint64_t j = 1; j < n; ++j) {
                total_sum += compute_jacobi_sum(i * step, j * step);
            }
        }

        double real_val = total_sum.real();
        return static_cast<uint64_t>(p_ + std::round(real_val));
    }

    [[nodiscard]] uint64_t modulus() const noexcept { return p_; }
    [[nodiscard]] uint64_t primitive_root() const noexcept { return g_; }

private:
    uint64_t p_;
    uint64_t g_;
    std::vector<int64_t> log_table_;

    static uint64_t power_mod(uint64_t base, uint64_t exp, uint64_t mod) {
        uint64_t res = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) res = (res * base) % mod;
            base = (base * base) % mod;
            exp >>= 1;
        }
        return res;
    }

    static bool is_primitive_root(uint64_t g, uint64_t p) {
        uint64_t phi = p - 1;
        uint64_t n = phi;
        for (uint64_t i = 2; i * i <= n; ++i) {
            if (n % i == 0) {
                if (power_mod(g, phi / i, p) == 1) return false;
                while (n % i == 0) n /= i;
            }
        }
        if (n > 1 && power_mod(g, phi / n, p) == 1) return false;
        return true;
    }

    static uint64_t find_primitive_root(uint64_t p) {
        for (uint64_t g = 2; g < p; ++g) {
            if (is_primitive_root(g, p)) return g;
        }
        return 2;
    }

    void build_log_table() {
        log_table_.assign(p_, -1);
        uint64_t cur = 1;
        for (uint64_t exp = 0; exp < p_ - 1; ++exp) {
            log_table_[cur] = static_cast<int64_t>(exp);
            cur = (cur * g_) % p_;
        }
    }

    [[nodiscard]] Complex eval_character(uint64_t x, uint64_t k) const {
        if (x == 0 || log_table_[x] == -1) return {0.0, 0.0};
        double angle = 2.0 * std::numbers::pi * static_cast<double>(k * log_table_[x]) / static_cast<double>(p_ - 1);
        return std::polar(1.0, angle);
    }
};

} // namespace math::number_theory

int main() {
    using namespace math::number_theory;

    uint64_t p = 13;
    uint64_t n = 4;

    JacobiSumCalculator calc(p);
    std::cout << "Поле F_" << calc.modulus() << ", первісний корінь g = " << calc.primitive_root() << "\n";

    auto j11 = calc.compute_jacobi_sum(3, 3);
    std::cout << "Сума Якобі J(χ³, χ³) = " << j11.real() << " + " << j11.imag() << "i\n";
    std::cout << "Модуль |J| = " << std::abs(j11) << " (Очікується √13 ≈ " << std::sqrt(p) << ")\n";

    auto points = calc.count_fermat_points(n);
    if (points) {
        std::cout << "Кількість точок на x^" << n << " + y^" << n << " = 1 (mod " << p << ") дорівнює: " << *points << "\n";
    }

    return 0;
}

#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numeric>
#include <numbers>
#include <iomanip>

class DirichletLCalculator {
public:
    using Complex = std::complex<double>;

    explicit DirichletLCalculator(int modulus) : p_(modulus) {
        g_ = find_primitive_root(p_);
        build_discrete_log_table();
    }

    [[nodiscard]] Complex eval_l_function(int char_index, Complex s, std::size_t max_terms) const {
        Complex sum{0.0, 0.0};
        const double phi_p = p_ - 1;

        for (std::size_t n = 1; n <= max_terms; ++n) {
            int rem = static_cast<int>(n % p_);
            if (rem == 0 || std::gcd(rem, p_) > 1) {
                continue;
            }

            int k = log_table_[rem];
            double angle = 2.0 * std::numbers::pi * char_index * k / phi_p;
            Complex chi_val = std::polar(1.0, angle);

            Complex n_minus_s = std::pow(static_cast<double>(n), -s);
            sum += chi_val * n_minus_s;
        }
        return sum;
    }

    [[nodiscard]] int modulus() const noexcept { return p_; }
    [[nodiscard]] int primitive_root() const noexcept { return g_; }

private:
    int p_;
    int g_;
    std::vector<int> log_table_;

    static int find_primitive_root(int p) {
        if (p == 2) return 1;
        int phi = p - 1;
        std::vector<int> factors;
        int n = phi;
        for (int i = 2; i * i <= n; ++i) {
            if (n % i == 0) {
                factors.push_back(i);
                while (n % i == 0) n /= i;
            }
        }
        if (n > 1) factors.push_back(n);

        for (int res = 2; res < p; ++res) {
            bool ok = true;
            for (int f : factors) {
                if (power_mod(res, phi / f, p) == 1) {
                    ok = false;
                    break;
                }
            }
            if (ok) return res;
        }
        return -1;
    }

    static long long power_mod(long long base, long long exp, long long mod) {
        long long res = 1;
        base %= mod;
        while (exp > 0) {
            if (exp % 2 == 1) res = (res * base) % mod;
            base = (base * base) % mod;
            exp /= 2;
        }
        return res;
    }

    void build_discrete_log_table() {
        log_table_.assign(p_, -1);
        long long cur = 1;
        for (int k = 0; k < p_ - 1; ++k) {
            log_table_[cur] = k;
            cur = (cur * g_) % p_;
        }
    }
};

int main() {
    constexpr int modulus = 5;
    DirichletLCalculator calc(modulus);

    std::cout << "Модуль p = " << calc.modulus() 
              << ", Первісний корінь g = " << calc.primitive_root() << "\n\n";

    const std::complex<double> s_eval{1.0, 0.0};
    constexpr std::size_t N_terms = 100000;

    std::cout << std::fixed << std::setprecision(6);
    for (int m = 0; m < modulus - 1; ++m) {
        auto l_val = calc.eval_l_function(m, s_eval, N_terms);
        std::cout << "Характер chi_" << m << ": L(1, chi) = " 
                  << l_val.real() << " + " << l_val.imag() << "i"
                  << " (модуль = " << std::abs(l_val) << ")\n";
    }

    return 0;
}

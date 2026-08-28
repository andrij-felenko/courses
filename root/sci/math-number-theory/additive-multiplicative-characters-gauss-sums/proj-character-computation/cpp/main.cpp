#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numeric>
#include <stdexcept>
#include <numbers>
#include <iomanip>

class DirichletCharacterSystem {
public:
    explicit DirichletCharacterSystem(int p) : p_(p) {
        if (p <= 1) {
            throw std::invalid_argument("Modulus must be prime > 1");
        }
        g_ = find_primitive_root(p);
        dlog_.resize(p, 0);

        // Побудова таблиці дискретного логарифмування за O(p)
        long long val = 1;
        for (int k = 0; k < p - 1; ++k) {
            dlog_[val] = k;
            val = (val * g_) % p;
        }
    }

    [[nodiscard]] int modulus() const noexcept { return p_; }
    [[nodiscard]] int generator() const noexcept { return g_; }

    // Обчислення значення характера χ_m(n)
    [[nodiscard]] std::complex<double> eval(int m, int n) const noexcept {
        if (n % p_ == 0) return {0.0, 0.0};
        int k = dlog_[n % p_];
        double angle = 2.0 * std::numbers::pi * m * k / (p_ - 1);
        return std::polar(1.0, angle);
    }

    // Обчислення суми Ґаусса g(χ_m)
    [[nodiscard]] std::complex<double> gauss_sum(int m) const noexcept {
        std::complex<double> sum{0.0, 0.0};
        for (int x = 1; x < p_; ++x) {
            auto chi_val = eval(m, x);
            double add_angle = 2.0 * std::numbers::pi * x / p_;
            auto add_val = std::polar(1.0, add_angle);
            sum += chi_val * add_val;
        }
        return sum;
    }

    // Перевірка ортогональності характерів
    [[nodiscard]] bool verify_orthogonality() const noexcept {
        int phi = p_ - 1;
        constexpr double eps = 1e-7;
        for (int i = 0; i < phi; ++i) {
            for (int j = 0; j < phi; ++j) {
                std::complex<double> dot{0.0, 0.0};
                for (int x = 1; x < p_; ++x) {
                    dot += eval(i, x) * std::conj(eval(j, x));
                }
                double expected = (i == j) ? static_cast<double>(phi) : 0.0;
                if (std::abs(dot - expected) > eps) return false;
            }
        }
        return true;
    }

private:
    int p_;
    int g_;
    std::vector<int> dlog_;

    static long long power_mod(long long base, long long exp, long long mod) noexcept {
        long long res = 1;
        base %= mod;
        while (exp > 0) {
            if (exp % 2 == 1) res = (res * base) % mod;
            base = (base * base) % mod;
            exp /= 2;
        }
        return res;
    }

    static int find_primitive_root(int p) {
        if (p == 2) return 1;
        int phi = p - 1;
        int n = phi;
        std::vector<int> prime_factors;

        for (int i = 2; i * i <= n; ++i) {
            if (n % i == 0) {
                prime_factors.push_back(i);
                while (n % i == 0) n /= i;
            }
        }
        if (n > 1) prime_factors.push_back(n);

        for (int g = 2; g < p; ++g) {
            bool ok = true;
            for (int factor : prime_factors) {
                if (power_mod(g, phi / factor, p) == 1) {
                    ok = false;
                    break;
                }
            }
            if (ok) return g;
        }
        return -1;
    }
};

int main() {
    constexpr int p = 7;
    try {
        DirichletCharacterSystem sys(p);

        std::cout << "=== [C++] Модуль p = " << sys.modulus() 
                  << ", Первісний корінь g = " << sys.generator() << " ===\n\n";

        std::cout << "Суми Ґаусса та перевірка модулів |g(χ)|:\n";
        for (int m = 0; m < sys.modulus() - 1; ++m) {
            auto g_sum = sys.gauss_sum(m);
            double mod = std::abs(g_sum);
            std::cout << std::format("g(χ_{}) = {:+.3f} {:+.3fi} | |g| = {:.4f} (теоретично: {:.4f})\n",
                                     m, g_sum.real(), g_sum.imag(), mod, std::sqrt(p));
        }

        bool ok = sys.verify_orthogonality();
        std::cout << "\nОртогональність характерів: " << (ok ? "ПРОЙДЕНО" : "ПОМИЛКА") << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << "\n";
        return 1;
    }

    return 0;
}

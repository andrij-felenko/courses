#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <iomanip>
#include <numeric>
#include <numbers>

class GaussSumCalculator {
public:
    using Complex = std::complex<double>;

    // Швидке піднесення до степеня за модулем з використанням __int128 проти переповнення
    static long long mod_pow(long long base, long long exp, long long mod) {
        long long result = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) result = static_cast<long long>((static_cast<__int128>(result) * base) % mod);
            base = static_cast<long long>((static_cast<__int128>(base) * base) % mod);
            exp >>= 1;
        }
        return result;
    }

    // Обчислення символу Лежандра (a/p)
    static int legendre_symbol(long long a, long long p) {
        a = (a % p + p) % p;
        if (a == 0) return 0;
        long long res = mod_pow(a, (p - 1) / 2, p);
        return (res == 1) ? 1 : -1;
    }

    // Алгоритм пошуку первісного кореня за модулем p
    static long long find_primitive_root(long long p) {
        if (p == 2) return 1;
        long long phi = p - 1;
        std::vector<long long> factors;
        long long n = phi;
        for (long long i = 2; i * i <= n; ++i) {
            if (n % i == 0) {
                factors.push_back(i);
                while (n % i == 0) n /= i;
            }
        }
        if (n > 1) factors.push_back(n);

        for (long long res = 2; res < p; ++res) {
            bool ok = true;
            for (long long factor : factors) {
                if (mod_pow(res, phi / factor, p) == 1) {
                    ok = false;
                    break;
                }
            }
            if (ok) return res;
        }
        return -1;
    }

    // 1. Обчислення квадратичної суми Гаусса g(1, p)
    static Complex quadratic_gauss_sum(long long p) {
        Complex sum{0.0, 0.0};
        const double angle_step = 2.0 * std::numbers::pi / static_cast<double>(p);
        for (long long n = 0; n < p; ++n) {
            long long k = (n * n) % p;
            double angle = angle_step * static_cast<double>(k);
            sum += std::polar(1.0, angle);
        }
        return sum;
    }

    // 2. Обчислення загальної суми Гаусса g(chi_m) для характеру m-го степеня
    static Complex general_gauss_sum(long long p, long long character_index) {
        long long g = find_primitive_root(p);
        if (g == -1) return {0.0, 0.0};

        // Таблиця дискретних логарифмів ind_g(a)
        std::vector<long long> log_table(p, 0);
        long long cur = 1;
        for (long long exp = 0; exp < p - 1; ++exp) {
            log_table[cur] = exp;
            cur = (cur * g) % p;
        }

        Complex sum{0.0, 0.0};
        const double angle_step_add = 2.0 * std::numbers::pi / static_cast<double>(p);
        const double angle_step_mult = 2.0 * std::numbers::pi / static_cast<double>(p - 1);

        for (long long a = 1; a < p; ++a) {
            long long k = log_table[a];
            double mult_angle = angle_step_mult * static_cast<double>((character_index * k) % (p - 1));
            double add_angle = angle_step_add * static_cast<double>(a);
            
            Complex chi_a = std::polar(1.0, mult_angle);
            Complex psi_a = std::polar(1.0, add_angle);
            sum += chi_a * psi_a;
        }
        return sum;
    }

    // 3. Обчислення суми Якобі J(chi_m1, chi_m2)
    static Complex jacobi_sum(long long p, long long m1, long long m2) {
        long long g = find_primitive_root(p);
        std::vector<long long> log_table(p, 0);
        long long cur = 1;
        for (long long exp = 0; exp < p - 1; ++exp) {
            log_table[cur] = exp;
            cur = (cur * g) % p;
        }

        Complex sum{0.0, 0.0};
        const double angle_step = 2.0 * std::numbers::pi / static_cast<double>(p - 1);

        for (long long a = 0; a < p; ++a) {
            long long b = (1 - a + p) % p;
            if (a == 0 || b == 0) continue;

            double angle1 = angle_step * static_cast<double>((m1 * log_table[a]) % (p - 1));
            double angle2 = angle_step * static_cast<double>((m2 * log_table[b]) % (p - 1));

            Complex chi1_a = std::polar(1.0, angle1);
            Complex chi2_b = std::polar(1.0, angle2);

            sum += chi1_a * chi2_b;
        }
        return sum;
    }
};

int main() {
    std::cout << std::fixed << std::setprecision(5);
    std::cout << "=== Обчислення сум Гаусса та Якобі (Мова C++20) ===\n\n";

    const std::vector<long long> primes = {5, 7, 13, 17, 19, 23, 29, 31};

    std::cout << "1. Верифікація закону знаку Гаусса g(1, p):\n";
    std::cout << std::setw(6) << "p" << std::setw(10) << "p mod 4" 
              << std::setw(22) << "g(1, p)" << std::setw(14) << "|g(1, p)|" 
              << std::setw(14) << "sqrt(p)" << "\n";
    std::cout << std::string(66, '-') << "\n";

    for (long long p : primes) {
        auto g = GaussSumCalculator::quadratic_gauss_sum(p);
        double mod_g = std::abs(g);
        double expected = std::sqrt(static_cast<double>(p));

        std::cout << std::setw(6) << p << std::setw(10) << (p % 4)
                  << std::setw(12) << g.real() << (g.imag() >= 0 ? " +" : " ") 
                  << std::setw(8) << g.imag() << "i"
                  << std::setw(14) << mod_g << std::setw(14) << expected << "\n";
    }

    std::cout << "\n2. Перевірка тотожності Якобі-Гаусса J(chi, chi) * g(chi^2) = g(chi)^2 для p = 13:\n";
    long long p = 13;
    long long m = 3; // Характер 3-го степеня mod 12

    auto g_chi = GaussSumCalculator::general_gauss_sum(p, m);
    auto g_chi2 = GaussSumCalculator::general_gauss_sum(p, (2 * m) % (p - 1));
    auto j_chi_chi = GaussSumCalculator::jacobi_sum(p, m, m);

    auto lhs = j_chi_chi * g_chi2;
    auto rhs = g_chi * g_chi;

    std::cout << "  g(chi)        = " << g_chi << "\n";
    std::cout << "  g(chi)^2      = " << rhs << "\n";
    std::cout << "  J(chi, chi)   = " << j_chi_chi << "\n";
    std::cout << "  g(chi^2)      = " << g_chi2 << "\n";
    std::cout << "  J * g(chi^2)  = " << lhs << "\n";
    std::cout << "  Різниця |LHS - RHS| = " << std::abs(lhs - rhs) << " (очікується 0)\n";

    return 0;
}

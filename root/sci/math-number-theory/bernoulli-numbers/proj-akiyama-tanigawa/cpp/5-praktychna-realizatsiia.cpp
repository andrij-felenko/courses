#include <iostream>
#include <vector>
#include <numeric>
#include <cmath>
#include <iomanip>
#include <numeric>

// Канонічний клас точного раціонального числа
class Rational {
public:
    int64_t num;
    int64_t den;

    Rational(int64_t n = 0, int64_t d = 1) : num(n), den(d) {
        reduce();
    }

    void reduce() {
        if (den == 0) {
            throw std::invalid_argument("Ділення на нуль у раціональній арифметиці");
        }
        if (den < 0) {
            num = -num;
            den = -den;
        }
        int64_t g = std::gcd(std::abs(num), den);
        num /= g;
        den /= g;
    }

    Rational operator-(const Rational& other) const {
        int64_t g = std::gcd(den, other.den);
        int64_t common_den = (den / g) * other.den;
        int64_t common_num = num * (other.den / g) - other.num * (den / g);
        return Rational(common_num, common_den);
    }

    Rational operator*(int64_t scalar) const {
        int64_t g = std::gcd(scalar, den);
        return Rational(num * (scalar / g), den / g);
    }
};

// Обчислення чисел Бернуллі за алгоритмом Акіями — Таніґави
std::vector<Rational> compute_bernoulli_cpp(int n) {
    std::vector<Rational> B(n + 1);
    std::vector<Rational> A(n + 1);

    for (int j = 0; j <= n; ++j) {
        A[j] = Rational(1, j + 1);
    }

    B[0] = A[0];

    for (int i = 1; i <= n; ++i) {
        for (int j = 0; j <= n - i; ++j) {
            A[j] = (A[j] - A[j + 1]) * (j + 1);
        }
        if (i == 1) {
            B[1] = Rational(-A[0].num, A[0].den);
        } else {
            B[i] = A[0];
        }
    }

    return B;
}

int main() {
    constexpr int max_n = 14;
    try {
        std::vector<Rational> B = compute_bernoulli_cpp(max_n);

        std::cout << "=== Обчислення чисел Бернуллі B_0 .. B_" << max_n << " (Мова C++) ===\n\n";
        for (int i = 0; i <= max_n; ++i) {
            std::cout << "B_" << std::left << std::setw(2) << i << " = "
                      << std::right << std::setw(12) << B[i].num << " / "
                      << std::left << std::setw(8) << B[i].den;
            if (B[i].num != 0) {
                std::cout << "  (≈ " << std::showpos << std::fixed << std::setprecision(10)
                          << static_cast<double>(B[i].num) / B[i].den << ")\n" << std::noshowpos;
            } else {
                std::cout << "  (  0.0000000000)\n";
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << '\n';
        return 1;
    }
    return 0;
}

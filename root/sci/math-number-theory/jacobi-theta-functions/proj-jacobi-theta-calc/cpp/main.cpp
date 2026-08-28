#include <iostream>
#include <cmath>
#include <vector>
#include <numbers>
#include <iomanip>
#include <stdexcept>

class JacobiThetaCalculator {
public:
    static constexpr double default_eps = 1e-15;

    // Обчислення theta3(q) з використанням модулярного перетворення Якобі
    static double theta3(double q, double eps = default_eps) {
        if (q < 0.0 || q >= 1.0) {
            throw std::invalid_argument("Параметр q повинен належати [0, 1)");
        }
        if (q == 0.0) return 1.0;

        // Модулярна редукція при q > 0.6
        if (q > 0.6) {
            const double t = -std::log(q) / std::numbers::pi;
            const double q_prime = std::exp(-std::numbers::pi / t);
            const double theta_prime = theta3_direct(q_prime, eps);
            return (1.0 / std::sqrt(t)) * theta_prime;
        }

        return theta3_direct(q, eps);
    }

    // Обчислення повного еліптичного інтеграла K(k) через AGM
    static double elliptic_K(double k, double eps = default_eps) {
        if (k < 0.0 || k >= 1.0) {
            throw std::invalid_argument("Модуль k повинен належати [0, 1)");
        }

        double a = 1.0;
        double b = std::sqrt(1.0 - k * k);

        while (std::abs(a - b) > eps) {
            const double a_next = 0.5 * (a + b);
            const double b_next = std::sqrt(a * b);
            a = a_next;
            b = b_next;
        }

        return std::numbers::pi / (2.0 * a);
    }

private:
    static double theta3_direct(double q, double eps) {
        double sum = 1.0;
        double term = 0.0;
        int n = 1;

        do {
            term = 2.0 * std::pow(q, static_cast<double>(n * n));
            sum += term;
            ++n;
        } while (term > eps && n < 1000);

        return sum;
    }
};

int main() {
    try {
        const std::vector<double> test_q = {0.1, 0.5, 0.9, 0.999, 0.99999};

        std::cout << std::fixed << std::setprecision(12);
        std::cout << "=== Обчислення theta3(q) (C++) ===\n";
        for (double q : test_q) {
            double val = JacobiThetaCalculator::theta3(q);
            std::cout << "q = " << std::setw(8) << q << " | theta3(q) = " << val << '\n';
        }

        std::cout << "\n=== Обчислення K(k) через AGM (C++) ===\n";
        double k = 0.5;
        double K_val = JacobiThetaCalculator::elliptic_K(k);
        std::cout << "k = " << k << " | K(k) = " << K_val << '\n';
    } 
    catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}

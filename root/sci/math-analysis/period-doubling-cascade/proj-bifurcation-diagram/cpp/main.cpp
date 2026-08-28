#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>

class FeigenbaumCalculator {
public:
    static double logistic(double x, double r) {
        return r * x * (1.0 - x);
    }

    static double logistic_derivative_r(double x, double r, double w) {
        return r * (1.0 - 2.0 * x) * w + x * (1.0 - x);
    }

    static double find_superstable_r(int n, double r_guess) {
        int period = 1 << n; // 2^n
        double r = r_guess;

        for (int iter = 0; iter < 100; ++iter) {
            double x = 0.5;
            double w = 0.0; // dx/dr

            for (int k = 0; k < period; ++k) {
                w = logistic_derivative_r(x, r, w);
                x = logistic(x, r);
            }

            double f_val = x - 0.5;
            double f_prime = w;

            if (std::abs(f_val) < 1e-13) {
                break;
            }

            r = r - f_val / f_prime;
        }

        return r;
    }

    static double calculate_lyapunov(double r, int num_iters = 50000) {
        double x = 0.5;
        // Transient cutoff
        for (int i = 0; i < 1000; ++i) {
            x = logistic(x, r);
        }

        double sum_log = 0.0;
        for (int i = 0; i < num_iters; ++i) {
            double deriv = std::abs(r * (1.0 - 2.0 * x));
            if (deriv < 1e-12) deriv = 1e-12;
            sum_log += std::log(deriv);
            x = logistic(x, r);
        }

        return sum_log / num_iters;
    }
};

int main() {
    std::cout << std::setprecision(12);
    std::cout << "=== Обчислення надстійких точок та сталих Фейгенбаума ===\n";

    std::vector<double> guesses = {2.0, 3.2, 3.498, 3.5546, 3.56666, 3.56924};
    std::vector<double> R_vals;

    for (size_t i = 0; i < guesses.size(); ++i) {
        double R = FeigenbaumCalculator::find_superstable_r(i, guesses[i]);
        R_vals.push_back(R);
        std::cout << "R_" << i << " = " << R << "\n";
    }

    std::cout << "\n=== Обчислення сталої delta ===\n";
    for (size_t i = 1; i + 1 < R_vals.size(); ++i) {
        double delta = (R_vals[i] - R_vals[i-1]) / (R_vals[i+1] - R_vals[i]);
        std::cout << "delta_" << i << " = " << delta << "\n";
    }

    return 0;
}

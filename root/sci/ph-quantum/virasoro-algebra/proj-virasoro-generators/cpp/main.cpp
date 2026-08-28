#include <iostream>
#include <vector>
#include <cmath>
#include <expected>
#include <string_view>

class VirasoroEvaluator {
private:
    double central_charge_;

public:
    explicit VirasoroEvaluator(double c) noexcept : central_charge_(c) {}

    [[nodiscard]] double central_term(int n, int m) const noexcept {
        if (n + m != 0) return 0.0;
        return (central_charge_ / 12.0) * static_cast<double>(n * n * n - n);
    }

    [[nodiscard]] bool verify_jacobi(int k, int m, int n) const noexcept {
        const double t1 = static_cast<double>(m - n) * central_term(k, m + n);
        const double t2 = static_cast<double>(n - k) * central_term(m, n + k);
        const double t3 = static_cast<double>(k - m) * central_term(n, k + m);
        return std::abs(t1 + t2 + t3) < 1e-9;
    }

    [[nodiscard]] static constexpr double kac_det_level2(double c, double h) noexcept {
        const double m11 = 4.0 * h + c / 2.0;
        const double m12 = 6.0 * h;
        const double m21 = 6.0 * h;
        const double m22 = 4.0 * h * (2.0 * h + 1.0);
        return (m11 * m22) - (m12 * m21);
    }
};

int main() {
    constexpr double c_bosonic_string = 26.0;
    VirasoroEvaluator vir(c_bosonic_string);

    std::cout << "C++ verification of Virasoro Algebra\n";
    std::cout << "Jacobi identity check (5, -8, 3): "
              << (vir.verify_jacobi(5, -8, 3) ? "PASSED" : "FAILED") << '\n';

    constexpr double c_ising = 0.5;
    constexpr double h_sigma = 1.0 / 16.0;
    constexpr double det2 = VirasoroEvaluator::kac_det_level2(c_ising, h_sigma);
    std::cout << "Kac determinant N=2 (Ising c=1/2, h=1/16): " << det2 << '\n';

    return 0;
}

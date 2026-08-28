#include <iostream>
#include <complex>
#include <cmath>
#include <numbers>
#include <iomanip>

int main() {
    constexpr std::uint64_t p = 7;
    constexpr std::size_t m = 3;
    using Complex = std::complex<double>;

    auto dlog = [&](std::uint64_t x) -> std::int64_t {
        if (x % p == 0) return -1;
        std::uint64_t curr = 1;
        for (std::uint64_t k = 0; k < p - 1; ++k) {
            if (curr == x % p) return static_cast<std::int64_t>(k);
            curr = (curr * 3) % p;
        }
        return 0;
    };

    auto psi = [&](std::uint64_t x) -> Complex {
        return std::polar(1.0, 2.0 * std::numbers::pi * static_cast<double>(x % p) / static_cast<double>(p));
    };

    // LHS computation
    Complex lhs{1.0, 0.0};
    for (std::size_t a = 0; a < m; ++a) {
        Complex g_shift{0.0, 0.0};
        for (std::uint64_t x = 1; x < p; ++x) {
            const auto k = dlog(x);
            const Complex chi_val = std::polar(1.0, 2.0 * std::numbers::pi * static_cast<double>(k) / 6.0);
            const Complex theta_val = std::polar(1.0, 2.0 * std::numbers::pi * static_cast<double>((k * a) % 3) / 3.0);
            g_shift += chi_val * theta_val * psi(x);
        }
        lhs *= g_shift;
    }

    // RHS computation
    const auto k6 = dlog(6);
    const Complex chi_m_inv = std::polar(1.0, 2.0 * std::numbers::pi * static_cast<double>(k6) / 6.0);

    Complex g_chi3{0.0, 0.0};
    for (std::uint64_t x = 1; x < p; ++x) {
        const auto k = dlog(x);
        const Complex chi3_val = std::polar(1.0, 2.0 * std::numbers::pi * static_cast<double>((k * 3) % 6) / 6.0);
        g_chi3 += chi3_val * psi(x);
    }

    Complex prod_theta{1.0, 0.0};
    for (std::size_t a = 1; a < m; ++a) {
        Complex g_th{0.0, 0.0};
        for (std::uint64_t x = 1; x < p; ++x) {
            const auto k = dlog(x);
            const Complex th_val = std::polar(1.0, 2.0 * std::numbers::pi * static_cast<double>((k * a) % 3) / 3.0);
            g_th += th_val * psi(x);
        }
        prod_theta *= g_th;
    }

    const Complex rhs = chi_m_inv * g_chi3 * prod_theta;
    const double diff = std::abs(lhs - rhs);

    std::cout << std::fixed << std::setprecision(5);
    std::cout << "C++ Multiplicative LHS = " << lhs << "\n";
    std::cout << "C++ Multiplicative RHS = " << rhs << "\n";
    std::cout << "C++ Diff = " << std::scientific << std::setprecision(9) << diff << "\n";

    return 0;
}

#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <numeric>
#include <iomanip>

class DavenportHasseVerifier {
public:
    using Complex = std::complex<double>;

    explicit DavenportHasseVerifier(std::uint64_t prime = 7, std::size_t ext_deg = 2)
        : p_(prime), s_(ext_deg), g_gen_(3) {}

    void execute_verification() const {
        // 1. Обчислюємо базову суму Гаусса у F_p
        const Complex g_small = compute_base_gauss_sum();
        
        std::cout << std::fixed << std::setprecision(5);
        std::cout << "C++ [F_" << p_ << "] Base Gauss sum g(χ, ψ) = " << g_small << "\n";
        std::cout << "C++ [F_" << p_ << "] Modulus |g| = " << std::abs(g_small) 
                  << " (Expected √" << p_ << " = " << std::sqrt(p_) << ")\n\n";

        // 2. Обчислюємо підняту суму у F_{p^s}
        const Complex g_lifted = compute_lifted_gauss_sum();
        std::cout << "C++ [F_" << (p_ * p_) << "] Lifted Gauss sum g(χ', ψ') = " << g_lifted << "\n";
        std::cout << "C++ [F_" << (p_ * p_) << "] Modulus |g_lifted| = " << std::abs(g_lifted) 
                  << " (Expected " << p_ << ")\n\n";

        // 3. Порівнюємо з підйомом (-1)^(s-1) * (g_small)^s
        const double sign_factor = ((s_ - 1) % 2 == 0) ? 1.0 : -1.0;
        const Complex predicted = sign_factor * std::pow(g_small, static_cast<double>(s_));

        const double diff = std::abs(g_lifted - predicted);
        std::cout << "C++ Predicted (-1)^(s-1) * g^s = " << predicted << "\n";
        std::cout << "C++ Diff = " << std::scientific << std::setprecision(9) << diff << "\n";

        if (diff < 1e-7) {
            std::cout << "C++ STATUS: Davenport-Hasse Relation Verified Successfully!\n";
        } else {
            std::cout << "C++ STATUS: Verification Failed!\n";
        }
    }

private:
    std::uint64_t p_;
    std::size_t s_;
    std::uint64_t g_gen_;

    [[nodiscard]] std::int64_t discrete_log(std::uint64_t x) const noexcept {
        if (x % p_ == 0) return -1;
        std::uint64_t curr = 1;
        for (std::uint64_t k = 0; k < p_ - 1; ++k) {
            if (curr == x % p_) return static_cast<std::int64_t>(k);
            curr = (curr * g_gen_) % p_;
        }
        return 0;
    }

    [[nodiscard]] Complex chi_base(std::uint64_t x) const noexcept {
        if (x % p_ == 0) return {0.0, 0.0};
        const auto k = discrete_log(x);
        const double angle = 2.0 * std::numbers::pi * static_cast<double>(k % 3) / 3.0;
        return std::polar(1.0, angle);
    }

    [[nodiscard]] Complex psi_base(std::uint64_t x) const noexcept {
        const double angle = 2.0 * std::numbers::pi * static_cast<double>(x % p_) / static_cast<double>(p_);
        return std::polar(1.0, angle);
    }

    [[nodiscard]] Complex compute_base_gauss_sum() const noexcept {
        Complex sum{0.0, 0.0};
        for (std::uint64_t x = 1; x < p_; ++x) {
            sum += chi_base(x) * psi_base(x);
        }
        return sum;
    }

    [[nodiscard]] Complex compute_lifted_gauss_sum() const noexcept {
        Complex sum{0.0, 0.0};
        for (std::uint64_t u = 0; u < p_; ++u) {
            for (std::uint64_t v = 0; v < p_; ++v) {
                if (u == 0 && v == 0) continue;
                const std::uint64_t norm_val = (u * u + v * v) % p_;
                const std::uint64_t trace_val = (2 * u) % p_;
                sum += chi_base(norm_val) * psi_base(trace_val);
            }
        }
        return sum;
    }
};

int main() {
    const DavenportHasseVerifier verifier(7, 2);
    verifier.execute_verification();
    return 0;
}

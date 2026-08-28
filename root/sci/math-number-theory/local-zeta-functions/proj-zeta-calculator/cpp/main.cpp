#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numeric>
#include <iomanip>
#include <expected>

namespace math::number_theory {

struct LocalZetaData {
    std::uint64_t p;
    std::int64_t a;
    std::uint64_t N1;
    std::complex<double> alpha1;
    std::complex<double> alpha2;
    bool hasse_satisfied;

    [[nodiscard]] std::uint64_t points_over_extension(std::size_t n) const noexcept {
        if (n == 1) return N1;

        std::int64_t s_prev2 = 2; // S_0
        std::int64_t s_prev1 = a; // S_1
        std::int64_t s_curr = s_prev1;

        for (std::size_t i = 2; i <= n; ++i) {
            s_curr = a * s_prev1 - static_cast<std::int64_t>(p) * s_prev2;
            s_prev2 = s_prev1;
            s_prev1 = s_curr;
        }

        std::uint64_t p_pow = 1;
        for (std::size_t i = 0; i < n; ++i) {
            p_pow *= p;
        }

        return p_pow + 1 - static_cast<std::uint64_t>(s_curr);
    }
};

enum class CurveError {
    InvalidPrime,
    SingularCurve
};

class EllipticCurveZeta {
private:
    std::uint64_t m_A;
    std::uint64_t m_B;
    std::uint64_t m_p;

    [[nodiscard]] static int legendre_symbol(std::uint64_t val, std::uint64_t p) noexcept {
        val %= p;
        if (val == 0) return 0;

        std::uint64_t res = 1;
        std::uint64_t base = val;
        std::uint64_t exp = (p - 1) / 2;

        while (exp > 0) {
            if (exp & 1) {
                res = static_cast<unsigned __int128>(res) * base % p;
            }
            base = static_cast<unsigned __int128>(base) * base % p;
            exp >>= 1;
        }

        return (res == 1) ? 1 : -1;
    }

public:
    constexpr EllipticCurveZeta(std::uint64_t A, std::uint64_t B, std::uint64_t p) noexcept
        : m_A(A), m_B(B), m_p(p) {}

    [[nodiscard]] std::expected<LocalZetaData, CurveError> analyze() const noexcept {
        if (m_p < 2) return std::unexpected(CurveError::InvalidPrime);
        
        // Перевірка дискримінанта 4A^3 + 27B^2 != 0 mod p (гладкість)
        unsigned __int128 disc_val = (4 * static_cast<unsigned __int128>(m_A) * m_A % m_p * m_A +
                                      27 * static_cast<unsigned __int128>(m_B) * m_B) % m_p;
        if (disc_val == 0) return std::unexpected(CurveError::SingularCurve);

        std::uint64_t affine_points = 0;
        for (std::uint64_t x = 0; x < m_p; ++x) {
            std::uint64_t rhs = (static_cast<unsigned __int128>(x) * x % m_p * x + m_A * x + m_B) % m_p;
            int leg = legendre_symbol(rhs, m_p);
            affine_points += static_cast<std::uint64_t>(1 + leg);
        }

        std::uint64_t N1 = affine_points + 1; // + non-affine point at infinity
        std::int64_t trace_a = static_cast<std::int64_t>(m_p + 1) - static_cast<std::int64_t>(N1);

        double bound = 2.0 * std::sqrt(static_cast<double>(m_p));
        bool hasse_ok = std::abs(trace_a) <= std::floor(bound);

        double re = static_cast<double>(trace_a) / 2.0;
        double disc_complex = 4.0 * static_cast<double>(m_p) - static_cast<double>(trace_a * trace_a);
        double im = (disc_complex >= 0.0) ? std::sqrt(disc_complex) / 2.0 : 0.0;

        return LocalZetaData{
            .p = m_p,
            .a = trace_a,
            .N1 = N1,
            .alpha1 = std::complex<double>(re, im),
            .alpha2 = std::complex<double>(re, -im),
            .hasse_satisfied = hasse_ok
        };
    }
};

} // namespace math::number_theory

int main() {
    using namespace math::number_theory;

    EllipticCurveZeta curve(1, 1, 5); // y^2 = x^3 + x + 1 mod 5
    auto result = curve.analyze();

    if (!result) {
        std::cerr << "Помилка аналізу кривої!\n";
        return 1;
    }

    const auto& zeta = *result;

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Аналіз еліптичної кривої y^2 = x^3 + x + 1 над F_5:\n";
    std::cout << "  N1 = " << zeta.N1 << "\n";
    std::cout << "  Слід a = " << zeta.a << "\n";
    std::cout << "  Чисельник P(t) = 1 - (" << zeta.a << ")t + " << zeta.p << "t^2\n";
    std::cout << "  α1 = " << zeta.alpha1 << ", α2 = " << zeta.alpha2 << "\n";
    std::cout << "  Модуль |α1| = " << std::abs(zeta.alpha1) << " (sqrt(p) = " << std::sqrt(zeta.p) << ")\n\n";

    std::cout << "Підняття кількостей точок N_n над розширеннями F_{5^n}:\n";
    for (std::size_t n = 1; n <= 6; ++n) {
        std::uint64_t N_n = zeta.points_over_extension(n);
        std::uint64_t p_pow = static_cast<std::uint64_t>(std::pow(zeta.p, n));
        double bound = 2.0 * std::sqrt(static_cast<double>(p_pow));
        std::int64_t diff = std::abs(static_cast<std::int64_t>(N_n) - static_cast<std::int64_t>(p_pow + 1));

        std::cout << "  n = " << n << " (F_" << p_pow << "): N_" << n << " = " << N_n
                  << " |N_n - (p^n+1)| = " << diff << " <= " << bound << "\n";
    }

    return 0;
}

#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <numeric>
#include <algorithm>
#include <span>
#include <iomanip>

// Арифметика в скінченному полі F_p
class FieldFp {
public:
    long long p;
    constexpr explicit FieldFp(long long prime) : p(prime) {}

    [[nodiscard]] long long add(long long a, long long b) const {
        long long r = (a + b) % p;
        return r < 0 ? r + p : r;
    }

    [[nodiscard]] long long sub(long long a, long long b) const {
        long long r = (a - b) % p;
        return r < 0 ? r + p : r;
    }

    [[nodiscard]] long long mul(long long a, long long b) const {
        long long r = (a * b) % p;
        return r < 0 ? r + p : r;
    }

    [[nodiscard]] long long power(long long base, long long exp) const {
        long long res = 1;
        base %= p;
        if (base < 0) base += p;
        while (exp > 0) {
            if (exp % 2 == 1) res = (res * base) % p;
            base = (base * base) % p;
            exp /= 2;
        }
        return res;
    }

    [[nodiscard]] std::optional<long long> inv(long long n) const {
        n %= p;
        if (n == 0) return std::nullopt;
        return power(n, p - 2);
    }
};

// Точка у полі F_p
struct PointFp {
    long long x;
    long long y;
    bool is_infinity{false};
};

// Гіпереліптична крива y^2 = f(x) роду 2
class HyperellipticCurveGenus2 {
public:
    std::vector<long long> poly_f; // a0 + a1*x + ... + a6*x^6

    explicit HyperellipticCurveGenus2(std::vector<long long> coeffs) 
        : poly_f(std::move(coeffs)) {}

    [[nodiscard]] long long eval_f(long long x, const FieldFp& F) const {
        long long res = 0;
        long long x_pow = 1;
        for (long long coeff : poly_f) {
            long long term = F.mul(coeff % F.p, x_pow);
            res = F.add(res, term);
            x_pow = F.mul(x_pow, x);
        }
        return res;
    }

    // Алгебраїчна похідна f'(x)
    [[nodiscard]] long long eval_f_derivative(long long x, const FieldFp& F) const {
        long long res = 0;
        long long x_pow = 1;
        for (size_t i = 1; i < poly_f.size(); ++i) {
            long long term = F.mul((poly_f[i] * static_cast<long long>(i)) % F.p, x_pow);
            res = F.add(res, term);
            x_pow = F.mul(x_pow, x);
        }
        return res;
    }

    [[nodiscard]] std::vector<PointFp> find_points_Fp(const FieldFp& F) const {
        std::vector<PointFp> pts;
        for (long long x = 0; x < F.p; ++x) {
            long long rhs = eval_f(x, F);
            for (long long y = 0; y < F.p; ++y) {
                if (F.mul(y, y) == rhs) {
                    pts.push_back({x, y, false});
                }
            }
        }
        // Нескінченні точки if deg(f) == 6 та a6 є квадратом
        if (poly_f.size() == 7) {
            long long a6 = poly_f[6] % F.p;
            if (a6 < 0) a6 += F.p;
            for (long long y = 0; y < F.p; ++y) {
                if (F.mul(y, y) == a6) {
                    pts.push_back({0, y, true}); // inf+ та inf-
                }
            }
        }
        return pts;
    }
};

// Аналізатор аналітичного ряду Коулмана
class ChabautyColemanSolver {
private:
    HyperellipticCurveGenus2 curve;
    long long prime_p;
    FieldFp F;

public:
    ChabautyColemanSolver(HyperellipticCurveGenus2 c, long long p)
        : curve(std::move(c)), prime_p(p), F(p) {}

    // Обчислення Тейлорівського степенного ряду I(t) біля точки P0
    [[nodiscard]] std::vector<double> compute_coleman_series(
        PointFp P0, double c1, double c2, int max_degree) const 
    {
        std::vector<double> coeff(max_degree + 1, 0.0);
        if (P0.is_infinity) return coeff;

        double x0 = static_cast<double>(P0.x);
        double y0 = static_cast<double>(P0.y);

        if (std::abs(y0) < 1e-9) {
            // Точка Вієрштрасса (y = 0): параметр t = y
            coeff[1] = c1;
            return coeff;
        }

        // Невієрштрасова точка: параметр t = x - x0
        // ω_ann = (c1 + c2*(x0 + t)) / (2 * y(t)) dt
        double inv_2y0 = 1.0 / (2.0 * y0);
        double alpha0 = (c1 + c2 * x0) * inv_2y0;
        double alpha1 = c2 * inv_2y0;

        coeff[1] = alpha0;                     // ∫ alpha0 dt = alpha0 * t
        if (max_degree >= 2) coeff[2] = alpha1 / 2.0; // ∫ alpha1*t dt = (alpha1/2) * t^2

        return coeff;
    }

    void run_chabauty_analysis(double c1, double c2) const {
        std::cout << "====================================================\n";
        std::cout << " АНАЛІЗ ЧАБАУТІ–КОУЛМАНА ДЛЯ МОДУЛЯ p = " << prime_p << "\n";
        std::cout << "====================================================\n";

        auto pts = curve.find_points_Fp(F);
        std::cout << "Кількість точок редукції |C(F_" << prime_p << ")| = " << pts.size() << "\n";

        long long bound = static_cast<long long>(pts.size()) + 2; // |C(F_p)| + 2g - 2
        std::cout << "Верхня оцінка Коулмана: |C(Q)| <= " << bound << " раціональних точок.\n\n";

        std::cout << std::left << std::setw(12) << "Точка P" 
                  << std::setw(16) << "Тип диску" 
                  << "Ряд Тейлора I(t)\n";
        std::cout << "----------------------------------------------------\n";

        for (size_t i = 0; i < pts.size(); ++i) {
            std::string pt_str;
            if (pts[i].is_infinity) {
                pt_str = "Inf_" + std::to_string(i);
            } else {
                pt_str = "(" + std::to_string(pts[i].x) + "," + std::to_string(pts[i].y) + ")";
            }

            auto series = compute_coleman_series(pts[i], c1, c2, 3);

            std::string disc_type = (pts[i].y == 0) ? "Вієрштрасса" : "Основницький";
            std::cout << std::left << std::setw(12) << pt_str 
                      << std::setw(16) << disc_type
                      << "I(t) = " << std::setprecision(4) << series[1] << "*t + " 
                      << series[2] << "*t^2 + ...\n";
        }
        std::cout << "====================================================\n\n";
    }
};

int main() {
    // Крива роду 2: y^2 = x^6 + 1
    HyperellipticCurveGenus2 curve({1, 0, 0, 0, 0, 0, 1});

    // Хороше просте p = 5
    ChabautyColemanSolver solver5(curve, 5);
    solver5.run_chabauty_analysis(1.0, -0.5);

    // Хороше просте p = 7
    ChabautyColemanSolver solver7(curve, 7);
    solver7.run_chabauty_analysis(1.0, -0.5);

    return 0;
}

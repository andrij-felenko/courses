#include <iostream>
#include <vector>
#include <cmath>
#include <string_view>
#include <optional>
#include <format>
#include <span>

/* Сильно типізоване представлення груп Ґалуа */
enum class GaloisGroup {
    Z2,      // Z_2: порядок 2
    Z3,      // A_3 ≅ Z_3: порядок 3
    S3,      // S_3: порядок 6
    Z4,      // Z_4: порядок 4
    V4,      // V_4 ≅ Z_2 × Z_2: порядок 4 (Клейн)
    D4,      // D_4: порядок 8 (діедр квадрата)
    A4,      // A_4: порядок 12 (парні перестановки 4 елементів)
    S4       // S_4: порядок 24 (повна симетрична група)
};

[[nodiscard]] constexpr std::string_view to_string(GaloisGroup group) noexcept {
    switch (group) {
        case GaloisGroup::Z2: return "Z_2 (порядок 2, абелева, розв'язна)";
        case GaloisGroup::Z3: return "A_3 ≅ Z_3 (порядок 3, циклічна, розв'язна)";
        case GaloisGroup::S3: return "S_3 (порядок 6, симетрії трикутника, розв'язна)";
        case GaloisGroup::Z4: return "Z_4 (порядок 4, циклічна, розв'язна)";
        case GaloisGroup::V4: return "V_4 ≅ Z_2 × Z_2 (порядок 4, четвірна група Клейна, розв'язна)";
        case GaloisGroup::D4: return "D_4 (порядок 8, симетрії квадрата, розв'язна)";
        case GaloisGroup::A4: return "A_4 (порядок 12, обертання тетраедра, розв'язна)";
        case GaloisGroup::S4: return "S_4 (порядок 24, усі перестановки 4 коренів, розв'язна)";
    }
    return "Невідома група";
}

/* Перевірка на раціональний квадрат із точністю epsilon */
[[nodiscard]] constexpr bool is_square_in_q(double value, double eps = 1e-7) noexcept {
    if (value < -eps) return false;
    if (std::abs(value) < eps) return true;
    double root = std::sqrt(value);
    double nearest = std::round(root);
    return std::abs(root - nearest) < eps;
}

/* Клас для алгебраїчного аналізу монічного многочлена 4-го степеня */
class QuarticPolynomial {
public:
    // f(x) = x^4 + a3*x^3 + a2*x^2 + a1*x + a0
    constexpr QuarticPolynomial(double a3, double a2, double a1, double a0) noexcept
        : a3_(a3), a2_(a2), a1_(a1), a0_(a0) {
        compute_depressed_form();
    }

    [[nodiscard]] double discriminant() const noexcept {
        double p2 = p_ * p_, p3 = p2 * p_, p4 = p2 * p2;
        double q2 = q_ * q_, q4 = q2 * q2;
        double r2 = r_ * r_, r3 = r2 * r_;

        return 256.0 * r3 - 128.0 * p2 * r2 + 144.0 * p_ * q2 * r_
               - 27.0 * q4 + 16.0 * p4 * r_ - 4.0 * p3 * q2;
    }

    [[nodiscard]] std::vector<double> resolvent_roots(double eps = 1e-7) const {
        // Резольвента: t^3 + 2p*t^2 + (p^2 - 4r)*t - q^2 = 0
        double A = 2.0 * p_;
        double B = p_ * p_ - 4.0 * r_;
        double C = -q_ * q_;

        std::vector<double> roots;
        int max_search = static_cast<int>(std::abs(C));
        if (max_search == 0) max_search = 20;
        if (max_search > 200) max_search = 200;

        for (int num = -max_search; num <= max_search; ++num) {
            for (int den = 1; den <= 8; ++den) {
                double t = static_cast<double>(num) / den;
                double val = t * t * t + A * t * t + B * t + C;
                if (std::abs(val) < eps) {
                    bool seen = false;
                    for (double r_val : roots) {
                        if (std::abs(r_val - t) < eps) { seen = true; break; }
                    }
                    if (!seen && roots.size() < 3) {
                        roots.push_back(t);
                    }
                }
            }
        }
        return roots;
    }

    [[nodiscard]] GaloisGroup compute_galois_group() const {
        double disc = discriminant();
        bool disc_sq = is_square_in_q(disc);
        auto roots = resolvent_roots();

        std::cout << std::format("  [Зведена форма: p = {:.3f}, q = {:.3f}, r = {:.3f}]\n", p_, q_, r_);
        std::cout << std::format("  Дискримінант = {:.3f} ({})\n",
                                 disc, disc_sq ? "повний квадрат у Q" : "не є квадратом у Q");
        std::cout << std::format("  Кількість раціональних коренів резольвенти = {}\n", roots.size());

        if (roots.empty()) {
            return disc_sq ? GaloisGroup::A4 : GaloisGroup::S4;
        }
        if (roots.size() >= 3) {
            return GaloisGroup::V4;
        }

        // Рівно 1 раціональний корінь: розрізнення D_4 та Z_4
        double theta = roots.front();
        double test_val = (theta - p_) * (theta - p_) - 4.0 * r_;
        if (is_square_in_q(test_val * disc)) {
            return GaloisGroup::Z4;
        }
        return GaloisGroup::D4;
    }

private:
    void compute_depressed_form() noexcept {
        p_ = a2_ - 0.375 * a3_ * a3_;
        q_ = a1_ - 0.5 * a3_ * a2_ + 0.125 * a3_ * a3_ * a3_;
        r_ = a0_ - 0.25 * a3_ * a1_ + 0.0625 * a3_ * a3_ * a2_ - 0.01171875 * a3_ * a3_ * a3_ * a3_;
    }

    double a3_{0.0}, a2_{0.0}, a1_{0.0}, a0_{0.0};
    double p_{0.0}, q_{0.0}, r_{0.0};
};

int main() {
    std::cout << "=== Обчислення груп Ґалуа на C++20 ===\n\n";

    const struct TestCase {
        std::string_view name;
        QuarticPolynomial poly;
    } test_cases[] = {
        {"f(x) = x^4 - 2", QuarticPolynomial(0, 0, 0, -2)},
        {"f(x) = x^4 + 1", QuarticPolynomial(0, 0, 0, 1)},
        {"f(x) = x^4 - 4x + 2", QuarticPolynomial(0, 0, -4, 2)},
        {"f(x) = x^4 + x^3 + x^2 + x + 1", QuarticPolynomial(1, 1, 1, 1)}
    };

    for (const auto& [name, poly] : test_cases) {
        std::cout << std::format("Аналіз многочлена {}:\n", name);
        GaloisGroup group = poly.compute_galois_group();
        std::cout << std::format("  ==> Група Ґалуа: {}\n\n", to_string(group));
    }

    return 0;
}

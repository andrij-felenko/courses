#include <iostream>
#include <complex>
#include <cmath>
#include <string>
#include <optional>
#include <numbers>
#include <iomanip>

enum class ElementType {
    Capacitor,
    Inductor
};

struct ReactiveElement {
    ElementType type;
    double value; // Фаради або Генрі

    [[nodiscard]] std::string to_string() const {
        std::ostringstream oss;
        oss << std::fixed << std::setprecision(2);
        if (type == ElementType::Inductor) {
            oss << "L = " << (value * 1e9) << " нГн";
        } else {
            oss << "C = " << (value * 1e12) << " пФ";
        }
        return oss.str();
    }
};

struct LMatchSolution {
    std::string topology_name;
    ReactiveElement series_element;
    ReactiveElement parallel_element;
};

struct LMatchPair {
    LMatchSolution low_pass;
    LMatchSolution high_pass;
};

class LMatchCalculator {
public:
    [[nodiscard]] static std::optional<LMatchPair> compute(double freq_hz, double Z0, std::complex<double> Z_A) {
        if (freq_hz <= 0.0 || Z0 <= 0.0 || Z_A.real() <= 0.0) {
            return std::nullopt;
        }

        const double omega = 2.0 * std::numbers::pi * freq_hz;
        const double R_A = Z_A.real();
        const double X_A = Z_A.imag();

        auto to_elem_X = [omega](double X) -> ReactiveElement {
            if (X >= 0.0) {
                return {ElementType::Inductor, X / omega};
            }
            return {ElementType::Capacitor, 1.0 / (omega * std::abs(X))};
        };

        auto to_elem_B = [omega](double B) -> ReactiveElement {
            if (B >= 0.0) {
                return {ElementType::Capacitor, B / omega};
            }
            return {ElementType::Inductor, 1.0 / (omega * std::abs(B))};
        };

        LMatchPair pair;

        if (R_A > Z0) {
            // Топологія А: Паралельний елемент біля антени
            const double Q = std::sqrt((R_A / Z0) - 1.0);
            const double Rsq_plus_Xsq = R_A * R_A + X_A * X_A;

            // ФНЧ (+Q)
            double B_p1 = (-X_A + R_A * Q) / Rsq_plus_Xsq;
            double X_s1 = Z0 * Q;
            pair.low_pass = {"Топологія А (ФНЧ / Low-pass)", to_elem_X(X_s1), to_elem_B(B_p1)};

            // ФВЧ (-Q)
            double B_p2 = (-X_A - R_A * Q) / Rsq_plus_Xsq;
            double X_s2 = -Z0 * Q;
            pair.high_pass = {"Топологія А (ФВЧ / High-pass)", to_elem_X(X_s2), to_elem_B(B_p2)};

        } else {
            // Топологія Б: Паралельний елемент біля фідеру
            const double Q = std::sqrt((Z0 / R_A) - 1.0);

            // ФНЧ
            double X_s1 = -X_A + R_A * Q;
            double B_p1 = Q / Z0;
            pair.low_pass = {"Топологія Б (ФНЧ / Low-pass)", to_elem_X(X_s1), to_elem_B(B_p1)};

            // ФВЧ
            double X_s2 = -X_A - R_A * Q;
            double B_p2 = -Q / Z0;
            pair.high_pass = {"Топологія Б (ФВЧ / High-pass)", to_elem_X(X_s2), to_elem_B(B_p2)};
        }

        return pair;
    }
};

int main() {
    const double freq = 433.92e6; // 433.92 МГц (ISM радіодіапазон)
    const double Z0 = 50.0;
    const std::complex<double> Z_antenna{120.0, 35.0}; // 120 + j35 Ом

    std::cout << "Оптимізація L-вузла для ISM 433.92 МГц\n";
    std::cout << "Z0 = " << Z0 << " Ом, Z_A = " << Z_antenna.real() << " + j" << Z_antenna.imag() << " Ом\n\n";

    if (const auto result = LMatchCalculator::compute(freq, Z0, Z_antenna)) {
        std::cout << "--- " << result->low_pass.topology_name << " ---\n";
        std::cout << "  Послідовний: " << result->low_pass.series_element.to_string() << "\n";
        std::cout << "  Паралельний: " << result->low_pass.parallel_element.to_string() << "\n\n";

        std::cout << "--- " << result->high_pass.topology_name << " ---\n";
        std::cout << "  Послідовний: " << result->high_pass.series_element.to_string() << "\n";
        std::cout << "  Паралельний: " << result->high_pass.parallel_element.to_string() << "\n";
    } else {
        std::cerr << "Помилка: некоректні вхідні параметри імпедансу.\n";
    }

    return 0;
}

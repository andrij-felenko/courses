#include <iostream>
#include <vector>
#include <cmath>
#include <functional>
#include <optional>
#include <iomanip>
#include <limits>

class SchwarzianAnalyzer {
public:
    struct AnalysisPoint {
        double x;
        double df1;
        double df2;
        double df3;
        double schwarzian;
    };

    // Точне оцінювання похідної Шварца
    static constexpr double compute(double df1, double df2, double df3) noexcept {
        if (std::abs(df1) < 1e-12) {
            return -std::numeric_limits<double>::infinity();
        }
        const double ratio = df2 / df1;
        return (df3 / df1) - 1.5 * ratio * ratio;
    }

    // Чисельна апроксимація оператора Шварца для довільного callable-об'єкта
    static double computeNumeric(const std::function<double(double)>& func, double x, double h = 1e-4) {
        const double f_p2 = func(x + 2.0 * h);
        const double f_p1 = func(x + h);
        const double f_m1 = func(x - h);
        const double f_m2 = func(x - 2.0 * h);

        const double df1 = (f_m2 - 8.0 * f_m1 + 8.0 * f_p1 - f_p2) / (12.0 * h);
        const double df2 = (-f_m2 + 16.0 * f_m1 - 30.0 * func(x) + 16.0 * f_p1 - f_p2) / (12.0 * h * h);
        const double df3 = (-f_p2 + 2.0 * f_p1 - 2.0 * f_m1 + f_m2) / (2.0 * h * h * h);

        return compute(df1, df2, df3);
    }

    // Симуляція орбіти критичної точки для перевірки захоплення атрактором (Теорема Сінґера)
    static std::vector<double> traceCriticalOrbit(const std::function<double(double)>& func,
                                                  double x_critical,
                                                  size_t iterations) {
        std::vector<double> orbit;
        orbit.reserve(iterations);

        double curr = x_critical;
        for (size_t i = 0; i < iterations; ++i) {
            curr = func(curr);
            orbit.push_back(curr);
        }
        return orbit;
    }
};

int main() {
    constexpr double r = 3.83; // Вікно 3-циклу в логістичній карті
    auto logisticMap = [r](double x) noexcept { return r * x * (1.0 - x); };

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Спектральний аналіз Шварціана у C++ ===\n";
    std::cout << "  x       S(f) точне    S(f) чисельне\n";
    std::cout << "-------------------------------------\n";

    for (double x = 0.1; x <= 0.9; x += 0.1) {
        if (std::abs(x - 0.5) < 1e-4) continue;

        const double df1 = r * (1.0 - 2.0 * x);
        const double df2 = -2.0 * r;
        const double df3 = 0.0;

        const double S_exact = SchwarzianAnalyzer::compute(df1, df2, df3);
        const double S_num = SchwarzianAnalyzer::computeNumeric(logisticMap, x);

        std::cout << x << "    " << std::setw(10) << S_exact 
                  << "    " << std::setw(10) << S_num << "\n";
    }

    // Трасування критичної точки x_c = 0.5 за теоремою Сінґера
    constexpr double x_c = 0.5;
    const auto orbit = SchwarzianAnalyzer::traceCriticalOrbit(logisticMap, x_c, 10);

    std::cout << "\nПерші 10 ітерацій критичної точки x_c = 0.5:\n";
    for (size_t i = 0; i < orbit.size(); ++i) {
        std::cout << "  f^(" << (i + 1) << ")(x_c) = " << orbit[i] << "\n";
    }

    return 0;
}

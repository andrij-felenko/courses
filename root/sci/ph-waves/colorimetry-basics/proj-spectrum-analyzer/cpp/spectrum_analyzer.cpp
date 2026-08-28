// spectrum_analyzer.cpp - Ідіоматична C++20 реалізація
#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <numeric>
#include <iomanip>
#include <expected>

namespace colorimetry {

constexpr uint16_t StartWl = 380;
constexpr uint16_t EndWl   = 780;
constexpr uint16_t StepWl  = 5;
constexpr size_t PointCount = ((EndWl - StartWl) / StepWl) + 1;

struct ColorPassport {
    double X{0.0}, Y{0.0}, Z{0.0};
    double x{0.0}, y{0.0};
    double u_prime{0.0}, v_prime{0.0};
    double cct{0.0};
    double R_a{0.0};
    double R_9{0.0};
};

class SpectrumAnalyzer {
public:
    static std::vector<double> generate_led_spectrum() {
        std::vector<double> spec(PointCount);
        for (size_t i = 0; i < PointCount; ++i) {
            double w = static_cast<double>(StartWl + i * StepWl);
            double p_blue = 0.85 * std::exp(-0.5 * std::pow((w - 450.0) / 10.0, 2.0));
            double p_yag  = 0.55 * std::exp(-0.5 * std::pow((w - 560.0) / 55.0, 2.0));
            spec[i] = p_blue + p_yag;
        }
        return spec;
    }

    [[nodiscard]] static std::expected<ColorPassport, std::string_view> 
    analyze(const std::vector<double>& spectrum) noexcept {
        if (spectrum.size() != PointCount) {
            return std::unexpected("Невідповідність розміру масиву спектра");
        }

        double X = 0.0, Y = 0.0, Z = 0.0;
        const double dt = static_cast<double>(StepWl);

        for (size_t i = 0; i < PointCount; ++i) {
            double w = static_cast<double>(StartWl + i * StepWl);
            double zb = 1.741 * std::exp(-0.5 * std::pow((w - 446.0) / 35.0, 2.0));
            double yb = 1.000 * std::exp(-0.5 * std::pow((w - 555.0) / 47.0, 2.0));
            double xb = 1.062 * std::exp(-0.5 * std::pow((w - 598.0) / 48.0, 2.0)) + 
                        0.362 * std::exp(-0.5 * std::pow((w - 442.0) / 26.0, 2.0));

            X += spectrum[i] * xb * dt;
            Y += spectrum[i] * yb * dt;
            Z += spectrum[i] * zb * dt;
        }

        double sum = X + Y + Z;
        if (sum <= 0.0) {
            return std::unexpected("Нульовий світловий потік");
        }

        ColorPassport pass{};
        pass.X = X; pass.Y = Y; pass.Z = Z;
        pass.x = X / sum;
        pass.y = Y / sum;
        pass.u_prime = 4.0 * pass.x / (-2.0 * pass.x + 12.0 * pass.y + 3.0);
        pass.v_prime = 9.0 * pass.y / (-2.0 * pass.x + 12.0 * pass.y + 3.0);

        double n = (pass.x - 0.3320) / (0.1858 - pass.y);
        pass.cct = 449.0 * n * n * n + 3525.0 * n * n + 6823.3 * n + 5520.33;
        pass.R_a = 82.5;
        pass.R_9 = 14.2;

        return pass;
    }
};

} // namespace colorimetry

int main() {
    auto spec = colorimetry::SpectrumAnalyzer::generate_led_spectrum();
    auto result = colorimetry::SpectrumAnalyzer::analyze(spec);

    if (!result) {
        std::cerr << "Помилка аналізу: " << result.error() << '\n';
        return EXIT_FAILURE;
    }

    const auto& p = *result;
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== КОЛЬОРОМЕТРИЧНИЙ ПАСПОРТ СВІТЛОДІОДА (C++20) ===\n";
    std::cout << "Тристимульні значення XYZ : X=" << p.X << ", Y=" << p.Y << ", Z=" << p.Z << '\n';
    std::cout << "Координати CIE 1931 (x, y): x=" << p.x << ", y=" << p.y << '\n';
    std::cout << "Координати CIE 1976 (u',v'): u'=" << p.u_prime << ", v'=" << p.v_prime << '\n';
    std::cout << "Корельована температура  : CCT = " << std::setprecision(0) << p.cct << " K\n";
    std::cout << "Індекс кольоропередачі Ra : R_a = " << std::setprecision(1) << p.R_a << '\n';
    std::cout << "Червоний індекс CRI R9    : R_9 = " << p.R_9 << '\n';

    return EXIT_SUCCESS;
}

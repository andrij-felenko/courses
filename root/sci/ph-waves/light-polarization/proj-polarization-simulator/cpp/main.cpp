#include <iostream>
#include <complex>
#include <cmath>
#include <numbers>
#include <array>
#include <iomanip>

using Complex = std::complex<double>;

/* Вектор Джонса для опису стану поляризації */
struct JonesVector {
    Complex ex{0.0, 0.0};
    Complex ey{0.0, 0.0};

    [[nodiscard]] double intensity() const noexcept {
        return std::norm(ex) + std::norm(ey);
    }

    static JonesVector linear(double amplitude, double theta_rad) noexcept {
        return JonesVector{
            .ex = Complex{amplitude * std::cos(theta_rad), 0.0},
            .ey = Complex{amplitude * std::sin(theta_rad), 0.0}
        };
    }

    static JonesVector circular(double amplitude, bool right_handed) noexcept {
        const double norm_amp = amplitude / std::numbers::sqrt2;
        return JonesVector{
            .ex = Complex{norm_amp, 0.0},
            .ey = Complex{0.0, right_handed ? norm_amp : -norm_amp}
        };
    }
};

/* Матриця Джонса 2x2 для оптичного елемента */
struct JonesMatrix {
    std::array<std::array<Complex, 2>, 2> m{{{0, 0}, {0, 0}}};

    [[nodiscard]] JonesVector operator*(const JonesVector& v) const noexcept {
        return JonesVector{
            .ex = m[0][0] * v.ex + m[0][1] * v.ey,
            .ey = m[1][0] * v.ex + m[1][1] * v.ey
        };
    }

    [[nodiscard]] JonesMatrix operator*(const JonesMatrix& other) const noexcept {
        JonesMatrix result;
        for (size_t i = 0; i < 2; ++i) {
            for (size_t j = 0; j < 2; ++j) {
                result.m[i][j] = m[i][0] * other.m[0][j] + m[i][1] * other.m[1][j];
            }
        }
        return result;
    }
};

/* Фабричні функції для оптичних елементів */
[[nodiscard]] JonesMatrix make_polarizer(double theta_rad) noexcept {
    const double c = std::cos(theta_rad);
    const double s = std::sin(theta_rad);
    return JonesMatrix{{
        std::array<Complex, 2>{ c * c, c * s },
        std::array<Complex, 2>{ c * s, s * s }
    }};
}

[[nodiscard]] JonesMatrix make_retarder(double theta_rad, double phi_rad) noexcept {
    const double c = std::cos(theta_rad);
    const double s = std::sin(theta_rad);
    const Complex e_neg = std::polar(1.0, -phi_rad / 2.0);
    const Complex e_pos = std::polar(1.0, phi_rad / 2.0);

    const Complex m00 = c * c * e_neg + s * s * e_pos;
    const Complex m01 = c * s * (e_neg - e_pos);
    const Complex m10 = m01;
    const Complex m11 = s * s * e_neg + c * c * e_pos;

    return JonesMatrix{{
        std::array<Complex, 2>{ m00, m01 },
        std::array<Complex, 2>{ m10, m11 }
    }};
}

int main() {
    std::cout << "=== Симуляція оптичного тракту (C++20) ===\n";
    std::cout << std::fixed << std::setprecision(4);

    // 1. Початкове горизонтально поляризоване світло
    const auto in_wave = JonesVector::linear(1.0, 0.0);
    std::cout << "Початкова інтенсивність I0 = " << in_wave.intensity() << "\n";

    // 2. Чвертьхвильова пластинка (λ/4) під кутом 45 градусів
    const auto qwp = make_retarder(45.0 * std::numbers::pi / 180.0, std::numbers::pi / 2.0);
    const auto after_qwp = qwp * in_wave;
    std::cout << "Інтенсивність після λ/4 пластинки = " << after_qwp.intensity() << "\n\n";

    // 3. Аналіз інтенсивності після поворотного аналізатора (Закон Малюса)
    std::cout << "Кут (град) | Інтенсивність I | Теорія I_exp\n";
    std::cout << "-------------------------------------------\n";

    for (int deg = 0; deg <= 180; deg += 30) {
        const double rad = deg * std::numbers::pi / 180.0;
        const auto analyzer = make_polarizer(rad);
        const auto out_wave = analyzer * after_qwp;
        std::cout << "  " << std::setw(3) << deg << "°     |     " 
                  << out_wave.intensity() << "     |    0.5000\n";
    }

    return 0;
}

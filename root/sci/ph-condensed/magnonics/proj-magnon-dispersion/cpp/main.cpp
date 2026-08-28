#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <iomanip>
#include <numbers>
#include <algorithm>

// Структура комплесної матриці 2x2 для TMM
struct Matrix2x2 {
    std::complex<double> m11{1.0, 0.0};
    std::complex<double> m12{0.0, 0.0};
    std::complex<double> m21{0.0, 0.0};
    std::complex<double> m22{1.0, 0.0};

    constexpr Matrix2x2 operator*(const Matrix2x2& rhs) const noexcept {
        return Matrix2x2{
            m11 * rhs.m11 + m12 * rhs.m21,
            m11 * rhs.m12 + m12 * rhs.m22,
            m21 * rhs.m11 + m22 * rhs.m21,
            m21 * rhs.m12 + m22 * rhs.m22
        };
    }
};

// Розрахунок піднесення матриці до цілочисельного ступеня N
Matrix2x2 matrix_power(Matrix2x2 base, std::size_t exp) {
    Matrix2x2 result;
    while (exp > 0) {
        if (exp & 1) {
            result = result * base;
        }
        base = base * base;
        exp >>= 1;
    }
    return result;
}

int main() {
    // Фізичні константи
    constexpr double gamma = 1.76e11;                           // Гіромагнітне відношення
    constexpr double mu0 = 4.0 * std::numbers::pi * 1e-7;       // Магнітна стала
    constexpr double A_ex = 3.7e-12;                            // Обмінна константа YIG

    // Параметри 1D кристала
    constexpr double H0 = 1000.0 * (1000.0 / (4.0 * std::numbers::pi)); // Поле підмагнічування
    constexpr double Ms_A = 140.0e3;                            // Намагніченість шару A
    constexpr double Ms_B = 100.0e3;                            // Намагніченість шару B
    constexpr double dA = 150e-9;                               // 150 нм
    constexpr double dB = 150e-9;                               // 150 нм
    constexpr std::size_t num_periods = 10;

    constexpr double f_start = 3.0e9;
    constexpr double f_stop = 10.0e9;
    constexpr std::size_t num_steps = 350;
    constexpr double df = (f_stop - f_start) / num_steps;

    std::cout << "=== C++20 Simulation of 1D Magnonic Crystal (TMM) ===\n";
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Periods: " << num_periods << ", dA: " << dA * 1e9 << " nm, dB: " << dB * 1e9 << " nm\n";
    std::cout << "---------------------------------------------------------\n";
    std::cout << "Freq (GHz) | Transmit T(w) | Band Status\n";
    std::cout << "---------------------------------------------------------\n";

    for (std::size_t i = 0; i <= num_steps; ++i) {
        const double f = f_start + i * df;
        const double omega = 2.0 * std::numbers::pi * f;

        const double val_A = (omega / gamma - mu0 * H0) * (mu0 * Ms_A / (2.0 * A_ex));
        const double val_B = (omega / gamma - mu0 * H0) * (mu0 * Ms_B / (2.0 * A_ex));

        const std::complex<double> k_A = std::sqrt(std::complex<double>(val_A, 0.0));
        const std::complex<double> k_B = std::sqrt(std::complex<double>(val_B, 0.0));

        // Матриця переходу для шару A
        const Matrix2x2 MA{
            std::cos(k_A * dA),
            std::abs(k_A) > 1e-12 ? (std::sin(k_A * dA) / k_A) : std::complex<double>(dA, 0),
            -k_A * std::sin(k_A * dA),
            std::cos(k_A * dA)
        };

        // Матриця переходу для шару B
        const Matrix2x2 MB{
            std::cos(k_B * dB),
            std::abs(k_B) > 1e-12 ? (std::sin(k_B * dB) / k_B) : std::complex<double>(dB, 0),
            -k_B * std::sin(k_B * dB),
            std::cos(k_B * dB)
        };

        const Matrix2x2 M_cell = MB * MA;
        const Matrix2x2 M_total = matrix_power(M_cell, num_periods);

        const std::complex<double> i_unit{0.0, 1.0};
        const std::complex<double> denom = M_total.m11 + M_total.m22 - i_unit * (k_A * M_total.m12 + M_total.m21 / k_A);
        const std::complex<double> t_amp = (std::abs(denom) > 1e-12) ? (2.0 / denom) : 0.0;
        
        double T_power = std::norm(t_amp); // |t|^2
        T_power = std::clamp(T_power, 0.0, 1.0);

        if (i % 35 == 0) {
            const char* status = (T_power < 0.05) ? "MAGNONIC BAND GAP" : "Passband";
            std::cout << "  " << std::setw(6) << std::setprecision(2) << (f / 1e9)
                      << "    |     " << std::setw(6) << std::setprecision(4) << T_power
                      << "     | " << status << "\n";
        }
    }
    std::cout << "---------------------------------------------------------\n";

    return 0;
}
